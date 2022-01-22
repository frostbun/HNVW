from sqlite3 import connect

from configs import DATABASE
TABLE = "guild_table"

# schema
with connect(DATABASE) as conn:
    conn.execute(
        f"""CREATE TABLE IF NOT EXISTS {TABLE} (
            guild_id TEXT PRIMARY KEY,
            auto_shuffle INTEGER NOT NULL,
            auto_loop INTEGER NOT NULL
        )"""
    )

class Guild:
    pass
