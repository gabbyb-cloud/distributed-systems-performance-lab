from fastapi import FastAPI, HTTPException

from app.database import fetch_item

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Distributed Systems Performance Lab is running"}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = fetch_item(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


