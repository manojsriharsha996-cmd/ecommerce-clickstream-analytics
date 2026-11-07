"""
Module: conversion_model.py
Description: Trains, tunes, and evaluates Machine Learning models for predicting
browsing-to-purchase conversion probability on clickstream sessions.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

FEATURES_CSV = "data/processed/session_features.csv"
MODEL_DIR = "models"
MODEL_PKL = os.path.join(MODEL_DIR, "conversion_pipeline.pkl")
METRICS_JSON = os.path.join(MODEL_DIR, "model_metrics.json")

def train_and_evaluate_models(data_path=FEATURES_CSV):
    """
    Trains multiple models, evaluates test set performance, and saves the top pipeline.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)
    print(f"[ConversionModel] Loading session features from {data_path}...")
    df = pd.read_csv(data_path)
    
    # Define feature groups
    # Note: We omit payment_info_count and checkout_start_count or keep them as early funnel signals.
    # To predict conversion during browsing/carting stages:
    categorical_cols = ["traffic_channel", "device"]
    numeric_cols = [
        "session_duration_seconds",
        "browsing_events_count",
        "browsing_dwell_seconds",
        "is_bounce",
        "page_view_count",
        "product_view_count",
        "cart_add_count",
        "max_product_price",
        "avg_product_price",
        "cart_value",
        "max_dwell_seconds",
        "avg_dwell_per_event",
        "cart_to_view_ratio",
        "hour_of_day",
        "is_weekend"
    ]
    
    X = df[categorical_cols + numeric_cols]
    y = df["target_converted"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    print(f"[ConversionModel] Training set: {X_train.shape[0]:,} samples | Test set: {X_test.shape[0]:,} samples")
    print(f"[ConversionModel] Class distribution - Converted: {y.mean():.2%}")
    
    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
            ("num", StandardScaler(), numeric_cols)
        ]
    )
    
    candidate_models = {
        "Random Forest": RandomForestClassifier(n_estimators=120, max_depth=10, random_state=42, class_weight="balanced"),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.08, max_depth=5, random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    }
    
    benchmarks = {}
    best_pipeline = None
    best_auc = -1.0
    best_model_name = ""
    
    for name, clf in candidate_models.items():
        print(f"[ConversionModel] Fitting {name}...")
        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", clf)
        ])
        pipe.fit(X_train, y_train)
        
        y_pred = pipe.predict(X_test)
        y_prob = pipe.predict_proba(X_test)[:, 1]
        
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        auc = float(roc_auc_score(y_test, y_prob))
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        benchmarks[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "confusion_matrix": cm
        }
        print(f"   -> {name} | ROC-AUC: {auc:.4f} | F1: {f1:.4f} | Precision: {prec:.4f} | Recall: {rec:.4f}")
        
        if auc > best_auc:
            best_auc = auc
            best_pipeline = pipe
            best_model_name = name

    # Feature Importance extraction from Best Pipeline
    feature_importances = {}
    if hasattr(best_pipeline.named_steps["classifier"], "feature_importances_"):
        ohe_cols = list(best_pipeline.named_steps["preprocessor"].named_transformers_["cat"].get_feature_names_out(categorical_cols))
        all_feature_names = ohe_cols + numeric_cols
        importances = best_pipeline.named_steps["classifier"].feature_importances_
        sorted_indices = np.argsort(importances)[::-1]
        for idx in sorted_indices[:15]:
            feature_importances[all_feature_names[idx]] = round(float(importances[idx]), 4)

    # Save artifacts
    joblib.dump(best_pipeline, MODEL_PKL)
    print(f"[ConversionModel] Best model ({best_model_name}) saved to: {MODEL_PKL}")
    
    results_payload = {
        "best_model": best_model_name,
        "best_roc_auc": round(best_auc, 4),
        "evaluation_metrics": benchmarks,
        "feature_importances": feature_importances,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "numeric_features": numeric_cols,
        "categorical_features": categorical_cols
    }
    
    with open(METRICS_JSON, "w") as f:
        json.dump(results_payload, f, indent=4)
        
    print(f"[ConversionModel] Performance report saved to: {METRICS_JSON}")
    return results_payload

def predict_single_session(session_dict, model_path=MODEL_PKL):
    """
    Real-time inference function for live session prediction.
    """
    model = joblib.load(model_path)
    df_sample = pd.DataFrame([session_dict])
    prob = model.predict_proba(df_sample)[0][1]
    is_convert = bool(prob >= 0.5)
    return {
        "conversion_probability": round(float(prob), 4),
        "predicted_conversion": is_convert,
        "intent_tier": "High" if prob >= 0.70 else "Medium" if prob >= 0.35 else "Low"
    }

if __name__ == "__main__":
    train_and_evaluate_models()
