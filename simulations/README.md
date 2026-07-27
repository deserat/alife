# Simulations

Building block simulations for the artificial life simulator. Each simulation lives in its own folder with its own README and output directory.

## Structure

```
simulations/
  pyproject.toml               — shared dependencies (matplotlib, numpy)
  .gitignore                   — ignores output/, *.mp4, *.png, __pycache__, venvs
  REVIEW.md                    — 2026-07-27 construct-validity audit of sims 01–06
  sim01_pheromone_trails/      — stigmergic coordination, vs. a pheromone-blind control
  sim02_dynamic_landscape/     — static vs. agent-modified fitness landscape
  sim03_chemical_organizations/— Chemical Organization Theory, fixed network
  sim04_evolving_networks/     — evolving reaction network, finite polymer space
  sim05_lambda_chemistry/      — AlChemy, unbounded lambda-expression space
  sim06_termite_mound/         — H7 trace→actor crossing (Grassé stigmergy)
  sim07_transport_coupling/    — H7 via structure-sourced transport field + `M_c` threshold
```

sim01–sim07 are all implemented. There is no sim08 yet — not even a DESIGN.md.

The canonical table of what each simulation found lives in `../CLAUDE.md` §2; it is not
duplicated here so the two cannot drift apart.

**Read `REVIEW.md` before citing any pre-2026-07-27 result.** A construct-validity audit
found that five of the six then-implemented simulations measured something other than what
they claimed. All were fixed and rerun; three headline results moved.

## Running

All sims use `uv run`:

```bash
cd ~/brain/artificial-life/simulations
uv run python3 sim01_pheromone_trails/sim01.py run
uv run python3 sim01_pheromone_trails/sim01.py visualize
uv run python3 sim01_pheromone_trails/sim01.py sweep_plot
```

Outputs (PNG, MP4) go to each sim's `output/` folder, which is gitignored.
