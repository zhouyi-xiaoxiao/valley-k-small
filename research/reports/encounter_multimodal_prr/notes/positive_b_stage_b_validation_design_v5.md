# Positive-`B` Stage-B validation design v5

Date: 2026-07-14  
Status: **GO-DESIGN / HOLD-EXECUTION**  
Authorization: **AUTHORIZED-SCIENTIFIC-COMMAND: NONE**

## 0. Purpose, normative construction, and non-execution boundary

This is a new result-blind design version.  It repairs the two findings in the
independent Round-70 attack without opening or changing any scientific object.
It does not overwrite v4.

The design inputs are:

| role | repository path | SHA-256 |
|---|---|---|
| attacked Stage-B v4 design | `notes/positive_b_stage_b_validation_design_v4.md` | `e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691` |
| Round-69 v4 resolution | `audits/round_69_stageb_v4_design_resolution.md` | `7972335d11cb55337c248a39967173d548d711dad937bf9dbdfefd9d29f2ef27` |
| Round-69 positive regressions | `code/test_stageb_v4_design_resolution.py` | `b882aaa1737847dd58606140466b9c03572211767ea9ad4c208d7cdb69c20fb2` |
| independent Round-70 attack | `audits/round_70_stageb_v4_independent_attack.md` | `0fa94a3d94db356e81f62746f267743bbc3f431dc82959894d00b88a9bea9c62` |
| Round-70 science-free checks | `code/test_stageb_v4_design_round70.py` | `bf91141021375fd583fc1e85a75c6c931fd966637ad628c8b5bd84b632262d20` |
| independent Round-67 attack | `audits/round_67_stageb_v3_independent_attack.md` | `4f71f9e517ce5d3ca44e403332fb52be37d070e7e546db284cbbed83bf4d6c35` |

V5 is deliberately a **hash-closed normative repair**.  The complete byte
snapshot of v4 at the hash above remains normative verbatim, except for the
following replacements:

1. v4 Section 3's T0 selector filenames are replaced by the v5 filenames in
   Section 2 below;
2. v4 Section 4 is replaced in full by Sections 3--5 below;
3. v4 Section 8.2 is replaced in full by Section 6 below; and
4. v4 Section 15's current design ledger is replaced by Section 11 below.

All other v4 clauses, equations, constants, claim limits, HOLD semantics, row
requirements, alpha/power contracts, seed bytes, pin graphs, and provenance
rules remain normative without reinterpretation.  If a replacement clause and
v4 conflict, the replacement clause controls.  If an implementation cannot
read and hash both this file and the pinned v4 snapshot, it is `HOLD-T0`.

Imported cross-references are mechanically remapped: v4's “Section 4 exactly”
means v5 Sections 3--5, v4's `Section-4.1` means v5 Section 3, and v4's
`Section-4.4 role ball` means the v5 Section-5 role ball.  No imported clause
may resolve a reference back into the superseded v4 Section 4.

No canonical Stage-A result, hidden scientific value, mesh-65/97 model,
Stage-B FV row, cusp/fold solve, off-lattice path, scientific producer,
scientific auditor, manifest, or main entry point was run or inspected while
making this design.  No science is authorized by this document.

## 1. Frozen scope and unchanged maximum claim

The maximum possible claim remains exactly the v4 finite-resolution claim:

> a mesh-, alignment-, and box-stable finite-volume numerical allocation
> cusp, with predeclared finite-resolution event-law features at unchanged
> physical controls independently preserved by the unbounded off-lattice Doi
> process.

In particular, the off-lattice calculation does not locate a cusp or fold,
prove a continuum/PDE cusp, prove a global exact mode count, or prove absence
of a local pair on the one-mode representative.  The following flags remain
false:

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

The eight fixed physical controls, seven grid-specific implicit roles, eight
FV configurations, 120-row matrix, and four-control MC subset are unchanged.

## 2. One-way freeze ladder and v5 T0 package

Before any Stage-A value is read, the following science-free package must be
written, hashed, independently attacked, and recorded by an external protocol:

```text
code/positive_b_stage_b_t1_selector_v5.py
code/test_positive_b_stage_b_t1_selector_v5.py
notes/positive_b_stage_b_t1_selector_protocol_v5.md
```

