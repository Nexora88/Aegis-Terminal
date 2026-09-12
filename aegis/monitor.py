import platform
import socket
import time

import psutil


def snapshot():
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net = psutil.net_io_counters()
    boot = psutil.boot_time()
    return {
        'hostname': socket.gethostname(),
        'platform': platform.platform(),
        'system': platform.system(),
        'release': platform.release(),
        'python': platform.python_version(),
        'cpu_percent': psutil.cpu_percent(interval=0.1),
        'cpu_count': psutil.cpu_count(logical=True),
        'memory_percent': vm.percent,
        'memory_used_bytes': vm.used,
        'memory_total_bytes': vm.total,
        'disk_percent': disk.percent,
        'disk_used_bytes': disk.used,
        'disk_total_bytes': disk.total,
        'boot_time': boot,
        'uptime_seconds': max(0, time.time() - boot),
        'network_sent_bytes': net.bytes_sent,
        'network_recv_bytes': net.bytes_recv,
    }


def processes(limit=25):
    out = []
    for p in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_percent']):
        try:
            info = p.info
            out.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(out, key=lambda x: (x.get('cpu_percent') or 0), reverse=True)[:limit]


def interfaces():
    result = {}
    for name, addrs in psutil.net_if_addrs().items():
        result[name] = [
            {
                'address': addr.address,
                'family': str(addr.family),
                'netmask': addr.netmask,
                'broadcast': addr.broadcast,
            }
            for addr in addrs
        ]
    return result
