import type { PatientSummary, PatientProfile, DigitalTwinState, TimelinePoint, BenchmarkResponse } from './types';

const API_BASE = '/api';

export async function fetchCohort(): Promise<PatientSummary[]> {
  const res = await fetch(`${API_BASE}/cohort`);
  if (!res.ok) throw new Error('Failed to fetch cohort');
  const data = await res.json();
  return data.cohort;
}

export async function fetchPatientProfile(patientId: string): Promise<PatientProfile> {
  const res = await fetch(`${API_BASE}/patients/${patientId}`);
  if (!res.ok) throw new Error(`Failed to fetch profile for ${patientId}`);
  return res.json();
}

export async function fetchPatientState(patientId: string): Promise<DigitalTwinState> {
  const res = await fetch(`${API_BASE}/patients/${patientId}/state`);
  if (!res.ok) throw new Error(`Failed to fetch state for ${patientId}`);
  return res.json();
}

export async function fetchPatientTimeline(patientId: string): Promise<TimelinePoint[]> {
  const res = await fetch(`${API_BASE}/patients/${patientId}/timeline`);
  if (!res.ok) throw new Error(`Failed to fetch timeline for ${patientId}`);
  const data = await res.json();
  return data.timeline;
}

export async function simulateScenario(patientId: string, adjustments: Record<string, number>) {
  const res = await fetch(`${API_BASE}/patients/${patientId}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ adjustments })
  });
  if (!res.ok) throw new Error('Simulation failed');
  return res.json();
}

export async function fetchBenchmarks(): Promise<BenchmarkResponse> {
  const res = await fetch(`${API_BASE}/benchmarks`);
  if (!res.ok) throw new Error('Failed to fetch benchmarks');
  return res.json();
}
