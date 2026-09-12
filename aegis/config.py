from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("AEGIS_DATA_DIR", BASE_DIR / "data"))
DB_PATH = DATA_DIR / "aegis.db"
DATA_DIR.mkdir(parents=True, exist_ok=True)
APP_NAME = "AEGIS TERMINAL"
