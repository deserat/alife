"""
Sim02: Dynamic Fitness Landscape
================================

Tests whether agents that modify their fitness landscape (stigmergic niche 
construction) produce qualitatively different dynamics from agents on a 
static landscape.

This simulation directly tests H4 (Dynamic Environment) and H8 (Computational
Complexity Enables Open-Endedness), and is a building block for testing H7
(Trace→Actor Crossing).

DESIGN:
-------
- A population of agents lives on an NK-like fitness landscape (grid of cells).
- Each agent has a "strategy" (binary string of length N).
- Fitness of a strategy depends on the cell it's on AND the landscape state.
- Two conditions:
  1. STATIC: The landscape is fixed. Agents adapt TO it.
  2. DYNAMIC: Agents modify the landscape as they act. Their actions leave
     stigmergic traces that change the fitness contribution of cells.
     This is niche construction — agents reshape the selection landscape.

MEASUREMENTS:
- Population diversity (number of distinct strategies)
- Mean fitness over time
- Landscape modification rate (how much the landscape changes)
- Multi-scale structure: do stigmergic traces form clusters? Do clusters
  persist? Do they develop their own dynamics?

WHAT IT TEACHES:
- Whether dynamic landscapes produce qualitatively different dynamics
- Whether stigmergic landscape modification enables sustained diversity
- Whether traces accumulate and form structures (building block for H7)
- The relationship between computational complexity and open-endedness

KEY FINDINGS:
- (To be filled after running)
"""

import random
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
import json
import os

# ============================================================================
# Configuration
# ============================================================================

GRID_SIZE = 20          # 20x20 grid of cells
N_GENES = 8             # Strategy string length
POP_SIZE = 200          # Population size
MUTATION_RATE = 0.02    # Per-gene mutation probability
N_GENERATIONS = 5000    # Simulation length
TRACE_DECAY = 0.005     # Stigmergic trace decay rate (for dynamic condition)
TRACE_DEPOSIT = 0.1     # How much trace an agent deposits per action
SEED = 42

# ============================================================================
# Agent
# ============================================================================

@dataclass
class Agent:
    strategy: np.ndarray  # Binary array of length N_GENES
    x: int
    y: int
    fitness: float = 0.0
    age: int = 0

    def copy(self) -> 'Agent':
        return Agent(strategy=self.strategy.copy(), x=self.x, y=self.y, fitness=0.0, age=0)

    def mutate(self, rate: float) -> 'Agent':
        new_strat = self.strategy.copy()
        for i in range(len(new_strat)):
            if random.random() < rate:
                new_strat[i] = 1 - new_strat[i]
        return Agent(strategy=new_strat, x=self.x, y=self.y, fitness=0.0, age=0)

# ============================================================================
# Landscape
# ============================================================================

