#!/usr/bin/env python3
"""
Генератор ключей активации для Legal English Trainer.
Запускай из корня проекта:  python scripts/keygen.py

Ключи можно раздавать студентам — каждый раз новый.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.license_manager import generate_key, validate_key


def main():
    print("=== Генератор ключей — Legal English Trainer ===\n")

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

    save = input("\nСохранить в файл keys.txt? [д/н]: ").strip().lower()
    if save in ("д", "y", "yes", "да"):
        path = os.path.join(os.path.dirname(__file__), "..", "keys.txt")
        mode = "a" if os.path.exists(path) else "w"
        with open(path, mode, encoding="utf-8") as f:
            for key in keys:
                f.write(key + "\n")
        print(f"Сохранено: {os.path.abspath(path)}")


if __name__ == "__main__":
    main()
