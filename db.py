import sqlite3
import os

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Updated logs table with confidence column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            username TEXT,
            action TEXT,
            details TEXT,
            confidence REAL DEFAULT 0.0
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database ready! Logs table created/updated at: {DB_PATH}")

def get_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()
    return logs

def add_log(username, action, details=""):
    """General log function (optional)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (username, action, details) VALUES (?, ?, ?)",
        (username, action, details)
    )
    conn.commit()
    conn.close()

def add_detection_log(username, action, details, confidence=0.0):
    """Special function for detection logs with confidence"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (username, action, details, confidence) VALUES (?, ?, ?, ?)",
        (username, action, details, confidence)
    )
    conn.commit()
    conn.close()

# Automatically create table when this file is imported
create_table()

if __name__ == "__main__":
    create_table()