import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from src.algorithms.spaced_repetition import SpacedRepetitionScheduler
from src.database.db_manager import DBManager
from src.gui.activation_dialog import ActivationDialog
from src.gui.attack_popup import AttackPopup
from src.gui.import_dialog import ImportDialog
from src.gui.main_window import MainWindow
from src.gui.quiz_dialog import QuizDialog
from src.gui.reset_dialog import ResetDialog
from src.gui.settings_dialog import SettingsDialog
from src.models.term import Term
from src.utils.license_manager import generate_key


class _SilentSounds:
    def play(self, name: str):
        return None


class GuiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self._tmpdir.name) / "gui.db"
        self.db = DBManager(str(db_path))
        self.scheduler = SpacedRepetitionScheduler(self.db)
        self.db.import_terms([
            {
                "term_eng": "Plaintiff",
                "term_rus": "Истец",
                "definition": "Party that brings a legal claim.",
                "category": "Civil Procedure",
                "example": "The plaintiff filed the complaint in court.",
            },
            {
                "term_eng": "Defendant",
                "term_rus": "Ответчик",
                "definition": "Party defending the lawsuit.",
                "category": "Civil Procedure",
                "example": "The defendant denied each allegation.",
            },
            {
                "term_eng": "Consideration",
                "term_rus": "Встречное удовлетворение",
                "definition": "Value exchanged under a contract.",
                "category": "Contract Law",
                "example": "The agreement failed for lack of consideration.",
            },
            {
                "term_eng": "Jurisdiction",
                "term_rus": "Юрисдикция",
                "definition": "Court's authority to hear a case.",
                "category": "Civil Procedure",
                "example": "The court lacked jurisdiction over the dispute.",
            },
            {
                "term_eng": "Tort",
                "term_rus": "Деликт",
                "definition": "Civil wrong causing legal liability.",
                "category": "Tort Law",
                "example": "Negligence is a common tort claim.",
            },
        ])
        self._stack = ExitStack()
        silent = _SilentSounds()
        for target in (
            "src.gui.flashcards_widget.get_sound_manager",
            "src.gui.match_widget.get_sound_manager",
            "src.gui.typing_widget.get_sound_manager",
            "src.gui.detective_widget.get_sound_manager",
            "src.gui.context_widget.get_sound_manager",
            "src.gui.boss_widget.get_sound_manager",
            "src.gui.quiz_dialog.get_sound_manager",
            "src.gui.attack_popup.get_sound_manager",
        ):
            self._stack.enter_context(patch(target, return_value=silent))

    def tearDown(self):
        self._stack.close()
        self.db.close()
        self._tmpdir.cleanup()

    def test_main_window_modes_smoke(self):
        window = MainWindow(self.db, self.scheduler, streak=3, username="Smoke", db_path=self.db.db_path)
        window.show()
        self.app.processEvents()

        self.assertEqual(window._tabs.count(), 8)

        flash = window.flashcards
        self.assertIsNotNone(flash.current_term)
        flash._show_translation()
        flash._rate(5)
        QTest.qWait(250)
        self.assertIsNotNone(flash.current_term)

        typing = window.typing
        typing.input_field.setText(typing._correct_answer())
        typing._check_answer()
        self.assertIn("Верно", typing.feedback_label.text())

        detective = window.detective
        detective.input_field.setText(detective._answer_text())
        detective._check_answer()
        self.assertTrue(detective._answered)

        context = window.context
        self.assertIsNotNone(context.current_term)
        context.answer_input.setText(context.current_term.term_eng)
        context._check_answer()
        self.assertTrue(context._answered)

        match = window.match
        match.count_spin.setValue(3)
        match._start_game()
        self.assertEqual(len(match.left_buttons), 3)
        right_pos = match.right_order.index(0)
        match._click_left(0)
        match._click_right(right_pos)
        self.assertEqual(match.correct, 1)

        boss = window.boss
        boss._start()
        self.assertTrue(boss._running)
        boss._answer(boss._correct_idx)
        QTest.qWait(350)
        self.assertGreaterEqual(boss._score, 1)
        boss._game_over("Smoke stop")
        self.assertFalse(boss._running)

        some_id = self.db.conn.execute("SELECT id FROM terms LIMIT 1").fetchone()[0]
        self.db.set_starred(some_id, True)
        window.favorites.refresh()
        self.assertGreaterEqual(len(window.favorites._terms), 1)

        window.stats.refresh()
        self.assertGreater(window.stats.table.rowCount(), 0)

        window.close()

    def test_dialogs_smoke(self):
        settings = SettingsDialog()
        self.assertEqual(settings.theme_combo.count(), 2)
        settings.close()

        importer = ImportDialog(self.db)
        importer.paste_area.setPlainText("Estoppel\tЭстоппель")
        importer._on_paste_changed()
        self.assertEqual(len(importer._rows), 1)
        importer.close()

        reset = ResetDialog(self.db)
        self.assertEqual(reset.windowTitle(), "Сброс")
        reset.close()

        seen_ids = [row["id"] for row in self.db.get_terms_by_category(limit=5)]
        quiz = QuizDialog(self.db, seen_ids)
        self.assertGreaterEqual(len(quiz._questions), 1)
        quiz.close()

        term_row = self.db.get_random_term()
        popup = AttackPopup(Term.from_row(term_row), self.scheduler)
        popup._skip()
        self.assertTrue(popup.result() in (0, 1))
        popup.close()

        activation = ActivationDialog()
        activation.key_input.setText(generate_key())
        activation._validate_key()
        self.assertEqual(activation._stack.currentIndex(), 1)
        activation.close()


if __name__ == "__main__":
    unittest.main()
