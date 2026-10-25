---
status: active
formed: "Session 79"
connected_to: "non-saturating-channels, two-wire-principle, H5, H7, H10, H11, multi-scale-composition"
topic: "the Gompertz-to-logistic transition in stigmergic systems — coherence, percolation, and the three-threshold design principle"
key_findings: "The fill cap trajectory (19 data points, n=550–15000) traces a complete Gompertz-to-logistic transition mediated by percolation. Haugen & Gilbert (2022, arXiv:2211.05653) show Gompertz growth (θ→0) is the coherent limit (long-range interactions dominate, aggregate dynamics depend only on collective mean); logistic growth (θ=1) is the pairwise limit (local interactions dominate). The boundary's coherent suppression is the θ→0 field; percolation (Moore 8-neighbor threshold ~0.407) is the symmetry-breaking transition where local bonds overwhelm the coherent field. Three thresholds: (1) persistence ceiling ~43.6% fill — stable composition impossible above this regardless of gain (30th mechanism, 46th mechanism); (2) fill cap acceleration ~75% fill — the coherent field's capping power begins to break (44th mechanism); (3) saturation ~100% fill — the boundary is irrelevant, g*→0 at n≈14000 (43rd mechanism). Session 94: the 30th ceiling (~43.6%) is NOT the Moore threshold (~40.7%) — gap 2.93pp > noise; three distinct thresholds (Moore ~40.7%, 30th ~43.6%, actual percolation ~59%); the 30th is percolation-adjacent boundary over-splitting, not percolation itself. Design principle: keep the stigmergic system in the Gompertz (coherent) regime, below ~44% fill for stable composition. Session 93: the fill cap's stretched exponential a·exp(b·√n) (R²=0.964) is the diffusion-limited signature — the √n is the diffusion length (boundary's suppression range grows as √n). NOT KJMA (α>1) but diffusion-limited (α=1/2). The √n unifies g*∝1/√n, fill∝exp(b·√n), co-presence∝1/√n."
---

# The Gompertz-to-Logistic Transition in Stigmergic Systems

## The Concept

The boundary's fill-capping mechanism (44th mechanism, Sessions 69–76) follows a
trajectory that maps onto the Gompertz-to-logistic transition in growth theory.
Haugen & Gilbert (2022, arXiv:2211.05653) derive Gompertz growth as the coherent
limit of a microscopic Richards model: a coherence parameter θ sets the coupling
between nodes on a network. At θ→0 (Gompertz), long-range interactions dominate
— each entity contributes linearly to the collective growth rate, and the
aggregate dynamics depend only on the collective mean (invariant to how
fluctuations are distributed). At θ=1 (logistic), pairwise/local interactions
dominate — the macroscopic drift acquires a dependence on microscopic variance.
The coherence parameter acts as a symmetry-breaking parameter.

Our stigmergic boundary is a coherent field: its suppression acts simultaneously
across the entire grid (like the "ubiquitous external field" Haugen & Gilbert
describe). Below the percolation threshold, this coherent field caps fill
logarithmically — the Gompertz regime. Above the threshold, local connectivity
(Moore 8-neighbor bonds) overwhelms the coherent field — the logistic regime.

## The Three Thresholds

The fill cap trajectory (19 data points, n=550 to n=15000) reveals three
thresholds of a single phase transition:

### 1. Persistence ceiling (~44% fill) — the 30th mechanism

The 46th mechanism's strongest form (Session 78): the persistence condition
(stable composition) has a hard density ceiling (~44% fill) independent of
boundary gain. Above this fill, the boundary cannot maintain stable composition
at any gain tested (g=0.0001–0.005). This is the spatial analog of a percolation
threshold for autopoietic boundaries: above the critical fill, the structures'
surface area exceeds what the boundary can suppress, regardless of bond strength
(gain). The boundary's gain is like bond strength; the fill fraction is like
occupation probability. Below the ceiling, the boundary maintains stable
composition; above it, the structures over-fragment.

This is the Gompertz regime's limit: the coherent field can maintain persistence
only below ~44% fill. Above it, the coherence is insufficient — the structures
are too large for the long-range suppression to hold them without over-splitting.

### 2. Fill cap acceleration (~75% fill) — the 44th mechanism breaks

