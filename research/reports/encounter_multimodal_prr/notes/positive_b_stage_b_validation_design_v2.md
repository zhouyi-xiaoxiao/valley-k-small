# Positive-`B` Stage-B validation design v2

Date: 2026-07-14  
Status: **GO-DESIGN / HOLD-EXECUTION**  
Scope: result-blind deterministic mesh/parity/box validation followed by a
separately frozen off-lattice event-law validation

## 0. Purpose, evidence boundary, and non-execution declaration

This document replaces the incomplete Stage-B contract described in Rounds 54
and 57.  It freezes an executable design; it is not a scientific result and
does not authorize a scientific run.

This design was written without opening a hidden or canonical positive-`B`
result, without evaluating a Stage-B finite-volume configuration, and without
generating a production Monte Carlo trajectory.  It does not modify or
supersede any producer, manifest, scientific result, post-result auditor, or
manuscript.  The following files are design evidence anchors only:

| role | repository path | SHA-256 |
|---|---|---|
| first Stage-B attack | `audits/round_54_stageb_design_attack.md` | `5de663b0db0147a27b7af8901f3ae0a26a72a333ab5f95fbd2610e92e9294265` |
| independent Stage-B re-audit | `audits/round_57_stageb_independent_reaudit.md` | `953bb602c29bb0ef2556e1a3ce63c0a309a4f298701c4ec7e6da9937194f0ab3` |
| allocation-cusp promotion design | `notes/positive_b_allocation_cusp_promotion_design.md` | `ad072e83004ea3e3b5c3d01a58a872b5aedca74d13400fa04d6f917d4a06d1f5` |
| off-lattice method design | `notes/off_lattice_doi_thinning_design.md` | `349541a954e665d0a68b3989e6f38f5edc725b00f77e4811147c1de262fc7961` |

Execution remains on HOLD until all upstream inputs and the two separately
pinned implementation/auditor chains in Section 12 exist and pass their own
pre-run audits.  A design GO must never be serialized as a scientific GO.

## 1. Claim boundary

The strongest claim licensed by an eventual pass of both stages is:

> a mesh-, alignment-, and box-stable **finite-volume numerical allocation
> cusp**, with its promoted finite-resolution event-law features independently
> preserved by the unbounded off-lattice Doi process.

The following flags remain false under this route:

```text
continuum_cusp_verified = false
PDE_cusp_verified = false
rigorous_FV_continuum_limit = false
global_exact_mode_count_verified = false
off_lattice_fourth_jet_verified = false
```

Off-lattice Monte Carlo owns survival, fixed basin masses, fixed-window
probabilities, and signed finite-resolution contrasts.  The FV calculation
owns roots, curvatures, fourth time jets, mixed allocation jets, rank, and the
numerical cusp.  Monte Carlo is not used to infer a fourth jet or the absence
of every additional mode.  A stronger continuum/PDE-cusp statement requires
a separately converged independent deterministic solver or a rigorous
a-posteriori/analytic error certificate for roots, jets, rank, and determinant.

## 2. Immutable freeze ladder

The freeze is a one-way state machine.  Each transition records the complete
input and output hashes; a failed transition is a finite structural HOLD, not
permission to edit the preceding state.

### `T0`: design skeleton — frozen by this document

Allowed knowledge is limited to disclosed pilots and the existing design
documents.  No Stage-A or Stage-B scientific value is substituted at `T0`.
This document freezes:

1. the control-role and selection algorithms in Section 3;
2. the eight FV configurations and row-allocation rule in Section 4;
3. the physical-strip operator and gate in Section 5;
4. the common-time-set transformation and reference-centred envelope in
   Section 6;
5. the variable-topology statement templates and binary endpoint convention
   in Section 7;
6. the universal `Lambda=0.35`, global-alpha, joint-power, two-pool, and
   no-top-up rules in Sections 8--10; and
7. the claim and failure semantics in Sections 1 and 11.

