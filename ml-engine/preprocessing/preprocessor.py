"""
UNSW-NB15 Cybersecurity Feature Preprocessing Pipeline
------------------------------------------------------
Cleans, encodes categorical network attributes, performs feature scaling,
and serializes pipeline artifacts for real-time inference.
Guarantees strict train/inference parity and zero target leakage.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Union
from sklearn.preprocessing import RobustScaler, OrdinalEncoder
from sklearn.compose import ColumnTransformer

PREPROCESSOR_DIR = os.path.dirname(os.path.abspath(__file__))
ML_ENGINE_DIR = os.path.dirname(PREPROCESSOR_DIR)
MODELS_DIR = os.path.join(ML_ENGINE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

SELECTED_FEATURES = [
    'dur', 'proto', 'service', 'state', 'spkts', 'dpkts', 'sbytes', 'dbytes',
    'rate', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'sinpkt',
    'dinpkt', 'smean', 'dmean', 'ct_srv_src', 'ct_dst_ltm', 'ct_src_dport_ltm',
    'ct_dst_sport_ltm', 'ct_dst_src_ltm'
]

CATEGORICAL_COLS = ['proto', 'service', 'state']
NUMERICAL_COLS = [c for c in SELECTED_FEATURES if c not in CATEGORICAL_COLS]

class NetworkTrafficPreprocessor:
    """
    Standardized Preprocessor fitting exclusively on training data.
    Uses ColumnTransformer with RobustScaler for numerical features
    and OrdinalEncoder with handle_unknown='use_encoded_value' for categoricals.
    """
    def __init__(self):
        self.feature_names = list(SELECTED_FEATURES)
        self.numerical_cols = list(NUMERICAL_COLS)
        self.categorical_cols = list(CATEGORICAL_COLS)
        self.is_fitted = False
        
        self.transformer = ColumnTransformer(
            transformers=[
                ('num', RobustScaler(), self.numerical_cols),
                ('cat', OrdinalEncoder(
                    handle_unknown='use_encoded_value',
                    unknown_value=-1
                ), self.categorical_cols)
            ],
            remainder='drop'
        )

    def fit(self, df: pd.DataFrame):
        """Fits preprocessing exclusively on the provided training dataframe."""
        df_clean = self._validate_and_sanitize(df, is_training=True)
        self.transformer.fit(df_clean)
        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transforms a dataframe into normalized feature matrix."""
        if not self.is_fitted:
            raise ValueError("Preprocessor has not been fitted yet! Call fit() on training data first.")
        df_clean = self._validate_and_sanitize(df, is_training=False)
        matrix = self.transformer.transform(df_clean)
        # Verify no NaN or Inf in transformed output
        matrix = np.nan_to_num(matrix, nan=0.0, posinf=1.0, neginf=-1.0)
        return matrix

    def transform_single(self, packet_dict: Dict[str, Any]) -> np.ndarray:
        """Transforms a single network flow dictionary for real-time inference."""
        df = pd.DataFrame([packet_dict])
        return self.transform(df)

    def _validate_and_sanitize(self, df: pd.DataFrame, is_training: bool = False) -> pd.DataFrame:
        """Validates schema, cleans missing/infinite values, and enforces feature order."""
        df_copy = pd.DataFrame(index=df.index)
        
        for col in self.numerical_cols:
            if col in df.columns:
                series = pd.to_numeric(df[col], errors='coerce')
                # Replace non-finite with 0.0 or column median if training
                series = series.replace([np.inf, -np.inf], np.nan)
                df_copy[col] = series.fillna(0.0)
            else:
                df_copy[col] = 0.0
                
        for col in self.categorical_cols:
            if col in df.columns:
                df_copy[col] = df[col].astype(str).str.strip().replace({'': '-', 'nan': '-', 'None': '-'})
            else:
                df_copy[col] = '-'
                
        return df_copy[SELECTED_FEATURES]

    def save(self, filepath: str = None):
        if filepath is None:
            filepath = os.path.join(MODELS_DIR, "preprocessor.joblib")
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str = None):
        if filepath is None:
            filepath = os.path.join(MODELS_DIR, "preprocessor.joblib")
        return joblib.load(filepath)

if __name__ == "__main__":
    print(f"NetworkTrafficPreprocessor schema: {len(SELECTED_FEATURES)} attributes.")
