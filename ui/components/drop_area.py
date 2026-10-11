import os
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QFileDialog
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent

class DropArea(QFrame):
    files_selected = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropArea")
        self.setStyleSheet("""
            QFrame#dropArea {
                border: 2px dashed #3b82f6;
                border-radius: 12px;
                background-color: #0f172a;
                min-height: 110px;
            }
            QFrame#dropArea:hover {
                border-color: #60a5fa;
                background-color: #1e293b;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(6)

        self.icon_label = QLabel("📥", self)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 32px;")

        self.title_label = QLabel("Drag & Drop Media Files Here", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #f8fafc;")

        self.subtitle_label = QLabel("Supports MP4, MOV, MKV, WebM, JPG, PNG, WebP (or click to browse)", self)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("font-size: 11px; color: #94a3b8;")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Video or Image Files",
                "",
                "Media Files (*.mp4 *.mov *.mkv *.webm *.avi *.m4v *.jpg *.jpeg *.png *.webp);;All Files (*.*)"
            )
            if files:
                self.files_selected.emit(files)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame#dropArea {
                    border: 2px dashed #10b981;
                    border-radius: 12px;
                    background-color: #1e3a8a;
                    min-height: 110px;
                }
            """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame#dropArea {
                border: 2px dashed #3b82f6;
                border-radius: 12px;
                background-color: #0f172a;
                min-height: 110px;
            }
            QFrame#dropArea:hover {
                border-color: #60a5fa;
                background-color: #1e293b;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        self.dragLeaveEvent(None)
        urls = event.mimeData().urls()
        files = []
        for url in urls:
            path = url.toLocalFile()
            if os.path.isfile(path):
                files.append(path)
        if files:
            self.files_selected.emit(files)
