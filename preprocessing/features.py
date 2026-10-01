"""Multimodal feature engineering engine: extracts windowed physiological features,
signal quality indexes, EHR profiles, and patient-specific baseline deviations.
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional

from preprocessing.quality import assess_signal_quality
from preprocessing.ecg import extract_ecg_features
from preprocessing.wearable import extract_scg_features, extract_pleth_respiration_features
from preprocessing.ehr import extract_ehr_features

def process_record_windows(
    record_id: str,
    patient_id: str,
    signal_data: np.ndarray,
    sig_names: List[str],
    fs: float,
    patient_metadata: Dict[str, Any],
    window_sec: float = 30.0,
    stride_sec: float = 30.0,
    baseline_window_count: int = 3
) -> pd.DataFrame:
    """Process a continuous multi-channel recording into windowed feature vectors.
    
    Args:
        record_id: e.g. TRM107-RHC1
        patient_id: e.g. TRM107
        signal_data: shape (N, C) array of physical signals
        sig_names: list of signal names
        fs: sampling frequency (e.g. 500 Hz)
        patient_metadata: row dictionary containing demographics, CDecomp, PDecomp, hemodynamics
        window_sec: window duration in seconds (default 30s)
        stride_sec: step between consecutive windows (default 30s)
        baseline_window_count: number of initial windows used to calibrate patient personal baseline
        
    Returns:
        pd.DataFrame with windowed multimodal features and personal baseline deviations.
    """
    total_samples = signal_data.shape[0]
    win_samples = int(window_sec * fs)
    stride_samples = int(stride_sec * fs)
    
    # Map channel names to column indices
    sig_map = {name.lower(): idx for idx, name in enumerate(sig_names)}
    
    def get_chan(name_candidates):
        for candidate in name_candidates:
            if candidate.lower() in sig_map:
                return signal_data[:, sig_map[candidate.lower()]]
        return None

    ecg_sig = get_chan(["patch_ecg", "ecg_lead_ii", "ecg_lead_i"])
    acc_lat = get_chan(["patch_acc_lat"])
    acc_hf = get_chan(["patch_acc_hf"])
    acc_dv = get_chan(["patch_acc_dv"])
    pleth_sig = get_chan(["pleth"])
    resp_sig = get_chan(["resp"])
    temp_sig = get_chan(["patch_temp"])
    rhc_sig = get_chan(["rhc_pressure"])

    ehr_feats = extract_ehr_features(patient_metadata)
    
    # Extract ground-truth labels
    pdecomp_label = patient_metadata.get("PDecomp", np.nan)
    cdecomp_label = patient_metadata.get("CDecomp", np.nan)
    pam_label = patient_metadata.get("PAM", np.nan)
    pcwm_label = patient_metadata.get("PCWM", np.nan)
    
    # Try parsing numeric labels if stored as string
    try:
        pdecomp_label = float(pdecomp_label)
    except (ValueError, TypeError):
        pdecomp_label = np.nan
    try:
        cdecomp_label = float(cdecomp_label)
    except (ValueError, TypeError):
        cdecomp_label = np.nan

    windows_data = []
    window_idx = 0
    start_sample = 0
    
    while start_sample + win_samples <= total_samples:
        end_sample = start_sample + win_samples
        time_sec = start_sample / fs
        
        # 1. Channel slices
        ecg_win = ecg_sig[start_sample:end_sample] if ecg_sig is not None else None
        lat_win = acc_lat[start_sample:end_sample] if acc_lat is not None else None
        hf_win = acc_hf[start_sample:end_sample] if acc_hf is not None else None
        dv_win = acc_dv[start_sample:end_sample] if acc_dv is not None else None
        pleth_win = pleth_sig[start_sample:end_sample] if pleth_sig is not None else None
        resp_win = resp_sig[start_sample:end_sample] if resp_sig is not None else None
        temp_win = temp_sig[start_sample:end_sample] if temp_sig is not None else None
        rhc_win = rhc_sig[start_sample:end_sample] if rhc_sig is not None else None
        
        # 2. Quality assessment
        q_ecg = assess_signal_quality(ecg_win, fs=fs, sig_type="ecg")
        q_scg = assess_signal_quality(dv_win, fs=fs, sig_type="scg") if dv_win is not None else {"quality_score": 0.0, "is_valid": False}
        
        # 3. Waveform features
        ecg_feats = extract_ecg_features(ecg_win, fs=fs)
        scg_feats = extract_scg_features(lat_win, hf_win, dv_win, fs=fs)
        pleth_resp_feats = extract_pleth_respiration_features(pleth_win, resp_win, temp_win, fs=fs)
        
        # 4. Instantaneous invasive pressure if available in recording
        rhc_mean = float(np.nanmean(rhc_win)) if rhc_win is not None and not np.all(np.isnan(rhc_win)) else np.nan
        
        win_record = {
            "record_id": record_id,
            "patient_id": patient_id,
            "window_idx": window_idx,
            "time_sec": round(time_sec, 1),
            # Quality
            "quality_ecg": q_ecg["quality_score"],
            "quality_scg": q_scg["quality_score"],
            "quality_overall": round((q_ecg["quality_score"] + q_scg["quality_score"]) / 2.0, 2),
            "signal_valid": int(q_ecg["is_valid"]),
            # Physiological
            **ecg_feats,
            **scg_feats,
            **pleth_resp_feats,
            "rhc_pressure_window_mean": round(rhc_mean, 2) if not np.isnan(rhc_mean) else np.nan,
            # EHR Static
            **ehr_feats,
            # Targets
            "label_pdecomp": pdecomp_label,
            "label_cdecomp": cdecomp_label,
            "target_pam": pam_label,
            "target_pcwm": pcwm_label
        }
        
        windows_data.append(win_record)
        window_idx += 1
        start_sample += stride_samples
        
    df_win = pd.DataFrame(windows_data)
    if df_win.empty:
        return df_win

    # 5. Calculate Patient-Specific Baseline and Deviations
    # Baseline is calibrated strictly using the first N baseline windows (no forward leakage!)
    calib_count = min(len(df_win), max(1, baseline_window_count))
    baseline_rows = df_win.iloc[:calib_count]
    
    dynamic_cols = [
        "ecg_hr_mean", "ecg_sdnn_ms", "ecg_rmssd_ms",
        "scg_dv_rms", "scg_total_energy", "scg_activity_index",
        "resp_rate_bpm", "skin_temp_mean", "pleth_amplitude_mean"
    ]
    
    for col in dynamic_cols:
        if col in df_win.columns:
            base_mean = float(baseline_rows[col].mean())
            base_std = float(baseline_rows[col].std()) if len(baseline_rows) > 1 else 1.0
            if np.isnan(base_std) or base_std < 1e-4:
                base_std = 1.0
                
            df_win[f"{col}_baseline"] = round(base_mean, 2)
            # Absolute personal deviation: current - baseline
            df_win[f"{col}_dev"] = round(df_win[col] - base_mean, 2)
            # Relative percentage personal deviation
            if abs(base_mean) > 1e-4:
                df_win[f"{col}_dev_pct"] = round(((df_win[col] - base_mean) / base_mean) * 100.0, 2)
            else:
                df_win[f"{col}_dev_pct"] = 0.0
            # Normalized z-score deviation
            df_win[f"{col}_zscore"] = round((df_win[col] - base_mean) / base_std, 2)

    return df_win
