"""Patient-level cross-validation and split manager.
Enforces ZERO data leakage by ensuring all windows from any patient belong strictly to a single partition.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from typing import Generator, Tuple, List, Dict, Any

def create_patient_level_kfold(
    df: pd.DataFrame,
    patient_col: str = "patient_id",
    target_col: str = "label_pdecomp",
    n_splits: int = 5,
    random_state: int = 42
) -> List[Dict[str, Any]]:
    """Generate k-fold splits grouped by patient_id with zero-leakage verification.
    
    Returns:
        List of dicts for each fold with:
            - 'fold': int
            - 'train_indices': np.ndarray
            - 'val_indices': np.ndarray
            - 'train_patients': set
            - 'val_patients': set
            - 'train_cases': (n_pos, n_neg)
            - 'val_cases': (n_pos, n_neg)
    """
    assert patient_col in df.columns, f"Missing patient column: {patient_col}"
    assert target_col in df.columns, f"Missing target column: {target_col}"
    
    # Drop rows where target is NaN
    valid_df = df.dropna(subset=[target_col]).copy()
    valid_indices = valid_df.index.to_numpy()
    groups = valid_df[patient_col].to_numpy()
    y = valid_df[target_col].to_numpy()
    
    unique_patients = np.unique(groups)
    actual_splits = min(n_splits, len(unique_patients))
    if actual_splits < n_splits:
        print(f"Warning: Only {len(unique_patients)} unique patients available. Reducing folds to {actual_splits}.")
        
    gkf = GroupKFold(n_splits=actual_splits)
    folds = []
    
    for fold_idx, (train_idx_rel, val_idx_rel) in enumerate(gkf.split(valid_df, y, groups)):
        train_idx = valid_indices[train_idx_rel]
        val_idx = valid_indices[val_idx_rel]
        
        train_pts = set(valid_df.loc[train_idx, patient_col].unique())
        val_pts = set(valid_df.loc[val_idx, patient_col].unique())
        
        # Rigorous Zero-Leakage Verification
        overlap = train_pts.intersection(val_pts)
        assert len(overlap) == 0, f"DATA LEAKAGE DETECTED! Patient overlap in Fold {fold_idx}: {overlap}"
        
        y_train = valid_df.loc[train_idx, target_col].to_numpy()
        y_val = valid_df.loc[val_idx, target_col].to_numpy()
        
        fold_info = {
            "fold": fold_idx,
            "train_indices": train_idx,
            "val_indices": val_idx,
            "train_patients": train_pts,
            "val_patients": val_pts,
            "train_pos": int(np.sum(y_train == 1)),
            "train_neg": int(np.sum(y_train == 0)),
            "val_pos": int(np.sum(y_val == 1)),
            "val_neg": int(np.sum(y_val == 0))
        }
        folds.append(fold_info)
        
    return folds

def print_split_summary(folds: List[Dict]):
    """Print readable validation summary across folds."""
    print(f"\n{'='*20} PATIENT-LEVEL ZERO-LEAKAGE SPLIT SUMMARY {'='*20}")
    for f in folds:
        print(f"Fold {f['fold']}:")
        print(f"  Train: {len(f['train_indices']):4d} windows across {len(f['train_patients']):2d} patients | Pos={f['train_pos']:2d}, Neg={f['train_neg']:2d}")
        print(f"  Val:   {len(f['val_indices']):4d} windows across {len(f['val_patients']):2d} patients | Pos={f['val_pos']:2d}, Neg={f['val_neg']:2d}")
    print(f"{'='*68}\n")
