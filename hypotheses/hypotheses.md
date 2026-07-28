# Hypotheses

All hypotheses for the artificial life simulator project. Each hypothesis is testable through simulation. Hypotheses are refined across sessions as new evidence accumulates.

---

## H1: The Composition Hypothesis

**ALife simulations stall because they lack multi-scale composition.** Emergent structures at one scale must interact to produce qualitatively new phenomena at another scale, where actors and interaction rules are fundamentally different. Without this, simulations converge to simple stable states.

**Refinement (Session 3):** The cross-scale interaction mechanism is stigmergy. Agents modify their environment (stigmergic traces), and those modifications persist and constrain future agents. The environment mediates between scales.

**Refinement (Session 4):** Smith & Bedau (1997) independently confirmed this hypothesis through empirical study of Echo. They found Echo lacks "the diversity of hierarchically organized adaptive aggregates" and proposed that the missing CAS property is "robust, open-ended emergence of hierarchical, adaptive structures."

**Refinement (2026-07-27, post code review — evidence base narrowed):** H1's substance is unchanged, but one of its supports is withdrawn. sim03 was cited as confirming that fixed networks stall; it cannot, because its organization lattice is fixed at construction and identical at every generation of every run (see `../simulations/REVIEW.md` §4). Smith & Bedau remains the external support, and it is strong. Our own simulations should now be described as **not yet having tested H1** rather than as confirming it: sim04 establishes only that a finite species space exhausts (510/510, unaffected by the fixes), and sim05 — once its measurement defects were corrected — shows composition succeeding in 2 of 6 pairs, which is mild evidence *against* the strongest reading of H1 rather than for it. The hypothesis stands on the literature and on the absence of any counterexample, not on our results.

**Test:** Build a simulation with explicit multi-scale composition mechanisms and compare to single-scale baseline. Measure: does the multi-scale version produce open-ended dynamics where the single-scale version stalls?

---

## H2: The ANT Translation Hypothesis

**ANT's translation (Callon's four moments) provides the computational primitives for phase transitions between scales.** Problematization → interessement → enrollment → mobilization maps to: pattern formation → attraction → collective formation → collective action as one. When a cluster of actors reaches threshold interaction density, they undergo enrollment and mobilize as a new actor at a higher scale.

**Status:** Unchanged. Still untested.

---

## H3: The Quasi-Object Resource Hypothesis

**Resources that transform through circulation (quasi-objects) produce richer dynamics than fixed-property resources.** A pheromone trail that strengthens/weaken with use is a quasi-object. A fixed-value food pellet is not.

**Refinement (Session 3):** Stigmergic traces are quasi-objects by definition — they are transformed by circulation. This provides independent support from the stigmergy literature.

**Support (Session 4):** Echo's trading resource behaves as a partial quasi-object — more copies of the traded resource in a genome change the population dynamics. But Echo's resources don't transform through circulation in the full Latourian sense.

**Test:** Compare simulations with fixed-value resources vs. quasi-object resources (resources that change properties as they circulate).

---

## H4: The Dynamic Environment Hypothesis

**The environment must be a stigmergic medium — both perceivable and modifiable.** Not just dynamic, but a participant in a stigmergic feedback loop. The environment stores information (trace), channels action (stimulation), and constrains future behavior.

**Refinement (Session 4):** The fitness landscape must be DYNAMIC — agents modify the landscape they're adapting to. Static landscapes (NK model, Echo) cannot produce multi-scale composition. Niche construction makes landscapes dynamic in biology; stigmergy makes them dynamic in simulation.

**Test:** Compare agents on static vs. dynamic fitness landscapes. The dynamic landscape is modified by agent behavior (stigmergic traces change the fitness function).

---

## H5: The Autopoiesis Persistence Hypothesis

**For an emergent structure to persist as a new actor at a higher scale, it must be autopoietic — it must maintain the network that constitutes it.** Self-maintenance is the persistence condition. Without it, emergent structures are transient patterns, not new actors.

**Status:** Unchanged. Theoretical grounding from Maturana & Varela.

---

## H6: The Multi-Scale Autopoiesis Hypothesis

**Complexification occurs when autopoietic systems interact stigmergically — through environmental modifications that persist and constrain.** The interaction network itself (mediated by stigmergic traces) becomes a candidate for higher-level autopoiesis.

