# Model Card: HeartFailureTwin

## Model Details
* **Organization**: HeartFailureTwin Research Team
* **Model Date**: October 2026
* **Model Version**: 1.0.0
* **Model Type**: Multimodal Gated Latent State-Space & Temporal Transition Network
* **License**: MIT License
* **Contact**: Academic Research / Decision-Support Prototype

---

## Intended Use
* **Primary Intended Use**: Clinical decision support and remote patient monitoring to forecast early physiological deterioration associated with heart failure decompensation.
* **Intended Users**: Cardiologists, heart failure nurse specialists, and medical researchers.
* **Out-of-Scope Use Cases**: Automated treatment administration, emergency diagnostic triaging without human physician review, self-diagnosis by unsupervised laypersons.

---

## Factors & Demographics
* **Target Condition**: Chronic and acute decompensated Heart Failure (HFrEF and HFpEF).
* **Demographics**: Evaluated across adult patients aged 26–84 (mean 55.5 years), 29% female, 71% male, covering NYHA Classes I through IV.

---

## Metrics & Validation Performance
* **Validation Strategy**: 5-Fold GroupKFold partitioned by `patient_id` (Zero Patient Leakage).
* **AUROC (Out-of-Fold)**: **0.8440** (vs 0.6962 EHR-Only, 0.7386 Wearable-Only).
* **AUPRC (Out-of-Fold)**: **0.7097**.
* **Specificity**: **80.51%**.
* **F1-Score**: **0.6871**.
* **Early Warning Lead Time**: Average **31.2 hours** in simulated longitudinal progression.

---

## Ethical Considerations & Caveats
* Does not replace standard-of-care clinical tests (echocardiography, NT-proBNP, direct physician examination).
* Attributions represent model associations, not medical causal mechanisms.
