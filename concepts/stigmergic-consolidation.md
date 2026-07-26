---
status: active
formed: "Session 7"
connected_to: "Stigmergy, multi-scale composition, H7, autopoiesis, niche construction, computational irreducibility"
topic: "stigmergic consolidation and the negative-feedback gap"
key_findings: "Positive stigmergic feedback alone produces diffuse scatter, not consolidated actors. The trace→actor crossing (H7) requires negative feedback — saturation, depletion, or environmental physics coupling that channels and constrains the positive loop. sim06's null result confirms this: the model has only positive feedback + weak decay, so structure never consolidates."
---

# Stigmergic Consolidation

**Status:** Active — formed Session 7
**Connected to:** Stigmergy, multi-scale composition, H7 (trace→actor crossing), autopoiesis, niche construction, computational irreducibility, multi-rate environment

## The Concept

Stigmergic systems coordinate via **positive feedback**: a trace stimulates more of
the same action (deposits attract deposits, pheromone trails recruit more ants).
This amplifies and exploits promising developments. But positive feedback alone
produces **diffuse scatter**, not consolidated structure. Without a counterbalancing
**negative feedback** — a mechanism by which a stronger trace eventually *reduces*
or *redirects* activity — the system nucleates everywhere and consolidates nowhere.

This is the **negative-feedback gap**: the missing ingredient between stigmergic
coordination (within-scale) and the trace→actor crossing (H7, between-scale).

## The Mechanism (from Heylighen 2016 and sim06)

Heylighen's analysis of stigmergy identifies two feedback regimes:

1. **Positive (amplifying):** stronger trace → more activity → stronger trace. This
   *exploits* affordances — it concentrates effort where there's already signal.
   Termite deposits attract more deposits; ant pheromone recruits more ants.

2. **Negative (suppressing):** stronger trace → *less* activity, or activity
   *redirected*. This *controls* — it prevents runaway and enforces division of
   labor. Heylighen's market example: more buying → higher price → less buying
   (self-limiting). Price is a quantitative stigmergic trace that carries its own
   inhibition.

**Complex self-organization requires both** (Heylighen: "The combination of positive
and negative feedbacks is typical for complex systems"). Positive feedback
amplifies; negative feedback stabilizes and diversifies. Without negative feedback,
positive feedback runs to saturation or monoculture — exactly what sim06 produced:
~230 scattered micro-pillars with no consolidation, high cell turnover, stability
~0.55 (well below the 0.90 H7 criterion).

## sim06's Null Result (the empirical anchor)

sim06 tested H7 with a minimal Grassé stigmergy model. The deposit rule
`p = DEPOSIT_BASE + DEPOSIT_GAIN · local/(1+local)` saturates at ~0.95 but **never
decreases** — there is no inhibition. Decay and diffusion provide weak negative
feedback but are too slow relative to the deposit rate. An extensive parameter
sweep (material_decay 0.005–0.4, deposit_base 0.005–0.05, phero_follow 0.6–0.95,
maintain_gain 0.1–0.5, reload_prob 0.15–0.3) found **no regime where the crossing
fires**. Self-maintenance builds 66% more structure than baseline — the positive
loop works — but neither condition meets the three H7 criteria simultaneously.

**Diagnosis:** the model has positive feedback (deposits attract deposits) + weak
decay, but no **consolidation mechanism** — no process that makes strong pillars
*inhibit* nearby nucleation, redirect termites away from saturated regions, or
channel building through environmental physics. The structure spreads because
every cell with any pheromone is (nearly) equally attractive.

## Environmental Physics Coupling (the Mahadevan model)

The Harvard/Mahadevan termite mound model (Ocko, Heyde & Mahadevan, PNAS 2019)
shows the missing ingredient in real termites: the mound is not just a passive
accumulation — it's a **ventilation structure whose own physics channels the
pheromone cues that guide building.** External temperature variations drive
internal airflow, which redistributes pheromones and metabolic gases, which trigger
building where the mound is too warm/leaky. The structure *is* the feedback path:
the macro-structure's physics (airflow, thermal mass) determines where the micro-
scale signal (pheromone) goes. This is the trace→actor loop made concrete, but it
requires the environment to have **physical transport dynamics**, not just decay.

In ANT terms: the mound is an actant not because it's big, but because its physical
state (porosity, temperature gradients) causally reshapes the network of cues.
Without that physics, the "trace" never becomes an "actor" — it stays a passive
accumulation.

## What This Implies for the Crossing (H7 refinement)

H7's three operational criteria (persistence despite erosion, non-reducible
dynamics, constraint on agents) implicitly assume the structure has its own
dynamics that aren't reducible to individual deposits. In sim06, the structure
*has* no dynamics of its own — it's just a sum of deposits. Self-maintenance
emission adds one dynamics (re-emitting pheromone), but that's still just "more
positive feedback at the structure." The crossing needs the structure to do
something deposits don't do: **transport, channel, inhibit, or compete.**

