"""
Мини-тест: 5 вопросов с вариантами ответов (multiple choice).
Вызывается из FlashcardsWidget после каждых 10 оценённых карточек.
"""
import random

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont

from ..models.term import Term
from ..utils.sound_manager import get_sound_manager

NUM_QUESTIONS = 5
NUM_OPTIONS = 4


class QuizDialog(QDialog):
    def __init__(self, db_manager, seen_term_ids: list[int], parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._sounds = get_sound_manager()
        self.setWindowTitle("Мини-тест")
        self.setMinimumSize(520, 400)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)

        self._questions: list[dict] = []   # {term, options: [Term], correct_idx}
        self._current = 0
        self._score = 0
        self._answered = False

        self._prepare_questions(seen_term_ids)
        self._build_ui()
        self._show_question()

    # ── Prepare questions ─────────────────────────────────────────────
    def _prepare_questions(self, seen_ids: list[int]):
        if not seen_ids:
            return
        sample_ids = random.sample(seen_ids, min(NUM_QUESTIONS, len(seen_ids)))
        for tid in sample_ids:
            row = self.db.get_term(tid)
            if row is None:
                continue
            correct = Term.from_row(row)
            distractors_rows = self.db.get_random_terms_for_quiz(
                exclude_ids=[tid], n=NUM_OPTIONS - 1
            )
            distractors = [Term.from_row(r) for r in distractors_rows]
            options = distractors + [correct]
            random.shuffle(options)
            correct_idx = options.index(correct)
            self._questions.append({
                "term": correct,
                "options": options,
                "correct_idx": correct_idx,
            })

    # ── Build UI ──────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #a8acc8; font-size: 12px;")
        hdr.addWidget(self.progress_label)
        hdr.addStretch()
        self.score_label = QLabel("Очки: 0")
        self.score_label.setStyleSheet("color: #7eb8f7; font-size: 12px;")
        hdr.addWidget(self.score_label)
        root.addLayout(hdr)

        # Question card
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        prompt = QLabel("Как переводится термин?")
        prompt.setStyleSheet("color: #a8acc8; font-size: 12px;")
        prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(prompt)

        self.term_label = QLabel("")
        f = QFont()
        f.setPointSize(20)
        f.setBold(True)
        self.term_label.setFont(f)
        self.term_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.term_label.setWordWrap(True)
        card_layout.addWidget(self.term_label)

        root.addWidget(card, stretch=1)

        # Options
        self.option_btns: list[QPushButton] = []
        for i in range(NUM_OPTIONS):
            btn = QPushButton("")
            btn.setMinimumHeight(42)
            btn.setObjectName("matchBtn")
            btn.clicked.connect(lambda _, idx=i: self._answer(idx))
            self.option_btns.append(btn)
            root.addWidget(btn)

        # Feedback
        self.feedback_label = QLabel("")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setFont(QFont("", 12, QFont.Weight.Bold))
        root.addWidget(self.feedback_label)

        # Next / Close button
        self.next_btn = QPushButton("Следующий →")
        self.next_btn.setMinimumHeight(38)
        self.next_btn.hide()
        self.next_btn.clicked.connect(self._next)
        root.addWidget(self.next_btn)

    # ── Logic ─────────────────────────────────────────────────────────
    def _show_question(self):
        if self._current >= len(self._questions):
            self._show_result()
            return
        q = self._questions[self._current]
        self._answered = False
        self.feedback_label.setText("")
        self.next_btn.hide()
        self.progress_label.setText(
            f"Вопрос {self._current + 1} из {len(self._questions)}"
        )
        self.term_label.setText(q["term"].term_eng)
        for i, btn in enumerate(self.option_btns):
            if i < len(q["options"]):
                btn.setText(q["options"][i].term_rus)
                btn.setEnabled(True)
                btn.setStyleSheet("")
                btn.show()
            else:
                btn.hide()

    def _answer(self, idx: int):
        if self._answered:
            return
        self._answered = True
        q = self._questions[self._current]
        correct = q["correct_idx"]

        for btn in self.option_btns:
            btn.setEnabled(False)

        if idx == correct:
            self._score += 1
            self.score_label.setText(f"Очки: {self._score}")
            self.option_btns[idx].setStyleSheet(
                "color: #b8f0c0; border: 2px solid #48b860;"
            )
            self.feedback_label.setText("Верно!")
            self.feedback_label.setStyleSheet("color: #b8f0c0;")
            self._sounds.play("correct")
        else:
            self.option_btns[idx].setStyleSheet(
                "color: #f8b0c0; border: 2px solid #c04050;"
            )
            self.option_btns[correct].setStyleSheet(
                "color: #b8f0c0; border: 2px solid #48b860;"
            )
            self.feedback_label.setText(
                f"Неверно. Правильно: {q['options'][correct].term_rus}"
            )
            self.feedback_label.setStyleSheet("color: #f8b0c0;")
            self._sounds.play("wrong")

        self.next_btn.setText(
            "Результат →" if self._current + 1 >= len(self._questions)
            else "Следующий →"
        )
        self.next_btn.show()

    def _next(self):
        self._current += 1
        self._show_question()

    def _show_result(self):
        total = len(self._questions)
        for btn in self.option_btns:
            btn.hide()
        self.next_btn.hide()
        self.term_label.setText(f"{self._score} / {total}")
        self.term_label.setStyleSheet(
            "color: #b8f0c0;" if self._score == total else ""
        )
        pct = self._score / total * 100 if total else 0
        msg = (
            "Отлично! Все правильно!" if pct == 100
            else f"Хороший результат!" if pct >= 60
            else "Стоит повторить материал."
        )
        self.feedback_label.setText(msg)
        self.feedback_label.setStyleSheet("color: #7eb8f7;")
        if pct == 100:
            self._sounds.play("complete")

        close_btn = QPushButton("Закрыть")
        close_btn.setMinimumHeight(38)
        close_btn.clicked.connect(self.accept)
        self.layout().addWidget(close_btn)
