import csv

from src.elevator import Elevator

class Output:
    def __init__(self, file_name, num_elevators):
        self.headers = ["time"] + [f"elevator{i}" for i in range(num_elevators)]
        self.file = open(f"data/{file_name}", "w", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.file, fieldnames=self.headers)
        self.writer.writeheader()

    def log_elevator_position(self, elevators: list[Elevator], time: int):
        entry = {"time": time}
        for i, elevator in enumerate(elevators):
            entry[f"elevator{i}"] = elevator.cur_floor
        self.writer.writerow(entry)

    def close(self):
        self.file.close()