"""sim06 — Termite mound: testing the H7 Trace->Actor Crossing Hypothesis.

Termites deposit soil pellets laced with a cement pheromone (Grasse stigmergy).
Deposits attract further deposits (positive feedback); pheromone decays (negative
feedback), producing pillars/archs no single agent plans. sim06 asks whether the
accumulated stigmergic trace field can *cross* from a passive coordination signal
to a self-maintaining actor — a structure with dynamics not reducible to its
parts, that constrains its builders, and that repairs itself after perturbation.

Two conditions are contrasted:
  - baseline:         termites build with decaying pheromone, no maintenance loop.
  - self_maintenance: the accumulated structure recruits termites to maintain it.

A crossing detector (Part 5) flags the timestep at which the trace field becomes
an actor; perturbation experiments (Part 8) provide the acid test for H7.
"""

import os
import sys
import json
import math
import time

import numpy as np

# ---------------------------------------------------------------------------
# Paths (built from the script's own location — never hardcode /home/vance/...)
# ---------------------------------------------------------------------------
SIM_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SIM_DIR, "results.json")
OUTPUT_DIR = os.path.join(SIM_DIR, "output")

# ---------------------------------------------------------------------------
# Simulation constants (module-level defaults; later Parts reference these)
# ---------------------------------------------------------------------------
GRID_SIZE = 100
N_TERMITES = 200
STEPS = 4000
SAMPLE_EVERY = 25
SEED = 42

# Field / stigmergy parameters
PHEROMONE_DECAY = 0.02          # per-step multiplicative decay of cement pheromone
PHEROMONE_DIFFUSE = 0.10         # fraction of pheromone that diffuses to neighbours/step
MATERIAL_DECAY = 0.0005          # slow erosion of deposited material (baseline erosion)
STRUCTURE_THRESHOLD = 1.0       # material level above which a cell counts as "structure"
DEPOSIT_PHEROMONE = 1.0          # cement pheromone added per deposit
PICKUP_PROB_BASE = 0.01          # base prob a loaded... (agent rules live in Part 2)


# ---------------------------------------------------------------------------
# Numpy -> JSON helper
# ---------------------------------------------------------------------------
def _pyify(x):
    """Recursively convert numpy scalars/arrays to JSON-native types."""
    if isinstance(x, dict):
        return {k: _pyify(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_pyify(v) for v in x]
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    return x


# ---------------------------------------------------------------------------
# RNG helper
# ---------------------------------------------------------------------------
def make_rng(seed=SEED):
    """Return a numpy random Generator seeded with *seed*."""
    return np.random.default_rng(seed)


# ---------------------------------------------------------------------------
# Field container (extended in Part 3)
# ---------------------------------------------------------------------------
class Field:
    """Holds the 2D grids the stigmergic environment is made of."""

    def __init__(self, size):
        self.size = size
        self.material = np.zeros((size, size), dtype=np.float64)    # deposited soil
        self.pheromone = np.zeros((size, size), dtype=np.float64)    # cement pheromone


# ---------------------------------------------------------------------------
# CLI commands (stubs — populated by later Parts)
# ---------------------------------------------------------------------------
def cmd_run():
    print("cmd_run not implemented yet (Part 6)")


def cmd_sweep_plot():
    print("cmd_sweep_plot not implemented yet (Part 7)")


def cmd_selftest():
    # Part 1 checks
    assert GRID_SIZE > 0 and N_TERMITES > 0 and STEPS > 0
    f = Field(GRID_SIZE)
    assert f.material.shape == (GRID_SIZE, GRID_SIZE)
    assert _pyify({"a": np.float64(1.5)}) == {"a": 1.5}
    print("selftest: Part 1 OK")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        cmd_run()
    elif cmd == "sweep_plot":
        cmd_sweep_plot()
    elif cmd == "selftest":
        cmd_selftest()
    else:
        print("usage: sim06.py [run|sweep_plot|selftest]")


if __name__ == "__main__":
    main()
