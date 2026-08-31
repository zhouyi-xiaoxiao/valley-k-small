# Positive-`B` Stage-B validation design v4

Date: 2026-07-14  
Status: **GO-DESIGN / HOLD-EXECUTION**  
Authorization: **AUTHORIZED-SCIENTIFIC-COMMAND: NONE**

## 0. Purpose, attacked snapshot, and non-execution boundary

This is a new design version.  It does not overwrite v3 and is not a
scientific result.  It repairs every open finding in the independent Round-67
attack while preserving the result-blind scope and the valid v3 role,
configuration, statistical-cardinality, rate, and claim decisions.

The design inputs are:

| role | repository path | SHA-256 |
|---|---|---|
| attacked Stage-B v3 design | `notes/positive_b_stage_b_validation_design_v3.md` | `0c7119870e173bfbe5042b3f1c19c7c5851061940cab66e7e0dab98f54becd58` |
| Round-65 v3 resolution | `audits/round_65_stageb_v3_design_repair.md` | `fcbb84e25073f00b5f76075cfacaf0c13a7cb788b8124020eff481a773c40bfb` |
| independent Round-67 attack | `audits/round_67_stageb_v3_independent_attack.md` | `4f71f9e517ce5d3ca44e403332fb52be37d070e7e546db284cbbed83bf4d6c35` |
| Round-67 science-free checks | `code/test_stageb_v3_design_round67.py` | `fc17fbbd5e648a6b8629fb07d6030931c3dcaa820466851f6a88e84b28317342` |
| allocation-cusp promotion design | `notes/positive_b_allocation_cusp_promotion_design.md` | `ad072e83004ea3e3b5c3d01a58a872b5aedca74d13400fa04d6f917d4a06d1f5` |

No hidden/canonical scientific value was opened.  No Stage-A candidate,
mesh-65/97 model, Stage-B FV row, cusp/fold solve, off-lattice trajectory,
scientific producer, or scientific auditor was run.  This document changes no
producer, manifest, main entry point, result, auditor, v3 file, or manuscript.

## 1. Maximum claim and nonclaims

An eventual complete pass supports at most:

> a mesh-, alignment-, and box-stable finite-volume numerical allocation
> cusp, with predeclared finite-resolution event-law features at unchanged
> physical controls independently preserved by the unbounded off-lattice Doi
> process.

The off-lattice method validates survival, event-basin masses, fixed window
probabilities used by the analysis, and predeclared positive local peak--valley
contrasts only at the unchanged anchor and one-/two-/three-mode phase
representatives.  It does not locate a cusp/fold, prove absence of a local pair
on the one-mode representative, or prove a global exact mode count.

These flags remain false:

```text
continuum_cusp_verified = false
PDE_cusp_verified = false
rigorous_FV_continuum_limit = false
global_exact_mode_count_verified = false
off_lattice_cusp_verified = false
off_lattice_fold_verified = false
off_lattice_fourth_jet_verified = false
off_lattice_unimodal_side_absence_verified = false
pool_statistical_equivalence_verified = false
```

The two-pool check is a powered same-generator regression diagnostic.  It is
not described as a statistical equivalence test.

## 2. Object classes and logical roles

### 2.1 Eight unchanged physical controls

At `T1`, freeze eight mutually byte-distinct controls:

```text
anchor_m3
representative_m1
representative_m2
representative_m3
offfold_negative_minus
offfold_negative_plus
offfold_positive_minus
offfold_positive_plus
```

Their binary64 `theta`, three weights, budget, support geometry, initial law,
horizon, and every physical parameter are unchanged on all FV grids.  Only

```text
C_MC = {anchor_m3, representative_m1,
        representative_m2, representative_m3}
```

enters off-lattice production, with frozen expected maximum counts `(3,1,2,3)`.
The four off-fold controls are deterministic FV challenges only.

### 2.2 Seven grid-specific implicit estimands

Each FV configuration independently solves:

```text
cusp
fold_negative_025  fold_negative_050  fold_negative_075
fold_positive_025  fold_positive_050  fold_positive_075
```

