# Round 62: independent adversarial attack on the Stage-B v2 design

Date: 2026-07-14  
Role: independent result-blind contract, provenance, geometry, and inference
audit  
Verdict: **HOLD-DESIGN / HOLD-EXECUTION / GO-AFTER-V3-REPAIR**

## 1. Scope and non-execution boundary

This round audits the design in
`notes/positive_b_stage_b_validation_design_v2.md`, the attacks and repair
claims in Rounds 54, 57, and 58, and the directly relevant frozen Stage-A,
positive-point, and off-lattice design anchors.  It specifically attacks:

1. the 15-role/eight-configuration matrix and its workload arithmetic;
2. fixed physical controls versus grid-specific cusp/fold solutions;
3. complete FV coverage and the `MR+F`-centred error envelope;
4. the physical partial-cell strip operator;
5. the global-alpha and joint-power contracts;
6. the `T0--T3` information boundary and hash provenance; and
7. the maximum claim licensed after eventual scientific passes.

No Stage-B finite-volume configuration was evaluated.  No scientific
trajectory was generated.  No hidden or canonical Stage-A/Stage-B result was
opened.  No producer, manifest, protocol, design, result, manuscript, or audit
program was modified.  The only repository change from this round is this
report.

The attacked snapshot is:

| role | repository path | SHA-256 |
|---|---|---|
| Stage-B v2 design | `notes/positive_b_stage_b_validation_design_v2.md` | `8d64c54c2d4727583dc9ee513fc3fc58af57835283b68111a648f6ef33f63f84` |
| Round-54 attack | `audits/round_54_stageb_design_attack.md` | `5de663b0db0147a27b7af8901f3ae0a26a72a333ab5f95fbd2610e92e9294265` |
| Round-57 re-audit | `audits/round_57_stageb_independent_reaudit.md` | `953bb602c29bb0ef2556e1a3ce63c0a309a4f298701c4ec7e6da9937194f0ab3` |
| Round-58 self-audit | `audits/round_58_stageb_v2_design_resolution.md` | `7f05c922a1835face49d58f0dfe06196e5a303b2909a4fc3f55fc2cd3d760d43` |
| allocation-cusp promotion design | `notes/positive_b_allocation_cusp_promotion_design.md` | `ad072e83004ea3e3b5c3d01a58a872b5aedca74d13400fa04d6f917d4a06d1f5` |
| allocation-cusp Stage-A v2 protocol | `notes/positive_b_allocation_cusp_discovery_protocol.md` | `fa26995c0af9824dbba7231ace4fc08cef9664cb3bd09021a5cb90c1eed393e0` |
| allocation-cusp Stage-A v2 manifest | `artifacts/data/positive_b_allocation_cusp_discovery_manifest.json` | `492922112d14ee62f610cfc3508f7286ff7d64ab28e5b7ea7b3fdff041ad78eb` |
| Stage-A post-result no-cycle protocol | `notes/positive_b_allocation_cusp_postresult_audit_protocol_v1.md` | `98edbadf0fa78afbe8e88d44f1377ac1f68f3ce348756153ce0fecd5025f1ebe` |
| off-lattice method design | `notes/off_lattice_doi_thinning_design.md` | `349541a954e665d0a68b3989e6f38f5edc725b00f77e4811147c1de262fc7961` |
| fixed positive-point protocol | `notes/positive_b_broad_four_slab_protocol.md` | `f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00` |
| fixed positive-point manifest | `artifacts/data/positive_b_broad_four_slab_manifest.json` | `955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c` |

All printed hashes above match the current regular files.  All 18 Stage-A
manifest pins and all 14 fixed-positive-point manifest pins were independently
rehash-checked and matched.  This verifies the available input snapshot, not a
scientific outcome.

## 2. Executive decision

The Round-58 repair correctly closes the *arithmetic* and fixed-control
versions of the Round-57 defects:

- all eight MC-promoted controls now have all eight FV configurations;
- the no-duplicate workload is 114 logical rows and `352,006,020`
  state-law cells per deterministic execution;
- `E_FV` is a genuine `MR+F`-centred empirical envelope for a fixed control and
  fixed measurable time set;
- physical partial-cell strip weights are mechanically valid;
- `Lambda=0.35` is a valid allocation-uniform domination rate;
- the alpha-family totals sum to `0.05`; and
- the proposed failure-union-bound construction can, once fully specified,
  certify joint rather than per-gate power.

