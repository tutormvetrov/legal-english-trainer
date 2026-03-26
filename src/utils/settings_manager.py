"""
Настройки приложения. Хранятся в ~/.letapp/settings.json
"""
import json
import pathlib

_FILE = pathlib.Path.home() / ".letapp" / "settings.json"

_DEFAULTS = {
    "font_size": 13,
    "boss_start_ms": 5000,
    "quiz_every": 10,
    "daily_goal": 20,
    "reminder_enabled": False,
    "reminder_hour": 9,
    "reminder_minute": 0,
    "attack_enabled": False,
    "attack_interval_min": 30,
}

_cache: dict | None = None


def get_settings() -> dict:
    global _cache
    if _cache is None:
        _cache = _load()
    return _cache


def save_settings(data: dict) -> None:
    global _cache
    _cache = data
    _FILE.parent.mkdir(parents=True, exist_ok=True)
    _FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load() -> dict:
    try:
        saved = json.loads(_FILE.read_text(encoding="utf-8"))
        merged = dict(_DEFAULTS)
        merged.update(saved)
        return merged
    except Exception:
        return dict(_DEFAULTS)
