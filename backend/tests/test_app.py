"""
Pytest tests for the FastAPI application using the official TestClient.
"""

# --- FIX: Import TestClient from FastAPI instead of httpx.AsyncClient ---
from fastapi.testclient import TestClient
import pandas as pd
from unittest.mock import patch

# Import the FastAPI app instance from your application file
from backend.app import app

# --- FIX: Create a single, synchronous TestClient instance ---
client = TestClient(app)


# --- FIX: Removed @pytest.mark.asyncio and async/await keywords ---
def test_health_endpoint():
    """Tests the /health endpoint for a 200 OK response."""
    # Use the client to make a request
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_threat_score_endpoint():
    """Tests the POST /threat/score endpoint with a valid custom payload."""
    payload = {
        "wind_speed": 18,
        "maximum_wind_speed": 22,
        "humidity": 80,
        "rain_intensity": 3,
        "barometric_pressure": 995,
    }
    response = client.post("/threat/score", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "level" in data
    assert "parameters" in data
    assert "raw" in data
    assert data["raw"]["wind_speed"] == payload["wind_speed"]


def test_latest_threat_endpoint():
    """
    Tests the GET /threat/latest endpoint.
    This test uses a mock to avoid actual file I/O.
    """
    mock_data = {
        "measurement_timestamp": ["2025-08-30 12:00:00"],
        "air_temperature": [28.5],
        "humidity": [88],
        "rain_intensity": [5.0],
        "wind_speed": [25.0],
        "maximum_wind_speed": [35.0],
        "barometric_pressure": [992.0],
    }
    mock_df = pd.DataFrame(mock_data)

    with patch("backend.app.pd.read_csv", return_value=mock_df):
        response = client.get("/threat/latest")

    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "level" in data
    assert "raw" in data
    assert data["raw"]["wind_speed"] == 25.0
