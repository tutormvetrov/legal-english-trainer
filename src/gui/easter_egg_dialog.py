"""
Пасхалка для Стефана. Показывает картинку и воспроизводит один из 4 весёлых звуков.
"""
import math
import os
import random
import struct
import sys
import tempfile
import wave

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont

try:
    from PyQt6.QtMultimedia import QSoundEffect
    from PyQt6.QtCore import QUrl
    _SOUND_OK = True
except Exception:
    _SOUND_OK = False

_TMPDIR = None


def _tmp() -> str:
    global _TMPDIR
    if _TMPDIR is None:
        _TMPDIR = tempfile.mkdtemp(prefix="let_egg_")
    return _TMPDIR


# ── Sound generators ──────────────────────────────────────────────────────────

def _write_wav(name: str, frames: bytes, sr: int = 44100) -> str:
    path = os.path.join(_tmp(), name)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(frames)
    return path


def _sine(freq: float, t: float, sr: int) -> float:
    return math.sin(2 * math.pi * freq * t / sr)


def _env(i: int, n: int, attack: float = 0.01, release: float = 0.05,
         sr: int = 44100) -> float:
    a = int(sr * attack)
    r = int(sr * release)
    if i < a:
        return i / a
    if i > n - r:
        return (n - i) / r
    return 1.0


def make_fanfare(sr: int = 44100) -> str:
    """Торжественный фанфар: C5-E5-G5-C6-E6 быстро и громко."""
    notes = [523, 659, 784, 1047, 1319]
    dur = 0.18
    frames = bytearray()
    for freq in notes:
        n = int(sr * dur)
        for i in range(n):
            v = _env(i, n, 0.005, 0.04, sr) * _sine(freq, i, sr)
            # Add slight harmonic
            v += 0.3 * _sine(freq * 2, i, sr) * _env(i, n, 0.005, 0.04, sr)
            frames += struct.pack("<h", int(v / 1.3 * 28000))
    return _write_wav("fanfare.wav", bytes(frames), sr)


def make_applause(sr: int = 44100) -> str:
    """Имитация аплодисментов: шумовые всплески с модуляцией."""
    dur = 2.5
    n = int(sr * dur)
    frames = bytearray()
    import random as rnd
    freqs = [600, 900, 1300, 1800, 2500, 3400, 4200]
    for i in range(n):
        t = i / sr
        # Rhythmic clap bursts at ~3 claps/sec
        clap_env = max(0.0, math.sin(math.pi * ((t * 3) % 1.0)) ** 0.5)
        # Sum of sines at speech-band freqs, randomised amplitudes
        val = sum(math.sin(2 * math.pi * f * t + rnd.uniform(0, math.pi))
                  for f in freqs)
        val *= clap_env * rnd.gauss(0.7, 0.25) / len(freqs)
        # Overall fade in/out
        env = min(1.0, min(t / 0.15, (dur - t) / 0.3))
        frames += struct.pack("<h", max(-32767, min(32767, int(val * env * 22000))))
    return _write_wav("applause.wav", bytes(frames), sr)


def make_tadaa(sr: int = 44100) -> str:
    """«Та-дааа» — два громких аккорда."""
    chord1 = [392, 494, 587]   # G4-B4-D5
    chord2 = [523, 659, 784, 1047]  # C5-E5-G5-C6
    frames = bytearray()
    for chord, dur, gap in [(chord1, 0.12, 0.06), (chord2, 0.55, 0)]:
        n = int(sr * dur)
        for i in range(n):
            v = sum(_sine(f, i, sr) for f in chord)
            v *= _env(i, n, 0.005, 0.12, sr) / len(chord)
            frames += struct.pack("<h", int(v * 26000))
        # gap
        frames += b"\x00\x00" * int(sr * gap)
    return _write_wav("tadaa.wav", bytes(frames), sr)


def make_jingle(sr: int = 44100) -> str:
    """Весёлый 8-битный джингл."""
    #        C5   E5   G5   E5   C5   G4   C5
    melody = [523, 659, 784, 659, 523, 392, 523]
    durs   = [0.12, 0.12, 0.12, 0.12, 0.12, 0.12, 0.30]
    frames = bytearray()
    for freq, dur in zip(melody, durs):
        n = int(sr * dur)
        for i in range(n):
            # Square-ish wave for 8-bit feel
            v = 1.0 if _sine(freq, i, sr) > 0 else -1.0
            v *= _env(i, n, 0.005, 0.06, sr) * 0.6
            frames += struct.pack("<h", int(v * 24000))
        frames += b"\x00\x00" * int(sr * 0.02)   # tiny pause between notes
    return _write_wav("jingle.wav", bytes(frames), sr)


# ── Sound catalogue ───────────────────────────────────────────────────────────

_MAKERS = [make_fanfare, make_applause, make_tadaa, make_jingle]
_EFFECTS: list = []


def _ensure_sounds():
    if not _SOUND_OK or _EFFECTS:
        return
    for maker in _MAKERS:
        path = maker()
        eff = QSoundEffect()
        eff.setSource(QUrl.fromLocalFile(path))
        eff.setVolume(0.75)
        _EFFECTS.append(eff)


def _play_random():
    _ensure_sounds()
    if _EFFECTS:
        random.choice(_EFFECTS).play()


# ── Dialog ────────────────────────────────────────────────────────────────────

def _find_image() -> str | None:
    """Ищет картинку в assets/ рядом с exe или с проектом."""
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(os.path.join(sys._MEIPASS, "assets"))
    candidates.append(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "..", "assets")
    )
    for folder in candidates:
        folder = os.path.normpath(folder)
        if os.path.isdir(folder):
            for f in os.listdir(folder):
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                    return os.path.join(folder, f)
    return None


class EasterEggDialog(QDialog):
    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎉")
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint
        )
        self.setMinimumWidth(420)
        self._build_ui(username)
        QTimer.singleShot(200, _play_random)

    def _build_ui(self, username: str):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        greeting = QLabel(f"Привет, {username}! 🎉")
        gf = QFont(); gf.setPointSize(18); gf.setBold(True)
        greeting.setFont(gf)
        greeting.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(greeting)

        img_path = _find_image()
        if img_path:
            img_label = QLabel()
            px = QPixmap(img_path)
            if not px.isNull():
                px = px.scaled(380, 380,
                               Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
            img_label.setPixmap(px)
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(img_label)

        caption = QLabel("Добро пожаловать в Legal English Trainer!")
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption.setStyleSheet("color: #a8acc8; font-size: 12px;")
        root.addWidget(caption)

        ok_btn = QPushButton("Вперёд, к знаниям! 🚀")
        ok_btn.setMinimumHeight(40)
        ok_btn.clicked.connect(self.accept)
        root.addWidget(ok_btn)

        self.adjustSize()
