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

import os
import json
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


def move_ant(world, ant, sensing=True):
    """Move ant, deposit pheromone if returning with food.

    `sensing=False` is the pheromone-blind control: ants still deposit and the
    field still decays, but the trace carries no information back to them. It
    is the only way to show that any structure in the field is *caused by*
    stigmergic feedback rather than by the ants' movement statistics alone.
    Reporting all-sensing runs at several decay rates cannot establish that.

    Implemented by zeroing the sensed values rather than branching around the
    steering logic, so the control consumes the RNG identically and the two
    conditions differ only in whether the pheromone field is readable.
    """
    if sensing:
        # Sensing: check left, center, right
        left = sense_pheromone(world, ant, -TURN_ANGLE)
        center = sense_pheromone(world, ant, 0)
        right = sense_pheromone(world, ant, TURN_ANGLE)
    else:
        left = center = right = 0.0

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
    """Count cells with significant pheromone.

    NOTE: this is a COVERAGE measure, not a trail measure. A laden ant deposits
    PHEROMONE_DEPOSIT (100) every step and decay is 2%/step, so a visited cell
    stays above threshold ~230 steps. The count therefore reports "cells visited
    by a laden ant recently" and rises with mere wandering — it cannot tell a
    consolidated trail from ants spreading pheromone everywhere. Use
    trail_concentration() for trail structure. See ../REVIEW.md section 6.
    """
    count = 0
    for x in range(world.width):
        for y in range(world.height):
            if world.pheromone[x][y] > threshold:
                count += 1
    return count


def trail_concentration(world, top_frac=0.05):
    """Fraction of total pheromone held by the densest `top_frac` of cells.

    A consolidated trail concentrates pheromone into a narrow path; diffuse
    wandering spreads it evenly. A perfectly uniform field scores ~top_frac
    (0.05), so values well above that indicate real trail structure. This is
    the structural counterpart to count_trail_cells' coverage count.
    """
    vals = sorted(
        (world.pheromone[x][y] for x in range(world.width) for y in range(world.height)),
        reverse=True)
    total = sum(vals)
    if total <= 0:
        return 0.0
    k = max(1, int(len(vals) * top_frac))
    return sum(vals[:k]) / total


def run_simulation(decay_rate=0.02, verbose=True, collect_frames=False, sensing=True, seed=42):
    """Run one simulation. Returns metrics and optional frames for visualization.

    `sensing=False` runs the pheromone-blind control (see move_ant).
    """
    global PHEROMONE_DECAY
    PHEROMONE_DECAY = decay_rate

    random.seed(seed)
    world = World.create(GRID_W, GRID_H)
    place_food(world)
    create_ants(world)

    metrics = []
    frames = []
    for step in range(MAX_STEPS):
        for ant in world.ants:
            move_ant(world, ant, sensing=sensing)
        decay_pheromone(world)
        world.step = step

        if step % 200 == 0:
            trail_cells = count_trail_cells(world)
            concentration = trail_concentration(world)
            food_left = sum(world.food.values())
            ants_with_food = sum(1 for a in world.ants if a.has_food)
            metrics.append({
                'step': step,
                'trail_cells': trail_cells,
                'trail_concentration': concentration,
                'food_remaining': food_left,
                'ants_carrying': ants_with_food
            })
            if verbose:
                print(f"  Step {step:4d} | trail_cells={trail_cells:4d} | conc={concentration:.3f} "
                      f"| food={food_left:3d} | carrying={ants_with_food:2d}")

        if collect_frames and step % 50 == 0:
            # Snapshot: pheromone grid + ant positions + food
            ph = [row[:] for row in world.pheromone]
            ants = [(a.x, a.y, a.has_food) for a in world.ants]
            food = dict(world.food)
            frames.append({'step': step, 'pheromone': ph, 'ants': ants, 'food': food})

    if verbose:
        print(f"\nFinal: trail_cells={count_trail_cells(world)}, food_remaining={sum(world.food.values())}")
    return metrics, world, frames


