import sqlite3
import os
from datetime import datetime

DB_PATH = "podcast_studio.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS podcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            filename TEXT,
            script TEXT,
            audience TEXT,
            file_size TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_podcast_data(title, filename, script, audience, file_size):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO podcasts (title, filename, script, audience, file_size)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, filename, script, audience, file_size))
    conn.commit()
    conn.close()

def get_podcast_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM podcasts ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    history = [dict(row) for row in rows]
    conn.close()
    return history

def remove_podcast_entry(podcast_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM podcasts WHERE id = ?', (podcast_id,))
    conn.commit()
    conn.close()
