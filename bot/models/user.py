from sqlite3 import connect

from . import DATABASE
TABLE = "user_table"

# schema
with connect(DATABASE) as conn:
    conn.execute(
        f"""CREATE TABLE IF NOT EXISTS {TABLE} (
            user_id TEXT PRIMARY KEY
        )"""
    )

class User:
    pass