The package must pin both the v5 hash and the imported v4 hash.  Its source
implements Sections 3--5 literally and its mutation tests cover every fixture
in Section 10.  Neither an implementation choice nor a rounding convention may
be supplied after Stage-A values are visible.

The rest of the v4 freeze ladder is unchanged:

```text
T0 selector code/tests/protocol, frozen before Stage-A read
  -> audited Stage-A object
  -> canonical T1 object/audit
  -> Stage-B scientific manifest M_B
  -> scientific result/evidence

M_B hash -> independent A_B
(M_B,A_B,A_B-tests) -> external no-cycle protocol
```

and, after an audited Stage-B result,

```text
audited Stage-B object
  -> canonical T2 object/audit
  -> MC scientific manifest M_MC
  -> scientific result/evidence

M_MC hash -> independent A_MC
(M_MC,A_MC,A_MC-tests) -> external no-cycle protocol.
```

`M_B` and `M_MC` never pin their respective auditors or external protocols.
No T1 selector may evaluate a new mesh-65/97 object.

## 3. Exact binary64 and directed-rounding vocabulary

### 3.1 Values, operations, and serialization

Every input named in Sections 3--5 is an exact IEEE-754 binary64 datum.  The
environment preserves subnormals, disables flush-to-zero and
denormals-are-zero, sets `FP_CONTRACT=OFF`, forbids FMA, forbids extended
intermediates, and uses round-to-nearest/ties-to-even.

For a finite exact real number `x`, define

```text
RN(x) = the unique IEEE-754 binary64 round-to-nearest/ties-to-even value.
```

Every displayed `RN(op(...))` first evaluates the arguments already shown as
binary64 values, then evaluates the one indicated operation as an exact real
operation, then applies `RN`.  There is no reassociation.  Unary negation and
`abs` are exact sign-bit operations.  A negative zero produced anywhere is
canonicalized to positive zero before comparison, ranking, or serialization.
Any nonfinite input or nonfinite intermediate is HOLD.

The constants used by the selector/radius/gate are the exact binary64 values:

```text
TARGET = 0x1.8000000000000p-1       # 0.75
THETA_BOUND = 0x1.3333333333333p-3  # binary64 0.15
TIME_SCALE = 0x1.1400000000000p+5  # 34.5
RHO_CAP = 0x1.0000000000000p-7     # 1/128
ODD_FLOOR = 0x1.ad7f29abcaf48p-25  # binary64 5e-8
```

Finite values serialize with Python-compatible lowercase `float.hex()` after
zero canonicalization.  Structured objects use duplicate-key-rejecting
canonical JSON.  Candidate and acceptance indices are unsigned integers.
Rank tuples compare finite binary64 fields by IEEE `totalOrder` and indices by
unsigned integer order.  The last index field is a deterministic tie-break;
duplicate logical objects or repeated indices are HOLD rather than ties.

### 3.2 Exact definitions of `down64` and `up64`

Let `B_f` be the finite binary64 numbers interpreted as exact reals.  For a
finite exact real `x` lying within the finite binary64 enclosure domain,

```text
down64(x) = max {b in B_f : b <= x},
up64(x)   = min {b in B_f : b >= x}.
```

If either set is empty or the required endpoint is nonfinite, the operation is
HOLD.  Equivalently, with `y=RN(x)` and an exact comparison between the real
values of `x` and `y`,

```text
down64(x) = y                 if real(y) <= x
            nextDown(y)       otherwise,

up64(x)   = y                 if real(y) >= x
            nextUp(y)         otherwise.
```

`nextDown` and `nextUp` are the immediately adjacent finite binary64 values in
numeric order.  Zero is canonicalized only after the inequality has been
established.

An expression inside a single `down64(E)` or `up64(E)` is evaluated as the
exact real syntax tree printed in `E`, with binary64 leaves interpreted
exactly.  It is **not** first rounded to nearest.  A nested `RN(...)`,
`down64(...)`, or `up64(...)` explicitly creates a binary64 leaf for the outer
expression.  This rule separates the RN selector from outward certificates
and removes any compiler-dependent intermediate convention.

The executable implementation uses integer/rational arithmetic for algebraic
expressions and an MPFR interval kernel for `sqrt`, `log`, and `exp`.  MPFR is
an implementation vehicle, not the definition: precision is doubled until a
certified interval identifies the unique RN result or the unique directed
endpoint.  The MPFR version, compiler, flags, rounding modes, and conformance
fixtures are pinned in the T0 package.  Host `libm` is forbidden for these
decisions.  Correctly rounded operations mean

