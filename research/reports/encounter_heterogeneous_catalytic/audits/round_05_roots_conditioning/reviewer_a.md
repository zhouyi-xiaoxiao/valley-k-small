# Round 05 roots, conditioning, tails, and convergence audit — Reviewer A

Date: 2026-07-11  
Reviewer: A (independent root and convergence stress audit)  
Verdict: **no B0 or B1; three bounded B2 claim-boundary issues found and resolved in the current snapshot; one B3 numerical-hardening recommendation**

## Scope and independence

I audited root isolation, continuation, conditioning, finite-horizon tails, fit-window
selection, and spatial/time discretization for the following evidence layers:

- the synchronous one-dimensional encounter chain and its independent-clock CTMC;
- the fixed-shape GIG fold and the physical finite-CTMC fold;
- the finite-radius 2D endpoint, matched-control, fold, trimodal, and
  centre-coordinate calculations;
- the 2D logarithmic-capacity and 3D Newtonian-capacity calculations; and
- the constructive GIG designs in dimensions $d=1,\ldots,4$.

I checked current source, saved numerical artifacts, manuscript text, notes, and
tests. I did not read a Round-05 Reviewer-B report. I did not edit any scientific
source, test, manuscript, numerical artifact, or proof; this file is my only
workspace output.

Severity follows `audits/README.md`: B0 blocks submission, B1 requires a material
change of derivation/evidence/framing, B2 is a bounded correction or mandatory
caveat, and B3 is optional hardening.

The main result is positive. I found no missing reported fold, no cut-off reported
mode, no near-even root in a declared finite model, no unstable solved fold, no
fit-window choice that manufactures a claimed exponent, and no hidden time-step
dependence. The finite 1D CTMC, physical CTMC fold, both finite 2D folds, four-grid
2D trimodality, and all 12 multidimensional GIG screening examples survive
independent root scans. The 2D capacity coefficient approaches its theoretical
value under a genuine grid/radius matrix. The 3D calculation is accurate along
its declared coupled path, but that path is not a separated double limit.

The most consequential root-level observation is that the five matched
homogeneous 2D controls are **not strictly unimodal**: each has a small second
local maximum. They are correctly *resolved-unimodal* under the declared 3%
rule. Patterning makes the late mode resolved; it does not create the mathematical
existence of that local maximum in this endpoint family. The distinction preserves
the paper's declared resolved-morphology conclusion but must appear everywhere,
not only in the abstract.

## Findings

### F1 — B2, resolved in the current snapshot: matched homogeneous controls are resolved-unimodal, not strictly unimodal

The canonical morphology calculation labels all five matched homogeneous
controls `unimodal`. A separate exact-semigroup derivative calculation gives a
different topological statement. For killed generator $T$, killing vector
$b$, and initial law $\alpha$, I evaluated

\[
f_t(t)=\alpha e^{Tt}Tb,
\qquad
f_{tt}(t)=\alpha e^{Tt}T^2b,
\]

bracketed every sign change of $f_t$, and refined the brackets with fresh
matrix exponentials. On every saved $9\times5$ through $17\times13$ grid,
the homogeneous control has maximum--minimum--maximum ordering. From the saved
curves, the second-peak/primary-peak ratios are

| grid | homogeneous second/primary peak | valley/second peak |
|---|---:|---:|
| $9\times5$ | 0.01753 | 0.82384 |
| $11\times7$ | 0.01437 | 0.63195 |
| $13\times9$ | 0.01810 | 0.42462 |
| $15\times11$ | 0.01716 | 0.31054 |
| $17\times13$ | 0.01023 | 0.34028 |

Thus every secondary maximum is genuine but lies below the declared 3% height
threshold. The independently refined midpoint-control roots are

| grid | exact $f_t=0$ times |
|---|---|
| $9\times5$ | 0.555305, 8.993556, 15.984435 |
| $11\times7$ | 0.636664, 8.622578, 17.767413 |
| $13\times9$ | 0.779249, 8.328089, 19.370221 |
| $15\times11$ | 0.867567, 8.203259, 20.096541 |
| $17\times13$ | 0.696963, 7.955459, 18.770119 |

