"""
WasteGuard AI - Unit Tests for SQLite Event Logger & Persistence
Compatible with standard unittest and pytest.
"""

import os
import sys
import tempfile
import unittest
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.event_logger import EventLogger


class TestEventLogger(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.logger = EventLogger(db_path=self.temp_db.name)

    def tearDown(self):
        del self.logger
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except PermissionError:
                pass  # Ignore Windows transient file lock on temp cleanup

    def test_log_and_retrieve_event(self):
        row_id = self.logger.log_event(
            source_mode="Dataset Testing",
            detected_class="Paper cups",
            confidence=0.92,
            selected_bin="Dry Waste",
            rule_category="Dry Waste",
            rule_result="Correct Disposal",
            alert_status="N/A"
        )
        self.assertGreater(row_id, 0)

        df = self.logger.get_events(limit=10)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["detected_class"], "Paper cups")
        self.assertEqual(df.iloc[0]["rule_result"], "Correct Disposal")

    def test_analytics_summary(self):
        self.logger.log_event("Live Camera", "Organic", 0.9, "Wet Waste", "Wet Waste", "Correct Disposal", "N/A")
        self.logger.log_event("Live Camera", "Plastic bottle", 0.85, "Wet Waste", "Dry Waste", "Confirmed Violation", "Triggered")
        self.logger.log_event("Live Camera", "Electronics", 0.70, "Dry Waste", "Needs Review", "Needs Review", "N/A")

        summary = self.logger.get_analytics_summary()
        self.assertEqual(summary["total_events"], 3)
        self.assertEqual(summary["correct_events"], 1)
        self.assertEqual(summary["confirmed_violations"], 1)
        self.assertEqual(summary["needs_review_events"], 1)
        self.assertEqual(summary["violation_rate_pct"], 33.3)

    def test_csv_export(self):
        self.logger.log_event("Video Simulation", "Glass bottle", 0.88, "Dry Waste", "Dry Waste", "Correct Disposal", "N/A")
        temp_csv = tempfile.NamedTemporaryFile(suffix=".csv", delete=False).name

        exported_path = self.logger.export_csv(temp_csv)
        self.assertTrue(os.path.exists(exported_path))

        exported_df = pd.read_csv(exported_path)
        self.assertEqual(len(exported_df), 1)
        self.assertEqual(exported_df.iloc[0]["detected_class"], "Glass bottle")
        if os.path.exists(temp_csv):
            try:
                os.remove(temp_csv)
            except PermissionError:
                pass


if __name__ == "__main__":
    unittest.main()
