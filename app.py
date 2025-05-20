import streamlit as st
from yt_dlp import YoutubeDL
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.settings import LoadSettingsFile

# Google Drive yetkilendirme (service account ile)
def gdrive_login():
    gauth = GoogleAuth(settings_file="settings.yaml")
    gauth.ServiceAuth()
    return GoogleDrive(gauth)

# Drive'a yükleme
def save_to_drive(audio_file):
    folder_id = "1qAMA1St9zPeCfjpcs10ielVBwfjnOnFz" 
    drive = gdrive_login()
    file = drive.CreateFile({
        'title': os.path.basename(audio_file),
        'parents': [{'id': folder_id}]
    })
    file.SetContentFile(audio_file)
    file.Upload()

# M4A indirici (ffmpeg gerekmez)
def download_m4a(youtube_url):
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio',
        'outtmpl': 'downloaded_audio.%(ext)s',
        'postprocessors': [],  # no ffmpeg
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    return 'downloaded_audio.m4a'

# Streamlit arayüzü
st.title("YouTube Audio Downloader 🎧")
url = st.text_input("YouTube URL")

if st.button("Download and Save to Drive"):
    if url:
        with st.spinner("Downloading audio..."):
            audio_file = download_m4a(url)
        with st.spinner("Uploading to Google Drive..."):
            save_to_drive(audio_file)
        st.success("All done! Check your Drive folder.")
