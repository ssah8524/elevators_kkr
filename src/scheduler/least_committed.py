from typing import Optional

from src.scheduler.scheduler import Scheduler
from src.passenger import Passenger
from src.elevator import Elevator


class LeastCommitted(Scheduler):
    def __init__(self, elevator_dict: dict):
        super().__init__(elevator_dict)

    def _find_best_elevator(self) -> Optional[Elevator]:
        available = [el for el in self.elevators.values() if self._available(el)]
        if not available:
            return None
        return min(available, key=lambda el: len(el.current_passengers) + len(el.assigned_passengers))

    def schedule(self, passengers_to_serve: list):
        all_passengers = self.waitlist + passengers_to_serve
        self.waitlist = []

        for passenger in all_passengers:
            elevator = self._find_best_elevator()
            if elevator:
                elevator.assigned_passengers.append(passenger)
            else:
                self.waitlist.append(passenger)
