# Round 69: Stage-B v4 result-blind design resolution

Date: 2026-07-14  
Role: v4 design repair and science-free adversarial resolution of Round 67  
Verdict: **GO-DESIGN / HOLD-EXECUTION**

## 1. Scope and immutable boundary

This round creates v4 without changing v3.  It repairs the one P0, three P1,
and three P2 findings in the independent Round-67 attack and adds a separate
positive-regression test file.  It does not execute or inspect science.

No hidden/canonical Stage-A or Stage-B scientific result was opened.  No
candidate, mesh-65/97 model, FV row, cusp/fold solve, MC trajectory, scientific
producer, main entry point, or scientific auditor was run.  No producer,
manifest, result, auditor, v3 design, or manuscript was modified.

The attacked and repaired snapshot is:

| role | repository path | SHA-256 |
|---|---|---|
| attacked v3 design | `notes/positive_b_stage_b_validation_design_v3.md` | `0c7119870e173bfbe5042b3f1c19c7c5851061940cab66e7e0dab98f54becd58` |
| Round-65 v3 resolution | `audits/round_65_stageb_v3_design_repair.md` | `fcbb84e25073f00b5f76075cfacaf0c13a7cb788b8124020eff481a773c40bfb` |
| independent Round-67 attack | `audits/round_67_stageb_v3_independent_attack.md` | `4f71f9e517ce5d3ca44e403332fb52be37d070e7e546db284cbbed83bf4d6c35` |
| historical Round-67 tests | `code/test_stageb_v3_design_round67.py` | `fc17fbbd5e648a6b8629fb07d6030931c3dcaa820466851f6a88e84b28317342` |
| v4 design | `notes/positive_b_stage_b_validation_design_v4.md` | `e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691` |
| v4 positive regressions | `code/test_stageb_v4_design_resolution.py` | `b882aaa1737847dd58606140466b9c03572211767ea9ad4c208d7cdb69c20fb2` |

The v4 design and positive-regression hashes above are their final content
hashes.

## 2. Executive decision

V4 preserves all already validated structural choices:

- eight unchanged fixed controls and seven grid-specific implicit roles;
- all 15 roles on all eight FV configurations;
- no off-lattice fold-transition/global-mode claim and no `m=1` contrast;
- Stage-A-saved-object-only off-fold selection;
- physical partial-cell strips and universal `Lambda=0.35`;
- 290 alpha atoms/tails summing exactly to `0.05`;
- 62 underlying joint-power atoms and `1-beta_all>=0.90`; and
- the finite-volume numerical-cusp/non-continuum claim boundary.

It changes the numerical logic in the places Round 67 showed were unsafe:

1. every deterministic value is now an outward interval;
2. `E_FV` is a full interval-difference hull containing both endpoint errors;
3. cusp/fold roots and outputs receive complete interval certificates;
4. role radii and selector arithmetic are fixed at T0 from saved fields only;
5. absolute caps and interval-certified odd-mesh contraction are restored; and
6. pool, identity, endpoint, and no-cycle wording is unambiguous.

The post-repair ledger is:

