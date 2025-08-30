"""
Basic tests for threat_model.calculate_threat_score
Run: pytest backend/tests/test_threat_model.py
"""

from backend.threat_model import calculate_threat_score


def test_score_shape_and_bounds():
    payload = {
        "wind_speed_m_s": 10.0,
        "wave_height_m": 1.2,
        "tide_level_m": 0.5,
        "turbidity_ntu": 5.0,
        "chlorophyll": 0.8,
        "sst": 28.0,
    }
    out = calculate_threat_score(payload)
    assert "score" in out
    assert 0 <= out["score"] <= 100
    assert out["threat_level"] in {"SAFE", "WATCH", "WARNING", "DANGER"}
    assert "components" in out
    assert "explanation" in out
