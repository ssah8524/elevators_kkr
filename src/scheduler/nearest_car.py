from src.scheduler.scheduler import Scheduler


class NearestCar(Scheduler):
    def __init__(self, elevator_dict: dict):
        super().__init__(elevator_dict)

    def schedule(self, passengers_to_serve: list):
        pass