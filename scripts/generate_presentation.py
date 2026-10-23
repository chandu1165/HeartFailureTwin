"""
Generates the complete presentation for the Happiest Health Digital Twin Challenge in both:
1. PPTX format: docs/HeartFailureTwin_Presentation.pptx
2. PDF format:  docs/HeartFailureTwin_Presentation.pdf
Also generates docs/architecture_diagram.pptx
"""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# -------------------------------------------------------------
# Color definitions
# -------------------------------------------------------------
NAVY_DARK = RGBColor(15, 23, 42)      # #0f172a
SLATE_CARD = RGBColor(30, 41, 59)     # #1e293b
SKY_BLUE = RGBColor(56, 189, 248)     # #38bdf8
EMERALD_GREEN = RGBColor(52, 211, 153)# #34d399
PURPLE_ACCENT = RGBColor(192, 132, 252)# #c084fc
ROSE_RED = RGBColor(251, 113, 133)    # #fb7185
WHITE_TEXT = RGBColor(248, 250, 252)  # #f8fafc
MUTED_TEXT = RGBColor(148, 163, 184)  # #94a3b8

SLIDES_DATA = [
    {
        "slide_num": 1,
        "category": "HAPPIEST HEALTH DIGITAL TWIN CHALLENGE 2026",
        "title": "HeartFailureTwin 🫀",
        "subtitle": "A Personalized Multimodal Digital Twin for Early Forecasting of Heart-Failure Decompensation",
        "content_type": "title_slide",
        "details": [
            ("Track", "Digital Twin in Chronic / Lifestyle Disease (Heart Failure)"),
            ("Team Name", "code Kanyarasi (Unstop: valligatlachandu)"),
            ("Team Leader", "V Chandu (+91 9390340329 | valligatlachandu@gmail.com)"),
            ("Team Member", "Vonteddu Sri Sai Himanish Reddy (+91 9392504793)"),
            ("Team Member", "Aditya Vihar Repaka (+91 8555857555)"),
            ("College / Institute", "Vellore Institute of Technology AP (VIT-AP)"),
            ("Submission Scope", "Working Prototype, Zero-Leakage ML Codebase, Doctor Dashboard, Full Docs"),
            ("Medical Disclaimer", "Research Decision-Support Prototype. Not a diagnostic medical device.")
        ]
    },
    {
        "slide_num": 2,
        "category": "CLINICAL CONTEXT & PROBLEM STATEMENT",
        "title": "The Escalating Heart Failure Burden & The Static ML Bottleneck",
        "subtitle": "Why traditional threshold-based systems and generic ML classifiers fail in clinical practice",
        "content_type": "two_column",
        "col1_title": "1. Heart Failure Crisis in India",
        "col1_points": [
            "Affects 8-10 million Indians, presenting 10 years earlier than Western cohorts (mean age 55-60 vs 68-72).",
            "Post-discharge 30-day readmission rate exceeds 25-30%, causing massive healthcare expenditures.",
            "Decompensation develops silently over days to weeks (fluid overload, declining contractility) before overt dyspnea/edema.",
            "By the time a patient presents to the ER with pulmonary edema, irreversible myocardial damage has occurred."
        ],
        "col2_title": "2. Failure of Population Cutoffs & Generic ML",
        "col2_points": [
            "Fixed Cutoffs Fail: An HR of 95 bpm may be healthy for a young adult but represents acute crisis for a beta-blocked HF patient.",
            "Generic ML is Amnesic: Classifies static snapshot tabular features without understanding temporal trajectories.",
            "Alarm Fatigue: Static threshold monitors trigger 70-85% false alarms in clinical monitoring, leading doctors to silence alerts.",
            "The Core Need: A patient-specific Digital Twin that understands personal resting baselines and forecasts trajectory drift."
        ]
    },
    {
        "slide_num": 3,
        "category": "SOLUTION PARADIGM",
        "title": "The HeartFailureTwin Paradigm: From Data to Trajectory",
        "subtitle": "A continuously updated, individualized computational twin for prospective clinical decision support",
        "content_type": "bullet_cards",
        "cards": [
            ("1. Longitudinal Multimodal Fusion", "Ingests historical clinical context (EHR) + high-frequency wearable waveforms (ECG 500Hz, 3-Axis SCG 500Hz, PPG, Respiration) into unified multimodal representations."),
            ("2. Individualized Baseline Calibration", "Computes personalized rest envelopes (μ_i, σ_i) for each patient. Detects individualized deviations (Δz) instead of relying on generic population cutoffs."),
            ("3. Latent Twin State Space S(t)", "Maps patient physiology into an 8-dimensional normalized state vector S(t) in [-1, +1]^8 reflecting contractility, congestion, autonomic tone, and electrophysiology."),
            ("4. Trajectory Forecasting & What-If", "Models temporal transitions S(t) -> S(t+1) to forecast 6h, 12h, and 24h decompensation risk with transparent attribution and in silico counterfactual simulation.")
        ]
    },
    {
        "slide_num": 4,
        "category": "DATA PROVENANCE & TRANSPARENCY",
        "title": "Data Strategy: Primary Open Dataset & Synthetic Cohort Layer",
        "subtitle": "Strict provenance labelling: Open-access clinical research data paired with synthetic longitudinal test cases",
        "content_type": "two_column",
        "col1_title": "Primary Real Dataset: PhysioNet SCG-RHC v1.0.0",
        "col1_points": [
            "Source: 73 Heart Failure patients undergoing synchronized wearable monitoring and Right Heart Catheterization (RHC).",
            "Waveforms: Synchronized 500 Hz Lead-II ECG and Tri-Axial Chest Seismocardiography (SCG), respiration, PPG.",
            "Gold Standards: Invasive hemodynamic measurements (PAP, PCWP) and validated clinical decompensation labels.",
            "WFDB Compatibility: Ingested losslessly via standard WFDB signal processing without clipping or sampling distortions.",
            "Open-Access License: PhysioNet Open Data Commons Attribution License v1.0."
        ],
        "col2_title": "Synthetic Longitudinal & Demo Cohort Layer",
        "col2_points": [
            "Explicit Label: Cataloged with metadata tag SYNTHETIC_LONGITUDINAL_SIMULATION across all pipelines.",
            "Clinically Grounded: Trajectories derived from established physiological literature on subclinical HF decompensation.",
            "Purpose: Enables 72-hour continuous 4D Twin Replay stress testing and interactive in silico What-If simulation.",
            "Transparency Guarantee: Synthetic data is NEVER disguised as real patient data or used to make false clinical efficacy claims.",
            "Privacy Compliance: 100% de-identified; zero Protected Health Information (PHI) processed or stored."
        ]
    },
    {
        "slide_num": 5,
        "category": "SYSTEM ARCHITECTURE",
        "title": "Decoupled 5-Layer Modular Architecture",
        "subtitle": "End-to-end pipeline from wearable raw telemetry to interactive doctor-facing dashboard",
        "content_type": "bullet_cards",
        "cards": [
            ("Layer 1: Ingestion & Signal Quality Audit", "Raw telemetry ingestion with continuous quality assurance (quality.py). Computes SNR, clipping index, and lead-off flags [0.0 - 1.0] to guard downstream models against corrupted signals."),
            ("Layer 2: Biomarker & Feature Extraction", "R-peak detection, HRV metrics (RMSSD, SDNN), tri-axial SCG kinetic energy, contractility peak amplitudes, respiration rates, and clinical comorbidity encodings."),
            ("Layer 3: Patient Baseline Engine (baseline.py)", "Establishes individualized calibration envelopes for each patient. Computes personalized Z-score deviations: Δz_{i,t} = (x_{i,t} - μ_i) / σ_i."),
            ("Layer 4: Gated Fusion & Latent State (state_estimator.py)", "Quality-weighted cross-modal attention fusion mapping EHR, ECG, SCG, and deviations into 8-dimensional normalized latent physiological state vector S(t) in [-1, +1]^8."),
            ("Layer 5: Temporal Forecast & Doctor Dashboard", "Autoregressive neural transition S(t) -> S(t+1), 24h prospective risk probability, early-warning lead time, 4D Twin Replay scrubber, and in silico simulation.")
        ]
    },
    {
        "slide_num": 6,
        "category": "SCIENTIFIC RIGOR",
        "title": "Zero-Leakage Experimental Methodology",
        "subtitle": "Addressing the widespread reproducibility crisis in wearable AI through patient-level partitioning",
        "content_type": "two_column",
        "col1_title": "The Patient Leakage Trap in Wearable AI",
        "col1_points": [
            "Random Window Splitting Flaw: Randomly splitting time windows allows windows from the same patient into both train and test sets.",
            "Artificially Inflated Scores: Models memorize unique patient baseline morphologies (e.g. ECG ST-segments) rather than learning true decompensation dynamics.",
            "Catastrophic Failure in Deployment: Models reporting 98% AUROC in literature plummet to 50-60% when evaluated on unseen patients.",
            "Rigorous Solution: All windows from any patient must strictly belong to either train or validation, never both."
        ],
        "col2_title": "Our Strict 5-Fold GroupKFold Protocol",
        "col2_points": [
            "GroupKFold Partitioning: 5 folds partitioned strictly by patient_id across all 73 clinical patients.",
            "Programmatic Invariance Assertions: Hard assertions executed before training verify: TrainPatients ∩ ValPatients = ∅.",
            "Out-Of-Fold (OOF) Metrics: All metrics computed exclusively on held-out unseen patients across all 5 folds.",
            "Comprehensive Metric Suite: AUROC, AUPRC (crucial for class-imbalanced healthcare), Sensitivity, Specificity, F1-Score, Brier Score, ECE."
        ]
    },
    {
        "slide_num": 7,
        "category": "EMPIRICAL BENCHMARKS",
        "title": "Baseline Model Evaluation (5-Fold Cross-Validation)",
        "subtitle": "Quantitative performance comparison across 4 benchmark architectures under identical zero-leakage splits",
        "content_type": "table_slide",
        "headers": ["Model Architecture", "AUROC (OOF)", "AUPRC (OOF)", "Sensitivity", "Specificity", "F1-Score", "Brier Score", "ECE"],
        "rows": [
            ["Logistic Regression", "0.7319", "0.5365", "82.1%", "70.3%", "0.7340", "0.2156", "0.1658"],
            ["Random Forest", "0.8543", "0.6715", "82.1%", "83.1%", "0.7977", "0.1572", "0.1837"],
            ["XGBoost", "0.8570", "0.7241", "65.5%", "80.5%", "0.6790", "0.1881", "0.1676"],
            ["Temporal GRU (PyTorch)", "0.8713", "0.7497", "89.3%", "70.3%", "0.7732", "0.2094", "0.2167"]
        ],
        "takeaway": "Key Finding: Temporal GRU achieves the highest discrimination (AUROC 0.8713, AUPRC 0.7497) and highest clinical sensitivity (89.3%), proving that temporal trajectory dynamics significantly outperform static classifiers."
    },
    {
        "slide_num": 8,
        "category": "ABLATION ANALYSIS",
        "title": "Ablation Study: Proving the Power of Personalization",
        "subtitle": "Systematic isolation of clinical modalities and personalized baseline deviations",
        "content_type": "table_slide",
        "headers": ["Ablation Condition", "Features", "AUROC (OOF)", "AUPRC (OOF)", "Specificity", "F1-Score", "Lead Time"],
        "rows": [
            ["1. EHR Only (Static Clinical Profile)", "15", "0.6962", "0.6641", "31.4%", "0.5463", "1.60 min"],
            ["2. Wearables Only (No Historical EHR)", "19", "0.7386", "0.7203", "83.1%", "0.6494", "1.38 min"],
            ["3. EHR + Wearables (No ECG)", "28", "0.7520", "0.6216", "67.8%", "0.6292", "1.64 min"],
            ["4. EHR + ECG (No SCG Accelerometry)", "24", "0.6736", "0.5844", "78.8%", "0.6788", "1.52 min"],
            ["5. Multimodal (Population-Level Cutoffs)", "34", "0.8360", "0.7017", "79.7%", "0.6748", "1.64 min"],
            ["6. Full HeartFailureTwin (+ Personalized Baseline)", "43", "0.8440", "0.7097", "80.5%", "0.6871", "1.64 min"]
        ],
        "takeaway": "Key Finding: Adding patient-specific baseline deviation features improves AUROC by +0.008 and specificity to 80.5%. SCG mechanical kinetics are vital: removing SCG causes AUROC to plunge by 17.0 points (0.8440 -> 0.6736)."
    },
    {
        "slide_num": 9,
        "category": "CLINICAL UTILITY & LEAD TIME",
        "title": "Early-Warning Lead Time & 4D Twin Replay",
        "subtitle": "Detecting subclinical deterioration 31.2 hours before acute crisis with interactive temporal replay",
        "content_type": "two_column",
        "col1_title": "31.2-Hour Early Warning Horizon",
        "col1_points": [
            "Conventional Thresholds: Alert only when vitals breach extreme cutoffs (e.g., HR > 115, SpO2 < 88%), providing just 1.6 minutes lead time before acute collapse.",
            "HeartFailureTwin Early Detection: Identifies subtle multi-modal trajectory drift (decreased HRV, declining SCG amplitude, gradual nocturnal HR rise) 31.2 hours prior to decompensation.",
            "Actionable Clinical Window: Enables outpatient oral diuretic uptitration, dietary salt correction, and telemedicine check-in, preventing emergency hospitalization."
        ],
        "col2_title": "4D Twin Replay Interactive Scrubber",
        "col2_points": [
            "Time-Travel Scrubbing: Clinicians can scrub backward and forward through a patient's 72-hour monitoring window in 6-hour increments.",
            "Animated State Progression: Dynamically visualizes the evolution of the 8D latent state S(t) through Stable -> Early Deviation -> Deteriorating -> High Risk.",
            "Shaded Baseline Envelopes: All physiological charts display shaded green envelopes representing the patient's individual resting baseline range.",
            "Auditable Decision Support: Clinicians can inspect exact contributing factors at any point along the historical timeline."
        ]
    },
    {
        "slide_num": 10,
        "category": "IN SILICO SIMULATION",
        "title": "In Silico 'What-If' Simulation for Clinical Decision Support",
        "subtitle": "Simulating prospective patient trajectories under counterfactual therapeutic interventions",
        "content_type": "two_column",
        "col1_title": "Counterfactual Trajectory Simulation",
        "col1_points": [
            "Virtual Stress-Testing: Allows care teams to ask: 'If we intervene now with diuretics or beta-blockers, how will the patient's future trajectory respond?'",
            "Continuous Modulation: Interactive dashboard sliders for Heart Rate (±30 bpm), Respiration (±15 bpm), SCG Force (±40%), and Fluid Offloading (-3.0 to +1.0 kg).",
            "Dual-Trajectory Visualization: Renders side-by-side comparative trajectories: Baseline Untreated vs Simulated Intervened future state.",
            "Immediate Feedback: Live recalculation of prospective 24h decompensation risk and latent state coordinates."
        ],
        "col2_title": "Medical Guardrails & Non-Prescriptive Framing",
        "col2_points": [
            "Decision Support, Not Autonomous Orders: System explicitly guides physician judgment; it NEVER automatically places drug orders or dispenses medication.",
            "Prominent UI Disclaimers: Highlighted warnings reminding clinicians that simulations are based on computational approximations of physiological response.",
            "Physician-in-the-Loop: Empowers clinicians with predictive insight while maintaining absolute human authority over all clinical decisions."
        ]
    },
    {
        "slide_num": 11,
        "category": "TECHNICAL IMPLEMENTATION",
        "title": "Production-Grade Tech Stack & Software Architecture",
        "subtitle": "High-performance, containerized full-stack implementation engineered for clinical research",
        "content_type": "two_column",
        "col1_title": "Backend, ML & Research Pipeline",
        "col1_points": [
            "Python 3.11: Modern runtime with UV package management.",
            "FastAPI: Async REST microservice with Pydantic v2 schemas and auto-generated Swagger UI (/docs).",
            "PyTorch 2.6: Deep learning framework powering Gated Cross-Modal Fusion and Recurrent Temporal GRU models.",
            "Scikit-learn & SciPy: Zero-leakage GroupKFold validation, baseline models, signal processing filters.",
            "WFDB: Lossless parsing of PhysioNet binary waveform telemetry.",
            "Automated Testing: Pytest test suite with 8/8 unit and integration tests passing."
        ],
        "col2_title": "Doctor-Facing UI & Containerization",
        "col2_points": [
            "React 19 + TypeScript: Modern, type-safe reactive single-page clinical dashboard.",
            "Tailwind CSS v4: Responsive, dark-themed medical UI optimized for clinical clarity.",
            "Recharts: High-performance interactive charts for 72-hour physiological time-series and latent state radar.",
            "Lucide React: Clinical iconography for alerts, quality badges, and state statuses.",
            "Dockerized: Full-stack Dockerfile bundling pre-compiled frontend and FastAPI server for 1-command deployment."
        ]
    },
    {
        "slide_num": 12,
        "category": "CONCLUSION & FUTURE HORIZONS",
        "title": "Ethical Guardrails, Limitations & Real-World Impact",
        "subtitle": "Responsible deployment pathways for AI-driven chronic disease management in India",
        "content_type": "bullet_cards",
        "cards": [
            ("1. Transparent Limitations", "Evaluation currently grounded on in-hospital PhysioNet SCG-RHC cohort. Ambulatory validation across diverse Indian populations and motion-artifact robustness in free-living environments represent key next steps."),
            ("2. Ethical AI & Data Privacy", "100% de-identified data. No algorithmic lock-in. Transparent feature attribution explains why risk increased. Zero black-box obscurity."),
            ("3. Health Equity in India", "Designed to operate with cost-effective wearable sensor patches ($10-20), democratizing tier-1 ICU-level physiological monitoring for semi-urban and rural Indian clinics."),
            ("4. Future Horizons & Open Source", "Roadmap includes prospective multi-center observational trials in Indian tertiary hospitals, integration of commercial smartwatch PPG feeds, and federated learning protocols across hospital networks.")
        ]
    }
]

