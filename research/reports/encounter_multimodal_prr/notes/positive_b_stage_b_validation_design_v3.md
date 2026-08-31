# Positive-`B` Stage-B validation design v3

Date: 2026-07-14  
Status: **GO-DESIGN / HOLD-EXECUTION**  
Scope: result-blind finite-volume validation of a grid-specific numerical
allocation cusp and its fold branches, followed by a separately frozen
off-lattice validation of event-law features at unchanged physical controls

## 0. Purpose, inputs, and non-execution boundary

This document replaces neither v2 nor any scientific artifact.  It creates a
new design version that repairs the independent Round-62 attack while
preserving the parts of v2 that survived that attack.  It is a design contract,
not evidence that Stage A or Stage B passed, and it authorizes no scientific
execution.

It was written from these four result-blind design/audit inputs:

| role | repository path | SHA-256 |
|---|---|---|
| Stage-B v2 design | `notes/positive_b_stage_b_validation_design_v2.md` | `8d64c54c2d4727583dc9ee513fc3fc58af57835283b68111a648f6ef33f63f84` |
| Round-57 re-audit | `audits/round_57_stageb_independent_reaudit.md` | `953bb602c29bb0ef2556e1a3ce63c0a309a4f298701c4ec7e6da9937194f0ab3` |
| Round-58 v2 resolution | `audits/round_58_stageb_v2_design_resolution.md` | `7f05c922a1835face49d58f0dfe06196e5a303b2909a4fc3f55fc2cd3d760d43` |
| Round-62 independent attack | `audits/round_62_stageb_v2_independent_attack.md` | `b72472e721a12c6d19e007273d6dd347430643f737d0168c2022010891a531b1` |

No hidden or canonical positive-`B` scientific result was opened.  No mesh,
finite-volume solve, Stage-A candidate evaluation, or Monte Carlo trajectory
was run.  No producer, manifest, main entry point, result, auditor, or
manuscript is modified by this design.

## 1. Maximum claim and explicit nonclaims

After every future deterministic and off-lattice gate passes, the strongest
permitted wording is:

> a mesh-, alignment-, and box-stable finite-volume numerical allocation
> cusp, with predeclared finite-resolution event-law features at unchanged
> physical controls independently preserved by the unbounded off-lattice Doi
> process.

The off-lattice method validates only survival, event-basin masses, fixed
window probabilities needed for the analysis, and predeclared **positive local
peak--valley contrasts** at the unchanged anchor and one-/two-/three-mode phase
representatives.  It does not locate a cusp or fold, prove that either side of
a fold is unimodal, prove a global exact mode count, or estimate a fourth time
jet.

These flags remain false even after a complete pass:

```text
continuum_cusp_verified = false
PDE_cusp_verified = false
rigorous_FV_continuum_limit = false
global_exact_mode_count_verified = false
off_lattice_cusp_verified = false
off_lattice_fold_verified = false
off_lattice_fourth_jet_verified = false
off_lattice_unimodal_side_absence_verified = false
```

There is no v3 statement called “both fold-side topology changes.”  The four
off-fold controls remain deterministic held-out FV challenges; they are not
off-lattice scientific controls and do not create a cross-method fold claim.

## 2. Two disjoint object classes

The word `control` is reserved for an unchanged physical input.  A
grid-specific solution is an `implicit estimand`, never a control byte string.

### 2.1 Frozen physical controls

At `T1`, freeze eight mutually distinct physical controls:

| group | role IDs | count |
|---|---|---:|
| positive-`B` anchor | `anchor_m3` | 1 |
| phase representatives | `representative_m1`, `representative_m2`, `representative_m3` | 3 |
| audited saved-object off-fold controls | `offfold_negative_minus`, `offfold_negative_plus`, `offfold_positive_minus`, `offfold_positive_plus` | 4 |
| **total** |  | **8** |

For each role, `T1` serializes the exact binary64 hex strings of `theta`, the
three allocation weights, budget, support geometry, initial-law parameters,
time horizon, and every other physical input.  Those bytes are identical on
all eight FV configurations.  No Stage-B value may move, refit, renormalize,
or replace them.

Only

```text
C_MC = {anchor_m3, representative_m1,
        representative_m2, representative_m3}
```

is promoted to off-lattice production.  Its expected retained-maximum counts
are exactly `(3,1,2,3)` in that order.  Any audited upstream mismatch is
`HOLD-T1` rather than permission to change the statement universe.

### 2.2 Grid-specific implicit estimands

Seven roles are solved independently on every FV configuration:

| group | role IDs | count |
|---|---|---:|
| cusp | `cusp` | 1 |
| negative oriented fold | `fold_negative_025`, `fold_negative_050`, `fold_negative_075` | 3 |
| positive oriented fold | `fold_positive_025`, `fold_positive_050`, `fold_positive_075` | 3 |
| **total** |  | **7** |

