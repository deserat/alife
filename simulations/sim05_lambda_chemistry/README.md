# Sim05: Lambda Calculus Chemistry — L1 Formation and L2 Composition Failure

## What it tests

Whether an unbounded molecule space (lambda calculus chemistry) can produce multi-scale composition (L2 organizations) where sim04's finite space (510 species) stalled. Specifically tests whether L1 organizations (autocatalytic sets of lambda expressions) can compose into L2 organizations.

Based on Fontana & Buss (1994) and Mathis et al. (2024, arXiv:2408.12137).

## Hypotheses tested

- **H1** (Composition): Does multi-scale composition emerge with unbounded space? (No — L2 coexistence = 0/6)
- **H8** (Computational Irreducibility): Can we predict which L1 organization will emerge? (No — different seeds produce different organizations)
- **H9** (Evolving Network): Does unbounded space prevent the "one bit" stall? (Partially — species space is never exhausted, but organizations still converge to small stable sets)
- **H10** (NEW): Unbounded molecule space alone is insufficient for multi-scale composition

## Design

- Lambda calculus expressions as molecules (infinite species space)
- Random expression generation (probabilistic grammar, max depth 5)
- Catalytic collisions: A + B → A + B + C where C = (A)B normalized
- Copy actions filtered (prevent L0 trivial fixed point)
- 4 independent L1 runs (pop_size=100, 5000 collisions each)
- 6 pairwise L2 composition tests (combine two L1s, run 5000 collisions)

## Results

### L1 Organization Formation

| Run | Seed | Final Unique | Species Ever Seen |
|-----|------|-------------|-------------------|
| 1 | 1 | 18 | 446 |
| 2 | 8 | 4 | 300 |
| 3 | 15 | 9 | 246 |
| 4 | 22 | 37 | 930 |

Mean final unique: 17.0. Each run converges to a small stable set (4-37 species) after exploring hundreds of species. No two runs converge to the same organization — each L1 is distinct.

### L2 Composition Tests

| Pair | Outcome | Sim to A | Sim to B | Final Unique |
|------|---------|----------|----------|-------------|
| 1+2 | Dominance A | 0.577 | 0.000 | 23 |
| 1+3 | Dominance A | 0.480 | 0.000 | 19 |
| 1+4 | Mutual Destruction | 0.029 | 0.016 | 90 |
| 2+3 | Dominance A | 0.429 | 0.000 | 6 |
| 2+4 | Mutual Destruction | 0.091 | 0.030 | 32 |
| 3+4 | Mutual Destruction | 0.000 | 0.077 | 89 |

- **Dominance**: 3/6 (50%) — one organization survives, the other is destroyed
- **Mutual Destruction**: 3/6 (50%) — both destroyed, novel organization emerges
- **Coexistence (L2)**: 0/6 (0%) — NO cases of successful composition

### Species Space Analysis

Total unique species across all 4 runs: 68 (in final populations). Each run explored 246-930 species — no finite exhaustion (sim04 exhausted 510). The unbounded space is confirmed.

## Key Findings

1. **L1 organizations emerge** from random initial conditions. Each run converges to a small stable set of mutually reproducing expressions. This confirms Fontana & Buss's core finding: self-organized complexity emerges from random interaction.

2. **L2 composition FAILS**. 0/6 pairs achieved coexistence. This is the central finding: even with an unbounded molecule space (infinite species), multi-scale composition (L2) does not emerge spontaneously. Dominance and mutual destruction are the only outcomes.

3. **Unbounded space is necessary but not sufficient.** Sim04 stalled at 510 species (finite space exhaustion). Sim05 never exhausts its space (246-930 species explored per run). But the composition problem persists. The bottleneck is not space — it's the mechanism of composition.

4. **Each L1 is unique.** No two runs produced the same organization. This is computational irreducibility (H8): you cannot predict which organization will emerge without running the simulation.

5. **Mutual destruction produces the most novel species.** When both L1s are destroyed, the resulting organization has the most unique species (89-90). This suggests that cross-organization interactions are productive (they generate novelty) but destabilizing (they destroy the original organizations).

## Limitations

- **Small scale**: 5000 collisions and pop_size=100 are much smaller than Mathis et al. 2024 (1M collisions, 1000 expressions). Results are qualitative, not statistical.
- **Simplified lambda calculus**: No alpha-conversion optimization, pragmatic reduction at 50 steps. Real AlChemy uses 500 steps. Some reactions that would terminate with more steps are marked elastic.
- **No syntactic filter analysis**: We filter copy actions but don't study the L0/L1 boundary systematically.
- **Single generator**: We use only the probabilistic grammar generator. Mathis et al. showed the permutation generator produces dramatically different results.
- **No perturbation robustness test**: We don't test whether L1 organizations survive perturbation (adding random expressions).

## What it teaches

1. **Unbounded molecule space does NOT solve the multi-scale composition problem.** This is the most important finding. Sim04 stalled because of finite space (510 species). Sim05 has infinite space but STILL fails at L2. The problem is architectural, not spatial.

2. **The "one bit" problem is reframed.** Sim04 confirmed Vasas et al.'s "one bit" limitation (finite heritable information). Sim05 shows that even with unbounded space, each L1 organization carries limited information. The bottleneck is not the number of possible molecules but the organization's structure.

3. **Three paths, same failure.** Echo (Holland's CAS model), chemical organizations (COT/Vasas), and AlChemy (lambda calculus) ALL fail at multi-scale composition. Each from a different starting point (CAS theory, origin-of-life chemistry, computational theory). This convergence is strong evidence that the composition problem is fundamental, not an artifact of any single approach.

4. **For sim06**: Need explicit composition mechanisms. The "glue" that enables L2 doesn't emerge spontaneously. It requires either:
   - Stigmergic traces that bridge organizations (our H7 trace→actor crossing)
   - Autopoietic boundaries that protect organizations during interaction (Holland's signals & boundaries)
   - Explicit selection for composability (which AlChemy lacks)
