import React from 'react';
import { Activity, Heart, ShieldAlert, Cpu, GitCompare, PlaySquare, LineChart } from 'lucide-react';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  selectedPatientId: string;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, selectedPatientId }) => {
  const tabs = [
    { id: 'cohort', label: 'Cohort Overview', icon: Activity },
    { id: 'twin', label: `Digital Twin (${selectedPatientId})`, icon: Cpu },
    { id: 'replay', label: 'Twin Replay', icon: PlaySquare },
    { id: 'whatif', label: 'What-If Simulation', icon: GitCompare },
    { id: 'benchmarks', label: 'Research & Ablation', icon: LineChart },
  ];

  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
      {/* Top Banner: Medical Research Disclaimer */}
      <div className="bg-amber-950/40 border-b border-amber-900/50 px-4 py-1.5 text-xs text-amber-300/90 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
          <span>
            <strong>RESEARCH & CLINICAL DECISION-SUPPORT PROTOTYPE:</strong> Computational Digital Twin system. Not a diagnostic device. Does not prescribe treatment or replace clinical evaluation.
          </span>
        </div>
        <div className="hidden md:flex items-center gap-3 text-[11px] text-amber-400/80">
          <span>Zero Patient-Leakage (GroupKFold)</span>
          <span>•</span>
          <span>PhysioNet SCG-RHC Cohort</span>
        </div>
      </div>

      {/* Main Header Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-rose-900/20">
            <Heart className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white">HeartFailureTwin</h1>
              <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-indigo-900/60 text-indigo-300 border border-indigo-700/50">
                v1.0 Research
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Personalized Multimodal Digital Twin for Early Forecasting of Heart-Failure Decompensation
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-xl border border-slate-800">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-600/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
