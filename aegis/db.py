from datetime import datetime, timezone
import sqlite3

from .config import DB_BACKEND, DB_PATH, DATABASE_URL


def _pg_connect():
    import psycopg
    return psycopg.connect(DATABASE_URL)


def init_db():
    if DB_BACKEND == "postgresql":
        with _pg_connect() as c:
            with c.cursor() as cur:
                cur.execute('CREATE TABLE IF NOT EXISTS events(id BIGSERIAL PRIMARY KEY,title TEXT NOT NULL,severity TEXT NOT NULL,source TEXT NOT NULL,details TEXT,created_at TIMESTAMPTZ NOT NULL)')
            c.commit()
        return
    with sqlite3.connect(DB_PATH) as c:
        c.execute('CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,severity TEXT,source TEXT,details TEXT,created_at TEXT)')


def add_event(title, severity, source, details):
    now = datetime.now(timezone.utc)
    if DB_BACKEND == "postgresql":
        with _pg_connect() as c:
            with c.cursor() as cur:
                cur.execute('INSERT INTO events(title,severity,source,details,created_at) VALUES(%s,%s,%s,%s,%s) RETURNING id', (title, severity, source, details, now))
                event_id = cur.fetchone()[0]
            c.commit()
            return event_id
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute('INSERT INTO events(title,severity,source,details,created_at) VALUES(?,?,?,?,?)', (title, severity, source, details, now.isoformat()))
        c.commit()
        return cur.lastrowid


def events(limit=50):
    limit = max(1, min(int(limit), 1000))
    if DB_BACKEND == "postgresql":
        with _pg_connect() as c:
            with c.cursor() as cur:
                cur.execute('SELECT id,title,severity,source,details,created_at FROM events ORDER BY id DESC LIMIT %s', (limit,))
                rows = cur.fetchall()
                return [dict(zip(("id", "title", "severity", "source", "details", "created_at"), row)) for row in rows]
    with sqlite3.connect(DB_PATH) as c:
        c.row_factory = sqlite3.Row
        return [dict(x) for x in c.execute('SELECT * FROM events ORDER BY id DESC LIMIT ?', (limit,)).fetchall()]
