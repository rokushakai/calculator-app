DROP TABLE IF EXISTS calculations;

CREATE TABLE calculations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expression TEXT NOT NULL,
    result REAL NOT NULL,
    memo TEXT
);