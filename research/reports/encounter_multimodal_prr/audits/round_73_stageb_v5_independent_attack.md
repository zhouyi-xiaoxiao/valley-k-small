# Round 73: independent adversarial pre-run attack on the Stage-B v5 design

Date: 2026-07-14  
Role: independent, result-blind numerical-analysis, floating-point, selector,
and provenance attacker; distinct from the v5 repair/resolution author  
Verdict: **ACCEPT-DESIGN / HOLD-EXECUTION**

## 1. Scope and hard non-execution boundary

This round independently attacked the complete bytes of
`notes/positive_b_stage_b_validation_design_v5.md`.  It read the complete v4
and v3 designs imported through the frozen hash chain, the complete Round-70
attack, the complete Round-72 resolution, and both the Round-70 and Round-72
science-free tests.  It specifically tried to recover or create bypasses in:

- the two-branch odd-mesh floor/contraction Boolean;
- scalar, vector, odd/even, three-grid, and topology coverage;
- exact-real directed rounding versus ordinary round-to-nearest;
- half-ulp, one-ulp, subnormal, signed-zero, `NaN`, and infinity boundaries;
- comparison-record, pair-rank, index, and cross-branch uniqueness;
- secant direction, orientation tie, displacement base, and local scale;
- saved-field role radii, box containment, and pairwise separation;
- hash inheritance, stale-object substitution, cross-reference replacement,
  no-cycle provenance, and execution authorization; and
- the completeness of the future T0 mutation/decision table.

No Stage-A object, hidden/canonical scientific value, mesh-65/97 model,
Stage-B row, cusp/fold solve, off-lattice trajectory, producer, scientific
auditor, scientific manifest, main entry point, result, evidence, or
manuscript was run, opened, or modified.  This round created only one
science-free design test and this report.

The attacked and supporting snapshots are:

| role | repository path | SHA-256 |
|---|---|---|
| attacked Stage-B v5 design | `notes/positive_b_stage_b_validation_design_v5.md` | `136085075ad23fc22a40cf03725c9151f11ff356cff4f6f39e5c5fbb24317ddd` |
| imported Stage-B v4 design | `notes/positive_b_stage_b_validation_design_v4.md` | `e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691` |
| inherited Stage-B v3 design | `notes/positive_b_stage_b_validation_design_v3.md` | `0c7119870e173bfbe5042b3f1c19c7c5851061940cab66e7e0dab98f54becd58` |
| independent Round-70 attack | `audits/round_70_stageb_v4_independent_attack.md` | `0fa94a3d94db356e81f62746f267743bbc3f431dc82959894d00b88a9bea9c62` |
| Round-72 v5 resolution | `audits/round_72_stageb_v5_design_resolution.md` | `5653bc0a56df5ee4189f28814440c6c25198ee5d0774524d1099dde8facf9f89` |
| Round-72 positive tests | `code/test_stageb_v5_design_resolution.py` | `702c2bcd1e46191b30b8c8a4e723a1c4d84b6807db6f091e90fae64b62f1f334` |
| Round-73 independent tests | `code/test_stageb_v5_design_round73.py` | `7d33e29f612d160e21e240169e7379ce91a78e0f8ff7bc6aff4298dc9b78d4ef` |

Every hash listed inside v5, v4, and v3 was independently rehashed and matched
the current repository bytes.  No stale or missing inherited object was found.

## 2. Executive decision

The Round-70 P0 bypass is closed.  The v5 floor branch requires the maximum of
**both** adjacent outward discrepancy bounds to be no larger than the exact
binary64 floor.  Otherwise the fine discrepancy upper bound must be strictly
smaller than the coarse separation lower bound.  The original
`0.300,0.300,0.304` counterexample is rejected by the complete v5 Boolean.

