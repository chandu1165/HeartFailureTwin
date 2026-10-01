"""Patient-Specific Baseline Engine.
Maintains personalized normal physiological ranges and computes individualized deviations.
"""
from typing import Dict, Any, List, Optional
import numpy as np

class PatientBaselineEngine:
    """Calculates and maintains patient-specific physiological baselines."""
    
    DEFAULT_RANGES = {
        "heart_rate_bpm": (60.0, 80.0, 70.0, 5.0), # min, max, mean, std
        "hrv_rmssd_ms": (25.0, 65.0, 42.0, 8.0),
        "scg_mechanical_energy": (10.0, 30.0, 18.0, 4.0),
        "respiration_rate_bpm": (12.0, 18.0, 15.0, 2.0),
        "pleth_amplitude": (1.0, 3.5, 2.2, 0.4),
        "skin_temp_celsius": (34.0, 36.5, 35.2, 0.4)
    }

    def __init__(self, patient_id: str, baseline_profiles: Optional[Dict[str, Dict[str, float]]] = None):
        self.patient_id = patient_id
        # { feature: { 'mean': val, 'std': val, 'q25': val, 'q75': val } }
        self.baselines: Dict[str, Dict[str, float]] = {}
        if baseline_profiles:
            self.baselines = baseline_profiles.copy()

    def calibrate_from_history(self, history_windows: List[Dict[str, float]]):
        """Calibrate personal baseline from a patient's historical or initial resting windows."""
        if not history_windows:
            return
            
        keys = list(self.DEFAULT_RANGES.keys())
        for k in keys:
            vals = [w[k] for w in history_windows if k in w and not np.isnan(w[k])]
            if len(vals) >= 2:
                mean_val = float(np.mean(vals))
                std_val = float(np.std(vals))
                if std_val < 0.1:
                    std_val = self.DEFAULT_RANGES[k][3] # fallback to default std
                self.baselines[k] = {
                    "mean": round(mean_val, 2),
                    "std": round(std_val, 2),
                    "min": round(float(np.min(vals)), 2),
                    "max": round(float(np.max(vals)), 2)
                }
            elif k in self.DEFAULT_RANGES:
                # Use clinical reference default
                d = self.DEFAULT_RANGES[k]
                self.baselines[k] = {
                    "mean": d[2],
                    "std": d[3],
                    "min": d[0],
                    "max": d[1]
                }

    def get_baseline_summary(self) -> Dict[str, Dict[str, float]]:
        """Return the dictionary of baseline values."""
        return self.baselines

    def compute_deviations(self, current_vitals: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Compare current vitals against personalized baseline.
        
        Returns:
            Dict mapping feature_name -> {
                'current': float,
                'baseline': float,
                'deviation_abs': float,
                'deviation_pct': float,
                'z_score': float,
                'is_abnormal': bool
            }
        """
        results = {}
        for feat, curr_val in current_vitals.items():
            if curr_val is None or np.isnan(curr_val):
                continue
                
            base_info = self.baselines.get(feat)
            if not base_info:
                # Fallback to default
                if feat in self.DEFAULT_RANGES:
                    d = self.DEFAULT_RANGES[feat]
                    base_mean = d[2]
                    base_std = d[3]
                else:
                    base_mean = curr_val
                    base_std = 1.0
            else:
                base_mean = base_info["mean"]
                base_std = base_info["std"]

            dev_abs = curr_val - base_mean
            dev_pct = (dev_abs / base_mean * 100.0) if abs(base_mean) > 1e-4 else 0.0
            z_score = dev_abs / base_std if base_std > 1e-4 else 0.0
            
            # An individual observation is considered personalized abnormal if |z| > 2.0 (outside 95% individual confidence envelope)
            is_abnormal = abs(z_score) >= 2.0

            results[feat] = {
                "current": round(float(curr_val), 2),
                "baseline": round(float(base_mean), 2),
                "deviation_abs": round(float(dev_abs), 2),
                "deviation_pct": round(float(dev_pct), 1),
                "z_score": round(float(z_score), 2),
                "is_abnormal": is_abnormal
            }
            
        return results