Changing one of these algorithms creates a new numbered design and requires a
new independent result-blind audit before any Stage-B value is computed.

### `T1`: Stage-A substitution and exact-control freeze

`T1` may occur only after an independently audited Stage-A PASS.  It may read
only that pinned Stage-A result, its evidence, and its post-result audit.  It
must not read a Stage-B value.  The deterministic transformation frozen at
`T0` is applied once to:

- substitute the audited cusp, branch orientations, branch nodes, phase
  representatives, and topology labels;
- construct the four exact fold-side controls by Section 3.2;
- freeze the exact binary64 physical-control bytes;
- freeze the immutable map

  ```text
  control bytes -> control hash -> every role label -> expected topology
                -> required deterministic rows -> MC statement template
  ```

- enumerate every required control--configuration row and the no-duplicate
  and byte-deduplicated workloads; and
- pin the deterministic Stage-B code, tests, protocol, manifest, result
  schema, auditor, adversarial auditor tests, resource caps, and two-process
  execution contract.

An unavailable Stage-A value, failed Stage-A audit, failed control selection,
byte ambiguity, missing role, or unexpected exact duplicate is
`HOLD-T1`.  It is not permission to choose another node, offset, representative,
or topology statement.

### `T2`: audited Stage-B substitution and exact MC-numerics freeze

`T2` may occur only after `GO-FV-STAGE-B` and its independent post-result
audit.  The exact controls and statement templates frozen at `T1` are
immutable.  `T2` may only substitute audited Stage-B numerical values into the
algorithms frozen at `T0`:

- `MR+F` roots and the resulting basin cuts and window widths;
- every same-time-set FV integral, `x_FV`, `E_FV`, and algebra/root residual;
- every positive method-discrepancy tolerance;
- the fully enumerated alpha-per-tail ledger;
- the powered common `N`, the two exact pool ranges, chunk ranges, and
  scientific ID namespace; and
- engine/package hashes, the exact-ID rerun namespace, failure policy, result
  schema, and pre-frozen post-result auditor chain.

No control, role, expected topology, statement type, root-selection rule,
window rule, alpha-family total, power target, `Lambda`, or scientific
threshold may change at `T2`.  A missing root, changed topology, nonpositive
tolerance, failed FV row, or infeasible power cap is `HOLD-T2`; the offending
control or statement cannot be dropped.

### `T3`: one scientific execution

After the complete `T2` hash exists, execute the two disjoint scientific pools
once, without inspecting partial counts for design decisions.  An operational
retry may repeat only the identical failed/incomplete trajectory-ID range under
the pre-frozen retry rule.  It may not allocate a new ID.  The exact-ID rerun
is a reproducibility duplicate and contributes no new evidence or alpha.

## 3. Frozen control construction and role map

### 3.1 Logical roles

At `T1`, instantiate these 15 logical roles:

| group | logical roles | count |
|---|---|---:|
| cusp | corrected cusp control | 1 |
| original anchor | exact bridge-selected positive-`B` anchor | 1 |
| phase representatives | exact one-, two-, and three-mode representatives | 3 |
| on-fold continuation | nodes nearest signed `|t-t_c|=0.25,0.50,0.75` on each of two oriented branches | 6 |
| off-fold controls | two symmetric sides of one frozen node on each branch | 4 |
| **total** |  | **15** |

The MC-promoted set is the anchor, the three phase representatives, and the
four off-fold controls: eight logical roles.  The cusp is additionally
claim-critical on `MR+F` but is not an MC event-law control.  The six on-fold
nodes are deterministic continuation checks only.

Every role remains in the result schema.  Exact physical controls may be
computed once only when their serialized binary64 weight vectors, geometry,
budget, and all other physical inputs are byte-identical.  Equality within a
tolerance is not deduplication.  A deduplicated row must retain every role
label and the one-to-many role map.  Duplicate discovery after `T1` is a
structural failure.

