import csv

from src.elevator import Elevator

class Output:
    def __init__(self, file_name, num_elevators):
        """Open a CSV file for writing elevator position logs."""
        self.headers = ["time"] + [f"elevator{i}" for i in range(num_elevators)]
        self.file = open(f"data/{file_name}", "w", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.file, fieldnames=self.headers)
        self.writer.writeheader()

    def log_elevator_position(self, elevators: list[Elevator], time: int):
        """Write one row recording each elevator's current floor at the given time tick."""
        entry = {"time": time}
        for i, elevator in enumerate(elevators):
            entry[f"elevator{i}"] = elevator.cur_floor
        self.writer.writerow(entry)

    def close(self):
        """Flush and close the underlying CSV file."""
        self.file.close()