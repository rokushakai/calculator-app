DROP TABLE IF EXISTS calculations;

CREATE TABLE calculations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  expression TEXT NOT NULL,
  result TEXT NOT NULL,
  memo TEXT
);