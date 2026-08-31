# Finite-radius 2D matched-budget fold certificate

## Status and claim boundary

This calculation is a **finite-grid mechanism certificate**, not a continuum
critical-parameter estimate.  It verifies that redistributing a fixed
per-lattice discrete state-sum killing budget can create a nondegenerate
min--max pair in the reaction-time density. A separate tensor-product
control-volume weighting audits the sensitivity to that discrete budget
measure. The fold equations and parameter
sensitivity are evaluated with sparse matrix exponentials and generator
actions, not sampled finite differences.

The fold coordinate is not grid-converged: the state-count-matched 9x5, 11x7,
and 13x9 values of `theta_c` are nonmonotone and span about `0.262`. A
tensor-product boundary-control-volume budget audit retains nondegenerate
physical folds on all three grids but moves the controls to
`0.6244, 0.2408, 0.4593`. Consequently, this calculation supports the
finite-lattice mechanism and its local normal form, but it does **not**
support quoting a continuum value of `theta_c`.

## Matched-budget family

Both walkers move on the unit square with reflecting CTMC boundaries and a
smooth transverse OU confinement of strength `1.5`.  The fixed parameters are

- walker 1: `D1=0.0025`, `v1x=0.115`;
- walker 2: `D2=0.0008`, `v2x=0.02`;
- starts: `(0,0.5)` and `(0.28,0.5)`;
- finite encounter radius: `a=0.17`;
- near centre patch: centre `(0.25,0.5)`, radius `0.18`, rate `0.5`;
- far centre patch: centre `(0.72,0.5)`, radius `0.20`, rate `15`.

On each grid the killing field is

\[
\kappa_\theta(c)=(1-\theta)\bar\kappa_h
 +\theta\left[0.5\,\mathbf 1_{C_{\rm near}}(c)
 +15\,\mathbf 1_{C_{\rm far}}(c)\right].
\]

If `N_T`, `N_n`, and `N_f` are the discrete encounter-tube, near-patch,
and far-patch state counts, respectively, then

\[
\bar\kappa_h=\frac{0.5N_n+15N_f}{N_T}.
\]

Thus the statewise sum of killing rates is identical for every `theta`, down
to floating-point roundoff:

| grid | `N_T` | `N_n` | `N_f` | `kappa_bar` | fixed budget |
|---|---:|---:|---:|---:|---:|
| 9x5 | 125 | 7 | 9 | 1.108 | 138.5 |
| 11x7 | 349 | 34 | 40 | 1.7679083094555874 | 617.0 |
| 13x9 | 1123 | 109 | 137 | 1.8784505788067676 | 2109.5 |

The budget is a discrete sum, so its numerical value scales with the number
of product states.  The comparison of interest is its exact constancy along
`theta` on each fixed grid.

## Exact fold equations

Let `A(theta)` be the killed row generator, `k(theta)` the total killing
vector, and

\[
x(t,\theta)=\exp[A(\theta)^\mathsf{T}t]p_0,
\qquad f(t,\theta)=x(t,\theta)^\mathsf{T}k(\theta).
\]

Time derivatives are sparse generator actions:

\[
f_t=x^\mathsf{T}Ak,\quad
f_{tt}=x^\mathsf{T}A^2k,\quad
f_{ttt}=x^\mathsf{T}A^3k.
\]

For `A_theta=dA/dtheta`, the state sensitivity satisfies

\[
\frac{d}{dt}
\begin{pmatrix}x\\x_\theta\end{pmatrix}
=
\begin{pmatrix}A^\mathsf{T}&0\\A_\theta^\mathsf{T}&A^\mathsf{T}\end{pmatrix}
\begin{pmatrix}x\\x_\theta\end{pmatrix},
\qquad x_\theta(0)=0.
\]

This augmented exponential gives

\[
f_{t\theta}=x_\theta^\mathsf{T}Ak
+x^\mathsf{T}(A_\theta k+Ak_\theta),
\]

with the analogous analytic expression used for `f_tt_theta`.  Solving
`f_t=f_tt=0` with this analytic Jacobian gives:

