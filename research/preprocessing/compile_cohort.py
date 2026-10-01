"""Compile all 83 JSON metadata records and merge with RHC_values.csv into a unified cohort table.
"""
import json
import re
from pathlib import Path
import pandas as pd
import numpy as np

DATA_DIR = Path("data/raw/processed_data")
META_DIR = Path("data/raw/meta_information")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def parse_patient_id(rec_name):
    # e.g., TRM128-RHC1 -> patient_id: TRM128, procedure_id: RHC1
    match = re.match(r"(TRM\d+)-(RHC\d+)", rec_name)
    if match:
        return match.group(1), match.group(2)
    return rec_name, "RHC1"

def main():
    rows = []
    json_files = sorted(list(DATA_DIR.glob("*.json")))
    print(f"Found {len(json_files)} JSON files.")

    for jf in json_files:
        rec_name = jf.stem
        patient_id, proc_id = parse_patient_id(rec_name)
        with open(jf, "r") as f:
            d = json.load(f)

        # Extract top-level fields
        row = {
            "record_id": rec_name,
            "patient_id": patient_id,
            "procedure_id": proc_id,
            "age": d.get("age"),
            "gender": d.get("gender"),
            "height_cm": d.get("height"),
            "weight_kg": d.get("weight"),
            "sbp": d.get("sbp"),
            "dbp": d.get("dbp"),
            "history": d.get("history of patient"),
            "CDecomp": d.get("CDecomp"), # Clinical decompensation
            "PDecomp": d.get("PDecomp"), # Physiological decompensation
            "NYHAC": d.get("NYHAC"),
            "outpatient": d.get("outpatient"),
            "heart_failure": d.get("heart failure"),
            "fine_alignment": d.get("fine_alignment"),
            "missing_maclab": d.get("Missing_MaclabRHC"),
            "dev_loc": d.get("DevLoc")
        }

        # Calculate BMI
        if row["height_cm"] and row["weight_kg"]:
            try:
                h_m = float(row["height_cm"]) / 100.0
                w_kg = float(row["weight_kg"])
                if h_m > 0:
                    row["bmi"] = round(w_kg / (h_m ** 2), 2)
            except (ValueError, TypeError):
                row["bmi"] = np.nan
        else:
            row["bmi"] = np.nan

        # Parse conditions from history text
        hist_text = str(row["history"]).upper() if row["history"] else ""
        row["hist_htn"] = int("HTN" in hist_text or "HYPERTENSION" in hist_text)
        row["hist_dm"] = int("DM" in hist_text or "DIABETES" in hist_text)
        row["hist_cad"] = int("CAD" in hist_text or "CORONARY" in hist_text)
        row["hist_hfref"] = int("HFREF" in hist_text)
        row["hist_hfpef"] = int("HFPEF" in hist_text)
        row["hist_ckd"] = int("CKD" in hist_text or "RENAL" in hist_text)
        row["hist_oht"] = int("OHT" in hist_text or "TRANSPLANT" in hist_text)

        # Mac-Lab hemodynamics measurements if present in json
        maclab = d.get("maclabMeas", {})
        if isinstance(maclab, dict):
            for k, v in maclab.items():
                clean_k = re.sub(r"[^a-zA-Z0-9_]", "_", k.strip().lower())
                row[f"meas_{clean_k}"] = v

        # Read signal length from .hea
        hea_file = DATA_DIR / f"{rec_name}.hea"
        if hea_file.exists():
            with open(hea_file, "r") as hf:
                first_line = hf.readline().strip().split()
                if len(first_line) >= 4:
                    row["num_channels"] = int(first_line[1])
                    row["sampling_rate"] = int(first_line[2])
                    row["num_samples"] = int(first_line[3])
                    row["duration_sec"] = round(int(first_line[3]) / int(first_line[2]), 1)

        rows.append(row)

    df_cohort = pd.DataFrame(rows)
    print(f"Cohort DataFrame created: {df_cohort.shape[0]} rows, {df_cohort.shape[1]} columns.")
    print(f"Unique patients: {df_cohort['patient_id'].nunique()}")

    # Merge with RHC_values.csv for ground-truth hemodynamics and physiological score
    rhc_csv = META_DIR / "RHC_values.csv"
    if rhc_csv.exists():
        df_rhc = pd.read_csv(rhc_csv)
        # Rename Study ID to standard format TRMXXX-RHCY
        df_rhc["record_id"] = df_rhc["Study ID"].str.replace(".", "-", regex=False)
        # Filter for baseline or unique records
        df_rhc_baseline = df_rhc[df_rhc["RHC Phase"] == "Baseline"].copy()
        
        # Select key columns
        rhc_cols_to_merge = [
            "record_id", "Physiological Score", "Classification",
            "PAS", "PAD", "PAM", "PAHR",
            "PCWA Wave", "PCWV Wave", "PCWM", "PCWHR",
            "Avg. COmL/min", "SVmL/beat", "TDCIL/min/m^2"
        ]
        available_cols = [c for c in rhc_cols_to_merge if c in df_rhc_baseline.columns]
        df_rhc_sub = df_rhc_baseline[available_cols].drop_duplicates(subset=["record_id"])
        
        df_merged = pd.merge(df_cohort, df_rhc_sub, on="record_id", how="left")
    else:
        df_merged = df_cohort

    # Clean numeric columns and mixed types
    for col in df_merged.columns:
        if col.startswith("meas_") or col in ["PAS", "PAD", "PAM", "PAHR", "PCWA Wave", "PCWV Wave", "PCWM", "PCWHR", "Avg. COmL/min", "SVmL/beat", "TDCIL/min/m^2", "age", "height_cm", "weight_kg", "sbp", "dbp"]:
            # Convert string numbers to float, replacing 'N/A', 'na', etc. with NaN
            df_merged[col] = pd.to_numeric(df_merged[col].replace(["N/A", "na", "NaN", ""], np.nan), errors="coerce")
        elif df_merged[col].dtype == object:
            # Ensure text columns are all string type to avoid arrow mixed-type issues
            df_merged[col] = df_merged[col].astype(str).replace(["nan", "None"], "")

    # Save to parquet and csv
    out_parquet = OUT_DIR / "cohort_metadata.parquet"
    out_csv = OUT_DIR / "cohort_metadata.csv"
    df_merged.to_parquet(out_parquet, index=False)
    df_merged.to_csv(out_csv, index=False)
    print(f"Saved merged cohort metadata to:\n  {out_parquet}\n  {out_csv}")

    # Summary stats
    print("\n=== SUMMARY STATISTICS ===")
    print(f"Total Procedures: {len(df_merged)}")
    print(f"Unique Patients: {df_merged['patient_id'].nunique()}")
    print("Clinical Decompensation (CDecomp):")
    print(df_merged["CDecomp"].value_counts(dropna=False))
    print("Physiological Decompensation (PDecomp):")
    print(df_merged["PDecomp"].value_counts(dropna=False))
    if "Physiological Score" in df_merged.columns:
        print("RHC Physiological Score:")
        print(df_merged["Physiological Score"].value_counts(dropna=False))
    print("NYHA Functional Class:")
    print(df_merged["NYHAC"].value_counts(dropna=False))

if __name__ == "__main__":
    main()
