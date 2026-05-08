from src.io.input import PoissonArrivalProcess, parse_csv
from src.io.output import Output
from src.scheduler.round_robin import RoundRobin
from src.elevator import Elevator

total_time_slots = 100
num_floors = 60
num_elevators = 10
max_passengers_per_elevator = 10
elevator_position_file_name = 'elevator_position.csv'

## Create an input sequence or read the file containing the input if one is provided

input_path = "data/input.csv"
input_data = parse_csv(input_path, num_floors)

if input_data is None:
    # Generate passengers per floor according to a Poisson distribution
    idx = 1
    input_data = []
    for i in range(1, num_floors + 1):
        process_per_floor = PoissonArrivalProcess(lam=0.1, seed=42)
        arrivals_per_floor = process_per_floor.simulate(num_slots=total_time_slots, src_floor=i, num_floors=num_floors, cur_idx=idx)
        idx += len(arrivals_per_floor)
        input_data = input_data + arrivals_per_floor

input_data.sort(key=lambda r: r.time)

## Perform Scheduling of passengers and assign them to elevators

output = Output(elevator_position_file_name, num_elevators)
elevators = [Elevator(i, num_floors, max_passengers_per_elevator, 0) for i in range(num_elevators)]
scheduler = RoundRobin(elevators)
for i in range(total_time_slots):
    passengers_to_serve = [input_data[j] for j in range(input_data) if input_data[j].request_time == i]
    scheduler.schedule(passengers_to_serve)

    for elevator in elevators:
        elevator.move(i)
    output.log_elevator_position(elevators, i)

## Obtain passenger delay statistics

wait_times = []
travel_times = []
total_times = []
for passenger in input_data:
    passenger.total_time = passenger.wait_time + passenger.travel_time
    wait_times.append(passenger.wait_time)
    travel_times.append(passenger.travel_time)
    total_times.append(passenger.total_time)


