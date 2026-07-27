#!/usr/bin/env python3
"""
Sim05: Lambda Calculus Chemistry (AlChemy-inspired)

Tests:
1. Do stable L1 organizations (autocatalytic sets of lambda expressions) emerge
   from random initial conditions in an unbounded molecule space?
2. Can two L1 organizations compose into an L2 organization (multi-scale composition)?
   - Three outcomes: Dominance, Mutual Destruction, Coexistence
3. Does the unbounded molecule space prevent the "one bit" stall from sim04?

Based on Fontana & Buss (1994) "The Arrival of the Fittest" and
Mathis et al. (2024) "Return to AlChemy" (arXiv:2408.12137).

Key connection to our thesis: AlChemy has UNBOUNDED molecule space (lambda calculus
expressions are infinite), yet L2 composition is RARE. This means unbounded space
alone does not solve the multi-scale composition problem — confirming H1 and motivating H10.
"""

import os
import random
import json
import sys
from collections import Counter, defaultdict
import time

# ============================================================
# Lambda Calculus Implementation
# ============================================================

_fresh_counter = [0]

def fresh_var():
    _fresh_counter[0] += 1
    return f"v{_fresh_counter[0]}"

class LExpr:
    """
    Lambda expression: one of
    - Var(name)
    - Abs(var_name, body)
    - App(func, arg)
    """
    __slots__ = ['kind', 'a', 'b', '_canon']

    def __init__(self, kind, a=None, b=None):
        self.kind = kind
        self.a = a  # var name (str) for Var, var name (str) for Abs, func (LExpr) for App
        self.b = b  # None for Var, body (LExpr) for Abs, arg (LExpr) for App
        self._canon = None

    def canonical(self, env=None):
        """de Bruijn-style canonical key. Alpha-equivalent expressions share it.

        Species identity MUST be alpha-invariant. Comparing bound-variable names
        directly makes (Lv1.v1) and (Lv2.v2) — both the identity function —
        distinct species. That inflates species counts and deflates every set
        intersection, which biased the L2 composition outcomes toward
        mutual_destruction. Worse, `subst` mints a fresh name on every
        capture-avoiding rename, so the same normal form reached twice usually
        compared unequal. See ../REVIEW.md section 2.

        A bound variable is keyed by its binding depth (number of intervening
        binders), so the key is independent of the names chosen.
        """
        if env is None:
            if self._canon is not None:
                return self._canon
            env = {}
            key = self._canonical(env)
            self._canon = key
            return key
        return self._canonical(env)

    def _canonical(self, env):
        if self.kind == 'var':
            # Bound -> de Bruijn index; free -> its own name (standardize()
            # removes free vars, but expressions are keyed safely regardless).
            return f"b{env[self.a]}" if self.a in env else f"f{self.a}"
        if self.kind == 'abs':
            inner = {k: v + 1 for k, v in env.items()}
            inner[self.a] = 0
            return f"(L.{self.b._canonical(inner)})"
        if self.kind == 'app':
            return f"({self.a._canonical(env)} {self.b._canonical(env)})"

    def __eq__(self, other):
        if not isinstance(other, LExpr): return False
        return self.canonical() == other.canonical()

    def __hash__(self):
        return hash(self.canonical())

    def __repr__(self):
        return self.to_str()
    
    def to_str(self):
        if self.kind == 'var': return self.a
        if self.kind == 'abs': return f"(λ{self.a}.{self.b.to_str()})"
        if self.kind == 'app': return f"({self.a.to_str()} {self.b.to_str()})"
    
    def size(self):
        if self.kind == 'var': return 1
        if self.kind == 'abs': return 1 + self.b.size()
        if self.kind == 'app': return 1 + self.a.size() + self.b.size()
    
    def free_vars(self):
        if self.kind == 'var': return {self.a}
        if self.kind == 'abs': return self.b.free_vars() - {self.a}
        if self.kind == 'app': return self.a.free_vars() | self.b.free_vars()
    
    def subst(self, var, repl):
        """Capture-avoiding substitution: replace free occurrences of var with repl."""
        if self.kind == 'var':
            return repl if self.a == var else self
        if self.kind == 'abs':
            if self.a == var:
                return self  # shadowed
            if self.a in repl.free_vars():
                # alpha-rename to avoid capture
                fv = fresh_var()
                new_body = self.b.subst(self.a, LExpr('var', fv))
                return LExpr('abs', fv, new_body.subst(var, repl))
            return LExpr('abs', self.a, self.b.subst(var, repl))
        if self.kind == 'app':
            return LExpr('app', self.a.subst(var, repl), self.b.subst(var, repl))
    
    def reduce_step(self):
        """Leftmost-outermost beta reduction. Returns (expr, reduced_bool)."""
        if self.kind == 'var':
            return self, False
        if self.kind == 'abs':
            body, reduced = self.b.reduce_step()
            return (LExpr('abs', self.a, body), True) if reduced else (self, False)
        if self.kind == 'app':
            if self.a.kind == 'abs':
                # Beta redex: (λx.body) arg → body[x:=arg]
                result = self.a.b.subst(self.a.a, self.b)
                return result, True
            func, reduced = self.a.reduce_step()
            if reduced:
                return LExpr('app', func, self.b), True
            arg, reduced = self.b.reduce_step()
            if reduced:
                return LExpr('app', self.a, arg), True
            return self, False
    
    def normalize(self, max_steps=200):
        """Reduce to normal form or give up."""
        expr = self
        for _ in range(max_steps):
            expr, reduced = expr.reduce_step()
            if not reduced:
                return expr, True  # reached normal form
        return expr, False  # did not terminate
    
    def is_identity(self):
        """Check if this is λx.x (identity/copy function)."""
        return (self.kind == 'abs' and 
                self.b.kind == 'var' and 
                self.b.a == self.a)


