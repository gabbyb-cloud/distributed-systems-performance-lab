# Distributed Systems Performance Lab

A small FastAPI performance lab for measuring backend behavior under caching, connection pooling, dependency failure, and increasing concurrency.

## Stack

Python · FastAPI · PostgreSQL · Redis · Docker Compose · Prometheus · pytest · GitHub Actions

## What It Demonstrates

* PostgreSQL connection pooling and before/after benchmarking
* Redis caching with cache hit/miss behavior
* Graceful PostgreSQL fallback during Redis failure
* Fail-fast timeout and retry configuration
* Concurrency and tail-latency analysis
* Prometheus-style application metrics
* Automated tests and CI

## Key Results

| Experiment          |   Throughput | Avg Latency |      p95 |       p99 |
| ------------------- | -----------: | ----------: | -------: | --------: |
| PostgreSQL baseline | 223.45 req/s |    44.67 ms | 77.22 ms | 113.41 ms |
| PostgreSQL + pool   | 640.24 req/s |    15.36 ms | 28.59 ms |  38.73 ms |
| Redis cache hits    | 652.08 req/s |    15.38 ms | 33.27 ms |  48.29 ms |
| Redis unavailable   | 395.10 req/s |    24.87 ms | 40.82 ms |  50.54 ms |

Connection pooling produced the largest performance improvement. Redis provided little additional benefit for this small local primary-key lookup workload. With Redis unavailable, the API remained operational by failing fast and falling back to PostgreSQL.

## Run Locally

```bash
cp .env.example .env
docker compose up -d
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app
```

Run tests:

```bash
python -m pytest -v
```

Detailed benchmark records are in [`experiments/`](experiments/).
