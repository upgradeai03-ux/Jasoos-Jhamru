"""
WasteGuard AI - Dataset Testing & Evaluation Engine
Inspects dataset splits, loads ground-truth YOLO annotations, computes detection metrics
(Precision, Recall, IoU), and previews model predictions alongside ground-truth labels.
"""

import os
import cv2
import yaml
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

DEFAULT_DATASET_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "YOLO Waste Detection.v1-v1.yolov8"
)


class DatasetManager:
    def __init__(self, dataset_dir: str = DEFAULT_DATASET_DIR):
        self.dataset_dir = dataset_dir
        self.yaml_path = os.path.join(dataset_dir, "data.yaml")
        self.nc = 0
        self.class_names: List[str] = []
        self.is_valid = False
        self.load_dataset_config()

    def load_dataset_config(self) -> bool:
        """Loads and parses data.yaml metadata."""
        if not os.path.exists(self.yaml_path):
            self.is_valid = False
            return False

        with open(self.yaml_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

        self.nc = cfg.get("nc", 0)
        self.class_names = cfg.get("names", [])
        self.is_valid = True
        return True

    def get_split_images(self, split: str = "test") -> List[str]:
        """Returns list of image filenames available in specified dataset split."""
        split_dir = os.path.join(self.dataset_dir, split, "images")
        if not os.path.exists(split_dir):
            return []

        valid_exts = (".jpg", ".jpeg", ".png", ".bmp")
        return [f for f in os.listdir(split_dir) if f.lower().endswith(valid_exts)]

    def load_ground_truth(self, split: str, image_filename: str, img_shape: Tuple[int, int]) -> List[Dict[str, Any]]:
        """
        Loads ground-truth YOLO bounding boxes for a given image.

        Args:
            split: 'train', 'valid', or 'test'
            image_filename: Name of image file (e.g. '001.jpg')
            img_shape: (height, width) of image

        Returns:
            List of ground-truth box dicts:
            [
                {
                    "class_id": int,
                    "class_name": str,
                    "bbox": [x1, y1, x2, y2]
                }, ...
            ]
        """
        base_name = os.path.splitext(image_filename)[0]
        label_filename = f"{base_name}.txt"
        label_path = os.path.join(self.dataset_dir, split, "labels", label_filename)

        if not os.path.exists(label_path):
            return []

        h, w = img_shape[:2]
        ground_truths = []

        with open(label_path, "r", encoding="utf-8") as lf:
            for line in lf:
                parts = line.strip().split()
                if len(parts) == 5:
                    cls_id = int(parts[0])
                    cx, cy, bw, bh = map(float, parts[1:])

                    # Convert normalized YOLO coordinates to pixel coordinates
                    x1 = int((cx - bw / 2.0) * w)
                    y1 = int((cy - bh / 2.0) * h)
                    x2 = int((cx + bw / 2.0) * w)
                    y2 = int((cy + bh / 2.0) * h)

                    cls_name = self.class_names[cls_id] if cls_id < len(self.class_names) else f"Class_{cls_id}"

                    ground_truths.append({
                        "class_id": cls_id,
                        "class_name": cls_name,
                        "bbox": [x1, y1, x2, y2]
                    })

        return ground_truths

    def draw_ground_truth_overlay(self, image: np.ndarray, ground_truths: List[Dict[str, Any]]) -> np.ndarray:
        """Draws distinct PURPLE bounding boxes for ground-truth annotations."""
        annotated = image.copy()

        for gt in ground_truths:
            x1, y1, x2, y2 = gt["bbox"]
            cls_name = gt["class_name"]

            color = (255, 0, 255)  # Purple (BGR)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            label_str = f"GT: {cls_name}"
            cv2.putText(
                annotated,
                label_str,
                (x1 + 5, max(15, y1 - 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )

        return annotated

    @staticmethod
    def compute_iou(boxA: List[int], boxB: List[int]) -> float:
        """Calculates Intersection over Union (IoU) between two bounding boxes [x1, y1, x2, y2]."""
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
        return float(iou)

    def evaluate_image_detections(
        self,
        predictions: List[Dict[str, Any]],
        ground_truths: List[Dict[str, Any]],
        iou_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Evaluates predictions against ground truth for a single image.

        Returns:
            Dict containing Precision, Recall, True Positives (TP), False Positives (FP), False Negatives (FN).
        """
        if not ground_truths:
            return {
                "tp": 0,
                "fp": len(predictions),
                "fn": 0,
                "precision": 0.0,
                "recall": 0.0,
                "note": "No ground truth available for this image."
            }

        matched_gt = set()
        tp = 0
        fp = 0

        for pred in predictions:
            best_iou = 0.0
            best_gt_idx = -1

            for idx, gt in enumerate(ground_truths):
                if pred["class_id"] == gt["class_id"]:
                    iou = self.compute_iou(pred["bbox"], gt["bbox"])
                    if iou > best_iou:
                        best_iou = iou
                        best_gt_idx = idx

            if best_iou >= iou_threshold and best_gt_idx not in matched_gt:
                tp += 1
                matched_gt.add(best_gt_idx)
            else:
                fp += 1

        fn = len(ground_truths) - len(matched_gt)
        precision = tp / float(tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / float(tp + fn) if (tp + fn) > 0 else 0.0

        return {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "mean_iou": round(best_iou, 3) if predictions else 0.0
        }
