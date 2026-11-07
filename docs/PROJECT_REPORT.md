# ACADEMIC PROJECT REPORT

## PROJECT TITLE:
### E-Commerce Clickstream Analytics: A Big-Data Clickstream Processing Pipeline Based Solution

---

### CANDIDATE AND INSTITUTIONAL DETAILS:
- **Student Name:** KOTAMSETTI MANOJ SRI HARSHA
- **Roll / Registration Number:** `23ME1A5433`
- **Faculty Guide / Supervisor:** Mr. S.V. Swamy
- **Academic Domain:** Big Data Analytics, Data Warehousing & Visualization
- **Date of Completion:** October 2026

---

## 1. ABSTRACT
In modern electronic commerce platforms, customer interactions generate massive volumes of continuous event streams known as clickstream data. Uncovering browsing-to-purchase conversion dynamics from these granular logs is vital for revenue optimization, cart abandonment recovery, and personalized marketing attribution. 

This study designs and implements an end-to-end Big-Data clickstream processing pipeline. The architecture ingests anonymized multi-session web event logs, models user behavior in an analytical dimensional Star Schema within a columnar Data Warehouse (DuckDB & Parquet), performs domain-tailored feature engineering (measuring dwell durations, cart-to-view ratios, and step-wise drop-offs), and deploys predictive machine learning classifiers (Gradient Boosting, Random Forest, Logistic Regression) to estimate real-time purchase propensity. The solution culminates in an interactive marketing-conversion dashboard that surfaces actionable conversion funnel analytics, acquisition channel attribution, and a real-time propensity scoring engine for marketing stakeholders.

---

## 2. PROBLEM STATEMENT
E-commerce enterprises face significant challenges in converting browsing traffic into completed purchases:
1. **High Velocity & Volume:** Continuous clickstream events cannot be efficiently processed by traditional transactional (OLTP) relational databases without severe performance degradation.
2. **Funnel Opacity:** Lack of visibility into intermediate friction points where prospective buyers drop off (e.g., product detail vs. cart vs. payment).
3. **Cart Abandonment:** Industry averages indicate that upwards of 70% of carts are abandoned without purchase. Detecting purchase propensity before session exit enables automated intervention.
4. **Attribution Complexity:** Difficulty in quantifying the relative return on marketing investment (ROMI) across paid ads, organic search, and direct referrals.

---

## 3. SYSTEM ARCHITECTURE & DATA WAREHOUSE DESIGN

### 3.1 Dimensional Modeling: Star Schema
To satisfy the requirements of high-speed OLAP aggregations, a dimensional Star Schema was engineered:

- **Fact Table: `fact_clickstream`**
  - *Grain:* One row per unique user interaction event.
  - *Attributes:* `event_id`, `date_key`, `event_timestamp`, `session_id`, `user_id`, `product_id`, `event_type`, `price`, `dwell_time_seconds`, `funnel_step_number`.

- **Dimension Table: `dim_sessions`**
  - *Grain:* One row per browsing session.
  - *Attributes:* `session_id`, `user_id`, `session_start`, `session_end`, `session_duration_seconds`, `total_events`, `is_bounce`, `is_cart_abandoned`, `is_converted`, `traffic_channel`, `device`, `location`.

- **Dimension Table: `dim_users`**
  - *Grain:* One row per registered/anonymized user.
  - *Attributes:* `user_id`, `total_sessions`, `first_seen`, `last_seen`, `lifetime_events`, `total_purchases`, `avg_session_duration`, `customer_segment`.

- **Dimension Table: `dim_products`**
  - *Grain:* One row per unique SKU.
  - *Attributes:* `product_id`, `category`, `base_price`, `total_views`, `total_cart_adds`, `total_purchases`.

- **Dimension Table: `dim_dates`**
  - *Grain:* One row per calendar date.
  - *Attributes:* `date_key`, `full_date`, `day_of_week`, `day_name`, `month`, `year`, `is_weekend`.

---

## 4. DOMAIN FEATURE ENGINEERING & PRE-PROCESSING
Feature extraction transforms raw click events into session-level behavioral signals:

1. **Engagement Metrics:**
   - Active browsing dwell time (`browsing_dwell_seconds`)
   - Average dwell duration per event (`avg_dwell_per_event`)
   - Session duration (`session_duration_seconds`)
   - Single-interaction bounce indicator (`is_bounce`)

2. **Intent & Shopping Cart Signals:**
   - Number of product views (`product_view_count`)
   - Number of cart additions (`cart_add_count`)
   - Cart-to-view interaction depth (`cart_to_view_ratio`)
   - Total cart monetary value (`cart_value`)
   - Maximum viewed item price (`max_product_price`)

3. **Contextual & Channel Attributes:**
   - Acquisition channel (One-hot encoded: Google Ads, Meta Ads, Organic, Newsletter, Direct)
   - Device platform (Mobile, Desktop, Tablet)
   - Temporal features: Hour of day (0-23) and Weekend flag (`is_weekend`)

---

## 5. EXPERIMENTAL EVALUATION & RESULTS

### 5.1 Model Comparison & Validation Metrics
The models were trained on 9,600 session feature vectors and evaluated on an independent test holdout of 2,400 sessions:

| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Gradient Boosting Classifier** | **97.33%** | **0.9294** | **0.8446** | **0.8850** | **0.9928** |
| Random Forest Classifier | 86.83% | 0.4748 | 0.9561 | 0.6345 | 0.9765 |
| Logistic Regression (Baseline) | 87.54% | 0.4930 | 0.9493 | 0.6490 | 0.9660 |

### 5.2 Key Findings:
- **Gradient Boosting** achieved superior overall balance (F1-score of 0.8850 and ROC-AUC of 0.9928), successfully minimizing false positives while capturing true converting customers.
- **Top Predictive Features:** The primary drivers of conversion were determined by Gini importance:
  1. `cart_add_count` (Intent to transact)
  2. `cart_value` (Committed expenditure)
  3. `browsing_events_count` & `browsing_dwell_seconds` (Session depth)
  4. `cart_to_view_ratio` (Selective browsing efficiency)

---

## 6. MARKETING-CONVERSION DASHBOARD DELIVERABLE
The final deliverable is an executive-facing interactive dashboard constructed using Streamlit:
- **Funnel Drop-off Visualization:** Displays conversion drop-offs from Page View -> Product View -> Cart Addition -> Checkout -> Payment -> Purchase.
- **Channel Attribution Breakdown:** Compares acquisition channels by attributed revenue, bounce rate, and customer acquisition efficiency.
- **Real-Time Propensity Calculator:** Allows marketing specialists to simulate live session attributes and receive instant conversion probability ratings with prescriptive intervention recommendations.
- **Interactive OLAP Console:** Enables ad-hoc SQL queries on the DuckDB dimensional warehouse for rapid business intelligence.

---

## 7. CONCLUSION & FUTURE WORK
The developed solution demonstrates how Big Data warehousing techniques combined with domain-tailored machine learning can convert high-velocity clickstream logs into actionable conversion intelligence. 

Future extensions include integrating Apache Kafka for sub-second streaming ingestion, deploying real-time automated webhook push notifications (such as WhatsApp/Email cart abandonment discounts), and extending user embeddings using graph neural networks (GNNs) for cross-session personalized product recommendations.
