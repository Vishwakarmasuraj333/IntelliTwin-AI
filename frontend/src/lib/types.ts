export interface ShapFeature {
  feature: string;
  feature_name_display: string;
  shap_value: number;
  feature_value: string | number;
  direction: 'increases_risk' | 'decreases_risk';
}

export interface PredictionResult {
  event_id: string;
  prediction: 'NORMAL' | 'ANOMALY';
  confidence: number;
  risk_score: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  attack_category: string;
  model_name: string;
  model_version: string;
  shap_values: ShapFeature[];
  analyzed_at: string;
  input_features: Record<string, any>;
}

export interface MitreTechnique {
  id: string;
  name: string;
  tactic: string;
}

export interface IncidentReport {
  report_id: string;
  event_id: string;
  title: string;
  executive_summary: string;
  technical_analysis: string;
  attack_category: string;
  mitre_attack: MitreTechnique[];
  why_suspicious: string[];
  investigation_steps: string[];
  mitigation_playbook: string[];
  confidence_assessment: string;
  generated_at: string;
  model_used: string;
}

export interface SecurityEventItem {
  id: string;
  user_id: string | null;
  prediction: 'NORMAL' | 'ANOMALY';
  confidence: number;
  risk_score: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  attack_category: string;
  model_version: string;
  created_at: string;
  event_data: Record<string, any>;
  shap_factors?: ShapFeature[];
}

export interface RocPoint {
  fpr: number;
  tpr: number;
}

export interface FeatureImportanceItem {
  feature: string;
  importance: number;
}

export interface ModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  confusion_matrix: number[][];
  roc_curve: RocPoint[];
  feature_importances: FeatureImportanceItem[];
}

export interface ModelComparisonData {
  dataset: {
    name: string;
    source: string;
    total_samples: number;
    train_samples: number;
    test_samples: number;
    features_count: number;
    feature_list: string[];
  };
  trained_at: string;
  best_model: string;
  models: Record<string, ModelMetrics>;
}

export interface TimelinePoint {
  timestamp: string;
  total: number;
  anomalies: number;
  normal: number;
}

export interface AttackDistributionItem {
  category: string;
  count: number;
  percentage: number;
}

export interface SeverityBreakdownItem {
  severity: string;
  count: number;
}

export interface DashboardStats {
  total_analyzed: number;
  suspicious_events: number;
  normal_events: number;
  anomaly_rate_percent: number;
  average_risk_score: number;
  high_critical_count: number;
  severity_breakdown: SeverityBreakdownItem[];
  attack_distribution: AttackDistributionItem[];
  timeline: TimelinePoint[];
}

export interface PresetPayload {
  proto: string;
  dur: number;
  sbytes: number;
  dbytes: number;
  spkts: number;
  dpkts: number;
  service: string;
  state: string;
  ct_srv_src: number;
  ct_dst_ltm: number;
  ct_src_dport_ltm: number;
  ct_dst_sport_ltm: number;
  ct_dst_src_ltm: number;
  sttl: number;
  dttl: number;
  sloss: number;
  dloss: number;
}

export interface NetworkPreset {
  name: string;
  description: string;
  category: string;
  payload: PresetPayload;
}

export interface SystemHealth {
  status: 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY';
  database: string;
  ml_models_loaded: boolean;
  active_model: string;
  shap_explainer_ready: boolean;
  gemini_api_configured: boolean;
  uptime_seconds: number;
  timestamp: string;
}

export interface AuditLog {
  id: string;
  action: string;
  user: string;
  ip_address?: string;
  details?: Record<string, any>;
  timestamp: string;
}
