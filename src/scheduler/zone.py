from src.scheduler.scheduler import Scheduler
from src.passenger import Passenger
from src.elevator import Elevator


class ZoneScheduler(Scheduler):
    """
    Static hard zones: floors are divided evenly across elevators.
    Each passenger is served exclusively by the elevator assigned to their source floor's zone.
    If that elevator is at capacity, the passenger is waitlisted.
    """

    def __init__(self, elevator_dict: dict):
        super().__init__(elevator_dict)
        n = len(elevator_dict)
        num_floors = elevator_dict[0].num_floors
        zone_size = num_floors / n
        self._zone_map = {
            i: el
            for i, el in elevator_dict.items()
        }
        self._zone_bounds = [
            (round(i * zone_size) + 1, round((i + 1) * zone_size))
            for i in range(n)
        ]

    def _elevator_for(self, floor: int) -> Elevator:
        for i, (lo, hi) in enumerate(self._zone_bounds):
            if lo <= floor <= hi:
                return self._zone_map[i]
        return self._zone_map[len(self._zone_map) - 1]

    def schedule(self, passengers_to_serve: list):
        all_passengers = self.waitlist + passengers_to_serve
        self.waitlist = []

        for passenger in all_passengers:
            elevator = self._elevator_for(passenger.source)
            if self._available(elevator):
                elevator.assigned_passengers.append(passenger)
            else:
                self.waitlist.append(passenger)
