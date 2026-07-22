"""
Sim03: Chemical Organization Theory — Trace Competition and Nested Organizations
================================================================================

Tests whether reaction networks with multiple competing trace types can produce
nested organizations (multi-scale structure), and whether the organization
structure satisfies the 8th CAS property (closure + self-maintenance).

This simulation directly tests:
- H7 (Trace→Actor Crossing): Do traces form self-maintaining organizations?
- H6 (Multi-Scale Autopoiesis): Do organizations contain suborganizations?
- H1 (Composition): Does multi-scale structure emerge from reaction dynamics?
- COT formalism: Can we operationalize closure + self-maintenance in a sim?

DESIGN:
-------
- A reaction network with resources (agents, trace types, energy) and reactions
- Multiple trace types (3) that compete and cooperate
- Agents catalyze reactions (deposit traces, consume traces, replicate)
- We check for organizations: closed + self-maintaining subsets of resources
- We check for nested organizations: suborganizations within organizations
- Compare: single trace type (like sim02) vs. multiple competing trace types

MEASUREMENTS:
- Number of organizations found over time
- Size of largest organization
- Number of nested organizations (suborganizations within organizations)
- Diversity of resources maintained
- Organization persistence (how long an organization survives)
- Resilience: recovery from perturbation

WHAT IT TEACHES:
- Whether COT formalism can be operationalized for ALife
- Whether multiple trace types prevent monoculture convergence (sim02's failure)
- Whether organizations emerge from reaction network dynamics
- Whether nested organizations (multi-scale structure) form
- Whether the 8th CAS property (closure + self-maintenance) is achievable

KEY FINDINGS:
- (To be filled after running)
"""

import random
import numpy as np
from dataclasses import dataclass, field
from typing import List, Set, Dict, Tuple, FrozenSet, Optional
from collections import defaultdict
import json
import os

# ============================================================================
# Configuration
# ============================================================================

N_AGENTS = 100           # Number of agents
N_TRACE_TYPES = 3       # Number of competing trace types (1 = sim02-like, 3 = new)
GRID_SIZE = 15          # Spatial grid for agent positions
N_GENERATIONS = 3000    # Simulation length
MUTATION_RATE = 0.03    # Probability of adding/removing a reaction per agent per gen
TRACE_DECAY = 0.01      # Trace decay rate (slow enough for accumulation)
ENERGY_INFLOW = 2.0     # External energy input per generation
REACTION_RATE_SCALE = 0.05  # Base reaction rate scaling
AGENT_DEATH_RATE = 0.005  # Per-generation agent death probability
PERTURBATION_GEN = 2000 # Generation to apply perturbation
PERTURBATION_STRENGTH = 0.5  # Fraction of resources removed
SEED = 42

# ============================================================================
# Reaction Network
# ============================================================================

@dataclass
class Reaction:
    """A reaction: set of input resources -> set of output resources."""
    inputs: FrozenSet[str]   # Resources consumed
    outputs: FrozenSet[str]  # Resources produced
    catalyst: Optional[str]  # Agent type that catalyzes this reaction (not consumed)

    def __repr__(self):
        cat = f" | {self.catalyst}" if self.catalyst else ""
        return f"{' + '.join(sorted(self.inputs)) or '∅'} -> {' + '.join(sorted(self.outputs)) or '∅'}{cat}"