The Round-70 P1 selector ambiguity is also closed at design level.  V5 fixes
the source join, record fields, rank, neighboring nodes, exact secant operands,
orientation scalar and zero HOLD, normal, both `ell` vectors, comparison-node
displacement, eligibility operations, side labels, complete pair rank,
duplicate/tie behavior, directed arithmetic, and both role-ball checks.  Two
implementations that obey the printed operation trace cannot choose different
controls by selecting a different base, tangent, orientation, norm order, or
rounding endpoint.

One evidence-level weakness was found in the Round-72 positive test: its
`discrepancy_upper` and `distance_lower` helpers use native binary64
round-to-nearest subtraction rather than the v5 exact-real `up64`/`down64`
definitions.  A proper point-interval fixture exactly at a binary64 midpoint
therefore passes the Round-72 helper's floor branch but is correctly rejected
by the normative v5 gate.  This does **not** invalidate v5; it shows that the
Round-72 helper is not itself the future production Boolean.  The new
independent Round-73 test closes this evidence gap using exact rational leaves
and directed binary64 endpoints, and the future T0 package remains required to
carry the same mutation.

The open design ledger is therefore:

```text
open P0 = 0
open P1 = 0
open P2 = 0

closed evidence-only observation = 1

design verdict    = ACCEPT-DESIGN
execution verdict = HOLD-EXECUTION
science status    = NOT RUN / NOT INSPECTED

AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

`ACCEPT-DESIGN` authorizes only construction and independent attack of the
science-free v5 T0 selector package.  It is not `GO-FV-STAGE-B`, does not
authorize Stage-A substitution, and cannot promote a manuscript claim.

## 3. Independent replay of the Round-70 odd-grid P0

### 3.1 Original finite bypass

For the Round-70 point intervals

```text
O113 = [0.300,0.300]
O129 = [0.300,0.300]
O161 = [0.304,0.304]
```

the v5 quantities are

```text
D_coarse_plus  = 0
D_fine_plus    > 0.003999999999999...
D_coarse_minus = 0.
```

The maximum adjacent upper discrepancy exceeds `ODD_FLOOR`; the strict branch
also fails because a positive fine upper discrepancy is not below zero.  The
complete Boolean returns false.  The independent test calls the complete gate,
not merely the strict-contraction sub-expression.

The two positive controls also behave as intended:

```text
O113=O129=O161                    -> both-at-floor branch passes
0.0 -> 0.4 -> 0.5 point intervals -> strict-contraction branch passes.
```

### 3.2 New half-ulp attack on RN-versus-outward evaluation

Let

```text
F = ODD_FLOOR = 0x1.ad7f29abcaf48p-25
x = F/2
y = nextUp(x).
```

The exact real sum satisfies

```text
x+y = (F+nextUp(F))/2.
```

Because `F` has the even significand at this tie, ordinary RN maps `x+y` back
to `F`, whereas the required outward upper endpoint is `nextUp(F)`.  Use the
proper point intervals

```text
O113=[ x, x]
O129=[-y,-y]
O161=[ x, x].
```

Then a native-RN helper reports both adjacent differences as `F` and accepts
the floor branch.  The v5 operation reports both `Dplus` values as
`nextUp(F)`.  Its coarse `Dminus` is at most `F`, so neither branch passes.
This is an exact one-bit distinction, not a tolerance argument.

This fixture confirms two things:

1. the v5 mathematical definition is fail-closed at the directed boundary;
2. the future T0 implementation/tests must not reuse the Round-72 native-RN
   helper as the exported production gate.

### 3.3 Vector, odd/even, and full-matrix coverage

The vector rule first takes coordinatewise outward `Dplus`/`Dminus` and then
the fixed `L_inf` maximum.  A two-coordinate fixture with one constant
coordinate and one Round-70 coordinate is rejected; a quiet coordinate cannot
hide a bad one.

The contraction decision uses all three declared odd grids in the fixed order
`O113 -> O129 -> O161`.  V5 separately retains all-eight-grid `E_FV`, absolute
caps, identical topology on the three odd grids, frozen-role topology on every
other required grid, and the parity, separate-box, combined-box, and
`MR+--MR+F` diagnostics.  A producer cannot switch to an even-only comparison,
drop one odd level, select a favorable coordinate, or replace the floor after
seeing a row.

No scalar/vector, odd/even, or three-grid bypass survived.

## 4. Independent replay of the Round-70 T0-selector P1

### 4.1 Source identity and comparison-node rank

The v5 selector requires exactly one same-index, byte-consistent object in
generation, mesh 65, and mesh 97.  Missing records, within-collection
duplicates, cross-record byte disagreement, and distinct indices with
identical physical-control bytes are HOLD.  Both evaluated rows must already
pass their frozen gates and saved topology.

Only comparison records whose target bytes equal the exact `TARGET` survive.
The complete rank is

```text
(abs(RN(realized_signed_offset-TARGET)),
 abs(normalized_fold_residual),
 acceptance_index).
