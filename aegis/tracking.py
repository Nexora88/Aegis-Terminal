"""Lawful public-data tracking adapters with a deterministic demo fallback."""

import os
from datetime import datetime, timezone
from math import atan2, cos, radians, sin, sqrt
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json


def _now():
    return datetime.now(timezone.utc).isoformat()


def _get_json(url, headers=None, timeout=8):
    request = Request(url, headers=headers or {"User-Agent": "Aegis-Terminal/0.3"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _distance_nm(lat1, lon1, lat2, lon2):
    r = 3440.069
    p1, p2 = radians(lat1), radians(lat2)
    dp = radians(lat2 - lat1)
    dl = radians(lon2 - lon1)
    a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return round(2 * r * atan2(sqrt(a), sqrt(1 - a)), 2)


def demo_aircraft():
    return [
        {'id': 'AEGIS-A001', 'callsign': 'DEMO101', 'type': 'AIRCRAFT', 'lat': 41.0082, 'lon': 28.9784, 'altitude_ft': 31000, 'speed_kt': 445, 'heading': 92, 'source': 'DEMO', 'updated': _now()},
        {'id': 'AEGIS-A002', 'callsign': 'DEMO202', 'type': 'AIRCRAFT', 'lat': 40.6401, 'lon': 22.9444, 'altitude_ft': 28000, 'speed_kt': 420, 'heading': 274, 'source': 'DEMO', 'updated': _now()},
    ]


def demo_vessels():
    return [
        {'id': 'AEGIS-V001', 'name': 'DEMO VESSEL 01', 'type': 'VESSEL', 'lat': 40.95, 'lon': 29.05, 'speed_kt': 12.4, 'heading': 178, 'source': 'DEMO', 'updated': _now()},
        {'id': 'AEGIS-V002', 'name': 'DEMO VESSEL 02', 'type': 'VESSEL', 'lat': 40.72, 'lon': 28.85, 'speed_kt': 8.7, 'heading': 62, 'source': 'DEMO', 'updated': _now()},
    ]


def opensky_aircraft():
    """Fetch OpenSky states when AEGIS_OPENSKY_URL is configured."""
    url = os.getenv("AEGIS_OPENSKY_URL", "https://opensky-network.org/api/states/all")
    try:
        data = _get_json(url)
        result = []
        for row in data.get("states", [])[:250]:
            if not row or row[5] is None or row[6] is None:
                continue
            result.append({
                'id': f"ICAO-{row[0]}", 'callsign': (row[1] or '').strip(), 'type': 'AIRCRAFT',
                'lat': row[6], 'lon': row[5], 'altitude_ft': round((row[7] or 0) * 3.28084),
                'speed_kt': round((row[9] or 0) * 1.94384), 'heading': round(row[10] or 0),
                'source': 'OpenSky', 'updated': _now()
            })
        return result
    except Exception:
        return []


def aisfriends_vessels():
    """Fetch AIS Friends data when an AEGIS_AIS_TOKEN is configured."""
    token = os.getenv("AEGIS_AIS_TOKEN")
    if not token:
        return []
    params = urlencode({'lat_min': 35.5, 'lat_max': 42.2, 'lon_min': 25.5, 'lon_max': 45.0, 'from': 30, 'format': 'json'})
    url = f"https://www.aisfriends.com/api/public/v1/vessels/bounding-box?{params}"
    try:
        data = _get_json(url, {'Authorization': f'Bearer {token}', 'Accept': 'application/json'})
        result = []
        for row in data if isinstance(data, list) else data.get('vessels', []):
            lat, lon = row.get('latitude'), row.get('longitude')
            if lat is None or lon is None:
                continue
            result.append({
                'id': f"MMSI-{row.get('mmsi')}", 'name': row.get('name') or 'UNKNOWN', 'type': 'VESSEL',
                'lat': lat, 'lon': lon, 'speed_kt': row.get('speed_over_ground') or 0,
                'heading': row.get('true_heading') or row.get('course_over_ground') or 0,
                'mmsi': row.get('mmsi'), 'imo': row.get('imo'), 'source': 'AIS Friends', 'updated': _now()
            })
        return result
    except Exception:
        return []


def tracks():
    aircraft = opensky_aircraft()
    vessels = aisfriends_vessels()
    live = bool(aircraft or vessels)
    return {
        'timestamp': _now(),
        'aircraft': aircraft or demo_aircraft(),
        'vessels': vessels or demo_vessels(),
        'mode': 'LIVE OPEN DATA' if live else 'DEMO FALLBACK',
        'providers': {'aircraft': 'OpenSky' if aircraft else 'DEMO', 'maritime': 'AIS Friends' if vessels else 'DEMO'},
    }


def track_distance(a, b):
    return _distance_nm(a['lat'], a['lon'], b['lat'], b['lon'])
