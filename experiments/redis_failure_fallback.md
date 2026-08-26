# Redis Failure Fallback

- Requests per run: 200
- Concurrency: 10
- Runs: 6
- Redis: unavailable
- PostgreSQL connection pool: enabled
- Redis retries: disabled
- Redis connect/read timeout: 0.1 seconds

## Average Results

- Throughput: 395.10 req/s
- Average latency: 24.87 ms
- p50: 24.08 ms
- p95: 40.82 ms
- p99: 50.54 ms
- Errors: 0

## Failure Behavior

Before fail-fast configuration, a Redis outage caused fallback requests to take about 8.3 seconds.

After disabling Redis retries and adding short socket timeouts, a single fallback request completed in about 0.022 seconds.

The API remained available and fell back to PostgreSQL during the Redis outage.
