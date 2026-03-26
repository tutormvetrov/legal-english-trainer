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
    from .gui.activation_dialog import ActivationDialog
    from .gui.easter_egg_dialog import EasterEggDialog
    from .utils.license_manager import is_activated, get_username, is_stefan
    from .utils.streak_manager import record_activity
except ImportError:
    sys.path.insert(0, BASE_DIR)
    from database.db_manager import DBManager
    from algorithms.spaced_repetition import SpacedRepetitionScheduler
    from gui.main_window import MainWindow
    from gui.activation_dialog import ActivationDialog
    from gui.easter_egg_dialog import EasterEggDialog
    from utils.license_manager import is_activated, get_username, is_stefan
    from utils.streak_manager import record_activity


DARK_STYLESHEET = """
QWidget {
    background-color: #2b2d3e;
    color: #e0e4f8;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #2b2d3e;
}

QTabWidget::pane {
    border: 1px solid #44475a;
    background-color: #2b2d3e;
}

QTabBar::tab {
    background-color: #23253a;
    color: #b8bcd8;
    padding: 8px 20px;
    border: 1px solid #44475a;
    border-bottom: none;
    min-width: 100px;
}

QTabBar::tab:selected {
    background-color: #2b2d3e;
    color: #e0e4f8;
    border-top: 2px solid #7eb8f7;
}

QTabBar::tab:hover:!selected {
    background-color: #32354d;
}

QPushButton {
    background-color: #3e4060;
    color: #e0e4f8;
    border: 1px solid #5a5d7a;
    border-radius: 6px;
    padding: 6px 16px;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #4e5170;
}

QPushButton:pressed {
    background-color: #5e6180;
}

QPushButton:disabled {
    background-color: #32354d;
    color: #6a6d8a;
}

QPushButton#knowBtn {
    background-color: #264d35;
    color: #b8f0c0;
    border: 1px solid #48b860;
}
QPushButton#knowBtn:hover {
    background-color: #30603f;
}

QPushButton#dontKnowBtn {
    background-color: #4d2630;
    color: #f8b0c0;
    border: 1px solid #c04050;
}
QPushButton#dontKnowBtn:hover {
    background-color: #603040;
}

QPushButton#matchBtn {
    background-color: #32354d;
    color: #e0e4f8;
    border: 1px solid #5a5d7a;
    border-radius: 6px;
    text-align: center;
    padding: 6px 10px;
}
QPushButton#matchBtn:hover {
    background-color: #3e4060;
}

QComboBox {
    background-color: #3e4060;
    color: #e0e4f8;
    border: 1px solid #5a5d7a;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 28px;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #3e4060;
    color: #e0e4f8;
    selection-background-color: #4e5170;
    border: 1px solid #5a5d7a;
}

QSpinBox {
    background-color: #3e4060;
    color: #e0e4f8;
    border: 1px solid #5a5d7a;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 28px;
}

QLineEdit {
    background-color: #3e4060;
    color: #e0e4f8;
    border: 1px solid #5a5d7a;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 14px;
}

QLineEdit:focus {
    border: 1px solid #7eb8f7;
}

QLabel {
    color: #e0e4f8;
}

QLabel#categoryTag {
    color: #7eb8f7;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QLabel#termLabel {
    color: #e0e4f8;
}

QLabel#translationLabel {
    color: #b8f0c0;
    font-weight: bold;
}

QLabel#definitionLabel {
    color: #c8cce8;
    font-size: 12px;
    font-style: italic;
}

QLabel#exampleLabel {
    color: #a8acc8;
    font-size: 11px;
}

QLabel#feedbackLabel {
    font-size: 13px;
}

QLabel#colHeader {
    color: #7eb8f7;
    font-weight: bold;
    font-size: 13px;
    padding: 4px 0;
}

QFrame#card {
    background-color: #32354d;
    border: 1px solid #44475a;
    border-radius: 12px;
}

QFrame#translationFrame {
    border-top: 1px solid #44475a;
    margin-top: 8px;
    padding-top: 8px;
}

QWidget#statCard {
    background-color: #32354d;
    border: 1px solid #44475a;
    border-radius: 8px;
    min-width: 110px;
}

QLabel#statValue {
    color: #7eb8f7;
}

QLabel#statTitle {
    color: #a8acc8;
    font-size: 11px;
}

QTableWidget {
    background-color: #32354d;
    alternate-background-color: #2b2d3e;
    gridline-color: #44475a;
    color: #e0e4f8;
    border: 1px solid #44475a;
    border-radius: 6px;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #44475a;
}

QHeaderView::section {
    background-color: #23253a;
    color: #7eb8f7;
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid #44475a;
    font-weight: bold;
}

QTableWidget QTableCornerButton::section {
    background-color: #23253a;
}

QScrollBar:vertical {
    background-color: #23253a;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #5a5d7a;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QStatusBar {
    background-color: #23253a;
    color: #8a8da8;
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

    # ── Проверка активации ────────────────────────────────────────────
    first_launch = not is_activated()
    if first_launch:
        dlg = ActivationDialog()
        if dlg.exec() != ActivationDialog.DialogCode.Accepted:
            sys.exit(0)
        username = dlg.username
    else:
        username = get_username()

    # ── Пасхалка для Стефана ─────────────────────────────────────────
    if first_launch and is_stefan(username):
        EasterEggDialog(username).exec()

    streak = record_activity()

    db = DBManager(DB_PATH)
    _import_terms_if_needed(db)
    scheduler = SpacedRepetitionScheduler(db)

    window = MainWindow(db, scheduler, streak=streak, username=username)
    window.show()

    exit_code = app.exec()
    db.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
