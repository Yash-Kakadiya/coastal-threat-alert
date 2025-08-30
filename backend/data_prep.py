"""
Data preprocessing utilities for coastal sensor CSVs.

Functions:
- load_csvs(paths) -> list of DataFrames
- merge_and_resample(df_list, freq='1T') -> per-location processed DataFrame
- save_processed(df, out_path)
This is a starting point — expand per your CSV schemas.
"""

from typing import List
import pandas as pd
import os


def load_csv(path: str, timestamp_col: str = "timestamp") -> pd.DataFrame:
    """Load CSV and parse timestamp column to UTC datetime index."""
    df = pd.read_csv(path, parse_dates=[timestamp_col])
    df[timestamp_col] = pd.to_datetime(df[timestamp_col], utc=True)
    return df


def merge_on_timestamp(
    dfs: List[pd.DataFrame], timestamp_col: str = "timestamp"
) -> pd.DataFrame:
    """
    Merge multiple dataframes on timestamp and optional location.
    Assumes each df has 'timestamp' and optionally 'location_id' or lat/lon.
    """
    # Start from the first df and merge sequentially (outer merge)
    merged = dfs[0].set_index(timestamp_col)
    for df in dfs[1:]:
        merged = merged.join(df.set_index(timestamp_col), how="outer", rsuffix="_r")
    # Sort and return
    merged = merged.sort_index()
    return merged


def resample_and_interpolate(df: pd.DataFrame, freq: str = "1T") -> pd.DataFrame:
    """
    Resample to fixed frequency (default 1 minute), forward/backfill small gaps,
    and interpolate numeric columns.
    """
    df_res = df.resample(freq).mean()
    # Interpolate numeric columns (limit can be tuned)
    df_res = df_res.interpolate(limit=10).ffill().bfill()
    return df_res


def save_processed(df: pd.DataFrame, out_path: str):
    """Save processed dataframe to parquet for faster IO."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_parquet(out_path)


# If you'd like a one-shot function:
def preprocess_csv_paths(csv_paths: List[str], out_path: str):
    dfs = [load_csv(p) for p in csv_paths]
    merged = merge_on_timestamp(dfs)
    processed = resample_and_interpolate(merged)
    save_processed(processed, out_path)
    return processed
