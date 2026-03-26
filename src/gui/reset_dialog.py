from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QInputDialog, QMessageBox, QApplication, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ResetDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setWindowTitle("Сброс")
        self.setFixedWidth(440)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        title = QLabel("Сброс данных")
        f = QFont(); f.setPointSize(15); f.setBold(True)
        title.setFont(f)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        # ── Сбросить прогресс ─────────────────────────────────────────
        root.addWidget(self._make_separator())

        progress_btn = QPushButton("Сбросить прогресс")
        progress_btn.setMinimumHeight(40)
        progress_btn.clicked.connect(self._reset_progress)
        root.addWidget(progress_btn)

        progress_hint = QLabel("Удаляет всю историю повторений.\nТермины, избранное и активация сохраняются.")
        progress_hint.setStyleSheet("color: #a8acc8; font-size: 12px;")
        progress_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(progress_hint)

        # ── Заводские настройки ───────────────────────────────────────
        root.addWidget(self._make_separator())

        factory_btn = QPushButton("Заводские настройки")
        factory_btn.setMinimumHeight(40)
        factory_btn.setStyleSheet(
            "QPushButton { color: #f38ba8; border: 1px solid #f38ba8; }"
            "QPushButton:hover { background: #3a1a1a; }"
        )
        factory_btn.clicked.connect(self._factory_reset)
        root.addWidget(factory_btn)

        factory_hint = QLabel("Сбрасывает прогресс и счётчик дней.\nПозволяет войти под новым именем.\nКлюч активации сохраняется.")
        factory_hint.setStyleSheet("color: #a8acc8; font-size: 12px;")
        factory_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(factory_hint)

        # ── Отмена ────────────────────────────────────────────────────
        root.addWidget(self._make_separator())

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setMinimumHeight(36)
        cancel_btn.clicked.connect(self.reject)
        root.addWidget(cancel_btn)

    def _make_separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #44475a;")
        return line

    def _reset_progress(self):
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Удалить всю историю повторений?\n\nТермины и избранное сохранятся.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.db.reset_progress()
        QMessageBox.information(self, "Готово", "Прогресс сброшен.")
        self.accept()

    def _factory_reset(self):
        new_name, ok = QInputDialog.getText(
            self, "Новое имя", "Введите новое имя пользователя:",
        )
        if not ok:
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Будут удалены:\n• весь прогресс повторений\n• счётчик дней подряд\n\n"
            f"Новое имя: «{new_name.strip() or '(не указано)'}»\n\n"
            "Приложение закроется для применения изменений. Продолжить?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        import pathlib
        try:
            from ..utils.license_manager import get_key, save_activation
            from ..utils.streak_manager import _FILE as _STREAK_FILE
        except ImportError:
            from utils.license_manager import get_key, save_activation
            from utils.streak_manager import _FILE as _STREAK_FILE

        self.db.reset_progress()

        streak_path = pathlib.Path(_STREAK_FILE)
        if streak_path.exists():
            streak_path.unlink()

        save_activation(get_key(), new_name.strip())
        # easter_shown не пишем → get_easter_shown() вернёт False → пасхалка сработает при след. запуске

        QApplication.quit()
