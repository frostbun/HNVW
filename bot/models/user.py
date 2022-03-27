from .database import Database

TABLE = "user_table"

# schema
with Database() as conn:
    conn.execute(
        f"""CREATE TABLE IF NOT EXISTS {TABLE} (
            user_id TEXT PRIMARY KEY
        )"""
    )

class User:
    pass
