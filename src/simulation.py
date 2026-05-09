import copy
from typing import Type
import numpy as np

from src.elevator import Elevator
from src.passenger import Passenger
from src.scheduler.scheduler import Scheduler
from src.io.input import PoissonArrivalProcess


def generate_input(
    num_floors: int,
    total_time_slots: int,
    load_per_floor_per_slot: float,
    seed: int = None,
) -> list[Passenger]:
    """Generate a stochastic passenger sequence via a Poisson arrival process."""
    idx = 1
    input_data = []
    for i in range(1, num_floors + 1):
        process = PoissonArrivalProcess(
            lam=load_per_floor_per_slot / num_floors, seed=seed
        )
        arrivals = process.simulate(
            num_slots=total_time_slots, src_floor=i, num_floors=num_floors, cur_idx=idx
        )
        idx += len(arrivals)
        input_data += arrivals
    input_data.sort(key=lambda p: p.request_time)
    return input_data


def run_simulation(
    num_elevators: int,
    max_passengers: int,
    num_floors: int,
    total_time_slots: int,
    scheduler_class: Type[Scheduler],
    input_data: list[Passenger],
) -> dict:
    """
    Run a full simulation and return statistics and trajectory data.
    Deep-copies input_data so the same dataset can be safely reused across algorithms.
    """
    passengers = copy.deepcopy(input_data)

    elevators = {i: Elevator(num_floors, max_passengers, 0) for i in range(num_elevators)}
    scheduler = scheduler_class(elevators)
    utilization = {i: [] for i in range(num_elevators)}
    positions = {i: [] for i in range(num_elevators)}

    def check_end() -> bool:
        return all(
            not el.current_passengers and not el.assigned_passengers
            for el in elevators.values()
        )

    for t in range(total_time_slots):
        for i, el in enumerate(elevators.values()):
            positions[i].append(el.cur_floor)
        passengers_to_serve = [p for p in passengers if p.request_time == t]
        scheduler.schedule(passengers_to_serve)
        for el in elevators.values():
            el.move(t)
        for i, el in enumerate(elevators.values()):
            utilization[i].append(len(el.current_passengers))

    t = total_time_slots
    while not check_end() or scheduler.waitlist:
        for i, el in enumerate(elevators.values()):
            positions[i].append(el.cur_floor)
        scheduler.schedule([])
        for el in elevators.values():
            el.move(t)
        for i, el in enumerate(elevators.values()):
            utilization[i].append(len(el.current_passengers))
        t += 1

    for i, el in enumerate(elevators.values()):
        positions[i].append(el.cur_floor)

    for p in passengers:
        if p.entering_time is not None and p.exit_time is not None:
            p.total_time = p.wait_time + p.travel_time

    served = [p for p in passengers if p.exit_time is not None]
    active_fractions = [
        sum(1 for v in utilization[i] if v > 0) / max(len(utilization[i]), 1)
        for i in range(num_elevators)
    ]

    return {
        "wait_times":      [p.wait_time for p in served],
        "travel_times":    [p.travel_time for p in served],
        "total_times":     [p.total_time for p in served],
        "active_fraction": float(np.mean(active_fractions)),
        "avg_load":        float(np.mean([np.mean(utilization[i]) for i in range(num_elevators)])),
        "positions":       positions,
        "total_ticks":     t,
        "passengers":      passengers,
        "num_served":      len(served),
        "num_total":       len(passengers),
    }
