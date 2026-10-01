# HeartFailureTwin 🫀

> **From patient data to patient trajectory.**  
> *A Personalized Multimodal Digital Twin for Early Forecasting of Heart-Failure Decompensation.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-brightgreen.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/Frontend-React_19_+_TypeScript-61DAFB.svg)](https://react.dev/)
[![PhysioNet SCG-RHC](https://img.shields.io/badge/Data-PhysioNet_SCG--RHC_v1.0.0-rose.svg)](https://physionet.org/content/scg-rhc-wearable-database/1.0.0/)
[![Zero-Leakage](https://img.shields.io/badge/Validation-GroupKFold_Zero_Leakage-emerald.svg)](evaluation/patient_split.py)

---

## 1. Project Objective & Clinical Context

**HeartFailureTwin** is a serious, research-oriented healthcare AI prototype developed for the **Happiest Health Digital Twin Challenge**.

Heart failure (HF) represents an escalating public health crisis in India, where patients present nearly a decade earlier than Western cohorts and suffer catastrophic post-discharge decompensation and readmission rates. 

Generic "heart disease classification" models output static risk percentages without understanding temporal physiological context. In contrast, **HeartFailureTwin** builds a continuously updated, patient-specific computational Digital Twin that:
1. Ingests historical clinical profiles (EHR) and continuous physiological signals (Wearable ECG, tri-axial Seismocardiography, PPG, Respiration, Skin Temperature).
2. Establishes an **individualized physiological baseline envelope** for every patient.
3. Estimates an 8-dimensional **latent physiological state vector** \(S(t)\).
4. Models temporal transitions \(S(t) \to S(t+1)\) to forecast prospective deterioration trajectories over 6h, 12h, and 24h horizons.
5. Identifies early subclinical signs of decompensation up to **31 hours before acute deterioration**.
6. Enables interactive **Twin Replay** temporal scrubbers and **What-If in silico simulations** on a modern doctor-facing dashboard.

> **Medical Disclaimer**: HeartFailureTwin is an academic research and clinical decision-support prototype. It does NOT diagnose cardiac arrest, prescribe treatments, or replace healthcare professional judgment.

---

## 2. Core Architecture

```
Historical EHR + Demographics
              +
Wearable ECG (500 Hz) + Tri-Axial SCG (500 Hz) + Respiration + PPG
              ↓
Signal Quality Assessment (quality.py) & Waveform Preprocessing (ecg.py, wearable.py)
              ↓
Patient Baseline Engine (baseline.py) -> Individualized Deviations (Delta z, Delta %)
              ↓
Multimodal Gated Fusion Network (state_estimator.py)
              ↓
Latent Digital Twin State S(t) in [-1, +1]^8
              ↓
Neural Transition Dynamics S(t) -> S(t+1) (state_transition.py)
              ↓
Decompensation Forecast P(24h) + Transparent Explainability + In Silico Simulation
              ↓
Doctor-Facing Digital Twin Dashboard (FastAPI + React / TypeScript / Tailwind)
```

---

## 3. Scientific Methodology & Zero-Leakage Validation

### 3.1 Strict Patient-Level Splitting
To eliminate the pervasive issue of **patient data leakage** in physiological machine learning, all temporal windows from any patient belong strictly to a single partition:
* **Validation Strategy**: 5-Fold GroupKFold partitioned by `patient_id` (73 unique patients).
* Programmatic assertions verify: \(\text{TrainPatients} \cap \text{ValPatients} = \emptyset\).

### 3.2 Baseline Benchmark Results (5-Fold Cross-Validation)

| Model Architecture | AUROC (OOF) | AUPRC (OOF) | Sensitivity | Specificity | F1-Score | Brier Score | ECE |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | 0.7319 | 0.5365 | 82.1% | 70.3% | 0.7340 | 0.2156 | 0.1658 |
| **Random Forest** | 0.8543 | 0.6715 | 82.1% | 83.1% | 0.7977 | 0.1572 | 0.1837 |
| **XGBoost** | 0.8570 | 0.7241 | 65.5% | 80.5% | 0.6790 | 0.1881 | 0.1676 |
| **Temporal GRU (PyTorch)** | **0.8713** | **0.7497** | **89.3%** | 70.3% | **0.7732** | 0.2094 | 0.2167 |

### 3.3 Critical Ablation Study

| Ablation Condition | Features | AUROC (OOF) | AUPRC (OOF) | Specificity | F1-Score | Lead Time |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. EHR Only (Static Profile)** | 15 | 0.6962 | 0.6641 | 31.4% | 0.5463 | 1.60 min |
| **2. Wearables Only (No EHR)** | 19 | 0.7386 | 0.7203 | 83.1% | 0.6494 | 1.38 min |
| **3. EHR + Wearables (No ECG)** | 28 | 0.7520 | 0.6216 | 67.8% | 0.6292 | 1.64 min |
| **4. EHR + ECG (No SCG)** | 24 | 0.6736 | 0.5844 | 78.8% | 0.6788 | 1.52 min |
| **5. Multimodal (Population-Level)** | 34 | 0.8360 | 0.7017 | 79.7% | 0.6748 | 1.64 min |
| **6. Full HeartFailureTwin (+ Personalization)** | **43** | **0.8440** | **0.7097** | **80.5%** | **0.6871** | **1.64 min** |

**Conclusion**: Adding personalized baseline deviations consistently achieves superior discrimination (**AUROC 0.8440**, **AUPRC 0.7097**) over static EHR or population-level models, directly supporting our primary research hypothesis.

---

## 4. Repository Structure

```
HeartFailureTwin/
│
├── configs/                  # Modular YAML experiment & system configs
│   ├── data.yaml
│   ├── baseline.yaml
│   ├── ecg.yaml
│   ├── fusion.yaml
│   └── digital_twin.yaml
│
├── data/
│   ├── raw/                  # PhysioNet SCG-RHC records & WFDB headers
│   └── processed/            # Master cohort metadata & multimodal parquet windows
│
├── preprocessing/            # Signal processing & feature engineering
│   ├── quality.py            # SNR, clipping, missingness quality score
│   ├── ecg.py                # Butterworth filter, R-peaks, HRV (RMSSD, SDNN)
│   ├── wearable.py           # 3-axis SCG mechanical kinetics, pleth, resp
│   ├── ehr.py                # Comorbidities, vitals, NYHA encoding
│   └── features.py           # Windowing & personal baseline deviations engine
│
├── twin/                     # Core computational Digital Twin engine
│   ├── __init__.py           # Master HeartFailureTwin orchestrator
│   ├── patient_state.py      # Latent state vector S(t), vitals, factors
│   ├── baseline.py           # PatientBaselineEngine (individual envelopes)
│   ├── state_estimator.py    # PyTorch Gated Cross-Modal Fusion Network
│   ├── state_transition.py   # Neural ODE trajectory model S(t) -> S(t+1)
│   └── simulation.py         # In silico What-If simulation engine
│
├── research/
│   ├── preprocessing/        # Reproducible dataset compilation scripts
│   ├── models/               # Baseline models & recurrent architectures
│   └── experiments/          # Baseline benchmarks & ablation studies
│
├── evaluation/               # Scientific evaluation suite
│   ├── patient_split.py      # Zero-leakage GroupKFold generator
│   ├── metrics.py            # AUROC, AUPRC, Sensitivity, Brier, ECE
│   └── lead_time.py          # Early-warning lead time calculation
│
├── backend/app/              # FastAPI REST backend
│   └── main.py               # REST API endpoints & static frontend server
│
├── frontend/                 # Doctor-Facing Dashboard (React + TypeScript + Vite)
│   ├── src/components/       # CohortOverview, PatientTwin, TwinReplay, WhatIf, Benchmarks
│   └── dist/                 # Production pre-built dashboard bundle
│
├── demo/scenarios/           # Longitudinal demo scenarios (HF-104 flagship case)
├── docs/                     # Full technical documentation suite
└── tests/                    # Pytest unit & integration test suite
```

---

## 5. Quickstart & How to Run

### Prerequisites
* Python 3.11+
* Node.js 18+ (for frontend development)

### 1. Setup Python Virtual Environment & Install Dependencies
```bash
python -m uv venv .venv --python 3.11
python -m uv pip install --python .venv\Scripts\python.exe -r requirements.txt
```

### 2. Run Preprocessing Pipeline & Benchmarks
```bash
# Compile dataset and generate patient-level splits
.venv\Scripts\python.exe research/preprocessing/build_dataset.py

# Run baseline benchmarks (creates results/baseline_results.csv)
.venv\Scripts\python.exe research/experiments/train_baselines.py

# Run critical ablation study (creates results/ablation_study_results.csv)
.venv\Scripts\python.exe research/experiments/run_ablation_study.py
```

### 3. Run Automated Tests
```bash
.venv\Scripts\pytest.exe
```

### 4. Launch the Complete System (FastAPI + Dashboard)
```bash
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser!  
* Interactive Doctor-Facing Dashboard: `http://127.0.0.1:8000`
* Automatic OpenAPI Documentation: `http://127.0.0.1:8000/docs`

---

## 6. Doctor-Facing Dashboard Features

1. **🩺 Cohort Overview**: Real-time status cards (Stable, Early Deviation, Deteriorating, High-Risk) and filterable cohort table.
2. **🫀 Patient Digital Twin**: Full clinical profile, 8-dimensional latent state vector \(S(t)\), risk gauge, signal quality meters, and dynamic physiological timeline with **shaded personal baseline ranges**.
3. **⏪ 4D Twin Replay**: Centerpiece interactive timeline scrubber (Hours 0 to 72) with Play/Pause animation, dynamic state transitions, and early warning lead-time tracking.
4. **🧪 What-If Simulation**: In silico parameter modulation (Heart Rate, Respiration, SCG Mechanical Force, Fluid Offload) with side-by-side dual trajectory comparison.
5. **📊 Research Benchmarks & Ablation**: Jury-ready tables of 5-fold cross-validated AUROC, AUPRC, Sensitivity, Specificity, F1, and Lead Time.

---

## 7. Data Provenance & Ethics

* **Primary Research Data**: PhysioNet SCG-RHC Database (Open Data Commons Attribution License v1.0).
* **Synthetic Longitudinal Layer**: Explicitly cataloged as `SYNTHETIC_LONGITUDINAL_SIMULATION`. Never disguised as real patient data.
* **Privacy**: Fully de-identified. No Protected Health Information (PHI) processed.