# ============================================================
# Random Expression Generation (probabilistic grammar)
# ============================================================

def gen_random_expr(depth, max_depth=7, p_app=0.35, p_abs=0.35, bound_vars=None):
    """Generate a random lambda expression using probabilistic grammar."""
    if bound_vars is None:
        bound_vars = []
    
    if depth >= max_depth:
        # Force variable
        if bound_vars:
            return LExpr('var', random.choice(bound_vars))
        else:
            v = fresh_var()
            return LExpr('abs', v, LExpr('var', v))  # λv.v (identity when no bound vars)
    
    r = random.random()
    
    if depth == 0:
        # At root, prefer abstraction or application
        r = random.random()
        if r < 0.45:
            v = fresh_var()
            body = gen_random_expr(depth + 1, max_depth, p_app, p_abs, bound_vars + [v])
            return LExpr('abs', v, body)
        elif r < 0.90:
            func = gen_random_expr(depth + 1, max_depth, p_app, p_abs, bound_vars)
            arg = gen_random_expr(depth + 1, max_depth, p_app, p_abs, bound_vars)
            return LExpr('app', func, arg)
        else:
            if bound_vars:
                return LExpr('var', random.choice(bound_vars))
            v = fresh_var()
            return LExpr('abs', v, LExpr('var', v))
    
    if r < p_app:
        func = gen_random_expr(depth + 1, max_depth, p_app, p_abs, bound_vars)
        arg = gen_random_expr(depth + 1, max_depth, p_app, p_abs, bound_vars)
        return LExpr('app', func, arg)
    elif r < p_app + p_abs:
        v = fresh_var()
        body = gen_random_expr(depth + 1, max_depth, p_app, p_abs, bound_vars + [v])
        return LExpr('abs', v, body)
    else:
        # Variable
        if bound_vars:
            return LExpr('var', random.choice(bound_vars))
        else:
            # No bound vars - wrap in abstraction
            v = fresh_var()
            return LExpr('abs', v, LExpr('var', v))


def standardize(expr):
    """Remove free variables by binding them with leading abstractions."""
    fv = expr.free_vars()
    for v in sorted(fv):
        expr = LExpr('abs', v, expr)
    return expr