```

Repeated acceptance indices and duplicate full ranks are HOLD.  The chosen
index must identify exactly one node with immediate predecessor and successor
in the saved ordered node array.  Thus record ties or array ambiguity cannot
fall through to a later favorable object.

### 4.2 Secant, orientation, displacement, and scale

The formerly prose-only choices are now an exact operation trace:

```text
c = RN(theta_n-theta_p) coordinatewise
dt = RN(t_n-t_p)
omega = RN(float64(sigma)*dt)
```

Zero `omega` is HOLD.  Negative `omega` negates both secant coordinates before
the fixed multiply/multiply/add/sqrt/divide normalization.  The normal is the
fixed rotation `(-u1,u0)`.  Neither a one-sided tangent nor a dot-product
orientation surrogate remains admissible.

The two `ell` operands are exactly `theta_b-theta_p` and
`theta_n-theta_b`.  Candidate displacement is exactly `theta_i-theta_b`.
Eligibility, side signs, and all five pair-rank fields have fixed RN operation
order.  Pair-rank ties, repeated objects/indices, and cross-branch collisions
are HOLD without trying a later pair.  The two count pairs must be exactly
`{(1,2),(2,3)}` and cannot be relabeled after selection.

Reversing the central subtraction, omitting the orientation flip, accepting a
zero orientation, using a predecessor/successor/fold/cusp/origin displacement,
using the long secant as `ell`, changing an eligibility boundary, or choosing a
later pair is therefore a literal contract violation rather than an alternate
implementation.

### 4.3 Tie, nonfinite, signed-zero, and subnormal boundaries

V5 rejects every nonfinite input and intermediate, disables FMA and extended
intermediates, preserves subnormals, and canonicalizes negative zero only
after the directed inequality needed to choose an endpoint.  The independent
test verified the exact subnormal enclosure

```text
down64(+minsub/2) = +0
up64(+minsub/2)   = +minsub
down64(-minsub/2) = -minsub
up64(-minsub/2)   = +0.
```

It also verifies that `NaN`, `+Inf`, and `-Inf` enter HOLD and that the zero
returned after the negative-half endpoint decision has a positive sign bit.
Rank values are finite, zeros are canonical, finite floats use lowercase
`float.hex()`, and integer indices remain separate unsigned fields.  No
signed-zero or total-order tie can change the selected logical object.

## 5. Directed arithmetic and role radii

V5 defines `down64` and `up64` as mathematical greatest-lower and
least-upper finite binary64 endpoints of an exact real expression.  A printed
expression inside one directed operator is not pre-rounded to nearest; an
inner `RN`, `down64`, or `up64` is an explicit binary64 leaf.  Algebraic
expressions therefore have a unique rational interpretation.

The pinned future MPFR kernel is only an implementation vehicle for `sqrt`,
`log`, and `exp`.  Precision must increase until the unique endpoint is
certified; exact square/midpoint comparisons and the exact `log(1)`/`exp(0)`
cases close equality termination.  Host `libm` cannot decide a selector,
radius, interval, or sample-size boundary.

For the seven saved role seeds, every global-box face distance and every
pairwise coordinate distance is rounded downward before the radius is formed:

```text
rho_i = down64(min(RHO_CAP,b_i/4,s_i/4)).
```

All `b_i`, `s_i`, and `rho_i` must be finite and positive.  The implementation
must then separately prove strict containment of all six faces and

```text
up64(rho_i+rho_j) < down64(d_exact(z_i,z_j))
```

for every pair.  The independent seven-seed fixture reconstructs the literal
formula and passes both properties.  The quarter factors also leave strict
mathematical slack; the outward post-check, rather than an assumed slack,
remains the acceptance decision.

No RN alias, up/down reversal, touching-ball, signed-zero, subnormal, or
nonfinite bypass survived.

## 6. Hash, cross-reference, attestation, and authorization audit

### 6.1 Hash-closed normative import

The complete v5, v4, and v3 hash chains were rehashed through every listed
design/audit/test dependency.  All current bytes match their frozen hashes.

V5 supplies an exhaustive four-item replacement map:

1. v4 T0 selector filenames become the v5 filenames;
2. v4 Section 4 becomes v5 Sections 3--5;
3. v4 Section 8.2 becomes v5 Section 6; and
4. v4 Section 15's ledger becomes v5 Section 11.

It explicitly remaps the surviving references to v4 Section 4, Section 4.1,
and the Section-4.4 role ball, and forbids resolving a reference back into the
superseded bytes.  The complete interval hull, implicit certificate, caps,
fixed-control estimands, inference, seed, resource, and no-cycle clauses remain
normative without reinterpretation.

### 6.2 Freeze and attestation graph

The future v5 T0 source/tests/protocol must be written, hashed, independently
attacked, and externally recorded before any Stage-A value is read.  They must
pin both the v5 and imported-v4 hashes.  At this audit snapshot those three
future package files do not exist, so the correct state remains
`HOLD-EXECUTION`; absence is not a design failure and was deliberately not
made a permanent regression-test assertion.

The downstream graphs retain the correct no-back-edge direction:

```text
M_B hash -> independent A_B
(M_B,A_B,A_B-tests) -> external no-cycle protocol

