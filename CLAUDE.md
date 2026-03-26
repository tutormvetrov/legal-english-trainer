# Desktop Vocabulary Trainer — полная техническая спецификация

Этот файл описывает архитектуру, все модули, API и паттерны приложения.
Используй его как отправную точку при создании нового тренажёра словаря
на любую тематику (медицина, IT, иностранный язык, профессиональные термины).

---

## Стек

| Слой | Технология | Почему |
|---|---|---|
| GUI | PyQt6 | Кроссплатформенный нативный UI, тёмные темы, анимации |
| База данных | SQLite (stdlib `sqlite3`) | Офлайн, без сервера, файл рядом с exe |
| Алгоритм повторения | SM-2 | Стандарт de facto для карточек |
| Упаковка | PyInstaller | Один exe/app без установки Python |
| CI/CD | GitHub Actions | Автосборка под Windows и macOS одновременно |
| Язык | Python 3.11+ | |

---

## Структура проекта

```
project/
├── run.py                        # Точка входа (добавляет root в sys.path, crash logging)
├── data/
│   └── terms.json                # Исходные данные (импортируются в БД при старте)
├── assets/
│   └── fonts/                    # TTF шрифты (Inter, etc.)
├── scripts/
│   ├── keygen.py                 # Генератор серийных ключей (для разработчика)
│   ├── reset_app.py              # Сброс состояния для тестирования
│   ├── generate_terms.py         # Генератор/редактор terms.json по батчам
│   ├── populate_db.py            # Ручной импорт terms.json → БД
│   ├── build_windows.bat         # Локальная сборка exe
│   └── build_macos.sh            # Локальная сборка app
├── .github/
│   └── workflows/
│       └── build.yml             # GitHub Actions: Windows + macOS → Release
└── src/
    ├── main.py                   # QApplication, тема, активация, streak, таймеры
    ├── version.py                # __version__, GITHUB_REPO
    ├── _stylesheet.py            # build_dark_stylesheet(font_size) → CSS str
    ├── database/
    │   ├── schema.sql            # DDL (CREATE TABLE IF NOT EXISTS)
    │   └── db_manager.py         # Единственный класс для работы с БД
    ├── models/
    │   └── term.py               # Dataclass Term с from_row(sqlite3.Row)
    ├── algorithms/
    │   └── spaced_repetition.py  # SM-2: review(term_id, quality 0-5)
    ├── utils/
    │   ├── helpers.py            # answers_match, shuffle_list
    │   ├── sound_manager.py      # WAV-тоны из stdlib wave+struct, QSoundEffect
    │   ├── tts_manager.py        # Windows SAPI / macOS say — без зависимостей
    │   ├── streak_manager.py     # Счётчик дней подряд (~/.letapp/streak.json)
    │   ├── license_manager.py    # Генерация и проверка серийных ключей
    │   ├── settings_manager.py   # ~/.letapp/settings.json, дефолты
    │   └── update_checker.py     # QThread → GitHub API → сигнал update_available
    └── gui/
        ├── main_window.py        # QMainWindow + QTabWidget + статусбар
        ├── flashcards_widget.py  # Карточки, SM-2, ★, 🔊, квиз-триггер
        ├── match_widget.py       # Сопоставление (два столбца кнопок)
        ├── typing_widget.py      # Ввод перевода с клавиатуры
        ├── detective_widget.py   # Детектив: угадай термин по определению
        ├── context_widget.py     # Вставь термин в предложение (___ blank)
        ├── favorites_widget.py   # Избранные термины (starred=1)
        ├── boss_widget.py        # Режим на скорость с таймером
        ├── stats_widget.py       # Прогресс, история ошибок, экспорт CSV
        ├── attack_popup.py       # «Термин атакует» — всплывающий попап
        ├── import_dialog.py      # Импорт из CSV/JSON или вставки текста
        ├── quiz_dialog.py        # Мини-тест multiple choice (5 вопросов)
        ├── settings_dialog.py    # Настройки (шрифт, цель, напоминание, атака)
        ├── activation_dialog.py  # Двухшаговая активация: ключ → имя
        ├── reset_dialog.py       # Сброс прогресса / заводские настройки
        └── easter_egg_dialog.py  # Пасхалка по имени пользователя
```

---

## Режимы обучения (все 9)

