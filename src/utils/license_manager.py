"""
Алгоритмическая проверка 20-значных ключей активации.

Структура ключа (20 символов, отображается как XXXXX-XXXXX-XXXXX-XXXXX):
  • символы 0–14 : seed (15 случайных символов из ALPHABET)
  • символы 15–19: checksum (5 символов, вычисленных из seed + SECRET)

Формат вывода: XXXXX-XXXXX-XXXXX-XXXXX  (дефисы декоративные, игнорируются)
"""

import json
import pathlib

# Алфавит: исключены 0/O и 1/I, чтобы избежать путаницы при ручном вводе
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_A = len(ALPHABET)

# Встроенная «соль» — меняй при форке, чтобы чужие генераторы не подошли
_SECRET = 0x4C4547414C454E47  # "LEGALENG" as int

# Файл хранения активации (в домашней директории пользователя)
_LICENSE_FILE = pathlib.Path.home() / ".letapp" / "license.dat"


# ── Алгоритм ──────────────────────────────────────────────────────────────────

def _hash_seed(seed: str) -> int:
    val = _SECRET
    for i, ch in enumerate(seed):
        val = (val * 1000003 + ALPHABET.index(ch) * (i + 1) * 37) & 0xFFFFFFFFFFFFFF
    return val


def _encode_hash(h: int, length: int = 5) -> str:
    chars = []
    for _ in range(length):
        chars.append(ALPHABET[h % _A])
        h //= _A
    return "".join(chars)


def generate_key() -> str:
    import random
    seed = "".join(random.choice(ALPHABET) for _ in range(15))
    checksum = _encode_hash(_hash_seed(seed))
    raw = seed + checksum
    return "-".join(raw[i:i + 5] for i in range(0, 20, 5))


def validate_key(key: str) -> bool:
    raw = key.upper().replace("-", "").replace(" ", "")
    if len(raw) != 20:
        return False
    if not all(c in ALPHABET for c in raw):
        return False
    seed, given = raw[:15], raw[15:]
    return _encode_hash(_hash_seed(seed)) == given


# ── Хранение активации ────────────────────────────────────────────────────────

def _read_data() -> dict:
    """Читает файл лицензии, поддерживает старый (plain key) и новый (JSON) форматы."""
    try:
        content = _LICENSE_FILE.read_text(encoding="utf-8").strip()
        try:
            return json.loads(content)
        except Exception:
            return {"key": content, "username": ""}  # старый формат
    except Exception:
        return {}


def is_activated() -> bool:
    if not _LICENSE_FILE.exists():
        return False
    try:
        return validate_key(_read_data().get("key", ""))
    except Exception:
        return False


def save_activation(key: str, username: str = "") -> None:
    _LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "key": key.upper().replace("-", "").replace(" ", ""),
        "username": username.strip(),
    }
    _LICENSE_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def get_username() -> str:
    return _read_data().get("username", "")


def get_key() -> str:
    return _read_data().get("key", "")


def get_easter_shown() -> bool:
    return bool(_read_data().get("easter_shown", False))


def set_easter_shown() -> None:
    data = _read_data()
    data["easter_shown"] = True
    _LICENSE_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def is_stefan(username: str) -> bool:
    return username.strip().lower() in (
        "стефан", "stefan", "stephan",
        "стефан тёхта", "стефан техта",
        "stephan tyokhta", "stefan tehta", "stefan tyohta",
    )


def deactivate() -> None:
    if _LICENSE_FILE.exists():
        _LICENSE_FILE.unlink()
