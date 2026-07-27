# Simulation Code Review — 2026-07-27

A construct-validity audit of all six implemented simulations (sim01–sim06, 3,232 lines of
Python), asking one question: **does each simulation measure the thing it claims to measure?**
Every claim below was verified against the committed `results.json` files, not inferred from
reading the code alone; reproduction snippets are given for each finding.

The methodology of this project is not in question — null results are reported honestly and
criticism sections are real. The problem found is narrower and fixable: **the detectors are
broken, not the models.**

## Bottom line

Five of six simulations measure something different from what they claim. The three results the
project's argument currently rests on are measurement artifacts:

| result | status |
|---|---|
| sim06 null → H7 unsupported | **artifact** — the crossing detector cannot fire in a positive-feedback model |
| sim05 0/6 L2 coexistence → H10 | **artifact** — 2/6 tests were mathematically incapable of returning coexistence; species identity is not alpha-invariant |
| sim02 "dynamic converges harder" → H4 | **confounded** — the trace bonus cannot reshape selection over strategies |

The encouraging reading: **H7 and H10 have not been tested and found wanting — they have not yet
been tested.** That is a better position than the repo currently believes it is in.

---

## Status: fixes applied 2026-07-27

All findings below have been addressed and every simulation rerun. The findings are left as
written — they are the record of what was found. Outcomes:

| # | sim | fix | did the conclusion change? |
|---|---|---|---|
| 1 | sim06 | criterion 2 replaced with mass saturation | **No, but the null is now meaningful.** Criterion 2 goes from 4/160 to 130/160 satisfied; the crossing still does not fire, with criterion 1 (stability 0.849–0.893 vs 0.90) now the binding constraint. A near miss, not a categorical failure. |
| 2 | sim05 | alpha-invariant species, survival fraction, balanced seeding | **Yes — materially.** 0/6 → **2/6 coexistence**, mutual destruction 3/6 → 1/6. H10's primary evidence was largely an artifact. |
| 3 | sim02 | trace made strategy-dependent and bounded | **No.** Dynamic still converges harder (diversity 2 vs 4), but now on comparable fitness scales (1.44× rather than 3224×) instead of on a runaway accumulator. |
| 4 | sim03 | closure guard, catalyst scope, resilience sampling | **Refined.** Organizations 15/16 → 8/9 (all now correctly contain `E`); resilience reads 2→2→2 and 9→9→9 rather than a spurious 0→9. The structural (non-emergent) caveat is now documented in the README. |
| 5 | sim04 | stable seeded hashing, plus set-iteration order in five places | **Reproducibility restored** (verified by two full runs). Scientific conclusions unchanged. |
| 6 | sim01 | pheromone-blind control, `trail_concentration` metric | **Yes.** The blind control scores ~3× higher on `trail_cells` than sensing does — the old metric ran *opposite* to trail formation. Concentration separates them correctly (0.786 vs 0.270). Sensing also forages slightly *worse* than blind. |

Two further defects were found while fixing and are documented in place: sim05's mixed
population was padded only from organization A (a ~9:1 abundance handicap — this, not the
metric, was the main cause of the 0/6 result), and sim04 had four additional set-iteration
order dependencies beyond the `hash()` call.

Thresholds were deliberately **not** retuned after any fix, so that no detector was selected
for producing a preferred answer. Where a result is threshold-sensitive it is reported as such:
sim05's 2/6 is stable across survival thresholds 0.45–0.70, and sim06's criterion 1 misses by
≤0.05.

Downstream prose updated: `sim06/README.md`, `sim06/DESIGN.md` (session log),
`sim07/DESIGN.md` (which had inherited the wrong diagnosis), `sim05/README.md` and its
`visualize.html` (which read now-renamed keys), `sim03/README.md` (new Results section),
`sim02/README.md`, `sim01/README.md`, `concepts/alchemy-lambda-chemistry.md`, and
`hypotheses/hypotheses.md` (H10 refinement + summary table).

