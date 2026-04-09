from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", tags=["system"])
    def root() -> dict[str, str]:
        return {
            "message": "Foodbase API is running.",
            "docs_url": "/docs",
        }

    app.include_router(api_router, prefix=settings.normalized_api_prefix)
    return app


app = create_app()
