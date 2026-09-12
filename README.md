# Aegis Terminal

**NEXORA DEFENSIVE OPERATIONS**  
**Founder & Independent Developer: Ahmet Eymen Bakraç**

Aegis Terminal is a modular defensive operations platform combining host telemetry, security-event analysis, lawful open-data aircraft/maritime tracking, track management and local secure communications.

> Aegis is designed for authorized defensive use on systems you own or are permitted to monitor. Aircraft and maritime modules use lawful public/open-data adapters only.

## Stack

- Python 3.11+
- FastAPI / Uvicorn
- psutil
- Pydantic
- SQLite
- cryptography / Fernet authenticated encryption
- Vanilla HTML/CSS/JavaScript

## Operations modules

- Command Center
- Aircraft tracking adapter (OpenSky)
- Maritime AIS adapter (AIS Friends)
- Radar / track-management layer
- CPU, memory, disk, network and process telemetry
- Security assessment and event stream
- SHA-256 file-integrity verification
- Local encrypted-message demonstration channel
- Terminal CLI
- Responsive operations dashboard

## Open-data configuration

Aegis falls back to clearly labeled demo tracks when credentials or live providers are unavailable.

Optional environment variables:

```bash
AEGIS_OPENSKY_URL=https://opensky-network.org/api/states/all
AEGIS_AIS_TOKEN=your_ais_friends_token
```

Do not commit API tokens or other secrets to GitHub. Provider terms, rate limits and commercial-use conditions must be reviewed before deploying Aegis as a public or commercial service.

## Run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn aegis.api:app --reload
```

Open `http://127.0.0.1:8000`.

## Brand

**AEGIS TERMINAL** is a Nexora product concept developed by **Ahmet Eymen Bakraç**. The product direction is a professional defensive operations center rather than a toy dashboard: clear telemetry, transparent data sources, modular providers and an explicit defensive-use boundary.

## Safety

Aegis is intentionally focused on defensive visibility and analysis. It does not perform credential theft, persistence, exploitation, destructive actions, unauthorized network intrusion, access to restricted radar systems, or interception/decryption of other people's communications.
