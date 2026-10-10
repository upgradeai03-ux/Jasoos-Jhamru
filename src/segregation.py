"""
WasteGuard AI - Segregation Rule Engine Module
Implements configurable mappings for Wet Waste, Dry Waste, and Needs Review rules,
confidence thresholding, consecutive-frame confirmation, and bin conflict detection.
"""

import os
import yaml
from typing import Dict, Any, List, Optional

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "configs", "segregation_rules.yaml"
)

class SegregationEngine:
    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        self.config_path = config_path
        self.categories: Dict[str, List[str]] = {}
        self.class_to_category: Dict[str, str] = {}
        self.settings: Dict[str, Any] = {
            "default_confidence_threshold": 0.35,
            "consecutive_frames_required": 2,
            "alert_cooldown_seconds": 5.0,
            "snapshot_violations": True
        }
        self.frame_history: List[str] = []
        self.load_config()

    def load_config(self) -> None:
        """Load segregation mappings and settings from YAML configuration file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Segregation rules config not found at: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

        raw_categories = cfg.get("categories", {})
        self.categories = {
            "Wet Waste": [item.strip() for item in raw_categories.get("wet_waste", [])],
            "Dry Waste": [item.strip() for item in raw_categories.get("dry_waste", [])],
            "Needs Review": [item.strip() for item in raw_categories.get("needs_review", [])]
        }

        # Build reverse lookup map (case-insensitive for robustness)
        self.class_to_category = {}
        for cat_name, item_list in self.categories.items():
            for item in item_list:
                self.class_to_category[item.lower()] = cat_name

        if "settings" in cfg and isinstance(cfg["settings"], dict):
            self.settings.update(cfg["settings"])

    def evaluate_detection(
        self,
        detected_class: str,
        confidence: float,
        selected_bin: str,
        confidence_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a single detected object against the selected disposal bin.

        Args:
            detected_class: Name of detected class from YOLO
            confidence: Confidence score (0.0 to 1.0)
            selected_bin: Bin selected by operator ("Wet Waste" or "Dry Waste")
            confidence_threshold: Optional override threshold

        Returns:
            Dict containing classification results, violation state, and explanatory rule message.
        """
        threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else float(self.settings.get("default_confidence_threshold", 0.35))
        )

        norm_class = detected_class.strip().lower()
        cat_name = self.class_to_category.get(norm_class, "Needs Review")

        # Low confidence check
        if confidence < threshold:
            return {
                "detected_class": detected_class,
                "confidence": confidence,
                "category": "Needs Review",
                "selected_bin": selected_bin,
                "status": "Uncertain",
                "is_correct": False,
                "is_violation": False,
                "is_uncertain": True,
                "reason": f"Low confidence ({confidence:.2f} < threshold {threshold:.2f}). Marked Needs Review."
            }

        # Unmapped or hazardous check
        if cat_name == "Needs Review":
            return {
                "detected_class": detected_class,
                "confidence": confidence,
                "category": "Needs Review",
                "selected_bin": selected_bin,
                "status": "Needs Review",
                "is_correct": False,
                "is_violation": False,
                "is_uncertain": True,
                "reason": f"Class '{detected_class}' requires special handling or manual review."
            }

        # Correct bin matching
        if cat_name.lower() == selected_bin.strip().lower():
            return {
                "detected_class": detected_class,
                "confidence": confidence,
                "category": cat_name,
                "selected_bin": selected_bin,
                "status": "Correct Disposal",
                "is_correct": True,
                "is_violation": False,
                "is_uncertain": False,
                "reason": f"Correct disposal! '{detected_class}' is classified as {cat_name}."
            }
        else:
            # Confirmed Bin Misplacement / Violation
            return {
                "detected_class": detected_class,
                "confidence": confidence,
                "category": cat_name,
                "selected_bin": selected_bin,
                "status": "Confirmed Violation",
                "is_correct": False,
                "is_violation": True,
                "is_uncertain": False,
                "reason": f"VIOLATION: '{detected_class}' is {cat_name}, but was placed in {selected_bin}!"
            }

    def evaluate_consecutive_frames(
        self,
        recent_classes: List[str],
        selected_bin: str,
        confidence: float,
        confidence_threshold: float
    ) -> Dict[str, Any]:
        """
        Requires N consecutive detections of the same class before confirming a violation.
        Prevents flickering / transient single-frame false alerts.
        """
        required_n = int(self.settings.get("consecutive_frames_required", 2))
        if len(recent_classes) < required_n:
            return {
                "status": "Pending Confirmation",
                "is_violation": False,
                "reason": f"Gathering frame history ({len(recent_classes)}/{required_n})."
            }

        # Check if all last N frames detect the same class
        last_n = recent_classes[-required_n:]
        if len(set(last_n)) == 1:
            detected_class = last_n[0]
            return self.evaluate_detection(detected_class, confidence, selected_bin, confidence_threshold)
        else:
            return {
                "status": "Uncertain",
                "is_violation": False,
                "reason": "Detection unstable across consecutive frames."
            }