| # | Вкладка | Виджет | Описание | SM-2 quality |
|---|---------|--------|----------|-------------|
| 1 | 🃏 Карточки | flashcards_widget.py | Показ термина → оцени знание. Анимации, категории, квиз каждые N карточек | 5 (знаю) / 1 (не знаю) |
| 2 | 🔗 Сопоставление | match_widget.py | Два столбца кнопок: термин ↔ перевод. Shake на ошибку | 5 (верное совпадение) |
| 3 | ✍️ Диктант | typing_widget.py | Введи перевод с клавиатуры. До 3 попыток, качество убывает | 5 / 4 / 3 / 0 |
| 4 | 🔍 Детектив | detective_widget.py | Угадай термин по определению. Открывай буквы (−10 очков), −25 за неверный ввод | 5 / 4 / 3 / 2 / 0 |
| 5 | 📖 Контекст | context_widget.py | Предложение с ___ вместо термина. Введи пропущенное слово | нет |
| 6 | ⭐ Избранное | favorites_widget.py | Все starred=1 термины. Поиск, детали, TTS, снять звезду | нет |
| 7 | 👊 Boss Mode | boss_widget.py | 4 варианта ответа, таймер убывает с каждым вопросом. Рекорд в ~/.letapp/highscore.json | нет |
| 8 | 📊 Статистика | stats_widget.py | Карточки прогресса, таблица по категориям, слабые термины, экспорт CSV | нет |
| — | ⚔ Термин атакует | attack_popup.py | По таймеру (N мин) поверх всех окон. Нельзя закрыть без ответа | 5 (верно) / 0 (пропустить) |

---

## Схема базы данных

```sql
CREATE TABLE IF NOT EXISTS terms (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    term_eng TEXT NOT NULL UNIQUE,   -- оригинал (любой язык источника)
    term_rus TEXT NOT NULL,          -- перевод
    definition TEXT,
    category TEXT,
    example  TEXT,
    starred  INTEGER DEFAULT 0       -- избранное
);

CREATE TABLE IF NOT EXISTS progress (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    term_id       INTEGER NOT NULL REFERENCES terms(id) ON DELETE CASCADE,
    last_reviewed DATE,
    ease_factor   REAL    DEFAULT 2.5,
    interval      INTEGER DEFAULT 1,
    repetition    INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    UNIQUE(term_id)
);
```

**Миграции:** `ALTER TABLE ... ADD COLUMN` в `db_manager._init_schema()` в `try/except`.

---

## DBManager — все методы

| Метод | Сигнатура | Описание |
|-------|-----------|----------|
| `is_terms_empty` | `() → bool` | Есть ли записи в terms |
| `import_terms` | `(terms: list[dict]) → None` | INSERT OR IGNORE батч |
| `get_term` | `(term_id: int) → Row\|None` | Один термин по PK |
| `get_all_categories` | `() → list[str]` | DISTINCT categories ORDER BY category |
| `get_terms_by_category` | `(category: str\|None, limit: int=10) → list[Row]` | Случайная выборка |
| `get_random_term` | `(category: str\|None) → Row\|None` | get_terms_by_category limit=1 |
| `get_progress` | `(term_id: int) → Row\|None` | Запись прогресса SM-2 |
| `upsert_progress` | `(term_id, last_reviewed, ease_factor, interval, repetition, correct_count) → None` | INSERT OR UPDATE |
| `get_due_terms` | `(category: str\|None, limit: int=10) → list[int]` | ID терминов к повторению |
| `get_stats` | `() → dict` | {total, learned, avg_ease_factor, today_reviews} |
| `get_stats_by_category` | `() → list[dict]` | [{category, total, learned}] |
| `export_progress_csv` | `(filepath: str) → None` | UTF-8-BOM CSV |
| `get_weak_terms` | `(limit: int=20) → list` | Термины с наименьшим ease_factor |
| `set_starred` | `(term_id: int, starred: bool) → None` | Переключить избранное |
| `get_starred_terms` | `() → list` | Все starred=1 |
| `get_random_terms_for_quiz` | `(exclude_ids: list[int], n: int=3) → list` | Дистракторы для квиза |
| `get_term_with_example` | `(category: str\|None) → Row\|None` | Термин с непустым example |
| `get_term_with_definition` | `(category: str\|None) → Row\|None` | Термин с непустым definition |
| `search_terms` | `(query: str, limit: int=100) → list[Row]` | LIKE %query% по EN/RU |
| `reset_progress` | `() → None` | DELETE FROM progress |
| `close` | `() → None` | Закрыть соединение |

