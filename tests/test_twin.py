"""Unit and integration tests for HeartFailureTwin core engine.
"""
import pytest
from twin import HeartFailureTwin, PatientProfile, PhysiologicalSnapshot

def test_twin_lifecycle_and_simulation():
    twin = HeartFailureTwin()

    profile = PatientProfile(
        patient_id="HF-104",
        age=64.0,
        gender="Male",
        nyha_class=3,
        hf_subtype="HFrEF",
        bmi=28.4,
        baseline_sbp=118.0,
        baseline_dbp=74.0,
        hypertension=True,
        diabetes=False,
        cad=True,
        ckd=False,
        prior_hospitalization=True
    )
    twin.initialize_patient(profile)

    snap = PhysiologicalSnapshot(
        timestamp_sec=3600.0,
        heart_rate_bpm=92.0,
        hrv_rmssd_ms=18.0,
        hrv_sdnn_ms=25.0,
        scg_mechanical_energy=11.2,
        scg_dorso_ventral_rms=9.1,
        respiration_rate_bpm=22.0,
        pleth_amplitude=1.4,
        skin_temp_celsius=35.1,
        quality_ecg=0.92,
        quality_scg=0.88,
        quality_overall=0.90
    )

    state = twin.update_state("HF-104", snap)
    assert state.patient_id == "HF-104"
    assert 0.0 <= state.risk_score <= 1.0
    assert len(state.state_vector) == 8
    assert "now" in state.forecast_trajectory
    assert "24h" in state.forecast_trajectory
    assert len(state.contributing_factors) > 0

    # What-if simulation
    sim_res = twin.simulate_what_if("HF-104", {"heart_rate_bpm": -18.0, "respiration_rate_bpm": -5.0})
    assert "original_risk" in sim_res
    assert "simulated_risk" in sim_res
    assert "disclaimer" in sim_res

if __name__ == "__main__":
    test_twin_lifecycle_and_simulation()
    print("All tests passed successfully!")
