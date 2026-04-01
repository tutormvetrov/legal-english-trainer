import csv
import json

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTabWidget, QWidget, QTextEdit, QRadioButton, QButtonGroup, QLineEdit,
    QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

_ALL_FIELDS = ("term_eng", "term_rus", "definition", "category", "example")
_REQUIRED = {"term_eng", "term_rus"}


class ImportDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._rows: list[dict] = []
        self.setWindowTitle("Импорт терминов")
        self.setMinimumSize(760, 560)
        self._build_ui()

    # ══════════════════════════════════════════════════════════════════
    # UI
    # ══════════════════════════════════════════════════════════════════
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_paste_tab(), "Вставить текст")
        self.tabs.addTab(self._build_file_tab(),  "Из файла")
        self.tabs.currentChanged.connect(self._on_tab_changed)
        root.addWidget(self.tabs, stretch=1)

        # Shared preview table
        preview_label = QLabel("Предпросмотр:")
        preview_label.setFont(QFont("", 10, QFont.Weight.Bold))
        root.addWidget(preview_label)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(list(_ALL_FIELDS))
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setFixedHeight(160)
        root.addWidget(self.table)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #a8acc8; font-size: 12px;")
        root.addWidget(self.status_label)

        # Bottom buttons
        btn_row = QHBoxLayout()
        self.import_btn = QPushButton("Импортировать")
        self.import_btn.setMinimumHeight(36)
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self._do_import)
        btn_row.addWidget(self.import_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setMinimumHeight(36)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        root.addLayout(btn_row)

    # ── Tab 1: paste text ─────────────────────────────────────────────
    def _build_paste_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 8)
        layout.setSpacing(10)

        # Delimiter controls row
        delimiters_row = QHBoxLayout()
        delimiters_row.setSpacing(32)

        delimiters_row.addLayout(self._build_delimiter_group(
            "Между термином и переводом",
            [("Tab", "\t"), ("Запятая", ","), ("Дефис", " - ")],
            attr_prefix="field"
        ))

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #44475a;")
        delimiters_row.addWidget(sep)

        delimiters_row.addLayout(self._build_delimiter_group(
            "Между строками",
            [("Новая строка", "\n"), ("Точка с запятой", ";")],
            attr_prefix="row"
        ))

        delimiters_row.addStretch()
        layout.addLayout(delimiters_row)

        # Text area
        self.paste_area = QTextEdit()
        self.paste_area.setPlaceholderText(
            "Вставьте текст сюда...\n\n"
            "Пример (Tab между термином и переводом, Enter между строками):\n"
            "Plaintiff\tИстец\n"
            "Defendant\tОтветчик\n"
            "Jurisdiction\tЮрисдикция"
        )
        self.paste_area.setFont(QFont("Courier New", 11))
        self.paste_area.textChanged.connect(self._on_paste_changed)
        layout.addWidget(self.paste_area, stretch=1)

        return tab

    def _build_delimiter_group(self, title: str, options: list,
                                attr_prefix: str) -> QVBoxLayout:
        """
        Строит группу радиокнопок для выбора разделителя.
        Сохраняет QButtonGroup и поле custom в self.<attr_prefix>_group / _custom.
        """
        col = QVBoxLayout()
        col.setSpacing(6)

        lbl = QLabel(title)
        lbl.setFont(QFont("", 10, QFont.Weight.Bold))
        col.addWidget(lbl)

        group = QButtonGroup(self)
        setattr(self, f"_{attr_prefix}_group", group)
        setattr(self, f"_{attr_prefix}_values", {})

        for i, (label, value) in enumerate(options):
            rb = QRadioButton(label)
            if i == 0:
                rb.setChecked(True)
            group.addButton(rb, i)
            getattr(self, f"_{attr_prefix}_values")[i] = value
            col.addWidget(rb)

        # Custom option
        custom_rb = QRadioButton("Другой:")
        custom_id = len(options)
        group.addButton(custom_rb, custom_id)
        getattr(self, f"_{attr_prefix}_values")[custom_id] = ""

        custom_row = QHBoxLayout()
        custom_row.setSpacing(6)
        custom_row.addWidget(custom_rb)

        custom_field = QLineEdit()
        custom_field.setFixedWidth(70)
        custom_field.setPlaceholderText("символ")
        custom_field.setObjectName("customDelim")
        custom_field.textChanged.connect(
            lambda text, pfx=attr_prefix, cid=custom_id:
                getattr(self, f"_{pfx}_values").__setitem__(cid, text)
        )
        custom_field.textChanged.connect(self._on_paste_changed)
        setattr(self, f"_{attr_prefix}_custom", custom_field)
        custom_row.addWidget(custom_field)
        col.addLayout(custom_row)

        group.idToggled.connect(lambda _id, checked, pfx=attr_prefix:
                                self._on_paste_changed() if checked else None)
        return col

    # ── Tab 2: file ───────────────────────────────────────────────────
    def _build_file_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 8)
        layout.setSpacing(10)

        info = QLabel(
            "Поддерживаемые форматы:\n"
            "  • CSV  — строка заголовка: term_eng, term_rus, definition, category, example\n"
            "  • JSON — массив объектов с теми же полями\n"
            "Обязательные поля: term_eng, term_rus.  Дубли (по term_eng) игнорируются."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        pick_row = QHBoxLayout()
        self.file_label = QLabel("Файл не выбран")
        self.file_label.setStyleSheet("color: #a8acc8;")
        pick_row.addWidget(self.file_label, stretch=1)
        pick_btn = QPushButton("Выбрать файл…")
        pick_btn.clicked.connect(self._pick_file)
        pick_row.addWidget(pick_btn)
        layout.addLayout(pick_row)

        layout.addStretch()
        return tab

    # ══════════════════════════════════════════════════════════════════
    # Paste-tab logic
    # ══════════════════════════════════════════════════════════════════
    def _field_sep(self) -> str:
        bid = self._field_group.checkedId()
        return self._field_values.get(bid, "\t")

    def _row_sep(self) -> str:
        bid = self._row_group.checkedId()
        return self._row_values.get(bid, "\n")

    def _on_paste_changed(self):
        if self.tabs.currentIndex() != 0:
            return
        text = self.paste_area.toPlainText().strip()
        if not text:
            self._rows = []
            self._refresh_preview()
            return
        try:
            self._rows = self._parse_paste(text)
            self._refresh_preview()
        except Exception as exc:
            self.status_label.setText(f"Ошибка: {exc}")
            self._rows = []
            self.import_btn.setEnabled(False)

    def _parse_paste(self, text: str) -> list[dict]:
        row_sep = self._row_sep()
        field_sep = self._field_sep()

        if not field_sep:
            raise ValueError("Укажите разделитель между термином и переводом")

        # Split by row separator (handle literal \n\n etc. if custom)
        raw_sep = row_sep.replace("\\n", "\n").replace("\\t", "\t")
        lines = [l for l in text.split(raw_sep) if l.strip()]

        rows = []
        for line in lines:
            parts = line.split(field_sep)
            if len(parts) < 2:
                continue
            term_eng = parts[0].strip()
            term_rus = parts[1].strip()
            definition = parts[2].strip() if len(parts) > 2 else ""
            category   = parts[3].strip() if len(parts) > 3 else "Импортированные"
            example    = parts[4].strip() if len(parts) > 4 else ""
            if not category:
                category = "Импортированные"
            if term_eng and term_rus:
                rows.append({
                    "term_eng": term_eng, "term_rus": term_rus,
                    "definition": definition, "category": category,
                    "example": example,
                })
        return rows

    # ══════════════════════════════════════════════════════════════════
    # File-tab logic
    # ══════════════════════════════════════════════════════════════════
    def _on_tab_changed(self, index: int):
        # Clear preview when switching tabs
        self._rows = []
        self._refresh_preview()
        if index == 0:
            self._on_paste_changed()

    def _pick_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл", "", "CSV и JSON (*.csv *.json)"
        )
        if not path:
            return
        self.file_label.setText(path)
        try:
            if path.lower().endswith(".csv"):
                self._rows = self._parse_csv(path)
            else:
                self._rows = self._parse_json(path)
            self._refresh_preview()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка чтения", str(exc))
            self._rows = []
            self.import_btn.setEnabled(False)
            self.status_label.setText("")

    def _parse_csv(self, path: str) -> list[dict]:
        rows = []
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(self._normalise_dict(dict(r)))
        return rows

    def _parse_json(self, path: str) -> list[dict]:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("JSON должен быть массивом объектов")
        return [self._normalise_dict(r) for r in data]

    def _normalise_dict(self, d: dict) -> dict:
        out = {field: str(d.get(field) or "").strip() for field in _ALL_FIELDS}
        missing = _REQUIRED - {k for k, v in out.items() if v}
        if missing:
            raise ValueError(
                f"Отсутствуют обязательные поля: {', '.join(sorted(missing))}"
            )
        if not out["category"]:
            out["category"] = "Импортированные"
        return out

    # ══════════════════════════════════════════════════════════════════
    # Shared preview & import
    # ══════════════════════════════════════════════════════════════════
    def _refresh_preview(self):
        self.table.setRowCount(0)
        preview = self._rows[:50]
        for row in preview:
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, field in enumerate(_ALL_FIELDS):
                self.table.setItem(r, c, QTableWidgetItem(row.get(field, "")))
        total = len(self._rows)
        if total == 0:
            self.status_label.setText("")
            self.import_btn.setEnabled(False)
            return
        shown = len(preview)
        suffix = f"  (показаны первые {shown})" if total > shown else ""
        self.status_label.setText(f"Найдено терминов: {total}{suffix}")
        self.import_btn.setEnabled(True)

    def _do_import(self):
        if not self._rows:
            return
        try:
            inserted = self.db.import_terms(self._rows)
            skipped = len(self._rows) - inserted
            QMessageBox.information(
                self, "Готово",
                f"Добавлено терминов: {inserted}\n"
                f"Пропущено дубликатов: {max(0, skipped)}"
            )
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка импорта", str(exc))
