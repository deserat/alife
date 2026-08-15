---
title: "Hypotheses"
topic: "testable hypotheses for the multi-scale ALife composition project"
status: active
date: "2026-08-15"
session: 31
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

**Status:** Refined (Session 31). The decoupled boundary sweep (Session 31) finds the binary gate (fixed suppression) is more stable than the gradient gate (proportional suppression) at the same max gain: stable composition 0/4→2/4 at g=0.5, 2/4→4/4 at g=0.9. But it produces less L2 formation (4/4→2/4 at g=0.5). Persistence (stability) and formation (L2 crossing) respond to different properties of the suppression curve: persistence needs full strength; formation needs wide coverage. The 1-seed control is 0/4 at ALL gains in BOTH modes. Session 30: at g=0.5, H7=4/4 and L2=4/4 co-occur with 2/4 clean but 0/4 stable. Session 31: the decoupled mode achieves 2/4 stable at g=0.5 while preserving H7=4/4. Autopoiesis is necessary for persistence, but the persistence-formation trade-off is about curve shape, not just gain magnitude.

**Log:** [logs/H5/](logs/H5/)

---

## H6: The Multi-Scale Autopoiesis Hypothesis

**Complexification occurs when autopoietic systems interact stigmergically — through environmental modifications that persist and constrain.** The interaction network itself (mediated by stigmergic traces) becomes a candidate for higher-level autopoiesis.

**Status:** Refined (Session 31). Structural decoupling of boundary strength from co-presence magnitude (Session 31) strengthens the persistence wire (stability 0/4→2/4 at g=0.5) while keeping the specificity wire (1-seed 0/4 at ALL gains in BOTH modes). But it weakens formation (L2 4/4→2/4 at g=0.5) — the persistence and formation wires need different curve shapes. A new axis: gradient vs binary suppression. Session 30: the two wires can partially decouple at intermediate gains (g=0.5: H7=4/4, L2=4/4, clean=2/4). Session 31: structural decoupling confirms the specificity wire is independent of the suppression curve, but the persistence-formation trade-off persists in a new form.

**Log:** [logs/H6/](logs/H6/)

---

## H7: The Trace→Actor Crossing Hypothesis

**Multi-scale composition occurs when accumulated stigmergic traces cross from passive coordination to autopoietic self-maintenance.** The crossing requires: (1) sufficient trace density, (2) self-reinforcing feedback (agents maintain the traces that constrain them), (3) the trace structure developing properties not reducible to individual traces.

**Current mechanism claim:** the crossing needs a non-saturating channel that *recruits* deposition as well as *limiting* it, not mere negative feedback through the cue field (see H11). The curvature channel (Facchini et al. 2020) is the strongest candidate: growth at convex tips recruits, biharmonic smoothing limits, and there is no saturating pheromone field in the model at all.

**Status:** Refined ×20. The decoupled boundary sweep (Session 31) finds H7 is unchanged between proportional and decoupled suppression modes (4/4 at g=0.3–0.7, 0/4 at g=0.9 in both). The suppression curve's SHAPE matters for stability, not H7: binary gates produce more stable composition (0/4→2/4 at g=0.5) but less L2 formation (4/4→2/4) than gradient gates at the same max gain. A new stable co-occurrence at decoupled g=0.7 seed=999 (H7=YES + coexist + stable). Session 30: at g=0.5, H7=4/4 and L2=4/4 co-occur with 2/4 clean but 0/4 stable. Session 31: the decoupled mode achieves 2/4 stable at g=0.5 while preserving H7=4/4. The 1-seed control is 0/4 at ALL gains in BOTH modes. **The trade-off is not just strength vs growth; it is gradient vs binary suppression. H7 crossing is independent of the suppression curve shape.**

