import streamlit as st
from yt_dlp import YoutubeDL
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
# from pydrive2.settings import LoadSettingsFile

import json
import re


def init_service():
    """Initialize Google Drive service account credentials and settings file. *_*"""
    try:
        sa = st.secrets.get("service_account")
        if not sa:
            print("Service account secret is missing or empty. *_*")
        elif not isinstance(sa, dict):
            print(f"Service account secret is not a dict: {type(sa)}. Value: {sa} *_*")
        
        if sa:
            # Ensure service-key.json is valid JSON
            with open("service-key.json", "w") as f:
                json.dump(sa, f)
    except Exception as e:
        print(f"Exception in init_service: {e} *_*")
        sa = None

    # settings.yaml her iki ortamda da mutlaka yaz:
    with open("settings.yaml", "w") as f:
        f.write(
            "client_config_backend: service\n"
            "service_config:\n"
            "  client_json_file_path: service-key.json\n"
        )


def gdrive_login():
    """Authenticate and return a GoogleDrive instance. *_*"""
    gauth = GoogleAuth(settings_file="settings.yaml")
    gauth.ServiceAuth()
    return GoogleDrive(gauth)


def sanitize_filename(title):
    """Sanitize a string to be a safe filename. *_*"""
    sanitized = re.sub(r'[\\/*?:"<>|]', "", title)
    sanitized = re.sub(r'\s+', '_', sanitized).strip('_')
    return sanitized


def download_youtube(youtube_url, download_audio=True, download_video=False):
    """Download audio and/or video from YouTube. *_*"""
    # Ortak seçenekler
    ydl_opts = {
        'quiet': True,
    }

    # Hangi formatlar indirilecek?
    formats = []
    if download_audio:
        formats.append('bestaudio[ext=m4a]/bestaudio')
    if download_video:
        formats.append('best[ext=mp4]/best')

    # İndirme çıktıları
    downloaded_files = []

    for fmt in formats:
        ext = 'm4a' if 'm4a' in fmt else 'mp4'
        filename = f'downloaded_media.{ext}'
        opts = {
            **ydl_opts,
            'format': fmt,
            'outtmpl': filename,
            'postprocessors': [],
        }
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = info.get("title", "downloaded_media")
        downloaded_files.append((filename, ext, title))

    return downloaded_files  # [(filename, ext, title), ...]


def save_to_drive(file_path, title, ext):
    """Upload a file to Google Drive in a specific folder. *_*"""
    init_service()
    folder_id = "1qAMA1St9zPeCfjpcs10ielVBwfjnOnFz"
    drive = gdrive_login()

    safe_title = sanitize_filename(title)
    drive_filename = f"{safe_title}.{ext}"

    file = drive.CreateFile({
        'title': drive_filename,
        'parents': [{'id': folder_id}]
    })
    file.SetContentFile(file_path)
    file.Upload()

    # Yüklemeden sonra yerel kopyayı sil
    try:
        file = None
        os.remove(file_path)
        st.write("Removed local file:\n")
        st.write(file_path)
    except OSError as e:
        st.warning(f"Could not delete local file {file_path}: {e}")

    return drive_filename

# Streamlit UI
st.title("Video Downloader 🎧")
url = st.text_input("Video URL")

st.markdown("Choose format to download:")
download_audio = st.checkbox("Download as M4A", value=True)
download_video = st.checkbox("Download as MP4")

if st.button("Download and Save to Drive"):
    if url and (download_audio or download_video):
        with st.spinner("Downloading.."):
            downloaded_files = download_youtube(url, download_audio, download_video)

        for file_path, ext, title in downloaded_files:
            with st.spinner(f"Uploading.. \n\n{title}.{ext} to Drive..."):
                uploaded_name = save_to_drive(file_path, title, ext)
            st.success(f"✅ Uploaded: {uploaded_name}")

    elif not (download_audio or download_video):
        st.warning("You must select at least one format to download.")