This refines H7: the trace→actor crossing requires not just that the trace
recruits its own maintenance (sim06's loop), but that the **accumulated structure
introduces a new dynamical degree of freedom** — a process that did not exist at
the deposit level. Candidates:

- **Saturation/inhibition:** a cell above a density cap repels deposits (negative
  feedback). Forces consolidation into *few* large pillars rather than many small.
- **Environmental transport:** the structure channels a diffusive/advective field
  (airflow analog) that redistributes pheromone away from saturated regions and
  toward gaps — the Mahadevan mechanism.
- **Competition between structures:** multiple trace types or clusters compete for
  a finite resource (termites, material), so growth of one inhibits another.
- **State transition:** inert substrate becomes active only above a mass threshold
  (Vance's termite-mound principle) — the structure's *state* changes, unlocking
  new dynamics.

## The Specific Mechanism (Session 8 refinement — environmental physics coupling)

Session 8 identified the *specific* negative-feedback mechanism the crossing requires:
**environmental physics coupling** — the accumulated structure must introduce a transport
dynamics that redistributes the cue field. See
[[concepts/environmental-physics-coupling]]. The Mahadevan group's termite mound model
(King/Ocko/Mahadevan PNAS 2015; Ocko/Heyde/Mahadevan PNAS 2019) shows real mounds are
ventilation organs whose own physics (diurnal thermal convection) channels the pheromone
cues that guide building — the structure IS the feedback path.

A 20-year modeling lineage (Deneubourg 1977 → Bonabeau 1997 → Ladley & Bullock 2004) shares
exactly sim06's limitation: deposited material has no influence on agent movement; pheromone
diffusion is decoupled from structure. sim06's null result is therefore not a failure of our
model but confirmation of a known field-wide gap. The minimal lumped prescription for sim07:
a structure-sourced transport field that vents pheromone away from saturated regions
(negative feedback), with a mass threshold `M_c` below which the structure is inert (Vance's
inert→active state transition). The crossing is predicted to coincide with the onset of
non-trivial transport above `M_c`.

## Relevance to the Project Arc

sims 03–05 showed composition fails without an explicit mechanism (H10). sim05
nominated stigmergy as the glue. sim06 tested the simplest stigmergic
self-maintenance and found: **positive stigmergic feedback alone amplifies building
but does not consolidate — the trace→actor crossing does not occur.** The missing
ingredient is negative feedback / environmental physics coupling. This is a real,
mechanistic refinement, not a failure: it tells us what sim07 must add. The
"dynamic landscape" the synthesis has been pointing toward (Session 4: NK ↔
stigmergy; Vance's multi-rate environment) is not just "a changing fitness
function" — it's an environment whose own physics becomes a new dynamical layer
once organization crosses a threshold. The crossing is the moment the environment
gains a degree of freedom it didn't have before.

## Criticisms

- The negative-feedback framing is well-established in self-organization theory
  (Heylighen, Camazine et al.); the novelty is applying it as the *diagnosis* of
  H7's failure and the *prescription* for the crossing.
- It's possible H7's operational criteria (0.90 stability, 0.60 constraint) are
  too strict and a different operationalization would classify sim06's weak
  structure-size separation (66% more cells) as a partial crossing. But stability
  0.55 is far from 0.90, and constraint 0.33 is far from 0.60 — the gap is large,
  not marginal.
- Real termites have many more mechanisms (king/queen pheromones, larval cues,
  tactile contact) that the minimal model omits; the null result is specific to
  the *minimal* Grassé model, not to stigmergy in general.

## Empirical Evidence

- **Heylighen (2016)**: theoretical — positive + negative feedback as the signature
  of complex stigmergic systems. Market price as negative-feedback stigmergic trace.
- **Ocko, Heyde & Mahadevan (PNAS 2019)**: model coupling termite behavior to mound
  environmental physics (airflow, temperature) reproduces the range of observed
  mound morphologies. The structure's physics — not just its mass — drives
  morphogenesis. (No single DOI found in extraction; see seas.harvard.edu summary.)
- **Dorigo et al. (ACO literature)**: ant colony optimization requires pheromone
  *evaporation* (negative feedback) to avoid trail saturation; convergence depends
  on the evaporation rate. Directly analogous to sim06's decay — but ACO's
  evaporation is tuned, while sim06's decay was too weak relative to deposit rate.
- **sim06 (this project)**: null result. Positive-feedback-only stigmergy (deposit
  saturates at 0.95, never inhibits) produces ~230 scattered micro-pillars,
  stability 0.55, no crossing across a wide parameter sweep. Self-maintenance
  emission (more positive feedback) amplifies but does not consolidate.
  See [sim06_termite_mound](https://alife.vancedubberly.com/sim06_termite_mound/visualize.html).

## Open Questions

- Which negative-feedback mechanism (saturation, transport, competition, state
  transition) is the *minimal* addition that produces the crossing? Each predicts
  a different morphology (few large pillars vs. channel networks vs.
  competing clusters).
- Is there a *phase transition* in the negative-feedback strength — below it,
  diffuse scatter (sim06); above it, consolidated actor? If so, where?
- Does environmental physics coupling (the Mahadevan mechanism) require modeling
  actual transport (PDEs), or can a minimal lumped analog (e.g. "pheromone flows
  down a material gradient") capture the consolidation?
- How does this interact with computational irreducibility (H8)? If the structure's
  physics is a new dynamical layer, is the system *more* irreducible at the
  crossing — the moment the environment gains a degree of freedom?

## Cross-References

- [[concepts/stigmergy]] — the base mechanism; this concept refines what's missing
- [[concepts/multi-scale-composition]] — the crossing is the composition event
- [[concepts/autopoiesis]] — self-maintenance is necessary but sim06 shows it's
  not sufficient without consolidation
- [[concepts/multi-rate-environment]] — Vance's termite-mound principle: inert →
  active substrate state transition
- [[hypotheses/H7]] — the trace→actor crossing; sim06's null result refines it
- Heylighen (2016), "Stigmergy as a Universal Coordination Mechanism"
- Ocko, Heyde & Mahadevan (2019), PNAS — termite mound morphogenesis via
  environmental physics coupling
