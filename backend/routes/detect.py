"""
WasteGuard AI - Image & Video Detection Endpoints
Handles multipart/form-data upload, file size & type validation, OpenCV decoding,
YOLO inference, segregation rule engine evaluation, and Base64 preview generation.
"""

import os
import cv2
import time
import base64
import numpy as np
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from backend.schemas.models import ImageDetectionResponse, DetectionItem

router = APIRouter(prefix="/api/detect", tags=["Detection Pipeline"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB limit

def get_router(detector, seg_engine, event_logger, alert_engine):
    @router.post("/image", response_model=ImageDetectionResponse)
    async def detect_image(
        file: UploadFile = File(...),
        selected_bin: str = Form("Dry Waste"),
        confidence_threshold: float = Form(0.35),
        log_event: bool = Form(True)
    ):
        start_time = time.time()

        # 1. Validate File Extension
        ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image format '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # 2. Read File Bytes & Validate File Size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum limit of 15MB. Provided size: {len(contents)/(1024*1024):.2f}MB"
            )

        # 3. Safe Image Decoding
        np_arr = np.frombuffer(contents, np.uint8)
        img_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img_bgr is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Corrupted image file or invalid image data stream."
            )

        h, w = img_bgr.shape[:2]

        # 4. Model Status Check
        if not detector.is_loaded:
            # Fallback or error if model isn't available
            if detector.load_error_msg:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Detection model unavailable: {detector.load_error_msg}"
                )

        # 5. Run Object Detector
        raw_detections = detector.detect(img_bgr, conf_threshold=confidence_threshold)

        detection_items = []
        evaluations = []
        has_violation = False

        for det in raw_detections:
            cls_name = det["class_name"]
            conf = det["confidence"]

            eval_res = seg_engine.evaluate_detection(
                detected_class=cls_name,
                confidence=conf,
                selected_bin=selected_bin,
                confidence_threshold=confidence_threshold
            )
            evaluations.append(eval_res)

            if eval_res["is_violation"]:
                has_violation = True
                alert_status = "Triggered"
            elif eval_res["is_correct"]:
                alert_status = "N/A"
            else:
                alert_status = "Suppressed"

            # Log to SQLite Event History
            if log_event:
                event_logger.log_event(
                    source_mode="Image Upload",
                    detected_class=cls_name,
                    confidence=conf,
                    selected_bin=selected_bin,
                    rule_category=eval_res["category"],
                    rule_result=eval_res["status"],
                    alert_status=alert_status
                )

            item = DetectionItem(
                class_id=det["class_id"],
                class_name=cls_name,
                confidence=round(conf, 4),
                bbox=det["bbox"],
                category=eval_res["category"],
                status=eval_res["status"],
                is_violation=eval_res["is_violation"],
                is_correct=eval_res["is_correct"],
                is_uncertain=eval_res["is_uncertain"],
                reason=eval_res["reason"]
            )
            detection_items.append(item)

        # 6. Generate Base64 Annotated Image Overlay
        annotated_bgr = detector.draw_overlays(img_bgr, raw_detections, evaluations)
        _, buffer = cv2.imencode('.jpg', annotated_bgr)
        base64_str = base64.b64encode(buffer).decode('utf-8')
        annotated_data_url = f"data:image/jpeg;base64,{base64_str}"

        inference_time_ms = round((time.time() - start_time) * 1000.0, 2)

        return ImageDetectionResponse(
            success=True,
            detections=detection_items,
            total_detected=len(detection_items),
            inference_time_ms=inference_time_ms,
            selected_bin=selected_bin,
            has_violation=has_violation,
            annotated_image_base64=annotated_data_url,
            image_dimensions=[w, h],
            model_name=detector.model_name
        )

    return router
