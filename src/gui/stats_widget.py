import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .import_dialog import ImportDialog


class StatsWidget(QWidget):
    def __init__(self, db_manager, db_path: str = ""):
        super().__init__()
        self.db = db_manager
        self._db_path = db_path
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

        # ── Weak terms table ──────────────────────────────────────────
        weak_label = QLabel("Сложные термины (чаще всего ошибаетесь):")
        weak_label.setFont(QFont("", 12, QFont.Weight.Bold))
        root.addWidget(weak_label)

        self.weak_table = QTableWidget()
        self.weak_table.setColumnCount(5)
        self.weak_table.setHorizontalHeaderLabels(
            ["Термин (EN)", "Термин (RU)", "Категория", "Лёгкость", "Ошибок"]
        )
        wh = self.weak_table.horizontalHeader()
        wh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        wh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        wh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        wh.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        wh.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.weak_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.weak_table.setAlternatingRowColors(True)
        self.weak_table.verticalHeader().setVisible(False)
        self.weak_table.setFixedHeight(180)
        root.addWidget(self.weak_table)

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

        import_btn = QPushButton("Импорт терминов…")
        import_btn.setMinimumHeight(36)
        import_btn.clicked.connect(self._import_terms)
        btn_row.addWidget(import_btn)

        backup_btn = QPushButton("💾 Резервная копия")
        backup_btn.setMinimumHeight(36)
        backup_btn.clicked.connect(self._backup_db)
        btn_row.addWidget(backup_btn)

        restore_btn = QPushButton("📂 Восстановить")
        restore_btn.setMinimumHeight(36)
        restore_btn.clicked.connect(self._restore_db)
        btn_row.addWidget(restore_btn)

        reset_btn = QPushButton("🔄 Сбросить")
        reset_btn.setMinimumHeight(36)
        reset_btn.setStyleSheet(
            "QPushButton { color: #f38ba8; }"
            "QPushButton:hover { color: #ff6b6b; }"
        )
        reset_btn.clicked.connect(self._open_reset_dialog)
        btn_row.addWidget(reset_btn)

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

        self._refresh_weak_table()

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

    def _refresh_weak_table(self):
        rows = self.db.get_weak_terms(limit=20)
        self.weak_table.setRowCount(0)
        for row in rows:
            r = self.weak_table.rowCount()
            self.weak_table.insertRow(r)
            self.weak_table.setItem(r, 0, QTableWidgetItem(row[0]))
            self.weak_table.setItem(r, 1, QTableWidgetItem(row[1]))
            self.weak_table.setItem(r, 2, QTableWidgetItem(row[2]))
            ef_item = self._centered(f"{row[3]:.2f}")
            # Colorise: red if ef < 2.0, yellow if < 2.5, green otherwise
            if row[3] < 2.0:
                ef_item.setForeground(__import__('PyQt6.QtGui', fromlist=['QColor']).QColor("#f38ba8"))
            elif row[3] < 2.5:
                ef_item.setForeground(__import__('PyQt6.QtGui', fromlist=['QColor']).QColor("#ffa726"))
            self.weak_table.setItem(r, 3, ef_item)
            self.weak_table.setItem(r, 4, self._centered(str(max(0, row[5]))))

    def _open_reset_dialog(self):
        from .reset_dialog import ResetDialog
        dlg = ResetDialog(self.db, self)
        if dlg.exec() == ResetDialog.DialogCode.Accepted:
            self.refresh()

    def _import_terms(self):
        dlg = ImportDialog(self.db, self)
        if dlg.exec():
            self.refresh()

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

    def _backup_db(self):
        if not self._db_path or not os.path.exists(self._db_path):
            QMessageBox.warning(self, "Ошибка", "Не удалось найти файл базы данных.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить резервную копию", "legal_english_backup.db",
            "База данных (*.db)"
        )
        if not path:
            return
        try:
            shutil.copy2(self._db_path, path)
            QMessageBox.information(self, "Готово", f"Резервная копия сохранена:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _restore_db(self):
        if not self._db_path:
            QMessageBox.warning(self, "Ошибка", "Не удалось найти файл базы данных.")
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать резервную копию", "",
            "База данных (*.db)"
        )
        if not path:
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Текущий прогресс будет заменён данными из резервной копии.\n"
            "Приложение закроется для применения изменений. Продолжить?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            self.db.close()
            shutil.copy2(path, self._db_path)
            from PyQt6.QtWidgets import QApplication
            QApplication.quit()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
