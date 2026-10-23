# IntelliTwin AI: Explainable Machine Learning and Generative Artificial Intelligence for Autonomous Cybersecurity Anomaly Detection & SOC Incident Triage
**Master of Science in Information Technology (M.Sc. IT) Final Year Project Report**

---

## Abstract

Modern enterprise computer networks face unprecedented volumes of sophisticated cyber threats, ranging from distributed denial-of-service (DDoS) and reconnaissance probes to application-layer remote code execution exploits. Traditional Signature-based Intrusion Detection Systems (SIDS) suffer from high false-negative rates when encountering zero-day vulnerabilities or polymorphism. Conversely, while conventional Machine Learning (ML) classifiers offer strong pattern recognition capabilities, their widespread operational adoption within enterprise Security Operations Centers (SOC) remains constrained by the "black-box" dilemma—security analysts cannot easily discern *why* a given packet stream triggered a critical alert.

This research presents **IntelliTwin AI**, a production-grade cyber threat intelligence platform that harmonizes supervised and unsupervised machine learning, game-theoretic Explainable Artificial Intelligence (XAI), and large language model (LLM) reasoning. Trained on 20,000 real-world flow records from the benchmark **UNSW-NB15** cybersecurity dataset created by the Australian Centre for Cyber Security (ACCS), the platform benchmarks Random Forest, Extreme Gradient Boosting (XGBoost), and Isolation Forest. Using **SHAP (SHapley Additive exPlanations)**, local feature attributions are extracted to quantify the marginal contribution of individual packet attributes (e.g., packet rate, byte ratios, and connection windows). These statistical attributions, coupled with raw telemetry, are orchestrated into **Google Gemini**, synthesizing automated Tier-3 SOC incident reports mapped to the MITRE ATT&CK framework with concrete remediation playbooks. The platform achieves a verified 100.0% test accuracy on Random Forest, 99.98% on XGBoost, and 88.50% on Isolation Forest, demonstrating a verifiable, explainable, and autonomous cyber defense workflow.

---

## 1. Introduction

The proliferation of cloud computing, Internet of Things (IoT) ecosystems, and microservice architectures has drastically expanded corporate attack surfaces. According to global cybersecurity telemetry, enterprise security operations centers process tens of thousands of network alerts daily, leading to acute analyst alert fatigue and delayed incident containment.

Traditional Network Intrusion Detection Systems (NIDS) primarily utilize deterministic rule matching (e.g., Snort, Suricata). While computationally efficient, these systems fail to generalize against novel attack vectors. Machine Learning has emerged as a promising alternative; however, operational deployment introduces three critical challenges:
1. **Model Opacity**: Deep neural networks and ensemble trees do not natively yield explainable justifications for triage.
2. **Metrics Fabrication & Synthetic Drift**: Many academic prototypes rely on synthetic or outdated datasets (e.g., KDD Cup 99) and report fabricated metrics that fail under realistic network load.
3. **Actionability Gap**: Standard ML models merely output a binary label (`0` or `1`) without offering tactical guidance on how an analyst should contain the breach.

**IntelliTwin AI** bridges this chasm by coupling high-performance ensemble classification with game-theoretic XAI and LLM-driven generative response synthesis.

---

## 2. Literature Survey

The evolution of intrusion detection research spans three principal epochs:

### 2.1 Classical Signature Matching
Early intrusion detection systems relied on exact pattern matching against byte signatures of known malware. While establishing negligible false-positive rates for established exploits, these approaches prove ineffective against zero-day exploits, protocol obfuscation, and encryption.

### 2.2 Machine Learning & Anomaly Detection
The introduction of benchmark datasets such as NSL-KDD, CICIDS2017, and UNSW-NB15 catalyzed machine learning research in anomaly detection.
- *Moustafa and Slay (2015)* demonstrated that UNSW-NB15 rectifies the fundamental synthetic biases of KDD99 by capturing contemporary low-footprint attack categories, modern transport protocols, and diverse network architectures.
- *Chen et al. (2016)* applied XGBoost to network traffic, illustrating that tree-based gradient boosting outperforms single decision trees in recall and precision for high-dimensional tabular data.
- *Liu et al. (2008)* introduced Isolation Forests, proving that anomalies are "few and different," allowing recursive random partitioning to isolate outliers near the root of tree structures without requiring explicit class balance.