def gen_standardized_expr(max_depth=7):
    """Generate a random standardized expression (no free variables)."""
    raw = gen_random_expr(0, max_depth)
    return standardize(raw)


# ============================================================
# AlChemy Simulation
# ============================================================

def collide(a, b, max_reduce=200):
    """Apply a to b, reduce to normal form. Returns (result, terminated)."""
    app = LExpr('app', a, b)
    result, terminated = app.normalize(max_reduce)
    return result, terminated


def run_alchemy(pop_size=200, n_collisions=30000, max_depth=7, max_reduce=200, 
                filter_copy=False, seed=0):
    """Run an AlChemy simulation.
    
    Args:
        pop_size: Maximum number of expressions in the soup
        n_collisions: Number of collision steps to run
        max_depth: Max depth for random expression generation
        max_reduce: Max beta reduction steps before giving up
        filter_copy: If True, reject reactions that produce identity (copy) functions
        seed: Random seed
    
    Returns:
        dict with: population (list of LExpr), species_history (list of (step, n_unique)), 
                   collision_log (list of (step, n_unique, n_total))
    """
    random.seed(seed)
    _fresh_counter[0] = 0
    
    # Initialize population with random standardized expressions
    population = []
    for _ in range(pop_size):
        expr = gen_standardized_expr(max_depth)
        _, term = expr.normalize(max_reduce)
        if term:
            population.append(expr)
    
    # Deduplicate initially (use string repr as key)
    # Actually keep duplicates - mass action depends on concentrations
    
    species_history = []
    collision_log = []
    new_species_events = []
    seen_species = set()
    
    for e in population:
        seen_species.add(e)
    
    species_history.append((0, len(seen_species)))
    
    for step in range(1, n_collisions + 1):
        if len(population) < 2:
            break
        
        # Pick two expressions at random (mass action: proportional to abundance)
        idx_a = random.randint(0, len(population) - 1)
        idx_b = random.randint(0, len(population) - 1)
        if idx_a == idx_b:
            continue
        
        a = population[idx_a]
        b = population[idx_b]
        
        # Collision: apply a to b (catalytic: A + B → A + B + C)
        result, terminated = collide(a, b, max_reduce)
        
        if not terminated:
            continue  # Elastic collision (non-terminating reduction)
        
        # Skip identity results (they'd dominate)
        if result.is_identity() and filter_copy:
            continue
        
        # Skip if result is same as both inputs (pure copy action A+B → 2A+B)
        if result == a or result == b:
            continue
        
        if result.size() > 30:
            continue  # Skip large expressions for computational tractability

        # Add result to population
        population.append(result)

        # Remove a random expression to maintain population size
        remove_idx = random.randint(0, len(population) - 1)
        population.pop(remove_idx)

        # Track new species
        if result not in seen_species:
            seen_species.add(result)
            new_species_events.append((step, result.size(), len(seen_species)))

        if step % 500 == 0 or step == n_collisions:
            unique = len(set(population))
            collision_log.append({
                'step': step,
                'n_unique': unique,
                'n_total': len(population),
                'n_species_ever': len(seen_species)
            })
            if step % 1000 == 0:
                print(f"    step {step}: {unique} unique, {len(seen_species)} ever seen")
    
    # Final population analysis
    final_species = Counter()
    for e in population:
        final_species[e] += 1
    
    return {
        'population': population,
        'final_species': final_species,
        'n_unique_final': len(final_species),
        'n_species_ever': len(seen_species),
        'collision_log': collision_log,
        'new_species_events': [(s, sz, ns) for s, sz, ns in new_species_events],
        'seed': seed
    }


# Fraction of an organization's species that must persist for it to count as
# surviving the mixture. 0.5 = "a majority of the organization is still there".
SURVIVAL_THRESHOLD = 0.5


