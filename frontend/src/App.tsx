import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { CohortOverview } from './components/CohortOverview';
import { PatientTwinView } from './components/PatientTwinView';
import { TwinReplayView } from './components/TwinReplayView';
import { WhatIfView } from './components/WhatIfView';
import { BenchmarksView } from './components/BenchmarksView';
import type {
  PatientSummary,
  PatientProfile,
  DigitalTwinState,
  TimelinePoint
} from './types';
import {
  fetchCohort,
  fetchPatientProfile,
  fetchPatientState,
  fetchPatientTimeline
} from './api';
import { Activity } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('cohort');
  const [selectedPatientId, setSelectedPatientId] = useState<string>('HF-104');
  
  const [cohort, setCohort] = useState<PatientSummary[]>([]);
  const [profile, setProfile] = useState<PatientProfile | null>(null);
  const [twinState, setTwinState] = useState<DigitalTwinState | null>(null);
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);
  
  const [loading, setLoading] = useState<boolean>(true);

  // Load cohort on initial mount
  useEffect(() => {
    fetchCohort()
      .then((data) => {
        setCohort(data);
      })
      .catch((err) => console.error('Error fetching cohort:', err))
      .finally(() => setLoading(false));
  }, []);

  // Load selected patient data
  useEffect(() => {
    if (!selectedPatientId) return;

    Promise.all([
      fetchPatientProfile(selectedPatientId),
      fetchPatientState(selectedPatientId),
      fetchPatientTimeline(selectedPatientId)
    ])
      .then(([prof, state, tl]) => {
        setProfile(prof);
        setTwinState(state);
        setTimeline(tl);
      })
      .catch((err) => console.error(`Error loading patient ${selectedPatientId}:`, err));
  }, [selectedPatientId]);

  const handleSelectPatient = (patientId: string, tab: string = 'twin') => {
    setSelectedPatientId(patientId);
    setActiveTab(tab);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        selectedPatientId={selectedPatientId}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center p-24 text-slate-400 space-y-3">
            <Activity className="w-8 h-8 animate-spin text-indigo-500" />
            <span className="text-sm font-medium">Initializing HeartFailureTwin Engine...</span>
          </div>
        ) : (
          <>
            {activeTab === 'cohort' && (
              <CohortOverview
                cohort={cohort}
                onSelectPatient={handleSelectPatient}
              />
            )}

            {activeTab === 'twin' && (
              <PatientTwinView
                profile={profile}
                state={twinState}
                timeline={timeline}
                onNavigateTab={(tab) => setActiveTab(tab)}
              />
            )}

            {activeTab === 'replay' && (
              <TwinReplayView
                timeline={timeline}
                profile={profile}
              />
            )}

            {activeTab === 'whatif' && (
              <WhatIfView
                state={twinState}
                patientId={selectedPatientId}
              />
            )}

            {activeTab === 'benchmarks' && (
              <BenchmarksView />
            )}
          </>
        )}
      </main>

      {/* Footer with Scientific Attribution and Provenance */}
      <footer className="bg-slate-900 border-t border-slate-800/80 py-4 px-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div>
            <strong>HeartFailureTwin</strong> • Happiest Health Digital Twin Challenge • Research Decision-Support Prototype
          </div>
          <div className="flex items-center gap-4 text-[11px] text-slate-400">
            <span>Primary Data: PhysioNet SCG-RHC v1.0.0</span>
            <span>•</span>
            <span>Zero-Leakage GroupKFold (73 Patients)</span>
            <span>•</span>
            <span>FastAPI + PyTorch + React</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
