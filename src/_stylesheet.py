"""
Theme stylesheets for the application.
"""

from copy import deepcopy


_DARK = {
    "window_bg": "#171a29",
    "text": "#eef2ff",
    "muted": "#98a0c4",
    "section": "#dbe3ff",
    "control": "#99a3ca",
    "empty_title": "#dfe6ff",
    "hero_eyebrow": "#7eb8f7",
    "hero_title": "#f7f9ff",
    "hero_subtitle": "#a7b1d8",
    "hero_meta": "#d7def9",
    "hero_chip_bg": "#232b45",
    "hero_chip_text": "#f1f5ff",
    "hero_chip_border": "#43557f",
    "stat_pill_bg": "#202640",
    "stat_pill_text": "#dfe7ff",
    "stat_pill_border": "#39456d",
    "term_eyebrow": "#7f8ab2",
    "term_text": "#f8faff",
    "translation_text": "#c3e88d",
    "definition_text": "#c0c8e8",
    "example_text": "#8890b8",
    "result_bg": "#1f2438",
    "result_border": "#373e60",
    "tab_top": "#1f243c",
    "tab_bottom": "#191e31",
    "tab_text": "#9aa2c8",
    "tab_border": "#2f3552",
    "tab_sel_top": "#283251",
    "tab_sel_bottom": "#202744",
    "tab_sel_text": "#f6f8ff",
    "tab_sel_border": "#4f6797",
    "tab_hover_top": "#2a2f4b",
    "tab_hover_bottom": "#1d2036",
    "tab_hover_text": "#d5dcf8",
    "btn_top": "#3a4167",
    "btn_bottom": "#2a3050",
    "btn_text": "#d7def9",
    "btn_border": "#4d547a",
    "btn_hover_top": "#485079",
    "btn_hover_bottom": "#394061",
    "btn_hover_text": "#f6f8ff",
    "btn_hover_border": "#6e78aa",
    "btn_press_top": "#272d48",
    "btn_press_bottom": "#353c5c",
    "btn_press_border": "#7eb8f7",
    "btn_disabled_bg": "#23263b",
    "btn_disabled_text": "#5f6485",
    "btn_disabled_border": "#30344f",
    "primary_top": "#5f93ee",
    "primary_bottom": "#3f6fcf",
    "primary_text": "#f8fbff",
    "primary_border": "#83b2ff",
    "primary_hover_top": "#70a1f4",
    "primary_hover_bottom": "#4b7bdd",
    "primary_hover_border": "#a4c8ff",
    "primary_pressed": "#3f6fcf",
    "subtle_bg": "#20243a",
    "subtle_text": "#bfc8ea",
    "subtle_border": "#3b4265",
    "subtle_hover_bg": "#272c45",
    "subtle_hover_text": "#eef2ff",
    "danger_top": "#5a2230",
    "danger_bottom": "#421520",
    "danger_text": "#ffced8",
    "danger_border": "#a24b63",
    "know_top": "#1e5232",
    "know_bottom": "#143a24",
    "know_text": "#c3e88d",
    "know_border": "#4a9830",
    "know_hover_top": "#286842",
    "know_hover_bottom": "#1e4c30",
    "know_hover_border": "#64c040",
    "know_pressed": "#143a24",
    "dont_top": "#521e28",
    "dont_bottom": "#3a1018",
    "dont_text": "#f07178",
    "dont_border": "#a03040",
    "dont_hover_top": "#682838",
    "dont_hover_bottom": "#4c1a22",
    "dont_hover_border": "#d04060",
    "dont_pressed": "#3a1018",
    "match_top": "#2e3252",
    "match_bottom": "#252844",
    "match_text": "#c8d0f0",
    "match_border": "#464a6e",
    "match_hover_top": "#3e4268",
    "match_hover_bottom": "#333658",
    "match_hover_border": "#6870a0",
    "match_hover_text": "#eeffff",
    "input_top": "#363d62",
    "input_bottom": "#282e4a",
    "input_text": "#eef2ff",
    "input_border": "#4a4f73",
    "input_bg": "#21253a",
    "input_focus_bg": "#1b2033",
    "focus_border": "#7eb8f7",
    "placeholder": "#7f86ab",
    "card_bg": "#21253a",
    "card_border": "#353a56",
    "card_accent": "#7eb8f7",
    "hero_top": "#202843",
    "hero_mid": "#1d2338",
    "hero_bottom": "#181d2e",
    "hero_border": "#39415f",
    "translation_border": "#353a56",
    "stat_top": "#262b45",
    "stat_bottom": "#1f2339",
    "stat_border": "#353a56",
    "stat_accent": "#7eb8f7",
    "stat_value": "#82aaff",
    "stat_title": "#8890b8",
    "table_bg": "#21253a",
    "table_alt": "#1b2033",
    "table_grid": "#343955",
    "table_text": "#eef2ff",
    "table_border": "#353a56",
    "table_selected": "#33405f",
    "header_top": "#1f2438",
    "header_bottom": "#1a1e31",
    "header_text": "#8fc2ff",
    "header_border": "#353a56",
    "header_corner": "#21243a",
    "scroll_bg": "#1a1c2e",
    "scroll_handle_top": "#464a6e",
    "scroll_handle_bottom": "#5a5e82",
    "scroll_handle_hover": "#6870a0",
    "status_top": "#1c2033",
    "status_bottom": "#171a29",
    "status_text": "#98a0c4",
    "status_border": "#353a56",
    "progress_bg": "#21253a",
    "progress_border": "#353a56",
    "progress_text": "#eef2ff",
    "progress_top": "#5580e0",
    "progress_bottom": "#82aaff",
    "group_border": "#353a56",
    "group_text": "#98a0c4",
    "checkbox_border": "#4a4f73",
    "checkbox_bg": "#21253a",
    "checkbox_checked": "#7eb8f7",
    "settings_link": "#7eb8f7",
    "settings_link_hover": "#a8d4ff",
    "goal_track_bg": "#32354d",
    "goal_track_border": "#44475a",
    "goal_complete": "#48b860",
    "goal_incomplete": "#7eb8f7",
    "star_bg": "#2a2e4a",
    "star_border": "#4a4e72",
    "star_hover_bg": "#363a5e",
    "star_text": "#eef2ff",
    "star_active": "#ffd700",
    "flash_correct": "#0e2e1c",
    "flash_wrong": "#2e0e16",
    "highlight_bg": "#3a2800",
    "highlight_text": "#ffcb6b",
}