At n=10000 (~75% fill), the fill cap accelerates dramatically (+14.5% from
n=8000's ~61%). The boundary retains ~25% of the grid as inter-structure void
but the fill is no longer logarithmic. The 47th mechanism (bimodal largest-
component fraction, percolation criticality) appears at n=8000 (~61% fill) —
the system flips between percolated (one spanning cluster at ~93%) and non-
percolated (two near-equal halves at ~48%) states. At n=10000, the bimodality
resolves to a single mode at ~97.5% (the 48th mechanism). The boundary's
coherent suppression is at the edge of its capability.

This is the transition regime: the coherent field and local connectivity are
in competition. The bimodality is the signature of percolation criticality —
near the threshold, the system is critical, and the seed determines which side
of the transition it falls on.

### 3. Saturation (~100% fill) — the 43rd mechanism's limit

At n=15000 (~100% fill), the boundary has zero capping power (ncomp=1,
largest_frac=100%). The g* limit sweep (Session 77) found the boundary's capping
power (gap to no-inhibition) decays exponentially: 16.2% → 8.3% → 4.3% → 1.2%
→ ~0 (n=11000 to 15000). The gap halves at each step — exponential decay of
the coherent field's effect. g* hits zero at n≈14000. The boundary becomes
irrelevant when fill ≈ 99%.

This is the logistic regime: local connectivity dominates entirely. The
boundary's long-range suppression is a perturbation the percolated structure
does not feel. The system is fully in the pairwise regime where local bonds
determine the dynamics.

## The Mapping

| Haugen & Gilbert (2022) | Our stigmergic system |
|---|---|
| Coherence parameter θ → 0 (Gompertz) | Low fill (< ~44%): boundary's coherent suppression dominates |
| Coherent field (external, ubiquitous) | Boundary's long-range B field (acts across entire grid) |
| θ = 1 (logistic, pairwise) | High fill (> ~75%): local Moore bonds dominate |
| Symmetry breaking at θ > 0 | Percolation transition (~0.407 Moore 8-neighbor) |
| Aggregate dynamics depend on collective mean only (θ=0) | Fill cap depends on total fill, not distribution between structures |
| Macroscopic drift acquires dependence on microscopic variance (θ>0) | Above percolation, fill depends on local connectivity structure |
| Gompertz growth = coherent limit | Logarithmic fill cap = coherent regime (R²=0.991 sub-percolation) |
| Logistic growth = pairwise limit | Fill → 100% = pairwise regime (local bonds overwhelm) |

The key insight: the boundary's coherent suppression is the stigmergic analog
of the "ubiquitous external field" that Haugen & Gilbert identify as the source
of Gompertz growth. The field acts simultaneously across all entities (grid
cells), producing the logarithmic fill cap. When percolation makes local
connectivity dominant, the coherent field loses its capping power — the
Gompertz-to-logistic transition.

## The Design Principle

**Keep the stigmergic system in the Gompertz (coherent) regime.**

The three thresholds define the design space:
- **Below ~44% fill**: stable composition is possible. The boundary's coherent
  suppression maintains the structures as separated droplets. This is the
  Gompertz regime — the fill cap is logarithmic, the boundary's gain scales as
  1/√n (Laplace pressure), and the 1-seed structural guarantee holds.
- **~44–75% fill**: composition is present but unstable (30th mechanism). The
  coherent field can maintain coexistence but not stable persistence. The fill
  cap is still sub-percolation but accelerating.
- **Above ~75% fill**: the coherent field breaks down (44th mechanism). The fill
  accelerates toward 100%. Composition collapses (coexist → 0/4). The system
  percolates and local bonds overwhelm the boundary's long-range suppression.

The design principle connects to the Gompertz-to-logistic framework: the
Gompertz regime (coherent, long-range) is where composition works; the logistic
regime (pairwise, local) is where it doesn't. The transition is mediated by
percolation — when the structure's local connectivity exceeds the coherent
field's suppression, the system crosses from Gompertz to logistic.

This is a design principle for multi-scale stigmergic systems: the boundary
must be strong enough to keep the system below the persistence ceiling (~44%
fill) but weak enough to avoid over-splitting. The 1/√n (Laplace pressure)
scaling of g* is the signature of the coherent regime — the boundary's gain
scales with the surface-to-volume ratio (∝ 1/√n), which is the geometric
expression of the coherent field's long-range nature.

## Cross-Domain Connections

- **Statistical physics → stigmergy**: the percolation threshold (~0.407 for
  Moore 8-neighbor) is the critical occupation probability where local
  connectivity overwhelms the coherent field. The fill cap's acceleration above
  this threshold is the approach to percolation.
- **Growth theory → stigmergy**: Haugen & Gilbert's coherence parameter θ maps
  to the fill fraction. The Gompertz (coherent) limit is the low-fill regime;
  the logistic (pairwise) limit is the high-fill regime. The transition is
  percolation-mediated.
- **Contact inhibition → stigmergy**: the fill cap is the stigmergic analog of
  contact inhibition in biological tissues (the 44th mechanism). Cells stop
  growing when they reach confluence; the boundary stops the structure from
  filling the grid. The log fill cap's sublinear growth (13.1·log₁₀(n) − 2.14)
  is the spatial analog of Gompertz growth under contact inhibition.
- **Control theory → stigmergy**: the boundary's gain g is like bond strength
  in percolation; the fill fraction is like occupation probability. The 30th
  mechanism (persistence ceiling independent of gain) says the topological
  transition (percolation) dominates over the dynamical parameter (gain) — the
  same way the percolation threshold is independent of bond strength.

## The Gompertz-to-Logistic Transition as a Phase Diagram

The fill cap's complete trajectory (13 points, Sessions 69–76):

| n | fill% | regime | mechanism |
|---|---|---|---|
| 1200 | 38.3% | Gompertz (coherent) | Log fill cap, 1/√n scaling |
| 1500 | 39.4% | Gompertz | |
| 1800 | 40.4% | Gompertz | |
| 2000 | 41.2% | Gompertz | |
| 2500 | 42.1% | Gompertz (edge) | |
| 3000 | 43.6% | **Persistence ceiling** | 30th mechanism: stable 0/4 |
| 4000 | 45.8% | Transition | 30th persists; coexist degrades |
| 5000 | 48.0% | Transition | Coexist 0/4 |
| 6000 | 50.6% | Transition | |
| 8000 | 60.7% | **Percolation criticality** | 47th: bimodal (93% vs 48%) |
| 10000 | 74.1% | **44th breaks** | 48th: spanning ~97.5%, 25% void |
| 12000 | 91.6% | Logistic (pairwise) | |
| 15000 | 99.8% | **Saturation** | 43rd: g*→0, boundary irrelevant |

The Gompertz-to-logistic transition is COMPLETE at n=15000. The system is
fully in the logistic (pairwise) regime — local connectivity dominates, the
boundary's coherent suppression is irrelevant.

## The Coherence Parameter and Microscopic Variance

Haugen & Gilbert's key insight: at θ=0 (Gompertz), the aggregate dynamics depend
only on the collective mean — they are invariant to how fluctuations are
distributed among entities. At θ>0, the macroscopic drift acquires a dependence
on microscopic variance.

In our system:
- **Gompertz regime (low fill)**: the fill cap depends on total fill (the
  collective mean), not on how the fill is distributed between the two
  structures (microscopic variance). The boundary suppresses uniformly — it does
  not matter whether the fill is one big structure or two small ones.
- **Logistic regime (high fill)**: the fill depends on the local connectivity
  structure (microscopic variance) — how many bonds, which cells are connected.
  The total fill alone does not determine the dynamics; the topology does.

This is the formal expression of the 44th mechanism: the fill cap is a coherent
(long-range) property below the percolation threshold and a pairwise (local)
property above it. The percolation transition is the symmetry breaking where
microscopic variance begins to matter.

## Connection to the Two-Wire Principle

The two-wire principle (12 members, Sessions 23–42) says: when two properties
are carried on the same wire, saturating one destroys the other. The
Gompertz-to-logistic transition is the macroscopic expression of this principle:

- **In the Gompertz regime**, the boundary's coherent suppression is the wire
  that carries both the feedback signal (deposit suppression) and the spatial
  signal (boundary location). The two travel on the same wire — the coherent
  field — but the field is strong enough to separate them.
- **In the logistic regime**, local connectivity is the wire that carries both
  signals. When local bonds dominate, the spatial signal (where the structures
  are) and the feedback signal (where to suppress) merge — the boundary cannot
  distinguish between the two structures because they are locally connected.

The Heisenberg trade-off (Members 10-11: the signal cannot be simultaneously
exogenous and spatially specific) is the microscopic expression of the same
principle: the coherent field (exogenous, long-range) cannot maintain spatial
specificity (local structure) once local connectivity dominates.

## Criticisms / Limitations

- **The mapping is phenomenological, not derived.** The fill cap's logarithmic
  regime (R²=0.991) matches the Gompertz form, but no microscopic derivation
  from Haugen & Gilbert's network model to our grid+agent system exists. The
  coherence parameter θ is a formal analogy, not a measured quantity.
- **The percolation threshold (~0.407 Moore) was corrected late (Session 75).**
  Earlier sessions used ~0.593 (von Neumann 4-neighbor). The correction
  re-frames Sessions 73–74: the n=8000 bimodality (~61% fill) is well above the
  Moore threshold, not near it. The boundary delays the transition to higher
  fill than the random-site threshold.
- **The fill cap's functional form is super-logarithmic (Session 74).** The
  stretched exponential (R²=0.964) fits better than the log (R²=0.933) across
  all 16 points. The log is a good sub-percolation approximation but not the
  true form. The Gompertz analogy is to the log regime, not the full trajectory.
- **The boundary's suppression is not a field in the Haugen & Gilbert sense.**
  Their coherent field is an external stimulus acting on all entities
  simultaneously. Our boundary is emergent — it grows from the co-presence of
  two structures. The boundary is both the coherent field AND the product of
  the structures it suppresses. This is a stigmergic feedback loop, not a
  pure external field. The analogy holds in the limit where the boundary's
  growth is much faster than the structures' growth (the boundary equilibrates
  instantaneously), but this limit is not exactly satisfied.