For configuration `g`, write the outputs as `z_cusp,g` and `z_b,a,g`; these
are allowed and expected to differ by grid.  What is frozen at `T1` is the
equation, chart, seed object ID, branch orientation, target offset, solver,
trust region, matching rule, and failure semantics.  The solved output bytes
are not known at `T1` and must never be represented as unchanged controls.

## 3. One-way `T0--T3` freeze

### `T0`: this design

`T0` freezes:

1. the two object classes and role IDs;
2. the saved-object-only off-fold selection rule;
3. all eight FV configurations and the 120-row matrix;
4. the implicit equation, matching, `MR+F` envelope, and margin algorithms;
5. the fixed-control time-set, FV envelope, strip, and event-law transforms;
6. the exact interval, `E_MC`, tolerance, atomization, alpha, power, seed,
   pool, retry, and replicate rules; and
7. the no-cycle pin graphs and claim boundary.

Changing any item produces v4 and requires another result-blind attack before
science.

### `T1`: audited Stage-A substitution, with no new discovery solve

`T1` may read only a future canonical Stage-A result, its two-process evidence,
and its independent post-result audit, all of which must pass.  It may perform
JSON/schema checks and the deterministic transformations in Sections 4 and 6.
It is expressly forbidden to construct or evaluate a mesh-65 or mesh-97 model,
rerun a candidate, or inspect a Stage-B value.

`T1` freezes:

- the eight exact fixed controls and their one-to-many role map;
- the seven implicit-role seed IDs, disjoint matching balls, equations,
  thresholds, and exact solver parameters;
- the 120 logical rows and exact resource caps;
- the deterministic Stage-B protocol, producer, tests, manifest, result
  schema, and pre-frozen independent-audit chain; and
- the exact upstream hash closure.

Missing saved objects, duplicate fixed controls, ambiguous membership,
overlapping implicit match balls, an ineligible off-fold pair, or any need for
a new 65/97 evaluation is `HOLD-T1`.

### `T2`: audited FV substitution and MC freeze

Only after a canonical `GO-FV-STAGE-B` plus independent audit may `T2`
substitute the audited `MR+F` roots and common-time-set FV integrals into the
already frozen formulas.  It freezes exact basins, windows, `x_FV`, `E_FV`,
scientific margins, tolerances, alpha rows, planning alternatives, common `N`,
ID ranges, engine/code hashes, and the off-lattice producer/auditor chain.

It may not change a physical control, topology count, root role, statement
type, interval method, atomization, tolerance formula, alpha family, `Lambda`,
or sample cap.  A missing/nonpositive transformation or power infeasibility is
`HOLD-T2`; statements and controls cannot be dropped.

### `T3`: one production experiment

Run two disjoint scientific pools once after the complete `T2` hash exists.
Partial counts cannot influence a design decision.  An operational retry uses
only the identical failed ID range.  The exact-ID replicate repeats all IDs
and is reproducibility evidence, not a third sample and not extra alpha.

## 4. Saved-object-only off-fold selection

This section replaces v2's forbidden new 65/97 offset search.

### 4.1 Exact source membership

For each `candidate_index`, an eligible saved phase object must have exactly
one byte-consistent member in each canonical Stage-A collection:

```text
bounded_phase_discovery.candidate_generation
bounded_phase_discovery.screened_mesh_65
bounded_phase_discovery.advanced_mesh_97
```

The generated `theta` and `weights` must byte-match the corresponding fields
in both evaluated rows.  Both rows must say `EVALUATED`, pass every frozen
control gate, have the same retained-maximum count and ordered topology, and
be covered by the Stage-A independent audit.  A representative copy is not a
new candidate and cannot replace a missing collection member.

The branch geometry comes only from the canonical mesh-97 saved branch object
and its exact `nodes` and `comparison_nodes`.  No value is recomputed with a
scientific model at `T1`.

### 4.2 Frozen branch frame

For each oriented branch `b`:

1. choose the saved comparison node whose target signed time offset is exactly
   binary64 `0.75`; if the schema contains more than one, rank by absolute
   offset mismatch, normalized fold residual, then acceptance index;
2. locate that acceptance index in the saved ordered node array and require a
   predecessor and successor;
3. set the chart tangent to the normalized central secant

   \[
   u_b={\theta_{next}-\theta_{previous}\over
              \|\theta_{next}-\theta_{previous}\|_2},
   \]

   orienting it so increasing signed branch time has positive dot product;
4. set the normal exactly to the `+pi/2` chart rotation
   `n_b=(-u_b[1],u_b[0])`; and
5. set the local scale

   \[
   \ell_b=\min(\|\theta_b-\theta_{previous}\|_2,
                \|\theta_{next}-\theta_b\|_2).
   \]

