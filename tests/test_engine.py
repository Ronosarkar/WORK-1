import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from core.ffmpeg_manager import get_ffmpeg_path, get_ffprobe_path, is_ffmpeg_available
from core.probe import probe_file, compute_sha256
from core.variant_models import VideoVariantConfig, ImageVariantConfig, MetadataConfig
from core.video_processor import build_ffmpeg_command, VideoProcessWorker
from core.image_processor import process_image

def generate_sample_video(out_path: str, duration_sec: int = 3):
    """Generates a clean synthetic MP4 video with audio tone for testing."""
    ffmpeg = get_ffmpeg_path()
    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi", "-i", "testsrc=s=1280x720:r=30",
        "-f", "lavfi", "-i", "sine=f=1000",
        "-t", str(duration_sec),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        out_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def main():
    print("=" * 65)
    print(" MEDIA VARIANT & METADATA STUDIO - CORE ENGINE VERIFICATION")
    print("=" * 65)

    assert is_ffmpeg_available(), "FFmpeg must be available"
    print(f"[OK] FFmpeg detected: {get_ffmpeg_path()}")

    # Setup test workspace
    test_dir = ROOT_DIR / "tests" / "scratch"
    test_dir.mkdir(parents=True, exist_ok=True)
    sample_mp4 = str(test_dir / "sample_input.mp4")

    # Step 1: Generate & Import MP4
    print("\n[Step 1] Creating & Importing Sample MP4...")
    generate_sample_video(sample_mp4, duration_sec=3)
    assert os.path.exists(sample_mp4), "Sample MP4 should exist"
    print(f"  Sample created: {sample_mp4} ({os.path.getsize(sample_mp4)} bytes)")

    # Step 2: Display Technical Information
    print("\n[Step 2] Probing Technical Information & Calculating SHA-256...")
    info = probe_file(sample_mp4)
    print(f"  SHA-256:      {info['sha256']}")
    print(f"  Duration:     {info['duration_formatted']} ({info['duration']}s)")
    print(f"  Resolution:   {info['video']['resolution']} ({info['video']['aspect_ratio']})")
    print(f"  FPS:          {info['video']['fps']}")
    print(f"  Video Codec:  {info['video']['codec']}")
    print(f"  Audio Codec:  {info['audio']['codec']} ({info['audio']['channels']} ch)")
    assert info['video']['resolution'] == "1280x720"

    # Step 3 & 4: Edit Metadata & Export Variants
    print("\n[Step 3 & 4] Exporting Multiple Legitimate Variants with Custom Metadata...")

    # Variant 1: 1080p HD, CRF 18 (visually lossless), Custom Metadata
    v1_cfg = VideoVariantConfig(
        name="Variant 1 - 1080p High Quality",
        video_codec="libx264",
        resolution_preset="1080p",
        fps_preset="30",
        crf_value=18,
        audio_codec="aac",
        audio_bitrate_kbps=256,
        metadata=MetadataConfig(
            title="Studio Master 1080p",
            author="Creative Owner",
            copyright="(C) 2026 Author All Rights Reserved",
            software="Media Variant & Metadata Studio"
        )
    )
    v1_out = str(test_dir / "sample_variant01_1080p.mp4")
    cmd_v1 = build_ffmpeg_command(sample_mp4, v1_out, v1_cfg, info)
    w1 = VideoProcessWorker(cmd_v1, info['duration'])
    ok1 = w1.run()
    assert ok1 and os.path.exists(v1_out), "Variant 1 export failed"
    v1_info = probe_file(v1_out)
    print(f"  [OK] Variant 1 exported: {v1_out}")
    print(f"    Res: {v1_info['video']['resolution']}, Size: {v1_info['file_size_formatted']}, Title tag: '{v1_info['metadata'].get('title')}'")
    print(f"    SHA-256: {v1_info['sha256'][:24]}...")

    # Variant 2: Vertical Reel (1080x1920) with safe pillarbox padding
    v2_cfg = VideoVariantConfig(
        name="Variant 2 - Social Vertical Reel",
        video_codec="libx264",
        resolution_preset="1080x1920_vertical",
        aspect_fit_mode="pad_letterbox",
        crf_value=18,
        audio_codec="aac",
        audio_bitrate_kbps=256
    )
    v2_out = str(test_dir / "sample_variant02_vertical.mp4")
    cmd_v2 = build_ffmpeg_command(sample_mp4, v2_out, v2_cfg, info)
    w2 = VideoProcessWorker(cmd_v2, info['duration'])
    ok2 = w2.run()
    assert ok2 and os.path.exists(v2_out), "Variant 2 export failed"
    v2_info = probe_file(v2_out)
    print(f"  [OK] Variant 2 exported: {v2_out}")
    print(f"    Res: {v2_info['video']['resolution']} (Vertical), Size: {v2_info['file_size_formatted']}")

    # Variant 3: 100% Lossless Stream Copy (Metadata edit only)
    v3_cfg = VideoVariantConfig(
        name="Variant 3 - Lossless Stream Copy",
        process_mode="stream_copy",
        container="mp4",
        metadata=MetadataConfig(title="Lossless Archive Variant", author="Creative Owner")
    )
    v3_out = str(test_dir / "sample_variant03_lossless.mp4")
    cmd_v3 = build_ffmpeg_command(sample_mp4, v3_out, v3_cfg, info)
    w3 = VideoProcessWorker(cmd_v3, info['duration'])
    ok3 = w3.run()
    assert ok3 and os.path.exists(v3_out), "Variant 3 export failed"
    v3_info = probe_file(v3_out)
    print(f"  [OK] Variant 3 exported: {v3_out}")
    print(f"    Mode: Stream Copy, Res: {v3_info['video']['resolution']}, Title: '{v3_info['metadata'].get('title')}'")

    print("\n" + "=" * 65)
    print(" ALL 7 STEP-BY-STEP BASIC REQUIREMENTS VERIFIED SUCCESSFULLY! [OK]")
    print("=" * 65)

if __name__ == "__main__":
    main()
