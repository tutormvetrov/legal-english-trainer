"""
Тёмная тема приложения. Вынесена в отдельный модуль для переиспользования.
"""


def build_dark_stylesheet(font_size: int = 13) -> str:
    return f"""
QWidget {{
    background-color: #2b2d3e;
    color: #e0e4f8;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: {font_size}px;
}}

QMainWindow, QDialog {{
    background-color: #2b2d3e;
}}

QTabWidget::pane {{
    border: 1px solid #44475a;
    background-color: #2b2d3e;
}}

QTabBar::tab {{
    background-color: #23253a;
    color: #b8bcd8;
    padding: 8px 20px;
    border: 1px solid #44475a;
    border-bottom: none;
    min-width: 100px;
}}

QTabBar::tab:selected {{
    background-color: #2b2d3e;
    color: #e0e4f8;
    border-top: 2px solid #7eb8f7;
}}

QTabBar::tab:hover:!selected {{
    background-color: #32354d;
}}

QPushButton {{
    background-color: #3e4060;
    color: #e0e4f8;
    border: 1px solid #5a5d7a;
    border-radius: 6px;
    padding: 6px 16px;
    min-height: 30px;
}}

QPushButton:hover {{
    background-color: #4e5170;
}}

QPushButton:pressed {{
    background-color: #5e6180;
}}

QPushButton:disabled {{
    background-color: #32354d;
    color: #6a6d8a;
}}

QPushButton#knowBtn {{
    background-color: #264d35;
    color: #b8f0c0;
    border: 1px solid #48b860;
}}
QPushButton#knowBtn:hover {{
    background-color: #30603f;
}}

QPushButton#dontKnowBtn {{
    background-color: #4d2630;
    color: #f8b0c0;
    border: 1px solid #c04050;
}}
QPushButton#dontKnowBtn:hover {{
    background-color: #603040;
}}

QPushButton#matchBtn {{
    background-color: #32354d;
    color: #e0e4f8;
    border: 1px solid #5a5d7a;
    border-radius: 6px;
    text-align: center;
    padding: 6px 10px;
}}
QPushButton#matchBtn:hover {{
    background-color: #3e4060;
}}

QComboBox {{
    background-color: #3e4060;
    color: #e0e4f8;
    border: 1px solid #5a5d7a;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 28px;
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox QAbstractItemView {{
    background-color: #3e4060;
    color: #e0e4f8;
    selection-background-color: #4e5170;
    border: 1px solid #5a5d7a;
}}

QSpinBox {{
    background-color: #3e4060;
    color: #e0e4f8;
    border: 1px solid #5a5d7a;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 28px;
}}

QLineEdit {{
    background-color: #3e4060;
    color: #e0e4f8;
    border: 1px solid #5a5d7a;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: {font_size + 1}px;
}}

QLineEdit:focus {{
    border: 1px solid #7eb8f7;
}}

QLabel {{
    color: #e0e4f8;
}}

QLabel#categoryTag {{
    color: #7eb8f7;
    font-size: {font_size - 2}px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

QLabel#termLabel {{
    color: #e0e4f8;
}}

QLabel#translationLabel {{
    color: #b8f0c0;
    font-weight: bold;
}}

QLabel#definitionLabel {{
    color: #c8cce8;
    font-size: {font_size - 1}px;
    font-style: italic;
}}

QLabel#exampleLabel {{
    color: #a8acc8;
    font-size: {font_size - 2}px;
}}

QLabel#feedbackLabel {{
    font-size: {font_size}px;
}}

QLabel#colHeader {{
    color: #7eb8f7;
    font-weight: bold;
    font-size: {font_size}px;
    padding: 4px 0;
}}

QFrame#card {{
    background-color: #32354d;
    border: 1px solid #44475a;
    border-radius: 12px;
}}

QFrame#translationFrame {{
    border-top: 1px solid #44475a;
    margin-top: 8px;
    padding-top: 8px;
}}

QWidget#statCard {{
    background-color: #32354d;
    border: 1px solid #44475a;
    border-radius: 8px;
    min-width: 110px;
}}

QLabel#statValue {{
    color: #7eb8f7;
}}

QLabel#statTitle {{
    color: #a8acc8;
    font-size: {font_size - 2}px;
}}

QTableWidget {{
    background-color: #32354d;
    alternate-background-color: #2b2d3e;
    gridline-color: #44475a;
    color: #e0e4f8;
    border: 1px solid #44475a;
    border-radius: 6px;
}}

QTableWidget::item {{
    padding: 6px;
}}

QTableWidget::item:selected {{
    background-color: #44475a;
}}

QHeaderView::section {{
    background-color: #23253a;
    color: #7eb8f7;
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid #44475a;
    font-weight: bold;
}}

QTableWidget QTableCornerButton::section {{
    background-color: #23253a;
}}

QScrollBar:vertical {{
    background-color: #23253a;
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: #5a5d7a;
    border-radius: 5px;
    min-height: 20px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QStatusBar {{
    background-color: #23253a;
    color: #8a8da8;
    font-size: {font_size - 2}px;
}}

QProgressBar {{
    background-color: #32354d;
    border: 1px solid #44475a;
    border-radius: 4px;
    text-align: center;
    color: #e0e4f8;
    font-size: {font_size - 2}px;
}}

QProgressBar::chunk {{
    background-color: #7eb8f7;
    border-radius: 3px;
}}

QGroupBox {{
    border: 1px solid #44475a;
    border-radius: 6px;
    margin-top: 8px;
    padding-top: 8px;
    font-weight: bold;
    color: #b8bcd8;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}}

QCheckBox {{
    color: #e0e4f8;
    spacing: 6px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid #5a5d7a;
    border-radius: 3px;
    background-color: #3e4060;
}}

QCheckBox::indicator:checked {{
    background-color: #7eb8f7;
    border-color: #7eb8f7;
}}
"""
