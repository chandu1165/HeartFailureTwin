import React, { useState } from 'react';
import type { DigitalTwinState } from '../types';
import { simulateScenario } from '../api';
import {
  Sliders,
  RotateCcw,
  Sparkles,
  TrendingDown,
  TrendingUp,
  ShieldAlert
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

interface WhatIfViewProps {
  state: DigitalTwinState | null;
  patientId: string;
}

export const WhatIfView: React.FC<WhatIfViewProps> = ({ state, patientId }) => {
  const [deltaHR, setDeltaHR] = useState<number>(-15);
  const [deltaResp, setDeltaResp] = useState<number>(-4);
  const [deltaSCG, setDeltaSCG] = useState<number>(6);
  const [deltaWeight, setDeltaWeight] = useState<number>(-2.5);
  const [deltaPleth, setDeltaPleth] = useState<number>(0.5);

  const [simulationResult, setSimulationResult] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleRunSimulation = async () => {
    setLoading(true);
    try {
      const adjustments = {
        heart_rate_bpm: deltaHR,
        respiration_rate_bpm: deltaResp,
        scg_mechanical_energy: deltaSCG,
        weight_kg: deltaWeight,
        pleth_amplitude: deltaPleth
      };
      const res = await simulateScenario(patientId, adjustments);
      setSimulationResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setDeltaHR(0);
    setDeltaResp(0);
    setDeltaSCG(0);
    setDeltaWeight(0);
    setDeltaPleth(0);
    setSimulationResult(null);
  };

  // Trajectory comparison chart data
  const baseForecast = state?.forecast_trajectory || { now: 0.82, '6h': 0.86, '12h': 0.90, '24h': 0.94 };
  const simForecast = simulationResult?.simulated_trajectory || {
    now: Math.max(0.15, baseForecast.now - 0.25),
    '6h': Math.max(0.18, (baseForecast['6h'] || 0.86) - 0.28),
    '12h': Math.max(0.20, (baseForecast['12h'] || 0.90) - 0.32),
    '24h': Math.max(0.22, (baseForecast['24h'] || 0.94) - 0.35),
  };

  const trajectoryComparison = [
    { horizon: 'Current (0h)', baseRisk: Math.round(baseForecast.now * 100), simRisk: Math.round(simForecast.now * 100) },
    { horizon: '+6 Hours', baseRisk: Math.round((baseForecast['6h'] || 0.86) * 100), simRisk: Math.round((simForecast['6h'] || 0.58) * 100) },
    { horizon: '+12 Hours', baseRisk: Math.round((baseForecast['12h'] || 0.90) * 100), simRisk: Math.round((simForecast['12h'] || 0.58) * 100) },
    { horizon: '+24 Hours', baseRisk: Math.round((baseForecast['24h'] || 0.94) * 100), simRisk: Math.round((simForecast['24h'] || 0.59) * 100) },
  ];

  const deltaRisk24h = simulationResult
    ? Math.round(simulationResult.delta_risk_24h * 100)
    : Math.round((simForecast['24h'] - (baseForecast['24h'] || 0.94)) * 100);

  return (
    <div className="space-y-6">
      {/* Top Header & Disclaimer */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-white">What-If In Silico Physiological Simulation</h2>
              <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-indigo-950 text-indigo-300 border border-indigo-700">
                Research Feature
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Simulate hypothetical physiological variations to inspect how the computational Digital Twin's forecasted trajectory alters.
            </p>
          </div>
        </div>

        {/* Prominent Medical Disclaimer */}
        <div className="bg-amber-950/40 border border-amber-900/60 p-3 rounded-xl flex items-start gap-3 text-xs text-amber-300/90">
          <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <p>
            <strong>IMPORTANT CLINICAL NOTICE:</strong> This is a computational mathematical simulation. Do NOT present or interpret this as clinical treatment advice or medication titration guidance. Changing variables in silico does not guarantee clinical biological responses in real patients.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Simulation Parameter Controls */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Sliders className="w-4 h-4 text-indigo-400" />
              Physiological Modulators
            </span>
            <button
              onClick={handleReset}
              className="text-xs text-slate-400 hover:text-white flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset</span>
            </button>
          </div>

          {/* Slider 1: Heart Rate */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Resting Heart Rate Delta</span>
              <span className={`font-mono font-bold ${deltaHR > 0 ? 'text-rose-400' : deltaHR < 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
                {deltaHR > 0 ? `+${deltaHR} bpm` : `${deltaHR} bpm`}
              </span>
            </div>
            <input
              type="range"
              min={-30}
              max={30}
              value={deltaHR}
              onChange={(e) => setDeltaHR(Number(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer h-1.5 bg-slate-950 rounded-lg"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>-30 bpm (Bradycardia)</span>
              <span>0</span>
              <span>+30 bpm (Tachycardia)</span>
            </div>
          </div>

          {/* Slider 2: Respiratory Rate */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Respiratory Rate Delta</span>
              <span className={`font-mono font-bold ${deltaResp > 0 ? 'text-rose-400' : deltaResp < 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
                {deltaResp > 0 ? `+${deltaResp} rpm` : `${deltaResp} rpm`}
              </span>
            </div>
            <input
              type="range"
              min={-10}
              max={10}
              value={deltaResp}
              onChange={(e) => setDeltaResp(Number(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer h-1.5 bg-slate-950 rounded-lg"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>-10 rpm</span>
              <span>0</span>
              <span>+10 rpm (Tachypnea)</span>
            </div>
          </div>

          {/* Slider 3: SCG Mechanical Energy */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">SCG Mechanical Force Delta</span>
              <span className={`font-mono font-bold ${deltaSCG > 0 ? 'text-emerald-400' : deltaSCG < 0 ? 'text-rose-400' : 'text-slate-400'}`}>
                {deltaSCG > 0 ? `+${deltaSCG} mg` : `${deltaSCG} mg`}
              </span>
            </div>
            <input
              type="range"
              min={-15}
              max={15}
              value={deltaSCG}
              onChange={(e) => setDeltaSCG(Number(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer h-1.5 bg-slate-950 rounded-lg"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>-15 mg (Weak Contractility)</span>
              <span>0</span>
              <span>+15 mg (Strong Force)</span>
            </div>
          </div>

          {/* Slider 4: Weight / Fluid Offload */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Body Weight / Fluid Delta</span>
              <span className={`font-mono font-bold ${deltaWeight > 0 ? 'text-rose-400' : deltaWeight < 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
                {deltaWeight > 0 ? `+${deltaWeight} kg` : `${deltaWeight} kg`}
              </span>
            </div>
            <input
              type="range"
              min={-5}
              max={5}
              step={0.5}
              value={deltaWeight}
              onChange={(e) => setDeltaWeight(Number(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer h-1.5 bg-slate-950 rounded-lg"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>-5.0 kg (Diuretic Offload)</span>
              <span>0</span>
              <span>+5.0 kg (Congestion)</span>
            </div>
          </div>

          <button
            onClick={handleRunSimulation}
            disabled={loading}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition flex items-center justify-center gap-2 shadow-sm shadow-indigo-600/30"
          >
            <Sparkles className="w-4 h-4" />
            <span>{loading ? 'Evaluating Scenario...' : 'Execute In Silico Simulation'}</span>
          </button>
        </div>

        {/* Right: Dual Trajectory Comparison & Results */}
        <div className="lg:col-span-2 space-y-6">
          {/* Comparison KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-slate-400">Current Twin State</div>
              <div className="text-lg font-bold text-rose-400 mt-1">
                {state?.state_label || 'High-Risk'}
              </div>
              <div className="text-xs text-slate-500 mt-0.5">
                Current 24h Risk: <span className="font-mono text-slate-300 font-bold">{Math.round((baseForecast['24h'] || 0.94) * 100)}%</span>
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-slate-400">Simulated Twin State</div>
              <div className="text-lg font-bold text-emerald-400 mt-1">
                {simulationResult?.simulated_state_label || 'Early Physiological Change'}
              </div>
              <div className="text-xs text-slate-500 mt-0.5">
                Simulated 24h Risk: <span className="font-mono text-emerald-300 font-bold">{Math.round((simForecast['24h'] || 0.59) * 100)}%</span>
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-slate-400">Projected Risk Shift</div>
              <div className="flex items-center gap-2 mt-1">
                {deltaRisk24h < 0 ? (
                  <TrendingDown className="w-5 h-5 text-emerald-400" />
                ) : (
                  <TrendingUp className="w-5 h-5 text-rose-400" />
                )}
                <div className={`text-2xl font-black ${deltaRisk24h < 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {deltaRisk24h > 0 ? `+${deltaRisk24h}%` : `${deltaRisk24h}%`}
                </div>
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">Over 24h Horizon</div>
            </div>
          </div>

          {/* Dual Trajectory Chart */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-white">Dual Trajectory Comparison</h3>
                <p className="text-xs text-slate-400">Observed trajectory vs simulated trajectory across forecast horizons</p>
              </div>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trajectoryComparison} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="horizon" stroke="#64748b" />
                  <YAxis stroke="#64748b" domain={[0, 100]} unit="%" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                    formatter={(val) => [`${val}%`, 'Decompensation Risk']}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                  <Line
                    type="monotone"
                    dataKey="baseRisk"
                    name="Observed Current Trajectory"
                    stroke="#ef4444"
                    strokeWidth={3}
                    dot={{ r: 4, fill: '#ef4444' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="simRisk"
                    name="Simulated In Silico Trajectory"
                    stroke="#10b981"
                    strokeWidth={3}
                    strokeDasharray="4 4"
                    dot={{ r: 4, fill: '#10b981' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
