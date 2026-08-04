import streamlit as st
import sys
import subprocess
import os

st.set_page_config(page_title="MediaAI Clip Downloader", page_icon="🎬", layout="centered")

st.title("🎬 MediaAI - YouTube Clip Downloader")
st.write("Cut and extract any video or audio clip online!")

video_url = st.text_input("Paste YouTube URL:", "")

col1, col2 = st.columns(2)
with col1:
    start_time = st.text_input("Start Time (HH:MM:SS):", "00:00:10")
with col2:
    end_time = st.text_input("End Time (HH:MM:SS):", "00:00:20")

mode = st.radio("Select Format:", ["audio", "video"], horizontal=True)
output_name = st.text_input("Output File Name:", "my_clip")

if st.button("🚀 Download Clip"):
    if not video_url:
        st.error("Please enter a valid YouTube URL!")
    else:
        st.info("Downloading clip... Please wait!")
        
        if mode == "audio":
            format_spec = "bestaudio[ext=m4a]/bestaudio/best"
            ext = "m4a"
            extra_args = []
        else:
            format_spec = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            ext = "mp4"
            extra_args = []

        output_file = f"{output_name}.{ext}"

        command = [
            sys.executable, "-m", "yt_dlp",
            "--download-sections", f"*{start_time}-{end_time}",
            "-f", format_spec,
            "--force-keyframes-at-cuts",
            *extra_args,
            "-o", output_file,
            video_url
        ]

        try:
            subprocess.run(command, check=True)
            st.success("Clip ready!")
            
            if os.path.exists(output_file):
                with open(output_file, "rb") as file:
                    st.download_button(
                        label="📥 Download to Device",
                        data=file,
                        file_name=output_file,
                        mime="audio/mp4" if mode == "audio" else "video/mp4"
                    )
        except Exception as e:
            st.error(f"Error: {e}")