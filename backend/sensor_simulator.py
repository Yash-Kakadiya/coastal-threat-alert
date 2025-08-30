"""
Sensor simulator to stream processed CSV/Parquet rows as "live" readings.

Usage:
    from sensor_simulator import SimulatedStream
    sim = SimulatedStream("data/processed/porbandar.parquet", delay_s=1.0)
    for payload in sim.stream():
        # payload is a dict with 'timestamp' and sensor fields
"""

import time
import pandas as pd
from typing import Generator


class SimulatedStream:
    def __init__(self, path: str, delay_s: float = 1.0):
        self.path = path
        self.delay_s = delay_s
        # Load into memory for simplicity (ok for demo-size datasets)
        self.df = pd.read_parquet(path)

    def stream(self) -> Generator[dict, None, None]:
        """Yield each row as a dict; sleep delay_s between yields."""
        for ts, row in self.df.iterrows():
            payload = row.to_dict()
            # Keep timestamp as ISO string
            payload["timestamp"] = pd.Timestamp(ts).isoformat()
            yield payload
            time.sleep(self.delay_s)
