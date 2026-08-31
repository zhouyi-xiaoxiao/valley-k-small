# Round 05 Reviewer B: roots, conditioning, tails, and convergence

Date: 2026-07-11  
Reviewer role: independent Reviewer B  
Scope: fixed-shape GIG folds, finite-CTMC channel modes and physical fold,
finite-radius 2D fold and trimodality roots, strict-versus-resolved morphology,
tail horizons, and 2D/3D mesh/radius convergence.

## Independence and verdict

I did **not** read any Round-05 Reviewer-A report. I inspected the scientific
source, manuscript, machine-readable artifacts, tests, and manifests directly.
I then performed read-only recomputations that do not take the serialized
conclusions as inputs: an exact rational Sturm count, positivity-preserving
uniformization checks, finer semigroup derivative scans, finite-difference
parameter sensitivities, direct Jacobian conditioning, normal-form prefactor
reconstruction, raw-NPZ root recounting, classifier replay, and independent
OLS fits.

**Verdict: PASS for the present finite-state and finite-grid claim boundary,
with four non-blocking B3 hardening findings.** I found no open B0, B1, or B2
scientific defect. The two finite 2D fold coordinates are correctly withheld
as nonconverged; the trimodal result is correctly bounded to detected roots on
four finite grids; the 3D shrinking-radius result is correctly identified as a
coupled radius/mesh path rather than a separated double limit.

The saved roots themselves are reproducible and nondegenerate. The principal
hardening issue is that the unconstrained physical-CTMC HYBR solve can report a
binary64-underflow zero as a successful root from other seeds. The archived
physical root is not such a root: it has positive density, small dimensionless
residuals, a nonsingular scaled Jacobian, stable finite-difference parameter
derivatives, and the expected held-out continuation.

## Severity summary

| Severity | Open | Verdict |
|---|---:|---|
| B0 | 0 | No submission-blocking mathematical or numerical contradiction. |
| B1 | 0 | No material failure of the reported finite-state/fold evidence. |
| B2 | 0 | Claim boundaries, root non-exhaustiveness, and coupled-limit caveats are present in the manuscript and artifacts. |
| B3 | 4 | Add an underflow/physical-domain root guard; record scaled Jacobian conditioning and the full 2D determinant; rename finite-scan “global mode” language; make sampled late-tail searches explicitly non-exhaustive and derivative-based. |

## 1. Fixed-shape GIG determinant: exact positive-root count

The implementation at
`code/validate_gig_fold.py:224-278` brackets strict sign changes of

\[
g_1'g_2''-g_2'g_1''=0
\]

on a logarithmic grid and refines them with Brent. For the declared rational
parameters

\[
(A_1,B_1,\nu_1)=\left(\frac{570}{7},\frac{81}{2000},2\right),
\qquad
(A_2,B_2,\nu_2)=\left(\frac{1125}{2},\frac9{1000},\frac32\right),
\]

I independently divided out the strictly positive factor \(g_1g_2\), cleared
\(t^6\), and formed the primitive integer polynomial

\[
\begin{aligned}
P(t)={}&750141t^6+173974500t^5-30982297500t^4\\
&+2119355000000t^3-525714637500000t^2\\
&-37701450000000000t+1439606250000000000.
\end{aligned}
\]

An exact `Fraction` Euclidean Sturm chain has length seven. Its sign-variation
counts are \(V(0^+)=3\) and \(V(+\infty)=1\), so \(P\) has **exactly two**
positive roots. The intervals \((28,29)\) and \((157,158)\) each contain one;
Brent refinement gives

\[
t_1=28.04109374475425,qquad
t_2=157.52784734713586,
\]

matching `artifacts/data/gig_fold_summary.json` to displayed precision. Thus
the two saved fixed-shape folds are not a missed-root artifact of the log grid.
The saved weights \(3.67235\times10^{-5}\) and \(0.878060\) lie in the simplex,
the third derivatives are nonzero, and the weight-transversality magnitudes
are \(2.18\times10^{-4}\) and \(1.96\times10^{-5}\).

This exact Sturm certificate is stronger than the current scan implementation
and would be worth archiving, but its absence does not invalidate the reported
canonical roots.

## 2. Finite CTMC: channel modes and physical fold

### 2.1 Channel modes

