"""
WasteGuard AI - Unit Tests for Segregation Rule Engine
Compatible with standard unittest and pytest.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.segregation import SegregationEngine


class TestSegregationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SegregationEngine()

    def test_wet_waste_correct_disposal(self):
        res = self.engine.evaluate_detection("Organic", confidence=0.85, selected_bin="Wet Waste", confidence_threshold=0.35)
        self.assertEqual(res["status"], "Correct Disposal")
        self.assertTrue(res["is_correct"])
        self.assertFalse(res["is_violation"])
        self.assertEqual(res["category"], "Wet Waste")

    def test_dry_waste_violation_in_wet_bin(self):
        res = self.engine.evaluate_detection("Cardboard", confidence=0.90, selected_bin="Wet Waste", confidence_threshold=0.35)
        self.assertEqual(res["status"], "Confirmed Violation")
        self.assertTrue(res["is_violation"])
        self.assertFalse(res["is_correct"])
        self.assertEqual(res["category"], "Dry Waste")

    def test_low_confidence_needs_review(self):
        res = self.engine.evaluate_detection("Plastic bottle", confidence=0.20, selected_bin="Dry Waste", confidence_threshold=0.50)
        self.assertEqual(res["status"], "Uncertain")
        self.assertTrue(res["is_uncertain"])
        self.assertEqual(res["category"], "Needs Review")

    def test_hazardous_or_unknown_class_needs_review(self):
        res = self.engine.evaluate_detection("Electronics", confidence=0.88, selected_bin="Dry Waste")
        self.assertEqual(res["status"], "Needs Review")
        self.assertTrue(res["is_uncertain"])
        self.assertEqual(res["category"], "Needs Review")

    def test_unmapped_unknown_class(self):
        res = self.engine.evaluate_detection("UnregisteredAlienItem", confidence=0.95, selected_bin="Dry Waste")
        self.assertEqual(res["status"], "Needs Review")
        self.assertEqual(res["category"], "Needs Review")


if __name__ == "__main__":
    unittest.main()
