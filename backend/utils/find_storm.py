"""
A utility script to analyze the cleaned dataset and find the row
with the highest threat score. This helps us identify the most
"interesting" part of the data for our simulation demo.
"""

import pandas as pd
from pathlib import Path
import sys

# --- FIX: Add the project root directory to Python's path ---
# This line is the key to solving the ImportError. It ensures that
# Python knows where to find the 'backend' package.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Now that the path is set, we can use absolute imports
from backend.threat_model import calculate_threat_score


def find_peak_threat_index():
    """
    Calculates the threat score for every row and finds the index of the max score.
    """
    processed_csv_path = (
        PROJECT_ROOT / "backend" / "data" / "processed" / "cleaned_weather.csv"
    )

    if not processed_csv_path.exists():
        print(f"❌ Error: Processed data not found at {processed_csv_path}")
        print("Please run `python backend/data_prep.py` first.")
        return None

    df = pd.read_csv(processed_csv_path)

    print(f"Analysing {len(df)} records to find peak threat...")

    scores = df.apply(calculate_threat_score, axis=1)
    df["threat_score"] = scores.apply(lambda x: x["score"])

    peak_index = df["threat_score"].idxmax()
    peak_score = df["threat_score"].max()

    print("\n" + "=" * 40)
    print(f"🌊 STORM PEAK IDENTIFIED! 🌊")
    print(f"Highest Threat Score: {peak_score:.2f}")
    print(f"Index in CSV: {peak_index}")
    print("=" * 40 + "\n")

    return peak_index


if __name__ == "__main__":
    find_peak_threat_index()
