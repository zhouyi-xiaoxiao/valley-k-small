# Round 37: unbounded off-lattice thinning design attack

Date: 2026-07-13  
Role: adversarial self-audit of a new, independent method design and bounded
proof of principle  
Execution boundary: no positive-`B` held-out mesh was run; no frozen
positive-`B` producer, test, protocol, manifest, or result was edited; no
manuscript file was edited.

## 1. Verdict

### Design/POC verdict: **PASS WITH PRODUCTION HOLD**

For its declared scope, the new proof of principle has no open P0, P1, or P2
finding.  It correctly realizes a transition-exact, unbounded-longitudinal,
off-lattice Doi thinning path; supplies a strict analytic homogeneous bound;
keeps the true contact discontinuity; uses the intended compact product
initial law; closes censored event mass by integer counts; and validates the
thinning core against a constant-hazard analytic invariant.

This is not a production independent-solver result.  The following remain
false in the machine-readable output:

```text
independent_solver_verified = false
publication_evidence = false
modality_confirmed = false
project_gate_passed = false
production_run_authorized = false
```

The project therefore remains **HOLD**.  A later protocol must freeze final
deterministic targets, controls, windows, cross-method tolerances, trajectory
count, seeds, chunk ledger, and a compiled/vectorized engine before a
scientific run.

## 2. Audited snapshot

| Role | SHA-256 |
|---|---|
| design note | `349541a954e665d0a68b3989e6f38f5edc725b00f77e4811147c1de262fc7961` |
| POC producer | `90466d074d3b6d302143919d4160beb36109e9686312e3a33670321e4f297e9d` |
| focused tests | `986e839ebaa7f5b56d328826312fcce1f1305a2493108e5da8d7558992cc365d` |
| POC result | `b657300581e5c7e4e482c5569b081bbdd5e4c281cec95b8ae5f074c8ae7571c1` |

The protected positive-`B` anchors still matched the Round 35 GO snapshot at
the end of this audit:

| Protected role | SHA-256 |
|---|---|
| frozen producer | `0c70ffb4a9034772928e2fa95d2ca79ef33754e5aa4157a2f101e15cb312b003` |
| frozen tests | `ee784d1cf6cc4e7ee66968deb8f3421394f697eebee3a50f783533aa469a8f78` |
| frozen protocol | `f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00` |
| frozen manifest | `01b435c834cec9e7bfde2069b19fcdcaa4e06178ccfe0d4b6082f0705dfd5805` |

At the namespace check, the positive-`B` artifact prefix contained only the
manifest.  No N=113 or N=129 output was created by this task.

## 3. Physics and exactness attacks

### 3.1 Generator coefficients and state space — passed

The code was reconstructed from the declared quotient rather than imported
from the FV implementation.  It propagates

- midpoint OU with generator diffusion coefficient `D/2`;
- longitudinal relative OU with coefficient `2D`;
- transverse relative Brownian motion with coefficient `2D`, wrapped on the
  period-one torus.

The resulting variances are respectively

```text
D(1-exp(-2 gamma dt))/(2 gamma)
2D(1-exp(-2 gamma dt))/gamma
4D dt before periodic wrapping.
```

A fixed-normal unit test independently evaluates all three formulas.  No
reflecting longitudinal boundary or time-stepping rule exists in the new
producer.

### 3.2 Initial law — passed

Each of the three initial coordinates is sampled independently from the
normalized compact bump of half-width `0.02`.  Rejection uses the exact ratio
`exp[-u^2/(1-u^2)]`; therefore the unknown normalization cancels.  The
512-attempt cap aborts rather than substituting a fallback.  A 128-path support
test checks all three marginals stay strictly inside their declared supports.

The binary64 bump normalization used only in the hazard was separately checked
by adaptive quadrature to absolute tolerance `2e-14`.  This is still numerical
arithmetic, which the design note explicitly distinguishes from transition-
exact sampling.

### 3.3 Killing field and conserved-budget factor — passed

The evaluated field is exactly

