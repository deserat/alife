---
status: active
formed: "Session 13"
connected_to: "stigmergic consolidation, environmental physics coupling, stigmergy, H7, H11, multi-rate environment, niche construction"
topic: "non-saturating stigmergic channels — geometry, humidity thresholds, and crowding as the biological grounding for H11 (sim09 fully implemented)"
key_findings: "Real termite construction is guided by THREE non-saturating, action-based channels rather than by a saturating pheromone field: (1) surface CURVATURE — Calovi et al. 2019 (Phil Trans R Soc B) disambiguated curvature from inclination and height across three orientations and found curvature is the 'consistent and sole driver' of construction in Macrotermes michaelseni; the SAME cue elicits OPPOSING actions depending on the termite's loaded/seeking state. (2) HUMIDITY THRESHOLDS — Carey/Bardunias/Nagpal/Werfel 2021 validated with a robot that termites deposit at the EDGE of the high-humidity zone, a threshold-triggered deposition rule. (3) CROWDING/INACTIVITY — Xiao et al. 2026 (arXiv:2607.19594) frame inactivity under confinement as 'distributed inhibition that prevents saturation.' SESSION 14 UNIFICATION: Facchini et al. 2020 (J R Soc Interface) and 2024 (eLife) showed the curvature and humidity channels are ONE physical quantity — evaporation flux ∝ surface curvature (Langmuir 1918) — and built a curvature-only phase-field growth model (no pheromone field at all) that reproduces real nest morphology. The convex (Facchini: deposit at tips) / concave (Calovi: activity at pits) contradiction is resolved: the two measured different action components (deposition vs aggregate activity). Facchini 2024 explicitly state 'experiments do not support a role for a putative cement pheromone' — two independent groups now report no cement pheromone. SESSION 17 (2026-08-02): sim09 FULLY IMPLEMENTED (all 9 Parts). SESSION 19 (2026-08-03): the d* sweep (100 combos) found 0/100 under the original detector — the mass-saturation gate was an unfalsifiable metric-ceiling bug (threshold ~100× below the Poisson noise floor). Corrected to a relative-slope plateau, the crossing FIRES in the curvature channel at every d in the tuned probe and does NOT fire in the baseline-pheromone control (same detector) — the first H7 crossing with a control arm. SESSION 20 (2026-08-04): the recruit-vs-limit 2×2 factorial isolates the halves. The RECRUIT half (curvature routing) is necessary and almost-sufficient for a stable crossing: recruit-only (d=0) is stable 3/4 seeds (hold 1.00 in 3, 0.65 in the borderline seed); neither (no recruit, no limit) is 0/4. The LIMIT half (biharmonic d-smoothing) alone is never stable (0/4 — criteria flicker, hold 0.40-0.55, because the smoothing shapes convex geometry no agent is routed to). But the limit half is a STABILITY AMPLIFIER: recruit+limit is stable 4/4 where recruit-only is 3/4 — the borderline seed becomes fully stable when d>0 is added. So 'recruit as well as limit' = recruit necessary + almost-sufficient; limit = stabilizer + morphology optimizer (causal, not strictly necessary). Determinism verified."
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
  regime, only the recruit flag differs). Determinism verified. See `recruit_limit_sweep.py`,
  `dstar_sweep.py`, `sim09.py` (corrected `detect_crossing`), and
  [`sim09`](https://alife.vancedubberly.com/sim09_curvature_channel/visualize.html).
- Can the three channels be separated in simulation (curvature alone, humidity/evaporation
  alone, crowding alone) to identify which is load-bearing for the crossing? Facchini 2024 says
  curvature ≡ evaporation, so those two are one channel; crowding (Xiao 2026) is the independent
  third. sim09 tests the curvature/evaporation channel; the crowding channel is a candidate sim10.
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
