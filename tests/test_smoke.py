from aegis.config import APP_NAME, DB_BACKEND
from aegis.antivirus import scanner_overview


def test_app_identity():
    assert APP_NAME == "AEGIS TERMINAL"
    assert DB_BACKEND in {"sqlite", "postgresql"}


def test_scanner_is_defensive():
    overview = scanner_overview()
    assert overview["status"] == "ACTIVE"
    assert "never executed" in overview["scope"]
