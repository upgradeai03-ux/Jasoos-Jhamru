"""
WasteGuard AI - Pydantic Request & Response Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DetectionItem(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: List[int]  # [x1, y1, x2, y2]
    category: str    # "Wet Waste", "Dry Waste", "Needs Review"
    status: str      # "Correct Disposal", "Confirmed Violation", "Needs Review", "Uncertain"
    is_violation: bool
    is_correct: bool
    is_uncertain: bool
    reason: str

class ImageDetectionResponse(BaseModel):
    success: bool
    detections: List[DetectionItem]
    total_detected: int
    inference_time_ms: float
    selected_bin: str
    has_violation: bool
    annotated_image_base64: Optional[str] = None
    image_dimensions: List[int] # [width, height]
    model_name: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str = "1.0.0"

class ModelStatusResponse(BaseModel):
    is_loaded: bool
    model_name: str
    model_path: str
    total_classes: int
    class_names: List[str]
    load_error: Optional[str] = None

class AnalyticsSummaryResponse(BaseModel):
    total_events: int
    correct_events: int
    confirmed_violations: int
    needs_review_events: int
    violation_rate_pct: float

class EventRecord(BaseModel):
    event_id: int
    timestamp: str
    source_mode: str
    detected_class: str
    confidence: float
    selected_bin: str
    rule_category: str
    rule_result: str
    alert_status: str
    snapshot_path: Optional[str] = None

class SegregationConfigResponse(BaseModel):
    categories: Dict[str, List[str]]
    settings: Dict[str, Any]
