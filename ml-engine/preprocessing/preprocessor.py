"""
UNSW-NB15 Cybersecurity Feature Preprocessing Pipeline
------------------------------------------------------
Cleans, encodes categorical network attributes, performs feature scaling,
and serializes pipeline artifacts for real-time inference.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler, LabelEncoder

PREPROCESSOR_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(os.path.dirname(PREPROCESSOR_DIR), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Selected robust feature set for detection and SHAP explanation
SELECTED_FEATURES = [
    'dur', 'proto', 'service', 'state', 'spkts', 'dpkts', 'sbytes', 'dbytes',
    'rate', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'sinpkt',
    'dinpkt', 'smean', 'dmean', 'ct_srv_src', 'ct_dst_ltm', 'ct_src_dport_ltm',
    'ct_dst_sport_ltm', 'ct_dst_src_ltm'
]

CATEGORICAL_COLS = ['proto', 'service', 'state']
NUMERICAL_COLS = [c for c in SELECTED_FEATURES if c not in CATEGORICAL_COLS]

class NetworkTrafficPreprocessor:
    def __init__(self):
        self.encoders = {}
        self.scaler = RobustScaler()
        self.feature_names = SELECTED_FEATURES
        self.is_fitted = False
        
    def fit(self, df: pd.DataFrame):
        df_copy = df.copy()
        
        # Fit LabelEncoders for categorical columns
        for col in CATEGORICAL_COLS:
            le = LabelEncoder()
            # Convert to string and handle unseen values safely
            col_data = df_copy[col].astype(str).tolist()
            col_data.append("unknown")
            le.fit(col_data)
            self.encoders[col] = le
            
        # Transform categoricals
        for col in CATEGORICAL_COLS:
            df_copy[col] = self.encoders[col].transform(df_copy[col].astype(str))
            
        # Fit scaler on numerical features
        self.scaler.fit(df_copy[NUMERICAL_COLS])
        self.is_fitted = True
        return self
        
    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Preprocessor has not been fitted yet!")
            
        df_copy = df.copy()
        
        # Ensure all required features are present; if missing, fill sensible defaults
        for col in SELECTED_FEATURES:
            if col not in df_copy.columns:
                if col in CATEGORICAL_COLS:
                    df_copy[col] = "unknown"
                else:
                    df_copy[col] = 0.0
                    
        # Encode categoricals with fallback for unseen classes
        for col in CATEGORICAL_COLS:
            le = self.encoders[col]
            classes = set(le.classes_)
            df_copy[col] = df_copy[col].astype(str).apply(lambda x: x if x in classes else "unknown")
            df_copy[col] = le.transform(df_copy[col])
            
        # Scale numericals
        scaled_numericals = self.scaler.transform(df_copy[NUMERICAL_COLS])
        scaled_num_df = pd.DataFrame(scaled_numericals, columns=NUMERICAL_COLS, index=df_copy.index)
        
        # Combine
        combined_df = pd.concat([df_copy[CATEGORICAL_COLS], scaled_num_df], axis=1)
        # Reorder to match exact SELECTED_FEATURES order
        ordered_df = combined_df[SELECTED_FEATURES]
        return ordered_df.values
        
    def transform_single(self, packet_dict: dict) -> np.ndarray:
        """Transforms a single network flow dictionary for real-time inference."""
        df = pd.DataFrame([packet_dict])
        return self.transform(df)

    def save(self, filepath: str = None):
        if filepath is None:
            filepath = os.path.join(MODELS_DIR, "preprocessor.joblib")
        joblib.dump(self, filepath)
        print(f"Saved preprocessor to {filepath}")

    @classmethod
    def load(cls, filepath: str = None):
        if filepath is None:
            filepath = os.path.join(MODELS_DIR, "preprocessor.joblib")
        return joblib.load(filepath)

if __name__ == "__main__":
    print(f"Feature schema defined with {len(SELECTED_FEATURES)} attributes.")