```text
P0 = 0
P1 = 0
P2 = 0

GO-DESIGN
HOLD-EXECUTION
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

## 3. P0 closure: a genuine outward interval envelope

### Round-67 defect

V3 used

```text
max(abs(qhat_g-qhat_ref),r_g,r_ref),
```

which returned `0.10` for

```text
qhat_g=0.00, qhat_ref=0.10, r_g=r_ref=0.08
```

even though admissible true endpoints differ by `0.26`.

### V4 repair

V4 first constructs

```text
I_g = [down64(qhat_g-r_g),up64(qhat_g+r_g)]
```

and defines

```text
E_FV = up64 max_g max(abs(L_g-U_ref),abs(U_g-L_ref)).
```

For symmetric intervals this contains

```text
abs(qhat_g-qhat_ref)+r_g+r_ref.
```

The Round-67 counterexample therefore gives `E_FV=0.26`, not `0.10`.
The full grid hull, every endpoint difference, `E_FV`, and explicit
reference-centred interval

```text
[down64(qhat_ref-E_FV),up64(qhat_ref+E_FV)]
```

are serialized.  Vectors are coordinatewise with a frozen scaled max norm;
curves are pointwise on all 401 times plus an outward supremum.

Every absolute cap, quarter-margin rule, tolerance, MC containment endpoint,
and power implication is required to use this repaired object.  There is no
remaining downstream route to substitute the old v3 maximum.  P0-1 is closed.

## 4. P1 closures

### P1-1 — incomplete implicit-root error propagation: CLOSED

V4 evaluates `F` and `J` as outward intervals on the role box.  It separately
records:

```text
rho_inv  inverse residual
eps_J    Jacobian evaluation interval
rho_lin  Newton linear-solve residual
eps_F    equation evaluation interval
K_up     perturbation-certified inverse norm
eta_up   correction plus all residual/evaluation terms
L_up     interval Jacobian Lipschitz bound
r_NK     outward Newton--Kantorovich radius.
```

An interval-Newton/Krawczyk inclusion must prove one unique root.  Merely
rounding an approximate linear solve upward is explicitly rejected.

More importantly, every fold role certifies the six-variable joint system

```text
(cusp equations, fold equations, t_fold-t_cusp-signed_offset)=0.
```

Thus the cusp interval, its linear/nonlinear errors, and the relative-time
coupling propagate into the fold coordinate box.  Every scalar/vector output
is interval-evaluated on that certified box with direct action/quadrature error
added.  Coordinate, weight, jet, singular-value, ratio, curvature, and curve
intervals then enter the Section-6 hull.  All three missing links identified by
Round 67 are closed.

### P1-2 — unavailable role radii and late selector implementation: CLOSED

V4 assumes no role-specific Stage-A radius.  For the saved cusp and six saved
comparison seeds it uses only:

```text
global box: 9<=t<=18, abs(theta_i)<=0.15
saved seed coordinates
fixed metric max(abs(dt)/34.5,abs(dtheta_1),abs(dtheta_2)).
```

It computes boundary distance `b_i`, nearest-seed separation `s_i`, and

```text
rho_i = down64(min(1/128,b_i/4,s_i/4)).
```

Positive radii and outward pairwise ball disjointness are mandatory.  This is
instantiable from saved fields and the global frozen box; missing fictional
upstream radius fields are no longer required.

The selector's IEEE rounding, operation order, no-FMA rule, subnormal policy,
dot/norm formula, signed-zero canonicalization, finite total order, and tie
semantics are written at T0.  A future selector source/tests/protocol must be
hashed and independently attacked **before** any Stage-A result is opened.
Consequently neither implementation nor floating tie behavior is selected at
the data boundary.

Candidate identity is also exact: the same index/bytes across the three named
collections is an intentional join; uniqueness is within each collection and
across distinct logical candidates.  Different indices with identical full
control bytes, duplicate entries within one collection, or cross-branch reuse
are HOLD.

### P1-3 — missing `E_abs` and odd-mesh contraction: CLOSED

V4 restores the promotion-design caps exactly:

| quantity | cap |
|---|---:|
| cusp/fold/root time | `0.05` |
| allocation-weight `L_inf` | `0.005` |
| peak/valley ratio | `0.02` |
| event-basin mass | `0.001` |
| final survival | `0.01` |
| scaled fourth derivative | `0.50` |
| singular value/ratio | `0.01` |
| dimensionless curvature | `0.02` |

For lower/upper scientific gates, the conservative margin is formed from all
eight interval endpoints and must satisfy

```text
d>0
E_FV <= min(E_abs,d/4).
```

Coordinates without a scientific inequality satisfy `E_abs` directly.

For interval values on `O113/O129/O161`, V4 defines the upper and lower
possible distances `D+` and `D-`.  It requires either the complete coarse
interval difference to be at most the exact `5e-8` roundoff floor or

```text
D+(O161,O129) < D-(O129,O113).
```

This is stronger and fail-closed relative to applying the point-estimate
inequality to uncertain endpoints.  The rule covers every promoted coordinate,
jet, singular diagnostic, curvature, ratio, mass, and final survival; topology
must also remain identical.  Noncontraction is HOLD.

## 5. P2 closures

### P2-1 — pool wording: CLOSED WITHOUT AN EQUIVALENCE CLAIM

Each pool must separately be compatible with the same planning/FV target.
The separately allocated pool-difference interval must contain zero and meet a
precision gate.  V4 names these fields:

```text
both_pools_compatible_with_common_target
pool_difference_interval_contains_zero
pool_regression_precision_passed.
```

The text says only “no detected same-generator regression at the designed
resolution.”  It explicitly states that the interval need not lie inside an
equivalence region and sets
`pool_statistical_equivalence_verified=false`.  No statistical-equivalence
claim remains.

### P2-2 — endpoint and duplicate identity semantics: CLOSED

The MC--FV acceptance interval has named `lower` and `upper` fields, each with
one formula; there is no double comma.  The cross-collection join and the true
duplicate domains are separately defined, so the three required copies of one
candidate cannot be rejected as duplicates.

### P2-3 — freeze/no-cycle vocabulary: CLOSED

The freeze ladder now states the actual order:

1. selector code/tests/protocol are frozen before Stage-A is read;
2. T1 freezes Stage-B science and the T2 compiler, then `M_B`;
3. only after the `M_B` hash exists is `A_B` frozen with that hash, and an
   external protocol records `(M_B,A_B,A_B-tests)`;
4. T2 analogously freezes `M_MC`; only afterward are `A_MC` and its external
   no-cycle protocol frozen.

Neither manifest pins its auditor/protocol.  Each auditor hard-codes the
already immutable manifest hash and imports no producer.  The ladder and graph
now use the same vocabulary and cannot be read as requiring a hash cycle.

## 6. Independent workload arithmetic

The eight state counts are:

```text
113^3       = 1,442,897
128^3       = 2,097,152
129^3       = 2,146,689
161^3       = 4,173,281
166*129*129 = 2,762,406
129*172*129 = 2,862,252
166*172*129 = 3,683,208
207*215*161 = 7,165,305
sum          = 26,333,190.
```

All eight fixed and seven implicit roles remain on every grid:

```text
logical rows                            = (8+7)*8 = 120
base-state cells / complete row pass    = 15*26,333,190
                                          = 394,997,850
