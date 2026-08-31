# Positive-`B` fixed-control robustness design v1

Date: 2026-07-14  
Stage: **F0 STATIC DESIGN**  
Decision: **GO-DESIGN / HOLD-IMPLEMENTATION / HOLD-SCIENCE**  
Authorized scientific command: **NONE**  
Positive-budget science run while writing this design: **NONE**

## 0. Purpose and non-execution boundary

This is the new fixed-control route required after the terminal allocation-v6
result `HOLD_SCIENCE_AUDIT_VALID`. It is not Stage-B v6, does not inherit a
cusp/fold object, and does not repair or reinterpret the failed allocation
homotopy.

The design prospectively tests three LP-derived controls predicted at the
free-exposure level to have one, two, and three maxima. All three use the same
installed budget `B=0.01`, transport, contact geometry, initial law, four
support profiles, support locations, and support widths. Only their conserved
allocation ratios differ.

This file freezes scientific intent and validation rules. It does not create
a producer, manifest, result, canonical pointer, or executable command. No
positive-budget row may be evaluated until:

1. this design has a stable SHA-256;
2. an independent design audit accepts the exact bytes;
3. a science-free implementation and schema/mutation suite exists;
4. that implementation has its own append-only F0 attestation and independent
   acceptance; and
5. a future F1 manifest pins all of those hashes before any F1 value is read.

## 1. Pinned evidence and route boundary

| input | SHA-256 | use |
|---|---|---|
| `audits/round_102_prr_posthold_strategy_attack.md` | `08ddd608de8b5431653d6f91f89f4869ca0f3a92bb6c4970d4eb9e406480b602` | post-HOLD route decision and fixed-control evidence requirements |
| `notes/modal_certificate_theory_and_prr_redirect.md` | `38dde114552d0cea69f714d7493d3cb6715e1b4ed436431045a50a57360326be` | repaired modal-certificate theorem, complete-window interpretation, and claim ceiling |
| `scratch/modal_certificate_lp_poc_result.json` | `6f04ef4c618677d6d26b80cd04e3d4f8c9918fd50a649cfc0dd0bf064ccce604` | exploratory raw LP ratios, checkpoints, and free-exposure diagnostics |
| `artifacts/data/positive_b_broad_four_slab_result.json` | `51e8eb4bdb652124865d0c39e6f36b99d13ed61578b161e0f75b142cada49401` | historical result-informed pilot only |
| `notes/positive_b_stage_b_validation_design_v4.md` | `e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691` | source of already attacked FV challenge/envelope primitives only |
| `notes/positive_b_stage_b_validation_design_v5.md` | `136085075ad23fc22a40cf03725c9151f11ff356cff4f6f39e5c5fbb24317ddd` | evidence that the old cusp-dependent chain cannot authorize this route |

The LP POC is explicitly exploratory, result-informed, free-exposure evidence.
It is a control-design input, not a positive-budget result, preregistered
discovery, interval certificate, or publication gate.

## 2. Maximum possible F1 claim

If every F1 gate in this design passes, the deterministic claim is limited to:

> On the declared finite window `0.5 <= t <= 35`, three allocations selected
> before positive-budget evaluation have respectively exactly one, two, and
> three nondegenerate local maxima in every required finite-volume
> configuration at the same physical budget `B=0.01`. Their root topology,
> curvature, relative peak/valley prominence, event-basin masses, survival,
> parity, alignment, and box diagnostics pass the predeclared complete
> all-configuration uncertainty envelope.

Even a full F1 pass does not establish:

- a continuum/PDE exact mode count;
- an unbounded-domain result;
- a root count outside `[0.5,35]`;
- an allocation cusp, fold manifold, or phase diagram;
- off-lattice absence of extra modes;
- continuous-density `L1` agreement; or
- positive-budget physical `d=3`.

F2/F3 independent-process evidence is still required for a PRR submission.

## 3. Frozen physical model

All primary controls use the same values:

| parameter | decimal binary64 input | `float.hex()` |
|---|---:|---|
| installed budget `B` | `0.01` | `0x1.47ae147ae147bp-7` |
| particle diffusion | `0.002` | `0x1.0624dd2f1a9fcp-9` |
| OU stiffness | `0.1` | `0x1.999999999999ap-4` |
| OU mean | `0.95` | `0x1.e666666666666p-1` |
| midpoint start | `0.14` | `0x1.1eb851eb851ecp-3` |
| relative-parallel start | `-0.35` | `-0x1.6666666666666p-2` |
| relative-perpendicular start | `0.0` | `0x0.0p+0` |
| initial half-width | `0.02` | `0x1.47ae147ae147bp-6` |
| contact radius | `0.16` | `0x1.47ae147ae147bp-3` |
| transverse period | `1.0` | `0x1.0000000000000p+0` |
| common support half-width | `0.04` | `0x1.47ae147ae147bp-5` |