These are not numerical tangencies. Solving every sign-changing $f_{tt}=0$
root and evaluating $f_t/f$ there gives a minimum absolute value between
0.0464 and 0.0520 for these midpoint controls. The same audit for the weighted
centre convention gives three simple roots and comparable margins. The coarsest
weighted patterned endpoint is classifier-labelled `shoulder` but is likewise
strictly bimodal; the label is a resolution category, not a root count.

The original validator inferred the control statement only from the multiscale
classifier (`code/validate_2d_matched_homogeneous.py:113-152,269-279`). During
this audit, the main thread added exact-semigroup stationary-point output and a
regression requiring two strict homogeneous maxima below the 3% resolution
threshold (`code/validate_2d_matched_homogeneous.py:155-215,281-340` and
`tests/test_encounter_2d_matched_control_artifacts.py:36-45`). Its revised module
docstring now states the correct mechanism: a resolution-class transition, not
creation of the mathematical second maximum
(`code/validate_2d_matched_homogeneous.py:11-16`).

The manuscript now uses that qualifier consistently. The abstract and
main-result list say `resolved-bimodal` versus `resolved-unimodal`
(`manuscript/encounter_modality_jcp.tex:61-69,169-175`). The matched-control
discussion and caption report the strict subthreshold maximum and call the
comparison a resolution-class change
(`manuscript/encounter_modality_jcp.tex:931-957`); the centre-coordinate
discussion and caption use the same semantics
(`manuscript/encounter_modality_jcp.tex:1051-1059,1070-1080`).

**Required interpretation.** The endpoint evidence supports a controlled change
in *observable/resolved* modality at fixed discrete killing budget. It does not
support the stronger sentence “patterning creates a second local maximum” for
M2D-E. This correction does not affect the separate M2D-F derivative fold, where
a strict stationary pair is genuinely born.

### F2 — B2, resolved in the current snapshot: finite sign-change scans detect simple roots but do not certify exhaustive root counts

Several validators use a dense sampled derivative followed by Brent refinement.
That is a sound way to obtain each bracketed simple root, but by itself it cannot
exclude

1. an even-multiplicity zero of $f_t$,
2. a narrow pair of sign-changing zeros inside one sample interval, or
3. a new pair beyond the finite audit horizon.

The implementation boundary is visible in the 2D fold endpoint scanner:
`_stationary_points_from_scan` accepts only sampled strict sign changes
(`code/validate_2d_matched_fold.py:535-545`). Consequently wording such as
“retains every strict stationary point” is too strong; “retains every detected
sign-changing stationary point” is the accurate claim. The fold itself is not
at risk because it is solved directly from $f_t=f_{tt}=0$, and the code
correctly injects the double root at criticality rather than asking a sign
scanner to find it (`code/validate_2d_matched_fold.py:606-645`).

The trimodal validator scans $f_t$ with spacing 0.02 on $[0,100]$, spacing 1
on $[100,2000]$, then refines five sign-change brackets
(`code/validate_2d_trimodal.py:188-260`). It also checks the off-root logarithmic
slope and the decreasing tail (`code/validate_2d_trimodal.py:268-326`). Those are
strong diagnostics, not an interval proof. During this audit, the main thread
corrected the claim boundary: the validator now asks for “five detected simple”
roots (`code/validate_2d_trimodal.py:2-9`), the note explicitly denies an
exhaustive count on $(0,\infty)$
(`notes/finite_radius_2d_trimodality.md:79-93`), and the manuscript says exactly
what the finite scan cannot exclude
(`manuscript/encounter_modality_jcp.tex:1125-1132`). The multidimensional GIG
section already has the same honest boundary
(`manuscript/encounter_modality_jcp.tex:1355-1361`).

My stronger numerical check solves every sign-changing root of $f_{tt}$ on the
trimodal audit grid and evaluates $f_t$ at those extrema. Each saved model has
five $f_{tt}$ roots. The minimum off-root value of $|f_t|/f$ at those
extrema is 0.01151, 0.01146, 0.01072, and 0.01074 on the four grids. Thus no
even root or near-tangency is numerically indicated. The finite trimodality
existence claim needs only the five listed alternating roots; an undiscovered
extra pair would not erase the three reported maxima.