```text
sqrtRN(x) = RN(sqrt(real(x)))
logRN(x)  = RN(log(real(x)))
expRN(x)  = RN(exp(real(x)))
```

with the corresponding exact-real `down64`/`up64` definitions for directed
endpoints.  Exact-boundary termination is not left to a tolerance: `sqrt`
uses an exact integer/rational square comparison against the candidate and RN
midpoint, while `log(1)=0` and `exp(0)=1` are handled as exact special cases.
For other valid algebraic inputs produced by the printed rational/binary
arithmetic, a nonzero algebraic binary64 boundary or midpoint cannot equal
`log(x)` or `exp(x)` (otherwise exponentiating a nonzero algebraic number
would be algebraic), so certified precision escalation separates the
boundary.  Invalid function domains are HOLD.

### 3.3 Exact two-vector primitives

For binary64 two-vectors, define in precisely this order:

```text
dot2RN(a,b):
  p0 = RN(a[0]*b[0])
  p1 = RN(a[1]*b[1])
  return RN(p0+p1)

norm2RN(a):
  p0 = RN(a[0]*a[0])
  p1 = RN(a[1]*a[1])
  ss = RN(p0+p1)
  return sqrtRN(ss)
```

No hypot substitution, FMA, compensated sum, or coordinate reordering is
permitted.  A zero or nonfinite normalization norm is HOLD.

## 4. Byte-unique T0 saved-object selector

### 4.1 Exact source join and comparison record

For candidate index `i`, require exactly one object in each canonical Stage-A
collection:

```text
candidate_generation
screened_mesh_65
advanced_mesh_97
```

The three records are an intentional cross-collection join.  They must have
the same index and byte-identical `theta` and weights.  Both evaluated rows
must be `EVALUATED`, pass every frozen control gate, and have identical saved
topology.  A duplicate within a collection, byte mismatch, missing record, or
two distinct indices with identical full physical-control bytes is HOLD.

For one saved branch let its orientation sign be the exact integer
`sigma in {-1,+1}`.  Each saved comparison record supplies exact fields

```text
target_offset, realized_signed_offset, normalized_fold_residual,
acceptance_index.
```

Keep only records whose `target_offset` bytes equal `TARGET`.  For each, form

```text
offset_error = abs(RN(realized_signed_offset - TARGET))
residual_key = abs(normalized_fold_residual)
record_rank = (offset_error, residual_key, acceptance_index).
```

Choose the first rank.  Repeated acceptance indices or duplicate full ranks
are HOLD.  Let `b` be the unique node at that acceptance index in the saved
ordered mesh-97 node array, and let `p` and `n` be the immediately preceding
and succeeding saved nodes.  Missing, duplicated, or non-adjacent nodes are
HOLD.  The exact node fields used below are
`(t_p,theta_p)`, `(t_b,theta_b)`, and `(t_n,theta_n)`.

### 4.2 Secant, orientation, normal, and scale

The central secant operands and subtraction order are:

```text
c0 = RN(theta_n[0] - theta_p[0])
c1 = RN(theta_n[1] - theta_p[1])
dt = RN(t_n - t_p)
omega = RN(float64(sigma) * dt)
```

If `omega==+0.0`, return HOLD.  If `omega<0`, replace
`c0=RN(-c0)` and `c1=RN(-c1)`; if `omega>0`, leave them unchanged.  Thus the
oriented secant points toward increasing `sigma*t`.  No dot-product surrogate,
one-sided secant, comparison-node tangent, or late sign convention is allowed.

Normalize and rotate in this exact order:

```text
c_norm = norm2RN((c0,c1))
u0 = RN(c0 / c_norm)
u1 = RN(c1 / c_norm)
n0 = RN(-u1)
n1 = u0
```

The two chart-distance operands are exactly:

```text
vp0 = RN(theta_b[0] - theta_p[0])
vp1 = RN(theta_b[1] - theta_p[1])
vn0 = RN(theta_n[0] - theta_b[0])
vn1 = RN(theta_n[1] - theta_b[1])
ell_previous = norm2RN((vp0,vp1))
ell_next = norm2RN((vn0,vn1))
ell = min(ell_previous,ell_next)
```

