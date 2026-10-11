import os
import subprocess
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QPlainTextEdit, QHeaderView, QAbstractItemView,
    QProgressBar, QGroupBox
)
from PySide6.QtCore import Qt
from typing import Dict, Any

class HistoryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.output_directory = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Batch Queue Table Box
        table_box = QGroupBox("Batch Queue & Technical Verification History", self)
        t_layout = QVBoxLayout(table_box)
        t_layout.setContentsMargins(10, 14, 10, 10)

        self.table = QTableWidget(self)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Status", "Source File", "Variant", "Progress", "Output Size", "Source SHA-256", "Output SHA-256", "Output Path"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)
        t_layout.addWidget(self.table)

        # Action Toolbar
        bar = QHBoxLayout()
        self.btn_open_folder = QPushButton("📂 Open Output Folder", self)
        self.btn_open_folder.clicked.connect(self.open_output_dir)

        self.btn_reveal_file = QPushButton("🔍 Reveal Selected File", self)
        self.btn_reveal_file.clicked.connect(self.reveal_selected)

        self.btn_clear_log = QPushButton("Clear Logs", self)
        self.btn_clear_log.clicked.connect(self.clear_logs)

        bar.addWidget(self.btn_open_folder)
        bar.addWidget(self.btn_reveal_file)
        bar.addStretch()
        bar.addWidget(self.btn_clear_log)
        t_layout.addLayout(bar)

        layout.addWidget(table_box)

        # Log Console Box
        log_box = QGroupBox("Live Processing Log", self)
        l_layout = QVBoxLayout(log_box)
        l_layout.setContentsMargins(10, 14, 10, 10)

        self.log_view = QPlainTextEdit(self)
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0b0f19;
                color: #a5f3fc;
                font-family: Consolas, monospace;
                font-size: 11px;
                border: 1px solid #1f2937;
            }
        """)
        self.log_view.setMaximumHeight(150)
        l_layout.addWidget(self.log_view)

        layout.addWidget(log_box)

    def set_output_dir(self, path: str):
        self.output_directory = path

    def add_job_row(self, job_id: str, src_name: str, var_name: str, src_sha: str) -> int:
        row = self.table.rowCount()
        self.table.insertRow(row)

        item_status = QTableWidgetItem("Queued")
        item_status.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, item_status)

        self.table.setItem(row, 1, QTableWidgetItem(src_name))
        self.table.setItem(row, 2, QTableWidgetItem(var_name))
        self.table.setItem(row, 3, QTableWidgetItem("0%"))
        self.table.setItem(row, 4, QTableWidgetItem("-"))
        self.table.setItem(row, 5, QTableWidgetItem(src_sha[:12] + "..." if src_sha else "-"))
        self.table.setItem(row, 6, QTableWidgetItem("-"))
        self.table.setItem(row, 7, QTableWidgetItem("-"))
        return row

    def update_job_status(self, row: int, status: str, pct: float, msg: str):
        if row < self.table.rowCount():
            item_status = self.table.item(row, 0)
            if item_status:
                item_status.setText(status)
                if status == "Completed":
                    item_status.setForeground(Qt.green)
                elif status == "Failed":
                    item_status.setForeground(Qt.red)
                elif status == "Processing":
                    item_status.setForeground(Qt.cyan)

            item_prog = self.table.item(row, 3)
            if item_prog:
                item_prog.setText(f"{pct:.0f}%")

    def complete_job_row(self, row: int, success: bool, out_path: str, out_sha: str, out_size: int):
        if row < self.table.rowCount():
            status_text = "Completed" if success else "Failed"
            self.update_job_status(row, status_text, 100.0 if success else 0.0, "")
            
            if success:
                size_mb = f"{out_size / (1024 * 1024):.2f} MB" if out_size >= 1024*1024 else f"{out_size / 1024:.1f} KB"
                self.table.setItem(row, 4, QTableWidgetItem(size_mb))
                self.table.setItem(row, 6, QTableWidgetItem(out_sha[:12] + "..." if out_sha else "-"))
                self.table.setItem(row, 7, QTableWidgetItem(out_path))

    def append_log(self, text: str):
        self.log_view.appendPlainText(text)

    def clear_logs(self):
        self.log_view.clear()
        self.table.setRowCount(0)

    def open_output_dir(self):
        if self.output_directory and os.path.isdir(self.output_directory):
            if sys.platform == "win32":
                os.startfile(self.output_directory)
            else:
                subprocess.Popen(["xdg-open", self.output_directory])

    def reveal_selected(self):
        selected = self.table.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            path_item = self.table.item(row, 7)
            if path_item:
                path = path_item.text()
                if os.path.isfile(path):
                    if sys.platform == "win32":
                        subprocess.run(["explorer", "/select,", os.path.normpath(path)])
                    else:
                        subprocess.Popen(["xdg-open", os.path.dirname(path)])
