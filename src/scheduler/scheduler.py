from abc import ABC, abstractmethod

from src.elevator import Elevator
from src.passenger import Passenger

class Scheduler(ABC):
    def __init__(self, elevator_dict: dict):
        self.elevators = elevator_dict
        self.waitlist: list[Passenger] = []

    @staticmethod
    def _available(elevator: Elevator) -> bool:
        committed = len(elevator.current_passengers) + len(elevator.assigned_passengers)
        return committed < elevator.max_passengers

    @abstractmethod
    def schedule(self, passengers_to_serve: list):
        pass