import streamlit as st
import os
import base64
import pandas as pd
import shutil
import zipfile
import io
import cv2
import numpy as np
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector, AdaptiveDetector
from moviepy.editor import VideoFileClip
from openai import OpenAI, RateLimitError

# --- 設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp_data")

# 顔認識用の分類器（OpenCV標準）をロード
face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)

def init_temp_dir():
    if os.path.exists(TEMP_DIR):
        try:
            shutil.rmtree(TEMP_DIR)
        except:
            pass
    os.makedirs(TEMP_DIR)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def evaluate_frame(frame_img):
    """
    フレームの品質をスコア化する関数
    1. ブレていないか（鮮明度）
    2. 人の顔が映っているか
    """
    # グレースケール変換
    gray = cv2.cvtColor(frame_img, cv2.COLOR_RGB2GRAY)
    
    # 1. 鮮明度スコア（ラプラシアン分散）
    # 数値が大きいほどエッジが効いている（ピントが合っている）
    sharpness_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # 2. 顔検出ボーナス
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    face_bonus = 0
    if len(faces) > 0:
        # 顔が見つかったら、鮮明度に関わらず大きく加点（+300点）
        # これにより「ブレてない風景」より「多少ブレてても人がいる」を優先する傾向にする
        face_bonus = 300
    
    total_score = sharpness_score + face_bonus
    return total_score

def save_best_frame(clip, start, end, output_path):
    """
    指定区間からベストな（鮮明かつ顔がある）フレームを探して保存
    """
    duration = end - start
    
    # チェックする候補の数（多いほど正確だが遅くなる）
    # 0.5秒以下の短いカットは真ん中1発勝負
    if duration < 0.5:
        t_candidates = [start + duration/2]
    else:
        # 始点と終点のギリギリは避けて、均等に5点サンプリング
        t_candidates = np.linspace(start + 0.1, end - 0.1, num=5)

    best_score = -1
    best_t = t_candidates[0]

    for t in t_candidates:
        try:
            # moviepyでフレーム取得 (numpy array)
            frame = clip.get_frame(t)
            score = evaluate_frame(frame)
            
            if score > best_score:
                best_score = score
                best_t = t
        except:
            continue
    
    # ベストな時間のフレームを保存
    clip.save_frame(output_path, t=best_t)


def detect_scenes(video_path, threshold=27.0, min_scene_len=15, use_adaptive=False):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    
    if use_adaptive:
        detector = AdaptiveDetector(adaptive_threshold=threshold, min_scene_len=min_scene_len)
    else:
        detector = ContentDetector(threshold=threshold, min_scene_len=min_scene_len)

    scene_manager.add_detector(detector)
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list(video_manager)
    return scene_list

def create_zip_file(data_list):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        df = pd.DataFrame(data_list)
        df["サムネイルファイル名"] = df["サムネイルパス"].apply(lambda x: os.path.basename(x))
        csv_data = df.drop(columns=["サムネイルパス"]).to_csv(index=False).encode('utf-8')
        zf.writestr("cut_list.csv", csv_data)
        for row in data_list:
            img_path = row["サムネイルパス"]
            if os.path.exists(img_path):
                zf.write(img_path, arcname=f"images/{os.path.basename(img_path)}")
    return zip_buffer.getvalue()

