"""
WasteGuard AI - Analytics & Trends Endpoints
"""

from fastapi import APIRouter
from backend.schemas.models import AnalyticsSummaryResponse
from typing import Dict, Any

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Trends"])

def get_router(event_logger):
    @router.get("", response_model=Dict[str, Any])
    def get_analytics():
        summary = event_logger.get_analytics_summary()
        df = event_logger.get_events(limit=5000)

        class_counts = {}
        result_counts = {}

        if not df.empty:
            class_counts = df["detected_class"].value_counts().to_dict()
            result_counts = df["rule_result"].value_counts().to_dict()

        return {
            "summary": summary,
            "class_distribution": class_counts,
            "result_distribution": result_counts
        }

    return router
