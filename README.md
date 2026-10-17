# Production Observability — Question 8

FastAPI service with Prometheus counter, health checks, and structured JSON request logs.

## GitHub Codespaces setup (without Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export STUDENT_EMAIL='22f1001970@ds.study.iitm.ac.in'
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

In the Codespaces **PORTS** tab, set port 8000 visibility to **Public**. Submit the base forwarded HTTPS URL, without an endpoint suffix. Keep the Codespace and Uvicorn running while grading.

## Test in another Codespaces terminal

```bash
curl -s http://127.0.0.1:8000/metrics | grep '^http_requests_total'
curl -s 'http://127.0.0.1:8000/work?n=5'
curl -s 'http://127.0.0.1:8000/work?n=2'
curl -s http://127.0.0.1:8000/healthz
curl -s 'http://127.0.0.1:8000/logs/tail?limit=10'
curl -s http://127.0.0.1:8000/metrics | grep '^http_requests_total'
```

`http_requests_total` increments for each HTTP request, including `/metrics`, `/healthz`, and `/logs/tail`. The metrics are in-process and the log ring buffer is in-memory, so run **one Uvicorn worker** and avoid restarting during a grading attempt. JSON logs also stream to stdout.
