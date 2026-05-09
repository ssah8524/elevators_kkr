from typing import List

from src.io.input import PoissonArrivalProcess, parse_csv
from src.io.output import Output
from src.scheduler.round_robin import RoundRobin
from src.scheduler.nearest_car import NearestCar
from src.elevator import Elevator


def check_end(elevators: List[Elevator]) -> bool:
    end = True
    for el in elevators:
        if el.current_passengers or el.assigned_passengers:
            end = False
            break
    return end

total_time_slots = 100
num_floors = 60
num_elevators = 10
max_passengers_per_elevator = 10
elevator_position_file_name = 'elevator_position.csv'
load_per_floor_per_slot = 0.1

## Create an input sequence or read the file containing the input if one is provided

input_path = "data/input.csv"
input_data = parse_csv(input_path, num_floors)

if input_data is None:
    # Generate passengers per floor according to a Poisson distribution
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
elevators = {i: Elevator(num_floors, max_passengers_per_elevator, 0) for i in range(num_elevators)}

rr_scheduler = RoundRobin(elevators)
nc_scheduler = NearestCar(elevators)
scheduler = nc_scheduler
for t in range(total_time_slots):
    output.log_elevator_position(list(elevators.values()), t)
    passengers_to_serve = [passenger for passenger in input_data if passenger.request_time == t]
    scheduler.schedule(passengers_to_serve)

    for elevator in list(elevators.values()):
        elevator.move(t)

## Continue to fulfill requests until all passengers arrive

t = total_time_slots
while not check_end(list(elevators.values())) or scheduler.waitlist:
    scheduler.schedule([])
    for elevator in list(elevators.values()):
        elevator.move(t)
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

print(wait_times)
print(travel_times)
print(total_times)