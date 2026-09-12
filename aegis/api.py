from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .antivirus import scan_file, scanner_overview
from .crypto import message_demo
from .db import add_event, events, init_db
from .decision import assess
from .integrity import sha256_file
from .monitor import interfaces, processes, snapshot
from .tracking import tracks

app = FastAPI(title='AEGIS TERMINAL', version='0.4.0')
init_db()


class EventPayload(BaseModel):
    title: str
    severity: str = 'INFO'
    source: str = 'dashboard'
    details: str = ''


class ScanPayload(BaseModel):
    path: str


@app.get('/', response_class=HTMLResponse)
def home():
    return (Path(__file__).parent / 'web' / 'index.html').read_text(encoding='utf-8')


@app.get('/api/health')
def health():
    return {'status': 'online', 'service': 'AEGIS TERMINAL', 'version': app.version, 'brand': 'NEXORA / AHMET EYMEN BAKRAÇ'}


@app.get('/api/system')
def system():
    return snapshot()


@app.get('/api/summary')
def summary():
    s = snapshot()
    r = assess(s)
    return {'system': s, 'assessment': r, 'scanner': scanner_overview()}


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


@app.get('/api/tracking')
def tracking():
    return tracks()


@app.get('/api/comms/demo')
def comms_demo():
    return message_demo()


@app.get('/api/security/scanner')
def security_scanner():
    return scanner_overview()


@app.post('/api/security/scan')
def security_scan(payload: ScanPayload):
    try:
        result = scan_file(payload.path)
        if result['verdict'] == 'MALICIOUS':
            add_event('Malware detection', 'HIGH', 'malware-scanner', result['path'])
        elif result['verdict'] == 'REVIEW':
            add_event('File requires security review', 'MEDIUM', 'malware-scanner', result['path'])
        return result
    except FileNotFoundError as exc:
        raise HTTPException(404, f'File not found: {exc}') from exc
    except PermissionError as exc:
        raise HTTPException(403, f'Permission denied: {exc}') from exc


@app.post('/api/integrity')
def integrity(payload: dict):
    try:
        return sha256_file(payload.get('path', ''))
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
