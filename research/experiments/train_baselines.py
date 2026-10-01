"""Benchmark comparison of classical and temporal baseline models for heart failure decompensation.
Models evaluated:
1. Logistic Regression
2. Random Forest
3. XGBoost
4. Temporal GRU (PyTorch)
Evaluated across zero-leakage patient-level folds.
Deliverable: results/baseline_results.csv
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import xgboost as xgb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.patient_split import create_patient_level_kfold
from evaluation.metrics import compute_classification_metrics
from research.models.recurrent import PhysiologicalGRU

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Selected features across modalities
FEATURE_COLS = [
    # Static EHR
    "ehr_age", "ehr_gender_male", "ehr_weight_kg", "ehr_bmi", "ehr_sbp", "ehr_dbp",
    "ehr_pulse_pressure", "ehr_map", "ehr_nyha", "ehr_htn", "ehr_dm", "ehr_cad",
    "ehr_ckd", "ehr_hfref", "ehr_hfpef",
    # Dynamic ECG
    "ecg_hr_mean", "ecg_hr_std", "ecg_sdnn_ms", "ecg_rmssd_ms", "ecg_pnn50", "ecg_qrs_energy",
    # Dynamic SCG
    "scg_dv_rms", "scg_dv_p2p", "scg_hf_rms", "scg_lat_rms", "scg_total_energy",
    "scg_spectral_centroid", "scg_activity_index",
    # Wearable Vitals
    "pleth_amplitude_mean", "pleth_amplitude_std", "resp_rate_bpm", "skin_temp_mean",
    # Signal Quality
    "quality_overall", "quality_ecg", "quality_scg"
]

def train_eval_logistic_regression(X_train, y_train, X_val, y_val):
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(imputer.fit_transform(X_train))
    X_v = scaler.transform(imputer.transform(X_val))
    
    clf = LogisticRegression(max_iter=1000, C=0.5, class_weight="balanced", random_state=42)
    clf.fit(X_tr, y_train)
    probs = clf.predict_proba(X_v)[:, 1]
    return probs

def train_eval_random_forest(X_train, y_train, X_val, y_val):
    imputer = SimpleImputer(strategy="median")
    X_tr = imputer.fit_transform(X_train)
    X_v = imputer.transform(X_val)
    
    clf = RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_split=4, class_weight="balanced", random_state=42)
    clf.fit(X_tr, y_train)
    probs = clf.predict_proba(X_v)[:, 1]
    return probs

def train_eval_xgboost(X_train, y_train, X_val, y_val):
    imputer = SimpleImputer(strategy="median")
    X_tr = imputer.fit_transform(X_train)
    X_v = imputer.transform(X_val)
    
    # Calculate scale_pos_weight
    pos_count = np.sum(y_train == 1)
    neg_count = np.sum(y_train == 0)
    scale_pos = (neg_count / pos_count) if pos_count > 0 else 1.0
    
    model = xgb.XGBClassifier(
        n_estimators=80,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos,
        eval_metric="logloss",
        random_state=42
    )
    model.fit(X_tr, y_train)
    probs = model.predict_proba(X_v)[:, 1]
    return probs

def train_eval_gru(X_train, y_train, X_val, y_val, seq_len: int = 3, epochs: int = 25):
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(imputer.fit_transform(X_train))
    X_v = scaler.transform(imputer.transform(X_val))
    
    # Create temporal pseudo-sequences (seq_len, dim)
    def make_sequences(arr):
        n, d = arr.shape
        seqs = []
        for i in range(n):
            if i < seq_len - 1:
                # Pad earlier steps with repeat
                pad = np.tile(arr[i], (seq_len - 1 - i, 1))
                seq = np.vstack([pad, arr[:i + 1]])
            else:
                seq = arr[i - seq_len + 1 : i + 1]
            seqs.append(seq)
        return np.array(seqs, dtype=np.float32)
        
    X_tr_seq = torch.tensor(make_sequences(X_tr), dtype=torch.float32)
    y_tr_tensor = torch.tensor(y_train, dtype=torch.float32)
    X_v_seq = torch.tensor(make_sequences(X_v), dtype=torch.float32)
    
    dataset = TensorDataset(X_tr_seq, y_tr_tensor)
    loader = DataLoader(dataset, batch_size=16, shuffle=True)
    
    torch.manual_seed(42)
    model = PhysiologicalGRU(input_dim=X_tr.shape[1], hidden_dim=24, num_layers=1, dropout=0.1)
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-4)
    
    model.train()
    for _ in range(epochs):
        for bx, by in loader:
            optimizer.zero_grad()
            preds = model(bx)
            loss = criterion(preds, by)
            loss.backward()
            optimizer.step()
            
    model.eval()
    with torch.no_grad():
        val_probs = model(X_v_seq).numpy()
    return val_probs

def main():
    print("=" * 70)
    print("  HEARTFAILURETWIN: BASELINE MODEL BENCHMARKING (PHASE 2)")
    print("=" * 70)
    
    # Load dataset
    data_path = Path("data/processed/multimodal_windows.parquet")
    df = pd.read_parquet(data_path)
    
    # Filter available features
    available_feats = [col for col in FEATURE_COLS if col in df.columns]
    print(f"Dataset shape: {df.shape}")
    print(f"Features used ({len(available_feats)}): {available_feats[:5]} ... {available_feats[-3:]}")
    
    # Load zero-leakage folds
    folds = create_patient_level_kfold(df, patient_col="patient_id", target_col="label_pdecomp", n_splits=5)
    
    models = {
        "Logistic Regression": train_eval_logistic_regression,
        "Random Forest": train_eval_random_forest,
        "XGBoost": train_eval_xgboost,
        "GRU (Recurrent)": train_eval_gru
    }
    
    results_records = []
    
    for model_name, train_fn in models.items():
        print(f"\n--- Evaluating {model_name} across 5 patient-level folds ---")
        fold_metrics = []
        oof_preds = np.zeros(len(df))
        oof_targets = np.zeros(len(df))
        valid_mask = np.zeros(len(df), dtype=bool)
        
        for f in folds:
            tr_idx = f["train_indices"]
            v_idx = f["val_indices"]
            
            X_train = df.loc[tr_idx, available_feats].to_numpy()
            y_train = df.loc[tr_idx, "label_pdecomp"].to_numpy().astype(int)
            X_val = df.loc[v_idx, available_feats].to_numpy()
            y_val = df.loc[v_idx, "label_pdecomp"].to_numpy().astype(int)
            
            preds = train_fn(X_train, y_train, X_val, y_val)
            oof_preds[v_idx] = preds
            oof_targets[v_idx] = y_val
            valid_mask[v_idx] = True
            
            m = compute_classification_metrics(y_val, preds)
            fold_metrics.append(m)
            print(f"  Fold {f['fold']} | Val Patients: {len(f['val_patients']):2d} | AUROC: {m['auroc']:.4f} | AUPRC: {m['auprc']:.4f} | F1: {m['f1']:.4f}")
            
        # Overall Out-of-Fold (OOF) Metrics
        oof_m = compute_classification_metrics(oof_targets[valid_mask], oof_preds[valid_mask])
        mean_auroc = np.mean([fm["auroc"] for fm in fold_metrics])
        mean_auprc = np.mean([fm["auprc"] for fm in fold_metrics])
        mean_f1 = np.mean([fm["f1"] for fm in fold_metrics])
        mean_brier = np.mean([fm["brier_score"] for fm in fold_metrics])
        mean_ece = np.mean([fm["ece"] for fm in fold_metrics])
        
        rec = {
            "Model": model_name,
            "AUROC_mean": round(mean_auroc, 4),
            "AUROC_OOF": oof_m["auroc"],
            "AUPRC_mean": round(mean_auprc, 4),
            "AUPRC_OOF": oof_m["auprc"],
            "Sensitivity": oof_m["sensitivity"],
            "Specificity": oof_m["specificity"],
            "Precision": oof_m["precision"],
            "F1_Score": oof_m["f1"],
            "Brier_Score": oof_m["brier_score"],
            "ECE": oof_m["ece"],
            "False_Alarm_Rate": oof_m["false_positive_rate"]
        }
        results_records.append(rec)
        
    df_results = pd.DataFrame(results_records)
    out_csv = RESULTS_DIR / "baseline_results.csv"
    df_results.to_csv(out_csv, index=False)
    
    print("\n" + "=" * 80)
    print("                    PHASE 2: BASELINE BENCHMARK RESULTS")
    print("=" * 80)
    print(df_results.to_string(index=False))
    print("=" * 80)
    print(f"\nSaved official benchmark table to: {out_csv}")

if __name__ == "__main__":
    main()
