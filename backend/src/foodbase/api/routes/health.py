from fastapi import APIRouter

from foodbase.config import get_settings
from foodbase.db.health import check_database_health

router = APIRouter(tags=["system"])


@router.get("/health")
def healthcheck() -> dict[str, str | None]:
    settings = get_settings()
    is_healthy, error_message = check_database_health()
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "database": "ok" if is_healthy else "error",
        "database_error": error_message,
    }


@router.get("/health/db")
def database_healthcheck() -> dict[str, str | None]:
    is_healthy, error_message = check_database_health()
    return {
        "database": "ok" if is_healthy else "error",
        "error": error_message,
    }
