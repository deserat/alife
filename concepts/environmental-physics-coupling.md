---
status: active
formed: "Session 9"
connected_to: "stigmergic consolidation, stigmergy, multi-scale composition, H7, H4, niche construction, multi-rate environment"
topic: "environmental physics coupling — the structure as a new dynamical degree of freedom"
key_findings: "The trace→actor crossing (H7) requires the accumulated structure to introduce physical transport dynamics absent at the deposit level. The Mahadevan group's termite mound model shows real mounds are ventilation structures whose own physics (diurnal thermal-oscillation-driven convection) redistributes the pheromone cues that guide building — the structure IS the feedback path. A 20-year lineage of stigmergic construction models (Deneubourg 1977 → Bonabeau 1997 → Ladley & Bullock 2004) all share the SAME limitation sim06 inherited: deposited material has no influence on agent movement, and pheromone diffusion is decoupled from structure. sim07 (Session 10) tested the minimal lumped version (structure-sourced scalar transport field T with mass threshold M_c) and found a NULL: no phase transition — scalar venting has the wrong sign for consolidation (it disperses the cue that recruits deposits), and the self-repair test shows repair tracks the deposit rule not T. The crossing requires DIRECTED transport (channel geometry) and/or an external multi-rate driver (H4), not just a structure-sourced scalar."
---

# Environmental Physics Coupling

**Status:** Active — formed Session 9
**Connected to:** [Stigmergic consolidation](stigmergic-consolidation.md), [stigmergy](stigmergy.md), [multi-scale composition](multi-scale-composition.md), H7 (trace→actor crossing), H4 (dynamic environment), [niche construction](stigmergy-vance-notes.md), [multi-rate environment](multi-rate-environment.md)

## The Concept

The accumulated stigmergic trace becomes an actor (the H7 crossing) only when it acquires
**dynamics that did not exist at the deposit level.** The cleanest formulation comes from the
Mahadevan group's termite mound work: a mound is not a passive accumulation of mud — it is a
**ventilation organ** whose own physical transport (airflow driven by diurnal temperature
oscillations) redistributes the very pheromone cues that guide further building. The
macro-structure's physics determines where the micro-scale signal goes. The structure is the
feedback path, not just the product.

This is the mechanism stigmergic-consolidation named as the missing ingredient: the
"environmental physics coupling" candidate for the negative feedback the positive stigmergic
loop needs in order to consolidate rather than scatter.

## The Mahadevan Mechanism (primary source)

