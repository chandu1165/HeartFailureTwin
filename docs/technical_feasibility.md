# Phase 0: Research Validation & Technical Feasibility Report

**Project**: HeartFailureTwin: A Personalized Multimodal Digital Twin for Early Forecasting of Heart-Failure Decompensation  
**Challenge**: Happiest Health Digital Twin Challenge  
**Date**: October 2026  
**Status**: VALIDATED & APPROVED  

---

## 1. Executive Summary & Challenge Alignment

The **HeartFailureTwin** project addresses heart failure (HF), a pervasive chronic condition with significant morbidity and mortality, particularly in India where heart failure affects patients at an earlier age (often a decade younger than in Western cohorts) and carries high readmission rates. 

Unlike generic "heart disease classification" models that output a static percentage, HeartFailureTwin formulates a **patient-specific computational Digital Twin** that continuously updates a latent physiological state vector \(S(t)\), measures personalized deviations from individual baselines, forecasts deterioration trajectories over a defined horizon, and provides transparent model attribution without making unsupported diagnostic claims.

| Challenge Requirement | Implementation in HeartFailureTwin | Status |
| :--- | :--- | :--- |
| **Chronic / Lifestyle Condition** | Heart Failure (HFrEF, HFpEF, ischemic & non-ischemic cardiomyopathy) | **Aligned** |
| **Historical EHR Data** | Demographics, NYHA class, BMI, hypertension, diabetes, CAD, CKD, baseline vitals | **Aligned** |
| **Dynamic Wearable / IoT Data** | Continuous Wearable ECG, tri-axial Seismocardiography (SCG), PPG/Pleth, Respiration, Temp | **Aligned** |
| **Digital Twin Concept** | Patient Profile + Dynamic Latent State \(S(t)\) + State Transition + Future Trajectory | **Aligned** |
| **Adverse Event Forecasting** | Acute physiological & clinical decompensation, hemodynamic congestion | **Aligned** |
| **Working Proof of Concept** | End-to-end reproducible pipeline with GroupKFold patient-level evaluation & benchmarks | **Aligned** |
| **Doctor-Facing Interface** | FastAPI backend + React/TypeScript Dashboard with Twin Replay, Timeline & What-If tools | **Aligned** |
| **Scientific Rigor & Ethics** | Zero patient leakage, clear data provenance, model explanation (not causal diagnosis) | **Aligned** |

---

## 2. Dataset Verification & Provenance

### 2.1 Primary Research Dataset: SCG-RHC Wearable Database
* **Source**: PhysioNet (Version 1.0.0, DOI: `10.13026/133d-pk11`, published March 2023).
* **Reference Publication**: Shandhi et al., *IEEE Transactions on Biomedical Engineering*, 69(8):2443–2455, 2022.
* **License**: Open Data Commons Attribution License v1.0 (ODC-By v1.0) — **Open Access**.
* **Cohort Overview**:
  * 73 unique heart failure patients (14 inpatients, 59 outpatients).
  * 83 total Right Heart Catheterization (RHC) procedures.
  * Synchronized continuous signals recorded at 500 Hz (WFDB Format 32):
    1. `patch_ECG`: Mid-sternum wearable patch ECG (mV)
    2. `patch_ACC_lat`: Wearable accelerometer lateral axis (mg)
    3. `patch_ACC_hf`: Head-to-foot axis (mg)
    4. `patch_ACC_dv`: Dorsal-ventral axis (mg) (SCG local mechanical vibration)
    5. `patch_Hum`: Humidity (%)
    6. `patch_Pre`: Pressure (mbar)
    7. `patch_Temp`: Skin temperature (°C)
    8. `ECG_lead_I`, `II`, `III`, `V1`: Multi-lead ECG (mV)
    9. `PLETH`: Photoplethysmogram / pulse oximetry (au)
    10. `RHC_pressure`: Direct invasive pulmonary catheter pressure (mmHg)
* **Cohort Demographics & Baseline Characteristics (Validated from Cohort Metadata)**:
  * Mean age: 55.5 years (range 26–84)
  * Gender: 24 Female (29%), 49 Male (71%)
  * NYHA Classification: NYHA I (6), NYHA II (16), NYHA III (52), NYHA IV (6)
  * Heart failure subtypes: HFrEF (78%), HFpEF (21%), OHT/transplant (6%)
  * Comorbidities: Hypertension (68%), Diabetes (35%), CAD (42%), CKD (28%)
