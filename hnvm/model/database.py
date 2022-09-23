from sqlite3 import connect

DB_URI = "db.sqlite3"

def connect_db():
    return connect(DB_URI)
