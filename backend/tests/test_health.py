from fastapi.testclient import TestClient

from foodbase.api.routes import health as health_route
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
    health_route.check_database_health = lambda: (True, None)  # type: ignore[assignment]
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "Foodbase API"
    assert payload["database"] == "ok"


def test_database_healthcheck_endpoint_reports_error() -> None:
    health_route.check_database_health = lambda: (False, "db unavailable")  # type: ignore[assignment]
    client = TestClient(app)

    response = client.get("/api/health/db")

    assert response.status_code == 200
    assert response.json() == {
        "database": "error",
        "error": "db unavailable",
    }
