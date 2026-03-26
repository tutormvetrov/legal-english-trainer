from PyQt6.QtWidgets import QMainWindow, QTabWidget, QStatusBar
from PyQt6.QtCore import Qt

from .flashcards_widget import FlashcardsWidget
from .match_widget import MatchWidget
from .typing_widget import TypingWidget
from .stats_widget import StatsWidget


class MainWindow(QMainWindow):
    def __init__(self, db_manager, scheduler):
        super().__init__()
        self.db = db_manager
        self.scheduler = scheduler
        self.setWindowTitle("Legal English Trainer")
        self.setMinimumSize(900, 650)
        self._build_ui()

    def _build_ui(self):
        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        self.flashcards = FlashcardsWidget(self.db, self.scheduler)
        self.match = MatchWidget(self.db, self.scheduler)
        self.typing = TypingWidget(self.db, self.scheduler)
        self.stats = StatsWidget(self.db)

        tabs.addTab(self.flashcards, "Карточки")
        tabs.addTab(self.match, "Сопоставление")
        tabs.addTab(self.typing, "Списывание")
        tabs.addTab(self.stats, "Статистика")

        # Refresh stats when tab is selected
        tabs.currentChanged.connect(self._on_tab_changed)

        self.setCentralWidget(tabs)
        self.setStatusBar(QStatusBar())

    def _on_tab_changed(self, index):
        if index == 3:
            self.stats.refresh()
