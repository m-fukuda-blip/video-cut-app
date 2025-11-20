{\rtf1\ansi\ansicpg932\cocoartf2821
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\froman\fcharset0 Times-Roman;\f1\fnil\fcharset128 HiraMinProN-W3;\f2\fnil\fcharset0 AppleColorEmoji;
}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;}
\paperw11900\paperh16840\margl1440\margr1440\vieww21000\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\qj\partightenfactor0

\f0\fs28 \cf2 \expnd0\expndtw0\kerning0
import streamlit as st
\f1 \

\f0 import os
\f1 \

\f0 import cv2
\f1 \

\f0 import base64
\f1 \

\f0 import pandas as pd
\f1 \

\f0 import shutil
\f1 \

\f0 from scenedetect import VideoManager, SceneManager
\f1 \

\f0 from scenedetect.detectors import ContentDetector
\f1 \

\f0 from moviepy.editor import VideoFileClip
\f1 \

\f0 from openai import OpenAI
\f1 \

\f0 \'a0
\f1 \

\f0 # --- 
\f1 \'90\'dd\'92\'e8
\f0  ---
\f1 \

\f0 TEMP_DIR = "temp_data"\'a0 # 
\f1 \'88\'ea\'8e\'9e\'83\'74\'83\'40\'83\'43\'83\'8b\'82\'f0\'95\'db\'91\'b6\'82\'b7\'82\'e9\'83\'74\'83\'48\'83\'8b\'83\'5f\

\f0 \'a0
\f1 \

\f0 def init_temp_dir():
\f1 \

\f0 \'a0\'a0\'a0 if not os.path.exists(TEMP_DIR):
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 os.makedirs(TEMP_DIR)
\f1 \

\f0 \'a0
\f1 \

\f0 def clear_temp_dir():
\f1 \

\f0 \'a0\'a0\'a0 if os.path.exists(TEMP_DIR):
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 shutil.rmtree(TEMP_DIR)
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 os.makedirs(TEMP_DIR)
\f1 \

\f0 \'a0
\f1 \

\f0 def encode_image(image_path):
\f1 \

