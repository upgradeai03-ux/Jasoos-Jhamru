"""
WasteGuard AI - Configuration Endpoints
"""

from fastapi import APIRouter
from backend.schemas.models import SegregationConfigResponse

router = APIRouter(prefix="/api/config", tags=["Configuration"])

def get_router(seg_engine):
    @router.get("/segregation", response_model=SegregationConfigResponse)
    def get_segregation_config():
        return {
            "categories": seg_engine.categories,
            "settings": seg_engine.settings
        }

    return router
