from enum import Enum

from src.passenger import Passenger


class ElevatorStatus(Enum):
    STOPPED = 0
    UP = 1
    DOWN = 2

class Elevator:
    def __init__(self, num_floors: int, max_passengers: int, cur_floor: int, status: ElevatorStatus=ElevatorStatus.STOPPED):
        self.max_passengers = max_passengers
        self.cur_floor = cur_floor
        self.num_floors = num_floors
        self.status = status
        self.assigned_passengers: list[Passenger] = []
        self.current_passengers: list[Passenger] = []

    def _drop_off(self, time):
        arrived_passengers = [passenger for passenger in self.current_passengers if passenger.dest == self.cur_floor]
        for passenger in arrived_passengers:
            passenger.exit_time = time + 1

        self.current_passengers = [passenger for passenger in self.current_passengers if passenger.dest != self.cur_floor]

        return

    def _pick_up(self):
        passengers_to_enter = [passenger for passenger in self.assigned_passengers if passenger.source == self.cur_floor]
        self.current_passengers = self.current_passengers + passengers_to_enter
        #TODO: add entry time for each picked up passenger
        self.assigned_passengers = [passenger for passenger in self.assigned_passengers if passenger.source != self.cur_floor]

    def move(self, time):
        self._pick_up()
        if self.status == ElevatorStatus.UP:
            if self.cur_floor < self.num_floors:
                self.cur_floor += 1
            else:
                self.status = ElevatorStatus.STOPPED
        elif self.status == ElevatorStatus.DOWN:
            if self.cur_floor > 1:
                self.cur_floor -= 1
            else:
                self.status = ElevatorStatus.STOPPED

        self._drop_off(time)
        if not self.current_passengers:
            self.status = ElevatorStatus.STOPPED