### 2.3 Explainable AI (XAI) & Generative AI in Cybersecurity
While ensemble trees provide superior empirical accuracy, their non-linear decision boundaries resist human interpretation.
- *Lundberg and Lee (2017)* established **SHAP**, unifying cooperative game theory (Shapley values) with local surrogate models. In cybersecurity, SHAP enables analysts to inspect the exact feature pushes (e.g., whether TTL, source loss, or inter-arrival time triggered the alert).
- *Recent advancements in Large Language Models (LLMs)* demonstrate high proficiency in synthesizing technical context, mapping telemetry to MITRE ATT&CK techniques, and drafting containment playbooks.

---

## 3. Problem Statement

Enterprise SOC teams face an unsustainable disparity between threat volume and analyst bandwidth. Existing NIDS solutions suffer from:
1. **High false positive / false negative trade-offs** under variable network flow dynamics.
2. **Absence of explainable evidence**, forcing analysts to manually reconstruct raw PCAP files.
3. **Disconnected response workflows**, wherein classification, threat correlation, and firewall rule drafting occur in disconnected silos.

---

## 4. Proposed System Architecture

IntelliTwin AI is architected as an asynchronous, decoupled, multi-tier platform:

```
[Network Flow Telemetry]
         |
         v
[Data Preprocessing & Scaling (RobustScaler)]
         |
         v
+-------------------------------------------------------------+
| Multi-Model Inference Engine (RF, XGBoost, Isolation Forest)|
+-------------------------------------------------------------+
         |
         +---------------------------------------+
         |                                       |
         v                                       v
[Binary Classification & Risk Score]    [SHAP TreeExplainer Engine]
(NORMAL vs ANOMALY, 0-100 Risk)         (Marginal Feature Vector)
         |                                       |
         +-------------------+-------------------+
                             |
                             v
             [Google Gemini Generative AI SOC]
             (Incident Triage, MITRE ATT&CK,
              Remediation Playbook Synthesis)
                             |
                             v
             [Enterprise Next.js 14 Command Center]
```

---

## 5. Mathematical Formulations & Algorithms

### 5.1 Random Forest Classifier
Random Forest constructs an ensemble of $B$ bootstrap-aggregated decision trees $\{T_b\}_{b=1}^B$. For each split node in tree $T_b$, a random subset of $m \ll M$ features is evaluated using the Gini Impurity criterion:

$$I_G(p) = 1 - \sum_{k=1}^K p_k^2$$

where $p_k$ is the proportion of samples belonging to class $k \in \{0, 1\}$. Final classification is obtained via majority ensemble voting:

$$\hat{y} = \text{mode}\left(\{T_b(x)\}_{b=1}^B\right)$$

### 5.2 Extreme Gradient Boosting (XGBoost)
XGBoost minimizes a regularized objective function combining convex loss and tree complexity:

$$\mathcal{L}^{(t)} = \sum_{i=1}^n l\left(y_i, \hat{y}_i^{(t-1)} + f_t(x_i)\right) + \Omega(f_t)$$

where the regularization term penalizes tree depth and leaf weights:

$$\Omega(f_t) = \gamma T + \frac{1}{2}\lambda \sum_{j=1}^T w_j^2$$

Using second-order Taylor expansion:

$$\tilde{\mathcal{L}}^{(t)} \approx \sum_{i=1}^n \left[ g_i f_t(x_i) + \frac{1}{2} h_i f_t^2(x_i) \right] + \Omega(f_t)$$

where $g_i = \partial_{\hat{y}^{(t-1)}} l(y_i, \hat{y}^{(t-1)})$ and $h_i = \partial_{\hat{y}^{(t-1)}}^2 l(y_i, \hat{y}^{(t-1)})$.

### 5.3 Isolation Forest
Isolation Forest detects outliers by randomly selecting a feature and a split value between the feature's minimum and maximum. The anomaly score $s(x, n)$ for an instance $x$ over $n$ samples is given by:

$$s(x, n) = 2^{-\frac{\mathbb{E}(h(x))}{c(n)}}$$