**Evidence:**
- sim06: near miss — stability 0.849–0.893 vs a 0.90 threshold; self-maintenance fragments instead of consolidating (H11's first data point). Detector-bug corrected 2026-07-27. Session 22: the saturating cue (as-built) crosses 16/16 stable without SM; the non-saturating cue crosses 0/16 stable without SM — cue-family reversal.
- sim07: null — scalar transport fragments monotonically (stability 0.876→0.739); wrong sign for consolidation.
- sim08: partial — non-saturating density cap consolidates morphology (pillars 101→52) but stability doesn't rise; necessary, not sufficient.
- sim09: **crossing fires** (Session 19, corrected detector) — curvature channel crosses at every d in the tuned probe; baseline control does not. Session 20: recruit half isolated as load-bearing + almost-sufficient; limit half as stability amplifier. Session 21: action-based property isolated as primary; non-saturating as secondary stability contributor (within action family). Session 23: φ_sat probe confirms the action/linear condition is saturated (max_curv 2.55 > c_sat 1.165, clamp_frac 1.0%) but still crosses — the routing decision preserves spatial contrast. Session 24: spatially-targeted recovery metric (patch_recovery) with mirror-patch control arm shows no targeted scar repair — targeted_repair (patch − mirror) is negative in all conditions; the crossing is a stability claim, not a self-repair claim. Session 25: the crossing does not compose — sim10's L2 test shows 15/16 two-seed runs merge at the crossing regime; the non-saturating glue composes no better than the saturating control. **Session 26: the long-range inhibitor (Turing lateral inhibition) is a weak positive — sim11 shows 2/4 clean coexistence at g=0.9 (up from 0/4), but 2/4 fragment; stable_l2 0/4 at all gains; h7 survives inhibition (4/4).** **Session 27: the autopoietic boundary (memory + growth/decay) is more stable but less specific — sim12 shows stable 4/4 (vs 1/4 passive), survives a 50% perturbation (B retains 91%), but 1-seed control 2/4; clean 2/4 = same as passive; h7=4/4.** **Session 28: direct-material co-presence (sim13) eliminates the torus leak (initial 1-seed co-presence <1% of 2-seed) but the 1-seed control still fires 1/4 — agent wander, not the torus leak, causes false boundaries. A radius sweep (8-30) reveals a breadth-specificity dimension: small → merges, medium → false positives, large → fragmentation. Clean 1/4 (worse than sim12's 2/4). l2_crossed=4/4 but l2_outcome=coexist only 1/4 — a new "fragmented" outcome. h7=4/4.** **Session 29: ID-tagged agents (sim14) break the false-positive mechanism — 1-seed control is 0/4 on ALL metrics (l2=0/4, coexist=0/4, stable=0/4, B_max=0.0). Clean composition 2/4 (matching shadow/passive). But the stronger boundary suppresses H7 crossing (0/4 — first time crossing lost across all seeds). The crossing and composition are in tension: the boundary that enables composition kills the crossing.** **Session 30: the inh_gain sweep (5 gains × 4 seeds) finds the trade-off is partially breakable — at g=0.5, H7=4/4 and L2=4/4 co-occur with 2/4 clean composition; at g=0.3, one seed achieves stable composition WITH H7 crossing. But stable composition (2/4 at g=0.9) comes at the cost of H7 suppression (0/4). The 1-seed control is 0/4 at ALL gains. The tension is between crossing and *stable* composition, not crossing and composition per se.** Determinism verified.