```text
(B/W) * sum_j w_j phi_s(M-c_j)
* 1{R_parallel^2 + d_W(R_perp,0)^2 < a^2}.
```

The `1/W` factor, `B=0.01`, all four weights, centers, half-width `0.04`, and
contact radius `0.16` match the broad family.  The disk indicator is not
smoothed or cell averaged.

### 3.4 Contact discontinuity — passed

The discontinuity does not invalidate thinning.  At every positive Poisson
candidate time the free transition has a continuous relative-coordinate
density, so contact-circle hits have probability zero.  The implementation's
strict-inside convention was attacked at the immediate predecessor float, the
boundary, and the immediate successor float.  Only the inside point has
positive hazard.

### 3.5 Homogeneous domination — passed

The audit recomputed the elementary certificate

```text
I_b >= exp(-4/3), max b = exp(-1), supports disjoint,
||K||_infinity <= B max(w) exp(1/3)/(W s)
                = 0.1245290564385021 < 0.13.
```

This proof does not depend on the sampled maximum or numerical normalization.
The tighter diagnostic maximum is `0.07393234251040665`.  Runtime code aborts
on `K>Lambda`; a mutation with hazard two and `Lambda=1` raises the expected
error.  There is no clipping branch.

### 3.6 Conditional thinning identity — passed

For a fixed free path, independently marking rate-`Lambda` Poisson points with
probability `K(X_t)/Lambda` gives conditional no-event probability

```text
exp[-integral_0^t K(X_s) ds].
```

Thus the accepted time has the unbounded Doi/Feynman--Kac law for bounded
measurable `K`.  A state-independent hazard `k=0.05` provides an independent
analytic invariant: `S(t)=exp(-kt)`.  Across six times the POC maximum error
was `0.0025736523102622977`, inside the alpha-0.001 DKW band
`0.010769427436720583`.

The DKW pass is a stochastic implementation check, not the proof of thinning
and not evidence for broad-family modality.

## 4. RNG and reproducibility attacks

### 4.1 Path isolation — passed

NumPy Philox is keyed by `(trajectory_id, master_seed+replicate_id mod 2^64)`.
For fixed frozen seeds and distinct replicate/path IDs, every trajectory has a
distinct 128-bit key.  Forward and reverse traversal produce identical path
records by ID; changing only the replicate ID changes the sample.  Hence
chunking and worker scheduling cannot change another path's stream.

### 4.2 Version and cross-platform boundary — correctly scoped

The raw Philox design is counter based, but distribution transforms and
floating `libm` behavior are not claimed byte-stable across arbitrary package
or hardware versions.  The result records NumPy `2.5.1` and SciPy `1.18.0`;
the design requires version pins and path fixtures for a compiled production
port.

### 4.3 Complete rerun — passed locally

Two complete POC executions produced identical canonical JSON with SHA-256

```text
b657300581e5c7e4e482c5569b081bbdd5e4c281cec95b8ae5f074c8ae7571c1.
```

This local POC rerun is not the two-pool scientific replication proposed for
production.

## 5. Estimator and power attacks

### 5.1 Survival and mass estimators — passed

Survival uses exact indicators `1{T>t}` and a simultaneous DKW band.  The three
event basins use deterministic valley cuts and integer counts.  The broad POC
records `mass_partition_count_error=0`; a synthetic test separately verifies
that three basin counts plus censoring equal `N` exactly.

One-sided Clopper--Pearson bounds are Bonferroni allocated across the three
masses.  No Wald interval is used for the small `0.005` probability.

### 5.2 Histogram/KDE selection bias — blocked by design

The scientific gate never asks a noisy histogram to locate modes.  Five
equal-width windows must be fixed from deterministic evidence before the
independent run.  Four simultaneous probability contrasts then test the
finite-resolution max--min pattern.  An adaptive KDE may be plotted only as a
non-gating visualization.

The design correctly refuses to infer stationary roots, fourth derivatives,
cusp rank, or Jacobians from Monte Carlo.