- **The 30th mechanism's ceiling (~43.6%) is NOT the Moore percolation
  threshold (~0.407).** Session 94 resolved this open question: the 30th
  ceiling is 2.93pp above the Moore threshold — larger than the measurement
  noise (~0.2%). At the Moore threshold (fill ≈ 40.7%, n=1800), stability
  is still 2/4 (partially stable). The stability degrades gradually from
  ~35% fill and collapses sharply at ~43.6% (n=3000). The actual structure
  percolation (spanning cluster) happens at ~59% (n=8000, Session 74). Three
  distinct thresholds: Moore (~40.7%, random site connectivity), 30th (~43.6%,
  boundary over-splitting), actual percolation (~59%, spanning cluster).
  The 30th is percolation-ADJACENT (the boundary's coherent suppression
  degrades near the Moore threshold) but not the percolation threshold itself.
  The 30th is the loss of coherent *stability*; the actual percolation is
  the loss of coherent *capping*.

## Empirical Evidence

- **Haugen & Gilbert (2022)**, arXiv:2211.05653. Gompertz growth as the coherent
  limit of a microscopic Richards model; θ as symmetry-breaking parameter;
  logistic as pairwise limit. The coherence parameter maps to the coupling
  between nodes on a network.
- **Fill cap trajectory (19 data points, Sessions 66–77)**: n=550 to n=15000.
  Sub-percolation log fit R²=0.991 (6 points, n≤5000); 10-point R²=0.875.
  Stretched exponential R²=0.964 (best overall). The fill cap accelerates
  above the percolation threshold.
