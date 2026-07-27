# Simulations

Mini simulations that build foundational algorithms for the artificial life simulator. Each solves one sub-problem at a time. These are building blocks — not tests of the full hypotheses, but code we'll need later.

## sim01_pheromone_trails.py — Stigmergic Coordination

**Status:** Complete, runs successfully

**What it tests:** Basic stigmergy — ants wander, find food, return to nest leaving pheromone trails. Tests whether trails form and how decay rate affects trail stability.

**What it teaches us:**
- Environmental trace deposition and decay
- Agent-trace interaction (sensing, following, reinforcing)
- The transient/persistent trade-off in stigmergic traces
- Decay rate sweep reveals an optimal zone — too fast (0.2) and trails can't form, too slow (0.001) and everything is covered in pheromone

**Control condition (added 2026-07-27).** Until now sim01 had no control, so it could
not show that any structure in the field was *caused by* stigmergic feedback rather than
by the ants' movement statistics. `run` now contrasts sensing ants against a
**pheromone-blind control** — ants that still deposit, with the field still decaying, but
that cannot read it:

| Metric | Sensing | Blind control |
|---|---:|---:|
| `trail_cells` (coverage) | 917 | **2582** |
| `trail_concentration` (structure) | **0.786** | 0.270 |
| food remaining (lower = better foraging) | 443 | **432** |

Two things follow, and both revise earlier readings of this simulation:

1. **`trail_cells` runs opposite to trail formation.** The blind control scores nearly
   three times higher on it. A laden ant deposits 100 units every step and decay is
   2%/step, so a visited cell stays above threshold ~230 steps — the count measures
   *coverage*, and blind ants that wander widely cover more ground. Trail structure needs
   `trail_concentration` (share of pheromone in the densest 5% of cells; a uniform field
   scores 0.05). By that measure sensing genuinely does form trails: 0.786 vs 0.270.
2. **Trail formation does not improve foraging here.** The blind control collected *more*
   food (68 units vs 57). Pheromone following concentrates the ants onto shared paths but
   does not, in this model, feed them better. Worth stating plainly since the ant-colony
   framing invites the opposite assumption.

**Key results from decay rate sweep (sensing condition):**

| decay | trail_cells | concentration | food remaining |
|---:|---:|---:|---:|
| 0.001 | 2683 | 0.404 | 437 |
| 0.01 | 1380 | 0.657 | 441 |
| 0.02 | 917 | 0.786 | 443 |
| 0.05 | 1128 | 0.523 | 440 |
| 0.1 | 580 | 0.764 | 419 |
| 0.2 | 421 | 0.847 | 428 |

**Observations:**
- At very low decay (0.001) pheromone saturates the grid — high coverage, low
  concentration (0.404). This is the "memory without adaptation" problem, and it is the
  one reading the old coverage metric got right.
- **The claim that high decay (0.2) means "no stable trails" was wrong.** Concentration is
  *highest* there (0.847); what falls is coverage. High decay produces few, sharply defined
  trails rather than none. The earlier interpretation followed from reading `trail_cells`
  as trail quality.
- Foraging varies little across the sweep (419–443 remaining of 500), so the decay rate
  has far less functional consequence in this model than the coverage numbers suggest.
- Concentration is not monotonic in decay (0.404 → 0.786 → 0.523 → 0.847), so there is no
  clean "optimal window" on this measure — the earlier ~0.01–0.05 window was an artifact
  of reading coverage.

**Building blocks provided:**
- 2D grid with pheromone field (deposition, decay, sensing)
- Agent movement and sensing
- Decay rate as a sweepable parameter
- Trail measurement (cell count above threshold)

**Next steps:**
- Add multiple food types to test trail competition
- Add pheromone evaporation to test trace differentiation
- Extend to test the trace→actor crossing hypothesis (H7): do accumulated traces ever become self-maintaining?
