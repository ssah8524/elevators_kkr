from dataclasses import dataclass
from typing import Optional

@dataclass
class Passenger:
    request_time: int
    passenger_id: int  # extracted from id, e.g. "passenger3" -> 3
    source: int
    dest: int

    entering_time: Optional[int] = None
    exit_time: Optional[int] = None
    total_time: Optional[int] = None

    @property
    def wait_time(self) -> int:
        """Ticks between request and boarding."""
        return self.entering_time - self.request_time

    @property
    def travel_time(self) -> int:
        """Ticks between boarding and alighting."""
        return self.exit_time - self.entering_time

