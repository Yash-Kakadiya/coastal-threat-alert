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

# backend/app.py
"""
Coastal Threat Alert System — FastAPI Entrypoint
================================================

Purpose
-------
Expose minimal, clean endpoints to:
1) Report service health
2) Score an on-demand sensor payload (strict schema)
3) Read the latest processed CSV row and return a threat score + raw values

Conventions
-----------
- Returns IST timestamps (Asia/Kolkata) in ISO 8601 with offset.
- Reads processed dataset from: backend/data/processed/cleaned_weather.csv
- Maps dataset columns into the keys expected by `calculate_threat_score`.
- Keeps endpoints small, explicit, and production-friendly for hackathon velocity.

Run (from repo root)
--------------------
    pip install -r backend/requirements.txt
    uvicorn backend.app:app --reload --port 8000

Health Check
------------
    GET http://127.0.0.1:8000/health  ->  {"status":"🌊 Coastal Lightweight health probe for uptime checks API is running!"}
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError, model_validator

# Relative import because this file lives inside the `backend` package
from .threat_model import calculate_threat_score

# ---- Constants --------------------------------------------------------------

PROCESSED_CSV = Path("backend/data/processed/cleaned_weather.csv")

# Preferred processed (snake_case) column names per your pipeline
SNAKE_CASE_MAP = {
    "station_name": "station_name",
    "measurement_timestamp": "measurement_timestamp",
    "wind_speed": "wind_speed",
    "maximum_wind_speed": "maximum_wind_speed",
    "humidity": "humidity",
    "rain_intensity": "rain_intensity",
    "barometric_pressure": "barometric_pressure",
}

# Fallback for legacy Title Case (in case processed file still has them)
TITLE_CASE_MAP = {
    "Station Name": "station_name",
    "Measurement Timestamp": "measurement_timestamp",
    "Wind Speed": "wind_speed",
    "Maximum Wind Speed": "maximum_wind_speed",
    "Humidity": "humidity",
    "Rain Intensity": "rain_intensity",
    "Barometric Pressure": "barometric_pressure",
}

IST_TZ = "Asia/Kolkata"  # for timestamps


# ---- Pydantic Models --------------------------------------------------------


class ThreatScoreRequest(BaseModel):
    """
    Strict schema for scoring a single sensor payload.
    Only these five fields are accepted.
    """

    wind_speed: float = Field(
        ..., description="Mean wind speed (m/s or km/h; must match thresholds' units)"
    )
    maximum_wind_speed: float = Field(..., description="Max gust speed over interval")
    humidity: float = Field(
        ..., ge=0, le=100, description="Relative humidity in percent"
    )
    rain_intensity: float = Field(
        ..., ge=0, description="Rain intensity (unit as defined in config)"
    )
    barometric_pressure: float = Field(
        ..., description="Pressure (hPa or mbar; must match thresholds' units)"
    )

    @model_validator(mode="after")
    def _sanity(self) -> "ThreatScoreRequest":
        # Add any lightweight cross-field checks here if needed.
        return self


class ThreatScoreResponse(BaseModel):
    score: float
    level: str
    parameters: Dict[str, int]


class LatestThreatResponse(ThreatScoreResponse):
    raw: Dict[str, Optional[float | str]]


# ---- FastAPI App ------------------------------------------------------------

app = FastAPI(
    title="Coastal Threat Alert API",
    description="Early warning API for coastal threats — rule-based v1",
    version="1.0.0",
)


# ---- Utilities --------------------------------------------------------------


def _localize_to_ist(ts: Optional[str | pd.Timestamp]) -> Optional[str]:
    """
    Convert an input timestamp (string or pandas Timestamp) to ISO 8601 in IST (+05:30).
    If ts is None or parsing fails, returns None.
    """
    if ts is None:
        return None
    try:
        # Parse with pandas (robust to many formats)
        dt = pd.to_datetime(ts, utc=True, errors="coerce")
        if pd.isna(dt):
            # Maybe it's already tz-aware/naive local time
            dt = pd.to_datetime(ts, errors="coerce")
        if pd.isna(dt):
            return None
        # Localize/convert to IST
        # If naive -> assume UTC first (dataset usually UTC), then convert
        if dt.tzinfo is None or dt.tz is None:
            dt = dt.tz_localize("UTC")
        dt_ist = dt.tz_convert(IST_TZ)
        return dt_ist.isoformat()
    except Exception:
        return None


def _load_latest_reading() -> Dict[str, Optional[float | str]]:
    """
    Load last row from processed CSV and map columns to model keys.
    Supports both snake_case (preferred) and legacy Title Case columns.

    Returns a dict with:
        {
          "station_name": str | None,
          "timestamp": ISO8601 IST | None,
          "wind_speed": float | None,
          "maximum_wind_speed": float | None,
          "humidity": float | None,
          "rain_intensity": float | None,
          "barometric_pressure": float | None
        }
    """
    if not PROCESSED_CSV.exists():
        raise HTTPException(
            status_code=404, detail="Processed dataset not found. Run data_prep first."
        )

    try:
        df = pd.read_csv(PROCESSED_CSV)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read processed CSV: {e}"
        )

    if df.empty:
        raise HTTPException(status_code=404, detail="Processed CSV is empty.")

    latest = df.iloc[-1]

    # Decide which mapping to use by checking column presence
    if set(SNAKE_CASE_MAP.keys()).intersection(df.columns):
        # Processed file has snake_case columns
        get = lambda col: latest.get(col, None)
        station_name = get("station_name")
        stamp = get("measurement_timestamp")
        reading = {
            "station_name": station_name if pd.notna(station_name) else None,
            "timestamp": _localize_to_ist(stamp),
            "wind_speed": (
                float(get("wind_speed")) if pd.notna(get("wind_speed")) else None
            ),
            "maximum_wind_speed": (
                float(get("maximum_wind_speed"))
                if pd.notna(get("maximum_wind_speed"))
                else None
            ),
            "humidity": float(get("humidity")) if pd.notna(get("humidity")) else None,
            "rain_intensity": (
                float(get("rain_intensity"))
                if pd.notna(get("rain_intensity"))
                else None
            ),
            "barometric_pressure": (
                float(get("barometric_pressure"))
                if pd.notna(get("barometric_pressure"))
                else None
            ),
        }
    else:
        # Fallback to Title Case mapping
        get = lambda col: latest.get(col, None)
        station_name = get("Station Name")
        stamp = get("Measurement Timestamp")
        reading = {
            "station_name": station_name if pd.notna(station_name) else None,
            "timestamp": _localize_to_ist(stamp),
            "wind_speed": (
                float(get("Wind Speed")) if pd.notna(get("Wind Speed")) else None
            ),
            "maximum_wind_speed": (
                float(get("Maximum Wind Speed"))
                if pd.notna(get("Maximum Wind Speed"))
                else None
            ),
            "humidity": float(get("Humidity")) if pd.notna(get("Humidity")) else None,
            "rain_intensity": (
                float(get("Rain Intensity"))
                if pd.notna(get("Rain Intensity"))
                else None
            ),
            "barometric_pressure": (
                float(get("Barometric Pressure"))
                if pd.notna(get("Barometric Pressure"))
                else None
            ),
        }

    return reading


def _to_model_row(raw: Dict[str, Optional[float | str]]) -> Dict[str, float]:
    """
    Convert a 'raw' reading dict into the minimal row dict expected by `calculate_threat_score`.
    Missing values default to 0.0 (conservative safe-side for rule-based).
    """
    return {
        "wind_speed": float(raw.get("wind_speed") or 0.0),
        "maximum_wind_speed": float(raw.get("maximum_wind_speed") or 0.0),
        "humidity": float(raw.get("humidity") or 0.0),
        "rain_intensity": float(raw.get("rain_intensity") or 0.0),
        "barometric_pressure": float(raw.get("barometric_pressure") or 0.0),
    }


# ---- Endpoints --------------------------------------------------------------


@app.get("/health")
def health() -> Dict[str, str]:
    """
    Lightweight health probe for uptime checks.
    """
    return {
        "status": "🌊 Coastal Lightweight health probe for uptime checks API is running!"
    }


@app.post("/threat/score", response_model=ThreatScoreResponse)
def score_threat(payload: ThreatScoreRequest) -> ThreatScoreResponse:
    """
    Score an ad-hoc sensor reading with strict validation.

    Request Body
    -----------
    {
      "wind_speed": 12.5,
      "maximum_wind_speed": 20.0,
      "humidity": 80.2,
      "rain_intensity": 0.5,
      "barometric_pressure": 1002.1
    }

    Response
    --------
    {
      "score": 41.7,
      "level": "Caution",
      "parameters": {"wind_speed": 1, ...}
    }
    """
    try:
        row = payload.model_dump()
        result = calculate_threat_score(row)
        return ThreatScoreResponse(**result)
    except ValidationError as e:
        # Should rarely trigger because FastAPI validates before handler
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {e}")


@app.get("/threat/latest", response_model=LatestThreatResponse)
def threat_latest() -> LatestThreatResponse:
    """
    Read the latest row from the processed CSV, compute threat score,
    and return both the score and the raw values used (incl. station & IST timestamp).

    Response Example
    ----------------
    {
      "score": 72.5,
      "level": "Warning",
      "parameters": {...},
      "raw": {
        "station_name": "PORBANDAR",
        "timestamp": "2025-08-30T12:30:00+05:30",
        "wind_speed": 16.2,
        "maximum_wind_speed": 25.1,
        "humidity": 84.0,
        "rain_intensity": 1.2,
        "barometric_pressure": 995.0
      }
    }
    """
    raw = _load_latest_reading()
    row = _to_model_row(raw)
    result = calculate_threat_score(row)
    return LatestThreatResponse(**result, raw=raw)
