---
status: active
formed: "Session 13"
connected_to: "stigmergic consolidation, environmental physics coupling, stigmergy, H7, H11, multi-rate environment, niche construction"
topic: "non-saturating stigmergic channels — geometry, humidity thresholds, and crowding as the biological grounding for H11 (sim09 fully implemented)"
key_findings: "Real termite construction is guided by THREE non-saturating, action-based channels rather than by a saturating pheromone field: (1) surface CURVATURE — Calovi et al. 2019 (Phil Trans R Soc B) disambiguated curvature from inclination and height across three orientations and found curvature is the 'consistent and sole driver' of construction in Macrotermes michaelseni; the SAME cue elicits OPPOSING actions depending on the termite's loaded/seeking state. (2) HUMIDITY THRESHOLDS — Carey/Bardunias/Nagpal/Werfel 2021 validated with a robot that termites deposit at the EDGE of the high-humidity zone, a threshold-triggered deposition rule. (3) CROWDING/INACTIVITY — Xiao et al. 2026 (arXiv:2607.19594) frame inactivity under confinement as 'distributed inhibition that prevents saturation.' SESSION 14 UNIFICATION: Facchini et al. 2020 (J R Soc Interface) and 2024 (eLife) showed the curvature and humidity channels are ONE physical quantity — evaporation flux ∝ surface curvature (Langmuir 1918) — and built a curvature-only phase-field growth model (no pheromone field at all) that reproduces real nest morphology. The convex (Facchini: deposit at tips) / concave (Calovi: activity at pits) contradiction is resolved: the two measured different action components (deposition vs aggregate activity). Facchini 2024 explicitly state 'experiments do not support a role for a putative cement pheromone' — two independent groups now report no cement pheromone. SESSION 17 (2026-08-02): sim09 FULLY IMPLEMENTED (all 9 Parts). SESSION 19 (2026-08-03): the d* sweep (100 combos) found 0/100 under the original detector — the mass-saturation gate was an unfalsifiable metric-ceiling bug (threshold ~100× below the Poisson noise floor). Corrected to a relative-slope plateau, the crossing FIRES in the curvature channel at every d in the tuned probe and does NOT fire in the baseline-pheromone control (same detector) — the first H7 crossing with a control arm. SESSION 20 (2026-08-04): the recruit-vs-limit 2×2 factorial found the recruit half (curvature routing) is necessary + almost-sufficient for a stable crossing; the limit half (biharmonic smoothing) alone is never stable (0/4) but is a stability amplifier (recruit+limit 4/4 vs recruit-only 3/4). SESSION 21 (2026-08-05): the saturating-action control resolved H11's confound — a saturating action-based channel (p = base + gain·c/(1+|c|)) still crosses in 8/8 seeds (stable 6/8) vs linear 8/8 (stable 7/8); the limit half rescues both to 4/4 at d=1. ACTION-BASED routing is the primary load-bearing property; NON-SATURATING is a secondary stability amplifier (mean hold drops 0.91→0.86 at d=0; criterion 3 holds 1.00 for both forms). H11's strict 'non-saturating' claim is partially weakened: a saturating action-based channel still crosses stably, but less robustly. The three-level causal decomposition: (1) action-based routing = primary, (2) non-saturating response = secondary stability, (3) biharmonic smoothing = tertiary stability + morphology."
---

# Non-Saturating Stigmergic Channels

**Status:** Active — formed Session 13
**Connected to:** [stigmergic consolidation](stigmergic-consolidation.md), [environmental physics coupling](environmental-physics-coupling.md), [stigmergy](stigmergy.md), H7, H11, [multi-rate environment](multi-rate-environment.md), [niche construction](stigmergy-vance-notes.md)

## The Concept

[H11](../hypotheses/hypotheses.md) predicts that the trace→actor crossing needs negative feedback
through a **channel that does not saturate** — acting on the *action* (deposit probability, geometry)
rather than on the *cue* field the agents read. This file supplies the biological grounding: real
termites appear to have evolved exactly such channels, and the saturating "cement pheromone" that
the classic Grassé model assumes is increasingly in doubt. Three independent lines of experimental
evidence converge on non-saturating, action-based feedback.

## 1. Surface curvature — the geometric channel (Calovi et al. 2019)

Calovi, Bardunias, Carey, Turner, Nagpal & Werfel (Phil Trans R Soc B, 2019; DOI 10.1098/rstb.2018.0374)
ran controlled field experiments on *Macrotermes michaelseni* in Namibia. They 3D-printed a test
surface with continuously varying curvature (concave, convex, flat), coated it with nest soil, and
mounted it in **three orientations** (horizontal, 45°, vertical) to disambiguate curvature from
inclination and geotaxis.

**Finding:** "curvature is the consistent and sole driver, among the measured geometric candidates,
of both early termite positioning and construction activity." Soil displacement correlated with
curvature across all three orientations; inclination and height did not. Concave (high positive
curvature) regions attract deposition; convex regions attract excavation.

**Why this matters for H11:**

- **Curvature is non-saturating.** Unlike a pheromone field whose deposit response flattens above
  φ≈1, curvature is a geometric quantity that the structure carries regardless of how much
  pheromone is present. You cannot "saturate" curvature by adding more deposits — each deposit
  *changes* the curvature, so the channel stays responsive. This is precisely the property H11
  says the crossing requires.
- **The rule is action-based and state-gated.** The same high-curvature cue elicits *opposing*
  actions — excavation OR deposition — depending on whether the termite is loaded with soil or
  seeking a digging site. The cue does not monotonically increase deposit probability; it routes
  the agent's current action. This is the "act on the action, not the cue" prescription, observed
  in the animal.
- **It is a genuine negative feedback.** Filling a concavity reduces its curvature, which
  removes the cue for further filling — a self-limiting loop. Excavating a convexity reduces its
  convexity, removing the cue for further excavation. The geometry carries its own inhibition.
- **It supplies the "directional bias" H11 listed.** Deposition preferentially at concavities IS
  building along existing wall edges rather than onto their centers.

The paper's own framing: "These two possibilities represent computations the liquid/solid brain
can perform, amplifying or smoothing out initial irregularities in tunnel walls." Amplify =
positive feedback (a concavity fills, deepening the concavity elsewhere); smooth = negative
feedback (a concavity fills and disappears). Both are mediated by the same non-saturating
geometric channel.

## 2. Humidity thresholds — the template channel (Carey et al. 2021; Bardunias et al. 2020)

Carey, Bardunias, Nagpal & Werfel (Front Robot AI, 2021; DOI 10.3389/frobt.2021.645728) tested the
"humidity template" hypothesis with a physical robot: termites deposit wet soil at the **edge** of
the high-humidity zone that extends from a tunnel mouth. The robot, controlled only by a local
humidity sensor, replicated the behavior — extending a semi-enclosed area in still air and closing
it off when a fan disturbed the humidity bubble.

**Why this matters for H11:**

- **Threshold-triggered, not graded.** Deposition fires at a humidity boundary (a level
  crossing), not as a saturating function of humidity level. This is the "refractory / threshold"
  channel — a discrete, non-saturating trigger.
- **The cue and the action are decoupled in the right way.** Humidity is the cue, but the
  feedback (depositing wet soil *extends* the humidity zone, moving the boundary) acts on the
  *geometry* of the boundary, not by raising the humidity level everywhere. Adding wet soil does
  not saturate a humidity response; it relocates a threshold.
- **External perturbation reroutes the action.** Wind shrinks the bubble → the same rule now
  *closes* the tunnel instead of extending it. A single non-saturating rule produces opposite
  morphological outcomes under different external conditions — a multi-rate-environment (H4)
  coupling, mediated by a non-saturating channel.

## 3. Crowding / inactivity as distributed inhibition (Xiao et al. 2026)