def survival_fraction(species_a, final_set):
    """Fraction of organization A's species still present in the final population.

    This is the metric the L2 question actually asks: did organization A
    persist? Jaccard (|A n F| / |A u F|) was used previously and is the wrong
    tool — because the combined population contains BOTH organizations plus any
    novel species, |A u F| is much larger than |A|, so Jaccard is capped by the
    size ratio no matter what the dynamics do. For two of the six sim05 pairs
    the ceiling was BELOW the 0.15 coexistence threshold (0.125 and 0.101), so
    those tests could not have returned coexistence even with both organizations
    fully intact. See ../REVIEW.md section 2.
    """
    set_a = set(species_a)
    if not set_a:
        return 0.0
    return len(set_a & set(final_set)) / len(set_a)


def jaccard_similarity(species_a, species_b):
    """Jaccard index between two sets of expressions.

    Retained only so results.json can report the old metric alongside the new
    one for continuity. Do not classify outcomes with it — see
    survival_fraction above.
    """
    set_a = set(species_a)
    set_b = set(species_b)
    if not set_a and not set_b:
        return 1.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def test_l2_composition(run_a, run_b, pop_size=400, n_collisions=20000, max_reduce=200, seed=42):
    """Combine two L1 organizations and test if they compose (L2) or not.
    
    Returns: dict with outcome ('dominance', 'mutual_destruction', 'coexistence'),
             similarity_a, similarity_b
    """
    random.seed(seed)

    # Get unique expressions from each run. Sorted by canonical key: iteration
    # order of a set of LExpr depends on string hashing, which Python randomizes
    # per process, so an unsorted list would make this test irreproducible
    # across runs.
    species_a = sorted(set(run_a['population']), key=lambda e: e.canonical())
    species_b = sorted(set(run_b['population']), key=lambda e: e.canonical())

    # Combine into one population, padding to pop_size.
    #
    # The padding must draw from BOTH organizations in alternation. It
    # previously drew only from species_a, so with |A|+|B| ~ 30 and
    # pop_size = 200 organization A received ~170 extra copies while B got only
    # its own ~20 members. Under mass action that is a ~9:1 abundance handicap,
    # and it made A win by construction — every one of the six pairs returned
    # `dominance_a`, i.e. the lower-indexed run always won. Equal total
    # abundance is the fair starting condition for asking whether two
    # organizations coexist. See ../REVIEW.md section 2.
    combined = species_a + species_b
    pad_sources = [s for s in (species_a, species_b) if s]
    i = 0
    while len(combined) < pop_size and pad_sources:
        combined.append(random.choice(pad_sources[i % len(pad_sources)]))
        i += 1
    combined = combined[:pop_size]
    
    # Run collision dynamics
    population = combined[:]
    seen_species = set(population)
    
    for step in range(1, n_collisions + 1):
        if len(population) < 2:
            break
        
        idx_a = random.randint(0, len(population) - 1)
        idx_b = random.randint(0, len(population) - 1)
        if idx_a == idx_b:
            continue
        
        a = population[idx_a]
        b = population[idx_b]
        
        result, terminated = collide(a, b, max_reduce)
        if not terminated:
            continue
        if result.is_identity():
            continue
        if result == a or result == b:
            continue
        if result.size() > 30:
            continue

        population.append(result)
        remove_idx = random.randint(0, len(population) - 1)
        population.pop(remove_idx)
    
    # Measure how much of each original organization persisted
    final_set = set(population)
    surv_a = survival_fraction(species_a, final_set)
    surv_b = survival_fraction(species_b, final_set)

    # Classify outcome on survival fraction (see survival_fraction docstring for
    # why Jaccard is unsuitable). Jaccard is still reported for continuity with
    # the pre-2026-07-27 results.
    threshold = SURVIVAL_THRESHOLD
    if surv_a >= threshold and surv_b >= threshold:
        outcome = 'coexistence'
    elif surv_a >= threshold:
        outcome = 'dominance_a'
    elif surv_b >= threshold:
        outcome = 'dominance_b'
    else:
        outcome = 'mutual_destruction'

    return {
        'outcome': outcome,
        'survival_a': round(surv_a, 4),
        'survival_b': round(surv_b, 4),
        'survival_threshold': threshold,
        'n_species_a': len(species_a),
        'n_species_b': len(species_b),
        # Legacy metric, reported for comparison only — not used to classify.
        'jaccard_a': round(jaccard_similarity(species_a, final_set), 4),
        'jaccard_b': round(jaccard_similarity(species_b, final_set), 4),
        'n_unique_final': len(final_set),
    }