two nominal complete passes             = 789,995,700.
```

Interval certification changes arithmetic around each solve but not the base
role--grid matrix.  The design still labels this as base-state cells, not a
resource upper bound, and separately requires action/vector/memory/time caps.

## 7. Independent alpha, power, and rate arithmetic

The alpha ledger remains exactly:

```text
12  * 1/1200  = 1/100
78  * 1/5200  = 3/200
84  * 1/5600  = 3/200
116 * 1/11600 = 1/100
sum             1/20 = 0.05.
```

Renaming the fourth family from consistency to same-generator regression does
not change its primitive intervals.  Its count remains
`8+(13+14)*2*2=116`.  The power primitives remain

```text
2*(4 survival + 9 basins + 4 S(100) + 14 windows) = 62.
```

The gate-to-atom implication must now consume the larger corrected interval
hull.  The statement count is unchanged; feasibility can only become harder.
The smallest `200,000` multiple with `1-beta_all>=0.90` is selected, or T2
holds at the unchanged `50,000,000` cap.

The universal rate independently recomputes as

```text
(0.01/0.04)*(1+2^-48)*exp(1/3)
  = 0.3489031062715236 < 0.35
margin = 0.001096893728476378.
```

The exact v4 SHA-256 counter domain/master material/block concatenation,
two-pool ID namespace, retry rule, and exact-ID zero-evidence replicate remain
fully specified.

## 8. New-risk adversarial pass

The repair was attacked for regressions introduced by intervalization:

| attack | resolution |
|---|---|
| Does the envelope omit either endpoint error? | no; each grid term contains both complete intervals and the reference self-term is `2*r_ref` |
| Can a quarter margin or MC gate still call the v3 formula? | no; every downstream use is normatively bound to Sections 6.1--6.2 |
| Is a vector/curve reduced to one convenient component/time? | no; coordinatewise and every 401-time interval plus supremum are required |
| Is an approximate Newton solve treated as exact? | no; inverse and correction residuals plus `F/J` errors are explicit |
| Is cusp error omitted from a fold? | no; every fold is a six-dimensional joint cusp--fold certificate |
| Can a radius depend on an unavailable upstream field? | no; only saved box/seed coordinates and a T0 constant enter |
| Can selector arithmetic be chosen after Stage-A? | no; source/tests/protocol and exact FP behavior freeze before Stage-A read |
| Can a large scientific margin bypass an absolute cap? | no; the gate is the minimum of cap and quarter margin |
| Can noncontracting odd grids pass the full envelope alone? | no; contraction/roundoff is a separate mandatory gate |
| Does the pool diagnostic imply equivalence? | no; target compatibility/no-detected-regression wording and a false equivalence flag are explicit |
| Can intentional collection copies trigger duplicate HOLD? | no; join versus uniqueness domains are disjoint |
| Can T1/T2 pin their auditor in a cycle? | no; auditor freeze follows the scientific-manifest hash and remains external |

No new open P0, P1, or P2 survived this pass.

## 9. Claim and execution boundary

Even after future scientific passes, v4 licenses only a finite-volume
mesh/alignment/box-stable numerical cusp plus independently preserved
unchanged-control event-law features.  It does not license a rigorous
continuum/PDE cusp, off-lattice cusp/fold/fourth jet, one-mode-side absence,
global exact mode count, or pool equivalence claim.

The current status is:

```text
design status    = GO-DESIGN
execution status = HOLD-EXECUTION
science status   = NOT RUN / NOT INSPECTED

P0 = 0
P1 = 0
P2 = 0

AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

## 10. Science-free regression evidence

The historical v3 test remains unchanged and continues to demonstrate why the
v3 formula fails.  The new positive test

```text
code/test_stageb_v4_design_resolution.py
```

checks:

1. the exact v4 snapshot;
2. the Round-67 counterexample now yields `0.26`;
3. every missing implicit-certificate term is normative;
4. saved-field role radii are positive/disjoint in a fixture;
5. absolute caps and interval odd contraction are present and discriminate a
   noncontracting fixture;
6. workload, alpha, power, and rate arithmetic remain exact; and
7. pool, endpoint, seed, authorization, and no-cycle wording is unambiguous.

Final verification is limited to `py_compile`, Ruff, the historical four
science-free tests, the six new science-free tests, path/hash assertions,
balanced Markdown fences, and small integer/rational calculations.  No
scientific entry point is authorized or invoked.