The four midpoint support centres, in immutable order, are

```text
(0.35, 0.60, 0.75, 0.90)
```

with binary64 representations

```text
(0x1.6666666666666p-2,
 0x1.3333333333333p-1,
 0x1.8000000000000p-1,
 0x1.ccccccccccccdp-1).
```

The normalized support profiles, contact functional, initial distribution,
coordinate convention, Doi killing convention, and physical budget functional
must be byte-identical in meaning across all controls and configurations.
Grid counts, cell sums without physical volumes, stationary exposure, or
contact-tube volume cannot replace the installed-budget functional.

## 4. Three primary controls and exact budget normalization

### 4.1 Raw LP provenance bytes

The source order is the support-centre order in Section 3. Raw binary64 ratios
are frozen exactly as follows:

| ID | target | raw decimal ratios | raw `float.hex()` ratios | raw exact sum |
|---|---:|---|---|---|
| `lp_m1` | 1 maximum | `(0.03, 0.9100000000000001, 0.03, 0.03)` | `(0x1.eb851eb851eb8p-6, 0x1.d1eb851eb8520p-1, 0x1.eb851eb851eb8p-6, 0x1.eb851eb851eb8p-6)` | `36028797018963973 / 36028797018963968` |
| `lp_m2` | 2 maxima | `(0.5420243013882049, 0.03, 0.048245050837663034, 0.37973064777413196)` | `(0x1.1584359032fd2p-1, 0x1.eb851eb851eb8p-6, 0x1.8b39347154f3cp-5, 0x1.84d81c65ea487p-2)` | `9007199254740991 / 9007199254740992` |
| `lp_m3` | 3 maxima | `(0.4016285358628774, 0.2761816314605931, 0.03, 0.2921898326765295)` | `(0x1.9b4482caaf892p-2, 0x1.1acf5b8b8445bp-2, 0x1.eb851eb851eb8p-6, 0x1.2b33cfbe47127p-2)` | `36028797018963967 / 36028797018963968` |

### 4.2 Exact mathematical controls

Binary64 simplex outputs do not sum to one as exact real dyadic rationals,
even when a floating summation rounds to `1.0`. To make “same installed
budget” mathematically literal, define once at F0

```text
S_c = exact rational sum of the four raw binary64 ratios,
w_c,j = raw_w_c,j / S_c.
```

The exact rational `w_c,j`—not a silently renormalized binary64 vector—is the
mathematical F1 control. The formula preserves every ratio and every strict LP
sign because it multiplies all raw weights by the same positive scalar. A
future implementation may use a point binary64 approximation only if it also
serializes an outward parameter interval containing the exact rational weight
and propagates that interval into every certified quantity.

This normalization is the only permitted pre-science canonicalization. It is
not optimization or post-result refitting. After this file is hash-frozen:

- no component may move independently;
- no weight may be clipped or projected;
- no failed control may be replaced by the historical anchor or another LP
  solution; and
- no configuration may use a different rounding of the exact rational control.

Every exact normalized weight is positive. The original nominal `0.03` LP
floor is provenance, not a future exact lower-bound claim; F1 requires strict
positivity and exact unit sum of the mathematical rational vector.

## 5. Historical anchor is context only

The prior result-informed control

```text
(0.28, 0.27736690132708747, 0.0857172266153233, 0.3569158720575891)
```

at `B=0.01` remains useful pilot/context evidence. It is not a primary F1
control and must not:

- substitute for `lp_m3`;
- enter the primary all-configuration envelope;
- rescue a failed primary row or gate;
- determine an F2 window, effect size, or sample count;
- support the prospective same-budget 1/2/3-control claim; or
- change the F1 global decision.

No new historical-anchor grid is required by this design. If a later project
runs it on new configurations, those rows must live in a separately named,
append-only context annex created after the primary F1 result and must have no
decision edge back into F1/F2.

## 6. Frozen full-window topology contract

The finite deterministic window is exactly

```text
I = [0.5,35.0].
```

The free-exposure LP checkpoints define broad root-search bands. They do not
serve as positive-budget values. Each band must contain exactly one certified
root with the listed type; all remaining time tiles must exclude zero from the
derivative interval.