* **Ground-Truth Target Labels**:
  * **Physiological Decompensation (`PDecomp`)**: 44 Compensated (53%), 39 Decompensated (47%) — **Well-balanced binary target**.
  * **Clinical Decompensation (`CDecomp`)**: 53 Compensated (64%), 30 Decompensated (36%).
  * **Invasive Hemodynamic Targets**: Mean Pulmonary Artery Pressure (`PAM`), PCWP (`PCWM`), Cardiac Output (`CO`), Stroke Volume (`SV`).

### 2.2 Secondary / Longitudinal Synthetic Cohort
To showcase multi-day continuous home-monitoring, **Twin Replay**, and **What-If simulation**, a synthetically generated longitudinal stream is constructed using empirical distributions drawn from the real SCG-RHC cohort and clinical HF literature.
* **Labeling Rule**: All simulated patient streams are explicitly marked as `DATA_PROVENANCE: SYNTHETIC_SIMULATION`. No synthetic stream is ever merged or reported as real clinical validation data.

---

## 3. Machine Learning Models & Licensing

| Model Family | Model / Architecture | Repository / License | Purpose in HeartFailureTwin |
| :--- | :--- | :--- | :--- |
| **Baselines** | Logistic Regression, Random Forest | scikit-learn (BSD-3) | Primary benchmark against non-personalized approaches |
| **Gradient Boosting** | XGBoost 3.2 | XGBoost (Apache 2.0) | High-performance tabular & window-feature baseline |
| **Recurrent Temporal** | GRU / LSTM | PyTorch 2.x (BSD-3) | Temporal baseline modeling physiological trends |
| **ECG Foundation** | ECG-FM / ECGFounder | Public Research Checkpoints | Frozen representations for ECG waveforms |
| **Digital Twin Engine** | Latent State Space Model \(S(t)\) | Custom PyTorch Architecture | Personalization, state transition, and future trajectory forecasting |

---

## 4. Methodological Rigor & Data Leakage Prevention

### 4.1 Strict Patient-Level Splitting
* **CRITICAL RULE**: All temporal windows and recordings from a single patient belong exclusively to either Train, Validation, or Test. Random window splitting across the cohort is strictly forbidden.
* **Validation Strategy**: 5-Fold GroupKFold partitioned by `patient_id` (73 groups).

### 4.2 Leakage Audit Protocol
* Feature extraction at timestamp \(t\) uses strictly historical observations \([t - W, t]\).
* Future measurements, post-procedural outcomes, and future hemodynamic interventions (e.g. Nipride/Nitro challenge timestamps) are masked prior to prediction time.
* Patient baselines \(\mu_i, \sigma_i\) are computed strictly on initial resting/baseline observation windows.

---

## 5. Evaluation Metrics

1. **Discrimination**:
   * Area Under ROC Curve (**AUROC**)
   * Area Under Precision-Recall Curve (**AUPRC**) — essential given clinical class imbalance.
2. **Clinical Utility & Classification**:
   * Sensitivity (Recall at fixed 90% target), Specificity, Precision, F1-Score.
3. **Calibration**:
   * Brier Score, Expected Calibration Error (ECE).
4. **Early Warning Metric**:
   * **Lead Time**: Time delta \(\Delta T\) between initial sustained Twin alert and recorded decompensation event.

---

## 6. Computational Feasibility & Resource Allocation

* **Execution Environment**: Windows x64, Python 3.11.16, PyTorch 2.14 CPU, XGBoost 3.2.
* **Strategy**:
  * Utilize pre-extracted WFDB window features and frozen representation vectors to avoid excessive multi-day GPU training overhead while retaining reproducibility and rapid inference.
  * Process an initial representative cohort of WFDB records (balanced across compensated and decompensated cases), scale to the full cohort, and run cross-validation seamlessly.
  * The FastAPI backend and React frontend are architected for lightweight, responsive execution.

---

## 7. Approval & Phase Transition

Phase 0 validation criteria are completely satisfied:
- [x] Challenge requirements and Indian clinical context defined
- [x] SCG-RHC database access verified via WFDB and metadata confirmed
- [x] Binary targets (`PDecomp`, `CDecomp`) and hemodynamic targets verified
- [x] Zero-leakage GroupKFold patient-level partitioning protocol established
- [x] Model licensing and dependency matrix cleared
- [x] Phase 1 implementation ready to proceed
