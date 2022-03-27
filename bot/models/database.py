from sqlite3 import connect

class Database:
    URI = "db.sqlite3"

    def __enter__(self):
        self.conn = connect(self.URI)
        return self.conn

    def __exit__(self, type, value, traceback):
        if type is None: self.conn.commit()
        self.conn.close()
        return True