| grid | `t_c` | `theta_c` | `f_t` residual | `f_tt` residual | `f_ttt` | `f_ttheta` |
|---|---:|---:|---:|---:|---:|---:|
| 9x5 | 16.8093320824 | 0.2753729985 | 6.1e-18 | -3.5e-17 | -1.34205e-5 | 1.66924e-4 |
| 11x7 | 18.0995322971 | 0.0138103513 | 8.7e-19 | 3.5e-18 | -7.8136e-6 | 2.8264e-4 |
| 13x9 | 16.5807587454 | 0.2558920083 | -4.3e-19 | 2.8e-17 | -5.9589e-6 | 7.4618e-5 |

Both `f_ttt` and `f_ttheta` are nonzero.  The two-by-two fold Jacobian
determinants are `2.2402e-9`, `2.2084e-9`, and `4.4464e-10`, respectively. At a held-out
offset `delta_theta=0.005`, the subcritical local window has no stationary
point and strictly negative `f_t`, whereas the supercritical window contains
one minimum and one maximum.

## Local scaling

Writing `mu=theta-theta_c`, the local equation is

\[
0=f_t\simeq f_{t\theta}\mu
 +\frac12 f_{ttt}(t-t_c)^2.
\]

It predicts peak--valley separation proportional to `mu^(1/2)` and prominence
proportional to `mu^(3/2)`. Sign-changing stationary roots were Brent-refined
with exact finite-state derivative evaluations at
`mu=0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05`.  Fits on the first
six values give:

| grid | separation exponent | prominence exponent |
|---|---:|---:|
| 9x5 | 0.498902 | 1.500051 |
| 11x7 | 0.493314 | 1.484297 |
| 13x9 | 0.499325 | 1.503854 |

The normal-form exponents are therefore stable even though the continuation
coordinate is not.

The generator also stores the multiplicative predictions, not only the
exponents.  If (a=f_{t\theta}), (b=f_{ttt}), and
(c=\sqrt{-2a/b}), then

\[
 \Delta t_{\rm NF}=2c\,\mu^{1/2},\qquad
 \mathcal P_{\rm NF}=\frac{2|b|}{3}c^3\mu^{3/2}.
\]

| grid | separation coefficient | prominence coefficient | smallest-step measured/predicted separation | smallest-step measured/predicted prominence |
|---|---:|---:|---:|---:|
| 9x5 | 9.97517718 | 0.001110066913 | 0.999903 | 0.999998 |
| 11x7 | 17.01132770 | 0.003205408694 | 0.999406 | 0.998599 |
| 13x9 | 10.00887637 | 0.000497897976 | 0.999941 | 1.000328 |

The first two continuation steps for each grid are regression-gated against
both ratios.  This detects sign and factor-of-two mistakes that exponent-only
fits cannot see.

## Budget-measure sensitivity

The principal finite-lattice path matches the unweighted sum over Markov
states. As a one-factor sensitivity check, define boundary-node trapezoidal
weights

\[
w_{ij}=h_xh_y q_iq_j,\qquad q=1\text{ in the interior},\quad q=1/2
\text{ on a boundary},
\]

and use `W=kron(w,w)` on the two-walker product space. This is equivalently a
tensor-product control-volume measure; it changes only the matching rule, not
the CTMC generator or masks. The homogeneous rate is then

\[
\bar\kappa_W=\frac{\sum_s W_s k_{\rm pat}(s)}
{\sum_s W_s I_{\rm tube}(s)}.
\]

All three weighted-budget paths have physical, nondegenerate folds:

| grid | `kappa_bar_W` | `t_c` | `theta_c` | Jacobian determinant |
|---|---:|---:|---:|---:|
| 9x5 | 1.8405315615 | 16.7451100058 | 0.6244414050 | 3.7165e-9 |
| 11x7 | 2.5055837563 | 18.1886131611 | 0.2407691277 | 7.0873e-10 |
| 13x9 | 2.4062051135 | 16.4316367746 | 0.4593453445 | 6.0471e-10 |

For comparison, direct one-dimensional quadrature of the exact
boundary-clipped midpoint domain gives `kappa_bar=2.2501572220`. The simpler
interior-patch factorization gives `2.2502050762`, only `2.13e-5` relatively
higher but not exact for these barely boundary-touching patches. Relative to
the exact clipped value, the weighted values have relative errors
`-18.2%, +11.4%, +6.9%`, closer than the unweighted errors
`-50.8%, -21.4%, -16.5%`; nevertheless the weighted fold controls remain
nonmonotone and span about `0.384`. Fold existence is robust to this control,
whereas the critical coordinate is not.

## Even-grid topology diagnostics

