# Unbounded off-lattice Doi thinning design

Date: 2026-07-13  
Status: **method design and bounded proof of principle; production run not authorized**

## 1. Purpose and claim boundary

Round 33 requires a killed-process calculation that is physically and
numerically independent of the reflected Scharfetter--Gummel finite-volume
semigroup.  The shortest exact-in-time route is conditional Poisson thinning
of the continuous Doi hazard on the unbounded longitudinal quotient.

This note specifies that route for the fixed broad four-slab physical-
`d=2` configuration at `B=0.01`.  It also records a small executable method
smoke.  It does **not** authorize the production Monte Carlo calculation and
does not set any of these flags to true:

- `independent_solver_verified`;
- `unbounded_domain_FV_limit_verified`;
- `modality_confirmed`; or
- `project_gate_passed`.

The production windows, deterministic comparison values, cross-method
tolerances, and any additional fixed-budget fold-side controls must be frozen
after the deterministic continuum/box analysis and before independent event
times are inspected.  No catalyst weight, geometry, budget, or validation
window may be refitted to a Monte Carlo result.

The implementation introduced here is entirely new:

- `code/off_lattice_doi_thinning_poc.py`;
- `code/test_off_lattice_doi_thinning_poc.py`; and
- `scratch/off_lattice_doi_thinning_poc_result.json`.

It imports no finite-volume producer and uses no grid, reflecting face,
Scharfetter--Gummel flux, cut-cell contact fraction, or matrix exponential.
No frozen positive-`B` producer, manifest, test, protocol, or result was edited
or executed during this work.

## 2. Continuous quotient and exact free transitions

The off-lattice state is

\[
 X_t=(M_t,R_t,Y_t)\in\mathbb R\times\mathbb R\times
 (\mathbb R/W\mathbb Z),
\]

where `M` is the longitudinal midpoint, `R` the longitudinal relative
coordinate, and `Y` the periodic transverse relative coordinate.  The frozen
physical values are

\[
 D=0.002,\quad \gamma=0.1,\quad \bar m=0.95,\quad W=1,
 \quad a=0.16.
\]

The free generator is

\[
 L_0={D\over2}\partial_{MM}-\gamma(M-\bar m)\partial_M
      +2D\partial_{RR}-\gamma R\partial_R+2D\partial_{YY}.
\]

For a candidate-time increment `Delta`, put `q=exp(-gamma Delta)`.  The
implementation samples the exact Markov transition

\[
 \begin{aligned}
 M'&=\bar m+q(M-\bar m)
   +\sqrt{\frac{D}{2\gamma}(1-q^2)}Z_M,\\
 R'&=qR+\sqrt{\frac{2D}{\gamma}(1-q^2)}Z_R,\\
 Y'&=\bigl[Y+\sqrt{4D\Delta}\,Z_Y\bigr]_W,
 \end{aligned}
\]

with independent standard normals.  Thus there is no Euler step and no time
mesh.  `M` and `R` remain unbounded; only `Y` is wrapped to `[-W/2,W/2)`.
The sole time truncation is right censoring at the declared horizon `T=100`.

## 3. Exact compact initial law

Let

\[
 b(u)=\mathbf 1_{|u|<1}\exp[-1/(1-u^2)],\qquad
 I_b=\int_{-1}^{1}b(u)\,du.
\]

With half-width `h=0.02`, the continuous initial law is the independent
product of normalized bumps centered at

\[
 (M_0,R_0,Y_0)=(0.14,-0.35,0).
\]

The periodic factor is wrapped only after sampling and its support is much
shorter than one period.  Each standardized bump variate is sampled by
rejection from `Uniform(-1,1)`, accepting with probability

\[
 \frac{b(u)}{b(0)}=\exp[-u^2/(1-u^2)].
\]

This sampler needs no numerical normalizing constant.  The implementation has
a 512-attempt fail-closed cap: reaching it aborts the calculation, with no
fallback and no conditional resampling of the whole trajectory.  Therefore a
successful trajectory has the intended law; a sampler failure cannot silently
bias it.

For hazard evaluation, `I_b` is represented by the independently evaluated
binary64 constant

```text
0.4439938161680794
```

and must be pinned with the source and checked against an independent
high-precision quadrature in the production preflight.