The equation, role ID, saved seed ID, target signed offset, chart, operation
order, certificate, and failure semantics are frozen.  The solved
`(t,theta,w)` values are grid-specific outputs and are never represented as
unchanged physical-control bytes.

## 3. Corrected one-way freeze ladder

### `T0`: design plus selector freeze before Stage-A values

This document freezes every mathematical transform, interval rule, radius
formula, selector operation, matrix row, statistical statement, and pin-graph
direction.  Before any canonical Stage-A result is opened, a future
science-free selector package

```text
code/positive_b_stage_b_t1_selector_v4.py
code/test_positive_b_stage_b_t1_selector_v4.py
notes/positive_b_stage_b_t1_selector_protocol_v4.md
```

must be hashed, independently attacked, and recorded by an external T0
protocol.  Its code implements Section 4 exactly.  A selector implementation
cannot be chosen after seeing Stage-A objects.

### `T1`: audited Stage-A substitution, then scientific-manifest freeze

`T1` may read only a canonical independently audited Stage-A result/evidence/
audit.  It runs the already frozen science-free selector; it may not construct
or evaluate mesh 65/97.  It writes a canonical T1 substitution object and
audit, freezes the Stage-B scientific protocol/producer/tests/dependencies,
the science-free T2 compiler/protocol/tests that will later apply Sections
10--12, and then freezes scientific manifest `M_B`.  Thus the T2
implementation is also fixed before a Stage-B value exists.

Only **after** `M_B` has an immutable hash is independent auditor `A_B` frozen
with that hash, followed by the external no-cycle protocol containing
`(M_B,A_B,A_B-tests)` hashes and a result-blind pre-run attack.  `M_B` never
pins `A_B` or that external protocol.

### `T2`: audited Stage-B substitution, then MC-manifest freeze

After canonical `GO-FV-STAGE-B` and its independent audit, the already frozen
T2 compiler substitutes interval-certified FV roots/estimands into Sections
10--12.  It writes a canonical T2 numerics object and audit, then freezes MC
scientific manifest `M_MC`.

Only after the `M_MC` hash exists is independent auditor `A_MC` frozen with
that hash, followed by its external no-cycle protocol and pre-run attack.
`M_MC` does not pin `A_MC` or that protocol.

### `T3`: one production experiment

Two disjoint pools run once.  Partial counts cannot change design.  An
operational retry repeats only the identical failed ID range.  The exact-ID
replicate repeats every ID and contributes no sample, alpha, or power.

## 4. T0-exact saved-object selector and role radii

### 4.1 Floating implementation contract

The T0 selector uses IEEE-754 binary64 round-to-nearest/ties-to-even, preserves
subnormals, forbids flush-to-zero/denormals-are-zero, sets `FP_CONTRACT=OFF`,
forbids FMA and extended intermediates, and rounds after every operation.
Nonfinite input is HOLD.

For two-vectors, operations are exactly:

```text
dot2(a,b) = rn(rn(a[0]*b[0]) + rn(a[1]*b[1]))
norm2(a)  = correctly_rounded_sqrt(
              rn(rn(a[0]*a[0]) + rn(a[1]*a[1])))
```

Subtraction, division, `abs`, `min`, and `max` follow the displayed left-to-
right order.  Negative zero is canonicalized to positive zero before ranking.
Finite rank fields use IEEE `totalOrder`; candidate indices are unsigned
integers and the final tie-break.  Byte serialization uses `float.hex()` and
canonical JSON.  The T0 tests include FMA-sensitive, one-ulp, signed-zero,
equal-rank, nonfinite, and collection-duplicate fixtures.

### 4.2 Exact cross-collection identity domain

For candidate index `i`, require exactly one object in each of:

```text
candidate_generation
screened_mesh_65
advanced_mesh_97
```

The three objects are an intentional **cross-collection join** and must share
the same candidate index and exact `theta/weights` bytes.  This is not a
duplicate error.

HOLD occurs if a collection contains the index more than once, two different
candidate indices in any collection share the same full physical-control
bytes, joined bytes disagree, or a selected index is reused by the other
branch.  Thus uniqueness is per collection and across distinct logical
candidates, not across the three intentional copies of one candidate.

