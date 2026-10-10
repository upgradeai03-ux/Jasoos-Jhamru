"""
WasteGuard AI - Unit Tests for Alert Engine & Cooldown Logic
Compatible with standard unittest and pytest.
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.alerts import AlertEngine


class TestAlertEngine(unittest.TestCase):
    def test_alert_trigger_and_cooldown(self):
        alert_sys = AlertEngine(cooldown_seconds=1.0, enabled=True)

        # First trigger
        res1 = alert_sys.trigger_violation_alert("Plastic bottle", "Wet Waste")
        self.assertTrue(res1["visual_warning"])

        # Immediate second trigger should be suppressed by cooldown
        res2 = alert_sys.trigger_violation_alert("Plastic bottle", "Wet Waste")
        self.assertFalse(res2["alert_played"])
        self.assertIn("cooldown active", res2["reason"].lower())

        # Wait for cooldown to expire
        time.sleep(1.1)
        res3 = alert_sys.trigger_violation_alert("Plastic bottle", "Wet Waste")
        self.assertTrue(res3["visual_warning"])

    def test_disabled_alert_system(self):
        alert_sys = AlertEngine(cooldown_seconds=5.0, enabled=False)
        res = alert_sys.trigger_violation_alert("Plastic bottle", "Wet Waste")
        self.assertFalse(res["alert_played"])
        self.assertIn("disabled", res["reason"].lower())
        self.assertTrue(res["visual_warning"])


if __name__ == "__main__":
    unittest.main()