# ============================================================
# Main Experiment
# ============================================================

def main():
    print("=" * 70)
    print("Sim05: Lambda Calculus Chemistry (AlChemy-inspired)")
    print("Testing: L1 organization emergence + L2 composition failure")
    print("=" * 70)
    
    results = {
        'experiment': 'sim05_lambda_calculus_chemistry',
        'params': {},
        'l1_runs': [],
        'l2_tests': [],
        'summary': {}
    }
    
    # --- Phase 1: Run independent L1 simulations ---
    print("\n--- Phase 1: L1 Organization Formation ---")
    
    n_runs = 4
    pop_size = 100
    n_collisions = 5000
    max_depth = 5
    max_reduce = 50
    
    results['params']['l1'] = {
        'n_runs': n_runs, 'pop_size': pop_size, 
        'n_collisions': n_collisions, 'max_depth': max_depth,
        'max_reduce': max_reduce, 'filter_copy': True
    }
    
    l1_runs = []
    for i in range(n_runs):
        print(f"\n  Run {i+1}/{n_runs} (seed={i*7+1})...")
        t0 = time.time()
        run = run_alchemy(
            pop_size=pop_size, n_collisions=n_collisions, 
            max_depth=max_depth, max_reduce=max_reduce,
            filter_copy=True, seed=i*7+1
        )
        elapsed = time.time() - t0
        n_unique = run['n_unique_final']
        n_ever = run['n_species_ever']
        print(f"    Final unique species: {n_unique}")
        print(f"    Total species ever seen: {n_ever}")
        print(f"    Time: {elapsed:.1f}s")
        
        # Convert population to serializable format
        pop_strs = [e.to_str() for e in run['population']]
        species_counts = {e.to_str(): c for e, c in run['final_species'].most_common(20)}
        
        run_data = {
            'seed': run['seed'],
            'n_unique_final': n_unique,
            'n_species_ever': n_ever,
            'collision_log': run['collision_log'],
            'new_species_count': len(run['new_species_events']),
            'top_species': species_counts,
            'elapsed_seconds': round(elapsed, 2)
        }
        l1_runs.append((run, run_data))
        results['l1_runs'].append(run_data)
    
    # Summary of L1 runs
    l1_unique_counts = [r[1]['n_unique_final'] for r in l1_runs]
    l1_species_ever = [r[1]['n_species_ever'] for r in l1_runs]
    results['summary']['l1_unique_counts'] = l1_unique_counts
    results['summary']['l1_species_ever'] = l1_species_ever
    results['summary']['l1_mean_unique'] = sum(l1_unique_counts) / len(l1_unique_counts)
    
    print(f"\n  L1 Summary: mean unique species = {results['summary']['l1_mean_unique']:.1f}")
    print(f"  Species ever seen: {l1_species_ever}")
    
    # --- Phase 2: L2 Composition Tests ---
    print("\n--- Phase 2: L2 Composition Tests ---")
    
    n_pairs = min(8, n_runs * (n_runs - 1) // 2)
    pairs = []
    for i in range(n_runs):
        for j in range(i+1, n_runs):
            pairs.append((i, j))
    pairs = pairs[:n_pairs]
    
    l2_outcomes = Counter()
    
    for pair_idx, (i, j) in enumerate(pairs):
        print(f"\n  L2 Test {pair_idx+1}/{len(pairs)}: Run {i+1} + Run {j+1}")
        t0 = time.time()
        
        l2_result = test_l2_composition(
            l1_runs[i][0], l1_runs[j][0],
            pop_size=200, n_collisions=5000, max_reduce=max_reduce,
            seed=100 + pair_idx
        )
        elapsed = time.time() - t0
        print(f"    Outcome: {l2_result['outcome']}")
        print(f"    Survival of A: {l2_result['survival_a']} "
              f"({l2_result['n_species_a']} species)  [jaccard {l2_result['jaccard_a']}]")
        print(f"    Survival of B: {l2_result['survival_b']} "
              f"({l2_result['n_species_b']} species)  [jaccard {l2_result['jaccard_b']}]")
        print(f"    Final unique: {l2_result['n_unique_final']}")
        print(f"    Time: {elapsed:.1f}s")
        
        l2_result['pair'] = (i, j)
        l2_result['elapsed_seconds'] = round(elapsed, 2)
        results['l2_tests'].append(l2_result)
        
        # Normalize outcome for counting
        if l2_result['outcome'].startswith('dominance'):
            l2_outcomes['dominance'] += 1
        else:
            l2_outcomes[l2_result['outcome']] += 1
    
    results['summary']['l2_outcomes'] = dict(l2_outcomes)
    results['summary']['l2_total_tests'] = len(pairs)
    
    print(f"\n  L2 Summary: {dict(l2_outcomes)}")
    
    # --- Phase 3: Control — species space growth (unbounded vs sim04's 510) ---
    print("\n--- Phase 3: Species Space Analysis ---")
    
    # Compare to sim04's finite space
    all_species_ever = set()
    for run, _ in l1_runs:
        all_species_ever.update(set(run['population']))
    
    results['summary']['total_unique_species_all_runs'] = len(all_species_ever)
    results['summary']['sim04_max_species'] = 510  # binary polymers up to length 8

    # Whether the runs actually explored DISJOINT regions of the space. The
    # previous flag here was `len(...) > 510 or all(...) == False`, which
    # evaluates True whenever any run had <=510 species — i.e. a tautology that
    # reported success regardless of the data (../REVIEW.md section 2). Measure
    # something falsifiable instead: overlap between the runs' final species.
    run_sets = [set(run['population']) for run, _ in l1_runs]
    pairwise_overlap = []
    for i in range(len(run_sets)):
        for j in range(i + 1, len(run_sets)):
            union = run_sets[i] | run_sets[j]
            pairwise_overlap.append(
                len(run_sets[i] & run_sets[j]) / len(union) if union else 0.0)
    mean_overlap = sum(pairwise_overlap) / len(pairwise_overlap) if pairwise_overlap else 0.0
    results['summary']['mean_pairwise_run_overlap'] = round(mean_overlap, 4)
    results['summary']['runs_explored_disjoint_regions'] = mean_overlap < 0.1

    print(f"  Total unique species across all runs: {len(all_species_ever)}")
    print(f"  Sim04 finite limit was: 510")
    print(f"  Mean pairwise overlap between runs' final species: {mean_overlap:.4f}")
    print(f"  Runs explored largely disjoint regions: {mean_overlap < 0.1}")
    
    # --- Save results ---
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}")
    
    # Print final summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"L1 Organization Formation:")
    print(f"  {n_runs} independent runs, mean {results['summary']['l1_mean_unique']:.1f} unique species")
    print(f"  Species ever seen per run: {l1_species_ever}")
    print(f"  (Sim04 exhausted 510 species; sim05 space is unbounded)")
    print(f"\nL2 Composition Tests:")
    print(f"  {len(pairs)} pairs tested")
    for outcome, count in l2_outcomes.items():
        print(f"  {outcome}: {count} ({100*count/len(pairs):.0f}%)")
    # Report the proportion rather than a binary verdict. The previous form
    # printed "L2 composition is RARE - confirms H1" whenever coexistence was
    # <= n_pairs // 3, which at 2/6 is a boundary case being reported as a
    # clean confirmation.
    n_coex = l2_outcomes.get('coexistence', 0)
    print(f"\nKey Finding: coexistence in {n_coex}/{len(pairs)} pairs "
          f"({100 * n_coex / len(pairs):.0f}%), at survival threshold "
          f"{SURVIVAL_THRESHOLD}. Interpret against H1/H10 with the threshold "
          f"sensitivity in README.md in view — this is a small sample and the "
          f"outcome classification is threshold-dependent.")
    
    return results


