import sqlite3
from datetime import datetime,timezone
from .config import DB_PATH

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute('CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,severity TEXT,source TEXT,details TEXT,created_at TEXT)')

def add_event(title,severity,source,details):
    with sqlite3.connect(DB_PATH) as c:
        cur=c.execute('INSERT INTO events(title,severity,source,details,created_at) VALUES(?,?,?,?,?)',(title,severity,source,details,datetime.now(timezone.utc).isoformat())); c.commit(); return cur.lastrowid

def events(limit=50):
    with sqlite3.connect(DB_PATH) as c:
        c.row_factory=sqlite3.Row
        return [dict(x) for x in c.execute('SELECT * FROM events ORDER BY id DESC LIMIT ?',(limit,)).fetchall()]