def process_video_and_analyze(api_key, video_file, max_scenes, threshold, min_scene_len, use_adaptive):
    client = OpenAI(api_key=api_key)
    init_temp_dir()

    video_path = os.path.join(TEMP_DIR, "input_video.mp4")
    try:
        with open(video_path, "wb") as f:
            f.write(video_file.read())
    except Exception as e:
        st.error(f"ファイル保存エラー: {e}")
        return []

    st.info("✂️ シーン検出中...")
    
    try:
        scenes = detect_scenes(video_path, threshold, min_scene_len, use_adaptive)
    except Exception as e:
        st.error(f"シーン検出失敗: {e}")
        return []

    st.write(f"合計 **{len(scenes)}** カット検出。ベストショット選抜を開始します...")
    
    if len(scenes) > max_scenes:
        st.warning(f"⚠️ デモ制限: 最初の {max_scenes} カットのみ処理します。")
        scenes = scenes[:max_scenes]

    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    full_clip = VideoFileClip(video_path)

    for i, scene in enumerate(scenes):
        start_t = scene[0].get_seconds()
        end_t = scene[1].get_seconds()
        duration = end_t - start_t
        
        status_text.text(f"分析中: カット {i+1}/{len(scenes)} (ベストフレーム探索中...)")
        
        thumb_filename = f"cut_{i+1:03}.jpg"
        thumb_path = os.path.join(TEMP_DIR, thumb_filename)
        
        # --- 改良点: ベストショット機能 ---
        try:
            save_best_frame(full_clip, start_t, end_t, thumb_path)
        except Exception as e:
            st.warning(f"フレーム保存エラー(skip): {e}")
            continue
        # -----------------------------

        # 音声処理
        audio_path = os.path.join(TEMP_DIR, f"audio_{i}.mp3")
        sub_clip = full_clip.subclip(start_t, end_t)
        transcript_text = "（なし）"

        if sub_clip.audio is not None:
            try:
                sub_clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
                with open(audio_path, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1", file=audio_file, language="ja"
                    )
                transcript_text = transcription.text if transcription.text else "（なし）"
            except RateLimitError:
                transcript_text = "❌ Error: 残高不足"
            except Exception:
                transcript_text = "（音声エラー）"

        # GPT-4o
        base64_image = encode_image(thumb_path)
        prompt = f"文字起こし:「{transcript_text}」。このカットの状況と意図を簡潔に要約して。"
        
        analysis = ""
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}
                ],
                max_tokens=200
            )
            analysis = response.choices[0].message.content
        except RateLimitError:
            analysis = "❌ Error: クレジット残高不足"
            st.error("⚠️ OpenAIの利用枠超過 (429) です。")
        except Exception as e:
            analysis = f"エラー: {e}"

        results.append({
            "カットNo": i+1,
            "開始": scene[0].get_timecode(),
            "終了": scene[1].get_timecode(),
            "サムネイルパス": thumb_path,
            "セリフ": transcript_text,
            "AI分析": analysis
        })
        progress_bar.progress((i + 1) / len(scenes))

    full_clip.close()
    status_text.text("完了！")
    return results

# --- UI ---
st.set_page_config(page_title="AIカット表メーカー BestShot", layout="wide")
st.title("🎬 AI映像カット表メーカー (ベストショット版)")

with st.sidebar:
    api_key = st.text_input("OpenAI API Key", type="password")
    
    st.divider()
    st.header("検出設定")
    use_adaptive = st.checkbox("Adaptiveモードを使う", value=False)
    threshold = st.slider("感度 (Threshold)", 10.0, 60.0, 27.0)
    min_scene_len = st.number_input("最小カット長 (フレーム)", value=15, min_value=1)
    max_scenes_limit = st.number_input("最大分析数", 5, 100, 10)

uploaded_file = st.file_uploader("動画 (MP4)", type=['mp4', 'mov'])

if uploaded_file and api_key:
    if st.button("🚀 分析スタート"):
        data = process_video_and_analyze(
            api_key, 
            uploaded_file, 
            max_scenes_limit,
            threshold,
            min_scene_len,
            use_adaptive
        )
        
        if data:
            st.success("分析完了！")
            
            zip_bytes = create_zip_file(data)
            st.download_button(
                label="📦 結果を一括ダウンロード (CSV+画像)",
                data=zip_bytes,
                file_name="cut_analysis_best.zip",
                mime="application/zip"
            )

            for row in data:
                col1, col2, col3 = st.columns([2, 2, 4])
                with col1:
                    st.image(row["サムネイルパス"])
                    st.caption(f"{row['開始']} - {row['終了']}")
                with col2:
                    st.write(f"🗣 {row['セリフ']}")
                with col3:
                    st.write(f"🤖 {row['AI分析']}")
                st.divider()
