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

**Key results from decay rate sweep:**
- decay=0.001 (near-permanent): 2683 trail cells — pheromone saturates the grid
- decay=0.01: 1380 trail cells — trails form but spread
- decay=0.02: 917 trail cells — good trail formation, food still being collected
- decay=0.05: 1128 trail cells — trails less stable but still functional
- decay=0.1: 580 trail cells — trails barely form, food collection impaired (419 left)
- decay=0.2: 421 trail cells — no stable trails, poor coordination (428 left)

**Observations:**
- There IS an optimal decay rate window (~0.01-0.05) where trails form but don't saturate
- The "hump" at step 600 (1685 cells) then decline shows trail consolidation — many short trails die, a few strong ones persist
- Food collection rate correlates with trail stability (ants with food at step 1000 = 45 out of 50)
- At very low decay (0.001), pheromone saturates the grid — can't distinguish trail from noise. This is the "memory without adaptation" problem
- At high decay (0.2), no trails persist — the "adaptation without memory" problem

**Building blocks provided:**
- 2D grid with pheromone field (deposition, decay, sensing)
- Agent movement and sensing
- Decay rate as a sweepable parameter
- Trail measurement (cell count above threshold)

**Next steps:**
- Add multiple food types to test trail competition
- Add pheromone evaporation to test trace differentiation
- Extend to test the trace→actor crossing hypothesis (H7): do accumulated traces ever become self-maintaining?
