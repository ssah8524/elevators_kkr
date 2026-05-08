from abc import ABC, abstractmethod

class Scheduler(ABC):
    def __init__(self, elevators: list):
        self.elevators = elevators

    @abstractmethod
    def schedule(self, users_to_serve: list):
        pass