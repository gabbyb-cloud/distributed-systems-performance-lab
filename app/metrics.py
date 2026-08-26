from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of API requests",
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "API request latency in seconds",
)

CACHE_HITS = Counter(
    "app_cache_hits_total",
    "Total Redis cache hits",
)

CACHE_MISSES = Counter(
    "app_cache_misses_total",
    "Total Redis cache misses",
)

CACHE_ERRORS = Counter(
    "app_cache_errors_total",
    "Total Redis errors",
)

POSTGRES_FALLBACKS = Counter(
    "app_postgres_fallbacks_total",
    "Requests served by PostgreSQL after cache miss or Redis failure",
)
