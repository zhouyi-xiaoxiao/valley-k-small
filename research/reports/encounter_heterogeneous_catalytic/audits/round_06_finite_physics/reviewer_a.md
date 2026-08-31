# Round 06 finite-radius 2D/3D physics audit — Reviewer A

Date: 2026-07-11  
Reviewer: A (independent physical, discretization, and numerical audit)  
Verdict: **no B0; one B1 framing error was found and corrected at source level during the audit, three bounded B2 issues were likewise corrected or explicitly downgraded in source, but the regenerated artifact gate is still open; one independent B2 provenance failure and two B3 hardening items remain**

## Scope and independence

I audited the finite-radius two- and three-dimensional claims against the live
manuscript, numerical kernels, generators, saved data, child manifests, and
focused tests.  In particular I tried to falsify:

- the reflecting boundary-node CTMC and its units;
- the finite-radius contact and catalytic-patch masks;
- the midpoint and diffusivity-weighted affine encounter coordinates;
- the equal-state-sum homogeneous budget;
- the claimed patterned-versus-homogeneous modality contrast;
- the separate interior, single-patch, co-located, and uniformly reactive
  controls;
- the two-dimensional logarithmic-capacity coefficient and Doi impedance;
- the three-dimensional Doi effective radius and reaction-limited law;
- grid/radius convergence language; and
- every attempted inference from a finite grid or a translation-invariant
  mean-time calculation to a bounded centre-patterned continuum modality
  result.

I did not inspect a Round-06 Reviewer-B report and did not edit a scientific
source, test, artifact, figure, notebook, or manuscript.  This report is my
only file write.  Severity follows `audits/README.md`: B0 blocks submission,
B1 materially changes the evidence or framing, B2 is a bounded correction or
required caveat, and B3 is optional hardening.

The underlying finite-state and capacity calculations are sound.  The main
issue was semantic but scientifically material: the original endpoint and
control language identified the canonical morphology classifier with strict
mathematical mode count.  Exact semigroup derivatives show that every matched
homogeneous endpoint already has a small second local maximum.  Patterning
promotes that subthreshold transport clock to a resolved mode; it does not
create the existence of the second maximum in M2D-E.  The independent M2D-F
folds remain genuine max--min pair-creation certificates, so this correction
does not remove the paper's finite-grid fold evidence.

During this audit the main thread corrected that language in the live
manuscript and validators.  It also corrected a finite-radius continuum-budget
reference, clarified that the 3D radius and grid limits are coupled, and
removed an incorrect implication that equal node weights are a drifted CTMC
invariant measure.  At the snapshot checked here, however, the corresponding
JSON/CSV/NPZ/figures/manifests had not yet been regenerated.  The focused live
gate therefore still failed on stale artifacts.  Source-level correction is
not a frozen publication certificate until those artifacts and tests agree.

## Findings

### F1 — B1, source-level correction complete but artifact revalidation open: resolved morphology was presented as strict modality creation

The saved M2D-E endpoint artifact classifies the patterned curves as
`bimodal` and their equal-budget homogeneous controls as `unimodal`.  The old
paper-facing interpretation was that spatial redistribution changed the
number of modes.  That inference is false for strict local maxima.

I independently formed

\[
 b=B\mathbf 1,\qquad b_1=Tb,\qquad b_2=T^2b,
\]

evaluated

\[
 f(t)=\alpha e^{Tt}b,\qquad
 f_t(t)=\alpha e^{Tt}b_1,\qquad
 f_{tt}(t)=\alpha e^{Tt}b_2,
\]

scanned `0 <= t <= 80` at `dt=0.1`, and Brent-refined every sign-changing
root of `f_t`.  All five patterned and all five homogeneous curves have the
strict ordering maximum--minimum--maximum:

| grid | patterned smaller/larger maximum | homogeneous smaller/larger maximum |
|---|---:|---:|
| `9x5` | 0.0458068 | 0.0175320 |
| `11x7` | 0.0638505 | 0.0143718 |
| `13x9` | 0.0814746 | 0.0180990 |
| `15x11` | 0.0754353 | 0.0171568 |
| `17x13` | 0.0762596 | 0.0102287 |

For example, the `11x7` homogeneous roots are

\[
 t=(0.6366640,\ 8.6225777,\ 17.7674134),
\]

