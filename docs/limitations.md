# HeartFailureTwin: Clinical Limitations & Ethical Boundaries

## 1. Prototype Positioning & Medical Boundaries

HeartFailureTwin is an academic research and clinical decision-support proof of concept. It has **NOT** received FDA, CE mark, or CDSCO medical device clearance.

### Explicit Prohibitions:
1. **NOT a Diagnostic Device**: The system does NOT diagnose cardiac arrest, myocardial infarction, acute pulmonary edema, or cardiogenic shock.
2. **NOT a Prescriptive System**: The system does NOT prescribe diuretics, inotropes, beta-blockers, or any pharmaceutical dosage adjustments.
3. **NOT a Physician Replacement**: HeartFailureTwin outputs computational states intended exclusively to prioritize clinical review by certified cardiologists and healthcare teams.
4. **NO Guarantee of Prevention**: A "Stable" computational state does not guarantee absence of future adverse events.

---

## 2. Technical & Data Limitations

### 2.1 Dataset Scale
* The primary experimental validation is conducted on the 73-patient PhysioNet SCG-RHC database. While this is the premier public dataset featuring simultaneous synchronized invasive hemodynamics and chest-worn mechanocardiography, larger multi-center cohorts (e.g. >10,000 patients) are required for full clinical deployment.

### 2.2 In-Hospital Catheter vs Longitudinal Ambient Wear
* Catheterization laboratory recordings capture acutely monitored patients during procedural maneuvers. Ambient home-monitoring encounters daily noise factors including ambulation, speech, posture shifts, and sensor misplacement.
* HeartFailureTwin introduces an explicit signal-quality assessment module (`quality.py`) to gate noisy windows, but further clinical validation in free-living environments is necessary.

### 2.3 Non-Causal Nature of Explainability
* Model-associated factors (e.g. "Resting Heart Rate Elevation", "Mechanical SCG Force Decline") indicate statistical correlations detected within the feature space. They must never be presented to clinicians as proven physiological causes of decompensation.

---

## 3. Patient Privacy & Safety Protections

* All data utilized in HeartFailureTwin is derived from fully de-identified open research repositories (PhysioNet) or generated as synthetic computational demonstrations.
* No Protected Health Information (PHI) or Personally Identifiable Information (PII) is processed or stored.
