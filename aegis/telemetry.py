"""Background telemetry collection, structured events and WebSocket fan-out."""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from .db import add_event
from .monitor import processes, snapshot
from .tracking import tracks

logger = logging.getLogger("aegis.telemetry")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def telemetry_event(event_type: str, data: Any, severity: str = "INFO", source: str = "aegis") -> dict:
    return {
        "timestamp": utc_now(),
        "source": source,
        "event_type": event_type,
        "severity": severity.upper(),
        "host": snapshot().get("hostname", "unknown"),
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
    # Keep the event stream compact: one structured telemetry event per cycle.
    add_event("Telemetry snapshot", "INFO", "telemetry", json.dumps({
        "cpu_percent": system.get("cpu_percent"),
        "memory_percent": system.get("memory_percent"),
        "process_count": len(top_processes),
        "aircraft": len(tracking.get("aircraft", [])),
        "vessels": len(tracking.get("vessels", [])),
    }))
    return payload


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
