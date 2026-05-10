from typing import Optional

from src.scheduler.scheduler import Scheduler
from src.passenger import Passenger
from src.elevator import Elevator, ElevatorStatus

class NearestCarSimple(Scheduler):
    def __init__(self, elevator_dict: dict):
        """Initialise the scheduler with the elevator fleet."""
        super().__init__(elevator_dict)

    def _find_nearest_elevator(self, passenger: Passenger) -> Optional[Elevator]:
        """Return the available elevator closest to the passenger's source floor, breaking ties by current load."""
        available = [el for el in self.elevators.values() if self._available(el)]
        if not available:
            return None

        return min(available, key=lambda el: (
            abs(el.cur_floor - passenger.source),
            len(el.current_passengers),
        ))

    def schedule(self, passengers_to_serve: list):
        """Assign each passenger to the closest available elevator by raw floor distance."""
        all_passengers = self.waitlist + passengers_to_serve
        self.waitlist = []

        for passenger in all_passengers:
            elevator = self._find_nearest_elevator(passenger)
            if elevator:
                elevator.assigned_passengers.append(passenger)
            else:
                self.waitlist.append(passenger)