The design is nevertheless not executable as written.  Three new P0 defects
remain:

1. the contract treats grid-specific implicit cusp/fold solutions as if they
   were immutable physical-control byte strings;
2. the claimed off-lattice fold-side topology changes have no statistical
   predicate on the lower-mode side; and
3. the off-fold control selection requires new mesh-65/97 evaluations not
   contained in the audited Stage-A result, contradicting the `T1` information
   boundary.

There are also three P1 and two P2 defects.  They do not invalidate the good
arithmetic, strip, rate, or fixed-control envelope checks.  They do invalidate
Round 58's `open design P0=P1=P2=0` conclusion.

The independent open ledger is:

```text
P0 = 3
P1 = 3
P2 = 2
```

The correct decision is therefore `HOLD-DESIGN`, not merely
`GO-DESIGN / HOLD-EXECUTION`.

## 3. Independent checks that pass

### 3.1 Logical roles, configurations, and workload

The role count is exactly

```text
cusp                         1
fixed positive-B anchor      1
phase representatives        3
on-fold continuation nodes   6
off-fold controls             4
total                        15
```

The eight state counts independently recompute as:

| configuration | tensor dimensions | state count |
|---|---:|---:|
| `O113/Base` | `113^3` | `1,442,897` |
| `E128/Base` | `128^3` | `2,097,152` |
| `O129/Base` | `129^3` | `2,146,689` |
| `O161/Base` | `161^3` | `4,173,281` |
| `M+` | `166*129*129` | `2,762,406` |
| `R+` | `129*172*129` | `2,862,252` |
| `MR+` | `166*172*129` | `3,683,208` |
| `MR+F` | `207*215*161` | `7,165,305` |

The first seven sum to `19,167,885`.  With 15 logical roles on each of those
configurations and nine on `MR+F`,

```text
logical rows                         = 7*15 + 9 = 114
first-seven state-law cells          = 15*19,167,885 = 287,518,275
MR+F state-law cells                 = 9*7,165,305   =  64,487,745
state-law cells per execution        =                 352,006,020
two nominal deterministic executions =                704,012,040
```

These numbers are correct for the no-byte-duplicate, one-base-law-per-row
accounting convention.  P0-1 and P2-2 below explain why they are not yet a
complete physical-row or resource accounting contract.

### 3.2 Complete fixed-control FV coverage

For the eight fixed MC-promoted logical controls, the matrix now contains every
odd/even, mesh, separate-box, combined-box, and `MR+F` row.  The cusp also has
eight configuration roles; the six on-fold continuation roles have the first
seven configurations.  Thus the specific Round-57 missing-off-fold-row defect
is closed.

For a *fixed* physical control and a scalar estimand integrated on the same
`MR+F`-derived measurable time set, the v2 formula

\[
 E_{FV}=\max\left\{\max_g|q_g-q_{MR+F}|,\max_g r_{{\rm alg},g}\right\}
\]

is a real reference-centred envelope.  Reapplying the Round-57 counterexample

```text
q_O129 = 0, q_O161 = -1, q_MR+ = 1, q_MR+F = 2
```

returns at least three because `|q_O161-q_MR+F|=3`; it cannot return the false
edge-increment value one.  Keeping the local edge differences only as
diagnostics is correct.

### 3.3 Partial-cell boundary strips

The cell-overlap definition

\[
 M_S(t)=\sum_i p_i(t)|C_i\cap S|/|C_i|
\]

is the correct piecewise-constant FV mass of a physical strip.  For rectangular
tensor cells, the union formula

\[
 \omega_{\rm union}=\omega_M+\omega_R-\omega_M\omega_R
\]

counts each midpoint/relative-strip intersection once.  A geometry-only check
on all eight configurations found every union weight in `[0,1]` and agreement
between the weighted grid volume and the analytic union volume fraction to at
most `3.34e-16` absolute.

The v2 design also correctly removes the invalid statement that reflected
killed-FV boundary mass is pointwise bounded by an unbounded free-OU strip
mass.  The latter is now only a plausibility diagnostic.

### 3.4 Universal thinning rate

For finite nonnegative unit allocations and the fixed disjoint supports,

\[
 {0.01\over 1\times0.04}e^{1/3}
 =0.3489031062715224<0.35.
\]