King, Ocko & Mahadevan (PNAS 2015, "Termite mounds harness diurnal temperature oscillations
for ventilation") measured in-situ airflow in *Odontotermes obesus* mounds and found:

- The mound walls are **highly porous** (37–47% air by volume) with **tiny pores** (~5 μm).
  This makes the surface a "breathable windbreaker": gas diffuses easily along concentration
  gradients, but pressure-driven bulk flow across the wall is blocked.
- **Diurnal ambient temperature oscillations** drive cyclic convection: thin outer
  "flute" conduits heat rapidly during the day relative to the deeper central chimney,
  pushing air *up the flutes and down the chimney* in a closed convection cell; the
  converse at night. These cyclic flows flush CO₂ and ventilate the colony.
- The key architectural principle: **geometry + heterogeneous thermal mass + porosity**
  converts a *passive oscillation* (day/night temperature) into *useful work* (directed
  flow). No pump, no wind, no termite effort — the structure's own physics does the
  transport.

Ocko, Heyde & Mahadevan (PNAS 2019, "Morphogenesis of termite mounds") extended this to
morphogenesis: a model coupling **environmental physics to insect behavior** reproduces the
range of observed mound shapes from a minimal set of dimensionless parameters. The structure's
thermal/flow state feeds back onto building behavior — the mound is not just built, it
*builds itself* by steering its own construction cues through its own physics.

**The H7 reading:** the moment the accumulated mud becomes a ventilation structure, it has
gained a **new dynamical degree of freedom** (bulk advective transport of pheromone) that no
individual deposit possesses. Before that moment, the mud is a trace (passive sum of
deposits). After it, the mud is an actor (its transport dynamics reshape the cue field and
thereby recruit its own maintenance). The crossing is the onset of the structure's physics as
a causal layer.

## The 20-Year Lineage of the Same Limitation (criticism / context)

A striking finding from tonight's research: the specific limitation that produced sim06's
null result is **not new**. It is the persistent, unsolved limitation of the entire
stigmergic-construction modeling lineage:

1. **Deneubourg (1977)** — the original pillar-formation model. Positive feedback among
   termites, "active" building material, and cement pheromone. Weaknesses (per Linardou 2008,
   UCL): unrealistic spatial/temporal input of new termites, unnatural pheromone diffusion,
   and — critically — **"the already deposited building material had no influence on the
   termite movement."**

2. **Bonabeau et al. (1997, 1998)** — extended Deneubourg with queen pheromone template, wind,
   enforced termite flow; produced royal chambers and walkways. **Same limitation remained:**
   "the building material had still no influence on the movement of termites and the diffusion
   of the pheromones was again unrealistic." The 2D world could not form enclosed volumes.

3. **Theraulaz & Bonabeau (1995)** — first 3D agent-based model (wasp nests). Local rules,
   existing material as a constraint. But unrealistic building material form and "imprecise
   communication."

4. **Ladley & Bullock (2004, 2005); Ladley (2004)** — combined active (recently deposited,
   pheromone-emitting) and inactive material; 3D agent-based; produced domes and walkways. But
   wind was modeled as a one-directional pheromone flow, and structures were "abstract and
   artificial."

**The persistent gap across all four:** the structure's *physics* is never coupled back to the
agents. The deposit changes the cue field only through passive diffusion/decay. There is no
mechanism by which accumulated structure introduces a new transport/inhibition/competition
dynamics. **sim06 is the minimal modern instance of this same class** — and it produced the
same qualitative failure mode (diffuse scatter, no consolidation).

This reframes sim06's null result: it is not a failure of *our* model, it is a confirmation
that the field's long-standing minimal stigmergy models lack the coupling the crossing
requires. The Mahadevan model is the first to actually include it — and it is not an agent
model, it is a physics model.

## What the Field Still Doesn't Know (the 2025 state of the art)

Karibi-Botoye, Theraulaz, Muljadi, Demyanov & Singh (J R Soc Interface, 2025) review X-ray
tomography + flow-field simulation of mounds. Their open questions are directly H7-relevant:

- **"What processes occur at smaller scales in the mound that control larger-scale
  observations?"** — This is the trace→actor crossing question stated in the field's own
  language. Smaller-scale (deposit/pore) processes controlling larger-scale (ventilation,
  morphology) observations is exactly the multi-scale composition problem.
- Structure–function relationships across species: are there *general principles* (the H7
  prediction: the crossing is a general phase transition, not species-specific).
- They note the Eastgate Centre and other "termite-inspired" buildings are
  **"bio-mythological inspired"** — they mimic the *appearance* without replicating the
  *physics*, because the physics is incompletely understood. This is the engineering
  consequence of the missing coupling: without the transport dynamics, you build a
  sculpture, not a lung.

Their prescription — multiscale numerical modelling of pressure/velocity/permeability/heat/CO₂
transport validated against experiment — is the *full-physics* version of what sim07 needs only
in minimal lumped form.

## The Minimal Lumped Version (sim07 design hypothesis)

The Mahadevan mechanism need not require full PDEs. The essential ingredient for H7 is:
**the accumulated structure channels a transport field that redistributes the cue (pheromone)
away from where it's saturated and toward where it's absent.** A minimal lumped analog:

- Introduce a scalar **transport field** `T(x,y)` (airflow analog) on the grid.
- The structure (material density `M`) **sources** `T`: cells with `M` above a threshold
  generate a local transport potential (the "thermal mass / chimney" effect).
- `T` flows down its own gradient (a single diffusion/advection step), so high-`M` regions
  push the pheromone field `P` *along* the transport direction.
- Net effect: saturated pillars **vent** their own pheromone away, creating a negative
  feedback — deposition near a saturated pillar is *redirected* to its flanks/gaps. This is
  the consolidation mechanism sim06 lacked.

**State-transition form (Vance's termite-mound principle):** below a mass threshold `M_c`,
the structure is inert (passive accumulation, sim06 behavior). Above `M_c`, the structure
*activates* — it begins sourcing `T` and thereby reshaping the cue field. The crossing is
predicted to coincide with the first cells exceeding `M_c` and the onset of non-trivial `T`.
This makes the H7 phase transition operationally testable: sweep `M_c` and look for the
morphology transition (scatter → few consolidated pillars with vented flanks) and the
detector firing.

This is the "dynamic landscape made concrete" the synthesis has pointed toward (Session 4:
NK ↔ stigmergy; Vance's multi-rate environment): not a changing fitness function, but an
environment whose own physics becomes a new causal layer once organization crosses a
threshold.

## sim07 result (Session 10, 2026-07-27) — NULL

sim07 implemented exactly the minimal lumped prescription above and tested it. **Result: no
phase transition in `M_c`.** Sweeping `M_c` from ∞ (inert) to 0.5 (almost always active):

| M_c | pillars | stability | crossed |
|---|---|---|---|
| ∞ | 57 | 0.876 | no |
| 3.0 | 75 | 0.856 | no |
| 1.5 | 87 | 0.823 | no |
| 0.5 | 128 | 0.739 | no |

As `M_c` drops, stability **decreases** monotonically and pillars **fragment** (57 → 128) — the
opposite of consolidation. A `transport_coupling` sweep (0.0 → 0.80) confirms no value crosses.
The perturbation/self-repair test: both conditions recover (recovery ≈ 1.0), but repair is
driven by the deposit rule (termites wander back), NOT by `T` — the **circularity safeguard
fails**, confirming `T` is not the causal layer.

**Diagnosis — the wrong sign for consolidation:** the negative feedback is real, but its effect
fragments rather than consolidates. Venting pheromone *away* from saturated pillars disperses
the very cue that recruits deposits. A lumped linear advection of a scalar cue does NOT
reproduce the Mahadevan mechanism, where **directed** flow carries the cue **along** channels
to where building should *continue*. The minimal lumped version lost the directionality that
makes real mound transport consolidate. The structure-sourced scalar `T` is a caricature too
coarse to produce the crossing.

**What the null rules out and leaves open:** "structure sources a scalar transport field" is
insufficient. Two refinements remain: (1) **directed transport** — channel geometry that
carries cue to building fronts, not away from them; or (2) an **external multi-rate driver**
(H4) — the diurnal oscillation the structure rectifies into directed flow, which sim07's
lumped `T` lacks entirely. Candidate sim08 tests the external-oscillation path.

## Criticisms

- The Mahadevan model is a *physics* model, not an agent model — it assumes the
  building-response-to-cue coupling rather than deriving it. sim07 would need to implement
  both the physics AND the agent response, risking circularity (we build in the crossing we
  claim to detect). Mitigation: the crossing detector must measure *emergent* structure
  dynamics (non-reducibility, constraint on agents, self-repair) independent of the
  transport rule we imposed. **(Session 10: this risk was realized — sim07's perturbation
  test showed repair tracks the deposit rule, NOT `T`, so `T` is not the causal layer.)**
- The 20-year lineage shows the "material doesn't influence movement" limitation is
  *known*; the question is whether adding transport is *sufficient* or whether additional
  mechanisms (queen templates, tactile cues, larval pheromones — all omitted) are also
  required. sim07 tests the *minimal* transport addition; **(Session 10: a null result — the
  minimal scalar transport is NOT sufficient; the crossing needs directed and/or externally-
  driven transport, not just a venting scalar.)**
- "Bio-mythological" risk applies to us too: a lumped `T` field is a caricature of
  convection. If sim07 "crosses," we must be careful the crossing isn't an artifact of the
  imposed transport rule. The perturbation/self-repair test (does the structure recruit
  maintenance after damage *through* its transport, not through the deposit rule?) is the
  safeguard.
- Real mounds use *diurnal oscillation* (a multi-rate external driver) as the energy source
  for transport. sim07's `T` field has no external clock unless we add one. Connection to
  multi-rate environment (H4): the crossing may require not just structure-sourced transport
  but an external oscillation the structure can rectify. This is a candidate for sim08.

## Empirical Evidence

- **King, Ocko & Mahadevan (PNAS 2015)**: in-situ measurement of diurnal cyclic convection
  in *O. obesus* mounds; geometry + heterogeneous thermal mass + porosity converts passive
  temperature oscillation into directed ventilation. The structure does the transport.
  (softmath.seas.harvard.edu PDF; DOI 10.1073/pnas.1510334112)
- **Ocko, Heyde & Mahadevan (PNAS 2019)**: model coupling environmental physics to building
  behavior reproduces the range of observed mound shapes from minimal dimensionless
  parameters. (DOI 10.1073/pnas.1818759116; cited 75×)
- **Linardou (2008, UCL MSc thesis)**: documents the persistent limitation across
  Deneubourg → Bonabeau → Ladley that deposited material has no influence on agent
  movement and pheromone diffusion is decoupled from structure. (discovery.ucl.ac.uk/14632)
- **Karibi-Botoye, Theraulaz et al. (J R Soc Interface 2025)**: review identifying the
  open question "what processes occur at smaller scales that control larger-scale
  observations" — the H7 question in field language — and the "bio-mythological" gap.
  (DOI 10.1098/rsif.2025.0263)
- **Heylighen (Cognitive Systems Research 2016)**: positive + negative feedback as the
  signature of complex stigmergic systems; the termite pillar as the paradigmatic positive
  feedback case. (DOI 10.1016/j.cogsys.2015.12.002)
- **sim06 (this project)**: null result — positive-feedback-only stigmergy produces diffuse
  scatter, no crossing. Confirms the lineage limitation in a minimal modern model.
- **sim07 (this project, Session 10)**: null result — a structure-sourced *scalar* transport
  field with mass threshold `M_c` does NOT produce a phase transition. Sweeping `M_c` from inert
  to fully active monotonically *decreases* stability (0.876 → 0.739) and *fragments* pillars
  (57 → 128); the crossing detector never fires; the perturbation/self-repair test shows repair
  tracks the deposit rule, not `T`. Diagnosis: scalar venting has the wrong sign for
  consolidation — it disperses the cue that recruits deposits. Rules out "structure sources a
  scalar transport field" as sufficient; leaves directed transport and/or an external
  multi-rate driver (H4) as the remaining candidates.
- **No empirical study** was found that directly tests whether adding environmental physics
  coupling to a stigmergic agent model produces a trace→actor crossing. This is the open
  gap sim07 is designed to fill.

## Open Questions

- Is the structure-sourced transport field *sufficient* for the crossing, or is an external
  oscillation (diurnal driver) also required (the multi-rate-environment link, H4)?
- Does the crossing coincide with the state-transition threshold `M_c` (inert → active), and
  is there a sharp phase transition in `M_c`? This would make H7 operationally a phase
  transition.
- Can the crossing be detected *independently* of the imposed transport rule (the
  circularity concern), via self-repair after perturbation?
- Does the consolidated morphology (few large vented pillars) match the Mahadevan
  morphospace, or does the lumped model produce a different morphology? A match would be
  cross-validation; a mismatch flags the lumped model as insufficient.

## Cross-References

- [[concepts/stigmergic-consolidation]] — names the negative-feedback gap; this concept
  supplies the specific mechanism (environmental physics coupling) for it
- [[concepts/stigmergy]] — the base mechanism; Heylighen's positive/negative feedback
  framing
- [[concepts/multi-scale-composition]] — the crossing is the composition event
- [[concepts/multi-rate-environment]] — the diurnal oscillation as the external energy
  source for transport; candidate sim08 extension
- [[concepts/stigmergy-vance-notes]] — Vance's inert→active substrate state transition
- [[hypotheses/H7]] — refined: crossing = onset of structure's own physics as causal layer
- [[hypotheses/H4]] — the dynamic environment, now made concrete as physics-coupled
- King, Ocko & Mahadevan (2015) PNAS; Ocko, Heyde & Mahadevan (2019) PNAS; Linardou (2008);
  Karibi-Botoye et al. (2025) J R Soc Interface; Heylighen (2016)
