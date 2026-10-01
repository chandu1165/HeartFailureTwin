"""EHR and Clinical Profile feature engineering module.
Parses demographics, comorbidities, vitals, and laboratory/hemodynamic profiles.
"""
import pandas as pd
import numpy as np

def extract_ehr_features(row: dict) -> dict:
    """Extract standardized clinical, demographic, and risk-stratification features from a patient record."""
    age = float(row.get("age", np.nan)) if row.get("age") is not None else np.nan
    gender_male = 1.0 if str(row.get("gender", "")).lower() in ["male", "m", "1"] else 0.0
    
    # Body metrics
    height_cm = float(row.get("height_cm", np.nan)) if row.get("height_cm") is not None else np.nan
    weight_kg = float(row.get("weight_kg", np.nan)) if row.get("weight_kg") is not None else np.nan
    bmi = float(row.get("bmi", np.nan)) if row.get("bmi") is not None else np.nan
    if np.isnan(bmi) and not np.isnan(height_cm) and not np.isnan(weight_kg) and height_cm > 50:
        bmi = round(weight_kg / ((height_cm / 100.0) ** 2), 2)
        
    # Baseline Blood Pressures & Hemodynamics
    sbp = float(row.get("sbp", np.nan)) if row.get("sbp") is not None else np.nan
    dbp = float(row.get("dbp", np.nan)) if row.get("dbp") is not None else np.nan
    
    pulse_pressure = np.nan
    map_pressure = np.nan
    if not np.isnan(sbp) and not np.isnan(dbp):
        pulse_pressure = round(sbp - dbp, 2)
        map_pressure = round(dbp + (sbp - dbp) / 3.0, 2)
        
    # Functional & Clinical Status
    nyha = float(row.get("NYHAC", 2.0)) if row.get("NYHAC") is not None else 2.0
    
    # Comorbidity indicators
    hist_htn = float(row.get("hist_htn", 0.0))
    hist_dm = float(row.get("hist_dm", 0.0))
    hist_cad = float(row.get("hist_cad", 0.0))
    hist_ckd = float(row.get("hist_ckd", 0.0))
    hist_hfref = float(row.get("hist_hfref", 1.0))
    hist_hfpef = float(row.get("hist_hfpef", 0.0))
    hist_oht = float(row.get("hist_oht", 0.0))
    
    # Prior hospitalization / outpatient flag
    outpatient = 1.0 if str(row.get("outpatient", "")).lower() in ["true", "1", "yes"] else 0.0

    return {
        "ehr_age": age,
        "ehr_gender_male": gender_male,
        "ehr_weight_kg": weight_kg,
        "ehr_height_cm": height_cm,
        "ehr_bmi": bmi,
        "ehr_sbp": sbp,
        "ehr_dbp": dbp,
        "ehr_pulse_pressure": pulse_pressure,
        "ehr_map": map_pressure,
        "ehr_nyha": nyha,
        "ehr_htn": hist_htn,
        "ehr_dm": hist_dm,
        "ehr_cad": hist_cad,
        "ehr_ckd": hist_ckd,
        "ehr_hfref": hist_hfref,
        "ehr_hfpef": hist_hfpef,
        "ehr_oht": hist_oht,
        "ehr_outpatient": outpatient
    }
