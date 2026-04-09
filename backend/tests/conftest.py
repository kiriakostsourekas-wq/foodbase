import pytest
from fastapi.testclient import TestClient

from foodbase.config import get_settings
from foodbase.db.session import get_db_session, reset_db_caches
from foodbase.main import app


class DummySession:
    pass


@pytest.fixture(autouse=True)
def reset_caches() -> None:
    get_settings.cache_clear()
    reset_db_caches()
    yield
    app.dependency_overrides.clear()
    get_settings.cache_clear()
    reset_db_caches()


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_db_session] = lambda: DummySession()
    with TestClient(app) as test_client:
        yield test_client