`validate_gig_fold.py:392-484` scans the analytical derivative
\(\alpha e^{Tt}Tb_j\), refines positive-to-negative crossings, checks negative
curvature, and selects the largest detected maximum. I reconstructed the
reversible similarity transform of each free walker; its maximum symmetry
error was \(1.67\times10^{-16}\). A positivity-preserving uniformization with
rate \(1.8162909135\), cross-checked against direct sparse exponentials, gives:

| Channel | root | derivative 0.5 before | derivative 0.5 after | curvature at root |
|---|---:|---:|---:|---:|
| near | 32.1534061543 | \(+1.96\times10^{-6}\) | \(-1.86\times10^{-6}\) | \(-3.82\times10^{-6}\) |
| far | 196.145870007 | \(+3.89\times10^{-7}\) | \(-3.84\times10^{-7}\) | \(-7.73\times10^{-7}\) |

An independent direct-semigroup scan with \(\Delta t=0.05\), ten times finer
than the production bracket grid, found one positive-to-negative crossing for
each channel on \(0\le t\le500\): \([32.15,32.20]\) and
\([196.10,196.15]\). Both derivatives are negative at \(t=500\). These checks
validate the reported continuous-time roots, not an interval theorem excluding
an even root or an arbitrarily narrow root pair.

### 2.2 Physical fold and conditioning

The stored fold is

\[
(t_*,\theta_*)=(37.0749586401533,-9.67536358534634),
\qquad f(t_*,\theta_*)=1.7873048347\times10^{-7}.
\]

It has dimensionless first/second residuals
\(7.12\times10^{-15}\) and \(6.78\times10^{-13}\), dimensionless third
derivative \(69.9421\), and dimensionless transversality \(-0.196202\). Central
differences in $\theta$, for steps from $10^{-4}$ to $3\times10^{-6}$,
give

\[
f_{tt\theta}=-4.5705818\times10^{-10}
\]

stably and reproduce the augmented sensitivity. In the natural dimensionless
coordinates \((\log t,\theta)\), for residuals
\((tf_t/f,t^2f_{tt}/f)\), the fold Jacobian is

\[
J_{\rm sc}=
\begin{pmatrix}
6.78\times10^{-13} & -0.196202\\
69.9421 & -3.51507
\end{pmatrix},
\]

with determinant \(13.7228\) and 2-norm condition number \(357.38\). This is
moderately conditioned, not singular. The raw Jacobian determinant is
\(2.32015\times10^{-19}\), but that dimensional number is not a useful
conditioning measure by itself. The held-out continuation slopes \(0.500954\)
and \(1.508770\), and first-step normal-form ratios within \(0.4\%\), provide an
independent local check (`tests/test_encounter_gig_fold.py:129-150`).

### B3-1: reject underflow-zero HYBR roots

`validate_gig_fold.py:487-558` checks only `solution.success` before accepting
the HYBR output. Using the same objective but different plausible seeds gives:

| seed | returned \((t,\theta)\) | density | scaled objective | solver status |
|---|---|---:|---|---|
| $(37,-9.7)$ | $(37.07496,-9.67536)$ | $1.79\times10^{-7}$ | physical residual | success |
| $(30,-10)$ | $(0.095644,-34.2859)$ | exactly `0.0` in binary64 | `(0.0, 0.0)` | success |
| $(45,-9)$ | $(0.095100,-43.7608)$ | exactly `0.0` in binary64 | `(0.0, 0.0)` | success |

The latter two are numerical underflow, not physical folds. Before accepting a
root, require a declared $(t,\theta)$ box, finite strictly positive density
above a scale-aware floor, finite dimensionless residuals, nonzero
transversality/third derivative, and agreement under at least two perturbed
seeds or a bounded two-dimensional root isolation. Store \(J_{\rm sc}\) and
its condition number in the artifact. Current tests on the saved artifact
would reject `NaN` dimensionless residuals, and the saved root passes all
independent checks, so this is a hardening finding rather than a current-result
failure.

### B3-2: finite-scan mode wording

The docstring at `validate_gig_fold.py:399-405` says “global mode,” although
the method only brackets sampled positive-to-negative crossings. Change this
to “largest detected negative-curvature mode on the declared horizon” and
serialize flags analogous to the trimodal artifact:
`exhaustive_root_count_claimed=false` and
`tangential_or_unresolved_pairs_excluded=false`. The manuscript statement at
`manuscript/encounter_modality_jcp.tex:832-841` needs no numerical correction;
it identifies the roots and honestly reports the GIG approximation error.