class FitnessLandscape:
    """
    A fitness landscape on a 2D grid. Each cell has an NK-like fitness function
    defined by epistatic interactions. In DYNAMIC mode, agent traces modify
    the fitness contributions.
    """
    def __init__(self, grid_size: int, n_genes: int, k: int, dynamic: bool, seed: int = 42):
        self.grid_size = grid_size
        self.n_genes = n_genes
        self.k = k  # Number of epistatic interactions per gene
        self.dynamic = dynamic
        self.rng = random.Random(seed)

        # Epistatic connections: which other genes each gene interacts with
        self.epistasis = []
        for i in range(n_genes):
            others = [j for j in range(n_genes) if j != i]
            self.rng.shuffle(others)
            self.epistasis.append(others[:k])

        # Base fitness contributions: for each cell, for each gene,
        # a lookup table from (gene_state, epistasis_states) -> contribution
        # Shape: (grid_size, grid_size, n_genes, 2^(k+1))
        contrib_size = 2 ** (k + 1)
        self.base_contributions = np.random.RandomState(seed).uniform(
            0, 1, size=(grid_size, grid_size, n_genes, contrib_size)
        ).astype(np.float64)

        # Stigmergic trace field (for dynamic mode)
        # Traces modify fitness contributions. Shape: (grid_size, grid_size, n_genes)
        self.trace_field = np.zeros((grid_size, grid_size, n_genes), dtype=np.float64)

        # Track landscape modification over time
        self.modification_history = []

    def get_fitness(self, strategy: np.ndarray, x: int, y: int) -> float:
        """Compute fitness of a strategy at a grid position."""
        total = 0.0
        for i in range(self.n_genes):
            # Build index into contribution table from gene i and its epistatic partners
            idx_bits = [strategy[i]]
            for j in self.epistasis[i]:
                idx_bits.append(strategy[j])
            idx = 0
            for b in idx_bits:
                idx = (idx << 1) | int(b)

            contribution = self.base_contributions[x, y, i, idx]

            # Dynamic mode: traces modify the fitness contribution
            if self.dynamic:
                # Trace adds a bias proportional to accumulated trace at this gene/cell
                contribution += self.trace_field[x, y, i]

            total += contribution

        # Normalize by n_genes to keep fitness in [0, 1+trace_bonus]
        return total / self.n_genes

    def deposit_traces(self, agents: List[Agent]):
        """Agents deposit stigmergic traces based on their strategy."""
        if not self.dynamic:
            return

        for agent in agents:
            for i in range(self.n_genes):
                if agent.strategy[i] == 1:  # Active genes deposit traces
                    self.trace_field[agent.x, agent.y, i] += TRACE_DEPOSIT

    def decay_traces(self):
        """Stigmergic traces decay over time."""
        if not self.dynamic:
            return
        self.trace_field *= (1.0 - TRACE_DECAY)

    def total_modification(self) -> float:
        """How much has the landscape been modified from the base?"""
        return float(np.sum(np.abs(self.trace_field)))

    def trace_clustering(self) -> Dict:
        """
        Measure whether traces form spatial clusters.
        Returns clustering statistics.
        """
        if not self.dynamic:
            return {"n_clusters": 0, "mean_cluster_size": 0, "max_cluster_size": 0}

        # Threshold traces to find active cells
        trace_magnitude = np.sum(np.abs(self.trace_field), axis=2)  # (grid, grid)
        active = trace_magnitude > 0.5  # Cells with significant traces

        if not np.any(active):
            return {"n_clusters": 0, "mean_cluster_size": 0, "max_cluster_size": 0}

        # Simple connected-component labeling (flood fill)
        visited = np.zeros_like(active, dtype=bool)
        clusters = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if active[i, j] and not visited[i, j]:
                    # Flood fill
                    size = 0
                    stack = [(i, j)]
                    while stack:
                        ci, cj = stack.pop()
                        if ci < 0 or ci >= self.grid_size or cj < 0 or cj >= self.grid_size:
                            continue
                        if visited[ci, cj] or not active[ci, cj]:
                            continue
                        visited[ci, cj] = True
                        size += 1
                        stack.extend([(ci+1, cj), (ci-1, cj), (ci, cj+1), (ci, cj-1)])
                    clusters.append(size)

        return {
            "n_clusters": len(clusters),
            "mean_cluster_size": np.mean(clusters) if clusters else 0,
            "max_cluster_size": max(clusters) if clusters else 0,
        }

    def trace_persistence(self) -> float:
        """How persistent are traces? High = stable structures, low = transient."""
        if not self.dynamic:
            return 0.0
        # Measure as ratio of trace magnitude to what would be if uniformly distributed
        total = np.sum(np.abs(self.trace_field))
        if total == 0:
            return 0.0
        # Entropy-based measure: lower entropy = more clustered = more persistent
        flat = np.abs(self.trace_field).flatten()
        flat = flat[flat > 0]
        if len(flat) < 2:
            return 0.0
        # Normalize
        flat = flat / flat.sum()
        entropy = -np.sum(flat * np.log(flat + 1e-10))
        max_entropy = np.log(len(flat))
        # Persistence = 1 - normalized_entropy (high when clustered)
        return 1.0 - (entropy / max_entropy if max_entropy > 0 else 0)


# ============================================================================
# Simulation
# ============================================================================

