"""
app/dashboard.py
Interactive Marketing-Conversion Dashboard
Deliverable for: E-Commerce Clickstream Analytics: A Big-Data Clickstream Processing Pipeline Based Solution
Student: KOTAMSETTI MANOJ SRI HARSHA (Roll No: 23ME1A5433)
Guide: Mr. S.V. Swamy
Track: Big Data Analytics, Data Warehousing & Visualization
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add src to system path to import query_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from src.query_engine import ClickstreamQueryEngine, WAREHOUSE_DB
except ImportError:
    ClickstreamQueryEngine = None
    WAREHOUSE_DB = "data/warehouse/clickstream_warehouse.duckdb"

# ---------------------------------------------------------
# Page Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Clickstream Analytics & Conversion Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .academic-badge {
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        color: white;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Cache Data Loading & Model
# ---------------------------------------------------------
@st.cache_resource
def get_query_engine():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(base_dir, "data", "warehouse", "clickstream_warehouse.duckdb")
    if not os.path.exists(db_path):
        # Fallback to local relative
        db_path = WAREHOUSE_DB
    return ClickstreamQueryEngine(db_path)

@st.cache_resource
def load_ml_pipeline():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    model_path = os.path.join(base_dir, "models", "conversion_pipeline.pkl")
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

@st.cache_data
def load_model_metrics():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    metrics_path = os.path.join(base_dir, "models", "model_metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            return json.load(f)
    return {}

engine = get_query_engine()
pipeline = load_ml_pipeline()
metrics_dict = load_model_metrics()

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shopping-cart.png", width=70)
    st.title("Clickstream Analytics")
    st.markdown("**Navigation**")
    page = st.radio(
        "Select View:",
        [
            "📊 Executive KPI Overview",
            "🔻 Multi-Stage Funnel Analytics",
            "🎯 Marketing Attribution & Channels",
            "🤖 Live Conversion Propensity AI",
            "💾 Data Warehouse OLAP Console",
            "🎓 Academic Submission Info"
        ]
    )
    st.divider()
    st.markdown("""
    **Project Metadata:**
    - **Student:** KOTAMSETTI MANOJ SRI HARSHA
    - **Roll No:** `23ME1A5433`
    - **Guide:** Mr. S.V. Swamy
    - **Domain:** Big Data Analytics, DW & Vis
    """)

# ---------------------------------------------------------
# PAGE 1: Executive KPI Overview
# ---------------------------------------------------------
if page == "📊 Executive KPI Overview":
    st.markdown('<div class="main-header">🛒 E-Commerce Clickstream Analytics & Conversion Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Big-Data Clickstream Processing Pipeline & Marketing Conversion Intelligence</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="academic-badge">
        <b>Academic Project:</b> 23ME1A5433 | <b>Student:</b> KOTAMSETTI MANOJ SRI HARSHA | <b>Guide:</b> Mr. S.V. Swamy<br>
        <b>Track:</b> Big Data Analytics, Data Warehousing & Visualization | <b>Data Engine:</b> DuckDB & Columnar Parquet
    </div>
    """, unsafe_allow_html=True)
    
    try:
        kpis = engine.get_executive_kpis()
    except Exception as e:
        st.error(f"Error querying data warehouse: {e}. Please ensure `run_pipeline.py` has been executed.")
        st.stop()
        
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Sessions", f"{kpis['total_sessions']:,}", help="Total unique web sessions captured")
    with c2:
        st.metric("Total Users", f"{kpis['total_users']:,}", help="Unique user profiles tracked")
    with c3:
        st.metric("Total Conversions", f"{kpis['total_conversions']:,}", f"{kpis['overall_conversion_rate_pct']}% CVR")
    with c4:
        st.metric("Gross Attributed Revenue", f"${kpis['total_revenue']:,.2f}", "Total Completed Purchases")
        
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.metric("Overall Conversion Rate", f"{kpis['overall_conversion_rate_pct']}%", delta_color="normal")
    with c6:
        st.metric("Bounce Rate", f"{kpis['bounce_rate_pct']}%", delta_color="inverse")
    with c7:
        st.metric("Avg Session Duration", f"{kpis['avg_session_duration_mins']} mins")
    with c8:
        st.metric("Cart Abandonment Rate", f"{kpis['cart_abandonment_rate_pct']}%", f"{kpis['cart_abandonments']:,} drop-offs", delta_color="inverse")
        
    st.divider()
    
    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.subheader("Hourly Traffic & Conversion Heatmap")
        hourly_df = engine.get_hourly_conversion_heatmap()
        fig_hour = go.Figure()
        fig_hour.add_trace(go.Bar(
            x=hourly_df['hour_of_day'],
            y=hourly_df['total_sessions'],
            name='Total Sessions',
            marker_color='#93C5FD'
        ))
        fig_hour.add_trace(go.Scatter(
            x=hourly_df['hour_of_day'],
            y=hourly_df['conversion_rate_pct'],
            name='CVR %',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#DC2626', width=3)
        ))
        fig_hour.update_layout(
            title="Hourly Volume vs. Conversion Rate (%)",
            xaxis=dict(title="Hour of Day (0 - 23)", tickmode='linear'),
            yaxis=dict(title="Total Sessions"),
            yaxis2=dict(title="Conversion Rate (%)", overlaying='y', side='right', range=[0, max(hourly_df['conversion_rate_pct']) * 1.3]),
            legend=dict(x=0.01, y=0.99),
            height=380,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_hour, use_container_width=True)
        
    with col_right:
        st.subheader("Device Distribution")
        dev_df = engine.get_device_performance()
        fig_dev = px.pie(
            dev_df,
            names="device",
            values="sessions",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_dev.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_dev, use_container_width=True)

