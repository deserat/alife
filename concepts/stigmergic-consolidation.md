---
status: active
formed: "Session 8"
connected_to: "Stigmergy, multi-scale composition, H7, H11, autopoiesis, niche construction, computational irreducibility, multi-rate environment"
topic: "stigmergic consolidation and the negative-feedback gap"
key_findings: "The trace→actor crossing (H7) requires negative feedback through a channel that DOES NOT SATURATE. Two independent attempts to add it via the pheromone field — sim06's self-emission and sim07's transport venting — both fragmented the structure monotonically (66-109 to 219-297 components; 57 to 128 pillars), because the deposit response is flat above phi~1 so the manipulation cannot express contrast. Prescription: inhibit deposition directly (density cap, refractory period, directional bias) rather than manipulating the cue field. NOTE: this file's original anchor (sim06 produces diffuse scatter) was wrong — that null came from a detector that could not fire; corrected, sim06 is a near miss at stability 0.849-0.893 vs 0.90."
---

# Stigmergic Consolidation

**Status:** Active — formed Session 8
**Connected to:** Stigmergy, multi-scale composition, H7 (trace→actor crossing), autopoiesis, niche construction, computational irreducibility, multi-rate environment

## The Concept

Stigmergic systems coordinate via **positive feedback**: a trace stimulates more of
the same action (deposits attract deposits, pheromone trails recruit more ants).
This amplifies and exploits promising developments. The claim of this file is that
positive feedback alone does not reach a **consolidated actor**: without a
counterbalancing **negative feedback** — a mechanism by which a stronger trace
eventually *reduces* or *redirects* activity — nucleation is never pruned.

This is a theoretical claim (Heylighen) plus two directional results, not an
observation of scatter. *(2026-07-27: it originally read "positive feedback alone
produces diffuse scatter … the system nucleates everywhere and consolidates
nowhere", anchored on sim06 numbers that were wrong. sim06's baseline is 66–109
components at compactness 0.109–0.120 and misses the crossing by ≤0.05 — not a
scatter. What supports the claim now is that both attempts to add feedback made
fragmentation **worse**: sim06's self-maintenance, 219–297 components; sim07's
transport field, 57→128 pillars as `M_c` fell.)*

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
positive feedback runs to saturation or monoculture.

> **Correction (2026-07-27).** This sentence originally continued "— exactly what
> sim06 produced: ~230 scattered micro-pillars with no consolidation, high cell
> turnover, stability ~0.55 (well below the 0.90 H7 criterion)." Every one of those
> figures was wrong against sim06's own `results.json`. Baseline is **66–109
> components** at compactness 0.109–0.120, stability **0.849–0.893**, retention 0.98.
> See `../simulations/REVIEW.md` §1.

## sim06's Null Result (the empirical anchor — substantially retracted)

sim06 tested H7 with a minimal Grassé stigmergy model. The deposit rule
`p = DEPOSIT_BASE + DEPOSIT_GAIN · local/(1+local)` saturates at ~0.95 but **never
decreases** — there is no inhibition. That design observation stands.

**What does not stand is the empirical anchor.** sim06's crossing detector could not
fire at all: criterion 2 required the deposit rate to fall below its early-run
average, which Grassé positive feedback makes impossible once structure exists. It
held only at samples 0–5, before any structure had formed. The parameter sweep
(material_decay 0.005–0.4, deposit_base 0.005–0.05, phero_follow 0.6–0.95,
maintain_gain 0.1–0.5, reload_prob 0.15–0.3) ran against that detector and therefore
established nothing; it has not been repeated.

With criterion 2 corrected it passes 130/160, and the binding constraint is
**criterion 1 — stability 0.849–0.893 against a 0.90 threshold, a miss of ≤0.05**.
Criterion 3 *passes* 154/160 for baseline (`deposit_on_structure` 0.70–0.79). The
structure is neither diffuse nor unselective.

**The one result that does support this file's thesis** is the self-maintenance
reversal. Adding *more* positive feedback made things worse in exactly the predicted
direction: self-maintenance is more fragmented than baseline (219–297 components vs
66–109) and less selective (0.43–0.53, criterion 3 failing 0/160), because
`maintain_gain=0.3` saturates the deposit response flat at ~0.87 everywhere and
destroys the spatial contrast stigmergy depends on. sim07's null adds a second
data point: a structure-sourced scalar transport field also increased fragmentation
monotonically (57→128 pillars as `M_c` fell) rather than consolidating.

**Revised diagnosis:** the model has positive feedback plus weak decay and no
*consolidation* mechanism — nothing that makes strong pillars inhibit nearby
nucleation or redirect builders away from saturated regions. This remains a
plausible reading, but it is now an inference from a near miss and from two
failed negative-feedback attempts, not from an observed scatter. Self-maintenance
builds 66% more structure than baseline (1876 vs 1131 cells) — that number is
unaffected by the fix and still stands.