### 3.2 Result-blind fold-side selection algorithm

For each of the two oriented Stage-A fold branches:

1. select the accepted on-fold node nearest signed `|t-t_c|=0.75`; ties are
   resolved by smaller normalized fold residual and then earlier acceptance
   index;
2. form the allocation-plane unit tangent in the frozen Helmert chart;
3. rotate the tangent by `+pi/2` in the frozen chart orientation and normalize
   it to obtain the signed normal `n_b`;
4. test symmetric offsets in the immutable order
   `{0.005, 0.010, 0.020}`:

   \[
     w_{b,-}(\delta)=w_b-\delta n_b,
     \qquad
     w_{b,+}(\delta)=w_b+\delta n_b;
   \]

5. choose the first offset for which both controls are finite, nonnegative,
   unit-sum, have minimum weight at least `0.03`, and both Stage-A discovery
   meshes 65 and 97 show the predeclared opposite adjacent topology with every
   unchanged discovery margin passing.

If no offset passes, the outcome is `HOLD-T1`.  The sign labels are geometric;
the topology attached to each sign is copied from the audited Stage-A result.
Stage B confirms the four exact byte strings and may not move them.

## 4. Complete FV validation matrix

### 4.1 Configurations

The transverse coordinate remains periodic with the unchanged physical width.
The deterministic configurations are:

| label | midpoint box/cells | relative-parallel box/cells | transverse cells | state count |
|---|---|---|---:|---:|
| `O113/Base` | `[-0.25,1.85] / 113` | `[-1.8,1.8] / 113` | 113 | `1,442,897` |
| `E128/Base` | `[-0.25,1.85] / 128` | `[-1.8,1.8] / 128` | 128 | `2,097,152` |
| `O129/Base` | `[-0.25,1.85] / 129` | `[-1.8,1.8] / 129` | 129 | `2,146,689` |
| `O161/Base` | `[-0.25,1.85] / 161` | `[-1.8,1.8] / 161` | 161 | `4,173,281` |
| `M+` | `[-0.55,2.15] / 166` | `[-1.8,1.8] / 129` | 129 | `2,762,406` |
| `R+` | `[-0.25,1.85] / 129` | `[-2.4,2.4] / 172` | 129 | `2,862,252` |
| `MR+` | `[-0.55,2.15] / 166` | `[-2.4,2.4] / 172` | 129 | `3,683,208` |
| `MR+F` | `[-0.55,2.15] / 207` | `[-2.4,2.4] / 215` | 161 | `7,165,305` |

Every one of the eight MC-promoted controls is evaluated on **all eight**
configurations.  The cusp is also evaluated on all eight.  The six on-fold
continuation nodes are required on the first seven configurations.  Therefore
the first seven configurations each carry all 15 roles, while `MR+F` carries
the cusp plus the eight MC-promoted roles, for nine roles.

No on-fold control may be used as a surrogate for a physically distinct
off-fold control.  A missing control--configuration row is a global HOLD and
must be serialized as `null` with a false structural gate.

### 4.2 Independently recomputed workload

In the no-byte-duplicate case, the complete logical and physical workload per
full execution is

```text
first seven rows = 7 * 15 = 105
MR+F rows        = 1 *  9 =   9
total rows                    114

sum(first seven state counts) = 19,167,885
15 * 19,167,885                = 287,518,275
9  *  7,165,305                =  64,487,745
state-law cells per execution  = 352,006,020
two deterministic executions  = 704,012,040
```

At `T1`, compute the exact physical workload again from the byte-deduplication
map as

\[
 W=\sum_g n_g\,u_g,
\]

where `n_g` is the state count and `u_g` is the number of unique physical
controls required on configuration `g`.  Always report both 114 logical rows
and the actual unique physical row count.  The value `352,006,020` may be
reported as the executed workload only if the no-duplicate cardinalities
`u_g=15` for the first seven grids and `u_MR+F=9` are verified.

## 5. Physical partial-cell boundary-strip operator

