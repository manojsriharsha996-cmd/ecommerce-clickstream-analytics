# PROJECT PRESENTATION & VIVA-VOCE DEFENSE GUIDE

## E-Commerce Clickstream Analytics: A Big-Data Clickstream Processing Pipeline Based Solution
- **Candidate:** KOTAMSETTI MANOJ SRI HARSHA (23ME1A5433)
- **Faculty Guide:** Mr. S.V. Swamy
- **Track:** Big Data Analytics, Data Warehousing & Visualization

---

## 1. 2-Minute Elevator Pitch
> *"Good morning respected Guide and Examiners. My project is 'E-Commerce Clickstream Analytics: A Big-Data Processing Pipeline Based Solution'. In modern e-commerce, millions of user click events happen every hour. The core problem is that raw logs are unstructured and too heavy for standard transactional databases, leaving marketing teams in the dark about why visitors drop off without buying.*
>
> *To solve this, I designed an end-to-end Big Data pipeline. First, high-volume clickstream logs are cleansed and stored in a dimensional Star Schema within a columnar Data Warehouse powered by DuckDB and Parquet. Next, I engineered domain-tailored behavioral features like dwell time, cart-to-view ratios, and stage drops. Using these features, I trained machine learning models—with Gradient Boosting reaching an outstanding 0.9928 ROC-AUC. Finally, I built an interactive Marketing-Conversion Dashboard that gives executives real-time funnel visibility, marketing channel ROI, and an instant purchase propensity scoring tool. Thank you."*

---

## 2. Frequently Asked Viva-Voce Questions & Strong Technical Answers

### Q1: Why did you use a Star Schema instead of normal 3NF (Third Normal Form)?
**Answer:** 
> *"In Big Data Analytics and Data Warehousing, 3NF is optimized for OLTP (transactional writes, updates, avoiding redundancy), but it requires numerous expensive JOIN operations that degrade analytical query speed. A Star Schema with one central Fact table (`fact_clickstream`) and surrounding Dimension tables (`dim_sessions`, `dim_users`, `dim_products`, `dim_dates`) denormalizes data purposefully to maximize read throughput, simplify OLAP aggregations, and allow sub-second slice-and-dice queries."*

### Q2: Why DuckDB and Parquet instead of a standard SQLite or MySQL database?
**Answer:**
> *"Traditional databases like SQLite and MySQL are row-oriented (storing data tuple by tuple). When running analytical queries like `SUM(price)` or `AVG(duration)`, row-oriented engines scan every single column from disk. DuckDB is an in-process vectorized columnar OLAP engine that reads only the specific columns needed, compressing data into Parquet files with SIMD optimizations. It processes tens of thousands of clickstream events in milliseconds with zero server overhead."*

### Q3: How did you prevent data leakage in your Machine Learning conversion model?
**Answer:**
> *"Data leakage occurs if the model is fed features that only exist after the conversion has already happened (for instance, counting payment events or post-purchase confirmation dwell times). To prevent this, our feature engineering module strictly filters out post-conversion events (`payment_info` and `purchase_completed`), computing only pre-transaction browsing depth, cart additions, session dwell time, and device context to make the prediction realistic for real-time scoring."*

### Q4: Which Machine Learning algorithm performed the best and why?
**Answer:**
> *"We benchmarked three algorithms: Logistic Regression (baseline), Random Forest, and Gradient Boosting. Gradient Boosting achieved the highest performance with a ROC-AUC of 0.9928, an F1-score of 0.8850, and 97.33% accuracy. It outperformed the others because gradient boosted trees excel at learning non-linear threshold interactions between cart values, dwell times, and categorical channels through iterative residual minimization."*

### Q5: How can a marketing stakeholder use this system in practice?
**Answer:**
> *"Through the interactive Marketing-Conversion Dashboard:
> 1. They can pinpoint the exact stage where traffic is lost in the conversion funnel.
> 2. They can compare acquisition channels (e.g. Meta Ads vs Google Ads) by attributed revenue and conversion rate to optimize advertising spend.
> 3. The live Propensity Calculator scores active sessions: if a user has high intent but hasn't checked out, the system can trigger an automated discount or free shipping notification to close the sale."*

---

## 3. Demo Walkthrough Steps for Evaluation
1. **Show Directory Structure:** Open the project folder in VS Code / File Explorer to show clean modular architecture (`src/`, `data/`, `app/`, `models/`, `docs/`).
2. **Execute Pipeline:** Double-click `run_pipeline.bat` or run `python run_pipeline.py`. Highlight the terminal log showing raw event generation, DuckDB warehouse Star Schema creation in ~1 second, feature extraction, and ML training benchmarks.
3. **Launch Dashboard:** Double-click `run_dashboard.bat`. Open browser to `http://localhost:8501`.
4. **Demonstrate Tabs:**
   - *Tab 1:* Show the 6 executive KPI cards and the interactive Conversion Funnel chart.
   - *Tab 2:* Show marketing channel revenue attribution and device breakdown.
   - *Tab 3:* Show product category affinity and the 24-hour diurnal conversion chart.
   - *Tab 4:* Show the model leaderboard and run a live prediction using the slider form.
   - *Tab 5:* Execute a live SQL query in the OLAP console to show the DuckDB Star Schema in action.
