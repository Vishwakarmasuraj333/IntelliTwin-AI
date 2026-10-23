'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { SystemHealth, AuditLog } from '@/lib/types';
import { Badge } from '@/components/ui/Badge';
import {
  Settings,
  ShieldCheck,
  Cpu,
  Key,
  Users,
  Database,
  Activity,
  CheckCircle2,
  AlertCircle,
  FileText,
  RefreshCw,
  Lock,
  LogOut,
  UserCheck
} from 'lucide-react';

export default function SettingsPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [token, setToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<any>(null);

  // Auth form state
  const [authEmail, setAuthEmail] = useState<string>('admin@intellitwin.ai');
  const [authPassword, setAuthPassword] = useState<string>('Admin@123456');
  const [authError, setAuthError] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState<boolean>(false);

  const fetchSettingsData = async (activeToken?: string | null) => {
    setLoading(true);
    try {
      const hData = await api.getSystemHealth().catch(() => null);
      if (hData) setHealth(hData);

      const authToken = activeToken !== undefined ? activeToken : token;
      if (authToken) {
        const lData = await api.getAuditLogs(authToken).catch(() => []);
        setAuditLogs(lData || []);
      } else {
        setAuditLogs([]);
      }
    } catch (e) {
      console.error('Error fetching settings:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const savedToken = typeof window !== 'undefined' ? sessionStorage.getItem('intellitwin_token') : null;
    const savedUser = typeof window !== 'undefined' ? sessionStorage.getItem('intellitwin_user') : null;
    if (savedToken) {
      setToken(savedToken);
      if (savedUser) setCurrentUser(JSON.parse(savedUser));
    }
    fetchSettingsData(savedToken);
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    try {
      const res = await api.login(authEmail, authPassword);
      setToken(res.access_token);
      setCurrentUser(res.user);
      sessionStorage.setItem('intellitwin_token', res.access_token);
      sessionStorage.setItem('intellitwin_user', JSON.stringify(res.user));
      await fetchSettingsData(res.access_token);
    } catch (err: any) {
      setAuthError(err.message || 'Authentication failed.');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setCurrentUser(null);
    sessionStorage.removeItem('intellitwin_token');
    sessionStorage.removeItem('intellitwin_user');
    setAuditLogs([]);
  };

  return (
    <div className="space-y-8 pb-12 font-mono">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2.5">
              <Settings className="w-6 h-6 text-cyan-400" />
              Platform Settings & Security Governance
            </h1>
            <Badge variant="cyan">ADMIN CONSOLE</Badge>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            System health diagnostic telemetry, Google Gemini integration status, RBAC access control & immutable audit trail.
          </p>
        </div>

        <button
          onClick={() => fetchSettingsData()}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-300 hover:text-cyan-400 text-xs transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          Run Health Diagnostics
        </button>
      </div>

      {/* Grid: Health Status + Authentication/Gemini */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Subsystem Health Diagnostics */}
        <div className="p-5 rounded-xl bg-[#0D1322] border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400" />
              Platform Health & Subsystem Probes
            </h3>
            <Badge variant={health?.status === 'HEALTHY' ? 'NORMAL' : 'MEDIUM'} dot>
              {health?.status || 'PROBING'}
            </Badge>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-2.5 rounded bg-slate-900/60 border border-slate-800">
              <span className="text-slate-400 flex items-center gap-2">
                <Database className="w-3.5 h-3.5 text-cyan-400" />
                Database Engine:
              </span>
              <span className="text-slate-200 font-semibold">{health?.database || 'Connecting...'}</span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded bg-slate-900/60 border border-slate-800">
              <span className="text-slate-400 flex items-center gap-2">
                <Cpu className="w-3.5 h-3.5 text-purple-400" />
                Active Champion Model:
              </span>
              <Badge variant="cyan">{health?.active_model || 'XGBoost'}</Badge>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded bg-slate-900/60 border border-slate-800">
              <span className="text-slate-400 flex items-center gap-2">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                ML Models Memory State:
              </span>
              <Badge variant={health?.ml_models_loaded ? 'NORMAL' : 'HIGH'}>
                {health?.ml_models_loaded ? 'LOADED & READY' : 'OFFLINE'}
              </Badge>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded bg-slate-900/60 border border-slate-800">
              <span className="text-slate-400 flex items-center gap-2">
                <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                SHAP TreeExplainer Subsystem:
              </span>
              <Badge variant={health?.shap_explainer_ready ? 'cyan' : 'MEDIUM'}>
                {health?.shap_explainer_ready ? 'INITIALIZED' : 'PENDING'}
              </Badge>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded bg-slate-900/60 border border-slate-800">
              <span className="text-slate-400 flex items-center gap-2">
                <Key className="w-3.5 h-3.5 text-amber-400" />
                Google Gemini API Status:
              </span>
              {health?.gemini_api_configured ? (
                <Badge variant="NORMAL">CONFIGURED (SERVER)</Badge>
              ) : (
                <Badge variant="purple">AUTONOMOUS FALLBACK ACTIVE</Badge>
              )}
            </div>

            <div className="flex items-center justify-between p-2.5 rounded bg-slate-900/60 border border-slate-800">
              <span className="text-slate-400">Server Process Uptime:</span>
              <span className="text-cyan-400 font-semibold">
                {health?.uptime_seconds ? `${health.uptime_seconds}s` : '0s'}
              </span>
            </div>
          </div>
        </div>

        {/* SOC Analyst / Admin Authentication Card */}
        <div className="p-5 rounded-xl bg-[#0D1322] border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Lock className="w-4 h-4 text-cyan-400" />
              Role-Based Access Control (RBAC)
            </h3>
            {currentUser && (
              <Badge variant="purple">{currentUser.role}</Badge>
            )}
          </div>

          {currentUser ? (
            <div className="space-y-4 text-xs">
              <div className="p-3 rounded bg-emerald-950/40 border border-emerald-500/30 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <UserCheck className="w-4 h-4 text-emerald-400" />
                  <div>
                    <div className="font-bold text-slate-100">{currentUser.name}</div>
                    <div className="text-[11px] text-slate-400">{currentUser.email}</div>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px]"
                >
                  <LogOut className="w-3 h-3" />
                  Sign Out
                </button>
              </div>

              <div className="p-3 rounded bg-slate-900/60 border border-slate-800 space-y-1.5 text-[11px] text-slate-400">
                <div className="font-bold text-slate-300">Session Privileges:</div>
                <div>&bull; Immutable SOC audit log inspection enabled.</div>
                <div>&bull; Real-time model architecture hot-swapping enabled.</div>
                <div>&bull; Authenticated inference session token active.</div>
              </div>
            </div>
          ) : (
            <form onSubmit={handleLogin} className="space-y-3 text-xs">
              <p className="text-[11px] text-slate-400">
                Authenticate with an authorized role to unlock privileged platform audit trails.
              </p>

              {authError && (
                <div className="p-2.5 rounded bg-red-950/40 border border-red-500/30 text-red-300 text-[11px]">
                  {authError}
                </div>
              )}

              <div>
                <label className="block text-slate-400 mb-1 text-[11px]">User Email</label>
                <input
                  type="email"
                  value={authEmail}
                  onChange={(e) => setAuthEmail(e.target.value)}
                  required
                  className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1 text-[11px]">Password</label>
                <input
                  type="password"
                  value={authPassword}
                  onChange={(e) => setAuthPassword(e.target.value)}
                  required
                  className="w-full px-3 py-1.5 rounded bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="flex items-center justify-between pt-1">
                <span className="text-[10px] text-slate-500">
                  Default Dev: admin@intellitwin.ai
                </span>
                <button
                  type="submit"
                  disabled={authLoading}
                  className="px-4 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs transition-colors"
                >
                  {authLoading ? 'Verifying...' : 'Authenticate'}
                </button>
              </div>
            </form>
          )}

          <div className="pt-2 border-t border-slate-800 text-[10px] text-slate-400 space-y-1">
            <div className="font-bold uppercase tracking-wider text-slate-500">Configured RBAC Roles:</div>
            <div className="flex flex-wrap gap-1.5">
              <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-700">ADMIN</span>
              <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-700">SECURITY_ANALYST</span>
              <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-700">USER</span>
            </div>
          </div>
        </div>
      </div>

      {/* Security Audit Trail Table */}
      <div className="p-5 rounded-xl bg-[#0D1322] border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-3">
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              Immutable SOC Audit Trail
            </h3>
            <p className="text-[11px] text-slate-400">
              Tamper-evident log of administrative actions, model inferences, and AI investigations.
            </p>
          </div>
          {token && (
            <Badge variant="cyan" dot>LIVE AUDIT STREAM</Badge>
          )}
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                <th className="py-2.5 px-3">Log ID</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3">User</th>
                <th className="py-2.5 px-3">IP Address</th>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {!token ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    <Lock className="w-5 h-5 text-slate-600 mx-auto mb-2" />
                    Authentication required. Sign in as an ADMIN above to view immutable security audit records.
                  </td>
                </tr>
              ) : auditLogs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    No audit records recorded in current session. Actions will stream here automatically.
                  </td>
                </tr>
              ) : (
                auditLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-900/40">
                    <td className="py-2.5 px-3 text-cyan-400 font-mono">#{log.id.slice(0, 8)}</td>
                    <td className="py-2.5 px-3 font-semibold text-slate-200">{log.action}</td>
                    <td className="py-2.5 px-3 text-slate-400">{log.user}</td>
                    <td className="py-2.5 px-3 text-slate-500 font-mono text-[11px]">{log.ip_address || '127.0.0.1'}</td>
                    <td className="py-2.5 px-3 text-slate-500 text-[11px]">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="py-2.5 px-3 text-slate-400 text-[11px] font-mono">
                      {log.details ? JSON.stringify(log.details) : '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