| control | frozen derivative checkpoints | ordered root-search bands and roles | exact F1 topology |
|---|---|---|---|
| `lp_m1` | `f'(5.5)>0`, `f'(12)<0` | `[5.5,12]: P1` | `maximum` |
| `lp_m2` | `f'(2)>0`, `f'(5.5)<0`, `f'(16)>0`, `f'(35)<0` | `[2,5.5]: P1`; `[5.5,16]: Q1`; `[16,35]: P2` | `maximum, minimum, maximum` |
| `lp_m3` | `f'(2)>0`, `f'(5)<0`, `f'(6.5)>0`, `f'(11)<0`, `f'(17)>0`, `f'(35)<0` | `[2,5]: P1`; `[5,6.5]: Q1`; `[6.5,11]: P2`; `[11,17]: Q2`; `[17,35]: P3` | `maximum, minimum, maximum, minimum, maximum` |

Additionally require `f'(t)>0` on the complete prefix from `0.5` to the first
listed positive checkpoint. For `lp_m1`, require `f'(t)<0` on `[12,35]`.
For `lp_m2` and `lp_m3`, the ordered search bands tile the remainder of the
window. Shared band endpoints are single checkpoints and cannot be assigned a
new root.

An extra root, a missing root, an unresolved zero tile, a root touching a
search-band boundary, a reversed type, or a root outside its role band is a
global F1 `HOLD`. “At least the desired number” cannot replace the frozen exact
finite-window topology.

## 7. Required finite-volume configurations

### 7.1 Existing refinement, parity, and box family

The physical boxes are unchanged. Baseline bounds are midpoint
`[-0.25,1.85]`, relative-parallel `[-1.8,1.8]`, and periodic transverse width
`1`. Enlarged bounds are exactly those below.

| label | midpoint box/cells | relative-parallel box/cells | transverse cells | states | purpose |
|---|---|---|---:|---:|---|
| `O113/Base` | `[-0.25,1.85]/113` | `[-1.8,1.8]/113` | `113` | `1,442,897` | coarse odd refinement |
| `E128/Base` | `[-0.25,1.85]/128` | `[-1.8,1.8]/128` | `128` | `2,097,152` | even parity baseline |
| `O129/Base` | `[-0.25,1.85]/129` | `[-1.8,1.8]/129` | `129` | `2,146,689` | primary odd refinement |
| `O161/Base` | `[-0.25,1.85]/161` | `[-1.8,1.8]/161` | `161` | `4,173,281` | fine odd refinement |
| `M+` | `[-0.55,2.15]/166` | `[-1.8,1.8]/129` | `129` | `2,762,406` | midpoint-box enlargement |
| `R+` | `[-0.25,1.85]/129` | `[-2.4,2.4]/172` | `129` | `2,862,252` | relative-box enlargement |
| `MR+` | `[-0.55,2.15]/166` | `[-2.4,2.4]/172` | `129` | `3,683,208` | combined box enlargement |
| `MR+F` | `[-0.55,2.15]/207` | `[-2.4,2.4]/215` | `161` | `7,165,305` | fine combined-box reference |

### 7.2 Explicit half-cell alignment family

Even parity alone is not called an explicit alignment test. The following
four same-box configurations are mandatory. They use the `E128/Base` spacing,
but shift the FV centres by half a cell without moving any physical support,
initial law, OU mean, contact set, or domain boundary.

| label | tensor states | frozen construction | states |
|---|---|---|---:|
| `A_M` | `129*128*128` | midpoint vertex-centred dual volumes; boundary volumes have half width | `2,113,536` |
| `A_R` | `128*129*128` | relative-parallel vertex-centred dual volumes; boundary volumes have half width | `2,113,536` |
| `A_Y` | `128*128*128` | periodic transverse cells shifted by exactly half one `E128` period cell | `2,097,152` |
| `A_MRY` | `129*129*128` | all three half-cell shifts combined | `2,130,048` |

For a reflecting interval `[L,U]` with `h=(U-L)/128`, a vertex-centred dual
grid has state locations `L+i h`, `i=0,...,128`, and control-volume boundaries
`L`, `L+h/2`, ..., `U-h/2`, `U`. The first and last volumes therefore have
width `h/2`. SG face conductances and row rates must include the actual
control-volume widths. Initial and support profiles are integrated over the
actual dual volumes; point sampling is forbidden.

For the periodic coordinate, `A_Y` uses the same 128 equal wrapped cells with
all cell boundaries translated by `h/2` modulo the period. Exact wrapped
contact fractions and initial-profile masses are recomputed on those cells.
Duplicating the periodic endpoint is forbidden.

