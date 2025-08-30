"""
Configurable constants for the threat scoring system.
Tweak weights and thresholds here for demo tuning.
"""

# Weights for scoring (sum of physical/env + anomaly weight should be 1.0)
WEIGHTS = {
    "physical": 0.55,
    "env": 0.35,
    "anomaly": 0.10,
    # breakdown inside groups
    "physical_components": {
        "wind": 0.25,
        "wave": 0.20,
        "tide": 0.10,
    },
    "env_components": {
        "turbidity": 0.18,
        "chlorophyll": 0.12,
        "sst": 0.05,
    },
}

# Domain clips for normalization (min, max)
CLIPS = {
    "wind_speed_m_s": (0.0, 50.0),  # m/s
    "wave_height_m": (0.0, 15.0),  # meters
    "turbidity_ntu": (0.0, 200.0),  # NTU
    "chlorophyll": (0.0, 50.0),  # mg/m3 or chlor_a
    "tide_level_m": (-5.0, 10.0),  # meters
    "sst": (-2.0, 40.0),  # deg C
}

# Threat level thresholds (0-100)
THRESHOLDS = {
    "SAFE": (0, 30),
    "WATCH": (31, 60),
    "WARNING": (61, 80),
    "DANGER": (81, 100),
}