**Current resolution.** The endpoint paragraph now says “every detected
sign-changing stationary point” and explicitly states that the finite scan does
not certify the absence of tangential or narrower roots between sample times
(`manuscript/encounter_modality_jcp.tex:1016-1027`). Together with the trimodal
and multidimensional caveats above, this closes the wording issue. Future code
and tests should continue to reserve `tail_complete` for a spectral/interval
bound rather than a finite sampled audit.

### F3 — B2, resolved by an explicit claim downgrade: the 3D small-target path is not a separated double limit

The fixed-$\chi$ shrinking-radius calculation pairs

\[
(a,N)=(0.18,41),(0.13,57),(0.095,79),(0.07,109),(0.055,139),(0.045,169),
\]

so $a/h=aN$ stays between 7.38 and 7.65
(`code/validate_3d_capacity.py:60-71,166-176`). Therefore $a\to0$ is taken at
essentially fixed local target resolution. The separate grid study is performed
only at $a=0.09$ (`code/validate_3d_capacity.py:60-63,152-163`). It cannot prove
that the discretization bias is uniform in $a$, and it cannot convert the
coupled-path slope into a certified continuum coefficient.

This is not a hypothetical scale mismatch. At fixed $a=0.09$, the six means
are

\[
3.487031, 3.477507, 3.486912, 3.487450, 3.484232, 3.486500.
\]

The finest-pair difference is 0.065%, but the range over the finest four is
0.092%. That is comparable to the reported 0.114% slope discrepancy. The
sequence is also nonmonotone, so a single finest-pair difference is not an
error bound. The excellent PCG residuals test the linear solve, not the
continuum discretization.

The current implementation now records
`fixed_chi_radius_and_grid_limits_separated = False`, sets
`continuum_capacity_coefficient_certified = False`, and labels the result a
coupled-path finite-grid check
(`code/validate_3d_capacity.py:273-345`; regression at
`tests/test_encounter_3d_artifacts.py:34-62`). The manuscript likewise calls the
0.114% agreement “continuum-compatible finite-grid evidence, not a separated
double-limit certification” and says that the two limits are not separately
extrapolated (`manuscript/encounter_modality_jcp.tex:1263-1289`). That bounded
downgrade resolves the overclaim without changing any computed number.

If a later version wants to promote the continuum coefficient, I recommend
cross-refinement at at least three radii. For two initial stress radii, useful
odd periodic grids are

- $a=0.095$: $N=59,79,99,119$, giving $a/h=5.61,7.51,9.41,11.31$;
- $a=0.055$: $N=101,139,173,199$, giving $a/h=5.56,7.65,9.52,10.95$.

Use at least four levels because the cell-averaged discontinuous Doi sphere has
geometric phase oscillations. Compare $p=1$, $p=2$, and fitted/shared-order
extrapolations with leave-one-resolution-out spreads; do not infer an error bar
from one three-point $h^2$ line. A third radius is needed to refit a continuum
slope rather than merely bound path bias. A `subcell_samples=6` versus 8 or 10
check at one medium and one fine grid per radius would separate geometry
quadrature from finite-difference error.

### F4 — B3: archive dimensionless conditioning, fit-window sensitivity, and exact-tail derivative margins

The solved folds are numerically sound, but the most persuasive conditioning
evidence is currently reconstructible rather than stored. For

\[
H(t,\theta)=(f_t,f_{tt}),\qquad
D H=\begin{pmatrix}f_{tt}&f_{t\theta}\\f_{ttt}&f_{tt\theta}\end{pmatrix},
\]

my independent values are:

| model | raw 2-norm condition number | dimensionless condition number | Newton correction from saved residuals $(\delta t,\delta\theta)$ |
|---|---:|---:|---|
| finite 1D CTMC | 4.81 | 45.6 | $(-4.27\times10^{-13},-3.63\times10^{-14})$ |
| finite 2D $11\times7$ | 38.0 | 656 | $(2.47\times10^{-13},-3.07\times10^{-15})$ |
| finite 2D $13\times9$ | 15.3 | 86.5 | $(-2.67\times10^{-12},-4.07\times10^{-14})$ |