---

## 1. sim06 — the H7 null result cannot fire, by construction

**Severity: critical.** This is the load-bearing result in the repo and the basis for sim07.

### The detector is logically incapable of firing

`detect_crossing` (sim06.py:445) requires all three criteria to hold for 4 consecutive samples.
Criterion 2 carries a second clause (sim06.py:476):

```python
c2 = (r["mean_pheromone_over_structure"] >= phero_elev
      and r["deposits_this_window"] < early_avg)
```

But the model is Grassé positive feedback: deposit probability rises from `deposit_base=0.02` on
bare ground to ~0.87 on structure. Deposits *accelerate* as structure forms, so the deposit rate
falls below its early-run average only during warm-up.

| condition | c1 stability ≥0.90 | c2b deposits < early_avg | c3 constraint ≥0.60 |
|---|---:|---:|---:|
| baseline | 9/160 | **4/160** — samples 0, 1, 2, 14 | 154/160 |
| self_maintenance | 7/160 | **6/160** — samples 0–5 only | 0/160 |

Criterion 2 is satisfiable only *before* a structure exists — exactly when a crossing cannot have
occurred. No parameter setting fixes this; it is a contradiction between the detector and the
model's own dynamics. The reported null therefore says nothing about H7.

### The README's root-cause analysis is wrong on every number

The README attributes the failure to criteria 1 and 3. Neither claim survives contact with
`results.json` (baseline, samples 40+):

| README prose | actual |
|---|---|
| "stability hovers at 0.55–0.60" | 0.85–0.89 |
| "deposits on structure ≥0.60 also fails (~0.33–0.57)" | 0.70–0.79 — **c3 passes 154/160** |
| "~230 scattered tiny pillars" | 101 |
| "low compactness ≈ 0.08" | 0.113 |

The README also contradicts its own results table, which correctly lists
`mean_stability_last25 = 0.874`. Criterion 3 fails only for the *self-maintenance* condition, not
for baseline.

### The self-maintenance condition inverts the hypothesis

It is supposed to consolidate the structure. It does the opposite:

| metric | baseline | self_maintenance |
|---|---:|---:|
| components (`n_pillars`) | 101 | **252** |
| `deposit_on_structure_fraction` | 0.72 | **0.47** |
| `mean_pheromone_over_structure` | 0.99 | 15.58 |

Cause: `maintain_gain=0.3` drives pheromone to ~15.6 over structure, but the deposit response
`p = base + gain·φ/(1+φ)` saturates above φ≈1. Combined with diffusion (`PHEROMONE_DIFFUSE=0.10`),
deposit probability goes flat at ~0.87 *everywhere*, destroying the spatial contrast that
stigmergy depends on. The condition does not implement "the structure recruits builders to
maintain it" — it floods the grid with pheromone.

### This propagates into sim07

`sim07_transport_coupling/DESIGN.md` inherits the wrong diagnosis verbatim — "diffuse scatter,
~230 micro-pillars, stability ~0.55" — and specifies success as "stability ≥0.90, constraint
≥0.60", never mentioning criterion 2, the criterion that actually blocked sim06. **As specified,
sim07 will likely reproduce the same null for the same unaddressed reason.**

### Fix

Replace criterion 2's second clause with something a positive-feedback model can satisfy — e.g.
pheromone sustained over structure while *net material influx* declines, or structure persisting
through a builder-removal window. Then correct the README root-cause paragraph and revise the
sim07 DESIGN before implementing it.

### Reproduce

```python
import json
d = json.load(open('sim06_termite_mound/results.json'))
for cond in ('baseline', 'self_maintenance'):
    h = d[cond]['history']; n = len(h); n_early = max(1, n // 5)
    early_avg = sum(r['deposits_this_window'] for r in h[:n_early]) / n_early
    print(cond, 'c2b true at:',
          [i for i, r in enumerate(h) if r['deposits_this_window'] < early_avg])
```

---