Both mesh rows must be saved as `EVALUATED`, pass every frozen control gate,
and have identical retained topology.  Missing saved coverage is HOLD; no new
65/97 evaluation is allowed.

### 4.3 Branch frame and off-fold pair

For each oriented mesh-97 saved branch:

1. take the comparison object with target offset exactly binary64 `0.75`;
   duplicates rank by offset mismatch, fold residual, acceptance index;
2. require its saved predecessor and successor;
3. compute the central chart secant, normalize by `norm2`, and orient it toward
   increasing signed branch time;
4. set `normal=(-tangent[1],tangent[0])`; and
5. set `ell` to the smaller chart distance to predecessor/successor.

For saved candidate displacement `d`, compute in the Section-4.1 order:

```text
s = dot2(normal,d)
q = dot2(tangent,d)
r = norm2(d)
```

Eligibility is

```text
0 < r <= 2*ell
abs(q) <= ell/2
abs(s) >= ell/16.
```

Enumerate opposite-sign pairs with distinct indices and retained-maximum counts
differing by one.  Rank lexicographically by

```text
max(r_minus,r_plus)/ell,
abs(s_minus+s_plus)/ell,
(abs(q_minus)+abs(q_plus))/ell,
min(index_minus,index_plus),
max(index_minus,index_plus).
```

Choose the unique first pair on each branch.  The two unordered count pairs
must be exactly `{(1,2),(2,3)}` and share no selected index.  Otherwise HOLD;
do not choose a later pair.  Copy exact saved bytes without interpolation,
offset, optimization, renormalization, or refit.

### 4.4 Seven role radii from saved fields only

No role-specific upstream trust radius is assumed.  Let the seven saved seeds
be the canonical cusp and six canonical comparison-node vectors
`z_i=(t_i,theta_i1,theta_i2)`.  Use the globally saved Stage-A box

```text
9 <= t <= 18
abs(theta_1) <= 0.15
abs(theta_2) <= 0.15
```

and metric

