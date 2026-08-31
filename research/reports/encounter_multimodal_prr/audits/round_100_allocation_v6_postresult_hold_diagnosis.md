# Round 100: allocation-v6 post-result scientific-HOLD diagnosis

Date: 2026-07-14  
Role: independent post-result diagnostician; no producer or auditor edit  
Decision: **EVIDENCE CHAIN ACCEPTED; TERMINAL V6 SCIENTIFIC HOLD; NO STAGE B**  
Open findings: **P0 = 1 scientific promotion blocker, P1 = 1 diagnostic limitation, P2 = 0**

## 1. Scope and non-execution declaration

This round inspected only the frozen protocol, manifest, producer source, the
three promoted canonical JSON artifacts, and the already published strategic
stopping rules. It did **not** invoke `--execute-frozen`,
`--execute-replica`, `run_formal`, `solve_cusp`, `run_homotopy`, or any mesh
constructor/evaluator. It did not run mesh 65 or 97, change a threshold,
continue a homotopy, inspect an absent hidden replica, or create a substitute
scientific artifact. The only workspace write in this round is this report.

The reviewed anchors are:

| role | SHA-256 |
|---|---|
| v6 manifest | `2e1223f6206c6ebc4adc5c11ed67672afdc55f68e90f725cf8b6930bb67b9948` |
| v6 producer | `b32260ad18abd3f159b7cac1dcd600be2507ff2a89cf60712c5c6f66ccbd70da` |
| discovery protocol | `3c56b307bed70c52152c31764aa84020b7c45770ea656e00fe1d54d47b51ab2b` |
| post-result audit protocol | `393b648c9ba36acc47b9c9acfbc86a82946df495fb36928f6ded91e826ca03b7` |
| canonical result | `47ad903f5d2f62cfdaf842219b1edc85f62089ce942663f67a89cc8be4ab5986` |
| reproducibility evidence | `d547d22ecde99d859545c772db06d681ebc7fcd6d9dc6fdbf1baa543eb9a6e55` |
| independent audit | `5a31dad6c153119c5b20549f7ba324045dd4ce78a7cbb1da715fa3d1f65841c2` |
| independent auditor | `38b7822efce5ddd3b0220549a94a259f393c44150f66a61140f9b58029bf23f0` |

## 2. Executive diagnosis

The formal chain behaved exactly as a fail-closed protocol should:

1. the seven-cell explicit-CSR preflight passed with maximum error
   `2.220446049250313e-16`;
2. mesh 65 solved the semidiscrete `B=0` homotopy row;
3. the next frozen row, `B=0.0025`, stopped with
   `reason = line_search_failed` at maximum dimensionless residual
   `1.354737396982097e-10`;
4. this exceeds the frozen convergence tolerance `1e-10`, so the row is not a
   converged cusp under the registered decision rule;
5. mesh 97 was correctly not built or run and is serialized as
   `NOT_RUN_AFTER_HOLD`;
6. both complete processes reproduced the same HOLD bytes; and
7. the independent auditor validated the evidence chain and returned
   `HOLD_SCIENCE_AUDIT_VALID`.

The only proved causal statement is therefore:

> The frozen Newton/line-search algorithm failed its predeclared convergence
> rule at the first positive-budget continuation row on mesh 65.

It is **not** proved that a physical or semidiscrete allocation cusp does not
exist at `B=0.0025`. Conversely, the small residual is **not** a proof that an
exact cusp exists nearby. The v6 scientific claim remains unestablished.

## 3. Exact numerical meaning of the failed row

For the saved snapshot, the producer defines the dimensionless cusp residual

\[
 \rho_\infty=
 \max\!\left(
 \left|\frac{tF_t}{F}\right|,
 \left|\frac{t^2F_{tt}}{F}\right|,
 \left|\frac{t^3F_{ttt}}{F}\right|
 \right),
\]

where `F=f/B` for positive `B`. The target equations are
`F_t=F_tt=F_ttt=0`; division by the positive density and powers of time makes
the stopping quantity dimensionless.

The two completed homotopy rows are:

| budget | point `(t, theta1, theta2)` | iterations | residual | result |
|---:|---|---:|---:|---|
| `0` | `(13.81588768648076, -0.01083037139771851, 0.006880298367769335)` | 6 | `5.764603304412123e-11` | converged |
| `0.0025` | `(13.771747378036672, -0.010901371542432058, 0.009908078896292763)` | 6 | `1.354737396982097e-10` | line search failed |

At `B=0.0025`, the residual is `1.354737396982097` times the frozen
tolerance, an absolute excess of `3.54737396982097e-11`. It must not be
rounded down or treated as a practical pass: the protocol fixed a strict
`<= 1e-10` convergence gate before the result existed.

