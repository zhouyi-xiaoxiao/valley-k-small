# Finite-radius 2D trimodality certificate

## Supported result

One fixed, obstacle-free two-walker model on the reflecting unit square has
three strict reaction-time modes on the `9x5`, `11x7`, `13x9`, and `15x11`
grids.  The canonical multiscale morphology classifier resolves all three
modes on the three finer grids and calls the contact-safe `9x5` case a
shoulder, although its raw density still has three maxima and 118 scale views
contain three accepted peaks. An independent generator-derivative audit detects five
simple positive-time stationary roots in the order

`maximum -- minimum -- maximum -- minimum -- maximum`.

At the three maxima the dominant reaction channels are, in temporal order,
the near, middle, and far catalytic patches.  Thus this example is not made by
adding signed component densities or by relabelling one physical sink: all
three patch rates and all channel fluxes are nonnegative, and the total
density is their exact sum.

## Fixed physical configuration

Both walkers move in the unit square with reflecting boundaries.  Their
continuous-time grid generators approximate advection-diffusion with a smooth
transverse Ornstein-Uhlenbeck confinement:

| quantity | walker 1 | walker 2 |
|---|---:|---:|
| diffusion | `0.0025` | `0.0008` |
| longitudinal drift | `0.10` | `0.02` |
| transverse confinement | `1.5` | `1.5` |
| initial position | `(0.05,0.50)` | `(0.20,0.50)` |

Reaction requires a finite inter-particle distance `a=0.13`.  Conditional on
that encounter, the arithmetic centre of the two walkers must lie in one of
three disjoint circular catalytic patches:

| patch | centre | radius | Doi rate |
|---|---|---:|---:|
| near | `(0.20,0.50)` | `0.06` | `0.03` |
| middle | `(0.70,0.50)` | `0.05` | `1.00` |
| far | `(0.94,0.50)` | `0.05` | `0.05` |

The far patch remains strictly inside the square, with physical boundary
clearance `0.01`.  There are no obstacles and no negative weights.

## Channel-clock interpretation

The spatial layout yields three maxima whose direct Doi fluxes are dominated,
in time order, by the near, middle, and far patches. Their timing is consistent
with short-launch, advective, and delayed downstream-return clocks. The
calculation does not decompose sample paths or prove that a specified survivor
population accumulates at the reflecting side; its direct evidence is the
ordered channel-flux dominance at the detected maxima. Changing only labels
would not produce that measured flux attribution.

For the `13x9` grid, the detected simple roots of `f_t`, refined with direct
finite-matrix semigroup derivative evaluations, are approximately

| root | time | type | dominant channel when a maximum |
|---:|---:|---|---|
| 1 | `1.01673` | maximum | near |
| 2 | `4.45517` | minimum | -- |
| 3 | `8.93626` | maximum | middle |
| 4 | `15.93406` | minimum | -- |
| 5 | `48.28197` | maximum | far |

The precise table for all four grids is generated in
`artifacts/data/finite_radius_2d_trimodal_roots.csv`.  Classifier valley ratios,
lobe masses, prominences, channel shares, root residuals, and tail quantities
are recorded rather than rounded in the JSON metrics file.

## Derivative and tail audit

For killed row generator `T`, total killing vector `b`, and initial row law
`alpha`,

\[
f^{(j)}(t)=\alpha e^{Tt}T^j b.
\]

The code scans `f_t` over the declared finite numerical audit interval
`[0,2000]`:
spacing `0.02` on `[0,100]`, followed by spacing `1` on `[100,2000]`.  Every
sign-change bracket is refined with Brent's method using fresh sparse matrix
exponentials, and `f_tt` classifies the root.  The scan also checks the
logarithmic slope away from the five declared roots to expose an unresolved
even-multiplicity tangency, and requires the derivative to remain negative
after the final maximum.

This is strong evidence for the five listed simple roots, not an exhaustive
root-count proof on `(0,infinity)`.  A finite sign-change scan cannot by itself
exclude an even-multiplicity tangency or an unresolved narrow root pair.  The
off-root logarithmic-slope diagnostic and an independent scan of the roots of
`f_tt` found no near-tangency in the four saved models, but no interval
certificate against additional roots is claimed.

Channel reaction masses are not inferred from a truncated plotting window.
They are integrated to `t=2000` in a single augmented sparse exponential.
The remaining survival mass, density, derivative, and augmented closure error
are archived for every grid.

## Claim boundary

This is a **finite-grid mechanism certificate**, not a continuum trimodality
theorem.  Four grids preserve three detected strict maxima, the detected root
ordering, and channel attribution; three finer grids also preserve resolved
trimodality, while the
coarsest is a conservative classifier shoulder. The last two grids give
similar stationary times. Nevertheless, the circular indicator masks are
not cell-averaged and contain only a small number of reactive product states
on every tested lattice. In fact, all patch radii are smaller than the
longitudinal spacing even on `15x11`; the near/middle/far reactive-state
counts are `3/3/2`, `5/5/3`, `4/4/3`, and `18/5/5` across the four grids.
Their nonmonotonicity is an aliasing diagnostic, not a refinement signature.
Therefore the present evidence supports the following claim:

> Three separated, nonnegative finite-radius catalytic patches generate three
> resolved reaction-time modes on three declared bounded finite two-particle
> 2D lattices and three strict, channel-attributed maxima on a fourth coarse
> lattice classified as a shoulder.

It does not yet support a universal continuum phase boundary or a converged
continuum parameter value.  Promotion to such a claim requires cell-averaged
patch masks, further refinement in the asymptotic regime, and a continuation
study showing that the two trimodality folds converge.

## Reproduction handles

- generator: `code/validate_2d_trimodal.py`;
- full metrics: `artifacts/data/finite_radius_2d_trimodal_metrics.json`;
- compact grid table: `artifacts/data/finite_radius_2d_trimodal_metrics.csv`;
- detected derivative roots: `artifacts/data/finite_radius_2d_trimodal_roots.csv`;
- archived curves: `artifacts/data/finite_radius_2d_trimodal_series.npz`;
- provenance: `artifacts/data/finite_radius_2d_trimodal.manifest.json`;
- vector figure: `artifacts/figures/finite_radius_2d_trimodality.pdf`.
