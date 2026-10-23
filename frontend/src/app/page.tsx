'use client';

import React from 'react';
import Link from 'next/link';
import { ShieldCheck, Activity, Terminal, Cpu, Sparkles, ArrowRight, Lock, CheckCircle2, AlertTriangle, Layers } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

export default function LandingPage() {
  return (
    <div className="space-y-16 py-6">
      {/* Hero Section */}
      <section className="text-center space-y-6 pt-6 pb-10 relative">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/70 border border-cyan-500/40 text-cyan-300 font-mono text-xs shadow-[0_0_15px_-3px_rgba(0,240,255,0.3)]">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-spin" />
          <span>PRODUCTION-GRADE AI SOC COPILOT &bull; M.SC. IT CAPSTONE</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight font-mono text-slate-100 max-w-4xl mx-auto leading-tight">
          Next-Gen Autonomous <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400">
            Cyber Threat Detection
          </span>
        </h1>

        <p className="max-w-2xl mx-auto text-slate-400 text-sm sm:text-base font-sans leading-relaxed">
          IntelliTwin AI combines deep network intrusion models trained on authentic UNSW-NB15 datasets,
          Explainable AI (SHAP) feature attributions, and Google Gemini Generative AI to deliver automated,
          enterprise-tier Security Operations Center (SOC) triage.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-6 py-3 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold font-mono text-sm transition-all shadow-[0_0_20px_rgba(0,240,255,0.4)]"
          >
            <Activity className="w-4 h-4" />
            Security Command Center
            <ArrowRight className="w-4 h-4 ml-1" />
          </Link>

          <Link
            href="/detection"
            className="flex items-center gap-2 px-6 py-3 rounded-lg bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-cyan-500/30 font-semibold font-mono text-sm transition-all"
          >
            <Terminal className="w-4 h-4 text-cyan-400" />
            Run Real-Time Simulator
          </Link>
        </div>

        {/* System Status Ticker */}
        <div className="pt-6 flex flex-wrap items-center justify-center gap-6 text-xs font-mono text-slate-400">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>UNSW-NB15 ML Engine: <b className="text-slate-200">ACTIVE</b></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400" />
            <span>SHAP TreeExplainer: <b className="text-slate-200">ONLINE</b></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-purple-400" />
            <span>Gemini AI Analyst: <b className="text-slate-200">ARMED</b></span>
          </div>
        </div>
      </section>

      {/* Architecture Showcase Cards */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Real ML Training */}
        <div className="p-6 rounded-xl bg-[#0D1322] border border-slate-800 hover:border-cyan-500/40 transition-all space-y-4 group">
          <div className="w-12 h-12 rounded-lg bg-cyan-950/60 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition-transform">
            <Cpu className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold font-mono text-slate-100">
            Real ML Pipeline (UNSW-NB15)
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed font-sans">
            Zero fabricated analytics. Models trained and cross-validated on 24 authentic network flow features
            from the Australian Centre for Cyber Security benchmark dataset.
          </p>
          <div className="pt-2 flex flex-wrap gap-2 text-[10px] font-mono">
            <Badge variant="cyan">Random Forest</Badge>
            <Badge variant="purple">XGBoost</Badge>
            <Badge variant="default">Isolation Forest</Badge>
          </div>
        </div>

        {/* Card 2: Explainable AI */}
        <div className="p-6 rounded-xl bg-[#0D1322] border border-slate-800 hover:border-emerald-500/40 transition-all space-y-4 group">
          <div className="w-12 h-12 rounded-lg bg-emerald-950/60 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-105 transition-transform">
            <Layers className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold font-mono text-slate-100">
            Explainable AI (SHAP)
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed font-sans">
            No black-box ambiguity. Every flagged anomaly computes exact Shapley feature attributions,
            pinpointing whether packet size, duration, or TTL caused the risk elevation.
          </p>
          <div className="pt-2 flex flex-wrap gap-2 text-[10px] font-mono">
            <Badge variant="NORMAL">TreeExplainer</Badge>
            <Badge variant="cyan">Local Feature Vectors</Badge>
          </div>
        </div>

        {/* Card 3: GenAI SOC Analyst */}
        <div className="p-6 rounded-xl bg-[#0D1322] border border-slate-800 hover:border-purple-500/40 transition-all space-y-4 group">
          <div className="w-12 h-12 rounded-lg bg-purple-950/60 border border-purple-500/30 flex items-center justify-center text-purple-400 group-hover:scale-105 transition-transform">
            <Sparkles className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold font-mono text-slate-100">
            Google Gemini SOC Analyst
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed font-sans">
            Automatically translates complex telemetry & SHAP values into Tier-3 SOC incident reports,
            MITRE ATT&CK technique IDs, and actionable firewall remediation playbooks.
          </p>
          <div className="pt-2 flex flex-wrap gap-2 text-[10px] font-mono">
            <Badge variant="purple">Gemini 1.5 Flash</Badge>
            <Badge variant="HIGH">MITRE ATT&CK</Badge>
            <Badge variant="cyan">Zero-Crash Safe</Badge>
          </div>
        </div>
      </section>

      {/* Interactive Telemetry Preview Banner */}
      <section className="p-6 sm:p-8 rounded-xl bg-gradient-to-r from-[#0D1322] via-[#0B182E] to-[#0D1322] border border-cyan-500/30 relative overflow-hidden">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
          <div className="space-y-2 text-left">
            <Badge variant="CRITICAL" dot>LIVE INCIDENT SIMULATION</Badge>
            <h2 className="text-xl sm:text-2xl font-bold font-mono text-slate-100">
              Test Attack Vectors with the Interactive Simulator
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 font-sans max-w-xl">
              Inject SYN flood DDoS bursts, port sweeps, or exploit payloads with 1 click.
              Witness the model calculate risk scores, generate SHAP waterfalls, and summon Gemini AI triage.
            </p>
          </div>
          <Link
            href="/detection"
            className="px-6 py-3 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold font-mono text-sm shrink-0 transition-colors"
          >
            Open ML Simulator &rarr;
          </Link>
        </div>
      </section>
    </div>
  );
}