These are discretizations of the same physical problem, not shifted physical
geometries. If the implementation cannot prove conservation, positivity,
physical-volume normalization, and detailed balance on the half-volume grids,
the alignment family and global F1 decision are `HOLD`; `E128/Base` cannot be
used as a surrogate.

### 7.3 Workload identity

The 12 configurations contain

```text
34,787,462 base states per one-control complete pass
104,362,386 base-state cells for 3 controls x 12 configurations
208,724,772 base-state cells for two complete process replicas.
```

These are state-cell counts, not bytes, FLOPs, Krylov iterations, interval
subtiles, or wall time. Every one of the 36 logical control-configuration rows
is mandatory. No equal-looking row may be deduplicated.

## 8. Rigorous finite-dimensional time-interval certificate

### 8.1 Why a dense time scan is insufficient

The exploratory POC used a dense floating-point diagnostic. F1 instead needs
a finite-dimensional certificate that excludes an unobserved stationary pair
between sample times. `scipy.sparse.linalg.expm_multiply` values plus sign
sampling do not provide that certificate.

The required route uses the positivity and `l1` contraction of the killed
sub-Markov semigroup, validated semigroup-action defects, local derivative
norms, and interval Taylor bounds. Discrete detailed balance and the
self-adjoint similarity remain mandatory, independent generator-structure
checks, but the global self-adjoint spectral norm bound is diagnostic only:
it is mathematically valid yet may be far too wide to exclude a single root.
It is never sufficient by itself for a v1 time tile.

If any required local contraction, action, rounding, or interval link cannot
be made rigorous for a row/configuration, its certificate is `null`,
`time_interval_certificate_passed=false`, and global F1 is `HOLD`.

### 8.2 Killed sub-Markov generator and independent reversibility check

For one fixed configuration and control, let `Q` be the finite row generator,
including diagonal Doi killing `k_i >= 0`, and let `p0` be the initial column
law. Require, in outward arithmetic,

```text
Q_ij >= 0 for i != j,       Q 1 = -k <= 0.
```

With

```text
p(t) = exp(Q^T t) p0,
f(t) = k^T p(t),
S(t) = 1^T p(t),
```

`exp(Q^T s)` is positive and an induced-`l1` contraction for every `s>=0`.
Indeed, `exp(Qs)1<=1`, so positivity gives

```text
||exp(Q^T s) x||_1 <= ||x||_1
```

for every signed vector `x`. The implementation must serialize a directed
Metzler/sign proof and the killed row-sum identity; a sampled numerical norm
or empirical mass decrease is not a substitute.

As a separate structural gate, the SG/periodic free generator must have
strictly positive cell stationary weights `pi_i` satisfying exact detailed
balance

```text
pi_i Q_ij = pi_j Q_ji  for every free edge i<->j.
```

Diagonal killing preserves this identity. With `D=diag(pi)`, require an
outward proof of

```text
H = D^(1/2) Q D^(-1/2) = H^T <= 0.
```

The nonpositivity proof is the discrete Dirichlet form

```text
x^T D Q x
 = -1/2 sum_{i,j} pi_i Q_ij (x_i-x_j)^2
   - sum_i pi_i k_i x_i^2 <= 0.
```

The future implementation must serialize positive `pi` bounds, edgewise
detailed-balance enclosures, conductance signs, killing signs, and the
Dirichlet-form construction. A floating residual near zero is not a proof.
For half-volume grids, `pi` and the conductances must include physical cell
volumes.

Define

```text
u = D^(-1/2) p0,
v = D^(1/2) k.
```

Then the global identity

```text
f^(r)(t) = u^T H^r exp(tH) v
```

is retained as a cross-check. The arbitrary scale of `pi` cancels from
`||u||_2 ||v||_2`. The corresponding global spectral bound and its condition
factor must be serialized as `self_adjoint_global_bound_diagnostic`, but v1
forbids using that field to close a time tile, root inclusion, or survival
gate. Survival is projected from the same validated sub-Markov state `p(t)`;
it is not a separate unvalidated exponential action.

### 8.3 Executable local `l1` derivative bounds

For every tile left endpoint `t_i` and integer `r>=0`, commutation of `Q^T`
with its semigroup gives, for `t>=t_i`,

```text
f^(r)(t)
 = k^T exp(Q^T(t-t_i)) (Q^T)^r p(t_i).
```

Define validated action vectors and directed upper norms

```text
x_r(t_i) = (Q^T)^r p(t_i),
M_r(t_i) = up(||k||_infinity ||x_r(t_i)||_1),  r=2,3,4.
```

Then

```text
|f^(r)(t)| <= M_r(t_i),       t>=t_i.
```

