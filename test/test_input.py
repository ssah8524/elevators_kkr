import pytest
from src.io.input import parse_passenger_id, parse_row, parse_csv, PoissonArrivalProcess


# --- parse_passenger_id ---

def test_parse_passenger_id_valid():
    assert parse_passenger_id("passenger3") == 3


def test_parse_passenger_id_case_insensitive():
    assert parse_passenger_id("Passenger10") == 10


def test_parse_passenger_id_invalid_raises():
    with pytest.raises(ValueError):
        parse_passenger_id("p3")


# --- parse_row ---

def test_parse_row_valid():
    raw = {"time": "5", "id": "passenger2", "source": "3", "dest": "8"}
    p = parse_row(raw, num_floors=10)
    assert p.request_time == 5
    assert p.passenger_id == 2
    assert p.source == 3
    assert p.dest == 8


def test_parse_row_floor_out_of_range_raises():
    raw = {"time": "0", "id": "passenger1", "source": "3", "dest": "99"}
    with pytest.raises(ValueError):
        parse_row(raw, num_floors=10)


def test_parse_row_bad_time_raises():
    raw = {"time": "abc", "id": "passenger1", "source": "1", "dest": "5"}
    with pytest.raises(ValueError):
        parse_row(raw, num_floors=10)


# --- PoissonArrivalProcess ---

def test_poisson_simulate_returns_passengers_on_correct_floor():
    process = PoissonArrivalProcess(lam=2.0, seed=42)
    passengers = process.simulate(num_slots=10, src_floor=3, num_floors=10, cur_idx=1)
    assert all(p.source == 3 for p in passengers)


def test_poisson_simulate_destinations_differ_from_source():
    process = PoissonArrivalProcess(lam=5.0, seed=0)
    passengers = process.simulate(num_slots=20, src_floor=5, num_floors=10, cur_idx=1)
    assert all(p.dest != p.source for p in passengers)


def test_poisson_simulate_ids_are_sequential():
    process = PoissonArrivalProcess(lam=1.0, seed=7)
    passengers = process.simulate(num_slots=10, src_floor=1, num_floors=5, cur_idx=10)
    for i, p in enumerate(passengers):
        assert p.passenger_id == 10 + i


def test_poisson_simulate_deterministic_with_seed():
    p1 = PoissonArrivalProcess(lam=1.0, seed=99)
    p2 = PoissonArrivalProcess(lam=1.0, seed=99)
    r1 = p1.simulate(num_slots=20, src_floor=2, num_floors=10, cur_idx=1)
    r2 = p2.simulate(num_slots=20, src_floor=2, num_floors=10, cur_idx=1)
    assert [(p.request_time, p.source, p.dest) for p in r1] == \
           [(p.request_time, p.source, p.dest) for p in r2]
