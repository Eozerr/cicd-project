import time
from flask import Blueprint, jsonify

from services.system_stats import (
    get_cpu_usage,
    get_cpu_info,
    get_ram_usage,
    get_disk_usage,
    get_uptime,
    get_network_stats,
    get_process_count,
    get_load_average,
    top_memory_processes
)

from services.cache import get_cached_system, set_cached_system


monitor_bp = Blueprint("monitor", __name__)


@monitor_bp.route("/system", methods=["GET"])
def system_metrics():

    start_time = time.time()

    # 🔥 cache kontrol
    cached = get_cached_system()
    if cached:
        cached["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
        return jsonify(cached)

    data = {
        "status": "ok",
        "cpu": {
            "usage_percent": get_cpu_usage(),
            "info": get_cpu_info()
        },
        "memory": get_ram_usage(),
        "disk": get_disk_usage(),
        "uptime": get_uptime(),
        "network": get_network_stats(),
        "process": get_process_count(),
        "load_average": get_load_average(),
        "top_memory_processes": top_memory_processes()
    }

    # cache'e yaz
    set_cached_system(data)

    data["response_time_ms"] = round((time.time() - start_time) * 1000, 2)

    return jsonify(data)