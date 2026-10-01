"""Evaluation metrics suite for heart failure decompensation forecasting.
Calculates AUROC, AUPRC, Sensitivity, Specificity, F1, Brier Score, and Calibration ECE.
"""
import numpy as np
from sklearn.metrics import (
    roc_auc_score,
    precision_recall_curve,
    auc,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score
)
from typing import Dict, Any

def compute_classification_metrics(y_true: np.ndarray, y_pred_prob: np.ndarray, threshold: float = 0.5) -> Dict[str, float]:
    """Compute comprehensive clinical ML metrics for binary decompensation forecasting."""
    y_true = np.asarray(y_true, dtype=int)
    y_pred_prob = np.asarray(y_pred_prob, dtype=float)
    y_pred_bin = (y_pred_prob >= threshold).astype(int)
    
    # 1. Discrimination: AUROC
    try:
        if len(np.unique(y_true)) > 1:
            auroc = float(roc_auc_score(y_true, y_pred_prob))
        else:
            auroc = 0.5
    except Exception:
        auroc = 0.5
        
    # 2. Discrimination: AUPRC (Precision-Recall AUC)
    try:
        if len(np.unique(y_true)) > 1:
            precision_vals, recall_vals, _ = precision_recall_curve(y_true, y_pred_prob)
            auprc = float(auc(recall_vals, precision_vals))
        else:
            auprc = float(np.mean(y_true))
    except Exception:
        auprc = float(np.mean(y_true))
        
    # 3. Calibration: Brier Score
    brier = float(brier_score_loss(y_true, y_pred_prob))
    
    # 4. Calibration: Expected Calibration Error (ECE)
    ece = compute_expected_calibration_error(y_true, y_pred_prob, n_bins=10)
    
    # 5. Confusion matrix metrics
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred_bin, labels=[0, 1]).ravel()
    sensitivity = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0 # Recall
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    precision = float(precision_score(y_true, y_pred_bin, zero_division=0))
    f1 = float(f1_score(y_true, y_pred_bin, zero_division=0))
    
    # False alarm rate (1 - specificity = FPR)
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

    return {
        "auroc": round(auroc, 4),
        "auprc": round(auprc, 4),
        "sensitivity": round(sensitivity, 4),
        "specificity": round(specificity, 4),
        "precision": round(precision, 4),
        "f1": round(f1, 4),
        "brier_score": round(brier, 4),
        "ece": round(ece, 4),
        "false_positive_rate": round(fpr, 4),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn)
    }

def compute_expected_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Compute Expected Calibration Error (ECE) with equal-width probability bins."""
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n = len(y_true)
    if n == 0:
        return 0.0
        
    for i in range(n_bins):
        in_bin = (y_prob > bin_boundaries[i]) & (y_prob <= bin_boundaries[i + 1])
        prop_in_bin = np.mean(in_bin)
        if prop_in_bin > 0:
            acc_in_bin = np.mean(y_true[in_bin])
            conf_in_bin = np.mean(y_prob[in_bin])
            ece += np.abs(acc_in_bin - conf_in_bin) * prop_in_bin
            
    return float(ece)