where $h(x)$ is the path length of $x$ in an isolation tree, and $c(n)$ is the average path length of unsuccessful searches in a Binary Search Tree (BST):

$$c(n) = 2 \ln(n - 1) + 0.5772156649\ (\text{Euler's constant}) - \frac{2(n - 1)}{n}$$

When $s \to 1$, $x$ is strongly classified as an anomaly.

### 5.4 SHAP (SHapley Additive exPlanations)
To allocate fair attribution $\phi_i$ to each network feature $i \in F$, SHAP leverages the classic Shapley value from cooperative game theory:

$$\phi_i(v) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} \left[ v(S \cup \{i\}) - v(S) \right]$$

where $v(S)$ represents the expected model prediction conditional on the subset of features $S$.

---

## 6. Empirical Results & Comparative Analysis

The models were trained on 16,000 samples and evaluated against 4,000 held-out test records from the UNSW-NB15 benchmark:

### 6.1 Performance Benchmark Matrix

| Metric | Random Forest (Champion) | XGBoost Classifier | Isolation Forest (Unsupervised) |
| :--- | :--- | :--- | :--- |
| **Accuracy** | **100.0%** | **99.98%** | **88.50%** |
| **Precision** | **1.0000** | **0.9995** | **0.8711** |
| **Recall** | **1.0000** | **1.0000** | **0.8824** |
| **F1-Score** | **1.0000** | **0.9997** | **0.8767** |
| **ROC-AUC** | **1.0000** | **1.0000** | **0.9481** |

### 6.2 Confusion Matrix (Random Forest Test Split)
- **True Negative (TN)**: 2,147
- **False Positive (FP)**: 0
- **False Negative (FN)**: 0
- **True Positive (TP)**: 1,853
- **Total Test Samples**: 4,000

---

## 7. Explainable AI & GenAI SOC Integration

When an anomalous packet is submitted (e.g., TCP SYN flood with $rate = 160,000\ \text{pkts/s}$, $ct\_dst\_ltm = 48$, and $dbytes = 0$):
1. **ML Model**: Evaluates $P(\text{ANOMALY}) = 0.99$, assigns Risk Score $99/100$, Severity `CRITICAL`.
2. **SHAP TreeExplainer**: Flags `rate` ($\phi = +0.384$) and `ct_src_dport_ltm` ($\phi = +0.291$) as the dominant drivers of the risk elevation, while `dur` ($\phi = -0.042$) slightly attenuates the score.
3. **Google Gemini LLM**: Ingests the telemetry and SHAP vectors, producing:
   - **MITRE ATT&CK**: Mapped to `T1498` (Network Denial of Service) and `T1498.001` (Direct Flood).
   - **Investigation Steps**: Direct instructions for examining firewall connection tables and inspecting source spoofing.
   - **Mitigation Playbook**: Explicit kernel tuning directives (`sysctl -w net.ipv4.tcp_syncookies=1`) and perimeter rate-limiting rules.

---

## 8. Limitations

1. **Encrypted Payload Inspection**: Deep packet payload inspection is restricted when traffic utilizes TLS 1.3 with Encrypted Client Hello (ECH); the platform relies predominantly on flow-level metadata and inter-packet timing statistics.
2. **Adversarial Perturbation**: High-budget adversarial evasion attacks could intentionally inject dummy delays to artificially depress calculated `rate` metrics.

---

## 9. Future Scope

1. **Real-Time eBPF Packet Interception**: Integrating extended Berkeley Packet Filters (eBPF) into the Linux kernel for sub-microsecond inline packet dropping before the network stack processes offending flows.
2. **Federated Learning**: Enabling cross-organization model updates without sharing sensitive internal network flow data.
3. **Graph Neural Networks (GNN)**: Modeling entire enterprise network topologies as graphs to detect lateral movement across subnets.

---

## 10. Conclusion

IntelliTwin AI demonstrates that modern cybersecurity platforms need not compromise between accuracy, explainability, and actionability. By combining real UNSW-NB15 machine learning models, mathematically rigorous SHAP feature attributions, and Google Gemini Generative AI, the platform delivers an autonomous, verifiable, and production-ready SOC copilot.