## 2. sim05 — two independent bugs manufacture the 0/6 result

**Severity: critical.** H10 rests entirely on 0/6 L2 coexistence.

### Species identity is not alpha-invariant

`LExpr.__eq__` compares bound-variable *names* (sim05.py:55), so `λv1.v1 ≠ λv2.v2` — verified:
they compare unequal, hash differently, and form a 2-element set. Meanwhile `subst` mints a fresh
variable on every capture-avoiding rename (sim05.py:90), so the same normal form reached twice
usually compares unequal.

Consequences: species counts are inflated (446 / 300 / 246 / 930 "species ever"), and every set
intersection is deflated — pushing outcomes systematically toward `mutual_destruction` and away
from `coexistence`.

### The Jaccard threshold is unreachable for a third of the tests

Coexistence requires `sim_a > 0.15` **and** `sim_b > 0.15`, where similarity is Jaccard
`|A∩F| / |A∪F|` (sim05.py:321). Because the final population contains both organizations plus
novel species, Jaccard is bounded by the size ratio — regardless of dynamics:

| pair | \|A\| | \|B\| | \|F\| | max possible Jaccard_a with A **100% intact** |
|---|---:|---:|---:|---:|
| [1,3] | 4 | 37 | 32 | **0.125** — below threshold |
| [2,3] | 9 | 37 | 89 | **0.101** — below threshold |
| [0,3] | 18 | 37 | 90 | 0.200 — requires ~75% retention |

Two of six pairs could not have registered coexistence under any dynamics whatsoever.

### There is no L1 organization detection at all

The module docstring asks "do stable L1 organizations (autocatalytic sets of lambda expressions)
emerge?" The code never tests closure or self-maintenance — it counts unique surviving species.
There is also no perturbation test anywhere in sim05, although
`concepts/alchemy-lambda-chemistry.md` states L1 organizations are "stable, robust to
perturbation."

### Other defects

- `sim05.py:542` writes `results.json` to an absolute hardcoded home-directory path, against the
  documented convention of deriving paths from `os.path.dirname(os.path.abspath(__file__))`.
- `sim05.py:533` — `sim05_unbounded_confirmed` is a tautology. Operator precedence makes it
  `(len(...) > 510) or (all(...) == False)`; whenever any run has ≤510 species the second
  disjunct is True, so the flag is essentially always True regardless of the data.
- No `selftest`, no `sys.argv` dispatcher.

### Fix

Make `LExpr` alpha-invariant (de Bruijn indices, or canonical renaming before hashing), and
replace Jaccard with survival fraction `|A∩F| / |A|` — which asks the actual question, "what
fraction of organization A persisted?" Then rerun. Add a closure/self-maintenance test if the L1
claim is to be retained.

---

## 3. sim02 — the dynamic condition cannot reshape selection over strategies

**Severity: high.**

`get_fitness` adds the trace term for gene *i* **regardless of the agent's own `strategy[i]`**
(sim02.py:139), while only agents with `strategy[i] == 1` deposit (sim02.py:153). The bonus is
therefore identical for every strategy at a given cell and **cannot change the ranking of
strategies anywhere**. It is a location-crowding bonus, not niche construction — the shape of the
landscape over strategies is unchanged from the static condition.

It also swamps the base landscape entirely. Base contributions are `Uniform(0,1)`, so static
fitness is bounded in [0,1]; dynamic mean fitness reaches **2488**:

| generation | static | dynamic | ratio |
|---:|---:|---:|---:|
| 10 | 0.6150 | 7.31 | 11.9× |
| 100 | 0.7718 | 796.63 | 1032× |
| 4999 | 0.7718 | 2488.27 | **3224×** |

The base landscape contributes ~0.03% of the dynamic signal. The run terminates at
`n_clusters=1, max_cluster_size=1, diversity=1` — the entire population collapses onto a single
cell running a single strategy, via runaway self-reinforcement. "Both converge; dynamic converges
harder" is descriptively true, but the cause is an unbounded positive-feedback accumulator, not
H4.

