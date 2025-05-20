import streamlit as st
from yt_dlp import YoutubeDL
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
# from pydrive2.settings import LoadSettingsFile

import json
import re


def init_service():
    # Streamlit secrets'ten oku ve geçici dosya olarak yaz
    with open("service-key.json", "w") as f:
        f.write(st.secrets["service_account"])
    
    # st.write(st.secrets["service_account"])

    # Ayar dosyasını da oluştur
    # with open("settings.yaml", "w") as f:
    #     f.write("""
    #         client_config_backend: service
    #         service_config:
    #         client_json_file_path: service-key.json
    #         """)


# Google Drive yetkilendirme (service account ile)
def gdrive_login():
    gauth = GoogleAuth(settings_file="settings.yaml")
    gauth.ServiceAuth()
    return GoogleDrive(gauth)

# Özel karakterleri temizle
def sanitize_filename(title):
    # Sadece harf, rakam, boşluk, tire ve alt çizgi kalsın
    sanitized = re.sub(r'[\\/*?:"<>|]', "", title)  # Windows için yasak karakterler
    sanitized = re.sub(r'\s+', '_', sanitized).strip('_')  # Boşlukları alt çizgi yap
    return sanitized

# M4A indirici ve başlık döndürücü
def download_m4a(youtube_url):
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio',
        'outtmpl': 'downloaded_audio.%(ext)s',
        'postprocessors': [],
        'quiet': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        title = info.get("title", "downloaded_audio")
    
    filename = 'downloaded_audio.m4a'
    return filename, title

# Google Drive'a yükle (başlığı kullanarak)
def save_to_drive(audio_file, title):
    folder_id = "1qAMA1St9zPeCfjpcs10ielVBwfjnOnFz"
    drive = gdrive_login()

    safe_title = sanitize_filename(title)
    drive_filename = f"{safe_title}.m4a"

    file = drive.CreateFile({
        'title': drive_filename,
        'parents': [{'id': folder_id}]
    })
    file.SetContentFile(audio_file)
    file.Upload()


init_service()

# Streamlit arayüzü
st.title("YouTube Audio Downloader 🎧")
url = st.text_input("YouTube URL")

if st.button("Download and Save to Drive"):
    if url:
        with st.spinner("Downloading audio..."):
            audio_file, title = download_m4a(url)
        
        message = f"""Uploading \n
                    "{title}"  
                """
        with st.spinner(message):
            save_to_drive(audio_file, title)
        st.success(f"All done! Check your Drive folder. file:{audio_file}")