Xiao, Wu, Lim, Su, Bardunias, Chatterjee & Bhamla (arXiv:2607.19594, Jul 2026, "Sensing, Traffic,
and Construction in Termites") review the coupled sensing-traffic-construction loop in subterranean
termites. Their framing of crowding is directly H11-relevant: "Under confinement, inactivity can
act as a form of distributed inhibition that prevents saturation." Congestion at an excavation
front generates queues that *redirect* workers to lateral digging (tunnel widening, branching)
rather than continuing to pile in.

**Why this matters for H11:**

- **Crowding is a density cap on action.** A cell that is "full" of termites suppresses further
  entry — a refractory period on the spatial slot. This is the "density cap" channel, the third
  mechanism H11 listed.
- **It acts on the action (where the termite goes), not on a cue field.** The termite does not
  read a saturating "crowding pheromone"; it physically cannot proceed, so it does something else.
  The inhibition is mechanical, not chemical, and therefore cannot saturate.

## The convergence, and what it implies

Three channels — curvature (geometry), humidity (threshold), crowding (mechanical density) — each
non-saturating, each acting on the action rather than the cue. Real termite construction appears to
rely on these and NOT on a saturating cement pheromone, which despite 60+ years of search
**"no cement pheromone has yet been identified"** (Calovi et al. 2019). The biological system
evolved away from the saturating channel H11 flags as self-defeating.

**This is strong external support for H11.** The hypothesis was derived from a bug fix in our own
code (two failed feedback attempts, both through the saturating pheromone field). The termite
literature independently shows that the channels real termites use are precisely the non-saturating
ones H11 prescribes, and that the saturating channel (cement pheromone) is the one biology may not
use at all. H11 may be less a rediscovery of ACO (which bounds the cue) and more a rediscovery of
what termites actually do.

**Implication for sim08 (the cheap test):** the density cap / curvature rule / humidity threshold
are not ad hoc additions chosen to make the crossing fire — they are the mechanisms the model
organism actually uses. sim06 used a saturating pheromone response because the lineage (Deneubourg
→ Bonabeau → Ladley) assumed a cement pheromone. The biological evidence now says that assumption
is likely wrong, and H11 explains *why* it fails: a saturating cue channel cannot express the
spatial contrast consolidation needs.

## Connection to the saturating response curve (H11's mechanism)

The deposit rule in sim06/sim07 is `p = DEPOSIT_BASE + DEPOSIT_GAIN · φ/(1+φ)`, flat above φ≈1.
Curvature feedback is the complementary case: the "response" to curvature is a *routing* decision
(excavate vs deposit, depending on state), not a saturating probability. The curvature channel
has no "flat above threshold" region — it stays discriminating because it is redefined by each
action. This is the formal distinction: **a saturating channel maps cue level → action intensity
and compresses; a non-saturating channel maps cue geometry → action selection and preserves
contrast.**

## Criticisms

- **Correlation, not mechanism (partially resolved 2026-07-29).** Calovi et al. establish
  correlation of construction with curvature, disambiguated from confounds, but the mechanism by
  which termites *assess* curvature "is unknown, but presumably involves a combination of
  antennation and proprioception." Facchini et al. 2024 now propose the transduction is indirect —
  termites sense curvature through **substrate evaporation flux**, which is analytically
  proportional to curvature (Langmuir 1918). This turns "correlation" into "one physical quantity,
  sensed through a gradient," but the sensing itself (humidity detection) remains inferred, not
  directly measured at the deposition site.
- **The convex/concave contradiction (resolved 2026-07-29).** Calovi 2019 (concave → activity)
  and Facchini 2024 (convex tips → deposit) appear to conflict. The resolution: Calovi measured
  *aggregate* activity (digging + building); Facchini isolated pellet *deposition*. Deposition is
  at convex tips; excavation is at concave pits. Both are curvature-driven; the action component
  differs. This is a caution against treating "construction" as a single action in a model —
  sim09 must separate deposit and excavate.
- **The three channels may not be independent.** Curvature, humidity, and crowding are coupled
  in real mounds (concavities hold humid air; narrow concavities crowd). Facchini 2024 unifies
  curvature and humidity as evaporation flux, reducing three to two (geometry/evaporation +
  crowding), but separating them in simulation remains an open experimental problem.
- **State-gating complicates replication.** The same curvature cue elicits excavation OR
  deposition depending on the termite's loaded state. A simulation must model that state to
  reproduce the effect — a richer agent than sim06's deposit-only rule.
- **No cement pheromone identified ≠ no chemical cue.** Absence of identification is not proof
  of absence; other chemical cues (trail pheromones, CO₂) may yet play roles. The claim is that
  the *saturating deposit-response* channel is not the primary one, not that chemistry is absent.
  Facchini 2024 strengthens this: their "experiments do not support a role for a putative cement
  pheromone" — now two independent groups.
- **Morphology ≠ crossing.** Facchini's curvature-only model reproduces nest *geometry* (pillars,
  walls, branching) but does not test self-maintenance, persistence against erosion, or
  perturbation repair. sim09 must add those tests — reproducing the morphology is necessary but
  not sufficient for the trace→actor crossing.

## Empirical Evidence

- **Calovi, Bardunias, Carey, Turner, Nagpal & Werfel (2019)**, Phil Trans R Soc B 374:20180374.
  Field experiments on *M. michaelseni*; curvature is the sole consistent driver of construction
  across three surface orientations, disambiguated from inclination and height. DOI 10.1098/rstb.2018.0374
- **Carey, Bardunias, Nagpal & Werfel (2021)**, Front Robot AI 8:645728. Robot validation of the
  humidity-template deposition rule; threshold-triggered, wind-rerouted. DOI 10.3389/frobt.2021.645728
- **Bardunias et al. (2020)** — the humidity-template hypothesis in *M. michaelseni* mounds.
- **Xiao, Wu, Lim, Su, Bardunias, Chatterjee & Bhamla (2026)**, arXiv:2607.19594. Review framing
  crowding/inactivity as distributed inhibition preventing saturation; curvature-biased
  excavation/deposition across subterranean and mound-building taxa.
- **Werfel, Petersen & Nagpal (2014)**, Science 343:754–758. Termite-inspired construction robots
  using only local sensing; inverse-problem design with threshold-triggered deposition.
  DOI 10.1126/science.1245842
- **Reina & Marshall (2022)**, PLoS Comput Biol 18:e1010090. Negative feedback in social-insect
  foraging suppresses *variance* (not just convergence) in small populations — an additional
  function for non-saturating inhibitory signals. DOI 10.1371/journal.pcbi.1010090
- **Stützle & Hoos (2000)**, MAX-MIN Ant System. Bounds the cue τ ∈ [τ_min, τ_max] to prevent
  stagnation — the closest ACO prior art, but acts on the cue field, not the action. H11's
  distinction: when the response saturates, cue-bounding is insufficient; action-based feedback
  is needed.
- **Facchini, Lazarescu, Perna & Douady (2020)**, J R Soc Interface 17:20200093. A curvature-only
  phase-field growth model (no pheromone field) that reproduces arboreal *Nasutitermes* nest
  geometry — walls branch, merge, invade space, with a characteristic length scale set by one
  parameter `d`. Public finite-difference code: github.com/oiluigioi/JRSI_2020_termite_nest.
  DOI 10.1098/rsif.2020.0093
- **Facchini et al. (2024)**, eLife 13:86843. "Substrate evaporation drives collective
  construction in termites." Shows evaporation flux ∝ surface curvature (Langmuir 1918), so the
  curvature and humidity channels are one physical quantity; termites sense curvature indirectly
  through evaporation. Curvature-only simulation matches experimental deposition patterns.
  Explicitly states "experiments do not support a role for a putative cement pheromone."
  Resolves the convex (deposit at tips) / concave (activity at pits) contradiction as different
  action components. DOI 10.7554/eLife.86843

## 4. The unification: curvature ≡ evaporation flux (Facchini et al. 2020, 2024)

The curvature and humidity channels are not separate. Facchini, Lazarescu, Perna & Douady
(2020, J R Soc Interface 17:20200093) proposed a **curvature-only growth model** for arboreal
*Nasutitermes* nests: a phase-field equation in which the nest is a scalar field `f` and growth is
driven by the **local mean curvature** of its surface, with a smoothing term that mimics the
pellet-size cutoff. A single nonlinear equation with one adjustable parameter `d` (the pattern
length scale) reproduces walls that expand, branch, merge, and invade space, and the abundance of
saddle-shaped (zero-mean-curvature) surfaces seen in CT-scanned real nests. **There is no
pheromone field in the model at all** — curvature alone organizes construction.

Facchini et al. (2024, eLife 13:86843) then showed *why*: evaporation flux is directly
proportional to surface curvature (a result going back to Langmuir 1918). Termites sense curvature
*indirectly through substrate evaporation* — the humidity gradient is maximal at pillar tips and
wall corners, exactly where deposition concentrates. This unifies Calovi 2019 (curvature) and
Carey 2021 (humidity) into one physical quantity: **the curvature channel IS the
humidity/evaporation channel, sensed through one physical gradient.** The humidity-template
threshold rule (Carey) and the curvature rule (Calovi) are the same mechanism at different scales
of description.

### The convex/concave contradiction, resolved