class ReactionNetwork:
    """
    A reaction network with resources and reactions.
    Resources include: agents (A1, A2, A3), traces (T1, T2, T3), energy (E).
    """
    def __init__(self, n_trace_types: int):
        self.n_trace_types = n_trace_types
        self.resources: Set[str] = set()
        self.reactions: List[Reaction] = []
        self.concentrations: Dict[str, float] = defaultdict(float)
        self._build_base_network()

    def _build_base_network(self):
        """Build the base reaction network."""
        # Resources
        self.resources.add("E")  # Energy (external input)
        for i in range(self.n_trace_types):
            self.resources.add(f"T{i}")  # Trace types
        for i in range(3):  # Agent types (up to 3)
            self.resources.add(f"A{i}")  # Agent types

        # Reactions:
        # 1. Energy inflow (external): ∅ -> E
        self.reactions.append(Reaction(
            inputs=frozenset(),
            outputs=frozenset(["E"]),
            catalyst=None
        ))

        # 2. Agents consume energy + deposit traces:
        # A_i + E -> A_i + T_i (agent i produces trace i)
        for i in range(min(self.n_trace_types, 3)):
            self.reactions.append(Reaction(
                inputs=frozenset([f"A{i}", "E"]),
                outputs=frozenset([f"A{i}", f"T{i}"]),
                catalyst=f"A{i}"
            ))

        # 3. Traces decay: T_i -> ∅
        for i in range(self.n_trace_types):
            self.reactions.append(Reaction(
                inputs=frozenset([f"T{i}"]),
                outputs=frozenset(),
                catalyst=None
            ))

        # 4. Agents consume traces for energy: A_i + T_j -> A_i + E (if i==j, more efficient)
        for i in range(min(self.n_trace_types, 3)):
            for j in range(self.n_trace_types):
                if i == j:
                    # Same-type: efficient conversion
                    self.reactions.append(Reaction(
                        inputs=frozenset([f"A{i}", f"T{j}"]),
                        outputs=frozenset([f"A{i}", "E"]),
                        catalyst=f"A{i}"
                    ))
                else:
                    # Cross-type: less efficient (competition)
                    self.reactions.append(Reaction(
                        inputs=frozenset([f"A{i}", f"T{j}"]),
                        outputs=frozenset([f"A{i}"]),  # Just consumes, no energy back
                        catalyst=f"A{i}"
                    ))

        # 5. Agents replicate using energy: A_i + E -> A_i + A_i
        for i in range(min(self.n_trace_types, 3)):
            self.reactions.append(Reaction(
                inputs=frozenset([f"A{i}", "E"]),
                outputs=frozenset([f"A{i}", f"A{i}"]),
                catalyst=None
            ))

        # 6. Agent death handled stochastically in step_dynamics (not as reaction)
        # Death rate depends on energy availability — starved agents die faster.

        # 7. Trace-trace interactions (cooperation/competition):
        if self.n_trace_types >= 2:
            # T0 + T1 -> T2 (combination creates new trace)
            self.reactions.append(Reaction(
                inputs=frozenset([f"T0", f"T1"]),
                outputs=frozenset([f"T2"]),
                catalyst=None
            ))
        if self.n_trace_types >= 3:
            # T2 + T0 -> T1 (cycle)
            self.reactions.append(Reaction(
                inputs=frozenset([f"T2", f"T0"]),
                outputs=frozenset([f"T1"]),
                catalyst=None
            ))

    def step_dynamics(self):
        """Execute one step of the reaction dynamics."""
        # Apply reactions with rates proportional to concentrations
        delta = defaultdict(float)

        for rxn in self.reactions:
            # Check if all inputs are available
            rate = 1.0
            for inp in rxn.inputs:
                if self.concentrations.get(inp, 0) <= 0:
                    rate = 0
                    break
                rate *= min(self.concentrations[inp], 1.0)  # Saturating kinetics

            # Catalyst boosts rate
            if rxn.catalyst and self.concentrations.get(rxn.catalyst, 0) > 0:
                rate *= min(self.concentrations[rxn.catalyst], 1.0)
            elif rxn.catalyst:
                rate = 0  # Need catalyst

            if rate <= 0:
                continue

            # Apply rates (scaled down for stability)
            rate *= REACTION_RATE_SCALE

            # Consume inputs
            for inp in rxn.inputs:
                delta[inp] -= rate

            # Produce outputs
            for out in rxn.outputs:
                delta[out] += rate

        # Apply changes
        for res, change in delta.items():
            self.concentrations[res] = max(0, self.concentrations[res] + change)

        # External energy inflow
        self.concentrations["E"] += ENERGY_INFLOW

        # Stochastic agent death (separate from reaction dynamics)
        for i in range(3):
            ai = f"A{i}"
            if ai in self.concentrations and self.concentrations[ai] > 0:
                # Death rate decreases with energy availability
                death_rate = AGENT_DEATH_RATE * max(0, 1 - self.concentrations.get("E", 0) / 20)
                self.concentrations[ai] *= (1.0 - death_rate)

        # Trace decay (in addition to decay reactions)
        for i in range(self.n_trace_types):
            ti = f"T{i}"
            if ti in self.concentrations:
                self.concentrations[ti] *= (1.0 - TRACE_DECAY)

        # Cap concentrations
        for res in self.concentrations:
            self.concentrations[res] = min(self.concentrations[res], 100.0)

    def check_organization(self, subset: Set[str]) -> bool:
        """
        Check if a subset of resources forms an organization
        (closure + self-maintenance).
        """
        # Closure: every reaction with all inputs in subset must have all outputs in subset
        for rxn in self.reactions:
            if rxn.inputs and all(inp in subset for inp in rxn.inputs):
                if not all(out in subset for out in rxn.outputs):
                    return False

        # Self-maintenance: every resource in subset that is consumed by some reaction
        # must also be produced by some reaction in the subset
        consumed = set()
        produced = set()
        for rxn in self.reactions:
            if rxn.inputs and all(inp in subset for inp in rxn.inputs):
                consumed |= rxn.inputs
                produced |= rxn.outputs
                # Catalyst is not consumed
                if rxn.catalyst:
                    consumed.discard(rxn.catalyst)

        for res in subset:
            if res in consumed and res not in produced:
                return False

        return True

    def find_organizations(self) -> List[Set[str]]:
        """Find all organizations (closed + self-maintaining subsets) in the network."""
        orgs = []
        resources = sorted(self.resources)
        # Check all non-empty subsets (feasible for small resource sets)
        from itertools import combinations
        for size in range(1, len(resources) + 1):
            for subset in combinations(resources, size):
                subset_set = set(subset)
                if self.check_organization(subset_set):
                    orgs.append(subset_set)
        return orgs

    def find_active_organizations(self) -> List[Set[str]]:
        """Find organizations where all resources have concentration > threshold."""
        all_orgs = self.find_organizations()
        active = []
        for org in all_orgs:
            if all(self.concentrations.get(r, 0) > 0.1 for r in org):
                active.append(org)
        return active

    def find_nested_organizations(self) -> List[Tuple[Set[str], Set[str]]]:
        """Find pairs where one organization is strictly contained in another."""
        orgs = self.find_active_organizations()
        nested = []
        for i, org1 in enumerate(orgs):
            for j, org2 in enumerate(orgs):
                if i != j and org1 < org2:  # Proper subset
                    nested.append((org1, org2))
        return nested