The dimensionless scaling uses input units $(t_*,\max(|\theta_*|,10^{-3}))$
and output units $(f_*/t_*,f_*/t_*^2)$. The 11x7 point is relatively sensitive
because $\theta_*$ is small, but the saved residuals imply negligible local
root error. The 0.242 cross-grid movement of the 2D fold is therefore a
discretization/model movement, not a failed nonlinear solve. For the physical
CTMC, an independent central difference gives
$f_{tt\theta}=-4.5705818\times10^{-10}$, stable from parameter step
$10^{-2}$ down to $3\times10^{-5}$.

Fit-window selection is also benign but worth archiving. Using the smallest
$n$ positive continuation steps gives:

| model | $n$ | separation exponent | prominence exponent |
|---|---:|---:|---:|
| 1D physical CTMC | 3 | 0.50025 | 1.50229 |
| 1D physical CTMC | 6 (reported) | 0.50095 | 1.50877 |
| 1D physical CTMC | 7 | 0.50155 | 1.51423 |
| 2D $11\times7$ | 3 | 0.49856 | 1.49659 |
| 2D $11\times7$ | 6 (reported) | 0.49331 | 1.48430 |
| 2D $11\times7$ | 8 | 0.48122 | 1.45675 |
| 2D $13\times9$ | 3 | 0.49986 | 1.50080 |
| 2D $13\times9$ | 6 (reported) | 0.49932 | 1.50385 |
| 2D $13\times9$ | 8 | 0.49796 | 1.51257 |

The smallest points are closest to the normal form. The fixed first-six choice
is conservative, not a post-selection trick. Persisting this small table would
make that fact visible to a reviewer.

For the trimodal roots, the crude timing-error proxy
$\max|f_t|/\min|f_{tt}|$ ranges from $1.61\times10^{-10}$ to
$3.44\times10^{-12}$ across the four grids. The exact-tail scans described
below also show strong negative logarithmic slopes. I recommend storing the
fold condition numbers, fit-window table, and $f_{tt}$-extremum/tail margins
in the JSON artifacts and regression-gating broad bounds. This is B3 because
the underlying results already pass.

## Independent root, tail, and convergence checks

### 1D synchronous chain and independent-clock CTMC

Across the complete saved synchronous PMFs, not merely the plotting window, I
find exactly two raw local maxima and one intervening minimum for each
$L=31,41,61,81$. The propagated unresolved mass is below $10^{-12}$, and
there are no tail extrema. The smallest relative adjacent-bin margin at a
reported late maximum is $2.87\times10^{-6}$ (at $L=61$); the peak is shallow
on the one-step lattice scale but not tied.

For the independent-clock CTMC, direct analytic derivatives give:

| $L$ | $f_t=0$ roots on $[0,1200]$ | minimum $|f_t|/f$ at an $f_{tt}=0$ extremum | survival at 1200 |
|---:|---|---:|---:|
| 31 | 32.153423, 78.278944, 196.092078 | 0.00658 | $3.67\times10^{-5}$ |
| 41 | 31.975756, 103.533453, 270.040734 | 0.00546 | $1.61\times10^{-4}$ |
| 61 | 31.975650, 153.547760, 434.341606 | 0.00452 | $1.89\times10^{-3}$ |

An additional derivative scan from 1200 to 5000 finds no sign change. The
largest tail logarithmic derivative is already negative, and the final
survivals are $1.12\times10^{-21},1.58\times10^{-20},5.97\times10^{-19}$.
Thus the finite plotting/classification horizon does not cut off a later mode.
The manuscript correctly presents this CTMC only as independent-clock
robustness, not a calibrated limit of the synchronous model.

### Fixed-shape GIG and physical CTMC fold

For the declared early/late GIG pair, clearing the positive density factors
reduces the fold determinant to the degree-six rational polynomial recorded in
the Round-04 algebra audit. An exact-rational Sturm count gives two and only two
positive roots, 28.0410937447543 and 157.527847347136. Both are interior
in weight and nondegenerate. This exact completeness is model-specific; the
generic 20,001-point routine at `code/validate_gig_fold.py:224-273` remains a
sign-change scanner, not an all-roots algorithm for arbitrary channels.

