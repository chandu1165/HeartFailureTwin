"""Temporal State Transition Model: S(t) -> S(t+1).
Autoregressively forecasts future Digital Twin states across temporal horizons.
"""
import torch
import torch.nn as nn
from typing import List, Dict, Any, Tuple

class DigitalTwinTransitionModel(nn.Module):
    """Models temporal state transitions: S(t+1) = S(t) + f(S(t), Delta_t)."""
    
    def __init__(self, state_dim: int = 8, hidden_dim: int = 32):
        super().__init__()
        self.state_dim = state_dim
        
        # Neural ODE / residual transition dynamics network
        self.transition_net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, state_dim)
        )
        
        # Trajectory deterioration risk head
        self.trajectory_risk_head = nn.Sequential(
            nn.Linear(state_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

    def forward(self, s_t: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Single-step transition: predicts delta S and future risk."""
        delta_s = self.transition_net(s_t)
        s_next = torch.clamp(s_t + delta_s, -1.0, 1.0)
        risk_next = self.trajectory_risk_head(s_next)
        return s_next, risk_next

    def forecast_trajectory(self, initial_state: torch.Tensor, steps: int = 5) -> List[Dict[str, float]]:
        """Unroll state transition model over future time steps.
        
        Returns:
            List of dicts: [{'step': 0, 'risk': r0, 'stability': s0}, ...]
        """
        self.eval()
        trajectory = []
        curr_s = initial_state.clone()
        
        with torch.no_grad():
            curr_risk = float(self.trajectory_risk_head(curr_s).item())
            # Overall stability is inversely related to norm of extreme state dimensions
            stability = float(1.0 - torch.clamp(torch.norm(curr_s, p=2) / 2.828, 0.0, 1.0).item())
            trajectory.append({
                "step": 0,
                "horizon_hours": 0.0,
                "risk": round(curr_risk, 4),
                "stability": round(stability, 3)
            })
            
            for step in range(1, steps + 1):
                curr_s, next_risk = self.forward(curr_s)
                risk_val = float(next_risk.item())
                stab_val = float(1.0 - torch.clamp(torch.norm(curr_s, p=2) / 2.828, 0.0, 1.0).item())
                trajectory.append({
                    "step": step,
                    "horizon_hours": round(step * 4.8, 1), # e.g. steps 1-5 map to ~5h to 24h
                    "risk": round(risk_val, 4),
                    "stability": round(stab_val, 3)
                })
                
        return trajectory