**Refinement (Session 4):** Smith & Bedau's proposed 8th CAS property — "the ability of emergent interacting components to create and flexibly maintain their own boundaries" — is autopoiesis. They identified it independently from a different starting point (empirical study of Echo vs. our ANT/stigmergy path). This is strong corroboration.

---

## H7: The Trace→Actor Crossing Hypothesis

**Multi-scale composition occurs when accumulated stigmergic traces cross from passive coordination to autopoietic self-maintenance.** The crossing requires: (1) sufficient trace density, (2) self-reinforcing feedback (agents maintain the traces that constrain them), (3) the trace structure developing properties not reducible to individual traces.

**Refinement (Session 4):** This IS Smith & Bedau's 8th CAS property. Stigmergy provides the mechanism for "creating boundaries" (traces that accumulate). Autopoiesis provides the mechanism for "flexibly maintaining boundaries" (self-production). The crossing from trace to actor is the phase transition they identified but never implemented.

**Refinement (Session 8 — sim06 null result; REWRITTEN 2026-07-27 after code review):** sim06 implemented the trace→actor feedback loop (the structure re-emits the pheromone that recruits builders) and found it amplifies building — **66% more structure, 1876 vs 1131 cells, retention 0.98 vs 0.96** — but does not cross.

*The original Session 8 refinement is retracted, and this paragraph replaces it rather than being appended, because it stated false measurements rather than a superseded interpretation.* The crossing detector as it then stood **could not fire at all**: criterion 2 required the deposit rate to fall below its early-run average, which Grassé positive feedback makes impossible once structure exists (deposit probability rises from `deposit_base`=0.02 on bare ground to ~0.87 on structure). It was satisfied only at samples 0–5, before any structure had formed. The Session 8 null therefore carried **no evidential weight**, and the parameter sweep run against it establishes nothing. The figures previously reported here — "~230 scattered micro-pillars", stability ~0.55, constraint 0.33, compactness 0.08 — were wrong against sim06's own `results.json`.

With criterion 2 replaced by mass saturation (pheromone over structure ≥0.5 *and* |material_growth_rate| < 0.01), it now passes **130/160** samples (135/160 for self-maintenance). The crossing still does not fire, but the binding constraint is now **criterion 1: stability 0.849–0.893 (baseline), 0.746–0.802 (self-maintenance) against a 0.90 threshold — a miss of ≤0.05.** Criterion 3 *passes* 154/160 for baseline (`deposit_on_structure` 0.70–0.79). Baseline morphology is 66–109 connected components at compactness 0.109–0.120 — not a diffuse scatter.

One finding runs **opposite** to the hypothesis: the self-maintenance condition is *more* fragmented than baseline (219–297 components) and *less* selective (0.43–0.53, criterion 3 failing 0/160), because `maintain_gain=0.3` saturates the deposit response flat at ~0.87 everywhere and destroys the spatial contrast stigmergy depends on. More positive feedback actively worked against consolidation.