For every non-periodic box, define four physical strips:

```text
S_M- = [M_min, M_min + 0.10] x full R_parallel x full R_perp
S_M+ = [M_max - 0.10, M_max] x full R_parallel x full R_perp
S_R- = full M x [R_min, R_min + 0.20] x full R_perp
S_R+ = full M x [R_max - 0.20, R_max] x full R_perp
```

Let `p_i(t)` be the unnormalized killed probability mass in tensor cell
`C_i`.  If the implementation stores a density, it must first multiply by the
exact cell volume.  For a strip `S`, compute

\[
 M_S(t)=\sum_i p_i(t)\frac{|C_i\cap S|}{|C_i|}.
\]

The one-dimensional overlap fractions are computed from physical faces:

\[
 \omega([a,b],[c,d])=
 {\max(0,\min(b,d)-\max(a,c))\over b-a}.
\]

For cell `i`, let `omega_M` be the sum of its disjoint lower and upper
midpoint-strip fractions, and define `omega_R` analogously.  The exact union
weight, including the midpoint/relative-strip intersections once, is

\[
 \omega_{\rm union}=\omega_M+\omega_R-\omega_M\omega_R.
\]

Record all four face masses and the union without normalization by survival.
Evaluate them for every required control/configuration at the fixed scan grid
`{k/4: k=0,...,400}`, at every saved stationary root and basin/window endpoint,
and at `T=100`.  Duplicate times are evaluated once by exact binary64 identity.
Require

```text
max over all required controls, configurations, and saved times
    M_union(t) <= 1e-6.
```

The individual faces, overlap weights, and union must be finite and
nonnegative, with the direct union integral agreeing with inclusion--exclusion
to `1e-14` absolute in non-scientific fixtures.

An unbounded free-OU tail calculation may be recorded only as a plausibility
diagnostic.  This design makes **no** claim that reflected killed FV strip mass
is bounded by unbounded free-OU strip mass.  No such inequality enters a gate,
an error envelope, or a scientific conclusion.

## 6. Common estimands and a true `MR+F`-centred FV envelope

### 6.1 One measurable time set across all grids

For each MC-promoted control `c`, apply the frozen Section 7 transformation to
the audited `MR+F` ordered root tuple to obtain one collection of measurable
time sets `A_c`: basin intervals, peak/valley windows, and the fixed survival
grid.  Every configuration integrates its own density over exactly these same
sets.  Grid-specific roots and windows remain diagnostics and are forbidden in
cross-grid estimands.

If a required configuration cannot evaluate the same set, cannot preserve the
root identity needed by the statement, or returns a nonfinite value, the row
is a structural HOLD.  It cannot be omitted from the envelope.

### 6.2 Reference-centred definition

For every scalar estimand `q(c;A)` and every MC-promoted control, define

\[
 x_{FV}(q,c;A)=q_{MR+F}(c;A),
\]

and

\[
 E_{FV}(q,c;A)=\max\left\{
   \max_{g\in\mathcal G}|q_g(c;A)-q_{MR+F}(c;A)|,
   \max_{g\in\mathcal G} r_{{\rm alg},g}(q,c;A)
 \right\},
\]

where

```text
G = {O113/Base, E128/Base, O129/Base, O161/Base,
     M+, R+, MR+, MR+F}
```

and `r_alg,g` is the independently converted algebra/root/integration residual
in the units of `q`.  Thus every promoted control has a complete odd/even,
mesh, separate-box, combined-box, and fine/large-box challenge around the
declared `MR+F` reference.

For a survival curve, compute this envelope at every time in the frozen grid
and also report its supremum.  For a vector, report coordinatewise envelopes
and the predeclared vector norm.  For a matched root, failure of root identity
is HOLD rather than an infinite or silently omitted difference.

The local differences

```text
O129--O161, E128--O129, Base--M+/R+/MR+, MR+--MR+F
```