**Next test:** Decouple boundary strength from co-presence precision (queued-topic #92) — a boundary whose suppression is a fixed constant, not proportional to B_norm. Also: agent movement restriction (queued-topic #93) to test whether deposit tagging alone suffices. Also: the Singh et al. EOD stigmergic medium (#74) and a later perturbation after true mass plateau (#76).

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

**Status:** Strengthened (Session 31). The decoupled boundary sweep (Session 31) tests decoupling boundary strength from co-presence precision: binary gate (fixed suppression) vs gradient gate (proportional suppression). Result: binary gates produce more stable composition (0/4→2/4 at g=0.5, 2/4→4/4 at g=0.9) but less L2 formation (4/4→2/4 at g=0.5). The trade-off is not just strength vs growth but gradient vs binary suppression. A new stable co-occurrence at decoupled g=0.7 seed=999 (H7=YES + coexist + stable). The 1-seed control is 0/4 at ALL gains in BOTH modes. The composition problem persists across nine mechanisms (adding decoupled boundary to the eight from Session 30). **The missing ingredient is not just decoupling strength from growth — it is a boundary whose curve shape provides both wide coverage (formation) and full strength (persistence).**

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

**Status:** Directionally confirmed (4/4), causally supported with a control arm, mechanism-decomposed, confound-resolved, 2×2-complete (Session 22), and the φ_sat predictor falsified as a unifying diagnostic (Session 23). The corrected detector fires the crossing in the curvature channel and not in the baseline-pheromone control (same detector, 0/3) — H11's channel distinction is the causal variable separating crossing from non-crossing. Session 20's 2×2 factorial isolated the halves: recruit = necessary + almost-sufficient; limit = stability amplifier. Session 21's saturating-action control resolved the action-based vs non-saturating confound: action-based routing is primary; non-saturating is a secondary stability amplifier **in the action family**. Session 22's cue-based non-saturating control completed the 2×2 and found the non-saturating property **reverses sign** across families: in the cue family, the non-saturating cue crosses 0/16 stable without self-maintenance vs 16/16 for the saturating cue. **H11's "self-defeating saturating channel" framing is backwards for the cue family — the self-defeating channel is the non-saturating cue (deposit-probability clamping), not the saturating cue.** Session 23 tested the φ_sat predictor (the deposit-probability saturation threshold as a unifying diagnostic): it is 50% accurate — correct for the cue family but wrong for the action family (action/linear is saturated but still crosses stably). **Deposit-probability saturation is self-defeating only in cue-based channels, where the deposit probability IS the spatial signal; in action-based channels, the routing decision (which direction to move) preserves spatial contrast independently of the deposit probability.** The unifying diagnostic is whether spatial contrast in the routing input survives the response curve, which depends on channel architecture, not just the saturation threshold.

**Log:** [logs/H11/](logs/H11/)

---

## Summary Table

| Hypothesis | Status | Evidence | Log |
|---|---|---|---|
| H1: Composition | Refined | Smith & Bedau (1997) independent confirmation; sim03 withdrawn as support (static lattice by construction) | [H1](logs/H1/) |
| H2: ANT Translation | Unchanged | Theoretical, untested | [H2](logs/H2/) |
| H3: Quasi-Object | Strengthened | Stigmergy literature support; Echo partial support | [H3](logs/H3/) |
| H4: Dynamic Environment | Refined | Fitness landscape criticism supports this | [H4](logs/H4/) |
| H5: Autopoiesis | Refined (S31) | sim12: memory improves persistence (4/4 vs 1/4); sim14: ID tagging breaks false positives (0/4); inh_gain sweep: at g=0.5 H7=4/4+L2=4/4 co-occur but 0/4 stable; decoupled sweep: binary gate more stable (2/4 at g=0.5) but less formation (L2 2/4); persistence-formation trade-off is curve shape, not just gain | [H5](logs/H5/) |
| H6: Multi-Scale Autopoiesis | Refined (S31) | sim14: ID tagging provides specificity (1-seed 0/4, B=0); inh_gain sweep: two wires partially decouple at g=0.5; decoupled sweep: structural decoupling strengthens persistence wire (stability 0/4→2/4) but weakens formation (L2 4/4→2/4); persistence and formation need different curve shapes | [H6](logs/H6/) |
| H7: Trace→Actor Crossing | Refined ×20; decoupled sweep: H7 unchanged between proportional and decoupled modes; binary gate more stable but less formation; new stable co-occurrence at decoupled g=0.7 seed 999; 1-seed 0/4 at ALL gains in BOTH modes | Session 31 decoupled sweep: binary gate stable 2/4 at g=0.5 vs 0/4 proportional; L2 2/4 vs 4/4; H7 4/4 in both; g=0.7 seed 999 stable+H7+coexist; g=0.9 stable 4/4 vs 2/4 but H7 0/4 in both | [H7](logs/H7/) |
| H8: Complexity Enables OEE | NEW | Kaznatcheev (2019), Wiser et al. (2013) | [H8](logs/H8/) |
| H9: Evolving Network | Untested (2026-07-27 correction) | Vasas et al. (2012) literature support; sim04's finite-space exhaustion survives but doesn't test the claim; sim03/sim05 withdrawn | [H9](logs/H9/) |
| H10: Unbounded Space Insufficiency | Strengthened (Session 31) | sim14 ID-tagged: first structurally clean composition (1-seed 0/4, B=0); decoupled sweep: binary gate more stable (2/4→4/4 at g=0.9) but less formation; trade-off is gradient vs binary, not just strength vs growth; nine mechanisms tested | [H10](logs/H10/) |
| H11: Saturating Channel | Directionally confirmed (4/4); causal with control arm; 2×2-complete; φ_sat predictor family-specific (cue only) | Session 23 φ_sat probe: predictor 50% accurate — deposit-probability saturation self-defeating only in cue channels (deposit prob IS spatial signal); action channels preserve spatial contrast via routing | [H11](logs/H11/) |
