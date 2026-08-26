# Redis Cache Hits

- Requests per run: 200
- Concurrency: 10
- Runs: 5
- PostgreSQL connection pool: enabled
- Redis cache: enabled

## Average Results

- Throughput: 652.08 req/s
- Average latency: 15.38 ms
- p50: 13.05 ms
- p95: 33.27 ms
- p99: 48.29 ms
- Errors: 0

## Comparison to Pooled PostgreSQL

- Throughput increased by 1.8%
- Average latency was effectively unchanged
- p50 decreased by 5.0%
- p95 increased by 16.4%
- p99 increased by 24.7%

Redis did not materially outperform pooled PostgreSQL for this small local primary-key lookup workload.
