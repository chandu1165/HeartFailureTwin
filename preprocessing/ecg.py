"""ECG processing module: filtering, R-peak detection, Heart Rate, and HRV metrics.
"""
import numpy as np
from scipy import signal

def bandpass_filter_ecg(ecg: np.ndarray, fs: float = 500.0, lowcut: float = 0.5, highcut: float = 45.0, order: int = 3) -> np.ndarray:
    """Apply zero-phase Butterworth bandpass filter to ECG waveform."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype="band")
    # Handle NaNs if present
    nan_mask = np.isnan(ecg)
    if np.all(nan_mask):
        return np.zeros_like(ecg)
    clean_ecg = ecg.copy()
    if np.any(nan_mask):
        clean_ecg[nan_mask] = np.nanmean(clean_ecg)
    filtered = signal.filtfilt(b, a, clean_ecg)
    return filtered

def find_r_peaks(filtered_ecg: np.ndarray, fs: float = 500.0) -> np.ndarray:
    """Find R-peaks using derivative, squaring, moving integration and peak detection."""
    if len(filtered_ecg) < int(fs * 2):
        return np.array([], dtype=int)
    
    # Derivative
    diff_sig = np.diff(filtered_ecg, prepend=filtered_ecg[0])
    # Squaring
    squared = diff_sig ** 2
    # Moving window integration (approx 150 ms)
    win_size = int(0.15 * fs)
    kernel = np.ones(win_size) / win_size
    integrated = np.convolve(squared, kernel, mode="same")
    
    # Adaptive thresholding
    threshold = np.mean(integrated) + 0.5 * np.std(integrated)
    min_distance = int(0.30 * fs) # minimum 300 ms between heartbeats (max 200 bpm)
    
    peaks, _ = signal.find_peaks(integrated, height=threshold, distance=min_distance)
    
    # Refine peak locations on original filtered signal (local maximum within +/- 50ms)
    refined_peaks = []
    search_radius = int(0.05 * fs)
    for p in peaks:
        start_idx = max(0, p - search_radius)
        end_idx = min(len(filtered_ecg), p + search_radius + 1)
        local_max = start_idx + np.argmax(filtered_ecg[start_idx:end_idx])
        refined_peaks.append(local_max)
        
    return np.array(sorted(list(set(refined_peaks))), dtype=int)

def extract_ecg_features(raw_ecg: np.ndarray, fs: float = 500.0) -> dict:
    """Extract clinical & physiological features from an ECG window (e.g. 30 seconds)."""
    default_features = {
        "ecg_hr_mean": np.nan,
        "ecg_hr_std": np.nan,
        "ecg_hr_min": np.nan,
        "ecg_hr_max": np.nan,
        "ecg_rr_mean_ms": np.nan,
        "ecg_sdnn_ms": np.nan,
        "ecg_rmssd_ms": np.nan,
        "ecg_pnn50": np.nan,
        "ecg_qrs_energy": np.nan,
        "ecg_r_peak_count": 0
    }
    
    if raw_ecg is None or len(raw_ecg) < int(fs * 3):
        return default_features

    filtered = bandpass_filter_ecg(raw_ecg, fs=fs)
    peaks = find_r_peaks(filtered, fs=fs)
    
    if len(peaks) < 3:
        return default_features

    # RR intervals in milliseconds
    rr_intervals_sec = np.diff(peaks) / fs
    rr_intervals_ms = rr_intervals_sec * 1000.0
    
    # Filter physiologically plausible RR intervals (300 ms to 2000 ms, corresponding to 30-200 bpm)
    valid_rr = rr_intervals_ms[(rr_intervals_ms >= 300.0) & (rr_intervals_ms <= 2000.0)]
    if len(valid_rr) < 2:
        return default_features

    # Instantaneous Heart Rates (bpm)
    hr_values = 60000.0 / valid_rr
    
    # Successive differences
    successive_diffs = np.diff(valid_rr)
    rmssd = float(np.sqrt(np.mean(successive_diffs ** 2)))
    pnn50 = float(np.sum(np.abs(successive_diffs) > 50.0) / len(successive_diffs)) if len(successive_diffs) > 0 else 0.0

    return {
        "ecg_hr_mean": float(np.round(np.mean(hr_values), 2)),
        "ecg_hr_std": float(np.round(np.std(hr_values), 2)),
        "ecg_hr_min": float(np.round(np.min(hr_values), 2)),
        "ecg_hr_max": float(np.round(np.max(hr_values), 2)),
        "ecg_rr_mean_ms": float(np.round(np.mean(valid_rr), 2)),
        "ecg_sdnn_ms": float(np.round(np.std(valid_rr), 2)),
        "ecg_rmssd_ms": float(np.round(rmssd, 2)),
        "ecg_pnn50": float(np.round(pnn50, 4)),
        "ecg_qrs_energy": float(np.round(np.mean(filtered[peaks] ** 2), 4)),
        "ecg_r_peak_count": int(len(peaks))
    }
