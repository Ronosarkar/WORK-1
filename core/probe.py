import os
import sys
import json
import hashlib
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from PIL import Image, ExifTags
from core.ffmpeg_manager import get_ffprobe_path

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp', '.gif'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.mkv', '.avi', '.webm', '.m4v', '.flv', '.wmv'}

def compute_sha256(filepath: str, block_size: int = 65536) -> str:
    """Computes SHA-256 hash of a file for integrity verification."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()

def format_file_size(size_bytes: int) -> str:
    """Formats bytes into human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def format_duration(seconds: float) -> str:
    """Formats duration in seconds into HH:MM:SS or MM:SS."""
    if seconds <= 0:
        return "00:00"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def probe_image(filepath: str) -> Dict[str, Any]:
    """Inspects image technical properties and EXIF metadata."""
    stat = os.stat(filepath)
    file_size = stat.st_size
    sha256 = compute_sha256(filepath)
    
    info: Dict[str, Any] = {
        "file_path": filepath,
        "file_name": os.path.basename(filepath),
        "media_type": "image",
        "file_size": file_size,
        "file_size_formatted": format_file_size(file_size),
        "sha256": sha256,
        "format": "Unknown",
        "width": 0,
        "height": 0,
        "resolution": "0x0",
        "color_mode": "Unknown",
        "color_profile": "Standard sRGB",
        "exif": {},
        "raw_metadata": {}
    }

    try:
        with Image.open(filepath) as img:
            info["format"] = img.format or Path(filepath).suffix.lstrip('.').upper()
            info["width"] = img.width
            info["height"] = img.height
            info["resolution"] = f"{img.width}x{img.height}"
            info["color_mode"] = img.mode
            
            # Check ICC profile
            icc = img.info.get('icc_profile')
            if icc:
                info["color_profile"] = f"Embedded ICC ({len(icc)} bytes)"
                
            # Read EXIF
            exif_dict = {}
            raw_exif = img.getexif()
            if raw_exif:
                for tag_id, value in raw_exif.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    # Avoid binary blobs in preview
                    if isinstance(value, bytes):
                        val_str = f"<binary {len(value)} bytes>"
                    else:
                        val_str = str(value)
                    exif_dict[tag_name] = val_str
            info["exif"] = exif_dict
            
    except Exception as e:
        logger.warning(f"Error opening image {filepath}: {e}")

    return info

def probe_video(filepath: str) -> Dict[str, Any]:
    """Inspects video and audio stream specs using ffprobe."""
    stat = os.stat(filepath)
    file_size = stat.st_size
    sha256 = compute_sha256(filepath)
    
    info: Dict[str, Any] = {
        "file_path": filepath,
        "file_name": os.path.basename(filepath),
        "media_type": "video",
        "file_size": file_size,
        "file_size_formatted": format_file_size(file_size),
        "sha256": sha256,
        "format": Path(filepath).suffix.lstrip('.').lower(),
        "duration": 0.0,
        "duration_formatted": "00:00",
        "bitrate_kbps": 0,
        "video": {
            "codec": "None",
            "codec_long": "None",
            "width": 0,
            "height": 0,
            "resolution": "0x0",
            "fps": 0.0,
            "bitrate_kbps": 0,
            "pixel_format": "",
            "aspect_ratio": "16:9"
        },
        "audio": {
            "codec": "None",
            "channels": 0,
            "channel_layout": "None",
            "sample_rate": 0,
            "bitrate_kbps": 0
        },
        "metadata": {}
    }

    ffprobe = get_ffprobe_path()
    if not ffprobe:
        logger.warning("ffprobe not available for probing video")
        return info

    cmd = [
        ffprobe,
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        filepath
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(proc.stdout)
        
        fmt = data.get("format", {})
        info["duration"] = float(fmt.get("duration", 0.0))
        info["duration_formatted"] = format_duration(info["duration"])
        if "bit_rate" in fmt:
            info["bitrate_kbps"] = int(int(fmt["bit_rate"]) / 1000)
            
        info["metadata"] = fmt.get("tags", {})

        streams = data.get("streams", [])
        for st in streams:
            codec_type = st.get("codec_type")
            if codec_type == "video" and info["video"]["codec"] == "None":
                w = st.get("width", 0)
                h = st.get("height", 0)
                info["video"]["width"] = w
                info["video"]["height"] = h
                info["video"]["resolution"] = f"{w}x{h}" if w and h else "Unknown"
                info["video"]["codec"] = st.get("codec_name", "unknown")
                info["video"]["codec_long"] = st.get("codec_long_name", info["video"]["codec"])
                info["video"]["pixel_format"] = st.get("pix_fmt", "")
                
                # Aspect ratio
                dar = st.get("display_aspect_ratio")
                if dar:
                    info["video"]["aspect_ratio"] = dar
                elif w and h:
                    info["video"]["aspect_ratio"] = f"{w}:{h}"
                
                # Frame rate calculation
                fps_str = st.get("r_frame_rate", "0/0")
                if "/" in fps_str:
                    num, den = fps_str.split("/")
                    if den != "0" and num != "0":
                        info["video"]["fps"] = round(float(num) / float(den), 2)
                        
                if "bit_rate" in st:
                    info["video"]["bitrate_kbps"] = int(int(st["bit_rate"]) / 1000)
                    
            elif codec_type == "audio" and info["audio"]["codec"] == "None":
                info["audio"]["codec"] = st.get("codec_name", "unknown")
                info["audio"]["channels"] = st.get("channels", 0)
                info["audio"]["channel_layout"] = st.get("channel_layout", "stereo" if st.get("channels") == 2 else "mono")
                info["audio"]["sample_rate"] = int(st.get("sample_rate", 0))
                if "bit_rate" in st:
                    info["audio"]["bitrate_kbps"] = int(int(st["bit_rate"]) / 1000)

    except Exception as e:
        logger.error(f"Error probing video {filepath}: {e}")

    return info

def probe_file(filepath: str) -> Dict[str, Any]:
    """Inspects either video or image file according to its extension."""
    ext = Path(filepath).suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return probe_image(filepath)
    else:
        return probe_video(filepath)