Also note the static condition returns hard-coded zeros from `trace_clustering` and
`trace_persistence` (sim02.py:171, 210), so the comparison rows for those metrics are vacuous by
construction rather than empirical.

### Fix

Make the trace term strategy-dependent (e.g. only apply the gene-*i* bonus when
`strategy[i] == 1`), and bound or normalize it so the two conditions remain on comparable
fitness scales.

---

## 4. sim03 — organizations are static, and the COT test is not COT

**Severity: high.**

`find_organizations()` (sim03.py:263) brute-forces all subsets of `self.resources` against
`self.reactions`. Neither collection ever changes after construction, so the result is identical
on every call. Verified across the full 3,000-generation run:

- `single_trace`: **15 organizations at every sampled generation**
- `multi_trace`: **16 organizations at every sampled generation**

"Do organizations emerge from reaction dynamics?" cannot be answered by this design — they are a
fixed combinatorial property of a hand-authored 7-resource network. Only *which* pre-existing
organizations are populated varies. "Converges by gen 1, stalls" is guaranteed a priori.

Three further defects in `check_organization` (sim03.py:234):

1. **Closure skips zero-input reactions.** The guard `if rxn.inputs and all(...)` (line 241)
   excludes the inflow reaction `∅ → E`. In COT, `∅ ⊆ S` holds for every subset, so that reaction
   applies universally and forces `E` into every organization. Subsets are being declared closed
   that are not.
2. **Self-maintenance ignores rates.** COT self-maintenance requires a positive flux vector
   yielding non-negative net production. The code checks only "if consumed, then also produced
   somewhere" — a purely qualitative proxy. A set can pass while being depleted.
3. **The catalyst discard corrupts the accumulator.** `consumed.discard(rxn.catalyst)` (line 255)
   mutates the *global* `consumed` set, so a later reaction that merely catalyzes X erases the
   record that an earlier reaction genuinely consumed X. The outcome is order-dependent.

### Fix

Either implement the flux-based self-maintenance condition properly, or restate what sim03
measures: the activity of a fixed organization lattice, not the emergence of one. Fix the closure
guard and move the catalyst discard inside the per-reaction scope regardless.

---

## 5. sim04 — results are not reproducible

**Severity: high.**

`_is_catalyst` (sim04.py:159) and `_catalyzes` (sim04.py:167) derive the catalysis structure from
`hash()` on tuples containing strings. Python randomizes string hashing per process, so the entire
catalysis map — the chemistry itself — differs on every invocation. Verified over three runs of
the identical expression:

```
hash(("abab", "catalyst")) % 1000  ->  992 / 410 / 696
```

The inline comment calls this "Deterministic pseudo-random based on hash"; it is not.
`self.rng = random.Random(seed)` is constructed at line 134 and never used for catalysis. The
committed `results.json` cannot be regenerated, so every sim04 finding is a single unreproducible
sample. This also directly violates the project's determinism rule.

### Fix

Draw catalysis from `self.rng` (or seed a dedicated `random.Random` per catalyst/reaction key).
Regenerate `results.json` and re-check the "exhausts space, stalls" conclusion.

---

## 6. sim01 — no control condition, and the metric measures coverage

**Severity: medium.**

`count_trail_cells` (sim01.py:158) counts cells with pheromone > 1.0. A laden ant deposits 100 per
step with decay 0.02, so a visited cell stays above threshold for roughly 230 steps. The metric
therefore reports "cells visited by a laden ant recently" — it rises with mere coverage and cannot
distinguish a consolidated trail from ants wandering everywhere while carrying food.

There is also no pheromone-blind control condition anywhere in sim01. The decay sweep varies a
parameter but never disables the mechanism, so "trails form" is not established by what is
measured.

Additionally, `visualize.html` reimplements the model in JavaScript rather than fetching
`results.json` (sim01 is the only sim with no `results.json`), so the visualization can drift from
the Python silently.