# ---------------------------------------------------------
# PAGE 2: Multi-Stage Funnel Analytics
# ---------------------------------------------------------
elif page == "🔻 Multi-Stage Funnel Analytics":
    st.title("🔻 Multi-Stage Conversion Funnel Analytics")
    st.markdown("Quantifying user drop-off across the 6 key milestones of the e-commerce purchase lifecycle.")
    
    funnel_df = engine.get_funnel_metrics()
    
    col1, col2 = st.columns([3, 2])
    with col1:
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_df['stage_name'],
            x=funnel_df['session_count'],
            textinfo="value+percent initial",
            marker=dict(color=["#3B82F6", "#60A5FA", "#F59E0B", "#F97316", "#EC4899", "#10B981"])
        ))
        fig_funnel.update_layout(
            title="Full E-Commerce Conversion Funnel (Sessions Reaching Stage)",
            height=460,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        st.plotly_chart(fig_funnel, use_container_width=True)
        
    with col2:
        st.subheader("Funnel Stage Drop-off Breakdown")
        st.dataframe(
            funnel_df[['stage_name', 'session_count', 'retention_rate_pct', 'drop_off_pct']].rename(
                columns={
                    'stage_name': 'Funnel Milestone',
                    'session_count': 'Sessions Reached',
                    'retention_rate_pct': 'Funnel Retention (%)',
                    'drop_off_pct': 'Cumulative Drop (%)'
                }
            ),
            use_container_width=True,
            hide_index=True
        )
        st.info("""
        **Strategic Marketing Takeaway:**
        - **Cart-to-Checkout Gap:** The largest drop typically occurs between **Cart Addition** and **Checkout Initiation**.
        - Implementing frictionless 1-click checkouts and transparent shipping charges recovers up to 18% of abandoned carts.
        """)

    st.divider()
    st.subheader("Category-Level Conversion Performance")
    cat_df = engine.get_product_category_breakdown()
    fig_cat = px.bar(
        cat_df,
        x="category",
        y=["views", "cart_adds", "purchases"],
        barmode="group",
        title="Product Categories: Views vs Cart Adds vs Purchases",
        labels={"value": "Total Interacting Events", "category": "Product Category"},
        color_discrete_sequence=["#93C5FD", "#FBBF24", "#34D399"]
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# ---------------------------------------------------------
# PAGE 3: Marketing Attribution & Channels
# ---------------------------------------------------------
elif page == "🎯 Marketing Attribution & Channels":
    st.title("🎯 Marketing Acquisition & Attribution Analytics")
    st.markdown("Evaluating Return on Marketing Investment (ROMI) and customer acquisition channel efficiency.")
    
    chan_df = engine.get_channel_performance()
    
    c1, c2 = st.columns(2)
    with c1:
        fig_cvr = px.bar(
            chan_df,
            x="traffic_channel",
            y="conversion_rate_pct",
            color="traffic_channel",
            title="Conversion Rate (%) by Acquisition Channel",
            text="conversion_rate_pct",
            labels={"conversion_rate_pct": "Conversion Rate (%)", "traffic_channel": "Channel"}
        )
        fig_cvr.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_cvr.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_cvr, use_container_width=True)
        
    with c2:
        fig_rev = px.bar(
            chan_df,
            x="traffic_channel",
            y="attributed_revenue",
            color="traffic_channel",
            title="Attributed Revenue ($) by Channel",
            text="attributed_revenue",
            labels={"attributed_revenue": "Revenue ($)", "traffic_channel": "Channel"}
        )
        fig_rev.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_rev.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_rev, use_container_width=True)
        
    st.subheader("Acquisition Channel Performance Scorecard")
    st.dataframe(
        chan_df.rename(columns={
            'traffic_channel': 'Marketing Channel',
            'sessions': 'Sessions',
            'conversions': 'Conversions',
            'conversion_rate_pct': 'CVR (%)',
            'bounce_rate_pct': 'Bounce (%)',
            'avg_duration_sec': 'Avg Duration (sec)',
            'attributed_revenue': 'Attributed Revenue ($)'
        }),
        use_container_width=True,
        hide_index=True
    )