## 4. Continuous catalyst and a strict homogeneous bound

The four slab centers, common half-width, and weights are

\[
 c=(0.35,0.60,0.75,0.90),\qquad s=0.04,
\]

\[
 w=(0.28,0.27736690132708747,0.0857172266153233,
     0.3569158720575891).
\]

Writing `phi_s(x)=b(x/s)/(s I_b)` and `d_W` for circular distance, the
unsmoothed continuous killing field is

\[
 K(M,R,Y)=\frac{B}{W}\sum_{j=1}^{4}w_j\phi_s(M-c_j)
 \mathbf 1\{R^2+d_W(Y,0)^2<a^2\},\qquad B=0.01.
\]

The catalyst bump is `C-infinity` at its support boundary.  The only spatial
discontinuity is the disk-contact indicator.  It must not be smoothed, sampled
on a grid, or replaced by a cell fraction in this solver.

A homogeneous domination rate can be certified without trusting numerical
quadrature.  On `|u|<=1/2`,

\[
 b(u)\ge e^{-4/3},\qquad I_b\ge e^{-4/3},\qquad
 \max b=e^{-1}.
\]

The four supports are disjoint, so at most one term is nonzero.  Hence

\[
 \|K\|_\infty
 \le {B\max_jw_j\over Ws}e^{1/3}
 =0.1245290564385021\ldots < \Lambda,
\]

and the solver freezes

\[
 \boxed{\Lambda=0.13}.
\]

The tighter profile-maximum diagnostic is `0.07393234251040665`, but it is not
used to justify `Lambda`.  Every evaluated rate must be finite, nonnegative,
and no larger than `Lambda`.  A violation aborts the run; clipping
`K/Lambda` to one is forbidden.

The contact-boundary convention (`<a` here) has no distributional effect.
At every positive Poisson candidate time the exact free transition has a
continuous density in the two relative coordinates, so the probability of
landing exactly on the contact circle is zero.  Bounded measurability, not
spatial continuity of `K`, is sufficient for thinning.

## 5. Why conditional thinning is exact

Independently of the free path, draw a rate-`Lambda` homogeneous Poisson
process.  At a candidate time `tau`, propagate `X_tau` with the exact free
transition above and accept a reaction with probability

\[
 K(X_\tau)/\Lambda.
\]

Conditional on one realized path, the probability of accepting no candidate
on `[0,t]` is the standard Poisson generating functional

\[
 \exp\left[-\int_0^tK(X_s)\,ds\right].
\]

Averaging over the free path gives the Feynman--Kac survival of the continuous
unbounded Doi process.  This argument permits bounded measurable hazards and
therefore covers the contact discontinuity.  “Exact” here means exact free
transition plus exact conditional thinning, with no spatial or time-step
discretization; it does not mean exact real arithmetic or an error-free
pseudorandom source.

## 6. Reproducibility and parallel execution

The proof of principle uses NumPy's counter-based `Philox` bit generator.  One
128-bit key is assigned to each `(master_seed, replicate_id, trajectory_id)`;
the path then consumes only its own stream.  A trajectory is consequently
unchanged by chunk size, worker count, scheduling order, or traversal order.
The unit tests reconstruct the same paths in forward and reverse order.

The production protocol should freeze:

1. the NumPy version and Philox key map;
2. two disjoint scientific replicate ID ranges;
3. the ordered trajectory ID range in every chunk;
4. raw integer counts and SHA-256 for every completed chunk;
5. a resume ledger that never reruns only an inconvenient statistical chunk;
6. one complete deterministic re-execution of the same IDs for byte/hash
   reproducibility; and
7. separate test seeds from all production seeds.

Distribution transforms such as `standard_normal` and `exponential` are
version-pinned even though Philox's raw integer stream is counter-stable.
Integer counts, rather than floating reduction order, should drive all final
survival, mass, and window estimates.

For scale, the provisional `N=6,000,000` pool can be split into two disjoint
`3,000,000`-trajectory scientific replicates and pooled only after a frozen
replicate-consistency check.  Path-keyed streams make multiprocessing safe.
The scalar Python proof of principle is not the required production engine;
the same formulas may be ported to a vectorized or compiled Philox kernel only
after cross-checking path fixtures and aggregate counts against this reference.

