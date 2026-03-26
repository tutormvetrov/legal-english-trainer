from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..models.term import Term
from ..utils.tts_manager import speak


class FavoritesWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self._terms: list[Term] = []
        self._selected: Term | None = None
        self._build_ui()

    def refresh(self):
        self.search_input.clear()
        rows = self.db.get_starred_terms()
        self._terms = [Term.from_row(r) for r in rows]
        self._populate_table()
        self._clear_detail()

    def _on_search(self, text: str):
        if text.strip():
            rows = self.db.search_terms(text.strip())
            self._terms = [Term.from_row(r) for r in rows]
            self.count_label.setText(f"Найдено: {len(self._terms)} терминов")
        else:
            rows = self.db.get_starred_terms()
            self._terms = [Term.from_row(r) for r in rows]
        self._populate_table()
        self._clear_detail()

    # ── UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("Избранное")
        f = QFont()
        f.setPointSize(16)
        f.setBold(True)
        title.setFont(f)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        # ── Search bar ────────────────────────────────────────────────
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по всем терминам…")
        self.search_input.textChanged.connect(self._on_search)
        search_row.addWidget(self.search_input)
        root.addLayout(search_row)

        self.count_label = QLabel("")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label.setStyleSheet("color: #a8acc8; font-size: 12px;")
        root.addWidget(self.count_label)

        # Split: table (left/top) + detail card (right/bottom)
        split = QHBoxLayout()
        split.setSpacing(16)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Термин (EN)", "Перевод (RU)", "Категория"])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self._on_select)
        split.addWidget(self.table, stretch=3)

        # Detail panel
        detail_col = QVBoxLayout()
        detail_col.setSpacing(10)

        self.detail_card = QFrame()
        self.detail_card.setObjectName("card")
        detail_layout = QVBoxLayout(self.detail_card)
        detail_layout.setContentsMargins(16, 16, 16, 16)
        detail_layout.setSpacing(10)

        self.d_eng = QLabel("")
        self.d_eng.setObjectName("termLabel")
        self.d_eng.setWordWrap(True)
        ef = QFont()
        ef.setPointSize(16)
        ef.setBold(True)
        self.d_eng.setFont(ef)
        detail_layout.addWidget(self.d_eng)

        self.d_rus = QLabel("")
        self.d_rus.setObjectName("translationLabel")
        self.d_rus.setWordWrap(True)
        rf = QFont()
        rf.setPointSize(13)
        self.d_rus.setFont(rf)
        detail_layout.addWidget(self.d_rus)

        self.d_def = QLabel("")
        self.d_def.setObjectName("definitionLabel")
        self.d_def.setWordWrap(True)
        detail_layout.addWidget(self.d_def)

        self.d_ex = QLabel("")
        self.d_ex.setObjectName("exampleLabel")
        self.d_ex.setWordWrap(True)
        detail_layout.addWidget(self.d_ex)

        detail_layout.addStretch()
        detail_col.addWidget(self.detail_card, stretch=1)

        # Buttons under detail
        btn_col = QVBoxLayout()
        btn_col.setSpacing(8)

        self.listen_btn = QPushButton("🔊 Послушать")
        self.listen_btn.setMinimumHeight(36)
        self.listen_btn.setEnabled(False)
        self.listen_btn.clicked.connect(self._listen)
        btn_col.addWidget(self.listen_btn)

        self.unstar_btn = QPushButton("☆ Убрать из избранного")
        self.unstar_btn.setMinimumHeight(36)
        self.unstar_btn.setEnabled(False)
        self.unstar_btn.clicked.connect(self._unstar)
        btn_col.addWidget(self.unstar_btn)

        detail_col.addLayout(btn_col)
        split.addLayout(detail_col, stretch=2)
        root.addLayout(split, stretch=1)

    # ── Data ──────────────────────────────────────────────────────────
    def _populate_table(self):
        self.table.setRowCount(0)
        for term in self._terms:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(term.term_eng))
            self.table.setItem(r, 1, QTableWidgetItem(term.term_rus))
            self.table.setItem(r, 2, QTableWidgetItem(term.category))
        self.count_label.setText(
            f"Помечено звёздочкой: {len(self._terms)} терминов"
            if self._terms else "Нет избранных терминов. "
                                "Нажмите ★ на карточке, чтобы добавить."
        )

    def _on_select(self):
        rows = self.table.selectedItems()
        if not rows:
            self._clear_detail()
            return
        idx = self.table.currentRow()
        if 0 <= idx < len(self._terms):
            self._selected = self._terms[idx]
            self._show_detail(self._selected)

    def _show_detail(self, t: Term):
        self.d_eng.setText(t.term_eng)
        self.d_rus.setText(t.term_rus)
        self.d_def.setText(t.definition or "")
        self.d_ex.setText(f'"{t.example}"' if t.example else "")
        self.listen_btn.setEnabled(True)
        self.unstar_btn.setEnabled(True)

    def _clear_detail(self):
        self._selected = None
        self.d_eng.setText("")
        self.d_rus.setText("")
        self.d_def.setText("")
        self.d_ex.setText("")
        self.listen_btn.setEnabled(False)
        self.unstar_btn.setEnabled(False)

    def _listen(self):
        if self._selected:
            speak(self._selected.term_eng)

    def _unstar(self):
        if self._selected:
            self.db.set_starred(self._selected.id, False)
            self.refresh()
