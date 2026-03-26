import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..models.term import Term


class MatchWidget(QWidget):
    def __init__(self, db_manager, scheduler):
        super().__init__()
        self.db = db_manager
        self.scheduler = scheduler
        self.terms = []
        self.selected_left = None   # index into self.terms
        self.selected_right = None  # index into self.terms (shuffled order)
        self.matched = set()        # matched term ids
        self.correct = 0
        self.left_buttons = []
        self.right_buttons = []
        self.right_order = []       # shuffled indices for right column
        self._build_ui()
        self._load_categories()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # ── Controls ──────────────────────────────────────────────────
        ctrl = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(180)
        ctrl.addWidget(QLabel("Категория:"))
        ctrl.addWidget(self.category_combo)
        ctrl.addSpacing(16)

        ctrl.addWidget(QLabel("Терминов:"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(3, 10)
        self.count_spin.setValue(5)
        ctrl.addWidget(self.count_spin)
        ctrl.addStretch()

        self.new_game_btn = QPushButton("Новая игра")
        self.new_game_btn.setMinimumWidth(130)
        self.new_game_btn.setMinimumHeight(36)
        self.new_game_btn.clicked.connect(self._start_game)
        ctrl.addWidget(self.new_game_btn)
        root.addLayout(ctrl)

        # ── Score ─────────────────────────────────────────────────────
        self.score_label = QLabel("")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_font = QFont()
        score_font.setPointSize(11)
        self.score_label.setFont(score_font)
        root.addWidget(self.score_label)

        # ── Game area ─────────────────────────────────────────────────
        game_row = QHBoxLayout()
        game_row.setSpacing(32)

        left_col = QVBoxLayout()
        left_col.setSpacing(8)
        self.left_header = QLabel("Термины")
        self.left_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_header.setObjectName("colHeader")
        left_col.addWidget(self.left_header)
        self.left_container = QVBoxLayout()
        self.left_container.setSpacing(8)
        left_col.addLayout(self.left_container)
        left_col.addStretch()
        game_row.addLayout(left_col, stretch=1)

        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        self.right_header = QLabel("Переводы")
        self.right_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_header.setObjectName("colHeader")
        right_col.addWidget(self.right_header)
        self.right_container = QVBoxLayout()
        self.right_container.setSpacing(8)
        right_col.addLayout(self.right_container)
        right_col.addStretch()
        game_row.addLayout(right_col, stretch=1)

        root.addLayout(game_row, stretch=1)

        # ── Result ────────────────────────────────────────────────────
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_font = QFont()
        result_font.setPointSize(14)
        result_font.setBold(True)
        self.result_label.setFont(result_font)
        self.result_label.hide()
        root.addWidget(self.result_label)

    def _load_categories(self):
        self.category_combo.clear()
        self.category_combo.addItem("Все категории")
        for cat in self.db.get_all_categories():
            self.category_combo.addItem(cat)

    def _current_category(self):
        text = self.category_combo.currentText()
        return None if text == "Все категории" else text

    def _clear_game(self):
        for btn in self.left_buttons + self.right_buttons:
            btn.setParent(None)
        self.left_buttons.clear()
        self.right_buttons.clear()

    def _start_game(self):
        self._clear_game()
        self.selected_left = None
        self.selected_right = None
        self.matched.clear()
        self.correct = 0
        self.result_label.hide()

        cat = self._current_category()
        n = self.count_spin.value()
        rows = self.db.get_terms_by_category(cat, limit=n)
        self.terms = [Term.from_row(r) for r in rows]

        if not self.terms:
            self.score_label.setText("Нет терминов для игры")
            return

        self.right_order = list(range(len(self.terms)))
        random.shuffle(self.right_order)
        self.score_label.setText(f"Совпадений: 0 / {len(self.terms)}")

        for i, term in enumerate(self.terms):
            btn = QPushButton(term.term_eng)
            btn.setObjectName("matchBtn")
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, idx=i: self._click_left(idx))
            self.left_buttons.append(btn)
            self.left_container.addWidget(btn)

        for pos, idx in enumerate(self.right_order):
            term = self.terms[idx]
            btn = QPushButton(term.term_rus)
            btn.setObjectName("matchBtn")
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, pos=pos: self._click_right(pos))
            self.right_buttons.append(btn)
            self.right_container.addWidget(btn)

    def _click_left(self, idx):
        if idx in self.matched or self.left_buttons[idx].isEnabled() is False:
            return
        # Deselect previous
        if self.selected_left is not None:
            self.left_buttons[self.selected_left].setObjectName("matchBtn")
            self.left_buttons[self.selected_left].setStyleSheet("")
        self.selected_left = idx
        self.left_buttons[idx].setObjectName("matchBtnSelected")
        self.left_buttons[idx].setStyleSheet("border: 2px solid #4fc3f7;")
        self._try_match()

    def _click_right(self, pos):
        term_idx = self.right_order[pos]
        if term_idx in self.matched or not self.right_buttons[pos].isEnabled():
            return
        if self.selected_right is not None:
            self.right_buttons[self.selected_right].setStyleSheet("")
        self.selected_right = pos
        self.right_buttons[pos].setStyleSheet("border: 2px solid #4fc3f7;")
        self._try_match()

    def _try_match(self):
        if self.selected_left is None or self.selected_right is None:
            return
        left_idx = self.selected_left
        right_pos = self.selected_right
        right_idx = self.right_order[right_pos]

        if left_idx == right_idx:
            # Correct
            self.correct += 1
            self.matched.add(left_idx)
            self.left_buttons[left_idx].setEnabled(False)
            self.left_buttons[left_idx].setStyleSheet("color: #66bb6a; border: 2px solid #66bb6a;")
            self.right_buttons[right_pos].setEnabled(False)
            self.right_buttons[right_pos].setStyleSheet("color: #66bb6a; border: 2px solid #66bb6a;")
            self.scheduler.review(self.terms[left_idx].id, 5)
        else:
            # Wrong
            self.left_buttons[left_idx].setStyleSheet("border: 2px solid #ef5350;")
            self.right_buttons[right_pos].setStyleSheet("border: 2px solid #ef5350;")
            # Reset after brief flash
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(600, lambda: self._reset_wrong(left_idx, right_pos))

        self.selected_left = None
        self.selected_right = None
        self.score_label.setText(f"Совпадений: {self.correct} / {len(self.terms)}")

        if self.correct == len(self.terms):
            self.result_label.setText(f"Правильно: {self.correct} из {len(self.terms)} 🎉")
            self.result_label.show()

    def _reset_wrong(self, left_idx, right_pos):
        if self.left_buttons[left_idx].isEnabled():
            self.left_buttons[left_idx].setStyleSheet("")
        if self.right_buttons[right_pos].isEnabled():
            self.right_buttons[right_pos].setStyleSheet("")
