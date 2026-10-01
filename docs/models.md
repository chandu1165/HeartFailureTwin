# HeartFailureTwin: Model Architecture & Foundation Models

## 1. Overview of Evaluated Models

HeartFailureTwin implements and benchmarks a hierarchical progression of models:

```
Tier 1: Classical Baselines (Logistic Regression, Random Forest, XGBoost)
   ↓
Tier 2: Temporal Recurrent Models (PyTorch GRU)
   ↓
Tier 3: Foundation Model Representations (ECG-FM / ECGFounder Frozen Vectors)
   ↓
Tier 4: Multimodal Digital Twin Latent State Space (MultimodalStateEstimator + Neural ODE Transition)
```

---

## 2. Foundation Models Investigation

### 2.1 ECG Foundation Models Summary Table

| Model | Repository | License | Input Channels | Pretraining Dataset | Parameters | Output Representation | Notes in HeartFailureTwin |
| :--- | :--- | :--- | :---: | :--- | :---: | :--- | :--- |
| **ECG-FM** | [bowang-lab/ECG-FM](https://github.com/bowang-lab/ECG-FM) | Apache 2.0 | 12-lead / Single-lead | MIMIC-IV-ECG & PhysioNet 2021 | 90.9M | 768-dim temporal sequence | **Primary candidate**; utilized as frozen embedding extractor to minimize compute |
| **ECGFounder** | [PKUDigitalHealth/ECGFounder](https://github.com/PKUDigitalHealth/ECGFounder) | Open Research | 12-lead | 10M+ ECG waveforms | 85M | 512-dim feature vector | Comparison candidate |
| **HuBERT-ECG** | Open Community | MIT | Multi-lead | PhysioNet Challenge | 95M | Latent speech-style tokens | Complex tokenization overhead |
| **MOMENT** | AutonLab / CMU | MIT | Multivariate Time-Series | Diverse multivariate benchmarks | 385M | Patch embeddings | Evaluated for multivariate sensor sequences |

### 2.2 Frozen Representation Strategy
To prevent prohibitive multi-day GPU training and maintain hackathon reproducibility on standard hardware:
1. Foundation model weights are maintained **strictly frozen**.
2. Waveform segments are passed through the encoder to extract dense representation vectors.
3. Dense embeddings are fused with structured EHR and personalized baseline deviation vectors.

---

## 3. The Digital Twin State Model

### 3.1 Latent State Vector \(S(t)\)
Rather than producing a scalar classification label, the Digital Twin estimates a continuous latent physiological state:
$$S(t) \in [-1, 1]^8$$
* **Dimensions 0–1**: Cardiovascular chronotropic & inotropic tone.
* **Dimensions 2–3**: Pulmonary mechanics & ventilatory efficiency.
* **Dimensions 4–5**: Mechanical contractility & local chest wall kinetic force.
* **Dimensions 6–7**: Overall autonomic stability index.

### 3.2 State Transition Dynamics
Future trajectory projection is modeled via residual transition dynamics:
$$S(t+1) = \text{clamp}(S(t) + f_\theta(S(t)), -1, 1)$$
Unrolling this network across 4 discrete steps yields prospective trajectory risks at **6h, 12h, and 24h** horizons.
