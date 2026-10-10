"""
WasteGuard AI - Dataset Lab Inspection Endpoints
"""

import os
import cv2
import base64
from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/api/dataset", tags=["Dataset Lab"])

def get_router(dataset_mgr, detector, seg_engine):
    @router.get("/summary")
    def get_dataset_summary():
        return {
            "is_valid": dataset_mgr.is_valid,
            "num_classes": dataset_mgr.nc,
            "class_names": dataset_mgr.class_names,
            "splits": {
                "train": len(dataset_mgr.get_split_images("train")),
                "valid": len(dataset_mgr.get_split_images("valid")),
                "test": len(dataset_mgr.get_split_images("test"))
            }
        }

    @router.get("/images")
    def get_split_images(split: str = Query("test")):
        return {
            "split": split,
            "images": dataset_mgr.get_split_images(split)[:100]
        }

    @router.get("/inspect")
    def inspect_dataset_image(
        split: str = Query("test"),
        image_name: str = Query(...),
        selected_bin: str = Query("Dry Waste"),
        confidence_threshold: float = Query(0.35)
    ):
        img_path = os.path.join(dataset_mgr.dataset_dir, split, "images", image_name)
        if not os.path.exists(img_path):
            raise HTTPException(status_code=404, detail=f"Image '{image_name}' not found in split '{split}'.")

        img_bgr = cv2.imread(img_path)
        if img_bgr is None:
            raise HTTPException(status_code=400, detail="Failed to read dataset image.")

        gt_boxes = dataset_mgr.load_ground_truth(split, image_name, img_bgr.shape)
        preds = detector.detect(img_bgr, conf_threshold=confidence_threshold)

        evaluations = []
        for p in preds:
            eval_res = seg_engine.evaluate_detection(p["class_name"], p["confidence"], selected_bin, confidence_threshold)
            evaluations.append(eval_res)

        pred_overlay = detector.draw_overlays(img_bgr, preds, evaluations)
        gt_overlay = dataset_mgr.draw_ground_truth_overlay(img_bgr, gt_boxes)

        _, pred_buf = cv2.imencode('.jpg', pred_overlay)
        _, gt_buf = cv2.imencode('.jpg', gt_overlay)

        pred_b64 = f"data:image/jpeg;base64,{base64.b64encode(pred_buf).decode('utf-8')}"
        gt_b64 = f"data:image/jpeg;base64,{base64.b64encode(gt_buf).decode('utf-8')}"

        metrics = dataset_mgr.evaluate_image_detections(preds, gt_boxes)

        return {
            "image_name": image_name,
            "split": split,
            "prediction_overlay_base64": pred_b64,
            "ground_truth_overlay_base64": gt_b64,
            "metrics": metrics,
            "predictions": preds,
            "ground_truths": gt_boxes
        }

    return router
