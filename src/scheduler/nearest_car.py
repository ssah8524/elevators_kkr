from src.scheduler.scheduler import Scheduler


class NearestCar(Scheduler):
    def __init__(self, elevators: list):
        super().__init__(elevators)

    def schedule(self, users_to_serve: list):
        pass