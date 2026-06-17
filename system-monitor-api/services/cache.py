import time

cache = {
    "data": None,
    "time": 0
}


def set_cached_system(data):
    # print("CACHE SET")
    cache["data"] = data
    cache["time"] = time.time()


def get_cached_system():
    # print("🔍 CACHE CHECK")

    if time.time() - cache["time"] < 2:
        # print("✅ CACHE HIT")
        return cache["data"]

    # print("❌ CACHE MISS")
    return None