_LIGHT = {
    "window_bg": "#f5efe4",
    "text": "#3f3024",
    "muted": "#8a755f",
    "section": "#5a4633",
    "control": "#8f7860",
    "empty_title": "#503d2d",
    "hero_eyebrow": "#a97a45",
    "hero_title": "#3f2f22",
    "hero_subtitle": "#7a6652",
    "hero_meta": "#755f4a",
    "hero_chip_bg": "#f2e5d1",
    "hero_chip_text": "#6a4f34",
    "hero_chip_border": "#c8a777",
    "stat_pill_bg": "#f4e8d6",
    "stat_pill_text": "#6a5137",
    "stat_pill_border": "#cdb08c",
    "term_eyebrow": "#9f8666",
    "term_text": "#35271d",
    "translation_text": "#6e8453",
    "definition_text": "#766657",
    "example_text": "#8f7d6c",
    "result_bg": "#f4e9db",
    "result_border": "#d4b892",
    "tab_top": "#f1e7d7",
    "tab_bottom": "#eadfcd",
    "tab_text": "#8f7860",
    "tab_border": "#d5c2a9",
    "tab_sel_top": "#fff8ee",
    "tab_sel_bottom": "#f6ebda",
    "tab_sel_text": "#5a4531",
    "tab_sel_border": "#c79b63",
    "tab_hover_top": "#fbf1e2",
    "tab_hover_bottom": "#efe2cf",
    "tab_hover_text": "#6b543d",
    "btn_top": "#f8f0e3",
    "btn_bottom": "#eadcc8",
    "btn_text": "#5a4732",
    "btn_border": "#ccb79e",
    "btn_hover_top": "#fff7ed",
    "btn_hover_bottom": "#efe0ca",
    "btn_hover_text": "#483625",
    "btn_hover_border": "#b88f5b",
    "btn_press_top": "#e8d7bd",
    "btn_press_bottom": "#dfccb1",
    "btn_press_border": "#a97f4d",
    "btn_disabled_bg": "#eee5d8",
    "btn_disabled_text": "#b09f89",
    "btn_disabled_border": "#dccdb8",
    "primary_top": "#c89156",
    "primary_bottom": "#a86e3c",
    "primary_text": "#fff8f0",
    "primary_border": "#b47a45",
    "primary_hover_top": "#d49d63",
    "primary_hover_bottom": "#b97d48",
    "primary_hover_border": "#9c6332",
    "primary_pressed": "#a86e3c",
    "subtle_bg": "#f4ebde",
    "subtle_text": "#6c5842",
    "subtle_border": "#cfbca3",
    "subtle_hover_bg": "#eee1cd",
    "subtle_hover_text": "#503f2d",
    "danger_top": "#b95157",
    "danger_bottom": "#963e46",
    "danger_text": "#fff6f4",
    "danger_border": "#a54f52",
    "know_top": "#91a977",
    "know_bottom": "#738a58",
    "know_text": "#fffdf5",
    "know_border": "#6f8653",
    "know_hover_top": "#9db684",
    "know_hover_bottom": "#7d9562",
    "know_hover_border": "#667c4c",
    "know_pressed": "#738a58",
    "dont_top": "#bf5b62",
    "dont_bottom": "#9d4049",
    "dont_text": "#fff7f5",
    "dont_border": "#ab5054",
    "dont_hover_top": "#ca686f",
    "dont_hover_bottom": "#a74850",
    "dont_hover_border": "#954044",
    "dont_pressed": "#9d4049",
    "match_top": "#f8f0e3",
    "match_bottom": "#ecdec8",
    "match_text": "#5c4935",
    "match_border": "#ccb69d",
    "match_hover_top": "#fff7ed",
    "match_hover_bottom": "#f2e5d3",
    "match_hover_border": "#b88f5b",
    "match_hover_text": "#433224",
    "input_top": "#fffaf2",
    "input_bottom": "#f6ecdd",
    "input_text": "#3f3024",
    "input_border": "#cdb9a1",
    "input_bg": "#fffaf2",
    "input_focus_bg": "#fffdf9",
    "focus_border": "#bc8750",
    "placeholder": "#a18d78",
    "card_bg": "#fffaf2",
    "card_border": "#dccbb5",
    "card_accent": "#b8864c",
    "hero_top": "#fbf4e9",
    "hero_mid": "#f5ebdb",
    "hero_bottom": "#efe1ce",
    "hero_border": "#d8b791",
    "translation_border": "#deceb7",
    "stat_top": "#fff8ee",
    "stat_bottom": "#f2e5d2",
    "stat_border": "#decbb1",
    "stat_accent": "#b8864c",
    "stat_value": "#9b6a39",
    "stat_title": "#8a745b",
    "table_bg": "#fffaf2",
    "table_alt": "#f8efe2",
    "table_grid": "#e0d0bb",
    "table_text": "#403025",
    "table_border": "#dccab3",
    "table_selected": "#efdeca",
    "header_top": "#f5ead8",
    "header_bottom": "#ecdec9",
    "header_text": "#96693a",
    "header_border": "#dcc7ac",
    "header_corner": "#f0e3d1",
    "scroll_bg": "#ece3d6",
    "scroll_handle_top": "#c9b18f",
    "scroll_handle_bottom": "#b89469",
    "scroll_handle_hover": "#a97a45",
    "status_top": "#f0e6d8",
    "status_bottom": "#e8dbc9",
    "status_text": "#7d6853",
    "status_border": "#d7c2a6",
    "progress_bg": "#f2e8db",
    "progress_border": "#d7c7b2",
    "progress_text": "#5b4936",
    "progress_top": "#bf9058",
    "progress_bottom": "#d4ae73",
    "group_border": "#d8c6b1",
    "group_text": "#8b755a",
    "checkbox_border": "#c8b59d",
    "checkbox_bg": "#fff8ef",
    "checkbox_checked": "#bc8750",
    "settings_link": "#a06a37",
    "settings_link_hover": "#c1894c",
    "goal_track_bg": "#eee2cf",
    "goal_track_border": "#d4bea0",
    "goal_complete": "#7f9963",
    "goal_incomplete": "#b8864c",
    "star_bg": "#f3e8d8",
    "star_border": "#cfb899",
    "star_hover_bg": "#eddcc4",
    "star_text": "#785c3c",
    "star_active": "#c7963a",
    "flash_correct": "#e6efda",
    "flash_wrong": "#f7dfe0",
    "highlight_bg": "#f4e2bf",
    "highlight_text": "#8a5f25",
}


