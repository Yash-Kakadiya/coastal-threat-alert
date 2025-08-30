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
# These values can be tuned based on meteorological standards for the Gujarat coast.
THRESHOLDS = {
    "wind_speed": [
        12,
        22,
        35,
    ],  # km/h converted to m/s approx -> now reflects Beaufort scale more
    "maximum_wind_speed": [18, 30, 45],  # m/s
    "humidity": [80, 90, 95],  # %
    "rain_intensity": [2.5, 7.5, 15],  # mm/hr (light, moderate, heavy)
    "barometric_pressure": [1005, 995, 985],  # hPa (lower = more dangerous)
}

# Weights for each parameter (contribution to total score).
# Increased importance for pressure and maximum wind speed.
WEIGHTS = {
    "wind_speed": 0.20,
    "maximum_wind_speed": 0.30,
    "humidity": 0.05,
    "rain_intensity": 0.15,
    "barometric_pressure": 0.30,
}
