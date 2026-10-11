import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field

from PySide6.QtCore import QObject, Signal, QThread, QMutex

from core.variant_models import VideoVariantConfig, ImageVariantConfig
from core.probe import probe_file, compute_sha256
from core.video_processor import build_ffmpeg_command, VideoProcessWorker
from core.image_processor import process_image

logger = logging.getLogger(__name__)

@dataclass
class JobItem:
    job_id: str
    input_file: str
    variant_index: int
    variant_name: str
    output_file: str
    media_type: str  # "video" or "image"
    config: Union[VideoVariantConfig, ImageVariantConfig]
    status: str = "queued"  # "queued", "processing", "completed", "failed", "cancelled"
    progress: float = 0.0
    status_message: str = "In queue"
    error_message: str = ""
    source_sha256: str = ""
    output_sha256: str = ""
    source_size: int = 0
    output_size: int = 0
    duration_sec: float = 0.0

class BatchQueueWorker(QThread):
    job_started = Signal(str)                          # job_id
    job_progress = Signal(str, float, str)            # job_id, percent, message
    job_completed = Signal(str, bool, str, str, int)  # job_id, success, out_path, out_sha256, out_size
    batch_finished = Signal(int, int)                 # total_success, total_failed
    log_message = Signal(str)                         # log string

    def __init__(self, jobs: List[JobItem], parent=None):
        super().__init__(parent)
        self.jobs = jobs
        self._is_cancelled = False
        self._current_video_worker: Optional[VideoProcessWorker] = None
        self._mutex = QMutex()

    def cancel_batch(self):
        self._mutex.lock()
        self._is_cancelled = True
        if self._current_video_worker:
            self._current_video_worker.cancel()
        self._mutex.unlock()

    def run(self):
        total_success = 0
        total_failed = 0

        self.log_message.emit(f"Starting batch execution of {len(self.jobs)} job(s)...")

        for job in self.jobs:
            if self._is_cancelled:
                job.status = "cancelled"
                job.status_message = "Cancelled by user"
                self.job_completed.emit(job.job_id, False, "", "", 0)
                continue

            job.status = "processing"
            self.job_started.emit(job.job_id)
            self.log_message.emit(f"Processing: {os.path.basename(job.input_file)} -> {job.variant_name}")

            # Ensure output directory exists
            out_dir = os.path.dirname(job.output_file)
            os.makedirs(out_dir, exist_ok=True)

            success = False
            try:
                # Probe input if needed
                source_info = probe_file(job.input_file)
                job.source_sha256 = source_info.get("sha256", "")
                job.source_size = source_info.get("file_size", 0)

                if job.media_type == "video":
                    total_dur = source_info.get("duration", 0.0)
                    cmd = build_ffmpeg_command(job.input_file, job.output_file, job.config, source_info)
                    
                    worker = VideoProcessWorker(cmd, total_dur)
                    self._mutex.lock()
                    self._current_video_worker = worker
                    self._mutex.unlock()

                    def on_video_progress(pct: float, msg: str):
                        job.progress = pct
                        job.status_message = msg
                        self.job_progress.emit(job.job_id, pct, msg)

                    success = worker.run(progress_callback=on_video_progress)

                    self._mutex.lock()
                    self._current_video_worker = None
                    self._mutex.unlock()

                else:  # Image processing
                    def on_image_progress(pct: float, msg: str):
                        job.progress = pct
                        job.status_message = msg
                        self.job_progress.emit(job.job_id, pct, msg)

                    success = process_image(job.input_file, job.output_file, job.config, progress_callback=on_image_progress)

                if success and os.path.isfile(job.output_file) and not self._is_cancelled:
                    job.status = "completed"
                    job.progress = 100.0
                    job.status_message = "Completed"
                    job.output_sha256 = compute_sha256(job.output_file)
                    job.output_size = os.path.getsize(job.output_file)
                    total_success += 1
                    self.log_message.emit(f"✓ Completed: {os.path.basename(job.output_file)} (SHA-256: {job.output_sha256[:12]}...)")
                    self.job_completed.emit(job.job_id, True, job.output_file, job.output_sha256, job.output_size)
                else:
                    if self._is_cancelled:
                        job.status = "cancelled"
                        job.status_message = "Cancelled"
                    else:
                        job.status = "failed"
                        job.status_message = "Processing failed"
                        total_failed += 1
                    # Remove partial output if failed or cancelled
                    if os.path.isfile(job.output_file):
                        try:
                            os.remove(job.output_file)
                        except Exception:
                            pass
                    self.job_completed.emit(job.job_id, False, "", "", 0)

            except Exception as e:
                logger.error(f"Error executing job {job.job_id}: {e}")
                job.status = "failed"
                job.error_message = str(e)
                job.status_message = f"Error: {e}"
                total_failed += 1
                self.log_message.emit(f"✗ Failed: {e}")
                self.job_completed.emit(job.job_id, False, "", "", 0)

        self.log_message.emit(f"Batch finished. Successful: {total_success}, Failed: {total_failed}")
        self.batch_finished.emit(total_success, total_failed)
