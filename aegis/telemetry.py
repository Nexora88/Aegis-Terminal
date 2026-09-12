"""Background telemetry collection, structured events and WebSocket fan-out."""

import asyncio
import json
import logging
import os
from collections import deque
from datetime import datetime, timezone
from typing import Any

from .db import add_event
from .monitor import processes, snapshot
from .tracking import tracks
from .log_export import emit_syslog

logger = logging.getLogger("aegis.telemetry")
TELEMETRY_LOG = deque(maxlen=1000)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def telemetry_event(event_type: str, data: Any, severity: str = "INFO", source: str = "aegis") -> dict:
    return {
        "timestamp": utc_now(),
        "source": source,
        "event_type": event_type,
        "severity": severity.upper(),
        "host": data.get("hostname", "unknown") if isinstance(data, dict) else "unknown",
        "data": data,
    }


class ConnectionManager:
    def __init__(self) -> None:
        self.connections = set()

    async def connect(self, websocket) -> None:
        await websocket.accept()
        self.connections.add(websocket)

    def disconnect(self, websocket) -> None:
        self.connections.discard(websocket)

    async def broadcast(self, payload: dict) -> None:
        if not self.connections:
            return
        message = json.dumps(payload, default=str)
        dead = []
        for websocket in tuple(self.connections):
            try:
                await websocket.send_text(message)
            except Exception:
                dead.append(websocket)
        for websocket in dead:
            self.disconnect(websocket)


manager = ConnectionManager()


async def collect_once() -> dict:
    system = await asyncio.to_thread(snapshot)
    top_processes = await asyncio.to_thread(processes, 25)
    tracking = await asyncio.to_thread(tracks)
    payload = {
        "timestamp": utc_now(),
        "system": system,
        "processes": top_processes,
        "tracking": tracking,
    }
    event = telemetry_event("telemetry.snapshot", payload, "INFO", "aegis-telemetry")
    TELEMETRY_LOG.append(event)
    add_event("Telemetry snapshot", "INFO", "telemetry", json.dumps({
        "cpu_percent": system.get("cpu_percent"),
        "memory_percent": system.get("memory_percent"),
        "process_count": len(top_processes),
        "aircraft": len(tracking.get("aircraft", [])),
        "vessels": len(tracking.get("vessels", [])),
    }))
    try:
        emit_syslog(event["event_type"], event["data"], event["severity"], event["source"])
    except Exception:
        logger.exception("syslog export failed")
    return payload


def recent_telemetry(limit: int = 100) -> list[dict]:
    limit = max(1, min(int(limit), 1000))
    return list(TELEMETRY_LOG)[-limit:][::-1]


async def collector_loop(stop_event: asyncio.Event) -> None:
    try:
        interval = max(5, int(os.getenv("AEGIS_COLLECT_INTERVAL", "15")))
    except ValueError:
        interval = 15
    while not stop_event.is_set():
        try:
            payload = await collect_once()
            await manager.broadcast({"type": "telemetry", "payload": payload})
        except Exception:
            logger.exception("background telemetry collection failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            pass
