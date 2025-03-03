# TrailHound v6.0

import webview
import subprocess
import requests
import os
import threading
import http.server
import socketserver

API_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_key.txt")
YTDLP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "th_ytdlp_runner.exe")

selected_dir = None
selected_foldername = None
httpd = None

def save_api_key(key):
    try:
        with open(API_KEY_FILE, "w") as f:
            f.write(key.strip())
        return "API key saved"
    except Exception as e:
        return f"Failed to save API key: {e}"

def load_api_key():
    if os.path.isfile(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as f:
            return f.read().strip()
    return ""

def fetch_youtube_links(query, api_key=None):
    results = []
    if api_key:
        try:
            url = (
                "https://www.googleapis.com/youtube/v3/search"
                f"?part=snippet&maxResults=4&q={query}&type=video&key={api_key}"
            )
            response = requests.get(url).json()
            if 'error' in response:
                return {'error': f"API error: {response['error'].get('message', 'Invalid API key or quota issue')}. Falling back to yt-dlp to scrape results (slower)..." }
            items = response.get('items', [])
            for it in items:
                vid = it['id']['videoId']
                link = f"https://www.youtube.com/watch?v={vid}"
                embed = f"https://www.youtube.com/embed/{vid}"
                title = it['snippet']['title']
                results.append({"title": title, "url": link, "embed": embed, "duration": "", "resolution": ""})
            return results
        except Exception as e:
            return {'error': f"API exception: {str(e)}. Falling back to yt-dlp."}

    try:
        command = [
            YTDLP_PATH,
            f'ytsearch4:{query}',
            '--print', '%(title)s||%(webpage_url)s||%(duration_string)s||%(height)sp',
            '--skip-download',
            '--no-warnings'
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')

        for line in lines:
            parts = line.split('||')
            if len(parts) >= 4:
                title = parts[0]
                url = parts[1]
                duration = parts[2]
                resolution = parts[3]
                embed = url.replace("watch?v=", "embed/")
                results.append({"title": title, "url": url, "embed": embed, "duration": duration, "resolution": resolution})
    except subprocess.CalledProcessError as e:
        return {'error': f'yt-dlp error: {str(e)}'}

    return results

def get_images_for_folder(foldername):
    global selected_dir
    if not selected_dir or not foldername:
        return {}

    images = {}
    base_name = foldername
    exts = ['png', 'jpg', 'jpeg', 'webp']

    for ext in exts:
        for file in [f"logo.{ext}", f"clearlogo.{ext}"]:
            if os.path.isfile(os.path.join(selected_dir, foldername, file)):
                images['logo'] = file
                break
        if 'logo' in images:
            break

    for ext in exts:
        for file in [f"{base_name}-clearart.{ext}", f"clearart.{ext}"]:
            if os.path.isfile(os.path.join(selected_dir, foldername, file)):
                images['clearart'] = file
                break
        if 'clearart' in images:
            break

    for ext in exts:
        for file in [f"{base_name}-fanart.{ext}", f"fanart.{ext}"]:
            if os.path.isfile(os.path.join(selected_dir, foldername, file)):
                images['fanart'] = file
                break
        if 'fanart' in images:
            break

    return images

def get_video_metadata(video_url):
    duration = ""
    resolution = ""
    try:
        result = subprocess.run(
            [YTDLP_PATH, '--print', '%(duration_string)s\n%(height)sp', '--skip-download', video_url],
            capture_output=True, text=True, check=True
        )
        output_lines = result.stdout.strip().split('\n')
        if len(output_lines) >= 2:
            duration = output_lines[0].strip()
            resolution = output_lines[1].strip()
    except subprocess.CalledProcessError:
        pass
    return {"duration": duration, "resolution": resolution}

def download_video(video_url, start=None, end=None):
    global selected_dir, selected_foldername
    try:
        if selected_dir and selected_foldername:
            output_dir = os.path.join(selected_dir, selected_foldername)
            safe_name = selected_foldername + '-trailer.%(ext)s'
            output = os.path.join(output_dir, safe_name)
        else:
            output = 'trailer_output.%(ext)s'

        command = [
            YTDLP_PATH,
            '-f', 'bestvideo[ext=mp4][height=720][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]',
            video_url,
            '-o', output,
            '--merge-output-format', 'mp4',
            '--remux-video', 'mp4'
        ]

        if start or end:
            section = f"*{start or ''}-{end or ''}"
            command.extend(['--download-sections', section])

        subprocess.run(command, check=True)
        return 'Download complete'
    except subprocess.CalledProcessError as e:
        return f'Download failed: {str(e)}'

def preview_trailer():
    global selected_dir, selected_foldername
    if selected_dir and selected_foldername:
        folder_path = os.path.join(selected_dir, selected_foldername)
        filename = os.path.join(folder_path, f"{selected_foldername}-trailer.mp4")
        try:
            os.startfile(folder_path)
            subprocess.Popen(['start', '', filename], shell=True)
            return 'Preview launched'
        except Exception as e:
            return f'Preview failed: {e}'
    return 'No folder selected'

def open_media_folder(foldername):
    global selected_dir
    if selected_dir and foldername:
        folder_path = os.path.join(selected_dir, foldername)
        try:
            os.startfile(folder_path)
            return 'Opened'
        except Exception as e:
            return f'Error opening: {e}'
    return 'No folder selected'

def mark_no_trailer(foldername):
    global selected_dir
    if selected_dir and foldername:
        folder_path = os.path.join(selected_dir, foldername)
        marker_path = os.path.join(folder_path, "notrailer.sad")
        try:
            with open(marker_path, "w") as f:
                f.write("No trailer available.")
            return "Marker created"
        except Exception as e:
            return f"Error creating marker: {e}"
    return "No folder selected"

def scan_media_directory(path):
    global selected_dir, httpd
    selected_dir = path

    if not os.path.isdir(path):
        return {'error': f'Not a valid directory: {path}'}

    if httpd:
        try:
            httpd.shutdown()
            httpd.server_close()
            httpd = None
            print("Previous server stopped and socket closed.")
        except Exception as e:
            print("Error stopping previous server:", e)

    threading.Thread(target=start_http_server, args=(path,), daemon=True).start()

    folders = []
    for name in os.listdir(path):
        full_path = os.path.join(path, name)
        if os.path.isdir(full_path):
            base_name = os.path.basename(full_path)
            trailer_found = False
            logo_found = False
            clearart_found = False
            fanart_found = False

            for ext in ['mp4', 'mkv', 'avi', 'mov', 'webm']:
                trailer_path = os.path.join(full_path, f"{base_name}-trailer.{ext}")
                if os.path.isfile(trailer_path):
                    trailer_found = True
                    break

            marker_path = os.path.join(full_path, "notrailer.sad")
            if os.path.isfile(marker_path):
                trailer_found = True

            exts = ['png', 'jpg', 'jpeg', 'webp']

            for ext in exts:
                for file in [f"logo.{ext}", f"clearlogo.{ext}"]:
                    if os.path.isfile(os.path.join(full_path, file)):
                        logo_found = True
                        break
                if logo_found:
                    break

            for ext in exts:
                if (
                    os.path.isfile(os.path.join(full_path, f"{base_name}-clearart.{ext}")) or
                    os.path.isfile(os.path.join(full_path, f"clearart.{ext}"))
                ):
                    clearart_found = True
                    break

            for ext in exts:
                if (
                    os.path.isfile(os.path.join(full_path, f"{base_name}-fanart.{ext}")) or
                    os.path.isfile(os.path.join(full_path, f"fanart.{ext}"))
                ):
                    fanart_found = True
                    break

            folders.append({'name': base_name, 'found': trailer_found, 'logo': logo_found, 'clearart': clearart_found, 'fanart': fanart_found})

    # folders.sort(key=lambda x: x['found'])
    return folders

def start_http_server(directory, port=8000):
    global httpd
    handler = http.server.SimpleHTTPRequestHandler
    os.chdir(directory)
    httpd = socketserver.TCPServer(("", port), handler)
    print(f"Serving local files at http://127.0.0.1:{port}/")
    httpd.serve_forever()

class Api:
    def mark_trailer_downloaded(self):
        global selected_foldername
        return selected_foldername

    def search(self, query, api_key=None):
        return fetch_youtube_links(query, api_key)

    def download(self, url, start=None, end=None):
        return download_video(url, start, end)

    def scan(self, dir_path):
        return scan_media_directory(dir_path)

    def select_folder(self):
        return webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)

    def set_foldername(self, name):
        global selected_foldername
        selected_foldername = name

    def fetch_metadata(self, url):
        return get_video_metadata(url)

    def preview(self):
        return preview_trailer()

    def open_folder(self, foldername):
        return open_media_folder(foldername)

    def get_images(self, foldername):
        return get_images_for_folder(foldername)

    def mark_no_trailer(self, foldername):
        return mark_no_trailer(foldername)

    def save_key(self, key):
        return save_api_key(key)

    def load_key(self):
        return load_api_key()

def start():
    api = Api()
    window = webview.create_window('TrailHound v6', 'index.html', width=1600, height=1050)
    window.expose(api.search)
    window.expose(api.download)
    window.expose(api.scan)
    window.expose(api.select_folder)
    window.expose(api.set_foldername)
    window.expose(api.fetch_metadata)
    window.expose(api.preview)
    window.expose(api.mark_trailer_downloaded)
    window.expose(api.open_folder)
    window.expose(api.get_images)
    window.expose(api.mark_no_trailer)
    window.expose(api.save_key)
    window.expose(api.load_key)
    webview.start()

if __name__ == '__main__':
    start()
