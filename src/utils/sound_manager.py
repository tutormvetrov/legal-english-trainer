"""
Генерирует WAV-тоны на лету (stdlib) и воспроизводит через QSoundEffect.
Если QtMultimedia недоступна — все вызовы play() молча игнорируются.
"""
import math
import struct
import tempfile
import wave
import os

_instance = None


def get_sound_manager():
    global _instance
    if _instance is None:
        _instance = SoundManager()
    return _instance


class SoundManager:
    def __init__(self):
        self._effects = {}
        self._ok = False
        self._tmpdir = tempfile.mkdtemp(prefix="let_snd_")
        self._init()

    # ── WAV generation ────────────────────────────────────────────────
    def _make_wav(self, name: str, freqs: list, dur: float = 0.13,
                  sr: int = 44100) -> str:
        path = os.path.join(self._tmpdir, name + ".wav")
        frames = []
        for freq in freqs:
            n = int(sr * dur)
            for i in range(n):
                # Short attack/release envelope to avoid clicks
                env = min(1.0, min(i, n - i) / max(1, int(sr * 0.009)))
                v = int(32767 * env * math.sin(2 * math.pi * freq * i / sr))
                frames.append(struct.pack("<h", v))
        with wave.open(path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(b"".join(frames))
        return path

    # ── Init ──────────────────────────────────────────────────────────
    def _init(self):
        try:
            from PyQt6.QtMultimedia import QSoundEffect
            from PyQt6.QtCore import QUrl

            sounds = {
                "correct":  ([659, 784], 0.13),          # E5 → G5
                "wrong":    ([185], 0.22),                # F#3 low thud
                "complete": ([523, 659, 784, 1047], 0.15),  # C5 E5 G5 C6
            }
            for name, (freqs, dur) in sounds.items():
                path = self._make_wav(name, freqs, dur)
                eff = QSoundEffect()
                eff.setSource(QUrl.fromLocalFile(path))
                eff.setVolume(0.55)
                self._effects[name] = eff
            self._ok = True
        except Exception:
            pass  # no sound — app still works

    # ── Public API ────────────────────────────────────────────────────
    def play(self, name: str):
        if self._ok and name in self._effects:
            self._effects[name].play()