def visualize():
    """Run simulation and save an animation + final heatmap as PNG."""
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import os

    print("Running simulation with frame collection...")
    metrics, world, frames = run_simulation(decay_rate=0.02, verbose=True, collect_frames=True)
    print(f"Collected {len(frames)} frames")

    outdir = os.path.dirname(os.path.abspath(__file__)) + "/output"
    os.makedirs(outdir, exist_ok=True)

    # --- Final heatmap ---
    ph_final = np.array(frames[-1]['pheromone'])
    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(ph_final.T, cmap='hot', origin='lower', interpolation='bilinear')

    # Mark nest
    ax.plot(world.nest[0], world.nest[1], 'go', markersize=12, label='Nest')
    # Mark food
    for (fx, fy), amt in frames[-1]['food'].items():
        if amt > 0:
            ax.plot(fx, fy, 'b^', markersize=10, label='Food' if 'Food' not in ax.get_legend_handles_labels()[1] else '')
    # Mark ants
    for ax_pos, ay_pos, has_food in frames[-1]['ants']:
        color = 'yellow' if has_food else 'cyan'
        ax.plot(ax_pos, ay_pos, '.', color=color, markersize=3)

    ax.set_title(f'Pheromone Field at Step {frames[-1]["step"]}\nDecay rate=0.02, Trail cells={count_trail_cells(world)}')
    ax.legend(loc='upper left', fontsize=8)
    plt.colorbar(im, ax=ax, label='Pheromone intensity')
    plt.tight_layout()
    plt.savefig(f"{outdir}/sim01_heatmap_final.png", dpi=150)
    print(f"Saved: {outdir}/sim01_heatmap_final.png")
    plt.close()

    # --- Animation ---
    fig, ax = plt.subplots(figsize=(8, 8))

    def update(frame_idx):
        ax.clear()
        f = frames[frame_idx]
        ph = np.array(f['pheromone'])
        max_ph = max(ph.max(), 1.0)
        ax.imshow(ph.T, cmap='hot', origin='lower', interpolation='bilinear', vmin=0, vmax=max_ph)
        ax.plot(world.nest[0], world.nest[1], 'go', markersize=12)
        for (fx, fy), amt in f['food'].items():
            if amt > 0:
                ax.plot(fx, fy, 'b^', markersize=10)
        for ax_pos, ay_pos, has_food in f['ants']:
            color = 'yellow' if has_food else 'cyan'
            ax.plot(ax_pos, ay_pos, '.', color=color, markersize=3)
        trail = sum(1 for row in ph for v in row if v > 1.0)
        ax.set_title(f'Step {f["step"]} | trail_cells={trail} | decay=0.02')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')

    print("Rendering animation...")
    anim = animation.FuncAnimation(fig, update, frames=len(frames), interval=200, blit=False)
    anim.save(f"{outdir}/sim01_animation.mp4", writer='ffmpeg', fps=5, dpi=100)
    print(f"Saved: {outdir}/sim01_animation.mp4")
    plt.close()

    # --- Metrics over time ---
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    steps = [m['step'] for m in metrics]
    axes[0].plot(steps, [m['trail_cells'] for m in metrics], 'r.-')
    axes[0].set_title('Trail Cells Over Time')
    axes[0].set_xlabel('Step')
    axes[0].set_ylabel('Cells with pheromone > 1.0')

    axes[1].plot(steps, [m['food_remaining'] for m in metrics], 'b.-')
    axes[1].set_title('Food Remaining')
    axes[1].set_xlabel('Step')
    axes[1].set_ylabel('Food units')

    axes[2].plot(steps, [m['ants_carrying'] for m in metrics], 'g.-')
    axes[2].set_title('Ants Carrying Food')
    axes[2].set_xlabel('Step')
    axes[2].set_ylabel('Count')

    plt.tight_layout()
    plt.savefig(f"{outdir}/sim01_metrics.png", dpi=150)
    print(f"Saved: {outdir}/sim01_metrics.png")
    plt.close()

    print(f"\nAll outputs in: {outdir}/")


