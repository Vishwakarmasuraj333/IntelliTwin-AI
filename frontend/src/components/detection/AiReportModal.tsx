'use client';

import React from 'react';
import { IncidentReport } from '@/lib/types';
import { X, Sparkles, ShieldAlert, CheckCircle2, Copy, Printer, Terminal, Crosshair, Wrench } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

interface AiReportModalProps {
  report: IncidentReport | null;
  isOpen: boolean;
  onClose: () => void;
}

export const AiReportModal: React.FC<AiReportModalProps> = ({ report, isOpen, onClose }) => {
  if (!isOpen || !report) return null;

  const copyToClipboard = () => {
    const text = `
=== INTELLITWIN AI - INCIDENT REPORT ===
Title: ${report.title}
Attack Vector: ${report.attack_category}
Model: ${report.model_used}
Generated: ${report.generated_at}

EXECUTIVE SUMMARY:
${report.executive_summary}

TECHNICAL ANALYSIS:
${report.technical_analysis}

WHY SUSPICIOUS:
${(report.why_suspicious || []).map((s) => `* ${s}`).join('\n')}

INVESTIGATION STEPS:
${(report.investigation_steps || []).map((s, i) => `${i + 1}. ${s}`).join('\n')}

MITIGATION PLAYBOOK:
${(report.mitigation_playbook || []).map((s, i) => `${i + 1}. ${s}`).join('\n')}
    `.trim();
    navigator.clipboard.writeText(text);
    alert('Incident report copied to clipboard.');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-[#0B0F19] border border-cyan-500/40 rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-[0_0_30px_-5px_rgba(0,240,255,0.2)] overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-[#070B14]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded bg-cyan-950/80 border border-cyan-500/40 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-cyan-400 font-bold uppercase tracking-wider">
                  GenAI Security Operations Center Report
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  {report.model_used}
                </span>
              </div>
              <h2 className="text-base sm:text-lg font-bold text-slate-100 font-mono mt-0.5">
                {report.title}
              </h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800/80 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="p-6 overflow-y-auto space-y-6 font-mono text-xs text-slate-300">
          {/* Metadata Bar */}
          <div className="flex flex-wrap items-center gap-2 p-3 rounded-lg bg-slate-900/60 border border-slate-800">
            <span className="text-slate-400">Target Vector:</span>
            <Badge variant="ANOMALY">{report.attack_category}</Badge>
            <span className="text-slate-400 ml-3">Event Ref:</span>
            <span className="text-cyan-400 font-mono">#{report.event_id.slice(0, 12)}</span>
            <span className="text-slate-400 ml-3">Confidence:</span>
            <span className="text-emerald-400 font-semibold">{report.confidence_assessment}</span>
          </div>

          {/* MITRE ATT&CK Mapping */}
          {report.mitre_attack && report.mitre_attack.length > 0 && (
            <div>
              <div className="text-slate-400 font-semibold mb-2 flex items-center gap-1.5">
                <Crosshair className="w-3.5 h-3.5 text-cyan-400" />
                MITRE ATT&CK Mapping
              </div>
              <div className="flex flex-wrap gap-2">
                {report.mitre_attack.map((m, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900 border border-slate-700 text-xs"
                  >
                    <span className="text-red-400 font-bold">{m.id}</span>
                    <span className="text-slate-300">{m.name}</span>
                    <span className="text-[10px] text-slate-500">({m.tactic})</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Executive Summary */}
          <div className="p-4 rounded-lg bg-cyan-950/20 border border-cyan-500/20 space-y-1.5">
            <div className="text-cyan-400 font-bold tracking-wide uppercase text-[11px]">
              Executive Summary (CISO Briefing)
            </div>
            <p className="text-slate-200 leading-relaxed font-sans text-sm">
              {report.executive_summary}
            </p>
          </div>

          {/* Technical Analysis */}
          <div>
            <div className="text-slate-300 font-semibold mb-2 flex items-center gap-1.5 text-sm">
              <Terminal className="w-4 h-4 text-cyan-400" />
              Technical Telemetry Deep Dive
            </div>
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 leading-relaxed font-mono">
              {report.technical_analysis}
            </div>
          </div>

          {/* Why Suspicious */}
          <div>
            <div className="text-slate-300 font-semibold mb-2 flex items-center gap-1.5 text-sm">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              Explainable AI Anomaly Factors
            </div>
            <div className="space-y-2">
              {(report.why_suspicious || []).map((item, i) => (
                <div
                  key={i}
                  className="p-2.5 rounded bg-slate-900/50 border border-slate-800 flex items-start gap-2"
                >
                  <span className="text-amber-400 font-bold">›</span>
                  <span className="text-slate-300">{item}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Investigation Steps */}
          <div>
            <div className="text-slate-300 font-semibold mb-2 flex items-center gap-1.5 text-sm">
              <Crosshair className="w-4 h-4 text-blue-400" />
              Recommended SOC Investigation Playbook
            </div>
            <div className="space-y-2">
              {(report.investigation_steps || []).map((step, i) => (
                <div
                  key={i}
                  className="p-2.5 rounded bg-slate-900/50 border border-slate-800 flex items-start gap-3"
                >
                  <span className="w-5 h-5 rounded-full bg-blue-950 border border-blue-500/40 text-blue-400 flex items-center justify-center text-[10px] shrink-0 font-bold">
                    {i + 1}
                  </span>
                  <span className="text-slate-300 leading-relaxed">{step}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Mitigation Playbook */}
          <div>
            <div className="text-slate-300 font-semibold mb-2 flex items-center gap-1.5 text-sm">
              <Wrench className="w-4 h-4 text-emerald-400" />
              Containment & Remediation Actions
            </div>
            <div className="space-y-2">
              {(report.mitigation_playbook || []).map((action, i) => (
                <div
                  key={i}
                  className="p-2.5 rounded bg-emerald-950/20 border border-emerald-500/20 flex items-start gap-3"
                >
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span className="text-slate-200 leading-relaxed">{action}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-slate-800 bg-[#070B14] flex items-center justify-between">
          <span className="text-[11px] text-slate-500 font-mono">
            Report ID: {report.report_id || 'LOCAL-AI-GEN'}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={copyToClipboard}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 hover:bg-slate-700 font-mono text-xs transition-colors"
            >
              <Copy className="w-3.5 h-3.5 text-cyan-400" />
              Copy Report
            </button>
            <button
              onClick={() => window.print()}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-semibold font-mono text-xs transition-colors"
            >
              <Printer className="w-3.5 h-3.5" />
              Print / Export
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
