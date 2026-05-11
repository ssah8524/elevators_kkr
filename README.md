# Elevator Scheduling System

A discrete-time simulation of an intelligent multi-elevator system. Passenger requests are generated stochastically or loaded from a CSV file, assigned to elevators by a scheduling algorithm, and served according to a LOOK movement policy. Multiple scheduling algorithms are implemented and compared across a range of arrival loads and building configurations.

---

## Project Structure

```
src/
  elevator.py          # Elevator state machine and movement logic
  passenger.py         # Passenger dataclass
  simulation.py        # Simulation runner (used by notebook and slide generator)
  io/
    input.py           # CSV parser and Poisson arrival process
    output.py          # Elevator position logger
  scheduler/
    scheduler.py       # Abstract base class
    round_robin.py     # Round Robin
    nearest_car.py     # Nearest Car
    nearest_idle.py    # Nearest Idle
    least_committed.py # Least Committed
    weighted_score.py  # Weighted Score (α · pickup time + β · committed count)
    zone.py            # Static Hard Zone Scheduler
presentation.ipynb     # Jupyter notebook with full analysis
main.py                # CLI entry point
data/input.csv         # Manual passenger input (gitignored)
```

---

## How to Run

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### CLI simulation

```bash
python main.py [options]

Options:
  --elevators N          Number of elevators (default: 10)
  --max-passengers N     Capacity per elevator (default: 10)
  --floors N             Number of floors (default: 60)
  --time-slots N         Simulation duration in ticks (default: 100)
  --load F               Passengers per floor per tick, e.g. 0.1 (stochastic only)
  --input {manual,stochastic}
  --input-file PATH      CSV file path (manual mode only)
  --scheduler {round-robin, nearest-car, nearest-car-simple, nearest-idle, weighted-score, least-committed}
```

**Manual input** (from CSV):
```bash
python main.py --input manual --input-file data/input.csv --scheduler nearest-car
```

**Stochastic input**:
```bash
python main.py --input stochastic --load 0.1 --elevators 5 --scheduler round-robin
```

CSV format:
```
time,id,source,dest
0,passenger1,1,51
6,passenger4,23,10
```

### Jupyter notebook

```bash
jupyter lab presentation.ipynb
```

Run all cells top to bottom. The load sweep (500 trials × 13 load points) takes several minutes.

---

## Assumptions and Simplifications

**Discrete time**
One tick equals one floor of travel. This ignores acceleration, door open/close time, and variable floor heights. It keeps the model analytically clean and focuses comparison on scheduling logic rather than physics.

**Capacity enforced at scheduling time**
When a passenger is assigned to an elevator, a slot is immediately reserved (`committed = current + assigned < max`). This prevents overloading even when passengers board at different future floors, but it may be overly conservative: an elevator passing through a pickup floor with fewer passengers than expected could have taken one more.

**Elevator movement policy**
Elevators sweep in one direction until no remaining targets (on-board destinations or assigned pickup floors) lie ahead, then reverse. This is the same policy used in real elevator controllers and disk scheduling. Elevators do not skip floors to pick up a passenger going the wrong way.

**Uniform floor distribution**
The Poisson arrival process generates passengers uniformly across all floors. Real buildings have non-uniform demand (ground floor, cafeteria floor, car park). This simplification makes load-sweep comparisons cleaner.

**Elevators start at random floors**
At the start of each simulation run, each elevator is placed at a floor sampled uniformly from [1, N]. This removes the cold-start bias that arises when all elevators begin at the ground floor, and better reflects a real building where elevators are distributed throughout the shaft at any given moment. Because the same random initialisation applies to all algorithms within a trial, comparisons remain fair.

**Single building, no inter-elevator coordination**
Schedulers make greedy, per-passenger decisions with no global look-ahead or cooperative re-assignment once a passenger is assigned.

---

## Time Spent

**3 days · ~22 hours**

Roughly split across: simulation engine and elevator logic (~7 h), scheduler implementations and debugging (~7 h), statistical analysis framework and Jupyter notebook (~5 h), Result interpretation and slides (~3 h).

---

## What I Would Improve With More Time

**1. Accurate capacity estimation at pickup time**
The current model reserves a slot at scheduling time based on the committed count, but it does not check how many passengers will still be on board when the elevator actually reaches the pickup floor. An elevator assigned five passengers all departing before the pickup floor could take on more; one with passengers boarding between now and the pickup could be full on arrival. Implementing a projected-occupancy function — simulating the elevator's route leg by leg and tracking boardings and alightings — would make the capacity check accurate rather than conservative.

**2. Express elevators**
Real high-rise buildings designate certain elevators as express: they only stop at a subset of floors (e.g. floors 1 and 30–60). The simulation model supports this naturally since the elevator movement policy already only stops at floors with assigned passengers. The required changes are: (a) add a `served_floors` set to the `Elevator` class, (b) filter assigned passengers in `_pick_up` to only those whose source is in that set, (c) extend the scheduler to route local vs express requests to the appropriate elevator pool. This would enable a new class of zone-based algorithm where zones are defined by express/local designation rather than floor ranges.

**3. Algorithms that jointly optimise load balancing and wait time**
The clearest finding from the simulation is that load balancing (Round Robin, Zone) and wait time minimisation (Nearest Car, Nearest Idle) pull in different directions — no single algorithm dominates across all load levels. The natural next step is a hybrid that optimises a joint objective. Two concrete directions: (a) a **Minimum Estimated Total Time** scheduler that scores each elevator by the passenger's estimated full journey time (wait until pickup + travel to destination), which naturally discounts overloaded elevators because their pickup time is longer; (b) the **Weighted Score** scheduler already implemented (`α · pickup_time + β · committed_count`) with `α` and `β` tuned empirically or via a sweep — the load-sweep plots make it straightforward to identify which load regime benefits from shifting weight toward one term or the other.