Around the physical CTMC fold, a global scan on $[0,500]$ gives one simple
late root at $t\simeq198.2746$ on the one-peak side and three roots on the
two-peak side: the born pair near $t=37.075$, plus the persistent late root.
For every declared continuation displacement
$\delta\theta=\pm0.001,\ldots,\pm0.064$, the global count agrees with the
local continuation record. At criticality the sign scan sees only the
persistent simple root, as it should; solving $f_{tt}=0$ recovers the double
root. A further scan from 500 to 5000 has no sign change and ends at survival
$1.323\times10^{-21}$. This closes the possible objection that the local
$\pm3$ continuation window silently omitted a competing late pair.

### 2D endpoints, fold, trimodality, and centre coordinate

For the two finite 2D fold grids, recomputation of the analytic Jacobians gives
the saved determinants $2.20844\times10^{-9}$ and
$4.44643\times10^{-10}$, with the residual corrections in F4. A coarse
independent continuation scan at $\theta=0,0.05,\ldots,1$ finds only one
root-count transition on either grid: $1\to3$ stationary points. It does not
prove uniqueness between parameter samples, but no second branch is indicated.
Held-out root-pair fits become closer to $(1/2,3/2)$ as the window shrinks, so
the reported first-six fits are not selected to create agreement.

For the primary obstacle-free 2D bimodal family, exact derivative scans to
$t=240$ give three simple $f_t$ roots on every $9\times5$ through
$15\times11$ grid and no further root in the tail. Solving the sampled
$f_{tt}$ brackets reveals no near-even root. This independently supports the
saved resolved classification, while the finite scanner should still not be
described as an interval theorem.

For the matched M2D-E family and both centre conventions, exact derivative
scans to $t=960$ find the three roots described in F1 and no post-window root
pair. The largest remaining survival is $1.22\times10^{-10}$. The supplemental
weighted-coordinate M2D-T calculation has five roots

\[
0.542887, 4.603738, 8.933932, 15.918386, 47.631365,
\]

with alternating curvature, minimum off-root $|f_t|/f=0.01116$, and
survival $5.77\times10^{-12}$ at 2000. The midpoint convention has the five
saved roots. Thus the centre-coordinate sensitivity changes masks and the
coarsest resolution label, but it does not introduce an undetected root loss in
the tested supplemental family.

For the main four-grid trimodal family, the independently solved $f_{tt}$
extrema give minimum $|f_t|/f$ margins 0.01151, 0.01146, 0.01072,
and 0.01074. Saved root residuals divided by the smallest curvature imply
sub-$2\times10^{-10}$ timing errors. The audit endpoint has negative derivative,
survival below $4.22\times10^{-11}$, and no additional detected tail root.
These checks strongly support the five simple roots while respecting the
non-exhaustive finite-scan boundary in F2.

### 2D and 3D capacity fits

The 2D logarithmic-capacity fit is not a held-out-window artifact. On the
finest $401^2$ grid, slope/theory is

- 0.98483 using all five radii (reported);
- 0.99008 using the smallest four radii; and
- 0.99695 using the smallest three radii.

The larger-radius three-point window gives 0.97604. Thus the small-target
coefficient moves toward theory as both the radius window shrinks and the grid
is refined. Across grids 161, 241, 321, and 401, the reported all-five ratios are
0.94970, 0.97899, 0.98388, and 0.98483. The $161^2$ smallest targets are
under-resolved, but the trend is explicit and the manuscript does not promote
the finest number to an exact continuum value.

For 3D, the slope/theory ratios using the smallest 3, 4, 5, and 6 radii are
0.999168, 0.998856, 0.997789, and 0.997160. The asymptotic-window trend is
excellent. F3 remains necessary because all these points share essentially the
same $a/h$; fit stability in $a$ does not replace cross-refinement in $h/a$.

### Multidimensional GIG screening designs

For every $d=1,2,3,4$ and each two-, three-, or four-channel construction, I
repeated the logarithmic score scan at 5,000, 20,000, and 80,000 samples and
doubled the published horizon from five to ten times the last isolated mode.
Every resolution and horizon gives exactly $2m-1$ roots. At the refined roots,
the global minimum dimensionless curvature is
$\min |t^2 f_{tt}/f|=1.971$. At every score extremum away from a root,
$\min |t f_t/f|=0.859$. These large margins explain why the root count is
insensitive to scan resolution. The result remains, correctly, a free-space
narrow-patch screening construction rather than a bounded-domain theorem.

