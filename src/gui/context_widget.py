"""
Режим «Контекст» — восстановление термина по примеру предложения.
Показывается предложение с пропущенным английским термином (___).
Пользователь вписывает пропущенное слово.
"""
import re

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

try:
    from ..models.term import Term
    from ..utils.sound_manager import get_sound_manager
    from ..utils import tts_manager
    from ..utils.helpers import answers_match
except ImportError:
    from models.term import Term
    from utils.sound_manager import get_sound_manager
    from utils import tts_manager
    from utils.helpers import answers_match


class ContextWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_term: Term | None = None
        self._sounds = get_sound_manager()
        self._score = 0
        self._total = 0
        self._answered = False
        self._build_ui()
        self._load_categories()
        self._next_term()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # ── Controls ──────────────────────────────────────────────────
        controls = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(200)
        self.category_combo.currentIndexChanged.connect(self._next_term)
        controls.addWidget(QLabel("Категория:"))
        controls.addWidget(self.category_combo)
        controls.addStretch()
        self.score_lbl = QLabel("Верно: 0 / 0")
        self.score_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        controls.addWidget(self.score_lbl)
        root.addLayout(controls)

        # ── Card ──────────────────────────────────────────────────────
        self.card_frame = QFrame()
        self.card_frame.setObjectName("card")
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(14)

        self.category_tag = QLabel("")
        self.category_tag.setObjectName("categoryTag")
        self.category_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.category_tag)

        hint = QLabel("Восстановите пропущенный термин:")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: #a8acc8; font-size: 12px;")
        card_layout.addWidget(hint)

        self.context_lbl = QLabel("")
        self.context_lbl.setObjectName("termLabel")
        self.context_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.context_lbl.setWordWrap(True)
        ctx_font = QFont()
        ctx_font.setPointSize(16)
        self.context_lbl.setFont(ctx_font)
        card_layout.addWidget(self.context_lbl)

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Введите пропущенный термин…")
        self.answer_input.returnPressed.connect(self._check_answer)
        self.answer_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.answer_input)

        self.feedback_lbl = QLabel("")
        self.feedback_lbl.setObjectName("feedbackLabel")
        self.feedback_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_lbl.setWordWrap(True)
        self.feedback_lbl.hide()
        card_layout.addWidget(self.feedback_lbl)

        self.translation_lbl = QLabel("")
        self.translation_lbl.setObjectName("translationLabel")
        self.translation_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.translation_lbl.setWordWrap(True)
        self.translation_lbl.hide()
        card_layout.addWidget(self.translation_lbl)

        card_layout.addStretch()
        root.addWidget(self.card_frame, stretch=1)

        # ── Buttons ───────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.listen_btn = QPushButton("🔊")
        self.listen_btn.setFixedSize(44, 44)
        self.listen_btn.setToolTip("Прослушать термин")
        self.listen_btn.clicked.connect(self._listen)
        self.listen_btn.hide()
        btn_row.addWidget(self.listen_btn)

        self.check_btn = QPushButton("Проверить")
        self.check_btn.setMinimumHeight(44)
        self.check_btn.clicked.connect(self._check_answer)
        btn_row.addWidget(self.check_btn)

        self.next_btn = QPushButton("Далее →")
        self.next_btn.setMinimumHeight(44)
        self.next_btn.clicked.connect(self._next_term)
        self.next_btn.hide()
        btn_row.addWidget(self.next_btn)

        root.addLayout(btn_row)

    def _load_categories(self):
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem("Все категории")
        for cat in self.db.get_all_categories():
            self.category_combo.addItem(cat)
        self.category_combo.blockSignals(False)

    def _current_category(self):
        text = self.category_combo.currentText()
        return None if text == "Все категории" else text

    def _next_term(self):
        self._answered = False
        cat = self._current_category()
        row = self.db.get_term_with_example(cat)
        if row is None:
            self.context_lbl.setText("Нет терминов с примерами для этой категории.")
            self.answer_input.setEnabled(False)
            self.check_btn.setEnabled(False)
            return
        self.check_btn.setEnabled(True)
        self.answer_input.setEnabled(True)
        self.current_term = Term.from_row(row)
        self._render()

    def _render(self):
        t = self.current_term
        self.category_tag.setText(t.category)
        self.feedback_lbl.hide()
        self.translation_lbl.hide()
        self.listen_btn.hide()
        self.next_btn.hide()
        self.check_btn.show()
        self.answer_input.setEnabled(True)
        self.answer_input.clear()
        self.answer_input.setFocus()
        self.context_lbl.setText(self._blank_example(t.example, t.term_eng))

    def _blank_example(self, example: str, term: str) -> str:
        if not example or not term:
            return example or ""
        return re.sub(re.escape(term), "___", example, flags=re.IGNORECASE)

    def _check_answer(self):
        if self._answered or self.current_term is None:
            return
        user_ans = self.answer_input.text().strip()
        if not user_ans:
            return
        self._answered = True
        self._total += 1
        correct = answers_match(user_ans, self.current_term.term_eng)
        self.answer_input.setEnabled(False)
        self.check_btn.hide()
        self.next_btn.show()
        self.listen_btn.show()
        self.feedback_lbl.show()
        self.translation_lbl.show()
        if correct:
            self._score += 1
            self.feedback_lbl.setText(f"✓ Верно! «{self.current_term.term_eng}»")
            self.feedback_lbl.setStyleSheet("color: #b8f0c0; font-weight: bold;")
            self._sounds.play("correct")
        else:
            self.feedback_lbl.setText(
                f"✗ Неверно. Правильный ответ: «{self.current_term.term_eng}»"
            )
            self.feedback_lbl.setStyleSheet("color: #f8b0c0; font-weight: bold;")
            self._sounds.play("wrong")
        self.translation_lbl.setText(f"Перевод: {self.current_term.term_rus}")
        self.score_lbl.setText(f"Верно: {self._score} / {self._total}")

    def _listen(self):
        if self.current_term:
            tts_manager.speak(self.current_term.term_eng)
