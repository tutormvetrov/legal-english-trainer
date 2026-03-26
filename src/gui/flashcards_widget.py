import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..models.term import Term


class FlashcardsWidget(QWidget):
    def __init__(self, db_manager, scheduler):
        super().__init__()
        self.db = db_manager
        self.scheduler = scheduler
        self.current_term = None
        self.direction_eng_to_rus = True  # True = EN→RU, False = RU→EN
        self.translation_shown = False
        self._build_ui()
        self._load_categories()
        self._next_term()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # ── Top controls ──────────────────────────────────────────────
        controls = QHBoxLayout()

        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(200)
        self.category_combo.currentIndexChanged.connect(self._next_term)
        controls.addWidget(QLabel("Категория:"))
        controls.addWidget(self.category_combo)
        controls.addSpacing(24)

        self.direction_btn = QPushButton("EN → RU")
        self.direction_btn.setCheckable(True)
        self.direction_btn.setChecked(False)
        self.direction_btn.setMinimumWidth(110)
        self.direction_btn.clicked.connect(self._toggle_direction)
        controls.addWidget(QLabel("Направление:"))
        controls.addWidget(self.direction_btn)
        controls.addStretch()

        self.counter_label = QLabel("")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        controls.addWidget(self.counter_label)

        root.addLayout(controls)

        # ── Card area ─────────────────────────────────────────────────
        self.card_frame = QFrame()
        self.card_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.card_frame.setObjectName("card")
        card_layout = QVBoxLayout(self.card_frame)
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
        term_font = QFont()
        term_font.setPointSize(22)
        term_font.setBold(True)
        self.term_label.setFont(term_font)
        card_layout.addWidget(self.term_label)

        # Translation area (hidden until revealed)
        self.translation_frame = QFrame()
        self.translation_frame.setObjectName("translationFrame")
        trans_layout = QVBoxLayout(self.translation_frame)
        trans_layout.setContentsMargins(0, 8, 0, 0)
        trans_layout.setSpacing(8)

        self.translation_label = QLabel("")
        self.translation_label.setObjectName("translationLabel")
        self.translation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.translation_label.setWordWrap(True)
        trans_font = QFont()
        trans_font.setPointSize(16)
        self.translation_label.setFont(trans_font)
        trans_layout.addWidget(self.translation_label)

        self.definition_label = QLabel("")
        self.definition_label.setObjectName("definitionLabel")
        self.definition_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.definition_label.setWordWrap(True)
        trans_layout.addWidget(self.definition_label)

        self.example_label = QLabel("")
        self.example_label.setObjectName("exampleLabel")
        self.example_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.example_label.setWordWrap(True)
        trans_layout.addWidget(self.example_label)

        self.translation_frame.hide()
        card_layout.addWidget(self.translation_frame)
        card_layout.addStretch()

        root.addWidget(self.card_frame, stretch=1)

        # ── Buttons ───────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)

        self.show_btn = QPushButton("Показать перевод")
        self.show_btn.setMinimumHeight(44)
        self.show_btn.clicked.connect(self._show_translation)
        btn_row.addWidget(self.show_btn)

        self.know_btn = QPushButton("Знаю ✓")
        self.know_btn.setObjectName("knowBtn")
        self.know_btn.setMinimumHeight(44)
        self.know_btn.hide()
        self.know_btn.clicked.connect(lambda: self._rate(5))
        btn_row.addWidget(self.know_btn)

        self.dontknow_btn = QPushButton("Не знаю ✗")
        self.dontknow_btn.setObjectName("dontKnowBtn")
        self.dontknow_btn.setMinimumHeight(44)
        self.dontknow_btn.hide()
        self.dontknow_btn.clicked.connect(lambda: self._rate(1))
        btn_row.addWidget(self.dontknow_btn)

        self.skip_btn = QPushButton("Пропустить →")
        self.skip_btn.setMinimumHeight(44)
        self.skip_btn.clicked.connect(self._next_term)
        btn_row.addWidget(self.skip_btn)

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
        # Prefer due terms; fall back to random
        due_ids = self.scheduler.get_due_terms(category=cat, limit=20)
        if due_ids:
            term_id = random.choice(due_ids)
            row = self.db.get_term(term_id)
        else:
            row = self.db.get_random_term(cat)

        if row is None:
            self.term_label.setText("Нет терминов")
            return

        self.current_term = Term.from_row(row)
        self._render_term()

        # Update due count
        total_due = len(self.scheduler.get_due_terms(category=cat, limit=1000))
        self.counter_label.setText(f"К повторению: {total_due}")

    def _render_term(self):
        if self.current_term is None:
            return
        self.translation_shown = False
        self.translation_frame.hide()
        self.show_btn.show()
        self.know_btn.hide()
        self.dontknow_btn.hide()

        self.category_tag.setText(self.current_term.category)

        if self.direction_eng_to_rus:
            self.term_label.setText(self.current_term.term_eng)
        else:
            self.term_label.setText(self.current_term.term_rus)

    def _show_translation(self):
        if self.current_term is None:
            return
        self.translation_shown = True

        if self.direction_eng_to_rus:
            self.translation_label.setText(self.current_term.term_rus)
        else:
            self.translation_label.setText(self.current_term.term_eng)

        self.definition_label.setText(self.current_term.definition)
        self.example_label.setText(f'"{self.current_term.example}"')

        self.translation_frame.show()
        self.show_btn.hide()
        self.know_btn.show()
        self.dontknow_btn.show()

    def _rate(self, quality: int):
        if self.current_term:
            self.scheduler.review(self.current_term.id, quality)
        self._next_term()
