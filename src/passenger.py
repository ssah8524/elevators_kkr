from dataclasses import dataclass

@dataclass
class Passenger:
    request_time: int
    passenger_id: int  # extracted from id, e.g. "passenger3" -> 3
    source: int
    dest: int

    entering_time: int
    exit_time: int
    total_time: int

    @property
    def wait_time(self) -> int:
        return self.entering_time - self.request_time

    @property
    def travel_time(self) -> int:
        return self.exit_time - self.entering_time

