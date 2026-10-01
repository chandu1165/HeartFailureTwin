"""Generates rich longitudinal demo trajectories for the Doctor-Facing Digital Twin Dashboard.
Includes:
1. Patient HF-104 (The flagship multi-stage longitudinal decompensation case with Twin Replay)
2. Patient HF-201 (Stable outpatient with compensated physiology)
3. Patient TRM128 (Real decompensated case from PhysioNet SCG-RHC)
4. Patient TRM107 (Real compensated case from PhysioNet SCG-RHC)
Clearly labels data provenance (REAL SCG-RHC vs SYNTHETIC LONGITUDINAL SIMULATION).
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

DEMO_DIR = Path("demo/scenarios")
DEMO_DIR.mkdir(parents=True, exist_ok=True)

def generate_patient_hf104_timeline():
    """Flagship demonstration patient: 5-stage progression over 72 hours leading to decompensation."""
    hours = np.linspace(0, 72, 25) # every 3 hours
    
    timeline = []
    # Baseline normal values
    base_hr = 72.0
    base_rmssd = 38.0
    base_scg = 22.0
    base_resp = 15.0
    base_pleth = 2.4
    base_temp = 35.4
    base_weight = 78.5
    
    for t_hr in hours:
        # Progression stages
        if t_hr <= 24: # Stage 1: Stable baseline
            stage = "Stage 1: Stable Baseline"
            state_label = "Stable"
            risk = float(np.clip(0.12 + 0.04 * np.sin(t_hr / 3.0), 0.08, 0.20))
            hr = base_hr + np.random.normal(0, 1.5)
            rmssd = base_rmssd + np.random.normal(0, 2.0)
            scg = base_scg + np.random.normal(0, 1.0)
            resp = base_resp + np.random.normal(0, 0.8)
            pleth = base_pleth + np.random.normal(0, 0.1)
            temp = base_temp + np.random.normal(0, 0.1)
            weight = base_weight + np.random.normal(0, 0.2)
            quality = 0.95
            
        elif t_hr <= 42: # Stage 2: Early physiological deviation (subclinical HR rise, autonomic withdrawal)
            stage = "Stage 2: Early Physiological Shift"
            state_label = "Early Physiological Change"
            progress = (t_hr - 24) / 18.0
            risk = float(0.22 + 0.20 * progress)
            hr = base_hr + 8.0 * progress + np.random.normal(0, 1.5)
            rmssd = base_rmssd - 10.0 * progress + np.random.normal(0, 1.5)
            scg = base_scg - 3.0 * progress + np.random.normal(0, 1.0)
            resp = base_resp + 2.5 * progress + np.random.normal(0, 0.8)
            pleth = base_pleth - 0.3 * progress + np.random.normal(0, 0.1)
            temp = base_temp + np.random.normal(0, 0.1)
            weight = base_weight + 0.8 * progress + np.random.normal(0, 0.2)
            quality = 0.92
            
        elif t_hr <= 60: # Stage 3: Progressive deterioration (tachypnea, contractility drop, fluid gain)
            stage = "Stage 3: Progressive Deterioration"
            state_label = "Deteriorating"
            progress = (t_hr - 42) / 18.0
            risk = float(0.48 + 0.25 * progress)
            hr = base_hr + 8.0 + 12.0 * progress + np.random.normal(0, 2.0)
            rmssd = base_rmssd - 10.0 - 12.0 * progress + np.random.normal(0, 1.5)
            scg = base_scg - 3.0 - 6.0 * progress + np.random.normal(0, 1.0)
            resp = base_resp + 2.5 + 4.5 * progress + np.random.normal(0, 1.0)
            pleth = base_pleth - 0.3 - 0.6 * progress + np.random.normal(0, 0.15)
            temp = base_temp - 0.3 * progress + np.random.normal(0, 0.1)
            weight = base_weight + 0.8 + 1.6 * progress + np.random.normal(0, 0.2)
            quality = 0.88
            
        else: # Stage 4 & 5: High-risk decompensation
            stage = "Stage 4: Impending Decompensation"
            state_label = "High-Risk" if t_hr < 68 else "Possible Decompensation"
            progress = (t_hr - 60) / 12.0
            risk = float(np.clip(0.74 + 0.18 * progress, 0.70, 0.94))
            hr = base_hr + 20.0 + 6.0 * progress + np.random.normal(0, 2.0)
            rmssd = base_rmssd - 22.0 - 4.0 * progress + np.random.normal(0, 1.5)
            scg = base_scg - 9.0 - 3.0 * progress + np.random.normal(0, 1.0)
            resp = base_resp + 7.0 + 3.0 * progress + np.random.normal(0, 1.2)
            pleth = base_pleth - 0.9 - 0.3 * progress + np.random.normal(0, 0.15)
            temp = base_temp - 0.4 + np.random.normal(0, 0.1)
            weight = base_weight + 2.4 + 0.8 * progress + np.random.normal(0, 0.2)
            quality = 0.85
            
        point = {
            "hour": round(float(t_hr), 1),
            "stage": stage,
            "state_label": state_label,
            "risk_score": round(float(risk), 3),
            "heart_rate_bpm": round(float(hr), 1),
            "hrv_rmssd_ms": round(float(max(6.0, rmssd)), 1),
            "scg_mechanical_energy": round(float(max(4.0, scg)), 1),
            "respiration_rate_bpm": round(float(resp), 1),
            "pleth_amplitude": round(float(max(0.4, pleth)), 2),
            "skin_temp_celsius": round(float(temp), 2),
            "weight_kg": round(float(weight), 2),
            "quality_overall": round(float(quality), 2),
            # Personal baseline references for overlay
            "base_hr": base_hr,
            "base_rmssd": base_rmssd,
            "base_scg": base_scg,
            "base_resp": base_resp,
            "base_weight": base_weight
        }
        timeline.append(point)
        
    patient_hf104 = {
        "patient_id": "HF-104",
        "provenance": "SYNTHETIC_LONGITUDINAL_SIMULATION",
        "name": "Arun Kumar (Demo HF-104)",
        "age": 64,
        "gender": "Male",
        "nyha_class": 3,
        "hf_subtype": "HFrEF (EF 28%)",
        "bmi": 27.6,
        "baseline_sbp": 122,
        "baseline_dbp": 76,
        "comorbidities": ["Hypertension", "Coronary Artery Disease", "Prior Decompensation Episode"],
        "timeline": timeline
    }
    
    with open(DEMO_DIR / "patient_hf104_timeline.json", "w") as f:
        json.dump(patient_hf104, f, indent=2)
    print("Generated patient_hf104_timeline.json")

def generate_patient_hf201_timeline():
    """Compensated outpatient demonstration: 72 hours remaining within stable envelope."""
    hours = np.linspace(0, 72, 25)
    timeline = []
    base_hr = 68.0
    base_rmssd = 44.0
    base_scg = 24.0
    base_resp = 14.0
    base_pleth = 2.6
    base_weight = 71.0
    
    for t_hr in hours:
        risk = float(np.clip(0.10 + 0.03 * np.cos(t_hr / 4.0), 0.08, 0.18))
        point = {
            "hour": round(float(t_hr), 1),
            "stage": "Compensated Home Monitoring",
            "state_label": "Stable",
            "risk_score": round(float(risk), 3),
            "heart_rate_bpm": round(float(base_hr + np.random.normal(0, 1.8)), 1),
            "hrv_rmssd_ms": round(float(base_rmssd + np.random.normal(0, 2.2)), 1),
            "scg_mechanical_energy": round(float(base_scg + np.random.normal(0, 1.2)), 1),
            "respiration_rate_bpm": round(float(base_resp + np.random.normal(0, 0.7)), 1),
            "pleth_amplitude": round(float(base_pleth + np.random.normal(0, 0.12)), 2),
            "skin_temp_celsius": round(35.5 + np.random.normal(0, 0.08), 2),
            "weight_kg": round(float(base_weight + np.random.normal(0, 0.15)), 2),
            "quality_overall": 0.94,
            "base_hr": base_hr,
            "base_rmssd": base_rmssd,
            "base_scg": base_scg,
            "base_resp": base_resp,
            "base_weight": base_weight
        }
        timeline.append(point)
        
    patient_hf201 = {
        "patient_id": "HF-201",
        "provenance": "SYNTHETIC_LONGITUDINAL_SIMULATION",
        "name": "Meera Sharma (Demo HF-201)",
        "age": 58,
        "gender": "Female",
        "nyha_class": 2,
        "hf_subtype": "HFpEF (EF 54%)",
        "bmi": 24.8,
        "baseline_sbp": 128,
        "baseline_dbp": 78,
        "comorbidities": ["Hypertension", "Type 2 Diabetes"],
        "timeline": timeline
    }
    
    with open(DEMO_DIR / "patient_hf201_timeline.json", "w") as f:
        json.dump(patient_hf201, f, indent=2)
    print("Generated patient_hf201_timeline.json")

def generate_real_physionet_cohort_sample():
    """Extract real patient sample records from our processed multimodal windows."""
    df = pd.read_parquet("data/processed/multimodal_windows.parquet")
    meta = pd.read_parquet("data/processed/cohort_metadata.parquet")
    
    summary = []
    unique_records = df["record_id"].unique()
    
    for rec_id in unique_records:
        rec_df = df[df["record_id"] == rec_id]
        meta_row = meta[meta["record_id"] == rec_id].iloc[0]
        
        # Calculate summary metrics
        hr_mean = float(rec_df["ecg_hr_mean"].dropna().mean()) if "ecg_hr_mean" in rec_df else 72.0
        scg_mean = float(rec_df["scg_total_energy"].dropna().mean()) if "scg_total_energy" in rec_df else 18.0
        pdecomp = int(meta_row.get("PDecomp", 0))
        cdecomp = int(meta_row.get("CDecomp", 0))
        
        status_label = "Decompensated" if pdecomp == 1 else "Compensated"
        state_label = "High-Risk" if pdecomp == 1 else "Stable"
        
        summary.append({
            "record_id": rec_id,
            "patient_id": meta_row["patient_id"],
            "provenance": "REAL_PHYSIONET_SCG_RHC",
            "age": int(meta_row.get("age", 55)),
            "gender": str(meta_row.get("gender", "M")),
            "nyha_class": int(meta_row.get("NYHAC", 3)),
            "pdecomp": pdecomp,
            "cdecomp": cdecomp,
            "status_label": status_label,
            "state_label": state_label,
            "hr_mean": round(hr_mean, 1),
            "scg_energy_mean": round(scg_mean, 1),
            "history": str(meta_row.get("history", "")),
            "num_windows": len(rec_df)
        })
        
    with open(DEMO_DIR / "real_physionet_cohort_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Generated real_physionet_cohort_summary.json with {len(summary)} real patients.")

if __name__ == "__main__":
    generate_patient_hf104_timeline()
    generate_patient_hf201_timeline()
    generate_real_physionet_cohort_sample()
