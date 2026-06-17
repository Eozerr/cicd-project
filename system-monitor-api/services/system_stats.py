import psutil
import os
from datetime import datetime


def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_cpu_info():
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True)
    }


def get_ram_usage():
    memory = psutil.virtual_memory()

    return {
        "total_gb": round(memory.total / (1024 ** 3), 2),
        "used_gb": round(memory.used / (1024 ** 3), 2),
        "percent": memory.percent
    }


def get_disk_usage():
    disk = psutil.disk_usage("/")

    return {
        "total_gb": round(disk.total / (1024 ** 3), 2),
        "used_gb": round(disk.used / (1024 ** 3), 2),
        "percent": disk.percent
    }


def get_uptime():
    boot_time = datetime.fromtimestamp(psutil.boot_time())

    return {
        "boot_time": boot_time.isoformat()
    }


def get_network_stats():
    net = psutil.net_io_counters()

    return {
        "bytes_sent": net.bytes_sent,
        "bytes_received": net.bytes_recv
    }


def get_process_count():
    return {
        "process_count": len(psutil.pids())
    }


def get_load_average():
    # Windows uyumsuz olabilir
    if hasattr(os, "getloadavg"):
        load1, load5, load15 = os.getloadavg()
        return {
            "1min": load1,
            "5min": load5,
            "15min": load15
        }

    return {
        "error": "load average not supported on this OS"
    }


def top_memory_processes(limit=5):
    processes = []

    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes.sort(key=lambda x: x["memory_percent"], reverse=True)

    return processes[:limit]