The state, each sparse matrix action, the exact-rational control interval,
every absolute-value reduction, and the final product must be outwardly
enclosed. F1 needs finite `M_2`, `M_3`, and `M_4` at every tile left endpoint.
An ordinary floating norm, a norm computed from a point state, overflow, or a
nonfinite upper endpoint is `HOLD`.

The old global self-adjoint estimate may also be computed from a directed
Gershgorin `Lambda`, but it remains a diagnostic even when narrower than an
uncertified plot. Only the local `M_r(t_i)` bounds above enter v1 Taylor tiles.

### 8.4 Validated absolute-time states and jets

At every requested dyadic tile endpoint or interval-Newton evaluation time
`t_i`, F1 needs an outward state enclosure and scalar jets

```text
[p](t_i) contains exp(Q^T t_i) p0,
J_r(t_i) contains k^T (Q^T)^r p(t_i),  r=0,1,2,3.
```

The frozen anti-wrapping rule is direct absolute-time evaluation from `p0` at
every requested `t_i`; a certified state may not be advanced from the previous
tile and silently reused. Construct an approximate path `z(s)` on `[0,t_i]`
and certify in `l1`

```text
d(s) = z'(s) - Q^T z(s),
epsilon(t_i) = ||z(0)-p0||_1
               + integral_0^t_i ||d(s)||_1 ds.
```

The sub-Markov contraction proves

```text
||z(t_i)-exp(Q^T t_i)p0||_1 <= epsilon(t_i).
```

The small projected exponential, Krylov/Arnoldi relation residual, restart
interfaces, roundoff, loss of orthogonality where relevant, sparse matrix
actions, starting-vector construction, exact-parameter enclosure, and defect
integral must all have directed error padding. An independently coded verifier
must recompute the generator identities, terminal residual data, defect bound,
state error, jets, and `M_r`; two complete process replicas must agree on the
canonical certificate bytes. Standard binary64 `expm`, unvalidated Lanczos,
or `expm_multiply` output alone is a mandatory `HOLD`.

The full vector state/action enclosures may be stored in content-addressed
append-only binary blobs rather than inline JSON, but their hashes, formats,
directed norm reductions, error budgets, and reconstruction metadata are
mandatory certificate fields. `S(t_i)=1^T p(t_i)` and all boundary masses are
formed from that same validated state and its `l1` error.

F0 may choose a concrete Krylov, Taylor, or uniformization implementation only
before its attestation is accepted; the method, precision, residual quadrature
or analytic integral, restart policy, and resource limits are then immutable.
Uniformization without a rigorous tail, sampled ODE integration, and
finite-difference time derivatives are forbidden substitutes.

### 8.5 Local interval tiles and adaptive stop

Start from the exact dyadic quarter grid on `[0.5,35]`. For a tile
`J=[t_i,t_i+delta]`, compute the validated left-endpoint state, jets, and local
bounds. Two independent consequences of Section 8.3 are formed with outward
interval arithmetic:

```text
[f']_L(J)  = J_1(t_i)
              + [-M_2(t_i) delta, M_2(t_i) delta],

[f'']_L(J) = J_2(t_i)
              + [-M_3(t_i) delta, M_3(t_i) delta],

[f']_T(J)  = J_1(t_i) + [0,delta] J_2(t_i)
              + [-M_3(t_i) delta^2/2, M_3(t_i) delta^2/2],

[f'']_T(J) = J_2(t_i) + [0,delta] J_3(t_i)
              + [-M_4(t_i) delta^2/2, M_4(t_i) delta^2/2].
```

Use the outward interval intersections

```text
[f'](J)  = [f']_L(J) intersection [f']_T(J),
[f''](J) = [f'']_L(J) intersection [f'']_T(J).
```

Both operands enclose the complete continuous-time range, so an empty
intersection indicates an arithmetic, state, or residual inconsistency and is
an immediate `HOLD`. These are contraction/Taylor enclosures, not sampled
interpolants.

Tiles whose required sign is certified are closed. Every unresolved tile is
bisected left first at its exact dyadic midpoint. The fixed limits are:

```text
initial tile width = 0.25
maximum bisection depth = 20
maximum interval-Newton steps per root cluster = 12
maximum final root-interval width = 0.05.
```

Changing any limit after seeing F1 output is forbidden.

### 8.6 Root inclusion and full-window exclusion

Within each frozen search band:

1. all tiles outside one connected candidate cluster must have `[f'](J)`
   strictly in the expected sign half-line: positive to the left and negative
   to the right of a maximum cluster, negative to the left and positive to
   the right of a minimum cluster;
