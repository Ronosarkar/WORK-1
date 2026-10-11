from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class MetadataConfig:
    title: str = ""
    author: str = ""
    creator: str = ""
    description: str = ""
    copyright: str = ""
    software: str = "Media Variant & Metadata Studio"
    creation_date: str = ""  # e.g., "now" or "2026-10-07"
    keywords: str = ""
    comment: str = ""
    strip_all_first: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "author": self.author,
            "creator": self.creator,
            "description": self.description,
            "copyright": self.copyright,
            "software": self.software,
            "creation_date": self.creation_date,
            "keywords": self.keywords,
            "comment": self.comment,
            "strip_all_first": self.strip_all_first
        }

@dataclass
class VideoVariantConfig:
    # Basic
    name: str = "Variant 1"
    enabled: bool = True
    process_mode: str = "reencode"  # "stream_copy" or "reencode"
    container: str = "mp4"           # "mp4", "mov", "mkv", "webm"
    
    # Video specs
    video_codec: str = "libx264"     # "libx264", "libx265", "libvpx-vp9", "libsvtav1", "copy"
    resolution_preset: str = "original" # "original", "1080p", "720p", "4k_2160p", "1080x1920_vertical", "1080x1080_square", "custom"
    custom_width: int = 1920
    custom_height: int = 1080
    aspect_fit_mode: str = "pad_letterbox" # "pad_letterbox", "safe_crop"
    fps_preset: str = "original"     # "original", "24", "30", "60", "custom"
    custom_fps: float = 30.0
    
    # Rate control & Quality
    quality_mode: str = "crf"        # "crf" (visually lossless) or "bitrate"
    crf_value: int = 18              # 17-18 is visually lossless for x264/x265
    video_bitrate_kbps: int = 8000   # Used if quality_mode == "bitrate"
    preset_speed: str = "medium"     # "veryfast", "faster", "fast", "medium", "slow"
    gop_keyframe_sec: float = 2.0    # -1 for default, 2.0 standard for web/social
    
    # Audio specs
    audio_codec: str = "aac"         # "copy", "aac", "mp3", "opus"
    audio_bitrate_kbps: int = 256    # 128, 192, 256, 320
    audio_sample_rate: int = 48000   # 0 for original, 44100, 48000
    audio_channels: str = "keep"     # "keep", "stereo", "mono"
    volume_normalize: bool = False   # EBU R128 loudness normalization
    
    # Trimming
    trim_enabled: bool = False
    trim_start: str = "00:00:00"
    trim_end: str = ""

    # Metadata
    metadata: MetadataConfig = field(default_factory=MetadataConfig)

@dataclass
class ImageVariantConfig:
    name: str = "Variant 1"
    enabled: bool = True
    output_format: str = "JPEG"      # "JPEG", "PNG", "WEBP"
    jpeg_quality: int = 92           # 1-100 (92 is high quality)
    resize_mode: str = "original"    # "original", "1080p", "1080x1920", "custom"
    custom_width: int = 1920
    custom_height: int = 1080
    strip_exif: bool = False
    preserve_icc: bool = True
    metadata: MetadataConfig = field(default_factory=MetadataConfig)

def get_default_social_presets():
    """Returns standard legitimate publishing presets."""
    return [
        {
            "name": "Standard High-Quality 1080p (H.264)",
            "video_codec": "libx264",
            "container": "mp4",
            "resolution_preset": "1080p",
            "fps_preset": "original",
            "quality_mode": "crf",
            "crf_value": 18,
            "audio_codec": "aac",
            "audio_bitrate_kbps": 256
        },
        {
            "name": "Social Vertical Reel/Shorts (1080x1920)",
            "video_codec": "libx264",
            "container": "mp4",
            "resolution_preset": "1080x1920_vertical",
            "fps_preset": "30",
            "aspect_fit_mode": "pad_letterbox",
            "quality_mode": "crf",
            "crf_value": 18,
            "audio_codec": "aac",
            "audio_bitrate_kbps": 256
        },
        {
            "name": "Modern Compact HEVC (H.265)",
            "video_codec": "libx265",
            "container": "mp4",
            "resolution_preset": "original",
            "fps_preset": "original",
            "quality_mode": "crf",
            "crf_value": 20,
            "audio_codec": "aac",
            "audio_bitrate_kbps": 256
        },
        {
            "name": "Master Stream Copy (Lossless Metadata Edit)",
            "video_codec": "copy",
            "container": "mp4",
            "process_mode": "stream_copy",
            "audio_codec": "copy"
        }
    ]
