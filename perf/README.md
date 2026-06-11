# Load Baseline

Lightweight local performance smoke for the API template.

## Purpose

`load_baseline.py` measures request latency and throughput for a single HTTP
endpoint. It is intended for local regression checks before larger load-testing
work in downstream projects.

## Run

Start the stack first:

```bash
make docker-up
```

Run the baseline against the API service from inside Docker:

```bash
make load-smoke
```

Override defaults when needed:

```bash
API_BASE_URL=http://api:8000 LOAD_REQUESTS=100 LOAD_CONCURRENCY=10 make load-smoke
```

## Result format

The script prints JSON with:

- `target`: requested URL
- `count`: completed requests
- `total_seconds`: wall-clock runtime
- `throughput_rps`: requests per second
- `min_ms`, `max_ms`, `mean_ms`
- `p50_ms`, `p95_ms`, `p99_ms`

Example:

```json
{
  "target": "http://api:8000/health",
  "count": 50,
  "total_seconds": 0.84,
  "throughput_rps": 59.52,
  "min_ms": 1.42,
  "max_ms": 18.77,
  "mean_ms": 4.91,
  "p50_ms": 4.12,
  "p95_ms": 11.36,
  "p99_ms": 18.77
}
```

Record results in project notes or CI artifacts when comparing changes over
time. This template does not enforce hard latency thresholds because hardware and
Docker overhead vary between machines.
