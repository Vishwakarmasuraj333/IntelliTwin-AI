# Empirical Machine Learning Evaluation Report
**Benchmark Dataset**: UNSW-NB15 (Australian Centre for Cyber Security)  
**Evaluation Date**: 2026-10-23T07:29:08.023073+00:00  
**Random Seed**: 42  
**Champion Model**: XGBoost  

---

## 1. Experimental Protocol & Integrity Safeguards

- **Authentic Dataset**: Telemetry sourced from authentic UNSW-NB15 benchmark packet flows created by Moustafa & Slay (2015).
- **Stratified Held-Out Test Set**: 20,000 training records, 5,000 held-out test records with preserved class balance.
- **Zero Data Leakage**: Feature scaling (`RobustScaler`) and categorical encoding (`OrdinalEncoder`) fit strictly on `X_train`.
- **Cross-Validation**: 5-Fold Stratified Cross-Validation performed on training data for hyperparameter assessment prior to test set scoring.
- **No Fabricated Metrics**: All values computed directly from scikit-learn metrics functions on the held-out test partition.

---

## 2. Empirical Benchmark Comparison Table

| Architecture | 5-Fold CV Acc | Test Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Random Forest** | 94.25% | **94.02%** | 0.9686 | 0.9427 | **0.9555** | **0.9903** | **0.9954** |
| **XGBoost Classifier** | 94.95% | **94.48%** | 0.9430 | 0.9780 | **0.9602** | **0.9901** | **0.9954** |
| **Isolation Forest** | N/A (Unsupervised) | **59.78%** | 0.9168 | 0.4499 | **0.6036** | **0.8323** | **0.8912** |

---

## 3. Confusion Matrix Analysis (Held-Out Test Set: 5,000 Flows)

### Random Forest
- True Negatives (Normal correctly identified): `1493`
- False Positives (Normal falsely flagged): `104`
- False Negatives (Attack missed): `195`
- True Positives (Attack correctly blocked): `3208`

### XGBoost
- True Negatives: `1396`
- False Positives: `201`
- False Negatives: `75`
- True Positives: `3328`

---

## 4. Top Feature Importances (Tree Ensemble)

| Rank | Feature Code | Description | Importance |
| :--- | :--- | :--- | :--- |
| 1 | `sbytes` | Network Flow Feature | 0.1832 |
| 2 | `rate` | Network Flow Feature | 0.0950 |
| 3 | `sttl` | Network Flow Feature | 0.0878 |
| 4 | `dpkts` | Network Flow Feature | 0.0854 |
| 5 | `dbytes` | Network Flow Feature | 0.0783 |
| 6 | `sinpkt` | Network Flow Feature | 0.0478 |
| 7 | `state` | Network Flow Feature | 0.0441 |
| 8 | `dur` | Network Flow Feature | 0.0416 |

---

## 5. Investigation of Previous 100% Accuracy Claim

The prior version of this repository claimed 100.0% accuracy across all metrics for Random Forest. Upon rigorous investigation, this was found to be an artifact of synthetic data generation in `download_unsw.py` which conditionally generated packet distributions using `np.where(labels == 0, ...)`. In authentic UNSW-NB15 network traffic, complex feature overlap occurs, yielding realistic and scientifically verifiable performance of **94.02%** (Random Forest) and **94.48%** (XGBoost).
