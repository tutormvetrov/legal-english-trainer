# Legal English Trainer

Десктопное приложение для изучения 1000 юридических терминов (английский–русский)
с использованием интервального повторения (алгоритм SM-2).

## Возможности

| Вкладка | Описание |
|---|---|
| **Карточки** | Показ термина, оценка «Знаю / Не знаю», SM-2 |
| **Сопоставление** | Соединить термин с переводом (3–10 пар) |
| **Списывание** | Ввести перевод с клавиатуры |
| **Статистика** | Прогресс по категориям, экспорт CSV |

**Категории терминов:**
- Contract Law (Договорное право) — 159
- Criminal Law (Уголовное право) — 151
- Corporate Law (Корпоративное право) — 147
- International Law (Международное право) — 148
- Civil Procedure (Гражданский процесс) — 158
- Property Law (Имущественное право) — 99
- Latin Terms (Латинские термины) — 138

## Требования

- Python 3.11+
- PyQt6

## Быстрый старт

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Запустить приложение
python -m src.main
```

База данных и импорт терминов создаются автоматически при первом запуске.

## Структура проекта

```
legal_english_trainer/
├── data/
│   ├── terms.json          # 1000 терминов
│   └── legal_english.db    # SQLite (создаётся автоматически)
├── src/
│   ├── main.py             # Точка входа
│   ├── database/           # DBManager, schema.sql
│   ├── models/             # Term dataclass
│   ├── algorithms/         # SM-2 алгоритм
│   ├── gui/                # PyQt6 виджеты
│   └── utils/              # Вспомогательные функции
└── scripts/
    ├── generate_terms.py   # Генератор terms.json
    ├── populate_db.py      # Ручной импорт в БД
    ├── build_windows.bat
    └── build_macos.sh
```

## Сборка в исполняемый файл

### Windows

```bat
scripts\build_windows.bat
```

Результат: `dist\LegalEnglishTrainer.exe`

### macOS

```bash
chmod +x scripts/build_macos.sh
./scripts/build_macos.sh
```

Результат: `dist/LegalEnglishTrainer.app`

> При первом запуске на macOS: правая кнопка мыши → «Открыть» (обход Gatekeeper).

> Если иконок `assets/legal.ico` / `assets/legal.icns` нет — параметр `--icon`
> автоматически пропускается. Добавьте иконки в папку `assets/` перед сборкой.

## Алгоритм SM-2

Каждый термин имеет:
- **ease_factor** — коэффициент лёгкости (мин. 1.3, по умолчанию 2.5)
- **interval** — интервал до следующего повторения (дни)
- **repetition** — счётчик успешных повторений

При оценке «Знаю» (quality ≥ 3) интервал растёт; при «Не знаю» — сбрасывается до 1 дня.
