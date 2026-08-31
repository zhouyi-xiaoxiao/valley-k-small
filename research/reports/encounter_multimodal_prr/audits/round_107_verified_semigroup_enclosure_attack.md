# Round 107 — independent attack on the verified semigroup enclosure

Date: 2026-07-14  
Auditor role: independent numerical-method adversary  
Verdict: **GO-METHOD / HOLD-PRODUCTION / HOLD-F1-SCIENCE**

## 1. Scope and immutable boundary

This round attacked the only open numerical-method P0 identified in the
sub-Markov interval design: whether a finite killed CTMC state and the scalar
quantities needed by the complete-window certificate can receive an explicit,
fail-closed forward enclosure in the presence of truncation and floating-point
roundoff.

The round did **not**:

- inspect a prospective LP control at positive budget;
- change any control, root band, tile, tolerance, or F0 gate;
- produce a topology or publication result;
- edit the manuscript, modal-theory note, or fixed-control F0 design; or
- use replica agreement as an error bound.

The only finite-budget diagnostic used the already known historical control on
`N=33`, solely to test method scale and ledger magnitudes.

## 2. Audited bytes

| artifact | SHA-256 | role |
|---|---|---|
| `notes/verified_semigroup_enclosure_design.md` | `860abf6f1f3b1d3466c8c1c8310266c65b7f9311438383983831243bb37b470e` | selected method, derivation, comparison, production contract |
| `code/verified_uniformization_enclosure.py` | `a4646f946b891133c972f62cd36a1cb177516793050c2b6e520cffceb57782ed` | method-only reference implementation |
| `code/test_verified_uniformization_enclosure.py` | `6b842112f71bf88d8447a88ccba21ef1d9cbe89676912e80789e7ce964acbe34` | analytic, mutation, randomized, tail, and reduction tests |
| `notes/submarkov_interval_certificate_design.md` | `65a9cc177396f925bddbd8cc8ef36515de2e1c0f763fa6694aad38488430f335` | upstream scalar/state requirement |
| `audits/round_105_fixed_control_f0_design_self_audit.md` | `0631d6b71d58349a75c1695aa02bea66ae3e1d27cc587e3fefb1904b0f77fef0` | upstream P0 statement and F1 hold |

## 3. Top-line result

The abstract P0—“does a mathematically explicit state/scalar enclosure exist
for this killed finite CTMC?”—is **closed**.  Uniformization with a rate-defined
killed generator, directed-MPFR Poisson weights, and an induced-`l1` binary64
ledger is sufficient.  The prototype implements the proof ingredients and
passes the executed small-chain and historical-method attacks.

The current F1 execution gate remains **HOLD** because the existing production
FV operator has not been replaced by the rate-defined/outward matrix-free
kernel, and because the exact-rational control/geometry/initial intervals and
machine-readable ledger are not yet integrated.  This is now a specific
implementation P0, not an unresolved choice of numerical analysis.

## 4. Adversarial attacks

### 4.1 Orientation and contraction

**Attack.** Could the proposed norm accidentally apply to `exp(tQ)` rather
than the actual column propagation `exp(tQ^T)`?

**Result. PASS.** For a killed row generator, `P=I+Q/lambda` is
row-substochastic, hence `P^T` and `exp(tQ^T)` are induced-`l1` contractions.
The implementation stores a row `Q`, propagates with the CSR transpose, and
uses maximum row absolute sums for `||Q^T||_1`.  Analytic two-state tests would
fail under the opposite orientation.

### 4.2 Rounded-diagonal attack

**Attack.** Treat the currently assembled historical CSR matrix as exact
binary64 and demand exact Metzler/killed-row structure.

**Result. FAIL FOR THE OLD OPERATOR; REPAIRED IN THE PROTOTYPE.** The known
`N=33` matrix had `35,937` rows and `247,203` nonzeros.  Ordinary reduction
reported a maximum row sum `2.876171523169546e-15` and `19,786` positive rows;
the exact-dyadic structural preflight also rejected a positive exact row.

The repair defines the target diagonal as the exact negative sum of
off-diagonal rates and killing, rounds the centre toward minus infinity, and
carries the resulting induced operator radius.  The historical radius was
`1.7741884350552795e-15`.  Both target and centre are then killed generators,
and target-to-centre uncertainty enters every uniformized power as
`delta_Q/lambda`.  No tolerance-based claim that the old positive row sums are
“close enough” remains.

### 4.3 Poisson-tail and transcendental attack

**Attack.** Underflow `exp(-x)`, corrupt the right tail, lower MPFR precision,
or stop at an insufficient term cap.

**Result. PASS.** Directed MPFR encloses `exp(-x)` and every recurrence weight;
the right tail uses a geometric upper bound only after its ratio is below one.
The mean-500 test closes a `1e-20` tail without binary64 `exp`.  Precision below
96 bits and a two-term cap both fail closed.

