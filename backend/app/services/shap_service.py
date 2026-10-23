"""
Explainable AI (XAI) Service with SHAP
---------------------------------------
Computes authentic SHapley Additive exPlanations for individual network anomaly detections.
Explains precisely which feature values shifted the risk score up or down.
Zero fabricated feature attributions - Failures are reported honestly.
"""

import os
import logging
import joblib
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from app.core.config import settings
from app.services.ml_service import FEATURE_DISPLAY_NAMES, FEATURE_UNITS, ml_engine
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
                logger.warning(f"SHAP explainer artifact not found at {path}. Explanations will report UNAVAILABLE.")
        except Exception as e:
            logger.error(f"Failed to load SHAP explainer: {e}")

    def explain_instance(
        self, enriched_features: Dict[str, Any], top_k: int = 8
    ) -> Tuple[List[Dict[str, Any]], Optional[float], str]:
        """
        Computes SHAP feature importance vectors for a single prediction.
        Returns:
            (factors_list, base_value, status_str)
        Never fabricates feature importances if the explainer is unavailable.
        """
        if ml_engine.preprocessor is None or self.explainer is None:
            logger.info("SHAP computation bypassed: Explainer or preprocessor is not loaded.")
            return [], None, "UNAVAILABLE"

        try:
            X_trans = ml_engine.preprocessor.transform_single(enriched_features)
            shap_obj = self.explainer(X_trans)

            base_val = None
            if hasattr(shap_obj, "base_values"):
                b_raw = shap_obj.base_values[0]
                if isinstance(b_raw, (np.ndarray, list)) and len(b_raw) > 1:
                    base_val = round(float(b_raw[1]), 4)
                else:
                    base_val = round(float(b_raw), 4)

            if hasattr(shap_obj, "values"):
                vals = shap_obj.values[0]
                # If multi-class or binary probability [samples, features, classes]
                if len(vals.shape) == 2:
                    vals = vals[:, 1]
            else:
                vals = shap_obj[0]

            features_with_shap = []
            for i, feat in enumerate(SELECTED_FEATURES):
                if i < len(vals):
                    val = float(vals[i])
                    raw_val = enriched_features.get(feat, 0)
                    direction = "increases_risk" if val > 0 else "decreases_risk"

                    features_with_shap.append({
                        "feature": feat,
                        "feature_name_display": FEATURE_DISPLAY_NAMES.get(feat, feat),
                        "shap_value": round(val, 4),
                        "feature_value": raw_val,
                        "direction": direction,
                        "units": FEATURE_UNITS.get(feat, ""),
                        "abs_val": abs(val)
                    })

            # Sort by absolute SHAP attribution magnitude
            features_with_shap.sort(key=lambda x: x["abs_val"], reverse=True)

            for item in features_with_shap:
                del item["abs_val"]

            return features_with_shap[:top_k], base_val, "SUCCESS"
        except Exception as e:
            logger.error(f"SHAP calculation error: {e}. Returning honest UNAVAILABLE status.")
            return [], None, "UNAVAILABLE"

shap_service = ShapExplanationService()
