from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QCheckBox, QDialogButtonBox, QFormLayout, QGroupBox, QMessageBox
)
from PyQt6.QtWidgets import QApplication

try:
    from ..utils.settings_manager import get_settings, save_settings
except ImportError:
    from utils.settings_manager import get_settings, save_settings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setMinimumWidth(400)
        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # ── Интерфейс ─────────────────────────────────────────────────
        iface = QGroupBox("Интерфейс")
        iface_form = QFormLayout(iface)
        self.font_spin = QSpinBox()
        self.font_spin.setRange(10, 20)
        self.font_spin.setSuffix(" px")
        iface_form.addRow("Размер шрифта:", self.font_spin)
        layout.addWidget(iface)

        # ── Обучение ──────────────────────────────────────────────────
        learn = QGroupBox("Обучение")
        learn_form = QFormLayout(learn)

        self.goal_spin = QSpinBox()
        self.goal_spin.setRange(5, 200)
        self.goal_spin.setSuffix(" карточек")
        learn_form.addRow("Цель на день:", self.goal_spin)

        self.quiz_spin = QSpinBox()
        self.quiz_spin.setRange(3, 30)
        self.quiz_spin.setSuffix(" карточек")
        learn_form.addRow("Квиз каждые:", self.quiz_spin)
        layout.addWidget(learn)

        # ── Boss Mode ─────────────────────────────────────────────────
        boss = QGroupBox("Boss Mode")
        boss_form = QFormLayout(boss)
        self.boss_spin = QSpinBox()
        self.boss_spin.setRange(2000, 10000)
        self.boss_spin.setSingleStep(500)
        self.boss_spin.setSuffix(" мс")
        boss_form.addRow("Начальное время:", self.boss_spin)
        layout.addWidget(boss)

        # ── Напоминание ───────────────────────────────────────────────
        remind = QGroupBox("Напоминание")
        remind_layout = QVBoxLayout(remind)
        self.reminder_check = QCheckBox("Показывать ежедневное напоминание")
        remind_layout.addWidget(self.reminder_check)

        time_row = QHBoxLayout()
        time_row.addWidget(QLabel("Время:"))
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setSuffix(" ч")
        time_row.addWidget(self.hour_spin)
        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setSuffix(" мин")
        time_row.addWidget(self.minute_spin)
        time_row.addStretch()
        remind_layout.addLayout(time_row)
        layout.addWidget(remind)

        # ── Кнопки ────────────────────────────────────────────────────
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._save_and_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _load(self):
        s = get_settings()
        self.font_spin.setValue(s["font_size"])
        self.goal_spin.setValue(s["daily_goal"])
        self.quiz_spin.setValue(s["quiz_every"])
        self.boss_spin.setValue(s["boss_start_ms"])
        self.reminder_check.setChecked(s["reminder_enabled"])
        self.hour_spin.setValue(s["reminder_hour"])
        self.minute_spin.setValue(s["reminder_minute"])

    def _save_and_accept(self):
        s = get_settings()
        old_font = s["font_size"]
        s["font_size"] = self.font_spin.value()
        s["daily_goal"] = self.goal_spin.value()
        s["quiz_every"] = self.quiz_spin.value()
        s["boss_start_ms"] = self.boss_spin.value()
        s["reminder_enabled"] = self.reminder_check.isChecked()
        s["reminder_hour"] = self.hour_spin.value()
        s["reminder_minute"] = self.minute_spin.value()
        save_settings(s)

        # Apply font size immediately via stylesheet rebuild
        if s["font_size"] != old_font:
            from .._stylesheet import build_dark_stylesheet
            QApplication.instance().setStyleSheet(
                build_dark_stylesheet(s["font_size"])
            )

        self.accept()
