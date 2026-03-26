CREATE TABLE IF NOT EXISTS terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term_eng TEXT NOT NULL UNIQUE,
    term_rus TEXT NOT NULL,
    definition TEXT,
    category TEXT,
    example TEXT,
    starred INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term_id INTEGER NOT NULL REFERENCES terms(id) ON DELETE CASCADE,
    last_reviewed DATE,
    ease_factor REAL DEFAULT 2.5,
    interval INTEGER DEFAULT 1,
    repetition INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    UNIQUE(term_id)
);
