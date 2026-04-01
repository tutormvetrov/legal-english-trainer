import sys
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    from .utils.license_manager import (is_activated, get_username, is_stefan,
                                          get_easter_shown, set_easter_shown)
    from .utils.streak_manager import record_activity
    from .utils.settings_manager import get_settings
    from .utils.update_checker import UpdateChecker
    from ._stylesheet import build_stylesheet
    from .version import __version__
    from .models.term import Term
    from .gui.attack_popup import AttackPopup
    from .app_profile import get_current_profile, project_root
    from .app_paths import get_runtime_db_path, get_terms_seed_path
except ImportError:
    sys.path.insert(0, BASE_DIR)
    from database.db_manager import DBManager
    from algorithms.spaced_repetition import SpacedRepetitionScheduler
    from gui.main_window import MainWindow
    from gui.activation_dialog import ActivationDialog
    from gui.easter_egg_dialog import EasterEggDialog
    from utils.license_manager import (is_activated, get_username, is_stefan,
                                       get_easter_shown, set_easter_shown)
    from utils.streak_manager import record_activity
    from utils.settings_manager import get_settings
    from utils.update_checker import UpdateChecker
    from _stylesheet import build_stylesheet
    from version import __version__
    from models.term import Term
    from gui.attack_popup import AttackPopup
    from app_profile import get_current_profile, project_root
    from app_paths import get_runtime_db_path, get_terms_seed_path


PROFILE = get_current_profile()
_ROOT = str(project_root())
DB_PATH = str(get_runtime_db_path(frozen=getattr(sys, "frozen", False)))
TERMS_JSON = str(get_terms_seed_path())


def _load_fonts():
    """Register custom TTF fonts from assets/fonts/ into Qt's font database."""
    from PyQt6.QtGui import QFontDatabase
    fonts_dir = os.path.join(_ROOT, "assets", "fonts")
    if not os.path.isdir(fonts_dir):
        return
    for fname in os.listdir(fonts_dir):
        if fname.lower().endswith(".ttf"):
            QFontDatabase.addApplicationFont(os.path.join(fonts_dir, fname))


def _import_terms_if_needed(db: DBManager):
    """Auto-import the active pack seed terms if the terms table is empty."""
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
    app.setApplicationName(PROFILE.app_name)
    _load_fonts()   # must be called after QApplication, before setStyleSheet
    settings = get_settings()
    font_size = settings.get("font_size", 13)
    theme = settings.get("theme", "dark")
    app.setStyleSheet(build_stylesheet(font_size, theme))

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
    if is_stefan(username) and not get_easter_shown():
        EasterEggDialog(username).exec()
        set_easter_shown()

    streak = record_activity()

    db = DBManager(DB_PATH)
    _import_terms_if_needed(db)
    scheduler = SpacedRepetitionScheduler(db)

    window = MainWindow(db, scheduler, streak=streak, username=username,
                        db_path=DB_PATH)
    window.show()

    # ── Таймер «Термин атакует» ───────────────────────────────────
    _attack_state = {"last_popup": None}

    def _check_attack():
        from datetime import datetime
        s = get_settings()
        if not s.get("attack_enabled", False):
            return
        interval_min = s.get("attack_interval_min", 30)
        now = datetime.now()
        last = _attack_state["last_popup"]
        if last and (now - last).total_seconds() / 60 < interval_min:
            return
        due_ids = scheduler.get_due_terms(category=None, limit=50)
        row = db.get_term(random.choice(due_ids)) if due_ids else db.get_random_term(None)
        if row is None:
            return
        _attack_state["last_popup"] = now
        AttackPopup(Term.from_row(row), scheduler, parent=None).exec()

    attack_timer = QTimer(app)
    attack_timer.setInterval(60_000)
    attack_timer.timeout.connect(_check_attack)
    attack_timer.start()

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
            webbrowser.open(f"https://github.com/{PROFILE.github_repo}/releases/latest")

    _updater = UpdateChecker(
        __version__, PROFILE.github_repo, user_agent=PROFILE.update_user_agent, parent=app
    )
    _updater.update_available.connect(_on_update_available)
    _updater.start()

    # ── Системный трей ────────────────────────────────────────────────
    tray = None
    if QSystemTrayIcon.isSystemTrayAvailable():
        pix = QPixmap(16, 16)
        pix.fill(QColor("#7eb8f7"))
        tray = QSystemTrayIcon(QIcon(pix), app)
        tray.setToolTip(PROFILE.app_name)

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
                    PROFILE.app_name,
                    PROFILE.reminder_message,
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
