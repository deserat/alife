---
status: active
formed: "Session 82"
connected_to: "two-wire-principle, gompertz-logistic-transition, non-saturating-channels, H5, H7, H10, H11"
topic: "the extensive/intensive signal distinction in stigmergic systems — why the boundary converts density-dependence into n-dependence"
key_findings: "The fill (total deposited material) is an extensive property — it scales with the deposit rate per termite × n (density-dependent). The co-presence signal (min of dilated ID-tagged material from two structures) is an intensive property — it depends on the spatial arrangement of material, not its total amount. The boundary acts on the intensive co-presence signal, not the extensive deposit rate. This disconnect converts the extensive fill's density-dependence into n-dependence: without the boundary, fill = density × dpt (density-dependent); with the boundary, fill = f(n) (n-dependent) because the boundary's suppression depends on n through the co-presence signal's spatial arrangement. Confirmed at three grid sizes (80×80, 160×160, 320×320): at matched density, fill decreases with grid size — the boundary is weaker on larger grids because the co-presence signal is sparser (same n, 4× area). The 50th mechanism (fill depends on absolute n) and the 53rd mechanism (boundary converts density-dependence into n-dependence) are both consequences of the extensive/intensive signal distinction."
---

# The Extensive/Intensive Signal Distinction in Stigmergic Systems

## The Concept

In thermodynamics, **extensive** properties (volume, mass, energy) scale with system
size — doubling the system doubles the property. **Intensive** properties (density,
temperature, pressure) do not — they are local and independent of system size. The
distinction is foundational: extensive properties measure *how much*, intensive properties
measure *how arranged*.

Our stigmergic system has the same distinction, and it explains why the boundary converts
density-dependence into n-dependence (the 50th and 53rd mechanisms).

### The fill is extensive

The total deposited material — the "fill" — scales with the deposit rate per termite
(dpt) multiplied by n_termites. Without the boundary:

  fill = dpt × n_termites × steps × (1 − erosion)

This is density-dependent: at matched density (n / grid²), the fill fraction is the same
regardless of grid size. Session 81 confirmed this: no-inhibition fill at 11.7/kc is 29.26%
on 320×320 (n=1200) ≈ 29.47% on 80×80 (n=75) — nearly identical at matched density.

### The co-presence signal is intensive

The co-presence signal — `min(dilate(material_by_id[0]), dilate(material_by_id[1]))` —
depends on the *spatial arrangement* of the two structures' material, not on the total
amount. It measures *where* the two structures overlap after dilation, not *how much*
material exists. At matched density on a larger grid, the same n termites spread material
over 4× the area, making the co-presence signal 4× sparser — a lower signal at the same
density.

### The boundary acts on the intensive signal

The boundary field B grows from the co-presence signal: `B = B·(1−decay) + growth·cp`.
The suppression is `p_dep *= (1 − g·B_norm/(1+B_norm))`. The boundary's suppression
depends on B, which depends on the co-presence signal — an intensive property. The
boundary does not act on the deposit rate (extensive); it acts on the spatial arrangement
(intensive).

### The disconnect

The fill (extensive) is density-dependent. The boundary acts on the co-presence signal
(intensive), which is n-dependent (depends on how many termites are spread across the
grid, not the density). The boundary's suppression therefore depends on n, not density.

