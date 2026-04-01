import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ..models.term import Term
from ..utils.sound_manager import get_sound_manager
from ..utils import tts_manager
from ..utils.settings_manager import get_settings
from .._stylesheet import get_theme_palette

QUIZ_EVERY = 10   # значение по умолчанию, переопределяется настройками

# ── Category accent colours ────────────────────────────────────────────────
# (text_colour, background, border/left-bar colour)
_CAT_COLORS = {
    "dark": {
        "Contract Law":      ("#ffcb6b", "#241a08", "#c89020"),
        "Criminal Law":      ("#f07178", "#240c12", "#b03040"),
        "Property Law":      ("#c3e88d", "#101e0a", "#4a9030"),
        "Corporate Law":     ("#c792ea", "#1c0e28", "#9050c0"),
        "Civil Procedure":   ("#89ddff", "#081820", "#3090b8"),
        "International Law": ("#82aaff", "#0c1428", "#4060c0"),
        "Latin Terms":       ("#e8c060", "#201808", "#b08020"),
    },
    "light": {
        "Contract Law":      ("#8b5b1d", "#f6e5c7", "#bf8c44"),
        "Criminal Law":      ("#8d4349", "#f8dede", "#c16a6f"),
        "Property Law":      ("#5c7142", "#e4edd7", "#91aa72"),
        "Corporate Law":     ("#6e5189", "#eadff4", "#a586c6"),
        "Civil Procedure":   ("#476f81", "#dfeef4", "#7ca6b6"),
        "International Law": ("#4d6789", "#e0e9f7", "#7b97bf"),
        "Latin Terms":       ("#7c5c2f", "#f4e5c6", "#c69a57"),
    },
}
_DEFAULT_CAT = {
    "dark": ("#82aaff", "#0c1428", "#4060c0"),
    "light": ("#6d593d", "#ede0cb", "#b8864c"),
}

