# ARCHITECTURE BLUEPRINT & DATA WAREHOUSE SCHEMA

## Project: E-Commerce Clickstream Analytics Pipeline
- **Student:** KOTAMSETTI MANOJ SRI HARSHA (23ME1A5433)
- **Guide:** Mr. S.V. Swamy
- **Track:** Big Data Analytics, Data Warehousing & Visualization

---

## 1. End-to-End Data Pipeline Architecture

```mermaid
flowchart TD
    subgraph DataCollection ["1. Ingestion Layer"]
        A["Website / Mobile App Clickstream Events"] --> B["Streaming / Batch Log Ingestor"]
        B --> C["Raw CSV Logs (data/raw/clickstream_logs.csv)"]
    end

    subgraph DataWarehousing ["2. Data Warehousing Layer (DuckDB & Parquet)"]
        C --> D["Staging Table (stg_clickstream)"]
        D --> E["ETL Cleansing & Dimensional Transformation"]
        E --> F1[("dim_users")]
        E --> F2[("dim_sessions")]
        E --> F3[("dim_products")]
        E --> F4[("dim_dates")]
        E --> F5[("fact_clickstream")]
    end

    subgraph MachineLearning ["3. ML Analytics & Propensity Modeling"]
        F2 --> G["Feature Engineering Pipeline"]
        F5 --> G
        G --> H["Session Feature Vectors (data/processed/)"]
        H --> I["Train/Test Split & Scaler"]
        I --> J["Gradient Boosting / Random Forest"]
        J --> K["Serialized Model (models/conversion_pipeline.pkl)"]
    end

    subgraph StakeholderLayer ["4. Delivery & Visualization Layer"]
        F5 --> L["OLAP Query Engine"]
        F2 --> L
        K --> M["Live Conversion Propensity Calculator"]
        L --> N["Interactive Marketing Dashboard (Streamlit)"]
        M --> N
    end
```

---

## 2. Dimensional Star Schema (Entity-Relationship Diagram)

```mermaid
erDiagram
    dim_users ||--o{ dim_sessions : "has sessions"
    dim_users ||--o{ fact_clickstream : "performs events"
    dim_sessions ||--o{ fact_clickstream : "contains events"
    dim_products ||--o{ fact_clickstream : "target of interaction"
    dim_dates ||--o{ fact_clickstream : "occurs on date"

    fact_clickstream {
        string event_id PK
        int date_key FK
        timestamp event_timestamp
        string session_id FK
        string user_id FK
        string product_id FK
        string event_type
        double price
        int dwell_time_seconds
        int funnel_step_number
    }

    dim_sessions {
        string session_id PK
        string user_id FK
        timestamp session_start
        timestamp session_end
        int session_duration_seconds
        int total_events
        int is_bounce
        int is_cart_abandoned
        int is_converted
        string traffic_channel
        string device
        string location
    }

    dim_users {
        string user_id PK
        int total_sessions
        timestamp first_seen
        timestamp last_seen
        int lifetime_events
        int total_purchases
        double avg_session_duration
        string customer_segment
    }

    dim_products {
        string product_id PK
        string category
        double base_price
        int total_views
        int total_cart_adds
        int total_purchases
    }

    dim_dates {
        int date_key PK
        date full_date
        int day_of_week
        string day_name
        int month
        int year
        int is_weekend
    }
```

---

## 3. Browsing-to-Purchase Funnel State Transitions

```mermaid
stateDiagram-v2
    [*] --> PageView: User Enters Site (Organic / Paid / Direct)
    PageView --> Bounce: Dwell < 10s & Exit (30%)
    PageView --> ProductView: Search / Catalog Navigation
    
    ProductView --> ProductView: Browse Additional Items
    ProductView --> DropOff: Exit Without Adding to Cart
    ProductView --> AddToCart: High Product Intent
    
    AddToCart --> CartAbandon: Exit With Items In Cart (Friction / High Cost)
    AddToCart --> CheckoutInitiated: Proceed to Checkout
    
    CheckoutInitiated --> DropOffAtPayment: Exit at Shipping / Payment Info
    CheckoutInitiated --> PaymentEntered: Fill Payment Details
    
    PaymentEntered --> PurchaseCompleted: Transaction Approved (Conversion!)
    PurchaseCompleted --> [*]
    Bounce --> [*]
    DropOff --> [*]
    CartAbandon --> [*]
```
