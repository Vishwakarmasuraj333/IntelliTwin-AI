'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { IncidentReport } from '@/lib/types';
import { Badge } from '@/components/ui/Badge';
import { AiReportModal } from '@/components/detection/AiReportModal';
import { FileText, Sparkles, Crosshair, ArrowRight, RefreshCw, ShieldAlert } from 'lucide-react';

export default function ReportsPage() {
  const [reports, setReports] = useState<IncidentReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<IncidentReport | null>(null);
  const [modalOpen, setModalOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const res = await api.getReports();
      setReports(res || []);
    } catch (e) {
      console.error('Failed to load reports:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const openReport = (report: IncidentReport) => {
    setSelectedReport(report);
    setModalOpen(true);
  };

  return (
    <div className="space-y-8 pb-12 font-mono">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2.5">
              <FileText className="w-6 h-6 text-cyan-400" />
              AI Generated Incident Investigation Reports
            </h1>
            <Badge variant="purple">GEMINI SOC COPILOT</Badge>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Archived incident reports synthesized by Google Gemini with MITRE ATT&CK mappings and mitigation playbooks.
          </p>
        </div>

        <button
          onClick={fetchReports}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-300 hover:text-cyan-400 text-xs transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          Refresh Archive
        </button>
      </div>

      {/* Reports Grid */}
      {reports.length === 0 ? (
        <div className="p-12 rounded-xl bg-[#0D1322] border border-slate-800 text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-purple-950/40 border border-purple-500/20 mx-auto flex items-center justify-center text-purple-400">
            <Sparkles className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-slate-200">No AI Reports Generated Yet</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            Run an anomaly detection simulation in the <b className="text-cyan-400">ML Simulator</b> or inspect any flagged event in the <b className="text-cyan-400">Command Center</b> to generate a full GenAI investigation report.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {reports.map((r) => (
            <div
              key={r.report_id || r.event_id}
              onClick={() => openReport(r)}
              className="p-5 rounded-xl bg-[#0D1322] border border-slate-800 hover:border-cyan-500/40 cursor-pointer transition-all space-y-3 group shadow-[0_0_15px_-3px_rgba(0,0,0,0.5)]"
            >
              <div className="flex items-center justify-between">
                <Badge variant="ANOMALY">{r.attack_category || 'Anomaly'}</Badge>
                <span className="text-[11px] text-slate-500">
                  {new Date(r.generated_at).toLocaleString()}
                </span>
              </div>

              <h3 className="text-sm font-bold text-slate-100 group-hover:text-cyan-300 transition-colors line-clamp-1">
                {r.title}
              </h3>

              <p className="text-xs text-slate-400 font-sans line-clamp-2 leading-relaxed">
                {r.executive_summary}
              </p>

              {/* MITRE Badges */}
              {r.mitre_attack && r.mitre_attack.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {r.mitre_attack.slice(0, 2).map((m, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[10px] text-slate-300 flex items-center gap-1"
                    >
                      <Crosshair className="w-2.5 h-2.5 text-red-400" />
                      {m.id}: {m.name}
                    </span>
                  ))}
                </div>
              )}

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs text-cyan-400">
                <span className="text-[11px] text-slate-500">
                  Event Ref: #{r.event_id.slice(0, 8)}
                </span>
                <span className="flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                  View Full Report <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* AI Report Modal */}
      <AiReportModal
        report={selectedReport}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </div>
  );
}
