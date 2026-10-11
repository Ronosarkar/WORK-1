import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QGridLayout, QPushButton, QApplication, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from typing import Dict, Any, Optional

class TechInfoPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Technical Integrity & Fingerprint Inspector", parent)
        self.current_info: Optional[Dict[str, Any]] = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 18, 14, 14)
        main_layout.setSpacing(10)

        # SHA-256 Hash Card
        hash_box = QFrame(self)
        hash_box.setStyleSheet("background-color: #0b0f19; border: 1px solid #1f2937; border-radius: 6px; padding: 6px;")
        hash_layout = QVBoxLayout(hash_box)
        hash_layout.setSpacing(4)
        
        lbl_title = QLabel("CRYPTOGRAPHIC SHA-256 CHECKSUM (VERIFICATION ONLY):", self)
        lbl_title.setStyleSheet("font-size: 11px; font-weight: 600; color: #38bdf8;")
        
        row_hash = QHBoxLayout()
        self.sha256_label = QLabel("No file selected", self)
        self.sha256_label.setStyleSheet("font-family: Consolas, monospace; font-size: 12px; color: #a5f3fc;")
        self.sha256_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        self.btn_copy_hash = QPushButton("📋 Copy Hash", self)
        self.btn_copy_hash.setStyleSheet("padding: 4px 10px; font-size: 11px;")
        self.btn_copy_hash.clicked.connect(self.copy_hash)
        
        row_hash.addWidget(self.sha256_label, 1)
        row_hash.addWidget(self.btn_copy_hash)
        hash_layout.addWidget(lbl_title)
        hash_layout.addLayout(row_hash)
        main_layout.addWidget(hash_box)

        # Grid of Technical Specs
        grid = QGridLayout()
        grid.setSpacing(8)

        def make_row(title: str, default_val: str = "-"):
            lbl_k = QLabel(f"<b>{title}:</b>", self)
            lbl_k.setStyleSheet("color: #94a3b8; font-size: 12px;")
            lbl_v = QLabel(default_val, self)
            lbl_v.setStyleSheet("color: #f8fafc; font-size: 12px;")
            lbl_v.setTextInteractionFlags(Qt.TextSelectableByMouse)
            return lbl_k, lbl_v

        self.k_fname, self.v_fname = make_row("Filename")
        self.k_size, self.v_size = make_row("File Size")
        self.k_dur, self.v_dur = make_row("Duration")
        self.k_res, self.v_res = make_row("Resolution & Ratio")
        self.k_fps, self.v_fps = make_row("Framerate (FPS)")
        self.k_vcodec, self.v_vcodec = make_row("Video Codec")
        self.k_vbitrate, self.v_vbitrate = make_row("Video Bitrate")
        self.k_acodec, self.v_acodec = make_row("Audio Codec")
        self.k_achannels, self.v_achannels = make_row("Audio Layout")
        self.k_asample, self.v_asample = make_row("Sample Rate")
        self.k_abitrate, self.v_abitrate = make_row("Audio Bitrate")
        self.k_meta, self.v_meta = make_row("Existing Metadata")

        # Row 0
        grid.addWidget(self.k_fname, 0, 0)
        grid.addWidget(self.v_fname, 0, 1)
        grid.addWidget(self.k_size, 0, 2)
        grid.addWidget(self.v_size, 0, 3)

        # Row 1
        grid.addWidget(self.k_dur, 1, 0)
        grid.addWidget(self.v_dur, 1, 1)
        grid.addWidget(self.k_res, 1, 2)
        grid.addWidget(self.v_res, 1, 3)

        # Row 2
        grid.addWidget(self.k_fps, 2, 0)
        grid.addWidget(self.v_fps, 2, 1)
        grid.addWidget(self.k_vcodec, 2, 2)
        grid.addWidget(self.v_vcodec, 2, 3)

        # Row 3
        grid.addWidget(self.k_vbitrate, 3, 0)
        grid.addWidget(self.v_vbitrate, 3, 1)
        grid.addWidget(self.k_acodec, 3, 2)
        grid.addWidget(self.v_acodec, 3, 3)

        # Row 4
        grid.addWidget(self.k_achannels, 4, 0)
        grid.addWidget(self.v_achannels, 4, 1)
        grid.addWidget(self.k_asample, 4, 2)
        grid.addWidget(self.v_asample, 4, 3)

        # Row 5
        grid.addWidget(self.k_abitrate, 5, 0)
        grid.addWidget(self.v_abitrate, 5, 1)
        grid.addWidget(self.k_meta, 5, 2)
        grid.addWidget(self.v_meta, 5, 3)

        main_layout.addLayout(grid)

    def copy_hash(self):
        text = self.sha256_label.text()
        if text and text != "No file selected":
            QApplication.clipboard().setText(text)

    def display_info(self, info: Optional[Dict[str, Any]]):
        self.current_info = info
        if not info:
            self.sha256_label.setText("No file selected")
            self.v_fname.setText("-")
            self.v_size.setText("-")
            self.v_dur.setText("-")
            self.v_res.setText("-")
            self.v_fps.setText("-")
            self.v_vcodec.setText("-")
            self.v_vbitrate.setText("-")
            self.v_acodec.setText("-")
            self.v_achannels.setText("-")
            self.v_asample.setText("-")
            self.v_abitrate.setText("-")
            self.v_meta.setText("-")
            return

        self.sha256_label.setText(info.get("sha256", "N/A"))
        self.v_fname.setText(info.get("file_name", "-"))
        self.v_size.setText(f"{info.get('file_size_formatted', '-')} ({info.get('file_size', 0):,} bytes)")

        media_type = info.get("media_type", "video")
        if media_type == "video":
            self.v_dur.setText(info.get("duration_formatted", "-"))
            vid = info.get("video", {})
            self.v_res.setText(f"{vid.get('resolution', '-')} ({vid.get('aspect_ratio', '-')})")
            self.v_fps.setText(f"{vid.get('fps', '-')} fps")
            self.v_vcodec.setText(f"{vid.get('codec', '-')} ({vid.get('pixel_format', '-')})")
            self.v_vbitrate.setText(f"{vid.get('bitrate_kbps', '-')} kbps" if vid.get('bitrate_kbps') else "Auto / Variable")

            aud = info.get("audio", {})
            self.v_acodec.setText(aud.get("codec", "-"))
            self.v_achannels.setText(f"{aud.get('channels', 0)} ch ({aud.get('channel_layout', '-')})")
            self.v_asample.setText(f"{aud.get('sample_rate', 0)} Hz" if aud.get('sample_rate') else "-")
            self.v_abitrate.setText(f"{aud.get('bitrate_kbps', '-')} kbps" if aud.get('bitrate_kbps') else "-")

            tags = info.get("metadata", {})
            tag_summary = ", ".join([f"{k}={v}" for k, v in list(tags.items())[:3]])
            self.v_meta.setText(tag_summary if tag_summary else "No embedded tags")

        else:  # Image
            self.v_dur.setText("N/A (Still Image)")
            self.v_res.setText(info.get("resolution", "-"))
            self.v_fps.setText("N/A")
            self.v_vcodec.setText(f"{info.get('format', '-')} ({info.get('color_mode', '-')})")
            self.v_vbitrate.setText(info.get("color_profile", "sRGB"))
            self.v_acodec.setText("N/A")
            self.v_achannels.setText("N/A")
            self.v_asample.setText("N/A")
            self.v_abitrate.setText("N/A")
            exif_count = len(info.get("exif", {}))
            self.v_meta.setText(f"{exif_count} EXIF tags detected" if exif_count > 0 else "None")
