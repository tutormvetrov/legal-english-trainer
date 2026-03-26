import sqlite3
import os
from pathlib import Path


class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    def _init_schema(self):
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, "r", encoding="utf-8") as f:
            self.conn.executescript(f.read())
        # Migration: add starred column for existing DBs
        try:
            self.conn.execute("ALTER TABLE terms ADD COLUMN starred INTEGER DEFAULT 0")
            self.conn.commit()
        except Exception:
            pass  # column already exists

    def is_terms_empty(self) -> bool:
        cur = self.conn.execute("SELECT COUNT(*) FROM terms")
        return cur.fetchone()[0] == 0

    def import_terms(self, terms: list[dict]):
        self.conn.executemany(
            "INSERT OR IGNORE INTO terms (term_eng, term_rus, definition, category, example) "
            "VALUES (:term_eng, :term_rus, :definition, :category, :example)",
            terms
        )
        self.conn.commit()

    def get_term(self, term_id: int) -> sqlite3.Row | None:
        cur = self.conn.execute("SELECT * FROM terms WHERE id = ?", (term_id,))
        return cur.fetchone()

    def get_all_categories(self) -> list[str]:
        cur = self.conn.execute("SELECT DISTINCT category FROM terms ORDER BY category")
        return [row[0] for row in cur.fetchall()]

    def get_terms_by_category(self, category: str | None = None, limit: int = 10) -> list[sqlite3.Row]:
        if category and category != "Все категории":
            cur = self.conn.execute(
                "SELECT * FROM terms WHERE category = ? ORDER BY RANDOM() LIMIT ?",
                (category, limit)
            )
        else:
            cur = self.conn.execute(
                "SELECT * FROM terms ORDER BY RANDOM() LIMIT ?", (limit,)
            )
        return cur.fetchall()

    def get_random_term(self, category: str | None = None) -> sqlite3.Row | None:
        rows = self.get_terms_by_category(category, limit=1)
        return rows[0] if rows else None

    def get_progress(self, term_id: int) -> sqlite3.Row | None:
        cur = self.conn.execute("SELECT * FROM progress WHERE term_id = ?", (term_id,))
        return cur.fetchone()

    def upsert_progress(self, term_id: int, last_reviewed: str, ease_factor: float,
                        interval: int, repetition: int, correct_count: int):
        self.conn.execute(
            """INSERT INTO progress (term_id, last_reviewed, ease_factor, interval, repetition, correct_count)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(term_id) DO UPDATE SET
                 last_reviewed = excluded.last_reviewed,
                 ease_factor = excluded.ease_factor,
                 interval = excluded.interval,
                 repetition = excluded.repetition,
                 correct_count = excluded.correct_count""",
            (term_id, last_reviewed, ease_factor, interval, repetition, correct_count)
        )
        self.conn.commit()

    def get_due_terms(self, category: str | None = None, limit: int = 10) -> list[int]:
        from datetime import date
        today = date.today().isoformat()
        if category and category != "Все категории":
            cur = self.conn.execute(
                """SELECT t.id FROM terms t
                   LEFT JOIN progress p ON t.id = p.term_id
                   WHERE t.category = ?
                     AND (p.term_id IS NULL
                          OR date(p.last_reviewed, '+' || p.interval || ' days') <= ?)
                   LIMIT ?""",
                (category, today, limit)
            )
        else:
            cur = self.conn.execute(
                """SELECT t.id FROM terms t
                   LEFT JOIN progress p ON t.id = p.term_id
                   WHERE p.term_id IS NULL
                      OR date(p.last_reviewed, '+' || p.interval || ' days') <= ?
                   LIMIT ?""",
                (today, limit)
            )
        return [row[0] for row in cur.fetchall()]

    def get_stats(self) -> dict:
        from datetime import date
        today = date.today().isoformat()
        total = self.conn.execute("SELECT COUNT(*) FROM terms").fetchone()[0]
        learned = self.conn.execute(
            "SELECT COUNT(*) FROM progress WHERE correct_count > 0"
        ).fetchone()[0]
        avg_ef_row = self.conn.execute("SELECT AVG(ease_factor) FROM progress").fetchone()[0]
        avg_ef = round(avg_ef_row, 2) if avg_ef_row else 2.5
        today_reviews = self.conn.execute(
            "SELECT COUNT(*) FROM progress WHERE last_reviewed = ?", (today,)
        ).fetchone()[0]
        return {
            "total": total,
            "learned": learned,
            "avg_ease_factor": avg_ef,
            "today_reviews": today_reviews,
        }

    def get_stats_by_category(self) -> list[dict]:
        cur = self.conn.execute(
            """SELECT t.category,
                      COUNT(t.id) AS total,
                      COUNT(CASE WHEN p.correct_count > 0 THEN 1 END) AS learned
               FROM terms t
               LEFT JOIN progress p ON t.id = p.term_id
               GROUP BY t.category
               ORDER BY t.category"""
        )
        return [{"category": r[0], "total": r[1], "learned": r[2]} for r in cur.fetchall()]

    def export_progress_csv(self, filepath: str):
        import csv
        cur = self.conn.execute(
            """SELECT t.term_eng, t.term_rus, t.category,
                      p.last_reviewed, p.correct_count, p.ease_factor
               FROM terms t
               LEFT JOIN progress p ON t.id = p.term_id
               ORDER BY t.category, t.term_eng"""
        )
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Термин (EN)", "Термин (RU)", "Категория",
                             "Последнее повторение", "Правильных ответов", "Коэффициент лёгкости"])
            writer.writerows(cur.fetchall())

    def get_weak_terms(self, limit: int = 20) -> list:
        """Термины с наименьшим ease_factor (чаще всего ошибаются)."""
        cur = self.conn.execute(
            """SELECT t.term_eng, t.term_rus, t.category,
                      p.ease_factor, p.correct_count,
                      (p.repetition - p.correct_count) AS errors
               FROM terms t
               JOIN progress p ON t.id = p.term_id
               WHERE p.repetition > 0
               ORDER BY p.ease_factor ASC, errors DESC
               LIMIT ?""",
            (limit,)
        )
        return cur.fetchall()

    def set_starred(self, term_id: int, starred: bool) -> None:
        self.conn.execute(
            "UPDATE terms SET starred = ? WHERE id = ?",
            (1 if starred else 0, term_id)
        )
        self.conn.commit()

    def get_starred_terms(self) -> list:
        cur = self.conn.execute(
            "SELECT * FROM terms WHERE starred = 1 ORDER BY category, term_eng"
        )
        return cur.fetchall()

    def get_random_terms_for_quiz(self, exclude_ids: list[int],
                                  n: int = 3) -> list:
        """Возвращает n случайных терминов, не входящих в exclude_ids."""
        placeholders = ",".join("?" * len(exclude_ids)) if exclude_ids else "0"
        cur = self.conn.execute(
            f"SELECT * FROM terms WHERE id NOT IN ({placeholders}) "
            f"ORDER BY RANDOM() LIMIT ?",
            (*exclude_ids, n)
        )
        return cur.fetchall()

    def get_term_with_example(self, category: str | None = None) -> sqlite3.Row | None:
        """Случайный термин с непустым примером предложения."""
        if category and category != "Все категории":
            cur = self.conn.execute(
                "SELECT * FROM terms WHERE category = ? "
                "AND example IS NOT NULL AND TRIM(example) != '' "
                "ORDER BY RANDOM() LIMIT 1",
                (category,)
            )
        else:
            cur = self.conn.execute(
                "SELECT * FROM terms WHERE example IS NOT NULL "
                "AND TRIM(example) != '' ORDER BY RANDOM() LIMIT 1"
            )
        return cur.fetchone()

    def search_terms(self, query: str, limit: int = 100) -> list[sqlite3.Row]:
        """Поиск по term_eng и term_rus (регистронезависимо)."""
        pattern = f"%{query}%"
        cur = self.conn.execute(
            "SELECT * FROM terms WHERE term_eng LIKE ? OR term_rus LIKE ? "
            "ORDER BY term_eng LIMIT ?",
            (pattern, pattern, limit)
        )
        return cur.fetchall()

    def reset_progress(self) -> None:
        """Удаляет всю историю повторений. Термины и избранное сохраняются."""
        self.conn.execute("DELETE FROM progress")
        self.conn.commit()

    def close(self):
        self.conn.close()
