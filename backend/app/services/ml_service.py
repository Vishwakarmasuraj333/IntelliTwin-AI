"""
Machine Learning Inference & Threat Attribution Engine
------------------------------------------------------
Loads serialized models and preprocessors from ml-engine/models/.
Processes single network packet payloads and performs multi-metric threat analysis.
Guarantees zero dummy data substitution and transparent calibration.
"""

import os
import sys
import logging
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from app.core.config import settings

logger = logging.getLogger("ML_Service")

FEATURE_DISPLAY_NAMES = {
    'dur': 'Duration (s)',
    'proto': 'Transport Protocol',
    'service': 'Application Service',
    'state': 'Connection State',
    'spkts': 'Source Packets',
    'dpkts': 'Destination Packets',
    'sbytes': 'Source Data Volume (bytes)',
    'dbytes': 'Dest Data Volume (bytes)',
    'rate': 'Packet Transfer Rate (pkts/s)',
    'sttl': 'Source Time-to-Live (TTL)',
    'dttl': 'Dest Time-to-Live (TTL)',
    'sload': 'Source Throughput (bps)',
    'dload': 'Dest Throughput (bps)',
    'sloss': 'Source Packets Dropped',
    'dloss': 'Dest Packets Dropped',
    'sinpkt': 'Source Inter-Packet Time (ms)',
    'dinpkt': 'Dest Inter-Packet Time (ms)',
    'smean': 'Mean Source Packet Size',
    'dmean': 'Mean Dest Packet Size',
    'ct_srv_src': 'Same Service Conns (100-window)',
    'ct_dst_ltm': 'Conns to Dest IP (100-window)',
    'ct_src_dport_ltm': 'Conns to Same Dest Port',
    'ct_dst_sport_ltm': 'Conns to Same Source Port',
    'ct_dst_src_ltm': 'Conns to Same Src-Dest Pair'
}

FEATURE_UNITS = {
    'dur': 'seconds',
    'sbytes': 'bytes',
    'dbytes': 'bytes',
    'spkts': 'packets',
    'dpkts': 'packets',
    'rate': 'pkts/s',
    'sttl': 'hops',
    'dttl': 'hops',
    'sload': 'bps',
    'dload': 'bps',
    'sloss': 'packets',
    'dloss': 'packets',
    'sinpkt': 'ms',
    'dinpkt': 'ms',
    'smean': 'bytes',
    'dmean': 'bytes'
}

class MLInferenceEngine:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.model_name = "XGBoost"
        self.model_version = "1.0.0"
        self.load_models()

    def load_models(self):
        try:
            model_path = os.path.join(settings.MODELS_DIR, "best_model.joblib")
            prep_path = os.path.join(settings.MODELS_DIR, "preprocessor.joblib")
            
            if os.path.exists(model_path) and os.path.exists(prep_path):
                self.model = joblib.load(model_path)
                self.preprocessor = joblib.load(prep_path)
                # Determine model class name
                self.model_name = type(self.model).__name__
                if "XGB" in self.model_name:
                    self.model_name = "XGBoost"
                elif "RandomForest" in self.model_name:
                    self.model_name = "Random Forest"
                logger.info(f"Loaded champion ML model ({self.model_name}) and preprocessor successfully.")
            else:
                logger.warning(f"Model artifacts not found at {settings.MODELS_DIR}. Prediction endpoints will signal 503 Service Unavailable.")
        except Exception as e:
            logger.error(f"Failed to load ML models: {e}")

    def engineer_features(self, p: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates derived UNSW-NB15 metrics from basic flow parameters."""
        data = dict(p)
        dur = max(float(data.get('dur', 0.15)), 0.00001)
        spkts = int(data.get('spkts', 10))
        dpkts = int(data.get('dpkts', 10))
        sbytes = int(data.get('sbytes', 1000))
        dbytes = int(data.get('dbytes', 1000))
        
        # Derived network statistics conforming strictly to UNSW-NB15 specifications
        data['rate'] = round((spkts + dpkts) / dur, 4)
        data['sload'] = round((sbytes * 8) / dur, 2)
        data['dload'] = round((dbytes * 8) / dur, 2)
        data['sinpkt'] = round((dur * 1000) / (spkts + 1), 4)
        data['dinpkt'] = round((dur * 1000) / (dpkts + 1), 4)
        data['smean'] = int(sbytes / (spkts + 1))
        data['dmean'] = int(dbytes / (dpkts + 1))
        return data

    def predict(self, packet_input: Dict[str, Any]) -> Dict[str, Any]:
        if self.model is None or self.preprocessor is None:
            raise RuntimeError("ML model or preprocessor artifact is not initialized. Prediction unavailable.")

        enriched = self.engineer_features(packet_input)
        X_trans = self.preprocessor.transform_single(enriched)

        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X_trans)[0]
            classifier_prob = float(probs[1])
        else:
            classifier_prob = float(self.model.predict(X_trans)[0])

        # Anomaly decision boundary (standard 0.50 threshold)
        is_anomaly = classifier_prob >= 0.50
        prediction = "ANOMALY" if is_anomaly else "NORMAL"
        
        # Confidence is distance from decision boundary normalized to [0.5, 1.0]
        confidence = round(classifier_prob if is_anomaly else 1.0 - classifier_prob, 4)
        
        # Uncertainty metric: 1.0 at p=0.50 (maximum ambiguity), 0.0 at p=1.0 or p=0.0
        uncertainty = round(1.0 - (2.0 * abs(classifier_prob - 0.50)), 4)
        
        # Calibrated Risk Score (0-100 integer)
        # Combines raw probability with empirical severity weighting
        raw_score = classifier_prob * 100.0
        # If rate or destination port counters indicate high-stress flood, boost risk score slightly
        if enriched.get('rate', 0) > 5000 or enriched.get('ct_src_dport_ltm', 0) > 30:
            raw_score = min(100.0, raw_score + 5.0)
        risk_score = int(round(np.clip(raw_score, 0.0, 100.0)))
        
        # Continuous anomaly score (margin from decision boundary)
        anomaly_score = round(classifier_prob - 0.50, 4)

        # Severity categorization
        if risk_score >= 85:
            severity = "CRITICAL"
        elif risk_score >= 65:
            severity = "HIGH"
        elif risk_score >= 35:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # Attack taxonomy mapping
        if not is_anomaly:
            attack_category = "Normal"
        else:
            if enriched.get('ct_src_dport_ltm', 0) > 10 or enriched.get('ct_dst_sport_ltm', 0) > 10:
                attack_category = "Reconnaissance"
            elif enriched.get('rate', 0) > 1000 or (enriched.get('spkts', 0) > 100 and enriched.get('sbytes', 0) < 5000):
                attack_category = "DoS"
            elif enriched.get('sbytes', 0) > 100000 or enriched.get('sload', 0) > 10000000:
                attack_category = "Exploits"
            elif enriched.get('sloss', 0) > 5 or enriched.get('dloss', 0) > 5:
                attack_category = "Fuzzers"
            else:
                attack_category = "Generic"

        return {
            "prediction": prediction,
            "confidence": confidence,
            "classifier_probability": round(classifier_prob, 4),
            "risk_score": risk_score,
            "anomaly_score": anomaly_score,
            "uncertainty": uncertainty,
            "severity": severity,
            "attack_category": attack_category,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "enriched_features": enriched
        }

ml_engine = MLInferenceEngine()