\f0 \'a0\'a0\'a0 """
\f1 \'89\'e6\'91\'9c\'82\'f0
\f0 Base64
\f1 \'83\'47\'83\'93\'83\'52\'81\'5b\'83\'68\'82\'b5\'82\'c4
\f0 GPT
\f1 \'82\'c9\'91\'97\'82\'ea\'82\'e9\'82\'e6\'82\'a4\'82\'c9\'82\'b7\'82\'e9
\f0 """
\f1 \

\f0 \'a0\'a0\'a0 with open(image_path, "rb") as image_file:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 return base64.b64encode(image_file.read()).decode('utf-8')
\f1 \

\f0 \'a0
\f1 \

\f0 def detect_scenes(video_path, threshold=27.0):
\f1 \

\f0 \'a0\'a0\'a0 """
\f1 \'83\'56\'81\'5b\'83\'93\'82\'cc\'90\'d8\'82\'e8\'91\'d6\'82\'ed\'82\'e8\'8e\'9e\'8a\'d4\'82\'f0\'8c\'9f\'8f\'6f
\f0 """
\f1 \

\f0 \'a0\'a0\'a0 video_manager = VideoManager([video_path])
\f1 \

\f0 \'a0\'a0\'a0 scene_manager = SceneManager()
\f1 \

\f0 \'a0\'a0\'a0 scene_manager.add_detector(ContentDetector(threshold=threshold))
\f1 \

\f0 \'a0\'a0\'a0 video_manager.start()
\f1 \

\f0 \'a0\'a0\'a0 scene_manager.detect_scenes(frame_source=video_manager)
\f1 \

\f0 \'a0\'a0\'a0 scene_list = scene_manager.get_scene_list(video_manager)
\f1 \

\f0 \'a0\'a0\'a0 return scene_list
\f1 \

\f0 \'a0
\f1 \

\f0 def process_video_and_analyze(api_key, video_file, max_scenes=10):
\f1 \

\f0 \'a0\'a0\'a0 """
\f1 \'93\'ae\'89\'e6\'8f\'88\'97\'9d\'82\'cc\'83\'81\'83\'43\'83\'93\'83\'8d\'83\'57\'83\'62\'83\'4e
\f0 """
\f1 \

\f0 \'a0\'a0\'a0 client = OpenAI(api_key=api_key)
\f1 \

\f0 \'a0\'a0\'a0 init_temp_dir()
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0 # 
\f1 \'93\'ae\'89\'e6\'82\'f0\'88\'ea\'8e\'9e\'95\'db\'91\'b6\

\f0 \'a0\'a0\'a0 video_path = os.path.join(TEMP_DIR, "input_video.mp4")
\f1 \

\f0 \'a0\'a0\'a0 with open(video_path, "wb") as f:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 f.write(video_file.read())
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0 st.info("\uc0\u9986 \u65039  
\f1 \'83\'56\'81\'5b\'83\'93\'81\'69\'83\'4a\'83\'62\'83\'67\'81\'6a\'82\'cc\'8c\'9f\'8f\'6f\'92\'86
\f0 ... 
\f1 \'93\'ae\'89\'e6\'82\'cc\'92\'b7\'82\'b3\'82\'c9\'82\'e6\'82\'c1\'82\'c4\'82\'cd\'8e\'9e\'8a\'d4\'82\'aa\'82\'a9\'82\'a9\'82\'e8\'82\'dc\'82\'b7\'81\'42
\f0 ")
\f1 \

\f0 \'a0\'a0\'a0 scenes = detect_scenes(video_path)
\f1 \

\f0 \'a0\'a0\'a0 st.write(f"
\f1 \'8d\'87\'8c\'76
\f0  **\{len(scenes)\}** 
\f1 \'8c\'c2\'82\'cc\'83\'4a\'83\'62\'83\'67\'82\'f0\'8c\'9f\'8f\'6f\'82\'b5\'82\'dc\'82\'b5\'82\'bd\'81\'42
\f0 ")
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0 if len(scenes) > max_scenes:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 st.warning(f"\uc0\u9888 \u65039  
\f1 \'83\'66\'83\'82\'82\'cc\'82\'bd\'82\'df\'81\'41\'8d\'c5\'8f\'89\'82\'cc
\f0  \{max_scenes\} 
\f1 \'83\'4a\'83\'62\'83\'67\'82\'cc\'82\'dd\'95\'aa\'90\'cd\'82\'b5\'82\'dc\'82\'b7\'81\'42\'81\'69\'91\'53\'83\'4a\'83\'62\'83\'67\'95\'aa\'90\'cd\'82\'cd\'83\'52\'81\'5b\'83\'68\'93\'e0\'82\'cc
\f0  max_scenes 
\f1 \'82\'f0\'95\'cf\'8d\'58\'82\'b5\'82\'c4\'82\'ad\'82\'be\'82\'b3\'82\'a2\'81\'6a
\f0 ")
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 scenes = scenes[:max_scenes]
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0 results = []
\f1 \

\f0 \'a0\'a0\'a0 progress_bar = st.progress(0)
\f1 \

\f0 \'a0\'a0\'a0 status_text = st.empty()
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0 full_clip = VideoFileClip(video_path)
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0 for i, scene in enumerate(scenes):
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 start_t = scene[0].get_seconds()
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 end_t = scene[1].get_seconds()
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 duration = end_t - start_t
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 # 
\f1 \'92\'5a\'82\'b7\'82\'ac\'82\'e9\'83\'4a\'83\'62\'83\'67\'82\'cd\'83\'58\'83\'4c\'83\'62\'83\'76\'81\'69\'83\'6d\'83\'43\'83\'59\'91\'ce\'8d\'f4\'81\'6a\

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 if duration < 0.5:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 continue
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 status_text.text(f"
\f1 \'95\'aa\'90\'cd\'92\'86
\f0 : 
\f1 \'83\'4a\'83\'62\'83\'67
\f0  \{i+1\} / \{len(scenes)\}")
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 # 1. 
\f1 \'83\'54\'83\'80\'83\'6c\'83\'43\'83\'8b\'89\'e6\'91\'9c\'82\'cc\'95\'db\'91\'b6\

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 thumb_path = os.path.join(TEMP_DIR, f"thumb_\{i\}.jpg")
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 mid_point = start_t + (duration / 2)
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 full_clip.save_frame(thumb_path, t=mid_point)
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 # 2. 
\f1 \'89\'b9\'90\'ba\'82\'cc\'90\'d8\'82\'e8\'8f\'6f\'82\'b5\

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 audio_path = os.path.join(TEMP_DIR, f"audio_\{i\}.mp3")
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 sub_clip = full_clip.subclip(start_t, end_t)
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 transcript_text = "
\f1 \'81\'69\'82\'c8\'82\'b5\'81\'6a
\f0 "
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 # 
\f1 \'89\'b9\'90\'ba\'82\'aa\'82\'a0\'82\'e9\'8f\'ea\'8d\'87\'82\'cc\'82\'dd\'8f\'88\'97\'9d\

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 if sub_clip.audio is not None:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 try:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 sub_clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 # Whisper
\f1 \'82\'c5\'95\'b6\'8e\'9a\'8b\'4e\'82\'b1\'82\'b5\

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 with open(audio_path, "rb") as audio_file:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 transcription = client.audio.transcriptions.create(
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 model="whisper-1", 
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 file=audio_file,
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 language="ja"
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 )
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 transcript_text = transcription.text if transcription.text else "
\f1 \'81\'69\'82\'c8\'82\'b5\'81\'6a
\f0 "
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 except Exception as e:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 print(f"Audio Error: \{e\}")
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 transcript_text = "
\f1 \'81\'69\'89\'b9\'90\'ba\'8f\'88\'97\'9d\'83\'47\'83\'89\'81\'5b\'81\'6a
\f0 "
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 # 3. GPT-4o (Vision) 
\f1 \'82\'c5\'89\'e6\'91\'9c\'82\'c6\'83\'65\'83\'4c\'83\'58\'83\'67\'82\'f0\'95\'aa\'90\'cd\

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 base64_image = encode_image(thumb_path)
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 prompt = f"""
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \'82\'b1\'82\'ea\'82\'cd\'93\'ae\'89\'e6\'82\'cc
\f0 1
\f1 \'83\'4a\'83\'62\'83\'67\'82\'c5\'82\'b7\'81\'42\

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \'89\'b9\'90\'ba\'82\'cc\'95\'b6\'8e\'9a\'8b\'4e\'82\'b1\'82\'b5
\f0 : 
\f1 \'81\'75
\f0 \{transcript_text\}
\f1 \'81\'76\

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \'88\'c8\'89\'ba\'82\'cc\'83\'74\'83\'48\'81\'5b\'83\'7d\'83\'62\'83\'67\'82\'c5\'8a\'c8\'8c\'89\'82\'c9\'93\'9a\'82\'a6\'82\'c4\'82\'ad\'82\'be\'82\'b3\'82\'a2\'81\'46\

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \'81\'79\'8f\'f3\'8b\'b5\'81\'7a
\f0 : 
\f1 \'89\'e6\'91\'9c\'82\'a9\'82\'e7\'93\'c7\'82\'dd\'8e\'e6\'82\'ea\'82\'e9\'8e\'8b\'8a\'6f\'93\'49\'82\'c8\'8f\'f3\'8b\'b5\'81\'69\'92\'4e\'82\'aa\'81\'41\'82\'c7\'82\'b1\'82\'c5\'81\'41\'89\'bd\'82\'f0\'82\'b5\'82\'c4\'82\'a2\'82\'e9\'82\'a9\'81\'6a\

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \'81\'79\'88\'d3\'90\'7d\'81\'7a
\f0 : 
\f1 \'83\'5a\'83\'8a\'83\'74\'82\'c6\'89\'e6\'91\'9c\'82\'f0\'8d\'87\'82\'ed\'82\'b9\'82\'c4\'81\'41\'82\'b1\'82\'cc\'83\'56\'81\'5b\'83\'93\'82\'aa\'89\'bd\'82\'f0\'93\'60\'82\'a6\'82\'c4\'82\'a2\'82\'e9\'82\'a9\

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 """
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 try:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 response = client.chat.completions.create(
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 model="gpt-4o",
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 messages=[
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 \{
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 "role": "user",
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 "content": [
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 \{"type": "text", "text": prompt\},
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 \{
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 "type": "image_url",
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 "image_url": \{
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 "url": f"data:image/jpeg;base64,\{base64_image\}"
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 \}
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 \}
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 ]
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 \}
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 ],
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 max_tokens=300
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 )
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 analysis = response.choices[0].message.content
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 except Exception as e:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 analysis = f"AI
\f1 \'95\'aa\'90\'cd\'83\'47\'83\'89\'81\'5b
\f0 : \{e\}"
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 results.append(\{
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 "
\f1 \'83\'4a\'83\'62\'83\'67
\f0 No": i+1,
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 "
\f1 \'8a\'4a\'8e\'6e
\f0 ": scene[0].get_timecode(),
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 "
\f1 \'8f\'49\'97\'b9
\f0 ": scene[1].get_timecode(),
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 "
\f1 \'83\'54\'83\'80\'83\'6c\'83\'43\'83\'8b\'83\'70\'83\'58
\f0 ": thumb_path,
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 "
\f1 \'83\'5a\'83\'8a\'83\'74
\f0 ": transcript_text,
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 "AI
\f1 \'95\'aa\'90\'cd
\f0 ": analysis
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 \})
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 progress_bar.progress((i + 1) / len(scenes))
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0 full_clip.close()
\f1 \

\f0 \'a0\'a0\'a0 status_text.text("
\f1 \'95\'aa\'90\'cd\'8a\'ae\'97\'b9\'81\'49
\f0 ")
\f1 \

\f0 \'a0\'a0\'a0 return results
\f1 \

\f0 \'a0
\f1 \

\f0 # --- Streamlit UI ---
\f1 \

\f0 st.set_page_config(page_title="AI
\f1 \'83\'4a\'83\'62\'83\'67\'95\'5c\'83\'81\'81\'5b\'83\'4a\'81\'5b
\f0 ", layout="wide")
\f1 \

\f0 st.title("
\f2 \uc0\u55356 \u57260 
\f0  AI
\f1 \'89\'66\'91\'9c\'83\'4a\'83\'62\'83\'67\'95\'5c\'83\'81\'81\'5b\'83\'4a\'81\'5b
\f0 ")
\f1 \

\f0 st.markdown("
\f1 \'89\'66\'91\'9c\'82\'f0\'83\'41\'83\'62\'83\'76\'83\'8d\'81\'5b\'83\'68\'82\'b7\'82\'e9\'82\'c6\'81\'41
\f0 **
\f1 \'83\'4a\'83\'62\'83\'67\'8a\'84\'82\'e8\'81\'45\'95\'b6\'8e\'9a\'8b\'4e\'82\'b1\'82\'b5\'81\'45\'93\'e0\'97\'65\'95\'aa\'90\'cd
\f0 **
\f1 \'82\'f0\'91\'53\'8e\'a9\'93\'ae\'82\'c5\'8d\'73\'82\'a2\'82\'dc\'82\'b7\'81\'42
\f0 ")
\f1 \

\f0 \'a0
\f1 \

\f0 # 
\f1 \'83\'54\'83\'43\'83\'68\'83\'6f\'81\'5b\'90\'dd\'92\'e8\

\f0 with st.sidebar:
\f1 \

\f0 \'a0\'a0\'a0 st.header("
\f1 \'90\'dd\'92\'e8
\f0 ")
\f1 \

\f0 \'a0\'a0\'a0 api_key = st.text_input("OpenAI API Key", type="password")
\f1 \

\f0 \'a0\'a0\'a0 st.caption("\uc0\u8251 GPT-4o
\f1 \'82\'f0\'8e\'67\'97\'70\'82\'b7\'82\'e9\'82\'bd\'82\'df
\f0 API
\f1 \'83\'4c\'81\'5b\'82\'aa\'95\'4b\'97\'76\'82\'c5\'82\'b7\'81\'42
\f0 ")
\f1 \

\f0 \'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0 threshold = st.slider("
\f1 \'83\'4a\'83\'62\'83\'67\'8c\'9f\'8f\'6f\'8a\'b4\'93\'78
\f0 ", 10.0, 60.0, 27.0)
\f1 \

\f0 \'a0\'a0\'a0 st.caption("
\f1 \'92\'6c\'82\'aa\'8f\'ac\'82\'b3\'82\'a2\'82\'d9\'82\'c7\'95\'71\'8a\'b4\'82\'c9\'83\'4a\'83\'62\'83\'67\'82\'f0\'8c\'9f\'8f\'6f\'82\'b5\'82\'dc\'82\'b7\'81\'42
\f0 ")
\f1 \

\f0 \'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0 max_scenes_limit = st.number_input("
\f1 \'8d\'c5\'91\'e5\'95\'aa\'90\'cd\'83\'4a\'83\'62\'83\'67\'90\'94\'81\'69\'8e\'8e\'97\'70\'90\'a7\'8c\'c0\'81\'6a
\f0 ", value=5, min_value=1)
\f1 \

\f0 \'a0
\f1 \

\f0 uploaded_file = st.file_uploader("
\f1 \'93\'ae\'89\'e6\'83\'74\'83\'40\'83\'43\'83\'8b
\f0  (MP4, MOV)", type=['mp4', 'mov'])
\f1 \

\f0 \'a0
\f1 \

\f0 if uploaded_file and api_key:
\f1 \

\f0 \'a0\'a0\'a0 if st.button("
\f2 \uc0\u55357 \u56960 
\f0  
\f1 \'95\'aa\'90\'cd\'83\'58\'83\'5e\'81\'5b\'83\'67
\f0 "):
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 try:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 data = process_video_and_analyze(api_key, uploaded_file, max_scenes=max_scenes_limit)
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 # --- 
\f1 \'8c\'8b\'89\'ca\'95\'5c\'8e\'a6
\f0  ---
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 st.divider()
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 st.subheader("
\f2 \uc0\u55357 \u56523 
\f0  
\f1 \'95\'aa\'90\'cd\'8c\'8b\'89\'ca
\f0 ")
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 # DataFrame
\f1 \'8d\'ec\'90\'ac\'81\'69\'83\'5f\'83\'45\'83\'93\'83\'8d\'81\'5b\'83\'68\'97\'70\'81\'6a\

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 df_export = pd.DataFrame(data)
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 # 
\f1 \'89\'e6\'91\'9c\'83\'70\'83\'58\'82\'cd
\f0 CSV
\f1 \'82\'c9\'8a\'dc\'82\'df\'82\'c4\'82\'e0\'88\'d3\'96\'a1\'82\'aa\'82\'c8\'82\'a2\'82\'cc\'82\'c5\'8f\'9c\'8a\'4f\'82\'b7\'82\'e9\'82\'a9\'83\'70\'83\'58\'82\'c6\'82\'b5\'82\'c4\'8e\'63\'82\'b7\

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 csv = df_export.drop(columns=["
\f1 \'83\'54\'83\'80\'83\'6c\'83\'43\'83\'8b\'83\'70\'83\'58
\f0 "]).to_csv(index=False).encode('utf-8')
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 st.download_button(
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 label="
\f2 \uc0\u55357 \u56510 
\f0  CSV
\f1 \'83\'66\'81\'5b\'83\'5e\'81\'69
\f0 Excel
\f1 \'97\'70\'81\'6a\'82\'f0\'83\'5f\'83\'45\'83\'93\'83\'8d\'81\'5b\'83\'68
\f0 ",
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 data=csv,
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 file_name='cut_list.csv',
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 mime='text/csv',
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 )
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 # 
\f1 \'83\'72\'83\'57\'83\'85\'83\'41\'83\'8b\'95\'5c\'8e\'a6\

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 for row in data:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 with st.container():
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 col1, col2, col3 = st.columns([2, 2, 4])
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 with col1:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 st.image(row["
\f1 \'83\'54\'83\'80\'83\'6c\'83\'43\'83\'8b\'83\'70\'83\'58
\f0 "], use_container_width=True)
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 st.caption(f"\{row['
\f1 \'8a\'4a\'8e\'6e
\f0 ']\} 
\f1 \'81\'60
\f0  \{row['
\f1 \'8f\'49\'97\'b9
\f0 ']\}")
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 with col2:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 st.markdown("**
\f2 \uc0\u55357 \u56803 \u65039 
\f0  
\f1 \'83\'5a\'83\'8a\'83\'74
\f0  / 
\f1 \'89\'b9\'90\'ba
\f0 **")
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 st.info(row["
\f1 \'83\'5a\'83\'8a\'83\'74
\f0 "])
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 with col3:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 st.markdown("**
\f2 \uc0\u55358 \u56598 
\f0  AI
\f1 \'95\'aa\'90\'cd
\f0  (
\f1 \'8e\'8b\'8a\'6f
\f0 +
\f1 \'92\'ae\'8a\'6f
\f0 )**")
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 st.write(row["AI
\f1 \'95\'aa\'90\'cd
\f0 "])
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 st.divider()
\f1 \

\f0 \'a0
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 except Exception as e:
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 st.error(f"
\f1 \'83\'47\'83\'89\'81\'5b\'82\'aa\'94\'ad\'90\'b6\'82\'b5\'82\'dc\'82\'b5\'82\'bd
\f0 : \{e\}")
\f1 \

\f0 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 st.warning("
\f1 \'83\'71\'83\'93\'83\'67
\f0 : 
\f1 \'93\'ae\'89\'e6\'83\'74\'83\'40\'83\'43\'83\'8b\'82\'aa\'89\'f3\'82\'ea\'82\'c4\'82\'a2\'82\'e9\'82\'a9\'81\'41
\f0 ffmpeg
\f1 \'82\'aa\'83\'43\'83\'93\'83\'58\'83\'67\'81\'5b\'83\'8b\'82\'b3\'82\'ea\'82\'c4\'82\'a2\'82\'c8\'82\'a2\'89\'c2\'94\'5c\'90\'ab\'82\'aa\'82\'a0\'82\'e8\'82\'dc\'82\'b7\'81\'42
\f0 ")
\f1 \

\f0 \'a0
\f1 \

\f0 elif uploaded_file and not api_key:
\f1 \

\f0 \'a0\'a0\'a0 st.warning("
\f2 \uc0\u55357 \u56392 
\f0  
\f1 \'8d\'b6\'82\'cc\'83\'54\'83\'43\'83\'68\'83\'6f\'81\'5b\'82\'c9
\f0 OpenAI API
\f1 \'83\'4c\'81\'5b\'82\'f0\'93\'fc\'97\'cd\'82\'b5\'82\'c4\'82\'ad\'82\'be\'82\'b3\'82\'a2\'81\'42
\f0 ")
\f1 \
}