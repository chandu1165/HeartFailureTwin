"""Multimodal Digital Twin Latent State Estimator (PyTorch).
Fuses EHR, ECG, Wearable SCG, and Personalized Deviations into latent physiological state S(t).
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Tuple, List, Optional

class MultimodalStateEstimator(nn.Module):
    """Deep Multimodal Fusion network estimating the latent Digital Twin state S(t)."""
    
    def __init__(
        self,
        ehr_dim: int = 15,
        ecg_dim: int = 6,
        wearable_dim: int = 11,
        dev_dim: int = 9,
        latent_state_dim: int = 8
    ):
        super().__init__()
        self.latent_state_dim = latent_state_dim
        
        # 1. Modality Encoders
        self.ehr_encoder = nn.Sequential(
            nn.Linear(ehr_dim, 24),
            nn.BatchNorm1d(24),
            nn.ReLU(),
            nn.Linear(24, 16),
            nn.ReLU()
        )
        
        self.ecg_encoder = nn.Sequential(
            nn.Linear(ecg_dim, 24),
            nn.BatchNorm1d(24),
            nn.ReLU(),
            nn.Linear(24, 16),
            nn.ReLU()
        )
        
        self.wearable_encoder = nn.Sequential(
            nn.Linear(wearable_dim, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU()
        )
        
        self.deviation_encoder = nn.Sequential(
            nn.Linear(dev_dim, 24),
            nn.BatchNorm1d(24),
            nn.ReLU(),
            nn.Linear(24, 16),
            nn.ReLU()
        )
        
        # 2. Gated Cross-Modal Fusion
        # Concatenate 4 modal embeddings (16 * 4 = 64)
        total_modal_dim = 16 * 4
        self.gate_network = nn.Sequential(
            nn.Linear(total_modal_dim, 64),
            nn.ReLU(),
            nn.Linear(64, total_modal_dim),
            nn.Sigmoid()
        )
        
        # 3. Latent State Projector -> S(t) in R^8
        self.state_projector = nn.Sequential(
            nn.Linear(total_modal_dim, 32),
            nn.ReLU(),
            nn.Linear(32, latent_state_dim),
            nn.Tanh() # Normalized latent physiological state in [-1, +1]^8
        )
        
        # 4. Multi-Task Heads from S(t)
        # Task 1: Decompensation Risk P(t)
        self.risk_head = nn.Sequential(
            nn.Linear(latent_state_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        
        # Task 2: Auxiliary Hemodynamics (PAP, PCWP) estimation
        self.hemodynamic_head = nn.Sequential(
            nn.Linear(latent_state_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 2) # [est_PAM, est_PCWM]
        )

    def forward(
        self,
        ehr_x: torch.Tensor,
        ecg_x: torch.Tensor,
        wearable_x: torch.Tensor,
        dev_x: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Forward pass.
        
        Returns:
            latent_state S(t): shape (batch, 8)
            decomp_risk P(t): shape (batch, 1)
            hemodynamic_est: shape (batch, 2)
        """
        # Encode modalities
        e_ehr = self.ehr_encoder(ehr_x)
        e_ecg = self.ecg_encoder(ecg_x)
        e_wear = self.wearable_encoder(wearable_x)
        e_dev = self.deviation_encoder(dev_x)
        
        # Concatenate
        combined = torch.cat([e_ehr, e_ecg, e_wear, e_dev], dim=-1)
        
        # Gating
        gates = self.gate_network(combined)
        gated_repr = combined * gates
        
        # Project to Latent Digital Twin State
        s_t = self.state_projector(gated_repr)
        
        # Predictions
        risk = self.risk_head(s_t)
        hemodynamics = self.hemodynamic_head(s_t)
        
        return s_t, risk, hemodynamics
