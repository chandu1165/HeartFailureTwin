"""End-to-end preprocessing pipeline for HeartFailureTwin.
Windows all available WFDB records, extracts multimodal physiological + EHR features,
computes patient-specific baseline deviations, performs quality checking,
and generates zero-leakage training-ready datasets.
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import wfdb

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.features import process_record_windows
from evaluation.patient_split import create_patient_level_kfold, print_split_summary

DATA_DIR = Path("data/raw/processed_data")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def build_multimodal_dataset(window_sec: float = 20.0, stride_sec: float = 10.0):
    print("=" * 70)
    print("  HEARTFAILURETWIN: MULTIMODAL DATASET PREPROCESSING PIPELINE")
    print("=" * 70)
    
    # 1. Load cohort metadata
    meta_path = OUT_DIR / "cohort_metadata.parquet"
    if not meta_path.exists():
        print("Error: cohort_metadata.parquet not found. Run compile_cohort.py first.")
        return
    df_meta = pd.read_parquet(meta_path)
    print(f"Loaded cohort metadata: {len(df_meta)} records across {df_meta['patient_id'].nunique()} patients.")
    
    # 2. Discover available WFDB records
    dat_files = sorted(list(DATA_DIR.glob("*.dat")))
    print(f"Found {len(dat_files)} waveform (.dat) files available on disk.")
    
    all_window_dfs = []
    processed_records = 0
    
    for dat_file in dat_files:
        rec_name = dat_file.stem
        meta_match = df_meta[df_meta["record_id"] == rec_name]
        if meta_match.empty:
            print(f"  Skipping {rec_name}: metadata not found.")
            continue
            
        meta_dict = meta_match.iloc[0].to_dict()
        patient_id = meta_dict["patient_id"]
        
        # Calculate samples in file
        file_bytes = dat_file.stat().st_size
        hea_file = DATA_DIR / f"{rec_name}.hea"
        n_channels = 16
        if hea_file.exists():
            with open(hea_file, "r") as hf:
                first_line = hf.readline().strip().split()
                if len(first_line) >= 2:
                    n_channels = int(first_line[1])
                    
        bytes_per_sample = 4 # format 32
        samples_in_file = file_bytes // (n_channels * bytes_per_sample)
        
        if samples_in_file < 500 * 10: # at least 10 seconds
            print(f"  Skipping {rec_name}: insufficient samples ({samples_in_file})")
            continue
            
        try:
            record_path = str(DATA_DIR / rec_name)
            rec = wfdb.rdrecord(record_path, sampto=samples_in_file)
            
            df_win = process_record_windows(
                record_id=rec_name,
                patient_id=patient_id,
                signal_data=rec.p_signal,
                sig_names=rec.sig_name,
                fs=rec.fs,
                patient_metadata=meta_dict,
                window_sec=window_sec,
                stride_sec=stride_sec,
                baseline_window_count=2
            )
            
            if not df_win.empty:
                all_window_dfs.append(df_win)
                processed_records += 1
                pdecomp = meta_dict.get("PDecomp", "NA")
                print(f"  Processed {rec_name:15s} | Pt: {patient_id:8s} | {len(df_win):2d} windows | PDecomp: {pdecomp} | Valid ECG: {df_win['signal_valid'].mean()*100:.0f}%")
        except Exception as e:
            print(f"  Error processing {rec_name}: {e}")
            
    if not all_window_dfs:
        print("Error: No window data generated.")
        return
        
    df_dataset = pd.concat(all_window_dfs, ignore_index=True)
    print("\n" + "=" * 70)
    print(f"DATASET EXTRACTION COMPLETE:")
    print(f"  Total records processed: {processed_records}")
    print(f"  Total windows generated: {len(df_dataset)}")
    print(f"  Unique patients:         {df_dataset['patient_id'].nunique()}")
    print(f"  Total feature columns:   {len(df_dataset.columns)}")
    print(f"  Physiological Decomp:    {df_dataset['label_pdecomp'].value_counts(dropna=False).to_dict()}")
    print(f"  Clinical Decomp:         {df_dataset['label_cdecomp'].value_counts(dropna=False).to_dict()}")
    print("=" * 70)
    
    # 3. Save processed dataset
    out_parquet = OUT_DIR / "multimodal_windows.parquet"
    out_csv = OUT_DIR / "multimodal_windows.csv"
    df_dataset.to_parquet(out_parquet, index=False)
    df_dataset.to_csv(out_csv, index=False)
    print(f"Saved dataset to:\n  {out_parquet}\n  {out_csv}")
    
    # 4. Generate & verify patient-level 5-fold cross-validation split
    folds = create_patient_level_kfold(df_dataset, patient_col="patient_id", target_col="label_pdecomp", n_splits=5)
    print_split_summary(folds)
    
    # Save fold assignments
    fold_df = df_dataset[["record_id", "patient_id", "window_idx", "time_sec", "label_pdecomp"]].copy()
    fold_df["fold"] = -1
    for f in folds:
        fold_df.loc[f["val_indices"], "fold"] = f["fold"]
    fold_df.to_csv(OUT_DIR / "patient_kfold_splits.csv", index=False)
    print(f"Saved patient-level splits to: {OUT_DIR / 'patient_kfold_splits.csv'}")

if __name__ == "__main__":
    build_multimodal_dataset()
