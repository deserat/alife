"""
Sim04: Evolving Reaction Networks — Novel Cores and Compartmentalization
=========================================================================

Tests whether reaction networks that generate NEW reactions (unlike sim03's
fixed network) can produce evolvable organizations, and whether
compartmentalization enables selection between them.

This directly tests:
- H7 (Trace→Actor Crossing): Do novel reactions produce new self-maintaining
  organizations (new actors) from existing resources (traces)?
- H1 (Composition): Does multi-scale structure (molecular + compartmental)
  emerge from evolving reaction dynamics?
- H9 (Evolving Network Evolvability): Does an evolving reaction network
  (new reactions appear) produce open-ended dynamics where a fixed
  network (sim03) stalls?
- H8 (Computational Irreducibility): Can we predict which novel cores will
  appear without simulating?

DESIGN:
-------
Based on Vasas et al. (2012) "Evolution before genes":

- A reaction network with a food set (small molecules)
- Catalyzed ligation/cleavage reactions between polymers (binary alphabet)
- Each molecule has probability P of catalyzing each reaction
- RARE uncatalyzed reactions produce novel species from the "shadow"
- If a novel species catalyzes its own production → new viable core
- Multiple compartments, each containing a reaction network
- Compartments grow and divide (stochastic segregation of molecules)
- Selection: compartments with more non-food mass grow faster
- Compare: fixed network (sim03-like) vs. evolving network (new reactions)

MEASUREMENTS:
- Number of distinct molecular species over time
- Number of autocatalytic cores discovered
- Number of organizations (closure + self-maintenance)
- Between-compartment diversity (different cores in different compartments)
- Total non-food mass across all compartments
- Whether the system explores new organizations (vs. converging to one)

KEY FINDINGS:
- (To be filled after running)
"""

import random
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, FrozenSet, Optional

# ============================================================================
# Configuration
# ============================================================================

ALPHABET = ("a", "b")          # Binary alphabet for polymers
MAX_FOOD_LENGTH = 3            # Food set: all polymers up to this length
MAX_POLYMER_LENGTH = 8         # Maximum polymer length (truncates search space)
P_CATALYST = 0.75              # Probability a molecule is a catalyst
P_CATALYZE = 0.005             # Per-reaction probability a catalyst catalyzes it
SPONTANEOUS_RATE = 0.01        # Rate of uncatalyzed novel reactions
N_COMPARTMENTS = 20            # Number of compartments
COMPARTMENT_CAPACITY = 200     # Molecules per compartment before division
PROPAGULE_SIZE = 50            # Molecules in each daughter after division
FOOD_INFLUX = 5.0              # Food molecules added per time step
DECAY_RATE = 0.001             # First-order decay for all molecules
CONCENTRATION_THRESHOLD = 0.5  # Below this, species is "absent"
N_TIME_STEPS = 1000            # Simulation length
RECORD_INTERVAL = 50           # Record metrics every N steps
SEED = 42

# ============================================================================
# Polymer Chemistry
# ============================================================================

def generate_food_set(max_len: int, alphabet: tuple) -> Set[str]:
    """Generate all polymers up to max_len."""
    food = set()
    for length in range(1, max_len + 1):
        for i in range(len(alphabet) ** length):
            s = []
            n = i
            for _ in range(length):
                s.append(alphabet[n % len(alphabet)])
                n //= len(alphabet)
            food.add("".join(s))
    return food


def cleavage_reactions(polymer: str) -> List[Tuple[str, str, str]]:
    """All ways to split polymer into two parts: (part1, part2, full)."""
    results = []
    for i in range(1, len(polymer)):
        results.append((polymer[:i], polymer[i:], polymer))
    return results


def ligation_reactions(p1: str, p2: str) -> str:
    """Ligation: join two polymers."""
    return p1 + p2


def all_possible_reactions(species: Set[str], max_len: int) -> List[Tuple[str, str, str]]:
    """Generate all possible ligation/cleavage reactions among species.
    Returns list of (reactant1, reactant2, product) where product = r1+r2.
    Cleavage is the reverse: product -> r1 + r2.
    """
    reactions = []
    species_list = sorted(species)
    # Ligation: r1 + r2 -> r1+r2
    for r1 in species_list:
        for r2 in species_list:
            product = r1 + r2
            if len(product) <= max_len:
                reactions.append((r1, r2, product))
    return reactions


