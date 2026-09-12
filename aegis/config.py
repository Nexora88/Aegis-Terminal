from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("AEGIS_DATA_DIR", BASE_DIR / "data")).expanduser()
DB_PATH = DATA_DIR / "aegis.db"
DATABASE_URL = os.getenv("AEGIS_DATABASE_URL", "").strip()
DB_BACKEND = "postgresql" if DATABASE_URL.startswith(("postgresql://", "postgres://")) else "sqlite"

try:
    COLLECT_INTERVAL = max(5, int(os.getenv("AEGIS_COLLECT_INTERVAL", "15")))
except ValueError:
    COLLECT_INTERVAL = 15

try:
    LOG_RETENTION_DAYS = max(1, min(int(os.getenv("AEGIS_LOG_RETENTION_DAYS", "90")), 3650))
except ValueError:
    LOG_RETENTION_DAYS = 90

APP_NAME = "AEGIS TERMINAL"
DATA_DIR.mkdir(parents=True, exist_ok=True)
