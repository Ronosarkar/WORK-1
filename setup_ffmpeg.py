"""
Setup script to detect or download FFmpeg & FFprobe for Windows.
"""
import sys
import logging
from core.ffmpeg_manager import is_ffmpeg_available, get_ffmpeg_path, get_ffprobe_path, download_ffmpeg_essentials, get_ffmpeg_version

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    print("=" * 60)
    print(" Media Variant & Metadata Studio - FFmpeg Setup Utility")
    print("=" * 60)
    
    if is_ffmpeg_available():
        print("[OK] FFmpeg is already installed and accessible:")
        print(f"  ffmpeg:  {get_ffmpeg_path()}")
        print(f"  ffprobe: {get_ffprobe_path()}")
        print(f"  version: {get_ffmpeg_version()}")
        return 0

    print("FFmpeg was not detected in PATH or local bin/ directory.")
    print("Downloading official Windows FFmpeg essentials build from Gyan.dev...")
    
    def on_progress(percent, msg):
        sys.stdout.write(f"\r[{percent:3d}%] {msg:<60}")
        sys.stdout.flush()

    success = download_ffmpeg_essentials(progress_callback=on_progress)
    print() # newline
    if success:
        print("[OK] Successfully installed FFmpeg & FFprobe into local bin/ directory!")
        print(f"  ffmpeg:  {get_ffmpeg_path()}")
        print(f"  ffprobe: {get_ffprobe_path()}")
        return 0
    else:
        print("[X] Failed to download FFmpeg automatically.")
        print("Please download ffmpeg.exe and ffprobe.exe and place them into the 'bin' folder,")
        print("or install via: winget install Gyan.FFmpeg")
        return 1

if __name__ == "__main__":
    sys.exit(main())
