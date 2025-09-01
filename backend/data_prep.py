"""
Data preprocessing utilities for coastal sensor CSVs.

Functions:
- load_csvs(paths) -> list of DataFrames
- merge_and_resample(df_list, freq='1T') -> per-location processed DataFrame
- save_processed(df, out_path)
This is a starting point — expand per your CSV schemas.
"""

# from typing import List
# import pandas as pd
# import os


# def load_csv(path: str, timestamp_col: str = "timestamp") -> pd.DataFrame:
#     """Load CSV and parse timestamp column to UTC datetime index."""
#     df = pd.read_csv(path, parse_dates=[timestamp_col])
#     df[timestamp_col] = pd.to_datetime(df[timestamp_col], utc=True)
#     return df


# def merge_on_timestamp(
#     dfs: List[pd.DataFrame], timestamp_col: str = "timestamp"
# ) -> pd.DataFrame:
#     """
#     Merge multiple dataframes on timestamp and optional location.
#     Assumes each df has 'timestamp' and optionally 'location_id' or lat/lon.
#     """
#     # Start from the first df and merge sequentially (outer merge)
#     merged = dfs[0].set_index(timestamp_col)
#     for df in dfs[1:]:
#         merged = merged.join(df.set_index(timestamp_col), how="outer", rsuffix="_r")
#     # Sort and return
#     merged = merged.sort_index()
#     return merged


# def resample_and_interpolate(df: pd.DataFrame, freq: str = "1T") -> pd.DataFrame:
#     """
#     Resample to fixed frequency (default 1 minute), forward/backfill small gaps,
#     and interpolate numeric columns.
#     """
#     df_res = df.resample(freq).mean()
#     # Interpolate numeric columns (limit can be tuned)
#     df_res = df_res.interpolate(limit=10).ffill().bfill()
#     return df_res


# def save_processed(df: pd.DataFrame, out_path: str):
#     """Save processed dataframe to parquet for faster IO."""
#     os.makedirs(os.path.dirname(out_path), exist_ok=True)
#     df.to_parquet(out_path)


# # If you'd like a one-shot function:
# def preprocess_csv_paths(csv_paths: List[str], out_path: str):
#     dfs = [load_csv(p) for p in csv_paths]
#     merged = merge_on_timestamp(dfs)
#     processed = resample_and_interpolate(merged)
#     save_processed(processed, out_path)
#     return processed

"""
data_prep.py

Purpose:
--------
Utility functions for loading, cleaning, and preprocessing raw sensor datasets
before they are used in the Coastal Threat Alert System.

Steps:
1. Load raw CSV from backend/data/raw/
2. Standardize column names (snake_case)
3. Parse timestamp column into datetime format
4. Select only relevant features for threat scoring
5. Save cleaned dataset to backend/data/processed/

Usage:
------
Run this script directly to clean the dataset:
    python data_prep.py
"""
"""
Data preprocessing pipeline for the Beach Weather Stations dataset.
"""
import pandas as pd
from pathlib import Path

# --- File Paths ---
BASE_DIR = Path(__file__).parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "beach_weather.csv"
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed" / "cleaned_weather.csv"


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9_]+", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
    )
    return df


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    # Relevant columns for threat scoring
    keep_cols = [
        "measurement_timestamp",
        "air_temperature",
        "humidity",
        "rain_intensity",
        "wind_speed",
        "maximum_wind_speed",
        "barometric_pressure",
    ]
    # Ensure all required columns exist, fill missing ones with None
    for col in keep_cols:
        if col not in df.columns:
            df[col] = None

    df = df[keep_cols]
    df["measurement_timestamp"] = pd.to_datetime(
        df["measurement_timestamp"], errors="coerce"
    )

    # --- FIX: Drop rows with any missing values in the key scoring columns ---
    # This is the most important step to guarantee data quality.
    scoring_cols = [
        "wind_speed",
        "maximum_wind_speed",
        "humidity",
        "rain_intensity",
        "barometric_pressure",
    ]
    df = df.dropna(subset=scoring_cols)

    df = df.sort_values("measurement_timestamp").reset_index(drop=True)
    return df


def main():
    print("🔄 Loading raw dataset...")
    df_raw = pd.read_csv(RAW_DATA_PATH)

    print("🧹 Cleaning and processing data...")
    df_clean_names = clean_column_names(df_raw)
    df_processed = process_data(df_clean_names)

    # Save the processed data
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_processed.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"✅ Saved {len(df_processed)} cleaned records to {PROCESSED_DATA_PATH}")


if __name__ == "__main__":
    main()