remain mandatory diagnostics, but their maximum is not called an uncertainty
envelope and is never substituted for the reference-centred formula above.

### 6.3 Margin consumption and method discrepancy

All original scientific floors/caps remain unchanged.  For each lower-bound
gate `q>=q0`, let `d=min_g q_g-q0`; for each upper-bound gate, let
`d=q0-max_g q_g`.  Require `d>0` and

\[
 E_{FV}\le\min(E_{\rm abs},d/4).
\]

For the later MC comparison require

\[
 |x_{MC}-x_{FV}|\le E_{MC}+E_{FV}+\tau_q.
\]

The deterministic `T2` substitution must produce positive tolerances satisfying

```text
basin mass:      tau_M <= min(0.001, (M_FV - 0.005)/4)
signed contrast: tau_D <= Delta_FV/4
window prob.:    tau_p <= min(0.002, min adjacent FV probability contrast/16)
survival:        tau_S = 0.01 on the fixed grid
```

If a right-hand side is nonpositive or the FV envelope consumes the margin,
the decision is HOLD.  Tolerances are not widened.

## 7. Frozen variable-topology statement skeleton

### 7.1 Root-to-time-set transformation

For each exact control, `T1` freezes its expected number `m` of retained
maxima and the ordered alternating root roles on `[0.5,35]`.  At `T2`, the
audited `MR+F` tuple is substituted without root reselection.

For `m` retained maxima and `m-1` retained valleys:

1. use the `MR+F` valley times `v_1<...<v_{m-1}` as basin cuts;
2. create `m` event basins

   ```text
   [0,v1), [v1,v2), ..., [v_(m-1),100]
   ```

   with the obvious single interval `[0,100]` for `m=1`;
3. let `z_1<...<z_(2m-1)` be the alternating maximum/valley targets and set

   \[
   h_c=\min\left(0.4,\frac14\min_j(z_{j+1}-z_j),
                      \frac12(z_1-0),\frac12(100-z_{2m-1})\right);
   \]

4. require finite `h_c>0` and define equal-width half-open windows
   `[z_j-h_c,z_j+h_c)`; and
5. enumerate the two adjacent peak-minus-valley average-density contrasts for
   every valley, in chronological order.

The transformation is deterministic.  It cannot discard a root, choose a
different valley, widen a window, or change `m` at `T2`.  A topology mismatch
or unusable tuple is HOLD.

### 7.2 Mandatory statements per control

The immutable statement template for each MC-promoted control contains:

- one DKW simultaneous survival statement on `{k/4:k=0,...,400}` and uniform
  FV--MC agreement;
- `m` basin-mass lower bounds, `m` basin agreements, and exact closure with
  `S(100)`;
- `2m-1` individual window-probability agreements;
- `2(m-1)` positive adjacent peak--valley average-density contrasts and their
  FV--MC agreements; and
- the two-pool consistency version of every survival, basin, window, and
  contrast estimand.

For each of the two fold branches, the two fixed off-fold controls additionally
carry the immutable statement that the expected adjacent topologies differ by
the Stage-A-declared fold transition.  Fixed-window contrasts establish only
that finite-resolution pattern; they do not establish a global exact mode
count.

No required statement may be dropped after `T1`.  A one-mode control has zero
peak--valley contrast rows by construction, not by post-result deletion.

### 7.3 Binary endpoint and ordering contract

Event times equal to an internal cut are assigned to the interval on the
right.  An event at exactly `T=100` belongs to the final event basin, while
survival is `T>100`.  Windows are left-closed/right-open.  Continuous-time
probability-zero arguments do not override these binary64 counting rules.

Controls are ordered by control SHA-256 and then role label.  Statements are
ordered by

```text
control hash, statement family, chronological index, estimand name,
pooled/pool-1/pool-2, lower/upper/two-sided tail.
```

Integer basin counts plus the `T>100` survival count must equal exactly the
number of valid IDs in each pool and in the pooled sample.  Window counts are
reconstructed from the same raw event-time ledger and raw hashes.

