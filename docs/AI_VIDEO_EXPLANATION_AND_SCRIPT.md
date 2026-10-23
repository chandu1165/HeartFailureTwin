# HeartFailureTwin: Complete AI Video Production Guide & Full Script

> **Video Title**: HeartFailureTwin: A Personalized Multimodal Digital Twin for Early Forecasting of Heart-Failure Decompensation  
> **Challenge**: Happiest Health Digital Twin Challenge 2026  
> **Team**: code Kanyarasi (Team Leader: V Chandu | Members: Vonteddu Sri Sai Himanish Reddy, Aditya Vihar Repaka)  
> **Institution**: Vellore Institute of Technology AP (VIT-AP University)  
> **Target Video Length**: 15–20 Minutes (Full End-to-End Walkthrough)  
> **Target Resolution**: 1080p (1920x1080), 30 or 60 fps, 16:9 Widescreen

---

## 🎬 1. AI Video Concept & Production Workflow

This guide provides the complete blueprint for producing a jury-grade, AI-assisted video presentation. You can produce this video in under 30 minutes using one of two simple approaches:

### Method A: Screen Recording + AI Voiceover (Recommended — 20 mins)
1. **Screen Capture**: Use **OBS Studio**, **Loom**, or Windows Game Bar (`Win + G`) to record your screen following the visual cues in each scene below (flipping between your presentation slides, the live doctor dashboard at `http://127.0.0.1:8000`, and VS Code).
2. **AI Voiceover**: Copy the word-for-word voiceover script below into **ElevenLabs** (use an authoritative, clear medical voice like "Adam" or "Marcus"), or use **Microsoft Clipchamp** (free on Windows, featuring free natural AI text-to-speech).
3. **Assemble**: Import your screen recording and AI voiceover track into Clipchamp, CapCut, or Premiere, line up the scenes with the audio, and export as MP4.

### Method B: AI Avatar Video (HeyGen / Synthesia / InVideo AI)
1. Upload your slides (`docs/HeartFailureTwin_Presentation.pdf`) into **InVideo AI**, **HeyGen**, or **D-ID**.
2. Select a professional avatar (doctor or clinical researcher) and paste the scene scripts below.
3. Insert clips of the live dashboard recording during Scenes 7, 8, and 9.

---

## ⏱️ 2. Minute-by-Minute Master Timeline

