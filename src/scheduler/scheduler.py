from abc import ABC, abstractmethod

from src.elevator import Elevator
from src.passenger import Passenger

class Scheduler(ABC):
    def __init__(self, elevator_dict: dict):
        """Store the elevator fleet and initialise an empty waitlist."""
        self.elevators = elevator_dict
        self.waitlist: list[Passenger] = []

    @staticmethod
    def _available(elevator: Elevator) -> bool:
        """Return True if the elevator has capacity for at least one more passenger."""
        committed = len(elevator.current_passengers) + len(elevator.assigned_passengers)
        return committed < elevator.max_passengers

    @abstractmethod
    def schedule(self, passengers_to_serve: list):
        """Assign passengers_to_serve (plus any waitlisted passengers) to elevators."""
        pass