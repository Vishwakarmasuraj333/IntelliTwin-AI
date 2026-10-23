'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { NetworkPreset, PresetPayload, PredictionResult, IncidentReport } from '@/lib/types';
import { Badge } from '@/components/ui/Badge';
import { ShapWaterfall } from '@/components/ui/ShapWaterfall';
import { AiReportModal } from '@/components/detection/AiReportModal';
import {
  Terminal,
  Play,
  Sparkles,
  ShieldAlert,
  Flame,
  CheckCircle2,
  Info,
  Sliders,
  Layers,
  ArrowRight,
} from 'lucide-react';

const DEFAULT_PAYLOAD: PresetPayload = {
  proto: 'tcp',
  dur: 0.15,
  sbytes: 1200,
  dbytes: 3500,
  spkts: 15,
  dpkts: 18,
  service: 'http',
  state: 'FIN',
  ct_srv_src: 2,
  ct_dst_ltm: 2,
  ct_src_dport_ltm: 1,
  ct_dst_sport_ltm: 1,
  ct_dst_src_ltm: 1,
  sttl: 64,
  dttl: 60,
  sloss: 0,
  dloss: 0,
};

export default function DetectionPage() {
  const [presets, setPresets] = useState<NetworkPreset[]>([]);
  const [formData, setFormData] = useState<PresetPayload>(DEFAULT_PAYLOAD);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [aiReport, setAiReport] = useState<IncidentReport | null>(null);
  const [isAiLoading, setIsAiLoading] = useState<boolean>(false);
  const [modalOpen, setModalOpen] = useState<boolean>(false);

  useEffect(() => {
    api.getAttackPresets().then(setPresets).catch(console.error);
  }, []);

  const handlePresetSelect = (preset: NetworkPreset) => {
    setFormData(preset.payload);
  };

  const handleInputChange = (field: keyof PresetPayload, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: typeof prev[field] === 'number' ? Number(value) : value,
    }));
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await api.predictNetworkTraffic(formData);
      setResult(res);
    } catch (err: any) {
      alert(`Inference failed: ${err.message || err}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!result?.event_id) return;
    setIsAiLoading(true);
    try {
      const rep = await api.generateAiReport(result.event_id);
      setAiReport(rep);
      setModalOpen(true);
    } catch (err: any) {
      alert(`Failed to generate AI report: ${err.message || err}`);
    } finally {
      setIsAiLoading(false);
    }
  };

  return (
    <div className="space-y-8 pb-12 font-mono">
      {/* Page Header */}
      <div className="border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2.5">
            <Terminal className="w-6 h-6 text-cyan-400" />
            ML Detection Workspace & Network Simulator
          </h1>
          <Badge variant="purple">XAI &bull; SHAP</Badge>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Submit raw network parameters, evaluate anomaly classifications, inspect local SHAP factor
          attributions, and trigger Google Gemini SOC investigation.
        </p>
      </div>

      {/* Preset Selector */}
      <div className="p-4 rounded-xl bg-[#0D1322] border border-slate-800 space-y-3">
        <div className="flex items-center justify-between text-xs text-slate-300 font-semibold">
          <span className="flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5 text-cyan-400" />
            Attack Simulation Presets (1-Click Fill)
          </span>
          <span className="text-[11px] text-slate-500">Curated from UNSW-NB15 Benchmark</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
          {presets.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handlePresetSelect(p)}
              className="p-2.5 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/40 text-left transition-all group"
            >
              <div className="flex items-center justify-between mb-1">
                <Badge
                  variant={
                    p.category === 'DoS'
                      ? 'CRITICAL'
                      : p.category === 'Exploits'
                      ? 'HIGH'
                      : p.category === 'Reconnaissance'
                      ? 'MEDIUM'
                      : 'NORMAL'
                  }
                >
                  {p.category}
                </Badge>
              </div>
              <div className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300">
                {p.name}
              </div>
              <div className="text-[10px] text-slate-500 line-clamp-2 mt-0.5">
                {p.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Workspace: Simulator Form + Results */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Form Inputs (7 cols) */}
        <form
          onSubmit={handlePredict}
          className="lg:col-span-7 p-6 rounded-xl bg-[#0D1322] border border-slate-800 space-y-5"
        >
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              Network Flow Attributes
            </h2>
            <span className="text-[11px] text-slate-400">UNSW-NB15 Standard Format</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            {/* Protocol */}
            <div>
              <label className="block text-slate-400 mb-1">Protocol (proto)</label>
              <select
                value={formData.proto}
                onChange={(e) => handleInputChange('proto', e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="tcp">TCP</option>
                <option value="udp">UDP</option>
                <option value="arp">ARP</option>
                <option value="icmp">ICMP</option>
                <option value="ospf">OSPF</option>
              </select>
            </div>

            {/* Service */}
            <div>
              <label className="block text-slate-400 mb-1">Service</label>
              <select
                value={formData.service}
                onChange={(e) => handleInputChange('service', e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="http">HTTP / HTTPS</option>
                <option value="dns">DNS</option>
                <option value="ftp">FTP</option>
                <option value="ssh">SSH</option>
                <option value="smtp">SMTP</option>
                <option value="-">None / Raw (-)</option>
              </select>
            </div>

            {/* State */}
            <div>
              <label className="block text-slate-400 mb-1">Connection State</label>
              <select
                value={formData.state}
                onChange={(e) => handleInputChange('state', e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="FIN">FIN (Closed)</option>
                <option value="CON">CON (Established)</option>
                <option value="INT">INT (Interrupted)</option>
                <option value="REQ">REQ (Requested)</option>
                <option value="RST">RST (Reset)</option>
              </select>
            </div>

            {/* Duration */}
            <div>
              <label className="block text-slate-400 mb-1">Duration (s)</label>
              <input
                type="number"
                step="0.001"
                min="0"
                value={formData.dur}
                onChange={(e) => handleInputChange('dur', e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Source Bytes */}
            <div>
              <label className="block text-slate-400 mb-1">Source Bytes (sbytes)</label>
              <input
                type="number"
                min="0"
                value={formData.sbytes}
                onChange={(e) => handleInputChange('sbytes', e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Destination Bytes */}
            <div>
              <label className="block text-slate-400 mb-1">Dest Bytes (dbytes)</label>
              <input
                type="number"
                min="0"
                value={formData.dbytes}
                onChange={(e) => handleInputChange('dbytes', e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Source Packets */}
            <div>
              <label className="block text-slate-400 mb-1">Source Packets (spkts)</label>
              <input
                type="number"
                min="1"
                value={formData.spkts}
                onChange={(e) => handleInputChange('spkts', e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Dest Packets */}
            <div>
              <label className="block text-slate-400 mb-1">Dest Packets (dpkts)</label>
              <input
                type="number"
                min="0"
                value={formData.dpkts}
                onChange={(e) => handleInputChange('dpkts', e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Source TTL */}
            <div>
              <label className="block text-slate-400 mb-1">Source TTL (sttl)</label>
              <input
                type="number"
                min="0"
                max="255"
                value={formData.sttl}
                onChange={(e) => handleInputChange('sttl', e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Connections to Dest Port */}
            <div>
              <label className="block text-slate-400 mb-1">Same Dest Port Count</label>
              <input
                type="number"
                min="1"
                value={formData.ct_src_dport_ltm}
                onChange={(e) => handleInputChange('ct_src_dport_ltm', e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Connections to Dest IP */}
            <div>
              <label className="block text-slate-400 mb-1">Conns to Dest IP</label>
              <input
                type="number"
                min="1"
                value={formData.ct_dst_ltm}
                onChange={(e) => handleInputChange('ct_dst_ltm', e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Packet Loss */}
            <div>
              <label className="block text-slate-400 mb-1">Packets Dropped (sloss)</label>
              <input
                type="number"
                min="0"
                value={formData.sloss}
                onChange={(e) => handleInputChange('sloss', e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
            <button
              type="button"
              onClick={() => setFormData(DEFAULT_PAYLOAD)}
              className="text-xs text-slate-400 hover:text-slate-200 transition-colors"
            >
              Reset to Baseline
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition-all shadow-[0_0_15px_rgba(0,240,255,0.3)] disabled:opacity-50"
            >
              <Play className={`w-3.5 h-3.5 fill-current ${loading ? 'animate-pulse' : ''}`} />
              {loading ? 'Evaluating Model Inference...' : 'Analyze Network Flow'}
            </button>
          </div>
        </form>

        {/* Results & Explainable AI (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {result ? (
            <div className="p-6 rounded-xl bg-[#0D1322] border border-cyan-500/40 space-y-5 shadow-[0_0_20px_-5px_rgba(0,240,255,0.15)] animate-in fade-in duration-300">
              {/* Classification Badge & Title */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <Badge variant={result.prediction === 'ANOMALY' ? 'ANOMALY' : 'NORMAL'} dot>
                    {result.prediction} DETECTED
                  </Badge>
                  <Badge variant={result.severity}>{result.severity}</Badge>
                </div>
                <span className="text-[10px] text-slate-400">
                  Model: {result.model_name}
                </span>
              </div>

              {/* Gauge & Metrics */}
              <div className="grid grid-cols-2 gap-4 p-4 rounded-lg bg-slate-950 border border-slate-800">
                <div>
                  <div className="text-[11px] text-slate-400">Risk Score</div>
                  <div
                    className={`text-3xl font-bold ${
                      result.risk_score > 70
                        ? 'text-red-400'
                        : result.risk_score > 40
                        ? 'text-amber-400'
                        : 'text-emerald-400'
                    }`}
                  >
                    {result.risk_score}
                    <span className="text-xs text-slate-500"> / 100</span>
                  </div>
                </div>

                <div>
                  <div className="text-[11px] text-slate-400">Suspected Vector</div>
                  <div className="text-sm font-bold text-slate-200 mt-1">
                    {result.attack_category}
                  </div>
                  <div className="text-[10px] text-slate-400">
                    Confidence: {(result.confidence * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Explainable AI (SHAP Waterfall) */}
              <div className="pt-2">
                <ShapWaterfall features={result.shap_values} />
              </div>

              {/* Action Button: Trigger GenAI Incident Report */}
              <div className="pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={handleGenerateReport}
                  disabled={isAiLoading}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-gradient-to-r from-cyan-600 via-teal-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-bold text-xs transition-all shadow-[0_0_20px_rgba(0,240,255,0.25)] disabled:opacity-50"
                >
                  <Sparkles className={`w-4 h-4 ${isAiLoading ? 'animate-spin' : ''}`} />
                  {isAiLoading
                    ? 'Synthesizing Gemini SOC Triage Report...'
                    : 'Summon Google Gemini SOC Analyst'}
                </button>
              </div>
            </div>
          ) : (
            <div className="p-8 rounded-xl bg-[#0D1322] border border-slate-800 text-center space-y-4">
              <div className="w-12 h-12 rounded-full bg-cyan-950/40 border border-cyan-500/20 mx-auto flex items-center justify-center text-cyan-400">
                <Info className="w-6 h-6" />
              </div>
              <h3 className="text-sm font-bold text-slate-200">Awaiting Simulation Input</h3>
              <p className="text-xs text-slate-400 max-w-xs mx-auto leading-relaxed">
                Select an attack preset above or customize the telemetry flow parameters on the left,
                then click <b className="text-cyan-400">Analyze Network Flow</b>.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Incident Report Modal */}
      <AiReportModal
        report={aiReport}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </div>
  );
}
