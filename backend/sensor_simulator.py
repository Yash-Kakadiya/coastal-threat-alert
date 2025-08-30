# """
# Sensor simulator to stream processed CSV/Parquet rows as "live" readings.

# Usage:
#     from sensor_simulator import SimulatedStream
#     sim = SimulatedStream("data/processed/porbandar.parquet", delay_s=1.0)
#     for payload in sim.stream():
#         # payload is a dict with 'timestamp' and sensor fields
# """

# import time
# import pandas as pd
# from typing import Generator


# class SimulatedStream:
#     def __init__(self, path: str, delay_s: float = 1.0):
#         self.path = path
#         self.delay_s = delay_s
#         # Load into memory for simplicity (ok for demo-size datasets)
#         self.df = pd.read_parquet(path)

#     def stream(self) -> Generator[dict, None, None]:
#         """Yield each row as a dict; sleep delay_s between yields."""
#         for ts, row in self.df.iterrows():
#             payload = row.to_dict()
#             # Keep timestamp as ISO string
#             payload["timestamp"] = pd.Timestamp(ts).isoformat()
#             yield payload
#             time.sleep(self.delay_s)

"""
Sensor simulator to stream processed CSV rows as "live" readings.

This module reads a CSV file and yields its rows one by one with a
delay, simulating a real-time data feed from a sensor station.
"""

import time
import pandas as pd
from typing import Generator, Dict, Any
import os


class CSVSimulatedStream:
    """
    Reads a CSV file and streams its rows as dictionaries.
    """

    def __init__(self, path: str, delay_s: float = 2.0):
        """
        Initializes the simulator.

        Parameters
        ----------
        path : str
            The full path to the CSV file.
        delay_s : float, optional
            The delay in seconds between yielding each row, by default 2.0.
        """
        self.path = path
        self.delay_s = delay_s
        # Load the entire CSV into memory. This is fine for our hackathon dataset.
        try:
            self.df = pd.read_csv(path)
            print(
                f"✅ Simulator loaded {len(self.df)} records from {os.path.basename(path)}."
            )
        except FileNotFoundError:
            print(f"❌ ERROR: Data file not found at {path}. Simulator cannot start.")
            self.df = pd.DataFrame()  # Create an empty dataframe to prevent crashes

    def stream(self) -> Generator[Dict[str, Any], None, None]:
        """
        A generator that yields each row as a dictionary and sleeps
        for the configured delay.
        """
        if self.df.empty:
            print("⚠️ Simulator has no data to stream.")
            return

        for index, row in self.df.iterrows():
            # Convert the row (a pandas Series) to a dictionary
            payload = row.to_dict()
            yield payload
            # This is a blocking sleep, which is fine for a simple script,
            # but we will use asyncio.sleep in our FastAPI endpoint.
            time.sleep(self.delay_s)