## 7. Estimands: no histogram-based modality gate

For each path record the first accepted time `T`, or right censor at 100.  The
primary estimators are integer-count estimators:

### 7.1 Survival

On a time grid frozen from the deterministic comparison,

\[
 \widehat S(t)=N^{-1}\sum_i\mathbf1\{T_i>t\}.
\]

Use the Dvoretzky--Kiefer--Wolfowitz band

\[
 \epsilon_S=\sqrt{\log(2/\alpha_S)/(2N)}
\]

for a simultaneous survival band.  This is stronger than separate pointwise
Wald intervals and remains valid on any fixed or post-evaluated time grid.

### 7.2 Valley-partitioned event masses

Let deterministic continuum/box analysis freeze valley cuts `v1<v2` before
the independent run.  Estimate

\[
 M_1=P(T\le v_1),\quad M_2=P(v_1<T\le v_2),\quad
 M_3=P(v_2<T\le100).
\]

Together with `S(100)` their empirical counts must sum exactly to `N`.
Use one-sided Clopper--Pearson limits with Bonferroni allocation across the
three masses.  A promoted mass requires both

\[
 L_i>0.005
\]

and an actual statistical radius no larger than one quarter of its distance
from the `0.005` scientific floor.

### 7.3 Finite-resolution modality contrasts

Monte Carlo cannot reliably locate zeros of `f_t`, and an adaptively tuned KDE
or visually selected histogram is not a topology certificate.  Instead, the
deterministic calculation must freeze equal-width, disjoint neighborhoods
around the ordered targets

\[
 P_1,V_1,P_2,V_2,P_3.
\]

For a window `A`, estimate the average density by

