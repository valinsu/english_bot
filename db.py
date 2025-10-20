import sqlite3

DB_PATH = "bot_data.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            user_id INTEGER PRIMARY KEY,
            username TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS sent_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT
        )
        """)
        conn.commit()

def add_subscriber(user_id, username):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO subscribers (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()

def get_all_subscribers():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, username FROM subscribers")
        return cur.fetchall()

def save_sent_message(user_id, message):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO sent_messages (user_id, message) VALUES (?, ?)", (user_id, message))
        conn.commit()

def is_message_sent(user_id, message):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM sent_messages WHERE user_id=? AND message=?", (user_id, message))
        return cur.fetchone() is not None