The failed saved point is not close to a registered physical boundary. Its
reconstructed allocation is

\[
 w=(0.28083436536623096,\ 0.23192230228653870,\
 0.19606863258766583,\ 0.29117469975956450),
\]

which sums to one. The minimum weight is `0.19606863258766583`, giving
`0.16606863258766583` headroom above the frozen `0.03` simplex gate. The time
has margins `4.771747378036672` and `4.228252621963328` to the lower and upper
faces of `[9,18]`. The allocation infinity norm is
`0.010901371542432058`, leaving `0.13909862845756793` to the `0.15` chart
boundary.

Thus the saved point itself did not fail because it left the trust box or
simplex. This does not prove that every attempted Newton trial was in the
box: those trial points were not serialized.

## 4. What `line_search_failed` does and does not establish

At each iteration the producer solves the raw analytic Newton system

\[
 DH\,\Delta=-H,
 \qquad H=(F_t,F_{tt},F_{ttt}),
\]

and considers the nine registered trial scales
`Delta/2^h`, `h=0,...,8`. A trial is accepted only if it is inside the trust
box, its evaluation is finite, and its dimensionless residual is **strictly**
smaller than the current residual. At iteration 6 no registered trial met all
three conditions, producing `line_search_failed`.

The saved data do not distinguish among:

- one or more trial points leaving the trust box;
- one or more trial evaluations failing or becoming nonfinite;
- finite in-box trials failing strict descent because the Newton direction is
  poorly conditioned for the scaled merit function; or
- stagnation at the accuracy floor of the matrix-free `expm_multiply` state
  and tangent evaluations.

No residual vector, raw/scaled Jacobian singular values, Newton step, trial
points, trial residuals, or per-trial rejection reasons are present in the
fixed HOLD schema. The independent auditor also explicitly does not recompute
the semigroup or run an independent cusp solver. Consequently, it would be an
overclaim to assign a unique numerical cause.

The observed facts support the following classification:

| interpretation | status | reason |
|---|---|---|
| frozen algorithmic convergence gate failed | **proved** | residual exceeds tolerance and no registered trial was accepted |
| current saved point violated time/theta/simplex bounds | **ruled out** | all reconstructed margins are large and positive |
| deterministic implementation result is reproducible | **proved** | two full processes produced byte-identical HOLD output |
| numerical stagnation or Jacobian conditioning caused the failure | **plausible but unproved** | residual is very small, but the needed trial/Jacobian diagnostics are absent |
| an exact semidiscrete cusp exists nearby | **not established** | a small residual alone gives no inverse-Jacobian or Newton--Kantorovich bound |
| no semidiscrete or physical cusp exists | **not established** | finite-iteration failure is not a nonexistence theorem |
| continuum positive-`B` cusp exists or is absent | **not addressed** | only one finite-volume mesh reached the failed positive-budget row |

In particular, `1.3547e-10` is a residual, not a distance in parameter space.
Without a lower bound on the smallest singular value of `DH` and a controlled
local Lipschitz or interval bound, it cannot be converted into a certified
distance to a root. The terminal `B=0.01` cusp diagnostics, quartic margin,
projected allocation rank, full-Jacobian rank, folds, remote pair, and phase
representatives were never reached.

## 5. Two-replica and independent-audit chain

The reproducibility evidence is internally complete and independently
cross-checked:

- `independent_process_count = 2` and `execution_order = sequential`;
- replica exit codes are exactly `[2,2]`, the registered scientific-HOLD exit;
- both replica result hashes and the canonical result hash are
  `47ad903f5d2f62cfdaf842219b1edc85f62089ce942663f67a89cc8be4ab5986`;
- `byte_identical = true`;
- before/after cryptographic pin snapshots are equal;
- before/after lexical metadata snapshots are equal;
- the first launch boundary reports no scientific path present, and the
  second reports only the owned first hidden replica;
- both promotion staging paths were absent at the registered boundaries;
- the two hidden replica paths and both staging paths are absent after clean
  promotion; and
- the canonical result hash independently equals the hash recorded in both
  the reproducibility evidence and the independent audit.

The independent audit has `audit_integrity_passed = true`, every named check
is true, `failed_checks = []`, `scientific_result_passed = false`, and
`release_status = HOLD_SCIENCE_AUDIT_VALID`. This is the correct distinction:
the evidence is valid, while the scientific discovery gate is not passed.

The absent hidden replicas were not and must not be reopened. Their equality
was captured before their registered cleanup and is attested by the canonical
reproducibility record plus the independent auditor's
`two_process_evidence` check.

