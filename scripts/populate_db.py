"""
Импорт data/terms.json в базу данных.
Запуск: python scripts/populate_db.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.database.db_manager import DBManager

TERMS_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "terms.json")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "legal_english.db")


def main():
    if not os.path.exists(TERMS_JSON):
        print(f"Файл не найден: {TERMS_JSON}")
        sys.exit(1)

    with open(TERMS_JSON, encoding="utf-8") as f:
        terms = json.load(f)

    db = DBManager(DB_PATH)
    db.import_terms(terms)
    total = db.conn.execute("SELECT COUNT(*) FROM terms").fetchone()[0]
    print(f"Импорт завершён. Терминов в базе: {total}")
    db.close()


if __name__ == "__main__":
    main()