## The Saturation Result (2026-07-27 — the sharpened claim)

This result was promoted to a hypothesis in its own right: **[[hypotheses/H11]] — The Saturating
Channel Hypothesis**. This section is its concept-level treatment; H11 carries the formal
statement, the criticisms, and the test.

This is now the core of the concept, and it came out of the code review rather than from
reading. **Two independent attempts to supply the missing negative feedback both made the
structure less consolidated, monotonically:**

| attempt | mechanism | components | stability |
|---|---|---|---:|
| sim06 self-maintenance | structure re-emits pheromone (`maintain_gain=0.3`) | 66–109 → **219–297** | 0.849–0.893 → 0.746–0.802 |
| sim07 transport field | structure sources `T`, vents pheromone toward gaps | 57 → **128** as `M_c` falls | 0.876 → **0.739** |

The common cause is the **agents' response curve, not the feedback itself**. Both mechanisms
act by manipulating the pheromone field, and the deposit rule
`p = DEPOSIT_BASE + DEPOSIT_GAIN · φ/(1+φ)` is effectively flat above φ≈1. Once the field is
driven high anywhere — and self-emission or venting both drive it high — deposit probability
sits at ~0.87 across the entire grid. The manipulation intended to *create* spatial contrast
operates precisely in the region where contrast cannot be expressed. Adding energy to a
saturating channel removes selectivity rather than producing it.

**Refined prescription:** the crossing does not need "negative feedback" in the abstract — it
needs negative feedback **through a channel that does not saturate**. Concretely, act on
deposit probability or on geometry directly:

- a **density cap** — deposition suppressed where material already exceeds a threshold;
- a **refractory period** — a cell that has just received a pellet is briefly unavailable;
- **directional bias** — building preferentially along existing wall edges rather than onto
  their centres.

Each of these creates contrast that survives however high the cue field goes, because the
inhibition is not mediated by the cue field. All three are cheaper to test than directed
transport, and they discriminate the refined claim from the coarse one: if non-saturating
inhibition consolidates where field manipulation fragmented, the saturation account is right.

**Why this matters beyond sim06:** it suggests Heylighen's positive/negative feedback framing
carries a hidden assumption — that the two act on comparable channels. Where the response to
the trace saturates, negative feedback delivered through that trace is self-defeating. That is
a general claim about stigmergic systems, not a quirk of this model.

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

## The Specific Mechanism (Session 9 refinement — environmental physics coupling)

Session 9 identified the *specific* negative-feedback mechanism the crossing requires:
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
  structure-size separation (66% more cells) as a partial crossing. **This
  criticism was originally dismissed here on the grounds that "stability 0.55 is
  far from 0.90, and constraint 0.33 is far from 0.60 — the gap is large, not
  marginal." That dismissal was wrong and is retracted (2026-07-27):** baseline
  stability is 0.849–0.893 — a miss of ≤0.05 — and constraint is 0.70–0.79, which
  *passes* the 0.60 threshold 154/160 samples. The criticism is now the stronger
  reading. Thresholds were deliberately not retuned after the detector fix, so as
  not to select a detector that produces the preferred answer, but the result
  should be described as a near miss rather than a failure.
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
  evaporation is tuned. *(2026-07-27: this originally added "while sim06's decay was
  too weak relative to deposit rate" — an inference from the retracted scatter
  diagnosis. sim06's decay has not been shown to be mistuned.)*
- **sim06 (this project)**: null result, but a weak one — the detector could not
  fire (see the retraction above). Corrected: baseline is 66–109 components,
  stability 0.849–0.893, criterion 3 passing 154/160 — a near miss, not a scatter.
  The result that *does* support consolidation is directional: self-maintenance
  emission (more positive feedback) amplifies building by 66% while making the
  structure more fragmented (219–297 components) and less selective (0.43–0.53).
  See [sim06_termite_mound](https://alife.vancedubberly.com/sim06_termite_mound/visualize.html).

## Open Questions

- Which negative-feedback mechanism (saturation, transport, competition, state
  transition) is the *minimal* addition that produces the crossing? Each predicts
  a different morphology (few large pillars vs. channel networks vs.
  competing clusters).
- Is there a *phase transition* in the negative-feedback strength — below it, the
  sim06 regime; above it, consolidated actor? If so, where? **sim07 tested exactly
  this for a scalar transport field and found no transition** — the response was
  monotonic and in the wrong direction (stability 0.876→0.739, pillars 57→128 as
  `M_c` fell). Any remaining version of this question needs a different mechanism,
  not a different threshold.
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
