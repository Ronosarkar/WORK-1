import os
import sys
import re
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

from core.ffmpeg_manager import get_ffmpeg_path
from core.variant_models import VideoVariantConfig
from core.metadata_manager import build_ffmpeg_metadata_args

logger = logging.getLogger(__name__)

def build_video_filter_chain(config: VideoVariantConfig, source_info: Dict[str, Any]) -> List[str]:
    """Assembles video filter elements ensuring high quality and correct dimensions."""
    filters = []

    # 1. Scaling & Aspect ratio handling
    res_mode = config.resolution_preset
    
    target_w, target_h = None, None
    if res_mode == "1080p":
        target_w, target_h = 1920, 1080
    elif res_mode == "720p":
        target_w, target_h = 1280, 720
    elif res_mode == "4k_2160p":
        target_w, target_h = 3840, 2160
    elif res_mode == "1080x1920_vertical":
        target_w, target_h = 1080, 1920
    elif res_mode == "1080x1080_square":
        target_w, target_h = 1080, 1080
    elif res_mode == "custom":
        target_w, target_h = config.custom_width, config.custom_height

    if target_w and target_h:
        if config.aspect_fit_mode == "pad_letterbox":
            # Scale proportionally to fit inside, pad rest with black
            scale_filter = (
                f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease:flags=lanczos,"
                f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2:color=black"
            )
            filters.append(scale_filter)
        elif config.aspect_fit_mode == "safe_crop":
            # Scale to fill completely, crop center
            scale_filter = (
                f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase:flags=lanczos,"
                f"crop={target_w}:{target_h}"
            )
            filters.append(scale_filter)
        else:
            # Direct fit maintaining even dimensions
            filters.append(f"scale={target_w}:{target_h}:flags=lanczos")
    else:
        # Original resolution: ensure dimensions are divisible by 2 for yuv420p
        filters.append("scale=trunc(iw/2)*2:trunc(ih/2)*2")

    # 2. Frame rate conversion
    if config.fps_preset == "24":
        filters.append("fps=24")
    elif config.fps_preset == "30":
        filters.append("fps=30")
    elif config.fps_preset == "60":
        filters.append("fps=60")
    elif config.fps_preset == "custom" and config.custom_fps > 0:
        filters.append(f"fps={config.custom_fps}")

    return filters

def build_audio_filter_chain(config: VideoVariantConfig) -> List[str]:
    """Assembles audio filters including volume normalization and channel mixing."""
    filters = []

    # EBU R128 loudness normalization
    if config.volume_normalize:
        filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")

    return filters