class Simulation:
    def __init__(self, dynamic: bool, k: int = 3, seed: int = SEED):
        random.seed(seed)
        np.random.seed(seed)
        self.dynamic = dynamic
        self.k = k
        self.landscape = FitnessLandscape(GRID_SIZE, N_GENES, k, dynamic, seed)
        self.agents: List[Agent] = []
        self.history: List[Dict] = []
        self._init_population()

    def _init_population(self):
        for _ in range(POP_SIZE):
            strategy = np.random.randint(0, 2, size=N_GENES)
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            self.agents.append(Agent(strategy=strategy, x=x, y=y))

    def step(self, generation: int):
        # 1. Evaluate fitness
        for agent in self.agents:
            agent.fitness = self.landscape.get_fitness(agent.strategy, agent.x, agent.y)
            agent.age += 1

        # 2. Selection — keep agents above median fitness
        fitnesses = [a.fitness for a in self.agents]
        median_fit = np.median(fitnesses) if fitnesses else 0

        # 3. Deposit stigmergic traces (dynamic mode only)
        self.landscape.deposit_traces(self.agents)

        # 4. Decay traces
        self.landscape.decay_traces()

        # 5. Reproduction — agents above median reproduce with mutation
        survivors = [a for a in self.agents if a.fitness >= median_fit]
        new_agents = []
        for agent in survivors:
            child = agent.mutate(MUTATION_RATE)
            # Child might move to a neighboring cell
            child.x = (agent.x + random.choice([-1, 0, 0, 1])) % GRID_SIZE
            child.y = (agent.y + random.choice([-1, 0, 0, 1])) % GRID_SIZE
            new_agents.append(child)

        # 6. Death — remove some random agents to maintain population
        all_agents = survivors + new_agents
        if len(all_agents) > POP_SIZE:
            # Keep the fittest
            all_agents.sort(key=lambda a: a.fitness, reverse=True)
            all_agents = all_agents[:POP_SIZE]
        elif len(all_agents) < POP_SIZE:
            # Add random agents
            while len(all_agents) < POP_SIZE:
                strategy = np.random.randint(0, 2, size=N_GENES)
                x = random.randint(0, GRID_SIZE - 1)
                y = random.randint(0, GRID_SIZE - 1)
                all_agents.append(Agent(strategy=strategy, x=x, y=y))

        self.agents = all_agents

        # 7. Record metrics
        strategies = [tuple(a.strategy) for a in self.agents]
        unique_strategies = len(set(strategies))
        mean_fitness = np.mean(fitnesses) if fitnesses else 0
        max_fitness = max(fitnesses) if fitnesses else 0
        modification = self.landscape.total_modification()
        clustering = self.landscape.trace_clustering()
        persistence = self.landscape.trace_persistence()

        self.history.append({
            "generation": generation,
            "population": len(self.agents),
            "diversity": unique_strategies,
            "mean_fitness": float(mean_fitness),
            "max_fitness": float(max_fitness),
            "landscape_modification": float(modification),
            "n_trace_clusters": clustering["n_clusters"],
            "mean_cluster_size": float(clustering["mean_cluster_size"]),
            "max_cluster_size": clustering["max_cluster_size"],
            "trace_persistence": float(persistence),
        })

    def run(self):
        for gen in range(N_GENERATIONS):
            self.step(gen)
            if gen % 500 == 0:
                h = self.history[-1]
                print(f"  Gen {gen:5d}: pop={h['population']}, div={h['diversity']}, "
                      f"fit={h['mean_fitness']:.4f}, mod={h['landscape_modification']:.2f}, "
                      f"clusters={h['n_trace_clusters']}, persist={h['trace_persistence']:.4f}")

    def get_results(self) -> Dict:
        return {
            "condition": "dynamic" if self.dynamic else "static",
            "k": self.k,
            "history": self.history,
        }


# ============================================================================
# Main
# ============================================================================

