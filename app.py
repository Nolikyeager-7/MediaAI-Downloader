import streamlit as st
import os
import yt_dlp

st.set_page_config(page_title="MediaAI Clip Downloader", page_icon="🎬", layout="centered")

st.title("🎬 MediaAI - YouTube Clip Downloader")
st.write("Cut and extract any video or audio clip online!")

video_url = st.text_input("Paste YouTube URL:", "")

col1, col2 = st.columns(2)
with col1:
    start_time = st.text_input("Start Time (HH:MM:SS):", "00:01:50")
with col2:
    end_time = st.text_input("End Time (HH:MM:SS):", "00:01:54")

mode = st.radio("Select Format:", ["audio", "video"], horizontal=True)
output_name = st.text_input("Output File Name:", "MyClip")

if st.button("🚀 Download Clip"):
    if not video_url:
        st.error("Please enter a valid YouTube URL!")
    else:
        st.info("Downloading clip... Please wait!")
        
        # Standardize output filename
        ext = "m4a" if mode == "audio" else "mp4"
        output_file = f"{output_name}.{ext}"

        if os.path.exists(output_file):
            os.remove(output_file)

        # Time string to seconds helper
        def to_seconds(t_str):
            parts = list(map(int, t_str.split(':')))
            if len(parts) == 3:
                return parts[0] * 3600 + parts[1] * 60 + parts[2]
            elif len(parts) == 2:
                return parts[0] * 60 + parts[1]
            return parts[0]

        try:
            start_sec = to_seconds(start_time)
            end_sec = to_seconds(end_time)

            ydl_opts = {
                'format': 'best' if mode == 'video' else 'bestaudio/best',
                'outtmpl': output_file,
                'download_ranges': yt_dlp.utils.download_range_func(None, [(start_sec, end_sec)]),
                'force_keyframes_at_cuts': True,
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'quiet': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            if os.path.exists(output_file):
                st.success("Clip ready!")
                with open(output_file, "rb") as file:
                    st.download_button(
                        label="📥 Download to Device",
                        data=file,
                        file_name=output_file,
                        mime="audio/mp4" if mode == "audio" else "video/mp4"
                    )
            else:
                st.error("Could not process video clip. Please check the URL/timestamps.")

        except Exception as e:
            st.error(f"Error: {e}")