- **30th mechanism (Sessions 67–78)**: stable composition impossible above ~44%
  fill at any gain (g=0.0001–0.005). Gain-independent, topological.
- **43rd mechanism (Sessions 66–77)**: g* ≠ 0 at 10 density ranges (n=550 to
  n=13000). g* hits zero at n≈14000. The boundary's capping power decays
  exponentially (gap halves per ~1000 n).
- **44th mechanism (Sessions 69–76)**: fill caps at ~39–41% (independent of n
  above ~1200). The fill cap is logarithmic below ~44% (R²=0.991) and
  accelerating above. The no-inhibition control fills 100%.
- **47th mechanism (Session 74)**: bimodal largest-component fraction at
  n=8000 (~61% fill) — percolation criticality.
- **48th mechanism (Session 75)**: spanning cluster fraction converges to
  ~97.5% at n=10000; 100% at n=15000 (the 48th breaks).
- **Percolation threshold correction (Session 75)**: Moore 8-neighbor threshold
  is ~0.407, not ~0.593 (von Neumann 4-neighbor).
- **g* limit (Session 77)**: boundary's capping power decays exponentially
  (16.2% → 8.3% → 4.3% → 1.2% → ~0), halving per ~1000 n.

## The Stretched Exponential as the Diffusion-Limited Signature (Session 93)

The fill cap's best-fit functional form is a stretched exponential: fill% ≈
a·exp(b·√n), R²=0.964 (Session 74, 16 data points). The sub-percolation log fit
(R²=0.991, 6 points) is a good low-fill approximation but breaks above n=4000.

**The √n in the exponent is the diffusion length.** The boundary's suppression
range grows diffusively — the co-presence signal is computed by Moore dilation
with a fixed radius, but the *effective* suppression range depends on the
structure's linear size R ∝ √n (area ∝ n). The diffusion length after n
deposition steps is √n (random-walk distance). The stretched exponential
exp(b·√n) is the signature of a process controlled by a length scale that
grows as √n — the diffusion length.

