# Legal English Trainer — контекст проекта

## Архитектура

```
src/main.py               — QApplication, тёмная тема, инициализация БД
src/database/db_manager.py — Единственный класс для работы с SQLite
src/database/schema.sql   — DDL для таблиц terms и progress
src/models/term.py        — Dataclass Term (from_row из sqlite3.Row)
src/algorithms/spaced_repetition.py — SM-2 через DBManager
src/utils/helpers.py      — shuffle_list, answers_match (нечувств. к регистру)
src/gui/main_window.py    — QMainWindow + QTabWidget (4 вкладки)
src/gui/flashcards_widget.py — Карточки + SM-2 оценка
src/gui/match_widget.py   — Сопоставление терминов (кнопки)
src/gui/typing_widget.py  — Ввод перевода, 3 попытки
src/gui/stats_widget.py   — Статистика + экспорт CSV
```

## Ключевые соглашения

- **Язык UI**: весь интерфейс на русском (строки прямо в коде)
- **Тема**: тёмная, определена в `src/main.py` константой `DARK_STYLESHEET`
- **БД**: одно подключение на сессию через `DBManager`; `row_factory = sqlite3.Row`
- **SM-2**: вызывается через `SpacedRepetitionScheduler.review(term_id, quality)`
- **Запуск**: `python -m src.main` из корня проекта
- **Данные**: `data/terms.json` — источник терминов; БД создаётся при старте

## Расширение

- Добавить термины: дописать батч в `scripts/generate_terms.py`, запустить скрипт
- Новая вкладка: создать виджет в `src/gui/`, добавить в `main_window.py`
- Сборка: `scripts/build_windows.bat` или `scripts/build_macos.sh`
