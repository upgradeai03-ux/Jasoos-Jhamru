"""
WasteGuard AI - FastAPI Backend Server
Main entrypoint initializing services, middleware, and API routes.
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure parent directory is in Python path for importing src modules
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.detector import WasteDetector
from src.segregation import SegregationEngine
from src.alerts import AlertEngine
from src.event_logger import EventLogger
from src.dataset_manager import DatasetManager

# Import route modules
from backend.routes import health, detect, events, analytics, dataset, config

# Initialize Core Services
seg_engine = SegregationEngine()
event_logger = EventLogger()
alert_engine = AlertEngine(cooldown_seconds=seg_engine.settings.get("alert_cooldown_seconds", 5.0))
dataset_mgr = DatasetManager()

# Discover & Load YOLO Model
available_models = WasteDetector.discover_models()
model_path = available_models[0]["path"] if available_models else "yolov8n.pt"
detector = WasteDetector(model_path)

# Initialize FastAPI App
app = FastAPI(
    title="WasteGuard AI API",
    description="Real-Time AI Waste Segregation & Compliance Backend Service",
    version="1.0.0"
)

# CORS Configuration for local frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(health.get_router(detector))
app.include_router(detect.get_router(detector, seg_engine, event_logger, alert_engine))
app.include_router(events.get_router(event_logger))
app.include_router(analytics.get_router(event_logger))
app.include_router(dataset.get_router(dataset_mgr, detector, seg_engine))
app.include_router(config.get_router(seg_engine))

@app.get("/")
def read_root():
    return {
        "app": "WasteGuard AI Backend API",
        "status": "online",
        "docs_url": "/docs",
        "model_loaded": detector.is_loaded,
        "model_name": detector.model_name
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
