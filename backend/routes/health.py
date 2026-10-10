"""
WasteGuard AI - Health & System Status Endpoints
"""

from fastapi import APIRouter
from datetime import datetime
from backend.schemas.models import HealthResponse, ModelStatusResponse

router = APIRouter(prefix="/api", tags=["Health & Status"])

def get_router(detector):
    @router.get("/health", response_model=HealthResponse)
    def check_health():
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }

    @router.get("/model/status", response_model=ModelStatusResponse)
    def check_model_status():
        names_list = list(detector.class_names.values()) if detector.class_names else []
        return {
            "is_loaded": detector.is_loaded,
            "model_name": detector.model_name,
            "model_path": detector.model_path or "None",
            "total_classes": len(names_list),
            "class_names": names_list,
            "load_error": detector.load_error_msg
        }

    return router