2. the candidate cluster must be strictly inside its search band;
3. `[f''](X)` on the candidate root interval `X` must exclude zero with the
   required maximum/minimum sign; and
4. interval Newton

   ```text
   N(X) = c - J_1(c)/[f''](X)
   ```

   must satisfy `N(X) subset interior(X)` after at most 12 steps.

The accepted root interval is the final outward intersection. Every tile in
the entire `[0.5,35]` window is therefore either strict-sign excluded or part
of exactly one unique-root inclusion. This is the finite-dimensional exact
root-count certificate.

Two disconnected candidate clusters, `0 in [f''](X)`, an interval-Newton
failure, a root width above `0.05`, or any unresolved tile at depth 20 is
`HOLD`. A dense scan cannot override it.

## 9. Root, shape, mass, and survival gates

All quantities below are interval quantities evaluated on the certified root
intervals. Point estimates may be reported for figures but never replace the
outward gate.

### 9.1 Root and curvature

For every expected root:

- the interval inclusion and full-window exclusion in Section 8 pass;
- root density has a strictly positive lower endpoint;
- the dimensionless curvature

  ```text
  chi = t^2 f''(t)/f(t)
  ```

  has the expected sign and `inf |chi| >= 0.05`;
- the interval root width is at most `0.05`; and
- a point-centre scaled residual `|t f'(t)/f(t)| <= 1e-8` is serialized only as
  a non-certifying regression diagnostic.

### 9.2 Peak balance, valley ratios, and prominence

Let `p_j` be certified peak-density intervals and `q_j` certified intervening
valley-density intervals.

- For `lp_m2` and `lp_m3`, require

  ```text
  min_j lower(p_j) / max_j upper(p_j) >= 0.10.
  ```

  For `lp_m1`, peak balance is exactly `null`, not a dummy `1` gate.
- For every intervening valley, require the outward ratio

  ```text
  upper(q_j) / min(lower(p_j),lower(p_{j+1})) <= 0.85.
  ```

- For every adjacent peak-valley pair, require normalized prominence

  ```text
  1 - upper(q_j)/lower(p_adjacent) >= 0.15.
  ```

- For `lp_m1`, which has no valley, define only the boundary prominence

  ```text
  1 - max(upper(f(0.5)),upper(f(35)))/lower(p_1) >= 0.15.
  ```

The `lp_m1` valley-ratio array is empty and its adjacent-prominence array is
empty. No absence test is inferred from MC later; exact finite-window absence
comes only from Section 8.

### 9.3 Event basins

Let the ordered valley roots be `q_1,...,q_{m-1}` and let final time be
`T_mass=100`. Define using validated survival intervals

```text
M_1 = 1-S(q_1),
M_j = S(q_{j-1})-S(q_j),
M_m = S(q_{m-1})-S(100).
```

For `lp_m1`, `M_1=1-S(100)`. Require:

- every basin-mass lower endpoint is at least `0.005`;
- the outward basin sum contains `1-S(100)` and has absolute closure radius at
  most `1e-9`;
- `0 < S(100) < 1` by strict interval endpoints;
- survival is nonincreasing at every quarter-grid time, every root endpoint,
  and tail times `35,50,75,100`, with maximum allowed certified increase
  `1e-12`; and
- the differential mass-balance interval contains zero with radius at most
  `1e-9` at the same times.

Survival at an uncertain valley time is enclosed by validated evaluations at
the root-interval endpoints plus monotonicity. A centre value alone is
forbidden.

### 9.4 Positivity and boundary diagnostics

Every row also requires:

- initial mass error at most `1e-12`;
- physical installed-budget error at most `1e-12` relative to exact `B=0.01`;
- nonnegative generator off-diagonals and killing;
- free row-sum error and killed identity `Q 1=-k` within independently frozen
  algebraic enclosures;
- state lower bounds no smaller than `-1e-12` at every evaluated state; and
- the mass fraction in the union of the outermost two FV layers of each
  reflecting coordinate at quarter-grid, root, and tail states no larger than
  `1e-6`.

The boundary-layer rule is a finite-dimensional box diagnostic, not an
unbounded-domain theorem.

## 10. Complete all-configuration envelope

### 10.1 Outward scalar envelope

Every promoted scalar on configuration `g` has a point centre `qhat_g` and a
total radius `r_g` including parameter, algebra, profile/contact integration,
generator, semigroup-action, interval-time, root, and direct-evaluation error.
Set

```text
I_g=[L_g,U_g]
   =[down64(qhat_g-r_g),up64(qhat_g+r_g)].
```

Use `ref=MR+F` and all 12 configurations