in max--min--max order.  Thus the homogeneous late maximum is real but only
`1.44%` of the primary maximum, below the declared `3%` resolution threshold.
The patterned counterpart has roots at
`0.9902551, 8.4992207, 19.5177396` and a `6.39%` peak ratio.

The same distinction matters in M2D-C.  On `11x7` I obtained:

| control | exact roots (max, min, max) | smaller/larger maximum |
|---|---|---:|
| separated boundary patches | `0.859802, 6.862925, 16.457526` | 0.385976 |
| single far patch | `4.991240, 6.514652, 16.799622` | 0.480321 |
| co-located labels | `4.970061, 6.526162, 16.767102` | 0.483706 |
| uniform reactivity | `1.072374, 7.704067, 23.947268` | 0.241152 |

The single and co-located controls are rejected because the intervening dip
is too shallow, not because a strict second maximum is absent.  The uniformly
reactive adverse control remains a genuine and resolved bimodal curve, so the
important conclusion that patterning is not necessary survives.

The current source-level resolution is scientifically correct:

- the manuscript now says that M2D-E is a
  `resolved-unimodal -> resolved-bimodal` or resolution-class change, retains
  the homogeneous strict maxima, and explicitly denies creation of a
  previously nonexistent extremum
  (`manuscript/encounter_modality_jcp.tex:931-957`);
- the controls are now called resolved-unimodal and their shallow strict
  extrema are disclosed (`manuscript/encounter_modality_jcp.tex:1086-1111`);
- the discussion and conclusion say that patterning promotes a subthreshold
  clock into a resolved mode (`manuscript/encounter_modality_jcp.tex:1318-1324,
  1479-1487`);
- the matched validator now stores strict stationary points, strict mode
  counts, and the homogeneous secondary-peak ratio
  (`code/validate_2d_matched_homogeneous.py:155-203,308-340`); and
- the mechanism validator does the same for all four controls
  (`code/validate_2d_mechanisms.py:150-207,322-340`).

This correction does not affect the M2D-F fold: that separately declared
family has a nondegenerate derivative tangency on each of two finite grids,
and the manuscript continues to withhold a continuum fold location because
the two critical controls differ by `0.242`
(`manuscript/encounter_modality_jcp.tex:985-1036`).

**Open gate.**  At the latest executed gate, the saved M2D-E and M2D-C JSON
files still lacked the new `resolved_classification`,
`strict_stationary_points`, and `strict_mode_count` fields.  Their source
hashes therefore also disagreed with their child manifests.  The B1 is not a
frozen resolution until both validators are rerun, the figures/manifests are
regenerated, the manuscript is rebuilt, and the focused tests pass without
excluding these checks.

### F2 — B2, corrected in source but not yet regenerated: the old “continuum area match” is not the finite-radius continuum budget

The discrete matching rule itself is exact and correct:

\[
 \bar\kappa_h
 =\frac{\sum_x K_{\rm pat}(x)}{N_{\rm tube}},
 \qquad
 \sum_xK_{\rm hom}(x)=\sum_xK_{\rm pat}(x).
\]

Direct mask counting independently reproduced every saved rate:

| grid | tube states | near states | far states | recomputed `kappa_bar` |
|---|---:|---:|---:|---:|
| `9x5` | 125 | 7 | 9 | 1.108000000 |
| `11x7` | 217 | 18 | 24 | 1.700460829 |
| `13x9` | 541 | 55 | 63 | 1.797597043 |
| `15x11` | 1333 | 132 | 159 | 1.838709677 |
| `17x13` | 2203 | 227 | 264 | 1.849069451 |

The old artifact nevertheless labelled

\[
 \pi\left(0.5\,0.18^2+15\,0.20^2\right)=1.935849393
\]

as the continuum matched rate and tested that the finest grid lay within
`5%`.  That expression is only the small-contact-radius area-average
reference.  At the actual finite contact radius `a=0.13`, the encounter-tube
cross-section is truncated near the square boundary.

For midpoint coordinates `C=(x1+x2)/2`, `r=x1-x2`, the transformation has
unit Jacobian and the exact tube volume in the unit square is

