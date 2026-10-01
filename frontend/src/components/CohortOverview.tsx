import React, { useState } from 'react';
import type { PatientSummary } from '../types';
import { Users, AlertTriangle, CheckCircle2, AlertCircle, Search, Cpu } from 'lucide-react';

interface CohortOverviewProps {
  cohort: PatientSummary[];
  onSelectPatient: (patientId: string, tab?: string) => void;
}

export const CohortOverview: React.FC<CohortOverviewProps> = ({ cohort, onSelectPatient }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterState, setFilterState] = useState<string>('all');

  const filteredCohort = cohort.filter((p) => {
    const matchesSearch =
      p.patient_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.hf_subtype.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesState = filterState === 'all' || p.state_label.toLowerCase().includes(filterState.toLowerCase());
    return matchesSearch && matchesState;
  });

  const stableCount = cohort.filter((p) => p.state_label === 'Stable').length;
  const earlyCount = cohort.filter((p) => p.state_label === 'Early Physiological Change').length;
  const detCount = cohort.filter((p) => p.state_label === 'Deteriorating').length;
  const highRiskCount = cohort.filter((p) => ['High-Risk', 'Possible Decompensation'].includes(p.state_label)).length;

  const getStateBadge = (state: string) => {
    switch (state) {
      case 'Stable':
        return 'bg-emerald-950/80 text-emerald-400 border-emerald-800/60';
      case 'Early Physiological Change':
        return 'bg-amber-950/80 text-amber-400 border-amber-800/60';
      case 'Deteriorating':
        return 'bg-orange-950/80 text-orange-400 border-orange-800/60';
      case 'High-Risk':
      case 'Possible Decompensation':
        return 'bg-rose-950/80 text-rose-400 border-rose-800/60 animate-pulse';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Total Monitored</span>
            <Users className="w-4 h-4 text-slate-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-white">{cohort.length}</div>
          <div className="mt-1 text-[11px] text-slate-500">Continuous Wearable + EHR</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-emerald-400 text-xs font-medium">
            <span>Stable Baseline</span>
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <div className="mt-2 text-2xl font-bold text-white">{stableCount}</div>
          <div className="mt-1 text-[11px] text-emerald-400/70">Within personal envelopes</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-amber-400 text-xs font-medium">
            <span>Early Deviation</span>
            <AlertCircle className="w-4 h-4" />
          </div>
          <div className="mt-2 text-2xl font-bold text-white">{earlyCount}</div>
          <div className="mt-1 text-[11px] text-amber-400/70">Subclinical trajectory shift</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-orange-400 text-xs font-medium">
            <span>Deteriorating</span>
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div className="mt-2 text-2xl font-bold text-white">{detCount}</div>
          <div className="mt-1 text-[11px] text-orange-400/70">Multi-signal abnormal trend</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-rose-400 text-xs font-medium">
            <span>High-Risk Review</span>
            <AlertTriangle className="w-4 h-4 animate-bounce" />
          </div>
          <div className="mt-2 text-2xl font-bold text-white">{highRiskCount}</div>
          <div className="mt-1 text-[11px] text-rose-400/70">Impending decompensation</div>
        </div>
      </div>

      {/* Cohort Table & Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-800 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <h2 className="text-base font-semibold text-white">Monitored Patient Cohort</h2>
            <span className="text-xs text-slate-400">({filteredCohort.length} of {cohort.length} displayed)</span>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search patient, ID, subtype..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <select
              value={filterState}
              onChange={(e) => setFilterState(e.target.value)}
              className="px-3 py-1.5 bg-slate-950 border border-slate-700 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
            >
              <option value="all">All Twin States</option>
              <option value="stable">Stable</option>
              <option value="early">Early Deviation</option>
              <option value="deteriorating">Deteriorating</option>
              <option value="high-risk">High-Risk</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-4 py-3 font-semibold">Patient & Clinical Subtype</th>
                <th className="px-4 py-3 font-semibold">Demographics</th>
                <th className="px-4 py-3 font-semibold">Digital Twin State</th>
                <th className="px-4 py-3 font-semibold">Decompensation Risk</th>
                <th className="px-4 py-3 font-semibold">Wearable Vitals</th>
                <th className="px-4 py-3 font-semibold">Data Provenance</th>
                <th className="px-4 py-3 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filteredCohort.map((patient) => {
                const isFlagship = patient.is_demo_flagship;
                return (
                  <tr
                    key={patient.patient_id}
                    className={`hover:bg-slate-800/40 transition-colors ${
                      isFlagship ? 'bg-indigo-950/20' : ''
                    }`}
                  >
                    <td className="px-4 py-3.5">
                      <div className="flex items-center gap-2">
                        <div>
                          <div className="font-semibold text-white flex items-center gap-1.5">
                            {patient.name}
                            {isFlagship && (
                              <span className="px-1.5 py-0.2 rounded text-[9px] bg-indigo-600 text-white font-bold">
                                Flagship Case
                              </span>
                            )}
                          </div>
                          <div className="text-[11px] text-slate-400 mt-0.5">
                            ID: <span className="font-mono text-slate-300">{patient.patient_id}</span> • {patient.hf_subtype}
                          </div>
                        </div>
                      </div>
                    </td>

                    <td className="px-4 py-3.5">
                      <div>
                        {patient.age}y / {patient.gender}
                      </div>
                      <div className="text-[11px] text-slate-500">NYHA Class {patient.nyha_class}</div>
                    </td>

                    <td className="px-4 py-3.5">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-[11px] font-medium border ${getStateBadge(patient.state_label)}`}>
                        {patient.state_label}
                      </span>
                    </td>

                    <td className="px-4 py-3.5">
                      <div className="w-32">
                        <div className="flex justify-between text-[11px] mb-1">
                          <span className="font-medium text-slate-200">{(patient.risk_score * 100).toFixed(1)}%</span>
                          <span className="text-[10px] text-slate-400">P(24h)</span>
                        </div>
                        <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              patient.risk_score > 0.65
                                ? 'bg-rose-500'
                                : patient.risk_score > 0.40
                                ? 'bg-amber-500'
                                : 'bg-emerald-500'
                            }`}
                            style={{ width: `${Math.min(100, patient.risk_score * 100)}%` }}
                          />
                        </div>
                      </div>
                    </td>

                    <td className="px-4 py-3.5">
                      <div className="flex items-center gap-3 text-[11px]">
                        <div>
                          <span className="text-slate-500">HR: </span>
                          <span className="font-mono font-medium text-slate-200">{patient.hr_bpm} bpm</span>
                        </div>
                        <div>
                          <span className="text-slate-500">SCG: </span>
                          <span className="font-mono font-medium text-slate-200">{patient.scg_energy} mg</span>
                        </div>
                      </div>
                    </td>

                    <td className="px-4 py-3.5">
                      <span className={`inline-flex px-1.5 py-0.5 rounded text-[10px] font-mono ${
                        patient.provenance === 'REAL_PHYSIONET_SCG_RHC'
                          ? 'bg-blue-950/70 text-blue-300 border border-blue-800/50'
                          : 'bg-purple-950/70 text-purple-300 border border-purple-800/50'
                      }`}>
                        {patient.provenance === 'REAL_PHYSIONET_SCG_RHC' ? 'Real PhysioNet' : 'Synthetic Stream'}
                      </span>
                    </td>

                    <td className="px-4 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {isFlagship && (
                          <button
                            onClick={() => onSelectPatient(patient.patient_id, 'replay')}
                            className="px-2.5 py-1 bg-indigo-900/60 hover:bg-indigo-800 text-indigo-200 border border-indigo-700/60 rounded text-[11px] font-medium transition-colors flex items-center gap-1"
                            title="Launch 4D Twin Replay"
                          >
                            <span>Replay</span>
                          </button>
                        )}
                        <button
                          onClick={() => onSelectPatient(patient.patient_id, 'twin')}
                          className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 rounded text-[11px] font-medium transition-colors flex items-center gap-1"
                        >
                          <Cpu className="w-3 h-3 text-indigo-400" />
                          <span>Inspect Twin</span>
                        </button>
                      </div>
                    </td>
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
