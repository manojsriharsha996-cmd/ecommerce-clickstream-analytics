"""
Module: feature_engineering.py
Description: Domain-specific feature engineering extracting behavioral session attributes,
funnel milestones, and purchase propensity metrics for Machine Learning models.
"""

import os
import duckdb
import pandas as pd
import numpy as np

PROCESSED_DATA_PATH = "data/processed/session_features.csv"
WAREHOUSE_DB = "data/warehouse/clickstream_warehouse.duckdb"

def extract_session_features(warehouse_db=WAREHOUSE_DB, output_csv=PROCESSED_DATA_PATH):
    """
    Extracts high-level machine learning feature vectors from the Data Warehouse.
    Produces session-level feature matrix with domain-specific metrics.
    """
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    con = duckdb.connect(database=warehouse_db)
    
    query = """
    WITH event_metrics AS (
        SELECT 
            session_id,
            COUNT(CASE WHEN event_type = 'page_view' THEN 1 END) AS page_view_count,
            COUNT(CASE WHEN event_type = 'product_view' THEN 1 END) AS product_view_count,
            COUNT(CASE WHEN event_type = 'add_to_cart' THEN 1 END) AS cart_add_count,
            COUNT(CASE WHEN event_type NOT IN ('payment_info', 'purchase_completed') THEN 1 END) AS browsing_events_count,
            SUM(CASE WHEN event_type NOT IN ('payment_info', 'purchase_completed') THEN dwell_time_seconds ELSE 0 END) AS browsing_dwell_seconds,
            MAX(price) AS max_product_price,
            ROUND(AVG(NULLIF(price, 0)), 2) AS avg_product_price,
            SUM(CASE WHEN event_type = 'add_to_cart' THEN price ELSE 0 END) AS cart_value,
            MAX(dwell_time_seconds) AS max_dwell_seconds
        FROM fact_clickstream
        GROUP BY session_id
    )
    SELECT 
        s.session_id,
        s.user_id,
        s.traffic_channel,
        s.device,
        s.location,
        s.session_duration_seconds,
        em.browsing_events_count,
        em.browsing_dwell_seconds,
        s.is_bounce,
        em.page_view_count,
        em.product_view_count,
        em.cart_add_count,
        COALESCE(em.max_product_price, 0.0) AS max_product_price,
        COALESCE(em.avg_product_price, 0.0) AS avg_product_price,
        COALESCE(em.cart_value, 0.0) AS cart_value,
        COALESCE(em.max_dwell_seconds, 0) AS max_dwell_seconds,
        ROUND(em.browsing_dwell_seconds / GREATEST(em.browsing_events_count, 1), 2) AS avg_dwell_per_event,
        ROUND(em.cart_add_count / GREATEST(em.product_view_count + 1, 1), 4) AS cart_to_view_ratio,
        hour(s.session_start) AS hour_of_day,
        dayofweek(s.session_start) AS day_of_week,
        CASE WHEN dayofweek(s.session_start) IN (0, 6) THEN 1 ELSE 0 END AS is_weekend,
        s.is_converted AS target_converted
    FROM dim_sessions s
    JOIN event_metrics em ON s.session_id = em.session_id
    """
    
    print("[FeatureEngineering] Extracting feature vectors via DuckDB analytical engine...")
    df = con.execute(query).df()
    con.close()
    
    # Fill remaining NaNs if any
    df = df.fillna(0)
    
    df.to_csv(output_csv, index=False)
    print(f"[FeatureEngineering] Engineered {len(df):,} session feature rows with {df.shape[1]} columns.")
    print(f"[FeatureEngineering] Conversion rate in dataset: {df['target_converted'].mean():.2%}")
    print(f"[FeatureEngineering] Saved features to: {output_csv}")
    return df

if __name__ == "__main__":
    extract_session_features()
