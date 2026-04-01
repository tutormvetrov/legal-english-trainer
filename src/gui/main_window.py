from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QLabel, QProgressBar,
    QPushButton, QHBoxLayout, QWidget, QFrame, QVBoxLayout
)
from PyQt6.QtCore import Qt

try:
    from .._stylesheet import get_theme_palette
    from ..utils.settings_manager import get_settings
except ImportError:
    from _stylesheet import get_theme_palette
    from utils.settings_manager import get_settings

from .flashcards_widget import FlashcardsWidget
from .match_widget import MatchWidget
from .typing_widget import TypingWidget
from .stats_widget import StatsWidget
from .favorites_widget import FavoritesWidget
from .boss_widget import BossWidget
from .context_widget import ContextWidget
from .detective_widget import DetectiveWidget


class MainWindow(QMainWindow):
    def __init__(self, db_manager, scheduler, streak: int = 0,
                 username: str = "", db_path: str = ""):
        super().__init__()
        self.db = db_manager
        self.scheduler = scheduler
        self.streak = streak
        self.username = username
        self._db_path = db_path
        self._update_title()
        self.setMinimumSize(960, 680)
        self._build_ui()
        self._refresh_goal()

    def _update_title(self):
        name_part   = f" — {self.username}" if self.username else ""
        streak_part = f"  🔥 {self.streak} дней подряд" if self.streak >= 2 else ""
        self.setWindowTitle(f"Legal English Trainer{name_part}{streak_part}")

    def _build_ui(self):
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.tabBar().setDrawBase(False)
        self._tabs = tabs

        self.flashcards = FlashcardsWidget(self.db, self.scheduler)
        self.match      = MatchWidget(self.db, self.scheduler)
        self.typing     = TypingWidget(self.db, self.scheduler)
        self.detective  = DetectiveWidget(self.db, self.scheduler)
        self.favorites  = FavoritesWidget(self.db)
        self.boss       = BossWidget(self.db)
        self.context    = ContextWidget(self.db, self.scheduler)
        self.stats      = StatsWidget(self.db, db_path=self._db_path)

        tabs.addTab(self.flashcards, "🃏 Карточки")
        tabs.addTab(self.match,      "🔗 Сопоставление")
        tabs.addTab(self.typing,     "✍️ Диктант")
        tabs.addTab(self.detective,  "🔍 Детектив")
        tabs.addTab(self.context,    "📖 Контекст")
        tabs.addTab(self.favorites,  "⭐ Избранное")
        tabs.addTab(self.boss,       "👊 Boss Mode")
        tabs.addTab(self.stats,      "📊 Статистика")

        tabs.currentChanged.connect(self._on_tab_changed)

        shell = QWidget()
        shell.setObjectName("appShell")
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(18, 18, 18, 18)
        shell_layout.setSpacing(14)

        hero = QFrame()
        hero.setObjectName("heroCard")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(22, 20, 22, 18)
        hero_layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        eyebrow = QLabel("LEGAL ENGLISH TRAINER")
        eyebrow.setObjectName("heroEyebrow")
        top_row.addWidget(eyebrow)
        top_row.addStretch()

        self._hero_chip = QLabel("")
        self._hero_chip.setObjectName("heroChip")
        self._hero_chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(self._hero_chip)

        hero_layout.addLayout(top_row)

        self._hero_title = QLabel()
        self._hero_title.setObjectName("heroTitle")
        hero_layout.addWidget(self._hero_title)

        self._hero_subtitle = QLabel(
            "Повторяйте термины в удобном режиме, отслеживайте прогресс и держите темп каждый день."
        )
        self._hero_subtitle.setObjectName("heroSubtitle")
        self._hero_subtitle.setWordWrap(True)
        hero_layout.addWidget(self._hero_subtitle)

        self._hero_meta = QLabel("")
        self._hero_meta.setObjectName("heroMeta")
        hero_layout.addWidget(self._hero_meta)

        shell_layout.addWidget(hero)
        shell_layout.addWidget(tabs, stretch=1)

        self.setCentralWidget(shell)
        self._refresh_header()

        # ── Status bar ────────────────────────────────────────────────
        status = QStatusBar()
        self.setStatusBar(status)

        # Daily goal progress
        self._goal_label = QLabel("Цель: 0 / 20")
        self._goal_label.setObjectName("mutedLabel")
        self._goal_label.setContentsMargins(8, 0, 8, 0)
        self._goal_bar = QProgressBar()
        self._goal_bar.setFixedWidth(120)
        self._goal_bar.setFixedHeight(14)
        self._goal_bar.setTextVisible(False)
        self._goal_bar.setRange(0, 100)
        status.addWidget(self._goal_label)
        status.addWidget(self._goal_bar)

        # Settings button (right side of status bar)
        settings_btn = QPushButton("Настройки")
        settings_btn.setFixedHeight(24)
        settings_btn.setObjectName("settingsLink")
        settings_btn.clicked.connect(self._open_settings)
        status.addPermanentWidget(settings_btn)

    def _on_tab_changed(self, index: int):
        # Uses identity checks — safe even if tab indices shift
        current = self._tabs.widget(index)
        if current is self.favorites:
            self.favorites.refresh()
        elif current is self.stats:
            self.stats.refresh()
        self._refresh_goal()

    def _refresh_header(self):
        title = f"Здравствуйте, {self.username}" if self.username else "Ваш ежедневный юридический английский"
        if self.streak >= 2:
            meta = f"Серия: {self.streak} дней подряд"
        else:
            meta = "Серия начнётся после второго дня подряд"
        self._hero_title.setText(title)
        self._hero_meta.setText(meta)

    def _refresh_goal(self):
        goal = get_settings().get("daily_goal", 20)
        theme = get_settings().get("theme", "dark")
        palette = get_theme_palette(theme)
        today_reviews = self.db.get_stats().get("today_reviews", 0)
        self._goal_label.setText(f"Цель на день: {today_reviews} / {goal}")
        goal_text = (
            f"Сегодня выполнено {today_reviews} из {goal} повторений."
            if goal else f"Сегодня выполнено {today_reviews} повторений."
        )
        self._hero_meta.setText(
            f"{self._hero_meta.text().split(' • ')[0]} • {goal_text}"
        )
        self._hero_chip.setText(f"Сегодня: {today_reviews}/{goal}")
        pct = min(100, int(today_reviews / goal * 100)) if goal else 0
        self._goal_bar.setValue(pct)
        color = palette["goal_complete"] if pct >= 100 else palette["goal_incomplete"]
        self._goal_bar.setStyleSheet(
            f"QProgressBar {{ background: {palette['goal_track_bg']};"
            f" border: 1px solid {palette['goal_track_border']}; border-radius: 3px; }}"
            f"QProgressBar::chunk {{ background: {color}; border-radius: 2px; }}"
        )

    def _open_settings(self):
        try:
            from .settings_dialog import SettingsDialog
        except ImportError:
            from settings_dialog import SettingsDialog
        dlg = SettingsDialog(self)
        dlg.exec()
        if getattr(self.flashcards, "current_term", None) is not None:
            self.flashcards._render_term()
        self._refresh_goal()
