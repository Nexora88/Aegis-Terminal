from contextlib import asynccontextmanager
from pathlib import Path
import asyncio

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from .antivirus import scan_file, scanner_overview
from .comms import init_comms, messages, send_message
from .crypto import message_demo
from .db import add_event, events, init_db
from .decision import assess
from .integrity import sha256_file
from .monitor import interfaces, processes, snapshot
from .tracking import tracks
from .telemetry import collector_loop, manager
from .log_export import json_line, emit_syslog

WEB_DIR = Path(__file__).parent / 'web'


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_comms()
    stop_event = asyncio.Event()
    collector = asyncio.create_task(collector_loop(stop_event))
    app.state.collector_stop = stop_event
    try:
        yield
    finally:
        stop_event.set()
        await collector


app = FastAPI(title='AEGIS TERMINAL', version='0.6.0', lifespan=lifespan)


class EventPayload(BaseModel):
    title: str
    severity: str = 'INFO'
    source: str = 'dashboard'
    details: str = ''


class ScanPayload(BaseModel):
    path: str


class MessagePayload(BaseModel):
    sender: str = 'AEGIS-OPERATOR'
    room: str = 'COMMAND'
    message: str


class IntegrityPayload(BaseModel):
    path: str


@app.get('/', response_class=HTMLResponse)
def home():
    return (WEB_DIR / 'index.html').read_text(encoding='utf-8')


@app.get('/aegis.css')
def css():
    return FileResponse(WEB_DIR / 'aegis.css', media_type='text/css')


@app.get('/aegis.js')
def js():
    return FileResponse(WEB_DIR / 'aegis.js', media_type='application/javascript')


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


@app.get('/api/logs/json')
def logs_json(limit: int = 100):
    limit = max(1, min(limit, 1000))
    return [json_line(x['title'], x['details'], x['severity'], x['source']) for x in events(limit)]


@app.get('/api/logs/syslog/status')
def syslog_status():
    import os
    return {'configured': bool(os.getenv('AEGIS_SYSLOG_HOST')), 'host': os.getenv('AEGIS_SYSLOG_HOST'), 'port': int(os.getenv('AEGIS_SYSLOG_PORT', '514'))}


@app.post('/api/logs/syslog/test')
def syslog_test():
    return {'sent': emit_syslog('Aegis SIEM test', {'status': 'ok'}, 'INFO', 'aegis-api')}


@app.websocket('/ws/telemetry')
async def telemetry_ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


@app.get('/api/assessment')
def risk():
    return assess(snapshot())


@app.get('/api/tracking')
def tracking():
    return tracks()


@app.get('/api/comms/demo')
def comms_demo():
    return message_demo()


@app.get('/api/comms/messages')
def comms_messages(room: str = 'COMMAND'):
    return messages(room)


@app.post('/api/comms/messages')
def comms_send(payload: MessagePayload):
    try:
        result = send_message(payload.sender, payload.room, payload.message)
        add_event('Secure message sent', 'INFO', 'secure-comms', payload.room)
        return result
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get('/api/security/scanner')
def security_scanner():
    return scanner_overview()


@app.get('/api/security/status')
def security_status():
    s = snapshot()
    assessment = assess(s)
    scanner = scanner_overview()
    return {
        'platform': 'AEGIS TERMINAL',
        'mode': 'DEFENSIVE',
        'posture': assessment,
        'scanner': scanner,
        'integrity': 'SHA-256 READY',
        'tracking': 'LAWFUL OPEN-DATA ADAPTERS',
        'communications': 'LOCAL ENCRYPTED ROOM',
        'interfaces': len(interfaces()),
        'unauthorized_actions': False,
    }


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


@app.get('/api/malware/status')
def malware_status_alias():
    return scanner_overview()


@app.post('/api/malware/scan')
def malware_scan_alias(payload: ScanPayload):
    return security_scan(payload)


@app.post('/api/integrity')
def integrity(payload: IntegrityPayload):
    try:
        result = sha256_file(payload.path)
        add_event('Integrity hash generated', 'INFO', 'integrity-engine', payload.path)
        return result
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
