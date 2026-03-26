from PyQt6.QtWidgets import QMainWindow, QTabWidget, QStatusBar
from PyQt6.QtCore import Qt

from .flashcards_widget import FlashcardsWidget
from .match_widget import MatchWidget
from .typing_widget import TypingWidget
from .stats_widget import StatsWidget
from .favorites_widget import FavoritesWidget
from .boss_widget import BossWidget


class MainWindow(QMainWindow):
    def __init__(self, db_manager, scheduler, streak: int = 0, username: str = ""):
        super().__init__()
        self.db = db_manager
        self.scheduler = scheduler
        self.streak = streak
        self.username = username
        self._update_title()
        self.setMinimumSize(900, 650)
        self._build_ui()

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
        self.favorites  = FavoritesWidget(self.db)
        self.boss       = BossWidget(self.db)
        self.stats      = StatsWidget(self.db)

        tabs.addTab(self.flashcards, "🃏 Карточки")
        tabs.addTab(self.match,      "🔗 Сопоставление")
        tabs.addTab(self.typing,     "✍️ Диктант")
        tabs.addTab(self.favorites,  "⭐ Избранное")
        tabs.addTab(self.boss,       "👊 Boss Mode")
        tabs.addTab(self.stats,      "📊 Статистика")

        tabs.currentChanged.connect(self._on_tab_changed)

        self.setCentralWidget(tabs)
        self.setStatusBar(QStatusBar())

    def _on_tab_changed(self, index: int):
        if index == 3:
            self.favorites.refresh()
        elif index == 5:
            self.stats.refresh()
