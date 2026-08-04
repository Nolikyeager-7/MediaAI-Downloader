import streamlit as st
import os
import re
import subprocess
import yt_dlp

st.set_page_config(page_title="MediaAI Clip Downloader", page_icon="🎬", layout="centered")

st.title("🎬 MediaAI - YouTube Clip Downloader")
st.write("Cut and extract any video or audio clip online!")

video_url = st.text_input("Paste YouTube URL:", "")

col1, col2 = st.columns(2)
with col1:
    start_time = st.text_input("Start Time (HH:MM:SS):", "00:01:00")
with col2:
    end_time = st.text_input("End Time (HH:MM:SS):", "00:02:00")

mode = st.radio("Select Format:", ["audio", "video"], horizontal=True)
output_name = st.text_input("Output File Name:", "MyClip")

def clean_youtube_url(url):
    url = url.split("?si=")[0].split("&")[0]
    match = re.search(r'(?:v=|\/live\/|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})', url)
    if match:
        return f"https://www.youtube.com/watch?v={match.group(1)}"
    return url

if st.button("🚀 Download Clip"):
    if not video_url:
        st.error("Please enter a valid YouTube URL!")
    else:
        st.info("Downloading and processing clip... Please wait!")
        
        cleaned_url = clean_youtube_url(video_url)
        ext = "m4a" if mode == "audio" else "mp4"
        temp_file = f"raw_video.{ext}"
        final_file = f"{output_name}.{ext}"

        # Clean old files
        for f in [temp_file, final_file]:
            if os.path.exists(f):
                os.remove(f)

        try:
            # Flexible format & 403 Forbidden bypass
            ydl_opts = {
                'format': 'bestaudio/best' if mode == 'audio' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': temp_file,
                'nocheckcertificate': True,
                'quiet': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios', 'mweb', 'android']
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([cleaned_url])

            # Trim clip using FFmpeg
            if os.path.exists(temp_file):
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-ss", start_time,
                    "-to", end_time,
                    "-i", temp_file,
                    "-c", "copy",
                    final_file
                ]
                
                res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

                if os.path.exists(final_file):
                    st.success("🎉 Clip Ready!")
                    with open(final_file, "rb") as file:
                        st.download_button(
                            label="📥 Download to Device",
                            data=file,
                            file_name=final_file,
                            mime="audio/mp4" if mode == "audio" else "video/mp4"
                        )
                else:
                    st.error("Trimming failed. Check timestamps.")
            else:
                st.error("Failed to fetch YouTube stream.")

        except Exception as e:
            st.error(f"Error details: {e}")

        # Cleanup temporary files
        if os.path.exists(temp_file):
            os.remove(temp_file)