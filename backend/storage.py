import sqlite3

DATABASE_NAME = "backend_storage.db"

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meldingen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tijdstip TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            gebruiker_id TEXT,
            status TEXT,
            locatie TEXT
        )
    """)
    conn.commit()
    conn.close()
