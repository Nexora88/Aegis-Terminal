"""Defensive malware-scanning adapters for Aegis Terminal.

The scanner is intentionally defensive: it inspects files the operator explicitly
selects, records findings, and never executes or modifies suspicious content.
ClamAV is optional; when unavailable Aegis still provides a lightweight local
heuristic layer and SHA-256 identification.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path

SUSPICIOUS_EXTENSIONS = {
    '.exe', '.dll', '.scr', '.bat', '.cmd', '.ps1', '.vbs', '.js', '.jar', '.msi', '.hta'
}
SUSPICIOUS_NAMES = {
    'autorun.inf', 'desktop.ini'
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def clamav_status() -> dict:
    binary = shutil.which('clamscan')
    if not binary:
        return {'available': False, 'engine': 'ClamAV', 'detail': 'clamscan not installed'}
    try:
        version = subprocess.run([binary, '--version'], capture_output=True, text=True, timeout=3)
        return {'available': version.returncode == 0, 'engine': 'ClamAV', 'detail': version.stdout.strip()}
    except Exception as exc:
        return {'available': False, 'engine': 'ClamAV', 'detail': str(exc)}


def scan_file(path_text: str) -> dict:
    path = Path(path_text).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path_text)

    digest = sha256(path)
    result = {
        'path': str(path),
        'name': path.name,
        'size_bytes': path.stat().st_size,
        'sha256': digest,
        'verdict': 'CLEAN',
        'confidence': 'LOW',
        'engine': 'Aegis local heuristic',
        'findings': [],
    }

    if path.suffix.lower() in SUSPICIOUS_EXTENSIONS:
        result['findings'].append(f'Executable or script file type: {path.suffix.lower()}')
        result['confidence'] = 'MEDIUM'

    if path.name.lower() in SUSPICIOUS_NAMES:
        result['findings'].append('Special startup/configuration filename requires review')
        result['confidence'] = 'MEDIUM'

    try:
        if path.stat().st_size <= 2 * 1024 * 1024 and path.suffix.lower() in {'.ps1', '.bat', '.cmd', '.vbs', '.js'}:
            text = path.read_text(encoding='utf-8', errors='ignore')
            patterns = [r'encodedcommand', r'frombase64string', r'invoke-expression', r'downloadstring', r'bitsadmin']
            hits = [p for p in patterns if re.search(p, text, re.I)]
            if hits:
                result['findings'].append('Script contains high-risk command patterns')
                result['verdict'] = 'REVIEW'
                result['confidence'] = 'HIGH'
    except OSError:
        result['findings'].append('File content could not be inspected')

    clam = clamav_status()
    if clam['available']:
        try:
            proc = subprocess.run(['clamscan', '--no-summary', str(path)], capture_output=True, text=True, timeout=30)
            result['engine'] = 'Aegis + ClamAV'
            if proc.returncode == 1 or 'FOUND' in proc.stdout:
                result['verdict'] = 'MALICIOUS'
                result['confidence'] = 'HIGH'
                result['findings'].append(proc.stdout.strip() or 'ClamAV detected a threat')
            elif proc.returncode == 0:
                result['findings'].append('ClamAV scan completed without a detection')
        except (OSError, subprocess.TimeoutExpired) as exc:
            result['findings'].append(f'ClamAV scan unavailable: {exc}')

    if result['verdict'] == 'CLEAN' and result['findings']:
        result['verdict'] = 'REVIEW'
    return result


def scanner_overview() -> dict:
    return {
        'status': 'ACTIVE',
        'mode': 'DEFENSIVE FILE INSPECTION',
        'engine': clamav_status(),
        'scope': 'Only operator-selected local files are inspected; suspicious content is never executed.',
    }