| Scene | Time | Focus Area | Visual Asset On Screen |
| :---: | :---: | :--- | :--- |
| **1** | **00:00 – 01:45** | Introduction, Team Affiliation & Vision | [Slide 1: Title Slide & Team Details](docs/HeartFailureTwin_Presentation.pdf#page=1) |
| **2** | **01:45 – 04:00** | Problem Statement & Pitfalls of Static ML | [Slides 2 & 3: Clinical Context & Solution Paradigm](docs/HeartFailureTwin_Presentation.pdf#page=2) |
| **3** | **04:00 – 06:00** | Data Strategy: PhysioNet SCG-RHC & Synthetic Layer | [Slide 4: Data Provenance & Ethics](docs/HeartFailureTwin_Presentation.pdf#page=4) |
| **4** | **06:00 – 08:30** | System Architecture & Mathematical Foundations | [Slide 5 & Architecture Diagram Vector PDF](docs/architecture_diagram.pdf) |
| **5** | **08:30 – 10:15** | Scientific Rigor: Zero-Leakage GroupKFold Validation | [Slide 6: Patient-Level Splitting & Protocol](docs/HeartFailureTwin_Presentation.pdf#page=6) |
| **6** | **10:15 – 12:30** | Empirical Benchmark Results & Critical Ablation Study | [Slides 7 & 8: Benchmark & Ablation Tables](docs/HeartFailureTwin_Presentation.pdf#page=7) |
| **7** | **12:30 – 14:45** | Live Demo: Doctor Dashboard & Patient Digital Twin | Live Browser (`http://127.0.0.1:8000` — Cohort & Patient Views) |
| **8** | **14:45 – 17:00** | Live Demo: 4D Twin Replay (31.2h Early Detection) | Live Browser (`http://127.0.0.1:8000` — Interactive Scrubber 0-72h) |
| **9** | **17:00 – 18:30** | Live Demo: In Silico "What-If" Counterfactual Simulation | Live Browser (`http://127.0.0.1:8000` — What-If Simulator Sliders) |
| **10** | **18:30 – 20:00** | Codebase Inspection, Limitations, Ethics & Wrap-Up | VS Code (Pytest 8/8 pass, `/docs` Swagger UI, Slides 11 & 12) |

---

## 🎙️ 3. Complete Word-for-Word Voiceover Script & Visual Directions

---

### SCENE 1: Introduction, Affiliation & High-Level Objective (00:00 – 01:45)
**Visual on Screen**: Display **Slide 1** of `docs/HeartFailureTwin_Presentation.pdf` (or PowerPoint). Highlight Team Name (`code Kanyarasi` / `valligatlachandu`), Team Leader (`V Chandu`), Members (`Vonteddu Sri Sai Himanish Reddy`, `Aditya Vihar Repaka`), and Institution (`Vellore Institute of Technology AP`).

> **AI Voiceover Script**:  
> *"Greetings distinguished judges and healthcare innovators. Welcome to our comprehensive presentation and working prototype demonstration of **HeartFailureTwin**: A Personalized Multimodal Digital Twin for Early Forecasting of Heart-Failure Decompensation.  
> 
> My name is **V Chandu**, leading team **code Kanyarasi** alongside my colleagues **Vonteddu Sri Sai Himanish Reddy** and **Aditya Vihar Repaka** from the **Vellore Institute of Technology AP**, submitting for the **Happiest Health Digital Twin Challenge 2026**.  
> 
> Our core philosophy is simple yet transformative: **From patient data to patient trajectory.**  
> 
> We did not build another generic, static machine learning classifier that outputs a single risk number. Instead, we have engineered a continuously updated, patient-specific computational Digital Twin. It integrates historical clinical records with high-frequency wearable physiological telemetry, calibrates an individualized resting envelope for every patient, tracks an 8-dimensional latent physiological state space, and forecasts prospective deterioration trajectories up to 31 hours before acute clinical collapse occurs.  
> 

> As an essential medical disclaimer: HeartFailureTwin is designed strictly as a clinical decision-support and research prototype. It does not replace medical practitioners, provide automated diagnostic declarations, or prescribe therapies. Let us now examine the clinical urgency that motivated this work."*

---

### SCENE 2: The Heart Failure Crisis & The Static ML Bottleneck (01:45 – 04:00)
**Visual on Screen**: Switch to **Slide 2** ("The Escalating Heart Failure Burden"), then smoothly transition to **Slide 3** ("The HeartFailureTwin Paradigm").

> **AI Voiceover Script**:  
> *"Heart failure represents an overwhelming public health crisis in India, impacting over 8 to 10 million individuals. Notably, Indian patients develop heart failure almost a decade earlier than Western cohorts—frequently in their mid-fifties during their peak productive years. Even more devastating is the 30-day post-discharge readmission rate, which exceeds 25 to 30 percent.  
> 
> Why does this happen? In heart failure, decompensation is not an instantaneous lightning strike. It is a slow, silent physiological deterioration that develops over days to weeks. Fluid gradually accumulates in the lungs and venous system, and myocardial contractility progressively deteriorates. However, by the time an outpatient experiences overt symptoms like severe breathlessness or swelling, they are already in acute pulmonary edema, necessitating an emergency ICU admission.  
> 
> Existing remote monitoring systems suffer from three critical flaws:  
> First, **fixed population thresholds**. Standard monitors sound an alert when heart rate exceeds 100 bpm. But for a heart failure patient on high-dose carvedilol or metoprolol whose baseline heart rate is 60, an elevation to 88 bpm represents severe autonomic distress, yet a population monitor stays silent.  
> Second, **amnesic snapshot classifiers**. Traditional AI models treat incoming observations as isolated snapshots, completely blind to the patient's underlying temporal trajectory.  
> And third, **severe alarm fatigue**. Up to 85% of threshold alerts are false alarms, leading clinicians to silence notifications.  
> 
> HeartFailureTwin solves this by establishing an individualized baseline envelope for each monitored patient, tracking subtle multimodal deviations, and projecting prospective state transitions."*

---

### SCENE 3: Data Strategy & Transparent Provenance (04:00 – 06:00)
**Visual on Screen**: Switch to **Slide 4** ("Data Strategy: Primary Open Dataset & Synthetic Cohort Layer").

> **AI Voiceover Script**:  
> *"A fundamental tenet of rigorous medical research is data transparency. We avoided the common pitfall of searching for a single mythical dataset that contains every conceivable clinical variable, nor did we disguise artificial data as real patient telemetry.  
> 
> Our primary empirical foundation is the open-access **PhysioNet SCG-RHC Wearable Seismocardiogram and Right Heart Catheter Database**, version 1.0.0. This rich clinical cohort consists of 73 heart-failure patients monitored simultaneously with wearable patch sensors and gold-standard invasive right-heart catheterization.  
> 
> The database provides continuous 500 Hertz Lead-II ECG, synchronized 500 Hertz tri-axial Seismocardiography—which measures mechanical chest wall vibrations directly reflecting myocardial contractility—along with photoplethysmography, respiration, non-invasive blood pressure, and invasive hemodynamic measurements like pulmonary artery pressure and wedge pressure. All waveforms were ingested losslessly using the standard WFDB signal processing standard.  
> 
> To support stress testing, 72-hour continuous trajectory scrubbers, and in silico simulation, we also established a secondary synthetic cohort layer. We emphasize that all synthetic streams are explicitly tagged with the metadata label `SYNTHETIC_LONGITUDINAL_SIMULATION`. They are never used to make false claims of clinical diagnostic efficacy, but rather to evaluate multi-day temporal tracking and counterfactual modeling."*

---

### SCENE 4: System Architecture & Mathematical Foundations (06:00 – 08:30)
**Visual on Screen**: Open **`docs/architecture_diagram.pdf`** (or Slide 5). Zoom in sequentially to Layer 1, Layer 2, Layer 3, Layer 4, and Layer 5.

> **AI Voiceover Script**:  
> *"Let us examine the end-to-end system architecture of HeartFailureTwin, detailed in our vector architecture diagram. The pipeline is structured across five decoupled, production-grade layers:  
> 
> In **Layer 1**, the system ingests raw multi-modal telemetry: continuous 500 Hz ECG, 500 Hz 3-axis SCG accelerometry, PPG, respiration, and clinical EHR profiles.  
> 
> In **Layer 2**, signals pass through a rigorous Signal Quality Assessor in `quality.py`. This computes continuous quality indices between 0.0 and 1.0 based on signal-to-noise ratio, baseline wander, and clipping saturation. In parallel, our feature extraction pipelines compute R-peak intervals, heart rate variability metrics such as RMSSD and SDNN, and seismocardiographic mechanical kinetic energy.  
> 
> In **Layer 3**, we introduce the **Patient-Specific Baseline Engine** in `baseline.py`. During an initial resting calibration window, the system estimates the patient's personalized mean $\mu_i$ and dispersion $\sigma_i$. All incoming physiological parameters are then converted into personalized Z-score deviations:  
> $\Delta z_{i, t} = (x_{i, t} - \mu_i) / \sigma_i$.  
> 
> In **Layer 4**, our PyTorch Gated Cross-Modal Fusion network in `state_estimator.py` maps each modality into a 16-dimensional embedding. It uses non-linear gated attention to weight each modality based on signal quality and cross-modal relevance, projecting them into an 8-dimensional normalized latent physiological state vector:  
> $S(t) \in [-1, +1]^8$.  
> This latent space encodes contractility, congestion, autonomic tone, and electrophysiological stability.  
> 
> Finally, in **Layer 5**, a neural state-transition operator models the temporal derivative $S(t) \to S(t+1)$, forecasting 24-hour prospective decompensation probabilities and powering our interactive doctor dashboard."*

---

### SCENE 5: Scientific Rigor & Zero-Leakage GroupKFold (08:30 – 10:15)
**Visual on Screen**: Switch to **Slide 6** ("Zero-Leakage Experimental Methodology").

> **AI Voiceover Script**:  
> *"A critical issue in modern biomedical machine learning is **patient data leakage**. Many published papers report extraordinary AUROCs of 98% by randomly splitting sliding time windows into train and test sets. When windows from the same patient appear in both partitions, the network simply memorizes that individual's unique resting waveform morphology, rather than learning true physiological pathology. When tested on real unseen patients, these models fail catastrophically.  
> 
> To ensure publication-grade scientific validity, HeartFailureTwin enforces a strict **5-Fold GroupKFold validation protocol**, partitioned strictly by `patient_id` across all 73 clinical subjects.  
> 
> Before any model is trained, hard programmatic assertions verify that the intersection of training patients and validation patients is completely empty: $\text{TrainPatients} \cap \text{ValPatients} = \emptyset$.  
> 
> Every single metric we report is computed strictly Out-Of-Fold on patients the model has never encountered before. Furthermore, because healthcare datasets are naturally class-imbalanced, we evaluate our models using the Area Under the Precision-Recall Curve (AUPRC), Brier score for probability calibration, and Expected Calibration Error, alongside traditional AUROC and F1-scores."*

---

### SCENE 6: Empirical Benchmark Results & Ablation Analysis (10:15 – 12:30)
**Visual on Screen**: Display **Slide 7** (Benchmark Table), then **Slide 8** (Ablation Study Table).

> **AI Voiceover Script**:  
> *"Here are our rigorous empirical results across four distinct model architectures evaluated under the identical 5-fold zero-leakage cross-validation protocol:  
> 
> As you can observe in Table 1:  
> * Baseline **Logistic Regression** achieved an Out-Of-Fold AUROC of 0.7319 and AUPRC of 0.5365.  
> * **Random Forest** achieved an AUROC of 0.8543 and AUPRC of 0.6715.  
> * **XGBoost** reached an AUROC of 0.8570 and AUPRC of 0.7241.  
> * And our **Temporal GRU model** achieved the highest overall performance: an Out-Of-Fold **AUROC of 0.8713**, an **AUPRC of 0.7497**, and an outstanding clinical **Sensitivity of 89.3%**.  
> 
> This proves our first research hypothesis: temporal recurrent modeling captures non-linear trajectory drifts that static classifiers fail to identify.  
> 
> Next, look at our Critical Ablation Study on Slide 8:  
> * Relying on **EHR clinical profiles alone** yields an AUROC of only 0.6962.  
> * Adding wearable waveforms without EHR yields 0.7386.  
> * When we remove Seismocardiography, AUROC plummets by 17 points down to 0.6736, demonstrating that mechanical chest vibration is an indispensable early biomarker of failing cardiac output.  
> * Finally, comparing condition 5—a population-level multimodal model—with condition 6—the full HeartFailureTwin with personalized baseline envelopes—shows that personalization increases AUROC to **0.8440**, improves specificity to **80.5%**, and achieves the highest overall F1-score of **0.6871**."*

---

### SCENE 7: Live Demonstration: Doctor Dashboard & Patient Twin (12:30 – 14:45)
**Visual on Screen**: Switch to web browser showing the live dashboard at **`http://127.0.0.1:8000`**.  
*Action*: Click on the **Cohort Overview** tab, scroll through the 4 risk summary cards (Stable, Early Deviation, Deteriorating, High-Risk), and click on patient **HF-104**.  
*Action*: Highlight the patient profile card, the 8-dimensional latent state radar chart, the signal quality indicators, and the physiological vitals chart showing the **shaded green baseline envelope**.

> **AI Voiceover Script**:  
> *"Now, let us experience the live, running prototype of HeartFailureTwin. Here is our doctor-facing clinical dashboard, served via FastAPI and rendered with React 19, TypeScript, Tailwind CSS, and Recharts.  
> 
> On the **Cohort Overview** screen, the clinical care team has immediate situational awareness. Patients are automatically triaged into four intuitive states: Stable, Early Deviation, Deteriorating, and High-Risk.  
> 
> Let us select patient **HF-104**, a 68-year-old male with ischemic cardiomyopathy, NYHA Class III heart failure, hypertension, and reduced ejection fraction.  
> 
> Here in the **Patient Digital Twin view**, notice three distinctive innovations:  
> First, on the upper left, we see the patient's current risk assessment and signal quality index—confirming high telemetry fidelity across ECG, SCG, and PPG.  
> Second, in the center, we visualize the patient's **8-Dimensional Latent Twin State Vector** $S(t)$. Rather than hiding behind a black box, this chart provides complete transparent explainability: contractility is depressed at negative 0.58, congestion index is elevated at positive 0.72, and autonomic tone indicates significant sympathetic compensation.  
> And third, look at the physiological timeline: the green shaded band represents patient HF-104's **personal resting baseline envelope**. Clinicians can immediately see that while his current heart rate of 86 bpm would appear completely normal to a standard population monitor, it is distinctly above his personal resting baseline of 68 bpm. Now let us examine the centerpiece of our prototype: 4D Twin Replay."*

---

### SCENE 8: The Centerpiece: 4D Twin Replay (31.2h Early Detection) (14:45 – 17:00)
**Visual on Screen**: Click on the **4D Twin Replay** tab in the dashboard.  
*Action*: Click the **Play** button, or drag the interactive timeline slider from **Hour 0** to **Hour 24**, then **Hour 48**, and finally **Hour 72**.  
*Action*: Point out how the state badge dynamically transitions from `STABLE` $\to$ `EARLY_DEVIATION` $\to$ `DETERIORATING` $\to$ `HIGH_RISK`. Highlight the **Early Warning Lead Time badge showing 31.2 hours**.

> **AI Voiceover Script**:  
> *"This is the **4D Twin Replay** engine. For a cardiologist reviewing a patient's case, time is the most critical dimension. Twin Replay allows the doctor to scrub backward and forward through 72 hours of continuous monitoring data.  
> 
> Notice what happens as we scrub forward in time:  
> At **Hour 0 to Hour 24**, the patient is in the `STABLE` state. All physiological parameters reside securely within their personalized green baseline boundaries.  
> 
> Around **Hour 32 to 36**, look closely at the SCG kinetic energy and heart rate variability. Long before any symptoms would be reported by the patient, the Digital Twin detects subclinical autonomic and mechanical drift, triggering the `EARLY_DEVIATION` state.  
> 
> By **Hour 48**, the state transitions to `DETERIORATING`, with progressive nocturnal heart rate elevation, decreasing respiratory stability, and rising congestion markers.  
> 
> Notice the crucial lead-time metric displayed here: **31.2 Hours Early Warning**.  
> While a traditional threshold alert would only fire at Hour 70 when the patient is already gasping for breath, HeartFailureTwin gave the care team a 31-hour actionable window. That is ample time for an outpatient nurse to call the patient, verify dietary compliance, adjust oral diuretic dosing, and prevent an emergency department admission. This demonstrates the tangible life-saving impact of our digital twin."*

---

### SCENE 9: In Silico "What-If" Counterfactual Simulation (17:00 – 18:30)
**Visual on Screen**: Click on the **What-If Simulation** tab.  
*Action*: Drag the **Fluid Offload** slider to **-1.5 kg** (simulating IV/oral diuretic effect).  
*Action*: Drag the **Heart Rate Modulation** slider to **-10 bpm** (simulating beta-blocker optimization).  
*Action*: Observe the simulated trajectory curve shifting from Red (High Risk) down to Green (Stable). Highlight the prominent medical disclaimer.

> **AI Voiceover Script**:  
> *"Next, we demonstrate our **In Silico What-If Simulation Engine**. One of the defining characteristics of a true Digital Twin is the capability to simulate counterfactual future trajectories under hypothetical physiological interventions.  
> 
> In this view, a clinician can test potential management hypotheses:  
> 'If we administer an oral diuretic and achieve a 1.5-kilogram fluid offload over the next 24 hours, how will this patient's prospective trajectory respond?'  
> 
> As we adjust the Fluid Offload slider to negative 1.5 kilograms and moderate heart rate by minus 10 bpm, the neural transition dynamics immediately recompute the prospective 24-hour state. Notice the dual trajectory comparison: the red dotted line shows the untreated trajectory heading toward high-risk decompensation, while the solid green curve demonstrates that the proposed intervention stabilizes the patient's latent state back into the safe envelope.  
> 
> We emphasize once again: the simulation does not prescribe medication or automate clinical decisions. It serves strictly as an intuitive computational scratchpad to augment clinical decision-making."*

---

### SCENE 10: Codebase Verification, Ethics & Conclusion (18:30 – 20:00)
**Visual on Screen**: Switch to VS Code terminal.  
*Action*: Run `.venv\Scripts\pytest.exe -v` in the terminal and show **8 passed in 7.8s**.  
*Action*: Open browser tab showing the interactive OpenAPI Swagger documentation at `http://127.0.0.1:8000/docs`.  
*Action*: Switch to **Slide 12** ("Conclusion & Future Horizons").

> **AI Voiceover Script**:  
> *"To verify the engineering integrity and reproducibility of our prototype, here is our automated test suite running in VS Code. As you can see, all eight unit and integration tests pass cleanly—verifying zero patient leakage, signal quality guards, cross-modal fusion math, and API endpoint schemas. Furthermore, our complete REST backend is fully documented with interactive OpenAPI Swagger docs at `/docs`.  
> 
> In conclusion, let us address limitations and our future horizon:  
> While our primary validation relies on the in-hospital PhysioNet SCG-RHC database, our future roadmap includes prospective observational studies in Indian tertiary hospitals and validating motion-artifact suppression in free-living ambulatory settings using commercial smartwatch sensors.  
> 
> HeartFailureTwin demonstrates that by shifting from static snapshot thresholds to patient-specific trajectory forecasting, we can empower Indian clinicians to detect heart-failure decompensation up to 31 hours earlier, reducing readmission rates and democratizing intensive cardiac monitoring.  
> 
> On behalf of team **code Kanyarasi**, **V. Chandu**, and the **Vellore Institute of Technology AP**, thank you for your time, consideration, and dedication to advancing digital health."*

---

## 🛠️ 4. Ready-to-Use Tools & Quick Production Checklist

| Tool | Purpose | Free / Accessible Link |
| :--- | :--- | :--- |
| **Microsoft Clipchamp** | Free Windows Screen Recorder + Natural AI Text-to-Speech | Built into Windows 11 or [clipchamp.com](https://clipchamp.com) |
| **OBS Studio** | High-definition open-source desktop & window capture | [obsproject.com](https://obsproject.com) |
| **ElevenLabs** | Studio-quality AI voiceover generator (Paste script $\to$ MP3) | [elevenlabs.io](https://elevenlabs.io) |
| **InVideo AI / HeyGen** | AI avatar video generator from text and slides | [invideo.io](https://invideo.io) / [heygen.com](https://heygen.com) |
| **YouTube** | Video hosting platform (Set visibility to **Unlisted**) | [studio.youtube.com](https://studio.youtube.com) |

### Final Step:
Once you have generated your video MP4 and uploaded it to YouTube as **Unlisted**, copy the link, paste it into **Section 6** of [`README.md`](../README.md#6-15-20-minute-demo-video-unlisted-youtube), and push your commits to GitHub:
```bash
git add README.md
git commit -m "Add final Unlisted YouTube demo link"
git push origin master
```
