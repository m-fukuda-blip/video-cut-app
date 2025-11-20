import streamlit as st
import os
import cv2
import base64
import pandas as pd
import shutil
import zipfile
import io
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from moviepy.editor import VideoFileClip
from openai import OpenAI, RateLimitError

# --- 設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp_data")

def init_temp_dir():
    """一時フォルダを初期化"""
    if os.path.exists(TEMP_DIR):
        try:
            shutil.rmtree(TEMP_DIR)
        except:
            pass
    os.makedirs(TEMP_DIR)

def encode_image(image_path):
    """画像をBase64エンコード"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def detect_scenes(video_path, threshold=27.0):
    """シーン検出"""
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list(video_manager)
    return scene_list

def create_zip_file(data_list):
    """CSVと画像をまとめてZIPにする"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. CSVを作成して追加
        df = pd.DataFrame(data_list)
        # CSV内では画像パスではなくファイル名だけにする
        df["サムネイルファイル名"] = df["サムネイルパス"].apply(lambda x: os.path.basename(x))
        csv_data = df.drop(columns=["サムネイルパス"]).to_csv(index=False).encode('utf-8')
        zf.writestr("cut_list.csv", csv_data)
        
        # 2. 画像ファイルを追加
        for row in data_list:
            img_path = row["サムネイルパス"]
            if os.path.exists(img_path):
                # ZIP内の images/ フォルダに入れる
                zf.write(img_path, arcname=f"images/{os.path.basename(img_path)}")
                
    return zip_buffer.getvalue()

def process_video_and_analyze(api_key, video_file, max_scenes=10):
    client = OpenAI(api_key=api_key)
    init_temp_dir()

    video_path = os.path.join(TEMP_DIR, "input_video.mp4")
    try:
        with open(video_path, "wb") as f:
            f.write(video_file.read())
    except Exception as e:
        st.error(f"ファイル保存エラー: {e}")
        return []

    st.info("✂️ シーン検出中... (数分かかる場合があります)")
    try:
        scenes = detect_scenes(video_path)
    except Exception as e:
        st.error(f"シーン検出失敗: {e}")
        return []

    st.write(f"合計 **{len(scenes)}** カット検出。")
    
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
        
        if duration < 0.5:
            continue

        status_text.text(f"AI分析中: カット {i+1}/{len(scenes)}")
        
        # 画像保存
        thumb_filename = f"cut_{i+1:03}.jpg"
        thumb_path = os.path.join(TEMP_DIR, thumb_filename)
        mid_point = start_t + (duration / 2)
        
        try:
            full_clip.save_frame(thumb_path, t=mid_point)
        except:
            continue

        # 音声処理
        audio_path = os.path.join(TEMP_DIR, f"audio_{i}.mp3")
        sub_clip = full_clip.subclip(start_t, end_t)
        transcript_text = "（なし）"

        # Whisper (音声)
        if sub_clip.audio is not None:
            try:
                sub_clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
                with open(audio_path, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1", file=audio_file, language="ja"
                    )
                transcript_text = transcription.text if transcription.text else "（なし）"
            except RateLimitError:
                transcript_text = "❌【エラー】OpenAIのクレジット残高不足です"
            except Exception as e:
                transcript_text = "（音声エラー）"

        # GPT-4o (画像)
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
            analysis = "❌【エラー】OpenAIのクレジット残高不足です。Billing設定を確認してください。"
            st.error("⚠️ OpenAIのAPI利用枠を超過しました（Error 429）。クレジットを追加してください。")
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
st.set_page_config(page_title="AIカット表メーカー", layout="wide")
st.title("🎬 AI映像カット表メーカー")

with st.sidebar:
    api_key = st.text_input("OpenAI API Key", type="password")
    st.info("💡 Error 429が出たら: OpenAIのBilling設定でクレジット残高を確認してください。")
    threshold = st.slider("カット検出感度", 10.0, 60.0, 27.0)
    max_scenes_limit = st.number_input("最大分析数", 5, 50, 5)

uploaded_file = st.file_uploader("動画 (MP4)", type=['mp4', 'mov'])

if uploaded_file and api_key:
    if st.button("🚀 分析スタート"):
        data = process_video_and_analyze(api_key, uploaded_file, max_scenes_limit)
        
        if data:
            st.success("分析完了！下のボタンからデータを一括ダウンロードできます。")
            
            # ZIPダウンロードボタン作成
            zip_bytes = create_zip_file(data)
            st.download_button(
                label="📦 結果をダウンロード (CSV + 画像ZIP)",
                data=zip_bytes,
                file_name="cut_analysis_result.zip",
                mime="application/zip"
            )

            # 画面表示
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
