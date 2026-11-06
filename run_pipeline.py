"""
Module: run_pipeline.py
Description: End-to-end Master Orchestrator for the Big Data Clickstream Processing Pipeline.

Project: E-commerce clickstream analytics: A big-data clickstream processing pipeline Based Solution
Student: KOTAMSETTI MANOJ SRI HARSHA (Roll No: 23ME1A5433)
Guide: Mr. S.V. Swamy
Track: Big Data Analytics, Data Warehousing & Visualization
"""

import sys
import os
import time

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.log_generator import generate_clickstream_dataset
from src.warehouse_etl import run_warehouse_etl
from src.feature_engineering import extract_session_features
from src.conversion_model import train_and_evaluate_models

def main():
    start_total = time.time()
    print("=" * 75)
    print("   BIG DATA CLICKSTREAM PROCESSING PIPELINE: CONVERSION INTELLIGENCE")
    print("   Student: KOTAMSETTI MANOJ SRI HARSHA | Roll No: 23ME1A5433")
    print("   Guide: Mr. S.V. Swamy")
    print("   Domain: Big Data Analytics, Data Warehousing & Visualization")
    print("=" * 75)
    
    # Step 1: Log Generation
    print("\n[STEP 1/4] Generating Enterprise Clickstream Log Stream...")
    t0 = time.time()
    raw_df = generate_clickstream_dataset(num_sessions=12000, output_csv="data/raw/clickstream_logs.csv")
    print(f"-> Generated {len(raw_df):,} events across 12,000 sessions in {time.time()-t0:.2f}s")
    
    # Step 2: Data Warehouse ETL
    print("\n[STEP 2/4] Executing Big Data Warehouse ETL (Star Schema in DuckDB & Parquet)...")
    t0 = time.time()
    wh_summary = run_warehouse_etl(raw_csv="data/raw/clickstream_logs.csv")
    print(f"-> Warehouse built in {time.time()-t0:.2f}s | Fact Events: {wh_summary['fact_events']:,} | Sessions: {wh_summary['dim_sessions']:,}")
    
    # Step 3: Feature Engineering
    print("\n[STEP 3/4] Extracting Domain-Specific Behavioral & Funnel Features...")
    t0 = time.time()
    features_df = extract_session_features()
    print(f"-> Extracted {len(features_df):,} session feature vectors in {time.time()-t0:.2f}s")
    
    # Step 4: Machine Learning Modeling
    print("\n[STEP 4/4] Training & Evaluating Conversion Prediction Models...")
    t0 = time.time()
    model_results = train_and_evaluate_models()
    print(f"-> Model training completed in {time.time()-t0:.2f}s")
    print(f"-> Best Classifier: {model_results['best_model']} (ROC-AUC: {model_results['best_roc_auc']})")
    
    total_time = time.time() - start_total
    print("\n" + "=" * 75)
    print(f"   PIPELINE EXECUTION COMPLETED SUCCESSFULLY IN {total_time:.2f} SECONDS!")
    print("   To launch the marketing dashboard, execute:")
    print("   .venv\\Scripts\\python.exe -m streamlit run app/dashboard.py")
    print("=" * 75)

if __name__ == "__main__":
    main()
