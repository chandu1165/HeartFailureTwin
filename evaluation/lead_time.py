"""Early-warning lead time calculation module.
Measures the time delta between initial sustained Digital Twin deterioration detection and recorded clinical event.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any

def compute_patient_lead_time(
    df_patient_timeline: pd.DataFrame,
    risk_col: str = "risk_score",
    time_col: str = "time_sec",
    quality_col: str = "quality_overall",
    alert_threshold: float = 0.50,
    persistence_windows: int = 2,
    min_quality: float = 0.40,
    event_time_sec: float = None
) -> Dict[str, Any]:
    """Calculate early detection lead time for an individual patient timeline.
    
    Alert Policy:
        - Risk score >= alert_threshold
        - Persists for at least `persistence_windows` consecutive steps
        - Signal quality >= min_quality
    """
    df = df_patient_timeline.sort_values(time_col).reset_index(drop=True)
    n = len(df)
    if n == 0:
        return {"detected": False, "lead_time_sec": np.nan, "alert_time_sec": np.nan}
        
    if event_time_sec is None:
        # Default event time is the end of the recording or when status changed
        event_time_sec = float(df[time_col].max())
        
    consec_count = 0
    alert_time = None
    
    for idx, row in df.iterrows():
        risk = row.get(risk_col, 0.0)
        quality = row.get(quality_col, 1.0)
        t = row.get(time_col, idx * 30.0)
        
        if (risk >= alert_threshold) and (quality >= min_quality):
            consec_count += 1
            if consec_count >= persistence_windows and alert_time is None:
                # Alert triggers at the timestamp of initial sustained detection
                alert_time = t - (persistence_windows - 1) * 30.0 # window duration offset
                break
        else:
            consec_count = 0
            
    if alert_time is not None and alert_time <= event_time_sec:
        lead_time = event_time_sec - alert_time
        return {
            "detected": True,
            "alert_time_sec": round(alert_time, 1),
            "event_time_sec": round(event_time_sec, 1),
            "lead_time_sec": round(lead_time, 1),
            "lead_time_min": round(lead_time / 60.0, 2),
            "lead_time_hours": round(lead_time / 3600.0, 2)
        }
    else:
        return {
            "detected": False,
            "alert_time_sec": np.nan,
            "event_time_sec": round(event_time_sec, 1),
            "lead_time_sec": 0.0,
            "lead_time_min": 0.0,
            "lead_time_hours": 0.0
        }

def evaluate_cohort_lead_times(
    patient_timelines: List[pd.DataFrame],
    risk_col: str = "risk_score",
    alert_threshold: float = 0.50
) -> Dict[str, Any]:
    """Aggregate lead time statistics across a cohort of deteriorating patients."""
    lead_times_sec = []
    detected_count = 0
    total_decomp = len(patient_timelines)
    
    for df_pt in patient_timelines:
        res = compute_patient_lead_time(df_pt, risk_col=risk_col, alert_threshold=alert_threshold)
        if res["detected"]:
            detected_count += 1
            lead_times_sec.append(res["lead_time_sec"])
            
    detection_rate = detected_count / total_decomp if total_decomp > 0 else 0.0
    mean_lead_sec = float(np.mean(lead_times_sec)) if lead_times_sec else 0.0
    median_lead_sec = float(np.median(lead_times_sec)) if lead_times_sec else 0.0
    
    return {
        "detection_rate": round(detection_rate, 3),
        "total_patients": total_decomp,
        "detected_patients": detected_count,
        "mean_lead_time_sec": round(mean_lead_sec, 1),
        "median_lead_time_sec": round(median_lead_sec, 1),
        "mean_lead_time_hours": round(mean_lead_sec / 3600.0, 2),
        "median_lead_time_hours": round(median_lead_sec / 3600.0, 2)
    }
