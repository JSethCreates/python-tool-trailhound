<p align="left">
  <img src="th.png" alt="TrailHound Logo" width="200">
</p>

#    TrailHound

TrailHound is a simple desktop tool to help you **check your local media folders for missing trailers and download them from YouTube**.

It uses [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) behind the scenes to handle searches, downloads, and trimming. You can also optionally use your own YouTube API key for faster searching.

---

![Screenshot](screenshots/1.PNG)

## ✨ Features

- ✅ **Scans your media folders for missing trailers** Select a media folder to scan, click an item to search for trailers, click a header to sort
- 🔎 **Searches YouTube** (via API key or using yt-dlp scraping if no key is provided) You may provide a different search term
- 🎥 **Downloads and optionally trims trailers using yt-dlp** Enter a start and/or end time to download a partial video (to cut off vanity titles) 
- 🚫 **Mark folders as "no trailer available"** to skip them in future scans (places 'notrailer.sad' file inside)
- 🖼️ **Artwork helper**: Displays 3 types of existing local artwork, if available (logo, clearart, fanart) and clicking an X links out to TVDB artwork pages
---

## 🚀 Installation

### ✅ Windows

Download and launch trailhound.exe

---

<details>
<summary> ### 💻 Run using Python Source</summary>

### Requirements

- Python 3.9 or newer
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) installed and on your PATH

### Install Python dependencies

```
pip install -r requirements.txt
```

### Install yt-dlp

```
pip install -U yt-dlp
```

### Required files

Download index.html, th_ytdlp_runner.exe and trailhound.py


### Run

```
python trailhound.py
```

</details>

---

## 🔑 YouTube API key (optional)

Using a YouTube API key is optional but recommended for smoother, faster searches. Its free, easy and only takes 30 seconds and 5 clicks:

<details>
<summary>How to get a YouTube API key</summary>

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable **YouTube Data API v3**.
4. Create credentials → API key.
5. Copy your key into TrailHound, save it for next run using the "Save API Key" button.

</details>

---

## 📝 License

TrailHound is licensed under the MIT License.  
See [LICENSE](./LICENSE) for details.

---
