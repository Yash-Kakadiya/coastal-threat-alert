"""
Configurable constants for the threat scoring system.
Tweak weights and thresholds here for demo tuning.
"""

# # Weights for scoring (sum of physical/env + anomaly weight should be 1.0)
# WEIGHTS = {
#     "physical": 0.55,
#     "env": 0.35,
#     "anomaly": 0.10,
#     # breakdown inside groups
#     "physical_components": {
#         "wind": 0.25,
#         "wave": 0.20,
#         "tide": 0.10,
#     },
#     "env_components": {
#         "turbidity": 0.18,
#         "chlorophyll": 0.12,
#         "sst": 0.05,
#     },
# }

# # Domain clips for normalization (min, max)
# CLIPS = {
#     "wind_speed_m_s": (0.0, 50.0),  # m/s
#     "wave_height_m": (0.0, 15.0),  # meters
#     "turbidity_ntu": (0.0, 200.0),  # NTU
#     "chlorophyll": (0.0, 50.0),  # mg/m3 or chlor_a
#     "tide_level_m": (-5.0, 10.0),  # meters
#     "sst": (-2.0, 40.0),  # deg C
# }

# # Threat level thresholds (0-100)
# THRESHOLDS = {
#     "SAFE": (0, 30),
#     "WATCH": (31, 60),
#     "WARNING": (61, 80),
#     "DANGER": (81, 100),
# }

"""
config.py

Purpose:
--------
Configuration file for rule-based threat scoring.

Defines thresholds, weights, and labels for different
environmental parameters such as wind speed, humidity,
rainfall intensity, and barometric pressure.

This can later be extended for dynamic configs (e.g. from Firebase).
"""

# Threat level categories
THREAT_LABELS = {0: "Safe", 1: "Caution", 2: "Warning", 3: "Danger"}

# Thresholds for different parameters
THRESHOLDS = {
    "wind_speed": [10, 20, 30],  # m/s
    "maximum_wind_speed": [15, 25, 35],  # m/s
    "humidity": [70, 85, 95],  # %
    "rain_intensity": [1, 5, 10],  # mm/hr
    "barometric_pressure": [1000, 990, 980],  # hPa (lower = more dangerous)
}

# Weights for each parameter (contribution to total score)
WEIGHTS = {
    "wind_speed": 0.25,
    "maximum_wind_speed": 0.25,
    "humidity": 0.15,
    "rain_intensity": 0.20,
    "barometric_pressure": 0.15,
}
