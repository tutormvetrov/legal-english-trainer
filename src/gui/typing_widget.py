from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFrame
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve
from PyQt6.QtGui import QFont

from ..models.term import Term
from ..utils.helpers import answers_match
from ..utils.sound_manager import get_sound_manager


class TypingWidget(QWidget):
    def __init__(self, db_manager, scheduler):
        super().__init__()
        self.db = db_manager
        self.scheduler = scheduler
        self.current_term = None
        self.direction_eng_to_rus = True
        self.attempts = 0
        self.score = 0
        self._sounds = get_sound_manager()
        self._shake_anim = None
        self._build_ui()
        self._load_categories()
        self._next_term()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # ── Controls ──────────────────────────────────────────────────
        ctrl = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(180)
        self.category_combo.currentIndexChanged.connect(self._next_term)
        ctrl.addWidget(QLabel("Категория:"))
        ctrl.addWidget(self.category_combo)
        ctrl.addSpacing(20)

        self.direction_btn = QPushButton("EN → RU")
        self.direction_btn.setMinimumWidth(110)
        self.direction_btn.setCheckable(True)
        self.direction_btn.clicked.connect(self._toggle_direction)
        ctrl.addWidget(QLabel("Направление:"))
        ctrl.addWidget(self.direction_btn)
        ctrl.addStretch()

        self.score_label = QLabel("Правильно: 0")
        ctrl.addWidget(self.score_label)
        root.addLayout(ctrl)

        # ── Card ──────────────────────────────────────────────────────
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(20)

        self.category_tag = QLabel("")
        self.category_tag.setObjectName("categoryTag")
        self.category_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.category_tag)

        self.term_label = QLabel("")
        self.term_label.setObjectName("termLabel")
        self.term_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.term_label.setWordWrap(True)
        tf = QFont()
        tf.setPointSize(22)
        tf.setBold(True)
        self.term_label.setFont(tf)
        card_layout.addWidget(self.term_label)

        prompt_lbl = QLabel("Введите перевод:")
        prompt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(prompt_lbl)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ваш ответ...")
        self.input_field.setMinimumHeight(40)
        self.input_field.returnPressed.connect(self._check_answer)
        card_layout.addWidget(self.input_field)

        self.feedback_label = QLabel("")
        self.feedback_label.setObjectName("feedbackLabel")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setWordWrap(True)
        fb_font = QFont()
        fb_font.setPointSize(12)
        self.feedback_label.setFont(fb_font)
        card_layout.addWidget(self.feedback_label)

        card_layout.addStretch()
        root.addWidget(card, stretch=1)

        # ── Buttons ───────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)

        self.check_btn = QPushButton("Проверить")
        self.check_btn.setMinimumHeight(44)
        self.check_btn.setMinimumWidth(140)
        self.check_btn.clicked.connect(self._check_answer)
        btn_row.addWidget(self.check_btn)

        self.next_btn = QPushButton("Следующий →")
        self.next_btn.setMinimumHeight(44)
        self.next_btn.setMinimumWidth(140)
        self.next_btn.hide()
        self.next_btn.clicked.connect(self._next_term)
        btn_row.addWidget(self.next_btn)

        self.skip_btn = QPushButton("Пропустить")
        self.skip_btn.setMinimumHeight(44)
        self.skip_btn.clicked.connect(self._skip)
        btn_row.addWidget(self.skip_btn)
        btn_row.addStretch()

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

    def _toggle_direction(self):
        self.direction_eng_to_rus = not self.direction_eng_to_rus
        self.direction_btn.setText("RU → EN" if not self.direction_eng_to_rus else "EN → RU")
        self._next_term()

    def _next_term(self):
        cat = self._current_category()
        row = self.db.get_random_term(cat)
        if row is None:
            self.term_label.setText("Нет терминов")
            return
        self.current_term = Term.from_row(row)
        self.attempts = 0
        self._render()

    def _render(self):
        if self.current_term is None:
            return
        self.category_tag.setText(self.current_term.category)
        if self.direction_eng_to_rus:
            self.term_label.setText(self.current_term.term_eng)
        else:
            self.term_label.setText(self.current_term.term_rus)

        self.input_field.clear()
        self.input_field.setEnabled(True)
        self.feedback_label.setText("")
        self.feedback_label.setStyleSheet("")
        self.check_btn.show()
        self.next_btn.hide()
        self.input_field.setFocus()

    def _correct_answer(self):
        if self.direction_eng_to_rus:
            return self.current_term.term_rus
        return self.current_term.term_eng

    def _check_answer(self):
        if self.current_term is None:
            return
        user = self.input_field.text()
        if not user.strip():
            return

        self.attempts += 1
        if answers_match(user, self._correct_answer()):
            quality = 5 if self.attempts == 1 else max(0, 4 - self.attempts)
            self.scheduler.review(self.current_term.id, quality)
            self.score += 1
            self.score_label.setText(f"Правильно: {self.score}")
            self.feedback_label.setText("✓ Верно!")
            self.feedback_label.setStyleSheet("color: #66bb6a;")
            self.input_field.setEnabled(False)
            self.check_btn.hide()
            self.next_btn.show()
            self._sounds.play("correct")
        else:
            self._sounds.play("wrong")
            self._shake_input()
            if self.attempts >= 3:
                self.scheduler.review(self.current_term.id, 0)
                self.feedback_label.setText(
                    f"✗ Неверно. Правильный ответ: {self._correct_answer()}"
                )
                self.feedback_label.setStyleSheet("color: #ef5350;")
                self.input_field.setEnabled(False)
                self.check_btn.hide()
                self.next_btn.show()
            else:
                self.feedback_label.setText(
                    f"✗ Неверно. Попыток: {self.attempts}/3. Попробуйте ещё."
                )
                self.feedback_label.setStyleSheet("color: #ffa726;")
                self.input_field.selectAll()
                self.input_field.setFocus()

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

    def _skip(self):
        if self.current_term:
            self.scheduler.review(self.current_term.id, 0)
        self._next_term()
