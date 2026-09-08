# Distributed Systems Performance Lab

A FastAPI lab exploring how connection pooling, caching, dependency failures, and concurrency affect backend performance.

## Stack

Python · FastAPI · PostgreSQL · Redis · Docker Compose · Prometheus client · pytest · GitHub Actions

## Engineering Focus

- PostgreSQL connection pooling
- Redis caching and expiration
- Database fallback when Redis fails
- Timeout and retry configuration
- Throughput and tail-latency measurement
- Application metrics
- Automated testing and CI

## Recorded Results

These local experiments used 200 measured requests per run at concurrency
10. The baseline, pooling, and cache-hit experiments used five runs each.
Redis-unavailable testing used six runs. All recorded runs reported zero
measured request errors.

| Experiment | Throughput | Average latency | p95 | p99 |
| --- | ---: | ---: | ---: | ---: |
| PostgreSQL baseline | 223.45 req/s | 44.67 ms | 77.22 ms | 113.41 ms |
| PostgreSQL with pooling | 640.24 req/s | 15.36 ms | 28.59 ms | 38.73 ms |
| Redis cache hits | 652.08 req/s | 15.38 ms | 33.27 ms | 48.29 ms |
| Redis unavailable | 395.10 req/s | 24.87 ms | 40.82 ms | 50.54 ms |

Connection pooling produced the largest improvement in these experiments.
Redis offered little additional benefit for the small local primary-key
lookup workload. During the Redis outage experiment, requests continued
through PostgreSQL fallback.

In a separate concurrency experiment, throughput peaked at concurrency
10 among the tested levels of 1, 10, 25, and 50. Higher concurrency increased
tail latency while throughput declined.

These are historical, workload-specific measurements. Hardware and system
load affect results. The current code always uses connection pooling and
checks Redis first; running it unchanged does not recreate the earlier
configurations without pooling or caching.

See [experiments/](experiments/) for the recorded configurations and results.

## Request Flow

1. Check Redis for the requested item.
2. Return a cached item if available.
3. On a cache miss or Redis error, query PostgreSQL.
4. Return HTTP 404 if the item does not exist.
5. Attempt to cache a database result for 60 seconds, then return it.

PostgreSQL uses a connection pool with a minimum of 1 and a maximum of
10 connections.

Redis connection and socket timeouts are each 0.1 seconds, with retries
disabled. These are per-operation settings, not an overall HTTP deadline.
Fallback requires PostgreSQL to remain available.

The PostgreSQL fallback counter includes ordinary cache misses as well
as Redis failures.

## Run Locally

Requirements:

- Python 3.14
- Docker with Docker Compose
- A shell supporting the commands below, such as Ubuntu or WSL

From the repository root, create configuration for a fresh checkout:

```bash
cp .env.example .env
```

Review the local development settings in `.env`. Preserve an existing
configuration instead of overwriting it.

Start PostgreSQL and Redis:

```bash
docker compose up -d
```

Create a Python environment, install dependencies, and start FastAPI:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app
```

The API runs at `http://127.0.0.1:8000`.

| Endpoint | Purpose |
| --- | --- |
| `/` | Application introduction |
| `/items/1` | Item lookup used by the benchmarks |
| `/metrics` | Prometheus-format application metrics |

The database initialization script runs when PostgreSQL creates a new
data volume. It does not automatically rerun against an existing volume.

## Tests

With the virtual environment activated:

```bash
python -m pytest -v
```

The current suite contains eight tests covering:

- Root endpoint response
- Cached item responses
- PostgreSQL fallback routing
- Missing item responses
- Cache reads and misses
- Redis read errors
- Redis write errors

The tests replace database queries and Redis operations with controlled
substitutes. They verify application behavior without establishing
end-to-end database availability or performance.

GitHub Actions is configured to run the suite on pushes and pull requests
using Python 3.14.

## Benchmarks

Keep the API running. In a second terminal, enter the repository directory
and activate the virtual environment:

```bash
source .venv/bin/activate
python benchmarks/baseline.py
python benchmarks/concurrency.py
```

Both scripts target `http://127.0.0.1:8000/items/1`.

The baseline script measures the currently running configuration with
200 requests at concurrency 10.

The concurrency script uses five trials at each concurrency level:
1, 10, 25, and 50. Each trial measures 200 requests. Both scripts issue
10 warm-up requests before each measured run.

Measurement details:

- Latency starts after acquiring a client concurrency slot, excluding
  time waiting for that slot.
- Latency statistics include successful and failed measured requests.
- Throughput counts all attempted measured requests.
- The concurrency summary averages trial-level percentiles rather than
  calculating percentiles across all requests combined.
- Read the error count alongside latency and throughput.

These short local runs do not establish production capacity.

## Limitations

- Results come from a small local item-lookup workload.
- Earlier experiment configurations require their corresponding historical
  code or setup to reproduce.
- Mocked tests do not replace integration testing with real services.
- Redis fallback does not protect against PostgreSQL failure.
- Metrics are exposed by the application; collecting and visualizing them
  requires separate monitoring infrastructure.

## Shutdown

Stop FastAPI with Ctrl+C, then stop the supporting containers:

```bash
docker compose down
```

The PostgreSQL data volume is preserved.
