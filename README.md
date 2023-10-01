# Python Tool - TrailHound

A Python GUI application that scans a user-selected media directory to identify TV/film folders lacking trailers.  
Integrates with the YouTube Data API to search for and preview trailers, allows trimming of unwanted portions, and saves the final trailer using the `media-name–trailer` naming convention.

## Features
- **Folder scanning**: Detects missing trailers in media library directories  
- **YouTube integration**: Requires a Google API key for querying trailer titles  
- **Video preview & trimming**: In-app player with start/end controls to cut promotional outro  
- **Automated download**: Saves trailers at configurable quality  
- **Status updates**: Marks folders with a ✓ once a trailer is saved  

## Requirements
- Python 3.x  
- `yt-dlp`  
- `ffmpeg`  
- `tkinter` (or another GUI framework)  
- A valid Google YouTube Data API key  

## Installation
1. Clone the repo:  
   ```bash
   git clone https://github.com/YourUsername/python-tool-trailhound.git
   cd python-tool-trailhound
   ```
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
3. Add your YouTube API key in `config.json` or provide when prompted.  

## Usage
```bash
python trailhound.py
```
1. Select your media directory  
2. Browse items missing trailers  
3. Preview, trim, and download trailers  
4. Enjoy automated trailer management!  

## License
This project is licensed under the MIT License.
