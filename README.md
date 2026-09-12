# Aegis Terminal

A modular defensive cybersecurity operations platform for local system monitoring, log analysis, file-integrity verification, security-event triage, and decision support.

> Aegis is designed for authorized defensive use on systems you own or are permitted to monitor.

## Stack

- Python 3.11+
- FastAPI / Uvicorn
- psutil
- Pydantic
- SQLite
- Vanilla HTML/CSS/JavaScript

## Features

- Live CPU, memory, disk and uptime telemetry
- Running-process overview
- Local network-interface inventory
- Log-file analysis with severity detection
- SHA-256 file integrity verification
- Local security-event database
- Rule-based security decision support
- Terminal CLI
- Browser dashboard

## Run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m aegis.cli
```

Dashboard:

```bash
uvicorn aegis.api:app --reload
```

Open `http://127.0.0.1:8000`.

## Safety

Aegis is intentionally focused on defensive visibility and analysis. It does not perform credential theft, persistence, exploitation, destructive actions, or unauthorized network intrusion.
