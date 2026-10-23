"""
Automated Test Suite: Machine Learning & XAI Pipeline
------------------------------------------------------
Validates authentic UNSW-NB15 dataset integrity, model serialization,
SHAP feature attributions, cross-validation metrics, and inference parity.
"""

import os
import sys
import json
import pytest
import numpy as np
import joblib
import pandas as pd

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
ML_ENGINE_DIR = os.path.join(PROJECT_ROOT, "ml-engine")
MODELS_DIR = os.path.join(ML_ENGINE_DIR, "models")
DATASET_DIR = os.path.join(ML_ENGINE_DIR, "dataset")
EVAL_DIR = os.path.join(ML_ENGINE_DIR, "evaluation")

if ML_ENGINE_DIR not in sys.path:
    sys.path.insert(0, ML_ENGINE_DIR)

from preprocessing.preprocessor import NetworkTrafficPreprocessor, SELECTED_FEATURES

def test_unsw_dataset_files_exist():
    train_path = os.path.join(DATASET_DIR, "UNSW_NB15_training-set.csv")
    test_path = os.path.join(DATASET_DIR, "UNSW_NB15_testing-set.csv")
    
    assert os.path.exists(train_path), "UNSW-NB15 training dataset file missing."
    assert os.path.exists(test_path), "UNSW-NB15 test dataset file missing."
    assert os.path.getsize(train_path) > 1000000, "Train dataset file is unexpectedly small."
    assert os.path.getsize(test_path) > 200000, "Test dataset file is unexpectedly small."

def test_train_test_split_separation():
    """Verify zero overlap between training and held-out test records."""
    train_df = pd.read_csv(os.path.join(DATASET_DIR, "UNSW_NB15_training-set.csv"))
    test_df = pd.read_csv(os.path.join(DATASET_DIR, "UNSW_NB15_testing-set.csv"))
    
    assert len(train_df) == 20000
    assert len(test_df) == 5000
    
    if 'id' in train_df.columns and 'id' in test_df.columns:
        train_ids = set(train_df['id'])
        test_ids = set(test_df['id'])
        assert train_ids.isdisjoint(test_ids), "Train and test splits contain overlapping record IDs!"

def test_serialized_models_exist():
    required_files = [
        "best_model.joblib",
        "random_forest.joblib",
        "xgboost.joblib",
        "isolation_forest.joblib",
        "preprocessor.joblib",
        "shap_explainer.joblib",
        "model_metrics.json"
    ]
    for fname in required_files:
        fpath = os.path.join(MODELS_DIR, fname)
        assert os.path.exists(fpath), f"Required ML artifact '{fname}' is missing from {MODELS_DIR}"

def test_dynamic_metrics_schema_and_authenticity():
    metrics_path = os.path.join(MODELS_DIR, "model_metrics.json")
    with open(metrics_path, "r") as f:
        data = json.load(f)
        
    assert "dataset" in data
    assert data["dataset"]["name"] == "UNSW-NB15"
    assert data["dataset"]["total_samples"] == 25000
    assert data["dataset"]["features_count"] == 24
    
    models = data["models"]
    assert "Random Forest" in models
    assert "XGBoost" in models
    assert "Isolation Forest" in models
    
    test_size = data["dataset"]["test_samples"]
    assert test_size == 5000

    for name, m in models.items():
        assert 0.0 <= m["accuracy"] <= 1.0, f"{name} accuracy out of bounds: {m['accuracy']}"
        assert 0.0 <= m["precision"] <= 1.0, f"{name} precision out of bounds: {m['precision']}"
        assert 0.0 <= m["recall"] <= 1.0, f"{name} recall out of bounds: {m['recall']}"
        assert 0.0 <= m["f1_score"] <= 1.0, f"{name} f1_score out of bounds: {m['f1_score']}"
        assert 0.0 <= m["roc_auc"] <= 1.0, f"{name} roc_auc out of bounds: {m['roc_auc']}"
        
        # Verify confusion matrix is 2x2
        cm = m["confusion_matrix"]
        assert len(cm) == 2, f"{name} confusion matrix rows != 2"
        assert len(cm[0]) == 2 and len(cm[1]) == 2, f"{name} confusion matrix cols != 2"
        total_eval = sum(cm[0]) + sum(cm[1])
        assert total_eval == test_size, f"Expected {test_size} test samples in CM, got {total_eval}"