### 4.4 Floating-ledger attack

**Attack.** Look for a long binary64 expression followed by only one
`nextafter`, an ordinary library row sum, or an undocumented reduction order.

**Result. FOUND AND REPAIRED BEFORE FREEZE.** The first prototype applied one
outward step after several scalar multiplications/additions and used a normal
CSR row reduction for one roundoff coefficient.  That was not a sufficient
formal ledger.  The frozen code now:

- applies outward rounding after each nonnegative scalar multiplication and
  addition;
- computes maximum centre row sums from exact dyadic entries;
- uses a deterministic pairwise tree for all `l1` norms and dense dots;
- uses an outward `gamma_k` constructed from an exact rational; and
- adds an absolute smallest-subnormal allowance for every operation family.

The exact-Fraction cancellation test for the pairwise dot passes.

### 4.5 Runtime-model attack

**Attack.** Change the floating environment or silently flush subnormals.

**Result. PASS ON THE PINNED RUNTIME.** The kernel preflight checks IEEE
binary64, C `FE_TONEAREST`, scalar subnormal multiplication/addition, and a
subnormal through the actual SciPy CSR action.  Failure raises
`VerificationFailure`; it cannot be converted to a warning.

### 4.6 Analytic state attack

**Attack.** Compare the enclosure with directed-MPFR one-state death, a closed
form two-state birth/killing law, and independently computed dense exponentials
for seeded small killed chains.

**Result. PASS.** Every independent reference lies within the saved `l1`
radius.  Generator sign, row-sum, diagonal, rate, and cap mutations fail.

### 4.7 Generator-action and scalar attack

**Attack.** Propagate an enclosed state through signed `Q^T` actions up to
order three, where cancellation removes the positivity used by the state
kernel.

**Result. PASS.** The action recurrence switches to the absolute induced norm
and a signed sparse-action roundoff bound.  Pairwise scalar enclosures contain
the dense analytic reference, and every `M_r` upper bound dominates the exact
small-chain value.

### 4.8 Time anchoring attack

**Attack.** Split a decimal endpoint into chunks using repeated floating
subtraction and compare with a direct propagation.

**Result. PASS.** Time inputs are exact dyadic `Fraction` values; equal rational
chunks close exactly to the target.  Direct and sequential nominal states are
within the sum of their independent radii.

### 4.9 Reproducibility-versus-proof attack

**Attack.** Remove the analytical ledger and substitute two byte-identical
runs or agreement with `expm_multiply`.

**Result. REJECTED BY DESIGN.** Neither replica agreement nor agreement with a
second binary64 exponential action appears in an enclosure formula.  Such
checks may remain regressions, but the proof fields are coefficient,
Poisson-tail, sparse-action, reduction, state, action, and scalar radii.

### 4.10 Cost attack

**Attack.** Determine whether the selected route is merely formal and clearly
impossible at the known stiffness.

**Result. NOT CLEARLY IMPOSSIBLE; PRODUCTION BENCHMARK STILL REQUIRED.** The
historical uniformization rates were:

| cells | `lambda` | `35 lambda` |
|---:|---:|---:|
| 33 | `12.064562872168926` | `422.2597005259124` |
| 65 | `41.18376980152154` | `1441.431943053254` |
| 113 | `119.09178809484058` | `4168.21258331942` |

On `N=33`, a full `t=35` method diagnostic used 615 Poisson powers and 0.114 s
after preflight, with state radius `8.398977312689668e-13`.  This establishes a
nonvacuous small historical calculation.  It does not benchmark the
`7,165,305`-state `MR+F` row or 36-row envelope.  The production algorithm must
use the tensor stencil; the explicit `Fraction`/CSR prototype is not an
acceptable storage or preflight strategy at that scale.

## 5. Route comparison verdict

### 5.1 Krylov defect

The exact contraction identity makes an `l1` defect integral a valid potential
certificate and Krylov may be materially faster.  It was not selected as the
reference because a finite-precision Arnoldi run needs all of the following:

1. an outward relation residual for `Q^T V - V H - h v e_m^T`;
2. an interval evaluation of the projected exponential and absolute defect
   integral;
3. initial normalization, sparse action, orthogonalization, dot, and basis
   storage roundoff; and
4. a fail-closed restart/step selector.

The current repository supplies none of those.  A conventional residual or
heuristic estimator is not interchangeable with a proved forward bound.
Krylov remains a future accelerator to be checked against uniformization.

### 5.2 Uniformization/Fox--Glynn/scaled chunks

