"""Wearable physiological signals processing: Tri-axial Seismocardiogram (SCG), Plethysmogram (PLETH), Respiration (RESP), and Temperature.
"""
import numpy as np
from scipy import signal

def bandpass_scg(acc_signal: np.ndarray, fs: float = 500.0, lowcut: float = 1.0, highcut: float = 40.0, order: int = 3) -> np.ndarray:
    """Filter accelerometer signal to extract cardiac seismocardiographic mechanical vibrations [1-40 Hz]."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype="band")
    nan_mask = np.isnan(acc_signal)
    clean_sig = acc_signal.copy()
    if np.any(nan_mask):
        clean_sig[nan_mask] = np.nanmean(clean_sig) if not np.all(nan_mask) else 0.0
    return signal.filtfilt(b, a, clean_sig)

def extract_scg_features(acc_lat: np.ndarray, acc_hf: np.ndarray, acc_dv: np.ndarray, fs: float = 500.0) -> dict:
    """Extract mechanocardiographic features from tri-axial SCG accelerometry."""
    features = {
        "scg_dv_rms": np.nan,
        "scg_dv_p2p": np.nan,
        "scg_hf_rms": np.nan,
        "scg_lat_rms": np.nan,
        "scg_total_energy": np.nan,
        "scg_spectral_centroid": np.nan,
        "scg_activity_index": np.nan
    }
    
    if acc_dv is None or len(acc_dv) < int(fs * 2):
        return features
        
    filt_dv = bandpass_scg(acc_dv, fs=fs)
    filt_hf = bandpass_scg(acc_hf, fs=fs) if acc_hf is not None else np.zeros_like(filt_dv)
    filt_lat = bandpass_scg(acc_lat, fs=fs) if acc_lat is not None else np.zeros_like(filt_dv)
    
    # RMS mechanical vibration (mg)
    rms_dv = float(np.sqrt(np.mean(filt_dv ** 2)))
    rms_hf = float(np.sqrt(np.mean(filt_hf ** 2)))
    rms_lat = float(np.sqrt(np.mean(filt_lat ** 2)))
    
    # Peak to peak on dorso-ventral axis (primary SCG axis)
    p2p_dv = float(np.percentile(filt_dv, 95) - np.percentile(filt_dv, 5))
    
    # Combined 3D mechanical kinetic intensity
    total_energy = float(np.sqrt(rms_dv**2 + rms_hf**2 + rms_lat**2))
    
    # Spectral centroid on SCG band (1-40 Hz)
    fft_vals = np.abs(np.fft.rfft(filt_dv))
    freqs = np.fft.rfftfreq(len(filt_dv), d=1.0/fs)
    band_mask = (freqs >= 1.0) & (freqs <= 40.0)
    if np.sum(fft_vals[band_mask]) > 1e-6:
        spec_centroid = float(np.sum(freqs[band_mask] * fft_vals[band_mask]) / np.sum(fft_vals[band_mask]))
    else:
        spec_centroid = 0.0
        
    # Gross movement / activity index (low frequency acceleration envelope)
    raw_mag = np.sqrt(acc_dv**2 + (acc_hf**2 if acc_hf is not None else 0) + (acc_lat**2 if acc_lat is not None else 0))
    act_index = float(np.std(raw_mag))

    return {
        "scg_dv_rms": round(rms_dv, 2),
        "scg_dv_p2p": round(p2p_dv, 2),
        "scg_hf_rms": round(rms_hf, 2),
        "scg_lat_rms": round(rms_lat, 2),
        "scg_total_energy": round(total_energy, 2),
        "scg_spectral_centroid": round(spec_centroid, 2),
        "scg_activity_index": round(act_index, 2)
    }

def extract_pleth_respiration_features(pleth: np.ndarray = None, resp: np.ndarray = None, temp: np.ndarray = None, fs: float = 500.0) -> dict:
    """Extract features from Plethysmogram (PPG), Respiration, and Skin Temperature."""
    features = {
        "pleth_amplitude_mean": np.nan,
        "pleth_amplitude_std": np.nan,
        "resp_rate_bpm": np.nan,
        "resp_variability": np.nan,
        "skin_temp_mean": np.nan,
        "skin_temp_slope": np.nan
    }
    
    # Plethysmography
    if pleth is not None and len(pleth) >= int(fs * 2) and not np.all(np.isnan(pleth)):
        clean_pleth = np.nan_to_num(pleth, nan=np.nanmean(pleth))
        # AC amplitude proxy
        p5 = np.percentile(clean_pleth, 5)
        p95 = np.percentile(clean_pleth, 95)
        features["pleth_amplitude_mean"] = round(float(p95 - p5), 3)
        features["pleth_amplitude_std"] = round(float(np.std(clean_pleth)), 3)
        
    # Respiration
    if resp is not None and len(resp) >= int(fs * 5) and not np.all(np.isnan(resp)):
        clean_resp = np.nan_to_num(resp, nan=np.nanmean(resp))
        # Respiration filter [0.1, 0.6 Hz] = 6 to 36 breaths/min
        nyq = 0.5 * fs
        try:
            b, a = signal.butter(2, [0.1 / nyq, 0.6 / nyq], btype="band")
            filt_resp = signal.filtfilt(b, a, clean_resp)
            peaks, _ = signal.find_peaks(filt_resp, distance=int(1.2 * fs)) # at least 1.2s between breaths
            if len(peaks) >= 2:
                dur_sec = len(resp) / fs
                resp_rate = (len(peaks) / dur_sec) * 60.0
                features["resp_rate_bpm"] = round(float(resp_rate), 1)
                breath_intervals = np.diff(peaks) / fs
                features["resp_variability"] = round(float(np.std(breath_intervals)), 3)
        except Exception:
            pass

    # Skin Temperature
    if temp is not None and len(temp) > 0 and not np.all(np.isnan(temp)):
        valid_temp = temp[~np.isnan(temp)]
        if len(valid_temp) > 0:
            features["skin_temp_mean"] = round(float(np.mean(valid_temp)), 2)
            if len(valid_temp) > 1:
                # Linear slope
                x = np.arange(len(valid_temp))
                slope, _ = np.polyfit(x, valid_temp, 1)
                features["skin_temp_slope"] = round(float(slope * fs * 60), 4) # change per minute
                
    return features
