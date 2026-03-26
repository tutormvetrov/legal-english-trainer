"""
Режим Детектив — угадай юридический термин по его определению.
Буквы открываются по одной (Wheel of Fortune style).
Очки зависят от количества использованных подсказок.
"""
import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve
from PyQt6.QtGui import QFont

try:
    from ..models.term import Term
    from ..utils.helpers import answers_match
    from ..utils.sound_manager import get_sound_manager
except ImportError:
    from models.term import Term
    from utils.helpers import answers_match
    from utils.sound_manager import get_sound_manager


class DetectiveWidget(QWidget):
    def __init__(self, db_manager, scheduler):
        super().__init__()
        self.db = db_manager
        self.scheduler = scheduler
        self._sounds = get_sound_manager()
        self.current_term: Term | None = None
        self._revealed: set[int] = set()
        self._reveal_count = 0
        self._wrong_guesses = 0
        self._score = 100
        self._session_points = 0
        self._session_correct = 0
        self._answered = False
        self._shake_anim = None
        self._build_ui()
        self._load_categories()
        self._next_term()

    # ── Build UI ───────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        # Controls row
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Категория:"))
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(190)
        ctrl.addWidget(self.category_combo)
        ctrl.addStretch()

        self.session_label = QLabel("Сессия: 0 правильно | 0 очков")
        self.session_label.setStyleSheet("color: #8890b8; font-size: 12px;")
        ctrl.addWidget(self.session_label)
        root.addLayout(ctrl)

        # Definition card
        def_card = QFrame()
        def_card.setObjectName("card")
        def_layout = QVBoxLayout(def_card)
        def_layout.setContentsMargins(16, 12, 16, 12)
        def_layout.setSpacing(6)

        hint_lbl = QLabel("Определение:")
        hint_lbl.setStyleSheet("color: #8890b8; font-size: 11px; letter-spacing: 1px;")
        def_layout.addWidget(hint_lbl)

        self.definition_label = QLabel()
        self.definition_label.setObjectName("definitionLabel")
        self.definition_label.setWordWrap(True)
        df = QFont()
        df.setPointSize(12)
        self.definition_label.setFont(df)
        self.definition_label.setStyleSheet("color: #c0c8e8; font-style: italic;")
        def_layout.addWidget(self.definition_label)

        root.addWidget(def_card)

        # Term display (underscores)
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setWordWrap(True)
        disp_font = QFont("Courier New", 22)
        disp_font.setBold(True)
        self.display_label.setFont(disp_font)
        self.display_label.setMinimumHeight(60)
        self.display_label.setStyleSheet("color: #eeffff; letter-spacing: 2px;")
        root.addWidget(self.display_label)

        # Score label
        score_row = QHBoxLayout()
        score_row.addStretch()
        self.score_label = QLabel("Очки: 100")
        self.score_label.setStyleSheet("color: #82aaff; font-weight: bold; font-size: 13px;")
        score_row.addWidget(self.score_label)
        root.addLayout(score_row)

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите термин целиком…")
        self.input_field.setMinimumHeight(40)
        self.input_field.returnPressed.connect(self._check_answer)
        input_row.addWidget(self.input_field, stretch=1)

        self.check_btn = QPushButton("Проверить")
        self.check_btn.setMinimumHeight(40)
        self.check_btn.setMinimumWidth(110)
        self.check_btn.clicked.connect(self._check_answer)
        input_row.addWidget(self.check_btn)
        root.addLayout(input_row)

        # Feedback
        self.feedback_label = QLabel("")
        self.feedback_label.setObjectName("feedbackLabel")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setWordWrap(True)
        self.feedback_label.hide()
        root.addWidget(self.feedback_label)

        # Action buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.reveal_btn = QPushButton("💡 Открыть букву  (−10 очков)")
        self.reveal_btn.setMinimumHeight(38)
        self.reveal_btn.clicked.connect(self._reveal_letter)
        btn_row.addWidget(self.reveal_btn)

        self.give_up_btn = QPushButton("Сдаться")
        self.give_up_btn.setMinimumHeight(38)
        self.give_up_btn.setStyleSheet("color: #8890b8;")
        self.give_up_btn.clicked.connect(self._give_up)
        btn_row.addWidget(self.give_up_btn)

        self.next_btn = QPushButton("Следующий →")
        self.next_btn.setMinimumHeight(38)
        self.next_btn.setMinimumWidth(130)
        self.next_btn.clicked.connect(self._next_term)
        self.next_btn.hide()
        btn_row.addWidget(self.next_btn)

        root.addLayout(btn_row)
        root.addStretch()

    # ── Categories ─────────────────────────────────────────────────────────

    def _load_categories(self):
        self.category_combo.clear()
        self.category_combo.addItem("Все категории")
        for cat in self.db.get_all_categories():
            self.category_combo.addItem(cat)
        self.category_combo.currentIndexChanged.connect(self._next_term)

    def _current_category(self) -> str | None:
        text = self.category_combo.currentText()
        return None if text == "Все категории" else text

    # ── Term logic ─────────────────────────────────────────────────────────

    def _next_term(self):
        cat = self._current_category()
        row = self.db.get_term_with_definition(cat)
        if row is None:
            row = self.db.get_random_term(cat)
        if row is None:
            self.definition_label.setText("Нет терминов в этой категории.")
            self.display_label.setText("")
            return
        self.current_term = Term.from_row(row)
        self._revealed = set()
        self._reveal_count = 0
        self._wrong_guesses = 0
        self._score = 100
        self._answered = False
        self._render()

    def _answer_text(self) -> str:
        if self.current_term is None:
            return ""
        return self.current_term.term_eng

    def _eligible_positions(self) -> list[int]:
        """Индексы букв, которые можно раскрыть (не первая буква слова, не пробел)."""
        answer = self._answer_text()
        positions = []
        prev_space = True
        for i, ch in enumerate(answer):
            if ch == ' ':
                prev_space = True
            else:
                if not prev_space:
                    positions.append(i)
                prev_space = False
        return positions

    def _build_display(self) -> str:
        """Строит строку вида 'A _ _ _ _ _  a _ _ _' для отображения."""
        if self.current_term is None:
            return ""
        answer = self._answer_text()
        chars = []
        prev_space = True
        for i, ch in enumerate(answer):
            if ch == ' ':
                chars.append('\u2002\u2002')  # en-spaces as word gap
                prev_space = True
            else:
                if prev_space:
                    chars.append(ch)       # first letter of word: always visible
                elif i in self._revealed:
                    chars.append(ch)       # revealed letter
                else:
                    chars.append('_')
                prev_space = False
        # Insert spaces between each character token for readability
        result = []
        for token in chars:
            if token == '\u2002\u2002':
                result.append('   ')       # word boundary gap
            else:
                result.append(f' {token} ')
        return ''.join(result).strip()

    def _render(self):
        t = self.current_term
        self.definition_label.setText(
            t.definition if t.definition and t.definition.strip()
            else (t.example or "Нет определения")
        )
        self.display_label.setText(self._build_display())
        self.display_label.setStyleSheet("color: #eeffff; letter-spacing: 2px;")
        self.score_label.setText("Очки: 100")
        self.feedback_label.hide()
        self.feedback_label.setText("")
        self.reveal_btn.setEnabled(True)
        self.give_up_btn.setEnabled(True)
        self.check_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.clear()
        self.next_btn.hide()
        self.input_field.setFocus()

    def _update_display(self):
        self.display_label.setText(self._build_display())

    # ── Game actions ───────────────────────────────────────────────────────

    def _reveal_letter(self):
        if self._answered:
            return
        eligible = self._eligible_positions()
        unrevealed = [p for p in eligible if p not in self._revealed]
        if not unrevealed:
            return
        self._revealed.add(random.choice(unrevealed))
        self._reveal_count += 1
        self._score = max(0, self._score - 10)
        self._update_display()
        self.score_label.setText(f"Очки: {self._score}")

    def _sm2_quality(self) -> int:
        if self._reveal_count == 0 and self._wrong_guesses == 0:
            return 5
        elif self._reveal_count <= 2 and self._wrong_guesses == 0:
            return 4
        elif self._reveal_count <= 4:
            return 3
        else:
            return 2

    def _check_answer(self):
        if self._answered:
            return
        user = self.input_field.text().strip()
        if not user:
            return

        if answers_match(user, self._answer_text()):
            self._answered = True
            quality = self._sm2_quality()
            self.scheduler.review(self.current_term.id, quality)
            self._session_correct += 1
            self._session_points += self._score
            self._sounds.play("correct")

            self.display_label.setText(self._answer_text())
            self.display_label.setStyleSheet("color: #c3e88d; letter-spacing: 2px;")
            self.feedback_label.setText(
                f"✓ Верно!   Очки за раунд: {self._score}"
            )
            self.feedback_label.setStyleSheet("color: #c3e88d; font-weight: bold; font-size: 13px;")
            self.feedback_label.show()
            self._update_session_label()
            self._show_next_btn()
        else:
            self._wrong_guesses += 1
            self._score = max(0, self._score - 25)
            self._sounds.play("wrong")
            self._shake_input()
            self.feedback_label.setText(
                f"✗ Неверно.   Очки: {self._score}"
            )
            self.feedback_label.setStyleSheet("color: #f07178;")
            self.feedback_label.show()
            self.score_label.setText(f"Очки: {self._score}")
            self.input_field.selectAll()
            self.input_field.setFocus()

    def _give_up(self):
        if self._answered:
            return
        self._answered = True
        self.scheduler.review(self.current_term.id, 0)
        self._score = 0
        self._sounds.play("wrong")
        self.display_label.setText(self._answer_text())
        self.display_label.setStyleSheet("color: #f07178; letter-spacing: 2px;")
        self.feedback_label.setText(f"Ответ: {self._answer_text()}")
        self.feedback_label.setStyleSheet("color: #f07178;")
        self.feedback_label.show()
        self.score_label.setText("Очки: 0")
        self._update_session_label()
        self._show_next_btn()

    def _show_next_btn(self):
        self.reveal_btn.setEnabled(False)
        self.give_up_btn.setEnabled(False)
        self.check_btn.setEnabled(False)
        self.input_field.setEnabled(False)
        self.next_btn.show()

    def _update_session_label(self):
        self.session_label.setText(
            f"Сессия: {self._session_correct} правильно | {self._session_points} очков"
        )

    def _shake_input(self):
        orig = self.input_field.pos()
        self._shake_anim = QPropertyAnimation(self.input_field, b"pos")
        self._shake_anim.setDuration(300)
        self._shake_anim.setKeyValueAt(0.0, orig)
        self._shake_anim.setKeyValueAt(0.2, QPoint(orig.x() - 7, orig.y()))
        self._shake_anim.setKeyValueAt(0.4, QPoint(orig.x() + 7, orig.y()))
        self._shake_anim.setKeyValueAt(0.6, QPoint(orig.x() - 5, orig.y()))
        self._shake_anim.setKeyValueAt(0.8, QPoint(orig.x() + 5, orig.y()))
        self._shake_anim.setKeyValueAt(1.0, orig)
        self._shake_anim.setEasingCurve(QEasingCurve.Type.Linear)
        self._shake_anim.start()
