# Round 47: result-blind allocation-cusp discovery freeze attack

Date: 2026-07-14  
Role: independent pre-execution attack on the mesh-65/97 Stage-A freeze  
Verdict: **PASS-FREEZE / HOLD-SCIENCE**

## 1. Scope and execution boundary

This round attacks the new fixed-`B` allocation-cusp discovery package before
any scientific Stage-A execution.  It reviewed the protocol, exact manifest,
formal runner, tests, small explicit-CSR dry run, output transaction, and claim
flags.

No mesh 65 or 97 allocation-cusp calculation was run.  No cusp, fold, remote
pair, phase-control, or representative result was read or produced.  Both
formal output paths and both hidden replica paths were absent after the audit.
The correct scientific status therefore remains HOLD.

The separately frozen positive-`B` four-slab v2 chain was neither imported by
the new runner nor edited.  Its hashes remained:

| frozen-v2 role | SHA-256 |
|---|---|
| producer | `adb9434daeccca721ab9c1014f194e0cf9c5c6d0bf092d31e050c040b4b94da8` |
| tests | `d60e837c949333d29f7287b17c5e24c6db742067a655bac5050b5966dc821329` |
| protocol | `f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00` |
| manifest | `955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c` |

## 2. Frozen package

| role | SHA-256 |
|---|---|
| discovery manifest / external anchor | `9863c2d08fecad4c56c52d9b4bf6978c18614e150269149bc0a2cce141981e58` |
| formal discovery runner | `9825d35e0a116ff0bcf83abcaba5d4f237e0e4d7875b64ceb87ccd2806fee0b2` |
| focused tests | `7285d9d1ccaf58cc43174bec48860085f5bc441e23449eeb67fe3be22361b217` |
| discovery protocol | `40ac57ca84f1d37010f12f75b7cd0d4c02ac5e35133f23ccf202f9eb7733033b` |

The manifest validates 13 unique report-relative regular-file pins.  It does
not pin this audit, avoiding a circular self-hash.

## 3. Severity convention and final count

- **P0:** can make a reported cusp/fold/phase result false, result-informed, or
  mathematically misoriented.
- **P1:** permits search leakage, non-fail-closed execution, nonreproducible
  selection, partial publication, or an invalid confirmation claim.
- **P2:** provenance, schema, or test weakness that does not alone reverse the
  scientific result.

Final open count for the freeze package:

```text
P0 = 0
P1 = 0
P2 = 0
```

This count applies to the pre-execution design and implementation.  It is not
a PASS-DISCOVERY result.

## 4. P0 attacks

### 4.1 Result-informed allocation plane

**Attack.**  Positive-`B` values could be used to rotate the allocation chart
onto a favorable pair of directions.

**Resolution.**  The manifest fixes the chart from the already disclosed
`B=0` full-simplex response only.  It pins all digits of `w_c^(0)` and `P`, the
Euclidean metric, decreasing-singular-value order, and largest-component sign
rule.  Tests enforce `1^T P=0`, `P^T P=I`, and unit-sum reference weights.
**Closed.**

### 4.2 Wrong fixed-budget tangent or missing direct observable term

**Attack.**  Reusing a total-budget tangent, reversing the row/column sign, or
evaluating only `kappa^T s_i` can give plausible but false projected rank.

**Resolution.**  The runner independently implements

\[
s_{i,t}=Q^Ts_i-BD_{u_i}p,
\qquad
F^{(r)}_{\theta_i}=s_i^Ta_r+p^Tb_{r,i}.
\]

The five-cell test compares both state tangents and observable jets through
order three with separately propagated centred allocation differences.  The
seven-cell dry run compares all four base/augmented row/column actions with an
explicit CSR construction; its maximum error was
`2.220446049250313e-16`.  **Closed.**

### 4.3 Incomplete cusp Jacobian or raw-units rank

**Attack.**  A solver could omit `F_tttt` or `F_ttt,theta`, or certify rank
using quantities that merely shrink with `B`.

**Resolution.**  The frozen map is exactly `H=(F_t,F_tt,F_ttt)` and the analytic
three-by-three Jacobian includes the fourth time jet and both third-order mixed
jets.  All residual, quartic, projected-response, full-Jacobian, and determinant
gates are dimensionless.  The two-step finite-difference audit covers every
Jacobian entry.  **Closed.**

### 4.4 One fold, wrong fold sign, or lost remote structure

**Attack.**  Both nominal predictors could enter the same half-branch, or a
local cusp pair could be mistaken for a three-mode structure after the remote
pair disappears.

**Resolution.**  The two predictor equations and offsets `-0.10,+0.10` are
literal manifest values.  Fixed-time correction precedes oriented
pseudo-arclength continuation.  Both halves must reach the frozen distance and
node count.  The finite stationary-root procedure must find a remote simple
max--min pair at the cusp and again at all six signed comparison nodes.  The
normal-form discriminant is not used as a root-count substitute.  **Closed as
a frozen test.**

### 4.5 Silent nonfinite structural result

**Attack.**  An absent root set originally risks producing an infinite
robustness score; rank or branch failure could likewise leak `NaN` into a
seemingly complete JSON object.

**Resolution.**  The final implementation uses `null` for unavailable
structures and a finite negative score sentinel only for internal bounded
ranking.  Recursive finite-JSON validation precedes replica acceptance.
Structural mesh rows and `NOT_RUN_AFTER_HOLD` rows have fixed keys.  **Closed.**

