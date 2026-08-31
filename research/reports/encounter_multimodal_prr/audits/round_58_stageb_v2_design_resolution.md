# Round 58: Stage-B v2 result-blind design resolution

Date: 2026-07-14  
Role: independent self-audit of the repaired Stage-B v2 design contract  
Verdict: **GO-DESIGN / HOLD-EXECUTION**

## 1. Scope and non-execution boundary

This round audits only the contract in
`notes/positive_b_stage_b_validation_design_v2.md`.  It did not open a hidden
or canonical positive-`B` result, run a scientific finite-volume
configuration, generate a scientific trajectory, or modify a producer,
manifest, result, post-result auditor, or manuscript.

The audited snapshot is:

| role | repository path | SHA-256 |
|---|---|---|
| repaired v2 design | `notes/positive_b_stage_b_validation_design_v2.md` | `8d64c54c2d4727583dc9ee513fc3fc58af57835283b68111a648f6ef33f63f84` |
| Round-54 attack | `audits/round_54_stageb_design_attack.md` | `5de663b0db0147a27b7af8901f3ae0a26a72a333ab5f95fbd2610e92e9294265` |
| Round-57 re-audit | `audits/round_57_stageb_independent_reaudit.md` | `953bb602c29bb0ef2556e1a3ce63c0a309a4f298701c4ec7e6da9937194f0ab3` |

The design hash was computed after the final alpha-ledger wording was fixed.
These are evidence anchors, not execution authorization.

## 2. Result-blind self-checks

### 2.1 Configuration and workload arithmetic

The eight state counts recompute from the frozen tensor dimensions as

```text
O113/Base  113^3       = 1,442,897
E128/Base  128^3       = 2,097,152
O129/Base  129^3       = 2,146,689
O161/Base  161^3       = 4,173,281
M+         166*129^2   = 2,762,406
R+         129*172*129 = 2,862,252
MR+        166*172*129 = 3,683,208
MR+F       207*215*161 = 7,165,305
```

The first seven sum to `19,167,885`.  With 15 controls on each first-seven
configuration and nine on `MR+F`, the no-byte-duplicate workload is

```text
logical rows                       = 7*15 + 9 = 114
first-seven state-law cells        = 15*19,167,885 = 287,518,275
MR+F state-law cells               = 9*7,165,305   =  64,487,745
state-law cells per execution      =                 352,006,020
two full deterministic executions =                 704,012,040
```

The v2 design also fails closed when exact byte duplicates exist: it preserves
114 logical role rows, recomputes the physical workload from the one-to-many
role map, and forbids claiming `352,006,020` as executed work unless the
no-duplicate cardinalities are verified.

### 2.2 Universal thinning rate and alpha total

The common physical bound recomputes to

```text
(0.01/0.04)*exp(1/3) = 0.3489031062715224 < 0.35.
```

The familywise allocations recompute to

```text
0.010 + 0.015 + 0.015 + 0.010 = 0.050.
```

The v2 ledger assigns each statement family unambiguously, counts every
one-/two-sided tail, includes poolwise, pooled, and pool-consistency claims,
and assigns no alpha to the exact-ID reproducibility duplicate.

### 2.3 Envelope logic

The Round-57 counterexample was re-applied:

```text
q_O129 = 0, q_O161 = -1, q_MR+ = 1, q_MR+F = 2.
```

The rejected edge-increment rule could return one.  The v2 formula instead
contains `|q_O161-q_MR+F|=3`, so its reference-centred empirical component is
at least three.  Every MC-promoted control has all eight configuration values,
all grids integrate over the same `MR+F`-derived measurable time set, and a
missing row/root identity is HOLD.  Thus `E_FV` is now an actual empirical
envelope around the declared `x_FV=q_MR+F`, augmented by converted algorithmic
residuals.

### 2.4 Physical-strip operator

The strip contract uses physical widths rather than cell counts.  The overlap
formula gives a fraction in `[0,1]` for boundary-straddling cells, and

```text
omega_union = omega_M + omega_R - omega_M*omega_R
```

counts midpoint/relative-strip intersections exactly once.  The stored
quantity is unnormalized killed probability mass.  Four face values and the
union are required at the full frozen time set, with union mass at most
`1e-6`.

Crucially, v2 explicitly deletes the invalid comparison theorem: an unbounded
free-OU tail is only an optional plausibility diagnostic.  It is neither an
upper bound on the reflected killed FV strip mass nor part of a gate or
uncertainty envelope.

### 2.5 Joint-power and freeze-boundary logic

The powered event is the conjunction of every mandatory scientific,
FV--MC-agreement, realized-precision, pool-consistency, and closure gate.  For
each candidate common `N`, v2 requires exact acceptance sets or conservative
atomic sufficient events and a failure union bound `beta_all(N)` satisfying

