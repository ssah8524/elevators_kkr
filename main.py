import argparse
import random
import numpy as np
from typing import List

from src.io.input import PoissonArrivalProcess, parse_csv
from src.io.output import Output
from src.scheduler.round_robin import RoundRobin
from src.scheduler.nearest_car_simple import NearestCarSimple
from src.scheduler.nearest_car import NearestCar
from src.scheduler.nearest_idle import NearestIdle
from src.scheduler.least_committed import LeastCommitted
from src.scheduler.weighted_score import WeightedScore

from src.elevator import Elevator


def check_end(elevators: List[Elevator]) -> bool:
    """Return True when every elevator has no on-board or assigned passengers remaining."""
    for el in elevators:
        if el.current_passengers or el.assigned_passengers:
            return False
    return True


parser = argparse.ArgumentParser(description="Elevator simulation")
parser.add_argument("--elevators", type=int, default=10, help="Number of elevators")
parser.add_argument("--max-passengers", type=int, default=10, help="Max passengers per elevator")
parser.add_argument("--time-slots", type=int, default=100, help="Number of time slots")
parser.add_argument("--floors", type=int, default=60, help="Number of floors")
parser.add_argument("--load", type=float, default=0.1, help="Passenger load per floor per time slot (stochastic mode only)")
parser.add_argument("--input", choices=["manual", "stochastic"], default="stochastic", help="Input mode: manual (CSV file) or stochastic (Poisson)")
parser.add_argument("--input-file", type=str, default="data/input.csv", help="Path to input CSV file (manual mode only)")
parser.add_argument("--scheduler", choices=["round-robin", "nearest-car", "nearest-car-simple", "nearest-idle", "weighted-score", "least-committed"], default="round-robin", help="Scheduling algorithm to use")
args = parser.parse_args()

num_elevators = args.elevators
max_passengers_per_elevator = args.max_passengers
total_time_slots = args.time_slots
num_floors = args.floors
load_per_floor_per_slot = args.load

elevator_position_file_name = 'elevator_position.csv'

## Create an input sequence or read the file containing the input if one is provided

if args.input == "manual":
    if args.load != parser.get_default("load"):
        print("Warning: --load is ignored in manual mode")
    input_data = parse_csv(args.input_file, num_floors)
    if input_data is None:
        raise FileNotFoundError(f"Input file not found: {args.input_file}")
else:
    idx = 1
    input_data = []
    for i in range(1, num_floors + 1):
        process_per_floor = PoissonArrivalProcess(lam=load_per_floor_per_slot / num_floors, seed=None)
        arrivals_per_floor = process_per_floor.simulate(num_slots=total_time_slots, src_floor=i, num_floors=num_floors, cur_idx=idx)
        idx += len(arrivals_per_floor)
        input_data = input_data + arrivals_per_floor

input_data.sort(key=lambda r: r.request_time)

## Perform Scheduling of passengers and assign them to elevators

output = Output(elevator_position_file_name, num_elevators)
if args.input == "manual":
    elevators = {i: Elevator(num_floors, max_passengers_per_elevator, 1) for i in range(num_elevators)}
else:
    elevators = {i: Elevator(num_floors, max_passengers_per_elevator, random.randint(1, num_floors)) for i in range(num_elevators)}
utilization = {i: [] for i in range(num_elevators)}

scheduler = RoundRobin(elevators)
if args.scheduler == "nearest-car-simple":
    scheduler = NearestCarSimple(elevators)
elif args.scheduler == "nearest-car":
    scheduler = NearestCar(elevators)
elif args.scheduler == "nearest-idle":
    scheduler = NearestIdle(elevators)
elif args.scheduler == "least-committed":
    scheduler = LeastCommitted(elevators)
elif args.scheduler == "weighted-score":
    scheduler = WeightedScore(elevators)

for t in range(total_time_slots):
    output.log_elevator_position(list(elevators.values()), t)
    passengers_to_serve = [passenger for passenger in input_data if passenger.request_time == t]
    scheduler.schedule(passengers_to_serve)
    for elevator in list(elevators.values()):
        elevator.move(t)
    for i, elevator in enumerate(elevators.values()):
        utilization[i].append(len(elevator.current_passengers))

## Continue to fulfill requests until all passengers arrive

t = total_time_slots
while not check_end(list(elevators.values())) or scheduler.waitlist:
    scheduler.schedule([])
    for elevator in list(elevators.values()):
        elevator.move(t)
    for i, elevator in enumerate(elevators.values()):
        utilization[i].append(len(elevator.current_passengers))
    t += 1

## Obtain passenger delay statistics

wait_times = []
travel_times = []
total_times = []
for passenger in input_data:
    passenger.total_time = passenger.wait_time + passenger.travel_time
    wait_times.append(passenger.wait_time)
    travel_times.append(passenger.travel_time)
    total_times.append(passenger.total_time)

output.close()

## Print statistics

def print_stats(label: str, values: list):
    """Print min, max, mean, median, and std for a list of numeric values."""
    arr = np.array(values)
    print(f"\n{label}")
    print(f"  min:    {arr.min():.1f}")
    print(f"  max:    {arr.max():.1f}")
    print(f"  mean:   {arr.mean():.1f}")
    print(f"  median: {np.median(arr):.1f}")
    print(f"  std:    {arr.std():.1f}")

print_stats("Wait times", wait_times)
print_stats("Travel times", travel_times)
print_stats("Total times", total_times)

active_fractions = [sum(1 for v in utilization[i] if v > 0) / len(utilization[i]) for i in range(num_elevators)]
avg_loads = [np.mean(utilization[i]) for i in range(num_elevators)]

print(f"\nElevator utilization")
print(f"  avg active fraction: {np.mean(active_fractions):.2%}")
print(f"  avg load:            {np.mean(avg_loads):.2f} passengers/tick")