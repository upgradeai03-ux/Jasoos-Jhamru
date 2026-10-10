"""
WasteGuard AI - Video Simulation Engine
Processes video streams, applies segregation rules, manages play/pause/stop state,
and deduplicates event logging so consecutive video frames don't generate duplicate records.
"""

import os
import cv2
import time
import numpy as np
from typing import Dict, Any, List, Optional, Callable


class VideoProcessor:
    def __init__(
        self,
        detector,
        segregation_engine,
        event_logger,
        alert_engine,
        snapshot_dir: str = "snapshots"
    ):
        self.detector = detector
        self.segregation_engine = segregation_engine
        self.event_logger = event_logger
        self.alert_engine = alert_engine
        self.snapshot_dir = snapshot_dir

        self.is_playing = False
        self.is_paused = False
        self.current_frame_idx = 0
        self.total_frames = 0
        self.cap = None

        # Tracking state to deduplicate consecutive frame events
        self.last_logged_class: Optional[str] = None
        self.last_logged_time: float = 0.0
        self.dedup_interval_sec: float = 3.0

        os.makedirs(self.snapshot_dir, exist_ok=True)

    def load_video(self, video_path: str) -> bool:
        """Loads a video file for simulation."""
        if not os.path.exists(video_path):
            return False

        if self.cap is not None:
            self.cap.release()

        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            return False

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame_idx = 0
        self.is_playing = True
        self.is_paused = False
        self.last_logged_class = None
        self.last_logged_time = 0.0
        return True

    def process_frame(
        self,
        selected_bin: str,
        conf_threshold: float,
        enable_alerts: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Reads and processes a single video frame.

        Returns:
            Dict containing annotated frame, detections, evaluations, and progress metrics.
        """
        if self.cap is None or not self.cap.isOpened():
            return None

        if self.is_paused or not self.is_playing:
            return None

        ret, frame = self.cap.read()
        if not ret:
            self.is_playing = False
            return None

        self.current_frame_idx += 1
        progress_pct = (self.current_frame_idx / self.total_frames * 100.0) if self.total_frames > 0 else 0.0

        # Run detector
        detections = self.detector.detect(frame, conf_threshold=conf_threshold)

        evaluations = []
        now = time.time()

        for det in detections:
            cls_name = det["class_name"]
            conf = det["confidence"]

            eval_res = self.segregation_engine.evaluate_detection(
                detected_class=cls_name,
                confidence=conf,
                selected_bin=selected_bin,
                confidence_threshold=conf_threshold
            )
            evaluations.append(eval_res)

            # Deduplication Check: Log event only if class changes OR dedup interval elapses
            should_log = (
                cls_name != self.last_logged_class or
                (now - self.last_logged_time) > self.dedup_interval_sec
            )

            if should_log:
                snapshot_path = None
                # Handle violation alert & snapshot
                alert_status = "Disabled"
                if eval_res["is_violation"]:
                    alert_res = self.alert_engine.trigger_violation_alert(cls_name, selected_bin)
                    alert_status = "Triggered" if alert_res["alert_played"] else "Suppressed"

                    # Save violation snapshot image
                    snap_filename = f"violation_vid_{int(now)}_{self.current_frame_idx}.jpg"
                    snapshot_path = os.path.join(self.snapshot_dir, snap_filename)
                    annotated_temp = self.detector.draw_overlays(frame, [det], [eval_res])
                    cv2.imwrite(snapshot_path, annotated_temp)
                else:
                    alert_status = "N/A"

                self.event_logger.log_event(
                    source_mode="Video Simulation",
                    detected_class=cls_name,
                    confidence=conf,
                    selected_bin=selected_bin,
                    rule_category=eval_res["category"],
                    rule_result=eval_res["status"],
                    alert_status=alert_status,
                    snapshot_path=snapshot_path
                )

                self.last_logged_class = cls_name
                self.last_logged_time = now

        # Draw overlays on frame
        annotated_frame = self.detector.draw_overlays(frame, detections, evaluations)

        return {
            "annotated_frame": annotated_frame,
            "raw_frame": frame,
            "detections": detections,
            "evaluations": evaluations,
            "current_frame": self.current_frame_idx,
            "total_frames": self.total_frames,
            "progress_pct": progress_pct
        }

    def pause(self) -> None:
        self.is_paused = True

    def resume(self) -> None:
        self.is_paused = False

    def stop(self) -> None:
        self.is_playing = False
        self.is_paused = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
