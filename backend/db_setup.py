import os
import sqlite3
from pathlib import Path

# Database path in the root folder
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "friday.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_column(conn, table_name, column_name, column_definition):
    columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table_name})")]
    if column_name not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create reminders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        time TEXT NOT NULL,
        date TEXT DEFAULT '',
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)
    ensure_column(conn, "reminders", "date", "TEXT DEFAULT ''")
    ensure_column(conn, "reminders", "priority", "TEXT DEFAULT 'medium'")

    # Create interaction_log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interaction_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        command TEXT NOT NULL,
        response TEXT NOT NULL,
        type TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    # Create settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        theme TEXT DEFAULT 'dark',
        voice_enabled INTEGER DEFAULT 1,
        volume REAL DEFAULT 1.0,
        rate INTEGER DEFAULT 190,
        weather_city TEXT DEFAULT 'Mumbai',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    # Seed default user if not exists
    cursor.execute("SELECT id FROM users WHERE username = 'friday_user'")
    user = cursor.fetchone()
    if not user:
        cursor.execute(
            "INSERT INTO users (username, name) VALUES (?, ?)",
            ("friday_user", "User")
        )
        user_id = cursor.lastrowid
        # Seed default settings
        cursor.execute(
            "INSERT INTO settings (user_id, theme, voice_enabled, volume, rate, weather_city) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, "dark", 1, 1.0, 190, "Mumbai")
        )
    else:
        user_id = user["id"]
        # Double check settings exist
        cursor.execute("SELECT id FROM settings WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO settings (user_id, theme, voice_enabled, volume, rate, weather_city) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, "dark", 1, 1.0, 190, "Mumbai")
            )

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
