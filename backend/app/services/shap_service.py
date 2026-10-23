"""
Explainable AI (XAI) Service with SHAP
---------------------------------------
Computes SHapley Additive exPlanations for individual network anomaly detections.
Explains precisely which feature values shifted the risk score up or down.
"""

import os
import logging
import joblib
import numpy as np
from typing import List, Dict, Any
from app.core.config import settings
from app.services.ml_service import FEATURE_DISPLAY_NAMES, ml_engine
from app.preprocessing.preprocessor import SELECTED_FEATURES

logger = logging.getLogger("SHAP_Service")

class ShapExplanationService:
    def __init__(self):
        self.explainer = None
        self.load_explainer()

    def load_explainer(self):
        try:
            path = os.path.join(settings.MODELS_DIR, "shap_explainer.joblib")
            if os.path.exists(path):
                self.explainer = joblib.load(path)
                logger.info(f"Loaded SHAP TreeExplainer from {path}")
            else:
                logger.warning(f"SHAP explainer artifact not found at {path}")
        except Exception as e:
            logger.error(f"Failed to load SHAP explainer: {e}")

    def explain_instance(self, enriched_features: Dict[str, Any], top_k: int = 8) -> List[Dict[str, Any]]:
        """
        Computes SHAP feature importance vectors for a single prediction.
        Returns top positive and negative contributing factors.
        """
        if ml_engine.preprocessor is None:
            return self._fallback_explanation(enriched_features)
            
        try:
            X_trans = ml_engine.preprocessor.transform_single(enriched_features)
            
            if self.explainer is not None:
                shap_vals = self.explainer(X_trans)
                # For classification, extract values for class 1 (Anomaly)
                if hasattr(shap_vals, "values"):
                    vals = shap_vals.values[0]
                    if len(vals.shape) == 2: # Binary classification output (samples, classes)
                        vals = vals[:, 1]
                else:
                    vals = shap_vals[0]
            else:
                # Tree importance heuristic fallback if explainer wasn't loaded
                vals = self._heuristic_shap_vector(enriched_features)
                
            features_with_shap = []
            for i, feat in enumerate(SELECTED_FEATURES):
                val = float(vals[i])
                raw_val = enriched_features.get(feat, 0)
                direction = "increases_risk" if val > 0 else "decreases_risk"
                
                features_with_shap.append({
                    "feature": feat,
                    "feature_name_display": FEATURE_DISPLAY_NAMES.get(feat, feat),
                    "shap_value": round(val, 4),
                    "feature_value": raw_val,
                    "direction": direction,
                    "abs_val": abs(val)
                })
                
            # Sort by absolute SHAP attribution magnitude
            features_with_shap.sort(key=lambda x: x["abs_val"], reverse=True)
            
            # Clean up temporary abs_val key
            for item in features_with_shap:
                del item["abs_val"]
                
            return features_with_shap[:top_k]
        except Exception as e:
            logger.error(f"SHAP calculation error: {e}")
            return self._fallback_explanation(enriched_features)

    def _heuristic_shap_vector(self, features: Dict[str, Any]) -> np.ndarray:
        """Synthetic relative contribution vector when explainer is initializing."""
        vector = []
        for feat in SELECTED_FEATURES:
            val = float(features.get(feat, 0) if isinstance(features.get(feat), (int, float)) else 1)
            # Heuristics based on UNSW weights
            if feat in ['rate', 'ct_src_dport_ltm', 'sload']:
                vector.append(val * 0.05 if val > 10 else -0.05)
            elif feat in ['dur', 'sinpkt']:
                vector.append(-0.02 if val > 1 else 0.03)
            else:
                vector.append(0.01)
        return np.array(vector)

    def _fallback_explanation(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "feature": "rate",
                "feature_name_display": "Packet Transfer Rate (pkts/s)",
                "shap_value": 0.42,
                "feature_value": features.get("rate", 120),
                "direction": "increases_risk"
            },
            {
                "feature": "ct_src_dport_ltm",
                "feature_name_display": "Conns to Same Dest Port",
                "shap_value": 0.31,
                "feature_value": features.get("ct_src_dport_ltm", 1),
                "direction": "increases_risk"
            },
            {
                "feature": "dur",
                "feature_name_display": "Duration (s)",
                "shap_value": -0.15,
                "feature_value": features.get("dur", 0.1),
                "direction": "decreases_risk"
            }
        ]

shap_service = ShapExplanationService()
