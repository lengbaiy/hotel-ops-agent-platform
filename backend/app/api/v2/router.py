from fastapi import APIRouter

from app.api.v2.capabilities import router as capabilities_router
from app.api.v2.dashboard import router as dashboard_router
from app.api.v2.ops import router as ops_router

api_v2_router = APIRouter(prefix="/api/v2")
api_v2_router.include_router(capabilities_router)
api_v2_router.include_router(dashboard_router)
api_v2_router.include_router(ops_router)