M_MC hash -> independent A_MC
(M_MC,A_MC,A_MC-tests) -> external no-cycle protocol.
```

Neither scientific manifest pins its future auditor or external protocol.
The external T0 record and later upstream hash closure must record the actual
v5/T0/test/audit bytes, including this independent acceptance and the half-ulp
mutation, before any scientific boundary is opened.  A stale report, changed
test, missing hash, symlink substitution, duplicate-key object, or post-freeze
drift is HOLD under the inherited provenance clauses.

### 6.3 Authorization

The design contains `AUTHORIZED-SCIENTIFIC-COMMAND: NONE` at both its header
and decision boundary.  It explicitly forbids Stage-A substitution, Stage-B
FV production, off-lattice production, scientific-manifest mutation, and
manuscript claim promotion.  This Round-73 acceptance does not change that
authorization string.

No stale-hash, cross-reference, cycle, or authorization bypass was found.

## 7. Non-regression of inherited scientific and statistical boundaries

The independent pass confirmed that the following v4 closures remain
normative and were not lost in the v5 patch:

- complete scalar/vector/401-time interval hulls, including the reference
  self-term and both endpoint errors;
- the six-variable joint cusp--fold system, residual-checked inverse and
  correction, Newton--Kantorovich/Krawczyk inclusion, root-box projections,
  direct-evaluation errors, role-ball containment, and branch/order gates;
- all eight absolute caps and the all-grid quarter-margin rule;
- the four-control off-lattice scope, nine basins, fourteen windows, ten
  positive local contrasts, and empty `m=1` contrast array;
- same-generator pool regression wording without equivalence promotion;
- the unchanged v4 counter domain, seed material, exact IDs, and no clipping;
  and
- the maximum claim remaining a finite-volume numerical cusp plus
  finite-resolution event-law validation, not a continuum/PDE/global-mode or
  off-lattice-cusp result.

The independent arithmetic recomputation gives:

```text
sum of eight state counts                  = 26,333,190
logical rows                               = 15*8 = 120
base-state cells per complete pass         = 394,997,850
two nominal passes                         = 789,995,700
alpha                                      = 1/20
power primitives                           = 62
universal thinning rate                    < 0.35.
```

No inherited claim, matrix, alpha, power, pool, rate, or seed regression was
found.

## 8. Adversarial decision table

| attack | independent result | decision |
|---|---|---|
| v4 coarse-floor/fine-jump OR bypass | exact v5 gate rejects | closed |
| both adjacent differences at floor | passes only when both outward bounds are at floor | intended |
| strict contraction | fine `Dplus` must be below coarse `Dminus` | intended |
| half-ulp RN alias at `ODD_FLOOR` | native helper accepts; exact v5 gate rejects | design closed; Round-73 test added |
| one bad vector coordinate | `L_inf` aggregate rejects | closed |
| omit/swap one odd level | fixed three-grid schema forbids | HOLD |
| even/parity/topology drift | all-grid envelope/topology/diagnostics remain mandatory | HOLD |
| predecessor/successor/fold/cusp/origin displacement | exact `theta_i-theta_b` contract forbids | HOLD |
| reverse secant/omit orientation flip/zero `omega` | fixed operation trace or zero HOLD | HOLD |
| long or one-sided `ell` | exact two local vectors forbid | HOLD |
| comparison/pair rank tie | duplicate full rank is HOLD | HOLD |
| duplicate index/object or cross-branch reuse | no later-pair fallback | HOLD |
| RN substituted for directed endpoint | half-ulp and rational adjacency tests reject | HOLD |
| signed zero/subnormal | canonicalization and exact enclosure are fixed | closed/HOLD as specified |
| `NaN`/infinity/nonfinite intermediate | global fail-closed rule | HOLD |
| role ball touches a face or another ball | strict outward checks reject | HOLD |
| stale v4/v5 bytes or dangling old Section 4 | hash/replacement map rejects | HOLD-T0 |
| missing/unaudited future T0 package | package absent at this snapshot | HOLD-EXECUTION |
| scientific command or claim promotion now | authorization remains `NONE` | forbidden |

The design-level decision table is complete enough to construct the future T0
package.  Presence-only tests will not suffice: the package must execute every
v5 Section-10 mutation and the independent half-ulp fixture above against its
actual exported Boolean and selector.

## 9. Executable evidence

The new independent test is science-free.  It uses frozen text/hashes, exact
`Fraction` leaves, binary64 adjacency, finite hand fixtures, and exact
integer/rational/decimal arithmetic.  It imports no scientific producer.

```text
python -m ruff check code/test_stageb_v5_design_round73.py
  All checks passed

python -m pytest -q code/test_stageb_v5_design_round73.py
  10 passed

python -m pytest -q \
  code/test_stageb_v3_design_round67.py \
  code/test_stageb_v4_design_resolution.py \
  code/test_stageb_v4_design_round70.py \
  code/test_stageb_v5_design_resolution.py \
  code/test_stageb_v5_design_round73.py
  33 passed

python -m py_compile code/test_stageb_v5_design_round73.py
  PASS
```

Ruff also passes jointly on the Round-69, Round-70, Round-72, and Round-73
tests.  The historical Round-67 test retains its already-recorded pre-existing
import-order lint only; its four executable checks pass unchanged, and its
frozen hash was not altered.

## 10. Final boundary and next permitted action

```text
P0 = 0
P1 = 0
P2 = 0

ACCEPT-DESIGN
HOLD-EXECUTION
NOT RUN / NOT INSPECTED

AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

The next permitted step is only to construct the three named v5 T0
selector/test/protocol files without reading Stage-A values, pin v5 and v4,
implement the exact outward half-ulp behavior, execute every Section-10
mutation, and subject those actual bytes to another independent pre-run
attack.  No Stage-A, Stage-B, off-lattice, manifest-promotion, or manuscript
claim action is authorized by this report.