## 5. P1 attacks

### 5.1 Unbounded candidate or root search

**Attack.**  Additional radii, directions, time ranges, or mesh-specific
controls could guarantee a selected-looking phase diagram.

**Resolution.**  The manifest fixes exactly 32 controls from four radii and
eight printed directions around the mesh-97 cusp.  All eligible controls are
screened on mesh 65; at most three per retained maximum count advance to mesh
97.  Ranking uses the frozen signed normalized score and lexicographic physical
weights.  The common physical controls are never retuned.  Root isolation is
limited to `[0.5,35]`, spacing `0.05`, sign-changing brackets, fixed Brent
tolerances, density/curvature/residual filters, and `0.25` root separation.
Search expansion after HOLD is forbidden.  **Closed.**

### 5.2 Tight thresholds used as a pre-screen to avoid unfavorable mesh 97

**Attack.**  Requiring every mesh-65 scientific margin before advancing could
silently shrink the declared top-three search and depart from the Round-36
ranking rule.

**Resolution.**  The final runner advances controls by retained topology,
endpoint signs, and frozen score, even when a score is negative.  A
representative passes only when the same physical control passes both meshes.
Thus unfavorable low-mesh margins remain visible rather than preventing the
predeclared mesh-97 evaluation.  **Closed.**

### 5.3 Mesh 97 evaluated after an earlier structural HOLD

**Attack.**  Building both scientific models up front could consume mesh-97
information even when the declared failure contract says the later row was not
run.

**Resolution.**  Each formal replica first performs the seven-cell CSR
preflight, then builds and runs mesh 65.  Mesh 97 is built only after mesh 65
passes.  The focused mock test observes exactly `(7,dry)` then `(65,formal)`
and no mesh-97 construction after an injected mesh-65 HOLD.  **Closed.**

### 5.4 Manifest substitution and time-of-check/time-of-use drift

**Attack.**  A caller could supply a newly hashed manifest with widened trust
boxes or mutate a pinned file during a replica.

**Resolution.**  The runner contains an exact manifest contract in addition
to the external SHA-256 requirement.  It validates every pin, rechecks the
manifest before/after each replica and before promotion, and rejects path
escape, duplicate paths, changed fields, changed pin roles, or changed hashes.
Mutation tests cover a phase-radius change and a runner-pin change.  **Closed.**

### 5.5 Nondeterministic or partial canonical publication

**Attack.**  One favorable process, thread-dependent BLAS, a partial JSON file,
or an evidence/result split could become canonical.

**Resolution.**  Formal execution requires two complete sequential subprocess
replicas with fixed one-thread environment variables, `PYTHONHASHSEED=0`, and
a pinned/restored NumPy seed.  Status, exit code, manifest citation, canonical
JSON, and byte identity must agree.  Result and evidence are staged, file- and
directory-synced, then replaced; any injected post-replace sync failure removes
both destinations.  Existing outputs are append-only.  Tests cover HOLD
promotion, mismatched replicas, wrong external hash, overwrite rejection, and
rollback.  **Closed.**

### 5.6 Discovery mislabeled confirmation

**Attack.**  Two low odd meshes in one box could be described as convergence
or a continuum cusp.

**Resolution.**  The only successful status is
`PASS_DISCOVERY_LOW_MESH_ONLY`.  Held-out mesh, parity, box, continuum,
unbounded-domain, independent-solver, and publication flags are hard-coded
false and copied into every dry-run/formal result.  Forbidden wording is also
serialized.  **Closed.**

## 6. P2 attacks

1. The protocol initially did not state that the remote pair is rerun at every
   fold comparison node.  The final protocol and manifest now say so.
   **Closed.**
2. The initial root packaging did not apply the frozen `0.25` neighbor
   separation to every reported eligible root.  Both neighbors are now checked
   before topology is formed.  **Closed.**
3. The representative gates initially omitted sampled-state negativity and
   sampled-survival monotonicity despite freezing their tolerances.  Both are
   now explicit Boolean gates.  **Closed.**
4. The comparison-node implementation initially selected only nodes already
   beyond each target offset.  It now minimizes the signed-offset mismatch over
   the branch and then applies the frozen residual/index tie-break.  **Closed.**

## 7. Executed checks

```text
python -m ruff format --check <runner> <tests>
2 files already formatted

python -m ruff check <runner> <tests>
All checks passed!

python -m py_compile <runner> <tests>
passed

python -m pytest -q <focused tests>
........... [100%]

python <runner> --algebra-dry-run --cells 7 \
  --expected-manifest-sha256 9863c2d08fecad4c56c52d9b4bf6978c18614e150269149bc0a2cce141981e58
status = PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE
scientific_meshes_executed = []
maximum explicit-CSR action error = 2.220446049250313e-16
```

The final manifest validation reported 13 valid pins.  A filesystem check
reported no canonical result, no reproducibility evidence, and no hidden
replica file.

## 8. Authorization boundary

Round 47 freezes a reproducible, result-blind Stage-A experiment.  It does not
authorize any statement that the positive-`B` allocation cusp exists.  The
formal run must use the external manifest hash printed above and must preserve
either PASS or HOLD without tuning.

If formal Stage A passes, its exact result and reproducibility hashes—not a
manually copied representative—must be frozen into a new Stage-B manifest
before meshes 113/128/129/161, parity, or box calculations.  If it holds, the
finite search may not expand under this protocol.
