"""
Boss Mode — режим на скорость.
Показывает английский термин, нужно нажать правильный русский перевод из 4 вариантов.
Таймер сокращается с каждым верным ответом. Ошибка или истёкший таймер — конец игры.
Рекорд сохраняется в директории активного app profile.
"""
import json
import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ..models.term import Term
from ..utils.sound_manager import get_sound_manager
from ..utils.settings_manager import get_settings
from ..app_paths import get_user_file

_HS_FILE = get_user_file("highscore.json")

START_MS = 5000      # начальное время на ответ, мс
MIN_MS   = 1200      # минимальное время
STEP_MS  = 150       # уменьшение времени за каждый верный ответ
NUM_OPTIONS = 4


class BossWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self._sounds = get_sound_manager()
        self._score = 0
        self._time_ms = START_MS
        self._running = False
        self._timer = QTimer(self)
        self._timer.setInterval(50)
        self._timer.timeout.connect(self._tick)
        self._elapsed_ms = 0
        self._highscore = self._load_hs()
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(14)

        # Header row
        hdr = QHBoxLayout()
        title = QLabel("Boss Mode")
        tf = QFont()
        tf.setPointSize(15)
        tf.setBold(True)
        title.setFont(tf)
        hdr.addWidget(title)
        hdr.addStretch()

        self.score_lbl = QLabel("Счёт: 0")
        sf = QFont()
        sf.setPointSize(13)
        self.score_lbl.setFont(sf)
        hdr.addWidget(self.score_lbl)

        self.hs_lbl = QLabel(f"Рекорд: {self._highscore}")
        self.hs_lbl.setStyleSheet("color: #a8acc8; font-size: 12px;")
        hdr.addWidget(self.hs_lbl)
        root.addLayout(hdr)

        subtitle = QLabel("Серия быстрых решений на время: каждый верный ответ повышает темп следующего раунда.")
        subtitle.setObjectName("mutedLabel")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        progress_note = QLabel("Режим аркадный: результаты не меняют spaced repetition и не засчитываются в дневной прогресс.")
        progress_note.setObjectName("mutedLabel")
        progress_note.setWordWrap(True)
        root.addWidget(progress_note)

        # Timer bar
        self.timer_bar = QProgressBar()
        self.timer_bar.setRange(0, 1000)
        self.timer_bar.setValue(1000)
        self.timer_bar.setTextVisible(False)
        self.timer_bar.setFixedHeight(10)
        self.timer_bar.setStyleSheet(
            "QProgressBar { background: #32354d; border-radius: 5px; }"
            "QProgressBar::chunk { background: #7eb8f7; border-radius: 5px; }"
        )
        root.addWidget(self.timer_bar)

        # Term card
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)

        self.term_lbl = QLabel("Нажмите «Старт» для начала")
        lf = QFont()
        lf.setPointSize(22)
        lf.setBold(True)
        self.term_lbl.setFont(lf)
        self.term_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.term_lbl.setWordWrap(True)
        card_layout.addWidget(self.term_lbl)

        self.speed_lbl = QLabel("")
        self.speed_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_lbl.setStyleSheet("color: #a8acc8; font-size: 11px;")
        card_layout.addWidget(self.speed_lbl)

        self.helper_lbl = QLabel("Нажмите старт, чтобы начать серию. Ошибка или тайм-аут сразу завершают игру.")
        self.helper_lbl.setObjectName("mutedLabel")
        self.helper_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.helper_lbl.setWordWrap(True)
        card_layout.addWidget(self.helper_lbl)

        root.addWidget(card, stretch=1)

        # Option buttons (2×2 grid)
        self.opt_btns: list[QPushButton] = []
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        for i in range(NUM_OPTIONS):
            btn = QPushButton("")
            btn.setMinimumHeight(48)
            btn.setObjectName("matchBtn")
            btn.clicked.connect(lambda _, idx=i: self._answer(idx))
            btn.setEnabled(False)
            self.opt_btns.append(btn)
            (row1 if i < 2 else row2).addWidget(btn)
        root.addLayout(row1)
        root.addLayout(row2)

        # Result label
        self.result_lbl = QLabel("")
        self.result_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rf = QFont()
        rf.setPointSize(14)
        rf.setBold(True)
        self.result_lbl.setFont(rf)
        self.result_lbl.setObjectName("resultBanner")
        self.result_lbl.hide()
        root.addWidget(self.result_lbl)

        # Start / Restart button
        self.start_btn = QPushButton("Старт")
        self.start_btn.setMinimumHeight(42)
        self.start_btn.setObjectName("primaryBtn")
        self.start_btn.clicked.connect(self._start)
        root.addWidget(self.start_btn)

    # ── Game logic ────────────────────────────────────────────────────
    def _start(self):
        self._score = 0
        self._time_ms = get_settings().get("boss_start_ms", START_MS)
        self._running = True
        self.result_lbl.hide()
        self.result_lbl.setText("")
        self.start_btn.setText("Рестарт")
        self.score_lbl.setText("Счёт: 0")
        self._next_question()

    def _next_question(self):
        rows = self.db.get_terms_by_category(None, limit=NUM_OPTIONS * 3)
        if len(rows) < NUM_OPTIONS:
            self._game_over("Недостаточно терминов для запуска режима.")
            return
        chosen = random.sample(rows, NUM_OPTIONS)
        self._correct_idx = random.randrange(NUM_OPTIONS)
        self._correct_term = Term.from_row(chosen[self._correct_idx])

        self.term_lbl.setText(self._correct_term.term_eng)
        self.term_lbl.setStyleSheet("")
        secs = self._time_ms / 1000
        self.speed_lbl.setText(f"Времени на ответ: {secs:.1f} с")
        self.helper_lbl.setText("Выберите правильный перевод до истечения шкалы времени.")

        for i, btn in enumerate(self.opt_btns):
            btn.setText(Term.from_row(chosen[i]).term_rus)
            btn.setEnabled(True)
            btn.setStyleSheet("")

        self._elapsed_ms = 0
        self.timer_bar.setValue(1000)
        self._timer.start()

    def _tick(self):
        self._elapsed_ms += 50
        remaining = max(0, 1000 - int(self._elapsed_ms / self._time_ms * 1000))
        self.timer_bar.setValue(remaining)

        # Color: green → yellow → red
        if remaining > 500:
            color = "#7eb8f7"
        elif remaining > 250:
            color = "#ffa726"
        else:
            color = "#f38ba8"
        self.timer_bar.setStyleSheet(
            f"QProgressBar {{ background: #32354d; border-radius: 5px; }}"
            f"QProgressBar::chunk {{ background: {color}; border-radius: 5px; }}"
        )

        if self._elapsed_ms >= self._time_ms:
            self._timer.stop()
            self._game_over("Время вышло!")

    def _answer(self, idx: int):
        self._timer.stop()
        for btn in self.opt_btns:
            btn.setEnabled(False)

        if idx == self._correct_idx:
            self._score += 1
            self.score_lbl.setText(f"Счёт: {self._score}")
            self.opt_btns[idx].setStyleSheet(
                "color: #b8f0c0; border: 2px solid #48b860;"
            )
            self._sounds.play("correct")
            self._time_ms = max(MIN_MS, self._time_ms - STEP_MS)
            QTimer.singleShot(300, self._next_question)
        else:
            self.opt_btns[idx].setStyleSheet(
                "color: #f8b0c0; border: 2px solid #c04050;"
            )
            self.opt_btns[self._correct_idx].setStyleSheet(
                "color: #b8f0c0; border: 2px solid #48b860;"
            )
            self._sounds.play("wrong")
            QTimer.singleShot(800, lambda: self._game_over("Неверный ответ!"))

    def _game_over(self, reason: str):
        self._running = False
        self._timer.stop()
        for btn in self.opt_btns:
            btn.setEnabled(False)
        self.timer_bar.setValue(0)
        self.term_lbl.setStyleSheet("color: #f38ba8;")
        self.helper_lbl.setText("Раунд завершён. Можно сразу перезапустить и попытаться улучшить результат.")

        new_hs = self._score > self._highscore
        if new_hs:
            self._highscore = self._score
            self._save_hs(self._highscore)
            self.hs_lbl.setText(f"Рекорд: {self._highscore}")

        msg = f"{reason}\nИтоговый счёт: {self._score}"
        if new_hs and self._score > 0:
            msg += "\nНовый личный рекорд."
        self.result_lbl.setText(msg)
        self.result_lbl.setStyleSheet(
            "color: #ffd700;" if new_hs else "color: #f8b0c0;"
        )
        self.result_lbl.show()

    # ── Highscore persistence ─────────────────────────────────────────
    def _load_hs(self) -> int:
        try:
            return json.loads(_HS_FILE.read_text(encoding="utf-8")).get("hs", 0)
        except Exception:
            return 0

    def _save_hs(self, value: int) -> None:
        _HS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _HS_FILE.write_text(json.dumps({"hs": value}), encoding="utf-8")
