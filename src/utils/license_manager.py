"""
Локальная активация приложения.

Ключ остаётся офлайн-проверяемым, но сохранённая активация дополнительно
подписывается и привязывается к текущей машине. Это не полноценная защита,
но убирает самый тривиальный перенос license-файла между устройствами.
"""

import base64
import getpass
import hashlib
import json
import pathlib
import platform
import uuid

# Алфавит: исключены 0/O и 1/I, чтобы избежать путаницы при ручном вводе
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_A = len(ALPHABET)

# Встроенная «соль» — меняй при форке, чтобы чужие генераторы не подошли
_SECRET = 0x4C4547414C454E47  # "LEGALENG" as int

_APP_DIR = pathlib.Path.home() / ".letapp"
_LICENSE_FILE = _APP_DIR / ".session.bin"
_LEGACY_LICENSE_FILE = _APP_DIR / "license.dat"
_FORMAT_VERSION = 2


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


def _normalize_key(key: str) -> str:
    return key.upper().replace("-", "").replace(" ", "")


def _machine_fingerprint() -> str:
    raw = "|".join([
        platform.system(),
        platform.release(),
        platform.machine(),
        platform.node(),
        getpass.getuser(),
        f"{uuid.getnode():012x}",
    ]).lower().encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]


def _sign_payload(payload_b64: str) -> str:
    raw = f"{_SECRET}:{payload_b64}:{_machine_fingerprint()}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _pack_envelope(data: dict) -> str:
    payload = {
        "key": _normalize_key(data.get("key", "")),
        "username": data.get("username", "").strip(),
        "easter_shown": bool(data.get("easter_shown", False)),
        "machine": _machine_fingerprint(),
    }
    payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("ascii")
    envelope = {
        "v": _FORMAT_VERSION,
        "payload": payload_b64,
        "sig": _sign_payload(payload_b64),
    }
    return json.dumps(envelope, ensure_ascii=False, separators=(",", ":"))


def _decode_envelope(data: dict) -> dict:
    payload_b64 = data.get("payload", "")
    sig = data.get("sig", "")
    if not payload_b64 or not sig:
        return {}
    if _sign_payload(payload_b64) != sig:
        return {}
    try:
        payload_raw = base64.urlsafe_b64decode(payload_b64.encode("ascii")).decode("utf-8")
        payload = json.loads(payload_raw)
    except Exception:
        return {}
    if payload.get("machine") != _machine_fingerprint():
        return {}
    payload["key"] = _normalize_key(payload.get("key", ""))
    payload["username"] = payload.get("username", "").strip()
    payload["easter_shown"] = bool(payload.get("easter_shown", False))
    return payload


def generate_key() -> str:
    import random
    seed = "".join(random.choice(ALPHABET) for _ in range(15))
    checksum = _encode_hash(_hash_seed(seed))
    raw = seed + checksum
    return "-".join(raw[i:i + 5] for i in range(0, 20, 5))


def validate_key(key: str) -> bool:
    raw = _normalize_key(key)
    if len(raw) != 20:
        return False
    if not all(c in ALPHABET for c in raw):
        return False
    seed, given = raw[:15], raw[15:]
    return _encode_hash(_hash_seed(seed)) == given


# ── Хранение активации ────────────────────────────────────────────────────────

def _parse_content(content: str) -> dict:
    try:
        data = json.loads(content)
    except Exception:
        return {"key": _normalize_key(content), "username": ""}

    if isinstance(data, dict) and data.get("v") == _FORMAT_VERSION:
        return _decode_envelope(data)

    if isinstance(data, dict):
        return {
            "key": _normalize_key(data.get("key", "")),
            "username": data.get("username", "").strip(),
            "easter_shown": bool(data.get("easter_shown", False)),
        }
    return {}


def _write_data(data: dict) -> None:
    _APP_DIR.mkdir(parents=True, exist_ok=True)
    _LICENSE_FILE.write_text(_pack_envelope(data), encoding="utf-8")
    if _LEGACY_LICENSE_FILE.exists():
        _LEGACY_LICENSE_FILE.unlink()

def _read_data() -> dict:
    """Читает файл лицензии, поддерживает legacy-форматы и новый machine-bound формат."""
    for path in (_LICENSE_FILE, _LEGACY_LICENSE_FILE):
        try:
            content = path.read_text(encoding="utf-8").strip()
        except Exception:
            continue
        if content:
            return _parse_content(content)
    return {}


def is_activated() -> bool:
    if not _LICENSE_FILE.exists() and not _LEGACY_LICENSE_FILE.exists():
        return False
    try:
        return validate_key(_read_data().get("key", ""))
    except Exception:
        return False


def save_activation(key: str, username: str = "") -> None:
    data = _read_data()
    data["key"] = _normalize_key(key)
    data["username"] = username.strip()
    _write_data(data)


def get_username() -> str:
    return _read_data().get("username", "")


def get_key() -> str:
    return _read_data().get("key", "")


def get_easter_shown() -> bool:
    return bool(_read_data().get("easter_shown", False))


def set_easter_shown() -> None:
    data = _read_data()
    data["easter_shown"] = True
    _write_data(data)


def is_stefan(username: str) -> bool:
    return username.strip().lower() in (
        # Russian
        "стефан", "стефан тёхта", "стефан техта",
        # English variants
        "stefan", "stephan", "stephen",
        "stefan tyokhta", "stefan tehta", "stefan tyohta",
        "stephan tyokhta", "stephen tyokhta",
    )


def deactivate() -> None:
    for path in (_LICENSE_FILE, _LEGACY_LICENSE_FILE):
        if path.exists():
            path.unlink()
