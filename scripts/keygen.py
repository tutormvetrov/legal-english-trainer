#!/usr/bin/env python3
"""
Генератор ключей активации для Legal English Trainer.
Запускай из корня проекта:  python scripts/keygen.py

Ключи можно раздавать студентам — каждый раз новый.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.app_profile import get_current_profile
from src.utils.license_manager import generate_key, validate_key
from src.app_paths import ensure_app_dir


def main():
    print(f"=== Генератор ключей — {get_current_profile().app_name} ===\n")

    while True:
        raw = input("Сколько ключей сгенерировать? [1]: ").strip()
        if raw == "":
            count = 1
        elif raw.isdigit() and int(raw) > 0:
            count = int(raw)
        else:
            print("Введите целое число больше нуля.")
            continue
        break

    print()
    keys = [generate_key() for _ in range(count)]
    for i, key in enumerate(keys, 1):
        print(f"  {i:>3}. {key}")

    print()

    # Самопроверка
    ok = all(validate_key(k) for k in keys)
    print(f"Проверка: {'все ключи корректны ✓' if ok else 'ОШИБКА ВАЛИДАЦИИ!'}")

    save = input("\nСохранить в локальный файл вне репозитория? [д/н]: ").strip().lower()
    if save in ("д", "y", "yes", "да"):
        out_dir = ensure_app_dir()
        path = out_dir / "generated_keys.txt"
        mode = "a" if path.exists() else "w"
        with open(path, mode, encoding="utf-8") as f:
            for key in keys:
                f.write(key + "\n")
        print(f"Сохранено: {path.resolve()}")


if __name__ == "__main__":
    main()
