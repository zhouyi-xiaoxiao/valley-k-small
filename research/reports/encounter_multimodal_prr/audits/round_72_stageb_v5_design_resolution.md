# Round 72: Stage-B v5 design resolution and adversarial non-regression audit

Date: 2026-07-14  
Role: result-blind design repair verifier  
Verdict: **GO-DESIGN / HOLD-EXECUTION**  
Round-70 design blockers: **CONFIRMED FREE (`P0=0`, `P1=0`, `P2=0`)**

## 1. Scope and strict non-execution boundary

This round read the complete independent Round-70 attack and its complete
science-free counterexample test, then checked the v5 repair against both open
findings and every v4 closure that Round 70 had already accepted.

The audited repair snapshot is:

| role | repository path | SHA-256 |
|---|---|---|
| Stage-B v5 design | `notes/positive_b_stage_b_validation_design_v5.md` | `136085075ad23fc22a40cf03725c9151f11ff356cff4f6f39e5c5fbb24317ddd` |
| v5 science-free resolution tests | `code/test_stageb_v5_design_resolution.py` | `702c2bcd1e46191b30b8c8a4e723a1c4d84b6807db6f091e90fae64b62f1f334` |
| attacked Stage-B v4 design | `notes/positive_b_stage_b_validation_design_v4.md` | `e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691` |
| independent Round-70 attack | `audits/round_70_stageb_v4_independent_attack.md` | `0fa94a3d94db356e81f62746f267743bbc3f431dc82959894d00b88a9bea9c62` |
| Round-70 counterexample tests | `code/test_stageb_v4_design_round70.py` | `bf91141021375fd583fc1e85a75c6c931fd966637ad628c8b5bd84b632262d20` |
| Round-69 v4 resolution | `audits/round_69_stageb_v4_design_resolution.md` | `7972335d11cb55337c248a39967173d548d711dad937bf9dbdfefd9d29f2ef27` |
| Round-69 positive tests | `code/test_stageb_v4_design_resolution.py` | `b882aaa1737847dd58606140466b9c03572211767ea9ad4c208d7cdb69c20fb2` |
| Round-67 v3 attack | `audits/round_67_stageb_v3_independent_attack.md` | `4f71f9e517ce5d3ca44e403332fb52be37d070e7e546db284cbbed83bf4d6c35` |

No Stage-A object, hidden/canonical scientific value, mesh-65/97 model,
Stage-B row, cusp/fold solve, off-lattice trajectory, scientific producer,
scientific auditor, manifest, main entry point, result, or manuscript was run,
opened, or changed.  The v4 design and all historical tests were left
unchanged.  This is design evidence only.

## 2. Executive decision

V5 closes the Round-70 P0 by replacing the one-sided roundoff exception with
one exact Boolean whose floor branch requires **both** adjacent odd-grid
differences to be at the floor.  The exact finite counterexample that passed
v4 now fails v5, while a both-at-floor fixture and a genuine strict-contraction
fixture still pass.

V5 closes the Round-70 P1 by giving a byte-unique mathematical selector before
any Stage-A read.  It fixes the comparison-node fields and rank, predecessor/
branch/successor operands, central secant subtraction order, orientation scalar
and zero-tie HOLD, normalization order, normal, both `ell` vectors, candidate
displacement base, eligibility operations, side labels, and complete pair-rank
operation order.  It separately defines RN and exact-real directed rounding,
including executable `nextDown`/`nextUp` semantics and certified
`sqrt`/`log`/`exp` handling.  Saved-field role radii now have explicit lower-
directed expressions plus independent global-box and pairwise-disjointness
checks.

The valid v4 clauses are protected by a hash-closed normative import with a
four-item replacement map.  The complete interval hull, six-variable implicit
certificate, absolute caps, pool non-equivalence semantics, no-cycle graph,
workload, alpha, power, rate, seed, and provenance requirements therefore
remain in force.  Positive regression tests recompute all cardinalities and
inspect these closures.

