from abc import ABC, abstractmethod

class Scheduler(ABC):
    def __init__(self, elevators: list):
        self.elevators = elevators

    @abstractmethod
    def schedule(self, passengers_to_serve: list):
        pass