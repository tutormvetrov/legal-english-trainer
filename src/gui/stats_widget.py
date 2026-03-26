import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class StatsWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        # ── Title ─────────────────────────────────────────────────────
        title = QLabel("Статистика обучения")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        # ── Summary cards ─────────────────────────────────────────────
        summary_row = QHBoxLayout()
        summary_row.setSpacing(16)

        self.total_card = self._make_stat_card("Всего терминов", "0")
        self.learned_card = self._make_stat_card("Изучено", "0")
        self.percent_card = self._make_stat_card("Прогресс", "0%")
        self.today_card = self._make_stat_card("Повторений сегодня", "0")
        self.ef_card = self._make_stat_card("Средняя лёгкость", "2.50")

        for card in (self.total_card, self.learned_card, self.percent_card,
                     self.today_card, self.ef_card):
            summary_row.addWidget(card)

        root.addLayout(summary_row)

        # ── Category table ────────────────────────────────────────────
        cat_label = QLabel("По категориям:")
        cat_label.setFont(QFont("", 12, QFont.Weight.Bold))
        root.addWidget(cat_label)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Категория", "Всего терминов", "Изучено", "Прогресс, %"]
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        root.addWidget(self.table, stretch=1)

        # ── Buttons ───────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        refresh_btn = QPushButton("Обновить")
        refresh_btn.setMinimumHeight(36)
        refresh_btn.clicked.connect(self.refresh)
        btn_row.addWidget(refresh_btn)

        export_btn = QPushButton("Экспорт в CSV")
        export_btn.setMinimumHeight(36)
        export_btn.clicked.connect(self._export_csv)
        btn_row.addWidget(export_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

    def _make_stat_card(self, title: str, value: str) -> QWidget:
        frame = QWidget()
        frame.setObjectName("statCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        val_lbl = QLabel(value)
        val_font = QFont()
        val_font.setPointSize(22)
        val_font.setBold(True)
        val_lbl.setFont(val_font)
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val_lbl.setObjectName("statValue")
        layout.addWidget(val_lbl)

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setObjectName("statTitle")
        layout.addWidget(title_lbl)

        frame._value_label = val_lbl
        return frame

    def _set_card(self, card, value: str):
        card._value_label.setText(value)

    def refresh(self):
        stats = self.db.get_stats()
        total = stats["total"]
        learned = stats["learned"]
        pct = round(learned / total * 100, 1) if total else 0

        self._set_card(self.total_card, str(total))
        self._set_card(self.learned_card, str(learned))
        self._set_card(self.percent_card, f"{pct}%")
        self._set_card(self.today_card, str(stats["today_reviews"]))
        self._set_card(self.ef_card, f"{stats['avg_ease_factor']:.2f}")

        rows = self.db.get_stats_by_category()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            cat_total = row["total"]
            cat_learned = row["learned"]
            cat_pct = round(cat_learned / cat_total * 100, 1) if cat_total else 0

            self.table.setItem(i, 0, QTableWidgetItem(row["category"]))
            self.table.setItem(i, 1, self._centered(str(cat_total)))
            self.table.setItem(i, 2, self._centered(str(cat_learned)))
            self.table.setItem(i, 3, self._centered(f"{cat_pct}%"))

    def _centered(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить прогресс", "progress.csv",
            "CSV файлы (*.csv)"
        )
        if not path:
            return
        try:
            self.db.export_progress_csv(path)
            QMessageBox.information(self, "Экспорт", f"Файл сохранён:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
