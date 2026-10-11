"""
Modern Dark Theme QSS Stylesheet for Media Variant & Metadata Studio
"""

DARK_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #0b0f19;
    color: #f1f5f9;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

QWidget {
    color: #f1f5f9;
    background-color: transparent;
}

/* Group Boxes & Panels */
QGroupBox {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    margin-top: 18px;
    padding-top: 14px;
    font-weight: 600;
    font-size: 13px;
    color: #93c5fd;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    background-color: #1f2937;
    border-radius: 4px;
    color: #60a5fa;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #1f2937;
    border-radius: 8px;
    background-color: #111827;
    top: -1px;
}

QTabBar::tab {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 10px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #1e293b;
    color: #38bdf8;
    font-weight: 600;
    border-bottom: 2px solid #38bdf8;
}

QTabBar::tab:hover:!selected {
    background-color: #1e293b;
    color: #cbd5e1;
}

/* Push Buttons */
QPushButton {
    background-color: #1f2937;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 7px 16px;
    color: #f3f4f6;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #374151;
    border-color: #4b5563;
}

QPushButton:pressed {
    background-color: #111827;
}

QPushButton:disabled {
    background-color: #111827;
    color: #4b5563;
    border-color: #1f2937;
}

QPushButton#primaryBtn {
    background-color: #2563eb;
    border: 1px solid #3b82f6;
    color: #ffffff;
    font-weight: 600;
    padding: 8px 20px;
}

QPushButton#primaryBtn:hover {
    background-color: #1d4ed8;
}

QPushButton#successBtn {
    background-color: #059669;
    border: 1px solid #10b981;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#successBtn:hover {
    background-color: #047857;
}

QPushButton#dangerBtn {
    background-color: #dc2626;
    border: 1px solid #ef4444;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#dangerBtn:hover {
    background-color: #b91c1c;
}

/* Input Fields & Combos */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit, QPlainTextEdit {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
    color: #f8fafc;
    selection-background-color: #2563eb;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #38bdf8;
    background-color: #111e38;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #334155;
}

QComboBox QAbstractItemView {
    background-color: #0f172a;
    border: 1px solid #334155;
    selection-background-color: #2563eb;
    color: #f8fafc;
    padding: 4px;
}

/* Tables */
QTableWidget, QTableView {
    background-color: #0b0f19;
    border: 1px solid #1f2937;
    gridline-color: #1e293b;
    border-radius: 6px;
    selection-background-color: #1e3a8a;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #111827;
    color: #94a3b8;
    padding: 8px;
    border: 0;
    border-bottom: 1px solid #334155;
    font-weight: 600;
}

/* Progress Bar */
QProgressBar {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 6px;
    text-align: center;
    color: #ffffff;
    font-weight: 600;
    height: 18px;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #38bdf8);
    border-radius: 5px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #0b0f19;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Labels */
QLabel {
    color: #e2e8f0;
}

QLabel#metaHeader {
    color: #38bdf8;
    font-weight: 600;
    font-size: 14px;
}

QLabel#badgeGreen {
    background-color: #064e3b;
    color: #6ee7b7;
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: 600;
    font-size: 11px;
}

QLabel#badgeRed {
    background-color: #7f1d1d;
    color: #fca5a5;
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: 600;
    font-size: 11px;
}
"""