```text
G={O113/Base,E128/Base,O129/Base,O161/Base,
   M+,R+,MR+,MR+F,A_M,A_R,A_Y,A_MRY}.
```

The complete discrepancy is

```text
E_FV(q)=up64 max_{g in G}
              max(|L_g-U_ref|,|U_g-L_ref|).
```

The reference self-term is `2 r_ref`. The full hull, every pairwise endpoint
difference, `E_FV`, and

```text
C_FV=[down64(qhat_ref-E_FV),up64(qhat_ref+E_FV)]
```

must be serialized. `max(point difference,separate errors)` is forbidden.

### 10.2 Absolute caps

| promoted quantity | `E_abs` |
|---|---:|
| stationary-root time | `0.05` |
| peak-balance ratio | `0.02` |
| valley ratio | `0.02` |
| normalized prominence | `0.02` |
| event-basin mass | `0.001` |
| final survival | `0.01` |
| dimensionless curvature | `0.02` |

For a lower gate `q>=q0`, let `d=min_g L_g-q0`; for an upper gate `q<=q0`,
let `d=q0-max_g U_g`. Require

```text
d>0 and E_FV(q) <= min(E_abs(q),d/4).
```

Unthresholded root times require `E_FV<=0.05`. Missing role identity, a `null`
inside a required class, or a nonfinite interval is `HOLD`.

### 10.3 Odd refinement contraction

For intervals `I_a=[L_a,U_a]`, define

```text
Dplus(I_a,I_b)=up64(max(|L_a-U_b|,|U_a-L_b|)),
Dminus(I_a,I_b)=down64(max(0,L_a-U_b,L_b-U_a)).
```

For every promoted scalar and every control, require either

```text
Dplus(I_O129,I_O113) <= 5e-8
```

or

```text
Dplus(I_O161,I_O129) < Dminus(I_O129,I_O113).
```

Topology and role identity must agree on all three odd grids. No subset or
inferred convergence order is permitted.

### 10.4 Parity, alignment, and box gates

In addition to the complete envelope:

- `E128/Base` and `O129/Base` must have identical certified topology and each
  promoted pairwise `Dplus` must not exceed its `E_abs`;
- each of `A_M,A_R,A_Y,A_MRY` must have identical topology to `E128/Base`, and
  every promoted pairwise `Dplus` to `E128/Base` must not exceed `E_abs`;
- each of `M+,R+,MR+,MR+F` must have the frozen topology;
- the local box comparisons `Base--M+`, `Base--R+`, `Base--MR+`, and
  `MR+--MR+F` must each satisfy the applicable `E_abs`; and
- every configuration must pass the boundary-layer rule independently.

The separate and combined alignment/box rows prevent cancellation from being
used as evidence. A combined row cannot replace a failed directional row.

## 11. F0 -> F1 -> F2 dependency and no-refit law

### F0: science-free implementation freeze

F0 must eventually contain, in append-only form:

- exact parsing of this design and all pinned inputs;
- exact rational control construction from raw hex ratios;
- all 12 configuration constructors;
- SG/periodic conservation and detailed-balance proofs, including half-volume
  grids;
- validated direct-from-zero sub-Markov semigroup actions, independent defect
  verification, local `M_2/M_3/M_4` bounds, and interval-time certificate
  implementation;
- exact output schemas and canonical JSON rules;
- positive and negative synthetic fixtures; and
- mutation tests for every control byte, topology role, time/checkpoint,
  configuration, threshold, cap, depth, and HOLD/null path.

F0 may use only synthetic/small explicit matrices and analytic fixtures. It
may not evaluate a primary control on a positive-budget production grid.

### F1: one deterministic campaign

A future F1 manifest may be created only after an independent F0 acceptance.
It must pin the design, F0 record, implementation, tests, dependencies,
runtime, exact controls, configurations, environment, output paths, and two
replica commands. F1 runs exactly the 36 required rows in two complete
processes. Canonical promotion requires byte-identical results or a frozen
HOLD; no partial pass is promoted.

### F2: off-lattice planning freeze

F2 begins only from an independently accepted F1 result and audit. A
mechanical selector fixed at F0 maps accepted `MR+F` root intervals and the
complete `E_FV` envelopes to physical basin cuts, fixed windows, positive
local contrasts, tolerances, familywise alpha, power, trajectory count, seed
domain, chunks, and two pools. F2 is planning only. The off-lattice science
run is a later F3.

If F1 is `HOLD`, F2 is not built. A historical-anchor value, failed-grid
subset, or exploratory free-exposure value cannot seed F2.

### No-refit law