class FlashcardsWidget(QWidget):
    def __init__(self, db_manager, scheduler):
        super().__init__()
        self.db = db_manager
        self.scheduler = scheduler
        self.current_term = None
        self.direction_eng_to_rus = True
        self.translation_shown = False
        self._sounds = get_sound_manager()
        self._rated_count = 0
        self._rated_ids: list[int] = []
        self._advance_pending = False
        self._build_ui()
        self._load_categories()
        self._next_term()

    # ── Build UI ───────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        # Controls row
        controls = QHBoxLayout()
        controls.setSpacing(10)
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(200)
        self.category_combo.currentIndexChanged.connect(self._next_term)
        cat_label = QLabel("Категория")
        cat_label.setObjectName("controlLabel")
        controls.addWidget(cat_label)
        controls.addWidget(self.category_combo)
        controls.addSpacing(18)

        self.direction_btn = QPushButton("EN → RU")
        self.direction_btn.setCheckable(True)
        self.direction_btn.setChecked(False)
        self.direction_btn.setMinimumWidth(110)
        self.direction_btn.setObjectName("subtleBtn")
        self.direction_btn.clicked.connect(self._toggle_direction)
        direction_label = QLabel("Направление")
        direction_label.setObjectName("controlLabel")
        controls.addWidget(direction_label)
        controls.addWidget(self.direction_btn)
        controls.addStretch()

        self.counter_label = QLabel("")
        self.counter_label.setObjectName("statPill")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        controls.addWidget(self.counter_label)
        root.addLayout(controls)

        # Card
        self.card_frame = QFrame()
        self.card_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.card_frame.setObjectName("card")
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(32, 24, 32, 30)
        card_layout.setSpacing(16)

        # Category tag row (balanced by a left spacer)
        top_row = QHBoxLayout()
        top_row.addSpacing(44)
        top_row.addStretch()

        self.category_tag = QLabel("")
        self.category_tag.setObjectName("categoryTag")
        self.category_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(self.category_tag)
        top_row.addStretch()

        self.star_btn = QPushButton("☆")
        self.star_btn.setFixedSize(44, 44)
        self.star_btn.setToolTip("Добавить в избранное")
        self.star_btn.setStyleSheet(self._star_button_style(False))
        self.star_btn.clicked.connect(self._toggle_star)
        top_row.addWidget(self.star_btn)
        card_layout.addLayout(top_row)

        self.term_eyebrow = QLabel("ТЕРМИН К ПОВТОРЕНИЮ")
        self.term_eyebrow.setObjectName("termEyebrow")
        self.term_eyebrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.term_eyebrow)

        self.term_label = QLabel("")
        self.term_label.setObjectName("termLabel")
        self.term_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.term_label.setWordWrap(True)
        self.term_label.setStyleSheet("background: transparent; border: none;")
        term_font = QFont("Playfair Display", 28)
        term_font.setBold(True)
        self.term_label.setFont(term_font)
        card_layout.addWidget(self.term_label)

        self.term_hint = QLabel("Откройте перевод, затем честно оцените, насколько уверенно знаете термин.")
        self.term_hint.setObjectName("mutedLabel")
        self.term_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.term_hint.setWordWrap(True)
        card_layout.addWidget(self.term_hint)

        # Translation area (hidden until revealed)
        self.translation_frame = QFrame()
        self.translation_frame.setObjectName("translationFrame")
        trans_layout = QVBoxLayout(self.translation_frame)
        trans_layout.setContentsMargins(0, 8, 0, 0)
        trans_layout.setSpacing(8)

        self.translation_label = QLabel("")
        self.translation_label.setObjectName("translationLabel")
        self.translation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.translation_label.setWordWrap(True)
        trans_font = QFont()
        trans_font.setPointSize(16)
        self.translation_label.setFont(trans_font)
        trans_layout.addWidget(self.translation_label)

        self.definition_label = QLabel("")
        self.definition_label.setObjectName("definitionLabel")
        self.definition_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.definition_label.setWordWrap(True)
        self.definition_label.setTextFormat(Qt.TextFormat.RichText)
        trans_layout.addWidget(self.definition_label)

        self.example_label = QLabel("")
        self.example_label.setObjectName("exampleLabel")
        self.example_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.example_label.setWordWrap(True)
        trans_layout.addWidget(self.example_label)

        self.translation_frame.hide()
        card_layout.addWidget(self.translation_frame)
        card_layout.addStretch()

        root.addWidget(self.card_frame, stretch=1)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.listen_btn = QPushButton("🔊")
        self.listen_btn.setFixedSize(44, 44)
        self.listen_btn.setToolTip("Прослушать произношение")
        self.listen_btn.setObjectName("subtleBtn")
        self.listen_btn.clicked.connect(self._listen)
        btn_row.addWidget(self.listen_btn)

        self.show_btn = QPushButton("Показать перевод")
        self.show_btn.setMinimumHeight(44)
        self.show_btn.setObjectName("primaryBtn")
        self.show_btn.clicked.connect(self._show_translation)
        btn_row.addWidget(self.show_btn)

        self.know_btn = QPushButton("Знаю ✓")
        self.know_btn.setObjectName("knowBtn")
        self.know_btn.setMinimumHeight(44)
        self.know_btn.hide()
        self.know_btn.clicked.connect(lambda: self._rate(5))
        btn_row.addWidget(self.know_btn)

        self.dontknow_btn = QPushButton("Не знаю ✗")
        self.dontknow_btn.setObjectName("dontKnowBtn")
        self.dontknow_btn.setMinimumHeight(44)
        self.dontknow_btn.hide()
        self.dontknow_btn.clicked.connect(lambda: self._rate(1))
        btn_row.addWidget(self.dontknow_btn)

        self.skip_btn = QPushButton("Пропустить →")
        self.skip_btn.setMinimumHeight(44)
        self.skip_btn.setObjectName("subtleBtn")
        self.skip_btn.clicked.connect(self._next_term_animated)
        btn_row.addWidget(self.skip_btn)

        root.addLayout(btn_row)

    # ── Category helpers ───────────────────────────────────────────────────

    def _cat_colors(self):
        theme = get_settings().get("theme", "dark")
        palette = _CAT_COLORS.get(theme, _CAT_COLORS["dark"])
        default = _DEFAULT_CAT.get(theme, _DEFAULT_CAT["dark"])
        if self.current_term is None:
            return default
        return palette.get(self.current_term.category, default)

    def _theme_palette(self):
        return get_theme_palette(get_settings().get("theme", "dark"))

    def _card_style(self, bg: str | None = None) -> str:
        palette = self._theme_palette()
        _, _, border_c = self._cat_colors()
        card_bg = bg or palette["card_bg"]
        return (
            f"QFrame#card {{ background-color: {card_bg};"
            f" border: 1px solid {palette['card_border']};"
            f" border-left: 3px solid {border_c};"
            f" border-radius: 16px; }}"
        )

    def _star_button_style(self, starred: bool) -> str:
        palette = self._theme_palette()
        text_color = palette["star_active"] if starred else palette["star_text"]
        return (
            "QPushButton {"
            f" font-size: 26px; color: {text_color};"
            f" border: 1px solid {palette['star_border']};"
            " border-radius: 8px;"
            f" background: {palette['star_bg']}; padding: 0; }}"
            "QPushButton:hover {"
            f" background: {palette['star_hover_bg']}; color: {palette['star_active']}; }}"
        )

    def _apply_card_style(self):
        self.card_frame.setStyleSheet(self._card_style())

    # ── Data loading ───────────────────────────────────────────────────────

    def _load_categories(self):
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem("Все категории")
        for cat in self.db.get_all_categories():
            self.category_combo.addItem(cat)
        self.category_combo.blockSignals(False)

    def _current_category(self):
        text = self.category_combo.currentText()
        return None if text == "Все категории" else text

    def _toggle_direction(self):
        self.direction_eng_to_rus = not self.direction_eng_to_rus
        self.direction_btn.setText("RU → EN" if not self.direction_eng_to_rus else "EN → RU")
        self._next_term()

    def _next_term(self):
        cat = self._current_category()
        due_ids = self.scheduler.get_due_terms(category=cat, limit=20)
        if due_ids:
            term_id = random.choice(due_ids)
            row = self.db.get_term(term_id)
        else:
            row = self.db.get_random_term(cat)

        if row is None:
            self.term_label.setText("Нет терминов")
            return

        self.current_term = Term.from_row(row)
        self._render_term()

        total_due = len(self.scheduler.get_due_terms(category=cat, limit=1000))
        self.counter_label.setText(f"К повторению: {total_due}")

    def _render_term(self):
        if self.current_term is None:
            return
        self.translation_shown = False
        self.translation_frame.hide()
        self.show_btn.show()
        self.know_btn.hide()
        self.dontknow_btn.hide()

        # Category tag with per-category accent color
        cat = self.current_term.category or ""
        text_c, bg_c, border_c = self._cat_colors()
        self.category_tag.setText(cat.upper())
        self.category_tag.setStyleSheet(
            f"background-color: {bg_c}; color: {text_c};"
            f" border: 1px solid {border_c}; border-radius: 10px;"
            f" padding: 3px 14px; font-weight: bold;"
            f" font-size: 11px; letter-spacing: 1px;"
        )

        # Card left-border accent
        self._apply_card_style()

        if self.direction_eng_to_rus:
            self.term_label.setText(self.current_term.term_eng)
            self.term_eyebrow.setText("ТЕРМИН К ПОВТОРЕНИЮ")
        else:
            self.term_label.setText(self.current_term.term_rus)
            self.term_eyebrow.setText("ПЕРЕВОД К ПОВТОРЕНИЮ")

        starred = getattr(self.current_term, "starred", 0)
        self.star_btn.setText("★" if starred else "☆")
        self.star_btn.setStyleSheet(self._star_button_style(bool(starred)))

    # ── Animations ─────────────────────────────────────────────────────────

    def _next_term_animated(self):
        if self._advance_pending:
            return
        self._advance_pending = True
        self._finish_card_advance()

    def _flash_then_next(self, flash_bg: str):
        """Flash card with colour, then safely advance to the next term."""
        if self._advance_pending:
            return
        self._advance_pending = True
        self.card_frame.setStyleSheet(self._card_style(flash_bg))
        self.show_btn.setEnabled(False)
        self.know_btn.setEnabled(False)
        self.dontknow_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)
        QTimer.singleShot(180, self._finish_card_advance)

    def _finish_card_advance(self):
        self.translation_frame.setGraphicsEffect(None)
        self._apply_card_style()
        self._next_term()
        self.show_btn.setEnabled(True)
        self.know_btn.setEnabled(True)
        self.dontknow_btn.setEnabled(True)
        self.skip_btn.setEnabled(True)
        self._advance_pending = False

    # ── Interaction ────────────────────────────────────────────────────────

    def _show_translation(self):
        if self.current_term is None:
            return
        self.translation_shown = True

        if self.direction_eng_to_rus:
            self.translation_label.setText(self.current_term.term_rus)
        else:
            self.translation_label.setText(self.current_term.term_eng)

        self.definition_label.setText(
            self._highlight_term(self.current_term.definition,
                                 self.current_term.term_eng)
        )
        self.example_label.setText(f'"{self.current_term.example}"')

        self.translation_frame.show()
        self.show_btn.hide()
        self.know_btn.show()
        self.dontknow_btn.show()

    def _rate(self, quality: int):
        if self.current_term:
            self.scheduler.review(self.current_term.id, quality)
            self._rated_ids.append(self.current_term.id)
            self._rated_count += 1
        self._sounds.play("correct" if quality >= 4 else "wrong")

        palette = self._theme_palette()
        flash_color = palette["flash_correct"] if quality >= 4 else palette["flash_wrong"]
        self._flash_then_next(flash_color)

        quiz_every = get_settings().get("quiz_every", QUIZ_EVERY)
        if self._rated_count > 0 and self._rated_count % quiz_every == 0:
            QTimer.singleShot(420, self._launch_quiz)

    def _toggle_star(self):
        if self.current_term is None:
            return
        new_state = not bool(getattr(self.current_term, "starred", 0))
        self.db.set_starred(self.current_term.id, new_state)
        row = self.db.get_term(self.current_term.id)
        if row:
            self.current_term = Term.from_row(row)
        self._render_term()

    def _highlight_term(self, text: str, term: str) -> str:
        import re, html
        if not text or not term:
            return html.escape(text) if text else ""
        escaped_text = html.escape(text)
        escaped_term = html.escape(term)
        palette = self._theme_palette()
        highlighted = (
            f'<span style="background-color:{palette["highlight_bg"]}; color:{palette["highlight_text"]};'
            f' border-radius:3px; padding:0 2px;">{escaped_term}</span>'
        )
        return re.sub(re.escape(escaped_term), highlighted,
                      escaped_text, flags=re.IGNORECASE)

    def _listen(self):
        if self.current_term is None:
            return
        text = self.current_term.term_eng if self.direction_eng_to_rus else self.current_term.term_rus
        tts_manager.speak(text)

    def _launch_quiz(self):
        from .quiz_dialog import QuizDialog
        quiz_every = get_settings().get("quiz_every", QUIZ_EVERY)
        dlg = QuizDialog(self.db, list(self._rated_ids[-quiz_every:]), self)
        dlg.exec()
