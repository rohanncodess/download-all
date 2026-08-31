# Universal Downloader

An automated Python downloader using `yt-dlp` and `FFmpeg` for downloading high-quality videos from YouTube, Instagram, and TikTok.

Normal YouTube videos keep their original resolution, while Shorts, Reels, and TikTok videos are formatted to 1080x1920 for vertical content.

## Features

* **Multi-Platform:** Supports YouTube, Instagram, and TikTok.
* **High-Quality Downloads:** Downloads the best available video and audio quality.
* **Smart Formatting:** Keeps normal YouTube videos unchanged and formats vertical content to 1080x1920.
* **Failsafe:** Keeps the original download if FFmpeg processing fails.
* **Metadata Tracking:** Saves download information to `reel_data.json`.
* **Duplicate Detection:** Skips URLs that have already been downloaded.
* **Clean Filenames:** Creates Windows-friendly filenames.

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

Install `yt-dlp`:

```bash
pip install yt-dlp
```

## Usage

Add URLs to `main.py`:

```python
URLS = [
    "YOUR_VIDEO_URL",
    "YOUR_REEL_URL",
    "YOUR_SHORT_URL"
]
```

Run:

```bash
python main.py
```

For Instagram authentication, place your cookies file in the project directory:

```text
insta_cookies.txt
```

## Output

Downloaded media is saved in:

```text
downloads/
```

Metadata is stored in:

```text
reel_data.json
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

Normal YouTube videos are kept at their downloaded resolution. YouTube Shorts, Instagram Reels, and TikTok videos are converted to 1080x1920.

Only download and process content you have permission to use, and follow the terms of service and copyright rules of the platforms involved.
