import pytest
from src.simulation import generate_input, run_simulation
from src.scheduler.round_robin import RoundRobin
from src.scheduler.nearest_car import NearestCar


BASE_CONFIG = dict(
    num_elevators=2,
    max_passengers=5,
    num_floors=10,
    total_time_slots=20,
)


# --- generate_input ---

def test_generate_input_returns_passengers():
    passengers = generate_input(num_floors=10, total_time_slots=50, load_per_floor_per_slot=5.0, seed=0)
    assert len(passengers) > 0


def test_generate_input_sorted_by_request_time():
    passengers = generate_input(num_floors=10, total_time_slots=20, load_per_floor_per_slot=0.5, seed=1)
    times = [p.request_time for p in passengers]
    assert times == sorted(times)


def test_generate_input_sources_within_floor_range():
    passengers = generate_input(num_floors=10, total_time_slots=20, load_per_floor_per_slot=0.5, seed=2)
    assert all(1 <= p.source <= 10 for p in passengers)
    assert all(1 <= p.dest <= 10 for p in passengers)


def test_generate_input_deterministic_with_seed():
    p1 = generate_input(num_floors=5, total_time_slots=10, load_per_floor_per_slot=1.0, seed=42)
    p2 = generate_input(num_floors=5, total_time_slots=10, load_per_floor_per_slot=1.0, seed=42)
    assert [(p.source, p.dest, p.request_time) for p in p1] == \
           [(p.source, p.dest, p.request_time) for p in p2]


# --- run_simulation ---

def test_run_simulation_all_passengers_served():
    passengers = generate_input(num_floors=10, total_time_slots=20, load_per_floor_per_slot=0.3, seed=5)
    result = run_simulation(**BASE_CONFIG, scheduler_class=RoundRobin, input_data=passengers)
    assert result["num_served"] == result["num_total"]


def test_run_simulation_wait_times_non_negative():
    passengers = generate_input(num_floors=10, total_time_slots=20, load_per_floor_per_slot=0.3, seed=6)
    result = run_simulation(**BASE_CONFIG, scheduler_class=NearestCar, input_data=passengers)
    assert all(t >= 0 for t in result["wait_times"])


def test_run_simulation_travel_times_positive():
    passengers = generate_input(num_floors=10, total_time_slots=20, load_per_floor_per_slot=0.3, seed=7)
    result = run_simulation(**BASE_CONFIG, scheduler_class=NearestCar, input_data=passengers)
    assert all(t > 0 for t in result["travel_times"])


def test_run_simulation_result_keys():
    passengers = generate_input(num_floors=10, total_time_slots=10, load_per_floor_per_slot=0.2, seed=8)
    result = run_simulation(**BASE_CONFIG, scheduler_class=RoundRobin, input_data=passengers)
    for key in ("wait_times", "travel_times", "total_times", "active_fraction", "avg_load",
                "positions", "total_ticks", "passengers", "num_served", "num_total"):
        assert key in result


def test_run_simulation_does_not_mutate_input():
    passengers = generate_input(num_floors=10, total_time_slots=10, load_per_floor_per_slot=0.3, seed=9)
    original = [(p.source, p.dest, p.request_time) for p in passengers]
    run_simulation(**BASE_CONFIG, scheduler_class=RoundRobin, input_data=passengers)
    after = [(p.source, p.dest, p.request_time) for p in passengers]
    assert original == after


def test_run_simulation_fixed_start_floor():
    passengers = generate_input(num_floors=10, total_time_slots=10, load_per_floor_per_slot=0.3, seed=10)
    result = run_simulation(**BASE_CONFIG, scheduler_class=RoundRobin,
                            input_data=passengers, start_floor=1)
    for positions in result["positions"].values():
        assert positions[0] == 1
