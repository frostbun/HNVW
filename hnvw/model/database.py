from sqlite3 import connect

DB_URL = "db.sqlite3"

def connect_db():
    return connect(DB_URL)