---

## Алгоритм SM-2

`SpacedRepetitionScheduler.review(term_id, quality)` — quality от 0 до 5:
- 5 = отлично, 4 = хорошо, 3 = неплохо, 1-2 = плохо, 0 = совсем не знаю

Интервалы: 1 день → 6 дней → `interval * ease_factor` дней.
`ef = max(1.3, ef + 0.1 - (5-q)*(0.08 + (5-q)*0.02))`

Методы: `review(term_id, quality) → int`, `get_due_terms(category, limit) → list[int]`, `get_stats() → dict`.

---

## Настройки приложения

Файл: `~/.letapp/settings.json`. API: `get_settings() → dict`, `save_settings(data)`.

| Ключ | Тип | Дефолт | Описание |
|------|-----|--------|----------|
| `font_size` | int | 13 | Глобальный размер шрифта (px) |
| `boss_start_ms` | int | 5000 | Начальное время Boss Mode (мс) |
| `quiz_every` | int | 10 | Карточек между квизами |
| `daily_goal` | int | 20 | Цель повторений в день |
| `reminder_enabled` | bool | False | Включить напоминание в трее |
| `reminder_hour` | int | 9 | Час напоминания |
| `reminder_minute` | int | 0 | Минута напоминания |
| `attack_enabled` | bool | False | Включить «Термин атакует» |
| `attack_interval_min` | int | 30 | Интервал между атаками (мин) |

---

## Файлы пользовательского состояния

```
~/.letapp/
├── license.dat      JSON: {key, username, easter_shown}
├── settings.json    JSON: словарь настроек
├── streak.json      JSON: {last_date: "YYYY-MM-DD", streak: int}
└── highscore.json   JSON: {hs: int}  — рекорд Boss Mode
```

---

## Звуковая система

`SoundManager` генерирует WAV через stdlib `wave`+`struct` в `tempfile.mkdtemp()`.
Синглтон: `get_sound_manager() → SoundManager`. API: `SoundManager.play(name: str)`.

| Звук | Ноты | Длительность |
|------|------|-------------|
| `"correct"` | E5→G5 (659, 784 Hz) | 0.13 сек × 2 |
| `"wrong"` | F#3 (185 Hz) | 0.22 сек |
| `"complete"` | C5-E5-G5-C6 | 0.15 сек × 4 |

Graceful fallback если `PyQt6.QtMultimedia` недоступен.

---

## TTS система

`tts_manager.speak(text)` — асинхронно (daemon thread), без возврата.

- **Windows**: PowerShell + `System.Speech`, выбирает `en-*` голос
- **macOS**: `say -v <voice>` пробует: Samantha, Alex, Tom, Karen, Daniel, Kate
- **Linux/другие**: тихо игнорируется

---

## Обновление (update checker)

`UpdateChecker(current_version, repo, parent)` наследует `QThread`.
Сигнал: `update_available(current: str, latest: str)`.
URL: `https://api.github.com/repos/{repo}/releases/latest`.
Сравнивает `_parse_version("v1.2.3") → (1, 2, 3)`. Ошибки поглощает молча.

---

## Активация (серийные ключи)

Структура: `XXXXX-XXXXX-XXXXX-XXXXX` (20 символов).
- символы 0-14: случайный seed; символы 15-19: checksum
- `_hash_seed` — polynomial rolling hash с солью `_SECRET`
- **Поменяй соль при форке** — чужие генераторы не подойдут

Хранение: `~/.letapp/license.dat`.

Поток:
1. `is_activated()` → `ActivationDialog` если нет
2. `is_stefan(username)` → `EasterEggDialog` (один раз, флаг `easter_shown`)

---

## Паттерны анимаций

**Shake** (match_widget, typing_widget, attack_popup, detective_widget):
```python
anim = QPropertyAnimation(widget, b"pos"); anim.setDuration(300)
anim.setKeyValueAt(0.0, orig); anim.setKeyValueAt(0.2, QPoint(orig.x()-7, orig.y()))
anim.setKeyValueAt(0.4, QPoint(orig.x()+7, orig.y()))  # ...
anim.setEasingCurve(QEasingCurve.Type.Linear); anim.start()
# Хранить в self._shake_anim — иначе GC удалит раньше времени
```

