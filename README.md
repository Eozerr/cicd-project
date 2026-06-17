# 🖥️ System Monitor API

![CI](https://github.com/Eozerr/cicd-project/actions/workflows/ci.yml/badge.svg)
![Docker](https://img.shields.io/docker/pulls/Eozerr/system-monitor-api?style=flat-square&logo=docker)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1.0-black?style=flat-square&logo=flask)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

A production-ready **real-time system metrics API** built with Python & Flask — featuring an in-memory caching layer with TTL logic, automated CI/CD pipeline, and Docker packaging.

> Designed as a lightweight alternative to heavyweight monitoring agents — expose your system internals over HTTP in seconds.

---

## 📌 What This Project Demonstrates

| Concept | Implementation |
|---|---|
| **REST API design** | Single-responsibility `/system` endpoint returning structured JSON |
| **Caching layer** | In-memory cache with TTL to prevent redundant syscalls |
| **System observability** | CPU, RAM, disk, network, process & load metrics via `psutil` |
| **CI/CD pipeline** | GitHub Actions: test → build → push on every commit |
| **Containerization** | Multi-stage aware Dockerfile, image published to Docker Hub |
| **Test automation** | pytest with fixture-based Flask test client |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  HTTP Request                    │
│                  GET /system                     │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│              Flask Application                   │
│                                                  │
│   ┌──────────────────────────────────────────┐  │
│   │           Cache Layer (TTL)              │  │
│   │                                          │  │
│   │   HIT  ──► return cached response        │  │
│   │   MISS ──► collect metrics ──► cache     │  │
│   └──────────────────────────────────────────┘  │
│                     │                            │
│                     ▼ (on cache miss)            │
│   ┌──────────────────────────────────────────┐  │
│   │         psutil Metrics Collection        │  │
│   │                                          │  │
│   │  cpu_usage  │  ram  │  disk  │  network  │  │
│   │  uptime     │  load │  procs │  top_mem  │  │
│   └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start

### Run with Docker (recommended)

```bash
docker pull eozerr/system-monitor-api:latest
docker run -d -p 5000:5000 eozerr/system-monitor-api:latest
curl http://localhost:5000/system
```

### Run locally

```bash
git clone https://github.com/eozerr/cicd-project.git
cd cicd-project/system-monitor-api
pip install -r requirements.txt
python app.py
```

---

## 📡 API Reference

### `GET /system`

Returns a full snapshot of system health metrics.

**Response** `200 OK`

```json
{
  "status": "ok",
  "cpu": {
    "usage_percent": 12.4,
    "info": {
      "physical_cores": 8,
      "logical_cores": 16,
      "max_freq_mhz": 3600
    }
  },
  "memory": {
    "total_gb": 16.0,
    "used_gb": 9.3,
    "available_gb": 6.7,
    "percent": 58.1
  },
  "disk": {
    "total_gb": 512.0,
    "used_gb": 210.4,
    "free_gb": 301.6,
    "percent": 41.1
  },
  "network": {
    "bytes_sent_mb": 1024.5,
    "bytes_recv_mb": 3200.1
  },
  "uptime": "2 days, 4:32:10",
  "process": {
    "total": 312
  },
  "load_average": [1.2, 0.9, 0.8],
  "top_memory_processes": [
    { "name": "chrome", "memory_mb": 820.4 },
    { "name": "python", "memory_mb": 112.1 }
  ],
  "response_time_ms": 3.21
}
```

---

## 🧠 Caching Layer — Design Decision

One of the core design choices in this project is the **in-memory cache with TTL (Time-To-Live)** logic, implemented in `services/cache.py`.

### Why cache system metrics?

Collecting metrics involves multiple syscalls (`psutil` reads `/proc` on Linux). Under high request rates, this becomes expensive. The cache solves this elegantly:

```
First request  → collect all metrics → store in cache → respond (slow path)
Next requests  → read from cache     → respond        (fast path, ~0ms overhead)
Cache expires  → collect again       → refresh cache  → respond
```

### How it works

```python
# Simplified TTL cache logic
_cache = None
_cache_time = None
TTL_SECONDS = 5

def get_cached_system():
    if _cache and (time.time() - _cache_time) < TTL_SECONDS:
        return _cache          # cache HIT
    return None                # cache MISS → collect fresh

def set_cached_system(data):
    _cache = data
    _cache_time = time.time()  # reset TTL clock
```

This is conceptually identical to how **Prometheus scrape intervals** work — metrics are sampled at a fixed cadence rather than on every request, reducing system overhead while maintaining freshness.

---

## 🔄 CI/CD Pipeline

Every `git push` to `master` automatically triggers:

```
git push
    │
    ▼
┌─────────────┐     pass      ┌──────────────────┐     push     ┌─────────────┐
│  Run Tests  │ ────────────► │  Docker Build    │ ──────────►  │  Docker Hub │
│  (pytest)   │               │  (Dockerfile)    │              │  Registry   │
└─────────────┘               └──────────────────┘              └─────────────┘
       │
       │ fail
       ▼
   ❌ Pipeline stops — image never built from broken code
```

**Pipeline file:** `.github/workflows/ci.yml`

- `test` job — installs dependencies, runs `pytest tests/ -v`
- `build-and-push` job — only runs if tests pass (`needs: test`)
- Docker image tagged with both `:latest` and `:git-sha` for full traceability

---

## 🧪 Tests

```bash
cd system-monitor-api
pytest tests/ -v
```

```
tests/test_api.py::test_system_metrics              PASSED
tests/test_api.py::test_system_metrics_returns_json PASSED

2 passed in 1.18s
```

Tests use a **pytest fixture** to spin up a Flask test client — no real server needed, no ports opened, fast and isolated.

---

## 📁 Project Structure

```
cicd-project/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions pipeline
│
├── system-monitor-api/
│    ├── app.py                  # Flask app entry point
│    ├── requirements.txt
│    │
│    ├── routes/
│    │   └── monitor.py          # /system endpoint
│    │
│    ├── services/
│    │   ├── system_stats.py     # psutil metric collectors
│    │   └── cache.py            # TTL cache implementation
│    │
│    └── tests/
│       ├── __init__.py
│       └── test_api.py         # pytest test suite
└── Dockerfile
       
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Framework | Flask 3.1.0 |
| Metrics | psutil 7.0.0 |
| Testing | pytest 8.4.1 |
| CI/CD | GitHub Actions |
| Container | Docker |
| Registry | Docker Hub |

---

## 🔮 Roadmap

- [ ] Add Prometheus `/metrics` endpoint (`prometheus_client`)
- [ ] Kubernetes deployment manifests (Helm chart)
- [ ] Grafana dashboard JSON for instant visualization
- [ ] Multi-endpoint support (per-subsystem routes)
- [ ] Configurable TTL via environment variable

---

## 👤 Author

**Ekrem Özer** — IT Support Specialist @ DP World | Cloud & DevOps Enthusiast

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/ekrem-%C3%B6zer-52830a267/)
[![Docker Hub](https://img.shields.io/badge/Docker_Hub-Eozerr-2496ED?style=flat-square&logo=docker)](https://hub.docker.com/u/Eozerr)
