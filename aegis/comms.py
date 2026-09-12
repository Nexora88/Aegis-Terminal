"""Local Aegis secure-room messaging.

Messages are encrypted before they are persisted locally. This is a small
single-node room, not a network interception system or a replacement for a
reviewed production E2EE protocol.
"""

from datetime import datetime, timezone
from pathlib import Path
import os
import sqlite3

from cryptography.fernet import Fernet

from .config import DB_PATH

KEY_PATH = Path(DB_PATH).with_name('aegis-comms.key')


def _key() -> bytes:
    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not KEY_PATH.exists():
        KEY_PATH.write_bytes(Fernet.generate_key())
        try:
            os.chmod(KEY_PATH, 0o600)
        except OSError:
            pass
    return KEY_PATH.read_bytes().strip()


def init_comms():
    with sqlite3.connect(DB_PATH) as c:
        c.execute('CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT,sender TEXT NOT NULL,room TEXT NOT NULL,ciphertext TEXT NOT NULL,created_at TEXT NOT NULL)')


def send_message(sender: str, room: str, message: str) -> dict:
    sender = (sender or 'AEGIS-OPERATOR').strip()[:48]
    room = (room or 'COMMAND').strip()[:48]
    message = message.strip()
    if not message:
        raise ValueError('Message cannot be empty')
    token = Fernet(_key()).encrypt(message.encode('utf-8')).decode('ascii')
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute('INSERT INTO messages(sender,room,ciphertext,created_at) VALUES(?,?,?,?)',(sender,room,token,now))
        c.commit()
        return {'id': cur.lastrowid, 'sender': sender, 'room': room, 'message': message, 'created_at': now, 'encrypted_at_rest': True}


def messages(room: str = 'COMMAND', limit: int = 50) -> list[dict]:
    with sqlite3.connect(DB_PATH) as c:
        c.row_factory = sqlite3.Row
        rows = c.execute('SELECT * FROM messages WHERE room=? ORDER BY id DESC LIMIT ?',(room, min(max(limit,1),100))).fetchall()
    cipher = Fernet(_key())
    out=[]
    for row in reversed(rows):
        try:
            text = cipher.decrypt(row['ciphertext'].encode('ascii')).decode('utf-8')
        except Exception:
            text = '[unable to decrypt locally]'
        out.append({'id': row['id'], 'sender': row['sender'], 'room': row['room'], 'message': text, 'created_at': row['created_at'], 'encrypted_at_rest': True})
    return out
