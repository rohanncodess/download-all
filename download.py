import os
import json
import re
import subprocess
import yt_dlp

# ================= CONFIG =================

DOWNLOAD_DIR = "downloads"
OUTPUT_JSON = "reel_data.json"

URLS = [
    "VIDEO_URL_HERE"
]

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ================= LOAD OLD DATA =================

all_data = []

if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        try:
            all_data = json.load(f)
        except json.JSONDecodeError:
            all_data = []

downloaded_urls = {
    item.get("source_url")
    for item in all_data
    if item.get("source_url")
}


# ================= CLEAN FILENAME =================

def clean_filename(text):

    text = (text or "").strip().replace("\n", " ")

    # Remove characters that Windows does not allow
    text = re.sub(r'[<>:"/\\|?*]', '', text)

    # Remove emojis and unusual characters
    text = re.sub(r'[^\w\s-]', '', text)

    text = re.sub(r'\s+', ' ', text).strip()

    return text[:80] if text else "downloaded_video"


# ================= CHECK IF VERTICAL =================

def is_vertical_video(info):
    """
    Returns True if the source video is vertical / reel-like.
    """

    width = info.get("width")
    height = info.get("height")

    if width and height:
        return height > width

    return False


# ================= CHECK PLATFORM =================

def get_platform(info):

    extractor = (info.get("extractor") or "").lower()

    if "youtube" in extractor:
        return "YouTube"

    if "instagram" in extractor:
        return "Instagram"

    if "tiktok" in extractor:
        return "TikTok"

    return extractor or "Unknown"


# ================= CHECK IF IT SHOULD BE 9:16 =================

def should_convert_to_reel(info):

    platform = get_platform(info)

    # Instagram and TikTok content should be reel format
    if platform in ["Instagram", "TikTok"]:
        return True

    # YouTube: only convert vertical videos (Shorts)
    if platform == "YouTube":
        return is_vertical_video(info)

    # Other platforms:
    # convert only if already vertical
    return is_vertical_video(info)


# ================= RUN FFMPEG =================

def run_ffmpeg(command):

    try:

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:

            print("\n[✗] FFmpeg Error:")
            print(result.stderr)

            return False

        return True

    except Exception as e:

        print(f"[✗] FFmpeg failed: {e}")

        return False


# ================= CONVERT REEL TO 1080x1920 =================

def process_reel(input_path, output_path):

    print("[⚙️] Reel/Short detected. Formatting to 1080x1920...")

    filter_chain = (
        "scale=1080:1920:"
        "force_original_aspect_ratio=decrease,"
        "pad=1080:1920:"
        "(ow-iw)/2:"
        "(oh-ih)/2:"
        "black,"
        "format=yuv420p"
    )

    command = [
        "ffmpeg",
        "-y",

        "-i", input_path,

        "-vf", filter_chain,

        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "medium",

        "-c:a", "aac",
        "-b:a", "192k",

        "-movflags", "+faststart",

        output_path
    ]

    return run_ffmpeg(command)


# ================= FIND DOWNLOADED FILE =================

def find_downloaded_file(info):

    requested_downloads = info.get("requested_downloads") or []

    # Check yt-dlp's recorded downloaded files
    for item in requested_downloads:

        filepath = item.get("filepath")

        if filepath and os.path.exists(filepath):
            return filepath

    # Fallback: try yt-dlp prepared filename
    try:

        filename = yt_dlp.YoutubeDL().prepare_filename(info)

        if os.path.exists(filename):
            return filename

    except:
        pass

    return None


# ================= DOWNLOAD =================

def download_media(url):

    # Best available HD quality.
    # For YouTube this prefers the best video + best audio.
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",

        "outtmpl": os.path.join(
            DOWNLOAD_DIR,
            "%(id)s.%(ext)s"
        ),

        "noplaylist": True,

        "quiet": False,

        "merge_output_format": "mp4",

        "cookiefile": (
            "insta_cookies.txt"
            if os.path.exists("insta_cookies.txt")
            else None
        )
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            print("[→] Extracting media...")

            info = ydl.extract_info(
                url,
                download=True
            )

        platform = get_platform(info)

        title = (
            info.get("title")
            or info.get("description")
            or info.get("id")
            or "downloaded_video"
        )

        clean_name = clean_filename(title)

        downloaded_path = find_downloaded_file(info)

        if not downloaded_path:

            print("[✗] Could not find the downloaded file.")

            return None

        # =========================================
        # CHECK IF REEL / SHORT
        # =========================================

        convert_to_reel = should_convert_to_reel(info)

        # =========================================
        # REELS / SHORTS / TIKTOK
        # =========================================

        if convert_to_reel:

            final_path = os.path.join(
                DOWNLOAD_DIR,
                f"{clean_name}_reel.mp4"
            )

            success = process_reel(
                downloaded_path,
                final_path
            )

            if not success:

                print(
                    "[⚠️] Conversion failed. "
                    "Keeping original download."
                )

                final_path = downloaded_path

            else:

                # Delete original temporary file
                if (
                    os.path.exists(downloaded_path)
                    and downloaded_path != final_path
                ):

                    os.remove(downloaded_path)

            media_type = "reel_or_short"

        # =========================================
        # NORMAL YOUTUBE / LANDSCAPE VIDEO
        # =========================================

        else:

            print(
                "[✓] Normal video detected. "
                "Keeping original resolution."
            )

            extension = os.path.splitext(
                downloaded_path
            )[1]

            final_path = os.path.join(
                DOWNLOAD_DIR,
                clean_name + extension
            )

            # Rename the downloaded file
            if downloaded_path != final_path:

                if os.path.exists(final_path):
                    os.remove(final_path)

                os.rename(
                    downloaded_path,
                    final_path
                )

            media_type = "normal_video"

        return {
            "platform": platform,
            "type": media_type,
            "username": info.get(
                "uploader",
                "unknown"
            ),
            "title": info.get("title", ""),
            "caption": info.get(
                "description",
                ""
            ),
            "video_file": final_path,
            "source_url": url,
            "original_url": info.get(
                "webpage_url",
                url
            ),
            "original_width": info.get(
                "width"
            ),
            "original_height": info.get(
                "height"
            )
        }

    except Exception as e:

        print(f"[✗] Download Error: {e}")

        return None


# ================= MAIN LOOP =================

for url in URLS:

    if url in downloaded_urls:

        print(
            f"[↩] Skipping "
            f"(Already downloaded): {url}"
        )

        continue

    print(f"\n[→] Downloading: {url}")

    result = download_media(url)

    if result:

        all_data.append(result)

        downloaded_urls.add(url)

        print(
            f"[✓] Download complete: "
            f"{result['video_file']}"
        )


# ================= SAVE JSON =================

with open(
    OUTPUT_JSON,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_data,
        f,
        indent=4,
        ensure_ascii=False
    )

print("\n[✓] Script pipeline complete.")