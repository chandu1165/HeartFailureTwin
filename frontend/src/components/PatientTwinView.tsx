import React, { useState } from 'react';
import type { PatientProfile, DigitalTwinState, TimelinePoint } from '../types';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceArea,
  ReferenceLine,
  AreaChart,
  Area
} from 'recharts';
import {
  Cpu,
  Activity,
  Sliders,
  PlaySquare,
  HelpCircle,
  Clock,
  Sparkles
} from 'lucide-react';

interface PatientTwinViewProps {
  profile: PatientProfile | null;
  state: DigitalTwinState | null;
  timeline: TimelinePoint[];
  onNavigateTab: (tab: string) => void;
}

export const PatientTwinView: React.FC<PatientTwinViewProps> = ({
  profile,
  state,
  timeline,
  onNavigateTab
}) => {
  const [activeSignal, setActiveSignal] = useState<'hr' | 'scg' | 'rmssd' | 'resp'>('hr');

  if (!profile || !state) {
    return (
      <div className="flex items-center justify-center p-12 text-slate-400">
        <Activity className="w-6 h-6 animate-spin mr-2 text-indigo-500" />
        <span>Loading patient Digital Twin data...</span>
      </div>
    );
  }

  const baseRanges = profile.baseline_ranges || {};
  const currentRiskPct = Math.round(state.risk_score * 100);

  // Trajectory projection points
  const forecast = state.forecast_trajectory || {};
  const trajectoryData = [
    { label: 'Observed -24h', risk: timeline[0] ? timeline[0].risk_score * 100 : 15, isFuture: false },
    { label: 'Observed -12h', risk: timeline[Math.floor(timeline.length / 2)] ? timeline[Math.floor(timeline.length / 2)].risk_score * 100 : 25, isFuture: false },
    { label: 'NOW', risk: currentRiskPct, isFuture: false },
    { label: '+6h Forecast', risk: Math.round((forecast['6h'] || 0.45) * 100), isFuture: true },
    { label: '+12h Forecast', risk: Math.round((forecast['12h'] || 0.58) * 100), isFuture: true },
    { label: '+24h Forecast', risk: Math.round((forecast['24h'] || 0.72) * 100), isFuture: true },
  ];

  return (
    <div className="space-y-6">
      {/* Top Patient Profile Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-950 border border-indigo-700/60 flex items-center justify-center text-indigo-400 font-bold text-lg">
              {profile.patient_id.split('-')[1] || profile.patient_id}
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-bold text-white">{profile.name}</h2>
                <span className="px-2 py-0.5 rounded text-xs font-semibold bg-indigo-950 text-indigo-300 border border-indigo-800">
                  {profile.hf_subtype}
                </span>
                <span className="px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-300">
                  NYHA Class {profile.nyha_class}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-4 mt-1.5 text-xs text-slate-400">
                <span>{profile.age} yrs • {profile.gender}</span>
                <span>BMI: {profile.bmi}</span>
                <span>Baseline BP: {profile.baseline_sbp}/{profile.baseline_dbp} mmHg</span>
                <span>Comorbidities: {profile.comorbidities.join(', ')}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onNavigateTab('replay')}
              className="px-3 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition flex items-center gap-2 shadow-sm shadow-indigo-600/30"
            >
              <PlaySquare className="w-3.5 h-3.5" />
              <span>Launch Twin Replay</span>
            </button>
            <button
              onClick={() => onNavigateTab('whatif')}
              className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-medium transition flex items-center gap-2"
            >
              <Sliders className="w-3.5 h-3.5 text-indigo-400" />
              <span>What-If Simulation</span>
            </button>
          </div>
        </div>
      </div>

      {/* Grid: Current State Card & Explainability */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Current State & Latent State Vector */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-indigo-400" />
              Digital Twin Current State
            </span>
            <span className="text-xs text-slate-500 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              Live Estimate
            </span>
          </div>

          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800/80">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-400">Computational State:</span>
                <div className="text-lg font-bold text-white mt-0.5">{state.state_label}</div>
              </div>
              <div className="text-right">
                <span className="text-xs text-slate-400">Decompensation Risk:</span>
                <div className={`text-2xl font-black ${currentRiskPct > 65 ? 'text-rose-400' : currentRiskPct > 40 ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {currentRiskPct}%
                </div>
              </div>
            </div>

            <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-slate-400 pt-2 border-t border-slate-800/60">
              <div>
                Trend: <span className="font-semibold text-slate-200">{state.risk_trend}</span>
              </div>
              <div>
                Alert Level: <span className="font-semibold text-amber-400">{state.alert_level}</span>
              </div>
              <div>
                Quality Index: <span className="font-mono text-emerald-400">{(state.data_quality.overall * 100).toFixed(0)}%</span>
              </div>
              <div>
                Confidence: <span className="font-semibold text-slate-200">{state.confidence}</span>
              </div>
            </div>
          </div>

          {/* 8-Dimensional Latent State Vector S(t) */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-medium">Latent Physiological State Vector S(t)</span>
              <span className="text-[10px] text-slate-500">[-1.0, +1.0] Normalized Space</span>
            </div>
            <div className="grid grid-cols-4 gap-1.5">
              {state.state_vector.map((val, idx) => (
                <div key={idx} className="bg-slate-950 p-2 rounded-lg border border-slate-800 text-center">
                  <div className="text-[9px] text-slate-500 font-mono">dim_{idx}</div>
                  <div className={`text-xs font-mono font-bold mt-0.5 ${val > 0.3 ? 'text-rose-400' : val < -0.3 ? 'text-blue-400' : 'text-slate-300'}`}>
                    {val > 0 ? `+${val.toFixed(2)}` : val.toFixed(2)}
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1 mt-1 overflow-hidden">
                    <div
                      className={`h-full ${val > 0 ? 'bg-rose-500' : 'bg-blue-500'}`}
                      style={{ width: `${Math.min(100, Math.abs(val) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Signal Quality Gauges */}
          <div className="pt-2 border-t border-slate-800/60 space-y-2 text-xs">
            <span className="text-slate-400 font-medium">Sensor Signal Quality Integrity</span>
            <div className="space-y-1.5">
              <div>
                <div className="flex justify-between text-[11px] text-slate-300 mb-0.5">
                  <span>Wearable Patch ECG</span>
                  <span className="font-mono text-emerald-400">{(state.data_quality.ecg * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-1.5">
                  <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${state.data_quality.ecg * 100}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[11px] text-slate-300 mb-0.5">
                  <span>Tri-Axial SCG (Accelerometry)</span>
                  <span className="font-mono text-emerald-400">{(state.data_quality.scg * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-1.5">
                  <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${state.data_quality.scg * 100}%` }} />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Explainability Panel */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-amber-400" />
              Explainability: Model-Associated Physiological Factors
            </span>
            <span className="text-[11px] text-slate-500 italic">Non-causal statistical attribution</span>
          </div>

          <div className="space-y-2.5">
            {state.contributing_factors.map((factor, idx) => (
              <div key={idx} className="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-slate-800 flex items-center justify-center text-[10px] font-bold text-slate-300">
                      {idx + 1}
                    </span>
                    <span className="text-sm font-semibold text-white">{factor.display_name}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-bold font-mono px-2 py-0.5 rounded ${
                      factor.deviation_pct > 0
                        ? 'bg-rose-950/80 text-rose-300 border border-rose-800/50'
                        : 'bg-blue-950/80 text-blue-300 border border-blue-800/50'
                    }`}>
                      {factor.deviation_pct > 0 ? `+${factor.deviation_pct.toFixed(1)}%` : `${factor.deviation_pct.toFixed(1)}%`} vs Baseline
                    </span>
                    <span className="text-xs text-amber-400 font-mono">Impact: {(factor.impact_score * 100).toFixed(0)}%</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-slate-400 pl-7">
                  <div>
                    Observed: <span className="font-mono font-medium text-slate-200">{factor.observed_value}</span> • 
                    Personal Baseline: <span className="font-mono text-slate-400">{factor.baseline_value}</span>
                  </div>
                  <div className="w-40 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="bg-amber-500 h-full rounded-full"
                      style={{ width: `${Math.min(100, factor.impact_score * 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 text-xs text-slate-400 flex items-start gap-2">
            <HelpCircle className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
            <p>
              <strong>Attribution Notice:</strong> Contributing factors describe physiological variables associated with the model's computed risk score relative to this patient's calibrated baseline. They are intended for clinical review and do not constitute direct medical proof of causality.
            </p>
          </div>
        </div>
      </div>

      {/* Dynamic Physiological Timeline with Baseline Overlays */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-semibold text-white">Longitudinal Physiological Timeline</h3>
            <p className="text-xs text-slate-400">
              Shaded bands represent the patient's personalized physiological baseline range
            </p>
          </div>

          {/* Signal Selector Buttons */}
          <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveSignal('hr')}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                activeSignal === 'hr' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Heart Rate (bpm)
            </button>
            <button
              onClick={() => setActiveSignal('scg')}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                activeSignal === 'scg' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              SCG Mechanical Energy
            </button>
            <button
              onClick={() => setActiveSignal('rmssd')}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                activeSignal === 'rmssd' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              HRV RMSSD (ms)
            </button>
            <button
              onClick={() => setActiveSignal('resp')}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                activeSignal === 'resp' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Respiration (bpm)
            </button>
          </div>
        </div>

        {/* Chart Container */}
        <div className="h-72 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={timeline} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="hour" stroke="#64748b" tickFormatter={(v) => `${v}h`} />
              <YAxis stroke="#64748b" domain={['auto', 'auto']} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                labelFormatter={(v) => `Timeline Hour: ${v}h`}
              />

              {/* Shaded Personal Baseline Envelope */}
              {activeSignal === 'hr' && baseRanges['heart_rate_bpm'] && (
                <ReferenceArea
                  y1={baseRanges['heart_rate_bpm'].min}
                  y2={baseRanges['heart_rate_bpm'].max}
                  fill="#6366f1"
                  fillOpacity={0.12}
                />
              )}
              {activeSignal === 'scg' && baseRanges['scg_mechanical_energy'] && (
                <ReferenceArea
                  y1={baseRanges['scg_mechanical_energy'].min}
                  y2={baseRanges['scg_mechanical_energy'].max}
                  fill="#6366f1"
                  fillOpacity={0.12}
                />
              )}
              {activeSignal === 'rmssd' && baseRanges['hrv_rmssd_ms'] && (
                <ReferenceArea
                  y1={baseRanges['hrv_rmssd_ms'].min}
                  y2={baseRanges['hrv_rmssd_ms'].max}
                  fill="#6366f1"
                  fillOpacity={0.12}
                />
              )}
              {activeSignal === 'resp' && baseRanges['respiration_rate_bpm'] && (
                <ReferenceArea
                  y1={baseRanges['respiration_rate_bpm'].min}
                  y2={baseRanges['respiration_rate_bpm'].max}
                  fill="#6366f1"
                  fillOpacity={0.12}
                />
              )}

              {/* Dynamic Signal Line */}
              {activeSignal === 'hr' && (
                <Line
                  type="monotone"
                  dataKey="heart_rate_bpm"
                  name="Heart Rate (bpm)"
                  stroke="#ef4444"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#ef4444' }}
                />
              )}
              {activeSignal === 'scg' && (
                <Line
                  type="monotone"
                  dataKey="scg_mechanical_energy"
                  name="SCG Mechanical Energy (mg)"
                  stroke="#38bdf8"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#38bdf8' }}
                />
              )}
              {activeSignal === 'rmssd' && (
                <Line
                  type="monotone"
                  dataKey="hrv_rmssd_ms"
                  name="HRV RMSSD (ms)"
                  stroke="#a855f7"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#a855f7' }}
                />
              )}
              {activeSignal === 'resp' && (
                <Line
                  type="monotone"
                  dataKey="respiration_rate_bpm"
                  name="Respiration Rate (bpm)"
                  stroke="#10b981"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#10b981' }}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Risk Trajectory: Past <-> NOW <-> Forecast */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <div>
          <h3 className="text-base font-semibold text-white">Decompensation Risk Trajectory & Forecast Horizon</h3>
          <p className="text-xs text-slate-400">
            Past trajectory transitioning into prospective 6-hour, 12-hour, and 24-hour deterioration forecast
          </p>
        </div>

        <div className="h-60 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trajectoryData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="label" stroke="#64748b" />
              <YAxis stroke="#64748b" domain={[0, 100]} unit="%" />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                formatter={(val) => [`${val}%`, 'Decompensation Risk']}
              />
              <ReferenceLine y={50} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: 'Early Alert Threshold (50%)', fill: '#f59e0b', fontSize: 10 }} />
              <ReferenceLine y={75} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'High-Risk Threshold (75%)', fill: '#ef4444', fontSize: 10 }} />
              <Area type="monotone" dataKey="risk" stroke="#f43f5e" strokeWidth={3} fillOpacity={1} fill="url(#riskGradient)" dot={{ r: 4, fill: '#f43f5e' }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
