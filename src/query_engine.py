"""
Module: query_engine.py
Description: Fast OLAP query engine leveraging DuckDB for real-time marketing analytics,
funnel progression, cohort conversion, and stakeholder KPIs.
"""

import duckdb
import pandas as pd

WAREHOUSE_DB = "data/warehouse/clickstream_warehouse.duckdb"

class ClickstreamQueryEngine:
    def __init__(self, db_path=WAREHOUSE_DB):
        self.db_path = db_path
        
    def _get_connection(self):
        return duckdb.connect(database=self.db_path, read_only=True)
        
    def get_executive_kpis(self):
        """Returns top-level KPIs for executive marketing stakeholders."""
        con = self._get_connection()
        query = """
        SELECT 
            COUNT(DISTINCT session_id) AS total_sessions,
            COUNT(DISTINCT user_id) AS total_users,
            SUM(CASE WHEN is_converted = 1 THEN 1 ELSE 0 END) AS total_conversions,
            ROUND(AVG(is_converted) * 100, 2) AS overall_conversion_rate_pct,
            ROUND(AVG(is_bounce) * 100, 2) AS bounce_rate_pct,
            ROUND(AVG(session_duration_seconds) / 60.0, 2) AS avg_session_duration_mins,
            SUM(CASE WHEN is_cart_abandoned = 1 THEN 1 ELSE 0 END) AS cart_abandonments,
            ROUND(
                SUM(CASE WHEN is_cart_abandoned = 1 THEN 1 ELSE 0 END) * 100.0 / 
                NULLIF(SUM(CASE WHEN has_cart_add = 1 THEN 1 ELSE 0 END), 0), 2
            ) AS cart_abandonment_rate_pct
        FROM dim_sessions
        """
        df = con.execute(query).df()
        
        # Total revenue from purchases
        rev_query = """
        SELECT ROUND(COALESCE(SUM(price), 0.0), 2) AS total_revenue
        FROM fact_clickstream
        WHERE event_type = 'purchase_completed'
        """
        revenue = con.execute(rev_query).fetchone()[0]
        con.close()
        
        kpis = df.to_dict(orient="records")[0]
        kpis["total_revenue"] = revenue
        return kpis

    def get_funnel_metrics(self):
        """Returns step-by-step conversion funnel drops."""
        con = self._get_connection()
        query = """
        SELECT 
            funnel_step_number,
            CASE 
                WHEN funnel_step_number = 1 THEN '1. Landing / Page View'
                WHEN funnel_step_number = 2 THEN '2. Product Exploration'
                WHEN funnel_step_number = 3 THEN '3. Cart Addition'
                WHEN funnel_step_number = 4 THEN '4. Checkout Initiated'
                WHEN funnel_step_number = 5 THEN '5. Payment Details'
                WHEN funnel_step_number = 6 THEN '6. Purchase Completed'
            END AS stage_name,
            COUNT(DISTINCT session_id) AS session_count
        FROM fact_clickstream
        WHERE funnel_step_number > 0
        GROUP BY funnel_step_number
        ORDER BY funnel_step_number
        """
        df = con.execute(query).df()
        con.close()
        
        if not df.empty:
            top_val = df.iloc[0]["session_count"]
            df["retention_rate_pct"] = (df["session_count"] / top_val * 100).round(2)
            df["drop_off_pct"] = (100 - df["retention_rate_pct"]).round(2)
        return df

    def get_channel_performance(self):
        """Marketing attribution and acquisition channel analytics."""
        con = self._get_connection()
        query = """
        SELECT 
            s.traffic_channel,
            COUNT(DISTINCT s.session_id) AS sessions,
            SUM(s.is_converted) AS conversions,
            ROUND(AVG(s.is_converted) * 100, 2) AS conversion_rate_pct,
            ROUND(AVG(s.is_bounce) * 100, 2) AS bounce_rate_pct,
            ROUND(AVG(s.session_duration_seconds), 1) AS avg_duration_sec,
            ROUND(COALESCE(SUM(CASE WHEN f.event_type = 'purchase_completed' THEN f.price ELSE 0 END), 0), 2) AS attributed_revenue
        FROM dim_sessions s
        LEFT JOIN fact_clickstream f ON s.session_id = f.session_id
        GROUP BY s.traffic_channel
        ORDER BY sessions DESC
        """
        df = con.execute(query).df()
        con.close()
        return df

    def get_device_performance(self):
        """Device breakdown analysis."""
        con = self._get_connection()
        query = """
        SELECT 
            device,
            COUNT(session_id) AS sessions,
            SUM(is_converted) AS conversions,
            ROUND(AVG(is_converted) * 100, 2) AS conversion_rate_pct,
            ROUND(AVG(is_bounce) * 100, 2) AS bounce_rate_pct
        FROM dim_sessions
        GROUP BY device
        ORDER BY sessions DESC
        """
        df = con.execute(query).df()
        con.close()
        return df

    def get_hourly_conversion_heatmap(self):
        """Heatmap of sessions and conversions across hours of the day."""
        con = self._get_connection()
        query = """
        SELECT 
            hour(session_start) AS hour_of_day,
            COUNT(session_id) AS total_sessions,
            SUM(is_converted) AS converted_sessions,
            ROUND(AVG(is_converted) * 100, 2) AS conversion_rate_pct
        FROM dim_sessions
        GROUP BY hour(session_start)
        ORDER BY hour_of_day
        """
        df = con.execute(query).df()
        con.close()
        return df

    def get_product_category_breakdown(self):
        """Category popularity and revenue distribution."""
        con = self._get_connection()
        query = """
        SELECT 
            p.category,
            SUM(p.total_views) AS views,
            SUM(p.total_cart_adds) AS cart_adds,
            SUM(p.total_purchases) AS purchases,
            ROUND(SUM(p.total_purchases) * 100.0 / NULLIF(SUM(p.total_views), 0), 2) AS view_to_purchase_pct
        FROM dim_products p
        GROUP BY p.category
        ORDER BY purchases DESC
        """
        df = con.execute(query).df()
        con.close()
        return df