\[
 \begin{aligned}
 V_{\rm tube}(a)
 &=\int_{|r|\le a}(1-|r_x|)(1-|r_y|)\,dr\\
 &=\pi a^2-\frac{8}{3}a^3+\frac12a^4.
 \end{aligned}
\]

Both patterned patches have centre-space boundary clearance greater than
`a/2=0.065`, so their relative disks are untruncated.  The correct finite-`a`
continuum match is therefore

\[
 \bar\kappa_{\rm cont}(a)
 =\frac{\pi a^2\,\pi(0.5\,0.18^2+15\,0.20^2)}
 {\pi a^2-(8/3)a^3+a^4/2}
 =2.169402271.
\]

An independent lattice-offset count confirms which reference the binary-node
scheme approaches: `kappa_bar` is `1.95858` on `25x19`, `2.06542` on
`49x37`, `2.09023` on `81x61`, and `2.13269` on `161x121`.  The saved
`17x13` value is `14.77%` below the correct finite-`a` reference, not `4.48%`
below a continuum limit.  This does not weaken the exact within-grid
counterfactual; it only removes a misleading convergence label.

The live validator now contains the correct formula and names
`continuum_patterned_area_weight`, `continuum_encounter_tube_volume`, and
`continuum_finite_a_matched_rate`
(`code/validate_2d_matched_homogeneous.py:73-87,368-371,459-468`).  The test
now checks the exact tube formula and explicitly expects the declared coarse
grid family still to be `10%--16%` below it
(`tests/test_encounter_2d_matched_control_artifacts.py:53-73`).

**Open gate.**  The saved JSON/CSV/figure/manifest still contained the old
`continuum_area_matched_rate` at the last check.  Regenerate them before this
finding is closed.

### F3 — B2, source-level caveat complete but artifact revalidation open: the 3D small-target and mesh limits are coupled

The 3D radius family uses

\[
 (a,N)=(0.18,41),(0.13,57),(0.095,79),(0.07,109),(0.055,139),(0.045,169).
\]

Thus `a/h=aN` remains between approximately `7.38` and `7.65` while `a` is
shrunk.  The excellent smallest-four fit therefore follows a coupled
`a -> 0`, `h -> 0` path with essentially fixed target resolution.  It is not
a separated double limit and cannot by itself certify the continuum capacity
coefficient.  The separate fixed-radius scan at `a=0.09` does demonstrate
grid stability at that radius, but it does not separate the two limits for
every point in the shrinking-radius family.

My independent least-squares recomputation from the saved rows gives

\[
 \text{slope}_{\rm small4}=0.0794864452524,
 \qquad
 \frac{\text{slope}}{1/(4\pi)}=0.998856129859,
\]

with `R^2=0.999999776946`.  These numbers are correct.  The appropriate claim
is that the coupled finite-grid path is continuum-compatible at `0.114%`, not
that it certifies a double-limit coefficient.

The live source now makes exactly that distinction:

- the generator records
  `fixed_chi_radius_and_grid_limits_separated = False` and
  `continuum_capacity_coefficient_certified = False`
  (`code/validate_3d_capacity.py:274-300,307-345`);
- the 3D note calls the result fixed-grid compatibility and states the
  `a/h=7.4--7.6` coupling
  (`notes/finite_radius_3d_capacity.md:111-130`); and
- the manuscript calls the `0.114%` result continuum-compatible finite-grid
  evidence, reports the separately refined fixed-radius check, and says the
  shrinking-radius limits were not separately extrapolated
  (`manuscript/encounter_modality_jcp.tex:1263-1309`).

**Open gate.**  At the last check, the saved 3D metrics still had status
`validated_with_small_target_and_grid_limitations` and lacked the new boolean
scope fields; the child manifest also hashed the pre-correction generator.
Regenerate the 3D data/figure/manifest and rerun the focused tests.

### F4 — B2: the 2D capacity child manifest does not hash the current solver

The focused capacity test fails because
`finite_radius_2d_capacity.manifest.json` records

```text
packages/vkcore/src/vkcore/encounter2d.py
sha256 = 3d8dae2951777a23c62d8068949f36c86358ba13d1b1a1b01fd01515e7a1b85a
```

whereas the current file hashes to

```text
fd122fa421a88f6826b41a31e86a9dfab94bd99ec5376e177e8a3fbfbda07d96
```

