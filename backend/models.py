from backend.db_setup import get_db_connection

class User:
    @staticmethod
    def get_default_user_id():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = 'friday_user'")
        row = cursor.fetchone()
        conn.close()
        if row:
            return row["id"]
        return 1

class Reminder:
    @staticmethod
    def get_all(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, text, time, date, priority, status, created_at FROM reminders WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def create(user_id, text, time, date="", priority="medium"):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (user_id, text, time, date, priority) VALUES (?, ?, ?, ?, ?)",
            (user_id, text, time, date, priority)
        )
        new_id = cursor.lastrowid
        conn.commit()
        cursor.execute(
            "SELECT id, text, time, date, priority, status, created_at FROM reminders WHERE id = ?",
            (new_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def delete(reminder_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def complete(reminder_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE reminders SET status = 'completed' WHERE id = ?", (reminder_id,))
        conn.commit()
        conn.close()
        return True

class InteractionLog:
    @staticmethod
    def log(user_id, command, response, response_type):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO interaction_log (user_id, command, response, type) VALUES (?, ?, ?, ?)",
            (user_id, command, response, response_type)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_all(user_id, limit=50):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, command, response, type, timestamp FROM interaction_log WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def clear(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM interaction_log WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True

class Settings:
    @staticmethod
    def get_by_user(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT theme, voice_enabled, volume, rate, weather_city FROM settings WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {
            "theme": "dark",
            "voice_enabled": 1,
            "volume": 1.0,
            "rate": 190,
            "weather_city": "Mumbai"
        }

    @staticmethod
    def update(user_id, theme, voice_enabled, volume, rate, weather_city):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE settings 
               SET theme = ?, voice_enabled = ?, volume = ?, rate = ?, weather_city = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE user_id = ?""",
            (theme, int(voice_enabled), float(volume), int(rate), weather_city, user_id)
        )
        conn.commit()
        cursor.execute(
            "SELECT theme, voice_enabled, volume, rate, weather_city FROM settings WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}
