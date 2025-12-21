import sqlite3
from datetime import datetime
import os

DB_PATH = "data/engine.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    curr = conn.cursor()
    curr.execute('''CREATE TABLE IF NOT EXISTS processed_trips 
                 (url TEXT PRIMARY KEY, title TEXT, substance TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def is_processed(url):
    conn = sqlite3.connect(DB_PATH)
    curr = conn.cursor()
    curr.execute("SELECT 1 FROM processed_trips WHERE url = ?", (url,))
    exists = curr.fetchone() is not None
    conn.close()
    return exists

def mark_as_processed(url, title, substance):
    conn = sqlite3.connect(DB_PATH)
    curr = conn.cursor()
    curr.execute("INSERT INTO processed_trips VALUES (?, ?, ?, ?)", 
                 (url, title, substance, datetime.now()))
    conn.commit()
    conn.close()