## 8. Universal off-lattice physical bound

Every production control uses the common homogeneous candidate rate

\[
 \boxed{\Lambda=0.35}.
\]

Before consuming a scientific ID, validate finite, nonnegative, unit-sum
weights and the disjoint slab-support premise.  For all such allocations,

\[
 \|K_w\|_\infty
 \le {B\max_jw_j\over Ws}e^{1/3}
 \le {0.01\over1\times0.04}e^{1/3}
 =0.3489031062715224\ldots <0.35.
\]

Every evaluated hazard must be finite, nonnegative, and no larger than
`0.35`.  A violation aborts the full run; clipping is forbidden.  Test and
scientific trajectory-ID namespaces are disjoint.

## 9. One global FWER ledger

Freeze `alpha_FWER=0.05` across all promoted controls, both scientific pools,
and all pooled claims:

| family | total alpha |
|---|---:|
| all pooled/poolwise DKW survival bands and FV--MC survival agreements | `0.010` |
| all pooled/poolwise basin lower bounds, basin agreements, and `S(100)` agreements | `0.015` |
| all pooled/poolwise peak--valley contrasts and individual-window agreements | `0.015` |
| all pool-1 versus pool-2 consistency statements | `0.010` |
| **total** | **`0.050`** |

At `T2`, enumerate every statement and required one-/two-sided tail using the
ordering in Section 7.3, then divide its family total equally across those
tails.  A two-sided row consumes two enumerated tails.  The exact-ID rerun
receives no alpha.  The ledger must sum in exact rational arithmetic before
conversion to binary64.  Missing or duplicated rows, a total different from
`0.05`, or a family reassignment is HOLD.

Bonferroni control requires no independence assumption.  Reusing the same
sample for pooled and pool-consistency statements is allowed only because all
of those tails are included in this single ledger.

## 10. Joint all-gates power, two pools, and no top-up

### 10.1 Powered event is the complete GO event

The power target is not per statement.  At `T2`, choose one common total
sample size `N` per deduplicated physical control such that, under the audited
Stage-B planning alternatives and the exact alpha ledger,

\[
 \Pr\{\text{all mandatory scientific, FV--MC agreement, precision,
 pool-consistency, and closure gates pass}\}\ge0.90.
\]

The two equal pools partition `N`; they do not each receive `N`.  Freeze a
chunk size of `100,000` trajectories per control per pool, so `N` is a
multiple of `200,000`.  Freeze the hard cap

```text
N_max = 50,000,000 trajectories per deduplicated physical control
        across both pools.
```

The exact-ID reproducibility rerun repeats all `N` IDs but is not part of the
power calculation.

### 10.2 Executable conservative certificate

For each candidate `N=200,000,400,000,...,N_max`:

1. construct the exact integer acceptance set for every one-sample binomial or
   DKW gate, including the scientific inequality, simultaneous confidence
   limit, realized quarter-margin precision, and FV--MC agreement;
2. for multinomial basin/window/contrast gates, use an exact joint calculation
   when implemented and independently tested; otherwise construct atomic
   binomial count-deviation events whose simultaneous occurrence implies every
   required gate by interval arithmetic;
3. include pooled, pool-1, pool-2, and pool-consistency failures, with pool
   sizes exactly `N/2`;
4. evaluate each atomic failure probability under the audited Stage-B planning
   probabilities using exact binomial tails or a rigorously outward-rounded
   bound; and
5. form the conservative union bound `beta_all(N)` over **every** atomic
   failure event.

The joint-power certificate is

```text
1 - beta_all(N) >= 0.90.
```

Choose the smallest candidate satisfying it.  The package must serialize the
complete gate-to-atom implication table, every alternative, every integer
acceptance boundary, every beta term, their sum, and an independent
recomputation.  Per-gate `0.90` power is explicitly insufficient.

