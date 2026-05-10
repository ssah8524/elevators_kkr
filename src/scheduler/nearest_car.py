from typing import Optional

from src.scheduler.scheduler import Scheduler
from src.passenger import Passenger
from src.elevator import Elevator, ElevatorStatus

class NearestCar(Scheduler):
    def __init__(self, elevator_dict: dict):
        """Initialise the scheduler with the elevator fleet."""
        super().__init__(elevator_dict)

    @staticmethod
    def _estimated_travel_time(el: Elevator, passenger: Passenger) -> int:
        """Estimate ticks from pickup to delivery, accounting for the elevator's current direction and turn floor."""
        all_dests = [p.dest for p in el.current_passengers + el.assigned_passengers]

        if el.status == ElevatorStatus.UP or passenger.source > el.cur_floor:
            turn_floor = max(all_dests) if all_dests else passenger.source
            turn_floor = max(turn_floor, passenger.source)
            if passenger.dest >= passenger.source:
                return passenger.dest - passenger.source
            return (turn_floor - passenger.source) + (turn_floor - passenger.dest)
        else:
            turn_floor = min(all_dests) if all_dests else passenger.source
            turn_floor = min(turn_floor, passenger.source)
            if passenger.dest <= passenger.source:
                return passenger.source - passenger.dest
            return (passenger.source - turn_floor) + (passenger.dest - turn_floor)

    def _find_best_elevator(self, passenger: Passenger) -> Optional[Elevator]:
        """Return the available elevator with the shortest effective pickup distance, preferring those already heading toward the passenger."""
        available = [el for el in self.elevators.values() if self._available(el)]
        if not available:
            return None

        heading_toward = [
            el for el in available if
            (el.status == ElevatorStatus.UP and el.cur_floor <= passenger.source) or
            (el.status == ElevatorStatus.DOWN and el.cur_floor >= passenger.source) or
            (el.status == ElevatorStatus.STOPPED)
        ]

        if heading_toward:
            return min(heading_toward, key=lambda el: (
                abs(el.cur_floor - passenger.source),
                self._estimated_travel_time(el, passenger),
            ))

        going_away = [
            el for el in available if
            (el.status == ElevatorStatus.UP and el.cur_floor > passenger.source) or
            (el.status == ElevatorStatus.DOWN and el.cur_floor < passenger.source)
        ]

        def effective_distance(el: Elevator) -> int:
            all_dests = [p.dest for p in el.current_passengers + el.assigned_passengers]
            if not all_dests:
                return abs(el.cur_floor - passenger.source)
            turn_floor = max(all_dests) if el.status == ElevatorStatus.UP else min(all_dests)
            return abs(el.cur_floor - turn_floor) + abs(turn_floor - passenger.source)

        return min(going_away, key=lambda el: (
            effective_distance(el),
            self._estimated_travel_time(el, passenger),
        ))

    def schedule(self, passengers_to_serve: list):
        """Assign each passenger to the nearest available car, waitlisting any that cannot be served."""
        all_passengers = self.waitlist + passengers_to_serve
        self.waitlist = []

        for passenger in all_passengers:
            elevator = self._find_best_elevator(passenger)
            if elevator:
                elevator.assigned_passengers.append(passenger)
            else:
                self.waitlist.append(passenger)
