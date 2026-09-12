from fastapi import FastAPI,HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from .db import init_db,events,add_event
from .monitor import snapshot,processes,interfaces
from .integrity import sha256_file
from .decision import assess
app=FastAPI(title='AEGIS TERMINAL')
init_db()
@app.get('/',response_class=HTMLResponse)
def home(): return (Path(__file__).parent/'web'/'index.html').read_text(encoding='utf-8')
@app.get('/api/health')
def health(): return {'status':'online','service':'AEGIS TERMINAL'}
@app.get('/api/system')
def system(): return snapshot()
@app.get('/api/processes')
def proc(): return processes()
@app.get('/api/interfaces')
def net(): return interfaces()
@app.get('/api/events')
def ev(): return events()
@app.get('/api/assessment')
def risk(): return assess(snapshot())
@app.post('/api/integrity')
def integrity(payload:dict):
    try: return sha256_file(payload.get('path',''))
    except FileNotFoundError as e: raise HTTPException(404,str(e))