# ============================================================================
# Reaction Network with Catalysis
# ============================================================================

class EvolvingReactionNetwork:
    """
    A reaction network where:
    - Molecules are binary polymers
    - Reactions are ligation (join) and cleavage (split)
    - Catalysis is random but fixed per (catalyst, reaction) pair
    - Novel species can appear via rare uncatalyzed reactions
    """

    def __init__(self, food_set: Set[str], seed: int):
        self.rng = random.Random(seed)
        self.food = food_set
        self.max_len = MAX_POLYMER_LENGTH

        # All known species (starts with food, grows as new appear)
        self.species: Set[str] = set(food_set)

        # Catalysis map: (catalyst, (r1, r2, product)) -> bool
        # Determined lazily — only checked when needed
        self._catalysis_cache: Dict[Tuple[str, Tuple[str, str, str]], bool] = {}

        # Concentrations: species -> count (integer molecules)
        self.concentrations: Dict[str, int] = defaultdict(int)
        for f in food_set:
            self.concentrations[f] = 50  # Start with some food

        # Track discovered cores
        self.cores_discovered: List[Set[str]] = []
        self.n_novel_species = 0
        self._active_catalysts: List[str] = []
        self.n_reactions_attempted = 0

    def _is_catalyst(self, molecule: str) -> bool:
        """Whether a molecule can be a catalyst at all."""
        # Use a hash-based deterministic check
        return hash((molecule, "catalyst")) % 1000 < P_CATALYST * 1000

    def _catalyzes(self, catalyst: str, reaction: Tuple[str, str, str]) -> bool:
        """Whether catalyst catalyzes this specific reaction."""
        key = (catalyst, reaction)
        if key in self._catalysis_cache:
            return self._catalysis_cache[key]
        # Deterministic pseudo-random based on hash
        val = (hash((catalyst, reaction, "cat")) % 10000) / 10000.0
        result = val < P_CATALYZE
        self._catalysis_cache[key] = result
        return result

    def _find_catalysts(self, reaction: Tuple[str, str, str]) -> List[str]:
        """Find all species that catalyze this reaction.
        Optimized: only check a random sample of catalyst candidates."""
        catalysts = []
        # Only check active species that are catalysts
        active_cats = [s for s in self._active_catalysts if self.concentrations.get(s, 0) >= 1]
        for s in active_cats:
            if self._catalyzes(s, reaction):
                catalysts.append(s)
        return catalysts

    def step(self, food_influx: float):
        """One time step of reaction dynamics."""
        # Add food
        for f in self.food:
            self.concentrations[f] += int(food_influx / len(self.food))

        # Get active species (above threshold)
        active = [s for s in self.species if self.concentrations.get(s, 0) >= 1]

        # Precompute active catalysts (species that can be catalysts)
        self._active_catalysts = [s for s in active if self._is_catalyst(s)]

        # Limit reaction enumeration: sample a subset of possible reactions
        # Full O(n^2) is too expensive for large species sets
        max_reactions = 200  # Cap per step
        reactions = []
        if len(active) <= 15:
            # Small enough to enumerate all
            for r1 in active:
                for r2 in active:
                    product = r1 + r2
                    if len(product) <= self.max_len and product != r1 and product != r2:
                        reactions.append((r1, r2, product))
        else:
            # Sample reactions
            for _ in range(max_reactions):
                r1 = self.rng.choice(active)
                r2 = self.rng.choice(active)
                product = r1 + r2
                if len(product) <= self.max_len and product != r1 and product != r2:
                    reactions.append((r1, r2, product))

        self.n_reactions_attempted += len(reactions)

        # Execute catalyzed reactions
        for r1, r2, product in reactions:
            if self.concentrations.get(r1, 0) < 1 or self.concentrations.get(r2, 0) < 1:
                continue
            # Check catalysis
            catalysts = self._find_catalysts((r1, r2, product))
            if not catalysts:
                continue
            # Execute reaction (one molecule per catalyst, per step)
            n_react = min(len(catalysts), self.concentrations[r1], self.concentrations[r2])
            if n_react > 0:
                self.concentrations[r1] -= n_react
                self.concentrations[r2] -= n_react
                self.concentrations[product] += n_react
                if product not in self.species:
                    self.species.add(product)
                    self.n_novel_species += 1

        # Rare uncatalyzed reactions (novel species from shadow)
        if active and self.rng.random() < SPONTANEOUS_RATE * len(active):
            # Pick two random active species, try to ligate
            r1 = self.rng.choice(active)
            r2 = self.rng.choice(active)
            product = r1 + r2
            if len(product) <= self.max_len and product not in self.species:
                self.concentrations[product] += 1
                self.species.add(product)
                self.n_novel_species += 1

        # Cleavage reactions (reverse of ligation) — sample
        for s in self.rng.sample(active, min(len(active), 20)):
            if len(s) < 2 or self.concentrations.get(s, 0) < 1:
                continue
            for i in range(1, len(s)):
                p1, p2 = s[:i], s[i:]
                if p1 in self.species and p2 in self.species:
                    catalysts = self._find_catalysts((p1, p2, s))
                    if catalysts:
                        n_cleave = min(len(catalysts), self.concentrations[s])
                        if n_cleave > 0:
                            self.concentrations[s] -= n_cleave
                            self.concentrations[p1] += n_cleave
                            self.concentrations[p2] += n_cleave

        # Decay
        for s in list(self.concentrations.keys()):
            if self.concentrations[s] > 0:
                self.concentrations[s] = max(0, self.concentrations[s] - int(self.concentrations[s] * DECAY_RATE))
            if self.concentrations[s] == 0 and s not in self.food:
                del self.concentrations[s]

    def get_nonfood_mass(self) -> int:
        """Total non-food molecules."""
        return sum(count for s, count in self.concentrations.items() if s not in self.food and count > 0)

    def get_total_mass(self) -> int:
        return sum(self.concentrations.values())

    def get_active_species(self) -> Set[str]:
        return {s for s in self.species if self.concentrations.get(s, 0) >= 1}

    def find_autocatalytic_loops(self) -> List[Set[str]]:
        """Find autocatalytic cores: sets where each member is produced
        by reactions catalyzed by members of the set."""
        active = self.get_active_species()
        nonfood = active - self.food
        if not nonfood:
            return []

        # Build catalysis graph: for each nonfood species, which other
        # nonfood species catalyze a reaction that produces it?
        producers: Dict[str, Set[str]] = defaultdict(set)  # species -> set of catalysts that help produce it

        for s in nonfood:
            # Who catalyzes reactions that produce s?
            for other in active:
                # Ligation: other + x -> s
                if s.startswith(other) and len(other) < len(s):
                    remainder = s[len(other):]
                    if remainder in active:
                        rxn = (other, remainder, s)
                        cats = self._find_catalysts(rxn)
                        for c in cats:
                            if c in nonfood:
                                producers[s].add(c)
                # Cleavage: longer -> s + other
                for longer in active:
                    if longer.startswith(s) and len(longer) > len(s):
                        remainder = longer[len(s):]
                        if remainder in active:
                            rxn = (s, remainder, longer)
                            cats = self._find_catalysts(rxn)
                            for c in cats:
                                if c in nonfood:
                                    producers[s].add(c)

        # Find strongly connected components (cores)
        # A core is a set where every member is produced by a catalyst in the set
        cores = []
        visited = set()
        for s in nonfood:
            if s in visited:
                continue
            # BFS: find all species reachable from s via producer links
            component = set()
            queue = [s]
            while queue:
                current = queue.pop()
                if current in component:
                    continue
                component.add(current)
                visited.add(current)
                # Who produces current? Add them
                for c in producers.get(current, []):
                    if c not in component:
                        queue.append(c)
                # Who does current produce? Add them
                for other in nonfood:
                    if current in producers.get(other, set()):
                        if other not in component:
                            queue.append(other)
            # Check if this is a real core (at least 2 members, or self-catalytic)
            if len(component) >= 1:
                # Verify: every member is produced by at least one other member
                is_core = False
                for m in component:
                    if producers.get(m, set()) & component:
                        is_core = True
                        break
                if is_core:
                    cores.append(component)

        # Deduplicate
        unique_cores = []
        seen = set()
        for c in cores:
            key = frozenset(c)
            if key not in seen:
                seen.add(key)
                unique_cores.append(c)

        return unique_cores


