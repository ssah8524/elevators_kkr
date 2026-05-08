from collections import deque

from src.scheduler.scheduler import Scheduler

class RoundRobin(Scheduler):
    def __init__(self, elevators: list):
        super().__init__(elevators)
        self.window = deque(maxlen=len(self.elevators))

    def schedule(self, passengers_to_serve: list):
        pass