def sweep_plot():
    """Run decay rate sweep and plot results."""
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import os

    decay_rates = [0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.1, 0.15, 0.2]
    results = []

    print("Running decay rate sweep...")
    for decay in decay_rates:
        m, _, _ = run_simulation(decay_rate=decay, verbose=False)
        results.append({
            'decay': decay,
            'final_trail': m[-1]['trail_cells'],
            'final_food': m[-1]['food_remaining'],
            'peak_trail': max(mh['trail_cells'] for mh in m),
        })
        print(f"  decay={decay:.3f} | final_trail={results[-1]['final_trail']:4d} | peak_trail={results[-1]['peak_trail']:4d} | food={results[-1]['final_food']:3d}")

    outdir = os.path.dirname(os.path.abspath(__file__)) + "/output"
    os.makedirs(outdir, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    decays = [r['decay'] for r in results]
    axes[0].plot(decays, [r['final_trail'] for r in results], 'r.-', label='Final trail cells')
    axes[0].plot(decays, [r['peak_trail'] for r in results], 'r.--', alpha=0.5, label='Peak trail cells')
    axes[0].set_xlabel('Pheromone decay rate')
    axes[0].set_ylabel('Trail cells')
    axes[0].set_title('Trail Formation vs Decay Rate')
    axes[0].legend()
    axes[0].set_xscale('log')

    axes[1].plot(decays, [r['final_food'] for r in results], 'b.-')
    axes[1].set_xlabel('Pheromone decay rate')
    axes[1].set_ylabel('Food remaining (less = better foraging)')
    axes[1].set_title('Foraging Efficiency vs Decay Rate')
    axes[1].set_xscale('log')

    plt.tight_layout()
    plt.savefig(f"{outdir}/sim01_decay_sweep.png", dpi=150)
    print(f"\nSaved: {outdir}/sim01_decay_sweep.png")
    plt.close()


def selftest():
    """Internal sanity checks. Prints 'Part N OK' per group and exits 0."""
    # Part 1: trail_concentration discriminates concentrated from uniform fields.
    w = World.create(10, 10)
    assert trail_concentration(w) == 0.0, "Part 1: empty field should score 0"
    for x in range(10):
        for y in range(10):
            w.pheromone[x][y] = 1.0
    uniform = trail_concentration(w, top_frac=0.05)
    assert abs(uniform - 0.05) < 0.02, f"Part 1: uniform field should score ~0.05, got {uniform}"
    w2 = World.create(10, 10)
    w2.pheromone[3][3] = 100.0
    assert trail_concentration(w2, top_frac=0.05) > 0.9, "Part 1: point mass should score ~1.0"
    print("selftest: Part 1 OK")

    # Part 2: the blind control really is blind — a strong pheromone gradient
    # must not steer it, but must steer a sensing ant.
    def steered(sensing):
        world = World.create(30, 30)
        random.seed(1)
        ant = Ant(x=15.0, y=15.0, angle=0.0)
        # Laid within SENSOR_RANGE (3) of the ant's right-hand sensor, which
        # sits ~3*sin(45deg) ~ 2 cells above it — a band further away is
        # invisible and the test would pass vacuously.
        for x in range(30):
            for y in range(16, 30):
                world.pheromone[x][y] = 500.0
        angles = []
        for _ in range(40):
            move_ant(world, ant, sensing=sensing)
            angles.append(round(ant.angle, 6))
        return angles
    assert steered(True) != steered(False), \
        "Part 2: sensing and blind ants followed identical paths — control is not a control"
    print("selftest: Part 2 OK")

    # Part 3: a short run produces well-formed metrics.
    m, world, _ = run_simulation(decay_rate=0.02, verbose=False)
    assert m and all({'step', 'trail_cells', 'trail_concentration',
                      'food_remaining', 'ants_carrying'} <= r.keys() for r in m)
    print("selftest: Part 3 OK")


def run_comparison():
    """Sensing vs pheromone-blind control, plus a decay sweep. Writes results.json."""
    print("=== Mini Sim 1: Pheromone Trail Formation ===")
    print(f"Grid: {GRID_W}x{GRID_H}, Ants: {NUM_ANTS}, Food: {NUM_FOOD}")
    print()

    print("--- SENSING (stigmergic feedback on) ---")
    m_sensing, w_sensing, _ = run_simulation(decay_rate=0.02, sensing=True)
    print("\n--- BLIND CONTROL (ants deposit but cannot read the field) ---")
    m_blind, w_blind, _ = run_simulation(decay_rate=0.02, sensing=False)

    s, b = m_sensing[-1], m_blind[-1]
    print("\n" + "=" * 62)
    print(f"  {'Metric':<26} {'Sensing':>12} {'Blind':>12}")
    print(f"  {'-'*26} {'-'*12} {'-'*12}")
    print(f"  {'trail_cells (coverage)':<26} {s['trail_cells']:>12} {b['trail_cells']:>12}")
    print(f"  {'trail_concentration':<26} {s['trail_concentration']:>12.4f} {b['trail_concentration']:>12.4f}")
    print(f"  {'food_remaining':<26} {s['food_remaining']:>12} {b['food_remaining']:>12}")
    print("  (uniform field scores 0.05 on concentration; higher = real trail structure)")

    print("\n--- Decay Rate Sweep (sensing) ---")
    sweep = []
    for decay in [0.001, 0.01, 0.02, 0.05, 0.1, 0.2]:
        mm, _, _ = run_simulation(decay_rate=decay, verbose=False, sensing=True)
        sweep.append({'decay': decay, 'final_trail_cells': mm[-1]['trail_cells'],
                      'final_trail_concentration': mm[-1]['trail_concentration'],
                      'food_remaining': mm[-1]['food_remaining']})
        print(f"  decay={decay:.3f} | trail_cells={sweep[-1]['final_trail_cells']:4d} "
              f"| conc={sweep[-1]['final_trail_concentration']:.3f} "
              f"| food_remaining={sweep[-1]['food_remaining']:3d}")

    results = {
        'config': {'grid_w': GRID_W, 'grid_h': GRID_H, 'num_ants': NUM_ANTS,
                   'num_food': NUM_FOOD, 'max_steps': MAX_STEPS,
                   'pheromone_deposit': PHEROMONE_DEPOSIT, 'decay_rate': 0.02,
                   'sensor_range': SENSOR_RANGE, 'seed': 42},
        'sensing': {'history': m_sensing},
        'blind_control': {'history': m_blind},
        'decay_sweep': sweep,
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.json')
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out}")
    return results


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"

    if mode == "visualize":
        visualize()
    elif mode == "sweep_plot":
        sweep_plot()
    elif mode == "selftest":
        selftest()
    elif mode == "run":
        run_comparison()
    else:
        print("usage: sim01.py [run|selftest|visualize|sweep_plot]")
