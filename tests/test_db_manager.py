import sqlite3
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from src.algorithms.spaced_repetition import SpacedRepetitionScheduler
from src.database.db_manager import DBManager


class DBManagerTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "app.db"
        self.db = DBManager(str(self.db_path))
        self.scheduler = SpacedRepetitionScheduler(self.db)
        self.sample_terms = [
            {
                "term_eng": "Plaintiff",
                "term_rus": "Истец",
                "definition": "Party bringing a lawsuit.",
                "category": "Civil Procedure",
                "example": "The plaintiff filed the complaint.",
            },
            {
                "term_eng": "Defendant",
                "term_rus": "Ответчик",
                "definition": "Party defending a lawsuit.",
                "category": "Civil Procedure",
                "example": "The defendant denied liability.",
            },
            {
                "term_eng": "Consideration",
                "term_rus": "Встречное удовлетворение",
                "definition": "Value exchanged under a contract.",
                "category": "Contract Law",
                "example": "The contract failed for lack of consideration.",
            },
        ]
        self.db.import_terms(self.sample_terms)

    def tearDown(self):
        self.db.close()
        self._tmpdir.cleanup()

    def _term_id(self, term_eng: str) -> int:
        row = self.db.conn.execute(
            "SELECT id FROM terms WHERE term_eng = ?", (term_eng,)
        ).fetchone()
        return row[0]

    def test_import_terms_reports_only_new_rows(self):
        inserted = self.db.import_terms(self.sample_terms)
        self.assertEqual(inserted, 0)

        inserted_new = self.db.import_terms([
            {
                "term_eng": "Jurisdiction",
                "term_rus": "Юрисдикция",
                "definition": "Power of a court to hear a case.",
                "category": "Civil Procedure",
                "example": "The court lacked jurisdiction.",
            }
        ])
        self.assertEqual(inserted_new, 1)

    def test_search_terms_is_case_insensitive_for_cyrillic_and_latin(self):
        ru_rows = self.db.search_terms("истец")
        en_rows = self.db.search_terms("plaintiff")

        self.assertEqual([row["term_eng"] for row in ru_rows], ["Plaintiff"])
        self.assertEqual([row["term_eng"] for row in en_rows], ["Plaintiff"])

    def test_reset_progress_keeps_terms_and_starred_state(self):
        plaintiff_id = self._term_id("Plaintiff")
        self.db.set_starred(plaintiff_id, True)
        self.scheduler.review(plaintiff_id, 5)

        self.db.reset_progress()

        progress_count = self.db.conn.execute("SELECT COUNT(*) FROM progress").fetchone()[0]
        starred = self.db.get_term(plaintiff_id)["starred"]
        total_terms = self.db.conn.execute("SELECT COUNT(*) FROM terms").fetchone()[0]
        self.assertEqual(progress_count, 0)
        self.assertEqual(starred, 1)
        self.assertEqual(total_terms, 3)

    def test_backup_and_restore_round_trip(self):
        plaintiff_id = self._term_id("Plaintiff")
        self.scheduler.review(plaintiff_id, 5)
        backup_path = Path(self._tmpdir.name) / "backup.db"

        self.db.backup_to(str(backup_path))
        self.db.validate_backup_file(str(backup_path))

        self.db.conn.execute("DELETE FROM terms WHERE term_eng = 'Defendant'")
        self.db.conn.commit()
        modified_count = self.db.conn.execute("SELECT COUNT(*) FROM terms").fetchone()[0]
        self.assertEqual(modified_count, 2)

        self.db.replace_with_backup(str(backup_path))
        self.db = DBManager(str(self.db_path))

        restored_count = self.db.conn.execute("SELECT COUNT(*) FROM terms").fetchone()[0]
        restored_progress = self.db.get_progress(plaintiff_id)
        self.assertEqual(restored_count, 3)
        self.assertIsNotNone(restored_progress)
        self.assertEqual(restored_progress["correct_count"], 1)

    def test_validate_backup_rejects_non_database_file(self):
        bad_path = Path(self._tmpdir.name) / "bad.db"
        bad_path.write_text("not a legal english backup", encoding="utf-8")

        with self.assertRaises((ValueError, sqlite3.DatabaseError)):
            self.db.validate_backup_file(str(bad_path))

    def test_stats_and_weak_terms_follow_progress_data(self):
        plaintiff_id = self._term_id("Plaintiff")
        defendant_id = self._term_id("Defendant")
        consideration_id = self._term_id("Consideration")

        self.scheduler.review(plaintiff_id, 5)
        self.scheduler.review(defendant_id, 0)

        yesterday = (date.today() - timedelta(days=1)).isoformat()
        self.db.upsert_progress(
            consideration_id, yesterday, 1.6, 1, 0, 0, 3
        )

        stats = self.db.get_stats()
        weak_terms = self.db.get_weak_terms(limit=3)

        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["learned"], 1)
        self.assertEqual(stats["today_reviews"], 2)
        self.assertGreaterEqual(stats["avg_ease_factor"], 1.3)

        self.assertEqual(weak_terms[0]["term_eng"], "Consideration")
        self.assertEqual(weak_terms[0]["errors"], 3)
        self.assertEqual(weak_terms[1]["term_eng"], "Defendant")


if __name__ == "__main__":
    unittest.main()
