"""Structured JSON and Syslog export for SIEM ingestion."""

import json
import logging
import logging.handlers
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("aegis.siem")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_log(event_type: str, data: Any, severity: str = "INFO", source: str = "aegis") -> dict:
    return {
        "timestamp": utc_now(),
        "source": source,
        "event_type": event_type,
        "severity": severity.upper(),
        "data": data,
    }


def json_line(event_type: str, data: Any, severity: str = "INFO", source: str = "aegis") -> str:
    return json.dumps(build_log(event_type, data, severity, source), separators=(",", ":"), default=str)


def emit_syslog(event_type: str, data: Any, severity: str = "INFO", source: str = "aegis") -> bool:
    host = os.getenv("AEGIS_SYSLOG_HOST")
    if not host:
        return False
    port = int(os.getenv("AEGIS_SYSLOG_PORT", "514"))
    facility = logging.handlers.SysLogHandler.LOG_LOCAL0
    handler = logging.handlers.SysLogHandler(address=(host, port), facility=facility)
    try:
        record = logging.LogRecord("aegis", logging.INFO, __file__, 0, json_line(event_type, data, severity, source), (), None)
        handler.emit(record)
        return True
    finally:
        handler.close()
