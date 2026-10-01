export interface PatientSummary {
  patient_id: string;
  record_id?: string;
  name: string;
  age: number;
  gender: string;
  nyha_class: number;
  hf_subtype: string;
  state_label: string;
  risk_score: number;
  alert_level: string;
  hr_bpm: number;
  resp_bpm: number;
  scg_energy: number;
  quality: number;
  provenance: string;
  is_demo_flagship: boolean;
}

export interface PatientProfile {
  patient_id: string;
  name: string;
  age: number;
  gender: string;
  nyha_class: number;
  hf_subtype: string;
  bmi: number;
  baseline_sbp: number;
  baseline_dbp: number;
  comorbidities: string[];
  provenance: string;
  baseline_ranges: Record<string, { min: number; max: number; mean: number }>;
}

export interface ContributingFactor {
  factor_name: string;
  display_name: string;
  observed_value: number;
  baseline_value: number;
  deviation_pct: number;
  impact_score: number;
  direction: string;
}

export interface DigitalTwinState {
  patient_id: string;
  timestamp_sec: number;
  state_label: string;
  state_vector: number[];
  risk_score: number;
  risk_trend: string;
  confidence: string;
  data_quality: {
    overall: number;
    ecg: number;
    scg: number;
  };
  current_vitals: Record<string, number>;
  baseline_deviations: Record<string, number>;
  contributing_factors: ContributingFactor[];
  forecast_trajectory: Record<string, number>;
  alert_level: string;
}

export interface TimelinePoint {
  hour: number;
  time_sec?: number;
  stage: string;
  state_label: string;
  risk_score: number;
  heart_rate_bpm: number;
  hrv_rmssd_ms: number;
  scg_mechanical_energy: number;
  respiration_rate_bpm: number;
  pleth_amplitude: number;
  skin_temp_celsius: number;
  weight_kg?: number;
  quality_overall: number;
  base_hr?: number;
  base_rmssd?: number;
  base_scg?: number;
  base_resp?: number;
  base_weight?: number;
}

export interface BenchmarkRecord {
  Model?: string;
  Ablation_Condition?: string;
  Num_Features?: number;
  AUROC_mean?: number;
  AUROC_OOF: number;
  AUPRC_mean?: number;
  AUPRC_OOF: number;
  Sensitivity: number;
  Specificity: number;
  Precision?: number;
  F1_Score: number;
  Brier_Score?: number;
  ECE?: number;
  False_Alarm_Rate?: number;
  Lead_Time_Min?: number;
}

export interface BenchmarkResponse {
  validation_strategy: string;
  cohort_source: string;
  baselines: BenchmarkRecord[];
  ablation_study: BenchmarkRecord[];
  research_conclusion: string;
}
