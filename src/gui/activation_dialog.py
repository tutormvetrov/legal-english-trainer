from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..utils.license_manager import ALPHABET, validate_key, save_activation


class ActivationDialog(QDialog):
    """
    Двухшаговый диалог активации:
      Шаг 1 — ввод серийного ключа
      Шаг 2 — ввод имени пользователя
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._key = ""
        self.username = ""
        self.setWindowTitle("Активация")
        self.setFixedSize(460, 300)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_key_page())
        self._stack.addWidget(self._build_name_page())
        root.addWidget(self._stack)

    # ── Шаг 1: ключ ──────────────────────────────────────────────────
    def _build_key_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(36, 32, 36, 28)
        layout.setSpacing(18)

        title = QLabel("Legal English Trainer")
        f = QFont(); f.setPointSize(16); f.setBold(True)
        title.setFont(f)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Введите серийный ключ для активации")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #a8acc8;")
        layout.addWidget(subtitle)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("XXXXX-XXXXX-XXXXX-XXXXX")
        self.key_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        kf = QFont("Courier New", 15); kf.setBold(True)
        self.key_input.setFont(kf)
        self.key_input.setMinimumHeight(46)
        self.key_input.setMaxLength(23)
        self.key_input.textChanged.connect(self._on_key_changed)
        layout.addWidget(self.key_input)

        self.key_error = QLabel("")
        self.key_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.key_error.setStyleSheet("color: #f38ba8; font-size: 12px;")
        layout.addWidget(self.key_error)

        btn_row = QHBoxLayout(); btn_row.setSpacing(12)
        self.next_btn = QPushButton("Далее →")
        self.next_btn.setMinimumHeight(38)
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self._validate_key)
        btn_row.addWidget(self.next_btn)

        cancel_btn = QPushButton("Выйти")
        cancel_btn.setMinimumHeight(38)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        return page

    def _on_key_changed(self, text: str):
        clean = "".join(c for c in text.upper() if c in ALPHABET)[:20]
        formatted = "-".join(clean[i:i+5] for i in range(0, len(clean), 5))
        self.key_input.blockSignals(True)
        self.key_input.setText(formatted)
        self.key_input.setCursorPosition(len(formatted))
        self.key_input.blockSignals(False)
        self.key_error.setText("")
        self.next_btn.setEnabled(len(clean) == 20)

    def _validate_key(self):
        key = self.key_input.text()
        if validate_key(key):
            self._key = key
            self._stack.setCurrentIndex(1)
            self.name_input.setFocus()
        else:
            self.key_error.setText("Неверный ключ. Проверьте и попробуйте снова.")
            self.key_input.setStyleSheet("border: 1px solid #f38ba8;")

    # ── Шаг 2: имя ───────────────────────────────────────────────────
    def _build_name_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(36, 32, 36, 28)
        layout.setSpacing(18)

        title = QLabel("Как вас зовут?")
        f = QFont(); f.setPointSize(16); f.setBold(True)
        title.setFont(f)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Только Ваше настоящее имя!")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #a8acc8;")
        layout.addWidget(subtitle)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите ваше имя...")
        self.name_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nf = QFont(); nf.setPointSize(14)
        self.name_input.setFont(nf)
        self.name_input.setMinimumHeight(46)
        self.name_input.returnPressed.connect(self._finish)
        layout.addWidget(self.name_input)

        layout.addStretch()

        btn_row = QHBoxLayout(); btn_row.setSpacing(12)
        activate_btn = QPushButton("Начать обучение ✓")
        activate_btn.setMinimumHeight(38)
        activate_btn.clicked.connect(self._finish)
        btn_row.addWidget(activate_btn)

        skip_btn = QPushButton("Пропустить")
        skip_btn.setMinimumHeight(38)
        skip_btn.setStyleSheet("color: #a8acc8;")
        skip_btn.clicked.connect(self._finish)
        btn_row.addWidget(skip_btn)
        layout.addLayout(btn_row)

        return page

    def _finish(self):
        self.username = self.name_input.text().strip()
        save_activation(self._key, self.username)
        self.accept()