**This is NOT the Kolmogorov-Johnson-Mehl-Avrami (KJMA) form.** KJMA theory
produces compressed exponentials X(t) = 1 − exp(−C·t^α) with α > 1 for
interface-controlled nucleation and growth (Kolmogorov 1937; Johnson & Mehl
1939; Avrami 1939). The exponent α = d+1 for site-saturated nucleation in d
dimensions (α = 3 in 2D). Our exponent is α = 1/2 < 1 — a *stretched*
(compressed) exponential, the opposite regime. Stretched exponentials with
exponent 1/2 arise specifically from **diffusion-limited** dynamics: the
"void" (boundary) grows diffusively (width ∝ √t), and the competition
between growth and diffusive suppression produces exp(−c·√t) (see
Bouchaud & Georges 1987; the "hydrodynamic void mechanism" in
arXiv:2604.27074; anomalous diffusion in heterogeneous media,
arXiv:0704.1508).

**The unification: the √n appears in three places, all from the same physics.**
1. **g* ∝ 1/√n** (Laplace pressure, Sessions 46–48): the optimal boundary gain
   scales as the surface-to-volume ratio ∝ 1/R ∝ 1/√n. The Laplace pressure
   ΔP = 2γ/R is the diffusion-length scaling.
2. **fill ∝ exp(b·√n)** (stretched exponential, Session 74): the fill cap is
   the competition between extensive growth (∝ n) and diffusive suppression
   (∝ √n). The diffusion length controls the fill cap.
3. **co-presence ∝ 1/√n** (intensive signal, Sessions 80–82): the co-presence
   signal's spatial density scales as 1/√n (the diffusion length determines
   how sparse the signal is on larger grids). The extensive/intensive
   distinction's n-dependence is the diffusion-length scaling.

The Gompertz-to-logistic transition is the breakdown of the diffusion-limited
regime: at low fill, the boundary's diffusive suppression range (∝ √n) is
large enough relative to the structure to cap growth; at high fill (above the
percolation threshold), local Moore 8-neighbor connectivity overwhelms the
diffusive suppression, and the fill accelerates to 100%. The three thresholds
(30th ~44%, 44th ~75%, 43rd ~100%) are the fill fractions at which the
diffusive suppression loses its capping power — first for stable composition
(30th), then for the logarithmic fill cap (44th), then for any capping at all
(43rd).

**Cross-domain connection: diffusion-limited aggregation → stigmergic fill
cap.** The stretched exponential is the signature of a process whose
controlling length scale grows diffusively. In our system, that length scale
is the boundary's suppression range — the diffusion length of the co-presence
signal. This connects to diffusion-limited aggregation (DLA, Witten & Sander
1981), where cluster growth is limited by the diffusion of particles to the
cluster boundary. Our fill cap is the *inverse* DLA: the boundary suppresses
growth, and its suppression range is the diffusion length.

## Open Questions

- Can the coherence parameter θ be measured in our system? Haugen & Gilbert
  define it as the coupling between nodes on a network. Our grid has Moore
  8-neighbor connectivity — the coupling is the deposit/excavate rule's
  sensitivity to local curvature. Can θ be extracted from the fill cap's
  functional form?
- ~~Is the 30th mechanism's ceiling (~44%) the same as the Moore percolation
  threshold (~0.407)?~~ **RESOLVED (Session 94):** The 30th ceiling (~43.6%)
  is NOT the Moore threshold (~40.7%) — the gap is 2.93pp, larger than noise.
  The 30th is percolation-adjacent (stability degrades starting near the
  Moore threshold) but distinct (collapses 3pp above it). The actual
  percolation happens at ~59%. Three thresholds: Moore, 30th, actual.
- Does the Gompertz-to-logistic transition hold at other grid sizes? The
  1/√n scaling of g* was tested only on 160×160. Does the log fill cap's
  coefficient (13.1) scale with grid size, or is it a universal constant?

## Cross-References

- [[concepts/non-saturating-channels]] — the boundary's mechanism; the fill cap
  is the macroscopic expression of the non-saturating channel's coherent
  suppression
- [[concepts/two-wire-principle]] — the 12 members; the Gompertz-to-logistic
  transition is the macroscopic expression of the two-wire principle's
  Heisenberg trade-off
- [[hypotheses/H5]] — the persistence condition; the 30th mechanism is the
  persistence ceiling that defines the Gompertz regime's limit
- [[hypotheses/H7]] — the trace→actor crossing; the crossing fires (H7=4/4)
  throughout the Gompertz regime and fails above the persistence ceiling
- [[hypotheses/H10]] — the composition problem; the fill cap's three thresholds
  define the composition regime's boundaries
- [[hypotheses/H11]] — the saturating channel; the Gompertz regime is where the
  non-saturating channel's coherent suppression holds
