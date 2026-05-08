import csv
import os
import re
import numpy as np
from typing import Optional

from src.passenger import Passenger

REQUIRED_HEADERS = {"time", "id", "source", "dest"}

def parse_passenger_id(value: str) -> int:
    match = re.fullmatch(r"passenger(\d+)", value.strip(), re.IGNORECASE)
    if not match:
        raise ValueError(f"Invalid passenger ID format: '{value}' (expected 'passengerN')")
    return int(match.group(1))

def parse_row(raw: dict, num_floors: int) -> Passenger:
    try:
        time = int(raw["time"].strip())
    except ValueError:
        raise ValueError(f"'time' must be an integer, got: '{raw['time']}'")

    source = int(raw["source"].strip())
    dest = int(raw["dest"].strip())
    if source > num_floors or dest > num_floors:
        raise ValueError(f"Source and destination must be smaller than {num_floors}")

    # Parse and validate passenger ID
    passenger_number = parse_passenger_id(raw["id"])


    return Passenger(
        request_time=time,
        passenger_id=passenger_number,
        source=source,
        dest=dest
    )

def parse_csv(filepath: str, num_floors: int) -> Optional[list[Passenger]]:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate headers
        headers = set(reader.fieldnames or [])
        missing = REQUIRED_HEADERS - headers
        if missing:
            raise ValueError(f"CSV is missing required headers: {missing}")

        # Parse rows
        rows = []
        for i, raw in enumerate(reader, start=2):
            try:
                rows.append(parse_row(raw, num_floors))
            except ValueError as e:
                print(f"Warning: skipping row {i}: {e}")

    print(f"Parsed {len(rows)} rows from '{filepath}'")
    return rows

class PoissonArrivalProcess:
    def __init__(self, lam: float, seed: int = None):
        self.lam = lam
        self.rng = np.random.default_rng(seed)

    def _simulate_arrivals(self, num_slots: int) -> np.ndarray:
        return self.rng.poisson(self.lam, size=num_slots)

    def _simulate_destination(self, src_floor: int, num_floors: int) -> int:
        values = [v for v in range(1, num_floors + 1) if v != src_floor]
        return int(self.rng.choice(values))

    def simulate(self, num_slots: int, src_floor: int, num_floors: int, cur_idx: int) -> list[Passenger]:
        arrivals = self._simulate_arrivals(num_slots)
        rows = []
        for time in range(num_slots):
            for _ in range(arrivals[time]):
                rows.append(
                    Passenger(
                        request_time=time,
                        passenger_id=cur_idx,
                        source=src_floor,
                        dest=self._simulate_destination(src_floor, num_floors)
                    )
                )
                cur_idx += 1

        return rows