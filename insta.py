import os
import json
import re
import subprocess
import yt_dlp

# ==== CONFIG ====
DOWNLOAD_DIR = "downloads"
OUTPUT_JSON = "reel_data.json"

URLS = [
    "REELS_URL"
]

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ==== LOAD OLD DATA ====
all_data = []
if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        try:
            all_data = json.load(f)
        except:
            all_data = []

downloaded_urls = {d.get("reel_url") for d in all_data if "reel_url" in d}

# ==== FIXED: CLEAN FILENAME (Removes Emojis & Windows-Breaking Characters) ====
def clean_filename(text):
    text = text.strip().replace("\n", " ")
    
    # Force drop smart quotes and brackets that upset argument streams
    text = text.replace('“', '').replace('”', '').replace('"', '').replace("'", "")
    
    # Keep ONLY alphanumeric text, normal spaces, hyphens, and underscores
    # This wipes out emojis (like hearts) entirely so Windows/FFmpeg don't crash
    text = re.sub(r'[^a-zA-Z0-9 \-_]', '', text)
    
    # Condense multiple trailing or internal spaces down to one
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text[:60] if text else "processed_shorts_video"

# ==== HIGH-QUALITY 9:16 FORCER & FINGERPRINT CHANGER ====
def edit_video_fingerprint(input_path, output_path):
    """
    Forces video into standard 1080x1920 (9:16) dimensions,
    micro-trims the timeline, and shifts pixel hashes to bypass unoriginal content filters.
    """
    print(f"[⚙️] Scaling to strict 1080x1920 and rewriting video metadata...")
    
    # 1. Scale down to fit inside a 1080x1920 box without stretching/squishing
    # 2. Pad any remaining edges with black bars to force exactly 1080x1920 resolution
    # 3. Alter contrast and saturation minimally to shift the file hash
    filter_chain = (
        "scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,"
        "eq=contrast=1.03:saturation=1.02"
    )
    
    command = [
        'ffmpeg', '-y',
        '-ss', '0.2',                        # Shave 0.2 seconds off the start
        '-i', input_path,
        '-vf', filter_chain,                 # Apply formatting filters
        '-c:v', 'libx264',
        '-crf', '18',                        # Visually lossless high-quality encoding
        '-preset', 'slow',                   # Higher compression efficiency pass
        '-c:a', 'aac',                       # High-quality audio codec
        '-b:a', '192k',                      # Solid audio bitrate
        output_path
    ]
    
    try:
        # Run FFmpeg and capture error logs silently
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"[✗] FFmpeg Error Log:\n{result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"[✗] Failed to execute FFmpeg: {e}")
        return False

# ==== DOWNLOAD & PROCESS FUNCTION WITH FAILSAFE ====
def download_and_process(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Grabs highest individual stream qualities available
        'outtmpl': f'{DOWNLOAD_DIR}/temp_raw_%(id)s.%(ext)s', # Temporary file pattern
        'noplaylist': True,
        'cookiefile': 'insta_cookies.txt' if os.path.exists('insta_cookies.txt') else None,
        'quiet': True,
        'merge_output_format': 'mp4'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            temp_raw_path = ydl.prepare_filename(info)

            caption = info.get("description", "") or ""
            clean_name = clean_filename(caption)
            final_processed_path = os.path.join(DOWNLOAD_DIR, clean_name + ".mp4")

            # Run through our strict 9:16 processor
            success = edit_video_fingerprint(temp_raw_path, final_processed_path)

            # Clean up raw temporary file if it still exists to save space
            if os.path.exists(temp_raw_path):
                os.remove(temp_raw_path)

            # CRITICAL FAILSAFE: If FFmpeg failed, remove the broken white-icon file 
            # and just save the raw download as a fallback so you don't lose the video asset.
            if not success or not os.path.exists(final_processed_path):
                print("[⚠️] FFmpeg edit failed. Cleaning up broken paths and saving unedited fallback.")
                if os.path.exists(final_processed_path):
                    os.remove(final_processed_path) # Drop broken white icon file
                
                fallback_path = os.path.join(DOWNLOAD_DIR, clean_name + "_fallback.mp4")
                ydl_opts['outtmpl'] = fallback_path
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_retry:
                    ydl_retry.extract_info(url, download=True)
                final_processed_path = fallback_path

            return {
                "platform": info.get("extractor"),
                "username": info.get("uploader", "unknown"),
                "caption": caption,
                "video_file": final_processed_path,
                "video_url": info.get("webpage_url", url),
                "reel_url": url
            }

        except Exception as e:
            print(f"[✗] Download Error: {e}")
            return None

# ==== MAIN LOOP ====
for url in URLS:
    if url in downloaded_urls:
        print(f"[↩] Skipping (Already handled): {url}")
        continue

    print(f"\n[→] Extracting: {url}")
    result = download_and_process(url)

    if result:
        all_data.append(result)
        downloaded_urls.add(url)
        print("[✓] Processed and Saved successfully.")

# ==== SAVE DATA TRACKING ====
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=4, ensure_ascii=False)

print("\n[✓] Script pipeline complete.")