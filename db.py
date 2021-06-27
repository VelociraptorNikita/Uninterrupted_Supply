import sqlite3


def open_db() -> sqlite3.Connection:
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    cur.executescript('''
CREATE TABLE IF NOT EXISTS purveyor (
    id    INTEGER PRIMARY KEY,
    name  TEXT    NOT NULL,
    price REAL,
    time  TEXT,
    x     REAL,
    y     REAL
);

CREATE TABLE IF NOT EXISTS purveyance (
    id          INTEGER PRIMARY KEY,
    weight      REAL    NOT NULL,
    shipment    TEXT,
    arrival     TEXT,
    production  TEXT,
    type        TEXT,
    id_purveyor INTEGER NOT NULL,
    FOREIGN KEY (id_purveyor)
    REFERENCES purveyor (id) 
);
''')
    return con


def get_data(table: str) -> {}:
    with open_db() as con:
        cur = con.cursor().execute(f'SELECT * FROM {table}')
        data = [list(line) for line in cur.fetchall()]
        headers = list(next(zip(*cur.description)))
        return {'headers': headers, 'data': data}


def set_data(table: str, data: list) -> None:
    with open_db() as con:
        cur = con.cursor()
        column_count = len(data[0])
        for line in data:
            cur.execute(f'INSERT INTO {table} VALUES (?{", ?" * (column_count - 1)})', line)
