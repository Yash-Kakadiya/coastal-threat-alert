# """
# FastAPI backend skeleton for Coastal Threat Alert System.
# Run (from repo root):
#     pip install -r backend/requirements.txt
#     uvicorn backend.app:app --reload --port 7777
# """

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import Optional, Dict, Any
# from .threat_model import calculate_threat_score

# app = FastAPI(title="Coastal Threat Alert - Backend")


# class ThreatRequest(BaseModel):
#     location_id: str
#     timestamp: Optional[str] = None  # ISO 8601; if None return latest
#     # optionally allow raw sensor override for quick testing:
#     sensor_override: Optional[Dict[str, Any]] = None


# @app.get("/health")
# def health():
#     return {"status": "ok"}


# @app.post("/get_threat_level")
# def get_threat_level(req: ThreatRequest):
#     """
#     Return threat score and explanation.

#     For initial commit this uses the sensor_override payload if provided.
#     Later this endpoint should load the latest processed sensor data for location.
#     """
#     # For the first commit, require sensor_override for deterministic demo
#     if not req.sensor_override:
#         raise HTTPException(
#             status_code=400,
#             detail="Provide sensor_override for demo or implement data loader.",
#         )

#     sensor_payload = req.sensor_override
#     # compute score
#     result = calculate_threat_score(sensor_payload)
#     # augment with requested metadata
#     result["location_id"] = req.location_id
#     result["timestamp"] = req.timestamp or sensor_payload.get("timestamp")
#     return result
# backend/app.py
"""
FastAPI entrypoint for Coastal Threat Alert backend.
Exposes endpoints to calculate threat scores from weather data or from dataset.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import pandas as pd

from backend.threat_model import calculate_threat_score


# Initialize FastAPI app
app = FastAPI(
    title="Coastal Threat Alert API",
    description="API for assessing coastal weather threats",
    version="1.0.0",
)


# ---------- Input Schema ----------
class WeatherData(BaseModel):
    wind_speed: float
    maximum_wind_speed: float
    humidity: float
    rain_intensity: float
    barometric_pressure: float


# ---------- Endpoints ----------
@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "🌊 Coastal Threat Alert API is running!"}


@app.post("/get_threat_level")
def get_threat_level(data: WeatherData):
    """
    Endpoint to calculate the coastal threat level.
    """
    reading = {
        "wind_speed": data.wind_speed,
        "maximum_wind_speed": data.maximum_wind_speed,
        "humidity": data.humidity,
        "rain_intensity": data.rain_intensity,
        "barometric_pressure": data.barometric_pressure,
    }

    result = calculate_threat_score(reading)
    return result


@app.get("/get_threat_from_csv")
def get_threat_from_csv():
    """
    Load the latest cleaned row from processed CSV
    and calculate threat score.
    """
    csv_path = Path("backend/data/processed/cleaned_weather.csv")

    if not csv_path.exists():
        return {"error": "Processed dataset not found. Run data_prep first."}

    df = pd.read_csv(csv_path)

    if df.empty:
        return {"error": "CSV is empty."}

    # Take the latest row
    latest_row = df.iloc[-1]

    # Map dataset columns to expected keys
    reading = {
        "wind_speed": latest_row.get("Wind Speed", 0),
        "maximum_wind_speed": latest_row.get("Maximum Wind Speed", 0),
        "humidity": latest_row.get("Humidity", 0),
        "rain_intensity": latest_row.get("Rain Intensity", 0),
        "barometric_pressure": latest_row.get("Barometric Pressure", 0),
    }

    result = calculate_threat_score(reading)
    return {"latest_reading": reading, "threat": result}