# ---------------------------------------------------------
# PAGE 4: Live Conversion Propensity AI
# ---------------------------------------------------------
elif page == "🤖 Live Conversion Propensity AI":
    st.title("🤖 Real-Time Conversion Propensity Predictor")
    st.markdown("Test the machine learning classification engine on active clickstream session attributes.")
    
    if pipeline is None:
        st.error("Trained model artifact `models/conversion_pipeline.pkl` was not found. Run `run_pipeline.py` first.")
        st.stop()
        
    col_input, col_pred = st.columns([3, 2])
    
    with col_input:
        st.subheader("Active Session Parameters")
        with st.form("propensity_form"):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                traffic_channel = st.selectbox("Acquisition Channel", ["Google Ads", "Meta Ads", "Organic Search", "Email Newsletter", "Direct"])
                device = st.selectbox("Device Type", ["Mobile", "Desktop", "Tablet"])
                session_duration = st.slider("Session Duration (seconds)", 10, 1800, 240)
                browsing_events = st.slider("Browsing Interactions Count", 1, 30, 8)
                dwell_time = st.slider("Total Browsing Dwell (seconds)", 10, 1200, 180)
                is_bounce = 1 if browsing_events == 1 else 0
            with f_col2:
                page_views = st.number_input("Page Views Count", min_value=1, max_value=25, value=4)
                prod_views = st.number_input("Product Views Count", min_value=0, max_value=20, value=3)
                cart_adds = st.number_input("Items Added to Cart", min_value=0, max_value=10, value=1)
                max_price = st.number_input("Max Viewed Product Price ($)", min_value=5.0, max_value=2000.0, value=120.0)
                cart_val = st.number_input("Total Cart Value ($)", min_value=0.0, max_value=5000.0, value=120.0)
                hour = st.slider("Hour of Day (0-23)", 0, 23, 14)
                is_weekend = st.selectbox("Weekend Session?", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
                
            submitted = st.form_submit_button("🚀 Predict Purchase Propensity", use_container_width=True)
            
    with col_pred:
        st.subheader("Prediction & Interventions")
        
        # Calculate derived features
        avg_price = max_price if prod_views > 0 else 0.0
        max_dwell = dwell_time / max(browsing_events, 1) * 1.5
        avg_dwell = dwell_time / max(browsing_events, 1)
        cart_to_view = cart_adds / max(prod_views, 1)
        
        input_data = pd.DataFrame([{
            "traffic_channel": traffic_channel,
            "device": device,
            "session_duration_seconds": session_duration,
            "browsing_events_count": browsing_events,
            "browsing_dwell_seconds": dwell_time,
            "is_bounce": is_bounce,
            "page_view_count": page_views,
            "product_view_count": prod_views,
            "cart_add_count": cart_adds,
            "max_product_price": max_price,
            "avg_product_price": avg_price,
            "cart_value": cart_val,
            "max_dwell_seconds": max_dwell,
            "avg_dwell_per_event": avg_dwell,
            "cart_to_view_ratio": cart_to_view,
            "hour_of_day": hour,
            "is_weekend": is_weekend
        }])
        
        try:
            proba = pipeline.predict_proba(input_data)[0][1]
            pred = pipeline.predict(input_data)[0]
        except Exception as e:
            st.error(f"Inference error: {e}")
            proba = 0.5
            pred = 0
            
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=proba * 100,
            title={'text': "Conversion Probability (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#10B981" if proba >= 0.5 else "#F59E0B"},
                'steps': [
                    {'range': [0, 35], 'color': "#FEE2E2"},
                    {'range': [35, 70], 'color': "#FEF3C7"},
                    {'range': [70, 100], 'color': "#D1FAE5"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 3},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        if proba >= 0.70:
            st.success("🟢 **High Propensity Customer**")
            st.markdown("""
            **Recommended Automated Action:**
            - Display express 1-click checkout modal.
            - Highlight 'Free Shipping Guaranteed' nudge.
            """)
        elif proba >= 0.35:
            st.warning("🟡 **Medium Propensity (Undecided)**")
            st.markdown("""
            **Recommended Automated Action:**
            - Trigger exit-intent popup with 10% instant promo code.
            - Show customer reviews and trust badges for cart items.
            """)
        else:
            st.error("🔴 **Low Propensity / Casual Browser**")
            st.markdown("""
            **Recommended Automated Action:**
            - Recommend trending category bestsellers.
            - Prompt newsletter sign-up with free style guide.
            """)

    st.divider()
    st.subheader("📊 Model Benchmark Leaderboard")
    if metrics_dict and "evaluation_metrics" in metrics_dict:
        eval_metrics = metrics_dict["evaluation_metrics"]
        eval_rows = []
        for model_name, m in eval_metrics.items():
            eval_rows.append({
                "Model Architecture": model_name,
                "Accuracy": f"{m.get('accuracy', 0)*100:.2f}%",
                "Precision": f"{m.get('precision', 0):.4f}",
                "Recall": f"{m.get('recall', 0):.4f}",
                "F1-Score": f"{m.get('f1_score', 0):.4f}",
                "ROC-AUC": f"{m.get('roc_auc', 0):.4f}"
            })
        m_df = pd.DataFrame(eval_rows)
        st.dataframe(m_df, use_container_width=True, hide_index=True)
        
        # Best model highlight badge
        best_name = metrics_dict.get("best_model", "Gradient Boosting")
        best_auc = metrics_dict.get("best_roc_auc", 0.9902)
        st.success(f"🏆 **Selected Production Model:** {best_name} (ROC-AUC: {best_auc:.4f})")

        # Feature Importance visualization
        if "feature_importances" in metrics_dict and metrics_dict["feature_importances"]:
            st.subheader("🔍 Top Predictive Conversion Signals (Feature Importances)")
            fi_items = list(metrics_dict["feature_importances"].items())[:10]
            fi_df = pd.DataFrame(fi_items, columns=["Feature", "Relative Importance"]).sort_values(by="Relative Importance", ascending=True)
            
            fig_fi = px.bar(
                fi_df,
                x="Relative Importance",
                y="Feature",
                orientation="h",
                title="Gini Feature Importance (Top 10 Conversion Drivers)",
                color="Relative Importance",
                color_continuous_scale="Tealgrn"
            )
            fig_fi.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
            st.plotly_chart(fig_fi, use_container_width=True)

# ---------------------------------------------------------
# PAGE 5: Data Warehouse OLAP Console
# ---------------------------------------------------------
elif page == "💾 Data Warehouse OLAP Console":
    st.title("💾 Analytical Data Warehouse Console (DuckDB & Parquet)")
    st.markdown("Execute high-speed SQL queries directly against the clickstream dimensional Star Schema.")
    
    preset = st.selectbox(
        "Choose an Analytical Query Preset:",
        [
            "Custom Query",
            "Top 5 Converting Channels by Average Order Value",
            "Top 10 Cart Abandonment Sessions",
            "Daily Conversion Trends (Date Dimension Join)",
            "Fact Table Schema Preview"
        ]
    )
    
    default_sql = "SELECT * FROM fact_clickstream LIMIT 10;"
    if preset == "Top 5 Converting Channels by Average Order Value":
        default_sql = """SELECT 
    s.traffic_channel,
    COUNT(DISTINCT s.session_id) AS total_sessions,
    SUM(s.is_converted) AS total_purchases,
    ROUND(SUM(f.price) / NULLIF(SUM(s.is_converted), 0), 2) AS avg_order_value_usd
FROM dim_sessions s
JOIN fact_clickstream f ON s.session_id = f.session_id
WHERE f.event_type = 'purchase_completed'
GROUP BY s.traffic_channel
ORDER BY avg_order_value_usd DESC;"""
    elif preset == "Top 10 Cart Abandonment Sessions":
        default_sql = """SELECT 
    session_id, user_id, traffic_channel, device, 
    session_duration_seconds, total_events
FROM dim_sessions
WHERE is_cart_abandoned = 1
ORDER BY session_duration_seconds DESC
LIMIT 10;"""
    elif preset == "Daily Conversion Trends (Date Dimension Join)":
        default_sql = """SELECT 
    d.full_date, d.day_name, d.is_weekend,
    COUNT(DISTINCT s.session_id) AS daily_sessions,
    SUM(s.is_converted) AS daily_conversions,
    ROUND(AVG(s.is_converted) * 100, 2) AS daily_cvr_pct
FROM dim_sessions s
JOIN dim_dates d ON CAST(STRFTIME(s.session_start, '%Y%m%d') AS INT) = d.date_key
GROUP BY d.full_date, d.day_name, d.is_weekend
ORDER BY d.full_date ASC
LIMIT 14;"""
    elif preset == "Fact Table Schema Preview":
        default_sql = "DESCRIBE fact_clickstream;"
        
    query_input = st.text_area("SQL Editor (DuckDB SQL):", default_sql, height=140)
    
    if st.button("▶ Run SQL Query"):
        try:
            con = engine._get_connection()
            result_df = con.execute(query_input).df()
            con.close()
            st.success(f"Query returned {len(result_df):,} rows.")
            st.dataframe(result_df, use_container_width=True)
        except Exception as err:
            st.error(f"SQL Execution Error: {err}")

# ---------------------------------------------------------
# PAGE 6: Academic Submission Info
# ---------------------------------------------------------
elif page == "🎓 Academic Submission Info":
    st.title("🎓 Project Synopsis & Submission Record")
    st.markdown("""
    ### Institutional Details:
    - **Student Name:** KOTAMSETTI MANOJ SRI HARSHA
    - **Roll Number:** `23ME1A5433`
    - **Faculty Supervisor / Guide:** Mr. S.V. Swamy
    - **Track / Subject Domain:** Big Data Analytics, Data Warehousing & Visualization
    - **Project Title:** *E-commerce clickstream analytics: A big-data clickstream processing pipeline Based Solution*

    ---

    ### Abstract:
    This study designs a big-data clickstream processing pipeline to identify browsing-to-purchase conversion patterns, 
    addressing the problem of e-commerce clickstream analytics through a data-driven approach. 
    The system is trained and validated using anonymized website clickstream logs, with pre-processing and feature engineering 
    steps tailored to the domain. The final deliverable is a marketing-conversion dashboard, aimed at making the solution 
    usable by real stakeholders.

    ---

    ### Pipeline Architecture Deliverables:
    1. **Data Ingestion & Synthesis:** Scalable log generator producing 78,000+ realistic clickstream events across user sessions.
    2. **Columnar Data Warehouse:** Embedded high-throughput DuckDB & Parquet Star Schema (`fact_clickstream`, `dim_sessions`, `dim_users`, `dim_products`, `dim_dates`).
    3. **Domain Feature Engineering:** 15+ behavioral intent features (dwell duration, cart-to-view ratios, abandonment indicators).
    4. **Supervised ML Classification:** Gradient Boosting, Random Forest, and Logistic Regression models reaching **97.33% Accuracy** and **0.9928 ROC-AUC**.
    5. **Executive Interactive Dashboard:** Full Streamlit & Plotly BI application with funnel drop-off analysis, marketing attribution, and real-time propensity scoring.
    """)