The resulting ledger is:

```text
P0 = 0
P1 = 0
P2 = 0

design status    = GO-DESIGN
execution status = HOLD-EXECUTION
science status   = NOT RUN / NOT INSPECTED

AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

This `GO-DESIGN` is intentionally narrow.  It permits the v5 design to undergo
another independent attack and permits later science-free construction of the
T0 selector package.  It does not authorize any Stage-A or Stage-B science.

## 3. P0 resolution: exact odd-mesh Boolean

### 3.1 The v4 bypass

The attacked v4 floor branch inspected only
`D+(O129,O113)<=5e-8`.  Therefore

```text
O113=[0.300,0.300]
O129=[0.300,0.300]
O161=[0.304,0.304]
reference=[0.302,0.302]
```

had

```text
D_coarse_plus  = 0
D_fine_plus    = 0.004
D_coarse_minus = 0
E_FV            = 0.002 <= E_abs,weight=0.005,
```

yet passed through the coarse-at-floor short circuit.

### 3.2 The v5 repair

V5 freezes the complete scalar Boolean as

```text
max(D_coarse_plus,D_fine_plus) <= ODD_FLOOR
or
D_fine_plus < D_coarse_minus,
```

where `ODD_FLOOR` is the exact binary64
`0x1.ad7f29abcaf48p-25`.  The first branch is now true only if both adjacent
differences are at the floor.  For the Round-70 fixture the maximum is `0.004`,
and strict contraction is also false, so the complete Boolean returns false.

The resolution test calls this complete Boolean, not just its contraction
sub-expression.  It also verifies:

```text
coarse=middle=fine  -> floor branch passes;
0.0 -> 0.4 -> 0.5  -> strict contraction passes.
```

The vector rule first forms coordinatewise interval distances, takes the fixed
`L_inf` aggregate for each adjacent level, and applies the same Boolean.  No
promoted diagnostic can use the old one-sided exception.

### 3.3 Failure semantics

The topology gate on all three odd grids and all other fixed grids remains
mandatory.  A failed Boolean is HOLD.  It cannot be repaired by changing the
grid subset, changing the floor, choosing a different diagnostic coordinate,
or inferring an empirical convergence order.  The P0 path is therefore closed
at design level.

## 4. P1 resolution: byte-unique selector

### 4.1 Exact branch object and comparison-node choice

V5 retains the intentional cross-collection join and requires exactly one
byte-consistent candidate record in generation, mesh 65, and mesh 97.  It now
names the comparison-record inputs:

```text
target_offset
realized_signed_offset
normalized_fold_residual
acceptance_index.
```

Only exact-byte `target_offset=0x1.8p-1` records are eligible.  The rank is

```text
(abs(RN(realized_signed_offset-TARGET)),
 abs(normalized_fold_residual),
 acceptance_index).
