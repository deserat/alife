# Simulations

Building block simulations for the artificial life simulator. Each simulation lives in its own folder with its own README and output directory.

## Structure

```
simulations/
  pyproject.toml          — shared dependencies (matplotlib, numpy)
  .gitignore               — ignores output/, *.mp4, *.png, __pycache__, venvs
  sim01_pheromone_trails/  — stigmergic coordination (pheromone trails)
  sim02_*/                 — (future)
  ...
```

## Running

All sims use `uv run`:

```bash
cd ~/brain/artificial-life/simulations
uv run python3 sim01_pheromone_trails/sim01.py run
uv run python3 sim01_pheromone_trails/sim01.py visualize
uv run python3 sim01_pheromone_trails/sim01.py sweep_plot
```

Outputs (PNG, MP4) go to each sim's `output/` folder, which is gitignored.