The strict margin is `0.0010968937284775993`.  Thus `Lambda=0.35`, together
with pre-ID physical-input validation and abort-on-rate-violation semantics, is
valid for the complete allocation simplex.  Reusing the POC's control-specific
`Lambda=0.13` would not be valid; v2 does not reuse it.

### 3.5 Alpha and joint-power architecture

The family totals recompute as

```text
0.010 + 0.015 + 0.015 + 0.010 = 0.050.
```

If every actual one-/two-sided statement is enumerated exactly once, the stated
Bonferroni ledger controls FWER without an independence assumption.  Treating
the exact-ID rerun as zero-alpha duplicate evidence is correct.

Likewise, an outward-rounded union bound over atomic failure events whose joint
complement implies every mandatory gate is a valid dependence-agnostic power
certificate.  Requiring `1-beta_all(N)>=0.90`, using `N/2` in each pool,
selecting the smallest `200,000` multiple, fixing `N_max=50,000,000`, and
forbidding top-up repairs the earlier per-statement-power error in principle.
P0-2 and P1-2 show that the current statement and atom sets are not yet fully
defined.

### 3.6 Claim boundary

The v2 claim discipline is correct.  Even an eventual dual pass can establish
only a mesh/alignment/box-stable **finite-volume numerical allocation cusp**
plus independently preserved unbounded-process finite-resolution event-law
features.  It does not establish a rigorous FV continuum limit, PDE cusp,
fourth off-lattice jet, or global exact mode count.  The corresponding strong
flags correctly remain false.

## 4. New P0 findings

### P0-1 — immutable control bytes conflict with grid-specific cusp/fold solves

The design currently uses one word, “control,” for two mathematically different
objects.

At `T1`, it requires exact binary64 physical-control bytes and an immutable
map from those bytes to every role and deterministic row
(`positive_b_stage_b_validation_design_v2.md`, lines 90--105).  Section 3 then
places the corrected cusp and six on-fold continuation nodes in the same
15-role control map (lines 146--167).  The final GO contract says all eight
configurations use unchanged controls (lines 595--604).

The frozen upstream contract requires the opposite operation for cusp and fold
roles.  The allocation-cusp promotion design explicitly permits re-solving the
same equations for **mesh-dependent cusp and fold coordinates**
(`positive_b_allocation_cusp_promotion_design.md`, lines 540--543), and Stage B
must solve the cusp and correct the six fold nodes on every required
configuration (lines 570--582).  The Stage-A v2 protocol repeats that Stage B
may re-solve the same equations but may not refit fixed physical controls
(`positive_b_allocation_cusp_discovery_protocol.md`, lines 306--310).

Those two requirements cannot both hold:

- if cusp/fold allocation bytes are held fixed across grids, most rows are not
  grid-specific zeros of the cusp/fold equations and cannot certify a
  mesh-stable cusp or fold; but
- if the equations are correctly re-solved on each grid, the allocation/time
  outputs change by configuration and violate the immutable control-byte and
  T1 deduplication map.

This is not a naming issue.  It determines what is being converged, which rows
can be byte-deduplicated, and whether `GO-FV-STAGE-B` is a cusp result at all.

**Required v3 repair:** split the role schema before any Stage-B value exists.

1. **Frozen physical-allocation roles:** anchor, three representatives, and four
   off-fold controls.  Their exact physical bytes remain identical on every
   required grid and may enter the byte-deduplication map.
2. **Grid-specific implicit-solution roles:** cusp and six on-fold continuation
   nodes.  Freeze equations, chart, seed/node ID, branch orientation,
   correction map, trust region, solver limits, matching rule, and failure
   semantics at `T1`; serialize the solved `(t,theta,w)` separately for every
   configuration at Stage B.  “No refit” means unchanged equations and role
   identity, not unchanged solution bytes.

The v3 workload must continue to report 114 logical role--configuration rows,
but it must not claim that every implicit-solution physical byte string was
known or deduplicated at `T1`.  A separate uncertainty contract for these
implicit solutions is required by P1-1.

### P0-2 — the off-lattice fold-side change has no statistical predicate

The root-to-window transform creates contrasts only for roots retained at that
control.  A control with `m=1` has one root/window, one basin, and zero
peak--valley contrasts.  The design explicitly says that a one-mode control has
zero contrast rows (`positive_b_stage_b_validation_design_v2.md`, lines
399--450).

