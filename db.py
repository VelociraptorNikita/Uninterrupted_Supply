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
    material INTEGER,
    periodicity INTEGER,
    discharge INTEGER,
    x     INTEGER,
    y     INTEGER
);
''')
    con.commit()
    # 
    return con


def get_data(table: str) -> dict:
    with open_db() as con:
        cur = con.cursor().execute(f'SELECT * FROM {table}')
        data = [list(line) for line in cur.fetchall()]
        headers = list(next(zip(*cur.description)))
        return {'headers': headers, 'data': data}

def clear(table: str) -> None:
    with open_db() as con:
        cur = con.cursor().execute(f'DELETE FROM {table}')
 

def set_data(table: str, data: list) -> None:
    with open_db() as con:
        cur = con.cursor()
        column_count = len(data)
        cur.execute(f'INSERT INTO {table} VALUES (?{", ?" * (column_count - 1)})', data)
        con.commit()
        # cur.execute(f'INSERT INTO {table} VALUES (?{", ?" * (column_count - 1)})', line)
