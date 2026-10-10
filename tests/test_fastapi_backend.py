"""
WasteGuard AI - Automated Test Suite for FastAPI Backend Endpoints
Tests health, model status, dataset inspection, event history, and image upload inference.
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.main import app


class TestFastAPIBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("timestamp", data)

    def test_model_status_endpoint(self):
        response = self.client.get("/api/model/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("is_loaded", data)
        self.assertIn("total_classes", data)

    def test_events_endpoint(self):
        response = self.client.get("/api/events?limit=5")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_analytics_endpoint(self):
        response = self.client.get("/api/analytics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("summary", data)
        self.assertIn("total_events", data["summary"])

    def test_dataset_summary_endpoint(self):
        response = self.client.get("/api/dataset/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_valid"])
        self.assertEqual(data["num_classes"], 42)
        self.assertEqual(data["splits"]["test"], 546)

    def test_invalid_image_upload_extension(self):
        files = {"file": ("malicious.exe", b"not-an-image", "application/octet-stream")}
        response = self.client.post("/api/detect/image", files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported image format", response.json()["detail"])

    def test_valid_dataset_image_detection(self):
        # Pick a sample image from the verified test split
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_img_dir = os.path.join(project_root, "YOLO Waste Detection.v1-v1.yolov8", "test", "images")
        test_images = [f for f in os.listdir(test_img_dir) if f.endswith(".jpg")]
        
        self.assertGreater(len(test_images), 0, "No test images found in dataset!")
        sample_img_path = os.path.join(test_img_dir, test_images[0])

        with open(sample_img_path, "rb") as f:
            img_bytes = f.read()

        files = {"file": (test_images[0], img_bytes, "image/jpeg")}
        data = {"selected_bin": "Dry Waste", "confidence_threshold": "0.30", "log_event": "true"}

        response = self.client.post("/api/detect/image", files=files, data=data)
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertTrue(res_data["success"])
        self.assertIn("detections", res_data)
        self.assertIn("annotated_image_base64", res_data)
        self.assertIn("inference_time_ms", res_data)


if __name__ == "__main__":
    unittest.main()
