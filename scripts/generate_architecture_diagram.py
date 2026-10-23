"""
Generates publication-quality Architecture Diagram in both PDF and PNG formats.
HeartFailureTwin: A Personalized Multimodal Digital Twin for Early Forecasting of Heart-Failure Decompensation.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

def generate_architecture_diagram():
    output_dir = Path("docs")
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / "architecture_diagram.pdf"
    png_path = output_dir / "architecture_diagram.png"

    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor('#0f172a') # Slate 900 dark theme
    ax.set_facecolor('#0f172a')

    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title Banner
    ax.text(8.0, 9.6, "HeartFailureTwin: End-to-End System Architecture", 
            fontsize=20, weight='bold', color='#f8fafc', ha='center', va='center')
    ax.text(8.0, 9.2, "From Multimodal Waveforms & EHR to Patient-Specific Digital Twin Trajectory Forecasting", 
            fontsize=11, color='#94a3b8', ha='center', va='center')

    # Color Palette
    c_ingest = '#1e293b'     # slate 800
    c_preproc = '#1e3a5f'    # deep blue
    c_base = '#064e3b'       # emerald 900
    c_twin = '#4c1d95'       # purple 900
    c_pred = '#701a75'       # fuchsia 900
    c_ui = '#14532d'         # green 900
    
    border_blue = '#38bdf8'  # sky 400
    border_emerald = '#34d399' # emerald 400
    border_purple = '#c084fc' # purple 400
    border_rose = '#fb7185'   # rose 400
    border_cyan = '#22d3ee'   # cyan 400

    def draw_box(x, y, w, h, bg, border, title, desc, title_color='#f8fafc', desc_color='#cbd5e1'):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12,rounding_size=0.15",
                                     linewidth=1.5, edgecolor=border, facecolor=bg)
        ax.add_patch(rect)
        if desc:
            ax.text(x + w/2, y + h*0.68, title, fontsize=10, weight='bold', color=title_color, ha='center', va='center')
            ax.text(x + w/2, y + h*0.35, desc, fontsize=7.5, color=desc_color, ha='center', va='center', multialignment='center')
        else:
            ax.text(x + w/2, y + h*0.5, title, fontsize=10, weight='bold', color=title_color, ha='center', va='center')

    def draw_arrow(x1, y1, x2, y2, color='#64748b', style='->', lw=1.5):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle=style, color=color, lw=lw, 
                                   shrinkA=4, shrinkB=4, mutation_scale=12))

    # --- ROW 1: S1 Data Ingestion & Provenance (x: 0.8 to 15.2, y: 7.2 to 8.7) ---
    s1_rect = patches.FancyBboxPatch((0.6, 7.2), 14.8, 1.6, boxstyle="round,pad=0.1,rounding_size=0.2",
                                     linewidth=1.0, edgecolor='#475569', facecolor='#090d16', linestyle='--')
    ax.add_patch(s1_rect)
    ax.text(0.8, 8.6, "LAYER 1: DATA INGESTION & CLINICAL PROVENANCE", fontsize=8.5, weight='bold', color='#38bdf8')

    draw_box(1.0, 7.4, 3.2, 0.95, c_ingest, border_blue, "Historical EHR & Clinical", "Demographics, Comorbidities,\nLab History, Prior HF (MIMIC/EHR)", '#38bdf8')
    draw_box(4.6, 7.4, 3.2, 0.95, c_ingest, border_blue, "Wearable ECG (500 Hz)", "Lead-II Waveform, R-peaks,\nRR intervals (PhysioNet SCG-RHC)", '#38bdf8')
    draw_box(8.2, 7.4, 3.2, 0.95, c_ingest, border_blue, "Tri-Axial SCG (500 Hz)", "Chest Wall Seismocardiography,\nMechanics & Contractility Force", '#38bdf8')
    draw_box(11.8, 7.4, 3.2, 0.95, c_ingest, border_blue, "Wearable Hemodynamics", "Photoplethysmography (PPG),\nRespiration & Skin Temperature", '#38bdf8')

    # Arrows Down to Layer 2
    draw_arrow(2.6, 7.4, 2.6, 6.4, color='#38bdf8')
    draw_arrow(6.2, 7.4, 6.2, 6.4, color='#38bdf8')
    draw_arrow(9.8, 7.4, 9.8, 6.4, color='#38bdf8')
    draw_arrow(13.4, 7.4, 13.4, 6.4, color='#38bdf8')

    # --- ROW 2: S2 Feature Engineering & Signal Quality (y: 5.2 to 6.4) ---
    s2_rect = patches.FancyBboxPatch((0.6, 5.0), 14.8, 1.6, boxstyle="round,pad=0.1,rounding_size=0.2",
                                     linewidth=1.0, edgecolor='#475569', facecolor='#090d16', linestyle='--')
    ax.add_patch(s2_rect)
    ax.text(0.8, 6.4, "LAYER 2: SIGNAL QUALITY AUDIT & PHYSIOLOGICAL PREPROCESSING", fontsize=8.5, weight='bold', color='#22d3ee')

    draw_box(1.0, 5.2, 3.2, 0.95, c_preproc, border_cyan, "Clinical Profiler (ehr.py)", "NYHA Stage, Charlson Index,\nHypertension, Diabetes Encoding", '#22d3ee')
    draw_box(4.6, 5.2, 3.2, 0.95, c_preproc, border_cyan, "HRV & Peak Extractor (ecg.py)", "Bandpass 0.5-40Hz, R-Peak Detection,\nRMSSD, SDNN, Heart Rate (bpm)", '#22d3ee')
    draw_box(8.2, 5.2, 3.2, 0.95, c_preproc, border_cyan, "Kinetics & Acoustics (wearable.py)", "SCG RMS Energy, Dorso-ventral Force,\nSpectral Centroid, Bandpass 1-40Hz", '#22d3ee')
    draw_box(11.8, 5.2, 3.2, 0.95, c_preproc, border_cyan, "Quality Guard (quality.py)", "Signal-to-Noise Ratio (SNR),\nClipping & Lead-Off [0.0 - 1.0]", '#22d3ee')

    # Arrows to Layer 3 (Baseline Engine) and Fusion
    draw_arrow(6.2, 5.2, 8.0, 4.4, color='#34d399')
    draw_arrow(9.8, 5.2, 8.0, 4.4, color='#34d399')

    # --- ROW 3: S3 Personalization Baseline Engine (y: 3.5 to 4.4) ---
    s3_rect = patches.FancyBboxPatch((4.0, 3.3), 8.0, 1.3, boxstyle="round,pad=0.1,rounding_size=0.2",
                                     linewidth=1.2, edgecolor=border_emerald, facecolor=c_base)
    ax.add_patch(s3_rect)
    ax.text(8.0, 4.25, "LAYER 3: PATIENT-SPECIFIC BASELINE ENGINE (baseline.py)", fontsize=10, weight='bold', color='#34d399', ha='center')
    ax.text(8.0, 3.75, "Individual Baseline Calibration Envelopes:  μ_i (rest),  σ_i (dispersion)\nPersonalized Z-Score Deviations:  Δz_{i,t} = (x_{i,t} - μ_i) / σ_i   (Zero-Leakage)", 
            fontsize=8.5, color='#e2e8f0', ha='center')

    # Arrows Down to Layer 4 (Fusion)
    draw_arrow(2.6, 5.2, 4.0, 2.7, color='#c084fc')
    draw_arrow(8.0, 3.3, 8.0, 2.8, color='#c084fc')
    draw_arrow(13.4, 5.2, 11.5, 2.7, color='#c084fc')

    # --- ROW 4: S4 Multimodal Gated Fusion & Latent Twin State (y: 1.8 to 2.8) ---
    s4_rect = patches.FancyBboxPatch((2.2, 1.8), 11.6, 1.1, boxstyle="round,pad=0.1,rounding_size=0.2",
                                     linewidth=1.5, edgecolor=border_purple, facecolor=c_twin)
    ax.add_patch(s4_rect)
    ax.text(8.0, 2.65, "LAYER 4: CROSS-MODAL GATED FUSION & LATENT TWIN STATE (state_estimator.py)", fontsize=10, weight='bold', color='#e9d5ff', ha='center')
    ax.text(8.0, 2.15, "Non-Linear Gated Attention Fusion  |  Modality Embeddings d=16  |  Quality-Weighted Gating\nLatent State Space:  S(t) ∈ [-1, +1]^8  (Normalized Physiological Twin State)", 
            fontsize=8.5, color='#f1f5f9', ha='center')

    # Arrows Down to Layer 5
    draw_arrow(4.5, 1.8, 3.2, 1.15, color='#fb7185')
    draw_arrow(8.0, 1.8, 8.0, 1.15, color='#fb7185')
    draw_arrow(11.5, 1.8, 12.8, 1.15, color='#fb7185')

    # --- ROW 5: S5 Temporal Dynamics, Forecasting & Doctor UI (y: 0.2 to 1.15) ---
    draw_box(0.8, 0.2, 4.2, 0.95, c_pred, border_rose, "Trajectory Forecast (state_transition.py)", 
             "Neural ODE Transition S(t) -> S(t+1)\nHorizon: 6h, 12h, 24h Decompensation Risk", '#fb7185')
    
    draw_box(5.8, 0.2, 4.4, 0.95, c_pred, border_rose, "In Silico What-If Engine (simulation.py)", 
             "Counterfactual Trajectory Simulation\n(Diuretic Titration, Beta-Blockade, Stress)", '#fb7185')
    
    draw_box(11.0, 0.2, 4.2, 0.95, c_ui, '#4ade80', "Doctor Dashboard (React + FastAPI)", 
             "Cohort View, 4D Twin Replay (0-72h),\nEarly-Warning Radar & Transparent XAI", '#4ade80')

    # Connect forecast & simulation to UI
    draw_arrow(5.0, 0.65, 5.8, 0.65, color='#4ade80')
    draw_arrow(10.2, 0.65, 11.0, 0.65, color='#4ade80')

    plt.tight_layout()
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Successfully generated {pdf_path} and {png_path}")

if __name__ == "__main__":
    generate_architecture_diagram()
