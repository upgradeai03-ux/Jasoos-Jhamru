"""
WasteGuard AI - Event Log & CSV Export Endpoints
"""

import os
from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from typing import List, Optional
from backend.schemas.models import EventRecord

router = APIRouter(prefix="/api/events", tags=["Event Log & History"])

def get_router(event_logger):
    @router.get("", response_model=List[EventRecord])
    def get_events(
        limit: int = Query(200, ge=1, le=5000),
        source_mode: Optional[str] = Query(None),
        rule_result: Optional[str] = Query(None)
    ):
        df = event_logger.get_events(limit=limit, source_mode=source_mode, rule_result=rule_result)
        if df.empty:
            return []
        
        records = df.to_dict(orient="records")
        return records

    @router.get("/export")
    def export_events_csv():
        export_path = os.path.join("logs", "wasteguard_export.csv")
        event_logger.export_csv(export_path)
        
        return FileResponse(
            path=export_path,
            filename="wasteguard_event_history.csv",
            media_type="text/csv"
        )

    return router