```text
1 - beta_all(N) >= 0.90.
```

This is a valid dependence-agnostic lower bound on the probability that the
entire experiment passes.  It repairs the earlier per-statement `0.90` rule.
The frozen multiple is `200,000`, the hard cap is `50,000,000` trajectories
per deduplicated control across both pools, and infeasibility is HOLD.  No
optional top-up is permitted.

Information flow is also now one-way:

- `T0` freezes selection and statement algorithms without Stage-A/B values;
- `T1` only substitutes an independently audited Stage-A result to freeze
  exact control bytes, roles, and expected statements before Stage B;
- `T2` only substitutes independently audited Stage-B values to instantiate
  cuts, windows, FV references/envelopes, tolerances, alpha tails, sample size,
  and exact MC numerics; and
- `T3` runs once, with identical-ID operational retries only.

The control/statement skeleton cannot change at `T2`.

## 3. Round-57 finding-by-finding resolution

| Round-57 finding | v2 repair | status |
|---|---|---|
| **P0-1:** no `E_FV` matrix for every MC control | all eight MC-promoted controls run on all eight configurations; cusp also runs on all eight; six on-fold nodes run on the first seven; 114-row/no-duplicate workload recomputed exactly | **CLOSED** |
| **P0-2:** edge differences are not an envelope about `MR+F` | `x_FV=q_MR+F`; `E_FV=max_g |q_g-q_MR+F|` plus converted residual, using identical time sets | **CLOSED** |
| **P1-1:** boundary strips mechanically undefined and invalid free-law inequality | exact physical partial-cell overlaps, inclusion--exclusion union, fixed time set and `1e-6` gate; invalid reflected-FV versus unbounded-free-OU inequality explicitly forbidden | **CLOSED** |
| **P1-2:** only per-statement power | powered event is the conjunction of all gates; exact/conservative atomic failure calculation requires `1-beta_all>=0.90` | **CLOSED** |
| **P1-3:** `T1/T2` can change controls/statements | `T0` freezes algorithms, `T1` only instantiates Stage-A controls/statements, `T2` only instantiates Stage-B MC numerics; missing values are HOLD | **CLOSED** |
| **P2-1:** endpoint and alpha ordering ambiguous | half-open binary64 intervals, exact `T=100` rule, canonical control/statement/tail order, rational alpha enumeration, and integer closure are frozen | **CLOSED** |
| **P2-2:** optional second solver can cause claim drift | narrow finite-volume numerical-cusp/event-law claim is explicit; all continuum/PDE/global-count flags remain false | **CLOSED** |

## 4. Retained Round-54 safeguards

The v2 repair preserves rather than weakens the earlier safeguards:

- universal `Lambda=0.35` with finite/nonnegative/unit-sum and support checks;
- one global `alpha_FWER=0.05` ledger across all controls and both pools;
- two disjoint scientific pools, with the exact-ID rerun treated only as a
  reproducibility duplicate;
- no top-up, no new IDs after counts, no moved cuts/windows, and no dropped
  controls;
- physical conservation, positivity, topology, odd/even, box, `MR+F`, and
  margin-consumption gates;
- two independently pinned implementation/auditor chains; and
- the focused claim boundary rather than a continuum/PDE fourth-jet claim.

## 5. Open-count and execution decision

For the seven Round-57 design defects, and for internal consistency of this v2
contract, the post-repair ledger is

```text
open design P0 = 0
open design P1 = 0
open design P2 = 0
```

This does **not** mean the experiment is ready to run.  The following are
unfilled one-way freeze slots or future implementation/evidence dependencies,
not hidden assumptions silently counted as design passes:

1. an admissible independently audited Stage-A PASS must be supplied at `T1`;
2. exact Stage-A-derived control bytes and the role/deduplication map do not yet
   exist in this design file;
3. the deterministic v2 producer/protocol/manifest/tests/pre-result auditor
   chain has not been created and audited here;
4. no `GO-FV-STAGE-B` result exists or is asserted here;
5. exact Stage-B-derived cuts, windows, `x_FV`, `E_FV`, tolerances, alpha rows,
   and powered `N` can only be instantiated at `T2`; and
6. the production off-lattice v2 chain, scientific pools, exact-ID rerun, and
   independent post-result audit have not been executed.

Therefore the correct status is:

```text
design status    = GO-DESIGN
execution status = HOLD-EXECUTION
science status   = NOT RUN / NOT INSPECTED
```

No producer, manifest, or manuscript should point to this design as scientific
evidence until the entire freeze ladder passes.
