from datetime import datetime, timezone
from math import atan2, cos, radians, sin, sqrt


def _now():
    return datetime.now(timezone.utc).isoformat()


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


def tracks():
    return {'timestamp': _now(), 'aircraft': demo_aircraft(), 'vessels': demo_vessels(), 'mode': 'DEMO / OPEN-DATA ADAPTER READY'}


def track_distance(a, b):
    return _distance_nm(a['lat'], a['lon'], b['lat'], b['lon'])
