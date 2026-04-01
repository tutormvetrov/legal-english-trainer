"""
Фоновая проверка обновлений через GitHub Releases API.
Запускается после старта приложения, не блокирует UI.
"""
import urllib.request
import json

from PyQt6.QtCore import QThread, pyqtSignal


def _parse_version(v: str) -> tuple:
    """'v1.2.3' или '1.2.3' → (1, 2, 3)"""
    return tuple(int(x) for x in v.lstrip("v").split("."))


class UpdateChecker(QThread):
    """
    Эмитирует update_available(current, latest) если на GitHub
    есть версия новее текущей. Молча игнорирует любые ошибки сети.
    """
    update_available = pyqtSignal(str, str)  # (current_version, latest_version)

    def __init__(self, current_version: str, repo: str, user_agent: str = "AppUpdater", parent=None):
        super().__init__(parent)
        self._current = current_version
        self._repo = repo
        self._user_agent = user_agent

    def run(self):
        try:
            url = f"https://api.github.com/repos/{self._repo}/releases/latest"
            req = urllib.request.Request(
                url,
                headers={"Accept": "application/vnd.github+json",
                         "User-Agent": self._user_agent},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())

            latest_tag = data.get("tag_name", "")
            if not latest_tag:
                return

            if _parse_version(latest_tag) > _parse_version(self._current):
                self.update_available.emit(self._current, latest_tag.lstrip("v"))

        except Exception:
            pass  # нет интернета, rate limit, любая ошибка — тихо игнорируем