## 3. Two-dimensional matched-budget folds

`code/validate_2d_matched_fold.py:257-353` computes generator derivatives and
an augmented-exponential $\theta$ sensitivity. I rebuilt both sparse families,
reevaluated each stored fold, and central-differenced the parameter direction.
The largest relative discrepancy in \(f_{t\theta}\) or \(f_{tt\theta}\) was
\(3.1\times10^{-7}\). The full Jacobians and the normal-form prefactors were
then reconstructed independently.

| Grid | \((t_c,\theta_c)\) | \((|f_t|,|f_{tt}|)\) | full \(\det J\) | scaled \(\kappa_2(J)\) | fitted exponents sep./prom. |
|---|---|---|---:|---:|---|
| \(11\times7\) | \((18.0995323,0.01381035)\) | \((8.67\times10^{-19},1.73\times10^{-18})\) | \(2.208445\times10^{-9}\) | 10.93 | \(0.493314,1.484297\) |
| \(13\times9\) | \((16.5807587,0.25589201)\) | \((3.04\times10^{-18},1.73\times10^{-17})\) | \(4.446435\times10^{-10}\) | 24.69 | \(0.499325,1.503854\) |

The direct coefficients

\[
c_{\rm sep}=2\sqrt{-2f_{t\theta}/f_{ttt}},\qquad
c_{\rm prom}=\frac23|f_{ttt}|
\left(-2f_{t\theta}/f_{ttt}\right)^{3/2}
\]

are \((17.0113277,0.00320540869)\) and
\((10.0088764,0.000497897976)\), exactly matching the artifact. At the smallest
held-out step, observed/predicted separation and prominence are
\((0.999406,0.998599)\) and \((0.999941,1.000328)\). This confirms the local
normal form and its prefactors, not only the exponents.

The critical controls differ by \(0.242082\), exceeding the declared 0.05
tolerance. `finite_radius_2d_fold_metrics.json` sets
`fold_location_grid_converged=false`, and the manuscript explicitly withholds
a continuum fold location at
`encounter_modality_jcp.tex:1043-1054,1468-1470`. That is the correct verdict.

### B3-3: store the full determinant and scaled condition number

At `validate_2d_matched_fold.py:337-348`, the serialized determinant is
implemented as \(-f_{t\theta}f_{ttt}\), omitting the
\(f_{tt}f_{tt\theta}\) term. At the saved roots the omitted term is negligible,
and the independently computed full determinants agree at the displayed
precision. Nevertheless the artifact should store `np.linalg.det(jacobian)`
and a dimensionless condition number. This prevents an approximate root with a
non-negligible \(f_{tt}\) residual from receiving an overstated nonsingularity
certificate.

## 4. Four-grid trimodality root audit

The root search at `code/validate_2d_trimodal.py:188-334` uses exact generator
derivatives, a fine scan \(\Delta t=0.02\) to \(t=100\), a unit-step scan to
\(t=2000\), and Brent refinement. I ignored the saved conclusion fields and
recounted sign changes directly from
`finite_radius_2d_trimodal_series.npz`.

| Grid | independently recounted roots | tail survival at 2000 |
|---|---|---:|
| \(9\times5\) | 0.834886, 3.823238, 8.531644, 17.305200, 34.211723 | \(4.218\times10^{-11}\) |
| \(11\times7\) | 0.489944, 4.178023, 8.488865, 16.654060, 38.582269 | \(3.416\times10^{-12}\) |
| \(13\times9\) | 0.919346, 4.516386, 9.014553, 15.956824, 48.233972 | \(1.890\times10^{-11}\) |
| \(15\times11\) | 0.859700, 4.942975, 9.330786, 15.595632, 48.838247 | \(2.161\times10^{-11}\) |

For every grid:

- all five saved roots fall strictly inside independently located sign-change
  brackets;
- curvature signs alternate maximum/minimum/maximum/minimum/maximum;
- the raw \(0.2\)-step density has three maxima and two minima;
- the exact maxima are dominated in order by near, middle, and far channels;
- \(f_t<0\) at every audit sample from 0.5 after the last root to \(t=2000\);
- the smallest absolute root curvature is \(6.62\times10^{-6}\), and the
  smallest off-root absolute log-slope diagnostic is \(0.01199\).