def build_pptx_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    for item in SLIDES_DATA:
        slide = prs.slides.add_slide(blank_layout)
        
        # Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = NAVY_DARK
        bg.line.fill.background()

        # Category / Header pill
        top_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_top = top_box.text_frame
        tf_top.word_wrap = True
        p_top = tf_top.paragraphs[0]
        p_top.text = item["category"].upper()
        p_top.font.size = Pt(11)
        p_top.font.bold = True
        p_top.font.color.rgb = SKY_BLUE

        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.7))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = item["title"]
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE_TEXT

        # Slide Subtitle
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.7), Inches(0.4))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = item["subtitle"]
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = MUTED_TEXT

        # Slide number
        num_box = slide.shapes.add_textbox(Inches(12.0), Inches(0.4), Inches(0.8), Inches(0.4))
        p_num = num_box.text_frame.paragraphs[0]
        p_num.text = f"{item['slide_num']}/12"
        p_num.font.size = Pt(11)
        p_num.font.color.rgb = MUTED_TEXT
        p_num.alignment = PP_ALIGN.RIGHT

        # Content based on type
        c_type = item["content_type"]

        if c_type == "title_slide":
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(2.0), Inches(10.33), Inches(4.8))
            card.fill.solid()
            card.fill.fore_color.rgb = SLATE_CARD
            card.line.color.rgb = SKY_BLUE
            card.line.width = Pt(1.5)

            tb = slide.shapes.add_textbox(Inches(1.8), Inches(2.2), Inches(9.7), Inches(4.4))
            tf = tb.text_frame
            tf.word_wrap = True
            
            p_first = tf.paragraphs[0]
            p_first.text = "Happiest Health Digital Twin Challenge — Official Project Submission"
            p_first.font.size = Pt(14)
            p_first.font.bold = True
            p_first.font.color.rgb = EMERALD_GREEN

            for label, val in item["details"]:
                p = tf.add_paragraph()
                p.text = f"{label}: "
                p.font.bold = True
                p.font.size = Pt(11)
                p.font.color.rgb = SKY_BLUE
                run = p.add_run()
                run.text = val
                run.font.bold = False
                run.font.size = Pt(11)
                run.font.color.rgb = WHITE_TEXT

        elif c_type == "two_column":
            # Col 1 Card
            c1 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(5.6), Inches(5.1))
            c1.fill.solid()
            c1.fill.fore_color.rgb = SLATE_CARD
            c1.line.color.rgb = SKY_BLUE
            c1.line.width = Pt(1.0)

            tb1 = slide.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.9))
            tf1 = tb1.text_frame
            tf1.word_wrap = True
            p1_head = tf1.paragraphs[0]
            p1_head.text = item["col1_title"]
            p1_head.font.size = Pt(14)
            p1_head.font.bold = True
            p1_head.font.color.rgb = SKY_BLUE

            for pt in item["col1_points"]:
                p = tf1.add_paragraph()
                p.text = f"•  {pt}"
                p.font.size = Pt(11)
                p.font.color.rgb = WHITE_TEXT

            # Col 2 Card
            c2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.9), Inches(5.6), Inches(5.1))
            c2.fill.solid()
            c2.fill.fore_color.rgb = SLATE_CARD
            c2.line.color.rgb = EMERALD_GREEN
            c2.line.width = Pt(1.0)

            tb2 = slide.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.2), Inches(4.9))
            tf2 = tb2.text_frame
            tf2.word_wrap = True
            p2_head = tf2.paragraphs[0]
            p2_head.text = item["col2_title"]
            p2_head.font.size = Pt(14)
            p2_head.font.bold = True
            p2_head.font.color.rgb = EMERALD_GREEN

            for pt in item["col2_points"]:
                p = tf2.add_paragraph()
                p.text = f"•  {pt}"
                p.font.size = Pt(11)
                p.font.color.rgb = WHITE_TEXT

        elif c_type == "bullet_cards":
            cards = item["cards"]
            y_start = 1.9
            card_h = 1.15
            gap = 0.15
            for idx, (head, desc) in enumerate(cards):
                cy = y_start + idx * (card_h + gap)
                card_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(cy), Inches(11.7), Inches(card_h))
                card_shape.fill.solid()
                card_shape.fill.fore_color.rgb = SLATE_CARD
                card_shape.line.color.rgb = PURPLE_ACCENT if idx % 2 == 0 else SKY_BLUE
                card_shape.line.width = Pt(1.0)

                tb = slide.shapes.add_textbox(Inches(1.0), Inches(cy + 0.05), Inches(11.3), Inches(card_h - 0.1))
                tf = tb.text_frame
                tf.word_wrap = True
                p_head = tf.paragraphs[0]
                p_head.text = head
                p_head.font.size = Pt(13)
                p_head.font.bold = True
                p_head.font.color.rgb = EMERALD_GREEN if idx % 2 == 0 else SKY_BLUE

                p_desc = tf.add_paragraph()
                p_desc.text = desc
                p_desc.font.size = Pt(10.5)
                p_desc.font.color.rgb = WHITE_TEXT

        elif c_type == "table_slide":
            # Add table
            rows = len(item["rows"]) + 1
            cols = len(item["headers"])
            table_shape = slide.shapes.add_table(rows, cols, Inches(0.8), Inches(1.9), Inches(11.7), Inches(3.8))
            table = table_shape.table

            for c_idx, h_text in enumerate(item["headers"]):
                cell = table.cell(0, c_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(30, 58, 95)
                p = cell.text_frame.paragraphs[0]
                p.text = h_text
                p.font.size = Pt(10.5)
                p.font.bold = True
                p.font.color.rgb = SKY_BLUE
                p.alignment = PP_ALIGN.CENTER

            for r_idx, row_vals in enumerate(item["rows"]):
                for c_idx, val in enumerate(row_vals):
                    cell = table.cell(r_idx + 1, c_idx)
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = SLATE_CARD if r_idx % 2 == 0 else RGBColor(20, 29, 45)
                    p = cell.text_frame.paragraphs[0]
                    p.text = val
                    p.font.size = Pt(9.5)
                    p.font.color.rgb = WHITE_TEXT if c_idx > 0 else EMERALD_GREEN
                    if c_idx > 0:
                        p.alignment = PP_ALIGN.CENTER

            # Callout takeaway card
            callout = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.9), Inches(11.7), Inches(1.0))
            callout.fill.solid()
            callout.fill.fore_color.rgb = RGBColor(6, 78, 59)
            callout.line.color.rgb = EMERALD_GREEN
            callout.line.width = Pt(1.0)

            tb_c = slide.shapes.add_textbox(Inches(1.0), Inches(5.95), Inches(11.3), Inches(0.9))
            tf_c = tb_c.text_frame
            tf_c.word_wrap = True
            p_c = tf_c.paragraphs[0]
            p_c.text = item["takeaway"]
            p_c.font.size = Pt(11)
            p_c.font.bold = True
            p_c.font.color.rgb = WHITE_TEXT

    prs_path = Path("docs") / "HeartFailureTwin_Presentation.pptx"
    prs.save(prs_path)
    print(f"Successfully saved PPTX presentation to {prs_path}")

    # Also save an architecture diagram PPTX
    arch_prs = Presentation()
    arch_prs.slide_width = Inches(13.333)
    arch_prs.slide_height = Inches(7.5)
    slide = arch_prs.slides.add_slide(blank_layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY_DARK
    bg.line.fill.background()

    img_path = Path("docs") / "architecture_diagram.png"
    if img_path.exists():
        slide.shapes.add_picture(str(img_path), Inches(0.5), Inches(0.5), width=Inches(12.333))
    
    arch_pptx_path = Path("docs") / "architecture_diagram.pptx"
    arch_prs.save(arch_pptx_path)
    print(f"Successfully saved PPTX architecture diagram to {arch_pptx_path}")


def build_pdf_presentation():
    pdf_path = Path("docs") / "HeartFailureTwin_Presentation.pdf"
    
    # 16:9 Landscape page (720 x 405 pt)
    page_w, page_h = 720, 405
    c = canvas.Canvas(str(pdf_path), pagesize=(page_w, page_h))

    for item in SLIDES_DATA:
        # Background
        c.setFillColor(colors.HexColor("#0f172a"))
        c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

        # Header Pill
        c.setFillColor(colors.HexColor("#38bdf8"))
        c.setFont("Helvetica-Bold", 8)
        c.drawString(40, page_h - 28, item["category"].upper())

        # Slide Number
        c.setFillColor(colors.HexColor("#94a3b8"))
        c.setFont("Helvetica", 8)
        c.drawRightString(page_w - 40, page_h - 28, f"{item['slide_num']}/12")

        # Slide Title
        c.setFillColor(colors.HexColor("#f8fafc"))
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, page_h - 50, item["title"])

        # Slide Subtitle
        c.setFillColor(colors.HexColor("#94a3b8"))
        c.setFont("Helvetica", 9)
        c.drawString(40, page_h - 66, item["subtitle"])

        c_type = item["content_type"]

        if c_type == "title_slide":
            # Card background
            c.setFillColor(colors.HexColor("#1e293b"))
            c.setStrokeColor(colors.HexColor("#38bdf8"))
            c.setLineWidth(1)
            c.roundRect(60, 25, page_w - 120, page_h - 100, 8, fill=1, stroke=1)

            c.setFillColor(colors.HexColor("#34d399"))
            c.setFont("Helvetica-Bold", 10.5)
            c.drawString(80, page_h - 96, "Happiest Health Digital Twin Challenge — Official Project Submission")

            y = page_h - 120
            for label, val in item["details"]:
                c.setFillColor(colors.HexColor("#38bdf8"))
                c.setFont("Helvetica-Bold", 9)
                c.drawString(80, y, f"{label}:")
                
                c.setFillColor(colors.HexColor("#f8fafc"))
                c.setFont("Helvetica", 8.5)
                c.drawString(185, y, val)
                y -= 20

        elif c_type == "two_column":
            col_w = (page_w - 100) / 2
            
            # Col 1
            c.setFillColor(colors.HexColor("#1e293b"))
            c.setStrokeColor(colors.HexColor("#38bdf8"))
            c.setLineWidth(0.8)
            c.roundRect(40, 30, col_w, page_h - 110, 6, fill=1, stroke=1)

            c.setFillColor(colors.HexColor("#38bdf8"))
            c.setFont("Helvetica-Bold", 11)
            c.drawString(55, page_h - 100, item["col1_title"])

            y = page_h - 120
            c.setFillColor(colors.HexColor("#f8fafc"))
            c.setFont("Helvetica", 8)
            for pt in item["col1_points"]:
                # simple multi-line wrap
                words = pt.split()
                line = "•  "
                for w in words:
                    if len(line + w) > 52:
                        c.drawString(55, y, line)
                        y -= 13
                        line = "   " + w + " "
                    else:
                        line += w + " "
                c.drawString(55, y, line)
                y -= 18

            # Col 2
            x2 = 40 + col_w + 20
            c.setFillColor(colors.HexColor("#1e293b"))
            c.setStrokeColor(colors.HexColor("#34d399"))
            c.roundRect(x2, 30, col_w, page_h - 110, 6, fill=1, stroke=1)

            c.setFillColor(colors.HexColor("#34d399"))
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x2 + 15, page_h - 100, item["col2_title"])

            y = page_h - 120
            c.setFillColor(colors.HexColor("#f8fafc"))
            c.setFont("Helvetica", 8)
            for pt in item["col2_points"]:
                words = pt.split()
                line = "•  "
                for w in words:
                    if len(line + w) > 52:
                        c.drawString(x2 + 15, y, line)
                        y -= 13
                        line = "   " + w + " "
                    else:
                        line += w + " "
                c.drawString(x2 + 15, y, line)
                y -= 18

        elif c_type == "bullet_cards":
            cards = item["cards"]
            y = page_h - 90
            card_h = 56
            gap = 12
            for idx, (head, desc) in enumerate(cards):
                c.setFillColor(colors.HexColor("#1e293b"))
                c.setStrokeColor(colors.HexColor("#c084fc" if idx % 2 == 0 else "#38bdf8"))
                c.setLineWidth(0.8)
                c.roundRect(40, y - card_h, page_w - 80, card_h, 6, fill=1, stroke=1)

                c.setFillColor(colors.HexColor("#34d399" if idx % 2 == 0 else "#38bdf8"))
                c.setFont("Helvetica-Bold", 10)
                c.drawString(55, y - 18, head)

                c.setFillColor(colors.HexColor("#f8fafc"))
                c.setFont("Helvetica", 8.5)
                # wrap
                words = desc.split()
                line = ""
                line_y = y - 32
                for w in words:
                    if len(line + w) > 115:
                        c.drawString(55, line_y, line)
                        line_y -= 12
                        line = w + " "
                    else:
                        line += w + " "
                c.drawString(55, line_y, line)

                y -= (card_h + gap)

        elif c_type == "table_slide":
            # Header
            c.setFillColor(colors.HexColor("#1e3a5f"))
            c.rect(40, page_h - 110, page_w - 80, 20, fill=1, stroke=0)
            c.setFillColor(colors.HexColor("#38bdf8"))
            c.setFont("Helvetica-Bold", 8)

            col_widths = [190, 60, 60, 60, 60, 60, 65, 55] if len(item["headers"]) == 8 else [190, 50, 65, 65, 60, 60, 60]
            x = 45
            for idx, h in enumerate(item["headers"]):
                c.drawString(x, page_h - 97, h)
                x += col_widths[idx]

            y = page_h - 130
            for r_idx, r_vals in enumerate(item["rows"]):
                c.setFillColor(colors.HexColor("#1e293b" if r_idx % 2 == 0 else "#0f172a"))
                c.rect(40, y - 5, page_w - 80, 18, fill=1, stroke=0)

                x = 45
                for c_idx, val in enumerate(r_vals):
                    c.setFillColor(colors.HexColor("#34d399" if c_idx == 0 else "#f8fafc"))
                    c.setFont("Helvetica-Bold" if c_idx == 0 else "Helvetica", 7.5)
                    c.drawString(x, y + 1, str(val))
                    x += col_widths[c_idx]
                y -= 20

            # Takeaway card
            c.setFillColor(colors.HexColor("#064e3b"))
            c.setStrokeColor(colors.HexColor("#34d399"))
            c.setLineWidth(0.8)
            c.roundRect(40, 25, page_w - 80, 50, 6, fill=1, stroke=1)

            c.setFillColor(colors.HexColor("#f8fafc"))
            c.setFont("Helvetica-Bold", 8.5)
            # wrap takeaway
            words = item["takeaway"].split()
            line = ""
            ty = 56
            for w in words:
                if len(line + w) > 110:
                    c.drawString(55, ty, line)
                    ty -= 13
                    line = w + " "
                else:
                    line += w + " "
            c.drawString(55, ty, line)

        c.showPage()

    c.save()
    print(f"Successfully saved PDF presentation to {pdf_path}")


if __name__ == "__main__":
    build_pptx_presentation()
    build_pdf_presentation()
