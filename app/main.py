from fastapi import FastAPI, HTTPException

from app.cache import cache_item, get_cached_item
from app.database import fetch_item

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Distributed Systems Performance Lab is running"}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    cached_item = get_cached_item(item_id)

    if cached_item is not None:
        cached_item["source"] = "redis"
        return cached_item

    item = fetch_item(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    cache_item(item)

    item["source"] = "postgresql"
    return item


