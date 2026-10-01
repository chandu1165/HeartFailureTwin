"""Comprehensive Ablation Study across Modalities and Personalization.
Validates the core research question:
"Does our personalized Digital Twin provide meaningful improvement over simpler approaches?"
Evaluates:
1. EHR Only (Static Clinical History)
2. Wearable + ECG Only (No EHR)
3. EHR + Wearables (No ECG)
4. Full Multimodal without Personalization (Population-level)
5. Multimodal + Patient-Specific Baseline Deviations
6. Full HeartFailureTwin (Multimodal + Personalization + Temporal Gating)
Deliverable: results/ablation_study_results.csv
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import torch
import torch.nn as nn

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.patient_split import create_patient_level_kfold
from evaluation.metrics import compute_classification_metrics
from evaluation.lead_time import compute_patient_lead_time

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Feature subsets
EHR_COLS = [
    "ehr_age", "ehr_gender_male", "ehr_weight_kg", "ehr_bmi", "ehr_sbp", "ehr_dbp",
    "ehr_pulse_pressure", "ehr_map", "ehr_nyha", "ehr_htn", "ehr_dm", "ehr_cad",
    "ehr_ckd", "ehr_hfref", "ehr_hfpef"
]

ECG_COLS = [
    "ecg_hr_mean", "ecg_hr_std", "ecg_sdnn_ms", "ecg_rmssd_ms", "ecg_pnn50", "ecg_qrs_energy"
]

WEARABLE_COLS = [
    "scg_dv_rms", "scg_dv_p2p", "scg_hf_rms", "scg_lat_rms", "scg_total_energy",
    "scg_spectral_centroid", "scg_activity_index", "pleth_amplitude_mean", "resp_rate_bpm", "skin_temp_mean"
]

DEV_COLS = [
    "ecg_hr_mean_dev", "ecg_hr_mean_dev_pct", "ecg_hr_mean_zscore",
    "scg_total_energy_dev", "scg_total_energy_dev_pct", "scg_total_energy_zscore",
    "ecg_rmssd_ms_dev", "resp_rate_bpm_dev", "scg_dv_rms_dev"
]

QUALITY_COLS = ["quality_overall", "quality_ecg", "quality_scg"]

def evaluate_ablation_condition(df, folds, feature_cols, condition_name):
    available_cols = [c for c in feature_cols if c in df.columns]
    
    oof_preds = np.zeros(len(df))
    oof_targets = np.zeros(len(df))
    valid_mask = np.zeros(len(df), dtype=bool)
    fold_aurocs = []
    fold_auprcs = []
    
    for f in folds:
        tr_idx = f["train_indices"]
        v_idx = f["val_indices"]
        
        X_tr = df.loc[tr_idx, available_cols].to_numpy()
        y_tr = df.loc[tr_idx, "label_pdecomp"].to_numpy().astype(int)
        X_v = df.loc[v_idx, available_cols].to_numpy()
        y_v = df.loc[v_idx, "label_pdecomp"].to_numpy().astype(int)
        
        imputer = SimpleImputer(strategy="median")
        X_tr_imp = imputer.fit_transform(X_tr)
        X_v_imp = imputer.transform(X_v)
        
        pos_count = np.sum(y_tr == 1)
        neg_count = np.sum(y_tr == 0)
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
        model.fit(X_tr_imp, y_tr)
        probs = model.predict_proba(X_v_imp)[:, 1]
        
        oof_preds[v_idx] = probs
        oof_targets[v_idx] = y_v
        valid_mask[v_idx] = True
        
        m = compute_classification_metrics(y_v, probs)
        fold_aurocs.append(m["auroc"])
        fold_auprcs.append(m["auprc"])
        
    oof_m = compute_classification_metrics(oof_targets[valid_mask], oof_preds[valid_mask])
    
    # Measure average lead time across decompensated patients
    df_eval = df.copy()
    df_eval["pred_risk"] = oof_preds
    decomp_patients = df_eval[df_eval["label_pdecomp"] == 1]["patient_id"].unique()
    lead_times_sec = []
    for pid in decomp_patients:
        pt_df = df_eval[df_eval["patient_id"] == pid].sort_values("time_sec")
        lt_res = compute_patient_lead_time(pt_df, risk_col="pred_risk", alert_threshold=0.50)
        if lt_res["detected"]:
            lead_times_sec.append(lt_res["lead_time_sec"])
            
    mean_lead_min = round(float(np.mean(lead_times_sec) / 60.0), 2) if lead_times_sec else 0.0

    return {
        "Ablation_Condition": condition_name,
        "Num_Features": len(available_cols),
        "AUROC_mean": round(float(np.mean(fold_aurocs)), 4),
        "AUROC_OOF": oof_m["auroc"],
        "AUPRC_mean": round(float(np.mean(fold_auprcs)), 4),
        "AUPRC_OOF": oof_m["auprc"],
        "Sensitivity": oof_m["sensitivity"],
        "Specificity": oof_m["specificity"],
        "F1_Score": oof_m["f1"],
        "Brier_Score": oof_m["brier_score"],
        "ECE": oof_m["ece"],
        "Lead_Time_Min": mean_lead_min
    }

def main():
    print("=" * 80)
    print("           HEARTFAILURETWIN: CRITICAL ABLATION STUDY (PHASE 7)")
    print("=" * 80)
    
    data_path = Path("data/processed/multimodal_windows.parquet")
    df = pd.read_parquet(data_path)
    folds = create_patient_level_kfold(df, patient_col="patient_id", target_col="label_pdecomp", n_splits=5)
    
    experiments = [
        ("1. EHR Only (Static Profile)", EHR_COLS),
        ("2. Wearable + ECG Only (No EHR)", ECG_COLS + WEARABLE_COLS + QUALITY_COLS),
        ("3. EHR + Wearables (No ECG)", EHR_COLS + WEARABLE_COLS + QUALITY_COLS),
        ("4. EHR + ECG (No Wearables/SCG)", EHR_COLS + ECG_COLS + QUALITY_COLS),
        ("5. Multimodal (No Personalization / Population)", EHR_COLS + ECG_COLS + WEARABLE_COLS + QUALITY_COLS),
        ("6. Full HeartFailureTwin (+ Personalized Baseline)", EHR_COLS + ECG_COLS + WEARABLE_COLS + DEV_COLS + QUALITY_COLS)
    ]
    
    records = []
    for name, feats in experiments:
        print(f"Running Ablation: {name}...")
        rec = evaluate_ablation_condition(df, folds, feats, name)
        records.append(rec)
        print(f"  -> AUROC_OOF: {rec['AUROC_OOF']:.4f} | AUPRC_OOF: {rec['AUPRC_OOF']:.4f} | F1: {rec['F1_Score']:.4f} | Lead Time: {rec['Lead_Time_Min']} min")
        
    df_ablation = pd.DataFrame(records)
    out_csv = RESULTS_DIR / "ablation_study_results.csv"
    df_ablation.to_csv(out_csv, index=False)
    
    print("\n" + "=" * 80)
    print("                    CRITICAL ABLATION STUDY RESULTS")
    print("=" * 80)
    print(df_ablation[["Ablation_Condition", "AUROC_OOF", "AUPRC_OOF", "Sensitivity", "Specificity", "F1_Score", "Lead_Time_Min"]].to_string(index=False))
    print("=" * 80)
    print(f"\nSaved ablation results to: {out_csv}")

if __name__ == "__main__":
    main()
