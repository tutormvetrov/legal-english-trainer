import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PyQt6.QtWidgets import QApplication

from src.algorithms.spaced_repetition import SpacedRepetitionScheduler
from src.database.db_manager import DBManager
from src.gui.context_widget import ContextWidget


class _SilentSounds:
    def play(self, name: str):
        return None


class ContextLearningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self._tmpdir.name) / "test.db"
        self.db = DBManager(str(db_path))
        self.scheduler = SpacedRepetitionScheduler(self.db)

    def tearDown(self):
        self.db.close()
        self._tmpdir.cleanup()

    def _import_terms(self):
        self.db.import_terms([
            {
                "term_eng": "consideration",
                "term_rus": "встречное удовлетворение",
                "definition": "Something of value exchanged in a contract.",
                "category": "Contract Law",
                "example": "Valid consideration is required for the agreement.",
            },
            {
                "term_eng": "plaintiff",
                "term_rus": "истец",
                "definition": "A party who brings a case before a court.",
                "category": "Civil Procedure",
                "example": "The plaintiff filed the claim in federal court.",
            },
        ])

    def test_get_term_with_example_can_be_limited_to_specific_ids(self):
        self._import_terms()
        rows = self.db.get_terms_by_category(limit=10)
        target_id = next(row["id"] for row in rows if row["term_eng"] == "plaintiff")

        row = self.db.get_term_with_example(term_ids=[target_id])

        self.assertIsNotNone(row)
        self.assertEqual(row["id"], target_id)

    def test_context_widget_prefers_due_terms_and_writes_progress(self):
        self._import_terms()
        consideration = self.db.conn.execute(
            "SELECT id FROM terms WHERE term_eng = 'consideration'"
        ).fetchone()[0]
        plaintiff = self.db.conn.execute(
            "SELECT id FROM terms WHERE term_eng = 'plaintiff'"
        ).fetchone()[0]

        # Make one term not due; the due queue should leave only "consideration".
        self.db.upsert_progress(
            plaintiff, "2099-01-01", 2.5, 5, 2, 2, 0
        )

        with patch("src.gui.context_widget.get_sound_manager", return_value=_SilentSounds()):
            widget = ContextWidget(self.db, self.scheduler)

        self.assertIsNotNone(widget.current_term)
        self.assertEqual(widget.current_term.id, consideration)

        widget.answer_input.setText("consideration")
        widget._check_answer()

        progress = self.db.get_progress(consideration)
        self.assertIsNotNone(progress)
        self.assertEqual(progress["correct_count"], 1)
        self.assertEqual(progress["wrong_count"], 0)
        self.assertEqual(progress["repetition"], 1)


if __name__ == "__main__":
    unittest.main()
