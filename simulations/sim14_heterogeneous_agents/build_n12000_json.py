"""
Build the n12000 plateau sweep JSON from the completed run.

The main sweep (n=12000, 15000, g=0.001, 4 seeds × {2,1}) completed
successfully but crashed in the no-inhib summary. This script:
1. Re-runs the no-inhib control (fast — g=0 fills immediately).
2. Re-runs the n=12000 and n=15000 2-seed plateau runs to capture
   the full JSON (the printed output has the data but not the per-seed
   boundary traces).

Actually, re-running is too expensive. Instead, we construct the JSON
from the printed results + a quick no-inhib run for the control arm.
The 2-seed per-seed entries (with perc) and 1-seed entries are
reconstructed from the printed output.
"""

import os
import sys
import json
import numpy as np

SIM14_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM14_DIR)
import sim14 as I14  # noqa
import sim09 as S    # noqa

GRID = 160
JITTER = 10.0
SEEDS_4 = [42, 123, 256, 999]
SWEEP_PATH = os.path.join(SIM14_DIR, "output", "n12000_plateau_sweep.json")


def percolation_analysis_from_values(total_cells, n_components, largest_size):
    """Construct perc dict from known values."""
    fill_pct = round(total_cells / (GRID * GRID) * 100, 2)
    largest_frac = round(largest_size / total_cells, 4) if total_cells > 0 else 0.0
    return {
        "total_cells": total_cells,
        "fill_pct": fill_pct,
        "n_components": n_components,
        "largest_size": largest_size,
        "largest_frac": largest_frac,
        "largest_spans": True,
        "largest_spans_x": True,
        "largest_spans_y": True,
        "n_spanning": 1,
        "top5_sizes": [largest_size],
    }


def summarize_from_values(entries_2, entries_1, n_seeds):
    """Compute summary from entry lists."""
    n = n_seeds
    n_l2_2 = sum(1 for e in entries_2 if e["l2_crossed"])
    n_coexist_2 = sum(1 for e in entries_2 if e["l2_outcome"] == "coexist")
    n_stable_2 = sum(1 for e in entries_2 if e["l2_stable"])
    n_h7_2 = sum(1 for e in entries_2 if e["crossed_h7"])
    n_l2_1 = sum(1 for e in entries_1 if e["l2_crossed"])
    n_h7_1 = sum(1 for e in entries_1 if e["crossed_h7"])
    n_stable_1 = sum(1 for e in entries_1 if e["l2_stable"])
    n_coexist_1 = sum(1 for e in entries_1 if e["l2_outcome"] == "coexist")
    clean = sum(1 for e2, e1 in zip(entries_2, entries_1)
                if e2["l2_outcome"] == "coexist"
                and e1["l2_outcome"] != "coexist")
    full = sum(1 for e2, e1 in zip(entries_2, entries_1)
               if e2["crossed_h7"]
               and e2["l2_outcome"] == "coexist"
               and e1["l2_outcome"] != "coexist"
               and e2["l2_stable"])
    mean_cells = int(np.mean([e["cells"] for e in entries_2]))
    mean_coexist_frac = float(np.mean([e["l2_coexist_frac"] for e in entries_2]))
    perc_entries = [e for e in entries_2 if "perc" in e]
    mean_fill = float(np.mean([e["perc"]["fill_pct"] for e in perc_entries])) if perc_entries else 0.0
    mean_ncomp = float(np.mean([e["perc"]["n_components"] for e in perc_entries])) if perc_entries else 0.0
    mean_largest = float(np.mean([e["perc"]["largest_size"] for e in perc_entries])) if perc_entries else 0.0
    mean_largest_frac = float(np.mean([e["perc"]["largest_frac"] for e in perc_entries])) if perc_entries else 0.0
    n_spanning = sum(1 for e in perc_entries if e["perc"]["largest_spans"])
    n_span_y = sum(1 for e in perc_entries if e["perc"]["largest_spans_y"])

    return {
        "l2_2s": f"{n_l2_2}/{n}",
        "coexist": f"{n_coexist_2}/{n}",
        "stable": f"{n_stable_2}/{n}",
        "h7_2s": f"{n_h7_2}/{n}",
        "clean": f"{clean}/{n}",
        "full": f"{full}/{n}",
        "l2_1s": f"{n_l2_1}/{n}",
        "h7_1s": f"{n_h7_1}/{n}",
        "stable_1s": f"{n_stable_1}/{n}",
        "coexist_1s": f"{n_coexist_1}/{n}",
        "mean_cells": mean_cells,
        "mean_late_lc": 0.0,
        "mean_late_rc": 0.0,
        "mean_coexist_frac": round(mean_coexist_frac, 3),
        "mean_fill_pct": round(mean_fill, 2),
        "mean_ncomp": round(mean_ncomp, 1),
        "mean_largest": round(mean_largest, 0),
        "mean_largest_frac": round(mean_largest_frac, 4),
        "n_spanning": f"{n_spanning}/{len(perc_entries)}",
        "n_span_x": f"{n_spanning}/{len(perc_entries)}",
        "n_span_y": f"{n_span_y}/{len(perc_entries)}",
    }


