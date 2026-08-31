# Round 44: fixed-budget allocation-cusp Stage-A code attack

Date: 2026-07-13  
Role: independent algebra, solver-interface, execution-boundary, and test attack  
Verdict: **PASS-ALGEBRA-SCAFFOLD / HOLD-SCIENCE**

## 1. Scope and final severity count

This round audits the new small-grid scaffold
`code/positive_b_allocation_cusp_stage_a.py` against the frozen design in
`notes/positive_b_allocation_cusp_promotion_design.md` and the Round-36
design attack.  It covers implementation algebra and bounded interfaces only.

Final open count:

- `P0=0`
- `P1=0`
- `P2=0`

This is the design's `PASS-ALGEBRA` rung.  It is **not** `PASS-DISCOVERY`:
meshes 65 and 97 were not executed, and no physical positive-`B` cusp, fold
branch, remote pair, or phase representative has been found.

## 2. Audited evidence and noninterference boundary

| role | SHA-256 |
|---|---|
| Stage-A scaffold | `a76773b61f1f2f11802d265d3e69ec632de0b4b0ccbada40a49180454d4981cf` |
| focused Stage-A tests | `c2370dfc69e1e775b486a8a9653f1877d2a28a5003999507ce65017bfcecc065` |
| allocation-cusp promotion design | `ad072e83004ea3e3b5c3d01a58a872b5aedca74d13400fa04d6f917d4a06d1f5` |
| Round-36 design attack | `62c42f1220bd0eeaf9810be5ef2e7cf7f1ff0035b39354838a41cfdda84dd394` |
| independent five-state algebra prototype | `547a1a983f8683acc103a05d47bbdc0f2111f4b9f680c571fa4371642d81241a` |
| prototype tests | `fa664d8d8737c7491c5663da8922b40ddcec9599b10463bff835f71dd04af7be` |

The concurrent positive-`B` point confirmation had already moved, by a
separately recorded serialization-only erratum, to this current frozen v2
boundary before the final Round-44 review:

| frozen-v2 role | SHA-256 |
|---|---|
| producer | `adb9434daeccca721ab9c1014f194e0cf9c5c6d0bf092d31e050c040b4b94da8` |
| tests | `d60e837c949333d29f7287b17c5e24c6db742067a655bac5050b5966dc821329` |
| protocol | `f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00` |
| manifest/anchor | `955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c` |
| operational erratum | `9843b323898b7e0e9edd0eff33431cddb9fb3d4d572caa4d9ebc5d1e5649592c` |

The Stage-A scaffold neither imports nor writes any of those files.  It does
not inspect a positive-`B` result.  Its only CLI mode is a small-grid dry run;
it writes no artifact.

## 3. P0 algebra attacks

### 3.1 Row/column orientation and fixed-budget tangent sign

The probability column uses `Q(theta,B)^T`.  The two state tangents propagate
with lower-block couplings `-B*diag(u_i)`, while row actions remain `Q`.  The
matrix-free base and augmented column/row actions were compared with separately
formed explicit CSR matrices.  Maximum errors on the executed seven-cell dry
run were between `1.67e-16` and `2.22e-16`.  **Closed.**

### 3.2 Direct observable terms and all mixed jets

The implementation carries

\[
 a_{r+1}=Qa_r,\qquad
 b_{r+1,i}=Qb_{r,i}-B D_{u_i}a_r,
\]

and evaluates

\[
 (f/B)^{(r)}_{\theta_i}=s_i^Ta_r+p^Tb_{r,i}.
\]

The audit explicitly attacked the common omission of the second term.  It now
checks `Q^r kappa` against explicit CSR powers and the complete observable
tangent recurrence against centred differences of separately rebuilt CSR
operators.  The seven-cell maximum errors were `5.55e-17` and `5.19e-12`,
respectively.  **Closed.**

### 3.3 Complete cusp map, Jacobian, and determinant factorization

`H=(F_t,F_tt,F_ttt)` uses `F=f/B`, and the analytic Jacobian includes
`F_tttt` and both allocation columns through `F_ttt,theta`.  State tangents
and the time/allocation Jacobian columns pass separate two-step finite-
difference gates.  The determinant identity is tested on a structurally
consistent exact synthetic cusp.  Rank-zero projected response returns a
finite singular-value ratio `0`, not `NaN`, so structural failure remains
serializable.  Non-cusp snapshots and hand-assembled inconsistent jet/Jacobian
fields are rejected.  **Closed.**

### 3.4 Fold predictor sign and branch tangent

The leading predictors satisfy

\[
R_1\eta=f_{tttt}\tau^3/3,\qquad
R_2\eta=-f_{tttt}\tau^2/2
\]

for both frozen offsets `tau=-0.10,+0.10`.  Predictor calls require a verified
near-cusp snapshot, chart-consistent weights, and both the cusp and predicted
point inside the frozen trust box.  Null-vector orientation requires a
verified near-fold snapshot and a finite, nonzero, nonorthogonal previous
direction.  **Closed.**

## 4. P1 fail-closed and scope attacks

### 4.1 Frozen trust region and bounded Newton

The exact trust configuration is enforced: `9<=t<=18`,
`||theta||_inf<=0.15`, `min(w)>=0.03`, at most 12 Newton updates and eight
step halvings.  A caller cannot substitute a wider `TrustBox`.  Every
nonfinite density, residual, Jacobian, step, or evaluation failure becomes an
explicit `HOLD_DISCOVERY` or `HOLD_BRANCH`.  Mock analytic maps verify one-step
success for the cusp solve, fixed-time fold correction, and pseudo-arclength
correction; a deliberately reversed Jacobian verifies no-descent HOLD.
**Closed.**

### 4.2 Exact budget schedule

The tuple is directly asserted as
`(0,0.0025,0.0050,0.0075,0.0100)`.  A successful mocked chain verifies all
five calls in that order; a failed solve stops immediately without schedule
rescue.  **Closed.**

### 4.3 No 65/97 execution or spoofed-model bypass

The public CLI requires `--algebra-dry-run`, caps grids at 25 cells, and
explicitly rejects 65 and 97.  Every computational operator revalidates the
model label against midpoint, relative, state, patch, and direction shapes,
so manually changing `model.cells` cannot bypass the boundary.  There is no
formal discovery entrypoint and no result writer.  **Closed.**

### 4.4 Remote-pair interface cannot become a hidden scan

The helper accepts supplied stationary candidates only.  It performs no root
or control scan.  The retained window `[0.5,35]`, cusp exclusion `0.25`,
relative-density floor `1e-8`, scaled-curvature floor `0.05`, scaled-root
residual cap `1e-8`, and root separation `0.25` are constants rather than
caller-adjustable arguments.  The max--min pair must lie on one side of the
cusp.  Nonpositive density, nonfinite inputs, cross-cusp pairs, and window-
external pairs fail closed.  **Closed.**

### 4.5 Reproducibility and ambient RNG isolation

Each matrix-free exponential propagation pins and restores NumPy's global RNG
state so SciPy norm estimation cannot depend on ambient process history.  Two
fresh five-cell CLI processes produced byte-identical JSON with SHA-256
`10c4112329efe266c4ad868c68bf1a8a0824bc5b32466d8574194c68e6216cef`.
The focused test also proves that ambient RNG state is restored.  **Closed.**

## 5. P2 test-strength attacks

The final tests no longer conditionally skip rank-sensitive assertions.  They
cover both predictor signs, rank-zero serialization, exact constants, full
five-budget ordering, successful and rejected Newton directions, both branch
correctors, evaluator-exception HOLD, remote-window and zero-density attacks,
spoofed scientific-mesh rejection, real dry-run packaging, and every negative
claim flag.  **Closed.**

## 6. Executed checks

```text
python -m ruff format --check \
  code/positive_b_allocation_cusp_stage_a.py \
  code/test_positive_b_allocation_cusp_stage_a.py
2 files already formatted

python -m ruff check <the same two files>
All checks passed!

python -m pytest -q code/test_positive_b_allocation_cusp_stage_a.py
........... [100%]

python code/positive_b_allocation_cusp_stage_a.py \
  --algebra-dry-run --cells 7
status = PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE
all algebra gates = true
scientific_stage_a_meshes_executed = []
all scientific claim flags = false
```

The seven-cell B=0 homotopy attempt returns `HOLD_DISCOVERY` at the first
step.  That is the correct fail-closed outcome for an intentionally coarse
algebra grid and is not evidence against or for the physical cusp.

## 7. Scientific boundary and next authorized step

Round 44 authorizes only the algebra scaffold.  It does not authorize a
manuscript cusp/fold claim, a formal Stage-A result, or the PRR gate.  Before
meshes 65/97 may run, the project still needs a separately reviewed Stage-A
discovery protocol/manifest that pins this code, the exact physical family,
solver tolerances, remote-root procedure, branch stopping rules, finite-
difference checks, output schema, and failure-atomic execution boundary.

Until that new freeze exists, the correct project state remains
**PASS-ALGEBRA-SCAFFOLD / HOLD-SCIENCE**.
