# Universal Downloader

An automated Python pipeline that downloads Instagram Reels using `yt-dlp`, standardizes them into 9:16 (1080x1920) format via `FFmpeg`, shifts pixel fingerprints to bypass unoriginal content filters, and exports video metadata into a JSON log.

## Features

* **High-Quality Video Extraction**: Powered by `yt-dlp` with cookie session support.
* **Aspect Ratio Standardization**: Enforces strict 1080x1920 (9:16) resolution with black padding to avoid video distortion.
* **Fingerprint Shift**: Applies slight temporal cuts (`-ss 0.2`) and subtle color/contrast modifications (`eq=contrast=1.03:saturation=1.02`) to alter the file hash.
* **Failsafe Mechanism**: Falls back to the raw unedited video download if FFmpeg processing encounters an issue.
* **Metadata Tracking**: Appends video details, creator username, reel URL, and original captions directly to a JSON database.

## Prerequisites

1. **Python 3.8+**
2. **FFmpeg**: Must be installed and added to your system environment variables (PATH).
   * **Windows**: `winget install ffmpeg`
   * **macOS**: `brew install ffmpeg`
   * **Linux**: `sudo apt install ffmpeg`

## Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/rohanncodess/download-all.git](https://github.com/rohanncodess/download-all.git)
   cd download-all