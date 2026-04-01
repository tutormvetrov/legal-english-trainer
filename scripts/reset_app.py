#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сброс состояния приложения для тестирования.
Запуск: python scripts/reset_app.py
"""
import sys
import pathlib
import shutil

sys.stdout.reconfigure(encoding="utf-8")

LETAPP = pathlib.Path.home() / ".letapp"

FILES = {
    ".session.bin":  "текущая machine-bound активация",
    "license.dat":   "legacy-активация и имя пользователя",
    "streak.json":   "streak (серия дней)",
    "highscore.json":"рекорд Boss Mode",
}

def main():
    print("=== Сброс состояния Legal English Trainer ===\n")

    if not LETAPP.exists():
        print("Папка ~/.letapp не найдена — приложение ещё не запускалось.")
        return

    for filename, description in FILES.items():
        path = LETAPP / filename
        if path.exists():
            path.unlink()
            print(f"  ✓ Удалён {filename}  ({description})")
        else:
            print(f"  — {filename} не найден (пропущено)")

    print("\nГотово. При следующем запуске снова появится экран активации.")

if __name__ == "__main__":
    main()
