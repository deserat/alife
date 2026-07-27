# Sim05: Lambda Calculus Chemistry — L1 Formation and L2 Composition Failure

## What it tests

Whether an unbounded molecule space (lambda calculus chemistry) can produce multi-scale composition (L2 organizations) where sim04's finite space (510 species) stalled. Specifically tests whether L1 organizations (autocatalytic sets of lambda expressions) can compose into L2 organizations.

Based on Fontana & Buss (1994) and Mathis et al. (2024, arXiv:2408.12137).

## Hypotheses tested

- **H1** (Composition): Does multi-scale composition emerge with unbounded space? (Sometimes — L2 coexistence = 2/6; the majority outcome is still dominance)
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

> **These results replace the pre-2026-07-27 numbers.** Three defects were found in code
> review and fixed; each one had biased the outcome away from coexistence. See
> "What changed and why" below, and `../REVIEW.md` §2.

### L1 Organization Formation

| Run | Seed | Final Unique | Species Ever Seen |
|-----|------|-------------|-------------------|
| 1 | 1 | 10 | 112 |
| 2 | 8 | 20 | 162 |
| 3 | 15 | 21 | 136 |
| 4 | 22 | 10 | 126 |

Mean final unique: 15.2. Each run converges to a small stable set (10–21 species) after
exploring 112–162 species. Mean pairwise overlap between the runs' final species is 0.061 —
the runs do explore largely disjoint regions.

### L2 Composition Tests

Classified on **survival fraction** (`|A ∩ final| / |A|`, threshold 0.5) — the fraction of each
organization still present at the end:

| Pair | Outcome | Survival A | Survival B | \|A\| | \|B\| | Final Unique |
|------|---------|-----------:|-----------:|------:|------:|-------------:|
| 1+2 | **Coexistence** | 0.800 | 1.000 | 10 | 20 | 23 |
| 1+3 | Dominance B | 0.000 | 0.809 | 10 | 21 | 18 |
| 1+4 | Dominance B | 0.400 | 0.600 | 10 | 10 | 12 |
| 2+3 | **Coexistence** | 0.700 | 0.714 | 20 | 21 | 34 |
| 2+4 | Mutual Destruction | 0.300 | 0.400 | 20 | 10 | 10 |
| 3+4 | Dominance A | 0.809 | 0.000 | 21 | 10 | 18 |

- **Coexistence (L2)**: **2/6 (33%)**
- **Dominance**: 3/6 (50%) — one organization survives, the other is destroyed
- **Mutual Destruction**: 1/6 (17%)

**Threshold sensitivity.** The 2/6 figure is stable across survival thresholds 0.45–0.70. It
rises to 3/6 at 0.40 and 4/6 at 0.30. The classification is therefore *not* an artifact of the
0.5 choice, though the sample is only six pairs.

### Species Space Analysis

Total unique species across all 4 runs: 53 (in final populations). Each run explored 112–162
species with no finite exhaustion (sim04 exhausted 510). Note the previous figures (246–930)
were inflated by the alpha-equivalence bug — the same function under different bound-variable
names was counted as many separate species.

## What changed and why (2026-07-27)

Three defects, each biasing against coexistence, found in code review:

1. **Species identity was not alpha-invariant.** `LExpr.__eq__` compared bound-variable
   *names*, so `λv1.v1` and `λv2.v2` — both the identity function — were different species.
   `subst` mints a fresh name on every capture-avoiding rename, so the same normal form
   reached twice usually compared unequal. This inflated species counts ~3–7× and deflated
   every set intersection. Fixed with de Bruijn-style canonical keys.
2. **Outcomes were classified on Jaccard.** `|A∩F| / |A∪F|` is capped by the size ratio: since
   the final population holds both organizations plus novel species, `|A∪F| >> |A|`. For two
   of the six pairs the ceiling was *below* the 0.15 coexistence threshold (0.125 and 0.101),
   so those tests could not have returned coexistence even with both organizations fully
   intact. Replaced with survival fraction.
3. **The mixed population was seeded almost entirely from organization A.** Padding to
   `pop_size` drew only from `species_a`, so with `|A|+|B| ≈ 30` and `pop_size = 200`,
   A received ~170 extra copies against B's ~20 — a ~9:1 abundance handicap under mass
   action. Every pair returned `dominance_a`; the lower-indexed run always won. Padding now
   alternates between both organizations. **This was the defect responsible for the 0/6
   result**; with equal starting abundance, dominance splits between A and B and coexistence
   appears.

Progression as each fix landed:

| state | coexistence | dominance | mutual destruction |
|---|---:|---:|---:|
| original | 0/6 | 3/6 (all A) | 3/6 |
| + alpha-invariance + survival fraction | 0/6 | 6/6 (all A) | 0/6 |
| + balanced seeding | **2/6** | 3/6 (mixed) | 1/6 |

`sim05.py selftest` now guards the first two properties directly.

## Key Findings

1. **L1 organizations emerge** from random initial conditions. Each run converges to a small
   stable set of mutually reproducing expressions. This confirms Fontana & Buss's core
   finding: self-organized complexity emerges from random interaction. (Caveat: sim05 counts
   surviving species; it does not test closure or self-maintenance, so "organization" here is
   weaker than the COT sense.)

2. **L2 composition is possible but not the norm — 2/6 (33%) coexistence.** This revises the
   earlier claim that composition never occurs. Even with an unbounded molecule space, most
   pairs still end in dominance, but coexistence is not the impossibility the original result
   suggested.

3. **Unbounded space is necessary but not sufficient.** Sim04 stalled at 510 species (finite
   space exhaustion). Sim05 never exhausts its space. Composition remains the minority
   outcome, so the bottleneck is still the mechanism rather than the space — but the evidence
   for that is now considerably weaker than 0/6 implied. **H10 should be re-examined against
   these numbers.**

4. **Each L1 is distinct.** No two runs produced the same organization (mean pairwise overlap
   0.061). This is computational irreducibility (H8): you cannot predict which organization
   emerges without running the simulation.

5. The earlier observation that "mutual destruction produces the most novel species" does not
   survive the fixes — only one pair now ends in mutual destruction, and its final population
   is the *smallest* (10 species), not the largest.

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
