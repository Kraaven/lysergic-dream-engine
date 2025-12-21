import subprocess
import random
import os

def create_video(audio_path, srt_path, output_path):
    bg_video = f"clips/{random.choice(os.listdir('clips'))}"
    bg_music = f"music/{random.choice(os.listdir('music'))}"
    
    # We use -vf "subtitles=..." to burn text into the 720p 16:9 frame
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", bg_video,
        "-i", audio_path,
        "-stream_loop", "-1", "-i", bg_music,
        "-filter_complex", 
        f"[0:v]scale=1280:720,setdar=16/9,subtitles={srt_path}:force_style='Alignment=2,FontSize=20'[v];"
        "[2:a]volume=0.08[bg];[1:a][bg]amix=inputs=2:duration=first[a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-shortest",
        output_path
    ]
    subprocess.run(cmd, check=True)