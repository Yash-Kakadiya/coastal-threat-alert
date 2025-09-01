"""
FastAPI application for the Coastal Threat Alert System.

This file defines the main API endpoints for the system:
- Health checks
- Fetching the latest threat score from processed sensor data
- Scoring a custom payload of sensor data
- A Server-Sent Events (SSE) stream for live threat updates
"""
from fastapi import FastAPI, HTTPException, Request

# --- FIX: Import CORSMiddleware ---
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
import pandas as pd

# --- FIX: Import UTC for modern, timezone-aware timestamps ---
from datetime import datetime, UTC
import os
import asyncio
import json

# Use relative imports to align with the project structure
from .threat_model import calculate_threat_score
from .sensor_simulator import CSVSimulatedStream

# --- Constants ---
PROCESSED_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "data", "processed", "cleaned_weather.csv"
)

# --- Pydantic Models for API Data Structure ---


class ThreatScoreInput(BaseModel):
    air_temperature: Optional[float] = None
    humidity: Optional[float] = None
    rain_intensity: Optional[float] = None
    wind_speed: Optional[float] = None
    maximum_wind_speed: Optional[float] = None
    barometric_pressure: Optional[float] = None


class ThreatScoreResponse(BaseModel):
    score: float = Field(
        ...,
        json_schema_extra={"example": 72.5},
        description="Threat score from 0 to 100.",
    )
    level: str = Field(
        ...,
        json_schema_extra={"example": "Warning"},
        description="Threat level (Safe, Caution, Warning, Danger).",
    )
    parameters: Dict[str, int] = Field(
        ...,
        json_schema_extra={"example": {"wind_speed": 2, "rain_intensity": 1}},
        description="Per-parameter risk levels (0-3).",
    )
    raw: Dict[str, Any] = Field(
        ...,
        json_schema_extra={
            "example": {
                "wind_speed": 16.2,
                "measurement_timestamp": "2025-08-30T12:00:00",
            }
        },
        description="The raw input values used for scoring.",
    )
    timestamp: datetime = Field(..., description="Timestamp of the assessment.")
    location_id: str = Field(
        ...,
        json_schema_extra={"example": "PORBANDAR"},
        description="Identifier for the sensor location.",
    )


# --- FastAPI Application Instance ---
app = FastAPI(
    title="Coastal Threat Alert System API",
    description="API for detecting and alerting on coastal environmental threats.",
    version="1.0.0",
)

# --- FIX: Add CORS Middleware ---
# This allows our frontend (running on localhost:5173) to communicate with our backend.
origins = [
    "http://localhost",
    "http://localhost:5173",  # The default Vite dev server port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


# --- SSE Stream Logic ---
async def threat_event_generator(request: Request):
    simulator = CSVSimulatedStream(PROCESSED_DATA_PATH, delay_s=2)
    for reading_dict in simulator.stream():
        if await request.is_disconnected():
            print("🛑 Client disconnected. Stopping stream.")
            break

        reading_series = pd.Series(reading_dict)
        threat_result = calculate_threat_score(reading_series)

        response_data = ThreatScoreResponse(
            score=threat_result["score"],
            level=threat_result["level"],
            parameters=threat_result["parameters"],
            raw=reading_dict,
            # --- FIX: Replaced deprecated utcnow() ---
            timestamp=datetime.now(UTC),
            location_id="PORBANDAR_STREAM",
        )
        yield f"data: {response_data.model_dump_json()}\n\n"
        await asyncio.sleep(simulator.delay_s)


@app.get("/threat/stream", tags=["Threat Assessment"])
async def threat_stream(request: Request):
    return StreamingResponse(
        threat_event_generator(request), media_type="text/event-stream"
    )


# --- Standard API Endpoints ---
@app.get("/health", tags=["Status"])
def get_health_status():
    return {"status": "ok"}


@app.get(
    "/threat/latest", response_model=ThreatScoreResponse, tags=["Threat Assessment"]
)
def get_latest_threat():
    try:
        df = pd.read_csv(PROCESSED_DATA_PATH)
        if df.empty:
            raise HTTPException(status_code=404, detail="Processed data file is empty.")

        latest_reading_series = df.iloc[-1]
        threat_result = calculate_threat_score(latest_reading_series)
        raw_values = latest_reading_series.to_dict()

        response = ThreatScoreResponse(
            score=threat_result["score"],
            level=threat_result["level"],
            parameters=threat_result["parameters"],
            raw=raw_values,
            # --- FIX: Replaced deprecated utcnow() ---
            timestamp=datetime.now(UTC),
            location_id="PORBANDAR_MAIN",
        )
        return response
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=f"Processed data file not found at {PROCESSED_DATA_PATH}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.post(
    "/threat/score", response_model=ThreatScoreResponse, tags=["Threat Assessment"]
)
def score_custom_threat(payload: ThreatScoreInput):
    payload_dict = payload.model_dump()
    custom_reading_series = pd.Series(payload_dict)
    threat_result = calculate_threat_score(custom_reading_series)

    """
    Example curl command to test this endpoint:
    $payload = @{
    wind_speed = 25.5;
    barometric_pressure = 990;
    rain_intensity = 5.2
    } | ConvertTo-Json

    Invoke-RestMethod -Uri "http://127.0.0.1:7777/threat/score" -Method POST -Body $payload -ContentType "application/json"
    """

    response = ThreatScoreResponse(
        score=threat_result["score"],
        level=threat_result["level"],
        parameters=threat_result["parameters"],
        raw=payload_dict,
        # --- FIX: Replaced deprecated utcnow() ---
        timestamp=datetime.now(UTC),
        location_id="CUSTOM_INPUT",
    )
    return response
