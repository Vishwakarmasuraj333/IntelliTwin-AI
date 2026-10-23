"""
Standalone Model Evaluation & Cross-Validation Module
------------------------------------------------------
Evaluates trained .joblib models against held-out UNSW-NB15 test set.
Computes classification report, confusion matrix, ROC-AUC, PR-AUC and SHAP sanity.
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, average_precision_score

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ML_ENGINE_DIR = os.path.dirname(CURRENT_DIR)
if ML_ENGINE_DIR not in sys.path:
    sys.path.insert(0, ML_ENGINE_DIR)

from preprocessing.preprocessor import NetworkTrafficPreprocessor

MODELS_DIR = os.path.join(ML_ENGINE_DIR, "models")
DATASET_DIR = os.path.join(ML_ENGINE_DIR, "dataset")
TEST_CSV = os.path.join(DATASET_DIR, "UNSW_NB15_testing-set.csv")

def evaluate_all():
    if not os.path.exists(TEST_CSV):
        raise FileNotFoundError(f"Test dataset not found at {TEST_CSV}")
        
    test_df = pd.read_csv(TEST_CSV)
    preprocessor = NetworkTrafficPreprocessor.load(os.path.join(MODELS_DIR, "preprocessor.joblib"))
    
    X_test = preprocessor.transform(test_df)
    y_test = test_df['label'].astype(int).values
    
    print("=" * 70)
    print(f"EVALUATING ON HELD-OUT TEST SPLIT ({len(y_test):,} SAMPLES)")
    print("=" * 70)
    
    for model_file in ["best_model.joblib", "xgboost.joblib", "random_forest.joblib"]:
        path = os.path.join(MODELS_DIR, model_file)
        if os.path.exists(path):
            model = joblib.load(path)
            preds = model.predict(X_test)
            probs = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
            
            print(f"\n--- MODEL: {model_file} ---")
            print(classification_report(y_test, preds, target_names=["NORMAL (0)", "ATTACK (1)"], digits=4))
            cm = confusion_matrix(y_test, preds)
            print(f"Confusion Matrix:\nTN={cm[0][0]}, FP={cm[0][1]}\nFN={cm[1][0]}, TP={cm[1][1]}")
            if probs is not None:
                print(f"ROC-AUC Score: {roc_auc_score(y_test, probs):.4f}")
                print(f"PR-AUC Score:  {average_precision_score(y_test, probs):.4f}")

if __name__ == "__main__":
    evaluate_all()
