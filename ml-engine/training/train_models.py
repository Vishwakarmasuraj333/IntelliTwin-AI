"""
IntelliTwin AI - Multi-Model Cybersecurity Anomaly Detection Training Pipeline
------------------------------------------------------------------------------
Trains Random Forest, XGBoost, and Isolation Forest models on UNSW-NB15.
Evaluates empirical metrics, computes SHAP TreeExplainer, and outputs model_metrics.json.
Zero fake metrics - All values derived from actual test set evaluation.
"""

import os
import sys
import json
import logging
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

# Adjust sys.path to enable intra-package imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ML_ENGINE_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, ML_ENGINE_DIR)

from dataset.download_unsw import prepare_dataset, TRAIN_CSV_PATH, TEST_CSV_PATH
from preprocessing.preprocessor import NetworkTrafficPreprocessor, SELECTED_FEATURES

from sklearn.ensemble import RandomForestClassifier, IsolationForest
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve
)
import shap

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ML_Pipeline")

MODELS_DIR = os.path.join(ML_ENGINE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)
METRICS_JSON_PATH = os.path.join(MODELS_DIR, "model_metrics.json")

def train_and_evaluate():
    logger.info("Step 1: Preparing UNSW-NB15 Dataset...")
    train_csv, test_csv = prepare_dataset()
    
    train_df = pd.read_csv(train_csv)
    test_df = pd.read_csv(test_csv)
    
    logger.info(f"Loaded {len(train_df)} training samples and {len(test_df)} test samples.")
    
    # Step 2: Preprocessing
    logger.info("Step 2: Fitting Preprocessor and scaling features...")
    preprocessor = NetworkTrafficPreprocessor()
    preprocessor.fit(train_df)
    preprocessor.save(os.path.join(MODELS_DIR, "preprocessor.joblib"))
    
    X_train = preprocessor.transform(train_df)
    y_train = train_df['label'].values
    
    X_test = preprocessor.transform(test_df)
    y_test = test_df['label'].values
    
    models = {}
    metrics_summary = {
        "dataset": {
            "name": "UNSW-NB15",
            "source": "Cyber Range Lab of the Australian Centre for Cyber Security (ACCS)",
            "total_samples": len(train_df) + len(test_df),
            "train_samples": len(train_df),
            "test_samples": len(test_df),
            "features_count": len(SELECTED_FEATURES),
            "feature_list": SELECTED_FEATURES,
            "anomaly_ratio_test": float(np.mean(y_test))
        },
        "trained_at": datetime.utcnow().isoformat() + "Z",
        "models": {}
    }
    
    # Step 3: Train Random Forest
    logger.info("Step 3A: Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    rf_probs = rf_model.predict_proba(X_test)[:, 1]
    
    rf_cm = confusion_matrix(y_test, rf_preds).tolist()
    rf_fpr, rf_tpr, _ = roc_curve(y_test, rf_probs)
    # Downsample ROC curve points to keep JSON compact for web charts
    roc_indices = np.linspace(0, len(rf_fpr) - 1, 30, dtype=int)
    rf_roc_pts = [{"fpr": round(float(rf_fpr[i]), 4), "tpr": round(float(rf_tpr[i]), 4)} for i in roc_indices]
    
    rf_feature_importances = [
        {"feature": feat, "importance": round(float(imp), 4)}
        for feat, imp in sorted(zip(SELECTED_FEATURES, rf_model.feature_importances_), key=lambda x: x[1], reverse=True)
    ]
    
    metrics_summary["models"]["Random Forest"] = {
        "accuracy": round(float(accuracy_score(y_test, rf_preds)), 4),
        "precision": round(float(precision_score(y_test, rf_preds)), 4),
        "recall": round(float(recall_score(y_test, rf_preds)), 4),
        "f1_score": round(float(f1_score(y_test, rf_preds)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, rf_probs)), 4),
        "confusion_matrix": rf_cm,
        "roc_curve": rf_roc_pts,
        "feature_importances": rf_feature_importances[:10]
    }
    joblib.dump(rf_model, os.path.join(MODELS_DIR, "random_forest.joblib"))
    models["Random Forest"] = (rf_model, metrics_summary["models"]["Random Forest"]["f1_score"])
    
    # Step 3B: Train XGBoost
    logger.info("Step 3B: Training XGBoost Classifier...")
    xgb_model = XGBClassifier(
        n_estimators=120,
        max_depth=6,
        learning_rate=0.08,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1
    )
    xgb_model.fit(X_train, y_train)
    xgb_preds = xgb_model.predict(X_test)
    xgb_probs = xgb_model.predict_proba(X_test)[:, 1]
    
    xgb_cm = confusion_matrix(y_test, xgb_preds).tolist()
    xgb_fpr, xgb_tpr, _ = roc_curve(y_test, xgb_probs)
    xgb_roc_pts = [{"fpr": round(float(xgb_fpr[i]), 4), "tpr": round(float(xgb_tpr[i]), 4)} for i in roc_indices]
    
    xgb_feature_importances = [
        {"feature": feat, "importance": round(float(imp), 4)}
        for feat, imp in sorted(zip(SELECTED_FEATURES, xgb_model.feature_importances_), key=lambda x: x[1], reverse=True)
    ]
    
    metrics_summary["models"]["XGBoost"] = {
        "accuracy": round(float(accuracy_score(y_test, xgb_preds)), 4),
        "precision": round(float(precision_score(y_test, xgb_preds)), 4),
        "recall": round(float(recall_score(y_test, xgb_preds)), 4),
        "f1_score": round(float(f1_score(y_test, xgb_preds)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, xgb_probs)), 4),
        "confusion_matrix": xgb_cm,
        "roc_curve": xgb_roc_pts,
        "feature_importances": xgb_feature_importances[:10]
    }
    joblib.dump(xgb_model, os.path.join(MODELS_DIR, "xgboost.joblib"))
    models["XGBoost"] = (xgb_model, metrics_summary["models"]["XGBoost"]["f1_score"])
    
    # Step 3C: Train Isolation Forest (Unsupervised Baseline)
    logger.info("Step 3C: Training Isolation Forest Baseline...")
    iso_model = IsolationForest(
        n_estimators=100,
        contamination=0.45,
        random_state=42,
        n_jobs=-1
    )
    iso_model.fit(X_train)
    iso_raw_preds = iso_model.predict(X_test)
    # IsolationForest outputs -1 for anomaly, 1 for normal -> convert to 1 (anomaly), 0 (normal)
    iso_preds = np.where(iso_raw_preds == -1, 1, 0)
    iso_scores = -iso_model.decision_function(X_test)
    
    iso_cm = confusion_matrix(y_test, iso_preds).tolist()
    metrics_summary["models"]["Isolation Forest"] = {
        "accuracy": round(float(accuracy_score(y_test, iso_preds)), 4),
        "precision": round(float(precision_score(y_test, iso_preds, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, iso_preds)), 4),
        "f1_score": round(float(f1_score(y_test, iso_preds, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, iso_scores)), 4),
        "confusion_matrix": iso_cm,
        "roc_curve": [],
        "feature_importances": []
    }
    joblib.dump(iso_model, os.path.join(MODELS_DIR, "isolation_forest.joblib"))
    
    # Step 4: Select Best Model and Setup SHAP Explainer
    logger.info("Step 4: Selecting Best Model and building SHAP Explainer...")
    best_model_name = "XGBoost" if metrics_summary["models"]["XGBoost"]["f1_score"] >= metrics_summary["models"]["Random Forest"]["f1_score"] else "Random Forest"
    best_model, best_f1 = models[best_model_name]
    logger.info(f"Champion Model selected: {best_model_name} (F1-Score: {best_f1})")
    
    joblib.dump(best_model, os.path.join(MODELS_DIR, "best_model.joblib"))
    metrics_summary["best_model"] = best_model_name
    
    # Build SHAP TreeExplainer on a background sample
    logger.info("Initializing SHAP TreeExplainer...")
    background_sample = X_train[:150]
    explainer = shap.TreeExplainer(best_model, data=background_sample)
    joblib.dump(explainer, os.path.join(MODELS_DIR, "shap_explainer.joblib"))
    
    # Save Dynamic Metrics JSON
    with open(METRICS_JSON_PATH, "w") as f:
        json.dump(metrics_summary, f, indent=2)
    logger.info(f"Generated dynamic metrics at: {METRICS_JSON_PATH}")
    
    # Print Summary Table
    print("\n" + "="*70)
    print("           INTELLITWIN AI - MODEL EVALUATION BENCHMARK")
    print("="*70)
    print(f"{'Model':<20} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'ROC-AUC':<10}")
    print("-" * 70)
    for name, m in metrics_summary["models"].items():
        print(f"{name:<20} | {m['accuracy']:<10} | {m['precision']:<10} | {m['recall']:<10} | {m['f1_score']:<10} | {m['roc_auc']:<10}")
    print("="*70 + "\n")
    return metrics_summary

if __name__ == "__main__":
    train_and_evaluate()
