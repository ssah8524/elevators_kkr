from collections import deque

from numpy.ma.core import true_divide

from src.elevator import Elevator
from src.scheduler.scheduler import Scheduler

class RoundRobin(Scheduler):
    def __init__(self, elevator_dict: dict):
        super().__init__(elevator_dict)
        self.elevator_head = 0

    def _available(self, elevator: Elevator) -> bool:
        if len(elevator.current_passengers) + len(elevator.assigned_passengers) < elevator.max_passengers:
            return True

        # Even if currently the number of current and schedules passengers may be at the limit,
        # it could be that that number reduces before the elevator picks this user up.


    def schedule(self, passengers_to_serve: list):
        if not passengers_to_serve:
            return

        for passenger in passengers_to_serve:
            cur_elevator = self.elevator_head
            if self._available(cur_elevator):
                self.elevators[cur_elevator].assigned_passengers.append(passenger)
                self.elevator_head += 1
                if self.elevator_head == len(self.elevators):
                    self.elevator_head = 0

