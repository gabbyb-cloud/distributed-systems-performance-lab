import time

from fastapi import FastAPI, HTTPException, Request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from app.cache import cache_item, get_cached_item
from app.database import fetch_item
from app.metrics import (
    POSTGRES_FALLBACKS,
    REQUEST_COUNT,
    REQUEST_LATENCY,
)

app = FastAPI()


@app.middleware("http")
async def track_requests(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    if request.url.path != "/metrics":
        REQUEST_COUNT.inc()
        REQUEST_LATENCY.observe(time.perf_counter() - start)

    return response


@app.get("/")
def root():
    return {"message": "Distributed Systems Performance Lab is running"}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    cached_item = get_cached_item(item_id)

    if cached_item is not None:
        cached_item["source"] = "redis"
        return cached_item

    POSTGRES_FALLBACKS.inc()

    item = fetch_item(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    cache_item(item)

    item["source"] = "postgresql"
    return item


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )



