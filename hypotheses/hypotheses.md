---
title: "Hypotheses"
topic: "testable hypotheses for the multi-scale ALife composition project"
status: active
date: "2026-08-03"
session: 19
count: 11
active: [H1, H2, H3, H4, H5, H6, H7, H8, H9, H10, H11]
logs: ["logs/H1/", "logs/H2/", "logs/H3/", "logs/H4/", "logs/H5/", "logs/H6/", "logs/H7/", "logs/H8/", "logs/H9/", "logs/H10/", "logs/H11/"]
summary: "Current state of all 11 hypotheses (H1-H11): statement, status, evidence, and next test only. Full refinement history for each lives in hypotheses/logs/HN/ and is appended there, not here."
---

# Hypotheses

All hypotheses for the artificial life simulator project. Each hypothesis is testable through simulation. This file holds only the current statement, status, evidence, and next test for each — the session-by-session refinement history that produced that state lives in `logs/HN/`, linked from each section.

---

## H1: The Composition Hypothesis

**ALife simulations stall because they lack multi-scale composition.** Emergent structures at one scale must interact to produce qualitatively new phenomena at another scale, where actors and interaction rules are fundamentally different. Without this, simulations converge to simple stable states.

**Mechanism (Session 3):** the cross-scale interaction mechanism is stigmergy — agents modify their environment (stigmergic traces), and those modifications persist and constrain future agents.

**Support:** Smith & Bedau (1997) independently confirmed this via empirical study of Echo, identifying the missing CAS property as "robust, open-ended emergence of hierarchical, adaptive structures."

**Status:** Refined. Stands on the literature and the absence of a counterexample, not on our own simulations — sim03 was withdrawn as support (2026-07-27) since its organization lattice is static by construction; sim04 and sim05 have not tested it either.

**Test:** Build a simulation with explicit multi-scale composition mechanisms and compare to single-scale baseline. Measure: does the multi-scale version produce open-ended dynamics where the single-scale version stalls?

**Log:** [logs/H1/](logs/H1/)

---

## H2: The ANT Translation Hypothesis

**ANT's translation (Callon's four moments) provides the computational primitives for phase transitions between scales.** Problematization → interessement → enrollment → mobilization maps to: pattern formation → attraction → collective formation → collective action as one. When a cluster of actors reaches threshold interaction density, they undergo enrollment and mobilize as a new actor at a higher scale.

**Status:** Unchanged. Still untested.

**Log:** [logs/H2/](logs/H2/)

---

## H3: The Quasi-Object Resource Hypothesis

**Resources that transform through circulation (quasi-objects) produce richer dynamics than fixed-property resources.** A pheromone trail that strengthens/weaken with use is a quasi-object. A fixed-value food pellet is not.

**Status:** Strengthened — stigmergic traces are quasi-objects by definition (Session 3); Echo's trading resource offers partial support (Session 4), though not in the full Latourian sense.

**Test:** Compare simulations with fixed-value resources vs. quasi-object resources (resources that change properties as they circulate).

**Log:** [logs/H3/](logs/H3/)

---

## H4: The Dynamic Environment Hypothesis

**The environment must be a stigmergic medium — both perceivable and modifiable — and where a fitness landscape is used, that landscape must be dynamic: agents modify the landscape they adapt to.** Not just dynamic, but a participant in a stigmergic feedback loop. The environment stores information (trace), channels action (stimulation), and constrains future behavior. Static landscapes (NK model, Echo) cannot produce multi-scale composition; niche construction makes landscapes dynamic in biology, stigmergy in simulation.

**Status:** Refined (Session 4).

**Test:** Compare agents on static vs. dynamic fitness landscapes. The dynamic landscape is modified by agent behavior (stigmergic traces change the fitness function).

**Log:** [logs/H4/](logs/H4/)

---

## H5: The Autopoiesis Persistence Hypothesis

**For an emergent structure to persist as a new actor at a higher scale, it must be autopoietic — it must maintain the network that constitutes it.** Self-maintenance is the persistence condition. Without it, emergent structures are transient patterns, not new actors.

**Status:** Unchanged. Theoretical grounding from Maturana & Varela.

**Log:** [logs/H5/](logs/H5/)

---

## H6: The Multi-Scale Autopoiesis Hypothesis

**Complexification occurs when autopoietic systems interact stigmergically — through environmental modifications that persist and constrain.** The interaction network itself (mediated by stigmergic traces) becomes a candidate for higher-level autopoiesis.

**Status:** Strengthened — Smith & Bedau's proposed 8th CAS property ("the ability of emergent interacting components to create and flexibly maintain their own boundaries") is autopoiesis, identified independently from a different starting point (Session 4).

**Log:** [logs/H6/](logs/H6/)

---

## H7: The Trace→Actor Crossing Hypothesis

**Multi-scale composition occurs when accumulated stigmergic traces cross from passive coordination to autopoietic self-maintenance.** The crossing requires: (1) sufficient trace density, (2) self-reinforcing feedback (agents maintain the traces that constrain them), (3) the trace structure developing properties not reducible to individual traces.

**Current mechanism claim:** the crossing needs a non-saturating channel that *recruits* deposition as well as *limiting* it, not mere negative feedback through the cue field (see H11). The curvature channel (Facchini et al. 2020) is the strongest candidate: growth at convex tips recruits, biharmonic smoothing limits, and there is no saturating pheromone field in the model at all.

**Status:** Refined ×8. **The crossing now fires with a control arm.** Session 19 found criterion 2's mass-saturation gate (`|growth_rate| < 0.01`) was an unfalsifiable metric-ceiling bug — its threshold sat ~100× below the Poisson noise floor of a 150-termite deposit process, so no finite-population run could ever pass it. Corrected to a relative-slope plateau (`|slope(M)|/mean(M) < 0.001` over K=16 samples), the crossing fires in the curvature channel (tuned probe, non-saturating grid: cells 3123–5754/6400) at every d ∈ [0,4], and does NOT fire in the baseline-pheromone control (same detector, 0/3 — the saturating rule never elevates the pheromone cue enough). crossing_step decreases 1550 → 900 as d rises; n_pillars falls 12 → 1 (consolidation). Honest limitation: the crossing fires at d=0 (no smoothing), so the **recruit half** (curvature routing + mass plateau) drives the verdict; the **limit half** (d-smoothing) controls morphology but is not necessary for the crossing. The recruit-vs-limit isolation is unfinished.

**Evidence:**
- sim06: near miss — stability 0.849–0.893 vs a 0.90 threshold; self-maintenance fragments instead of consolidating (H11's first data point). Detector-bug corrected 2026-07-27.
- sim07: null — scalar transport fragments monotonically (stability 0.876→0.739); wrong sign for consolidation.
- sim08: partial — non-saturating density cap consolidates morphology (pillars 101→52) but stability doesn't rise; necessary, not sufficient.
- sim09: **crossing fires** (Session 19, corrected detector) — curvature channel crosses at every d in the tuned probe; baseline control does not. The d* sweep (100 combos) confirmed the old gate was the blocker, not the mechanism. Determinism verified.

**Next test:** isolate the recruit and limit halves — a recruit-only condition (curvature routing, d=0) vs a limit-only condition (d-smoothing, no curvature routing) — to determine whether the recruit half alone is sufficient or the limit half contributes to the crossing verdict. Then a spatially-targeted recovery metric to make the perturbation acid test decisive.

**Log:** [logs/H7/](logs/H7/)

---

## H8: The Computational Complexity Enables Open-Endedness Hypothesis (NEW — Session 4)

**Computational irreducibility at each scale is a NECESSARY condition for open-ended evolution.** On easy (computationally reducible) landscapes, evolution finds optima quickly and stops. On hard (computationally irreducible) landscapes, evolution cannot find optima and keeps searching — this IS open-endedness.

**Evidence:** Kaznatcheev (2019) proved that NK landscapes with K > 1 are PLS-complete — even local optima cannot be found in polynomial time. Wiser et al. (2013) showed E. coli fitness grows by power law (not exponential), consistent with hard landscape dynamics. Kaznatcheev argues this computational constraint ENABLES unbounded fitness growth.

**Implication for multi-scale composition:** Each scale in a multi-scale ALife simulation must have computationally irreducible dynamics. Cross-scale interactions must PRESERVE this irreducibility — if one scale becomes computationally reducible (e.g., agents find the optimal strategy), the system converges and stalls. The multi-scale structure must maintain irreducibility at all scales simultaneously.

**Test:** Compare simulations with reducible vs. irreducible dynamics at each scale. Measure: does the irreducible version produce open-ended dynamics where the reducible version converges?

**Log:** [logs/H8/](logs/H8/)

---

## H9: The Evolving Network Hypothesis (NEW — Session 5)

**A reaction network that generates new reactions (evolving network) can produce evolvable organizations where a fixed reaction network (same initial conditions, no new reactions) converges to a single static organization and stalls.** The key mechanism is the appearance of novel viable autocatalytic cores via rare uncatalyzed reactions, combined with compartmentalization that enables selection between cores.

**Evidence:**
- Vasas et al. (2010, PNAS): Autocatalytic sets (fixed networks) lack evolvability — they converge to a single attractor and cannot depart from the steady-state built into the dynamical equations.
- Vasas et al. (2012, Biology Direct): When rare uncatalyzed reactions are allowed, novel viable cores appear (5/460 runs). Multiple cores create multiple attractors with different growth rates, enabling natural selection. A 1% selective advantage shifts population composition.
- Our sim03: withdrawn as evidence. The organization lattice is static by construction (fixed hand-authored network, identical at every generation of every run), so it cannot demonstrate that fixed networks fail to evolve.
- Fontana & Buss (1994): Lambda calculus chemistry (AlChemy) produces "organizational transitions" — shifts between qualitatively different organizational regimes — when new molecules appear as products of reactions.

**Connection to H7:** The appearance of a novel viable core IS the trace→actor crossing. Existing resources are traces; the novel reaction produces a new self-maintaining set (organization/actor) from them.

**Connection to H8:** You cannot predict which novel cores will appear — you must simulate. The space of possible reactions is too large to enumerate, and viability depends on the entire network state.

**Status:** Untested (2026-07-27 correction) — sim03 and sim05 withdrawn as evidence, and sim04's comparative result corrected from "5 vs 4 cores" to 3-vs-3 (no difference; the original run used Python's non-deterministic `hash()`). Only sim04's finite-space exhaustion (510/510, both conditions) survives, and it doesn't test H9's claim. Vasas et al. (2012) remains the literature support.

**Test:** Compare fixed network (no new reactions, sim03-like) vs. evolving network (new reactions appear) with compartmentalization. Measure: does the evolving network discover new species, new organizations, and maintain between-compartment diversity where the fixed network converges? To be informative this needs an unbounded or much larger species space — in a 510-species world both arms exhaust it and the comparison is uninformative by construction.

**Log:** [logs/H9/](logs/H9/)

---

## H10: The Unbounded Space Insufficiency Hypothesis (NEW — Session 6)

**An unbounded molecule space (infinite possible species) is necessary but not sufficient for multi-scale composition.** Even when the species space is infinite (lambda calculus chemistry), single-scale organizations (L1) form but do not compose into multi-scale structures (L2) without explicit composition mechanisms.

**Evidence:**
- Our sim04 (finite space, 510 species): both fixed and evolving networks exhaust the finite space and stall. Novel reactions are redundant when catalyzed reactions already explore the space.
- Our sim05 (unbounded space, lambda calculus): stable species sets emerge from random initial conditions (**10–21** per run, mean 15.2), each run explores **112–162** unique species with mean pairwise overlap 0.061. The space is never exhausted. L2 composition (coexistence) = **2/6**; dominance 3/6, mutual destruction 1/6. sim05 never tests closure or self-maintenance, so these are surviving species sets rather than organizations in the COT sense.
- Mathis et al. (2024) systematic reanalysis of AlChemy: "stable organizations cannot be easily combined into higher order entities." L2 coexistence is rare across all tested pairs.
- Fontana & Buss (1994) original: L2 organizations identified but rare, requiring specific "glue" expressions that bridge L1s.

**Connection to H1:** Refines H1 — the stall is not due to finite species space (sim04) but persists with infinite space (sim05); the bottleneck is architectural (no composition mechanism), not spatial.

**Connection to H7:** The "glue" that enables L2 is analogous to the trace→actor crossing — it requires stigmergic traces, autopoietic boundaries, or explicit selection for composability. AlChemy has none of these.

**Connection to H8:** Each L1 run produces a unique, unpredictable organization, and whether two L1s compose is also unpredictable — computational irreducibility at both the organization-formation and composition levels.

**Three paths, same failure:** Echo (CAS theory), chemical organizations (origin-of-life chemistry), and AlChemy (computational theory) all fail at multi-scale composition, from three different starting points — evidence the composition problem is fundamental, though sim05's leg of this argument is weaker post-correction.

**Status:** Weakened (2026-07-27), not refuted. sim05 corrected from 0/6 to 2/6 L2 coexistence; composition is a minority outcome rather than categorically absent. Independent literature support (Mathis et al. 2024; Fontana & Buss 1994) is untouched.

**Test:** Build a simulation with explicit composition mechanisms (stigmergic bridges between organizations, autopoietic boundaries, selection for composability) and compare to AlChemy without these mechanisms. Measure: does the version with composition mechanisms produce L2 where the plain version fails?

**Log:** [logs/H10/](logs/H10/)

---

## H11: The Saturating Channel Hypothesis (NEW — 2026-07-27)

**Negative feedback delivered *through* a stigmergic trace is self-defeating wherever the agents' response to that trace saturates.** The manipulation intended to create spatial contrast operates in the region where contrast cannot be expressed, so adding feedback energy to a saturated channel removes selectivity instead of producing it. Consolidation therefore requires feedback through a channel that remains responsive and that *recruits* further building as well as *limiting* it — acting on the action (deposit probability, geometry) rather than on the cue the agents read.

**Origin:** this hypothesis came out of the 2026-07-27 construct-validity review rather than from reading. It was invisible beforehand because sim06's crossing detector could not fire, so the condition-to-condition comparison that reveals it was never examined.

**Evidence — four independent mechanisms, same direction (non-saturating channels consolidate; saturating ones fragment):**

| attempt | mechanism | result |
|---|---|---|
| sim06 self-maintenance | structure re-emits pheromone (saturating cue) | fragments: 66–109 → 219–297 components, stability 0.849–0.893 → 0.746–0.802 |
| sim07 transport field | structure vents pheromone toward gaps (saturating cue) | fragments: 57 → 128 pillars as `M_c` falls, stability 0.876 → 0.739 |
| sim08 density cap | hard gate on deposit action (non-saturating, limits only) | consolidates: pillars 101 → 52; crossing still doesn't fire |
| sim09 curvature channel | growth+smoothing on geometry (non-saturating, recruits AND limits) | consolidates in tuned probes: pillars 25 → 2 as `d` rises |

**Mechanism:** the deposit rule is `p = DEPOSIT_BASE + DEPOSIT_GAIN · φ/(1+φ)`, which is effectively flat above φ≈1. Self-emission and venting both drive the pheromone field high; deposit probability then sits at ~0.87 everywhere, destroying the spatial contrast stigmergy depends on. Non-saturating channels (a hard action gate, or curvature acting on geometry directly) don't share this failure mode.

**Connection to H7:** sharpens H7's prescription from "negative feedback" in the abstract to a specific channel property; sim08 and sim09 corroborate directionally but H7's crossing itself still hasn't fired.

**Connection to H4 (Dynamic Environment):** a saturated medium is a single-rate medium no matter how many processes write to it — the failure mode H4's "genuinely responsive environment" must avoid.

