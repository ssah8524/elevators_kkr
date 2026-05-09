from typing import Optional

from src.scheduler.nearest_car import NearestCar
from src.passenger import Passenger
from src.elevator import Elevator, ElevatorStatus


class NearestIdle(NearestCar):
    def __init__(self, elevator_dict: dict):
        super().__init__(elevator_dict)

    def _find_best_elevator(self, passenger: Passenger) -> Optional[Elevator]:
        available = [el for el in self.elevators.values() if self._available(el)]
        if not available:
            return None

        idle = [el for el in available if el.status == ElevatorStatus.STOPPED]
        if idle:
            return min(idle, key=lambda el: abs(el.cur_floor - passenger.source))

        return super()._find_best_elevator(passenger)

    def schedule(self, passengers_to_serve: list):
        all_passengers = self.waitlist + passengers_to_serve
        self.waitlist = []

        for passenger in all_passengers:
            elevator = self._find_best_elevator(passenger)
            if elevator:
                elevator.assigned_passengers.append(passenger)
            else:
                self.waitlist.append(passenger)