All other source and output hashes in that child manifest matched.  The
manifest was generated before later `encounter2d.py` changes.  This is a real
provenance failure even though the periodic-capacity path appears numerically
unchanged.

To separate provenance from physics, I reran four representative solves with
the current code.  The `N=401`, `a=0.05`, `kappa=400` mean was
`0.6278696550264866`, and the `a=0.02`, `kappa=2500` mean was
`0.7715239654719307`; both agree with the artifact to floating roundoff.  The
fixed-`kappa` `N=241` means at `a=0.12` and `0.02` also reproduced exactly.
Therefore I found no numerical capacity drift, but the stale hash means the
saved artifact is not currently self-authenticating.

**Required correction.**  Regenerate the 2D capacity child manifest from the
current solver (or rerun the validator if the publication workflow requires
all outputs to be refreshed) and make
`tests/test_encounter_2d_capacity_artifacts.py:58-74` pass.

### F5 — B3: persist the coordinate-control strict roots rather than asserting them only in prose

The revised manuscript accurately says that all six homogeneous controls in
the midpoint-versus-weighted coordinate audit are resolved-unimodal while
small strict secondary maxima remain
(`manuscript/encounter_modality_jcp.tex:1051-1058`).  The current coordinate
validator and artifact, however, do not store derivative-refined stationary
points.

I independently verified the statement.  The weighted-coordinate homogeneous
secondary/primary ratios are `0.0144047`, `0.0125697`, and `0.0190486` on
`9x5`, `11x7`, and `13x9`; the midpoint values are `0.0175320`, `0.0143718`,
and `0.0180990`.  Each curve has a max--min--max root ordering.

This is not a correctness defect, but storing these roots and ratios in
`finite_radius_2d_centre_coordinate.json` would make the new manuscript
sentence directly traceable rather than dependent on an unpersisted audit.

### F6 — B3: tail-certify the longest uniform-domain clock scan in the saved artifact

The uniform-domain scan ends at `t=160`.  At `L=3`, the late maximum is at
`122.2`, but saved survival at the horizon is still `0.1520`.  The linear
late-clock fit is correct:

\[
 t_{\rm late}=49.1314L-25.3714,
 \qquad R^2=0.999964,
 \qquad 0.02\times49.1314=0.98263.
\]

I extended only the `L=3` curve from `t=160` to `960`.  No additional sampled
local maximum appeared, survival fell from `0.1520168` to
`1.12e-21`, and the density was monotonically decaying over the extension.
Persisting this late audit would remove an avoidable horizon question from the
boundary-clock control.  The existing claim about the location of the already
observed late maximum is nevertheless supported.

## Checks that passed

### Reflecting boundary-node CTMC, masks, and units

The method identity is now honest.  `RectangularGrid2D` uses boundary nodes at
spacing `L/(n-1)`, not finite-volume cell centres
(`packages/vkcore/src/vkcore/encounter2d.py:29-90`).  The generator rates are

\[
 q_{i,i\pm e_x}=\frac{D}{h_x^2}+\frac{[\pm v_x]_+}{h_x},
 \qquad
 q_{i,i\pm e_y}=\frac{D}{h_y^2}+\frac{[\pm v_y]_+}{h_y},
\]

with `v_y=-gamma(y-y0)`, omitted outward jumps, and a diagonal equal to minus
the actual escape rate
(`packages/vkcore/src/vkcore/encounter2d.py:341-406`).  Hence all off-diagonal
rates are nonnegative and every row sum vanishes.  The units are consistent:
`D/h^2`, `v/h`, `gamma`, and intrinsic Doi `kappa` all have units `1/time`.

For the drifted principal `11x7` walker I explicitly found
`max |Q 1| < 5e-16`.  I also falsified the old invariant-measure wording:
`max |pi_uniform Q|=0.0818182`, while only the zero-drift chain has uniform
stationary mass.  The current manuscript correctly calls the equal weights a
geometric state-sum quadrature and says the budget is not a stationary-exposure
match (`manuscript/encounter_modality_jcp.tex:848-863`).