The minimum is by numeric value after zero canonicalization.  Equal values
produce that same value, not a branch-dependent choice.  Nonpositive `ell` is
HOLD.

### 4.3 Candidate displacement, eligibility, labels, and pair rank

For candidate `i`, the displacement base is the comparison node `b`, never the
fold, cusp, predecessor, successor, or origin:

```text
d0_i = RN(theta_i[0] - theta_b[0])
d1_i = RN(theta_i[1] - theta_b[1])
s_i = dot2RN((n0,n1),(d0_i,d1_i))
q_i = dot2RN((u0,u1),(d0_i,d1_i))
r_i = norm2RN((d0_i,d1_i))

two_ell = RN(0x1.0000000000000p+1 * ell)
half_ell = RN(ell / 0x1.0000000000000p+1)
sixteenth_ell = RN(ell / 0x1.0000000000000p+4)
```

Eligibility is the conjunction

```text
r_i > 0
r_i <= two_ell
abs(q_i) <= half_ell
abs(s_i) >= sixteenth_ell.
```

Enumerate all eligible distinct-index pairs with
`s_minus<0<s_plus` and saved retained-maximum counts differing by exactly one.
The minus/plus labels are determined only by the computed signs of `s`; they
are not supplied by collection order or candidate index.  For each pair form,
in this order,

```text
k1 = RN(max(r_minus,r_plus) / ell)
k2 = RN(abs(RN(s_minus+s_plus)) / ell)
k3n = RN(abs(q_minus) + abs(q_plus))
k3 = RN(k3n / ell)
k4 = min(index_minus,index_plus)
k5 = max(index_minus,index_plus)
pair_rank = (k1,k2,k3,k4,k5).
```

Choose the unique first rank.  Duplicate indices/objects/ranks are HOLD; do
not choose a later pair.  Repeat independently on the second branch.  A
cross-branch candidate collision is HOLD and cannot be repaired by choosing
the next pair.  The two unordered saved maximum-count pairs must be exactly
`{(1,2),(2,3)}`.  The resulting four branch-side labels and exact copied
control bytes are frozen at T1.  Interpolation, refit, optimization,
renormalization, and topology relabeling are forbidden.

## 5. Exact saved-field role radii

Let the seven saved seeds in ascending role-ID order be
`z_i=(t_i,theta_i0,theta_i1)`.  Their exact global box and metric remain

```text
9 <= t <= 18
abs(theta_0) <= THETA_BOUND
abs(theta_1) <= THETA_BOUND
d(z,z') = max(abs(t-t')/TIME_SCALE,
              abs(theta_0-theta'_0),abs(theta_1-theta'_1)).
```

This section uses lower directed bounds, not an RN approximation to a radius.
For each seed, evaluate the following exact-real expressions from binary64
leaves:

```text
bt_lo = down64((real(t_i)-real(9.0))/real(TIME_SCALE))
bt_hi = down64((real(18.0)-real(t_i))/real(TIME_SCALE))
b0 = down64(real(THETA_BOUND)-abs(real(theta_i0)))
b1 = down64(real(THETA_BOUND)-abs(real(theta_i1)))
b_i = min(bt_lo,bt_hi,b0,b1)
```

For every `j != i`, define

```text
dt_ij = down64(abs(real(t_i)-real(t_j))/real(TIME_SCALE))
d0_ij = down64(abs(real(theta_i0)-real(theta_j0)))
d1_ij = down64(abs(real(theta_i1)-real(theta_j1)))
dlo_ij = max(dt_ij,d0_ij,d1_ij)
s_i = min_{j != i} dlo_ij
rho_i = down64(min(real(RHO_CAP),
                   real(b_i)/4,
                   real(s_i)/4)).
```

All seven `b_i`, `s_i`, and `rho_i` must be finite and strictly positive.  The
implementation must then independently outward-check both properties:

```text
closed metric ball B(z_i,rho_i) is strictly inside the global box;
up64(real(rho_i)+real(rho_j)) < down64(d_exact(z_i,z_j))
for every i<j.
```

Here `d_exact` is the exact-real metric expression above.  The first check
outward-evaluates all six coordinate faces, including the time displacement
`TIME_SCALE*rho_i`.  Failure is `HOLD-T1`.  The certified implicit root box
must later lie strictly inside its role ball, and the v4
`E_FV,S <= rho_role/4` gate remains additional.

