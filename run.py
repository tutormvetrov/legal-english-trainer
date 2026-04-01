"""
Точка входа для запуска приложения:
    python run.py
"""
import sys
import os
import pathlib
import traceback
import datetime

# Add project root to path so 'src' is importable as a package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app_paths import get_user_file
from src.app_profile import get_current_profile

_LOG_FILE = get_user_file("crash.log")


def _write_crash_log(exc: BaseException) -> str:
    _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        f"\n{'=' * 60}\n"
        f"CRASH  {timestamp}\n"
        f"Python {sys.version}\n"
        f"Platform: {sys.platform}\n"
        f"Frozen: {getattr(sys, 'frozen', False)}\n"
        f"{'=' * 60}\n"
        f"{traceback.format_exc()}"
    )
    with open(_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    return str(_LOG_FILE)


def _show_crash_dialog(log_path: str, tb: str) -> None:
    """Show a minimal Qt error dialog (if Qt is available)."""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        _app = QApplication.instance() or QApplication(sys.argv)
        short = tb.strip().splitlines()[-1] if tb.strip() else "Unknown error"
        app_name = get_current_profile().app_name
        msg = QMessageBox()
        msg.setWindowTitle(f"{app_name} — Ошибка запуска")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(f"Приложение завершилось с ошибкой:\n\n{short}")
        msg.setInformativeText(f"Подробности сохранены в:\n{log_path}")
        msg.setDetailedText(tb)
        msg.exec()
    except Exception:
        pass  # if Qt itself is broken, just exit silently


from src.main import main

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        tb = traceback.format_exc()
        log_path = _write_crash_log(exc)
        _show_crash_dialog(log_path, tb)
        sys.exit(1)