# ============================================================================
# Compartment
# ============================================================================

@dataclass
class Compartment:
    """A compartment containing a reaction network."""
    network: EvolvingReactionNetwork
    age: int = 0
    divisions: int = 0

    def total_mass(self) -> int:
        return self.network.get_total_mass()

    def nonfood_mass(self) -> int:
        return self.network.get_nonfood_mass()

    def step(self, food_influx: float):
        self.network.step(food_influx)
        self.age += 1

    def should_divide(self) -> bool:
        return self.total_mass() >= COMPARTMENT_CAPACITY

    def divide(self, rng: random.Random) -> 'Compartment':
        """Divide this compartment into two daughters."""
        # Stochastic segregation: randomly distribute molecules
        daughter_conc = defaultdict(int)
        for s, count in self.network.concentrations.items():
            for _ in range(count):
                if rng.random() < 0.5:
                    daughter_conc[s] += 1
                else:
                    # stays in parent (reduce parent's count)
                    pass
        # Reduce parent's concentrations
        for s in list(self.network.concentrations.keys()):
            self.network.concentrations[s] = self.network.concentrations[s] - daughter_conc[s]
            if self.network.concentrations[s] < 0:
                self.network.concentrations[s] = 0

        # Create daughter network (shares species set, catalysis cache)
        daughter_net = EvolvingReactionNetwork(self.network.food, rng.randint(0, 10**9))
        daughter_net.species = set(self.network.species)
        daughter_net._catalysis_cache = self.network._catalysis_cache  # Share cache
        daughter_net.concentrations = daughter_conc

        self.divisions += 1
        self.age = 0

        return Compartment(network=daughter_net, age=0)


