# TrailHound v3.2
import webview
import threading
import json
import requests
import subprocess
import os
from urllib.parse import urlparse, unquote

API_KEY = 'AIzaSyB_OAvzxJaC0arQbLzepinZEbhZaJryNDA'

selected_dir = None
selected_foldername = None

def tmp(query):
    return query.replace(' ', '%20')

def fetch_youtube_links(query):
    try:
        url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&maxResults=5&q={tmp(query)}&type=video&key={API_KEY}"
        )
        items = requests.get(url).json().get('items', [])
    except Exception as e:
        return {'error': str(e)}

    results = []
    for it in items:
        vid = it['id']['videoId']
        link = f"https://www.youtube.com/watch?v={vid}"
        embed = f"https://www.youtube.com/embed/{vid}"

        # Use yt-dlp to fetch duration and resolution
        duration = ""
        resolution = ""
        try:
            result = subprocess.run(
                ['yt-dlp', '--print', '%(duration_string)s\n%(height)sp', '--skip-download', link],
                capture_output=True, text=True, check=True
            )
            output_lines = result.stdout.strip().split('\n')
            if len(output_lines) >= 2:
                duration = output_lines[0].strip()
                resolution = output_lines[1].strip()
        except subprocess.CalledProcessError:
            duration = ""
            resolution = ""

        title = it['snippet']['title']
        results.append({"title": title, "url": link, "embed": embed, "duration": duration, "resolution": resolution})
    return results

def download_video(video_url, start=None, end=None):
    global selected_dir, selected_foldername
    try:
        # Determine output directory and filename
        if selected_dir and selected_foldername:
            output_dir = os.path.join(selected_dir, selected_foldername)
            safe_name = selected_foldername + '-trailer.%(ext)s'
            output = os.path.join(output_dir, safe_name)
        else:
            output = 'trailer_output.%(ext)s'

        command = ['yt-dlp', '-f', 'best', video_url, '-o', output]

        if start or end:
            section = f"*{start or ''}-{end or ''}"
            command.extend(['--download-sections', section])

        subprocess.run(command, check=True)
        return 'Download complete'
    except subprocess.CalledProcessError as e:
        return f'Download failed: {str(e)}'

def scan_media_directory(path):
    global selected_dir
    selected_dir = path

    if not os.path.isdir(path):
        return {'error': f'Not a valid directory: {path}'}

    folders = []
    for name in os.listdir(path):
        full_path = os.path.join(path, name)
        if os.path.isdir(full_path):
            base_name = os.path.basename(full_path)
            trailer_found = False
            for ext in ['mp4', 'mkv', 'avi', 'mov', 'webm']:
                trailer_path = os.path.join(full_path, f"{base_name}-trailer.{ext}")
                if os.path.isfile(trailer_path):
                    trailer_found = True
                    break
            folders.append({'name': base_name, 'found': trailer_found})
    return folders

class Api:
    def search(self, query):
        return fetch_youtube_links(query)

    def download(self, url, start=None, end=None):
        return download_video(url, start, end)

    def scan(self, dir_path):
        return scan_media_directory(dir_path)

    def select_folder(self):
        return webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)

    def set_foldername(self, name):
        global selected_foldername
        selected_foldername = name


def start():
    api = Api()
    window = webview.create_window('YouTube Viewer/Downloader - TrailHound v3.0', 'index.html', width=2760, height=1035)
    window.expose(api.search)
    window.expose(api.download)
    window.expose(api.scan)
    window.expose(api.select_folder)
    window.expose(api.set_foldername)
    webview.start()

if __name__ == '__main__':
    start()
