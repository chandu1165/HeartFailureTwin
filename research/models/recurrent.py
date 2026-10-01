"""PyTorch Temporal Recurrent (GRU/LSTM) baseline model for physiological sequences.
"""
import torch
import torch.nn as nn
import numpy as np

class PhysiologicalGRU(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 32, num_layers: int = 1, dropout: float = 0.2):
        super().__init__()
        self.gru = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, 16),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, seq_len, input_dim)
        out, _ = self.gru(x)
        # Take the last time step embedding
        last_step = out[:, -1, :]
        prob = self.classifier(last_step).squeeze(-1)
        return prob