# ============================================================================
# Simulation
# ============================================================================

class Simulation:
    def __init__(self, evolving: bool, seed: int = SEED, label: str = ""):
        self.evolving = evolving
        self.label = label
        self.rng = random.Random(seed)
        food = generate_food_set(MAX_FOOD_LENGTH, ALPHABET)

        # Initialize compartments
        self.compartments: List[Compartment] = []
        for i in range(N_COMPARTMENTS):
            net = EvolvingReactionNetwork(food, seed + i)
            self.compartments.append(Compartment(network=net))

        self.history: List[Dict] = []
        self.global_species: Set[str] = set(food)

    def step(self, t: int):
        """One time step."""
        new_compartments = []

        for comp in self.compartments:
            comp.step(FOOD_INFLUX)
            self.global_species |= comp.network.species

            if comp.should_divide():
                daughter = comp.divide(self.rng)
                new_compartments.append(daughter)

        self.compartments.extend(new_compartments)

        # If too many compartments, remove the ones with least mass (selection)
        if len(self.compartments) > N_COMPARTMENTS * 2:
            self.compartments.sort(key=lambda c: c.total_mass(), reverse=True)
            self.compartments = self.compartments[:N_COMPARTMENTS]

        # Record
        if t % RECORD_INTERVAL == 0 or t == N_TIME_STEPS - 1:
            self.record(t)

    def record(self, t: int):
        """Record metrics."""
        total_mass = sum(c.total_mass() for c in self.compartments)
        total_nonfood = sum(c.nonfood_mass() for c in self.compartments)
        n_species = len(self.global_species)
        n_compartments = len(self.compartments)

        # Count cores in a sample of compartments
        n_cores = 0
        core_sizes = []
        for c in self.compartments[:5]:  # Sample first 5
            cores = c.network.find_autocatalytic_loops()
            n_cores += len(cores)
            core_sizes.extend(len(core) for core in cores)

        # Between-compartment diversity: how many distinct active species sets?
        active_sets = []
        for c in self.compartments[:10]:
            active = frozenset(c.network.get_active_species())
            active_sets.append(active)
        n_distinct = len(set(active_sets))

        self.history.append({
            "time": t,
            "n_compartments": n_compartments,
            "n_species": n_species,
            "total_mass": total_mass,
            "total_nonfood_mass": total_nonfood,
            "n_cores_sampled": n_cores,
            "core_sizes": core_sizes,
            "n_distinct_compartment_types": n_distinct,
        })

    def run(self):
        print(f"\n{'='*60}")
        print(f"Sim04: {self.label}")
        print(f"{'='*60}")
        for t in range(N_TIME_STEPS):
            self.step(t)
            if t % 500 == 0 or t == N_TIME_STEPS - 1:
                h = self.history[-1]
                print(f"  t={t:5d}: comps={h['n_compartments']:3d}, "
                      f"species={h['n_species']:4d}, mass={h['total_mass']:6d}, "
                      f"nonfood={h['total_nonfood_mass']:5d}, "
                      f"cores={h['n_cores_sampled']:2d}, "
                      f"diversity={h['n_distinct_compartment_types']}")

    def get_results(self) -> Dict:
        return {
            "label": self.label,
            "evolving": self.evolving,
            "history": self.history,
        }


