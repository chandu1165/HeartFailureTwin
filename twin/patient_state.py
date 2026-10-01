"""Patient Digital Twin state representations and definitions.
Defines the computational latent physiological state, vitals snapshot, and trajectory points.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import numpy as np

COMPUTATIONAL_STATES = [
    "Stable",
    "Early Physiological Change",
    "Deteriorating",
    "High-Risk",
    "Possible Decompensation"
]

@dataclass
class PatientProfile:
    """Static and historical EHR clinical information."""
    patient_id: str
    age: float
    gender: str
    nyha_class: int
    hf_subtype: str # e.g. HFrEF, HFpEF
    bmi: float
    baseline_sbp: float
    baseline_dbp: float
    hypertension: bool
    diabetes: bool
    cad: bool
    ckd: bool
    prior_hospitalization: bool
    notes: str = ""

@dataclass
class PhysiologicalSnapshot:
    """Dynamic wearable physiological observation at timestamp t."""
    timestamp_sec: float
    heart_rate_bpm: float
    hrv_rmssd_ms: float
    hrv_sdnn_ms: float
    scg_mechanical_energy: float
    scg_dorso_ventral_rms: float
    respiration_rate_bpm: float
    pleth_amplitude: float
    skin_temp_celsius: float
    quality_ecg: float
    quality_scg: float
    quality_overall: float

@dataclass
class ContributingFactor:
    """Factor associated with the model prediction (non-causal attribution)."""
    factor_name: str
    display_name: str
    observed_value: float
    baseline_value: float
    deviation_pct: float
    impact_score: float # positive means increases decompensation risk
    direction: str # 'increasing', 'decreasing', 'elevated', 'depressed'

@dataclass
class DigitalTwinState:
    """Continuously updated computational representation of patient's current physiological state."""
    patient_id: str
    timestamp_sec: float
    state_label: str # One of COMPUTATIONAL_STATES
    state_vector: List[float] # Latent state dimensions: [cardio, respiratory, mechanical, metabolic]
    risk_score: float # 0.0 to 1.0
    risk_trend: str # 'Improving', 'Stable', 'Slowly Increasing', 'Rapidly Deteriorating'
    confidence: str # 'High', 'Moderate', 'Low'
    data_quality: Dict[str, float]
    current_vitals: Dict[str, float]
    baseline_deviations: Dict[str, float]
    contributing_factors: List[ContributingFactor]
    forecast_trajectory: Dict[str, float] # { 'now': p0, '6h': p1, '12h': p2, '24h': p3 }
    alert_level: str # 'NORMAL', 'ADVISORY', 'EARLY_WARNING', 'HIGH_PRIORITY_REVIEW'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "patient_id": self.patient_id,
            "timestamp_sec": self.timestamp_sec,
            "state_label": self.state_label,
            "state_vector": self.state_vector,
            "risk_score": round(self.risk_score, 4),
            "risk_trend": self.risk_trend,
            "confidence": self.confidence,
            "data_quality": self.data_quality,
            "current_vitals": self.current_vitals,
            "baseline_deviations": self.baseline_deviations,
            "contributing_factors": [
                {
                    "factor_name": cf.factor_name,
                    "display_name": cf.display_name,
                    "observed_value": cf.observed_value,
                    "baseline_value": cf.baseline_value,
                    "deviation_pct": cf.deviation_pct,
                    "impact_score": cf.impact_score,
                    "direction": cf.direction
                }
                for cf in self.contributing_factors
            ],
            "forecast_trajectory": self.forecast_trajectory,
            "alert_level": self.alert_level
        }