This converts the extensive fill's density-dependence into n-dependence:
- **Without the boundary:** fill = density × dpt → density-dependent
- **With the boundary:** fill = f(n) → n-dependent (the boundary's suppression
  depends on the co-presence signal's spatial arrangement, which depends on n)

## Empirical Evidence

### The 50th mechanism (Session 80): fill depends on absolute n, not density

At matched density (23.4/kc), fill decreases with grid size:
- 80×80 (n=150): 48.26%
- 160×160 (n=600): 31.23%
- 320×320 (n=2400): 24.72%

The per-density prediction (same fill at same density) is falsified at all three grid
sizes. The fill depends on absolute n, not density.

### The 53rd mechanism (Session 81): boundary converts density-dependence into n-dependence

Without the boundary (no-inhibition), the fill IS density-dependent:
- 320×320 (n=1200, 11.7/kc): 29.26%
- 80×80 (n=75, 11.7/kc): 29.47%
- Nearly identical at matched density.

With the boundary (g=0.01), the fill becomes n-dependent:
- 320×320 (n=1200, 11.7/kc): 15.82%
- 160×160 (n=300, 11.7/kc): 21.29% (directly measured, Session 82; the
  earlier 43.49% was an extrapolation from the n≥550 plateau data)
- 80×80 (n=75, 11.7/kc): 29.47%

The boundary's suppression is n-dependent (weaker on larger grids) because the
co-presence signal is sparser at the same density on a larger grid. The
monotonic decrease (fill_80 > fill_160 > fill_320) holds at all densities tested
(11.7/kc, 23.4/kc).

### The 52nd mechanism: the co-presence signal is intensive

The co-presence signal depends on the spatial overlap of two dilated ID-tagged material
arrays. At matched density on a larger grid, the same n termites spread material over
4× the area. The dilated overlap (co-presence) is lower — the signal is sparser. The
boundary's suppression (proportional to B_norm, which is proportional to co-presence)
is therefore weaker. The signal's intensity (spatial density of the overlap) decreases
with grid size at matched density, while the fill (extensive) remains density-dependent
without the boundary.

**Session 83 refinement: the co-presence at steady state is NOT purely intensive.**
Direct measurement (copresence_density_sweep.py) at two densities (23.4/kc, 46.9/kc)
across three grid sizes found:
- The co-presence COVERAGE (fraction of cells with cp > 0) saturates at ~98–100%
  regardless of grid size — not a discriminating metric.
- The co-presence MEAN is non-monotonic (decreases from 80×80 to 160×160, then
  increases to 320×320) and endogenous — it is both cause and consequence of the
  boundary's feedback loop.
- The 320×320 has the HIGHEST cp_mean (0.447 at 23.4/kc, 0.450 at 46.9/kc) but the
  LOWEST fill (25.0%, 36.2%) — the co-presence is NOT "sparser on larger grids."

The n-dependence comes from the NORMALIZATION, not the signal. The steady-state B
(extensive — scales with absolute material/n) is normalized by the initial b_scale
(intensive — same at matched density, from seed regions at the same relative positions).
The ratio B_norm = B/b_scale is n-dependent (extensive / intensive), making the
suppression n-dependent, making the fill n-dependent.

**Methodology lesson: a signal measured inside a feedback loop is both cause and
consequence — it cannot test the loop's causality.** The co-presence at steady state
is shaped by the boundary's suppression, which is shaped by the co-presence. To test
the intensive/extensive distinction, measure OUTSIDE the loop (no-inhibition) or
BEFORE the loop has had an effect (initial state).

## The Thermodynamic Analogy

| Thermodynamics | Stigmergic system |
|---|---|
| Extensive (volume, mass) | Fill (total deposited material) — scales with dpt × n |
| Intensive (density, pressure) | Co-presence signal (spatial overlap of structures) — local, arrangement-dependent |
| System size | Grid size |
| Number of particles | Number of termites |
| Density = N/V | n / grid² (termite density) |
| Pressure (intensive) scales with density at fixed T | Co-presence (intensive) scales with n at fixed grid |
| Volume (extensive) scales with N at fixed density | Fill (extensive) scales with dpt × n at fixed density |

The key insight: the boundary acts on an intensive property (co-presence), while the
quantity it controls (fill) is extensive. The boundary's suppression depends on the
co-presence signal's spatial density, which depends on n and grid size — not on the
fill's density. This is why the fill's density-dependence is converted into n-dependence:
the boundary mediates through an intensive signal that "measures" arrangement, not amount.

## Connection to the Two-Wire Principle

The extensive/intensive distinction is the 13th member of the two-wire principle:

> **Member 13 — The extensive/intensive signal distinction (Session 82).** The fill
> (extensive) and the co-presence signal (intensive) travel on separate wires. The
> boundary acts on the intensive wire (co-presence → B → suppression), not the extensive
> wire (deposit rate → fill). The fill's density-dependence (extensive) is converted
> into n-dependence (intensive) because the boundary mediates through the intensive
> signal. This is the thermodynamic expression of the two-wire principle: the feedback
> signal (suppression) and the controlled quantity (fill) travel on separate wires
> because they have different scaling (intensive vs extensive).

The 12th member (structure-to-grid ratio) is the finite-size expression: the
structural guarantee depends on the ratio of structure size to grid area, which is
an intensive quantity (arrangement-dependent). The 13th member generalizes this: ALL
of the boundary's properties — suppression, structural guarantee, fill cap — depend on
the intensive co-presence signal, not the extensive fill.

## Connection to the Gompertz-to-Logistic Transition

The Gompertz-to-logistic transition (Sessions 69–79) maps the fill cap trajectory onto
the coherence parameter θ from Haugen & Gilbert (2022). The three thresholds (30th ~44%,
44th ~75%, 43rd ~100%) are fill-fraction thresholds.

The extensive/intensive distinction explains why the thresholds are fill-fraction
thresholds, not density thresholds: the boundary acts on the intensive co-presence
signal, which is a fill-fraction-like quantity (spatial density of the overlap). The
coherence parameter θ measures the coupling between the extensive fill and the intensive
co-presence — at low fill (Gompertz regime), the boundary's intensive signal controls
the fill (coherent); at high fill (logistic regime), the fill's extensive growth
overwhelms the intensive signal (percolation, pairwise dominance).

The design principle "keep the system in the Gompertz regime" is equivalent to "keep
the intensive signal strong enough to control the extensive fill" — the co-presence
signal must be dense enough (spatially) for the boundary's suppression to matter.

## The Gain Compensation Result (Session 82)

Session 82 tested the gain compensation: 320×320 at n=1200 × g=[0.01–0.12] × 4
seeds. **Result: NOT gain-compensable.** The fill on 320×320 monotonically
DECREASES with gain (15.82% → 14.14%). Higher gain suppresses MORE, not less —
gain amplifies the sparse co-presence signal's magnitude, making the boundary
suppress harder in the wrong places. The co-presence signal's sparsity is a
spatial-arrangement property (intensive) — gain amplifies magnitude (extensive),
it cannot fix spatial coverage. This is the thermodynamic analog of trying to
compensate for low pressure (intensive) by increasing the volume (extensive) —
the two are independent axes.

**Session 84: the 53rd mechanism is FALSIFIED — the n-dependence is from the focal bias, not the boundary.**

The no-inhibition co-presence sweep (mode="hetero" g=0 — focal bias, ID-tagged, no boundary)
measured the co-presence OUTSIDE the boundary's feedback loop. The fill is n-dependent
EVEN WITHOUT the boundary: at 23.4/kc, fill = 48.33% (80×80) → 31.58% (160×160) →
24.95% (320×320). The focal bias (1-cell steps toward home) is an absolute spatial scale
that is less effective on larger grids. The boundary adds <0.5% at g=0.01 (fill deltas:
-0.07%, -0.48%, +0.05%). The co-presence is extensive without the boundary too (cp_mean:
0.330 → 0.293 → 0.452, same non-monotonic pattern).

The 53rd mechanism's original control (mode="none" — no focal bias, no boundary) was
confounded: it changed two variables (focal bias + boundary) simultaneously. The correct
control (mode="hetero" g=0) holds the focal bias constant and varies only the boundary.
The n-dependence is from the focal bias, not the boundary. The 50th mechanism's empirical
finding (fill depends on absolute n) holds but its mechanism is the focal bias, not the
boundary — at the gains where it was tested (g=0.01-0.02), the boundary is negligible.

**Methodology lesson: the control must isolate one variable at a time.** This is the
control-arm pattern (#75) recurring: a control that confounds two variables cannot
attribute the effect to either.

## Criticisms / Limitations (updated Session 84)

- **The thermodynamic analogy is phenomenological, not derived.** The extensive/intensive
  distinction in thermodynamics is precisely defined (Euler homogeneity). Our co-presence
  signal is not formally intensive in the Euler sense — it is a computational quantity
  (min of dilated arrays) that behaves like an intensive property (arrangement-dependent,
  not amount-dependent). The analogy holds operationally but not formally.
- **The co-presence signal is not purely intensive.** It does depend on the total amount
  of material (more material → more overlap after dilation). It is intensive in the
  sense that its *spatial density* (how concentrated the overlap is) depends on the
  arrangement, not the total. At very low n, the co-presence is zero (no overlap); at
  very high n, it saturates (full overlap everywhere). The intensive behavior holds
  in the intermediate regime where the structures are compact but not percolated.
- **The 50th mechanism has only been tested at three grid sizes.** The monotonic
  decrease (fill_80 > fill_160 > fill_320 at matched density) is confirmed at
  23.4/kc and 11.7/kc (the 11.7/kc sign flip was an extrapolation artifact —
  corrected in Session 82). A third density (46.9/kc) would strengthen the
  conclusion; the 53rd mechanism's mechanism (intensive signal sparsity) is
  confirmed by the no-inhibition control and the gain compensation test.
- **The co-presence signal's spatial density is not yet measured directly.** The
  extensive/intensive distinction is currently phenomenological — the fill
  decreases with grid size at matched density (qualitative), and gain cannot
  compensate (qualitative). A direct measurement of the co-presence signal's
  spatial density (fraction of cells with co-presence > 0) at matched density
  across grid sizes would make the distinction quantitative (Session 83).

## Cross-Domain Connections

- **Thermodynamics → stigmergy:** The extensive/intensive distinction applies to
  stigmergic signals. The fill (extensive) is density-dependent; the co-presence
  (intensive) is arrangement-dependent. The boundary mediates through the intensive
  signal, converting the extensive fill's density-dependence into n-dependence.
- **Statistical physics → stigmergy:** The co-presence signal is like a local order
  parameter (intensive — it measures the local correlation between two structures).
  The fill is like the total magnetization (extensive — it measures the total amount
  of aligned material). The boundary acts on the local order parameter, not the total
  magnetization.
- **Control theory → stigmergy:** The boundary's gain g is like a controller acting
  on a local (intensive) measurement. The controller's effectiveness depends on the
  measurement's spatial coverage, not just its magnitude. A sparse measurement
  (low spatial coverage) cannot be compensated by higher gain — the controller
  acts on the wrong locations.

## Cross-References

- [[concepts/two-wire-principle]] — the 13th member: extensive and intensive signals on
  separate wires
- [[concepts/gompertz-logistic-transition]] — the fill-fraction thresholds are intensive
  thresholds (co-presence density, not fill amount)
- [[concepts/non-saturating-channels]] — the boundary's mechanism; the co-presence signal
  is the intensive channel
- [[hypotheses/H5]] — the persistence condition; the 30th mechanism's ceiling is an
  intensive threshold (the co-presence signal's spatial density falls below the
  boundary's maintenance threshold)
- [[hypotheses/H7]] — the trace→actor crossing; the crossing is robust (4/4) because
  it depends on the intensive curvature signal, not the extensive fill
- [[hypotheses/H10]] — the composition problem; the fill cap's n-dependence is the
  extensive/intensive signal distinction's macroscopic expression