**Connection to the multi-rate environment (Vance's contribution):** it is not enough that different actors operate at different rates; the medium must stay responsive across the range those rates drive it through — saturation collapses a multi-rate medium into a single-rate one.

**Criticism / limitations:**
- Both data points in the original (sim06, sim07) came from the same model family (Grassé stigmergy on a grid) with the same response curve, so that pair's replication was weaker than two genuinely independent systems — sim08 and sim09 since strengthen this, sim09 especially (no pheromone field at all).
- The saturating form `φ/(1+φ)` was a modeling choice, not a measurement of real termites. A non-saturating deposit rule might be biologically wrong even if it consolidates better.
- **Literature check (2026-07-27):** H11 is a partial rediscovery, not fully novel. The ACO literature addresses the same underlying problem through two mechanisms:
  - **Evaporation** (`τ ← (1-ρ)τ`): Dorigo & Stützle's ACO book notes evaporation "plays the important function of bounding the maximum value achievable by pheromone trails" — i.e., preventing the saturation that H11 identifies. But evaporation acts on the cue field itself (lowering τ), which is precisely the channel H11 says is problematic. It works in ACO because ACO's response function does not saturate the way `φ/(1+φ)` does — ACO uses `τ^α · η^β` which is unbounded.
  - **MAX-MIN Ant System** (Stützle & Hoos, 2000): explicitly bounds τ ∈ [τ_min, τ_max] to prevent stagnation. This is the closest prior art — it recognizes that unbounded pheromone causes convergence problems and caps the field. But it caps the cue, not the action; H11's contribution is the claim that acting on deposit probability (the action) rather than on pheromone level (the cue) is the critical distinction.
  - **Novelty status:** the observation that saturation destroys spatial contrast is not in the ACO literature, because ACO does not use saturating response functions. The prescription (act on the action, not the cue) is novel within the stigmergy/ALife literature. H11 should be framed as extending the ACO insight to systems with saturating response functions, not as a wholly new discovery.
  - **Experiment confound:** the density-cap and curvature tests are both action-based AND non-saturating simultaneously, so they cannot fully distinguish "action-based" from "non-saturating" as the causal variable. A cleaner test would include a condition that is action-based but saturating (e.g. a deposit-probability cap that itself saturates) to isolate the two factors.

**Test:** run sim06 with negative feedback delivered through a non-saturating channel — a density cap, a refractory period, or directional bias along existing wall edges — and compare against both sim06's self-maintenance condition and sim07's transport condition. Prediction: non-saturating inhibition consolidates (components fall, stability rises) where field manipulation fragmented. If instead it also fragments, H11 is wrong and the problem lies deeper than the response curve.

**Status:** Directionally confirmed (4/4 mechanisms), now causally supported with a control arm (Session 19). The corrected detector fires the crossing in the curvature channel and not in the baseline-pheromone control (same detector, 0/3) — H11's channel distinction is the causal variable separating crossing from non-crossing, not just a directional correlate of morphology. The recruit half (non-saturating curvature routing) is load-bearing for the crossing; the limit half (d-smoothing) is load-bearing for morphology but not necessary for the verdict — so the "recruit as well as limit" refinement is half-supported.

**Log:** [logs/H11/](logs/H11/)

---

## Summary Table

| Hypothesis | Status | Evidence | Log |
|---|---|---|---|
| H1: Composition | Refined | Smith & Bedau (1997) independent confirmation; sim03 withdrawn as support (static lattice by construction) | [H1](logs/H1/) |
| H2: ANT Translation | Unchanged | Theoretical, untested | [H2](logs/H2/) |
| H3: Quasi-Object | Strengthened | Stigmergy literature support; Echo partial support | [H3](logs/H3/) |
| H4: Dynamic Environment | Refined | Fitness landscape criticism supports this | [H4](logs/H4/) |
| H5: Autopoiesis | Unchanged | Maturana & Varela grounding | [H5](logs/H5/) |
| H6: Multi-Scale Autopoiesis | Strengthened | Smith & Bedau 8th property = autopoiesis | [H6](logs/H6/) |
| H7: Trace→Actor Crossing | Refined ×8; crossing fires with a control arm | Corrected mass-saturation gate (was unfalsifiable); curvature channel crosses in tuned probe, baseline control does not; recruit half drives it | [H7](logs/H7/) |
| H8: Complexity Enables OEE | NEW | Kaznatcheev (2019), Wiser et al. (2013) | [H8](logs/H8/) |
| H9: Evolving Network | Untested (2026-07-27 correction) | Vasas et al. (2012) literature support; sim04's finite-space exhaustion survives but doesn't test the claim; sim03/sim05 withdrawn | [H9](logs/H9/) |
| H10: Unbounded Space Insufficiency | Weakened (2026-07-27) | sim05 corrected: 2/6 L2 coexistence (was 0/6 — artifact); Mathis et al. 2024, Fontana & Buss 1994 unaffected | [H10](logs/H10/) |
| H11: Saturating Channel | Directionally confirmed (4/4); causal with control arm | Corrected detector: curvature channel crosses, baseline control does not — channel distinction is causal; recruit half load-bearing, limit half not | [H11](logs/H11/) |
