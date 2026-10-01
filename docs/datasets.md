# HeartFailureTwin: Dataset Documentation & Provenance

## 1. Multi-Source Transparent Data Strategy

In accordance with strict clinical AI governance principles, HeartFailureTwin adheres to an explicit data provenance protocol. Every data source in the system is clearly cataloged under one of two designations:
1. `REAL_PHYSIONET_SCG_RHC`: Real open physiological research database.
2. `SYNTHETIC_LONGITUDINAL_SIMULATION`: Clearly labeled computational simulation derived from real empirical distributions.

Synthetic data is never combined or reported as real clinical evidence.

---

## 2. Primary Research Dataset: SCG-RHC

* **Full Title**: SCG-RHC: Wearable Seismocardiogram Signal and Right Heart Catheter Database
* **Version**: 1.0.0 (Published March 31, 2023)
* **PhysioNet Link**: [https://physionet.org/content/scg-rhc-wearable-database/1.0.0/](https://physionet.org/content/scg-rhc-wearable-database/1.0.0/)
* **DOI**: `10.13026/133d-pk11`
* **License**: Open Data Commons Attribution License v1.0 (ODC-By v1.0)
* **Citation**: Chan, M., Klein, L., Fan, J., & Inan, O. (2023). SCG-RHC: Wearable Seismocardiogram Signal and Right Heart Catheter Database. PhysioNet.

### 2.1 Database Overview
* **Cohort Size**: 73 unique heart failure patients (14 inpatients, 59 outpatients).
* **Procedures**: 83 synchronized Right Heart Catheterization (RHC) recordings.
* **Sampling Rate**: 500 Hz (WFDB Format 32).
* **Total Signal Channels**: 16 channels:
  * `patch_ECG`: Mid-sternum wearable patch ECG (mV)
  * `patch_ACC_lat`: Lateral axis accelerometry (mg)
  * `patch_ACC_hf`: Head-to-foot axis accelerometry (mg)
  * `patch_ACC_dv`: Dorso-ventral axis accelerometry (mg, Seismocardiography)
  * `patch_Hum`: Sensor humidity (%)
  * `patch_Pre`: Ambient barometric pressure (mbar)
  * `patch_Temp`: Skin surface temperature (°C)
  * `ECG_lead_I`, `II`, `III`, `V1`: Multi-lead ECG (mV)
  * `PLETH`: Photoplethysmogram / pulse oximetry (au)
  * `RHC_pressure`: Invasive Right Heart Catheter blood pressure (mmHg)

### 2.2 Clinical & Ground-Truth Labels
* **Physiological Decompensation (`PDecomp`)**:
  * 0 = Compensated (44 cases, 53%)
  * 1 = Decompensated (39 cases, 47%)
* **Clinical Decompensation (`CDecomp`)**:
  * 0 = Compensated (53 cases, 64%)
  * 1 = Decompensated (30 cases, 36%)
* **Invasive Hemodynamic Parameters**:
  * Pulmonary Artery Pressure Mean (`PAM`), Systolic (`PAS`), Diastolic (`PAD`)
  * Pulmonary Capillary Wedge Pressure Mean (`PCWM`)
  * Cardiac Output (`Avg. COmL/min`), Cardiac Index (`TDCIL/min/m^2`), Stroke Volume (`SVmL/beat`)
* **New York Heart Association (NYHA) Class**:
  * Class I (6), Class II (16), Class III (52), Class IV (6)

---

## 3. Secondary Longitudinal Simulation Layer

Because in-hospital catheterization datasets measure hours rather than weeks of continuous data, an explicit synthetic simulation layer is generated to demonstrate multi-day home-monitoring, **Twin Replay**, and **What-If simulation**:

* **Patient HF-104 (Flagship Decompensation Case)**:
  * Profile: 64-year-old male, NYHA III, HFrEF (EF 28%), Hypertension, CAD.
  * Timeline: 72 continuous monitoring hours spanning 5 stages:
    1. Hours 0–24: Compensated resting baseline (HR 70–74 bpm, SCG 21–23 mg).
    2. Hours 24–42: Subclinical autonomic shift (HR rising, HRV RMSSD dropping).
    3. Hours 42–60: Progressive deterioration (Tachypnea 21 bpm, fluid gain +2.4 kg, SCG contractility dropping).
    4. Hours 60–72: High-risk impending decompensation (Risk > 80%, sustained alert).
* **Patient HF-201 (Stable Outpatient Case)**:
  * Profile: 58-year-old female, NYHA II, HFpEF, Hypertension, Diabetes.
  * Timeline: 72 continuous monitoring hours consistently remaining within the personal baseline envelope (Risk < 20%).