This is the accepted reference because positivity and Poisson truncation make
the target state, tail, and roundoff live in one norm without a detailed-balance
condition factor.  The prototype uses directed MPFR recurrence with mean-500
chunks.  Fox--Glynn scaling is optional optimization, not a missing proof
ingredient; if introduced, its normalization and both tails require the same
directed ledger.

### 5.3 Rational/resolvent

The resolvent of a contraction generator is bounded in the right half-plane,
but that alone does not certify a high-order inverse Laplace/contour method.
The repository has no directed contour truncation/quadrature or verified
shifted linear solves on the tensor grids.  Backward-Euler/Erlang products are
positive but too low order to be the minimum viable substitute.  This route is
therefore rejected for F0 v1.

## 6. Executed verification

```text
../../../.venv/bin/python -m pytest -q -ra -p no:cacheprovider \
  code/test_verified_uniformization_enclosure.py
............ [100%]
12 passed

../../../.venv/bin/python -m ruff check \
  code/verified_uniformization_enclosure.py \
  code/test_verified_uniformization_enclosure.py
All checks passed!

../../../.venv/bin/python -m ruff format --check \
  code/verified_uniformization_enclosure.py \
  code/test_verified_uniformization_enclosure.py
2 files already formatted
```

The historical method-only diagnostic additionally returned:

```text
preflight: 2.24 s
t=0.5: mean 6.0323, 39 terms, state radius 1.9326e-14
t=35 : mean 422.2597, 615 terms, state radius 8.3990e-13
```

No prospective-control value was printed or stored.

## 7. Findings and required closure

| ID | priority | finding | consequence | required closure |
|---|---:|---|---|---|
| R107-P0-1 | P0 | the current production FV generator/evaluator is not the verified rate-defined kernel; its old stored diagonal fails exact killed-row structure | no present F1 row can claim a full-window interval certificate | implement the outward rate-stencil rebuild, target `delta_Q`, `delta_P`, matrix-free `P^T` action, scalar/action ledger, and exact schema; independently audit the frozen implementation before any prospective-control evaluation |
| R107-P1-1 | P1 | exact-rational control weights, FV/contact/support coefficients, and the initial law do not yet supply induced operator/observable/state intervals to the new kernel | the semigroup prototype encloses a supplied finite CTMC, not yet the entire exact F1 input contract | build coefficient and initial-state interval records with source hashes and mutation tests; feed their radii into the same ledger |
| R107-P1-2 | P1 | the 12-grid/36-row workload, anchor count, largest-grid memory, and radius growth are not benchmarked | the route may still hit a deterministic resource or interval-width HOLD | run only synthetic, small explicit, and historical method benchmarks first; freeze term, time, memory, anchor, and radius ceilings before F1 |
| R107-P1-3 | P1 | no append-only production certificate JSON, validator, or independent mutation suite exists | successful arrays could be reported without the proof provenance | freeze exact fields and HOLD codes; independently mutate structure, coefficients, tails, reductions, time coverage, runtime, and resource caps |
| R107-P2-1 | P2 | the reference recomputes Poisson weights from zero and may incur avoidable small-chunk overhead | performance only | consider directed Fox--Glynn/scaled weights after the reference implementation passes; no science-facing selector change after F1 values |
| R107-P2-2 | P2 | the runtime check is pinned to macOS `FE_TONEAREST` semantics and `gmpy2 2.2.1` | portability only | pin the runtime closure now; a new platform requires its own smoke test and audit rather than silently inheriting the certificate |

Counts:

```text
open P0 = 1  (production integration, not method existence)
open P1 = 3
open P2 = 2
```

## 8. Claim boundary

The strongest valid statement after Round 107 is:

> A forward `l1` enclosure for the finite killed-CTMC state, its first three
> generator-action scalars, and the local `M_r` bounds is mathematically and
> computationally realizable by directed uniformization; a proof prototype
> passes analytic, mutation, randomized small-chain, and historical
> method-only diagnostics.

It is not yet valid to say:

- that any new LP control has one, two, or three positive-budget modes;
- that a production FV row has passed the interval certificate;
- that the 36-row workload is feasible;
- that an ordinary `expm_multiply` output is certified; or
- that F1, F2, F3, continuum, or PRR promotion gates have passed.

## 9. Final gate

```text
method selection                         PASS: uniformization reference
state forward enclosure                  PASS in proof prototype
scalar/action/M_r enclosure              PASS in proof prototype
Poisson tail and transcendental ledger   PASS
floating roundoff ledger                 PASS after repair
historical small-grid feasibility        PASS as method diagnostic
production FV integration                HOLD (R107-P0-1)
new-control positive-budget execution    NOT AUTHORIZED
```

The next permitted task is a science-free F0 production implementation and
independent attack of these exact bytes.  The next prohibited task remains any
positive-budget evaluation of the three prospective LP controls.
