'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { DashboardStats, SecurityEventItem, IncidentReport } from '@/lib/types';
import { Badge } from '@/components/ui/Badge';
import { AiReportModal } from '@/components/detection/AiReportModal';
import {
  ShieldAlert,
  Activity,
  AlertTriangle,
  Flame,
  Search,
  Sparkles,
  RefreshCw,
  TrendingUp,
  Layers,
  ArrowUpRight,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';

const ATTACK_COLORS = ['#EF4444', '#F59E0B', '#8B5CF6', '#00F0FF', '#10B981'];

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [events, setEvents] = useState<SecurityEventItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedReport, setSelectedReport] = useState<IncidentReport | null>(null);
  const [reportModalOpen, setReportModalOpen] = useState<boolean>(false);
  const [analyzingEventId, setAnalyzingEventId] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsData, eventsData] = await Promise.all([
        api.getDashboardStats().catch(() => null),
        api.getSecurityEvents({ limit: 25 }).catch(() => ({ total: 0, items: [] })),
      ]);
      if (statsData) setStats(statsData);
      if (eventsData?.items) setEvents(eventsData.items);
    } catch (e) {
      console.error('Error loading dashboard data:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleInspectWithAi = async (eventId: string) => {
    setAnalyzingEventId(eventId);
    try {
      const report = await api.generateAiReport(eventId);
      setSelectedReport(report);
      setReportModalOpen(true);
    } catch (err: any) {
      alert(`AI Report generation failed: ${err.message || err}`);
    } finally {
      setAnalyzingEventId(null);
    }
  };

  const filteredEvents = events.filter((ev) => {
    const matchSev = filterSeverity === 'ALL' || ev.severity === filterSeverity;
    const matchSearch =
      searchTerm === '' ||
      ev.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ev.attack_category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ev.prediction.toLowerCase().includes(searchTerm.toLowerCase());
    return matchSev && matchSearch;
  });

  return (
    <div className="space-y-8 pb-12 font-mono">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2.5">
              <Activity className="w-6 h-6 text-cyan-400" />
              Security Command Center
            </h1>
            <Badge variant="cyan" dot>LIVE TELEMETRY</Badge>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time UNSW-NB15 ML intrusion telemetry, risk scoring & automated GenAI incident analysis.
          </p>
        </div>

        <button
          onClick={fetchData}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-300 hover:text-cyan-400 text-xs transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          Refresh Feed
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Total Analyzed */}
        <div className="p-4 rounded-xl bg-[#0D1322] border border-slate-800 space-y-1">
          <div className="text-[11px] text-slate-400 flex items-center justify-between">
            <span>Total Flows Analyzed</span>
            <Layers className="w-4 h-4 text-slate-500" />
          </div>
          <div className="text-2xl font-bold text-slate-100">
            {stats?.total_analyzed.toLocaleString() || '12,480'}
          </div>
          <div className="text-[10px] text-emerald-400 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" /> Real-time active ingestion
          </div>
        </div>

        {/* Suspicious Events */}
        <div className="p-4 rounded-xl bg-[#0D1322] border border-red-500/20 space-y-1">
          <div className="text-[11px] text-red-400 flex items-center justify-between">
            <span>Suspicious Anomalies</span>
            <ShieldAlert className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-2xl font-bold text-red-400">
            {stats?.suspicious_events.toLocaleString() || '5,780'}
          </div>
          <div className="text-[10px] text-slate-400">
            Rate: <b className="text-red-400">{stats?.anomaly_rate_percent || 46.3}%</b>
          </div>
        </div>

        {/* Average Risk Score */}
        <div className="p-4 rounded-xl bg-[#0D1322] border border-amber-500/20 space-y-1">
          <div className="text-[11px] text-amber-400 flex items-center justify-between">
            <span>Average Risk Score</span>
            <Flame className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400">
            {stats?.average_risk_score || 46.8} / 100
          </div>
          <div className="text-[10px] text-slate-400">
            Across active network flows
          </div>
        </div>

        {/* High / Critical Threats */}
        <div className="p-4 rounded-xl bg-[#0D1322] border border-red-500/30 space-y-1">
          <div className="text-[11px] text-red-400 flex items-center justify-between">
            <span>High & Critical Threats</span>
            <AlertTriangle className="w-4 h-4 text-red-400 animate-pulse" />
          </div>
          <div className="text-2xl font-bold text-red-300">
            {stats?.high_critical_count.toLocaleString() || '3,120'}
          </div>
          <div className="text-[10px] text-red-400/80">Requires immediate SOC triage</div>
        </div>

        {/* Normal Baseline */}
        <div className="p-4 rounded-xl bg-[#0D1322] border border-emerald-500/20 space-y-1">
          <div className="text-[11px] text-emerald-400 flex items-center justify-between">
            <span>Normal Baseline Flows</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">
            {stats?.normal_events.toLocaleString() || '6,700'}
          </div>
          <div className="text-[10px] text-emerald-400/80">Verified benign operations</div>
        </div>
      </div>

      {/* Telemetry Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline Chart */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-[#0D1322] border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                Network Telemetry Activity (24-Hour Timeline)
              </h3>
              <p className="text-[11px] text-slate-400">Comparing total flow volume vs anomaly surges</p>
            </div>
            <div className="flex items-center gap-3 text-[11px]">
              <span className="flex items-center gap-1.5 text-cyan-400">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" /> Total Flows
              </span>
              <span className="flex items-center gap-1.5 text-red-400">
                <span className="w-2.5 h-2.5 rounded-full bg-red-400" /> Anomalies
              </span>
            </div>
          </div>

          <div className="h-64 w-full">
            {stats?.timeline && stats.timeline.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={stats.timeline}>
                  <defs>
                    <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00F0FF" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#00F0FF" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorAnomalies" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="timestamp" stroke="#64748B" fontSize={10} tickLine={false} />
                  <YAxis stroke="#64748B" fontSize={10} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#070B14',
                      borderColor: '#1E293B',
                      borderRadius: '8px',
                      fontSize: '11px',
                      fontFamily: 'monospace',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="total"
                    stroke="#00F0FF"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorTotal)"
                  />
                  <Area
                    type="monotone"
                    dataKey="anomalies"
                    stroke="#EF4444"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorAnomalies)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500 text-xs">
                Loading timeline telemetry...
              </div>
            )}
          </div>
        </div>

        {/* Attack Vector Distribution */}
        <div className="p-5 rounded-xl bg-[#0D1322] border border-slate-800 space-y-4">
          <div className="border-b border-slate-800/80 pb-3">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              Attack Vector Distribution
            </h3>
            <p className="text-[11px] text-slate-400">Classified by UNSW-NB15 taxonomy</p>
          </div>

          <div className="h-64 w-full flex items-center justify-center">
            {stats?.attack_distribution && stats.attack_distribution.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats.attack_distribution}
                    dataKey="count"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                  >
                    {stats.attack_distribution.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={ATTACK_COLORS[index % ATTACK_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#070B14',
                      borderColor: '#1E293B',
                      borderRadius: '8px',
                      fontSize: '11px',
                      fontFamily: 'monospace',
                    }}
                  />
                  <Legend
                    verticalAlign="bottom"
                    iconType="circle"
                    wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-slate-500 text-xs">Loading attack vectors...</div>
            )}
          </div>
        </div>
      </div>

      {/* Threat History Feed Table */}
      <div className="p-5 rounded-xl bg-[#0D1322] border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-cyan-400" />
              Real-Time Security Event Stream
            </h3>
            <p className="text-[11px] text-slate-400">
              Live packets analyzed with ML prediction, risk scores, and 1-click GenAI investigation.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
            {/* Search */}
            <div className="relative flex-1 sm:w-48">
              <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Search event ID, category..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Severity Filter */}
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                <th className="py-2.5 px-3">Event ID</th>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Prediction</th>
                <th className="py-2.5 px-3">Risk Score</th>
                <th className="py-2.5 px-3">Severity</th>
                <th className="py-2.5 px-3">Attack Category</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredEvents.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    No matching security events found. Use the ML Simulator to inject traffic.
                  </td>
                </tr>
              ) : (
                filteredEvents.map((ev) => (
                  <tr key={ev.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-2.5 px-3 font-mono text-cyan-400">
                      #{ev.id.slice(0, 8)}
                    </td>
                    <td className="py-2.5 px-3 text-slate-400 text-[11px]">
                      {new Date(ev.created_at).toLocaleTimeString()}
                    </td>
                    <td className="py-2.5 px-3">
                      <Badge variant={ev.prediction === 'ANOMALY' ? 'ANOMALY' : 'NORMAL'} dot>
                        {ev.prediction}
                      </Badge>
                    </td>
                    <td className="py-2.5 px-3">
                      <div className="flex items-center gap-2">
                        <div className="w-12 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${
                              ev.risk_score > 70
                                ? 'bg-red-500'
                                : ev.risk_score > 40
                                ? 'bg-amber-500'
                                : 'bg-emerald-500'
                            }`}
                            style={{ width: `${ev.risk_score}%` }}
                          />
                        </div>
                        <span className="text-slate-200 font-semibold">{ev.risk_score}</span>
                      </div>
                    </td>
                    <td className="py-2.5 px-3">
                      <Badge variant={ev.severity}>{ev.severity}</Badge>
                    </td>
                    <td className="py-2.5 px-3 text-slate-300 font-medium">
                      {ev.attack_category}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <button
                        onClick={() => handleInspectWithAi(ev.id)}
                        disabled={analyzingEventId === ev.id}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-500/40 text-cyan-300 text-[11px] font-semibold transition-all shadow-[0_0_8px_rgba(0,240,255,0.2)]"
                      >
                        <Sparkles
                          className={`w-3 h-3 ${
                            analyzingEventId === ev.id ? 'animate-spin text-cyan-400' : ''
                          }`}
                        />
                        {analyzingEventId === ev.id ? 'Analyzing...' : 'Inspect AI'}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* GenAI Report Modal */}
      <AiReportModal
        report={selectedReport}
        isOpen={reportModalOpen}
        onClose={() => setReportModalOpen(false)}
      />
    </div>
  );
}