# ============================================================================
# Simulation
# ============================================================================

class Simulation:
    def __init__(self, n_trace_types: int, seed: int = SEED):
        random.seed(seed)
        np.random.seed(seed)
        self.n_trace_types = n_trace_types
        self.network = ReactionNetwork(n_trace_types)
        self.history: List[Dict] = []

        # Initialize concentrations
        self.network.concentrations["E"] = 10.0
        for i in range(n_trace_types):
            self.network.concentrations[f"A{i}"] = 5.0
            self.network.concentrations[f"T{i}"] = 1.0

    def step(self, generation: int):
        """One generation of dynamics."""
        # Run several reaction steps per generation
        for _ in range(10):
            self.network.step_dynamics()

        # Perturbation
        if generation == PERTURBATION_GEN:
            for res in list(self.network.concentrations.keys()):
                self.network.concentrations[res] *= (1 - PERTURBATION_STRENGTH)

        # Record metrics
        concentrations = dict(self.network.concentrations)
        active_resources = sum(1 for v in concentrations.values() if v > 0.1)

        # Find organizations (every 100 generations and at final generation)
        n_orgs = 0
        n_active_orgs = 0
        n_nested = 0
        max_org_size = 0
        org_details = []

        compute_orgs = (generation % 100 == 0) or (generation == N_GENERATIONS - 1)
        if compute_orgs:
            all_orgs = self.network.find_organizations()
            active_orgs = self.network.find_active_organizations()
            n_orgs = len(all_orgs)
            n_active_orgs = len(active_orgs)
            max_org_size = max((len(o) for o in active_orgs), default=0)
            nested = self.network.find_nested_organizations()
            n_nested = len(nested)
            for org in active_orgs:
                org_details.append(sorted(org))

        self.history.append({
            "generation": generation,
            "n_active_resources": active_resources,
            "concentrations": {k: round(v, 3) for k, v in concentrations.items()},
            "n_organizations": n_orgs,
            "n_active_organizations": n_active_orgs,
            "max_org_size": max_org_size,
            "n_nested_organizations": n_nested,
            "active_org_details": org_details,
        })

    def run(self):
        for gen in range(N_GENERATIONS):
            self.step(gen)
            if gen % 500 == 0:
                h = self.history[-1]
                print(f"  Gen {gen:5d}: active_res={h['n_active_resources']}, "
                      f"E={h['concentrations'].get('E', 0):.2f}, "
                      f"orgs={h['n_active_organizations']}, "
                      f"max_org={h['max_org_size']}, "
                      f"nested={h['n_nested_organizations']}")

    def get_results(self) -> Dict:
        return {
            "n_trace_types": self.n_trace_types,
            "history": self.history,
        }


