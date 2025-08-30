# """
# Threat model v0 (rule-based).
# Contains calculate_threat_score() which accepts a dict of sensor values and
# returns a dictionary:
# {
#   "score": int,               # 0-100
#   "threat_level": "SAFE"|"WATCH"|...,
#   "components": {...},        # normalized component contributions
#   "anomaly_flags": {...},     # optional zscores or flags
#   "explanation": str,
#   "raw_params": {...}
# }
# This is intended to be simple and interpretable.
# """

# from typing import Dict, Any
# import numpy as np
# from .config import WEIGHTS, CLIPS, THRESHOLDS


# def _clip_and_norm(value: float, key: str) -> float:
#     """Clip a sensor value to domain and normalize to 0-1 (linear)."""
#     if value is None or (isinstance(value, float) and np.isnan(value)):
#         return 0.0
#     lo, hi = CLIPS.get(key, (0.0, 1.0))
#     v = float(value)
#     v_clipped = max(lo, min(hi, v))
#     # protect against division by zero
#     denom = hi - lo if hi - lo != 0 else 1.0
#     return (v_clipped - lo) / denom


# def _map_score_to_level(score: int) -> str:
#     """Map integer 0-100 to threat level string."""
#     for level, (lo, hi) in THRESHOLDS.items():
#         if lo <= score <= hi:
#             return level
#     # fallback
#     if score < 0:
#         return "SAFE"
#     return "DANGER"


# def calculate_threat_score(sensor_payload: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Compute a 0-100 threat score for a single timestamp/location.

#     sensor_payload: expected keys (some optional)
#         - wind_speed_m_s, wave_height_m, tide_level_m, turbidity_ntu,
#           chlorophyll, sst (sea surface temp)
#     """
#     # Normalize inputs to 0-1
#     norm = {
#         "wind": _clip_and_norm(sensor_payload.get("wind_speed_m_s"), "wind_speed_m_s"),
#         "wave": _clip_and_norm(sensor_payload.get("wave_height_m"), "wave_height_m"),
#         "tide": _clip_and_norm(sensor_payload.get("tide_level_m"), "tide_level_m"),
#         "turbidity": _clip_and_norm(
#             sensor_payload.get("turbidity_ntu"), "turbidity_ntu"
#         ),
#         "chlorophyll": _clip_and_norm(sensor_payload.get("chlorophyll"), "chlorophyll"),
#         "sst": _clip_and_norm(sensor_payload.get("sst"), "sst"),
#     }

#     # Physical and environmental aggregates using configured weights
#     phys_w = WEIGHTS["physical_components"]
#     env_w = WEIGHTS["env_components"]

#     physical_score = (
#         phys_w["wind"] * norm["wind"]
#         + phys_w["wave"] * norm["wave"]
#         + phys_w["tide"] * norm["tide"]
#     )
#     env_score = (
#         env_w["turbidity"] * norm["turbidity"]
#         + env_w["chlorophyll"] * norm["chlorophyll"]
#         + env_w["sst"] * norm["sst"]
#     )

#     base = WEIGHTS["physical"] * physical_score + WEIGHTS["env"] * env_score

#     # Simple anomaly boost: check rapid increases using available keys (placeholder)
#     # For initial commit, we use a naive boost: if any normalized value > 0.9, add small boost
#     anomaly_indicator = max(list(norm.values()))
#     anomaly_boost = WEIGHTS["anomaly"] * (
#         1.0 if anomaly_indicator > 0.95 else (anomaly_indicator / 3.0)
#     )

#     raw_score = base + anomaly_boost
#     # Ensure between 0 and 1
#     raw_score = max(0.0, min(1.0, raw_score))
#     score100 = int(round(raw_score * 100))

#     comp = {
#         "physical_score": round(float(physical_score), 4),
#         "env_score": round(float(env_score), 4),
#         "anomaly_indicator": round(float(anomaly_indicator), 4),
#     }

#     level = _map_score_to_level(score100)

#     explanation = (
#         f"{level}: Physical factors (wind/wave/tide) contribute {comp['physical_score']:.2f}, "
#         f"environmental factors {comp['env_score']:.2f}. Anomaly indicator {comp['anomaly_indicator']:.2f}."
#     )

#     return {
#         "score": score100,
#         "threat_level": level,
#         "components": comp,
#         "anomaly_flags": {"simple_peak": anomaly_indicator > 0.95},
#         "explanation": explanation,
#         "raw_params": sensor_payload,
#     }

"""
threat_model.py

Purpose:
--------
Implements the rule-based threat scoring system for the
Coastal Threat Alert System.

Uses thresholds and weights defined in config.py to
calculate a threat score (0–100) and map it to a threat level.
"""

import pandas as pd
from .config import THRESHOLDS, WEIGHTS, THREAT_LABELS

# from backend.config import THRESHOLDS, WEIGHTS, THREAT_LABELS


def calculate_parameter_score(value: float, thresholds: list) -> int:
    """
    Assigns a risk level (0–3) based on thresholds.

    Parameters
    ----------
    value : float
        Sensor measurement.
    thresholds : list
        Threshold values for caution, warning, danger.

    Returns
    -------
    int
        Risk level (0=Safe, 1=Caution, 2=Warning, 3=Danger).
    """
    if value is None:
        return 0
    if value < thresholds[0]:
        return 0
    elif value < thresholds[1]:
        return 1
    elif value < thresholds[2]:
        return 2
    else:
        return 3


def calculate_threat_score(row: pd.Series) -> dict:
    """
    Compute overall threat score for a single sensor reading.

    Parameters
    ----------
    row : pd.Series
        A row from the processed dataset.

    Returns
    -------
    dict
        {
            "score": float,
            "level": str,
            "parameters": {param: risk_level}
        }
    """
    parameter_scores = {}
    weighted_sum = 0
    total_weight = sum(WEIGHTS.values())

    for param, thresholds in THRESHOLDS.items():
        value = row.get(param)
        risk_level = calculate_parameter_score(value, thresholds)
        parameter_scores[param] = risk_level

        weighted_sum += (risk_level / 3) * WEIGHTS[param] * 100

    # Normalize
    score = weighted_sum / total_weight
    # Map to threat level
    if score < 25:
        level = THREAT_LABELS[0]
    elif score < 50:
        level = THREAT_LABELS[1]
    elif score < 75:
        level = THREAT_LABELS[2]
    else:
        level = THREAT_LABELS[3]

    return {"score": round(score, 2), "level": level, "parameters": parameter_scores}
