# Distributed Systems Performance Lab

A FastAPI performance and resilience lab exploring how **PostgreSQL connection pooling, Redis caching, dependency failure, and concurrency** affect backend behavior.

The project is designed around a practical reliability question:

> How does a backend behave as load changes, dependencies fail, and infrastructure choices change?

## Stack

Python · FastAPI · PostgreSQL · Redis · Docker Compose · Prometheus client · pytest · GitHub Actions

---

## Key Findings

The most important result from the recorded local experiments was that **PostgreSQL connection pooling produced the largest performance improvement for this workload**.

Measured throughput increased from:

```text
223.45 req/s  →  640.24 req/s
```

Redis cache hits measured **652.08 req/s**, only a small additional improvement over the pooled PostgreSQL result for this particular primary-key lookup workload.

During the Redis-unavailable experiment, requests continued through PostgreSQL fallback instead of failing solely because the cache dependency was unavailable.

A separate concurrency experiment also showed that more concurrency was not automatically better: throughput peaked at concurrency 10 among the tested levels of 1, 10, 25, and 50, while higher concurrency increased tail latency and reduced throughput.

These results are workload-specific local measurements, not production-capacity claims.

---

## Reliability Questions Explored

| Question | What the lab tests |
| --- | --- |
| Does database connection reuse matter? | PostgreSQL baseline compared with connection pooling |
| Does caching always improve performance? | Redis cache-hit performance compared with pooled PostgreSQL |
| What happens if Redis becomes unavailable? | Requests fall back to PostgreSQL |
| How does concurrency affect the service? | Throughput and tail latency measured at multiple concurrency levels |
| Can dependency behavior be observed? | Application metrics expose request and fallback behavior |
| Are failure paths tested? | Automated tests cover Redis errors and PostgreSQL fallback routing |

---

## Engineering Focus

- PostgreSQL connection pooling
- Redis caching and expiration
- Graceful database fallback when Redis fails
- Timeout and retry configuration
- Throughput measurement
- Average, p95, and p99 latency analysis
- Concurrency testing
- Dependency-failure behavior
- Prometheus-format application metrics
- Automated testing and CI

---

## Recorded Results

These local experiments used 200 measured requests per run at concurrency 10.

The baseline, pooling, and cache-hit experiments used five runs each. Redis-unavailable testing used six runs. All recorded runs reported zero measured request errors.

| Experiment | Throughput | Average latency | p95 | p99 |
| --- | ---: | ---: | ---: | ---: |
| PostgreSQL baseline | 223.45 req/s | 44.67 ms | 77.22 ms | 113.41 ms |
| PostgreSQL with pooling | 640.24 req/s | 15.36 ms | 28.59 ms | 38.73 ms |
| Redis cache hits | 652.08 req/s | 15.38 ms | 33.27 ms | 48.29 ms |
| Redis unavailable | 395.10 req/s | 24.87 ms | 40.82 ms | 50.54 ms |

### What the measurements suggest

**Connection pooling** produced the largest improvement in these experiments.

**Redis** offered little additional benefit for this small local primary-key lookup workload once PostgreSQL pooling was enabled.

**Redis failure** degraded performance, but requests continued through PostgreSQL fallback.

**Higher concurrency** did not continuously improve throughput. Beyond the best tested level, tail latency increased while throughput declined.

These are historical, workload-specific measurements. Hardware and system load affect results. The current code always uses connection pooling and checks Redis first; running it unchanged does not recreate the earlier configurations without pooling or caching.

See [experiments/](experiments/) for the recorded configurations and results.

---

## Request and Failure Flow

```text
Client request
      |
      v
Check Redis
   |      |
 hit    miss/error
   |      |
   v      v
return   PostgreSQL pool
cache        |
result       v
          query item
             |
      +------+------+
      |             |
    found        missing
      |             |
      v             v
attempt cache     HTTP 404
write
      |
      v
return response
```

The design treats Redis as an optimization rather than the source of truth.