The maximum Brent residual is \(1.863\times10^{-15}\), the minimum classifier
margin is \(0.005685\), and the minimum dominant channel share is \(0.7182\).
The artifact and focused test explicitly set both
`exhaustive_positive_time_root_count_claimed=false` and
`tangential_or_unresolved_narrow_root_pairs_excluded=false`
(`tests/test_encounter_2d_trimodal_artifacts.py:20-68`). The detailed manuscript
is equally precise at `encounter_modality_jcp.tex:1166-1187`.

For editorial consistency, README line 32 should say “five **detected,
Brent-refined exact-semigroup** stationary roots,” rather than “five exact
stationary roots.” This is wording hardening; the manuscript and artifact do
not claim a global exact root count.

## 5. Strict roots versus resolved morphology

The canonical classifier thresholds are declared at
`validate_2d_matched_homogeneous.py:91-122` and implemented in
`packages/vkcore/src/vkcore/morphology.py:832-891,954-1150`. Replaying the
classifier from the archived time series reproduces all five paired labels.
Directly recomputing ratios from the exact-semigroup stationary points gives:

| Grid | homogeneous strict secondary/primary | patterned strict secondary/primary | patterned valley/weaker peak |
|---|---:|---:|---:|
| \(9\times5\) | 0.017532 | 0.045807 | 0.6783 |
| \(11\times7\) | 0.014372 | 0.063851 | 0.4583 |
| \(13\times9\) | 0.018099 | 0.081475 | 0.3082 |
| \(15\times11\) | 0.017157 | 0.075435 | 0.2440 |
| \(17\times13\) | 0.010229 | 0.076260 | 0.2304 |

Both endpoints have two strict maxima on every grid. Every homogeneous
secondary maximum fails the declared 3% relative-height threshold; every
patterned endpoint passes the complete multiscale classifier. The manuscript
therefore correctly says “promotion of a subthreshold transport clock,” not
creation of a new mathematical extremum
(`encounter_modality_jcp.tex:958-984`).

The adverse controls also preserve the distinction. `single_far` and
`coalesced_far` have strict secondary/primary ratios 0.4803 and 0.4837, but
their valley/weaker-peak ratios are 0.9597 and 0.9570, above the 0.80 resolved
threshold; they are resolved-unimodal rather than strictly unimodal.
`separated_boundary` and `uniform_reactivity` have valley ratios 0.5043 and
0.2588 and are resolved-bimodal. This supports the narrow mechanism statement
and rules out necessity language.

## 6. Tail horizons and what they do not certify

The saved survival bounds are numerically adequate for the claims made:

- physical CTMC fold: \(S(5000)=1.323\times10^{-21}\), mass-closure error
  \(4.00\times10^{-15}\);
- matched M2D-E family: maximum patterned \(S(960)=1.212\times10^{-10}\),
  maximum homogeneous \(S(960)=8.492\times10^{-30}\);
- two primary 2D fold grids: all endpoint \(S(480)\le9.575\times10^{-10}\);
- five-grid fold endpoint robustness audit: all ten tails below
  \(1.9\times10^{-6}\);
- trimodal family: maximum \(S(2000)=4.218\times10^{-11}\), with augmented
  mass-closure errors at most \(1.63\times10^{-12}\).

As an independent worst-tail check, I rebuilt the \(9\times5\) patterned and
homogeneous M2D-E generators. A derivative scan with \(\Delta t=1\) from
\(t=80\) to 960 found no sign change and had \(f_t<0\) at every point; the
direct survivals reproduced \(1.2117334505792\times10^{-10}\) and
\(8.4916339308229\times10^{-30}\).

Survival at a late horizon is a remaining-mass bound; by itself it is not a
root-isolation theorem. The trimodal artifact correctly separates those two
ideas. The matched-control late audit at
`validate_2d_matched_homogeneous.py:125-142` instead searches sampled density
maxima at spacing four. Its current result is supported by the finer derivative
check above, but the generic implementation should be hardened.

### B3-4: make late searches derivative-based and explicitly bounded