\[
 \widehat{\bar f}_A={\#\{T_i\in A\}\over N|A|}.
\]

Simultaneous one-sided Clopper--Pearson bounds must establish all four signs

\[
 \bar f_{P_1}>\bar f_{V_1},\quad
 \bar f_{P_2}>\bar f_{V_1},\quad
 \bar f_{P_2}>\bar f_{V_2},\quad
 \bar f_{P_3}>\bar f_{V_2}.
\]

These are finite-resolution physical contrasts, not a standalone proof of
five stationary points.  The converged deterministic solver remains
responsible for root isolation, curvatures, pointwise valley ratios, fourth
time jets, allocation rank, and the cusp Jacobian.  The independent solver
checks that the corresponding event-time pattern is present without the FV
box or discretization.

For fold-side controls, the same rule is applied to separately frozen windows
and the predeclared one-/two-/three-mode contrast pattern.  Window centers or
widths may not be moved after seeing independent counts.

## 8. Preliminary power calculation

Use a familywise type-I allocation

| Family | Allocated alpha |
|---|---:|
| survival DKW band | `0.01` |
| three basin-mass bounds | `0.02` |
| four peak--valley contrasts | `0.02` |

The already disclosed `N=97` feasibility trace has smallest mass
`p1=0.005307459366939327`.  Treating this only as a planning alternative, the
exact binomial power of the Bonferroni one-sided mass test at `N=6,000,000` is
`0.9999999999999994`.  At the nominal expected count, its two-tail
Clopper--Pearson interval is

```text
[0.005234372874031841, 0.005381356494689576]
```

with maximum radius `7.389712775024947e-05`, below one quarter of the disclosed
threshold distance, `7.686484173483163e-05`.

Using half-width `0.4` windows centered at the disclosed N=97 roots, the
PCHIP-integrated planning probabilities were

```text
(0.0014755815480, 0.0012142342226, 0.0017866740293,
 0.0014651531386, 0.0017189852934).
```

A conservative union-bound calculation combines binomial tail quantiles with
the simultaneous one-sided Clopper--Pearson limits.  At `N=6,000,000` it
certifies at least `0.90` joint power for the four contrast signs under those
planning alternatives.

Therefore `6,000,000` is a defensible **provisional** scale, not a frozen
production number.  The calculation must be repeated with the final
continuum/box window integrals and final smallest mass before production.  If
the true smallest mass is at or below `0.005`, no finite sample size can rescue
the scientific gate.  If its margin shrinks, the one-quarter-error rule, not
the round number six million, controls the required `N`.

## 9. Cross-method gates to freeze before production

For every independent estimand, first integrate the deterministic FV
continuum/box density over exactly the same time set.  Do not compare a window
average with a pointwise peak height.  Report

\[
 x_{FV}\pm E_{FV},\qquad x_{MC}\pm E_{MC}.
\]

Freeze a method-discrepancy allowance `tau_x` before independent outcomes and
require

\[
 |x_{FV}-x_{MC}|\le E_{FV}+E_{MC}+\tau_x.
\]

Every `tau_x` must be smaller than one quarter of the deterministic distance
to the nearest scientific threshold.  The minimum production package is:

1. simultaneous survival agreement on the frozen time grid;
2. agreement of all three valley-partitioned event masses and `S(100)`;
3. exact empirical mass closure to one;
4. all four trimodal window contrasts with simultaneous passing-side bounds;
5. cross-method agreement of all five window probabilities, not only their
   signs;
6. the analogous predeclared contrast pattern at each promoted fold-side
   representative;
7. stability across the two independent trajectory pools; and
8. zero rate-bound, RNG-key, sampler-cap, nonfinite-state, or chunk-ledger
   failures.

The MC calculation does not validate `f_tttt`, mixed allocation jets,
singular values, or the cusp Jacobian.  Those quantities must pass mesh,
alignment, and box convergence in the deterministic route.

## 10. Bounded proof-of-principle result

The lightweight run used 32,768 paths for the analytic invariant and 16,384
paths for the frozen broad configuration.  It is intentionally far below the
production power requirement.

### Analytic one-channel invariant

With a state-independent hazard `k=0.05` thinned from `Lambda=0.13`, the exact
reaction law is exponential with survival `exp(-kt)`.  On six times through
40, the maximum empirical error was

```text
0.0025736523102622977
```

inside the `alpha=0.001` simultaneous DKW half-width

```text
0.010769427436720583.
```

This validates the candidate/acceptance machinery against an analytic killed
law.  The exact thinning identity in Section 5, not the probabilistic DKW
outcome, is the mathematical justification.

### Broad-configuration smoke

The state-dependent run completed without a rate-bound violation.  Its
largest evaluated rate was `0.07393234140131526`, and 193,465 candidate points
were processed.  The N=97 valley-cut smoke counts were

```text
(76, 286, 2487), with 13,535 survivors at T=100.
```

The first mass estimate was below `0.005`, but its wide simultaneous interval
`[0.0034284,0.0061243]` contains the disclosed deterministic value.  At this
small sample size the window counts are only `(25,19,41,26,29)`.  Consequently
this smoke neither passes nor fails the physical mass/modality claim; it only
shows that the exact state-dependent path and estimator pipeline executes.

Two complete executions produced byte-identical JSON with SHA-256

```text
b657300581e5c7e4e482c5569b081bbdd5e4c281cec95b8ae5f074c8ae7571c1.
```

Current source anchors are

| Role | SHA-256 |
|---|---|
| proof-of-principle producer | `90466d074d3b6d302143919d4160beb36109e9686312e3a33670321e4f297e9d` |
| focused tests | `986e839ebaa7f5b56d328826312fcce1f1305a2493108e5da8d7558992cc365d` |
| proof-of-principle result | `b657300581e5c7e4e482c5569b081bbdd5e4c281cec95b8ae5f074c8ae7571c1` |

These are POC provenance anchors only.  Any production optimization changes
the source anchor and requires a new pre-run audit.

## 11. Production stop/go sequence

1. Complete and audit the deterministic mesh/alignment and box estimates.
2. Freeze the exact FV comparison grid, valley cuts, time windows, window
   widths, fold-side controls, all `E_FV`, and every `tau_x`.
3. Recompute the power plan from those frozen alternatives; freeze `N`, seeds,
   ID ranges, chunks, package versions, and failure policy.
4. Cross-check a compiled/vectorized engine against fixed trajectory fixtures
   and this POC's aggregate analytic invariant.
5. Run the two disjoint production pools without inspecting partial scientific
   estimates; permit resume only by predeclared chunk IDs.
6. Apply simultaneous intervals and cross-method gates once.
7. Repeat the exact IDs for reproducibility and run an independent audit.

Until all seven steps pass, the correct project decision is **HOLD**.
