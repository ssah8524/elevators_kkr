from src.elevator import Elevator
from src.scheduler.scheduler import Scheduler

class RoundRobin(Scheduler):
    def __init__(self, elevator_dict: dict):
        """Initialise with a rotating pointer starting at elevator 0."""
        super().__init__(elevator_dict)
        self.elevator_head = 0

    @staticmethod
    def _available(elevator: Elevator) -> bool:
        """Return True if the elevator has capacity for at least one more passenger."""
        committed = len(elevator.current_passengers) + len(elevator.assigned_passengers)
        return committed < elevator.max_passengers

    def schedule(self, passengers_to_serve: list):
        """Assign each passenger to the next available elevator in rotation."""
        all_passengers = self.waitlist + passengers_to_serve
        self.waitlist = []

        for passenger in all_passengers:
            assigned = False
            for i in range(len(self.elevators)):
                idx = (self.elevator_head + i) % len(self.elevators)
                if self._available(self.elevators[idx]):
                    self.elevators[idx].assigned_passengers.append(passenger)
                    self.elevator_head = (idx + 1) % len(self.elevators)
                    assigned = True
                    break
            if not assigned:
                self.waitlist.append(passenger)


