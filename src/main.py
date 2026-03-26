import sys
import os

# Resolve paths for both normal run and PyInstaller bundle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, "frozen", False):
    # Running inside a PyInstaller bundle
    _ROOT = sys._MEIPASS
else:
    # Running from source: src/ → parent is project root
    _ROOT = os.path.join(BASE_DIR, "..")

DATA_DIR = os.path.join(_ROOT, "data")
DB_PATH = os.path.join(DATA_DIR, "legal_english.db")
TERMS_JSON = os.path.join(_ROOT, "data", "terms.json")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

# Support both `python -m src.main` and direct `python src/main.py` / PyInstaller
try:
    from .database.db_manager import DBManager
    from .algorithms.spaced_repetition import SpacedRepetitionScheduler
    from .gui.main_window import MainWindow
except ImportError:
    sys.path.insert(0, BASE_DIR)
    from database.db_manager import DBManager
    from algorithms.spaced_repetition import SpacedRepetitionScheduler
    from gui.main_window import MainWindow


DARK_STYLESHEET = """
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #1e1e2e;
}

QTabWidget::pane {
    border: 1px solid #313244;
    background-color: #1e1e2e;
}

QTabBar::tab {
    background-color: #181825;
    color: #a6adc8;
    padding: 8px 20px;
    border: 1px solid #313244;
    border-bottom: none;
    min-width: 100px;
}

QTabBar::tab:selected {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border-top: 2px solid #89b4fa;
}

QTabBar::tab:hover:!selected {
    background-color: #24273a;
}

QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 16px;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #45475a;
}

QPushButton:pressed {
    background-color: #585b70;
}

QPushButton:disabled {
    background-color: #24273a;
    color: #585b70;
}

QPushButton#knowBtn {
    background-color: #1e3a2a;
    color: #a6e3a1;
    border: 1px solid #40a85a;
}
QPushButton#knowBtn:hover {
    background-color: #2a5a3a;
}

QPushButton#dontKnowBtn {
    background-color: #3a1e1e;
    color: #f38ba8;
    border: 1px solid #a83a3a;
}
QPushButton#dontKnowBtn:hover {
    background-color: #5a2a2a;
}

QPushButton#matchBtn {
    background-color: #24273a;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    text-align: center;
    padding: 6px 10px;
}
QPushButton#matchBtn:hover {
    background-color: #313244;
}

QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 28px;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    selection-background-color: #45475a;
    border: 1px solid #45475a;
}

QSpinBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 28px;
}

QLineEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 14px;
}

QLineEdit:focus {
    border: 1px solid #89b4fa;
}

QLabel {
    color: #cdd6f4;
}

QLabel#categoryTag {
    color: #89b4fa;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QLabel#termLabel {
    color: #cdd6f4;
}

QLabel#translationLabel {
    color: #a6e3a1;
    font-weight: bold;
}

QLabel#definitionLabel {
    color: #bac2de;
    font-size: 12px;
    font-style: italic;
}

QLabel#exampleLabel {
    color: #9399b2;
    font-size: 11px;
}

QLabel#feedbackLabel {
    font-size: 13px;
}

QLabel#colHeader {
    color: #89b4fa;
    font-weight: bold;
    font-size: 13px;
    padding: 4px 0;
}

QFrame#card {
    background-color: #24273a;
    border: 1px solid #313244;
    border-radius: 12px;
}

QFrame#translationFrame {
    border-top: 1px solid #313244;
    margin-top: 8px;
    padding-top: 8px;
}

QWidget#statCard {
    background-color: #24273a;
    border: 1px solid #313244;
    border-radius: 8px;
    min-width: 110px;
}

QLabel#statValue {
    color: #89b4fa;
}

QLabel#statTitle {
    color: #9399b2;
    font-size: 11px;
}

QTableWidget {
    background-color: #24273a;
    gridline-color: #313244;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #313244;
}

QHeaderView::section {
    background-color: #181825;
    color: #89b4fa;
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid #313244;
    font-weight: bold;
}

QTableWidget QTableCornerButton::section {
    background-color: #181825;
}

QScrollBar:vertical {
    background-color: #181825;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QStatusBar {
    background-color: #181825;
    color: #6c7086;
    font-size: 11px;
}
"""


def _import_terms_if_needed(db: DBManager):
    """Auto-import terms.json if the terms table is empty."""
    if not db.is_terms_empty():
        return
    import json
    if not os.path.exists(TERMS_JSON):
        return
    with open(TERMS_JSON, encoding="utf-8") as f:
        terms = json.load(f)
    db.import_terms(terms)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Legal English Trainer")
    app.setStyleSheet(DARK_STYLESHEET)

    db = DBManager(DB_PATH)
    _import_terms_if_needed(db)
    scheduler = SpacedRepetitionScheduler(db)

    window = MainWindow(db, scheduler)
    window.show()

    exit_code = app.exec()
    db.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