# ============================================================================
# Main
# ============================================================================

def main():
    global SPONTANEOUS_RATE
    print("=" * 60)
    print("Sim04: Evolving Reaction Networks")
    print("Novel Cores, Compartmentalization, Evolvability")
    print("=" * 60)
    print(f"Food set: polymers up to length {MAX_FOOD_LENGTH} ({len(ALPHABET)}-letter alphabet)")
    print(f"P_catalyst={P_CATALYST}, P_catalyze={P_CATALYZE}")
    print(f"Spontaneous rate={SPONTANEOUS_RATE}")
    print(f"Compartments={N_COMPARTMENTS}, capacity={COMPARTMENT_CAPACITY}")
    print(f"Time steps={N_TIME_STEPS}")

    # Condition 1: Fixed network (no spontaneous reactions)
    orig_spont = SPONTANEOUS_RATE

    SPONTANEOUS_RATE = 0.0
    sim_fixed = Simulation(evolving=False, seed=SEED, label="FIXED NETWORK (no novel reactions)")
    sim_fixed.run()

    # Condition 2: Evolving network (spontaneous reactions produce novel species)
    SPONTANEOUS_RATE = orig_spont
    sim_evolving = Simulation(evolving=True, seed=SEED, label="EVOLVING NETWORK (novel reactions)")
    sim_evolving.run()

    # Comparison
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)

    hf = sim_fixed.history[-1]
    he = sim_evolving.history[-1]

    print(f"\n{'Metric':<35} {'Fixed':>12} {'Evolving':>12}")
    print(f"  {'-'*33} {'-'*12} {'-'*12}")
    print(f"  {'Species discovered':.<35} {hf['n_species']:>12} {he['n_species']:>12}")
    print(f"  {'Total mass':.<35} {hf['total_mass']:>12} {he['total_mass']:>12}")
    print(f"  {'Non-food mass':.<35} {hf['total_nonfood_mass']:>12} {he['total_nonfood_mass']:>12}")
    print(f"  {'Cores (sampled)':.<35} {hf['n_cores_sampled']:>12} {he['n_cores_sampled']:>12}")
    print(f"  {'Compartment diversity':.<35} {hf['n_distinct_compartment_types']:>12} {he['n_distinct_compartment_types']:>12}")

    # Save results
    results = {
        "config": {
            "alphabet": ALPHABET,
            "max_food_length": MAX_FOOD_LENGTH,
            "max_polymer_length": MAX_POLYMER_LENGTH,
            "p_catalyst": P_CATALYST,
            "p_catalyze": P_CATALYZE,
            "spontaneous_rate": orig_spont,
            "n_compartments": N_COMPARTMENTS,
            "compartment_capacity": COMPARTMENT_CAPACITY,
            "propagule_size": PROPAGULE_SIZE,
            "n_time_steps": N_TIME_STEPS,
            "seed": SEED,
        },
        "fixed_network": sim_fixed.get_results(),
        "evolving_network": sim_evolving.get_results(),
    }

    output_path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