Nevertheless, the next paragraph adds an immutable assertion that each
off-fold pair has different adjacent topology (lines 443--447), and
`GO-OFF-LATTICE` requires both fold-side changes to pass (lines 608--614).  No
measurable statistic, sign, confidence row, or acceptance set is defined for
the missing local max--min pair on the lower-mode side.

For example, on a one-to-two fold pair, all current lower-side statements can
pass after checking one window, one basin, survival, and FV agreement.  They do
not exclude the same additional finite-resolution max--min structure that the
higher-side control is meant to exhibit.  Uniform DKW/FV agreement at the
declared tolerance is not, by itself, a topology test.  Therefore “the two
topologies differ” is presently a label, not an enumerated scientific event.
It cannot be assigned alpha, included in `beta_all`, or independently audited.

This defect was already identified as an unresolved production blocker in the
off-lattice POC audit: fold-side controls **and their expected contrast
patterns** had to be frozen (`round_37_off_lattice_design_attack.md`, lines
247--255).  Freezing only the controls does not close the pattern obligation.

**Required v3 repair, choose one before Stage B:**

1. For each fold pair, freeze a common pair-level set of equal-width time
   windows, derived without MC data from one fixed fold reference, and one or
   more signed finite-resolution functionals evaluated on **both** sides.
   Freeze the expected opposite signs or a signed difference-of-contrasts,
   strict deterministic margins, same-time-set FV values, `E_FV`, deterministic
   `tau`, confidence construction, tail rows, alpha allocation, and power atoms.
   The common predicate must remain meaningful when one side has no retained
   stationary pair.
2. Otherwise delete “both fold-side topology changes” from `GO-OFF-LATTICE`
   and narrow the claim to preservation of the individually predeclared
   positive contrasts on the higher-mode controls.  Do not call that a
   validated fold-side modality transition.

MC still must not be used to claim global exact mode counts or a fourth jet.

### P0-3 — `T1` off-fold selection needs unaudited new Stage-A-mesh values

The `T1` information contract says it may read only the independently audited
Stage-A result, evidence, and post-result audit, and may not read Stage-B values
(`positive_b_stage_b_validation_design_v2.md`, lines 83--110).

However, the off-fold selection algorithm then tests up to three symmetric
offsets per branch and chooses the first for which **both mesh 65 and mesh 97**
show the opposite topology with all discovery margins (lines 169--195).  The
current frozen Stage-A v2 protocol contains cusp homotopy, branches, six
on-fold comparison nodes, and the finite 32-control phase search, but it does
not contain these 12 branch-normal offset candidates.  Its formal Stage-A
result therefore cannot supply the required candidate evaluations.  Nor can
the sign topology be “copied from the audited Stage-A result,” as line 194
claims, because those physical controls were never among its frozen rows.

Running new mesh-65/97 evaluations after the Stage-A audit and then selecting
the first passing offset would create a new scientific selection stage.  The
current v2 chain gives that stage no pre-run manifest, canonical result schema,
two-process evidence, or pre-frozen independent auditor.  Pinning the final
four weights only after those values are seen would be a fail-open provenance
boundary.

**Required v3 repair, choose one:**

1. If Stage A has not run, create a new Stage-A version that freezes and
   serializes every candidate offset row on both discovery meshes, with the
   already fixed first-passing selection rule and post-result auditor.
2. Create a separate result-blind `T1-selection` producer/protocol/manifest and
   no-cycle post-result auditor, all frozen and independently attacked before
   evaluating any candidate offset.  The later Stage-B manifest must pin its
   canonical result and audit.
3. Use only audited Stage-A saved objects and an entirely analytic,
   byte-deterministic normal-form rule that needs no new mesh evaluation.  In
   that case delete the mesh-65/97 candidate-pass clause rather than silently
   evaluating it.

Whichever route is used, the topology labels must come from the resulting
audited selection object, not be described as already present in the current
Stage-A result.

## 5. New P1 findings

### P1-1 — no mesh/box uncertainty rule is defined for implicit cusp/fold outputs

The repaired `MR+F`-centred `E_FV` is defined only for an MC-promoted fixed
control and a common measurable event-law time set
(`positive_b_stage_b_validation_design_v2.md`, lines 309--365).  The cusp is
not MC-promoted, and its `(t_c,theta_c,w_c)`, fourth jet, response singular
values, rank, and determinant are grid-specific implicit-solution quantities.
The on-fold nodes are also implicit solutions and are absent from `MR+F`.

