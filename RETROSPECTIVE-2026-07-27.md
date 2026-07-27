# Retrospective — 2026-07-27 construct-validity review

**Audience: the nightly researcher agent.** Read this alongside `simulations/REVIEW.md`
(what each simulation actually measured) and `CLAUDE.md` §4 (the workflow it changed).
This document is the *why* and the *what next*.

---

## 1. What happened

A code review of all seven simulations asked one question: **does each simulation measure
what it claims to measure?** Five of six then-implemented sims did not. Every sim was fixed
and rerun, and the surrounding prose — daily reports, concepts, glossary, hypotheses,
synthesis — was corrected to match.

Three headline results moved and one reversed:

| result | before | after |
|---|---|---|
| sim05 L2 coexistence (H10's primary evidence) | 0/6 | **2/6** |
| sim06 crossing detector (H7's primary evidence) | "null across a wide sweep" | **detector could never fire**; corrected, a near miss — stability 0.849–0.893 vs a 0.90 threshold |
| sim01 trail formation | "optimal decay window 0.01–0.05" | metric ran **opposite** to trail formation; no window exists |
| sim04 evolving vs fixed networks | "5 vs 4 cores — modest improvement" | **3 vs 3 — no difference**; prior run was not reproducible at all |

One new hypothesis came out of it — **H11, the Saturating Channel Hypothesis** — which is
better evidence for H7's mechanism than the claim it replaced.

---

## 2. The mistakes, grouped by root cause

These are patterns, not incidents. Each one produced multiple downstream errors.

### 2.1 Detectors that can only return one answer

sim06's crossing detector required the deposit rate to fall **below its early-run average**.
Under Grassé positive feedback the deposit rate rises as structure forms, so that clause held
only at samples 0–5 — before any structure existed. The detector was mathematically incapable
of firing. Two full sessions of research were spent explaining a null that contained no
information.

**This is the single most expensive class of error in the project.** A null from an
unvalidated detector is not a finding; it is an absence of measurement, and it is worse than
no result because it reads as evidence.

### 2.2 Metrics whose ceiling sits below the decision threshold

sim05 classified outcomes on Jaccard similarity against a 0.15 coexistence threshold. Because
the final population contains both organizations plus novel species, Jaccard is bounded by the
size ratio — and for two of six pairs the arithmetic **maximum** was 0.125 and 0.101. Those
tests could not have returned coexistence under any dynamics whatsoever.

### 2.3 No control arm

sim01 measured `trail_cells` and concluded trails form. With a pheromone-blind control added,
the blind ants scored **2582 against sensing's 917** — the metric runs opposite to the thing it
names. Without a control there was no way to distinguish trail formation from ants covering
ground.

### 2.4 Non-determinism reported as a result

sim04 derived its catalysis map — which molecule catalyses which reaction, i.e. the chemistry
itself — from Python's builtin `hash()`, which is randomized per process. Every number it ever
reported was a single unrepeatable sample. Four additional set-iteration-order dependencies
compounded it.

### 2.5 Building on an unvalidated diagnosis

This is the most damaging pattern because it compounds. sim06's *stated* root cause ("diffuse
scatter, ~230 micro-pillars, stability 0.55") was wrong on every number against its own
`results.json`. Session 9 then built an entire mechanism hypothesis on that diagnosis, and
sim07's DESIGN inherited the wrong figures verbatim. Three sessions of work rested on numbers
that a single `grep` of the data file would have refuted.

### 2.6 Prose drifting from data

Eight daily reports, four concept files, the glossary and three hypotheses asserted figures
their own `results.json` contradicted. Nobody re-read the data after writing the prose.

### 2.7 Procedures that exist only in an agent's prompt

The mirror publish procedure lived nowhere on disk. Its working clone was an abandoned `/tmp`
directory that had drifted 11 commits behind origin, and the mirror had accumulated an orphaned
`simulations/sim01_pheromone_trails.py` from a superseded layout, because copy-based publishing
only ever added and overwrote, never deleted. Undocumented procedure decays silently.

### 2.8 Directory-wide staging

`git add artificial-life/` is directory-narrow, not change-narrow. It swept an unrelated review
pass into a commit titled "sim07 implementation", which then required a history rewrite.

---

## 3. Errors made *during* the review itself

Recorded because they are the same failure modes, and because a retrospective that only
indicts past work is not a retrospective.

- **A `pre-push` hook that passed its own test.** The first version compared against the
  remote's SHA — but the public mirror is a separate clone with independent history, so that
  SHA does not exist locally. `git diff` errored, the file list came back empty, and the push
  was allowed. It was caught only by running a real `--force --dry-run`. *A guard that has not
  been tested against the real adversarial case is not a guard.* It now fails closed.
- **A correction that contradicted itself.** The fix to `alchemy-lambda-chemistry.md` called
  the "246–930 species" figure an artifact in one paragraph and asserted it as fact eight lines
  later. Corrections need the same full-file check as original claims.
- **A caching delay misdiagnosed as a failed deploy.** The site served a stale copy for an hour
  under `max-age=3600`. The object generation on the response did not match the bucket's —
  comparing those two numbers first would have answered it immediately.
- **An abandoned scratch directory described as production tooling.** `/tmp/alife_gh` was
  called "the clone your publish workflow uses" before checking; the reflog showed it was
  created ad hoc by a prior session and referenced by nothing.
- **Weak reasoning offered in place of a checked one.** A step was skipped for a stated reason
  that turned out to be wrong when tested; the real reason for caution was different and
  better. Test first, then explain.

---

## 4. How to avoid this — concrete, checkable

Added to `CLAUDE.md` §4 step 6. Restated here with the reasoning:

1. **Positive control, every time.** Before trusting any detector, feed it a synthetic input
   that *should* trip it and assert that it does; then negate each criterion in turn and assert
   it withholds. `cmd_selftest` Part 5 in `sim06.py` is the working template. This one check
   would have caught §2.1 immediately.
2. **Compute your metric's ceiling.** For any threshold decision, ask what the metric's maximum
   value is given the data's shape. If the maximum can fall below the threshold, the test is
   not a test.
3. **Every claim of an effect needs a control arm.** "Trails form" requires ants that cannot
   read pheromone. "Evolving beats fixed" requires the fixed arm to be able to win.
4. **Determinism is a precondition, not a nicety.** Never use `hash()` on strings for anything
   that must reproduce; never iterate a `set` where the order feeds an RNG or an output. Verify
   by running twice and diffing, not by reading the code.
5. **Re-read the data file before writing the prose, and again after.** If a paragraph states a
   number, that number should have been read from `results.json` in the same sitting.
6. **Ask which direction each defect pushes.** If every bug you find biases toward the result
   you expected, treat the result as unproven no matter how clean it looks. All three sim05
   defects pushed away from coexistence. That pattern is itself evidence.
7. **A null result must name its binding constraint.** "It didn't fire" is not a finding.
   "Criterion 1 held 9/160, criterion 2 130/160, criterion 3 154/160" is. Per-criterion pass
   rates make an unfalsifiable detector obvious at a glance.
8. **Write procedures to disk.** If a step exists only in a prompt, it will drift.

---

## 5. How this should redirect the research

### 5.1 The evidence base is thinner than recorded — say so in writing

The project's strongest claim has been that **three independent traditions converge** on
composition being hard: Echo (Smith & Bedau), COT/Vasas, and AlChemy (Mathis et al.).
That convergence is real **in the literature**. But our own simulations did not independently
reproduce it, and sim05 now mildly contradicts its strongest reading:

- sim03 was cited as confirming Vasas *through simulation*. It cannot — its organization
  lattice is fixed at construction and identical at every generation of every run.
- sim05 was cited as confirming Mathis et al. at 0/6. Corrected, it is 2/6.

**Stop citing our own sims as a third independent leg.** What sims 03–05 actually established
is narrower: a finite species space exhausts (sim04, 510/510), and fixed networks have static
organization lattices (sim03, true by construction).

### 5.2 H7 is open, not failed — and that changes priorities

The corrected sim06 misses the crossing by **≤0.05 on one criterion**, with criterion 3 passing
154/160. That is a near miss, not a categorical failure. The implication: the crossing may be
reachable with a far smaller change than the directed-transport machinery currently planned.

**Highest-value next step is not sim08.** It is repeating sim06's Part-8 parameter sweep against
the working detector (queued-topics #54). The original sweep ran against a detector that could
not fire, so the claim "no regime produces the crossing" is unsupported in either direction —
and a crossing regime may already lie inside the space that was swept.

### 5.3 H11 gives a cheaper experiment than sim08

Two independent attempts at negative feedback both *increased* fragmentation — sim06's
self-emission (66–109 → 219–297 components) and sim07's transport venting (57 → 128 pillars) —
because both acted through a cue field whose deposit response saturates above φ≈1.

The refined prescription is negative feedback through a **non-saturating channel**: a density
cap, a refractory period, or directional bias acting on deposit probability directly. This is
substantially cheaper than directed transport and it discriminates H11 from the coarse
"needs negative feedback" claim (queued-topics #53).

**Before claiming novelty for H11, do a literature pass.** Ant Colony Optimization tunes
evaporation against exactly this pressure, and MAX-MIN Ant System bounds pheromone explicitly.
H11 may be a rediscovery, and finding that out is cheap.

### 5.4 The most informative question in the repo is now a pure analysis

sim05's 2/6 coexistence creates a **within-experiment contrast that did not exist at 0/6**:
what distinguishes the two pairs that coexisted from the four that did not? Organization size?
Structural overlap? Specific "glue" expressions of the kind Fontana & Buss describe? This needs
no new code — only analysis of the committed `results.json` (queued-topics #52). If size
predicts it, that is a very different story from glue, and it bears directly on H10.

### 5.5 H9 needs a different experiment entirely

H9 now has **no supporting simulation evidence in this repo** — its one positive measurement
(sim04's "5 vs 4 cores") was retracted. Worse, its stated test cannot be informative as
designed: in a 510-species space that both arms exhaust, fixed-vs-evolving is uninformative by
construction. Testing H9 requires an unbounded or much larger species space.

### 5.6 Treat sim05's "L1 organizations" as unvalidated

sim05 reports surviving species sets and calls them L1 organizations, drawing an analogy to
COT's closure + self-maintenance. It tests neither property. Either implement the test — sim03
has a structural version already — or restate what sim05 measures. The L1/L2 framing is what
connects sim05 to H10 and to the COT literature, so this is load-bearing (queued-topics #56).

---

## 6. Suggested order of work

1. **#52** — what distinguishes sim05's coexisting pairs. Pure analysis, no new code, tests H10.
2. **#54** — repeat sim06's sweep against the working detector. Cheap; may settle H7 for this model.
3. **#53** — non-saturating inhibition. The direct test of H11, cheaper than sim08.
4. Literature pass on H11 vs ACO pheromone bounding, before publishing it as novel.
5. Only then sim08 (directed / externally-driven transport).

The first three are all cheaper than what was previously queued as top priority, and each one
tests a hypothesis whose evidence base the review just weakened.
