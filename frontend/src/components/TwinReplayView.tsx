import React, { useState, useEffect } from 'react';
import type { TimelinePoint, PatientProfile } from '../types';
import {
  Play,
  Pause,
  RotateCcw,
  SkipForward,
  SkipBack,
  AlertTriangle,
  Heart,
  Wind
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine
} from 'recharts';

interface TwinReplayViewProps {
  timeline: TimelinePoint[];
  profile: PatientProfile | null;
}

export const TwinReplayView: React.FC<TwinReplayViewProps> = ({ timeline, profile }) => {
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);

  const totalSteps = timeline.length;
  const currentPoint = timeline[currentIndex] || timeline[0];

  useEffect(() => {
    let interval: any = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentIndex((prev) => {
          if (prev >= totalSteps - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1000 / playbackSpeed);
    }
    return () => clearInterval(interval);
  }, [isPlaying, playbackSpeed, totalSteps]);

  if (!currentPoint) {
    return <div className="p-12 text-slate-400 text-center">Loading timeline playback data...</div>;
  }

  // Active risk percentage
  const riskPct = Math.round(currentPoint.risk_score * 100);

  // Partial timeline up to current scrubber index for animated chart progression
  const animatedChartData = timeline.slice(0, currentIndex + 1).map((p) => ({
    hour: `${p.hour}h`,
    risk: Math.round(p.risk_score * 100),
    hr: p.heart_rate_bpm,
    resp: p.respiration_rate_bpm,
    scg: p.scg_mechanical_energy
  }));

  // Early warning detection threshold check
  const alertTriggeredIndex = timeline.findIndex((p) => p.risk_score >= 0.50);
  const isAlertActive = currentIndex >= alertTriggeredIndex && alertTriggeredIndex !== -1;
  const leadTimeHours = alertTriggeredIndex !== -1 ? Math.max(0, 72 - timeline[alertTriggeredIndex].hour) : 0;

  const getStateColor = (state: string) => {
    switch (state) {
      case 'Stable':
        return 'text-emerald-400 bg-emerald-950/80 border-emerald-800';
      case 'Early Physiological Change':
        return 'text-amber-400 bg-amber-950/80 border-amber-800';
      case 'Deteriorating':
        return 'text-orange-400 bg-orange-950/80 border-orange-800';
      case 'High-Risk':
      case 'Possible Decompensation':
        return 'text-rose-400 bg-rose-950/80 border-rose-800 animate-pulse';
      default:
        return 'text-slate-300 bg-slate-800 border-slate-700';
    }
  };

  return (
    <div className="space-y-6">
      {/* Replay Controller Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-white">4D Twin Replay: Longitudinal Decompensation Timeline</h2>
              <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-indigo-950 text-indigo-300 border border-indigo-700">
                {profile?.name || 'Patient HF-104 Demo'}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Step forward and backward through 72 hours of continuous physiological monitoring to witness state evolution.
            </p>
          </div>

          {/* Early Warning Lead Time Indicator */}
          {isAlertActive && (
            <div className="bg-rose-950/60 border border-rose-800/80 px-4 py-2 rounded-xl flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 animate-bounce" />
              <div>
                <div className="text-xs font-bold text-rose-300">EARLY WARNING ACTIVE</div>
                <div className="text-[11px] text-rose-400/90 font-mono">
                  Lead Time Before Acute Event: <span className="font-bold underline">{leadTimeHours.toFixed(1)} Hours</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Timeline Scrubber & Controls */}
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800/80 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className={`p-2.5 rounded-xl font-medium transition flex items-center gap-2 text-xs ${
                  isPlaying ? 'bg-amber-600 text-white' : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm shadow-indigo-600/30'
                }`}
              >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                <span>{isPlaying ? 'Pause Replay' : 'Play Trajectory'}</span>
              </button>

              <button
                onClick={() => {
                  setIsPlaying(false);
                  setCurrentIndex(0);
                }}
                className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs transition"
                title="Reset to 0h"
              >
                <RotateCcw className="w-4 h-4" />
              </button>

              <button
                onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
                className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs transition"
                title="Step Back"
              >
                <SkipBack className="w-4 h-4" />
              </button>

              <button
                onClick={() => setCurrentIndex((prev) => Math.min(totalSteps - 1, prev + 1))}
                className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs transition"
                title="Step Forward"
              >
                <SkipForward className="w-4 h-4" />
              </button>
            </div>

            {/* Playback Speed */}
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span>Speed:</span>
              {[1, 2, 4].map((spd) => (
                <button
                  key={spd}
                  onClick={() => setPlaybackSpeed(spd)}
                  className={`px-2 py-0.5 rounded text-xs font-mono font-medium ${
                    playbackSpeed === spd ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  {spd}x
                </button>
              ))}
            </div>

            {/* Active Timepoint Info */}
            <div className="text-right">
              <span className="text-xs text-slate-400">Current Monitoring Time:</span>
              <div className="text-base font-mono font-bold text-white">Hour {currentPoint.hour}h of 72.0h</div>
            </div>
          </div>

          {/* Scrubber Range Slider */}
          <div className="pt-2">
            <input
              type="range"
              min={0}
              max={totalSteps - 1}
              value={currentIndex}
              onChange={(e) => {
                setIsPlaying(false);
                setCurrentIndex(Number(e.target.value));
              }}
              className="w-full accent-indigo-500 cursor-pointer h-2 bg-slate-800 rounded-lg"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
              <span>0h (Baseline)</span>
              <span>24h (Early Change)</span>
              <span>48h (Deteriorating)</span>
              <span>72h (High-Risk)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Dynamic State Dashboard at Current Timepoint */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* State Badge Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="text-xs text-slate-400 font-medium">Digital Twin State</div>
          <div className={`text-base font-bold px-3 py-1.5 rounded-lg border text-center ${getStateColor(currentPoint.state_label)}`}>
            {currentPoint.state_label}
          </div>
          <div className="text-[11px] text-slate-400 text-center font-medium">{currentPoint.stage}</div>
        </div>

        {/* Risk Score Meter */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex justify-between text-xs text-slate-400">
            <span>Decompensation Risk</span>
            <span className="font-mono text-slate-300">P(24h)</span>
          </div>
          <div className={`text-2xl font-black ${riskPct > 65 ? 'text-rose-400' : riskPct > 40 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {riskPct}%
          </div>
          <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${
                riskPct > 65 ? 'bg-rose-500' : riskPct > 40 ? 'bg-amber-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${riskPct}%` }}
            />
          </div>
        </div>

        {/* Heart Rate Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1">
              <Heart className="w-3.5 h-3.5 text-rose-400" />
              Resting HR
            </span>
            <span className="text-[10px] text-slate-500">Base: 72</span>
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            {currentPoint.heart_rate_bpm} <span className="text-xs text-slate-400 font-normal">bpm</span>
          </div>
          <div className={`text-[11px] font-mono ${currentPoint.heart_rate_bpm > 80 ? 'text-rose-400' : 'text-emerald-400'}`}>
            {currentPoint.heart_rate_bpm > 72 ? `+${(currentPoint.heart_rate_bpm - 72).toFixed(1)} bpm above personal baseline` : 'Within baseline envelope'}
          </div>
        </div>

        {/* Respiration & Mechanics */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1">
              <Wind className="w-3.5 h-3.5 text-emerald-400" />
              Respiration & SCG
            </span>
            <span className="text-[10px] text-slate-500">Breaths / Kinetic</span>
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            {currentPoint.respiration_rate_bpm} <span className="text-xs text-slate-400 font-normal">rpm</span>
          </div>
          <div className="text-[11px] text-slate-400 font-mono">
            SCG Energy: <span className="text-sky-400 font-bold">{currentPoint.scg_mechanical_energy} mg</span>
          </div>
        </div>
      </div>

      {/* Animated Risk Trajectory Graph */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-semibold text-white">Animated Trajectory Curve (Up to Current Step)</h3>
          <span className="text-xs text-slate-400">Updates dynamically during playback</span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={animatedChartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="replayGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="hour" stroke="#64748b" />
              <YAxis stroke="#64748b" domain={[0, 100]} unit="%" />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                formatter={(val) => [`${val}%`, 'Decompensation Risk']}
              />
              <ReferenceLine y={50} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: 'Early Alert (50%)', fill: '#f59e0b', fontSize: 10 }} />
              <ReferenceLine y={75} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'Decompensation Threshold (75%)', fill: '#ef4444', fontSize: 10 }} />
              <Area type="monotone" dataKey="risk" stroke="#f43f5e" strokeWidth={3} fillOpacity={1} fill="url(#replayGradient)" dot={{ r: 3, fill: '#f43f5e' }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
