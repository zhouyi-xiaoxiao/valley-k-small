# Round 25 independent G1d fold audit

Date: 2026-07-13  
Scope: formal G1d finite-grid fold artifact, frozen runner, manifest, protocol,
and their pinned G1c inputs

## 1. Verdict

**PASS: G1d confirms one result-informed finite-grid, finite-budget fold.**

The augmented state/control sensitivity, observable action-jet recursion,
Newton Jacobian, fold residual, weight/budget reconstruction, side topology,
and finite-difference checks survive independent derivation and numerical
recomputation.  A full rerun to a temporary output also reproduces the result
within sparse-exponential roundoff without modifying the formal artifact.

This pass authorizes a separately frozen mesh/box convergence campaign.  It
does **not** establish a continuum fold, a global phase map, a cusp,
trimodality, observable peak prominence, an independent-solver result, or the
project/PRR gate.

Severity ledger:

| Severity | Count | Disposition |
|---|---:|---|
| P0 | 0 | No invalidating scientific or implementation defect |
| P1 | 0 | No blocker to a frozen convergence campaign |
| P2 | 2 | Transpose notation should be made explicit in future protocols; side `root_count` is a sign-changing-root screen, not a global root certificate |

Both P2 items are scope/documentation issues.  They do not change the current
fold because the generator tangent is diagonal and the local fold normal form
is independently nondegenerate.

## 2. Frozen files and hashes

| File | SHA256 |
|---|---|
| `artifacts/data/continuum_g1d_fold_confirmation_result.json` | `268e3f988330a2f28ad79b22cdf1f7e53a0142dc007d2a2a7cbfe40d18f91f92` |
| `code/continuum_g1d_fold_confirmation.py` | `5fa43e9482e5ee60cd5fb5c19427b1e749b750116f0861f5277e9fe1be46f3ec` |
| `artifacts/data/continuum_g1d_fold_confirmation_manifest.json` | `2efb66fd4a924b036217368de9429df74872808de45375817b78c79635fad439` |
| `notes/g1d_fold_confirmation_protocol.md` | `572ca5b9b18fc614bf45811c02700c5fa62d57e969181ce4c7c5c02099c1ff4c` |
| pinned G1c result | `cce1e34c599564dc932da6af4d4146c2c396836990e9b51414fc2f843e123bb4` |
| pinned G1c manifest | `543ee21928cf009867bd194d3bb2f6929a3557458733c50ff613c2f664f1d593` |
| pinned Round 24 topology review | `ec25be8159d7d28c73f758a9545731cef44621abd12aa5d4ef2789305c8c1870` |

Every pin in the G1d manifest matches the current file.  The formal result
artifact retained its original hash after the temporary rerun.

## 3. Independent recomputation methods

Three checks were kept distinct.

1. **Algebraic re-derivation.**  I derived the state sensitivity and action
   jets from the row-generator convention, without assuming the protocol's
   block orientation.
2. **Independent full-state calculation.**  Starting from the pinned G1c
   baseline, I rebuilt the arbitrary-weight killing and used an explicit
   `A_lambda.T` augmented block.  I independently formed all action jets and
   compared the state sensitivity with centered state finite differences.
3. **Complete temporary rerun.**  The pinned runner was executed with output
   `/tmp/continuum_g1d_fold_confirmation_reaudit.json`; it returned
   `PASS_FINITE_GRID_FOLD_ONLY` with SHA256
   `f645b89839333ed4470524ef97891cbbfd7d37c74d9c81e12e7198459ff0808b`.

The temporary file was not used to replace or edit the formal artifact.

## 4. Generator and augmented sensitivity orientation

### 4.1 Row-generator convention

The G1 finite-volume generator `A` is stored as a row generator:

```text
free row sums = 0,
killed row sums = -K.
```

For a column of cell masses, the forward equation is therefore

```text
q_dot = A.T q.
```

Along the frozen segment,

```text
w(lambda) = (0.2, 0.1 lambda, 0.8-0.1 lambda),
K_lambda  = budget_density (0,0.1,-0.1) dot patch_profiles times contact,
A_lambda  = -diag(K_lambda).
```

Differentiating the state equation gives

```text
s_dot = A.T s + A_lambda.T q,
s(0) = 0.
```

Thus the mathematically general lower-left block is `A_lambda.T`.  In G1d,
`A_lambda` is diagonal, so `A_lambda.T = A_lambda` exactly.  The runner's
block

```text
[[A.T, 0],
 [A_lambda, A.T]]
```

is therefore correctly oriented for this model.  The independent rebuild
measured the maximum entry of `A_lambda-A_lambda.T` as exactly zero.

### P2.1: protocol portability notation

Equation (2) of the protocol writes `A_lambda` rather than
`A_lambda.T`.  It is correct only because the frozen control changes diagonal
killing and not transport.  A future protocol with control-dependent drift or
diffusion must write the transpose explicitly.  This is not an error in the
current calculation.

## 5. Action-jet control recursion

The reaction density is represented as

```text
f = q.T K.
```

