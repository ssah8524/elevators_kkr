import pytest
from src.elevator import Elevator, ElevatorStatus
from src.passenger import Passenger


def make_passenger(src, dest, request_time=0, pid=1):
    return Passenger(request_time=request_time, passenger_id=pid, source=src, dest=dest)


# --- _pick_up ---

def test_pick_up_boards_passenger_at_source():
    el = Elevator(num_floors=10, max_passengers=5, cur_floor=3)
    p = make_passenger(src=3, dest=8)
    el.assigned_passengers = [p]
    el._pick_up(time=0)
    assert p in el.current_passengers
    assert p not in el.assigned_passengers
    assert p.entering_time == 0


def test_pick_up_does_not_board_passenger_at_wrong_floor():
    el = Elevator(num_floors=10, max_passengers=5, cur_floor=3)
    p = make_passenger(src=5, dest=8)
    el.assigned_passengers = [p]
    el._pick_up(time=0)
    assert p not in el.current_passengers
    assert p in el.assigned_passengers


# --- _drop_off ---

def test_drop_off_removes_passenger_at_destination():
    el = Elevator(num_floors=10, max_passengers=5, cur_floor=8)
    p = make_passenger(src=3, dest=8, request_time=0)
    p.entering_time = 1
    el.current_passengers = [p]
    el._drop_off(time=5)
    assert p not in el.current_passengers
    assert p.exit_time == 6


def test_drop_off_keeps_passenger_not_at_destination():
    el = Elevator(num_floors=10, max_passengers=5, cur_floor=4)
    p = make_passenger(src=1, dest=8)
    p.entering_time = 1
    el.current_passengers = [p]
    el._drop_off(time=5)
    assert p in el.current_passengers


# --- _set_direction (LOOK policy) ---

def test_direction_up_when_target_above():
    el = Elevator(num_floors=10, max_passengers=5, cur_floor=3, status=ElevatorStatus.STOPPED)
    el.assigned_passengers = [make_passenger(src=7, dest=9)]
    el._set_direction()
    assert el.status == ElevatorStatus.UP


def test_direction_down_when_target_below():
    el = Elevator(num_floors=10, max_passengers=5, cur_floor=8, status=ElevatorStatus.STOPPED)
    el.assigned_passengers = [make_passenger(src=2, dest=5)]
    el._set_direction()
    assert el.status == ElevatorStatus.DOWN


def test_direction_stopped_when_no_passengers():
    el = Elevator(num_floors=10, max_passengers=5, cur_floor=5, status=ElevatorStatus.UP)
    el._set_direction()
    assert el.status == ElevatorStatus.STOPPED


def test_look_reverses_when_no_targets_ahead():
    el = Elevator(num_floors=10, max_passengers=5, cur_floor=8, status=ElevatorStatus.UP)
    p = make_passenger(src=2, dest=4)
    p.entering_time = 0
    el.current_passengers = [p]
    el._set_direction()
    assert el.status == ElevatorStatus.DOWN


def test_look_continues_up_when_targets_ahead():
    el = Elevator(num_floors=10, max_passengers=5, cur_floor=4, status=ElevatorStatus.UP)
    p = make_passenger(src=2, dest=9)
    p.entering_time = 0
    el.current_passengers = [p]
    el._set_direction()
    assert el.status == ElevatorStatus.UP


# --- move ---

def test_move_increments_floor_going_up():
    el = Elevator(num_floors=10, max_passengers=5, cur_floor=3, status=ElevatorStatus.UP)
    el.assigned_passengers = [make_passenger(src=7, dest=9)]
    el.move(time=0)
    assert el.cur_floor == 4


def test_move_decrements_floor_going_down():
    el = Elevator(num_floors=10, max_passengers=5, cur_floor=5, status=ElevatorStatus.DOWN)
    el.assigned_passengers = [make_passenger(src=2, dest=4)]
    el.move(time=0)
    assert el.cur_floor == 4


def test_move_does_not_exceed_top_floor():
    el = Elevator(num_floors=10, max_passengers=5, cur_floor=10, status=ElevatorStatus.UP)
    p = make_passenger(src=10, dest=10)
    el.assigned_passengers = [p]
    el.move(time=0)
    assert el.cur_floor == 10


def test_move_does_not_go_below_floor_1():
    el = Elevator(num_floors=10, max_passengers=5, cur_floor=1, status=ElevatorStatus.DOWN)
    p = make_passenger(src=1, dest=1)
    el.assigned_passengers = [p]
    el.move(time=0)
    assert el.cur_floor == 1
