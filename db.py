import sqlite3

def get_connection():
    return sqlite3.connect("fitness.db")

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise TEXT NOT NULL,
        sets INTEGER,
        reps INTEGER,
        weight REAL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
