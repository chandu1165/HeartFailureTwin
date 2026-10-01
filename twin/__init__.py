"""HeartFailureTwin: A Personalized Multimodal Digital Twin for Early Forecasting of Heart-Failure Decompensation.
Master Twin Orchestrator.
"""
from typing import Dict, List, Optional, Any
import numpy as np
import torch

from twin.patient_state import (
    PatientProfile,
    PhysiologicalSnapshot,
    DigitalTwinState,
    ContributingFactor,
    COMPUTATIONAL_STATES
)
from twin.baseline import PatientBaselineEngine
from twin.state_estimator import MultimodalStateEstimator
from twin.state_transition import DigitalTwinTransitionModel
from twin.simulation import WhatIfSimulationEngine, DISCLAIMER_TEXT

class HeartFailureTwin:
    """Core computational Digital Twin engine for heart-failure patient monitoring and forecasting."""
    
    def __init__(self, weights_path: Optional[str] = None):
        self.patients: Dict[str, PatientProfile] = {}
        self.baselines: Dict[str, PatientBaselineEngine] = {}
        self.states: Dict[str, DigitalTwinState] = {}
        self.state_history: Dict[str, List[DigitalTwinState]] = {}
        
        # Initialize neural estimators
        self.estimator = MultimodalStateEstimator(
            ehr_dim=15,
            ecg_dim=6,
            wearable_dim=11,
            dev_dim=9,
            latent_state_dim=8
        )
        self.transition = DigitalTwinTransitionModel(state_dim=8, hidden_dim=32)
        
        # Try loading pretrained weights if provided
        if weights_path:
            try:
                ckpt = torch.load(weights_path, map_location="cpu")
                if "estimator" in ckpt:
                    self.estimator.load_state_dict(ckpt["estimator"])
                if "transition" in ckpt:
                    self.transition.load_state_dict(ckpt["transition"])
                print(f"Loaded Digital Twin weights from {weights_path}")
            except Exception as e:
                print(f"Could not load weights from {weights_path}: {e}")
                
        self.estimator.eval()
        self.transition.eval()
        self.simulation_engine = WhatIfSimulationEngine(self)

    def initialize_patient(
        self,
        profile: PatientProfile,
        initial_history: Optional[List[Dict[str, float]]] = None
    ) -> PatientBaselineEngine:
        """Register a patient profile and calibrate personal baseline envelope."""
        pid = profile.patient_id
        self.patients[pid] = profile
        b_engine = PatientBaselineEngine(pid)
        if initial_history:
            b_engine.calibrate_from_history(initial_history)
        self.baselines[pid] = b_engine
        self.state_history[pid] = []
        return b_engine

    def update_state(
        self,
        patient_id: str,
        snapshot: PhysiologicalSnapshot
    ) -> DigitalTwinState:
        """Process incoming physiological snapshot, update latent state S(t), and forecast trajectory."""
        if patient_id not in self.patients:
            raise ValueError(f"Patient {patient_id} not registered. Call initialize_patient first.")
            
        profile = self.patients[patient_id]
        b_engine = self.baselines[patient_id]
        
        # Current vitals dict
        vitals_dict = {
            "heart_rate_bpm": snapshot.heart_rate_bpm,
            "hrv_rmssd_ms": snapshot.hrv_rmssd_ms,
            "hrv_sdnn_ms": snapshot.hrv_sdnn_ms,
            "scg_mechanical_energy": snapshot.scg_mechanical_energy,
            "scg_dorso_ventral_rms": snapshot.scg_dorso_ventral_rms,
            "respiration_rate_bpm": snapshot.respiration_rate_bpm,
            "pleth_amplitude": snapshot.pleth_amplitude,
            "skin_temp_celsius": snapshot.skin_temp_celsius
        }
        
        # Personal baseline deviations
        devs = b_engine.compute_deviations(vitals_dict)
        dev_dict_summary = {k: v["deviation_pct"] for k, v in devs.items()}
        
        # Prepare neural inputs
        # 1. EHR vector (dim 15)
        ehr_vec = torch.tensor([[
            profile.age / 100.0,
            1.0 if profile.gender.lower() in ["m", "male"] else 0.0,
            profile.bmi / 50.0,
            profile.baseline_sbp / 200.0,
            profile.baseline_dbp / 120.0,
            (profile.baseline_sbp - profile.baseline_dbp) / 80.0,
            (profile.baseline_dbp + (profile.baseline_sbp - profile.baseline_dbp)/3.0) / 150.0,
            profile.nyha_class / 4.0,
            float(profile.hypertension),
            float(profile.diabetes),
            float(profile.cad),
            float(profile.ckd),
            1.0 if "ref" in profile.hf_subtype.lower() else 0.0,
            1.0 if "pef" in profile.hf_subtype.lower() else 0.0,
            float(profile.prior_hospitalization)
        ]], dtype=torch.float32)
        
        # 2. ECG vector (dim 6)
        ecg_vec = torch.tensor([[
            snapshot.heart_rate_bpm / 150.0,
            snapshot.hrv_sdnn_ms / 100.0,
            snapshot.hrv_rmssd_ms / 100.0,
            0.05, # pnn50
            0.5, # qrs energy
            float(snapshot.quality_ecg)
        ]], dtype=torch.float32)
        
        # 3. Wearable vector (dim 11)
        wearable_vec = torch.tensor([[
            snapshot.scg_dorso_ventral_rms / 50.0,
            snapshot.scg_mechanical_energy / 50.0,
            snapshot.scg_mechanical_energy / 30.0, # p2p
            snapshot.scg_mechanical_energy * 0.4, # hf
            snapshot.scg_mechanical_energy * 0.3, # lat
            12.5 / 40.0, # spectral centroid
            0.15, # activity index
            snapshot.pleth_amplitude / 5.0,
            snapshot.respiration_rate_bpm / 30.0,
            snapshot.skin_temp_celsius / 40.0,
            float(snapshot.quality_scg)
        ]], dtype=torch.float32)
        
        # 4. Personal deviation vector (dim 9)
        dev_vec = torch.tensor([[
            devs.get("heart_rate_bpm", {}).get("z_score", 0.0),
            devs.get("hrv_rmssd_ms", {}).get("z_score", 0.0),
            devs.get("hrv_sdnn_ms", {}).get("z_score", 0.0),
            devs.get("scg_mechanical_energy", {}).get("z_score", 0.0),
            devs.get("scg_dorso_ventral_rms", {}).get("z_score", 0.0),
            devs.get("respiration_rate_bpm", {}).get("z_score", 0.0),
            devs.get("pleth_amplitude", {}).get("z_score", 0.0),
            devs.get("skin_temp_celsius", {}).get("z_score", 0.0),
            float(snapshot.quality_overall)
        ]], dtype=torch.float32)
        
        # Neural forward pass
        with torch.no_grad():
            s_t, risk_t, hemo_est = self.estimator(ehr_vec, ecg_vec, wearable_vec, dev_vec)
            risk_val = float(risk_t.squeeze().item())
            s_t_list = [round(float(x), 3) for x in s_t.squeeze().tolist()]
            
            # Forecast future trajectory using transition model
            traj_steps = self.transition.forecast_trajectory(s_t, steps=4)
            forecast_dict = {
                "now": round(risk_val, 4),
                "6h": traj_steps[1]["risk"],
                "12h": traj_steps[2]["risk"],
                "24h": traj_steps[4]["risk"]
            }

        # Determine computational state label
        if risk_val < 0.25:
            state_label = "Stable"
            alert_level = "NORMAL"
        elif risk_val < 0.45:
            state_label = "Early Physiological Change"
            alert_level = "ADVISORY"
        elif risk_val < 0.70:
            state_label = "Deteriorating"
            alert_level = "EARLY_WARNING"
        elif risk_val < 0.85:
            state_label = "High-Risk"
            alert_level = "HIGH_PRIORITY_REVIEW"
        else:
            state_label = "Possible Decompensation"
            alert_level = "HIGH_PRIORITY_REVIEW"
            
        # Determine trend compared to previous history
        history = self.state_history[patient_id]
        if len(history) >= 1:
            prev_risk = history[-1].risk_score
            delta_risk = risk_val - prev_risk
            if delta_risk > 0.08:
                risk_trend = "Rapidly Deteriorating"
            elif delta_risk > 0.02:
                risk_trend = "Slowly Increasing"
            elif delta_risk < -0.04:
                risk_trend = "Improving"
            else:
                risk_trend = "Stable"
        else:
            risk_trend = "Stable"

        # Signal confidence
        q_overall = snapshot.quality_overall
        if q_overall >= 0.75:
            confidence = "High"
        elif q_overall >= 0.45:
            confidence = "Moderate"
        else:
            confidence = "Low"

        # Explainability: Factors associated with the prediction (transparent non-causal attribution)
        factors = []
        for feat, d in devs.items():
            z = d["z_score"]
            abs_z = abs(z)
            if abs_z >= 0.8:
                # Factor direction
                if feat == "heart_rate_bpm" and z > 0:
                    factors.append(ContributingFactor(
                        factor_name=feat,
                        display_name="Resting Heart Rate Elevation",
                        observed_value=d["current"],
                        baseline_value=d["baseline"],
                        deviation_pct=d["deviation_pct"],
                        impact_score=round(min(1.0, abs_z * 0.25), 3),
                        direction="elevated"
                    ))
                elif feat == "respiration_rate_bpm" and z > 0:
                    factors.append(ContributingFactor(
                        factor_name=feat,
                        display_name="Respiratory Rate Elevation (Tachypnea)",
                        observed_value=d["current"],
                        baseline_value=d["baseline"],
                        deviation_pct=d["deviation_pct"],
                        impact_score=round(min(1.0, abs_z * 0.30), 3),
                        direction="elevated"
                    ))
                elif feat == "hrv_rmssd_ms" and z < 0:
                    factors.append(ContributingFactor(
                        factor_name=feat,
                        display_name="Autonomic HRV Depression",
                        observed_value=d["current"],
                        baseline_value=d["baseline"],
                        deviation_pct=d["deviation_pct"],
                        impact_score=round(min(1.0, abs_z * 0.20), 3),
                        direction="depressed"
                    ))
                elif feat == "scg_mechanical_energy" and z < 0:
                    factors.append(ContributingFactor(
                        factor_name=feat,
                        display_name="Cardio-Mechanical Contractility Decline",
                        observed_value=d["current"],
                        baseline_value=d["baseline"],
                        deviation_pct=d["deviation_pct"],
                        impact_score=round(min(1.0, abs_z * 0.25), 3),
                        direction="depressed"
                    ))
                elif feat == "pleth_amplitude" and z < 0:
                    factors.append(ContributingFactor(
                        factor_name=feat,
                        display_name="Peripheral Perfusion Attenuation",
                        observed_value=d["current"],
                        baseline_value=d["baseline"],
                        deviation_pct=d["deviation_pct"],
                        impact_score=round(min(1.0, abs_z * 0.15), 3),
                        direction="depressed"
                    ))
                    
        # Sort factors by impact
        factors = sorted(factors, key=lambda f: f.impact_score, reverse=True)[:5]

        twin_state = DigitalTwinState(
            patient_id=patient_id,
            timestamp_sec=snapshot.timestamp_sec,
            state_label=state_label,
            state_vector=s_t_list,
            risk_score=risk_val,
            risk_trend=risk_trend,
            confidence=confidence,
            data_quality={
                "overall": round(snapshot.quality_overall, 2),
                "ecg": round(snapshot.quality_ecg, 2),
                "scg": round(snapshot.quality_scg, 2)
            },
            current_vitals=vitals_dict,
            baseline_deviations=dev_dict_summary,
            contributing_factors=factors,
            forecast_trajectory=forecast_dict,
            alert_level=alert_level
        )
        
        self.states[patient_id] = twin_state
        self.state_history[patient_id].append(twin_state)
        return twin_state

    def update_state_from_vitals(
        self,
        patient_id: str,
        vitals: Dict[str, float],
        timestamp_sec: float = 0.0
    ) -> Dict[str, Any]:
        """Convenience method for what-if simulation from raw vitals dictionary."""
        snapshot = PhysiologicalSnapshot(
            timestamp_sec=timestamp_sec,
            heart_rate_bpm=vitals.get("heart_rate_bpm", 72.0),
            hrv_rmssd_ms=vitals.get("hrv_rmssd_ms", 35.0),
            hrv_sdnn_ms=vitals.get("hrv_sdnn_ms", 45.0),
            scg_mechanical_energy=vitals.get("scg_mechanical_energy", 18.0),
            scg_dorso_ventral_rms=vitals.get("scg_dorso_ventral_rms", 14.0),
            respiration_rate_bpm=vitals.get("respiration_rate_bpm", 16.0),
            pleth_amplitude=vitals.get("pleth_amplitude", 2.2),
            skin_temp_celsius=vitals.get("skin_temp_celsius", 35.4),
            quality_ecg=1.0,
            quality_scg=1.0,
            quality_overall=1.0
        )
        return self.update_state(patient_id, snapshot).to_dict()

    def get_state(self, patient_id: str) -> Optional[Dict[str, Any]]:
        state = self.states.get(patient_id)
        return state.to_dict() if state else None

    def get_history(self, patient_id: str) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self.state_history.get(patient_id, [])]

    def simulate_what_if(
        self,
        patient_id: str,
        adjustments: Dict[str, float]
    ) -> Dict[str, Any]:
        """Perform What-If physiological modulation scenario."""
        curr_state = self.get_state(patient_id)
        if not curr_state:
            raise ValueError(f"No active state found for patient {patient_id}")
        return self.simulation_engine.run_simulation(curr_state, adjustments)