### Fix

Add a control arm with pheromone sensing disabled, and add a trail-structure metric — e.g. path
concentration, or nest-to-food connectivity — alongside the coverage count.

---

## Convention compliance

Against the conventions documented in `CLAUDE.md` §3:

As found (2026-07-27, before fixes):

| sim | `selftest` | argv CLI | hardcoded path | global RNG seed | `results.json` |
|---|---|---|---|---|---|
| sim01 | ✗ | ✓ | — | ✗ `random.seed` | **missing** |
| sim02 | ✗ | ✗ | — | ✗ | ✓ |
| sim03 | ✗ | ✗ | — | ✗ | ✓ |
| sim04 | ✗ | ✗ | — | — (uses `hash`) | ✓ |
| sim05 | ✗ | ✗ | **✓ line 542** | ✗ | ✓ |
| sim06 | ✓ | ✓ | — | ✓ clean | ✓ |

After fixes — sim01 and sim05 gained a `selftest` and sim01 a `results.json`; sim05's hardcoded
path is gone. sim02/sim03/sim04 still lack a `selftest` and an argv dispatcher and still seed the
global RNG; those are convention gaps rather than correctness defects, and were left alone since
each is deterministic as written. sim04's determinism is now enforced by construction rather than
by accident.

sim06 is the only simulation that follows the documented conventions throughout — the
DESIGN.md-driven, Part-by-Part process demonstrably worked, and should be the template for
sim07 and beyond.

Two further notes:

- sim06's `selftest` re-seeds inside its loop (`termite_step(t2, f2, make_rng(456), params2)` at
  sim06.py:711), so all 100 iterations draw identical randomness. The assertions still pass but
  the test is weaker than it appears.
- `sim07_transport_coupling/` contains a `results.json` and `visualize.html` with no `sim07.py`.
  The JSON is an honest placeholder (`"status": "design_sketch"`, `metrics: null`), which is fine,
  but a committed visualization fetches it.

---

## Recommended order of work — all completed 2026-07-27

1. ~~Fix sim06's criterion 2 before implementing sim07.~~ **Done.** sim07's DESIGN has been
   corrected and now names all three criteria, flagging that continuous venting could break the
   saturation half of criterion 2.
2. ~~Rerun sim05's L2 classification with survival fraction and alpha-invariant identity.~~
   **Done**, plus the seeding-bias fix found in the process. Result moved 0/6 → 2/6.
3. ~~Seed sim04's catalysis deterministically.~~ **Done**, plus five set-ordering fixes;
   reproducibility verified by two full runs.
4. ~~Make sim02's trace strategy-dependent; add a pheromone-blind control to sim01.~~ **Done.**

Items 1 and 2 changed what the project believes about H7 and H10, as anticipated. Item 4 also
changed a claim: sim01's coverage metric turned out to run opposite to trail formation.

## What this leaves open

Not addressed, and each a judgement call rather than a defect:

- **sim03's self-maintenance is still a qualitative proxy**, not COT's flux condition, and its
  organizations remain a structural property of a hand-authored network. Making it real means
  either implementing the flux test or restating what sim03 claims to measure. The caveat is now
  documented in the code and README.
- **sim05 still never tests closure or self-maintenance**, so its "L1 organizations" are
  surviving species sets. The concept file and H10 now say so.
- **sim06's `structure_stability` is not invariant to `sample_every`** — a shorter sampling
  interval would raise the same structure's measured stability. Cross-run comparisons are only
  valid at equal sampling intervals; noted in the sim06 README limitations.
- **The pre-2026-07-27 sim06 parameter sweep has not been repeated.** It ran against the broken
  detector, so it establishes nothing about where the crossing might fire.
- **sim02 and sim03 still lack `selftest`/argv dispatchers**, and sim01's `visualize.html` is a
  JavaScript reimplementation rather than a consumer of `results.json`, so it can drift from the
  Python silently.
