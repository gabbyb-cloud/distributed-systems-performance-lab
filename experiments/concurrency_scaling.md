# Concurrency Scaling

- Requests per trial: 200
- Trials per level: 5
- Concurrency levels: 1, 10, 25, 50
- Redis cache: enabled
- PostgreSQL connection pool: enabled
- Errors across measured requests: 0

## Results

| Concurrency | Throughput | Avg Latency | p95 | p99 |
|---|---:|---:|---:|---:|
| 1 | 319.29 req/s | 3.18 ms | 5.26 ms | 6.98 ms |
| 10 | 373.96 req/s | 25.87 ms | 58.29 ms | 89.03 ms |
| 25 | 305.26 req/s | 79.81 ms | 209.81 ms | 303.22 ms |
| 50 | 302.79 req/s | 151.44 ms | 448.64 ms | 561.31 ms |

## Observation

Throughput peaked around concurrency 10 in this local environment. Increasing concurrency beyond that reduced throughput while sharply increasing tail latency, indicating saturation and request queueing.
