from enum import Enum

from src.passenger import Passenger


class ElevatorStatus(Enum):
    STOPPED = 0
    UP = 1
    DOWN = 2

class Elevator:
    def __init__(self, elevator_id: int, num_floors: int, max_passengers: int, cur_floor: int, status: ElevatorStatus=ElevatorStatus.STOPPED):
        self.elevator_id = elevator_id
        self.max_passengers = max_passengers
        self.cur_floor = cur_floor
        self.status = status
        self.assigned_passengers = []
        self.current_passengers = []

    def move(self):
        if self.status = ElevatorStatus.UP:
            if cur_floor ==
