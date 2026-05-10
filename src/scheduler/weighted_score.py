from typing import Optional

from src.scheduler.scheduler import Scheduler
from src.passenger import Passenger
from src.elevator import Elevator, ElevatorStatus


class WeightedScore(Scheduler):
    """
    Score each elevator as alpha * estimated_pickup_time + beta * committed_count.
    alpha=1, beta=0  →  pure proximity (Nearest Car-like)
    alpha=0, beta=1  →  pure load balancing (Least Committed-like)
    """

    def __init__(self, elevator_dict: dict, alpha: float = 1.0, beta: float = 1.0):
        """Initialise with tunable weights: alpha scales pickup time, beta scales committed passenger count."""
        super().__init__(elevator_dict)
        self.alpha = alpha
        self.beta = beta

    @staticmethod
    def _estimated_pickup_time(el: Elevator, passenger: Passenger) -> int:
        """Estimate ticks until the elevator reaches the passenger's source floor."""
        if el.status == ElevatorStatus.STOPPED:
            return abs(el.cur_floor - passenger.source)

        all_dests = [p.dest for p in el.current_passengers + el.assigned_passengers]

        if el.status == ElevatorStatus.UP:
            if passenger.source >= el.cur_floor:
                return passenger.source - el.cur_floor
            turn_floor = max(all_dests) if all_dests else el.cur_floor
            return (turn_floor - el.cur_floor) + (turn_floor - passenger.source)
        else:  # DOWN
            if passenger.source <= el.cur_floor:
                return el.cur_floor - passenger.source
            turn_floor = min(all_dests) if all_dests else el.cur_floor
            return (el.cur_floor - turn_floor) + (passenger.source - turn_floor)

    def _score(self, el: Elevator, passenger: Passenger) -> float:
        """Compute alpha * pickup_time + beta * committed_count for a given elevator and passenger."""
        pickup_time = self._estimated_pickup_time(el, passenger)
        committed = len(el.current_passengers) + len(el.assigned_passengers)
        return self.alpha * pickup_time + self.beta * committed

    def _find_best_elevator(self, passenger: Passenger) -> Optional[Elevator]:
        """Return the available elevator with the lowest weighted score."""
        available = [el for el in self.elevators.values() if self._available(el)]
        if not available:
            return None
        return min(available, key=lambda el: self._score(el, passenger))

    def schedule(self, passengers_to_serve: list):
        """Assign each passenger to the elevator with the lowest weighted score."""
        all_passengers = self.waitlist + passengers_to_serve
        self.waitlist = []

        for passenger in all_passengers:
            elevator = self._find_best_elevator(passenger)
            if elevator:
                elevator.assigned_passengers.append(passenger)
            else:
                self.waitlist.append(passenger)
