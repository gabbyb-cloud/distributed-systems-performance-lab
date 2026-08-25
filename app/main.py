from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Distributed Systems Performance Lab is running"}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {
        "item_id": item_id,
        "name": f"item-{item_id}",
        "source": "application",
    }

