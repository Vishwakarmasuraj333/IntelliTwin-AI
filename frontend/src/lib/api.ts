import {
  DashboardStats,
  NetworkPreset,
  PredictionResult,
  IncidentReport,
  SecurityEventItem,
  ModelComparisonData,
  SystemHealth,
  AuditLog,
  PresetPayload,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });

    if (!res.ok) {
      let errorMsg = `API Error ${res.status}: ${res.statusText}`;
      try {
        const errorData = await res.json();
        if (errorData.detail) errorMsg = errorData.detail;
        else if (errorData.message) errorMsg = errorData.message;
      } catch {
        // ignore parse error
      }
      throw new Error(errorMsg);
    }
    return (await res.json()) as T;
  } catch (err: any) {
    console.error(`Fetch error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Dashboard Telemetry
  getDashboardStats: () => fetchJson<DashboardStats>('/dashboard/stats'),

  // Presets & Simulator
  getAttackPresets: () => fetchJson<NetworkPreset[]>('/detection/presets'),
  predictNetworkTraffic: (packet: PresetPayload) =>
    fetchJson<PredictionResult>('/detection/predict', {
      method: 'POST',
      body: JSON.stringify(packet),
    }),

  // GenAI SOC Analyst Reports
  generateAiReport: (eventId: string, customNotes?: string) =>
    fetchJson<IncidentReport>('/reports/generate', {
      method: 'POST',
      body: JSON.stringify({ event_id: eventId, custom_notes: customNotes }),
    }),
  getReports: () => fetchJson<IncidentReport[]>('/reports'),
  getReportById: (reportId: string) => fetchJson<IncidentReport>(`/reports/${reportId}`),

  // Threat History Events
  getSecurityEvents: (params?: { severity?: string; prediction?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.severity) q.append('severity', params.severity);
    if (params?.prediction) q.append('prediction', params.prediction);
    if (params?.limit) q.append('limit', String(params.limit));
    return fetchJson<{ total: number; items: SecurityEventItem[] }>(`/events?${q.toString()}`);
  },

  // Dynamic ML Models & Comparison
  getModelComparison: () => fetchJson<ModelComparisonData>('/models/comparison'),
  switchActiveModel: (modelName: string, token?: string) =>
    fetchJson<{ status: string; active_model: string }>(`/models/switch/${modelName}`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    }),

  // Admin & Governance
  getSystemHealth: () => fetchJson<SystemHealth>('/admin/health'),
  getAuditLogs: (token?: string) =>
    fetchJson<AuditLog[]>('/admin/audit-logs', {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    }),
};