## 6. Hard stop for the v6 branch

The following actions are forbidden as continuations of this frozen v6 run:

1. rerunning mesh 65 or manually running mesh 97;
2. relaxing the convergence tolerance, for example from `1e-10` to `2e-10`;
3. adding Newton iterations or line-search halvings;
4. changing the budget schedule, initial point, chart, trust box, physical
   family, geometry, support, or total budget;
5. expanding the search or selecting another allocation plane;
6. treating the near-threshold residual as a pass;
7. invoking the held-out Stage-B chain, because no Stage-A cusp,
   representatives, branch orientations, or comparison nodes exist to freeze;
8. claiming a positive-`B` cusp, folds, phase manifold, cusp-organized
   multimodality, or PRR release from this artifact; or
9. replacing the missing same-family evidence with the unrelated three-slab
   fold or generic catastrophe language.

The canonical v6 status is terminal and remains `HOLD_DISCOVERY`. It must not
be overwritten or retrospectively promoted.

## 7. Protocol-compliant next routes and publication boundary

### 7.1 Immediate registered route: redirect

The promotion design says that a failed Stage-A cusp is `HOLD_DISCOVERY`, not
permission to alter the plane, schedule, geometry, or trust region. Its
stopping rule points to Round 33 when the same-family cusp fails. Round 33's
registered redirect is a focused PRE/JCP-style paper on conserved-reactivity
reaction-time shape plus the scoped fixed-finite-mode theorem.

For that route:

- retain the already validated exact/weak-budget theory and the separately
  frozen positive-`B` multimodal point within their existing scopes;
- remove a finite-positive-`B` catastrophe or allocation-phase-manifold
  headline;
- do not present this failed iterate as a cusp result; and
- if an independent unbounded killed-process calculation is pursued, freeze
  it separately as validation of the fixed positive-`B` topology, survival,
  and event masses, not as validation of absent cusp/fold data.

This can remain publishable, but it is not the registered `SEND-2D` PRR
package. The preferred PRR spine required the same-family positive-`B` cusp,
both branches, converged mesh/parity/box evidence, and independent unbounded
validation; its first numerical promotion gate is now open.

### 7.2 Optional future method study: outside v6, not a rescue rerun

If the mathematical existence question is important enough to revisit, the
only defensible option is a **new, explicitly post-result and method-focused
protocol**. It would not be Stage B, would not be result-blind discovery, and
could not retroactively change the v6 HOLD. Before any new scientific solve,
it should freeze at least:

- the unchanged physical family, chart, budget schedule, and convergence
  target, avoiding threshold relaxation;
- an independently implemented residual evaluator and nonlinear solver, or a
  higher-precision/validated numerical route;
- serialization of the full residual vector, scaled Jacobian singular values,
  Newton step, every trial scale, every rejection reason, and an explicit
  semigroup error budget; and
- a root-certification criterion such as an independently checked
  Newton--Kantorovich or interval-Newton enclosure, with a predeclared failure
  outcome.

Such a study could distinguish solver stagnation from root absence. It would
still require fresh independent confirmation before supporting a strong
publication claim, and it must not be counted as the already failed v6
discovery replicate. The current protocol itself authorizes no further mesh
execution.

## 8. Severity ledger

### P0.1 — positive-`B` allocation cusp not established

The central same-family cusp/fold/phase claim needed by the registered PRR
promotion route is absent. Mesh 97, terminal-budget diagnostics, branches,
remote pair, representatives, and every Stage-B quantity are correctly
not-run. This is a scientific release blocker, not an artifact-integrity
defect.

### P1.1 — HOLD schema cannot identify the numerical failure mechanism

The fixed row proves fail-closed convergence but omits the residual components,
Jacobian conditioning, Newton step, trial values, and rejection categories
needed to separate semigroup accuracy-floor stagnation from conditioning or
invalid trials. This does not invalidate the HOLD. It must be repaired only in
a future separately frozen method-study schema, never by editing the current
producer or result.

### P2

No P2 presentation or evidence-hygiene finding was identified in the three
canonical JSON artifacts.

Final ledger:

```text
artifact/evidence integrity = ACCEPT
scientific status           = HOLD_DISCOVERY
audit release status        = HOLD_SCIENCE_AUDIT_VALID
P0                          = 1 (PRR allocation-cusp promotion blocked)
P1                          = 1 (failure-mechanism diagnostics unavailable)
P2                          = 0
mesh 65 rerun               = FORBIDDEN IN V6
mesh 97                     = NOT RUN; MANUAL RUN FORBIDDEN
Stage B                     = NOT AUTHORIZED
current publication route   = REDIRECT / NARROW CLAIMS
```