Facchini 2024 and Calovi 2019 appear to contradict: Facchini finds **deposition at convex pillar
tips**; Calovi finds **activity at concave regions**. The resolution is that the two studies
measured different things. Calovi measured aggregate construction activity (digging + building
together); Facchini isolated pellet *deposition* specifically. Deposition is at convex tips
(growth extends the structure upward/outward); excavation is at concave pits (material removed
from pits). Both are curvature-driven, but the *action component* differs. The Calovi
state-gating (loaded → deposit at concavity, seeking → excavate at convexity) and the Facchini
result (deposit at convex tips) are consistent once you separate the actions: *where* a termite
deposits depends on its loaded state, and the Facchini experiments observed primarily
depositing (loaded) termites on pre-made topography.

For sim09 this means the rule is **state-gated**: loaded termites deposit at high curvature
(convex tips of the material field); unloaded termites excavate at low curvature (concavities).
This is richer than sim06's deposit-only rule and is exactly the "recruits as well as limits"
channel: depositing at a convex tip *extends* the tip (recruits further building there) while
the smoothing term (Facchini's `d`) limits feature size — both consolidation properties the
density cap lacked.

### Positive feedback through roughness — the recruit mechanism

Facchini 2024 notes a subtle but crucial feedback: adding pellets to a convex region makes the
surface *rougher* (more local curvature variation), which *further focuses* evaporation/deposition
there. This is a genuine positive feedback through the geometry itself, not through a saturating
cue field. It is the **recruit** half of the "recruits as well as limits" requirement: the
structure's own shape, once nucleated, amplifies the cue that recruits further building *at the
same location*. The density cap (sim08) had only the limit half; curvature has both.

### No cement pheromone (again, and stronger)

Facchini 2024 explicitly state their "experiments do not support a role for a putative cement
pheromone." This is now two independent groups (Calovi 2019, Facchini 2024) reporting no cement
pheromone, plus a curvature-only model that reproduces real morphology without it. The saturating
cue the Grassé lineage assumed is not just unused — it is unnecessary to reproduce the target
phenomenon. H11's flag on the saturating channel is corroborated at the level of *sufficiency*,
not just absence.

## 5. The published curvature growth model (the sim09 substrate)

The Facchini 2020 growth equation (the one sim09 should adapt to 2D):

```
∂f/∂t = f(1−f) · [ −(1/2)·∇·n  +  d·Δ(∇·n) ]
```

where `f` ∈ [0,1] is the phase field (1 = nest material, 0 = empty), `n = ∇f/|∇f|` is the surface
normal, and `d` sets the pattern length scale. Approximated (Facchini 2020) as:

```
∂f/∂t ≈ f(1−f) · [ (1/2)·Δf  +  d·Δ²f ]
```

- The growth term `(1/2)·Δf` is the **mean curvature** (Laplacian of the height field) — positive
  at convex tips (growth), negative at concavities (excavation). This is the recruit mechanism.
- The smoothing term `d·Δ²f` (biharmonic / curvature diffusion) mimics the pellet cutoff — sharp
  features are smoothed. This is the limit mechanism.
- The prefactor `f(1−f)` restricts growth to the *surface* (the boundary of the structure), not
  the bulk — deposits happen at edges, not interiors. This is spatial selectivity without a
  saturating cue.
- For large `d` the equation is **linearly unstable**: walls expand, branch, and merge, invading
  all space — the consolidation morphology. Below the instability, growth stalls.

**Why this matters for H7/sim09.** This is a non-saturating, geometry-based channel that
*recruits* (deposition at convex tips extends the tip) AND *limits* (smoothing caps feature size),
restricted to the structure surface by `f(1−f)`. It has no pheromone field to saturate. The
instability in `d` is a candidate phase-transition parameter: below it, diffuse growth (sim06
regime); above it, consolidated morphology (the crossing candidate). Public finite-difference
code exists (github.com/oiluigioi/JRSI_2020_termite_nest) — sim09 adapts this to sim06's 2D
grid + agent framework, replacing the pheromone-deposit rule with a curvature-deposit rule.

## Open Questions

- Does a minimal simulation with a curvature-based deposit rule (convex tip → deposit,
  concavity → excavate, state-gated, with a smoothing term) consolidate where sim06's
  saturating-pheromone rule fragmented, AND fire the crossing? This is the direct test of H7's
  refined prescription and is candidate **sim09**.
- Is the `d` instability the *phase transition* the crossing needs? If crossing fires only above
  the curvature-instability threshold and not below it, `d` is to sim09 what `M_c` was to sim07 —
  but with a mechanism (curvature) that recruits as well as limits, where the scalar transport
  only dispersed. **sim09 FULLY IMPLEMENTED (Session 17, all 9 Parts [x]); crossing corrected
  and FIRES (Session 19, 2026-08-03).** The d* sweep (100 combos, dpb × decay × d) found 0/100
  under the original detector — the mass-saturation gate (`|growth_rate|<0.01`) was an
  unfalsifiable metric-ceiling bug, its threshold ~100× below the Poisson noise floor of a
  150-termite deposit process. Corrected to a relative-slope plateau
  (`|slope(M)|/mean(M)<0.001` over K=16 samples), the crossing fires in the curvature channel
  at every d ∈ [0,4] in the tuned probe (dpb=0.01, decay=0.002, non-saturating grid 3123–5754/6400
  cells) and does NOT fire in the baseline-pheromone control (same detector, 0/3 — the
  saturating rule never elevates the pheromone cue enough). crossing_step decreases 1550→900 as
  d rises; n_pillars falls 12→1 (consolidation); roughness rises 0.44→0.77. **Session 20
  (2026-08-04) recruit-vs-limit isolation:** a 2×2 factorial (recruit ON/OFF × limit ON/OFF)
  with a seed-robustness pass (4 seeds) found the recruit half (curvature routing) is necessary
  and almost-sufficient for a *stable* crossing: recruit-only (d=0) is stable 3/4 seeds (hold
  1.00 in 3, 0.65 in the borderline seed); neither (no recruit, no limit) is 0/4. The limit
  half (biharmonic d-smoothing) alone is never stable (0/4 — criteria flicker, hold 0.40–0.55,
  because the smoothing shapes convex geometry no agent is routed to; criterion 3
  `deposits_on_convex_fraction` oscillates around 0.60). But the limit half is a **stability
  amplifier**: recruit+limit is stable 4/4 where recruit-only is 3/4 — the borderline seed
  becomes fully stable (hold 1.0) when d>0 is added. So "recruit as well as limit" = recruit
  necessary + almost-sufficient; limit = stabilizer + morphology optimizer (causal, not
  strictly necessary). The decisive contrast is recruit ON vs OFF at d=0 (same detector, same
  regime, only the recruit flag differs). **Session 21 (2026-08-05) saturating-action control:**
  the same curvature routing but a saturating response `p = base + gain·c/(1+|c|)` instead of
  linear `p = base + gain·c` — both action-based, only the linear form non-saturating. The
  saturating action crosses in 8/8 seeds (stable 6/8) vs linear 8/8 (stable 7/8); the limit half
  rescues both to 4/4 at d=1. ACTION-BASED routing is the primary load-bearing property;
  NON-SATURATING is a secondary stability amplifier (mean hold drops 0.91→0.86 at d=0;
  criterion 3 holds 1.00 for both forms — saturation slows mass equilibration, not spatial
  selectivity). H11's strict "non-saturating" claim is partially weakened: a saturating
  action-based channel still crosses stably, but less robustly. Determinism verified. See
  `saturating_action_sweep.py`, `recruit_limit_sweep.py`, `dstar_sweep.py`, `sim09.py`
  (corrected `detect_crossing`), and
  [`sim09`](https://alife.vancedubberly.com/sim09_curvature_channel/visualize.html).
- **SESSION 22 (2026-08-06) cue-based non-saturating control — the 2×2 completes, non-saturating
  REVERSES SIGN across families.** sim06's as-built saturating cue `p = base + gain·φ/(1+φ)` was
  contrasted with a non-saturating (linear) cue `p = base + gain·φ` (clamped to 1.0), both cue-based.
  Seed-42 factorial (64 conditions): saturating cue crosses 32/32 (stable 32/32, hold 1.000); linear
  cue crosses 19/32 (stable 16/32, hold 0.527). **Without self-maintenance: saturating cue 16/16
  stable; linear cue 0/16 stable.** With SM: both 16/16 stable. Seed robustness (4 seeds) confirms.
  The non-saturating property helps in the action family (sim09: 7/8 vs 6/8) but HURTS in the cue
  family (sim06: 0/16 vs 16/16 w/o SM) — a sign reversal. **Mechanism: deposit-probability
  clamping.** The linear cue hits p=1.0 at φ≈1.15 — every high-pheromone cell deposits at 100%,
  flattening the gradient; mean pheromone over structure drops to 0.467 (vs saturating's 0.749),
  below the 0.5 crossing threshold. The saturating cue's `φ/(1+φ)` compression *prevents*
  deposit-probability saturation and preserves spatial contrast. The "self-defeating" channel is
  the **non-saturating cue** (deposit-probability clamping), not the saturating cue — H11's
  original framing was backwards for the cue family. Self-maintenance rescues the linear cue (4/4
  stable) by sustaining pheromone elevation regardless of the response curve. See
  `cue_response_sweep.py` and `sim06.py` (`deposit_response` parameter, selftest Part 5d).
- Does the crossing compose? — the L2 question with a non-saturating glue (#62) remains the
  next major test.
- **Does the φ_sat predictor generalize? — DONE (Session 23). NO.** The deposit-probability
  saturation threshold (φ_sat = the input at which p_deposit first reaches 1.0) was tested as
  a unifying diagnostic across all four cells of the 2×2. A direct probe (`phi_sat_probe.py`)
  of sim06 (cue) and sim09 (action) at their crossing-proven regimes found the predictor is
  **50% accurate — no better than chance.** It correctly predicts the cue family (saturated→fails,
  unsaturated→crosses) but fails for the action family: action/linear is saturated (max curvature
  2.55 > c_sat 1.165, clamp fraction 1.0%) but still crosses stably. The clamping fraction is
  tiny everywhere (0–7%). The difference: in the cue family, the deposit probability IS the
  spatial signal — clamping it destroys the gradient. In the action family, spatial contrast
  lives in the **routing decision** (which direction the termite moves), not the deposit
  probability — the response curve saturates the *gain* (how hard to deposit), not the *routing*
  (where to go). The unifying diagnostic is **whether spatial contrast in the routing input
  survives the response curve**, which depends on channel architecture, not just the saturation
  threshold. Determinism verified. See `phi_sat_probe.py` and H7/H11 Session-23 refinements.
- **Does the crossing produce targeted scar repair? — DONE (Session 24). NO.** The
  spatially-targeted recovery metric (`patch_recovery_probe.py`, queued-topic #60)
  added a `patch_recovery` (material in the damaged patch / pre-damage patch material)
  and a `mirror_recovery` control (an undamaged same-size region's growth). The grid-wide
  `recovery` conflated scar repair with volume restoration — the baseline's 47× was
  unbounded accumulation. `targeted_repair = patch_recovery − mirror_recovery` is
  **negative in all four conditions** (tuned: curvature −1.95, baseline −1.65; default:
  curvature −0.60, baseline −51.0). Neither channel preferentially repairs the damage
  site; the scar grows slower than an equivalent undamaged region (re-nucleation lag)
  in every case. The crossing fires (stability, roughness, mass-plateau) but the
  structure does not self-repair in the targeted sense. The crossing is a
  stability/persistence claim, not a scar-targeting claim. The Session 17 "self-repair"
  report was an artifact of the grid-wide metric. Determinism verified. See
  `patch_recovery_probe.py` and H7 Session-24 refinement.
- Can the three channels be separated in simulation (curvature alone, humidity/evaporation
  alone, crowding alone) to identify which is load-bearing for the crossing? Facchini 2024 says
  curvature ≡ evaporation, so those two are one channel; crowding (Xiao 2026) is the independent
  third. sim09 tests the curvature/evaporation channel; the crowding channel is a candidate sim10.
- **Does the crossing compose? — DONE (Session 25). NO.** sim10 ran two
  curvature-channel structures in adjacent regions of one grid (shared
  field, shared agent pool, one-seed control, baseline-pheromone control).
  At the H7 crossing regime (decay=0.002), **15/16 two-seed runs merge
  into a single structure crossing the midline** — the curvature channel
  consolidates too aggressively for coexistence. The first L2 detector
  (per-region material retention) was broken: the one-seed control fired
  "coexist" because a single structure fills both halves (the control-arm
  lesson #75 again). The corrected detector counts connected components
  lying entirely within each region (crossing the midline = merged). The
  1-seed control then correctly fires 0/16 coexist. The offset×decay sweep
  (384 runs) found coexistence at higher erosion, but the 1-seed control
  fires there too (fragmentation, not composition). The non-saturating
  glue composes no better than the saturating control (2-seed coexist:
  25/96 curvature vs 21/96 baseline; 1-seed: 16/96 vs 22/96). The crossing
  is a single-structure phenomenon; L2 needs a boundary mechanism the
  curvature channel lacks. Determinism verified. See `sim10_l2_composition/`
  and H7/H10 Session-25 refinements. **Honest nuance:** at higher decay
  (the fragmentation regime), the curvature channel shows a modest
  stable_l2 advantage over the 1-seed control (+11/80 vs +3/80 for
  baseline), but the 1-seed control still fires there (16/80 coexist),
  so this is partial composition at best, not clean L2 emergence.
- **Session 26: the boundary mechanism (long-range inhibition).** sim11
  added the Turing/Gierer-Meinhardt long-range inhibitor
  (`I = max(0, far_smoothed_material − material)` — self-cancelling:
  zero at structures, high in the gap). At g=0.9, 2/4 seeds show clean
  composition (2-seed coexist AND 1-seed does NOT) — up from 0/4 with no
  inhibition. But 2/4 fragment (the 1-seed control fires too), and
  stable_l2 shows no stable advantage (0/4 at all gains). The H7
  crossing survives inhibition (h7=4/4). **The self-cancelling
  inhibitor is the critical design insight**: a simple smoothed-material
  inhibitor is always highest AT the structure (self-defeating) — it
  killed all building. The subtraction (far − local) isolates the
  distant-structure signal from the local-structure signal, so the
  inhibitor acts only in the gap. This is a general principle: a
  long-range inhibitor must not self-inhibit. The composition problem is
  not just missing lateral inhibition; even the textbook boundary
  mechanism produces only weak, non-robust partial coexistence.
- Is the state-gating (loaded vs seeking) essential, or does a deposit-only curvature rule
  (deposit at convex tips, no excavation) suffice to consolidate? Facchini's growth model uses
  only growth (no excavation term) and still reproduces morphology.
- How does curvature feedback relate to the directed-transport candidate
  (environmental-physics coupling)? Curvature *is* directed geometry — the Facchini growth
  equation routes building along convex tips, which is the minimal lumped form of "channel
  geometry carrying cue to building fronts." sim09 may unify the directed-transport and
  non-saturating-inhibition candidates into one mechanism, as queued-topic 58 predicted.

## Cross-References

- [[hypotheses/H11]] — the saturating channel hypothesis; this file is its biological grounding
- [[hypotheses/H7]] — the trace→actor crossing; non-saturating channels are the candidate
  mechanism the crossing needs
- [[concepts/stigmergic-consolidation]] — names the negative-feedback gap; this file supplies the
  biological channels that fill it
- [[concepts/environmental-physics-coupling]] — the directed-transport candidate; curvature may
  be its geometric minimal form
- [[concepts/stigmergy]] — the base mechanism; the cement pheromone assumption is in doubt
- [[concepts/multi-rate-environment]] — humidity template's wind-perturbation is a multi-rate
  external driver acting through a non-saturating channel

## Session 27: The Autopoietic Boundary — Memory Buys Persistence, Costs Specificity

sim12 added an autopoietic boundary field B with its own growth/decay
dynamics: `B_new = B * (1 − b_decay) + b_growth * co_presence`, where
`co_presence = min(left_shadow, right_shadow)` — the overlap of the two
structures' far-field shadows. B suppresses deposit probability in the gap,
like sim11's passive I, but B has a time constant of its own (half-life ~138
steps) — it has **memory**.

**The autopoietic boundary is more stable.** In a 4-seed robustness sweep,
B produces stable coexistence in 4/4 seeds (vs 1/4 for the passive). It
survives a 50% material-removal perturbation (B retains 91% at 100 steps;
the coexistence persists). This is the first perturbation in this project
where coexistence actually persists through a structural shock — the
memory gives B a persistence the passive I lacks.

**But its memory also creates false boundaries.** The 1-seed control fires
in 2/4 (vs 1/4 for the passive) — B's memory accumulates co-presence from
a single structure's spread across the torus. The co-presence signal (min
of left and right shadows) was designed to be specific to two-structure
interaction, but on a small torus the single seed's shadow wraps around,
and agent-deposited material in both halves creates a non-zero co-presence
even for one seed.

**Clean composition is 2/4 for both — the memory-specificity trade-off
cancels out.** The autopoietic boundary trades specificity for stability.
The missing ingredient is not just autopoiesis (memory) or a boundary
mechanism — it is a mechanism that combines memory with specificity. The
boundary needs both properties on separate wires: (1) persistence
(autopoiesis — memory, self-maintenance through perturbation) and (2)
specificity (the boundary exists because TWO structures interact, not
one). This is the temporal analog of the two-wire principle (#73) and the
self-cancelling inhibitor (#82).

### Session 28 — Direct-material co-presence: the torus leak was not the cause

sim13 replaced sim12's diffused-shadow co-presence (which wraps on the
torus, creating false boundaries) with a direct-material max filter (no
x-wrapping). The initial 1-seed co-presence drops to <1% of the 2-seed
value — the torus leak IS eliminated. But the 1-seed control still fires
1/4 (seed 123) — **agent wander on the torus deposits material in both
halves, creating real co-presence from a single structure**. The false
boundaries are not caused by the diffusion wrapping; they are caused by
agent wander.

A radius sweep (8-30) reveals a breadth-specificity dimension of the
trade-off: small radius → boundary too narrow → structures merge; medium
radius → agent-wander false positives; large radius → b_scale
normalization produces clean composition for 1 seed but fragmentation
(3/4). At no radius does the direct-material approach achieve better than
1/4 clean composition — strictly worse than sim12's 2/4.

**The memory-specificity trade-off is not a property of the co-presence
signal — it is a property of the system.** Agents on a torus distribute
material everywhere, and any boundary broad enough to prevent merging is
also broad enough to pick up wander material. The fix is not a better
spatial filter — it is a mechanism that keeps agents near their structure
(agent fidelity, heterogeneous policies). A spatial filter can detect
WHERE material is but cannot determine WHICH structure it belongs to.

### Session 29 (2026-08-13) — ID-tagged agents: structural specificity, strength-vs-growth trade-off

sim14 tested agent-level fidelity: each termite carries a structure ID (0=left, 1=right). Deposits are tagged with the depositor's ID. Co-presence = min(dilate(material_by_id[0]), dilate(material_by_id[1])). For a single seed, all material is id=0 — co-presence is **structurally zero** (B_max=0.0 across all seeds). The 1-seed control is 0/4 on ALL metrics — the first structurally clean composition.

**The false-positive mechanism is broken.** Compare: sim12 shadow 1-seed l2=4/4, coexist=2/4; sim13 direct 1-seed l2=4/4, coexist=1/4; sim14 hetero 1-seed l2=0/4, coexist=0/4. Agent IDs provide structural specificity that no spatial filter can: the boundary grows only where two DISTINCT agent populations meet.

**But the H7 crossing is suppressed (0/4).** The ID-based co-presence is higher and more localized, producing a stronger B that suppresses growth below the crossing threshold (cells: 167 vs 3714 for shadow). Clean composition is 2/4 (matching shadow/passive).

**The trade-off shifts from specificity-vs-memory to strength-vs-growth.** Sessions 27-28: memory (persistence) vs. specificity (no false positives). sim14 resolves specificity — agent IDs are structurally specific. But the stronger boundary suppresses the structures it protects. The crossing (self-maintenance) and composition (interaction) are now in tension, not just separable. The missing ingredient is a mechanism that decouples boundary strength from boundary specificity.

### Session 30 (2026-08-14) — inh_gain sweep: the trade-off is partially breakable

The inh_gain sweep tested sim14's ID-tagged boundary at five gains (0.1, 0.3, 0.5, 0.7, 0.9) with 4-seed robustness, mapping the strength-vs-growth frontier. Session 29 tested only g=0.9 (too strong — H7=0/4). The sweep asks: is there a gain where both H7 crossing AND L2 composition co-occur?

| gain | l2(2s) | coexist | stable | h7(2s) | clean | l2(1s) | h7(1s) | cells |
|------|--------|---------|--------|--------|-------|--------|--------|-------|
| 0.1  | 0/4    | 1/4     | 0/4    | 4/4    | 1/4   | 0/4    | 4/4    | 4107  |
| 0.3  | 2/4    | 1/4     | 1/4    | 4/4    | 1/4   | 0/4    | 4/4    | 3515  |
| 0.5  | 4/4    | 2/4     | 0/4    | 4/4    | 2/4   | 0/4    | 4/4    | 2672  |
| 0.7  | 4/4    | 1/4     | 0/4    | 4/4    | 1/4   | 0/4    | 4/4    | 1383  |
| 0.9  | 4/4    | 2/4     | 2/4    | 0/4    | 2/4   | 0/4    | 4/4    | 194   |

**The trade-off is partially breakable.** At g=0.5, H7=4/4 and L2=4/4 co-occur with 2/4 clean composition — the first co-occurrence of crossing and composition. At g=0.3, seed 999 achieves stable composition WITH H7 crossing — the single best co-occurrence. But stable composition (2/4 at g=0.9) comes at the cost of H7 suppression (0/4).

**The 1-seed control is 0/4 at ALL gains.** The structural specificity of agent-level tagging holds across the entire strength spectrum — it is not a parameter artifact but a structural property.

**The tension is between crossing and *stable* composition, not crossing and composition per se.** At g=0.5 (H7=4/4, L2=4/4), stable=0/4 — the composition is present but transient. At g=0.9 (stable=2/4), H7=0/4. The boundary strength that stabilizes composition is the same strength that suppresses the crossing's self-maintenance. The trade-off is parameter-dependent, not fundamental, but is not robust (seed-dependent, rarely stable).

**The missing ingredient is refined.** Session 29 said "decouple boundary strength from boundary specificity." Session 30 sharpens: specificity is solved at all gains (1-seed 0/4). The missing ingredient is "decouple boundary strength from growth suppression" — a boundary whose suppression is independent of the co-presence signal's magnitude (queued-topic #92), or agent movement restriction (queued-topic #93).

### Session 31 (2026-08-15) — decoupled boundary: binary vs gradient suppression

The decoupled boundary sweep (queued-topic #92) tested whether decoupling boundary strength from co-presence precision breaks the strength-vs-growth trade-off. The decoupled mode uses fixed suppression (`supp = g` wherever B exists, `B_norm > 0.01`) instead of proportional suppression (`supp = g * B_norm / (1 + B_norm)`). Same B field, same b_scale, same gains — only the suppression curve shape differs.

**H7 is unchanged between modes.** Both preserve H7 at g=0.3–0.7 (4/4) and suppress at g=0.9 (0/4). The crossing depends on overall structure growth, not the boundary's suppression curve shape.

**The suppression curve's SHAPE matters for stability, not just its magnitude.** A binary gate (full suppression or none) produces MORE STABLE composition than a gradient gate (proportional suppression) at the same max gain:

| mode | gain | l2(2s) | coexist | stable | h7(2s) | clean | cells |
|---|---|---|---|---|---|---|---|
| proportional | 0.5 | 4/4 | 2/4 | 0/4 | 4/4 | 2/4 | 2672 |
| decoupled | 0.5 | 2/4 | 1/4 | **2/4** | 4/4 | 1/4 | 2584 |
| proportional | 0.9 | 4/4 | 2/4 | 2/4 | 0/4 | 2/4 | 194 |
| decoupled | 0.9 | 4/4 | 2/4 | **4/4** | 0/4 | 2/4 | 204 |

But the binary gate produces LESS L2 formation (g=0.5: 4/4→2/4). The gradient provides a wider zone of partial suppression that better prevents merging; the binary gate's sharp cutoff leaves a narrower barrier. The trade-off: binary = narrower but stronger (more stable); gradient = wider but weaker (more formation).

**A new stable co-occurrence.** Decoupled g=0.7 seed=999 achieves H7=YES + coexist + stable — the first stable co-occurrence at g=0.7 (proportional mode's only stable co-occurrence was g=0.3 seed=999).

**The 1-seed control is 0/4 at ALL gains in BOTH modes.** The structural specificity guarantee holds regardless of the suppression curve.

**The persistence-formation trade-off.** Persistence (stability) and formation (L2 crossing) respond to different properties of the suppression curve: persistence needs full strength (binary); formation needs wide coverage (gradient). This is a new axis of the trade-off — not strength vs growth, but gradient vs binary. The missing ingredient is a boundary whose curve shape provides both wide coverage (formation) and full strength (persistence).

## Session 32: The Hybrid Suppression Curve

Queued-topic #99: a clipped gradient `supp = min(g * B_norm / (1 + B_norm), g * k)` — proportional at low B_norm (gradient coverage for formation) with a fixed plateau at g*k (stability without full-strength binary gate). The SVM hinge-loss-cap analogy: cap the loss to prevent overfitting (cap the suppression to prevent over-killing the crossing).

**The hybrid cap PRESERVES the H7 crossing at g=0.9 where both proportional and decoupled lose it.** At g=0.9: proportional H7=0/4, decoupled H7=0/4, hybrid_k08 H7=4/4. The cap at g*k reduces max suppression below the crossing-killing threshold (transition between g*k=0.72 and 0.81). This refines Session 31's claim that "H7 is independent of the suppression curve": the crossing is independent of the curve SHAPE at a given max suppression, but NOT independent of the max suppression magnitude. H7 depends on max supp (g*k), not gain (g) or curve shape.

**A new stable co-occurrence at g=0.9.** hybrid_k05 g=0.9 seed=123 achieves H7=YES + coexist + stable — the first stable co-occurrence at the highest gain with H7 preserved. Both pure modes lose H7 at g=0.9 (the gain that produces the most stable composition: decoupled stable=4/4 at g=0.9). The hybrid with low k extends H7 into the high-stability regime.

**The hybrid produces MORE clean co-occurrences overall.** hybrid_k08: 5 clean (1 stable); hybrid_k07: 4 clean (2 stable); proportional: 4 clean (1 stable); hybrid_k05: 3 clean (2 stable); decoupled: 2 clean (1 stable); hybrid_k09: 2 clean (1 stable). The hybrid generates more composition events than either pure mode.

**But the persistence-formation trade-off is only PARTIALLY broken.** At g=0.9: hybrid_k05 achieves stable (2/4) but L2=2/4; hybrid_k07/08 achieve L2=4/4 but stable=0/4. The trade-off shifts from "H7 vs stability" (proportional/decoupled) to "H7+L2 vs H7+stable" (hybrid). The full co-occurrence (H7 + L2 + stable + clean) remains 2/4 at best (hybrid_k07 at g=0.5, g=0.7) — the same ceiling as both pure modes.

**The trade-off is about max suppression magnitude.** The hybrid's key insight: H7 depends on the max suppression (g*k), not the gain (g) or the curve shape. At g=0.9, proportional (max supp=0.9) and decoupled (max supp=0.9) both lose H7; hybrid_k08 (max supp=0.72) preserves it. The composition problem is not about finding the right curve shape — it's about the fundamental tension between max suppression high enough for stability and low enough for the crossing.

**The cap as saturation prevention.** The hybrid cap is structurally analogous to MAX-MIN Ant System's τ_max bound (Stützle & Hoos, 2000): bounding the maximum value to prevent stagnation. The hybrid bounds the maximum suppression rather than the maximum pheromone, but the principle is the same: unbounded feedback kills the system; a cap preserves responsiveness. This connects to H11's two-wire principle: combining formation (gradient) and persistence (plateau) on one wire (the B field) partially works, but the tension persists because the cap constrains both.

### Session 33: The dual mode — two-wire principle confirmed

**Separate B fields with different dynamics break the persistence-formation trade-off for stability.** The dual mode uses two B fields: B_form (gradient suppression, faster decay 2× default — responsive, wide coverage for formation) and B_persist (binary suppression, slower decay 1× default — memory, plateau for persistence). Total suppression = min(g_form * Bf_norm/(1+Bf_norm) + g_persist * [Bp>0.01], 0.99).

**Best config: dual f=0.3 p=0.3 (max_supp=0.60).** H7=4/4, L2=4/4, clean=2/4, **stable=3/4**. The 3/4 stable rate is the highest ever achieved with full H7 AND full L2. At the same L2 and clean rates as proportional g=0.5 (which had stable=0/4), stability improved from 0/4 to 3/4. The two-wire principle works: separate dynamics (faster decay for formation, slower for persistence) break the trade-off that single-wire modes (proportional, decoupled, hybrid) could not.

**But the full co-occurrence (H7+clean+stable) is 1/4.** The 3/4 stable includes seeds where the composition is stable but not clean (fragmented, or merged at the end). The ceiling is about outcome quality, not stability.

**The max suppression threshold holds across channel architectures.** H7=4/4 at max_supp ≤ 0.70, partial (1-2/4) at 0.80, 0/4 at ≥ 0.90. The threshold between 0.72 and 0.81 (Session 32) is independent of whether the boundary uses one wire or two.

**The 1-seed control is 0/4 at ALL 9 configs.** Both B fields are structurally zero for a single seed (ID-tagged co-presence = 0 → both B_form and B_persist = 0).

**The two-wire principle in its purest form.** The family of "separate wires" principles (two-wire #73, self-cancelling inhibitor #82, memory-specificity #86) all say the same thing: when two properties are carried on the same wire, saturating one destroys the other. The dual mode is the strongest confirmation: formation and persistence on the same B field (one wire) could not achieve 3/4 stable; on separate B fields with different dynamics, they can.

### Session 34: Agent movement restriction breaks the outcome-quality ceiling

**Agent spatial fidelity is a third axis.** Eleven boundary mechanisms (Sessions 25-33) could not break the outcome-quality ceiling (clean vs fragmented vs merged). The twelfth mechanism — agent movement restriction (focal-point attraction) — breaks it: full co-occurrence (H7+clean+stable) goes from 1/4 → 4/4 at movement_bias ≥ 0.3.

**Mechanism: agent wander was saturating the co-presence signal.** When agents wander freely (bias=0.0), their ID-tagged material spreads across both halves of the torus, making co-presence high everywhere — not just at the boundary. The B field grows diffusely, creating fragmented or merged boundaries. Movement_bias concentrates each ID's material in its home region, reducing co-presence outside the boundary and making the boundary signal sharper. This is the spatial analog of the two-wire principle: the boundary signal (co-presence → B) and the spatial noise (agent wander) were on the same wire — movement_bias separates them by reducing the noise.

**The transition is sharp: bias=0.0 → 1/4, bias=0.3 → 4/4.** No intermediate values. H7 crossing is preserved at 4/4 across all bias values (max suppression 0.60 is well below the 0.72-0.81 threshold). The 1-seed control is 0/4 at all bias values. Structures get smaller with higher bias (cells: 2031→1375) but remain clean, stable, and H7-crossing.

**Cross-domain: Richardson et al. (2022, Nature Comms).** Real social insects achieve spatial fidelity through LOCAL mechanisms — locomotion adjustment (changing movement diffusivity by zone) and boundary effects (turning at zone edges) — NOT through focal-point attraction (global bias toward a center point). Our simulation uses the simplest global mechanism and still produces a dramatic improvement. But the biological evidence suggests local mechanisms might be even more effective. The key insight: spatial fidelity is necessary for clean composition, regardless of the mechanism. The composition problem is as much about agent distribution as about boundary design.

**The three-wire principle.** The family of "separate wires" principles extends: (1) two-wire principle (#73): feedback signal and spatial signal on separate channels; (2) self-cancelling inhibitor (#82): distant signal and local signal on separate wires; (3) memory-specificity (#86): persistence and specificity on separate wires; (4) dual mode (S33): formation and persistence on separate B fields; (5) agent distribution (S34): boundary and agent movement on separate axes. All five say the same thing: when two properties are carried on the same wire, saturating one destroys the other.

### Session 35: Local movement mechanisms — the stigmergic feedback loop is self-defeating

**Biologically-grounded local movement mechanisms (Richardson et al. 2022) fail where global focal-point attraction succeeds.** Two local mechanisms that real social insects use were implemented: (1) boundary effects — agents turn back when they encounter the B field (closes a stigmergic loop: B → movement → co-presence → B); (2) locomotion adjustment — agents move slowly inside their home half, quickly outside.

| mode | coexist | stable | clean | full | cells | b_max |
|------|---------|--------|-------|------|-------|-------|
| none (no restriction) | 2/4 | 3/4 | 2/4 | 1/4 | 2031 | ~48 |
| focal (global, bias=0.3) | 4/4 | 4/4 | 4/4 | 4/4 | 1770 | ~33 |
| boundary (local, stigmergic) | 0/4 | 0/4 | 0/4 | 0/4 | 951 | ~104 |
| diffusivity (local, zone-based) | 1/4 | 1/4 | 1/4 | 0/4 | 2665 | ~48 |

**The boundary mode is self-defeating — the stigmergic feedback loop over-amplifies B.** When agents turn back at high B, they concentrate material → increase co-presence → grow B → more agents turn back. This positive feedback pushes b_max to 70-203 (vs 30-50 for focal), fragmenting all structures (4/4 fragmented, 0/4 coexist). The B field serves double duty — deposit suppression AND agent movement — and the feedback amplifies B beyond what deposit suppression needs. This is the same pattern as H11's saturating cue channel: the feedback signal (B) and the spatial signal (agent distribution) on the SAME WIRE.

**The focal mode succeeds because it uses SEPARATE wires.** B → deposit suppression (feedback signal); fixed home center → agent movement (spatial signal). The movement target doesn't depend on the emergent B field, so no feedback loop amplifies it.

**The two-wire principle's sixth member: movement-wire decoupling.** The family now has six members:
1. Two-wire (#73): feedback signal and spatial signal on separate channels
2. Self-cancelling inhibitor (#82): distant signal and local signal on separate wires
3. Memory-specificity (#86): persistence and specificity on separate wires
4. Dual mode (S33): formation and persistence on separate B fields
5. Agent distribution (S34): boundary and agent movement on separate axes
6. Movement-wire decoupling (S35): deposit suppression and agent movement on separate signals

**Cross-domain: Richardson et al. (2022) — real insects use local mechanisms with separate sensory channels.** Real social insects achieve spatial fidelity through local mechanisms (boundary effects, locomotion adjustment), but they have richer sensory channels (chemical blends on nest surfaces) that provide separate wires for zone identification vs. boundary detection. Our simulation's B field is the only available signal, so using it for both deposit suppression and agent movement creates the self-defeating loop. The biological lesson is not that local mechanisms fail — it's that local mechanisms require separate sensory channels to avoid the self-defeating feedback.

**H7 crossing is 4/4 across ALL modes.** The crossing is independent not just of agent movement magnitude (Session 34) but of the movement MECHANISM. The 1-seed control is 0/4 at all modes.

### Session 36: Zone mode — separate sensory channel breaks the loop but doesn't recover composition

**The zone mode gives agents a separate sensory channel: own-ID material (dilated) for zone identification, NOT B for deposit suppression.** Session 35 predicted that local mechanisms need separate sensory channels (Richardson et al. 2022). The zone mode implements this: agents read their own ID's material to determine zone membership, and B for deposit suppression. The movement signal (own-ID material) is independent of B — no B → movement feedback can amplify.

| mode | coexist | stable | clean | full | cells | b_max |
|------|---------|--------|-------|------|-------|-------|
| none (no restriction) | 2/4 | 3/4 | 2/4 | 1/4 | 2030 | 47.9 |
| focal (global, bias=0.3) | 4/4 | 4/4 | 4/4 | 4/4 | 1770 | 32.9 |
| boundary (local, stigmergic) | 0/4 | 0/4 | 0/4 | 0/4 | 951 | 104.5 |
| zone (separate channel) | 0/4 | 1/4 | 0/4 | 0/4 | 1873 | 50.2 |

**The stigmergic feedback loop IS broken (b_max 50.2 ≈ none's 47.9 vs boundary's 104.5).** The zone mode's b_max is nearly identical to the no-restriction baseline — the B → movement → co-presence → B loop is absent. The boundary mode's 2× amplification was the loop's signature; the zone mode eliminates it. This confirms Session 35's diagnosis: the movement-wire coupling (not the movement mechanism per se) is the causal variable.

**But composition is WORSE than no restriction (0/4 coexist vs 2/4 for "none").** The separate wire exists but carries a noisy signal. The zone signal (dilated own-ID material) is endogenous (depends on agent deposits) and diffuse (dilation spreads it). Agents outside their zone take large steps toward home; inside, small random steps. The large-step-outside rule fragments structures (3/4 fragmented). The focal mode's signal (fixed home center) is exogenous and precise — it tells agents exactly where to go.

**The two-wire principle's seventh member: signal quality on the separate wire.** A separate wire with a noisy signal doesn't recover the function. Breaking the feedback loop is necessary but not sufficient — the replacement signal must also be precise enough to concentrate agents effectively. The focal mode's exogenous fixed-center signal is the gold standard; the zone mode's endogenous dilated-material signal is too coarse.

**The 1-seed control: l2_crossed=0/4 (structural guarantee holds), but l2_outcome has a new leak (1/4 "coexist").** The movement restriction fragments the single-seed structure, creating components on both sides of the midline. The l2_crossed metric (sustained persistence) is 0/4, but the outcome classifier (final-state) flags "coexist" in 1/4. This is a new failure mode: the movement mechanism itself creates spurious multi-region components.

**H7 crossing is 4/4 across all modes.** The crossing is independent of the movement mechanism and the movement signal quality. The 1-seed control is 0/4 on l2_crossed at all modes.

**Determinism verified** (zone seed=42: fragmented, 2007 cells — identical across two runs).

### Session 37: Home-jitter sweep — exogeneity is the load-bearing property

**The focal mode's advantage is exogeneity (loop-breaking), not precision (noise-free).** Session 36 asked whether the focal advantage comes from being exogenous (unreachable by the system's feedback loop) or precise (noise-free). The home-jitter sweep added Gaussian noise to the focal home center: jitter ∈ {0, 2, 5, 10, 20, 40} cells (0–50% of the 80-cell grid).

| jitter | l2(2s) | coexist | stable | h7(2s) | clean | full | l2(1s) | h7(1s) | cells | b_max |
|--------|--------|---------|--------|--------|-------|------|--------|--------|-------|-------|
| 0.0 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4/4 | 1770 | 32.9 |
| 2.0 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4/4 | 1886 | 35.5 |
| 5.0 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4/4 | 1932 | 35.8 |
| 10.0 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4/4 | 1970 | 41.1 |
| 20.0 | 2/4 | 1/4 | 0/4 | 4/4 | 1/4 | 0/4 | 0/4 | 4/4 | 2022 | 46.9 |
| 40.0 | 3/4 | 3/4 | 3/4 | 4/4 | 3/4 | 2/4 | 0/4 | 4/4 | 2034 | 49.0 |

**A noisy exogenous signal (jitter=10, 12.5% of grid) preserves 4/4 full co-occurrence.** The signal stays exogenous (drawn from the RNG, not from the system state), so no feedback loop can amplify it — even when noisy. Up to 12.5% of the grid, the jitter is pure noise that averages out over 2000 steps; the agents still converge to their correct home regions.

**The collapse at jitter=20 is misdirection, not noise intolerance.** At 25% of the grid, the jitter can push the home center past the midline (home_x=20, jitter=20 → home can be at x=0 or x=40, and x=40 is in the RIGHT half for id=0 agents). The agents are sometimes directed to the WRONG half — systematically wrong, not noisy. This is not noise tolerance failing; it is a spatial aliasing artifact.

**The non-monotonic partial recovery at jitter=40 confirms: random direction beats systematically wrong direction.** At 50% of the grid, the jitter is so large that the home center is uniformly random — the agents are rarely directed to the wrong half consistently (the jitter overshoots the midline in both directions). A random home center that is sometimes right (3/4 coexist) outperforms one that is consistently wrong (jitter=20: 1/4 coexist). This non-monotonicity is the signature of misdirection, not noise: if it were noise, the result would degrade monotonically.

**The decisive comparison: noisy exogenous vs noisy endogenous at the same B magnitude.** Jitter=40 (exogenous, b_max=49.0): 3/4 coexist, 3/4 stable. Zone mode (endogenous, b_max=50.2): 0/4 coexist, 1/4 stable. At nearly identical B magnitude, the exogenous signal outperforms the endogenous signal on every axis. The composition problem is not about signal quality in general — it is about whether the signal is reachable by the system's own dynamics. An exogenous signal cannot be shaped by the feedback loop; an endogenous signal is inherently shaped by the dynamics it is trying to control.

**The two-wire principle's eighth member: exogeneity.** The family of "separate wires" principles now has eight members. The eighth refines the seventh: the relevant signal quality is not precision (noise amplitude) but exogeneity (whether the signal is reachable by the system's own dynamics). A noisy exogenous signal outperforms a noisy endogenous signal at the same B magnitude. The signal must not only be on a separate wire — it must be on a wire the system cannot reach.

**H7 crossing is 4/4 at all jitter values.** The 1-seed control is 0/4 at all jitter values. Determinism verified at jitter=20 (fragmented, 1879 cells) and jitter=10 (coexist, 2019 cells) — identical across two runs each.


### Session 38: Per-agent jitter and grid-size scaling — noise structure and density dependence

**Per-agent persistent jitter reverses the mode advantage at high noise.** The per-step jitter (fresh noise each step) is temporally averaged — errors cancel over many steps. The per-agent jitter (fixed at init) is spatially correlated — the error is consistent. At jitter=10 (12.5%): per_step 4/4, per_agent 1/4 coexist — temporal averaging wins. At jitter=20 (25%): per_step 1/4, per_agent 3/4 coexist + 4/4 stable — spatial correlation wins. The crossover is non-monotonic.

| mode | jitter | l2(2s) | coexist | stable | h7(2s) | clean | full | l2(1s) | h7(1s) | cells | b_max |
|------|--------|--------|---------|--------|--------|-------|------|--------|--------|-------|-------|
| per_step | 0.0 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4/4 | 1770 | 32.9 |
| per_step | 10.0 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4/4 | 1970 | 41.1 |
| per_step | 20.0 | 2/4 | 1/4 | 0/4 | 4/4 | 1/4 | 0/4 | 0/4 | 4/4 | 2022 | 46.9 |
| per_step | 40.0 | 3/4 | 3/4 | 3/4 | 4/4 | 3/4 | 2/4 | 0/4 | 4/4 | 2034 | 49.0 |
| per_agent | 0.0 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4/4 | 1770 | 32.9 |
| per_agent | 10.0 | 3/4 | 1/4 | 1/4 | 4/4 | 1/4 | 1/4 | 0/4 | 4/4 | 2145 | 40.3 |
| per_agent | 20.0 | 4/4 | 3/4 | 4/4 | 4/4 | 3/4 | 3/4 | 0/4 | 4/4 | 2038 | 46.4 |
| per_agent | 40.0 | 2/4 | 2/4 | 0/4 | 4/4 | 2/4 | 0/4 | 1/4 | 4/4 | 1954 | 47.7 |

**Mechanism: consistency vs averaging.** At moderate noise, per-step's temporal averaging keeps the mean home center near the true center (errors cancel); per-agent's fixed error doesn't cancel, and some agents are systematically in the wrong half. At high noise, per-step's averaging breaks down (each step can cross the midline, scattering agents); per-agent's fixed error keeps material concentrated — the structure may be misplaced but doesn't fragment.

**Grid-size does not scale the tolerance.** The 160×160 grid at jitter=20 (12.5% of 160, same fraction as 80×80 at jitter=10) produces 0/4 coexist and 0/4 H7. The same 150 termites on 4× the area produce sparser structures. The 1-seed l2 control leaks at 160×160 (2/4 at jit=20, 4/4 at jit=40).

| grid | jitter | frac% | l2(2s) | coexist | stable | h7(2s) | clean | full | l2(1s) | h7(1s) | cells |
|------|--------|-------|--------|---------|--------|--------|-------|------|--------|--------|-------|
| 80 | 0.0 | 0.0% | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4/4 | 1770 |
| 80 | 10.0 | 12.5% | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4/4 | 1970 |
| 80 | 20.0 | 25.0% | 2/4 | 1/4 | 0/4 | 4/4 | 1/4 | 0/4 | 0/4 | 4/4 | 2022 |
| 80 | 40.0 | 50.0% | 3/4 | 3/4 | 3/4 | 4/4 | 3/4 | 2/4 | 0/4 | 4/4 | 2034 |
| 160 | 0.0 | 0.0% | 4/4 | 4/4 | 3/4 | 4/4 | 4/4 | 3/4 | 0/4 | 4/4 | 1674 |
| 160 | 10.0 | 6.2% | 4/4 | 4/4 | 1/4 | 2/4 | 4/4 | 1/4 | 0/4 | 4/4 | 1685 |
| 160 | 20.0 | 12.5% | 4/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 2/4 | 4/4 | 1216 |
| 160 | 40.0 | 25.0% | 4/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 4/4 | 4/4 | 921 |

**The tolerance is about absolute displacement relative to structure density, not jitter/grid fraction.** The composition problem is density-dependent: the same termite count on a larger grid produces sparser structures that are more vulnerable to fragmentation and to the 1-seed control leaking.

**The two-wire principle's ninth member: noise structure on the exogenous wire.** The family now has nine members. The ninth refines the eighth: exogeneity is necessary but not sufficient — the noise structure (temporal vs spatial correlation) must match the noise magnitude. Temporal averaging at moderate noise, spatial correlation at high noise.

**H7 crossing is 4/4 at 80×80 all conditions.** At 160×160, H7 drops with jitter (2/4 at jit=10, 0/4 at jit≥20) — a structure-density effect, not a crossing-mechanism effect. Determinism verified.

## Session 39 — PID D-term: endogenous anticipatory suppression is self-defeating

The PID D-term (queued-topic #103) adds an anticipatory boundary wire to the dual mode: B_deriv grows from the positive part of the co-presence rate of change (cp_delta = max(0, cp - cp_prev)) and decays fast (4× default decay). The D term is anticipatory — it strengthens the boundary BEFORE structures merge, not after.

**At the optimal config (dual f=0.3 p=0.3, focal bias=0.3): the D term is neutral.** 4/4 full co-occurrence at ALL g_deriv (0.0–0.3). The D term neither helps nor hurts — the focal bias already achieves 4/4.

**Without focal bias: the D term is destructive.** The dual-no-focal baseline (g_deriv=0.0) achieves 4/4 L2, 2/4 coexist, 3/4 stable, 1/4 full. Adding g_deriv=0.1 drops stable to 0/4 and full to 0/4. At g_deriv=0.3, coexist collapses to 0/4 (all outcomes fragment). The D term's anticipatory suppression reads the system's own co-presence (endogenous), creating a stigmergic feedback loop: cp rises → B_deriv rises → suppression increases → structures stop growing → cp falls → B_deriv decays → suppression drops → structures grow again → cp rises. This oscillation amplifies rather than damps.

| g_deriv | max_supp | l2(2s) | coexist | stable | h7(2s) | clean | full | l2(1s) | h7(1s) | cells |
|----------|----------|--------|---------|--------|--------|-------|------|--------|--------|-------|
| 0.00 | 0.60 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4/4 | 1770 |
| 0.05 | 0.65 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4/4 | 1794 |
| 0.10 | 0.70 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4/4 | 1797 |
| 0.20 | 0.80 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4/4 | 1831 |
| 0.30 | 0.90 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4/4 | 1705 |

Without focal bias:

| g_deriv | max_supp | l2(2s) | coexist | stable | h7(2s) | clean | full | l2(1s) | h7(1s) | cells |
|----------|----------|--------|---------|--------|--------|-------|------|--------|--------|-------|
| 0.00 | 0.60 | 4/4 | 2/4 | 3/4 | 4/4 | 2/4 | 1/4 | 0/4 | 4/4 | 2031 |
| 0.10 | 0.70 | 3/4 | 3/4 | 0/4 | 4/4 | 3/4 | 0/4 | 0/4 | 4/4 | 1957 |
| 0.20 | 0.80 | 3/4 | 2/4 | 1/4 | 4/4 | 2/4 | 1/4 | 0/4 | 4/4 | 1940 |
| 0.30 | 0.90 | 4/4 | 0/4 | 1/4 | 4/4 | 0/4 | 0/4 | 0/4 | 4/4 | 1848 |
| 0.50 | 1.10 | 3/4 | 3/4 | 0/4 | 4/4 | 3/4 | 0/4 | 0/4 | 4/4 | 1865 |

**The two-wire principle's tenth member: an endogenous anticipatory signal is self-defeating.** The nine previous members all say: when two properties are carried on the same wire, saturating one destroys the other. The tenth adds: when the signal is derived from the system's own state, the feedback loop amplifies oscillations rather than damping them. The D term is the temporal analog of the boundary mode's spatial failure (Session 35): both read an endogenous signal for suppression decisions, both create self-amplifying loops. Only an exogenous anticipatory signal (one the system cannot reach) could be beneficial — and no such signal exists in the current architecture.

**The D term cannot substitute for agent locality.** The focal bias is exogenous (fixed home center, unreachable by system dynamics). The D term is endogenous (cp_delta from co-presence from agent positions). The D term's failure mirrors the boundary mode's failure (Session 35) and the zone mode's failure (Session 36): all three read the system's own state for movement/suppression decisions. The exogenous focal bias remains the only mechanism achieving 4/4 full co-occurrence — the composition problem's missing ingredient is an exogenous signal, not anticipatory dynamics.
