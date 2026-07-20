#!/usr/bin/env python3
"""
Mini Simulation 1: Pheromone Trail Formation
=============================================
Building block: stigmergic coordination via environmental traces.

Simple agents wander a grid. When they find food, they return to nest
leaving a pheromone trail. Pheromone decays over time. Other agents are
attracted to stronger pheromone. Tests: do trails form? How does decay
rate affect trail stability?

This is the most basic stigmergy algorithm — ant colony foraging.
It gives us the foundational code for environmental traces, decay,
and agent-trace interaction that we'll need for larger simulations.

Run: python3 sim01_pheromone_trails.py
"""

import random
import math
from dataclasses import dataclass, field
from typing import List, Tuple

# --- Parameters (testable) ---
GRID_W = 60
GRID_H = 60
NUM_ANTS = 50
NUM_FOOD = 5
NEST_X, NEST_Y = GRID_W // 2, GRID_H // 2
MAX_STEPS = 2000
PHEROMONE_DEPOSIT = 100.0
PHEROMONE_DECAY = 0.02  # lambda — sweep this parameter
PHEROMONE_THRESHOLD = 0.01
SENSOR_RANGE = 3
RANDOM_TURN_PROB = 0.1
TURN_ANGLE = math.pi / 4


@dataclass
class Ant:
    x: float
    y: float
    angle: float
    has_food: bool = False
    steps_since_food: int = 0


@dataclass
class World:
    width: int
    height: int
    pheromone: list  # 2D grid of float
    food: dict  # (x,y) -> amount
    nest: Tuple[int, int]
    ants: List[Ant] = field(default_factory=list)
    step: int = 0

    @classmethod
    def create(cls, w, h):
        return cls(
            width=w, height=h,
            pheromone=[[0.0] * h for _ in range(w)],
            food={},
            nest=(NEST_X, NEST_Y)
        )


def place_food(world):
    """Scatter food sources around the grid."""
    for _ in range(NUM_FOOD):
        fx = random.randint(5, world.width - 5)
        fy = random.randint(5, world.height - 5)
        world.food[(fx, fy)] = 100


def create_ants(world):
    """Spawn ants at the nest."""
    for _ in range(NUM_ANTS):
        world.ants.append(Ant(
            x=NEST_X + random.uniform(-2, 2),
            y=NEST_Y + random.uniform(-2, 2),
            angle=random.uniform(0, 2 * math.pi)
        ))


def sense_pheromone(world, ant, angle_offset=0):
    """Sense pheromone ahead of the ant."""
    sense_angle = ant.angle + angle_offset
    sx = int(ant.x + math.cos(sense_angle) * SENSOR_RANGE)
    sy = int(ant.y + math.sin(sense_angle) * SENSOR_RANGE)
    if 0 <= sx < world.width and 0 <= sy < world.height:
        return world.pheromone[sx][sy]
    return 0.0


def move_ant(world, ant):
    """Move ant, deposit pheromone if returning with food."""
    # Sensing: check left, center, right
    left = sense_pheromone(world, ant, -TURN_ANGLE)
    center = sense_pheromone(world, ant, 0)
    right = sense_pheromone(world, ant, TURN_ANGLE)

    if random.random() > RANDOM_TURN_PROB:
        if center >= left and center >= right:
            pass  # go straight
        elif left > right:
            ant.angle -= TURN_ANGLE
        elif right > left:
            ant.angle += TURN_ANGLE
    else:
        ant.angle += random.uniform(-TURN_ANGLE, TURN_ANGLE)

    # Move
    ant.x += math.cos(ant.angle)
    ant.y += math.sin(ant.angle)

    # Wrap or bounce
    if ant.x < 0: ant.x = 0; ant.angle = math.pi - ant.angle
    if ant.x >= world.width: ant.x = world.width - 1; ant.angle = math.pi - ant.angle
    if ant.y < 0: ant.y = 0; ant.angle = -ant.angle
    if ant.y >= world.height: ant.y = world.height - 1; ant.angle = -ant.angle

    # Deposit pheromone if carrying food (trail back to nest)
    if ant.has_food:
        ix, iy = int(ant.x), int(ant.y)
        if 0 <= ix < world.width and 0 <= iy < world.height:
            world.pheromone[ix][iy] += PHEROMONE_DEPOSIT

    # Check if at nest
    dx = ant.x - world.nest[0]
    dy = ant.y - world.nest[1]
    if ant.has_food and math.sqrt(dx*dx + dy*dy) < 3:
        ant.has_food = False
        ant.angle += math.pi  # turn around

    # Check if on food
    fx, fy = int(ant.x), int(ant.y)
    if (fx, fy) in world.food and not ant.has_food:
        if world.food[(fx, fy)] > 0:
            world.food[(fx, fy)] -= 1
            ant.has_food = True
            ant.angle += math.pi  # turn around
            ant.steps_since_food = 0

    ant.steps_since_food += 1


def decay_pheromone(world):
    """Decay all pheromone."""
    for x in range(world.width):
        for y in range(world.height):
            if world.pheromone[x][y] > 0:
                world.pheromone[x][y] *= (1 - PHEROMONE_DECAY)
                if world.pheromone[x][y] < PHEROMONE_THRESHOLD:
                    world.pheromone[x][y] = 0.0


def count_trail_cells(world, threshold=1.0):
    """Count cells with significant pheromone — proxy for trail formation."""
    count = 0
    for x in range(world.width):
        for y in range(world.height):
            if world.pheromone[x][y] > threshold:
                count += 1
    return count


def run_simulation(decay_rate=0.02, verbose=True):
    """Run one simulation. Returns metrics."""
    global PHEROMONE_DECAY
    PHEROMONE_DECAY = decay_rate

    random.seed(42)
    world = World.create(GRID_W, GRID_H)
    place_food(world)
    create_ants(world)

    metrics = []
    for step in range(MAX_STEPS):
        for ant in world.ants:
            move_ant(world, ant)
        decay_pheromone(world)
        world.step = step

        if step % 200 == 0:
            trail_cells = count_trail_cells(world)
            food_left = sum(world.food.values())
            ants_with_food = sum(1 for a in world.ants if a.has_food)
            metrics.append({
                'step': step,
                'trail_cells': trail_cells,
                'food_remaining': food_left,
                'ants_carrying': ants_with_food
            })
            if verbose:
                print(f"  Step {step:4d} | trail_cells={trail_cells:4d} | food={food_left:3d} | carrying={ants_with_food:2d}")

    if verbose:
        print(f"\nFinal: trail_cells={count_trail_cells(world)}, food_remaining={sum(world.food.values())}")
    return metrics, world


if __name__ == "__main__":
    print("=== Mini Sim 1: Pheromone Trail Formation ===")
    print(f"Grid: {GRID_W}x{GRID_H}, Ants: {NUM_ANTS}, Food: {NUM_FOOD}")
    print(f"Decay rate: {PHEROMONE_DECAY}")
    print()

    print("Running baseline simulation...")
    metrics, world = run_simulation(decay_rate=0.02)

    print("\n--- Decay Rate Sweep ---")
    for decay in [0.001, 0.01, 0.02, 0.05, 0.1, 0.2]:
        m, _ = run_simulation(decay_rate=decay, verbose=False)
        final_trail = m[-1]['trail_cells']
        final_food = m[-1]['food_remaining']
        print(f"  decay={decay:.3f} | final_trail_cells={final_trail:4d} | food_remaining={final_food:3d}")

    print("\nDone. See simulations/README.md for analysis.")
