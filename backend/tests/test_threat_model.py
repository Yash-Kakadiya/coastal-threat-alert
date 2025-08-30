# """
# Basic tests for threat_model.calculate_threat_score
# Run: pytest backend/tests/test_threat_model.py
# """

# from backend.threat_model import calculate_threat_score


# def test_score_shape_and_bounds():
#     payload = {
#         "wind_speed_m_s": 10.0,
#         "wave_height_m": 1.2,
#         "tide_level_m": 0.5,
#         "turbidity_ntu": 5.0,
#         "chlorophyll": 0.8,
#         "sst": 28.0,
#     }
#     out = calculate_threat_score(payload)
#     assert "score" in out
#     assert 0 <= out["score"] <= 100
#     assert out["threat_level"] in {"SAFE", "WATCH", "WARNING", "DANGER"}
#     assert "components" in out
#     assert "explanation" in out

"""
test_threat_model.py

Purpose:
--------
Unit tests for the threat_model.py module.
Ensures that calculate_threat_score() works correctly
with sample input rows from the processed dataset.
"""

import pandas as pd
from backend.threat_model import calculate_threat_score


def test_calculate_threat_score_basic():
    """
    Test scoring on a dummy row with moderate values.
    """
    row = pd.Series(
        {
            "wind_speed": 18,
            "maximum_wind_speed": 22,
            "humidity": 80,
            "rain_intensity": 3,
            "barometric_pressure": 995,
        }
    )

    result = calculate_threat_score(row)

    assert "score" in result
    assert "level" in result
    assert "parameters" in result

    print("Threat Score:", result)


def test_calculate_threat_score_extreme():
    """
    Test scoring on extreme values (simulate cyclone).
    """
    row = pd.Series(
        {
            "wind_speed": 40,
            "maximum_wind_speed": 50,
            "humidity": 98,
            "rain_intensity": 15,
            "barometric_pressure": 970,
        }
    )

    result = calculate_threat_score(row)

    print("Extreme Threat Score:", result)
    assert result["level"] in ["Warning", "Danger"]