## 6. Corrected interval-certified odd-mesh gate

For scalar intervals `I_a=[L_a,U_a]`, retain the v4 definitions

```text
Dplus(I_a,I_b) = up64(max(abs(real(L_a)-real(U_b)),
                            abs(real(U_a)-real(L_b))))

Dminus(I_a,I_b) = down64(max(0,
                              real(L_a)-real(U_b),
                              real(L_b)-real(U_a))).
```

For each promoted scalar set

```text
D_coarse_plus = Dplus(I_O129,I_O113)
D_fine_plus   = Dplus(I_O161,I_O129)
D_coarse_minus = Dminus(I_O129,I_O113).
```

The exact production Boolean is

```text
odd_gate = (
    max(D_coarse_plus,D_fine_plus) <= ODD_FLOOR
    or
    D_fine_plus < D_coarse_minus
).
```

Thus the floor exception applies only when **both adjacent differences** are
at the floor.  The Round-70 fixture

```text
O113=[0.300,0.300]
O129=[0.300,0.300]
O161=[0.304,0.304]
reference=[0.302,0.302]
```

must return false even though its complete reference envelope is `0.002` and
passes the allocation-weight absolute cap `0.005`.  Any production
implementation whose exact exported Boolean accepts this fixture is rejected
at T0.

For a vector, first define each adjacent `Dplus_inf` as the maximum coordinate
`Dplus` and each `Dminus_inf` as the maximum coordinate `Dminus`; then apply
the identical Boolean to those three values.  Every scalar coordinate, weight
component, root time, jet, singular value/ratio, curvature, peak/valley ratio,
basin mass, final survival, and other promoted diagnostic is covered.

Topology must be identical on `O113`, `O129`, and `O161` and match the frozen
role on every other required grid.  Parity, separate-box, combined-box, and
`MR+--MR+F` diagnostics remain mandatory.  A failed Boolean is HOLD; it cannot
be repaired by selecting a subset, changing the floor, or inferring an order.

## 7. Explicit non-regression closure inherited from v4

The normative import preserves the following already-audited closures.  They
are restated here as a review checklist, not weakened alternatives.

### 7.1 Correct complete interval envelope

Every deterministic scalar uses

```text
I_g = [down64(qhat_g-r_g),up64(qhat_g+r_g)]
E_FV = up64(max_g max(abs(L_g-U_ref),abs(U_g-L_ref)))
C_FV = [down64(qhat_ref-E_FV),up64(qhat_ref+E_FV)].
```

This covers `abs(qhat_g-qhat_ref)+r_g+r_ref`; the reference self-term is
`2*r_ref`.  It applies coordinatewise to vectors and at all 401 points to
curves.  Every cap, margin, tolerance, MC containment, and power implication
uses this same envelope.  The v3 maximum of point difference and separate
errors remains forbidden.

### 7.2 Complete implicit certificate

Each fold certifies the six-variable joint system

```text
(F_cusp(z_C), f_t(z_F), f_tt(z_F), t_F-t_C-sigma*a) = 0
```

and retains `rho_inv`, `eps_J`, `gamma`, `K_up`, `rho_lin`, `eps_F`,
`eta_up`, `L_up`, and `r_NK`, plus an interval-Newton/Krawczyk unique-root
inclusion.  The joint cusp projection lies within the standalone cusp box;
all outputs are outward interval evaluations over the certified root box with
direct evaluation error added.  Role-ball containment, interval branch/order,
simplex, nonoverlap, and scaled `E_FV,S <= rho_role/4` gates remain mandatory.

### 7.3 Absolute caps

All eight v4 caps remain exact:

| quantity | `E_abs` |
|---|---:|
| root time | `0.05` |
| allocation weight `L_inf` | `0.005` |
| peak/valley ratio | `0.02` |
| event-basin mass | `0.001` |
| final survival | `0.01` |
| scaled fourth derivative | `0.50` |
| singular value or ratio | `0.01` |
| dimensionless curvature | `0.02` |

Thresholded quantities require all-eight-grid positive margin and
`E_FV <= min(E_abs,d/4)`; unthresholded coordinates require `E_abs` directly.
An unlisted diagnostic remains structural-only until a new result-blind design
assigns a cap.