- On 12x8, a numerical solve of the finite-matrix fold equations locates a
  nondegenerate root at
  `(t,theta)=(18.2687686834,-0.0615843784)`, outside the physical interval
  `theta in [0,1]`.
- On 10x6, a curvature-branch scan over `theta=-0.2,...,0.1` and
  `t in [0.01,40]`, followed by four bounded analytic-Jacobian least-squares
  starts, finds no root. All four attempts converge to the same positive near
  miss near `(15.319799,-0.09567453)`, with
  `f_t=3.8721282e-6` and `|f_tt|<=4.4e-12`.

These are bounded search results, not an exhaustive proof of root absence.
They explain why endpoint topology need not alternate cleanly with grid size.

## Lattice-resolution boundary

The upwind cell Péclet numbers and radius-to-spacing ratios are persisted in
the metrics. They remain too large/small, respectively, to interpret these
moderate lattices as a controlled convergence sequence for the displayed
continuum SDE. The supported object is therefore the declared finite CTMC
family. A continuum-fold promotion requires a resolved finite-volume/FEM or
relative--centre solver and an independent numerical method.

## Five-grid endpoint audit

Endpoint robustness is evaluated independently of the fold solve on grids
`9x5`, `10x6`, `11x7`, `12x8`, and `13x9`. Every detected sign-changing
stationary point is retained; the finite scan is not an exhaustive
even-multiplicity-root certificate. A secondary maximum is called *resolved*
only when its height is at
least `3%` of the primary maximum and the intervening valley is at most `95%`
of the smaller maximum.

For this M2D-F family the saved final-law diagnostics verify zero contact and
active-sink mass, unit total mass, and the declared position means on every
tested grid. They do not separately persist the original bilinear contact mass
or the selector path, so no byte-for-byte fast-path claim is inferred from
these artifacts.

| grid | homogeneous strict | homogeneous ratio | patterned strict | patterned ratio | patterned valley ratio |
|---|---|---:|---|---:|---:|
| 9x5 | unimodal | 0 | bimodal | 0.03533 | 0.92525 |
| 10x6 | bimodal ripple | 0.02897 | bimodal | 0.11303 | 0.83920 |
| 11x7 | unimodal | 0 | bimodal | 0.05282 | 0.74912 |
| 12x8 | bimodal ripple | 0.00799 | bimodal | 0.05748 | 0.69589 |
| 13x9 | unimodal | 0 | bimodal | 0.03551 | 0.79248 |

Under the declared resolution rule, all five homogeneous endpoints are
resolved-unimodal and all five patterned endpoints are resolved-bimodal. The table explicitly
shows that the even grids contain small homogeneous reflection ripples; they
are classified as unresolved rather than silently deleted.  Tails at `t=480`
are below `1.9e-6` on all ten endpoint runs. Thus omitted probability mass is
below two parts per million, which is a useful probability-closure diagnostic
but is not directly comparable to the declared 3% peak-height threshold. Total
tail mass alone does not exclude a narrow high late peak, and this endpoint calculation has no
interval-exhaustive derivative audit on `(45,480)`. The reported resolved class
therefore applies to the declared stationary-point scan and tail horizon; no
stronger absence claim for a narrow late extremum is made.

## What may and may not enter the paper

The following statements are supported:

1. spatial redistribution alone, at an exactly matched discrete killing
   budget and fixed transport, can create a min--max pair;
2. the fold is nondegenerate on all three tested physical fold grids and
   persists under the product-control-volume budget measure;
3. square-root separation and `3/2` prominence follow from and numerically
   match the local fold normal form;
4. amplitude-resolved endpoint modality agrees on five grids.

The following statement is withheld:

> `theta_c` has converged to a continuum physical value.

Promotion beyond a mechanism certificate requires cell-averaged reaction
masks (or a comparably controlled spatial discretization), at least three
successively refined grids in the asymptotic regime, and a stable extrapolated
fold coordinate.  The current non-convergence must remain visible in the main
text or limitations, not only in supplementary material.

## Reproduction handles

- generator: `code/validate_2d_matched_fold.py`;
- metrics: `artifacts/data/finite_radius_2d_fold_metrics.json` and `.csv`;
- series: `artifacts/data/finite_radius_2d_fold_series.npz`;
- provenance: `artifacts/data/finite_radius_2d_fold.manifest.json`;
- vector figure: `artifacts/figures/finite_radius_2d_fold_validation.pdf`.