Every norm and dot product uses the future pinned binary64 implementation in
the written operation order.  A nonfinite value, zero secant, nonpositive
`ell_b`, missing neighbor, or orientation tie is `HOLD-T1`.

### 4.3 Eligibility and deterministic pair rank

For a saved eligible candidate `i`, let

```text
d_i = theta_i - theta_b
s_i = dot(n_b,d_i)
q_i = dot(u_b,d_i)
r_i = norm_2(d_i)
```

It belongs to the local candidate set only if

```text
0 < r_i <= 2*ell_b
abs(q_i) <= ell_b/2
ell_b/16 <= abs(s_i)
```

Enumerate every pair `(i_minus,i_plus)` with `s_minus<0<s_plus`, different
candidate indices, and retained-maximum counts differing by exactly one.  Rank
pairs lexicographically by

```text
max(r_minus,r_plus)/ell_b,
abs(s_minus+s_plus)/ell_b,
(abs(q_minus)+abs(q_plus))/ell_b,
min(candidate_index_minus,candidate_index_plus),
max(candidate_index_minus,candidate_index_plus).
```

Choose the unique first pair.  Attach its already audited mesh-65/97 topology
labels; do not calculate a new label.  Repeat for the other branch.  If no
pair exists, a rank field is nonfinite, the two branches reuse any candidate,
or two distinct objects share a candidate index/byte string, return
`HOLD-T1`.  Do not choose the next pair after a cross-branch collision.

After both pairs are selected, their two unordered retained-maximum-count
pairs must be exactly `{(1,2),(2,3)}`.  Otherwise `HOLD-T1`; the branch labels
are not reassigned to make this true.

The four selected `theta` and `weights` bytes are copied verbatim.  There is no
normal offset, interpolation, optimization, renormalization, or refit.  Their
Stage-B topology checks are deterministic FV checks only and are absent from
the off-lattice statement set.

## 5. Eight FV configurations and corrected workload

The physical boxes and grids remain exactly:

| label | midpoint box/cells | relative-parallel box/cells | transverse cells | states |
|---|---|---|---:|---:|
| `O113/Base` | `[-0.25,1.85] / 113` | `[-1.8,1.8] / 113` | 113 | `1,442,897` |
| `E128/Base` | `[-0.25,1.85] / 128` | `[-1.8,1.8] / 128` | 128 | `2,097,152` |
| `O129/Base` | `[-0.25,1.85] / 129` | `[-1.8,1.8] / 129` | 129 | `2,146,689` |
| `O161/Base` | `[-0.25,1.85] / 161` | `[-1.8,1.8] / 161` | 161 | `4,173,281` |
| `M+` | `[-0.55,2.15] / 166` | `[-1.8,1.8] / 129` | 129 | `2,762,406` |
| `R+` | `[-0.25,1.85] / 129` | `[-2.4,2.4] / 172` | 129 | `2,862,252` |
| `MR+` | `[-0.55,2.15] / 166` | `[-2.4,2.4] / 172` | 129 | `3,683,208` |
| `MR+F` | `[-0.55,2.15] / 207` | `[-2.4,2.4] / 215` | 161 | `7,165,305` |

Every one of the eight fixed controls is evaluated unchanged on all eight
configurations.  Every one of the seven implicit roles is independently
solved on all eight, including `MR+F`; this is needed for the cusp/fold
reference-centred envelopes in Section 6.  Therefore:

```text
logical roles                              = 8 fixed + 7 implicit = 15
logical role--configuration rows           = 15*8 = 120
sum of first-seven state counts             = 19,167,885
sum including MR+F                          = 26,333,190
no-duplicate base-state cells / row pass    = 15*26,333,190
                                             = 394,997,850
two nominal deterministic executions        = 789,995,700
```

The earlier `114` and `352,006,020` counts are not v3 counts.  V3 adds six
`MR+F` fold solves; it does not remove the four `MR+F` off-fold FV checks merely
because those controls no longer enter Monte Carlo.

`394,997,850` is labelled only **base-state cells per one complete row pass**.
It is not a FLOP count, Krylov-action count, augmented-vector count, memory
bound, or wall-time estimate.  The seven implicit rows are execution
obligations even if two output vectors accidentally coincide.  The eight
fixed controls must be mutually byte-distinct at `T1`; otherwise `HOLD-T1`.

Every missing row is serialized as a fixed-schema structural HOLD.  No row is
dropped after a resource or solver failure.

## 6. Grid-specific cusp/fold equations, matching, and envelopes

### 6.1 Fixed equations and single-seed correction

Let `f_g(t;theta)` be the killed-FV event density on configuration `g` under
the unchanged physical model.  In the frozen two-coordinate Helmert chart,
the cusp solve is

