from .database import connect_db

TABLE = "user_table"

# schema
with connect_db() as conn:
    conn.execute(
        f"""CREATE TABLE IF NOT EXISTS {TABLE} (
            user_id TEXT PRIMARY KEY
        )"""
    )

class User:
    pass
