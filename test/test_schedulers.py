import pytest
from src.elevator import Elevator, ElevatorStatus
from src.passenger import Passenger
from src.scheduler.round_robin import RoundRobin
from src.scheduler.nearest_car import NearestCar
from src.scheduler.nearest_idle import NearestIdle
from src.scheduler.least_committed import LeastCommitted
from src.scheduler.weighted_score import WeightedScore
from src.scheduler.zone import ZoneScheduler


def make_elevator(cur_floor, num_floors=20, max_passengers=5, status=ElevatorStatus.STOPPED):
    return Elevator(num_floors=num_floors, max_passengers=max_passengers, cur_floor=cur_floor, status=status)


def make_passenger(src, dest, pid=1, request_time=0):
    return Passenger(request_time=request_time, passenger_id=pid, source=src, dest=dest)


def make_fleet(floors, **kwargs):
    return {i: make_elevator(f, **kwargs) for i, f in enumerate(floors)}


# --- RoundRobin ---

class TestRoundRobin:
    def test_assigns_to_first_elevator(self):
        fleet = make_fleet([1, 10])
        sched = RoundRobin(fleet)
        p = make_passenger(5, 15)
        sched.schedule([p])
        assert p in fleet[0].assigned_passengers

    def test_rotates_to_next_elevator(self):
        fleet = make_fleet([1, 10])
        sched = RoundRobin(fleet)
        p1 = make_passenger(1, 5, pid=1)
        p2 = make_passenger(2, 6, pid=2)
        sched.schedule([p1, p2])
        assert p1 in fleet[0].assigned_passengers
        assert p2 in fleet[1].assigned_passengers

    def test_waitlists_when_all_full(self):
        fleet = make_fleet([1], max_passengers=1)
        sched = RoundRobin(fleet)
        p1 = make_passenger(1, 5, pid=1)
        p2 = make_passenger(2, 6, pid=2)
        fleet[0].current_passengers = [p1]
        sched.schedule([p2])
        assert p2 in sched.waitlist

    def test_waitlist_retried_next_tick(self):
        fleet = make_fleet([1], max_passengers=1)
        sched = RoundRobin(fleet)
        p = make_passenger(1, 5)
        fleet[0].current_passengers = [make_passenger(2, 6)]
        sched.schedule([p])
        assert p in sched.waitlist
        fleet[0].current_passengers = []
        sched.schedule([])
        assert p in fleet[0].assigned_passengers
        assert not sched.waitlist


# --- NearestCar ---

class TestNearestCar:
    def test_assigns_to_closest_elevator(self):
        fleet = make_fleet([2, 18])
        sched = NearestCar(fleet)
        p = make_passenger(src=3, dest=10)
        sched.schedule([p])
        assert p in fleet[0].assigned_passengers

    def test_prefers_elevator_heading_toward_passenger(self):
        fleet = {
            0: make_elevator(cur_floor=5, status=ElevatorStatus.UP),
            1: make_elevator(cur_floor=4, status=ElevatorStatus.DOWN),
        }
        sched = NearestCar(fleet)
        p = make_passenger(src=8, dest=15)
        sched.schedule([p])
        assert p in fleet[0].assigned_passengers

    def test_waitlists_when_all_full(self):
        fleet = make_fleet([5], max_passengers=1)
        fleet[0].current_passengers = [make_passenger(1, 2)]
        sched = NearestCar(fleet)
        p = make_passenger(5, 10)
        sched.schedule([p])
        assert p in sched.waitlist


# --- NearestIdle ---

class TestNearestIdle:
    def test_prefers_idle_over_moving(self):
        fleet = {
            0: make_elevator(cur_floor=4, status=ElevatorStatus.UP),
            1: make_elevator(cur_floor=6, status=ElevatorStatus.STOPPED),
        }
        sched = NearestIdle(fleet)
        p = make_passenger(src=5, dest=10)
        sched.schedule([p])
        assert p in fleet[1].assigned_passengers

    def test_falls_back_to_nearest_car_when_no_idle(self):
        fleet = {
            0: make_elevator(cur_floor=2, status=ElevatorStatus.UP),
            1: make_elevator(cur_floor=15, status=ElevatorStatus.DOWN),
        }
        sched = NearestIdle(fleet)
        p = make_passenger(src=3, dest=10)
        sched.schedule([p])
        assert p in fleet[0].assigned_passengers


# --- LeastCommitted ---

class TestLeastCommitted:
    def test_assigns_to_least_loaded(self):
        fleet = make_fleet([1, 10])
        p_existing = make_passenger(1, 5, pid=99)
        fleet[0].current_passengers = [p_existing]
        sched = LeastCommitted(fleet)
        p = make_passenger(3, 8)
        sched.schedule([p])
        assert p in fleet[1].assigned_passengers

    def test_waitlists_when_all_full(self):
        fleet = make_fleet([5], max_passengers=1)
        fleet[0].current_passengers = [make_passenger(1, 2)]
        sched = LeastCommitted(fleet)
        p = make_passenger(5, 10)
        sched.schedule([p])
        assert p in sched.waitlist


# --- WeightedScore ---

class TestWeightedScore:
    def test_pure_proximity_matches_nearest_car(self):
        fleet = make_fleet([2, 18])
        sched = WeightedScore(fleet, alpha=1.0, beta=0.0)
        p = make_passenger(src=3, dest=10)
        sched.schedule([p])
        assert p in fleet[0].assigned_passengers

    def test_pure_load_balancing_picks_least_loaded(self):
        fleet = make_fleet([1, 2])
        fleet[0].current_passengers = [make_passenger(1, 5, pid=99)]
        sched = WeightedScore(fleet, alpha=0.0, beta=1.0)
        p = make_passenger(src=1, dest=10)
        sched.schedule([p])
        assert p in fleet[1].assigned_passengers


# --- ZoneScheduler ---

class TestZoneScheduler:
    def test_assigns_to_correct_zone(self):
        fleet = make_fleet([1, 11], num_floors=20)
        sched = ZoneScheduler(fleet)
        p_low = make_passenger(src=3, dest=15, pid=1)
        p_high = make_passenger(src=15, dest=3, pid=2)
        sched.schedule([p_low, p_high])
        assert p_low in fleet[0].assigned_passengers
        assert p_high in fleet[1].assigned_passengers

    def test_waitlists_when_zone_elevator_full(self):
        fleet = make_fleet([1, 11], num_floors=20, max_passengers=1)
        fleet[0].current_passengers = [make_passenger(1, 5, pid=99)]
        sched = ZoneScheduler(fleet)
        p = make_passenger(src=3, dest=15)
        sched.schedule([p])
        assert p in sched.waitlist
