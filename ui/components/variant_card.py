import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QComboBox, QSpinBox, QSlider, QCheckBox,
    QPushButton, QGroupBox, QStackedWidget, QFrame
)
from PySide6.QtCore import Qt, Signal
from core.variant_models import VideoVariantConfig, ImageVariantConfig, MetadataConfig

class VariantCard(QFrame):
    duplicate_requested = Signal(int)  # index of variant to duplicate across all

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("variantCard")
        self.setStyleSheet("""
            QFrame#variantCard {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Header Bar: Enable Checkbox, Name, Preset Selector, Duplicate Button
        header = QHBoxLayout()
        self.chk_enabled = QCheckBox(f"Variant {index + 1}", self)
        self.chk_enabled.setChecked(True)
        self.chk_enabled.setStyleSheet("font-weight: 700; font-size: 13px; color: #38bdf8;")

        self.input_name = QLineEdit(f"Variant {index + 1}", self)
        self.input_name.setMaximumWidth(160)

        lbl_preset = QLabel("Preset:", self)
        lbl_preset.setStyleSheet("color: #94a3b8;")
        self.combo_preset = QComboBox(self)
        self.combo_preset.addItems([
            "Custom Settings",
            "YouTube High-Quality (1080p 60fps)",
            "Social Reel / Shorts (1080x1920 30fps)",
            "Square Social Feed (1080x1080 30fps)",
            "Compact HEVC / H.265 (High Efficiency)",
            "Lossless Stream Copy (Metadata Only, 0 Re-encode)"
        ])
        self.combo_preset.currentIndexChanged.connect(self._on_preset_selected)

        self.btn_duplicate = QPushButton("Apply to All Variants", self)
        self.btn_duplicate.setStyleSheet("font-size: 11px; padding: 4px 8px;")
        self.btn_duplicate.clicked.connect(lambda: self.duplicate_requested.emit(self.index))

        header.addWidget(self.chk_enabled)
        header.addWidget(self.input_name)
        header.addWidget(lbl_preset)
        header.addWidget(self.combo_preset, 1)
        header.addWidget(self.btn_duplicate)
        layout.addLayout(header)

        # Process Mode: Re-encode vs Stream Copy
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Processing Mode:"))
        self.combo_mode = QComboBox(self)
        self.combo_mode.addItems(["Re-encode (Quality Control & Scaler)", "Stream Copy (100% Lossless, Instant)"])
        self.combo_mode.currentIndexChanged.connect(self._on_mode_changed)
        mode_row.addWidget(self.combo_mode, 1)
        
        mode_row.addWidget(QLabel("Container:"))
        self.combo_container = QComboBox(self)
        self.combo_container.addItems(["mp4", "mov", "mkv", "webm"])
        mode_row.addWidget(self.combo_container)
        layout.addLayout(mode_row)

        # Video Settings Box
        self.video_box = QGroupBox("Video Settings (Fidelity Prioritized)", self)
        v_grid = QGridLayout(self.video_box)
        v_grid.setSpacing(8)

        # Row 0: Codec & Resolution
        v_grid.addWidget(QLabel("Video Codec:"), 0, 0)
        self.combo_vcodec = QComboBox(self)
        self.combo_vcodec.addItems(["libx264 (H.264 - Universal)", "libx265 (HEVC - Compact)", "libvpx-vp9 (WebM)", "copy"])
        v_grid.addWidget(self.combo_vcodec, 0, 1)

        v_grid.addWidget(QLabel("Resolution:"), 0, 2)
        self.combo_res = QComboBox(self)
        self.combo_res.addItems([
            "Original Resolution",
            "1080p Full HD (1920x1080)",
            "720p HD (1280x720)",
            "4K Ultra HD (3840x2160)",
            "Vertical 9:16 (1080x1920 Reel/Short)",
            "Square 1:1 (1080x1080)",
            "Custom"
        ])
        v_grid.addWidget(self.combo_res, 0, 3)

        # Row 1: Aspect Fit & Framerate
        v_grid.addWidget(QLabel("Aspect Ratio Fit:"), 1, 0)
        self.combo_fit = QComboBox(self)
        self.combo_fit.addItems(["Pillarbox/Letterbox (Safe Padding)", "Safe Center Crop (Fill Screen)"])
        v_grid.addWidget(self.combo_fit, 1, 1)

        v_grid.addWidget(QLabel("Framerate (FPS):"), 1, 2)
        self.combo_fps = QComboBox(self)
        self.combo_fps.addItems(["Original FPS", "60 FPS", "30 FPS", "24 FPS (Cinematic)"])
        v_grid.addWidget(self.combo_fps, 1, 3)

        # Row 2: Quality CRF vs Bitrate
        v_grid.addWidget(QLabel("Rate Control:"), 2, 0)
        self.combo_quality_mode = QComboBox(self)
        self.combo_quality_mode.addItems(["CRF (Visually Lossless)", "Target Bitrate (kbps)"])
        v_grid.addWidget(self.combo_quality_mode, 2, 1)

        crf_row = QHBoxLayout()
        self.slider_crf = QSlider(Qt.Horizontal, self)
        self.slider_crf.setRange(14, 28)
        self.slider_crf.setValue(18)  # 18 is visually lossless
        self.lbl_crf_val = QLabel("CRF 18 (Visually Lossless)", self)
        self.lbl_crf_val.setStyleSheet("color: #38bdf8; font-weight: 600;")
        self.slider_crf.valueChanged.connect(self._on_crf_changed)
        crf_row.addWidget(self.slider_crf)
        crf_row.addWidget(self.lbl_crf_val)
        v_grid.addLayout(crf_row, 2, 2, 1, 2)

        # Row 3: Keyframe / GOP
        v_grid.addWidget(QLabel("GOP / Keyframe:"), 3, 0)
        self.combo_gop = QComboBox(self)
        self.combo_gop.addItems(["2.0 seconds (Recommended for Web/Social)", "Auto (Source default)", "1.0 second (Fast Seek)"])
        v_grid.addWidget(self.combo_gop, 3, 1)

        layout.addWidget(self.video_box)

        # Audio Settings Box
        self.audio_box = QGroupBox("Audio Settings", self)
        a_grid = QGridLayout(self.audio_box)
        a_grid.setSpacing(8)

        a_grid.addWidget(QLabel("Audio Codec:"), 0, 0)
        self.combo_acodec = QComboBox(self)
        self.combo_acodec.addItems(["aac (High Quality)", "copy (Pass-Through)", "mp3", "opus"])
        a_grid.addWidget(self.combo_acodec, 0, 1)

        a_grid.addWidget(QLabel("Audio Bitrate:"), 0, 2)
        self.combo_abitrate = QComboBox(self)
        self.combo_abitrate.addItems(["256 kbps (Studio Quality)", "320 kbps (Maximum)", "192 kbps", "128 kbps"])
        a_grid.addWidget(self.combo_abitrate, 0, 3)

        a_grid.addWidget(QLabel("Channels:"), 1, 0)
        self.combo_achannels = QComboBox(self)
        self.combo_achannels.addItems(["Keep Source Channels", "Stereo (2 Channels)", "Mono (1 Channel)"])
        a_grid.addWidget(self.combo_achannels, 1, 1)

        self.chk_loudnorm = QCheckBox("Loudness Normalization (EBU R128)", self)
        self.chk_loudnorm.setToolTip("Normalizes volume to platform streaming standards without clipping")
        a_grid.addWidget(self.chk_loudnorm, 1, 2, 1, 2)

        layout.addWidget(self.audio_box)

        # Image Settings Box
        self.image_box = QGroupBox("Image Output Settings", self)
        i_grid = QGridLayout(self.image_box)
        i_grid.setSpacing(8)

        i_grid.addWidget(QLabel("Format:"), 0, 0)
        self.combo_img_fmt = QComboBox(self)
        self.combo_img_fmt.addItems(["JPEG", "PNG (Lossless)", "WebP"])
        i_grid.addWidget(self.combo_img_fmt, 0, 1)

        i_grid.addWidget(QLabel("JPEG/WebP Quality:"), 0, 2)
        self.spin_img_quality = QSpinBox(self)
        self.spin_img_quality.setRange(1, 100)
        self.spin_img_quality.setValue(92)
        i_grid.addWidget(self.spin_img_quality, 0, 3)

        self.chk_strip_exif = QCheckBox("Remove EXIF metadata on export", self)
        self.chk_preserve_icc = QCheckBox("Preserve Color Profile (ICC)", self)
        self.chk_preserve_icc.setChecked(True)
        i_grid.addWidget(self.chk_strip_exif, 1, 0, 1, 2)
        i_grid.addWidget(self.chk_preserve_icc, 1, 2, 1, 2)

        layout.addWidget(self.image_box)

    def _on_crf_changed(self, val: int):
        desc = "Visually Lossless" if val <= 18 else ("High Quality" if val <= 23 else "Standard")
        self.lbl_crf_val.setText(f"CRF {val} ({desc})")

    def _on_mode_changed(self, idx: int):
        is_copy = idx == 1
        self.video_box.setEnabled(not is_copy)
        self.audio_box.setEnabled(not is_copy)

    def _on_preset_selected(self, idx: int):
        if idx == 1:  # YouTube 1080p 60fps
            self.combo_mode.setCurrentIndex(0)
            self.combo_vcodec.setCurrentIndex(0)  # libx264
            self.combo_res.setCurrentIndex(1)     # 1080p
            self.combo_fps.setCurrentIndex(1)     # 60fps
            self.slider_crf.setValue(18)
            self.combo_acodec.setCurrentIndex(0)  # aac
            self.combo_abitrate.setCurrentIndex(0) # 256k
        elif idx == 2:  # Reel 1080x1920 30fps
            self.combo_mode.setCurrentIndex(0)
            self.combo_vcodec.setCurrentIndex(0)
            self.combo_res.setCurrentIndex(4)     # Vertical 9:16
            self.combo_fps.setCurrentIndex(2)     # 30fps
            self.combo_fit.setCurrentIndex(0)     # Pillarbox
            self.slider_crf.setValue(18)
        elif idx == 3:  # Square 1080x1080
            self.combo_mode.setCurrentIndex(0)
            self.combo_vcodec.setCurrentIndex(0)
            self.combo_res.setCurrentIndex(5)     # Square
            self.combo_fps.setCurrentIndex(2)     # 30fps
            self.slider_crf.setValue(18)
        elif idx == 4:  # Compact HEVC
            self.combo_mode.setCurrentIndex(0)
            self.combo_vcodec.setCurrentIndex(1)  # libx265
            self.combo_res.setCurrentIndex(0)     # Original
            self.slider_crf.setValue(20)
        elif idx == 5:  # Lossless Stream Copy
            self.combo_mode.setCurrentIndex(1)

    def get_video_config(self) -> VideoVariantConfig:
        cfg = VideoVariantConfig()
        cfg.name = self.input_name.text().strip() or f"Variant {self.index + 1}"
        cfg.enabled = self.chk_enabled.isChecked()
        cfg.process_mode = "stream_copy" if self.combo_mode.currentIndex() == 1 else "reencode"
        cfg.container = self.combo_container.currentText()

        # Codec
        v_idx = self.combo_vcodec.currentIndex()
        cfg.video_codec = ["libx264", "libx265", "libvpx-vp9", "copy"][v_idx]

        # Resolution
        res_idx = self.combo_res.currentIndex()
        res_map = ["original", "1080p", "720p", "4k_2160p", "1080x1920_vertical", "1080x1080_square", "custom"]
        cfg.resolution_preset = res_map[res_idx]
        cfg.aspect_fit_mode = "pad_letterbox" if self.combo_fit.currentIndex() == 0 else "safe_crop"

        # FPS
        fps_idx = self.combo_fps.currentIndex()
        cfg.fps_preset = ["original", "60", "30", "24"][fps_idx]

        # Quality
        cfg.quality_mode = "crf" if self.combo_quality_mode.currentIndex() == 0 else "bitrate"
        cfg.crf_value = self.slider_crf.value()

        # GOP
        gop_idx = self.combo_gop.currentIndex()
        cfg.gop_keyframe_sec = [2.0, -1.0, 1.0][gop_idx]

        # Audio
        a_idx = self.combo_acodec.currentIndex()
        cfg.audio_codec = ["aac", "copy", "mp3", "opus"][a_idx]
        br_idx = self.combo_abitrate.currentIndex()
        cfg.audio_bitrate_kbps = [256, 320, 192, 128][br_idx]
        ch_idx = self.combo_achannels.currentIndex()
        cfg.audio_channels = ["keep", "stereo", "mono"][ch_idx]
        cfg.volume_normalize = self.chk_loudnorm.isChecked()

        return cfg

    def get_image_config(self) -> ImageVariantConfig:
        cfg = ImageVariantConfig()
        cfg.name = self.input_name.text().strip() or f"Variant {self.index + 1}"
        cfg.enabled = self.chk_enabled.isChecked()
        cfg.output_format = ["JPEG", "PNG", "WEBP"][self.combo_img_fmt.currentIndex()]
        cfg.jpeg_quality = self.spin_img_quality.value()
        cfg.strip_exif = self.chk_strip_exif.isChecked()
        cfg.preserve_icc = self.chk_preserve_icc.isChecked()
        return cfg

    def apply_config(self, other_cfg: VideoVariantConfig):
        """Copies configuration from another variant config."""
        self.combo_mode.setCurrentIndex(1 if other_cfg.process_mode == "stream_copy" else 0)
        idx_c = self.combo_container.findText(other_cfg.container)
        if idx_c >= 0:
            self.combo_container.setCurrentIndex(idx_c)

        codec_map = {"libx264": 0, "libx265": 1, "libvpx-vp9": 2, "copy": 3}
        if other_cfg.video_codec in codec_map:
            self.combo_vcodec.setCurrentIndex(codec_map[other_cfg.video_codec])

        res_map = {"original": 0, "1080p": 1, "720p": 2, "4k_2160p": 3, "1080x1920_vertical": 4, "1080x1080_square": 5, "custom": 6}
        if other_cfg.resolution_preset in res_map:
            self.combo_res.setCurrentIndex(res_map[other_cfg.resolution_preset])

        self.slider_crf.setValue(other_cfg.crf_value)
        self.chk_loudnorm.setChecked(other_cfg.volume_normalize)
