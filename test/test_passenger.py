import pytest
from src.passenger import Passenger


def test_wait_time():
    p = Passenger(request_time=5, passenger_id=1, source=2, dest=10, entering_time=8)
    assert p.wait_time == 3


def test_travel_time():
    p = Passenger(request_time=0, passenger_id=1, source=1, dest=5, entering_time=2, exit_time=6)
    assert p.travel_time == 4


def test_defaults_are_none():
    p = Passenger(request_time=0, passenger_id=1, source=1, dest=2)
    assert p.entering_time is None
    assert p.exit_time is None
    assert p.total_time is None