## 8. Workload, alpha, power, pool, and rate invariants

The eight state counts still sum to `26,333,190`.  With eight fixed and seven
implicit roles, the design still requires

```text
15*8 = 120 logical role--configuration rows
15*26,333,190 = 394,997,850 base-state cells per complete row pass
2*394,997,850 = 789,995,700 base-state cells for two nominal passes.
```

No implicit role or failed row can be deduplicated or dropped.

The alpha ledger remains exactly

```text
12/1200 + 78/5200 + 84/5600 + 116/11600 = 1/20 = 0.05,
```

with 290 atoms/tails.  The power primitive count remains
`2*(4+9+4+14)=62`.  The four controls retain mode maxima `(3,1,2,3)`, nine
basins, fourteen windows, and ten positive local contrasts; the `m=1`
contrast array is empty.

Each MC pool must separately pass the common target.  Its difference interval
must contain zero and meet the fixed regression precision rule.  This remains
a same-generator regression diagnostic, **not statistical equivalence**.
Named `fv_acceptance.lower` and `fv_acceptance.upper` endpoints remain
mandatory.

The universal rate remains

```text
(0.01/0.04)*(1+2^-48)*exp(1/3)
  = 0.3489031062715236... < 0.35.
```

No hazard clipping is allowed.

## 9. Seed and provenance non-regression

To avoid silently changing a future random experiment, v5 intentionally
retains the exact v4 counter domain and master material:

```text
positive-b-stage-b-v4-off-lattice-sha256-counter-v1
positive-b-stage-b-v4-fixed-master-seed-v1
```

The block remains

```text
SHA256(domain || 0x00 || SHA256(master_material) || 0x00 ||
       T2_hash_bytes || H_c || p || u64be(i) || u64be(j)).
```

The T0/T1/T2/T3 no-cycle ordering, lexical no-symlink checks, immutable
snapshots, duplicate-key rejection, failure-atomic promotion, rollback,
post-promotion rehash, resource caps, disjoint pools, exact-ID retry, and
zero-alpha/zero-power replicate rules all remain normative.

## 10. Mandatory science-free mutation fixtures

Before any Stage-A read, the v5 selector tests must demonstrate all of:

1. the Round-70 `0.300,0.300,0.304` fixture fails the **complete** production
   odd Boolean, while a both-at-floor fixture and a strict-contraction fixture
   pass;
2. replacing `theta_i-theta_b` by displacement from `theta_p`, `theta_n`, a
   fold, a cusp, or zero changes the frozen fixture's selection or changes GO
   to HOLD, and every such mutation is rejected;
3. reversing `theta_n-theta_p`, omitting the `omega<0` flip, using a one-sided
   secant, or accepting `omega==0` changes the expected frame/labels or HOLD,
   and every mutation is rejected;
4. replacing either `ell` vector by a different base or swapping the written
   subtraction order changes a one-ulp boundary fixture and is rejected;
5. exact rational halfway/one-ulp fixtures prove
   `down64(x) <= x <= up64(x)`, adjacency where `x` is not representable, and
   a mutation using RN for a directed endpoint fails;
6. outward role-ball fixtures prove both global-box containment and all-pair
   disjointness, including a one-ulp mutation that fails one of them;
7. FMA-sensitive, signed-zero, subnormal, duplicate-index, duplicate-rank,
   nonfinite, comparison-record tie, and cross-branch collision fixtures fail
   closed; and
8. all historical Round-67, Round-69, and Round-70 science-free tests still
   pass unchanged.

These fixtures are part of the T0 mathematical contract.  Presence-only text
tests are insufficient for the selector package.

## 11. Current decision and execution boundary

The two Round-70 findings are closed at design level:

```text
open design P0 = 0
open design P1 = 0
open design P2 = 0

design status    = GO-DESIGN
execution status = HOLD-EXECUTION
science status   = NOT RUN / NOT INSPECTED

AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

`GO-DESIGN` licenses only independent attack of this v5 design and later
science-free construction/audit of the T0 selector package.  It does not
authorize Stage-A substitution, Stage-B FV production, off-lattice production,
manifest mutation, or manuscript claim promotion.  An independent v5 audit
must still confirm `P0=0,P1=0` before any next implementation boundary.
