"""
Озвучка текста без сторонних зависимостей.

Windows: Windows Speech API через PowerShell, явно выбирает en-* голос.
macOS:   встроенная команда `say`, явно выбирает английский голос.
Другие платформы: молча игнорируется.
"""
import subprocess
import sys
import threading

# Предпочтительные английские голоса macOS (в порядке приоритета).
# Доступность зависит от версии системы, поэтому список длинный.
_MAC_EN_VOICES = [
    "Samantha",  # en-US, установлен по умолчанию на большинстве Mac
    "Alex",      # en-US, классический голос (macOS < Ventura)
    "Tom",       # en-US
    "Karen",     # en-AU
    "Daniel",    # en-GB
    "Kate",      # en-GB
]


def speak(text: str) -> None:
    """Произносит текст асинхронно. Не блокирует UI."""
    if sys.platform == "win32":
        threading.Thread(target=_speak_windows, args=(text,), daemon=True).start()
    elif sys.platform == "darwin":
        threading.Thread(target=_speak_macos, args=(text,), daemon=True).start()
    # Linux и прочие: нет встроенного TTS без зависимостей — молча пропускаем


def _speak_windows(text: str) -> None:
    safe = text.replace('"', '').replace("'", "\\'")
    cmd = (
        'Add-Type -AssemblyName System.Speech; '
        '$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
        '$en = $s.GetInstalledVoices() | '
        '  Where-Object { $_.VoiceInfo.Culture.Name -like "en*" } | '
        '  Select-Object -First 1; '
        'if ($en) { $s.SelectVoice($en.VoiceInfo.Name) }; '
        f'$s.Speak("{safe}")'
    )
    try:
        subprocess.run(
            ["powershell", "-WindowStyle", "Hidden", "-Command", cmd],
            creationflags=subprocess.CREATE_NO_WINDOW,
            timeout=15,
        )
    except Exception:
        pass


def _speak_macos(text: str) -> None:
    # Пробуем голоса из списка по очереди, берём первый доступный
    for voice in _MAC_EN_VOICES:
        result = subprocess.run(
            ["say", "-v", voice, "--", text],
            capture_output=True,
            timeout=15,
        )
        if result.returncode == 0:
            return  # успешно

    # Ни один предпочтительный голос не найден — используем системный по умолчанию
    try:
        subprocess.run(["say", "--", text], timeout=15)
    except Exception:
        pass