## Execution record and reproduction commands

The principal artifact generators are:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python research/reports/encounter_heterogeneous_catalytic/code/build_report.py
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python research/reports/encounter_heterogeneous_catalytic/code/validate_gig_fold.py
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python research/reports/encounter_heterogeneous_catalytic/code/validate_2d_finite_radius.py
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python research/reports/encounter_heterogeneous_catalytic/code/validate_2d_matched_homogeneous.py
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python research/reports/encounter_heterogeneous_catalytic/code/validate_2d_matched_fold.py
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python research/reports/encounter_heterogeneous_catalytic/code/validate_2d_trimodal.py
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python research/reports/encounter_heterogeneous_catalytic/code/validate_2d_centre_coordinate.py
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python research/reports/encounter_heterogeneous_catalytic/code/validate_2d_capacity.py
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python research/reports/encounter_heterogeneous_catalytic/code/validate_3d_capacity.py
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python research/reports/encounter_heterogeneous_catalytic/code/validate_multid_gig_design.py
```

The independent derivative audit used generator actions rather than finite
differences. Its core calculation for any killed finite model was:

```python
k = np.asarray(model.channel_rate_matrix.sum(axis=1)).reshape(-1)
Ak, A2k = model.killed_generator @ k, model.killed_generator @ (model.killed_generator @ k)
states = expm_multiply(model.killed_generator.T, initial, start=t0, stop=t1, num=n)
ft, ftt = states @ Ak, states @ A2k
brackets = np.flatnonzero(np.signbit(ft[:-1]) != np.signbit(ft[1:]))
extrema = np.flatnonzero(np.signbit(ftt[:-1]) != np.signbit(ftt[1:]))
```

Every bracket quoted above was refined with `scipy.optimize.brentq` and a fresh
`expm_multiply`; $f_t/f$ was then evaluated at every refined $f_{tt}=0$
point to stress even roots.

The focused regression command was:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -q -p no:cacheprovider \
  tests/test_fpt.py tests/test_morphology.py \
  tests/test_encounter_gig_fold.py \
  tests/test_encounter_2d_artifacts.py \
  tests/test_encounter_2d_matched_control_artifacts.py \
  tests/test_encounter_2d_matched_fold.py \
  tests/test_encounter_2d_matched_fold_artifacts.py \
  tests/test_encounter_2d_trimodal_artifacts.py \
  tests/test_encounter_2d_centre_coordinate_artifacts.py \
  tests/test_encounter_2d_capacity_artifacts.py \
  tests/test_encounter_3d_artifacts.py \
  tests/test_encounter_multid_gig_design.py \
  tests/test_encounter_manuscript.py \
  tests/test_encounter_publication_pipeline.py
```

After the corrected 2D/3D artifacts were regenerated, this command produced
54 passes and two failures. Both failures are confined to the aggregate
`publication_pipeline.manifest.json`, whose source/output inventory predates the
in-turn source, manuscript, notebook, and child-artifact updates. All child
scientific artifact tests, including their own manifest hashes, pass. Rebuilding
the aggregate inventory after the final manuscript edit is the remaining
pipeline step; it is not a numerical-root failure.

## Submission assessment

No root, fold, tail, or convergence issue found here requires abandoning the
encounter program or changing the principal derivations. The finite 1D and 2D
folds are well conditioned at their saved roots; local normal-form fits improve
as the fitting window shrinks; the bounded 2D trimodality examples have large
root and classifier margins; and the multidimensional GIG designs are far from
tangency in the tested families.

For a strong journal submission, the non-negotiable language boundaries are:

1. matched M2D-E controls are **resolved-unimodal with a subthreshold strict
   second maximum**;
2. finite sign scans provide **detected** root counts, not interval-certified
   exhaustive counts; and
3. current 3D capacity agreement is **coupled-path, continuum-compatible
   finite-grid evidence**, not a separated $a\to0,h/a\to\infty$ coefficient.

With those boundaries enforced and the artifacts/manifests regenerated, the
root/conditioning evidence is suitable as a finite-model mechanism package.
A later promotion from finite-model evidence to a continuum theorem would need
interval/spectral tail control for root exhaustiveness and cross-refined
capacity/fold calculations, not merely denser versions of the same scans.
