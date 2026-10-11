import os
import sys
import uuid
import time
import socket
import threading
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory

# Base paths
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.ffmpeg_manager import is_ffmpeg_available, get_ffmpeg_version
from core.probe import probe_file, format_file_size, compute_sha256
from core.variant_models import VideoVariantConfig, ImageVariantConfig, MetadataConfig
from core.video_processor import build_ffmpeg_command, VideoProcessWorker
from core.image_processor import process_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="web/templates")
# Allow large media file uploads (up to 1 GB)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024

UPLOAD_DIR = ROOT_DIR / "web_uploads"
EXPORT_DIR = ROOT_DIR / "web_exports"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# In-memory session tracking
jobs_status = {}

def cleanup_worker(max_age_seconds: int = 3600):
    """Periodically purges files older than 1 hour to prevent cloud disk overflow."""
    while True:
        try:
            now = time.time()
            for directory in [UPLOAD_DIR, EXPORT_DIR]:
                for f in directory.iterdir():
                    if f.is_file():
                        file_age = now - f.stat().st_mtime
                        if file_age > max_age_seconds:
                            try:
                                f.unlink()
                                logger.info(f"Purged expired temporary file: {f.name}")
                            except Exception as ex:
                                logger.warning(f"Failed to delete {f.name}: {ex}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        time.sleep(600)  # Check every 10 minutes

# Start background cleanup daemon
threading.Thread(target=cleanup_worker, daemon=True).start()

def get_local_ip() -> str:
    """Finds the primary local LAN IP address of this machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def is_cloud_env() -> bool:
    """Checks if running inside a cloud environment (Hugging Face, Render, Railway, etc.)."""
    return bool(os.environ.get("SPACE_ID") or os.environ.get("RENDER") or os.environ.get("RAILWAY_STATIC_URL") or os.environ.get("IS_CLOUD"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/network-info")
def network_info():
    ip = get_local_ip()
    port = int(os.environ.get("PORT", 7860 if is_cloud_env() else 8080))
    return jsonify({
        "ip": ip,
        "port": port,
        "url": f"http://{ip}:{port}",
        "is_cloud": is_cloud_env(),
        "ffmpeg_available": is_ffmpeg_available()
    })

@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"}), 400

    file_id = str(uuid.uuid4())[:8]
    ext = Path(file.filename).suffix
    saved_name = f"{file_id}_{file.filename}"
    saved_path = UPLOAD_DIR / saved_name
    file.save(str(saved_path))

    try:
        info = probe_file(str(saved_path))
        return jsonify({
            "success": True,
            "file_id": saved_name,
            "info": info
        })
    except Exception as e:
        logger.error(f"Probe failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/process", methods=["POST"])
def process():
    data = request.json or {}
    file_id = data.get("file_id")
    presets = data.get("presets", ["reel"])
    meta_dict = data.get("metadata", {})

    input_path = UPLOAD_DIR / file_id
    if not input_path.exists():
        return jsonify({"success": False, "error": "Input file not found"}), 404

    job_id = str(uuid.uuid4())[:8]
    jobs_status[job_id] = {
        "progress": 0.0,
        "status_message": "Starting job...",
        "completed": False,
        "outputs": []
    }

    # Run in background thread so HTTP response returns instantly
    threading.Thread(target=run_mobile_job, args=(job_id, str(input_path), presets, meta_dict), daemon=True).start()

    return jsonify({"success": True, "job_id": job_id})

def run_mobile_job(job_id: str, input_path: str, presets: list, meta_dict: dict):
    try:
        info = probe_file(input_path)
        is_video = info.get("media_type") == "video"
        base_name = Path(input_path).stem
        outputs = []

        total_tasks = len(presets)
        
        meta = MetadataConfig(
            title=meta_dict.get("title", ""),
            author=meta_dict.get("author", ""),
            copyright=meta_dict.get("copyright", "")
        )

        for idx, preset_key in enumerate(presets):
            step_base = (idx / total_tasks) * 100.0
            step_scale = (1.0 / total_tasks)

            if is_video:
                cfg = VideoVariantConfig(metadata=meta)
                if preset_key == "reel":
                    cfg.name = "Instagram Reel (9:16)"
                    cfg.resolution_preset = "1080x1920_vertical"
                    cfg.fps_preset = "30"
                    out_name = f"{base_name}_reel.mp4"
                elif preset_key == "youtube":
                    cfg.name = "YouTube HD (1080p)"
                    cfg.resolution_preset = "1080p"
                    cfg.fps_preset = "60"
                    out_name = f"{base_name}_youtube_1080p.mp4"
                elif preset_key == "hevc":
                    cfg.name = "Compact HEVC H.265"
                    cfg.video_codec = "libx265"
                    out_name = f"{base_name}_hevc.mp4"
                elif preset_key == "lossless":
                    cfg.name = "Lossless Stream Copy"
                    cfg.process_mode = "stream_copy"
                    out_name = f"{base_name}_lossless.mp4"
                else:
                    cfg.name = "Standard 1080p"
                    out_name = f"{base_name}_variant.mp4"

                out_path = EXPORT_DIR / out_name
                cmd = build_ffmpeg_command(input_path, str(out_path), cfg, info)
                
                def on_prog(pct, msg):
                    overall = step_base + (pct * step_scale)
                    jobs_status[job_id]["progress"] = overall
                    jobs_status[job_id]["status_message"] = f"Generating {cfg.name} ({pct:.0f}%)..."

                worker = VideoProcessWorker(cmd, info.get("duration", 0.0))
                ok = worker.run(progress_callback=on_prog)
                if ok and out_path.exists():
                    out_size = os.path.getsize(str(out_path))
                    sha = compute_sha256(str(out_path))
                    outputs.append({
                        "name": cfg.name,
                        "filename": out_name,
                        "size_formatted": format_file_size(out_size),
                        "sha256": sha
                    })

            else:  # Image processing
                img_cfg = ImageVariantConfig(metadata=meta)
                out_name = f"{base_name}_{preset_key}.jpg"
                out_path = EXPORT_DIR / out_name
                ok = process_image(input_path, str(out_path), img_cfg)
                if ok and out_path.exists():
                    out_size = os.path.getsize(str(out_path))
                    sha = compute_sha256(str(out_path))
                    outputs.append({
                        "name": f"Variant {preset_key.upper()}",
                        "filename": out_name,
                        "size_formatted": format_file_size(out_size),
                        "sha256": sha
                    })

        jobs_status[job_id]["progress"] = 100.0
        jobs_status[job_id]["status_message"] = "Completed!"
        jobs_status[job_id]["completed"] = True
        jobs_status[job_id]["outputs"] = outputs

    except Exception as e:
        logger.error(f"Job {job_id} error: {e}")
        jobs_status[job_id]["status_message"] = f"Error: {e}"
        jobs_status[job_id]["completed"] = True

@app.route("/api/progress/<job_id>")
def get_progress(job_id):
    job = jobs_status.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)

@app.route("/api/download/<filename>")
def download_file(filename):
    return send_from_directory(EXPORT_DIR, filename, as_attachment=True)

def start_server(port=None):
    if port is None:
        port = int(os.environ.get("PORT", 7860 if is_cloud_env() else 8080))
    local_ip = get_local_ip()
    print("=" * 65)
    print("  MEDIA VARIANT STUDIO - RUNNING")
    print("=" * 65)
    if is_cloud_env():
        print(f"  [CLOUD ENVIRONMENT DETECTED] Listening on port {port}")
    else:
        print(f"  [PC Local Access]    http://localhost:{port}")
        print(f"  [PHONE ACCESS LINK]  http://{local_ip}:{port}")
    print("=" * 65)
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    start_server()
