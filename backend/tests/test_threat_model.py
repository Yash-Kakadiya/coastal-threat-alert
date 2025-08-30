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
from backend.config import THRESHOLDS, WEIGHTS, THREAT_LABELS


def calculate_parameter_score(param: str, value: float, thresholds: list) -> int:
    """
    Assigns a risk level (0–3) based on thresholds.
    This version correctly handles inverted parameters like barometric pressure.

    Parameters
    ----------
    param : str
        The name of the parameter being scored (e.g., "wind_speed").
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

    # Special handling for barometric pressure where lower is more dangerous
    if param == "barometric_pressure":
        if value > thresholds[0]:
            return 0
        elif value > thresholds[1]:
            return 1
        elif value > thresholds[2]:
            return 2
        else:
            return 3

    # Standard handling for all other parameters
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
        # Pass the parameter name to the scoring function
        risk_level = calculate_parameter_score(param, value, thresholds)
        parameter_scores[param] = risk_level

        weighted_sum += (risk_level / 3) * WEIGHTS[param] * 100

    # Normalize
    score = weighted_sum / total_weight if total_weight > 0 else 0
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
