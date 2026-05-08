import csv

from src.elevator import Elevator

class Output:
    def __init__(self, file_name, num_elevators):
        headers = ["time"]
        for i in range(num_elevators):
            headers.append("elevator{}".format(i))

        with open(f"data/{file_name}", "w", newline="", encoding="utf-8") as f:
            self.writer = csv.DictWriter(f, fieldnames=headers)
            self.writer.writeheader()

    def log_elevator_position(self, elevators: list[Elevator], time: int):
        entry = [time]
        for elevator in elevators:
            entry.append(elevator.cur_floor)

        self.writer.writerow(entry)
