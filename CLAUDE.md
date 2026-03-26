# Desktop Vocabulary Trainer — архитектурный справочник

Этот файл описывает архитектуру приложения и все ключевые решения.
Используй его как отправную точку при создании нового тренажёра словаря
на любую тематику (медицина, IT, иностранный язык, профессиональные термины и т.д.).

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
├── run.py                        # Точка входа (добавляет root в sys.path)
├── data/
│   └── terms.json                # Исходные данные (импортируются в БД при старте)
├── assets/                       # Иконки, изображения
├── scripts/
│   ├── keygen.py                 # Генератор серийных ключей (для разработчика)
│   ├── reset_app.py              # Сброс состояния для тестирования
│   ├── build_windows.bat         # Локальная сборка exe
│   └── build_macos.sh            # Локальная сборка app
├── .github/
│   └── workflows/
│       └── build.yml             # GitHub Actions: Windows + macOS → Release
└── src/
    ├── main.py                   # QApplication, тема, активация, streak, запуск окна
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
    │   └── license_manager.py    # Генерация и проверка серийных ключей
    └── gui/
        ├── main_window.py        # QMainWindow + QTabWidget
        ├── flashcards_widget.py  # Карточки, SM-2, ★, 🔊, квиз-триггер
        ├── match_widget.py       # Сопоставление (два столбца кнопок)
        ├── typing_widget.py      # Ввод перевода с клавиатуры
        ├── favorites_widget.py   # Избранные термины (starred=1)
        ├── boss_widget.py        # Режим на скорость с таймером
        ├── stats_widget.py       # Прогресс, история ошибок, экспорт CSV
        ├── import_dialog.py      # Импорт из CSV/JSON или вставки текста
        ├── quiz_dialog.py        # Мини-тест multiple choice (5 вопросов)
        ├── activation_dialog.py  # Двухшаговая активация: ключ → имя
        └── easter_egg_dialog.py  # Пасхалка по имени пользователя
```

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

**Миграции:** при добавлении новых колонок — `ALTER TABLE ... ADD COLUMN` в
`db_manager._init_schema()`, обёрнутый в `try/except` (игнорирует повторное добавление).

---

## Алгоритм SM-2

`SpacedRepetitionScheduler.review(term_id, quality)` — качество от 0 до 5:
- 5 = отлично знаю
- 4 = знаю с небольшим усилием
- 1-3 = знаю плохо
- 0 = не знаю совсем

Интервалы: 1 день → 6 дней → `interval * ease_factor` дней.
ease_factor меняется по формуле: `ef = ef + 0.1 - (5-q)*(0.08 + (5-q)*0.02)`, минимум 1.3.

---

## Серийные ключи (офлайн-активация)

Структура: 20 символов → `XXXXX-XXXXX-XXXXX-XXXXX`
- символы 0-14: случайный seed
- символы 15-19: checksum = `encode(_hash_seed(seed))`

`_hash_seed` — polynomial rolling hash с встроенной солью `_SECRET`.
Соль менять при форке, чтобы сторонние генераторы не подходили.

Хранение: `~/.letapp/license.dat` (JSON: `{key, username}`).
Тестирование: `python scripts/reset_app.py` удаляет все файлы состояния.

Пасхалка: `license_manager.is_stefan(username)` — список имён-триггеров,
показывает `easter_egg_dialog.py` с картинкой из `assets/` и случайным звуком.

---

## Звуки (без зависимостей)

`sound_manager.py` генерирует WAV-тоны через stdlib `wave` + `struct` во временную
папку при старте, воспроизводит через `QSoundEffect`. Три тона: correct, wrong, complete.

`tts_manager.py` — озвучка текста:
- Windows: PowerShell + `System.Speech`, явно выбирает `en-*` голос
- macOS: `say -v Samantha` (перебирает список английских голосов)
- Другие платформы: молча игнорируется

---

## Тёмная тема

Вся тема — одна строка `DARK_STYLESHEET` в `src/main.py`.
Применяется глобально через `app.setStyleSheet(DARK_STYLESHEET)`.

Именованные объекты (через `setObjectName`):
`card`, `matchBtn`, `knowBtn`, `dontKnowBtn`, `categoryTag`,
`termLabel`, `translationLabel`, `definitionLabel`, `statCard`, `statValue`.

Чередование строк таблицы: задавать `alternate-background-color` в stylesheet,
иначе Qt возьмёт системный белый цвет.

---

## Точка входа и PyInstaller

`run.py` добавляет корень проекта в `sys.path` — единственный способ запускать
и как `python run.py`, и внутри PyInstaller-бандла.

В `src/main.py` пути к данным резолвятся через:
```python
if getattr(sys, "frozen", False):
    _ROOT = sys._MEIPASS   # PyInstaller распаковывает сюда
else:
    _ROOT = os.path.join(BASE_DIR, "..")
```

Импорты оборачиваются в `try/except ImportError` для поддержки обоих режимов запуска.

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

`.github/workflows/build.yml`:
- Триггер на push в master/main и на теги `v*`
- `build-windows` (windows-latest) → `LegalEnglishTrainer.exe`
- `build-macos` (macos-latest) → `.app` → `hdiutil` → `.dmg`
- `release` (только при теге) — создаёт GitHub Release с обоими файлами

Выпуск новой версии:
```bash
git tag v1.2.0
git push origin v1.2.0
```

---

## Добавление нового режима обучения

1. Создать `src/gui/my_widget.py` (наследник `QWidget`)
2. Добавить в `main_window.py`: `self.my = MyWidget(self.db, self.scheduler)`
3. `tabs.addTab(self.my, "🆕 Название")`
4. Если нужно обновление при переключении — добавить в `_on_tab_changed`

## Адаптация под новую предметную область

1. Заменить `data/terms.json` — структура: `[{term_eng, term_rus, definition, category, example}]`
2. Переименовать `term_eng`/`term_rus` в schema.sql под нужные языки
3. Обновить список триггеров пасхалки в `license_manager.is_stefan()`
4. Поменять соль `_SECRET` в `license_manager.py`
5. Обновить `DARK_STYLESHEET` под нужную цветовую схему