def cmd_selftest():
    """Internal sanity checks. Prints 'Part N OK' per group and exits 0."""
    # Part 1: alpha-invariant species identity. This is the property whose
    # absence biased the L2 outcomes — guard it hard.
    id1 = LExpr('abs', 'v1', LExpr('var', 'v1'))
    id2 = LExpr('abs', 'v2', LExpr('var', 'v2'))
    assert id1 == id2, "Part 1: alpha-equivalent identities compare unequal"
    assert hash(id1) == hash(id2), "Part 1: alpha-equivalent identities hash differently"
    assert len({id1, id2}) == 1, "Part 1: alpha-equivalent identities are distinct set members"

    # Nested binders must not collapse: (Lx.Ly.x) and (Lx.Ly.y) differ.
    k_comb = LExpr('abs', 'x', LExpr('abs', 'y', LExpr('var', 'x')))
    ki_comb = LExpr('abs', 'x', LExpr('abs', 'y', LExpr('var', 'y')))
    assert k_comb != ki_comb, "Part 1: distinct combinators collapsed to one species"
    # ...and renaming those binders must not change identity.
    k_renamed = LExpr('abs', 'p', LExpr('abs', 'q', LExpr('var', 'p')))
    assert k_comb == k_renamed, "Part 1: renaming nested binders changed species identity"

    # Free variables stay distinguishable.
    assert LExpr('var', 'z') != LExpr('var', 'w'), "Part 1: distinct free vars merged"
    print("selftest: Part 1 OK")

    # Part 2: reduction preserves species identity across fresh-name minting.
    _fresh_counter[0] = 0
    inner = LExpr('abs', 'x', LExpr('app', LExpr('var', 'x'), LExpr('var', 'y')))
    app1 = LExpr('app', LExpr('abs', 'y', inner), LExpr('var', 'q'))
    r1, ok1 = app1.normalize(50)
    _fresh_counter[0] = 500          # different fresh-name stream
    app2 = LExpr('app', LExpr('abs', 'y', inner), LExpr('var', 'q'))
    r2, ok2 = app2.normalize(50)
    assert ok1 and ok2, "Part 2: normalization did not terminate"
    assert r1 == r2, "Part 2: same normal form counted as two species under different names"
    print("selftest: Part 2 OK")

    # Part 3: survival_fraction measures what the L2 question asks, and is not
    # capped by the size of the final population the way Jaccard is.
    a = [LExpr('var', 'a1'), LExpr('var', 'a2')]
    big_final = set(a) | {LExpr('var', f'n{i}') for i in range(50)}
    assert survival_fraction(a, big_final) == 1.0, \
        "Part 3: fully-surviving organization did not score 1.0"
    assert jaccard_similarity(a, big_final) < 0.15, \
        "Part 3: expected Jaccard to be crushed by a large final set"
    assert survival_fraction(a, set()) == 0.0
    assert survival_fraction([], big_final) == 0.0
    half = survival_fraction(a, {LExpr('var', 'a1')})
    assert abs(half - 0.5) < 1e-9, f"Part 3: expected 0.5, got {half}"
    print("selftest: Part 3 OK")

    # Part 4: a short AlChemy run produces a population and terminates.
    run = run_alchemy(pop_size=20, n_collisions=200, max_depth=4,
                      max_reduce=30, filter_copy=True, seed=3)
    assert run['n_unique_final'] >= 1, "Part 4: run produced an empty population"
    assert run['n_species_ever'] >= run['n_unique_final']
    print("selftest: Part 4 OK")


def main_cli():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        cmd_selftest()
    elif cmd == "run":
        main()
    else:
        print("usage: sim05.py [run|selftest]")


if __name__ == '__main__':
    main_cli()