def build_ffmpeg_command(
    input_path: str,
    output_path: str,
    config: VideoVariantConfig,
    source_info: Dict[str, Any]
) -> List[str]:
    """Generates the full FFmpeg command list for execution."""
    ffmpeg_exe = get_ffmpeg_path()
    if not ffmpeg_exe:
        raise RuntimeError("FFmpeg executable not found.")

    cmd = [ffmpeg_exe, "-hide_banner", "-y"]

    # Trimming start (placed before -i for fast seek)
    if config.trim_enabled and config.trim_start:
        cmd.extend(["-ss", config.trim_start.strip()])

    cmd.extend(["-i", input_path])

    # Trimming end
    if config.trim_enabled and config.trim_end:
        cmd.extend(["-to", config.trim_end.strip()])

    # Stream Copy Mode (Zero re-encoding, 100% lossless)
    if config.process_mode == "stream_copy":
        cmd.extend(["-c:v", "copy"])
        cmd.extend(["-c:a", "copy"])
    else:
        # Video encoding
        if config.video_codec == "copy":
            cmd.extend(["-c:v", "copy"])
        else:
            cmd.extend(["-c:v", config.video_codec])
            
            # Pixel format standard for compatibility
            if config.video_codec in ("libx264", "libx265"):
                cmd.extend(["-pix_fmt", "yuv420p"])

            # Video Filters
            vf = build_video_filter_chain(config, source_info)
            if vf:
                cmd.extend(["-vf", ",".join(vf)])

            # Quality / Rate control
            if config.quality_mode == "crf":
                cmd.extend(["-crf", str(config.crf_value)])
                cmd.extend(["-preset", config.preset_speed])
            else:
                br = f"{config.video_bitrate_kbps}k"
                max_br = f"{int(config.video_bitrate_kbps * 1.5)}k"
                buf = f"{config.video_bitrate_kbps * 2}k"
                cmd.extend(["-b:v", br, "-maxrate", max_br, "-bufsize", buf])

            # GOP / Keyframe settings
            if config.gop_keyframe_sec > 0:
                fps = source_info.get("video", {}).get("fps", 30.0) or 30.0
                gop_size = max(1, int(fps * config.gop_keyframe_sec))
                cmd.extend(["-g", str(gop_size), "-keyint_min", str(gop_size)])

        # Audio encoding
        if config.audio_codec == "copy":
            cmd.extend(["-c:a", "copy"])
        else:
            cmd.extend(["-c:a", config.audio_codec])
            cmd.extend(["-b:a", f"{config.audio_bitrate_kbps}k"])
            
            if config.audio_sample_rate > 0:
                cmd.extend(["-ar", str(config.audio_sample_rate)])

            if config.audio_channels == "stereo":
                cmd.extend(["-ac", "2"])
            elif config.audio_channels == "mono":
                cmd.extend(["-ac", "1"])

            af = build_audio_filter_chain(config)
            if af:
                cmd.extend(["-af", ",".join(af)])

    # Inject metadata
    cmd.extend(build_ffmpeg_metadata_args(config.metadata))

    # Faststart optimization for MP4/MOV
    ext = Path(output_path).suffix.lower()
    if ext in (".mp4", ".mov", ".m4v"):
        cmd.extend(["-movflags", "+faststart"])

    # Progress output to stdout for real-time progress parsing
    cmd.extend(["-progress", "pipe:1", output_path])

    return cmd

class VideoProcessWorker:
    """Manages active FFmpeg execution, progress callbacks, and cancellation."""
    def __init__(self, cmd: List[str], total_duration_sec: float):
        self.cmd = cmd
        self.total_duration_sec = total_duration_sec
        self.process: Optional[subprocess.Popen] = None
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
            except Exception:
                pass

    def run(self, progress_callback: Optional[Callable[[float, str], None]] = None) -> bool:
        try:
            # Startup info to prevent popup console on Windows
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            self.process = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                startupinfo=startupinfo,
                bufsize=1,
                encoding="utf-8",
                errors="replace"
            )

            time_pattern = re.compile(r"out_time_ms=(\d+)")
            speed_pattern = re.compile(r"speed=\s*([\d\.]+x)")

            last_pct = 0.0
            cur_speed = "1.0x"
            all_output = []

            while True:
                if self._is_cancelled:
                    if self.process.poll() is None:
                        self.process.kill()
                    return False

                line = self.process.stdout.readline()
                if not line:
                    if self.process.poll() is not None:
                        break
                    continue

                line_str = line.strip()
                all_output.append(line_str)
                
                # Parse progress
                m_time = time_pattern.search(line_str)
                if m_time and self.total_duration_sec > 0:
                    microsec = int(m_time.group(1))
                    cur_sec = microsec / 1_000_000.0
                    pct = min(99.0, (cur_sec / self.total_duration_sec) * 100.0)
                    last_pct = pct
                    if progress_callback:
                        progress_callback(pct, f"Processing: {pct:.1f}% ({cur_speed})")

                m_speed = speed_pattern.search(line_str)
                if m_speed:
                    cur_speed = m_speed.group(1)

            ret = self.process.wait()
            if ret == 0:
                if progress_callback:
                    progress_callback(100.0, "Complete!")
                return True
            else:
                tail = "\n".join(all_output[-25:])
                logger.error(f"FFmpeg failed with exit code {ret}:\n{tail}")
                return False

        except Exception as e:
            logger.error(f"VideoProcessWorker exception: {e}")
            return False