Yet `GO-FV-STAGE-B` requires cusp, fold, rank, odd-refinement, parity, box, and
`MR+F` challenges to pass (lines 593--606).  The design says the old scientific
floors/caps remain, but it does not define the v2 cross-configuration envelope,
reference, vector norm, or node matching for these implicit outputs.  Passing a
per-grid nondegeneracy floor is not enough: eight well-conditioned cusps at
substantially different physical allocations would not demonstrate a stable
single numerical cusp.

**Required repair:** after separating the role classes in P0-1, freeze:

- the exact matched cusp output vector and scale/metric;
- `MR+F`-centred coordinatewise and norm envelopes, or an explicitly bounded
  pairwise diameter, over all eight cusp solutions;
- the exact absolute caps and quarter-margin rules for every claimed cusp jet,
  singular value, ratio, and determinant;
- branch/node correspondence by saved signed Stage-A role ID; and
- a first-seven reference or pairwise-diameter rule for each on-fold solution,
  since no `MR+F` on-fold row is scheduled.

Missing, mismatched, or branch-swapped implicit solutions must be structural
HOLD rows, not dropped comparisons.

### P1-2 — the `T0` statistical transformation still has selectable degrees of freedom

The design uses `E_MC` in the cross-method inequality but never defines it for
basin probabilities, window probabilities, or contrasts (lines 367--393).  It
also freezes only inequalities for `tau_M`, `tau_D`, and `tau_p`, leaving a
continuum of allowed tolerances at `T2`.  For vectors it asks for a
“predeclared vector norm” without selecting the norm (lines 353--356).

The power section similarly permits an exact joint calculation “when
implemented” and otherwise an unspecified choice of atomic binomial sufficient
events (lines 542--570).  Different valid atomizations and interval/radius
conventions can materially change both the computed `N` and whether the
`N_max` feasibility gate passes.  They may all be conservative, so this is not
an automatic type-I error, but they are not the deterministic `T0 -> T2`
transformation claimed by the freeze ladder.

**Required repair:** before any Stage-B value exists, freeze:

1. the exact DKW and binomial/multinomial confidence constructions, tail
   conventions, and outward rounding;
2. an exact formula for every `E_MC`, including signed contrasts;
3. deterministic equalities and rounding for every `tau`, not only upper
   bounds;
4. every scalar/vector norm and algebra-residual conversion;
5. one ordered gate-to-atom implication algorithm with a deterministic fallback
   rule; and
6. the exact statement/tail cardinality calculator and mutation tests.

Then `T2` may substitute audited FV values only.  It may not select the
interval, atomization, norm, or largest convenient tolerance after inspecting
those values.

### P1-3 — the future auditor provenance graph does not explicitly break the hash cycle

Section 12 lists each future scientific protocol, producer, tests, manifest,
auditor, and auditor tests, and requires them to be pinned before execution
(`positive_b_stage_b_validation_design_v2.md`, lines 627--650).  It does not
list an external no-cycle audit protocol or state which immutable object pins
the auditor after the manifest hash exists.

The existing Stage-A chain shows the necessary pattern explicitly:

- the scientific manifest pins producer/tests/scientific protocol but not its
  independent auditor;
- the auditor hard-codes the externally frozen manifest hash; and
- a separate result-blind post-result-audit protocol records the manifest,
  auditor, and auditor-test hashes without being pinned back by the manifest
  (`positive_b_allocation_cusp_postresult_audit_protocol_v1.md`, lines 6--27).

Without the same directed graph, “pin manifest and auditor” can become an
impossible hash cycle or leave the auditor mutable after science.

**Required repair:** add one separate no-cycle post-result-audit protocol to
each future chain.  Each must be frozen and independently attacked before the
corresponding scientific result exists, state the one-way pin graph, record the
manifest/auditor/auditor-test hashes, and forbid the scientific manifest from
pinning back to it.

## 6. New P2 findings

### P2-1 — branch-normal and binary64 allocation serialization need one exact convention

The phrase “nearest signed `|t-t_c|=0.75`” mixes a sign with an absolute value,
and “allocation-plane unit tangent in the frozen Helmert chart” does not say
whether the tangent is the normalized theta projection of the saved oriented
three-dimensional pseudo-arclength null vector or a finite difference between
saved nodes.  Those choices can produce different normals and therefore
different physical control bytes.