The pair generator is the correctly ordered Kronecker sum.  Contact is tested
by `|X1-X2|^2 <= a^2`, the catalytic coordinate is
`C_eta=eta X1+(1-eta)X2`, and circular patch masks are binary node tests.
Channel rates add on overlaps and are subtracted from the diagonal
(`packages/vkcore/src/vkcore/encounter2d.py:449-537`).  Propagation with
`expm_multiply(T.T, initial)` is the correct column action corresponding to
row-vector dynamics, and flux is `p(t)B`
(`packages/vkcore/src/vkcore/encounter2d.py:564-613`).

The exact operator identity

\[
 T\mathbf 1+B\mathbf 1=0
\]

holds to the recorded `3.8e-15` level or better.  A zero-motion reactive state
also reproduces `kappa exp(-kappa t)` in the core tests
(`tests/test_encounter_2d.py:130-155`).

### Midpoint versus diffusivity-weighted coordinates

The bounded model consistently declares the physical midpoint `eta=1/2`.
The free-space noise-decoupling coordinate instead uses

\[
 \eta_* = \frac{D_2}{D_1+D_2}=0.242424\ldots,
 \qquad
 C_\eta=R+(\eta-\eta_*)r.
\]

The two are not treated as equivalent.  Direct mask reconstruction reproduced
the saved near/far Jaccard distances exactly:

| grid | near distance | far distance |
|---|---:|---:|
| `9x5` | 0.222222 | 0.100000 |
| `11x7` | 0.100000 | 0.076923 |
| `13x9` | 0.229508 | 0.149254 |

The coarse patterned classification changes from bimodal to shoulder; the
finer two remain resolved-bimodal under both coordinates.  The manuscript
correctly withholds equivalence and continuum robustness
(`manuscript/encounter_modality_jcp.tex:1039-1080`).

### Interior and adverse controls

The M2D-C far centre-space patch at `x=0.75`, radius `0.18`, has clearance
`0.07`; since `a/2=0.065`, even its reactive pair cross-section remains just
inside the particle domain.  The four saved grids are resolved-bimodal and
tail-complete.  The manuscript correctly says this is not proof of wall
independence because late paths may still reach the reflecting boundary
(`manuscript/encounter_modality_jcp.tex:1095-1099`).

The uniformly reactive `11x7` adverse control is independently strict and
resolved bimodal.  It therefore correctly rules out any claim that spatial
patterning is necessary.  M2D-C is also explicitly declared a different
parameter family, not a factorial ablation of M2D-E or M2D-F.

### Two-dimensional capacity

For a translation-invariant torus, the quotient to `r=X1-X2` is exact and has
relative diffusivity `D_rel=D1+D2`.  The local Green singularity

