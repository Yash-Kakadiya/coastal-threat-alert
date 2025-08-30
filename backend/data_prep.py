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

import pandas as pd
from pathlib import Path

# Paths
RAW_DATA_PATH = Path("backend/data/raw/beach_weather.csv")
PROCESSED_DATA_PATH = Path("backend/data/processed/cleaned_weather.csv")


def load_raw_data(path: Path) -> pd.DataFrame:
    """
    Load the raw beach weather dataset from CSV.

    Parameters
    ----------
    path : Path
        Path to the raw CSV file.

    Returns
    -------
    df : pd.DataFrame
        Loaded DataFrame.
    """
    return pd.read_csv(path)


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert column names to snake_case for consistency.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    df : pd.DataFrame
        DataFrame with cleaned column names.
    """
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )
    return df


def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the dataset:
    - Parse timestamp
    - Keep relevant columns only
    - Drop missing values

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    df : pd.DataFrame
        Cleaned DataFrame.
    """
    # Parse timestamp
    df["measurement_timestamp"] = pd.to_datetime(
        df["measurement_timestamp"], errors="coerce"
    )

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
    df = df[keep_cols]

    # Drop rows with missing values
    df = df.dropna()

    # Sort by time (important for simulation)
    df = df.sort_values("measurement_timestamp").reset_index(drop=True)

    return df


def save_processed_data(df: pd.DataFrame, path: Path):
    """
    Save cleaned dataset to processed folder.

    Parameters
    ----------
    df : pd.DataFrame
    path : Path
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main():
    """Main function to run preprocessing pipeline."""
    print("🔄 Loading raw dataset...")
    df_raw = load_raw_data(RAW_DATA_PATH)

    print("🧹 Cleaning column names...")
    df_clean = clean_column_names(df_raw)

    print("⚙️ Preprocessing dataset...")
    df_processed = preprocess_dataset(df_clean)

    print(f"💾 Saving processed dataset → {PROCESSED_DATA_PATH}")
    save_processed_data(df_processed, PROCESSED_DATA_PATH)

    print("✅ Preprocessing complete.")


if __name__ == "__main__":
    main()
