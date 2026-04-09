from fastapi import APIRouter

from foodbase.api.routes.ai import router as ai_router
from foodbase.api.routes.health import router as health_router
from foodbase.api.routes.organizations import router as organizations_router
from foodbase.api.routes.reference_data import router as reference_data_router

api_router = APIRouter()
api_router.include_router(ai_router)
api_router.include_router(health_router)
api_router.include_router(organizations_router)
api_router.include_router(reference_data_router)
