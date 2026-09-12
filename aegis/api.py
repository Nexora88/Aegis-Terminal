from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .db import add_event, events, init_db
from .decision import assess
from .integrity import sha256_file
from .monitor import interfaces, processes, snapshot

app = FastAPI(title='AEGIS TERMINAL', version='0.2.0')
init_db()


class EventPayload(BaseModel):
    title: str
    severity: str = 'INFO'
    source: str = 'dashboard'
    details: str = ''


@app.get('/', response_class=HTMLResponse)
def home():
    return (Path(__file__).parent / 'web' / 'index.html').read_text(encoding='utf-8')


@app.get('/api/health')
def health():
    return {'status': 'online', 'service': 'AEGIS TERMINAL', 'version': app.version}


@app.get('/api/system')
def system():
    return snapshot()


@app.get('/api/summary')
def summary():
    s = snapshot()
    r = assess(s)
    return {'system': s, 'assessment': r}


@app.get('/api/processes')
def proc():
    return processes()


@app.get('/api/interfaces')
def net():
    return interfaces()


@app.get('/api/events')
def ev():
    return events()


@app.post('/api/events')
def create_event(payload: EventPayload):
    event_id = add_event(payload.title, payload.severity.upper(), payload.source, payload.details)
    return {'id': event_id, 'status': 'recorded'}


@app.get('/api/assessment')
def risk():
    return assess(snapshot())


@app.post('/api/integrity')
def integrity(payload: dict):
    try:
        return sha256_file(payload.get('path', ''))
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
