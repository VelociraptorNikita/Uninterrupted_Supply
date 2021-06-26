import sqlite3


def get_data(who: str) -> dict:
    with sqlite3.connect('data.db') as con:
        cur = con.cursor().execute('SELECT * FROM ' + who)
        data = [list(line) for line in cur.fetchall()]
        headers = list(next(zip(*cur.description)))
        return {'headers': headers, 'data': data}