def run_comparison():
    """Run both static and dynamic conditions and compare."""
    print("=" * 70)
    print("Sim02: Dynamic Fitness Landscape — Static vs. Dynamic Comparison")
    print("=" * 70)
    print(f"Grid: {GRID_SIZE}x{GRID_SIZE}, N={N_GENES}, K={3}, Pop={POP_SIZE}")
    print(f"Generations: {N_GENERATIONS}, Mutation: {MUTATION_RATE}")
    print(f"Trace decay: {TRACE_DECAY}, Trace deposit: {TRACE_DEPOSIT}")
    print()

    # Run static condition
    print("--- STATIC LANDSCAPE (agents cannot modify landscape) ---")
    sim_static = Simulation(dynamic=False, k=3, seed=SEED)
    sim_static.run()

    print()

    # Run dynamic condition
    print("--- DYNAMIC LANDSCAPE (agents modify landscape stigmergically) ---")
    sim_dynamic = Simulation(dynamic=True, k=3, seed=SEED)
    sim_dynamic.run()

    print()

    # Compare results
    print("=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)

    static_h = sim_static.history
    dynamic_h = sim_dynamic.history

    # Final state
    s_final = static_h[-1]
    d_final = dynamic_h[-1]

    print(f"\nFinal state (generation {N_GENERATIONS}):")
    print(f"  {'Metric':<25} {'Static':>12} {'Dynamic':>12}")
    print(f"  {'-'*25} {'-'*12} {'-'*12}")
    print(f"  {'Diversity':.<25} {s_final['diversity']:>12} {d_final['diversity']:>12}")
    print(f"  {'Mean fitness':.<25} {s_final['mean_fitness']:>12.4f} {d_final['mean_fitness']:>12.4f}")
    print(f"  {'Max fitness':.<25} {s_final['max_fitness']:>12.4f} {d_final['max_fitness']:>12.4f}")
    print(f"  {'Landscape mod':.<25} {s_final['landscape_modification']:>12.2f} {d_final['landscape_modification']:>12.2f}")
    print(f"  {'Trace clusters':.<25} {s_final['n_trace_clusters']:>12} {d_final['n_trace_clusters']:>12}")
    print(f"  {'Trace persistence':.<25} {s_final['trace_persistence']:>12.4f} {d_final['trace_persistence']:>12.4f}")

    # Time series comparison
    print(f"\nDiversity over time (every 1000 generations):")
    print(f"  {'Gen':>6} {'Static':>10} {'Dynamic':>10}")
    for i in range(0, N_GENERATIONS, 1000):
        s = static_h[i]
        d = dynamic_h[i]
        print(f"  {s['generation']:>6} {s['diversity']:>10} {d['diversity']:>10}")

    # Mean fitness over time
    print(f"\nMean fitness over time (every 1000 generations):")
    print(f"  {'Gen':>6} {'Static':>10} {'Dynamic':>10}")
    for i in range(0, N_GENERATIONS, 1000):
        s = static_h[i]
        d = dynamic_h[i]
        print(f"  {s['generation']:>6} {s['mean_fitness']:>10.4f} {d['mean_fitness']:>10.4f}")

    # Check for open-ended dynamics
    # Open-ended = diversity does not converge to 1, fitness does not plateau
    s_div_final_1000 = [h['diversity'] for h in static_h[-1000:]]
    d_div_final_1000 = [h['diversity'] for h in dynamic_h[-1000:]]
    s_div_range = max(s_div_final_1000) - min(s_div_final_1000)
    d_div_range = max(d_div_final_1000) - min(d_div_final_1000)

    print(f"\nDiversity dynamics in final 1000 generations:")
    print(f"  Static:  range = {s_div_range:.1f} ({'OPEN' if s_div_range > 5 else 'CONVERGED'})")
    print(f"  Dynamic: range = {d_div_range:.1f} ({'OPEN' if d_div_range > 5 else 'CONVERGED'})")

    s_fit_final_1000 = [h['mean_fitness'] for h in static_h[-1000:]]
    d_fit_final_1000 = [h['mean_fitness'] for h in dynamic_h[-1000:]]
    s_fit_trend = np.polyfit(range(len(s_fit_final_1000)), s_fit_final_1000, 1)[0]
    d_fit_trend = np.polyfit(range(len(d_fit_final_1000)), d_fit_final_1000, 1)[0]

    print(f"\nFitness trend in final 1000 generations:")
    print(f"  Static:  slope = {s_fit_trend:.6f} ({'GROWING' if abs(s_fit_trend) > 1e-5 else 'PLATEAUED'})")
    print(f"  Dynamic: slope = {d_fit_trend:.6f} ({'GROWING' if abs(d_fit_trend) > 1e-5 else 'PLATEAUED'})")

    # Save results
    results = {
        "config": {
            "grid_size": GRID_SIZE,
            "n_genes": N_GENES,
            "k": 3,
            "pop_size": POP_SIZE,
            "mutation_rate": MUTATION_RATE,
            "n_generations": N_GENERATIONS,
            "trace_decay": TRACE_DECAY,
            "trace_deposit": TRACE_DEPOSIT,
            "seed": SEED,
        },
        "static": sim_static.get_results(),
        "dynamic": sim_dynamic.get_results(),
    }

    output_path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")

    return results


if __name__ == "__main__":
    run_comparison()