If a Redis read fails, the request can continue through PostgreSQL as long as the database remains available.

PostgreSQL uses a connection pool with a minimum of 1 and a maximum of 10 connections.

Redis connection and socket timeouts are each 0.1 seconds, with retries disabled. These are per-operation settings, not an overall HTTP deadline.

The PostgreSQL fallback counter includes ordinary cache misses as well as Redis failures.

---

## Resilience Behavior

The Redis failure path demonstrates a simple reliability principle:

```text
Dependency failure
      |
      v
Detect Redis error
      |
      v
Use PostgreSQL fallback
      |
      v
Return request result
      |
      v
Expose fallback through metrics
```

This does **not** make the service fully fault tolerant—PostgreSQL must still be available—but it prevents a cache outage from automatically becoming an application outage.

---

## Observability

The application exposes Prometheus-format metrics at:

```text
/metrics
```

The lab uses metrics to make application and dependency behavior observable rather than evaluating performance only from client-side benchmark output.

Metrics are exposed by the application; collecting and visualizing them requires separate monitoring infrastructure.

---

## Run Locally

### Requirements

- Python 3.14
- Docker with Docker Compose
- A shell supporting the commands below, such as Ubuntu or WSL

From the repository root, create configuration for a fresh checkout:

```bash
cp .env.example .env
```

Review the local development settings in `.env`. Preserve an existing configuration instead of overwriting it.

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

The database initialization script runs when PostgreSQL creates a new data volume. It does not automatically rerun against an existing volume.

---

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

The tests replace database queries and Redis operations with controlled substitutes. They verify application behavior without establishing end-to-end database availability or performance.

GitHub Actions runs the suite on pushes and pull requests using Python 3.14.

---

## Benchmarks

Keep the API running. In a second terminal, enter the repository directory and activate the virtual environment:

```bash
source .venv/bin/activate
python benchmarks/baseline.py
python benchmarks/concurrency.py
```

Both scripts target:

```text
http://127.0.0.1:8000/items/1
```

The baseline script measures the currently running configuration with 200 requests at concurrency 10.

The concurrency script uses five trials at each concurrency level: 1, 10, 25, and 50. Each trial measures 200 requests. Both scripts issue 10 warm-up requests before each measured run.

### Measurement details

- Latency starts after acquiring a client concurrency slot, excluding time waiting for that slot.
- Latency statistics include successful and failed measured requests.
- Throughput counts all attempted measured requests.
- The concurrency summary averages trial-level percentiles rather than calculating percentiles across all requests combined.
- Error counts should be read alongside latency and throughput.

These short local runs do not establish production capacity.

---

## Engineering Takeaways

### Measure before optimizing

The experiments showed that the largest improvement did not come from adding a cache. For this workload, connection pooling mattered much more.

### More concurrency is not automatically more throughput

Increasing concurrent work can increase contention and tail latency rather than continually increasing useful throughput.

### Optional dependencies should fail gracefully when practical

Redis improves the request path, but the service can continue through PostgreSQL when Redis is unavailable.

### Tail latency matters

Average latency alone does not describe the experience of slower requests, so the lab records p95 and p99 measurements as well.

### Performance claims need context

The README records workload size, concurrency, run count, and limitations so local benchmark results are not presented as production capacity.

---

## Limitations

- Results come from a small local item-lookup workload.
- Earlier experiment configurations require their corresponding historical code or setup to reproduce.
- Mocked tests do not replace integration testing with real services.
- Redis fallback does not protect against PostgreSQL failure.
- Metrics are exposed by the application; collecting and visualizing them requires separate monitoring infrastructure.

---

## Shutdown

Stop FastAPI with Ctrl+C, then stop the supporting containers:

```bash
docker compose down
```

The PostgreSQL data volume is preserved.

---

## Engineering Focus

This lab connects backend performance testing with reliability engineering by asking not only **how fast is the service?**, but also:

**What becomes the bottleneck? What happens under concurrency? What happens when a dependency fails? And how do we measure the result?**
