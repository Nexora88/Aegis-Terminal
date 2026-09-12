from pathlib import Path
import hashlib

def sha256_file(path):
    p=Path(path).expanduser().resolve()
    if not p.is_file(): raise FileNotFoundError(str(p))
    h=hashlib.sha256(); size=0
    with p.open('rb') as f:
        while b:=f.read(1024*1024): size+=len(b); h.update(b)
    return {'path':str(p),'size_bytes':size,'sha256':h.hexdigest(),'modified':p.stat().st_mtime}
