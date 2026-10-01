"""Test FastAPI backend endpoints using TestClient.
"""
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_cohort():
    response = client.get("/api/cohort")
    assert response.status_code == 200
    data = response.json()
    assert "cohort" in data
    assert len(data["cohort"]) > 0

def test_patient_profile():
    response = client.get("/api/patients/HF-104")
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == "HF-104"
    assert "baseline_ranges" in data

def test_patient_timeline():
    response = client.get("/api/patients/HF-104/timeline")
    assert response.status_code == 200
    data = response.json()
    assert "timeline" in data
    assert len(data["timeline"]) > 0

def test_patient_state():
    response = client.get("/api/patients/HF-104/state")
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "state_label" in data
    assert "forecast_trajectory" in data

def test_simulation():
    req_body = {
        "adjustments": {
            "heart_rate_bpm": -15.0,
            "respiration_rate_bpm": -4.0
        }
    }
    response = client.post("/api/patients/HF-104/simulate", json=req_body)
    assert response.status_code == 200
    data = response.json()
    assert "simulated_risk" in data
    assert "disclaimer" in data

def test_benchmarks():
    response = client.get("/api/benchmarks")
    assert response.status_code == 200
    data = response.json()
    assert "baselines" in data
    assert "ablation_study" in data

if __name__ == "__main__":
    test_health()
    test_cohort()
    test_patient_profile()
    test_patient_timeline()
    test_patient_state()
    test_simulation()
    test_benchmarks()
    print("All API tests passed successfully!")
