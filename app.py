import streamlit as st
import os
import cv2
import base64
import pandas as pd
import shutil
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from moviepy.editor import VideoFileClip
from openai import OpenAI

# --- 設定 ---
TEMP_DIR = "temp_data"  # 一時ファイルを保存するフォルダ

def init_temp_dir():
    """一時フォルダを作成"""
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def clear_temp_dir():
    """一時フォルダをリセット"""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR)

def encode_image(image_path):
    """画像をBase64エンコードしてGPTに送れるようにする"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def detect_scenes(video_path, threshold=27.0):
    """シーンの切り替わり時間を検出"""
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list(video_manager)
    return scene_list

def process_video_and_analyze(api_key, video_file, max_scenes=10):
    """動画処理のメインロジック"""
    # OpenAIクライアントの初期化
    client = OpenAI(api_key=api_key)
    
    # 一時フォルダの準備
    clear_temp_dir()

    # 動画を一時保存
    video_path = os.path.join(TEMP_DIR, "input_video.mp4")
    with open(video_path, "wb") as f:
        f.write(video_file.read())

    st.info("✂️ シーン（カット）の検出中... 動画の長さによっては時間がかかります。")
    
    # シーン検出実行
    try:
        scenes = detect_scenes(video_path)
    except Exception as e:
        st.error(f"シーン検出エラー: {e}")
        return []

    st.write(f"合計 **{len(scenes)}** 個のカットを検出しました。")

    if len(scenes) > max_scenes:
        st.warning(f"⚠️ デモのため、最初の {max_scenes} カットのみ分析します。")
        scenes = scenes[:max_scenes]

    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    # 動画クリップの読み込み
    full_clip = VideoFileClip(video_path)

    for i, scene in enumerate(scenes):
        start_t = scene[0].get_seconds()
        end_t = scene[1].get_seconds()
        duration = end_t - start_t
        
        # 極端に短いカット（0.5秒未満）はスキップ
        if duration < 0.5:
            continue

        status_text.text(f"分析中: カット {i+1} / {len(scenes)}")
        
        # --- 1. サムネイル画像の保存 ---
        thumb_path = os.path.join(TEMP_DIR, f"thumb_{i}.jpg")
        # カットの中間地点の時間を計算
        mid_point = start_t + (duration / 2)
        # フレームを保存
        full_clip.save_frame(thumb_path, t=mid_point)

        # --- 2. 音声の切り出しと文字起こし ---
        audio_path = os.path.join(TEMP_DIR, f"audio_{i}.mp3")
        sub_clip = full_clip.subclip(start_t, end_t)
        
        transcript_text = "（なし）"
        
        # 音声データがある場合のみ処理
        if sub_clip.audio is not None:
            try:
                # 音声ファイルを書き出し
                sub_clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
                
                # Whisper APIで文字起こし
                with open(audio_path, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1", 
                        file=audio_file,
                        language="ja"
                    )
                transcript_text = transcription.text if transcription.text else "（なし）"
            except Exception as e:
                # 音声がない、またはエラーの場合はスルー
                transcript_text = "（音声なし/エラー）"

        # --- 3. GPT-4o (Vision) で画像とテキストを分析 ---
        base64_image = encode_image(thumb_path)
        
        prompt = f"""
        これは動画の1カットです。
        音声の文字起こし: 「{transcript_text}」
        
        以下のフォーマットで簡潔に答えてください：
        【状況】: 画像から読み取れる視覚的な状況（誰が、どこで、何をしているか）
        【意図】: セリフと画像を合わせて、このシーンが何を伝えているか
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            analysis = response.choices[0].message.content
        except Exception as e:
            analysis = f"AI分析エラー: {e}"

        # 結果をリストに追加
        results.append({
            "カットNo": i+1,
            "開始": scene[0].get_timecode(),
            "終了": scene[1].get_timecode(),
            "サムネイルパス": thumb_path,
            "セリフ": transcript_text,
            "AI分析": analysis
        })
        
        # プログレスバー更新
        progress_bar.progress((i + 1) / len(scenes))

    full_clip.close()
    status_text.text("分析完了！")
    return results

# --- Streamlit UI ---
st.set_page_config(page_title="AIカット表メーカー", layout="wide")
st.title("🎬 AI映像カット表メーカー")
st.markdown("映像をアップロードすると、**カット割り・文字起こし・内容分析**を全自動で行います。")

# サイドバー設定
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.caption("※GPT-4oを使用するためAPIキーが必要です。")
    
    threshold = st.slider("カット検出感度", 10.0, 60.0, 27.0)
    st.caption("値が小さいほど敏感にカットを検出します。")
    
    max_scenes_limit = st.number_input("最大分析カット数", value=5, min_value=1, max_value=50)

uploaded_file = st.file_uploader("動画ファイル (MP4, MOV)", type=['mp4', 'mov'])

if uploaded_file and api_key:
    if st.button("🚀 分析スタート"):
        try:
            data = process_video_and_analyze(api_key, uploaded_file, max_scenes=max_scenes_limit)
            
            # --- 結果表示 ---
            st.divider()
            st.subheader("📋 分析結果")

            if data:
                # ダウンロード用データ作成（画像パスは除外）
                df_export = pd.DataFrame(data)
                csv = df_export.drop(columns=["サムネイルパス"]).to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="💾 CSVデータをダウンロード",
                    data=csv,
                    file_name='cut_list.csv',
                    mime='text/csv',
                )

                # ビジュアル表示
                for row in data:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 2, 4])
                        
                        with col1:
                            # 画像を表示
                            if os.path.exists(row["サムネイルパス"]):
                                st.image(row["サムネイルパス"], use_column_width=True)
                            st.caption(f"{row['開始']} 〜 {row['終了']}")
                        
                        with col2:
                            st.markdown("**🗣️ セリフ / 音声**")
                            st.info(row["セリフ"])
                        
                        with col3:
                            st.markdown("**🤖 AI分析 (視覚+聴覚)**")
                            st.write(row["AI分析"])
                        
                        st.divider()
            else:
                st.warning("シーンが検出されませんでした。感度（threshold）を調整してみてください。")

        except Exception as e:
            st.error(f"予期せぬエラーが発生しました: {e}")
            st.warning("ヒント: 大きすぎる動画ファイルはメモリ不足になることがあります。短い動画で試してください。")

elif uploaded_file and not api_key:
    st.warning("👈 左のサイドバーにOpenAI APIキーを入力してください。")
