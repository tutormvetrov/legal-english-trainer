import sys
import os
import pathlib

# Resolve paths for both normal run and PyInstaller bundle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, "frozen", False):
    # Running inside a PyInstaller bundle
    _ROOT = sys._MEIPASS
    # _MEIPASS is read-only on macOS — store user data in ~/.letapp/
    _USER_DATA = pathlib.Path.home() / ".letapp"
    _USER_DATA.mkdir(parents=True, exist_ok=True)
    DB_PATH = str(_USER_DATA / "legal_english.db")
else:
    # Running from source: src/ → parent is project root
    _ROOT = os.path.join(BASE_DIR, "..")
    DB_PATH = os.path.join(_ROOT, "data", "legal_english.db")

TERMS_JSON = os.path.join(_ROOT, "data", "terms.json")

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QPalette, QColor, QIcon, QPixmap
from PyQt6.QtCore import Qt, QTimer

# Support both `python -m src.main` and direct `python src/main.py` / PyInstaller
try:
    from .database.db_manager import DBManager
    from .algorithms.spaced_repetition import SpacedRepetitionScheduler
    from .gui.main_window import MainWindow
    from .gui.activation_dialog import ActivationDialog
    from .gui.easter_egg_dialog import EasterEggDialog
    from .utils.license_manager import is_activated, get_username, is_stefan
    from .utils.streak_manager import record_activity
    from .utils.settings_manager import get_settings
    from .utils.update_checker import UpdateChecker
    from ._stylesheet import build_dark_stylesheet
    from .version import __version__, GITHUB_REPO
except ImportError:
    sys.path.insert(0, BASE_DIR)
    from database.db_manager import DBManager
    from algorithms.spaced_repetition import SpacedRepetitionScheduler
    from gui.main_window import MainWindow
    from gui.activation_dialog import ActivationDialog
    from gui.easter_egg_dialog import EasterEggDialog
    from utils.license_manager import is_activated, get_username, is_stefan
    from utils.streak_manager import record_activity
    from utils.settings_manager import get_settings
    from utils.update_checker import UpdateChecker
    from _stylesheet import build_dark_stylesheet
    from version import __version__, GITHUB_REPO


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
    font_size = get_settings().get("font_size", 13)
    app.setStyleSheet(build_dark_stylesheet(font_size))

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

    window = MainWindow(db, scheduler, streak=streak, username=username,
                        db_path=DB_PATH)
    window.show()

    # ── Проверка обновлений (фоновый поток) ───────────────────────────
    def _on_update_available(current: str, latest: str):
        from PyQt6.QtWidgets import QMessageBox
        import webbrowser
        msg = QMessageBox(window)
        msg.setWindowTitle("Доступно обновление")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(f"Вышла новая версия <b>{latest}</b>.<br>У вас установлена {current}.")
        msg.setInformativeText("Хотите открыть страницу загрузки?")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")

    _updater = UpdateChecker(__version__, GITHUB_REPO, parent=app)
    _updater.update_available.connect(_on_update_available)
    _updater.start()

    # ── Системный трей ────────────────────────────────────────────────
    tray = None
    if QSystemTrayIcon.isSystemTrayAvailable():
        pix = QPixmap(16, 16)
        pix.fill(QColor("#7eb8f7"))
        tray = QSystemTrayIcon(QIcon(pix), app)
        tray.setToolTip("Legal English Trainer")

        tray_menu = QMenu()
        open_act = tray_menu.addAction("Открыть")
        open_act.triggered.connect(lambda: (window.show(), window.raise_()))
        tray_menu.addSeparator()
        quit_act = tray_menu.addAction("Выход")
        quit_act.triggered.connect(app.quit)
        tray.setContextMenu(tray_menu)
        tray.activated.connect(
            lambda reason: (window.show(), window.raise_())
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None
        )
        tray.show()

        # Проверка напоминания раз в минуту
        _shown = {"date": None}

        def _check_reminder():
            from datetime import datetime, date
            s = get_settings()
            if not s.get("reminder_enabled"):
                return
            now = datetime.now()
            today = date.today().isoformat()
            if (_shown["date"] != today
                    and now.hour == s["reminder_hour"]
                    and now.minute == s["reminder_minute"]):
                _shown["date"] = today
                tray.showMessage(
                    "Legal English Trainer",
                    "Не забудь повторить термины сегодня! 📚",
                    QSystemTrayIcon.MessageIcon.Information,
                    5000,
                )

        reminder_timer = QTimer(app)
        reminder_timer.setInterval(60_000)
        reminder_timer.timeout.connect(_check_reminder)
        reminder_timer.start()

    exit_code = app.exec()
    db.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