The printed columns of `P` also sum in decimal to `3e-16` and `1e-16`, not
exactly zero, so an undefined demand for binary64 “unit-sum” is not an exact
serialization rule even though the error is physically negligible and far
below the `Lambda=0.35` margin.

**Required repair:** identify the saved Stage-A node ID directly; freeze the
theta-projection formula, norm, zero-projection HOLD threshold, the explicit
`+pi/2` matrix, all floating evaluation/rounding steps, and either an exact
normalization rule or a finite sum tolerance with a corresponding analytic
rate bound.  Serialize both theta and weight bytes.

### P2-2 — `352,006,020` state-law cells is not a resource upper bound

The arithmetic counts one base state vector per role--configuration row.  A
cusp Newton step carries the base state plus allocation tangents and repeated
time/allocation actions; fold correction, root scanning, and Krylov iterations
multiply the work again.  The design acknowledges future resource caps but the
headline number can still be misread as total numerical volume.

**Required repair:** retain `352,006,020` under the exact label
“no-duplicate base-state cells per full row pass,” and separately freeze the
maximum augmented-vector count, Newton/fold/root evaluations, Krylov actions,
memory high-water estimate, and wall-time abort semantics.  A resource abort
must remain operational failure/HOLD, never permission to drop rows.

## 7. Complete v3 repair order

The shortest fail-closed repair is:

1. split fixed physical allocations from grid-specific implicit cusp/fold
   solutions;
2. move off-fold selection into an auditable pre-Stage-B result object;
3. define common pair-level fold-side MC predicates, or delete the fold-change
   claim;
4. freeze implicit-solution mesh/box envelopes and role matching;
5. fully specify `E_MC`, every `tau`, every norm, the confidence construction,
   and the gate-to-atom power algorithm;
6. add explicit acyclic auditor pin graphs for deterministic Stage B and
   off-lattice production;
7. close the exact branch-normal/binary64 and resource-accounting P2 items; and
8. run another independent result-blind design audit.

Only after that audit reports open `P0=P1=0` may a deterministic Stage-B
implementation package be authorized.  No finding here is permission to tune a
control, scientific threshold, time window, grid, box, or sample size after a
scientific value is observed.

## 8. Final GO/HOLD and claim boundary

### Current decision

```text
design status    = HOLD-DESIGN
execution status = HOLD-EXECUTION
science status   = NOT RUN / NOT INSPECTED
```

The 114-row arithmetic, fixed-control FV coverage, `MR+F` envelope, strip
geometry, universal `Lambda`, alpha total, and high-level joint-power route all
pass this audit.  They are necessary components of v3, not scientific results.

### GO condition after repair

`GO-DESIGN` requires a numbered v3 contract that closes all three P0 and all
three P1 findings, preserves the already passed checks, and receives a new
independent result-blind audit.  P2 closure is required before implementation
freeze so that exact control bytes and resource caps are reproducible.

### Maximum later scientific wording

Even after a repaired deterministic Stage B and off-lattice production both
pass, the strongest supported wording remains:

> a mesh-, alignment-, and box-stable finite-volume numerical allocation cusp,
> with predeclared finite-resolution event-law features independently preserved
> by the unbounded off-lattice Doi process.

The phrase “fold-side modality changes” may be added only if P0-2 is repaired
with a common, powered, simultaneous, two-sided-control statistical predicate.
No repair in this report licenses a rigorous continuum/PDE cusp, an
off-lattice fourth jet, or a global exact mode count.

## 9. Read-only verification commands

The following classes of commands were used:

```text
shasum -a 256 <design/audit/protocol/manifest paths>
```

All snapshot hashes matched.

```text
python3 <small JSON pin-map rehasher>
```

All 18 Stage-A manifest pins and all 14 fixed-point manifest pins matched
regular report-local files.

```text
python3 <integer role/configuration/state-count recomputation>
```

It returned `114`, `352006020`, and `704012040` for the declared nominal
counts.

```text
python3 <geometry-only partial-cell strip overlap check>
```

All eight configurations had union weights in `[0,1]`; the largest analytic
union-volume discrepancy was below `3.34e-16`.

No scientific producer, auditor, formal manifest entry point, FV solve, or
Monte Carlo path generator was run.