The inference that the crossing needs a **new dynamical degree of freedom** absent at the deposit level — environmental transport (Mahadevan), saturation/inhibition, competition, or a substrate state transition (Vance's termite-mound principle) — may still be correct, but it must now rest on the near-miss and on the self-maintenance reversal, not on the "diffuse scatter" characterization that motivated it. See [[concepts/stigmergic-consolidation]] and `../simulations/REVIEW.md` §1. Status: **H7 not refuted, and not strongly tested either** — sim06 leaves the crossing an open question rather than a demonstrated failure.

**Refinement (Session 9 — the specific mechanism identified):** The "new dynamical degree of
freedom" is now specified: **environmental physics coupling** — the accumulated structure must
introduce a *transport dynamics* that redistributes the cue (pheromone) field away from
saturated regions and toward gaps. The Mahadevan group's termite mound model (King/Ocko/
Mahadevan, PNAS 2015; Ocko/Heyde/Mahadevan, PNAS 2019) shows real mounds are ventilation
organs whose own physics (diurnal thermal convection) channels the very pheromone cues that
guide building — the structure IS the feedback path. A 20-year stigmergic-construction
modeling lineage (Deneubourg 1977 → Bonabeau 1997 → Ladley & Bullock 2004) all share sim06's
exact limitation (deposited material has no influence on agent movement; pheromone diffusion
decoupled from structure). *(Corrected 2026-07-27: this refinement originally added that
"sim06's null result is confirmation of a known field-wide gap, not a failure of our model."
That does not hold — sim06's null was in part a failure of our own detector, which could not
fire. The literature argument about the lineage is independent and stands on its own; the
sim06 leg of it does not.)* The minimal lumped prescription: a structure-sourced transport
field with a mass threshold `M_c` (inert → active state transition, Vance's principle) — below
`M_c`, the sim06 regime; above, consolidated actor. The crossing is predicted to be a
phase transition in `M_c`. See [[concepts/environmental-physics-coupling]]. Status: **H7
further refined, testable** — sim07 implements the transport field and tests the `M_c`
phase transition.

**Refinement (Session 10 — sim07 null result):** A structure-sourced *scalar* transport field
with a mass threshold `M_c` is **not sufficient** for the crossing. sim07 implemented exactly the
minimal lumped prescription above (T sourced above `M_c`, diffuses, vents pheromone from
saturated to gap regions) and swept `M_c` from inert to fully active. Result: no phase
transition. Stability *decreases* monotonically as `M_c` drops (0.876 → 0.739); pillars
*fragment* (57 → 128); the crossing detector never fires for any `M_c` or `transport_coupling`;
and the perturbation/self-repair test shows repair tracks the deposit rule, NOT `T` (the
circularity safeguard fails — `T` is not the causal layer). Diagnosis: the negative feedback
is real but its effect has the **wrong sign for consolidation** — venting pheromone away from
saturated pillars disperses the very cue that recruits deposits, fragmenting rather than
consolidating. A lumped linear advection of a scalar cue does not reproduce the Mahadevan
mechanism, where *directed* flow carries the cue *along* channels to where building should
continue. Two candidates remain: (1) **directed transport** (channel geometry that carries
cue to building fronts, not away from them — the directionality lost in the lumped scalar),
or (2) an **external multi-rate driver** (the diurnal oscillation, H4) the structure rectifies
into directed flow — the Mahadevan energy source sim07 omits (candidate sim08). Status:
**H7 refined again, not refuted** — the null specifies that the transport must be *directed*
(not a venting scalar) and/or *externally driven* (H4), not merely structure-sourced. See
[[concepts/environmental-physics-coupling]].

**Refinement (2026-07-27, post code review — the prescription sharpens: saturation, not absence of feedback):** Correcting sim06's detector removed H7's original evidence but surfaced better evidence in its place, pointing at a more specific mechanism.

**Two independent attempts to add the "missing" negative feedback both made consolidation worse, monotonically:**

| attempt | mechanism | components | stability |
|---|---|---|---:|
| sim06 self-maintenance | structure re-emits pheromone (`maintain_gain=0.3`) | 66–109 → **219–297** | 0.849–0.893 → 0.746–0.802 |
| sim07 transport field | structure sources `T`, vents pheromone to gaps | 57 → **128** as `M_c` falls | 0.876 → **0.739** |

Both act *through the pheromone field*, and the deposit response saturates: `p = base + gain·φ/(1+φ)` is flat above φ≈1, so once the field is driven high anywhere, deposit probability sits at ~0.87 **everywhere** and the spatial contrast stigmergy depends on is destroyed. Pushing more signal through a saturating channel does not create selectivity — it removes it.

This finding is now stated formally as **H11 (The Saturating Channel Hypothesis)**. So the Session 8/9 prescription ("the crossing needs negative feedback / a new dynamical degree of freedom") is too coarse. It has now been tried twice and fragmented twice. The refined claim: **the crossing needs negative feedback through a channel that does not saturate** — acting on deposit probability or on geometry directly (a density cap, a refractory period, directional bias along existing walls), rather than by manipulating the cue field the agents read. This is sharper and more falsifiable than the original, and it is testable more cheaply than directed transport.

Note what this does to the evidential picture: H7's mechanism claim is now supported by a *positive, replicated, directional* result (two mechanisms, same failure direction, same explanation) rather than by the "diffuse scatter" characterization it replaces — which was never observed. Status: **H7 not refuted, not strongly tested, and better specified than before.**

**Test:** Build a simulation where agents leave persistent traces, and observe whether traces cross from coordination to self-maintenance. Measure: does the trace structure develop its own dynamics? Does it resist perturbation (self-repair)? Does it constrain agent behavior in ways not derivable from individual traces? sim07 added a structure-sourced scalar transport field with threshold `M_c` and tested whether the crossing fires as a phase transition in `M_c` — it did not. Next, in increasing cost: (a) **non-saturating inhibition** — a density cap or refractory period acting directly on deposit probability, testing the refinement above; (b) *directed* transport (channel geometry); (c) an external oscillation (H4) the structure rectifies.

**Refinement (Session 13, 2026-07-28 — sim08 tests (a); non-saturating inhibition
necessary but not sufficient):** sim08 added a non-saturating density cap (a hard gate
on the deposit action, not a graded cue function) to sim06's Grassé model. The cap
**consolidates morphology** — pillars fall 101 → 52 as the cap tightens, and the
pheromone field is de-saturated (max 8.01 → 2.50) — confirming the direction of H11's
prescription: a non-saturating action-channel prunes nucleation where the saturating
cue-channel could not. **But the crossing does not fire** for any cap strength;
stability does not rise (0.874 → 0.775 at the tightest cap). The cap limits growth
without recruiting maintenance, so it corrects the fragmentation symptom (pillars)
but not the persistence symptom (stability). The crossing therefore needs a non-
saturating channel that **recruits** as well as limits — the curvature channel real
termites use (Calovi 2019: concavity → fill, each deposit extends the concavity)
does both; the density cap only limits. The boundary narrows again: (sim06) positive
feedback alone insufficient → (sim07) scalar cue-transport insufficient → (sim08)
non-saturating limitation insufficient → the crossing needs a non-saturating channel
that also feeds back positively into its own maintenance. Candidate next: a curvature/
deposition-edge rule. See [`concepts/non-saturating-channels.md`](../concepts/non-saturating-channels.md).

---

## H8: The Computational Complexity Enables Open-Endedness Hypothesis (NEW — Session 4)

**Computational irreducibility at each scale is a NECESSARY condition for open-ended evolution.** On easy (computationally reducible) landscapes, evolution finds optima quickly and stops. On hard (computationally irreducible) landscapes, evolution cannot find optima and keeps searching — this IS open-endedness.

**Evidence:** Kaznatcheev (2019) proved that NK landscapes with K > 1 are PLS-complete — even local optima cannot be found in polynomial time. Wiser et al. (2013) showed E. coli fitness grows by power law (not exponential), consistent with hard landscape dynamics. Kaznatcheev argues this computational constraint ENABLES unbounded fitness growth.

**Implication for multi-scale composition:** Each scale in a multi-scale ALife simulation must have computationally irreducible dynamics. Cross-scale interactions must PRESERVE this irreducibility — if one scale becomes computationally reducible (e.g., agents find the optimal strategy), the system converges and stalls. The multi-scale structure must maintain irreducibility at all scales simultaneously.

**Test:** Compare simulations with reducible vs. irreducible dynamics at each scale. Measure: does the irreducible version produce open-ended dynamics where the reducible version converges?

---

## H9: The Evolving Network Hypothesis (NEW — Session 5)

**A reaction network that generates new reactions (evolving network) can produce evolvable organizations where a fixed reaction network (same initial conditions, no new reactions) converges to a single static organization and stalls.** The key mechanism is the appearance of novel viable autocatalytic cores via rare uncatalyzed reactions, combined with compartmentalization that enables selection between cores.

**Evidence:**
- Vasas et al. (2010, PNAS): Autocatalytic sets (fixed networks) lack evolvability — they converge to a single attractor and cannot depart from the steady-state built into the dynamical equations.
- Vasas et al. (2012, Biology Direct): When rare uncatalyzed reactions are allowed, novel viable cores appear (5/460 runs). Multiple cores create multiple attractors with different growth rates, enabling natural selection. A 1% selective advantage shifts population composition.
- Our sim03: fixed reaction network converges immediately (by generation 1) and never changes for 3000 generations. *(Corrected 2026-07-27: this is not a confirmation. The organization lattice is enumerated from a fixed, hand-authored network and is identical at every sampled generation of every run — the stall is guaranteed by the design. The concentration equilibrium is a real result; the organizational stall is not a test. Counts also changed after a closure fix: 8 organizations single / 9 multi, 1/24 nested pairs.)*
- Fontana & Buss (1994): Lambda calculus chemistry (AlChemy) produces "organizational transitions" — shifts between qualitatively different organizational regimes — when new molecules appear as products of reactions.

**Connection to H7:** The appearance of a novel viable core IS the trace→actor crossing. Existing resources are traces; the novel reaction produces a new self-maintaining set (organization/actor) from them.

**Connection to H8:** You cannot predict which novel cores will appear — you must simulate. The space of possible reactions is too large to enumerate, and viability depends on the entire network state.

**The "one bit" limitation:** A single viable core carries ~1 bit of heritable information (present/absent). Open-ended evolution requires unlimited heritable information. The evolving network extends the "adjacent possible" — each new core opens new reaction possibilities — but whether this produces true open-endedness or just limited multi-attractor dynamics is an open question.

**Refinement (2026-07-27, post code review — two legs weakened, one survives):** H9's supporting evidence has thinned considerably.

- **Withdrawn:** "sim03 negative." Its organization lattice is static by construction, so it cannot demonstrate that fixed networks fail to evolve (see H9's evidence bullet above).
- **Withdrawn:** "sim05 shows unbounded space stalls differently." Corrected, sim05 gives 2/6 L2 coexistence — it does not show a stall.
- **Withdrawn:** the comparative result. sim04 was recorded as showing the evolving network finding *more* autocatalytic cores (5 vs 4) — a "modest improvement" that was H9's only positive simulation evidence. Corrected, it is **3 vs 3, no difference**, and the earlier figures came from a run that was not reproducible at all (catalysis was derived from Python's per-process-randomized `hash()`).
- **Survives:** sim04's finite-space exhaustion. Both conditions saturate at 510/510 species and neither produces open-ended evolution. That is a structural bound and is unaffected by the determinism fix.

Net: H9's claim that evolving networks overcome the fixed-network stall currently has **no supporting simulation evidence in this repo** — the one measurement that appeared to support it has been retracted. Vasas et al. (2012) still supports it in the literature. H9 should be treated as untested rather than partially confirmed, and the test below has in effect not yet been run under conditions that could answer it: sim04's finite space exhausts before the evolving mechanism has room to matter.

**Test:** Compare fixed network (no new reactions, sim03-like) vs. evolving network (new reactions appear) with compartmentalization. Measure: does the evolving network discover new species, new organizations, and maintain between-compartment diversity where the fixed network converges? *(To be informative this now needs an unbounded or much larger species space — in a 510-species world both arms exhaust it and the comparison is uninformative by construction.)*

---

## H10: The Unbounded Space Insufficiency Hypothesis (NEW — Session 6)

**An unbounded molecule space (infinite possible species) is necessary but not sufficient for multi-scale composition.** Even when the species space is infinite (lambda calculus chemistry), single-scale organizations (L1) form but do not compose into multi-scale structures (L2) without explicit composition mechanisms.

**Evidence:**
- Our sim04 (finite space, 510 species): both fixed and evolving networks exhaust the finite space and stall. Novel reactions are redundant when catalyzed reactions already explore the space.
- Our sim05 (unbounded space, lambda calculus): stable species sets emerge from random initial conditions (**10–21** per run, mean 15.2), each run explores **112–162** unique species with mean pairwise overlap 0.061. The space is NEVER exhausted. L2 composition (coexistence) = **2/6**; dominance 3/6, mutual destruction 1/6. *(Corrected 2026-07-27: previously "4-37 stable species per run", "246-930 unique species", "0/6 coexistence", "Dominance (50%) and Mutual Destruction (50%) are the only outcomes" — the species counts were inflated ~3–6× by a non-alpha-invariant equality, and the outcome distribution was an artifact. See the 2026-07-27 refinement below.)* Note also that sim05 never tests closure or self-maintenance, so these are surviving species sets rather than organizations in the COT sense.
- Mathis et al. (2024) systematic reanalysis of AlChemy: "stable organizations cannot be easily combined into higher order entities." L2 coexistence is rare across all tested pairs.
- Fontana & Buss (1994) original: L2 organizations identified but rare, requiring specific "glue" expressions that bridge L1s.

**Connection to H1:** This refines H1. The original formulation was: "ALife simulations stall because they lack multi-scale composition." H10 adds: the stall is NOT due to finite species space (sim04's problem) — it persists with infinite space (sim05). The bottleneck is architectural (no composition mechanism), not spatial (no room for novelty).

**Connection to H7:** The "glue" that enables L2 is analogous to the trace→actor crossing. Glue doesn't emerge spontaneously — it requires either stigmergic traces that bridge organizations, autopoietic boundaries that protect during interaction, or explicit selection for composability. AlChemy has none of these.

**Connection to H8:** Each L1 run produces a unique organization — unpredictable from initial conditions. Whether two L1s will compose is also unpredictable. Computational irreducibility at the organization-formation level AND at the composition level.

**Three paths, same failure:** Echo (Holland's CAS model), chemical organizations (COT/Vasas), and AlChemy (lambda calculus) ALL fail at multi-scale composition. Each from a different starting point (CAS theory, origin-of-life chemistry, computational theory). This convergence is strong evidence the composition problem is fundamental, not an artifact of any single approach.

**Test:** Build a simulation with explicit composition mechanisms (stigmergic bridges between organizations, autopoietic boundaries, selection for composability) and compare to AlChemy without these mechanisms. Measure: does the version with composition mechanisms produce L2 where the plain version fails?

**Refinement (2026-07-27, post code review — H10's primary evidence was substantially an artifact):** A construct-validity audit of the simulation code (`../simulations/REVIEW.md`) found three defects in sim05's L2 test, each biasing against coexistence: (1) species identity was not alpha-invariant, so the same lambda term under different bound-variable names counted as distinct species — inflating species counts and deflating every set intersection; (2) outcomes were classified on Jaccard similarity, whose arithmetic ceiling fell *below* the 0.15 coexistence threshold for two of the six pairs, making coexistence undetectable for those regardless of dynamics; (3) the mixed population was padded almost entirely from organization A, handing it a roughly 9:1 abundance advantage under mass action — which is why all six pairs originally returned dominance by the lower-indexed run.

With all three corrected, sim05 gives **2/6 coexistence (33%), 3 dominance, 1 mutual destruction**, stable across survival thresholds 0.45–0.70. The "0/6, dominance and mutual destruction are the only outcomes" claim above does not hold.

H10 is **weakened but not refuted.** Coexistence remains the minority outcome, so unbounded space still looks insufficient on its own, and the independent evidence (Mathis et al. 2024; Fontana & Buss 1994) is untouched. But "L1 organizations do not compose" was too strong — in this model they compose about a third of the time. The "three paths, same failure" convergence argument above should be read with that in mind: sim05 is now a weaker leg of it than when written. Note also that sim05 never tests closure or self-maintenance, so its "L1 organizations" are surviving species sets rather than organizations in the COT sense — an independent reason to treat this evidence as softer than originally stated.

---

## H11: The Saturating Channel Hypothesis (NEW — 2026-07-27)

**Negative feedback delivered *through* a stigmergic trace is self-defeating wherever the agents' response to that trace saturates.** The manipulation intended to create spatial contrast operates in the region where contrast cannot be expressed, so adding feedback energy to a saturated channel removes selectivity instead of producing it. Consolidation therefore requires feedback through a channel that remains responsive — acting on the *action* (deposit probability, geometry) rather than on the *cue* the agents read.

**Origin:** this hypothesis came out of the 2026-07-27 construct-validity review rather than from reading. It was invisible beforehand because sim06's crossing detector could not fire, so the condition-to-condition comparison that reveals it was never examined.

**Evidence — two independent mechanisms, same failure direction:**

| attempt | mechanism | components | stability |
|---|---|---|---:|
| sim06 self-maintenance | structure re-emits pheromone (`maintain_gain=0.3`) | 66–109 → **219–297** | 0.849–0.893 → 0.746–0.802 |
| sim07 transport field | structure sources `T`, vents pheromone toward gaps | 57 → **128** as `M_c` falls | 0.876 → **0.739** |

Both were designed to *consolidate*. Both fragmented, monotonically, and in sim07's case across a full `M_c` sweep with no threshold effect anywhere. Neither result is a near miss or a parameter-tuning artifact.

**Mechanism:** the deposit rule is `p = DEPOSIT_BASE + DEPOSIT_GAIN · φ/(1+φ)`, which is effectively flat above φ≈1. Self-emission and venting both drive the pheromone field high; combined with diffusion, deposit probability then sits at ~0.87 **everywhere**. The spatial contrast that stigmergy depends on is destroyed by the very mechanism intended to sharpen it. sim06's self-maintenance condition is the cleanest demonstration: it is *more* fragmented (219–297 vs 66–109 components) and *less* selective (`deposit_on_structure` 0.43–0.53 vs 0.70–0.79) than the baseline it was supposed to improve on.

**Connection to H7:** this sharpens H7's prescription. The Session 8/9 refinements called for "negative feedback" or "a new dynamical degree of freedom" in the abstract. That has now been attempted twice and failed twice, both times for the same reason. H11 says the missing ingredient was never the *presence* of negative feedback but the *channel* it acts through. If H11 holds, H7's crossing should be reachable with a much simpler mechanism than directed transport.

**Connection to H4 (Dynamic Environment):** a saturated medium is a single-rate medium no matter how many processes write to it. H4 requires the environment to be a genuine participant — perceivable *and* modifiable — but a cue field pinned at the top of its response curve is no longer perceivable in any discriminating sense. H11 is the failure mode H4 must avoid.

**Connection to the multi-rate environment (Vance's contribution):** approaches the same idea from the other side. It is not enough that different actors operate at different rates; the medium must stay *responsive* across the range those rates drive it through. Saturation collapses a multi-rate medium into a single-rate one.

**Criticism / limitations:**
- Both data points come from the same model family (Grassé stigmergy on a grid), so the replication is weaker than two genuinely independent systems would be. The response curve is also *the same function* in both, which is the point of the hypothesis but does limit how independent the confirmations are.
- The saturating form `φ/(1+φ)` was a modeling choice, not a measurement of real termites. A non-saturating deposit rule might be biologically wrong even if it consolidates better.
- **Literature check (2026-07-27):** H11 is a partial rediscovery, not fully novel. The ACO literature addresses the same underlying problem through two mechanisms:
  - **Evaporation** (`τ ← (1-ρ)τ`): Dorigo & Stützle's ACO book notes evaporation "plays the important function of bounding the maximum value achievable by pheromone trails" — i.e., preventing the saturation that H11 identifies. But evaporation acts on the cue field itself (lowering τ), which is precisely the channel H11 says is problematic. It works in ACO because ACO's response function does not saturate the way `φ/(1+φ)` does — ACO uses `τ^α · η^β` which is unbounded.
  - **MAX-MIN Ant System** (Stützle & Hoos, 2000): explicitly bounds τ ∈ [τ_min, τ_max] to prevent stagnation. This is the closest prior art — it recognizes that unbounded pheromone causes convergence problems and caps the field. But it caps the cue, not the action; H11's contribution is the claim that acting on deposit probability (the action) rather than on pheromone level (the cue) is the critical distinction.
  - What H11 adds beyond ACO: the explicit distinction between **channel saturation** (a property of the response function) and **feedback through the cue** (a property of where the feedback acts). ACO's evaporation and MMAS's bounding both operate on the cue field. H11 predicts that when the response function saturates, cue-based feedback is insufficient regardless of how it is tuned, and action-based feedback (density caps, refractory periods) is needed. This is a testable claim that ACO does not make, because ACO's response functions do not saturate in the biological sense.
  - **Novelty status:** the observation that saturation destroys spatial contrast is not in the ACO literature, because ACO does not use saturating response functions. The prescription (act on the action, not the cue) is novel within the stigmergy/ALife literature. The underlying problem (bounded pheromone causes stagnation) is known in ACO. H11 should be framed as extending the ACO insight to systems with saturating response functions, not as a wholly new discovery.
  - **Experiment confound:** all three proposed test mechanisms (density cap, refractory period, directional bias) are both action-based AND non-saturating simultaneously. The planned experiment therefore cannot distinguish "action-based" from "non-saturating" as the causal variable. If non-saturating inhibition consolidates, it could be because the channel is non-saturating, because it acts on the action, or both. A cleaner test would include a condition that is action-based but saturating (e.g. a deposit-probability cap that itself saturates) to isolate the two factors. Without that control, the experiment confirms "non-saturating action-based feedback works" but does not discriminate which property is load-bearing.

**Test:** run sim06 with negative feedback delivered through a non-saturating channel — a density cap (deposition suppressed where material exceeds a threshold), a refractory period (a cell that just received a pellet is briefly unavailable), or directional bias along existing wall edges. Compare against both sim06's self-maintenance condition and sim07's transport condition. Prediction: **non-saturating inhibition consolidates (components fall, stability rises) where field manipulation fragmented.** If instead it also fragments, H11 is wrong and the problem lies deeper than the response curve. This is substantially cheaper than directed transport and discriminates the two accounts directly.

**Refinement (Session 13, 2026-07-28 — sim08 partial corroboration, boundary sharpened):**
sim08 tested the cheapest non-saturating channel — a **density cap** (a cell at/above
`DENSITY_CAP` cannot receive deposits; a hard boolean gate on the action, not a graded
cue function) — reusing sim06's metrics and detector unchanged.

**Result: H11 confirmed in direction, sharpened in sufficiency.**

- **The cap consolidates morphology, monotonically.** Sweeping the cap from ∞ (off) to
  1.5, pillars fall 101 → 52, and the pheromone field is de-saturated (max pheromone
  8.01 → 2.50). This is exactly the effect H11 predicts: a non-saturating action-gate
  prevents the cue field from being driven flat and prunes nucleation. The direction
  H11 claimed is real and replicated in a third independent mechanism.
- **But the cap does NOT produce the crossing.** Stability does not rise (0.874 → 0.775
  at the tightest cap); the detector never fires for any cap strength. The cap reduces
  building *volume* (1131 → 619 cells) without raising *persistence*.
- **The cap does NOT rescue cue-based feedback.** cap+self_maintenance (262 pillars,
  stability 0.763) is no better than self_maintenance alone (252, 0.775) — consistent
  with H11: the cue channel, not the feedback energy, is the problem.

**What this means for H11.** Non-saturating inhibition is **necessary-but-not-sufficient**.
A cap that *only limits growth* corrects the fragmentation symptom (pillars) but not the
persistence symptom (stability) — the crossing needs a structure that holds its mass
against erosion, and a pure limiter reduces mass rather than recruiting its maintenance.
The crossing therefore needs a non-saturating channel that **recruits** as well as limits:
the curvature channel in real termites (Calovi 2019) does both — it routes deposition to
concavities (limits scatter) AND each deposit extends the concavity (recruits further
building at the edge). The density cap only limits. Candidate next: a curvature/
deposition-edge rule that routes AND limits. See
[`concepts/non-saturating-channels.md`](../concepts/non-saturating-channels.md) and
[sim08](https://alife.vancedubberly.com/sim08_density_cap/visualize.html).

**H11's status is now: directionally confirmed (3/3 mechanisms), but the "consolidation
requires non-saturating feedback" claim is refined to "consolidation requires non-
saturating feedback that RECRUITS, not merely one that LIMITS."** The cheap test did not
settle the crossing but it did discriminate: the cap consolidates where cue-feedback
fragments, so the channel distinction H11 draws is real; the cap alone just isn't enough.

---

## Summary Table

| Hypothesis | Status | Evidence |
|---|---|---|
| H1: Composition | Refined | Smith & Bedau (1997) independent confirmation; sim03 shows a fixed network's organization lattice is static — but that is true by construction, not an empirical finding |
| H2: ANT Translation | Unchanged | Theoretical, untested |
| H3: Quasi-Object | Strengthened | Stigmergy literature support; Echo partial support |
| H4: Dynamic Environment | Refined | Fitness landscape criticism supports this |
| H5: Autopoiesis | Unchanged | Maturana & Varela grounding |
| H6: Multi-Scale Autopoiesis | Strengthened | Smith & Bedau 8th property = autopoiesis |
| H7: Trace→Actor Crossing | Refined (×4); sim08 (2026-07-28) non-saturating cap consolidates morphology but not the crossing | S&B 8th property; sim06 near miss (stability 0.849–0.893 vs 0.90); sim07 null (scalar transport insufficient); sim08 partial (cap prunes pillars 101→52 but stability doesn't rise, crossing doesn't fire) — non-saturating inhibition necessary but not sufficient |
| H8: Complexity Enables OEE | NEW | Kaznatcheev (2019), Wiser et al. (2013) |
| H9: Evolving Network | Refined; two legs weakened 2026-07-27 | Vasas et al. (2012); sim04 confirms finite space stall (510/510 species — survives the determinism fix). Weakened: sim03's "negative" is structural, not empirical; sim05 no longer shows unbounded space stalling (2/6 coexistence) |
| H10: Unbounded Space Insufficiency | WEAKENED (2026-07-27) | sim05 corrected: 2/6 L2 coexistence (was 0/6 — artifact); Mathis et al. 2024, Fontana & Buss 1994 unaffected |
| H11: Saturating Channel | Directionally confirmed (3/3), boundary sharpened (2026-07-28) | sim06 self-maintenance and sim07 transport both fragmented through the saturating cue field; sim08 density cap (non-saturating action-gate) consolidates morphology (pillars 101→52, max pheromone 8.01→2.50) but does not fire the crossing — necessary-but-not-sufficient. Literature: ACO evaporation / MAX-MIN Ant System bound the cue; H11 says act on the action. Termite biology (Calovi 2019 curvature; Carey 2021 humidity; Xiao 2026 crowding) uses non-saturating channels, not a saturating cement pheromone. Refined: the crossing needs a non-saturating channel that RECRUITS, not merely one that LIMITS |
