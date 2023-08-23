import sqlite3

class Database:
    def __init__(self, db_file='ProjectHealth.db'):
        self.db_file = db_file

    def connect(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mac TEXT NOT NULL,
                steps INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            );
        """)

    def insert_data(self, mac, steps, timestamp):
        self.cursor.execute("""
            INSERT INTO Steps (mac, steps, timestamp)
            VALUES (?, ?, ?);
        """, (mac, steps, timestamp))

        self.conn.commit()
