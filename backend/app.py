"""
FastAPI backend skeleton for Coastal Threat Alert System.
Run (from repo root):
    pip install -r backend/requirements.txt
    uvicorn backend.app:app --reload --port 7777
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from .threat_model import calculate_threat_score

app = FastAPI(title="Coastal Threat Alert - Backend")


class ThreatRequest(BaseModel):
    location_id: str
    timestamp: Optional[str] = None  # ISO 8601; if None return latest
    # optionally allow raw sensor override for quick testing:
    sensor_override: Optional[Dict[str, Any]] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/get_threat_level")
def get_threat_level(req: ThreatRequest):
    """
    Return threat score and explanation.

    For initial commit this uses the sensor_override payload if provided.
    Later this endpoint should load the latest processed sensor data for location.
    """
    # For the first commit, require sensor_override for deterministic demo
    if not req.sensor_override:
        raise HTTPException(
            status_code=400,
            detail="Provide sensor_override for demo or implement data loader.",
        )

    sensor_payload = req.sensor_override
    # compute score
    result = calculate_threat_score(sensor_payload)
    # augment with requested metadata
    result["location_id"] = req.location_id
    result["timestamp"] = req.timestamp or sensor_payload.get("timestamp")
    return result