```

The selected acceptance index uniquely identifies branch node `b`; its
immediate ordered neighbors are `p` and `n`.  Duplicate, missing, repeated, or
non-adjacent objects are HOLD.

### 4.2 Exact secant and orientation

The previously prose-only frame is now an operation trace:

```text
c_j = RN(theta_n[j]-theta_p[j])
dt = RN(t_n-t_p)
omega = RN(float64(sigma)*dt).
```

`omega==0` is HOLD.  `omega<0` negates both secant coordinates; `omega>0`
keeps them.  Normalization uses the printed multiply/multiply/add/sqrt/divide
order, with no FMA, hypot, reassociation, or one-sided substitute.  The normal
is the fixed `+pi/2` rotation `(-u_1,u_0)`.

The test exercises `sigma=-1`, confirms the tangent and side-label reversal,
and confirms that a zero orientation scalar is HOLD.  An implementation cannot
choose a different orientation convention after viewing candidates.

### 4.3 Exact `ell`, displacement, eligibility, and pair rank

The local scale is exactly the minimum of

```text
norm2RN(theta_b-theta_p)
norm2RN(theta_n-theta_b),
```

with coordinate subtraction and norm order fixed.  A mutation using the full
`theta_n-theta_p` span changes a frozen eligibility fixture from false to true
and is detected.

Candidate displacement is exactly

```text
d_i = RN(theta_i-theta_b)
```

coordinatewise.  A fixture eligible from `b` becomes ineligible when the base
is mutated to `p`, demonstrating that the formerly missing base is material.
The orientation-derived sign of `s_i` supplies minus/plus labels.  Pair rank
fixes every addition, absolute value, division, and final index field.  No
collection ordering or late branch relabel is admissible.

### 4.4 RN versus directed endpoints

V5 distinguishes two different contracts:

```text
RN(x)      = nearest binary64, ties to even;
down64(x)  = greatest finite binary64 <= exact real x;
up64(x)    = least finite binary64 >= exact real x.
```

With `y=RN(x)`, exact comparison selects `y` or one `nextDown`/`nextUp` step.
The expression inside a directed operator is an exact-real syntax tree from
binary64 leaves; it is not an already-RN intermediate unless an inner
`RN(...)` is printed explicitly.

For exact `x=1/10`, binary64 RN lies above the rational.  The test confirms

```text
down64(x) < x < up64(x)=RN(x)
nextUp(down64(x)) = up64(x).
```

Thus replacing `down64` with RN fails an executable mutation.  Algebraic
expressions use integer/rational evaluation.  `sqrt`, `log`, and `exp` use a
pinned MPFR precision-escalation kernel whose certified interval must identify
the unique required endpoint; host `libm` is not the definition and cannot
make a gate decision.  Exact square comparisons resolve representable/halfway
`sqrt` cases, and exact `log(1)`/`exp(0)` cases are special-cased, so precision
escalation has no unresolved exact-boundary convention.

### 4.5 Role radii and two independent checks

V5 computes lower-directed boundary distances and exact-metric pair distances
from saved binary64 fields, then

```text
rho_i=down64(min(1/128,b_i/4,s_i/4)).
```

It does not apply `down64` to an unspecified RN expression.  It independently
outward-checks:

1. every closed metric ball is strictly inside all six global-box faces; and
2. `up64(rho_i+rho_j)<down64(d_exact(z_i,z_j))` for every pair.

The seven-seed positive fixture passes both.  A boundary fixture with two
next-down radii passes strict separation, while mutating both to rounded `0.1`
touches the separation and fails.  The global-box and disjointness portion of
Round-70 P1 is therefore explicit and executable.

## 5. Non-regression audit of accepted v4 closures

### 5.1 Normative import is closed, not informal

V5 pins the complete v4 bytes by SHA-256 and gives an exhaustive replacement
map: selector filenames, Section 4, Section 8.2, and the current ledger.  Every
other v4 clause remains normative verbatim.  An implementation that cannot
read and hash both snapshots is `HOLD-T0`.  This prevents a repair edit from
silently dropping a prior gate.  V5 also explicitly remaps imported references
from v4 Section 4/4.1/4.4 to v5 Sections 3--5, so no surviving v4 clause can
resolve a dangling reference into the superseded selector text.

### 5.2 Correct interval hull remains mandatory

The scalar interval remains

```text
I_g=[down64(qhat_g-r_g),up64(qhat_g+r_g)]
E_FV=up64 max_g max(abs(L_g-U_ref),abs(U_g-L_ref)).
```

It contains both endpoint errors and in the symmetric case covers
`abs(qhat_g-qhat_ref)+r_g+r_ref`.  The reference self-term remains `2*r_ref`.
Coordinatewise vector envelopes, all-401-time curve envelopes, absolute caps,
quarter margins, tolerance transforms, MC containment, and power implications
all use this object.

### 5.3 Implicit root/output certificate remains complete

Every fold retains the six-variable joint cusp--fold system with
`t_F-t_C-sigma*a=0`.  The mandatory quantities remain

```text
rho_inv, eps_J, gamma, K_up,
rho_lin, eps_F, eta_up, L_up, r_NK,
```

plus interval-Newton/Krawczyk unique-root inclusion.  Cusp uncertainty enters
the fold system, root-box projections define coordinate intervals, and every
output is interval-evaluated over the certified box with direct evaluation
error added.

### 5.4 Caps, pools, no-cycle graph, and seeds remain closed

The eight caps remain `0.05`, `0.005`, `0.02`, `0.001`, `0.01`, `0.50`,
`0.01`, and `0.02` for their exact v4 quantity classes.  All-eight interval
margins still require `E_FV<=min(E_abs,d/4)` where thresholded.

The two-pool check remains a powered same-generator regression diagnostic.
It is explicitly not statistical equivalence.  Both pools separately target
the common object; the difference interval must contain zero and meet the
fixed precision condition.

The manifest/auditor graph remains one-way: immutable manifest hash first,
independent auditor second, external protocol third.  A scientific manifest
never pins its own auditor.

V5 intentionally retains the exact v4 SHA-256 counter domain and master
material, including `u64be(i)||u64be(j)`.  Repairing selector arithmetic does
not silently change a later random experiment.

## 6. Independent arithmetic recomputation

The eight state counts recompute to

```text
26,333,190.
```

Therefore

```text
logical rows                         = 15*8 = 120
base-state cells / complete pass     = 15*26,333,190
                                    = 394,997,850
