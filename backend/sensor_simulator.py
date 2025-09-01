import time
import pandas as pd
from typing import Generator, Dict, Any
import os

# --- Using the index you discovered to create a demo "story" ---
STORM_PEAK_INDEX = 43090
DEMO_SEQUENCE_LENGTH = 100  # We will show 100 data points in our story


class CSVSimulatedStream:
    """
    Creates a compelling demo sequence around the storm peak, starting
    calm, building to the crisis, and then showing the aftermath.
    """

    def __init__(
        self, path: str, delay_s: float = 1.5
    ):  # Faster delay for a snappier demo
        self.path = path
        self.delay_s = delay_s
        self.demo_df = pd.DataFrame()
        try:
            df = pd.read_csv(path)
            print(f"✅ Simulator loaded {len(df)} records to build demo sequence.")
            self._create_demo_sequence(df)
        except FileNotFoundError:
            print(f"❌ ERROR: Data file not found at {path}. Simulator cannot start.")

    def _create_demo_sequence(self, df: pd.DataFrame):
        """Builds a curated list of data points for the demo."""
        # Ensure the peak index is valid
        if STORM_PEAK_INDEX >= len(df):
            print("Peak index is out of bounds. Using a random slice.")
            start = max(0, len(df) - DEMO_SEQUENCE_LENGTH)
            self.demo_df = df.iloc[start:].reset_index(drop=True)
            return

        # Create a slice of data centered around the storm peak
        start_index = max(0, STORM_PEAK_INDEX - (DEMO_SEQUENCE_LENGTH // 2))
        end_index = min(len(df), STORM_PEAK_INDEX + (DEMO_SEQUENCE_LENGTH // 2))

        storm_slice = df.iloc[start_index:end_index]

        # Add a few seconds of calm data at the beginning to show the transition
        calm_slice = df.iloc[100:105]  # Pick 5 known calm rows from the start

        self.demo_df = pd.concat([calm_slice, storm_slice]).reset_index(drop=True)
        print(
            f"🌪️ Demo sequence created with {len(self.demo_df)} data points, centered on storm peak."
        )

    def stream(self) -> Generator[Dict[str, Any], None, None]:
        if self.demo_df.empty:
            return

        current_index = 0
        while True:
            row = self.demo_df.iloc[current_index]
            yield row.to_dict()
            time.sleep(self.delay_s)

            current_index += 1
            if current_index >= len(self.demo_df):
                current_index = 0  # Loop the demo sequence