\[
 G(r,r')\sim-\frac{1}{2\pi D_{\rm rel}}\log|r-r'|
\]

has the correct sign and units.  Matching a regular interior Doi solution
`I0(qr)` to the exterior logarithmic field gives the dimensionless intrinsic
impedance

\[
 \beta_{\rm int}^{\rm Doi}
 =\frac{I_0(\lambda)}{\lambda I_1(\lambda)},
 \qquad \lambda=a\sqrt{\kappa/D_{\rm rel}}.
\]

Its weak-reaction limit is `2/lambda^2`, which recovers the area reaction rate
`kappa*pi*a^2`.

Independent ordinary least squares on the saved mean-time rows reproduced:

| `N` | fitted slope / `1/(2*pi)` | `R^2` |
|---:|---:|---:|
| 161 | 0.949695 | 0.9994294 |
| 241 | 0.978987 | 0.9999057 |
| 321 | 0.983883 | 0.9999581 |
| 401 | 0.984829 | 0.9999607 |

The finest grid resolves the smallest disk with `a/h=8.02`.  At fixed
`kappa=1`, the maximum error from `1/(kappa*pi*a^2)` is `0.8313%`, attained at
the largest tested radius.  I also checked the discrete integrated backward
identity `kappa*mean(chi*u)=1` to `1.1e-12` in a fresh `81x81` solve.

These results support a translation-invariant mean-time calibration, not a
centre-patterned continuum modality theorem, exactly as stated in
`manuscript/encounter_modality_jcp.tex:1202-1227,1431-1433`.

### Three-dimensional Doi effective radius

For the exterior capture field `c_out=1-a_eff/r` and regular interior field
`c_in proportional to sinh(qr)/r`, continuity of value and flux at `r=a`
gives

\[
 \frac{a_{\rm eff}}{a}
 =1-\frac{\tanh z}{z},
 \qquad z=a\sqrt{\kappa/D_{\rm rel}}=\sqrt\chi.
\]

Thus

\[
 k_{\rm Doi}^{(3)}=4\pi D_{\rm rel}a_{\rm eff}.
\]

For small `chi`,

\[
 a_{\rm eff}
 =a\left(\frac{\chi}{3}-\frac{2\chi^2}{15}+O(\chi^3)\right),
\]

so `k_Doi -> kappa*(4*pi*a^3/3)`.  The formula and the Taylor coefficients in
`packages/vkcore/src/vkcore/encounter3d.py:106-157` are correct.

I independently assembled the periodic seven-point operator on a `9^3` grid
and compared it with the matrix-free PCG solver.  The outside means were
`3.2267330094397946` and `3.2267330094400024`, a relative difference of
`6.4e-14`; `kappa*mean(chi*u)=0.9999999999999999`.  This checks the FFT
preconditioned implementation independently of its own artifact.

From the saved production rows:

- the fixed-radius `a=0.09` finest-grid pair differs by `0.0651%`;
- the maximum target-volume error at the finest fixed-radius grid is
  `1.09e-5`;
- the fixed-`kappa` smallest-radius volume-law error is `0.0423%`;
- the largest reported relative linear residual is `6.23e-14`; and
- the largest solve has `169^3=4,826,809` states without an assembled matrix.

The units are also correct: `4*pi*D*a_eff` is volume/time and
`V/(4*pi*D*a_eff)` is time.

## Executed checks and current gate state

The initial finite-2D focused suite, before the live audit corrections, was:

```text
uv run pytest -q \
  tests/test_encounter_2d.py \
  tests/test_encounter_2d_artifacts.py \
  tests/test_encounter_2d_centre_coordinate_artifacts.py \
  tests/test_encounter_2d_matched_control_artifacts.py \
  tests/test_encounter_2d_matched_fold.py \
  tests/test_encounter_2d_matched_fold_artifacts.py \
  tests/test_encounter_2d_mechanisms_artifacts.py \
  tests/test_encounter_2d_trimodal_artifacts.py
```

Result: `31 passed`.

The capacity/core suite initially gave `13 passed, 1 failed`; the sole failure
was the stale 2D capacity source hash described in F4.  After the main thread
added the honest strict-mode, finite-`a`, and coupled-limit fields to source
and tests, I reran the combined live gate:

```text
uv run pytest -q \
  tests/test_encounter_2d.py \
  tests/test_encounter_2d_matched_control_artifacts.py \
  tests/test_encounter_2d_mechanisms_artifacts.py \
  tests/test_encounter_2d_capacity_artifacts.py \
  tests/test_encounter_3d.py \
  tests/test_encounter_3d_artifacts.py
```

Result at that instant: `20 passed, 9 failed`.  The failures were all
traceable to source/test versus not-yet-regenerated artifact fields or child
hashes, plus F4's older 2D capacity hash.  They are not evidence of a failed
semigroup or capacity solve, but they are real publication-gate failures.

## Publication boundary and required closeout

I found no B0 in the finite-radius physics.  The following statements are
supported once the live corrections are frozen:

1. The declared reflecting boundary-node CTMC and binary-mask Doi model are
   valid finite-state models with correct units and mass balance.
2. M2D-E shows that spatial redistribution of an exactly matched discrete
   budget can promote a pre-existing subthreshold transport clock into a
   resolved mode across five declared grids.
3. M2D-F supplies genuine nondegenerate finite-grid fold certificates, but not
   a grid-converged critical control.
4. A non-touching centre-space patch retains resolved bimodality, without
   proving wall independence.
5. Uniform reactivity can itself be bimodal, so patterning is not necessary.
6. The periodic 2D and 3D solvers reproduce the appropriate capacity scalings
   as finite-grid, translation-invariant mean-time benchmarks; they do not
   establish centre-patterned continuum modality.

Before Round 06 can close, rerun at least the corrected matched-endpoint,
mechanism-control, and 3D-capacity validators; refresh the 2D capacity child
manifest; rebuild dependent figures/manuscript artifacts; and rerun the
focused gates with zero exclusions.  F5 and F6 are optional but would make the
evidence boundary substantially easier for an external referee to audit.