_THEMES = {
    "dark": _DARK,
    "light": _LIGHT,
}


def get_theme_palette(theme: str = "dark") -> dict:
    return deepcopy(_THEMES.get(theme, _DARK))


def build_stylesheet(font_size: int = 13, theme: str = "dark") -> str:
    p = get_theme_palette(theme)
    p.update({
        "font_size": font_size,
        "font_size_plus_1": font_size + 1,
        "font_size_plus_4": font_size + 4,
        "font_size_plus_10": font_size + 10,
        "font_size_minus_1": font_size - 1,
        "font_size_minus_2": font_size - 2,
    })
    return """
QWidget {{
    background-color: transparent;
    color: {text};
    font-family: "Inter", "Segoe UI", Arial, sans-serif;
    font-size: {font_size}px;
}}

QMainWindow, QDialog, QWidget#appShell {{
    background-color: {window_bg};
}}

QTabWidget::pane {{
    border: none;
    background-color: transparent;
    top: -2px;
}}

QTabBar::tab {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {tab_top}, stop:1 {tab_bottom});
    color: {tab_text};
    padding: 8px 16px;
    border: 1px solid {tab_border};
    min-width: 88px;
    margin-right: 6px;
    border-radius: 9px;
}}

QTabBar::tab:selected {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {tab_sel_top}, stop:1 {tab_sel_bottom});
    color: {tab_sel_text};
    border: 1px solid {tab_sel_border};
}}

QTabBar::tab:hover:!selected {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {tab_hover_top}, stop:1 {tab_hover_bottom});
    color: {tab_hover_text};
}}

QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {btn_top}, stop:1 {btn_bottom});
    color: {btn_text};
    border: 1px solid {btn_border};
    border-radius: 9px;
    padding: 7px 16px;
    min-height: 30px;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {btn_hover_top}, stop:1 {btn_hover_bottom});
    color: {btn_hover_text};
    border-color: {btn_hover_border};
}}

QPushButton:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {btn_press_top}, stop:1 {btn_press_bottom});
    border-color: {btn_press_border};
}}

QPushButton:disabled {{
    background: {btn_disabled_bg};
    color: {btn_disabled_text};
    border-color: {btn_disabled_border};
}}

QPushButton#primaryBtn {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {primary_top}, stop:1 {primary_bottom});
    color: {primary_text};
    border: 1px solid {primary_border};
    font-weight: bold;
}}

QPushButton#primaryBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {primary_hover_top}, stop:1 {primary_hover_bottom});
    border-color: {primary_hover_border};
}}

QPushButton#primaryBtn:pressed {{
    background: {primary_pressed};
}}

QPushButton#subtleBtn {{
    background: {subtle_bg};
    color: {subtle_text};
    border: 1px solid {subtle_border};
}}

QPushButton#subtleBtn:hover {{
    background: {subtle_hover_bg};
    color: {subtle_hover_text};
}}

QPushButton#dangerBtn {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {danger_top}, stop:1 {danger_bottom});
    color: {danger_text};
    border: 1px solid {danger_border};
}}

QPushButton#knowBtn {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {know_top}, stop:1 {know_bottom});
    color: {know_text};
    border: 1px solid {know_border};
    font-weight: bold;
}}

QPushButton#knowBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {know_hover_top}, stop:1 {know_hover_bottom});
    border-color: {know_hover_border};
}}

QPushButton#knowBtn:pressed {{
    background: {know_pressed};
}}

QPushButton#dontKnowBtn {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {dont_top}, stop:1 {dont_bottom});
    color: {dont_text};
    border: 1px solid {dont_border};
    font-weight: bold;
}}

QPushButton#dontKnowBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {dont_hover_top}, stop:1 {dont_hover_bottom});
    border-color: {dont_hover_border};
}}

QPushButton#dontKnowBtn:pressed {{
    background: {dont_pressed};
}}

QPushButton#matchBtn {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {match_top}, stop:1 {match_bottom});
    color: {match_text};
    border: 1px solid {match_border};
    border-radius: 7px;
    text-align: center;
    padding: 6px 10px;
}}

QPushButton#matchBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {match_hover_top}, stop:1 {match_hover_bottom});
    border-color: {match_hover_border};
    color: {match_hover_text};
}}

QPushButton#settingsLink {{
    background: transparent;
    border: none;
    color: {settings_link};
    font-size: 12px;
    padding: 0 8px;
}}

QPushButton#settingsLink:hover {{
    color: {settings_link_hover};
}}

QComboBox {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {input_top}, stop:1 {input_bottom});
    color: {input_text};
    border: 1px solid {input_border};
    border-radius: 8px;
    padding: 4px 10px;
    min-height: 28px;
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox QAbstractItemView {{
    background-color: {input_bg};
    color: {input_text};
    selection-background-color: {table_selected};
    border: 1px solid {input_border};
}}

QSpinBox {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {input_top}, stop:1 {input_bottom});
    color: {input_text};
    border: 1px solid {input_border};
    border-radius: 8px;
    padding: 4px 8px;
    min-height: 28px;
}}

QLineEdit, QTextEdit {{
    background-color: {input_bg};
    color: {input_text};
    border: 1px solid {input_border};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: {font_size_plus_1}px;
}}

QLineEdit:focus, QTextEdit:focus {{
    border: 1px solid {focus_border};
    background-color: {input_focus_bg};
}}

QLineEdit::placeholder, QTextEdit::placeholder {{
    color: {placeholder};
}}

QLabel {{
    color: {text};
    background: transparent;
}}

QLabel#mutedLabel {{
    color: {muted};
}}

QLabel#sectionLabel {{
    color: {section};
    font-weight: bold;
}}

QLabel#controlLabel {{
    color: {control};
    font-size: {font_size_minus_1}px;
    font-weight: bold;
}}

QLabel#emptyTitle {{
    color: {empty_title};
    font-weight: bold;
    font-size: {font_size_plus_4}px;
}}

QLabel#emptyText {{
    color: {muted};
    font-size: {font_size_minus_1}px;
}}

QLabel#heroEyebrow {{
    color: {hero_eyebrow};
    font-size: {font_size_minus_2}px;
    font-weight: bold;
    letter-spacing: 1px;
}}

QLabel#heroTitle {{
    color: {hero_title};
    font-size: {font_size_plus_10}px;
    font-weight: bold;
}}

QLabel#heroSubtitle {{
    color: {hero_subtitle};
    font-size: {font_size}px;
}}

QLabel#heroMeta {{
    color: {hero_meta};
    font-size: {font_size_minus_1}px;
}}

QLabel#heroChip {{
    background: {hero_chip_bg};
    color: {hero_chip_text};
    border: 1px solid {hero_chip_border};
    border-radius: 12px;
    padding: 8px 12px;
    font-size: {font_size_minus_1}px;
    font-weight: bold;
}}

QLabel#statPill {{
    background: {stat_pill_bg};
    color: {stat_pill_text};
    border: 1px solid {stat_pill_border};
    border-radius: 11px;
    padding: 6px 10px;
    font-size: {font_size_minus_1}px;
    font-weight: bold;
}}

QLabel#termEyebrow {{
    color: {term_eyebrow};
    font-size: {font_size_minus_2}px;
    letter-spacing: 1px;
    font-weight: bold;
}}

QLabel#resultBanner {{
    background: {result_bg};
    border: 1px solid {result_border};
    border-radius: 10px;
    padding: 12px 14px;
}}

QLabel#categoryTag {{
    color: {hero_eyebrow};
    font-size: {font_size_minus_1}px;
    font-weight: bold;
    letter-spacing: 1px;
    border-radius: 10px;
    padding: 3px 14px;
}}

QLabel#termLabel {{
    color: {term_text};
}}

QLabel#translationLabel {{
    color: {translation_text};
    font-weight: bold;
}}

QLabel#definitionLabel {{
    color: {definition_text};
    font-size: {font_size_minus_1}px;
    font-style: italic;
}}

QLabel#exampleLabel {{
    color: {example_text};
    font-size: {font_size_minus_2}px;
}}

QLabel#feedbackLabel {{
    font-size: {font_size}px;
}}

QLabel#colHeader {{
    color: {hero_eyebrow};
    font-weight: bold;
    font-size: {font_size}px;
    padding: 4px 0;
}}

QFrame#card {{
    background-color: {card_bg};
    border: 1px solid {card_border};
    border-left: 3px solid {card_accent};
    border-radius: 16px;
}}

QFrame#heroCard {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {hero_top}, stop:0.55 {hero_mid}, stop:1 {hero_bottom});
    border: 1px solid {hero_border};
    border-radius: 18px;
}}

QFrame#translationFrame {{
    border-top: 1px solid {translation_border};
    margin-top: 8px;
    padding-top: 8px;
}}

QWidget#statCard {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {stat_top}, stop:1 {stat_bottom});
    border: 1px solid {stat_border};
    border-top: 2px solid {stat_accent};
    border-radius: 12px;
    min-width: 110px;
}}

QLabel#statValue {{
    color: {stat_value};
}}

QLabel#statTitle {{
    color: {stat_title};
    font-size: {font_size_minus_2}px;
}}

QTableWidget {{
    background-color: {table_bg};
    alternate-background-color: {table_alt};
    gridline-color: {table_grid};
    color: {table_text};
    border: 1px solid {table_border};
    border-radius: 10px;
}}

QTableWidget::item {{
    padding: 6px;
}}

QTableWidget::item:selected {{
    background-color: {table_selected};
}}

QHeaderView::section {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {header_top}, stop:1 {header_bottom});
    color: {header_text};
    padding: 7px 10px;
    border: none;
    border-bottom: 1px solid {header_border};
    font-weight: bold;
}}

QTableWidget QTableCornerButton::section {{
    background-color: {header_corner};
}}

QScrollBar:vertical {{
    background-color: {scroll_bg};
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {scroll_handle_top}, stop:1 {scroll_handle_bottom});
    border-radius: 4px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {scroll_handle_hover};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QStatusBar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {status_top}, stop:1 {status_bottom});
    color: {status_text};
    font-size: {font_size_minus_2}px;
    border-top: 1px solid {status_border};
}}

QProgressBar {{
    background-color: {progress_bg};
    border: 1px solid {progress_border};
    border-radius: 5px;
    text-align: center;
    color: {progress_text};
    font-size: {font_size_minus_2}px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {progress_top}, stop:1 {progress_bottom});
    border-radius: 4px;
}}

QGroupBox {{
    border: 1px solid {group_border};
    border-radius: 10px;
    margin-top: 8px;
    padding-top: 10px;
    font-weight: bold;
    color: {group_text};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}}

QCheckBox {{
    color: {text};
    spacing: 6px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {checkbox_border};
    border-radius: 4px;
    background-color: {checkbox_bg};
}}

QCheckBox::indicator:checked {{
    background-color: {checkbox_checked};
    border-color: {checkbox_checked};
}}
""".format(**p)


def build_dark_stylesheet(font_size: int = 13) -> str:
    return build_stylesheet(font_size=font_size, theme="dark")


def build_light_stylesheet(font_size: int = 13) -> str:
    return build_stylesheet(font_size=font_size, theme="light")

