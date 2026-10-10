"""
WasteGuard AI - SQLite Event Storage & Analytics Engine
Stores event history, handles deduplication, provides analytics queries, and exports to CSV.
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "logs", "wasteguard_events.db"
)


class EventLogger:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Initializes SQLite events table if it does not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    source_mode TEXT NOT NULL,
                    detected_class TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    selected_bin TEXT NOT NULL,
                    rule_category TEXT NOT NULL,
                    rule_result TEXT NOT NULL,
                    alert_status TEXT NOT NULL,
                    snapshot_path TEXT
                )
            """)
            conn.commit()

    def log_event(
        self,
        source_mode: str,
        detected_class: str,
        confidence: float,
        selected_bin: str,
        rule_category: str,
        rule_result: str,
        alert_status: str,
        snapshot_path: Optional[str] = None
    ) -> int:
        """Inserts a single waste disposal event into SQLite storage."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO waste_events (
                    timestamp, source_mode, detected_class, confidence,
                    selected_bin, rule_category, rule_result, alert_status, snapshot_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                now_str, source_mode, detected_class, float(confidence),
                selected_bin, rule_category, rule_result, alert_status, snapshot_path
            ))
            conn.commit()
            return cursor.lastrowid

    def get_events(
        self,
        limit: int = 500,
        source_mode: Optional[str] = None,
        rule_result: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetches stored events as a Pandas DataFrame for dashboard rendering and analytics."""
        query = "SELECT * FROM waste_events"
        params = []
        conditions = []

        if source_mode:
            conditions.append("source_mode = ?")
            params.append(source_mode)
        if rule_result:
            conditions.append("rule_result = ?")
            params.append(rule_result)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY event_id DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)

        return df

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Calculates real runtime metrics (Total, Correct, Violations, Needs Review, Violation Rate)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM waste_events")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM waste_events WHERE rule_result = 'Correct Disposal'")
            correct = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM waste_events WHERE rule_result = 'Confirmed Violation'")
            violations = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM waste_events WHERE rule_result IN ('Needs Review', 'Uncertain')")
            review = cursor.fetchone()[0]

        violation_rate = round((violations / total * 100.0), 1) if total > 0 else 0.0

        return {
            "total_events": total,
            "correct_events": correct,
            "confirmed_violations": violations,
            "needs_review_events": review,
            "violation_rate_pct": violation_rate
        }

    def export_csv(self, export_filepath: str) -> str:
        """Exports the entire event history database to a CSV file."""
        df = self.get_events(limit=100000)
        os.makedirs(os.path.dirname(os.path.abspath(export_filepath)), exist_ok=True)
        df.to_csv(export_filepath, index=False)
        return export_filepath

    def clear_history(self) -> None:
        """Clears all stored runtime event records (for testing or reset)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM waste_events")
            conn.commit()