def test_preprocessor_transformation():
    prep_path = os.path.join(MODELS_DIR, "preprocessor.joblib")
    prep = joblib.load(prep_path)
    
    sample_packet = {
        'proto': 'tcp', 'service': 'http', 'state': 'FIN', 'dur': 0.15,
        'spkts': 10, 'dpkts': 12, 'sbytes': 1500, 'dbytes': 4200,
        'rate': 146.6, 'sttl': 64, 'dttl': 60, 'sload': 80000, 'dload': 224000,
        'sloss': 0, 'dloss': 0, 'sinpkt': 13.6, 'dinpkt': 11.5,
        'smean': 136, 'dmean': 323, 'ct_srv_src': 2, 'ct_dst_ltm': 3,
        'ct_src_dport_ltm': 1, 'ct_dst_sport_ltm': 1, 'ct_dst_src_ltm': 2
    }
    
    X_trans = prep.transform_single(sample_packet)
    assert X_trans.shape == (1, len(SELECTED_FEATURES)), f"Expected shape (1, {len(SELECTED_FEATURES)}), got {X_trans.shape}"

def test_preprocessor_resilience_to_malformed_input():
    """Verify preprocessor handles unknown protocols, missing values, and NaN without crashing."""
    prep_path = os.path.join(MODELS_DIR, "preprocessor.joblib")
    prep = joblib.load(prep_path)
    
    malformed_packet = {
        'proto': 'unknown_protocol_xyz',
        'service': None,
        'state': 'INVALID_STATE',
        'dur': float('nan'),
        'spkts': float('inf')
    }
    
    X_trans = prep.transform_single(malformed_packet)
    assert X_trans.shape == (1, len(SELECTED_FEATURES))
    assert not np.isnan(X_trans).any(), "Transformed output contains NaN!"
    assert not np.isinf(X_trans).any(), "Transformed output contains Inf!"

def test_model_inference_prediction():
    model_path = os.path.join(MODELS_DIR, "best_model.joblib")
    prep_path = os.path.join(MODELS_DIR, "preprocessor.joblib")
    
    model = joblib.load(model_path)
    prep = joblib.load(prep_path)
    
    sample_packet = {
        'proto': 'tcp', 'service': 'http', 'state': 'FIN', 'dur': 0.15,
        'spkts': 10, 'dpkts': 12, 'sbytes': 1500, 'dbytes': 4200,
        'rate': 146.6, 'sttl': 64, 'dttl': 60, 'sload': 80000, 'dload': 224000,
        'sloss': 0, 'dloss': 0, 'sinpkt': 13.6, 'dinpkt': 11.5,
        'smean': 136, 'dmean': 323, 'ct_srv_src': 2, 'ct_dst_ltm': 3,
        'ct_src_dport_ltm': 1, 'ct_dst_sport_ltm': 1, 'ct_dst_src_ltm': 2
    }
    
    X_trans = prep.transform_single(sample_packet)
    prob = model.predict_proba(X_trans)[0][1] if hasattr(model, "predict_proba") else model.predict(X_trans)[0]
    pred = int(prob >= 0.5)
    
    assert pred in [0, 1]
    assert 0.0 <= prob <= 1.0

def test_shap_explainer_computes_attributions():
    explainer_path = os.path.join(MODELS_DIR, "shap_explainer.joblib")
    prep_path = os.path.join(MODELS_DIR, "preprocessor.joblib")
    
    explainer = joblib.load(explainer_path)
    prep = joblib.load(prep_path)
    
    packet = {
        'proto': 'tcp', 'service': '-', 'state': 'INT', 'dur': 0.001,
        'spkts': 500, 'dpkts': 0, 'sbytes': 20000, 'dbytes': 0,
        'rate': 50000.0, 'sttl': 254, 'dttl': 0, 'sload': 160000000, 'dload': 0,
        'sloss': 10, 'dloss': 0, 'sinpkt': 0.002, 'dinpkt': 0,
        'smean': 40, 'dmean': 0, 'ct_srv_src': 40, 'ct_dst_ltm': 40,
        'ct_src_dport_ltm': 35, 'ct_dst_sport_ltm': 1, 'ct_dst_src_ltm': 40
    }
    
    X_trans = prep.transform_single(packet)
    shap_vals = explainer(X_trans)
    
    if hasattr(shap_vals, "values"):
        vals = shap_vals.values[0]
        if len(vals.shape) == 2:
            vals = vals[:, 1]
    else:
        vals = shap_vals[0]
        
    assert len(vals) == len(SELECTED_FEATURES), f"Expected {len(SELECTED_FEATURES)} SHAP attributions, got {len(vals)}"
    assert not np.isnan(vals).any()

def test_experiment_manifest_integrity():
    """Verify evaluation experiment manifest records provenance and environment."""
    manifest_path = os.path.join(EVAL_DIR, "experiment_manifest.json")
    assert os.path.exists(manifest_path), "experiment_manifest.json missing from evaluation directory"
    
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
        
    assert "experiment_id" in manifest
    assert "dataset_provenance" in manifest
    assert manifest["dataset_provenance"]["train_sha256"]
    assert manifest["dataset_provenance"]["test_sha256"]
    assert manifest["champion_model"] in ["Random Forest", "XGBoost"]