# ============================================================================
# Main
# ============================================================================

def run_comparison():
    """Run comparison: single trace type vs. multiple trace types."""
    print("=" * 70)
    print("Sim03: Chemical Organization Theory — Trace Competition & Nested Orgs")
    print("=" * 70)
    print(f"Agents: {N_AGENTS}, Generations: {N_GENERATIONS}")
    print(f"Trace decay: {TRACE_DECAY}, Energy inflow: {ENERGY_INFLOW}")
    print(f"Perturbation at gen {PERTURBATION_GEN} (strength {PERTURBATION_STRENGTH})")
    print()

    # Condition 1: Single trace type (like sim02)
    print("--- SINGLE TRACE TYPE (baseline, sim02-like) ---")
    sim1 = Simulation(n_trace_types=1, seed=SEED)
    sim1.run()

    print()

    # Condition 2: Multiple competing trace types
    print("--- MULTIPLE TRACE TYPES (3 competing types) ---")
    sim2 = Simulation(n_trace_types=3, seed=SEED)
    sim2.run()

    print()

    # Comparison
    print("=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)

    h1 = sim1.history[-1]
    h2 = sim2.history[-1]

    print(f"\nFinal state (generation {N_GENERATIONS}):")
    print(f"  {'Metric':<30} {'Single':>12} {'Multi':>12}")
    print(f"  {'-'*30} {'-'*12} {'-'*12}")
    print(f"  {'Active resources':.<30} {h1['n_active_resources']:>12} {h2['n_active_resources']:>12}")
    print(f"  {'Active organizations':.<30} {h1['n_active_organizations']:>12} {h2['n_active_organizations']:>12}")
    print(f"  {'Max org size':.<30} {h1['max_org_size']:>12} {h2['max_org_size']:>12}")
    print(f"  {'Nested organizations':.<30} {h1['n_nested_organizations']:>12} {h2['n_nested_organizations']:>12}")

    # Organization details at final state
    print(f"\nActive organizations (final state):")
    print(f"  Single trace:")
    for org in h1.get("active_org_details", []):
        print(f"    {org}")
    if not h1.get("active_org_details"):
        print(f"    (none)")

    print(f"  Multi trace:")
    for org in h2.get("active_org_details", []):
        print(f"    {org}")
    if not h2.get("active_org_details"):
        print(f"    (none)")

    # Check for recovery from perturbation
    print(f"\nResilience (perturbation at gen {PERTURBATION_GEN}):")
    pre_pert = sim1.history[PERTURBATION_GEN - 1]
    post_pert = sim1.history[PERTURBATION_GEN]
    final = sim1.history[-1]

    for label, sim_hist in [("Single", sim1.history), ("Multi", sim2.history)]:
        pre = sim_hist[PERTURBATION_GEN - 1]
        post = sim_hist[PERTURBATION_GEN]
        fin = sim_hist[-1]
        print(f"  {label}:")
        print(f"    Pre-pert:  {pre['n_active_resources']} resources, {pre['n_active_organizations']} orgs")
        print(f"    Post-pert: {post['n_active_resources']} resources, {post['n_active_organizations']} orgs")
        print(f"    Final:     {fin['n_active_resources']} resources, {fin['n_active_organizations']} orgs")

    # Save results
    results = {
        "config": {
            "n_agents": N_AGENTS,
            "n_generations": N_GENERATIONS,
            "trace_decay": TRACE_DECAY,
            "energy_inflow": ENERGY_INFLOW,
            "perturbation_gen": PERTURBATION_GEN,
            "perturbation_strength": PERTURBATION_STRENGTH,
            "seed": SEED,
        },
        "single_trace": sim1.get_results(),
        "multi_trace": sim2.get_results(),
    }

    output_path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")

    return results


if __name__ == "__main__":
    run_comparison()