\[
 F^C_g(t,\theta)=
 (\partial_t f_g,\partial_t^2 f_g,\partial_t^3 f_g)=0.
\]

For branch sign `sigma in {-1,+1}` and
`a in {0.25,0.50,0.75}`, the matched fold solve is

\[
 F^F_{g,\sigma,a}(t,\theta)=
 (\partial_t f_g,\partial_t^2 f_g,
  t-t_{C,g}-\sigma a)=0.
\]

Thus correspondence is defined by a saved branch ID and an exact signed time
offset, not by choosing the nearest favorable Stage-B node.

The cusp starts only from the saved audited Stage-A cusp.  Each fold role
starts only from its saved audited Stage-A comparison-node `theta`, with time
replaced by `t_C,g+sigma*a`.  The future `T1` manifest must copy, by exact
upstream key, the derivative convention, scaling, Newton tolerance, maximum
iteration count, line-search sequence, Krylov tolerance/action cap, and
nonfinite/factorization failure rules used by the audited Stage-A equation.
There is no second seed, random restart, cross-grid warm start, or changed
equation.  Failure is a finite structural HOLD.

### 6.2 Disjoint role matching

Use the dimensionless matching norm

\[
 d(z,z')=\max(|t-t'|/34.5,|\theta_1-\theta'_1|,
                         |\theta_2-\theta'_2|).
\]

At `T1`, the cusp match radius is the exact upstream cusp trust radius in this
norm.  For each fold seed, set its radius to the smaller of its exact upstream
trust radius and one quarter of its distance to every other saved fold seed.
All radii must be finite and positive, and the seven closed seed balls must be
pairwise disjoint.  These radii are frozen before Stage B.

For every grid, require:

- the corrected result lies strictly inside its role ball after the prescribed
  cusp-relative time shift;
- the cusp and fold residuals meet the unchanged upstream caps;
- `t_fold-t_cusp` has the exact role sign and target offset within the frozen
  equation residual cap;
- the three roles on each branch preserve `0.25<0.50<0.75` order;
- branch orientation agrees with the saved Stage-A orientation; and
- no solved point enters another role ball or shares an output identity.

A missing, multiply matched, branch-swapped, crossed, or boundary-tied solution
is HOLD.  The auditor reconstructs every match from saved IDs and raw outputs.

### 6.3 `MR+F`-centred implicit envelopes

Algorithmic uncertainty is converted before any cross-grid comparison.  For
each implicit row, use the scaled equation Jacobian `J`, residual `F`, an
outward interval upper bound `L` on the Jacobian Lipschitz constant throughout
the frozen role ball, and

```text
eta = up64(norm_inf(solve(J,F)))
K   = up64(norm_inf(inv(J)))
h   = up64(K*L*eta).
```

The inverse norm is obtained by a residual-checked linear solve, not a bare
condition-number print.  Require `h<=1/2`.  The coordinate error certificate is
the outward Newton--Kantorovich radius

\[
 r_{alg,z}=up64\left({1-\sqrt{1-2h}\over K L}\right)
\]

with the `L=0` limit `r_alg,z=eta`.  For a scalar diagnostic `q`, use an
outward interval gradient bound `G_q` on the same ball and an independently
bounded direct evaluation error `r_eval,q`:

\[
 r_{alg,q}=up64(G_q r_{alg,z}+r_{eval,q}).
\]

The interval box, derivative implementation, directed rounding, and every
`r_eval` conversion are pinned at `T1`.  Failure to establish the Lipschitz,
inverse, or direct-evaluation bound is HOLD; a raw nonlinear residual is not
silently treated as an output error.

For every implicit role `r`, configuration `g`, and reported scalar field
`q` in the frozen output schema, set

\[
 x^{r,q}_{FV}=q_{r,MR+F},
\qquad
 E^{r,q}_{FV}=\max\left(
       \max_g|q_{r,g}-q_{r,MR+F}|,
       \max_g r^{r,q}_{alg,g}\right),
\]

where `r_alg` is a pre-frozen residual-to-output bound in the same units.
The mandatory fields are `(t,theta_1,theta_2,w_1,w_2,w_3)`, the equation
residuals, the signed fourth time jet at the cusp, fold curvature/nondegeneracy
diagnostics, the two allocation-response singular values, and every
rank/determinant diagnostic used by the numerical-cusp claim.  Missing
residual conversion is HOLD; zero is not assumed.

For the coordinate vector, also report

\[
 E^{r,z}_{FV}=\max_g d(z_{r,g},z_{r,MR+F})
\]

augmented by the normalized algebraic coordinate bound.  Require

```text
E_FV(r,z) <= frozen_match_radius(r)/4.
```

For every unchanged lower scientific gate `q>=q0`, define

```text
d_q = min_g(q_r,g) - q0
```

and for every unchanged upper gate `q<=q0`, define

```text
d_q = q0 - max_g(q_r,g).
```

For an absolute nondegeneracy gate, first orient the sign from the saved
Stage-A role, then use the corresponding signed lower gate.  Require

```text
d_q > 0
E_FV(r,q) <= d_q/4
```

in addition to every per-grid gate.  For residual gates `abs(r)<=r0`, require
the outward-rounded residual plus its conversion bound to be at most `r0` on
every grid.  No threshold or sign can be chosen from Stage-B outputs.

The local odd/even, refinement, separate-box, combined-box, and
`MR+--MR+F` differences remain diagnostics, but the scientific uncertainty is
the complete `MR+F`-centred envelope above.

## 7. Fixed-control FV estimands and boundary strips

### 7.1 Common measurable time sets

For each `c in C_MC`, use only its audited `MR+F` ordered stationary-root tuple
to construct the basins and windows in Section 8.  Every grid integrates its
own event density over those **same physical time sets**.  Grid-specific
windows are diagnostics only.  A missing root identity, topology mismatch, or
unavailable integral is HOLD.

For each scalar probability, survival value, or local contrast `q`, set

\[
 x_{FV}=q_{MR+F},\qquad
 E_{FV}=\max\left\{\max_g|q_g-q_{MR+F}|,
                         \max_g r_{alg,g}(q)\right\}.
\]

All eight configurations enter every promoted fixed-control envelope.  For a
survival curve, calculate the expression at all 401 fixed times and report the
supremum.  Coordinatewise values and the max norm are both serialized for a
vector.  The unchanged quarter-margin rule applies to every deterministic
floor/cap.

The four off-fold fixed controls use the same eight-grid pointwise envelope
for their deterministic topology and physical-law diagnostics, but they have
no `T2` windows, no MC tolerance, and no off-lattice statement.

### 7.2 Physical partial-cell strips

Retain the four physical strips of widths `0.10` in midpoint and `0.20` in
relative-parallel coordinates.  If cell `C_i` stores killed mass `p_i`, use

\[
 M_S(t)=\sum_i p_i(t){|C_i\cap S|\over|C_i|}.
\]

For tensor overlap fractions `omega_M` and `omega_R`, the union weight is

\[
 \omega_{union}=\omega_M+\omega_R-\omega_M\omega_R.
\]

Require finite weights in `[0,1]`, direct/inclusion--exclusion agreement within
`1e-14` on non-scientific fixtures, and

```text
max union strip mass over all 120 rows and all required saved times <= 1e-6.
```

Required times are `{k/4:k=0,...,400}`, all saved stationary roots and
basin/window endpoints, and `T=100`, deduplicated only by exact binary64 time
identity.  The unbounded free-OU strip probability is a diagnostic only and is
never an upper bound on reflected killed-FV strip mass.

## 8. Exact off-lattice estimands; no fold-topology claim

### 8.1 Basins and windows

For each `c in C_MC`, `T1` freezes `m=(3,1,2,3)` and the alternating
`MR+F` role skeleton.  At `T2`, substitute the audited roots

```text
z_1 < ... < z_(2m-1)
```

without reselecting them.  The `m-1` valleys are basin cuts, producing

```text
[0,v1), [v1,v2), ..., [v_(m-1),100].
```

For `m>1`, define

\[
 h_c=\min\left(0.4,{1\over4}\min_j(z_{j+1}-z_j),
                 {z_1\over2},{100-z_{2m-1}\over2}\right).
\]

For `m=1`, define explicitly

\[
 h_c=\min(0.4,z_1/2,(100-z_1)/2).
\]

Require finite `h_c>0`.  Windows are `[z_j-h_c,z_j+h_c)`.  Event time at an
internal cut goes right; time exactly `100` belongs to the final basin;
survival is `T>100`.  Windows are left-closed/right-open.

The primitive counts per control are:

| expected `m` | basins | windows | positive local contrasts |
|---:|---:|---:|---:|
| 1 | 1 | 1 | 0 |
| 2 | 2 | 3 | 2 |
| 3 | 3 | 5 | 4 |

Across `(anchor_m3,representative_m1,representative_m2,representative_m3)`
this gives 9 basins, 14 windows, and 10 positive contrast statements.

The `m=1` control has no valley and therefore **no contrast object at all**.
There is no dummy zero, contract-zero contrast, absence test, or zero-alpha
placeholder.

### 8.2 Scientific statements

For every control and pooled/pool-1/pool-2 view require:

- one simultaneous survival band on `{k/4:k=0,...,400}` and FV agreement;
- every basin mass to exceed `0.005`, agree with FV, and close with `S(100)`;
- each window probability to agree with FV; and
- for `m>=2`, each chronological adjacent maximum-minus-valley average-density
  contrast to have a positive lower confidence endpoint and agree with FV.

Because all windows for a control have width `2h_c`, a contrast is exactly

\[
 D=(p_{maximum}-p_{valley})/(2h_c).
\]

These are positive local finite-resolution features.  They do not assert that
the one-mode representative has no unobserved local pair or that any control
has a global exact number of modes.

## 9. Exact tolerances, intervals, and `E_MC`

### 9.1 Directed binary64 convention

`down64(x)` is the greatest finite binary64 value no larger than nonnegative
real `x`; `up64(x)` is the least finite binary64 value no smaller than `x`.
Transcendentals are evaluated with at least 256-bit MPFR precision and directed
rounding before binary64 conversion.  Package, ABI, and implementation hashes
are frozen at `T2`.  A disagreement with an independently recomputed directed
value is HOLD.

### 9.2 Deterministic tolerance equalities

For a basin mass, let

```text
d_M = x_FV - E_FV - 0.005
tau_M = down64(min(0.001,d_M/4)).
```

For a local contrast, let

```text
d_D = x_FV - E_FV
tau_D = down64(d_D/4).
```

For each control with contrasts, let

```text
gamma = min over adjacent peak/valley pairs
        (p_peak,FV - E_peak,FV - p_valley,FV - E_valley,FV)
tau_p = down64(min(0.002,gamma/16)).
```

For the `m=1` control, which has no adjacent pair, set the window agreement
tolerance exactly to `tau_p=0x1.0624dd2f1a9fcp-10` (the binary64 encoding of
decimal `0.001`).  Survival uses

```text
tau_S = 0x1.47ae147ae147bp-7
```

(the binary64 encoding of decimal `0.01`).  All derived tolerances must be
finite and positive.  The deterministic margin gates additionally require the
Section-6/7 reference-centred envelope to consume no more than one quarter of
its separately defined scientific margin.  A nonpositive margin is `HOLD-T2`,
never a reason to widen a tolerance.

### 9.3 Frozen confidence construction

For a binomial count `k` from `n` valid IDs and one-sided rational alpha
`alpha_tail`, use the outward Hoeffding interval

\[
 r_H=up64\sqrt{{\log(1/\alpha_{tail})\over2n}},\quad
 [L,U]=[\max(0,k/n-r_H),\min(1,k/n+r_H)],
\]

with the division and endpoints outward rounded.  A two-sided probability row
uses its separately enumerated lower and upper tail atoms.

For a survival empirical function and one two-sided band atom `alpha_band`, use

\[
 r_{DKW}=up64\sqrt{{\log(2/\alpha_{band})\over2n}}
\]

uniformly over all 401 times, clipped to `[0,1]` only after outward rounding.

For a scalar probability, define

```text
E_MC = max(k/n-L,U-k/n).
```

For a contrast, its interval is

\[
 [(L_{peak}-U_{valley})/(2h),
  (U_{peak}-L_{valley})/(2h)]
\]

with outward rounding, and `E_MC` is the larger distance from the point
estimate to either endpoint.  There is no separate inferred contrast for
`m=1`.

Every MC--FV agreement gate is interval containment:

\[
 [L_q,U_q]\subseteq
 [x_{FV}-E_{FV}-\tau_q,,x_{FV}+E_{FV}+\tau_q].
\]

Positive contrasts also require `L_D>0`; basin masses require `L_M>0.005`.
Realized precision requires `E_MC<=tau_q`.  Survival uses the pointwise DKW
band and `tau_S`.  Pool-consistency intervals are constructed from the
separate consistency-family radii in Section 10 and must contain zero; their
realized half-width must not exceed the sum of the two applicable `tau` values.

## 10. One exact global-alpha atom ledger

Freeze `alpha_FWER=1/20=0.05`.  Controls are ordered by control hash and role
ID; views are `pool_1,pool_2,pooled`; within a control, basins, windows, and
contrasts are chronological.  Derived statements consume no extra alpha
because they are implications of the enumerated simultaneous primitive
intervals.

The exact universe is:

| family | primitive atoms/tails | count | alpha each | family total |
|---|---|---:|---:|---:|
| survival | 4 controls * 3 views, one two-sided DKW band atom | 12 | `1/1200` | `1/100` |
| basin/tail | (9 basin + 4 `S(100)`) * 3 views * 2 Hoeffding tails | 78 | `1/5200` | `3/200` |
| windows/contrasts | 14 windows * 3 views * 2 Hoeffding tails | 84 | `1/5600` | `3/200` |
| pool consistency | 8 pool-specific DKW band atoms plus (13 basin/tail + 14 window) * 2 pools * 2 tails | 116 | `1/11600` | `1/100` |
| **total** |  | **290** |  | **`1/20`** |

The contrast statements are derived from the 14 window intervals; their ten
positive lower endpoints and FV agreements are mandatory.  The `m=1` window
is counted once, but no nonexistent contrast is inserted.  Basin closure and
integer-ledger closure are deterministic identities and consume no alpha.

The ledger is generated in exact rational arithmetic and then independently
recomputed.  Any missing/extra atom, changed `m`, duplicate primitive,
misordered row, or total other than `1/20` is `HOLD-T2`.

## 11. Exact atomization and joint power at least 0.90

### 11.1 Planning alternative and primitive atoms

The planning alternative at `T2` is exactly the audited `MR+F` probability
vector and survival curve on the common time sets; no pilot or MC count enters
it.  This is a conditional design-power statement, not an assertion that the
off-lattice truth equals FV.

Only pool-level random primitives are needed; pooled quantities are exact sums
of the two pools.  For each pool the canonical atom list contains:

```text
4 controlwise survival empirical-process atoms
9 basin-count atoms
4 S(100)-count atoms
14 window-count atoms
```

There are exactly `2*(4+9+4+14)=62` power atoms.  Contrasts, pooled views,
basin closure, and pool consistency are deterministic functions of these
atoms.  There is no atom for a nonexistent `m=1` contrast.

### 11.2 Frozen gate-to-atom transformation

For candidate total `N`, each pool has `n=N/2`.  Substitute the exact
confidence radii from Section 9 into every mandatory gate and express that
gate as one or two affine inequalities in the primitive probabilities or a
uniform survival inequality.  Evaluate its exact positive planning slack.

For each affine inequality with coefficients `a_j`, confidence-radius
consumption `c`, and remaining slack `s=planning_margin-c`, require `s>0` and
assign every participating primitive the sufficient empirical-deviation cap

\[
 \delta_{gate}=down64\left({s\over2\sum_j|a_j|}\right).
\]

For survival, use the analogous remaining uniform slack divided by two.
For each canonical primitive atom, take the minimum positive `delta_gate` over
all poolwise, pooled, scientific, agreement, precision, and consistency gates
that consume it.  Interval arithmetic must verify mechanically that the
Cartesian product of these 62 atom events implies **every** mandatory GO gate.
There is no alternative “exact joint method,” discretionary slack split, or
fallback atomization.

### 11.3 Failure bound and sample-size choice

For a bin probability `p_star`, define integer bounds

```text
k_low  = ceil(n*(p_star-delta))
k_high = floor(n*(p_star+delta))
```

with directed arithmetic and clipping to `[0,n]`.  Its atom failure
probability is the exact binomial probability outside `[k_low,k_high]`,
computed with a pinned implementation and outward-rounded CDF/SF.  A survival
atom uses the outward DKW bound

\[
 \min(1,2\exp(-2n\delta^2)).
\]

Sum all 62 outward upper bounds without an independence assumption:

\[
 \beta_{all}(N)=up64\sum_{a=1}^{62}\beta_a(N).
\]

Enumerate

```text
N = 200,000, 400,000, ..., 50,000,000
```

and choose the first even `N` for which every cap is positive, the implication
audit passes, and

```text
1 - beta_all(N) >= 0.90.
```

Serialize all 62 caps, integer bounds, tail probabilities, the implication
matrix, sum order, and an independent recomputation.  If no candidate passes,
the outcome is `HOLD-T2`.  No top-up, larger cap, dropped control, or altered
window is allowed.

## 12. Universal rate, exact IDs, seeds, retries, and replicate

### 12.1 Physical input and thinning rate

Before an ID is consumed, validate three finite nonnegative weights and

```text
abs(fsum(weights)-1) <= 2^-48.
```

Serialize both `theta.float.hex()` and every `weight.float.hex()`; the pinned
Stage-A chart reconstruction must reproduce the saved weight bytes exactly.
With the finite-sum tolerance,

\[
 {0.01(1+2^{-48})\over0.04}e^{1/3}
 =0.3489031062715236\ldots < \boxed{0.35}.
\]

Every hazard must be finite, nonnegative, and no larger than `0.35`.  Clipping
is forbidden; any violation aborts the whole run.

### 12.2 Counter-based seed and ID namespace

Freeze the ASCII domain separator

```text
positive-b-stage-b-v3-off-lattice-sha256-counter-v1
```

and master material

```text
positive-b-stage-b-v3-fixed-master-seed-v1
```

For control hash `H_c`, pool byte `p in {0x01,0x02}`, local trajectory ID `i`
as unsigned big-endian 64-bit, and block counter `j` as unsigned big-endian
64-bit, the random block is

```text
SHA256(domain || 0x00 || SHA256(master_material) || 0x00 ||
       T2_hash_bytes || H_c_bytes || p || u64be(i) || u64be(j)).
```

The future pinned producer freezes byte-to-uniform conversion, Gaussian
conversion, OU bridge arithmetic, and consumption order.  Test IDs use a
different literal domain and cannot overlap science.

Each pool uses local IDs `0,...,N/2-1`; pool byte and control hash make the
global namespace disjoint.  Chunk size is exactly `100,000` local IDs.  A
retry repeats the identical `(control,pool,ID range,T2 hash)` and may occur
only after an operationally incomplete chunk, before its counts are admitted.
New IDs and optional top-up are forbidden.

The exact-ID replicate reruns both pools with the same blocks and must reproduce
the raw event-time ledger and canonical summaries byte for byte.  It contributes
no sample, alpha, or power.

## 13. Acyclic provenance and resource contract

### 13.1 Required one-way hash graph

For deterministic Stage B:

```text
audited Stage-A result/evidence/audit
        -> canonical T1 substitution object and audit
        -> Stage-B scientific manifest M_B
        -> Stage-B canonical result/evidence
M_B hash -> hard-coded by independent auditor A_B
(M_B hash, A_B hash, A_B-test hash)
        -> separate Stage-B no-cycle audit protocol P_B
```

`M_B` pins this v3 design, the T1 object/audit, scientific protocol, producer,
tests, and dependencies.  It does **not** pin `A_B`, its tests, or `P_B`.
`A_B` hard-codes `M_B` and imports no producer.  `P_B` is frozen and attacked
before the scientific result exists and is not pinned back by `M_B`.

For off-lattice production:

```text
audited Stage-B result/evidence/audit
        -> canonical T2 numerics object and audit
        -> MC scientific manifest M_MC
        -> MC canonical result/evidence
M_MC hash -> hard-coded by independent auditor A_MC
(M_MC hash, A_MC hash, A_MC-test hash)
        -> separate MC no-cycle audit protocol P_MC
```

The same no-back-edge rule applies.  A manifest/auditor/protocol cycle or an
unfrozen auditor is `HOLD-EXECUTION`.

### 13.2 Resource limits

Before execution, `M_B` must freeze maximum augmented vectors per row,
Newton/fold iterations, root evaluations, Krylov actions, resident bytes,
scratch bytes, per-row wall time, and full-run wall time.  These caps are
derived only from implementation structure and non-scientific fixtures, then
independently attacked.  A cap hit is an operational HOLD with complete
fixed-schema null rows; it never permits a smaller matrix.

Both scientific chains require lexical `lstat`/`O_NOFOLLOW` pin checks, exact
start/end byte snapshots, no-concurrent-writer windows, canonical result and
evidence bytes, two independent deterministic executions or two scientific
pools as applicable, failure-atomic promotion, rollback, and post-promotion
rehashing.

## 14. GO/HOLD semantics

### `GO-FV-STAGE-B`

Requires two byte-identical complete executions and an independent audit
establishing:

1. all 120 logical rows and all fixed-schema objects are present;
2. fixed controls have unchanged bytes, while all seven implicit roles were
   re-solved and uniquely matched on every grid;
3. all physical-law, strip, root, topology, cusp/fold residual,
   nondegeneracy/rank, resource, and margin gates pass;
4. every cusp/fold coordinate and diagnostic has the complete `MR+F`-centred
   envelope and quarter-margin gate; and
5. every `C_MC` common-time-set fixed-control envelope passes.

This supports only a mesh/alignment/box-stable **finite-volume numerical
cusp** and its matched numerical fold structure.  It is not a continuum/PDE
theorem.

### `GO-OFF-LATTICE`

Requires the two frozen pools, pooled analysis, exact-ID replicate, and
independent audit to pass all 290-alpha-atom inference contracts, all 62-atom
power implications, survival, basin, window, positive local contrast,
FV-agreement, precision, pool-consistency, closure, rate, ID, and byte gates.

It sets only

```text
independent_unbounded_unchanged_control_event_law_validated = true
```

and none of the cusp/fold/global-mode flags in Section 1.

### Global HOLD

Any upstream audit failure; unavailable saved object; forbidden 65/97
evaluation at `T1`; ambiguous membership; changed fixed bytes; implicit-match
failure; missing row/atom/ID; nonfinite value; failed margin; infeasible power;
alpha mismatch; resource/rate violation; adaptive count use; top-up;
nonidentical replicate; hash drift; or post-result audit failure is a global
HOLD.

## 15. Current design decision

This document closes the Round-62 design findings without inspecting science:

```text
open design P0 = 0
open design P1 = 0
open design P2 = 0

design status    = GO-DESIGN
execution status = HOLD-EXECUTION
science status   = NOT RUN / NOT INSPECTED
```

Execution remains held until a future audited Stage-A canonical object exists,
`T1` succeeds without new discovery evaluation, both implementation/no-cycle
chains are built and independently attacked, deterministic Stage B passes,
`T2` freezes feasible exact MC numerics, and the off-lattice chain passes.