### 5.3 Power and quarter-margin rule — passed as preliminary planning

The POC computes exact binomial power for a **fixed** provisional
`N=6,000,000`; it does not call a discontinuous exact-test power curve
monotone or claim an exact minimal sample size.  At the disclosed N=97
smallest-mass alternative, power exceeds `0.999999999999999`, and the nominal
Clopper--Pearson radius `7.3897e-05` is below the quarter-margin target
`7.6865e-05`.

A separate union-bound certificate gives at least 0.90 joint power for the four
window contrasts under the disclosed N=97 planning probabilities.  Both
calculations are explicitly invalidated for production if final deterministic
alternatives change.

### 5.4 Cross-method comparability — passed at design level

The note requires FV integration over the exact same windows as MC.  It
forbids comparing a point peak to a window average and freezes the rule

```text
|x_FV-x_MC| <= E_FV + E_MC + tau_cross,
tau_cross < one quarter of the distance to the nearest threshold.
```

Final numerical values for `E_FV` and `tau_cross` do not yet exist, so this is
a production blocker rather than evidence.

## 6. Findings found and repaired during this attack

1. **Potential P1: a claimed minimum exact sample size would be invalid.**
   Exact-test power has small sawtooth changes when the critical count jumps.
   The code was changed to evaluate power and CP precision at the fixed
   provisional `N=6,000,000`, not to claim a globally minimal `N`.
2. **Potential P1: bump normalization provenance was too implicit.**  The
   binary64 constant is now serialized and checked against an independent
   quadrature; sampling remains normalization-free.
3. **Potential P1: broad-run mass closure was inferable but not serialized.**
   Censored survivor count and `mass_partition_count_error=0` are now explicit.
4. **Potential P2: initial-support correctness lacked a direct mutation.**  A
   128-path product-support test was added.

All four were closed before this final snapshot.  No threshold, physical
input, or frozen positive-`B` file was changed to close them.

## 7. Remaining production blockers, not POC defects

These are hard gates for a future independent-solver claim:

1. final continuum/box survival, valley cuts, and five window integrals are not
   frozen;
2. fold-side allocation controls and their expected contrast patterns are not
   frozen;
3. all `E_FV`, `tau_cross`, seed/ID/chunk contracts, and final `N` are missing;
4. the scalar Python POC has not been replaced by and fixture-matched to a
   production engine;
5. no six-million-path scientific pool has been run;
6. the state-dependent broad law has no closed-form comparator, so its
   scientific validation must come from predeclared cross-method agreement;
7. MC cannot close deterministic cusp-jet, rank, or fourth-derivative gates;
   and
8. the small broad smoke has only `(25,19,41,26,29)` window counts and is
   intentionally powerless for modality.

Any attempt to set `independent_solver_verified=true` before these close is a
P0 claim error.

## 8. Verification commands

```text
.venv/bin/ruff format --check \
  research/reports/encounter_multimodal_prr/code/off_lattice_doi_thinning_poc.py \
  research/reports/encounter_multimodal_prr/code/test_off_lattice_doi_thinning_poc.py
```

Passed: both files already formatted.

```text
.venv/bin/ruff check \
  research/reports/encounter_multimodal_prr/code/off_lattice_doi_thinning_poc.py \
  research/reports/encounter_multimodal_prr/code/test_off_lattice_doi_thinning_poc.py
```

Passed.

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -ra \
  -p no:cacheprovider \
  research/reports/encounter_multimodal_prr/code/test_off_lattice_doi_thinning_poc.py
```

Passed: **10/10**.

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python \
  research/reports/encounter_multimodal_prr/code/off_lattice_doi_thinning_poc.py \
  --run-poc
```

Passed twice with byte-identical output.

## 9. Final decision

The off-lattice route is mathematically sound, genuinely independent of the
FV discretization, and bounded enough to promote to a separately frozen
production protocol.  The current artifact is only a reference implementation
and power/design audit.  Scientific status remains **HOLD** until the final
targets are frozen and the powered independent run passes without refitting.
