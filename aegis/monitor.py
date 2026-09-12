import psutil, platform, socket

def snapshot():
    vm=psutil.virtual_memory(); d=psutil.disk_usage('/')
    return {'hostname':socket.gethostname(),'platform':platform.platform(),'cpu_percent':psutil.cpu_percent(interval=.1),'memory_percent':vm.percent,'disk_percent':d.percent,'boot_time':psutil.boot_time()}

def processes(limit=20):
    out=[]
    for p in psutil.process_iter(['pid','name','username','cpu_percent','memory_percent']):
        try: out.append(p.info)
        except (psutil.NoSuchProcess,psutil.AccessDenied): pass
    return sorted(out,key=lambda x:(x.get('cpu_percent') or 0),reverse=True)[:limit]

def interfaces():
    return {n:[a.address for a in addrs] for n,addrs in psutil.net_if_addrs().items()}