Because `q_dot=A.T q`, define

```text
v_0 = K,
v_(r+1) = A v_r.
```

Then `f^(r)=q.T v_r`.  Differentiating with respect to the segment control
gives exactly

```text
v'_0 = K_lambda,
v'_(r+1) = A_lambda v_r + A v'_r,
partial_lambda f^(r) = s.T v_r + q.T v'_r.
```

There is no missing transpose in the observable recursion: `v_r` is an
action on the observable side, while the state uses `A.T`.  There is also no
missing direct term; `v'_0=K_lambda` supplies it.

The independent full-state recomputation obtained:

| Quantity | Independent value | Formal artifact value | Absolute difference |
|---|---:|---:|---:|
| `f` | `0.025624055108537082` | `0.02562405510853511` | `1.97e-15` |
| `f_t` | `-6.938893903907228e-18` | `6.938893903907228e-18` | `1.39e-17` |
| `f_tt` | `-2.7755575615628914e-17` | `5.551115123125783e-17` | `8.33e-17` |
| `f_ttt` | `-0.00017526530100608895` | `-0.00017526530104250426` | `3.64e-14` |
| `f_lambda` | `0.005357433850539441` | `0.0053574338505390316` | `4.09e-16` |
| `f_tlambda` | `-0.0007985425141329922` | `-0.0007985425141329341` | `5.81e-17` |
| `f_ttlambda` | `-0.00014285646011006486` | `-0.0001428564601099469` | `1.18e-16` |

At centered control step `2e-4`, the independent state finite difference
agreed with the augmented sensitivity to relative L1 error
`2.815e-9`.  Independent observable finite differences agreed with
`f_tlambda` and `f_ttlambda` to relative errors `7.79e-10` and `3.21e-10`.

## 6. Fold, Jacobian, weights, and budget

The formal solution is

```text
t_*      = 10.502258314511947,
lambda_* = 0.6388077420868951,
w_*      = (0.2, 0.06388077420868951, 0.7361192257913105).
```

The weights reconstruct exactly from the declared segment, sum to one, and
have minimum `0.0638807742`, above the frozen `0.02` floor.  The tangent
weights sum to zero.  The recomputed physical-budget relative error is
`3.701e-16`, and the tangent-budget absolute error is `7.174e-18`.

The raw fold system and Jacobian are

```text
(f_t,f_tt) = (6.938893903907228e-18,
              5.551115123125783e-17),

J = [[f_tt,  f_tlambda],
     [f_ttt, f_ttlambda]]
  = [[ 5.551115123125783e-17, -7.985425141329341e-4],
     [-1.752653010425043e-4,  -1.428564601099469e-4]],

det(J) = -1.3995679413475498e-7.
```

Applying the declared row scaling and logarithmic-time column scaling gives

```text
J_dimless = [[ 2.38944900595346e-13, -0.32729010779212786],
             [-7.923118868104377,    -0.6149182984544783]],

det(J_dimless) = -2.5931584283918703.
```

The determinant and both normal-form coefficients are separated from zero by
orders of magnitude.  The Newton history decreases from scaled residuals
`(1.33e-2,2.28e-2)` to at most `2.39e-13` in four evaluations.

## 7. Exact frozen-gate replay

| Gate | Observed | Frozen threshold | Result |
|---|---:|---:|---|
| Newton evaluations | `4` | `<=12` | PASS |
| time | `10.5022583` | `[8,14]` | PASS |
| control | `0.6388077421` | `[0.45,0.9]` | PASS |
| max scaled fold residual | `2.389e-13` | `<=1e-9` | PASS |
| minimum weight | `0.0638808` | `>=0.02` | PASS |
| abs scaled `f_ttt` | `7.92312` | `>=1e-3` | PASS |
| abs scaled `f_tlambda` | `0.327290` | `>=1e-3` | PASS |
| abs dimensionless determinant | `2.59316` | `>=1e-4` | PASS |
| fine finite-difference maximum relative error | `6.817e-8` | `<=2e-4` | PASS |
| finite-difference error decreases | `2.606e-7 -> 6.817e-8` | strictly decreasing | PASS |
| side signatures | `3: max-min-max`, `1: max` | one versus three | PASS |
| foundation gates | `15/15` | all | PASS |

All eleven stored acceptance booleans are true.

## 8. One-versus-three topology

At `lambda_*-0.02`, the refined simple roots are

| time | type | scaled curvature |
|---:|---|---:|
| `5.0100920238` | maximum | `-2.43843` |
| `10.1065281822` | minimum | `+0.321407` |
| `10.9613789208` | maximum | `-0.327220` |

At `lambda_*+0.02`, only the persistent early maximum is retained, at
`5.0361116775` with scaled curvature `-2.38092`.  Every refined first-
derivative residual is below `9e-14` after scaling.

The signs also agree with the independently reconstructed fold normal form.
Here `f_ttt<0` and `f_tlambda<0`; a negative control displacement creates a
nearby minimum on the early-time side of `t_*` and a nearby maximum on the
late-time side, while a positive displacement removes that pair.  The stored
root ordering is exactly this prediction.