two nominal complete passes          = 789,995,700.
```

The exact alpha ledger is

```text
12/1200 + 78/5200 + 84/5600 + 116/11600
  = 1/100 + 3/200 + 3/200 + 1/100
  = 1/20 = 0.05.
```

The power primitive count remains

```text
2*(4+9+4+14)=62.
```

The rate recomputes as

```text
(0.01/0.04)*(1+2^-48)*exp(1/3)
  = 0.3489031062715236... < 0.35.
```

No workload, alpha, power, or rate regression was found.

## 7. Executable evidence

The new v5 checks passed:

```text
python3 code/test_stageb_v5_design_resolution.py
  Ran 8 tests -- OK

python3 -m py_compile code/test_stageb_v5_design_resolution.py
  PASS
```

All historical design tests passed unchanged:

```text
python3 code/test_stageb_v3_design_round67.py
  Ran 4 tests -- OK

python3 code/test_stageb_v4_design_resolution.py
  Ran 6 tests -- OK

python3 code/test_stageb_v4_design_round70.py
  Ran 5 tests -- OK
```

One discovery invocation over all four files returned:

```text
python3 -m unittest discover -s code -p 'test_stageb_v*_*.py'
  Ran 23 tests -- OK
```

The tests are science-free: they use finite hand fixtures, exact rational
arithmetic, binary64 adjacency, text/hash pins, and integer/rational workload
checks.  They do not inspect a scientific value.

## 8. Remaining implementation and independent-audit boundary

This resolution verifies that the v5 mathematical contract is closed.  It is
not the actual T0 selector implementation.  Before any Stage-A read, the
future source, tests, and protocol named by v5 must exist, pin v4 and v5, and
pass all mutation families listed in v5 Section 10, including FMA-sensitive,
subnormal, signed-zero, duplicate/tie, nonfinite, cross-branch collision,
directed-transcendental, role-ball, displacement-base, orientation, and full
odd-Boolean fixtures.

The next audit must be performed independently and result-blind against the v5
bytes and, later, against the actual selector bytes.  `GO-DESIGN` must not be
misread as `GO-FV-STAGE-B` or `GO-OFF-LATTICE`.

## 9. Final boundary

```text
ROUND-70 DESIGN BLOCKERS: CONFIRMED FREE

P0 = 0
P1 = 0
P2 = 0

GO-DESIGN
HOLD-EXECUTION
NOT RUN / NOT INSPECTED

AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

Pending: independent v5 design attack, then science-free construction and
independent attack of the pinned v5 T0 selector package.
