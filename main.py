import json
import logging
import math
import os
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from threading import Lock

from fastapi import FastAPI, Query, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, generate_latest

app = FastAPI(title="Production Observability API")
START_TIME = time.monotonic()
REGISTRY = CollectorRegistry()
REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests received by the service",
    registry=REGISTRY,
)
LOGS = deque(maxlen=1000)
LOG_LOCK = Lock()
logger = logging.getLogger("observability")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.propagate = False


@app.middleware("http")
async def record_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    start = time.monotonic()
    REQUESTS.inc()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        entry = {
            "level": "INFO" if status_code < 500 else "ERROR",
            "ts": datetime.now(timezone.utc).isoformat(),
            "path": request.url.path,
            "request_id": request_id,
            "method": request.method,
            "status_code": status_code,
            "duration_ms": round((time.monotonic() - start) * 1000, 3),
        }
        with LOG_LOCK:
            LOGS.append(entry)
        logger.info(json.dumps(entry, separators=(",", ":")))


@app.get("/work")
def work(n: int = Query(default=1, ge=0)):
    # Perform n units of simple deterministic work, without blocking for long durations.
    total = 0
    for i in range(n):
        total += i * i
    return {"email": os.getenv("STUDENT_EMAIL", "22f1001970@ds.study.iitm.ac.in"), "done": n}


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


@app.get("/healthz")
def healthz():
    uptime = time.monotonic() - START_TIME
    return {"status": "ok", "uptime_s": max(0.0, uptime)}


@app.get("/logs/tail")
def logs_tail(limit: int = Query(default=10, ge=0, le=1000)):
    with LOG_LOCK:
        return list(LOGS)[-limit:] if limit else []