**Card fade-out/in** (flashcards_widget):
- Fade-out: `QGraphicsOpacityEffect` + `QPropertyAnimation(b"opacity")`, 100ms InQuad
- **ВАЖНО**: `setGraphicsEffect(None)` ДО обновления контента → иначе QPainter double-begin
- Fade-in: 180ms OutQuad, opacity 0→1

**Flash-then-navigate**: `setStyleSheet(color)` → `QTimer.singleShot(220)` → `_next_term_animated()`

---

## Система цветов категорий

```python
_CAT_COLORS = {  # (text_color, background, border/accent)
    "Contract Law":      ("#ffcb6b", "#241a08", "#c89020"),
    "Criminal Law":      ("#f07178", "#240c12", "#b03040"),
    "Property Law":      ("#c3e88d", "#101e0a", "#4a9030"),
    "Corporate Law":     ("#c792ea", "#1c0e28", "#9050c0"),
    "Civil Procedure":   ("#89ddff", "#081820", "#3090b8"),
    "International Law": ("#82aaff", "#0c1428", "#4060c0"),
    "Latin Terms":       ("#e8c060", "#201808", "#b08020"),
}
```

Применяется к: тегу категории (`QLabel#categoryTag`) и левой рамке карточки.

---

## Логика триггера квиза

В `flashcards_widget._rate()`: каждые `quiz_every` карточек (из settings).
`QTimer.singleShot(420, self._launch_quiz)` — ждёт flash-анимацию.
`QuizDialog` получает ID последних `quiz_every` карточек + дистракторы из БД.

---

## Тёмная тема

`build_dark_stylesheet(font_size: int = 13) → str` в `src/_stylesheet.py`.
`app.setStyleSheet(build_dark_stylesheet(font_size))` — глобально.
Перестраивается без перезапуска при изменении font_size.

Палитра: фон `#1a1c2e`, поверхность `#252840`, текст `#eeffff`, акцент `#82aaff`.

Именованные объекты: `card`, `matchBtn`, `knowBtn`, `dontKnowBtn`, `categoryTag`,
`termLabel`, `translationLabel`, `definitionLabel`, `exampleLabel`, `feedbackLabel`,
`statCard`, `statValue`, `statTitle`, `colHeader`.

---

## Точка входа и PyInstaller

```python
if getattr(sys, "frozen", False):
    _ROOT = sys._MEIPASS        # read-only!
    _USER_DATA = Path.home() / ".letapp"
    DB_PATH = str(_USER_DATA / "legal_english.db")  # writable
else:
    _ROOT = os.path.join(BASE_DIR, "..")
    DB_PATH = os.path.join(_ROOT, "data", "legal_english.db")
```

Команды сборки:
```bash
# Windows
pyinstaller --onefile --windowed --name "AppName" \
  --add-data "data/terms.json;data" \
  --add-data "src/database/schema.sql;src/database" \
  --add-data "assets;assets" run.py

# macOS (разделитель : вместо ;)
pyinstaller --windowed --name "AppName" \
  --add-data "data/terms.json:data" \
  --add-data "src/database/schema.sql:src/database" \
  --add-data "assets:assets" run.py
```

---

## GitHub Actions (автосборка)

Триггер: push в master/main + теги `v*`.
- `build-windows` → `.exe`; `build-macos` → ad-hoc codesign → `.dmg`
- `release` (только при теге) → GitHub Release

```bash
git tag v1.3.0 && git push origin v1.3.0
```

---

## Добавление нового режима обучения

1. Создать `src/gui/my_widget.py` (наследник `QWidget`)
2. `main_window.py`: `self.my = MyWidget(self.db, self.scheduler)`
3. `tabs.addTab(self.my, "🆕 Название")`
4. При переключении — добавить в `_on_tab_changed` через `current is self.my`

## Адаптация под новую предметную область

1. Заменить `data/terms.json` — структура: `[{term_eng, term_rus, definition, category, example}]`
2. Переименовать `term_eng`/`term_rus` в schema.sql
3. Обновить список триггеров пасхалки в `license_manager.is_stefan()`
4. Поменять соль `_SECRET` в `license_manager.py`
5. Обновить `_CAT_COLORS` в `flashcards_widget.py`
6. Обновить цветовую схему в `_stylesheet.py`