\[
 d(z,z')=\max(|t-t'|/34.5,|\theta_1-\theta'_1|,
                         |\theta_2-\theta'_2|).
\]

In ascending role-ID order, compute with the Section-4.1 implementation:

\[
 b_i=\min((t_i-9)/34.5,(18-t_i)/34.5,
          0.15-|\theta_{i1}|,0.15-|\theta_{i2}|),
\]

\[
 s_i=\min_{j\ne i}d(z_i,z_j),\qquad
 \rho_i=down64(\min(1/128,b_i/4,s_i/4)).
\]

All terms must be finite and strictly positive.  The seven closed balls must
be pairwise disjoint under an outward interval check; otherwise `HOLD-T1`.
This formula depends only on the saved global box and saved seed coordinates,
is fully fixed at T0, and is instantiated without a scientific solve.

## 5. Eight configurations and independently closed workload

The unchanged configurations and state counts are:

| label | tensor dimensions | states |
|---|---:|---:|
| `O113/Base` | `113*113*113` | `1,442,897` |
| `E128/Base` | `128*128*128` | `2,097,152` |
| `O129/Base` | `129*129*129` | `2,146,689` |
| `O161/Base` | `161*161*161` | `4,173,281` |
| `M+` | `166*129*129` | `2,762,406` |
| `R+` | `129*172*129` | `2,862,252` |
| `MR+` | `166*172*129` | `3,683,208` |
| `MR+F` | `207*215*161` | `7,165,305` |

All eight fixed controls and all seven implicit roles are required on all eight
configurations:

```text
sum of state counts                         = 26,333,190
logical roles                               = 8+7 = 15
logical role--configuration rows            = 15*8 = 120
base-state cells per complete row pass      = 15*26,333,190
                                              = 394,997,850
two nominal complete row passes             = 789,995,700
```

These are base-state cells, not FLOPs, augmented vectors, Krylov actions,
bytes, memory, or time.  No implicit solve is pre-deduplicated.  A missing row
is a fixed-schema HOLD and cannot be dropped after a resource failure.

## 6. Outward interval foundation and corrected `E_FV`

### 6.1 Scalar interval and interval-difference hull

Every reported deterministic scalar has a point estimate `qhat_g` and a total
certified radius `r_g` that already includes algebra, linear/nonlinear solve,
quadrature/action, and direct-evaluation errors applicable to that quantity.
Define

\[
 I_g=[L_g,U_g]=
 [down64(qhat_g-r_g),up64(qhat_g+r_g)].
\]

Let `ref=MR+F`.  Serialize the full grid hull

\[
 H_q=[\min_gL_g,\max_gU_g]
\]

and the true grid-to-reference discrepancy bound

\[
 E_{FV}(q)=up64\max_{g\in G}
    \max(|L_g-U_{ref}|,|U_g-L_{ref}|),
\tag{6.1}
\]

where

```text
G = {O113/Base,E128/Base,O129/Base,O161/Base,
     M+,R+,MR+,MR+F}.
```

For symmetric input intervals, every term is at least

```text
abs(qhat_g-qhat_ref) + r_g + r_ref
```

up to outward rounding.  In particular, the reference self-term is `2*r_ref`,
not zero.  The reference-centred interval used downstream is

\[
 C_{FV}(q)=[C^-_q,C^+_q]=
 [down64(qhat_{ref}-E_{FV}),up64(qhat_{ref}+E_{FV})].
\tag{6.2}
\]

`H_q`, every endpoint-difference interval, `E_FV`, and `C_FV` are serialized.
The old `max(observed difference, endpoint errors)` formula is forbidden.

### 6.2 Vector, matrix diagnostic, and curve intervals

For a vector, apply (6.1) coordinatewise.  With a T0-frozen diagonal scale
`S`, define

\[
 E_{FV,S}=up64\max_j E_{FV,j}/S_j.
\]

Weights use `S_j=1`; the matching coordinate vector uses
`S=(34.5,1,1)`.  Interval affine chart evaluation produces weight boxes before
the coordinate envelope is calculated.

For singular values, determinants, ratios, curvatures, and jets, use outward
interval extensions on the certified coordinate box plus their direct
evaluation errors; a point diagnostic with a raw residual is not admissible.

For survival or another curve on the fixed 401-time grid, calculate (6.1) at
every time and serialize the pointwise values and their outward supremum.  No
grid/time/coordinate component may be silently omitted.

### 6.3 Mandatory downstream use

Every absolute cap, quarter-margin rule, tolerance derivation, MC--FV
containment interval, and power implication uses (6.1)--(6.2).  No downstream
section may substitute a point difference or the old v3 maximum.

## 7. Complete implicit-root and diagnostic certificate

### 7.1 Equations

For configuration `g`, the cusp equation is

\[
 F^C_g(t,\theta)=(f_t,f_{tt},f_{ttt})=0.
\]

For sign `sigma` and `a in {0.25,0.50,0.75}`, do not treat the computed cusp
time as exact.  Certify the six-variable joint system

\[
 G^{\sigma,a}_g(z_C,z_F)=
 (F^C_g(z_C),f_t(z_F),f_{tt}(z_F),
  t_F-t_C-\sigma a)=0.
\tag{7.1}
\]

The final row stores both the standalone cusp certificate and every joint
cusp--fold certificate.  The cusp projection of each joint box must intersect
and be contained in the standalone certified cusp box.  Thus cusp-time error
is propagated through the relative fold equation and all fold outputs.

### 7.2 Interval `F/J` and residual-checked linear algebra

For either the 3D cusp or 6D joint system, let `Fhat,Jhat` be point evaluations,
`[F]` and `[J]` their outward interval evaluations on the frozen role/product
box, `R` an approximate inverse, and `s` an approximate Newton correction.
Compute and serialize:

```text
rho_inv = up64(norm_inf(I - R*Jhat))
eps_J   = up64(sup norm_inf([J] - Jhat))
gamma   = up64(rho_inv + norm_inf(R)*eps_J)
```

Require `gamma<1`, then

\[
 K_{up}=up64(\|R\|_\infty/(1-\gamma)).
\]

The correction solve is independently residual-checked:

```text
rho_lin = up64(norm_inf(Jhat*s + Fhat))
eps_F   = up64(sup norm_inf([F] - Fhat))
eta_up  = up64(norm_inf(s)
                + K_up*(rho_lin + eps_F + eps_J*norm_inf(s))).
```

This explicitly includes the linear-solve residual and the `F/J` evaluation
errors.  Rounding an approximate `solve(J,F)` result upward by one ulp is not a
certificate.

Let `L_up` be an outward interval bound on the Jacobian Lipschitz constant on
the same box.  Require

```text
h = up64(K_up*L_up*eta_up) <= 1/2.
```

The Newton--Kantorovich radius is

\[
 r_{NK}=up64((1-\sqrt{1-2h})/(K_{up}L_{up})),
\]

with the exact `L_up=0` limit `r_NK=eta_up`.  An interval-Newton/Krawczyk
inclusion must additionally establish one unique root strictly inside the
role/product box.  Failure of either certificate is HOLD.

### 7.3 Coordinate and output intervals

The certified interval root box, not a scalar raw residual, defines each
coordinate interval.  For the joint fold system, project the 6D root box onto
`z_F`; retain the correlated `z_C` projection for the relative-time audit.

For every reported scalar/vector diagnostic `q`, evaluate an outward interval
extension `[q]` over the certified root box and add the independently bounded
direct action/quadrature error before rounding.  The resulting radius around
`qhat` is the smallest outward symmetric radius containing `[q]`; those
intervals enter Section 6.

The coordinate interval box must be strictly contained in its Section-4.4
role ball.  For each role, the Section-6 scaled coordinate envelope must pass

```text
E_FV,S <= rho_role/4.
```

Branch sign/order, `0.25<0.50<0.75`, orientation, weight positivity, and
cross-role nonoverlap are evaluated on interval boxes.  An interval touching a
wrong sign, order boundary, simplex floor, or another role ball is HOLD.

## 8. Absolute caps, scientific margins, and odd-mesh contraction

### 8.1 Complete `E_abs` table

For every promoted quantity in one of the following classes, use this unchanged
promotion-design map:

| quantity | `E_abs` |
|---|---:|
| cusp, fold, or stationary-root time | `0.05` |
| allocation weight, vector `L_inf` | `0.005` |
| peak/valley ratio | `0.02` |
| event-basin mass | `0.001` |
| final survival | `0.01` |
| scaled fourth derivative | `0.50` |
| singular value or singular-value ratio | `0.01` |
| dimensionless curvature | `0.02` |

A diagnostic outside these eight classes remains a per-grid structural audit
only and receives no mesh-stable or cross-method claim wording.  Promoting such
a diagnostic is `HOLD-T0` until a new numbered design supplies its absolute
cap; it cannot inherit infinity.  Rank is promoted through the listed singular
values/ratio, while determinant-factorization residual remains a per-grid
structural check.

For a lower gate `q>=q0`, use all eight outward intervals:

\[
 q_{cons}=\min_gL_g,\qquad d=q_{cons}-q_0.
\]

For an upper gate `q<=q0`, use

\[
 q_{cons}=\max_gU_g,\qquad d=q_0-q_{cons}.
\]

Require on all eight grids

\[
 d>0,\qquad E_{FV}(q)\le\min(E_{abs,q},d/4).
\tag{8.1}
\]

Coordinates without a scientific inequality, including cusp/fold/root time
and allocation weights, must satisfy the applicable `E_abs` directly.  Weight
vectors use the maximum coordinate envelope.  The match-radius gate in
Section 7 is additional, not a replacement.

### 8.2 Interval-certified odd-mesh contraction

For scalar intervals `I_a=[L_a,U_a]`, define

\[
 D^+(I_a,I_b)=up64\max(|L_a-U_b|,|U_a-L_b|),
\]

\[
 D^-(I_a,I_b)=down64\max(0,L_a-U_b,L_b-U_a).
\]

For every scalar coordinate, weight component, root time, jet, singular
value/ratio, curvature, peak/valley ratio, basin mass, final survival, and
other promoted diagnostic, require either

```text
D+(I_O129,I_O113) <= 5e-8
```

or the strict certified contraction

```text
D+(I_O161,I_O129) < D-(I_O129,I_O113).
```

For a vector, `D+_inf` is the maximum coordinate `D+` and `D-_inf` is the
maximum coordinate `D-`; apply the same rule.  The roundoff floor is exactly
`5e-8`.  Topology must be identical on `O113`, `O129`, and `O161` and must also
match the frozen role on every other required grid.  A noncontracting sequence
is HOLD, not permission to select another grid subset or infer an order.

Parity, separate-box, combined-box, and `MR+--MR+F` differences remain
mandatory diagnostics, while (6.1), (8.1), and this odd contraction are the
scientific gates.

## 9. Fixed-control estimands and physical strips

For every `c in C_MC`, audited `MR+F` roots define one common physical set of
basins/windows.  All eight grids integrate their own density over exactly
those sets.  Every probability, survival value, and local contrast receives a
total interval and the corrected Section-6 grid/reference envelope.  Missing
root identity or common-set integral is HOLD.

The four off-fold controls use all eight grids for fixed-control topology and
physical-law diagnostics, but have no MC windows or cross-method fold claim.

The partial-cell strip rule remains

\[
 M_S(t)=\sum_i p_i(t)|C_i\cap S|/|C_i|,
\qquad
\omega_{union}=\omega_M+\omega_R-\omega_M\omega_R.
\]

Use midpoint strip width `0.10`, relative-parallel width `0.20`, all 120 rows,
the 401 quarter-time points, saved roots/endpoints, and `T=100`.  Require

```text
max outward upper endpoint of union strip mass <= 1e-6.
```

Weights lie in `[0,1]`; direct/inclusion--exclusion fixture agreement is
`<=1e-14`.  The unbounded free-OU strip is diagnostic only, never an upper
bound for reflected killed FV.

## 10. Off-lattice bins and positive local statements

For `(anchor_m3,representative_m1,representative_m2,representative_m3)`, the
frozen `m` values are `(3,1,2,3)`.  The `MR+F` interval-certified ordered roots
define valley basin cuts and equal-width windows.

For `m>1`,

\[
 h=\min(0.4,{1\over4}\min_j(z_{j+1}-z_j),z_1/2,
                                  (100-z_{2m-1})/2),
\]

and for `m=1`,

\[
 h=\min(0.4,z_1/2,(100-z_1)/2).
\]

The complete root intervals must preserve strict ordering and positive window
separation; otherwise HOLD.  Windows are left-closed/right-open.  Internal
basin endpoints go right; event time exactly `100` is in the last basin and
survival means `T>100`.

The exact counts remain:

| object | total |
|---|---:|
| basins | `3+1+2+3 = 9` |
| windows | `5+1+3+5 = 14` |
| positive local contrasts | `4+0+2+4 = 10` |

The `m=1` contrast array is empty.  There is no dummy zero, absence test, or
zero-alpha placeholder.  A contrast is the adjacent maximum-minus-valley
average-density difference `(p_peak-p_valley)/(2h)` and supports only a
positive local finite-resolution feature.

## 11. Tolerances, confidence intervals, and pool diagnostic

### 11.1 Directed tolerances from corrected intervals

Let `qhat_ref` be the reported `MR+F` centre and let `E_FV` be (6.1).  Define

```text
d_M   = qhat_ref - E_FV - 0.005
tau_M = down64(min(0.001,d_M/4))

d_D   = qhat_ref - E_FV
tau_D = down64(d_D/4)
```

For adjacent windows,

```text
gamma = min(qhat_peak-E_peak-qhat_valley-E_valley)
tau_p = down64(min(0.002,gamma/16)).
```

For `m=1`, set `tau_p=0x1.0624dd2f1a9fcp-10` (binary64 decimal
`0.001`).  Set `tau_S=0x1.47ae147ae147bp-7` (binary64 decimal `0.01`).
All values must be finite/positive and every Section-8 gate must already pass.

### 11.2 Exact confidence construction and `E_MC`

For binomial count `k/n` and one-sided rational `alpha_tail`, use

\[
 r_H=up64\sqrt{\log(1/\alpha_{tail})/(2n)},
\]

with outward interval

```text
lower = down64(max(0,k/n-r_H))
upper = up64(min(1,k/n+r_H)).
```

For a two-sided survival band atom `alpha_band`, use

\[
 r_{DKW}=up64\sqrt{\log(2/\alpha_{band})/(2n)}.
\]

For a probability, `E_MC=max(k/n-lower,upper-k/n)`.  For contrast,

```text
lower = down64((L_peak-U_valley)/(2h))
upper = up64((U_peak-L_valley)/(2h)),
```

and `E_MC` is the larger endpoint distance from the point contrast.

The MC--FV acceptance interval has named endpoints and one separator:

```text
fv_acceptance.lower = down64(qhat_ref - E_FV - tau_q)
fv_acceptance.upper = up64(qhat_ref + E_FV + tau_q)
```

Require the MC interval to be contained in these endpoints and
`E_MC<=tau_q`.  Basin lower endpoints exceed `0.005`; local contrast lower
endpoints exceed zero.  Every use of `E_FV` here means Section 6.1.

### 11.3 Two-pool same-generator regression diagnostic

Each pool separately must pass containment and precision against the same
frozen planning/FV target.  A separately alpha-allocated interval for
`q_pool1-q_pool2` must contain zero, and its half-width must be no larger than
the sum of the two applicable precision tolerances.

This is reported exactly as:

```text
both_pools_compatible_with_common_target = true/false
pool_difference_interval_contains_zero = true/false
pool_regression_precision_passed = true/false
```

Passing means no detected same-generator regression at the designed
resolution.  It is **not statistical equivalence**: the difference interval
need not be contained in a predeclared equivalence region, and no equivalence
flag or wording is allowed.

## 12. Exact alpha and joint-power contracts

### 12.1 Global `alpha=0.05`

The atom/tail universe is unchanged except that the fourth family is named
`pool same-generator regression diagnostics`:

| family | count | alpha each | total |
|---|---:|---:|---:|
| 4 controls * 3 survival views | 12 | `1/1200` | `1/100` |
| (9 basins + 4 `S(100)`) * 3 views * 2 tails | 78 | `1/5200` | `3/200` |
| 14 windows * 3 views * 2 tails | 84 | `1/5600` | `3/200` |
| 8 pool DKW atoms + (13 basin/tail + 14 window) * 2 pools * 2 tails | 116 | `1/11600` | `1/100` |
| **total** | **290** |  | **`1/20=0.05`** |

The ten contrast intervals derive from window intervals.  There is no `m=1`
contrast atom.  Exact rational enumeration and an independent recomputation
are mandatory.

### 12.2 Sixty-two power atoms and corrected implications

The pool primitives remain

```text
2*(4 survival processes + 9 basins + 4 S(100) + 14 windows) = 62.
```

The planning alternative is the audited `MR+F` probability/survival object,
before MC.  For each candidate `N` with pool size `n=N/2`, substitute the exact
confidence radii and the corrected Section-6 `C_FV` endpoints into every
scientific, containment, precision, pooled, and pool-regression gate.

For affine gate coefficients `a_j`, confidence consumption `c`, and positive
remaining planning slack `s`, use the unique sufficient cap

\[
 \delta_{gate}=down64(s/(2\sum_j|a_j|)).
\]

Each primitive receives the minimum cap from all gates using it.  Interval
arithmetic must prove the Cartesian product of 62 atom events implies every GO
gate, including the newly enlarged interval-hull containment.  There is no
alternative atomization.

Bin atoms use exact outward binomial probability outside
`[ceil(n(p-delta)),floor(n(p+delta))]`; survival uses outward
`min(1,2 exp(-2n delta^2))`.  Sum all 62 upper bounds without independence.
Choose the first

```text
N = 200,000,400,000,...,50,000,000
```

with every positive cap and `1-beta_all>=0.90`.  Otherwise `HOLD-T2`; no
top-up, larger cap, altered interval, or dropped statement is allowed.

## 13. Universal rate, seeds, pools, and exact-ID replicate

Weights are finite/nonnegative and satisfy

```text
abs(fsum(weights)-1) <= 2^-48.
```

The independent rate calculation is

\[
 (0.01/0.04)(1+2^{-48})e^{1/3}
 =0.3489031062715236\ldots<\boxed{0.35},
\]

with margin `0.001096893728476378`.  Each hazard is finite, nonnegative, and
`<=0.35`; clipping is forbidden.

The SHA-256 counter domain remains

```text
positive-b-stage-b-v4-off-lattice-sha256-counter-v1
```

The master material is exactly

```text
positive-b-stage-b-v4-fixed-master-seed-v1
```

For control-hash bytes `H_c`, pool byte `p in {0x01,0x02}`, unsigned
big-endian 64-bit local ID `i`, unsigned big-endian 64-bit counter `j`, and the
32 raw bytes of the canonical T2 hash, a random block is exactly

```text
SHA256(domain || 0x00 || SHA256(master_material) || 0x00 ||
       T2_hash_bytes || H_c || p || u64be(i) || u64be(j)).
```

The future code hash freezes byte-to-uniform/Gaussian conversion and draw
order.  Pool bytes and control hashes separate namespaces.  Each pool has
local IDs `0,...,N/2-1`, chunk size `100,000`, no new-ID retry, and no top-up.
The exact-ID replicate must reproduce raw and canonical bytes and has zero
alpha/power.

## 14. No-cycle graph, canonical bytes, and resources

The directed graphs are:

```text
T0 selector code/tests/protocol (frozen before Stage-A read)
  -> audited Stage-A object
  -> canonical T1 object/audit
  -> Stage-B scientific manifest M_B
  -> scientific result/evidence

M_B hash -> independent A_B
(M_B,A_B,A_B-tests) -> external no-cycle protocol
```

and

```text
audited Stage-B object
  -> canonical T2 object/audit
  -> MC scientific manifest M_MC
  -> scientific result/evidence

M_MC hash -> independent A_MC
(M_MC,A_MC,A_MC-tests) -> external no-cycle protocol.
```

Neither scientific manifest pins its auditor or external protocol.  Each
auditor hard-codes the already immutable manifest hash and imports no producer.

Both chains require lexical `lstat/O_NOFOLLOW`, no-concurrent-writer windows,
exact initial/final snapshots, duplicate-key rejection, canonical result and
evidence bytes, failure-atomic promotion, rollback, and post-promotion rehash.

Before science, freeze maximum augmented vectors, nonlinear iterations, root
evaluations, Krylov actions, resident/scratch bytes, row/full-run wall time,
and abort semantics from code structure and non-scientific fixtures.  A cap hit
is operational HOLD, never permission to reduce 120 rows.

## 15. GO/HOLD semantics and current decision

`GO-FV-STAGE-B` requires two byte-identical complete 120-row executions and an
independent audit establishing fixed-control identity, unique interval-
certified grid-specific cusp/fold roots, complete Section-6 envelopes, every
`E_abs`/quarter-margin/odd-contraction gate, physical laws/strips, common time
sets, resources, and exact provenance.

`GO-OFF-LATTICE` requires both pools, pooled analysis, exact-ID replicate, all
290 alpha atoms/tails, all 62 power implications, survival/basin/window/local-
contrast statements, corrected FV containment, the pool regression diagnostic,
closure, rate, ID, byte, and independent-audit gates.

The design ledger after the Round-67 repair is:

```text
open design P0 = 0
open design P1 = 0
open design P2 = 0

design status    = GO-DESIGN
execution status = HOLD-EXECUTION
science status   = NOT RUN / NOT INSPECTED

AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

Execution remains held until the T0 selector, audited Stage-A input, T1
scientific package and no-cycle audit chain, complete deterministic Stage-B
pass, T2 package, and off-lattice chain all exist and pass independent attacks.
