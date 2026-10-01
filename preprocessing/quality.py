"""Signal quality assessment for physiological waveforms (ECG, SCG, PLETH).
Detects clipping, missing segments, baseline drift, and flatlines.
"""
import numpy as np

def assess_signal_quality(signal: np.ndarray, fs: float = 500.0, sig_type: str = "ecg") -> dict:
    """Assess signal quality for a 1D waveform window.
    
    Returns:
        dict with:
            - is_valid (bool): overall acceptability
            - quality_score (float): 0.0 (unusable) to 1.0 (pristine)
            - missing_ratio (float)
            - clipping_ratio (float)
            - snr_est (float)
            - issues (list of str)
    """
    if signal is None or len(signal) == 0:
        return {
            "is_valid": False,
            "quality_score": 0.0,
            "missing_ratio": 1.0,
            "clipping_ratio": 0.0,
            "snr_est": 0.0,
            "issues": ["empty_signal"]
        }
    
    issues = []
    n = len(signal)
    
    # 1. Missingness / NaNs
    nan_mask = np.isnan(signal) | np.isinf(signal)
    missing_ratio = float(np.sum(nan_mask) / n)
    if missing_ratio > 0.10:
        issues.append(f"high_missing_data_{missing_ratio:.2f}")
    
    # Clean signal for further checks
    valid_sig = signal[~nan_mask]
    if len(valid_sig) < int(fs * 2): # less than 2 seconds of valid data
        return {
            "is_valid": False,
            "quality_score": 0.0,
            "missing_ratio": missing_ratio,
            "clipping_ratio": 0.0,
            "snr_est": 0.0,
            "issues": issues + ["insufficient_valid_samples"]
        }
        
    # 2. Flatline / zero-variance check
    std_val = float(np.std(valid_sig))
    if std_val < 1e-6:
        issues.append("flatline_zero_variance")
        return {
            "is_valid": False,
            "quality_score": 0.0,
            "missing_ratio": missing_ratio,
            "clipping_ratio": 0.0,
            "snr_est": 0.0,
            "issues": issues
        }
        
    # 3. Clipping / Saturation check
    min_val, max_val = np.min(valid_sig), np.max(valid_sig)
    clip_thresh_hi = max_val - 0.01 * (max_val - min_val)
    clip_thresh_lo = min_val + 0.01 * (max_val - min_val)
    hi_clips = np.sum(valid_sig >= clip_thresh_hi)
    lo_clips = np.sum(valid_sig <= clip_thresh_lo)
    clipping_ratio = float((hi_clips + lo_clips) / len(valid_sig))
    if clipping_ratio > 0.15:
        issues.append(f"signal_saturation_{clipping_ratio:.2f}")

    # 4. Signal-to-Noise Ratio (SNR) proxy based on frequency energy ratio
    # For ECG/SCG, physiological energy is mainly between 0.5 - 40 Hz
    fft_vals = np.abs(np.fft.rfft(valid_sig - np.mean(valid_sig)))
    freqs = np.fft.rfftfreq(len(valid_sig), d=1.0/fs)
    
    if sig_type == "ecg":
        band_mask = (freqs >= 0.5) & (freqs <= 45.0)
    elif sig_type == "scg":
        band_mask = (freqs >= 1.0) & (freqs <= 40.0)
    else:
        band_mask = (freqs >= 0.1) & (freqs <= 10.0)
        
    band_energy = np.sum(fft_vals[band_mask] ** 2)
    total_energy = np.sum(fft_vals ** 2) + 1e-12
    snr_est = float(band_energy / total_energy)
    
    if snr_est < 0.20:
        issues.append(f"low_snr_{snr_est:.2f}")
        
    # Compute continuous quality score [0.0, 1.0]
    score = 1.0 - (missing_ratio * 0.5) - (clipping_ratio * 0.3)
    score = score * min(1.0, snr_est * 1.25)
    quality_score = float(np.clip(score, 0.0, 1.0))
    
    is_valid = (quality_score >= 0.40) and (missing_ratio < 0.20)
    
    return {
        "is_valid": is_valid,
        "quality_score": round(quality_score, 3),
        "missing_ratio": round(missing_ratio, 3),
        "clipping_ratio": round(clipping_ratio, 3),
        "snr_est": round(snr_est, 3),
        "issues": issues
    }