After F0 is accepted, the following are immutable:

- control ratios and exact normalization;
- `B`, geometry, supports, initial law, and contact rule;
- time window, checkpoints, search bands, metric definitions, thresholds,
  caps, configurations, alignment construction, and reference grid;
- interval method, bisection/Newton limits, schema, and hard-stop semantics;
  and
- F1-to-F2 selector logic.

No output-dependent weight, budget, mesh, box, origin, root band, window,
threshold, solver tolerance, precision, or sample-size change is allowed.
Changing the scientific contract requires a new version, an explicit
result-informed label, new confirmation data, and no reuse of the old result
as held out.

## 12. Append-only schema contract

No schema file is created by this note. Future artifacts must use new paths
and immutable content hashes. At minimum:

### F0 record

```text
schema_version
stage = positive_b_fixed_control_f0
status = PASS_F0_IMPLEMENTATION | HOLD_F0
design_sha256
source_hashes
implementation_hashes
exact_control_rationals
configuration_contract
certificate_contract
synthetic_test_ledger
mutation_test_ledger
authorized_scientific_command = null
limitations
```

### F1 manifest/result/audit

```text
manifest: schema_version, stage, f0_record_sha256, design_sha256,
          pinned_hashes, exact_controls, configurations, environment,
          replica_commands, output_paths, forbidden_claims

result:   schema_version, stage, status, manifest_sha256, f0_record_sha256,
          36 required control_rows, generator_structure_certificates,
          content_addressed_state_action_blobs,
          per_time_action_defect_and_roundoff_budgets,
          per_tile_J0_to_J3_and_M2_to_M4,
          local_lipschitz_and_taylor_intersections,
          root_inclusion_and_full_window_exclusion_ledger,
          self_adjoint_global_bound_diagnostics, all_config_envelopes,
          all_gates_passed, required_false_claim_flags, limitations

audit:    schema_version, stage, release_status, result_sha256,
          manifest_sha256, audit_integrity_passed,
          scientific_result_passed, independent_checks, limitations
```

### F2 plan/audit

```text
plan:  schema_version, stage, accepted_f1_result_sha256,
       accepted_f1_audit_sha256, selector_hash,
       physical_basins, windows, contrasts, E_FV, tolerances,
       alpha_ledger, power, N, seed_domain, chunks, pools,
       authorized_scientific_command = null

audit: schema_version, stage, plan_sha256, dependency_checks,
       power_checks, multiplicity_checks, no_refit_checks, status
```

Every result path must contain a unique frozen run or content identifier.
Overwriting an existing F0/F1/F2 artifact is forbidden. A later index may
append a new pointer; it may not mutate an old object.

## 13. Hard stops

Any one of the following returns global `HOLD` and stops downstream work:

1. a source/design/hash/schema mismatch;
2. a control parse, exact-rational normalization, positivity, or budget error;
3. any missing control-configuration row;
4. failure to prove SG/periodic conservation, detailed balance, or `H<=0`;
5. an unvalidated/directly chained semigroup state, missing independent defect
   verification, ordinary-binary64-only error budget, nonfinite local
   derivative bound, or disagreement between certificate replicas;
6. an empty local-bound/Taylor intersection, unresolved time tile, failed
   interval Newton inclusion, extra/missing root, wrong role, root-band
   boundary contact, or adaptive-limit exhaustion;
7. failure of curvature, peak, valley, prominence, basin, survival, mass
   balance, positivity, or boundary gates;
8. failure of complete envelope, odd contraction, parity, alignment, or any
   directional/combined box challenge;
9. nonidentical process replicas;
10. any post-output refit, tolerance change, grid subset, role substitution,
    historical-anchor rescue, or F2 construction from a held F1 result.

No hard stop may be converted to PASS by “near tolerance,” visual inspection,
a dense scan, more trajectories, or a manuscript wording change.

## 14. Current ledger

```text
F0 design bytes                         = WRITTEN BY THIS NOTE
independent F0 design acceptance        = NOT YET ESTABLISHED
F0 implementation/schema/tests          = NOT BUILT
validated sub-Markov time certificate    = NOT BUILT
half-cell FV implementation             = NOT BUILT
F0 append-only attestation               = NOT BUILT
F1 manifest                              = NOT BUILT
F1 positive-budget execution             = NOT AUTHORIZED
F2 off-lattice planning                  = NOT BUILT
F3 off-lattice execution                 = NOT AUTHORIZED
historical anchor role                   = PILOT/CONTEXT ONLY
```

The only present authorization is independent attack of this static F0
design. Scientific execution remains on HOLD.
