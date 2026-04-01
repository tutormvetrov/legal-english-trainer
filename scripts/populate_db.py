"""
Импорт seed-пакета в базу данных.
Запуск: python scripts/populate_db.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.app_paths import get_runtime_db_path, get_terms_seed_path
from src.database.db_manager import DBManager

TERMS_JSON = get_terms_seed_path()
DB_PATH = get_runtime_db_path(frozen=False)


def main():
    if not TERMS_JSON.exists():
        print(f"Файл не найден: {TERMS_JSON}")
        sys.exit(1)

    with open(TERMS_JSON, encoding="utf-8") as f:
        terms = json.load(f)

    db = DBManager(str(DB_PATH))
    db.import_terms(terms)
    total = db.conn.execute("SELECT COUNT(*) FROM terms").fetchone()[0]
    print(f"Импорт завершён. Терминов в базе: {total}")
    db.close()


if __name__ == "__main__":
    main()
