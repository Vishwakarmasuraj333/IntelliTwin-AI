'use client';

import React from 'react';
import { ShapFeature } from '@/lib/types';
import { ArrowUpRight, ArrowDownRight, Info } from 'lucide-react';

interface ShapWaterfallProps {
  features: ShapFeature[];
  baseRisk?: number;
}

export const ShapWaterfall: React.FC<ShapWaterfallProps> = ({ features }) => {
  if (!features || features.length === 0) {
    return (
      <div className="p-6 text-center text-slate-500 font-mono text-xs border border-dashed border-slate-800 rounded-lg">
        No SHAP attribution vectors available for this transaction.
      </div>
    );
  }

  // Find max absolute value for proportional bar scaling
  const maxAbs = Math.max(...features.map((f) => Math.abs(f.shap_value)), 0.01);

  return (
    <div className="space-y-4 font-mono">
      <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800 pb-2">
        <span className="flex items-center gap-1.5 font-semibold text-slate-300">
          <Info className="w-3.5 h-3.5 text-cyan-400" />
          Feature Attribution (SHAP TreeExplainer)
        </span>
        <span className="text-[11px] text-slate-500">Positive: Threat Push | Negative: Baseline Push</span>
      </div>

      <div className="space-y-3">
        {features.map((item, index) => {
          const isRiskIncrease = item.direction === 'increases_risk';
          const percentage = Math.min((Math.abs(item.shap_value) / maxAbs) * 100, 100);

          return (
            <div key={index} className="group">
              <div className="flex items-center justify-between text-xs mb-1">
                <div className="flex items-center gap-2">
                  {isRiskIncrease ? (
                    <ArrowUpRight className="w-3.5 h-3.5 text-red-400 shrink-0" />
                  ) : (
                    <ArrowDownRight className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  )}
                  <span className="text-slate-200 font-medium group-hover:text-cyan-300 transition-colors">
                    {item.feature_name_display}
                  </span>
                  <span className="text-[10px] text-slate-500 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                    val: {String(item.feature_value)}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`font-semibold ${
                      isRiskIncrease ? 'text-red-400' : 'text-emerald-400'
                    }`}
                  >
                    {isRiskIncrease ? '+' : ''}
                    {item.shap_value.toFixed(4)}
                  </span>
                </div>
              </div>

              {/* Proportional Bar */}
              <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden flex border border-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isRiskIncrease
                      ? 'bg-gradient-to-r from-red-600 to-red-400 shadow-[0_0_8px_rgba(239,68,68,0.5)]'
                      : 'bg-gradient-to-r from-emerald-600 to-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.5)]'
                  }`}
                  style={{ width: `${Math.max(percentage, 5)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