If no candidate at or below `N_max` passes, the outcome is `HOLD-T2`.  Claim
narrowing is allowed only in a new design completed before any scientific ID
exists; increasing `N_max`, dropping a control, changing a window, or relaxing
a gate after seeing a count is forbidden.

### 10.3 Pools, retries, and no top-up

Pool 1 and pool 2 use disjoint, precomputed trajectory-ID ranges.  A chunk
ledger is append-only and records exact ID range, input hash, output count
vector, raw event-time hash, completion state, and retry lineage.  A failed or
incomplete chunk may be recomputed only with the identical ID range and frozen
inputs before its scientific counts are inspected.  New IDs, optional top-up,
post-count sample-size changes, and silent chunk replacement are forbidden.

For each estimand, freeze simultaneous poolwise intervals and require the
absolute pool difference to be no larger than the sum of the allocated
poolwise radii plus the predeclared binary64 rounding allowance.  These gates
are included in both the alpha ledger and the joint-power certificate.

## 11. GO/HOLD semantics

### `GO-FV-STAGE-B`

Requires two byte-identical full executions and an independent post-result
audit establishing:

1. all 114 logical rows and every required physical row are present;
2. all geometry, conservation, positivity, tail, root, cusp, fold, rank,
   topology, partial-strip, and resource gates pass;
3. all eight configurations use unchanged controls and common time sets;
4. odd refinement, parity, separate-box, combined-box, and `MR+F` challenges
   pass without refitting; and
5. every promoted reference-centred `E_FV` and margin rule passes.

This sets only finite-volume mesh/alignment/box robustness flags.

### `GO-OFF-LATTICE`

Requires both frozen scientific pools, their pooled analysis, the exact-ID
rerun, and an independent post-result audit establishing the single global
alpha contract, every promoted survival/mass/window/contrast/agreement gate,
both fold-side changes, all pool-consistency gates, integer closure, and zero
physical/ledger/ID/rate failures.

This sets `independent_unbounded_event_law_validated=true` and none of the
strong continuum-cusp flags in Section 1.

### Global HOLD conditions

Any upstream audit failure; missing control, row, statement, or ID; changed
control; failed topology; nonfinite value; failed conservation or strip gate;
margin consumption; power infeasibility; alpha mismatch; rate violation;
partial-count adaptation; optional top-up; nonidentical reproducibility rerun;
or post-result audit failure is a global HOLD.

## 12. Required future implementation chains

This design does not create or authorize these files.  They must be built,
tested adversarially, frozen, and independently audited before execution:

```text
notes/positive_b_stage_b_validation_protocol_v2.md
code/positive_b_stage_b_validation_v2.py
code/test_positive_b_stage_b_validation_v2.py
artifacts/data/positive_b_stage_b_validation_v2_manifest.json
code/audit_positive_b_stage_b_validation_v2.py
code/test_audit_positive_b_stage_b_validation_v2.py

notes/off_lattice_doi_thinning_production_protocol_v2.md
code/off_lattice_doi_thinning_production_v2.py
code/test_off_lattice_doi_thinning_production_v2.py
artifacts/data/off_lattice_doi_thinning_production_v2_manifest.json
code/audit_off_lattice_doi_thinning_production_v2.py
code/test_audit_off_lattice_doi_thinning_production_v2.py
```

Both chains require full start/end pin snapshots, exact schemas, finite
structural HOLD rows, two-process/two-pool reproducibility as applicable,
final-byte rehashing, failure-atomic canonical promotion, and rollback tests.

## 13. Current decision

This v2 contract closes the seven design defects newly identified in Round 57
without inspecting a scientific outcome.  The design ledger is

```text
open design P0 = 0
open design P1 = 0
open design P2 = 0
```

Execution is nevertheless **HOLD** because no admissible Stage-A substitution,
`T1` implementation/manifest/auditor package, deterministic Stage-B PASS,
`T2` production-MC freeze, or production result is asserted here.
