"""
Module: warehouse_etl.py
Description: Big Data Warehouse ETL pipeline.
Builds an analytical Star Schema (Fact and Dimension tables) in DuckDB & Parquet.
"""

import os
import duckdb
import pandas as pd
import numpy as np

WAREHOUSE_DB = "data/warehouse/clickstream_warehouse.duckdb"
WAREHOUSE_DIR = "data/warehouse"

def run_warehouse_etl(raw_csv="data/raw/clickstream_logs.csv"):
    """
    Executes the Data Warehouse ETL:
    1. Extracts raw clickstream event stream.
    2. Cleanses and transforms data.
    3. Builds Star Schema:
       - dim_users
       - dim_products
       - dim_sessions
       - dim_dates
       - fact_clickstream
    4. Persists into DuckDB and columnar Parquet.
    """
    os.makedirs(WAREHOUSE_DIR, exist_ok=True)
    print(f"[WarehouseETL] Initializing Data Warehouse build at {WAREHOUSE_DB}...")
    
    con = duckdb.connect(database=WAREHOUSE_DB)
    
    # 1. Load staging table from raw CSV
    print(f"[WarehouseETL] Ingesting staging data from {raw_csv}...")
    con.execute(f"""
        CREATE OR REPLACE TABLE stg_clickstream AS
        SELECT 
            event_id,
            CAST(timestamp AS TIMESTAMP) AS event_timestamp,
            session_id,
            user_id,
            event_type,
            page_url,
            COALESCE(product_id, 'NONE') AS product_id,
            COALESCE(product_category, 'General') AS product_category,
            CAST(price AS DOUBLE) AS price,
            CAST(dwell_time_seconds AS INTEGER) AS dwell_time_seconds,
            traffic_channel,
            device,
            location
        FROM read_csv_auto('{raw_csv}')
    """)
    
    total_events = con.execute("SELECT count(*) FROM stg_clickstream").fetchone()[0]
    print(f"[WarehouseETL] Staged {total_events:,} raw events.")

    # 2. Build Dimension: dim_dates
    print("[WarehouseETL] Constructing Dimension: dim_dates...")
    con.execute("""
        CREATE OR REPLACE TABLE dim_dates AS
        WITH distinct_dates AS (
            SELECT DISTINCT CAST(event_timestamp AS DATE) AS full_date
            FROM stg_clickstream
        )
        SELECT 
            strftime(full_date, '%Y%m%d')::INT AS date_key,
            full_date,
            dayofweek(full_date) AS day_of_week,
            dayname(full_date) AS day_name,
            month(full_date) AS month,
            year(full_date) AS year,
            CASE WHEN dayofweek(full_date) IN (0, 6) THEN 1 ELSE 0 END AS is_weekend
        FROM distinct_dates
        ORDER BY full_date
    """)

    # 3. Build Dimension: dim_products
    print("[WarehouseETL] Constructing Dimension: dim_products...")
    con.execute("""
        CREATE OR REPLACE TABLE dim_products AS
        SELECT 
            product_id,
            COALESCE(MAX(product_category), 'General') AS category,
            COALESCE(MAX(price), 0.0) AS base_price,
            COUNT(CASE WHEN event_type = 'product_view' THEN 1 END) AS total_views,
            COUNT(CASE WHEN event_type = 'add_to_cart' THEN 1 END) AS total_cart_adds,
            COUNT(CASE WHEN event_type = 'purchase_completed' THEN 1 END) AS total_purchases
        FROM stg_clickstream
        WHERE product_id != 'NONE'
        GROUP BY product_id
    """)

    # 4. Build Dimension: dim_sessions
    print("[WarehouseETL] Constructing Dimension: dim_sessions with behavioral metrics...")
    con.execute("""
        CREATE OR REPLACE TABLE dim_sessions AS
        SELECT 
            session_id,
            user_id,
            MIN(event_timestamp) AS session_start,
            MAX(event_timestamp) AS session_end,
            epoch(MAX(event_timestamp)) - epoch(MIN(event_timestamp)) AS session_duration_seconds,
            COUNT(event_id) AS total_events,
            SUM(dwell_time_seconds) AS total_dwell_seconds,
            MAX(traffic_channel) AS traffic_channel,
            MAX(device) AS device,
            MAX(location) AS location,
            CASE WHEN COUNT(event_id) = 1 THEN 1 ELSE 0 END AS is_bounce,
            MAX(CASE WHEN event_type = 'product_view' THEN 1 ELSE 0 END) AS has_product_view,
            MAX(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS has_cart_add,
            MAX(CASE WHEN event_type = 'checkout_start' THEN 1 ELSE 0 END) AS has_checkout,
            MAX(CASE WHEN event_type = 'purchase_completed' THEN 1 ELSE 0 END) AS is_converted,
            CASE 
                WHEN MAX(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) = 1 
                 AND MAX(CASE WHEN event_type = 'purchase_completed' THEN 1 ELSE 0 END) = 0 
                THEN 1 ELSE 0 
            END AS is_cart_abandoned
        FROM stg_clickstream
        GROUP BY session_id, user_id
    """)

    # 5. Build Dimension: dim_users (RFM & Lifetime aggregation)
    print("[WarehouseETL] Constructing Dimension: dim_users with RFM metrics...")
    con.execute("""
        CREATE OR REPLACE TABLE dim_users AS
        SELECT 
            user_id,
            COUNT(session_id) AS total_sessions,
            MIN(session_start) AS first_seen,
            MAX(session_end) AS last_seen,
            SUM(total_events) AS lifetime_events,
            SUM(is_converted) AS total_purchases,
            ROUND(AVG(session_duration_seconds), 1) AS avg_session_duration,
            MAX(traffic_channel) AS primary_traffic_channel,
            MAX(device) AS primary_device,
            MAX(location) AS location,
            CASE WHEN SUM(is_converted) > 0 THEN 'Purchaser' ELSE 'Prospect' END AS customer_segment
        FROM dim_sessions
        GROUP BY user_id
    """)

    # 6. Build Fact Table: fact_clickstream
    print("[WarehouseETL] Constructing Fact Table: fact_clickstream...")
    con.execute("""
        CREATE OR REPLACE TABLE fact_clickstream AS
        SELECT 
            s.event_id,
            strftime(s.event_timestamp, '%Y%m%d')::INT AS date_key,
            s.event_timestamp,
            s.session_id,
            s.user_id,
            s.product_id,
            s.event_type,
            s.price,
            s.dwell_time_seconds,
            CASE 
                WHEN s.event_type = 'page_view' THEN 1
                WHEN s.event_type = 'product_view' THEN 2
                WHEN s.event_type = 'add_to_cart' THEN 3
                WHEN s.event_type = 'checkout_start' THEN 4
                WHEN s.event_type = 'payment_info' THEN 5
                WHEN s.event_type = 'purchase_completed' THEN 6
                ELSE 0
            END AS funnel_step_number
        FROM stg_clickstream s
    """)

    # Export to Parquet for fast columnar analytical queries
    parquet_path = os.path.join(WAREHOUSE_DIR, "fact_clickstream.parquet")
    con.execute(f"COPY fact_clickstream TO '{parquet_path}' (FORMAT PARQUET)")
    
    sessions_parquet = os.path.join(WAREHOUSE_DIR, "dim_sessions.parquet")
    con.execute(f"COPY dim_sessions TO '{sessions_parquet}' (FORMAT PARQUET)")
    
    print("[WarehouseETL] Parquet columnar partitions successfully exported.")
    
    # Summary of warehouse entities
    summary = {
        "fact_events": con.execute("SELECT count(*) FROM fact_clickstream").fetchone()[0],
        "dim_sessions": con.execute("SELECT count(*) FROM dim_sessions").fetchone()[0],
        "dim_users": con.execute("SELECT count(*) FROM dim_users").fetchone()[0],
        "dim_products": con.execute("SELECT count(*) FROM dim_products").fetchone()[0],
        "dim_dates": con.execute("SELECT count(*) FROM dim_dates").fetchone()[0]
    }
    
    con.close()
    print(f"[WarehouseETL] Warehouse build complete! Summary: {summary}")
    return summary

if __name__ == "__main__":
    run_warehouse_etl()
