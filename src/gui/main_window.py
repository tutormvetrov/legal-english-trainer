from PyQt6.QtWidgets import QMainWindow, QTabWidget, QStatusBar, QLabel, QProgressBar, QPushButton, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt

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

        self.flashcards = FlashcardsWidget(self.db, self.scheduler)
        self.match      = MatchWidget(self.db, self.scheduler)
        self.typing     = TypingWidget(self.db, self.scheduler)
        self.detective  = DetectiveWidget(self.db, self.scheduler)
        self.favorites  = FavoritesWidget(self.db)
        self.boss       = BossWidget(self.db)
        self.context    = ContextWidget(self.db)
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

        self.setCentralWidget(tabs)

        # ── Status bar ────────────────────────────────────────────────
        status = QStatusBar()
        self.setStatusBar(status)

        # Daily goal progress
        self._goal_label = QLabel("Цель: 0 / 20")
        self._goal_label.setStyleSheet("color: #a8acc8; padding: 0 8px;")
        self._goal_bar = QProgressBar()
        self._goal_bar.setFixedWidth(120)
        self._goal_bar.setFixedHeight(14)
        self._goal_bar.setTextVisible(False)
        self._goal_bar.setRange(0, 100)
        status.addWidget(self._goal_label)
        status.addWidget(self._goal_bar)

        # Settings button (right side of status bar)
        settings_btn = QPushButton("⚙ Настройки")
        settings_btn.setFixedHeight(24)
        settings_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; "
            "color: #7eb8f7; font-size: 12px; padding: 0 8px; }"
            "QPushButton:hover { color: #a8d4ff; }"
        )
        settings_btn.clicked.connect(self._open_settings)
        status.addPermanentWidget(settings_btn)

    def _on_tab_changed(self, index: int):
        # Uses identity checks — safe even if tab indices shift
        tab_widget = self.centralWidget()
        current = tab_widget.widget(index)
        if current is self.favorites:
            self.favorites.refresh()
        elif current is self.stats:
            self.stats.refresh()
        self._refresh_goal()

    def _refresh_goal(self):
        try:
            from ..utils.settings_manager import get_settings
        except ImportError:
            from utils.settings_manager import get_settings
        goal = get_settings().get("daily_goal", 20)
        today_reviews = self.db.get_stats().get("today_reviews", 0)
        self._goal_label.setText(f"Цель на день: {today_reviews} / {goal}")
        pct = min(100, int(today_reviews / goal * 100)) if goal else 0
        self._goal_bar.setValue(pct)
        color = "#48b860" if pct >= 100 else "#7eb8f7"
        self._goal_bar.setStyleSheet(
            f"QProgressBar {{ background: #32354d; border: 1px solid #44475a; border-radius: 3px; }}"
            f"QProgressBar::chunk {{ background: {color}; border-radius: 2px; }}"
        )

    def _open_settings(self):
        try:
            from .settings_dialog import SettingsDialog
        except ImportError:
            from settings_dialog import SettingsDialog
        dlg = SettingsDialog(self)
        dlg.exec()
        self._refresh_goal()
