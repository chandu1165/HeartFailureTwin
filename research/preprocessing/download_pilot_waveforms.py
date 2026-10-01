"""Rapidly download calibrated real waveform segments for a balanced cohort of patients using HTTP Range requests.
This enables efficient, reproducible WFDB processing without downloading 11.6 GB uncompressed.
"""
import requests
from pathlib import Path
import pandas as pd
import wfdb

BASE_URL = "https://physionet.org/files/scg-rhc-wearable-database/1.0.0/processed_data/"
DATA_DIR = Path("data/raw/processed_data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 2.5 MB = 2,560,000 bytes. Format 32 * 16 channels = 64 bytes/sample -> 40,000 samples (80.0 seconds at 500 Hz)
BYTES_TO_FETCH = 2_560_000

def download_patient_waveforms(n_per_class: int = 10):
    df_meta = pd.read_parquet("data/processed/cohort_metadata.parquet")
    
    # Select distinct patients balanced on PDecomp
    comp = df_meta[df_meta["PDecomp"] == 0].drop_duplicates(subset=["patient_id"]).head(n_per_class)
    decomp = df_meta[df_meta["PDecomp"] == 1].drop_duplicates(subset=["patient_id"]).head(n_per_class)
    
    cohort = pd.concat([comp, decomp]).sort_values("record_id")
    print(f"Target cohort size: {len(cohort)} recordings across {cohort['patient_id'].nunique()} patients.")
    
    session = requests.Session()
    session.headers.update({"User-Agent": "HeartFailureTwin-Research/1.0"})
    
    success = 0
    for idx, row in cohort.iterrows():
        rec_id = row["record_id"]
        dat_path = DATA_DIR / f"{rec_id}.dat"
        hea_path = DATA_DIR / f"{rec_id}.hea"
        
        if dat_path.exists() and dat_path.stat().st_size >= BYTES_TO_FETCH:
            print(f"  {rec_id}: already present ({dat_path.stat().st_size / 1024:.0f} KB)")
            success += 1
            continue
            
        url = f"{BASE_URL}{rec_id}.dat"
        headers = {"Range": f"bytes=0-{BYTES_TO_FETCH - 1}"}
        downloaded = False
        for attempt in range(3):
            try:
                r = session.get(url, headers=headers, timeout=25)
                if r.status_code in [200, 206]:
                    dat_path.write_bytes(r.content)
                    actual_samples = len(r.content) // (16 * 4)
                    print(f"  Downloaded {rec_id}.dat ({len(r.content)/1024:.0f} KB, {actual_samples} samples, {actual_samples/500:.1f}s)")
                    success += 1
                    downloaded = True
                    break
                else:
                    print(f"  Attempt {attempt+1} Failed {rec_id} (HTTP {r.status_code})")
            except Exception as e:
                print(f"  Attempt {attempt+1} error fetching {rec_id}: {e}")
                import time
                time.sleep(1.5)
        if not downloaded:
            print(f"  Could not download {rec_id} after 3 attempts.")
            
    print(f"\nCohort download complete. Available records: {success} / {len(cohort)}")

if __name__ == "__main__":
    download_patient_waveforms(n_per_class=10)