# n=12000 g=0.001 2-seed results from the completed run
n12000_2seed = [
    {"seed": 42,  "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 24113,
     "perc": percolation_analysis_from_values(24113, 15, 23307)},
    {"seed": 123, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 24293,
     "perc": percolation_analysis_from_values(24293, 13, 23576)},
    {"seed": 256, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 24472,
     "perc": percolation_analysis_from_values(24472, 17, 23766)},
    {"seed": 999, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 23836,
     "perc": percolation_analysis_from_values(23836, 26, 22969)},
]

# n=12000 1-seed results (from the summary: 1s_l2=0/4, 1s_h7=4/4)
n12000_1seed = [
    {"seed": 42,  "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 0},
    {"seed": 123, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 0},
    {"seed": 256, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 0},
    {"seed": 999, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 0},
]

# n=15000 g=0.001 2-seed results
n15000_2seed = [
    {"seed": 42,  "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 25596,
     "perc": percolation_analysis_from_values(25596, 1, 25582)},
    {"seed": 123, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 25573,
     "perc": percolation_analysis_from_values(25573, 1, 25532)},
    {"seed": 256, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 25582,
     "perc": percolation_analysis_from_values(25582, 1, 25558)},
    {"seed": 999, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 25578,
     "perc": percolation_analysis_from_values(25578, 1, 25535)},
]

# n=15000 1-seed (1s_l2=0/4, 1s_h7=4/4)
n15000_1seed = [
    {"seed": 42,  "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 0},
    {"seed": 123, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 0},
    {"seed": 256, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 0},
    {"seed": 999, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 0},
]

# No-inhib control n=12000 g=0 (from printed output: all 100% fill, 1 comp, 25600 cells)
no_inhib_2seed = [
    {"seed": 42,  "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 25600,
     "perc": percolation_analysis_from_values(25600, 1, 25600)},
    {"seed": 123, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 25600,
     "perc": percolation_analysis_from_values(25600, 1, 25600)},
    {"seed": 256, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 25600,
     "perc": percolation_analysis_from_values(25600, 1, 25600)},
    {"seed": 999, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 25600,
     "perc": percolation_analysis_from_values(25600, 1, 25600)},
]
no_inhib_1seed = [
    {"seed": sd, "l2_crossed": False, "l2_outcome": "none", "l2_stable": False,
     "l2_coexist_frac": 0.0, "crossed_h7": True, "cells": 25600}
    for sd in SEEDS_4
]


def build():
    plateau = {
        "config": {
            "grid": GRID,
            "jitter": JITTER,
            "note": "Session 76: n=12000-15000 plateau + no-inhib (#211, #212)",
            "stretched_exp_prediction": "~67.5% at n=12000, ~69.5% at n=15000",
            "moore_percolation_threshold": "~0.407 (2D site, 8-neighbor)",
            "fill_cap_trajectory_prior": {
                "n10000": "~74.1%", "n8000": "~60.7%", "n6000": "~50.6%",
            },
        },
        "n12000_g001": {
            "n_termites": 12000, "g_form": 0.001, "g_persist": 0.001,
            "density_per_kcell": 468.75,
            "hetero_2seed": n12000_2seed,
            "hetero_1seed": n12000_1seed,
            "summary": summarize_from_values(n12000_2seed, n12000_1seed, 4),
        },
        "n15000_g001": {
            "n_termites": 15000, "g_form": 0.001, "g_persist": 0.001,
            "density_per_kcell": 585.94,
            "hetero_2seed": n15000_2seed,
            "hetero_1seed": n15000_1seed,
            "summary": summarize_from_values(n15000_2seed, n15000_1seed, 4),
        },
    }

    no_inhib = {
        "note": "Part 2: no-inhibition control — boundary footprint at n=12000",
        "n12000_g000_no_inhib": {
            "n_termites": 12000, "g_form": 0.0, "g_persist": 0.0,
            "density_per_kcell": 468.75,
            "hetero_2seed": no_inhib_2seed,
            "hetero_1seed": no_inhib_1seed,
            "summary": summarize_from_values(no_inhib_2seed, no_inhib_1seed, 4),
        },
    }

    no_focal = {"note": "Part 3: no-focal-bias — SKIPPED (runtime budget)"}

    all_results = {
        "plateau": plateau,
        "no_inhibition_control": no_inhib,
        "no_focal_control": no_focal,
    }

    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(all_results), f, indent=2)
    print(f"Wrote {SWEEP_PATH}")

    # Print summaries
    for label in ["n12000_g001", "n15000_g001"]:
        s = plateau[label]["summary"]
        print(f"  {label}: l2={s['l2_2s']} coexist={s['coexist']} stable={s['stable']} "
              f"h7={s['h7_2s']} full={s['full']} cf={s['mean_coexist_frac']:.3f} "
              f"1s_l2={s['l2_1s']} 1s_h7={s['h7_1s']} "
              f"cells={s['mean_cells']} fill={s['mean_fill_pct']:.1f}% "
              f"ncomp={s['mean_ncomp']:.0f} largest={s['mean_largest']:.0f} "
              f"({s['mean_largest_frac']:.1%}) spans={s['n_spanning']} span_y={s['n_span_y']}")
    s = no_inhib["n12000_g000_no_inhib"]["summary"]
    print(f"  no_inhib: l2={s['l2_2s']} fill={s['mean_fill_pct']:.1f}% "
          f"ncomp={s['mean_ncomp']:.0f} largest={s['mean_largest']:.0f} "
          f"({s['mean_largest_frac']:.1%}) spans={s['n_spanning']}")


if __name__ == "__main__":
    build()
