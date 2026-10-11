import os
import sys
import traceback
from pathlib import Path

# Ensure project root is in python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from ui.main_window import MainWindow

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler to prevent silent crash and show error dialog."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print("FATAL ERROR:\n", err_msg, file=sys.stderr)
    try:
        QMessageBox.critical(None, "Application Error", f"An unexpected error occurred:\n\n{err_msg}")
    except Exception:
        pass

sys.excepthook = handle_exception

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Media Variant & Metadata Studio")
    app.setOrganizationName("MediaStudio")

    window = MainWindow()
    window.show()
    window.raise_()
    window.activateWindow()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
