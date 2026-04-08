from fastapi import FastAPI

from foodbase.api.router import api_router
from foodbase.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @app.get("/", tags=["system"])
    def root() -> dict[str, str]:
        return {
            "message": "Foodbase API is running.",
            "docs_url": "/docs",
        }

    app.include_router(api_router, prefix="/api")
    return app


app = create_app()
