from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Distributed Systems Performance Lab is running"
    }


def test_cache_hit(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "get_cached_item",
        lambda item_id: {
            "item_id": item_id,
            "name": f"item-{item_id}",
        },
    )

    response = client.get("/items/1")

    assert response.status_code == 200
    assert response.json()["source"] == "redis"


def test_postgres_fallback(monkeypatch):
    monkeypatch.setattr(main_module, "get_cached_item", lambda item_id: None)
    monkeypatch.setattr(
        main_module,
        "fetch_item",
        lambda item_id: {
            "item_id": item_id,
            "name": f"item-{item_id}",
        },
    )
    monkeypatch.setattr(main_module, "cache_item", lambda item: None)

    response = client.get("/items/1")

    assert response.status_code == 200
    assert response.json()["source"] == "postgresql"


def test_missing_item(monkeypatch):
    monkeypatch.setattr(main_module, "get_cached_item", lambda item_id: None)
    monkeypatch.setattr(main_module, "fetch_item", lambda item_id: None)

    response = client.get("/items/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}
    