# Universal Downloader

An automated Python pipeline for downloading Instagram Reels using `yt-dlp`, standardizing videos to 9:16 (1080x1920) with `FFmpeg`, and storing video metadata in a JSON log.

## Features

* **High-Quality Video Extraction**: Uses `yt-dlp` with optional Instagram cookie session support.
* **Video Processing**: Applies minor timeline and visual adjustments during processing.
* **Failsafe Mechanism**: Saves the original downloaded video if FFmpeg processing fails.
* **Metadata Tracking**: Stores the platform, username, caption, video path, video URL, and Reel URL in `reel_data.json`.
* **Duplicate Detection**: Automatically skips URLs that have already been processed.
* **Clean Filenames**: Generates Windows-friendly filenames from video captions.

## Prerequisites

* Python 3.8+
* FFmpeg
* `yt-dlp`

### Install FFmpeg

**Windows**

```bash
winget install ffmpeg
```

**macOS**

```bash
brew install ffmpeg
```

**Linux**

```bash
sudo apt install ffmpeg
```

Verify FFmpeg:

```bash
ffmpeg -version
```

## Installation

Clone the repository:

```bash
git clone https://github.com/rohanncodess/download-all.git
cd download-all
```

Install the Python dependency:

```bash
pip install yt-dlp
```

## Usage

Add your Reel URLs to `main.py`:

```python
URLS = [
    "YOUR_REEL_URL"
]
```

Then run:

```bash
python main.py
```

If authentication is required, place your Instagram cookies file in the project directory:

```text
insta_cookies.txt
```

The script automatically detects and uses it when available.

## Output

Processed videos are saved inside:

```text
downloads/
```

Metadata is stored in:

```text
reel_data.json
```

Example metadata:

```json
{
    "platform": "Instagram",
    "username": "username",
    "caption": "Example caption",
    "video_file": "downloads/example.mp4",
    "video_url": "https://www.instagram.com/reel/...",
    "reel_url": "https://www.instagram.com/reel/..."
}
```

## Project Structure

```text
download-all/
├── main.py
├── downloads/
├── reel_data.json
├── insta_cookies.txt
└── README.md
```

## Notes

The video processing step makes formatting and encoding changes to downloaded media. It should not be used to evade platform moderation, copyright enforcement, or content-ownership systems.

Only download and process content you have permission to use, and follow the terms of service of the platform and the rights of content creators.
