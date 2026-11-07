"""
tests/test_pipeline.py
Unit and Integration Test Suite for the Big Data Clickstream Processing Pipeline.

Project: E-commerce clickstream analytics: A big-data clickstream processing pipeline Based Solution
Student: KOTAMSETTI MANOJ SRI HARSHA (Roll No: 23ME1A5433)
Guide: Mr. S.V. Swamy
Track: Big Data Analytics, Data Warehousing & Visualization
"""

import os
import sys
import unittest
import pandas as pd
import duckdb
import joblib

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.log_generator import generate_clickstream_dataset
from src.warehouse_etl import run_warehouse_etl, WAREHOUSE_DB
from src.feature_engineering import extract_session_features
from src.conversion_model import predict_single_session, MODEL_PKL
from src.query_engine import ClickstreamQueryEngine


class TestClickstreamPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up test environment and file paths."""
        cls.test_raw_csv = os.path.join(PROJECT_ROOT, "data", "raw", "clickstream_logs.csv")
        cls.test_db = os.path.join(PROJECT_ROOT, "data", "warehouse", "clickstream_warehouse.duckdb")
        cls.test_features = os.path.join(PROJECT_ROOT, "data", "processed", "session_features.csv")
        cls.test_model = os.path.join(PROJECT_ROOT, "models", "conversion_pipeline.pkl")

    def test_01_raw_logs_exist_and_valid(self):
        """Verify that raw clickstream event logs exist and match required schema."""
        self.assertTrue(os.path.exists(self.test_raw_csv), "Raw clickstream log file is missing.")
        df = pd.read_csv(self.test_raw_csv, nrows=50)
        required_cols = [
            "event_id", "timestamp", "session_id", "user_id", "event_type",
            "page_url", "traffic_channel", "device", "location"
        ]
        for col in required_cols:
            self.assertIn(col, df.columns, f"Required column '{col}' missing from raw logs.")
        self.assertGreater(len(df), 0, "Raw logs file is empty.")

    def test_02_warehouse_star_schema_tables(self):
        """Verify that the DuckDB Data Warehouse contains all Star Schema tables."""
        self.assertTrue(os.path.exists(self.test_db), "DuckDB warehouse file does not exist.")
        con = duckdb.connect(self.test_db, read_only=True)
        tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
        con.close()

        expected_tables = ["fact_clickstream", "dim_sessions", "dim_users", "dim_products", "dim_dates"]
        for tbl in expected_tables:
            self.assertIn(tbl, tables, f"Expected Star Schema table '{tbl}' was not found in warehouse.")

    def test_03_fact_table_grain_and_metrics(self):
        """Verify fact_clickstream table row count, grain, and foreign key relations."""
        con = duckdb.connect(self.test_db, read_only=True)
        event_count = con.execute("SELECT count(*) FROM fact_clickstream").fetchone()[0]
        distinct_events = con.execute("SELECT count(DISTINCT event_id) FROM fact_clickstream").fetchone()[0]
        con.close()

        self.assertGreater(event_count, 1000, "Fact table has fewer rows than expected.")
        self.assertEqual(event_count, distinct_events, "Fact table has duplicate event IDs.")

    def test_04_session_features_and_no_leakage(self):
        """Ensure feature engineering output is valid and free from post-conversion leakage."""
        self.assertTrue(os.path.exists(self.test_features), "Engineered features CSV is missing.")
        df = pd.read_csv(self.test_features, nrows=100)

        # Confirm target is binary (0 or 1)
        self.assertTrue(set(df["target_converted"].unique()).issubset({0, 1}))

        # Confirm no negative durations or prices
        self.assertTrue((df["session_duration_seconds"] >= 0).all())
        self.assertTrue((df["browsing_dwell_seconds"] >= 0).all())
        self.assertTrue((df["cart_value"] >= 0).all())

    def test_05_ml_pipeline_model_inference(self):
        """Test trained model pipeline for live session inference and propensity calculation."""
        self.assertTrue(os.path.exists(self.test_model), "Serialized ML model pipeline is missing.")
        model = joblib.load(self.test_model)
        self.assertIsNotNone(model, "Failed to deserialize model pipeline.")

        # Test single session prediction
        sample_session = {
            "traffic_channel": "Google Ads",
            "device": "Desktop",
            "session_duration_seconds": 320,
            "browsing_events_count": 9,
            "browsing_dwell_seconds": 210,
            "is_bounce": 0,
            "page_view_count": 4,
            "product_view_count": 3,
            "cart_add_count": 2,
            "max_product_price": 149.99,
            "avg_product_price": 89.50,
            "cart_value": 179.00,
            "max_dwell_seconds": 65,
            "avg_dwell_per_event": 23.3,
            "cart_to_view_ratio": 0.66,
            "hour_of_day": 15,
            "is_weekend": 0
        }
        res = predict_single_session(sample_session, model_path=self.test_model)
        self.assertIn("conversion_probability", res)
        self.assertIn("predicted_conversion", res)
        self.assertIn("intent_tier", res)
        self.assertGreaterEqual(res["conversion_probability"], 0.0)
        self.assertLessEqual(res["conversion_probability"], 1.0)
        self.assertIn(res["intent_tier"], ["High", "Medium", "Low"])

    def test_06_query_engine_kpis(self):
        """Test OLAP Query Engine analytical methods."""
        engine = ClickstreamQueryEngine(self.test_db)
        kpis = engine.get_executive_kpis()

        self.assertIn("total_sessions", kpis)
        self.assertIn("total_users", kpis)
        self.assertIn("total_conversions", kpis)
        self.assertIn("overall_conversion_rate_pct", kpis)
        self.assertGreater(kpis["total_sessions"], 0)
        self.assertGreater(kpis["total_users"], 0)

        # Test Funnel metrics
        funnel_df = engine.get_funnel_metrics()
        self.assertFalse(funnel_df.empty, "Funnel metrics DataFrame is empty.")
        self.assertIn("stage_name", funnel_df.columns)
        self.assertIn("session_count", funnel_df.columns)


if __name__ == "__main__":
    unittest.main(verbosity=2)
