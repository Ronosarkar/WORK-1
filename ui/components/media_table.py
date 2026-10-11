import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QAbstractItemView, QLabel
)
from PySide6.QtCore import Qt, Signal
from typing import Dict, Any, List

class MediaTable(QWidget):
    file_selected = Signal(str)      # Emits selected filepath for inspection
    file_count_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.files_data: Dict[str, Dict[str, Any]] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Toolbar
        bar = QHBoxLayout()
        self.lbl_count = QLabel("Imported Media: 0 items", self)
        self.lbl_count.setStyleSheet("font-weight: 600; color: #94a3b8;")
        
        self.btn_remove = QPushButton("Remove Selected", self)
        self.btn_remove.clicked.connect(self.remove_selected)
        
        self.btn_clear = QPushButton("Clear All", self)
        self.btn_clear.clicked.connect(self.clear_all)

        bar.addWidget(self.lbl_count)
        bar.addStretch()
        bar.addWidget(self.btn_remove)
        bar.addWidget(self.btn_clear)
        layout.addLayout(bar)

        # Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Type", "Filename", "Resolution", "Duration", "FPS", "Bitrate", "File Size", "Full Path"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        layout.addWidget(self.table)

    def add_media(self, info: Dict[str, Any]):
        path = info["file_path"]
        if path in self.files_data:
            return  # Already present

        self.files_data[path] = info
        row = self.table.rowCount()
        self.table.insertRow(row)

        mtype = info.get("media_type", "video")
        type_icon = "🎬 Video" if mtype == "video" else "🖼️ Image"
        fname = info.get("file_name", "")
        
        if mtype == "video":
            res = info.get("video", {}).get("resolution", "-")
            dur = info.get("duration_formatted", "-")
            fps = f"{info.get('video', {}).get('fps', 0)} fps"
            br = f"{info.get('bitrate_kbps', 0)} kbps" if info.get('bitrate_kbps') else "Variable"
        else:
            res = info.get("resolution", "-")
            dur = "N/A"
            fps = "N/A"
            br = info.get("color_mode", "-")

        size_str = info.get("file_size_formatted", "-")

        self.table.setItem(row, 0, QTableWidgetItem(type_icon))
        self.table.setItem(row, 1, QTableWidgetItem(fname))
        self.table.setItem(row, 2, QTableWidgetItem(res))
        self.table.setItem(row, 3, QTableWidgetItem(dur))
        self.table.setItem(row, 4, QTableWidgetItem(fps))
        self.table.setItem(row, 5, QTableWidgetItem(br))
        self.table.setItem(row, 6, QTableWidgetItem(size_str))
        
        path_item = QTableWidgetItem(path)
        self.table.setItem(row, 7, path_item)

        self._update_count()

        # Automatically select the first added row
        if row == 0:
            self.table.selectRow(0)

    def _on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            path_item = self.table.item(row, 7)
            if path_item:
                self.file_selected.emit(path_item.text())

    def remove_selected(self):
        selected_rows = sorted([r.row() for r in self.table.selectionModel().selectedRows()], reverse=True)
        for r in selected_rows:
            path_item = self.table.item(r, 7)
            if path_item and path_item.text() in self.files_data:
                del self.files_data[path_item.text()]
            self.table.removeRow(r)
        self._update_count()

    def clear_all(self):
        self.table.setRowCount(0)
        self.files_data.clear()
        self._update_count()

    def _update_count(self):
        cnt = self.table.rowCount()
        self.lbl_count.setText(f"Imported Media: {cnt} item{'s' if cnt != 1 else ''}")
        self.file_count_changed.emit(cnt)

    def get_all_paths(self) -> List[str]:
        return list(self.files_data.keys())

    def get_info(self, path: str) -> Optional[Dict[str, Any]]:
        return self.files_data.get(path)
