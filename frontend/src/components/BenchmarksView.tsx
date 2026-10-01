import React, { useState, useEffect } from 'react';
import type { BenchmarkResponse } from '../types';
import { fetchBenchmarks } from '../api';
import {
  ShieldCheck,
  Activity,
  Layers,
  Award,
  Zap,
  GitBranch
} from 'lucide-react';

export const BenchmarksView: React.FC = () => {
  const [data, setData] = useState<BenchmarkResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchBenchmarks()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center p-12 text-slate-400">
        <Activity className="w-6 h-6 animate-spin mr-2 text-indigo-500" />
        <span>Loading research benchmark results...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Research Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-white">Scientific Evaluation & Ablation Study</h2>
              <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-700">
                Peer-Review Ready
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Rigorous experimental comparison against classical baselines and systematic modality ablations.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs bg-slate-950 px-3 py-2 rounded-xl border border-slate-800">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <span className="text-slate-300">
              <strong>Validation Protocol:</strong> 5-Fold GroupKFold by Patient (ZERO Patient Leakage)
            </span>
          </div>
        </div>

        {/* Central Research Finding */}
        <div className="bg-indigo-950/40 border border-indigo-900/60 p-4 rounded-xl text-xs text-indigo-200/90 flex items-start gap-3">
          <Award className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
          <div>
            <div className="font-bold text-white mb-0.5">Empirical Research Conclusion</div>
            <p>{data.research_conclusion}</p>
          </div>
        </div>
      </div>

      {/* Table 1: Model Comparison (Baselines) */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-semibold text-white">Baseline Benchmark Comparison (5-Fold Cross-Validation)</h3>
          </div>
          <span className="text-[11px] text-slate-400">All models evaluated on out-of-fold patient partitions</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-4 py-3 font-semibold">Model Architecture</th>
                <th className="px-4 py-3 font-semibold">AUROC (OOF)</th>
                <th className="px-4 py-3 font-semibold">AUPRC (OOF)</th>
                <th className="px-4 py-3 font-semibold">Sensitivity (Recall)</th>
                <th className="px-4 py-3 font-semibold">Specificity</th>
                <th className="px-4 py-3 font-semibold">F1-Score</th>
                <th className="px-4 py-3 font-semibold">Brier Score</th>
                <th className="px-4 py-3 font-semibold">Calibration (ECE)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {data.baselines.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-4 py-3 font-semibold text-white flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-indigo-500" />
                    {row.Model}
                  </td>
                  <td className="px-4 py-3 font-mono font-bold text-emerald-400">{row.AUROC_OOF.toFixed(4)}</td>
                  <td className="px-4 py-3 font-mono text-indigo-300">{row.AUPRC_OOF.toFixed(4)}</td>
                  <td className="px-4 py-3 font-mono">{(row.Sensitivity * 100).toFixed(1)}%</td>
                  <td className="px-4 py-3 font-mono">{(row.Specificity * 100).toFixed(1)}%</td>
                  <td className="px-4 py-3 font-mono font-bold text-white">{row.F1_Score.toFixed(4)}</td>
                  <td className="px-4 py-3 font-mono text-slate-400">{row.Brier_Score?.toFixed(4)}</td>
                  <td className="px-4 py-3 font-mono text-slate-400">{row.ECE?.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Table 2: Critical Ablation Study */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-amber-400" />
            <h3 className="text-sm font-semibold text-white">Critical Modality & Personalization Ablation Study</h3>
          </div>
          <span className="text-[11px] text-slate-400">Tests contribution of EHR, SCG, ECG, and Personalization</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-4 py-3 font-semibold">Ablation Condition</th>
                <th className="px-4 py-3 font-semibold">Features</th>
                <th className="px-4 py-3 font-semibold">AUROC (OOF)</th>
                <th className="px-4 py-3 font-semibold">AUPRC (OOF)</th>
                <th className="px-4 py-3 font-semibold">Sensitivity</th>
                <th className="px-4 py-3 font-semibold">Specificity</th>
                <th className="px-4 py-3 font-semibold">F1-Score</th>
                <th className="px-4 py-3 font-semibold">Lead Time (Min)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {data.ablation_study.map((row, idx) => {
                const isFullTwin = row.Ablation_Condition?.includes('Full HeartFailureTwin');
                return (
                  <tr
                    key={idx}
                    className={`hover:bg-slate-800/40 transition-colors ${
                      isFullTwin ? 'bg-indigo-950/30 font-semibold' : ''
                    }`}
                  >
                    <td className="px-4 py-3 text-white flex items-center gap-2">
                      {isFullTwin && <Zap className="w-3.5 h-3.5 text-amber-400" />}
                      {row.Ablation_Condition}
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-400">{row.Num_Features}</td>
                    <td className="px-4 py-3 font-mono font-bold text-emerald-400">{row.AUROC_OOF.toFixed(4)}</td>
                    <td className="px-4 py-3 font-mono text-indigo-300">{row.AUPRC_OOF.toFixed(4)}</td>
                    <td className="px-4 py-3 font-mono">{(row.Sensitivity * 100).toFixed(1)}%</td>
                    <td className="px-4 py-3 font-mono">{(row.Specificity * 100).toFixed(1)}%</td>
                    <td className="px-4 py-3 font-mono font-bold text-white">{row.F1_Score.toFixed(4)}</td>
                    <td className="px-4 py-3 font-mono text-amber-300 font-bold">{row.Lead_Time_Min?.toFixed(2)} min</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