The complete temporary rerun reproduced both root-count signatures and all
four root times within `4.7e-13`.

### P2.2: topology-screen boundary

The side evaluator brackets strict sign changes on a `0.02` time grid and
then refines them exactly.  It robustly confirms the four reported simple
roots, but it is not an interval-arithmetic exclusion of an additional
even-multiplicity root or a sub-grid max-min pair.  Therefore `root_count`
must be read as the count of retained sign-changing roots on the frozen
screen, not a theorem giving the global critical-point count.  This is
consistent with the artifact's one-fold scope and its explicit refusal of a
global phase-map or trimodality claim.

## 9. Finite-difference audit

The formal centered-control checks give:

| step | max relative error | `f_tlambda` relative error | `f_ttlambda` relative error |
|---:|---:|---:|---:|
| `1e-3` | `2.606e-7` | `2.061e-8` | `2.606e-7` |
| `5e-4` | `6.817e-8` | `5.158e-9` | `6.817e-8` |

The roughly fourfold reduction is the expected centered-difference behavior.
The independent `2e-4` check reported in Section 5 is stronger still.  These
checks independently support both the augmented sensitivity orientation and
the action-jet derivative recursion.

## 10. Foundation and claim flags

All foundation diagnostics pass, including:

- exact weight sum and nonnegative weights;
- unit patch integrals;
- fixed physical budget and zero tangent budget;
- exact kappa, killing, and generator-tangent reconstructions;
- killed mass balance `1.288e-14`;
- initial mass error `8.882e-16`;
- zero initial contact mass; and
- nonnegative kappa and killing.

The artifact's claim flags are correctly fail-closed:

```text
status                    = PASS_FINITE_GRID_FOLD_ONLY
finite_grid_fold_confirmed = true
finite_B_Doi_fold          = true
continuum_verified         = false
project_gate_passed        = false
evidence_timing            = POST_RESULT_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY
```

The `finite_B_Doi_fold` flag is safe only together with the adjacent
`finite_grid` scope; it must never be quoted as a continuum Doi result.

## 11. Two no-result execution amendments

The frozen protocol predates the successful result and already contains all
scientific choices: selected segment, initial guess, solve box, offset `0.02`,
time window `[3,18]`, spacing `0.02`, root tolerances, finite-difference steps,
and every acceptance threshold.

The two manifest amendments change only how that decimal time grid is
represented:

1. replace accumulated `arange` values by integer ticks times `0.02`; and
2. avoid re-inferring spacing from adjacent binary floats by using a local
   integer-tick chunk evaluator.

The successful evaluator still uses 901 points from 0 to 18, analyzes 3 to
18, limits chunks to 51 points, and advances every exponential by the same
integer number of `0.02` steps.  No physical parameter, candidate segment,
offset, time window, tolerance, or acceptance gate changed.

Filesystem chronology is consistent with the amendment record: the protocol
was fixed before the runner, the runner and manifest were amended before the
result file was first created, and the result writer writes only after a full
run.  No alternative G1d result artifact exists in the report tree.  This is
not independent historical proof of every failed command, but there is no
evidence of post-result scientific retuning and the pinned successful code
implements exactly the frozen protocol.

## 12. Temporary rerun reproducibility

The complete rerun preserved every nonnumeric field and every gate.  Sparse
exponential roundoff changed only insignificant final digits:

- fold time by `4.78e-13`;
- fold control by `2.09e-14`;
- scaled `f_ttt` by `5.41e-10` (`6.83e-11` relative);
- dimensionless determinant by `1.77e-10`; and
- side-root times by at most `4.62e-13`.

The fold residual itself changed sign at the `1e-13` scaled level, as expected
for a converged numerical zero, while all nondegeneracy margins remained
unchanged at reported precision.

The runner passes `ruff check` and Python compilation.  It currently fails
only `ruff format --check` because the formatter would make mechanical layout
changes; there is no lint or execution failure.  No dedicated G1d unit-test
file exists, so the convergence campaign should add focused small-matrix tests
for the augmented block and action recursion rather than relying only on this
full-size audit.

## 13. Mesh-convergence authorization

**AUTHORIZED, with a new prospective freeze.**  The next campaign may test
this single branch on odd/even meshes and box levels, with the following
quantities frozen and followed:

1. the selected control segment and its parameterization;
2. the Newton root continued from this fold;
3. the complete scaled fold jet and dimensionless Jacobian determinant;
4. minimum weights, physical budget, positivity, and mass balance;
5. local one-versus-three normal-form topology; and
6. a fail-closed rule if the branch leaves the interior or loses
   nondegeneracy.

The campaign should add at least one independently implemented state/control
sensitivity check and separate mesh error from finite-box error.  Until those
levels converge, the only valid conclusion remains:

> one result-informed fold of the `65 x 65 x 49` finite-volume Doi model at
> finite budget `B=0.6`.

It is not yet a physical continuum fold, a global allocation phase map, or an
observable trimodal reaction-time result.
