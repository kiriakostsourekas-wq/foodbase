from fastapi.testclient import TestClient

from foodbase.main import app


def test_root_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Foodbase API is running.",
        "docs_url": "/docs",
    }


def test_healthcheck_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "Foodbase API"