For M2D-E/M2D-C tail audits, archive the actual late time grid and \(f_t\),
bracket every detected sign change with the exact semigroup, and serialize
`exhaustive=false` unless interval isolation is performed. Wording such as “no
post-window maxima were detected on the declared audit grid” is preferable to
an unqualified “no post-window maxima were found.” This does not change the
resolved labels on the shape window or the very small remaining-mass bounds.

## 7. Mesh/radius convergence and coupled limits

### 7.1 Two dimensions

Independent OLS fits of the archived fixed-
\(\chi=\kappa a^2/D_r=1\) means against \(\log(1/a)\) reproduce:

| grid \(n\) | slope/theory | relative slope error | \(R^2\) | minimum \(a/h\) |
|---:|---:|---:|---:|---:|
| 161 | 0.949695 | 5.030% | 0.999429 | 3.22 |
| 241 | 0.978987 | 2.101% | 0.999906 | 4.82 |
| 321 | 0.983883 | 1.612% | 0.999958 | 6.42 |
| 401 | 0.984829 | 1.517% | 0.999961 | 8.02 |

For each fixed physical radius, the last two grid means differ by only
0.011%--0.084%. This is strong finite-grid calibration of the logarithmic
slope, with a visible 1.52% coefficient discrepancy; it is not a theorem for
the reflecting centre-patterned model. The manuscript states exactly that
these are translation-invariant relative-coordinate benchmarks
(`encounter_modality_jcp.tex:1252-1277,1481-1483`).

### 7.2 Three dimensions

Independent refits against \(1/a_{\rm eff}\) give:

- all six coupled-path points: slope/theory \(0.997160\), relative error
  \(0.2840\%\), \(R^2=0.99999815\);
- smallest four radii: slope/theory \(0.998856\), relative error \(0.11439\%\),
  \(R^2=0.99999978\);
- fixed \(a=0.09\): last-pair grid difference \(0.0651\%\);
- smallest-radius fixed-\(\kappa\) scaled mean: \(1.0004232\).

However, the shrinking-radius path holds \(a/h\) only between 7.38 and 7.645.
Thus radius and grid limits are coupled. The smallest-radius mean remains
3.09% below its leading small-target term, consistent with a non-negligible
additive periodic correction. The metrics set
`fixed_chi_radius_and_grid_limits_separated=false` and
`continuum_capacity_coefficient_certified=false`; the manuscript repeats this
at `encounter_modality_jcp.tex:1313-1339`. No double-limit promotion is present.

The same discipline is applied to modality: the five-grid M2D-E endpoint
labels are robust, but the finest discrete matched rate \(1.84907\) is still
14.8% below the finite-\(a\) continuum geometric reference \(2.16940\); the 2D
fold control is nonconverged; and the four-grid trimodal family is explicitly
not a cell-averaged continuum trimodal region.

## 8. Focused gates

I ran the following read-only focused suite with bytecode and pytest cache
disabled:

```text
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -q -p no:cacheprovider \
  tests/test_encounter_gig_fold.py \
  tests/test_encounter_2d_matched_fold.py \
  tests/test_encounter_2d_matched_fold_artifacts.py \
  tests/test_encounter_2d_trimodal_artifacts.py \
  tests/test_encounter_2d_matched_control_artifacts.py \
  tests/test_encounter_2d_mechanisms_artifacts.py \
  tests/test_encounter_2d_centre_coordinate_artifacts.py \
  tests/test_encounter_2d_capacity_artifacts.py \
  tests/test_encounter_3d.py \
  tests/test_encounter_3d_artifacts.py
```

Result: **43 passed**. These gates include the child-manifest output hashes,
the fold nondegeneracy and continuation checks, strict/resolved semantics,
trimodal non-exhaustiveness flags, tail bounds, and 2D/3D convergence limits.

## Final disposition

The core Round-05 conclusions are numerically and logically supportable:

1. the canonical fixed-shape GIG determinant has exactly two positive roots;
2. the reported finite-CTMC channel roots and physical fold are reproducible;
3. both 2D folds are locally nondegenerate and have the predicted prefactors,
   while their critical control is not grid-converged;
4. the bounded trimodal family has five detected alternating simple roots and
   three resolved, channel-attributed maxima on each tested grid, without a
   global root-count claim;
5. strict roots, resolved morphology, tail mass, and continuum limits are kept
   conceptually separate.

Before artifact freeze, implement the four B3 hardening items above. None
requires changing the reported scientific numbers or strengthening the claim
boundary.
