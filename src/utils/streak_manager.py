"""
Streak — счётчик дней подряд активности.
Хранится в ~/.letapp/streak.json
"""
import json
import pathlib
from datetime import date

_FILE = pathlib.Path.home() / ".letapp" / "streak.json"


def record_activity() -> int:
    """
    Вызывается при запуске приложения.
    Возвращает текущий streak (число дней подряд).
    """
    today = date.today().isoformat()
    data = _load()

    last = data.get("last_date")
    streak = data.get("streak", 0)

    if last == today:
        pass  # уже записано сегодня
    elif last == _yesterday():
        streak += 1
    else:
        streak = 1  # пропуск — сброс

    _save({"last_date": today, "streak": streak})
    return streak


def get_streak() -> int:
    data = _load()
    last = data.get("last_date")
    streak = data.get("streak", 0)
    # если последний вход был не сегодня и не вчера — streak обнулён
    if last not in (date.today().isoformat(), _yesterday()):
        return 0
    return streak


def _yesterday() -> str:
    from datetime import timedelta
    return (date.today() - timedelta(days=1)).isoformat()


def _load() -> dict:
    try:
        return json.loads(_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(data: dict) -> None:
    _FILE.parent.mkdir(parents=True, exist_ok=True)
    _FILE.write_text(json.dumps(data), encoding="utf-8")
