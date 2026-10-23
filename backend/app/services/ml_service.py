"""
Machine Learning Inference & Threat Attribution Engine
------------------------------------------------------
Loads serialized models and preprocessors from ml-engine/models/.
Processes single network packet payloads and performs multi-metric threat analysis.
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

class MLInferenceEngine:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.model_name = "Random Forest"
        self.model_version = "1.0.0"
        self.load_models()

    def load_models(self):
        try:
            model_path = os.path.join(settings.MODELS_DIR, "best_model.joblib")
            prep_path = os.path.join(settings.MODELS_DIR, "preprocessor.joblib")
            
            if os.path.exists(model_path) and os.path.exists(prep_path):
                self.model = joblib.load(model_path)
                self.preprocessor = joblib.load(prep_path)
                logger.info(f"Loaded ML model from {model_path} and preprocessor from {prep_path}")
            else:
                logger.warning(f"Model artifacts not found at {settings.MODELS_DIR}. Inference running in fallback mode.")
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
        
        # Derived network statistics
        data['rate'] = round((spkts + dpkts) / dur, 4)
        data['sload'] = round((sbytes * 8) / dur, 2)
        data['dload'] = round((dbytes * 8) / dur, 2)
        data['sinpkt'] = round((dur * 1000) / (spkts + 1), 4)
        data['dinpkt'] = round((dur * 1000) / (dpkts + 1), 4)
        data['smean'] = int(sbytes / (spkts + 1))
        data['dmean'] = int(dbytes / (dpkts + 1))
        return data

    def predict(self, packet_input: Dict[str, Any]) -> Dict[str, Any]:
        enriched = self.engineer_features(packet_input)
        
        if self.model is None or self.preprocessor is None:
            # Fallback heuristic if models have not yet been trained
            logger.warning("Using heuristic rule-based detection due to missing serialized model.")
            is_anomaly = enriched['rate'] > 500 or enriched['ct_src_dport_ltm'] > 15
            prob = 0.88 if is_anomaly else 0.12
        else:
            X_trans = self.preprocessor.transform_single(enriched)
            if hasattr(self.model, "predict_proba"):
                prob = float(self.model.predict_proba(X_trans)[0][1])
            else:
                prob = float(self.model.predict(X_trans)[0])
                
        is_anomaly = prob >= 0.50
        prediction = "ANOMALY" if is_anomaly else "NORMAL"
        confidence = round(prob if is_anomaly else 1.0 - prob, 4)
        risk_score = int(round(prob * 100))
        
        # Severity calculation
        if risk_score >= 85:
            severity = "CRITICAL"
        elif risk_score >= 65:
            severity = "HIGH"
        elif risk_score >= 35:
            severity = "MEDIUM"
        else:
            severity = "LOW"
            
        # Attack category classification
        if not is_anomaly:
            attack_category = "Normal"
        else:
            # Conditionally map to UNSW-NB15 attack taxonomy
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
            "risk_score": risk_score,
            "severity": severity,
            "attack_category": attack_category,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "enriched_features": enriched
        }

ml_engine = MLInferenceEngine()
