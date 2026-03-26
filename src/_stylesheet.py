"""
Тёмная тема приложения. Вынесена в отдельный модуль для переиспользования.
"""


def build_dark_stylesheet(font_size: int = 13) -> str:
    return f"""
QWidget {{
    background-color: #1a1c2e;
    color: #eeffff;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: {font_size}px;
}}

QMainWindow, QDialog {{
    background-color: #1a1c2e;
}}

/* ── Tabs ──────────────────────────────────────────────────────────────── */

QTabWidget::pane {{
    border: 1px solid #3a3d5c;
    background-color: #1a1c2e;
    border-radius: 0 4px 4px 4px;
}}

QTabBar::tab {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #21243a, stop:1 #1a1c2e);
    color: #8890b8;
    padding: 9px 22px;
    border: 1px solid #3a3d5c;
    border-bottom: none;
    min-width: 100px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background: #1a1c2e;
    color: #eeffff;
    border-top: 3px solid #82aaff;
    padding-top: 7px;
}}

QTabBar::tab:hover:!selected {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2a2d46, stop:1 #1e2138);
    color: #c0c8e8;
}}

/* ── Buttons ───────────────────────────────────────────────────────────── */

QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #363a5e, stop:1 #292d4e);
    color: #c8d0f0;
    border: 1px solid #4a4e72;
    border-radius: 7px;
    padding: 6px 16px;
    min-height: 30px;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #464a72, stop:1 #383c60);
    color: #eeffff;
    border-color: #6870a0;
}}

QPushButton:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #292d4e, stop:1 #363a5e);
    border-color: #82aaff;
}}

QPushButton:disabled {{
    background: #252840;
    color: #555878;
    border-color: #353858;
}}

QPushButton#knowBtn {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1e5232, stop:1 #143a24);
    color: #c3e88d;
    border: 1px solid #4a9830;
    font-weight: bold;
}}
QPushButton#knowBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #286842, stop:1 #1e4c30);
    border-color: #64c040;
}}
QPushButton#knowBtn:pressed {{
    background: #143a24;
}}

QPushButton#dontKnowBtn {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #521e28, stop:1 #3a1018);
    color: #f07178;
    border: 1px solid #a03040;
    font-weight: bold;
}}
QPushButton#dontKnowBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #682838, stop:1 #4c1a22);
    border-color: #d04060;
}}
QPushButton#dontKnowBtn:pressed {{
    background: #3a1018;
}}

QPushButton#matchBtn {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2e3252, stop:1 #252844);
    color: #c8d0f0;
    border: 1px solid #464a6e;
    border-radius: 7px;
    text-align: center;
    padding: 6px 10px;
}}
QPushButton#matchBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3e4268, stop:1 #333658);
    border-color: #6870a0;
    color: #eeffff;
}}

/* ── Inputs ────────────────────────────────────────────────────────────── */

QComboBox {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #363a5e, stop:1 #292d4e);
    color: #eeffff;
    border: 1px solid #4a4e72;
    border-radius: 7px;
    padding: 4px 8px;
    min-height: 28px;
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox QAbstractItemView {{
    background-color: #252840;
    color: #eeffff;
    selection-background-color: #363a5e;
    border: 1px solid #4a4e72;
}}

QSpinBox {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #363a5e, stop:1 #292d4e);
    color: #eeffff;
    border: 1px solid #4a4e72;
    border-radius: 7px;
    padding: 4px 8px;
    min-height: 28px;
}}

QLineEdit {{
    background-color: #252840;
    color: #eeffff;
    border: 1px solid #4a4e72;
    border-radius: 7px;
    padding: 6px 12px;
    font-size: {font_size + 1}px;
}}

QLineEdit:focus {{
    border: 1px solid #82aaff;
    background-color: #1e2238;
}}

/* ── Labels ────────────────────────────────────────────────────────────── */

QLabel {{
    color: #eeffff;
}}

QLabel#categoryTag {{
    color: #82aaff;
    font-size: {font_size - 1}px;
    font-weight: bold;
    letter-spacing: 1px;
    border-radius: 10px;
    padding: 3px 14px;
}}

QLabel#termLabel {{
    color: #eeffff;
}}

QLabel#translationLabel {{
    color: #c3e88d;
    font-weight: bold;
}}

QLabel#definitionLabel {{
    color: #c0c8e8;
    font-size: {font_size - 1}px;
    font-style: italic;
}}

QLabel#exampleLabel {{
    color: #8890b8;
    font-size: {font_size - 2}px;
}}

QLabel#feedbackLabel {{
    font-size: {font_size}px;
}}

QLabel#colHeader {{
    color: #82aaff;
    font-weight: bold;
    font-size: {font_size}px;
    padding: 4px 0;
}}

/* ── Cards ─────────────────────────────────────────────────────────────── */

QFrame#card {{
    background-color: #252840;
    border: 1px solid #3a3d5c;
    border-left: 3px solid #82aaff;
    border-radius: 14px;
}}

QFrame#translationFrame {{
    border-top: 1px solid #3a3d5c;
    margin-top: 8px;
    padding-top: 8px;
}}

/* ── Stat cards ────────────────────────────────────────────────────────── */

QWidget#statCard {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2a2e4a, stop:1 #222540);
    border: 1px solid #3a3d5c;
    border-top: 2px solid #82aaff;
    border-radius: 10px;
    min-width: 110px;
}}

QLabel#statValue {{
    color: #82aaff;
}}

QLabel#statTitle {{
    color: #8890b8;
    font-size: {font_size - 2}px;
}}

/* ── Table ─────────────────────────────────────────────────────────────── */

QTableWidget {{
    background-color: #252840;
    alternate-background-color: #1e2138;
    gridline-color: #3a3d5c;
    color: #eeffff;
    border: 1px solid #3a3d5c;
    border-radius: 8px;
}}

QTableWidget::item {{
    padding: 6px;
}}

QTableWidget::item:selected {{
    background-color: #363a5e;
}}

QHeaderView::section {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #21243a, stop:1 #1c1f34);
    color: #82aaff;
    padding: 7px 10px;
    border: none;
    border-bottom: 1px solid #3a3d5c;
    font-weight: bold;
}}

QTableWidget QTableCornerButton::section {{
    background-color: #21243a;
}}

/* ── Scrollbar ─────────────────────────────────────────────────────────── */

QScrollBar:vertical {{
    background-color: #1a1c2e;
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #464a6e, stop:1 #5a5e82);
    border-radius: 4px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: #6870a0;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ── Status bar ────────────────────────────────────────────────────────── */

QStatusBar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1e2138, stop:1 #1a1c2e);
    color: #8890b8;
    font-size: {font_size - 2}px;
    border-top: 1px solid #3a3d5c;
}}

/* ── Progress bar ──────────────────────────────────────────────────────── */

QProgressBar {{
    background-color: #252840;
    border: 1px solid #3a3d5c;
    border-radius: 5px;
    text-align: center;
    color: #eeffff;
    font-size: {font_size - 2}px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5580e0, stop:1 #82aaff);
    border-radius: 4px;
}}

/* ── Misc ──────────────────────────────────────────────────────────────── */

QGroupBox {{
    border: 1px solid #3a3d5c;
    border-radius: 8px;
    margin-top: 8px;
    padding-top: 8px;
    font-weight: bold;
    color: #8890b8;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}}

QCheckBox {{
    color: #eeffff;
    spacing: 6px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid #4a4e72;
    border-radius: 4px;
    background-color: #252840;
}}

QCheckBox::indicator:checked {{
    background-color: #82aaff;
    border-color: #82aaff;
}}
"""
