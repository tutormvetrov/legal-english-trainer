"""
«Термин атакует» — всплывающий поверх всех окон диалог.
Появляется по таймеру, требует ввести правильный перевод.
Нельзя закрыть без ответа.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve
from PyQt6.QtGui import QFont

try:
    from ..models.term import Term
    from ..utils.helpers import answers_match
    from ..utils.sound_manager import get_sound_manager
except ImportError:
    from models.term import Term
    from utils.helpers import answers_match
    from utils.sound_manager import get_sound_manager


class AttackPopup(QDialog):
    def __init__(self, term: Term, scheduler, direction_eng_to_rus: bool = True, parent=None):
        super().__init__(parent)
        self.term = term
        self.scheduler = scheduler
        self.direction_eng_to_rus = direction_eng_to_rus
        self._sounds = get_sound_manager()
        self._shake_anim = None
        self._answered = False

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog
        )
        self.setMinimumWidth(440)
        self.setMinimumHeight(280)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        # Title row
        title_row = QHBoxLayout()
        icon_lbl = QLabel("⚔")
        icon_lbl.setStyleSheet("font-size: 20px;")
        title_row.addWidget(icon_lbl)
        title_lbl = QLabel("  Термин атакует!")
        tf = QFont()
        tf.setPointSize(13)
        tf.setBold(True)
        title_lbl.setFont(tf)
        title_lbl.setStyleSheet("color: #f07178;")
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        root.addLayout(title_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #3a3d5c; max-height: 1px; border: none;")
        root.addWidget(sep)

        # Term card
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(8)

        direction_lbl = QLabel("EN → RU" if self.direction_eng_to_rus else "RU → EN")
        direction_lbl.setStyleSheet("color: #8890b8; font-size: 11px; letter-spacing: 1px;")
        direction_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(direction_lbl)

        self.term_label = QLabel()
        self.term_label.setObjectName("termLabel")
        self.term_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.term_label.setWordWrap(True)
        lf = QFont("Georgia", 20)
        lf.setBold(True)
        self.term_label.setFont(lf)
        prompt_text = self.term.term_eng if self.direction_eng_to_rus else self.term.term_rus
        self.term_label.setText(prompt_text)
        card_layout.addWidget(self.term_label)

        root.addWidget(card)

        # Input
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите перевод…")
        self.input_field.setMinimumHeight(42)
        self.input_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_field.returnPressed.connect(self._check_answer)
        root.addWidget(self.input_field)

        # Feedback
        self.feedback_label = QLabel("")
        self.feedback_label.setObjectName("feedbackLabel")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setWordWrap(True)
        self.feedback_label.hide()
        root.addWidget(self.feedback_label)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.check_btn = QPushButton("Проверить")
        self.check_btn.setMinimumHeight(38)
        self.check_btn.clicked.connect(self._check_answer)
        btn_row.addWidget(self.check_btn)

        self.skip_btn = QPushButton("Пропустить")
        self.skip_btn.setMinimumHeight(38)
        self.skip_btn.setStyleSheet("color: #8890b8;")
        self.skip_btn.clicked.connect(self._skip)
        btn_row.addWidget(self.skip_btn)

        root.addLayout(btn_row)

        self.input_field.setFocus()

    def _correct_answer(self) -> str:
        return self.term.term_rus if self.direction_eng_to_rus else self.term.term_eng

    def _check_answer(self):
        if self._answered:
            return
        user = self.input_field.text()
        if not user.strip():
            return

        if answers_match(user, self._correct_answer()):
            self._answered = True
            self.scheduler.review(self.term.id, 5)
            self._sounds.play("correct")
            self.feedback_label.setText("✓ Правильно!")
            self.feedback_label.setStyleSheet("color: #c3e88d; font-weight: bold; font-size: 14px;")
            self.feedback_label.show()
            self.check_btn.setEnabled(False)
            self.skip_btn.setEnabled(False)
            self.input_field.setEnabled(False)
            QTimer.singleShot(900, self.accept)
        else:
            self._sounds.play("wrong")
            self._shake()
            self.feedback_label.setText("✗ Неверно. Попробуйте ещё.")
            self.feedback_label.setStyleSheet("color: #f07178;")
            self.feedback_label.show()
            self.input_field.selectAll()
            self.input_field.setFocus()

    def _skip(self):
        self._answered = True
        self.scheduler.review(self.term.id, 0)
        self.accept()

    def _shake(self):
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

    def closeEvent(self, event):
        if not self._answered:
            event.ignore()
        else:
            event.accept()
