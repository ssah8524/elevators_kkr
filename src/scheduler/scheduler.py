from abc import ABC, abstractmethod

class Scheduler(ABC):
    def __init__(self, elevator_dict: dict):
        self.elevators = elevator_dict

    @abstractmethod
    def schedule(self, passengers_to_serve: list):
        pass