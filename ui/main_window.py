import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QLineEdit, QFileDialog, QSpinBox,
    QProgressBar, QMessageBox, QScrollArea, QSplitter, QStatusBar,
    QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont

from core.ffmpeg_manager import is_ffmpeg_available, get_ffmpeg_version, download_ffmpeg_essentials
from core.probe import probe_file
from core.variant_models import VideoVariantConfig, ImageVariantConfig
from core.batch_queue import JobItem, BatchQueueWorker
from ui.styles.dark_theme import DARK_STYLESHEET
from ui.components.drop_area import DropArea
from ui.components.media_table import MediaTable
from ui.components.tech_info_panel import TechInfoPanel
from ui.components.metadata_panel import MetadataPanel
from ui.components.variant_card import VariantCard
from ui.components.history_panel import HistoryPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Variant & Metadata Studio")
        self.resize(1280, 850)
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(DARK_STYLESHEET)

        # State
        self.active_worker: Optional[BatchQueueWorker] = None
        self.default_export_dir = str(Path.home() / "Videos" / "MediaVariantStudio_Exports")
        os.makedirs(self.default_export_dir, exist_ok=True)

        self._init_ui()
        self._check_ffmpeg_status()

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(14, 12, 14, 12)
        root_layout.setSpacing(10)

        # 1. Top Header Bar (Title, FFmpeg Badge, Output Folder)
        header_bar = QFrame(self)
        header_bar.setStyleSheet("background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 6px;")
        h_layout = QHBoxLayout(header_bar)
        h_layout.setContentsMargins(10, 6, 10, 6)

        title_lbl = QLabel("🎥 Media Variant & Metadata Studio", self)
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #f8fafc;")
        h_layout.addWidget(title_lbl)

        # FFmpeg status pill
        self.lbl_ffmpeg_status = QLabel("Checking FFmpeg...", self)
        self.lbl_ffmpeg_status.setObjectName("badgeGreen")
        h_layout.addWidget(self.lbl_ffmpeg_status)

        self.btn_setup_ffmpeg = QPushButton("Download FFmpeg", self)
        self.btn_setup_ffmpeg.setVisible(False)
        self.btn_setup_ffmpeg.clicked.connect(self._auto_setup_ffmpeg)
        h_layout.addWidget(self.btn_setup_ffmpeg)

        h_layout.addStretch()

        # Output Folder selector
        h_layout.addWidget(QLabel("Output Folder:", self))
        self.txt_out_dir = QLineEdit(self.default_export_dir, self)
        self.txt_out_dir.setMinimumWidth(260)
        h_layout.addWidget(self.txt_out_dir)

        btn_browse_out = QPushButton("Browse...", self)
        btn_browse_out.clicked.connect(self._browse_output_dir)
        h_layout.addWidget(btn_browse_out)

        btn_open_out = QPushButton("Open Folder", self)
        btn_open_out.clicked.connect(self._open_output_dir)
        h_layout.addWidget(btn_open_out)

        root_layout.addWidget(header_bar)

        # 2. Main Tabbed Navigation
        self.tabs = QTabWidget(self)

        # TAB 1: Media Import & Technical Inspector
        tab_import = QWidget()
        ti_layout = QVBoxLayout(tab_import)
        ti_layout.setContentsMargins(8, 8, 8, 8)
        ti_layout.setSpacing(10)

        self.drop_area = DropArea(self)
        self.drop_area.files_selected.connect(self._on_files_imported)
        ti_layout.addWidget(self.drop_area)

        splitter_import = QSplitter(Qt.Vertical, self)
        self.media_table = MediaTable(self)
        self.media_table.file_selected.connect(self._on_media_selected_for_inspect)

        self.tech_panel = TechInfoPanel(self)
        splitter_import.addWidget(self.media_table)
        splitter_import.addWidget(self.tech_panel)
        splitter_import.setStretchFactor(0, 3)
        splitter_import.setStretchFactor(1, 2)
        ti_layout.addWidget(splitter_import)

        self.tabs.addTab(tab_import, "1. Media Queue & Inspector")

        # TAB 2: Multiple Export Variants Studio
        tab_variants = QWidget()
        tv_layout = QVBoxLayout(tab_variants)
        tv_layout.setContentsMargins(8, 8, 8, 8)
        tv_layout.setSpacing(10)

        # Variant control bar
        vbar = QHBoxLayout()
        vbar.addWidget(QLabel("<b>Number of Export Variants:</b>", self))
        self.spin_variant_count = QSpinBox(self)
        self.spin_variant_count.setRange(1, 20)
        self.spin_variant_count.setValue(3)  # default 3 variants
        self.spin_variant_count.valueChanged.connect(self._on_variant_count_changed)
        vbar.addWidget(self.spin_variant_count)

        btn_preset_social = QPushButton("⚡ Setup Social 3-Pack (Reel, YouTube HD, HEVC)", self)
        btn_preset_social.clicked.connect(self._setup_social_trio)
        vbar.addWidget(btn_preset_social)

        vbar.addStretch()
        tv_layout.addLayout(vbar)

        # Variant tabs container
        self.variant_tab_widget = QTabWidget(self)
        self.variant_cards: List[VariantCard] = []
        tv_layout.addWidget(self.variant_tab_widget)

        self.tabs.addTab(tab_variants, "2. Export Variants Studio (1–20)")

        # TAB 3: Metadata Editor
        tab_metadata = QWidget()
        tm_layout = QVBoxLayout(tab_metadata)
        tm_layout.setContentsMargins(8, 8, 8, 8)
        self.meta_editor = MetadataPanel("Global Non-Content Metadata Template", self)
        tm_layout.addWidget(self.meta_editor)
        self.tabs.addTab(tab_metadata, "3. Metadata Studio")

        # TAB 4: Batch Export & History
        tab_batch = QWidget()
        tb_layout = QVBoxLayout(tab_batch)
        tb_layout.setContentsMargins(8, 8, 8, 8)
        tb_layout.setSpacing(10)

        # Execution controls
        exec_bar = QHBoxLayout()
        self.btn_start_batch = QPushButton("🚀 Start Batch Export", self)
        self.btn_start_batch.setObjectName("primaryBtn")
        self.btn_start_batch.setFixedHeight(38)
        self.btn_start_batch.clicked.connect(self._start_batch_export)

        self.btn_cancel_batch = QPushButton("⏹ Cancel Processing", self)
        self.btn_cancel_batch.setObjectName("dangerBtn")
        self.btn_cancel_batch.setFixedHeight(38)
        self.btn_cancel_batch.setEnabled(False)
        self.btn_cancel_batch.clicked.connect(self._cancel_batch_export)

        exec_bar.addWidget(self.btn_start_batch, 2)
        exec_bar.addWidget(self.btn_cancel_batch, 1)
        tb_layout.addLayout(exec_bar)

        # Batch progress bar
        self.batch_progress = QProgressBar(self)
        self.batch_progress.setValue(0)
        self.batch_progress.setFixedHeight(22)
        tb_layout.addWidget(self.batch_progress)

        self.history_panel = HistoryPanel(self)
        self.history_panel.set_output_dir(self.txt_out_dir.text())
        tb_layout.addWidget(self.history_panel)

        self.tabs.addTab(tab_batch, "4. Batch Processing & History")

        root_layout.addWidget(self.tabs)

        # Build initial variant cards (default 3)
        self._on_variant_count_changed(3)
        self._setup_social_trio()

        # Status Bar
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready. Drag media files into the Queue to begin.")

    def _check_ffmpeg_status(self):
        if is_ffmpeg_available():
            ver = get_ffmpeg_version()
            short_ver = ver.split()[2] if len(ver.split()) > 2 else "Available"
            self.lbl_ffmpeg_status.setText(f"✓ FFmpeg {short_ver} Ready")
            self.lbl_ffmpeg_status.setObjectName("badgeGreen")
            self.lbl_ffmpeg_status.setStyleSheet("background-color: #064e3b; color: #6ee7b7; border-radius: 4px; padding: 3px 8px; font-weight: 600;")
            self.btn_setup_ffmpeg.setVisible(False)
        else:
            self.lbl_ffmpeg_status.setText("✗ FFmpeg Not Found")
            self.lbl_ffmpeg_status.setStyleSheet("background-color: #7f1d1d; color: #fca5a5; border-radius: 4px; padding: 3px 8px; font-weight: 600;")
            self.btn_setup_ffmpeg.setVisible(True)

    def _auto_setup_ffmpeg(self):
        self.statusBar.showMessage("Downloading FFmpeg essentials build...")
        self.btn_setup_ffmpeg.setEnabled(False)
        success = download_ffmpeg_essentials()
        if success:
            QMessageBox.information(self, "FFmpeg Installed", "FFmpeg and FFprobe have been successfully configured!")
            self._check_ffmpeg_status()
        else:
            QMessageBox.critical(self, "Download Failed", "Failed to download FFmpeg automatically. Please install it manually or place ffmpeg.exe into bin/ folder.")
            self.btn_setup_ffmpeg.setEnabled(True)

    def _browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.txt_out_dir.text())
        if dir_path:
            self.txt_out_dir.setText(dir_path)
            self.history_panel.set_output_dir(dir_path)

    def _open_output_dir(self):
        self.history_panel.set_output_dir(self.txt_out_dir.text())
        self.history_panel.open_output_dir()

    def _on_files_imported(self, file_paths: List[str]):
        count = 0
        for p in file_paths:
            try:
                info = probe_file(p)
                self.media_table.add_media(info)
                count += 1
            except Exception as e:
                self.history_panel.append_log(f"Error inspecting {p}: {e}")
        self.statusBar.showMessage(f"Imported {count} file(s) into queue.")

    def _on_media_selected_for_inspect(self, file_path: str):
        info = self.media_table.get_info(file_path)
        self.tech_panel.display_info(info)

    def _on_variant_count_changed(self, count: int):
        current_len = len(self.variant_cards)
        if count > current_len:
            for i in range(current_len, count):
                card = VariantCard(i, self)
                card.duplicate_requested.connect(self._duplicate_variant_to_all)
                self.variant_cards.append(card)
                self.variant_tab_widget.addTab(card, f"Variant {i + 1}")
        elif count < current_len:
            for i in range(current_len - 1, count - 1, -1):
                card = self.variant_cards.pop()
                self.variant_tab_widget.removeTab(i)
                card.deleteLater()

    def _setup_social_trio(self):
        """Applies high-quality presets for the first 3 variants."""
        if len(self.variant_cards) >= 1:
            c1 = self.variant_cards[0]
            c1.input_name.setText("YouTube HD (1080p 60fps)")
            c1.combo_preset.setCurrentIndex(1)
        if len(self.variant_cards) >= 2:
            c2 = self.variant_cards[1]
            c2.input_name.setText("Instagram Reel (1080x1920)")
            c2.combo_preset.setCurrentIndex(2)
        if len(self.variant_cards) >= 3:
            c3 = self.variant_cards[2]
            c3.input_name.setText("Modern Compact HEVC (H.265)")
            c3.combo_preset.setCurrentIndex(4)

    def _duplicate_variant_to_all(self, source_index: int):
        if source_index >= len(self.variant_cards):
            return
        source_cfg = self.variant_cards[source_index].get_video_config()
        for i, card in enumerate(self.variant_cards):
            if i != source_index:
                card.apply_config(source_cfg)
        QMessageBox.information(self, "Applied", f"Settings from Variant {source_index + 1} applied to all variants!")

    def _start_batch_export(self):
        input_paths = self.media_table.get_all_paths()
        if not input_paths:
            QMessageBox.warning(self, "No Input Files", "Please import at least one video or image into the queue first.")
            self.tabs.setCurrentIndex(0)
            return

        out_dir = self.txt_out_dir.text().strip()
        if not out_dir:
            QMessageBox.warning(self, "Missing Output Directory", "Please select an output folder.")
            return
        os.makedirs(out_dir, exist_ok=True)
        self.history_panel.set_output_dir(out_dir)

        # Global Metadata
        global_meta = self.meta_editor.get_metadata_config()

        # Build job list
        jobs: List[JobItem] = []
        for src_path in input_paths:
            src_name = Path(src_path).stem
            src_info = self.media_table.get_info(src_path) or probe_file(src_path)
            is_video = src_info.get("media_type") == "video"

            for idx, card in enumerate(self.variant_cards):
                if not card.chk_enabled.isChecked():
                    continue

                var_name = card.input_name.text().strip() or f"Variant{idx+1}"
                sanitized_var_name = "".join([c if c.isalnum() or c in "-_" else "_" for c in var_name])

                if is_video:
                    cfg = card.get_video_config()
                    cfg.metadata = global_meta
                    ext = cfg.container
                    out_filename = f"{src_name}_variant{idx+1:02d}_{sanitized_var_name}.{ext}"
                    out_path = os.path.join(out_dir, out_filename)

                    job = JobItem(
                        job_id=f"{src_name}_v{idx+1}",
                        input_file=src_path,
                        variant_index=idx + 1,
                        variant_name=var_name,
                        output_file=out_path,
                        media_type="video",
                        config=cfg,
                        duration_sec=src_info.get("duration", 0.0)
                    )
                else:
                    cfg = card.get_image_config()
                    cfg.metadata = global_meta
                    ext = cfg.output_format.lower()
                    if ext == "jpeg":
                        ext = "jpg"
                    out_filename = f"{src_name}_variant{idx+1:02d}_{sanitized_var_name}.{ext}"
                    out_path = os.path.join(out_dir, out_filename)

                    job = JobItem(
                        job_id=f"{src_name}_v{idx+1}",
                        input_file=src_path,
                        variant_index=idx + 1,
                        variant_name=var_name,
                        output_file=out_path,
                        media_type="image",
                        config=cfg
                    )

                jobs.append(job)

        if not jobs:
            QMessageBox.warning(self, "No Variants Enabled", "Please enable at least one variant to export.")
            self.tabs.setCurrentIndex(1)
            return

        # Setup History Panel Table
        self.tabs.setCurrentIndex(3)  # Switch to Batch tab
        job_row_map: Dict[str, int] = {}
        for j in jobs:
            row = self.history_panel.add_job_row(j.job_id, os.path.basename(j.input_file), j.variant_name, j.source_sha256)
            job_row_map[j.job_id] = row

        self.btn_start_batch.setEnabled(False)
        self.btn_cancel_batch.setEnabled(True)
        self.batch_progress.setValue(0)
        self.statusBar.showMessage(f"Processing batch of {len(jobs)} variant task(s)...")

        # Launch Worker Thread
        self.active_worker = BatchQueueWorker(jobs, self)
        
        def on_job_started(jid):
            row = job_row_map.get(jid)
            if row is not None:
                self.history_panel.update_job_status(row, "Processing", 0.0, "")

        def on_job_prog(jid, pct, msg):
            row = job_row_map.get(jid)
            if row is not None:
                self.history_panel.update_job_status(row, "Processing", pct, msg)

        def on_job_comp(jid, success, out_path, out_sha, out_size):
            row = job_row_map.get(jid)
            if row is not None:
                self.history_panel.complete_job_row(row, success, out_path, out_sha, out_size)

        def on_batch_fin(succ, fail):
            self.btn_start_batch.setEnabled(True)
            self.btn_cancel_batch.setEnabled(False)
            self.batch_progress.setValue(100)
            self.statusBar.showMessage(f"Batch completed: {succ} successful, {fail} failed.")
            QMessageBox.information(
                self, "Batch Complete",
                f"Batch export finished!\n\nSuccessfully generated: {succ} variant(s)\nFailed: {fail}\n\nFiles saved in:\n{out_dir}"
            )

        def on_log(msg):
            self.history_panel.append_log(msg)

        self.active_worker.job_started.connect(on_job_started)
        self.active_worker.job_progress.connect(on_job_prog)
        self.active_worker.job_completed.connect(on_job_comp)
        self.active_worker.batch_finished.connect(on_batch_fin)
        self.active_worker.log_message.connect(on_log)

        self.active_worker.start()

    def _cancel_batch_export(self):
        if self.active_worker:
            self.statusBar.showMessage("Cancelling batch processing...")
            self.active_worker.cancel_batch()
            self.btn_cancel_batch.setEnabled(False)
