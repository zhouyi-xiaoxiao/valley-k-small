# Round 54: result-blind Stage-B parity/box and off-lattice design attack

Date: 2026-07-14  
Role: independent, result-blind design audit for the positive-`B` broad-four-slab
PRR promotion path  
Verdict: **HOLD-STAGE-B / GO-ROUTE-AFTER-REPAIR**

## 1. Scope and non-execution boundary

This round addresses only the next validation layer for the physical-`d=2`,
`B=0.01` broad-four-slab family:

1. finite-volume mesh, odd/even alignment, and reflecting-box robustness; and
2. an unbounded, off-lattice Doi/Feynman--Kac thinning validation.

It did not run mesh 65, 97, 113, 128, 129, or 161; did not run an enlarged
box or a production Monte Carlo trajectory; did not open any hidden replica;
and did not read a positive-`B` scientific result.  It did not modify the
positive-`B` point producer, its manifest, the allocation producer/manifest,
or either manuscript.

The following source snapshot was read:

| role | repository path | SHA-256 |
|---|---|---|
| Stage-B promotion design | `notes/positive_b_allocation_cusp_promotion_design.md` | `ad072e83004ea3e3b5c3d01a58a872b5aedca74d13400fa04d6f917d4a06d1f5` |
| off-lattice method design | `notes/off_lattice_doi_thinning_design.md` | `349541a954e665d0a68b3989e6f38f5edc725b00f77e4811147c1de262fc7961` |
| off-lattice POC source | `code/off_lattice_doi_thinning_poc.py` | `90466d074d3b6d302143919d4160beb36109e9686312e3a33670321e4f297e9d` |
| off-lattice POC tests | `code/test_off_lattice_doi_thinning_poc.py` | `986e839ebaa7f5b56d328826312fcce1f1305a2493108e5da8d7558992cc365d` |
| Round-37 POC audit | `audits/round_37_off_lattice_design_attack.md` | `1ba9b37898bfb17d66bbaae0f6ec2a976966a6e33e6bebf73919c68f679828dd` |
| Round-50 Stage-A pre-run attack | `audits/round_50_allocation_discovery_prerun_attack.md` | `059e3f33b9a8e32cfe2e4ca26d1916dceac61b9fb53d89c77cdfdeb4a568829d` |
| fixed-point protocol | `notes/positive_b_broad_four_slab_protocol.md` | `f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00` |
| fixed-point manifest | `artifacts/data/positive_b_broad_four_slab_manifest.json` | `955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c` |
| PRR promotion audit | `audits/round_33_prr_promotion_strategy.md` | `4c2037ebcbeb2f6cc2a38ac56919d513120683a294249432cca1f615b85d4f56` |

The hashes above are evidence anchors, not authorization to execute their
scientific entry points.

## 2. Executive decision

The overall route remains correct:

> repaired Stage-A discovery -> frozen same-FV-family mesh/parity/box
> confirmation -> separately frozen unbounded off-lattice validation.

The present implementation is not ready to start Stage B.  Four P0 and seven
P1 issues below must be closed in new, separately pinned packages.  The most
important newly exposed defects are:

- `Lambda=0.13` is proved only for the original weight vector, not for the
  allocation/fold controls that Stage B is meant to validate;
- the current Monte Carlo design has no familywise inference contract for
  several controls with different numbers of peaks, valleys, and basins;
- the deterministic box design reports a boundary-strip mass but freezes
  neither a physical strip nor an acceptance threshold;
- the deterministic matrix has no fine-grid/enlarged-box corner, so mesh--box
  interaction and the exact `x_FV +/- E_FV` used by Monte Carlo remain
  ambiguous; and
- `N=6,000,000` is a pilot number supported by a nominal-count precision
  calculation, not yet the frozen powered sample size, and no no-top-up rule
  exists.

These findings change the formal Stage-B freeze, not the scientific route.

## 3. Three evidence classes that must not be conflated

### 3.1 Same-family FV confirmation is not solver independence

`O113`, `E128`, `O129`, `O161`, and the proposed box matrix all use the same
Scharfetter--Gummel tensor generator, cell-averaged catalyst profile, exact
cut-cell disk fractions, and matrix-exponential route.  They are valuable
mesh, alignment, and truncation challenges.  They are not independent
solvers.

In particular, agreement of the odd sequence and `E128` can expose
grid-locking and nonconvergence, but it cannot expose a shared sign,
quadrature, generator, or boundary-condition error.  The local explicit-CSR
and finite-difference checks are implementation audits of the same method,
not a second physical realization.

### 3.2 Off-lattice thinning is genuinely independent for event-law observables

The route in `notes/off_lattice_doi_thinning_design.md` is physically and
numerically distinct: it has exact free OU/Brownian transitions, unbounded
longitudinal coordinates, the unsmoothed disk indicator, conditional Poisson
thinning, no FV grid, no reflecting faces, no SG flux, no cut-cell fraction,
and no matrix exponential.  If the production package is independently
implemented and frozen, it is a genuine independent solver for:

- survival;
- valley-partitioned event masses;
- probabilities in fixed peak/valley time windows; and
- finite-resolution modality changes across fixed fold-side controls.

### 3.3 Monte Carlo does not certify a cusp fourth jet

Off-lattice event times cannot stably reconstruct
`f_tttt`, mixed allocation jets, projected singular values, or the cusp
Jacobian.  Those remain deterministic quantities.

Therefore the shortest focused-PRR claim is:

> a mesh/alignment/box-stable **numerical FV allocation cusp**, whose
> representative event-time modality changes, survival, and basin masses are
> independently preserved by the unbounded continuous Doi process.

This combined triangulation is a defensible minimum without a second
deterministic discretization, provided every gate below passes and the paper
uses the wording above.  It does **not** license “a continuum/PDE cusp with a
validated fourth jet.”

If the title, abstract, or theorem-facing conclusion claims the latter, one
of the following becomes a conditional P0 requirement:

1. an independent FEM/DG/spectral killed-Doi solver with independently
   integrated contact geometry and complete allocation/time sensitivities
   through fourth order; or
2. a rigorous a posteriori FV error certificate controlling the same roots,
   fourth jet, mixed jets, rank, and determinant away from zero.

No flag named `continuum_cusp_verified` or `PDE_cusp_verified` should be true
under the minimum route.  A second deterministic solver would materially
strengthen the paper, but it is not the shortest necessary addition for the
focused claim.

## 4. Severity ledger

Severity is relative to the focused-PRR route:

- **P0:** can make the physical validation false, result-informed, or
  statistically invalid, or blocks the claimed evidence class.
- **P1:** can leave mesh/box/MC uncertainty non-fail-closed or materially
  underdetermined.
- **P2:** terminology, provenance, or compute-planning weakness that does not
  alone reverse a scientific result.

Open count for an executable Stage-B package:

```text
P0 = 4
P1 = 7
P2 = 3
```

### P0-1 — Stage A is still a hard upstream no-go

`audits/round_50_allocation_discovery_prerun_attack.md` records
`HOLD-PREEXECUTION / NO-GO-65-97`, with open conservation, signed-branch,
complete-phase-screen, provenance, schema, and atomic-promotion failures.
Until a new Stage-A v2 runner/protocol/manifest and pre-frozen post-result
auditor close those findings, there is no admissible cusp, branch identity,
representative set, or comparison-node set to pin into Stage B.

**Required:** repair and re-freeze Stage A from zero; convert every strict
Round-50 `xfail` to a passing regression; execute and independently audit
Stage A only after that.  Stage B must pin the audited Stage-A result and
audit hashes.

### P0-2 — `Lambda=0.13` is not valid for the allocation control family

Section 4 of `notes/off_lattice_doi_thinning_design.md` and
`analytic_killing_bound` in `code/off_lattice_doi_thinning_poc.py` prove

\[
 \|K_w\|_\infty
 \le {B\max_j w_j\over Ws}\,e^{1/3}.
\]

The number `0.13` uses the original `max(w)=0.356915872...`.  The Stage-A
simplex gate only enforces `min(w)>=0.03`; a selected fold-side or phase
control can have a much larger maximum weight.  A runtime check only at
visited candidate points does not repair an invalid global domination rate:
the process can miss the high-rate region, never raise, and still be biased.

A result-blind bound valid for every nonnegative unit-sum allocation is

\[
 {B\max_jw_j\over Ws}e^{1/3}
 \le {B\over Ws}e^{1/3}
 = {0.01\over 1\cdot0.04}e^{1/3}
 <0.35.
\]

**Required:** freeze `Lambda=0.35` for every production control, or freeze a
separately audited per-control rounded-up bound before generating any
scientific event time.  Reusing `0.13` outside the original weight vector is
forbidden.

The universal bound increases the candidate intensity by

```text
0.35 / 0.13 = 2.692307...
```

relative to the POC.  This cost is preferable to a result-dependent rate and
should be budgeted explicitly.

### P0-3 — multi-control, variable-topology inference is not frozen

The POC functions `basin_counts` and `window_counts` implement one trimodal
law with two valley cuts and five windows.  Stage B is supposed to validate a
union of one-/two-/three-mode representatives and controls on both sides of
both folds.  These laws have different numbers of roots, valleys, event
basins, and contrast inequalities.

The alpha table in Section 8 of `notes/off_lattice_doi_thinning_design.md`
allocates `0.01+0.02+0.02=0.05` for one trimodal law.  Reusing that allocation
for each control would inflate the familywise false-positive rate.  “The
analogous pattern” is not an executable statistical contract.

**Required:** before production, serialize the exact control list and, for
each control, the number/order of windows, valley cuts, basins, and signed
contrasts.  Freeze one global `alpha_FWER=0.05` ledger across all promoted MC
statements, including both scientific pools.  A conservative acceptable
allocation is:

| family | total alpha |
|---|---:|
| simultaneous survival statements | `0.010` |
| all basin-mass lower bounds and agreements | `0.015` |
| all peak--valley contrast and window-probability statements | `0.015` |
| two-pool consistency statements | `0.010` |

Within each family, divide by the frozen number of controls/statements and by
the required one-/two-sided tails.  Other allocations are acceptable only if
they are frozen and audited before scientific IDs are generated.  Missing or
failed analysis for any promoted control is a global HOLD; controls may not be
dropped after counts are known.

### P0-4 — “continuum cusp” is a conditional claim error

The same-FV-family matrix can empirically converge fourth jets; off-lattice
MC can independently validate distributions.  Neither validates the fourth
jet of the unbounded continuum process.  Thus:

- `PASS-FV-ALLOCATION-CUSP` plus `PASS-OFF-LATTICE-EVENT-LAW` can support the
  focused numerical-cusp claim in Section 3;
- they cannot set `continuum_cusp_verified=true`;
- if that stronger wording remains central, the second deterministic solver
  or rigorous jet error bound in Section 3 is mandatory.

This is a conditional P0: it is closed by narrowing the claim, not by adding
more Monte Carlo paths.

### P1-1 — boundary-strip evidence has no physical definition or gate

Section 6 of `notes/positive_b_allocation_cusp_promotion_design.md` requires
“boundary-strip mass,” but does not freeze the strip width, coordinate split,
time set, normalization, or threshold.  The current fixed-point builder uses
a two-cell union mask; two cells have different physical widths on different
meshes and boxes and therefore are not comparable truncation diagnostics.

**Required minimum freeze:** use physical, not cell-count, strips

```text
M lower/upper strip width = 0.10
R_parallel lower/upper strip width = 0.20
```

and record their four separate unnormalized killed masses plus the union at
every saved scan time, stationary root, cusp/fold node, and tail checkpoint.
Require the union mass to be at most `1e-6` on every configuration.  Before
the run, also pin the analytic free-OU union-bound calculation from the compact
initial support; killed subprobability in a strip cannot exceed its free-law
counterpart.  The numerical gate and analytic diagnostic must both be finite;
neither may be invented after box values are seen.

### P1-2 — no fine-grid/enlarged-box corner and no unique FV reference

The proposed matrix refines only the baseline box and enlarges boxes only at
approximately `O129` spacing.  It therefore does not observe a grid--box
interaction.  It also leaves ambiguous whether an off-lattice comparison
uses `O161/Base`, `O129/MR+`, an extrapolation, or an envelope as `x_FV`.

**Required minimum additional corner:** add

```text
MR+F:
  midpoint box/cells          [-0.55, 2.15] / 207
  relative-parallel box/cells [-2.4, 2.4] / 215
  transverse cells            161
```

The counts preserve the `O161` physical spacings to rounding.  Run at least
the complete cusp jet/rank, the original positive-`B` anchor, all promoted
one-/two-/three-mode laws, and all off-lattice fold-side controls on this
corner.  It is not necessary to repeat every intermediate arclength node
there if both branch endpoints and the complete branch already pass the
seven-grid matrix.

For every MC estimand, define

```text
x_FV = the MR+F value
E_FV = maximum of
       O129--O161 baseline refinement,
       E128--O129 alignment,
       Base--M+/R+/MR+ box changes,
       MR+(O129 spacing)--MR+F refinement,
       and the independently converted algebra/root residual.
```

No Richardson order is required.  Raw values and the full envelope remain
primary.  This gives the independent comparison one unambiguous deterministic
reference and tests the missing interaction.

### P1-3 — `tau_cross` is undefined for quantities without a threshold

The off-lattice design requires `tau_x` to be less than one quarter of the
distance to a scientific threshold.  A survival coordinate and an individual
window probability have no such threshold.  The present rule cannot be
instantiated for them.

**Required:** freeze quantity-specific rules before MC:

- masses: `tau_M <= min(0.001, (M_FV-0.005)/4)`;
- signed contrasts `Delta=p_peak-p_valley`:
  `tau_Delta <= Delta_FV/4`;
- each window probability: use the smallest adjacent deterministic contrast
  and require `tau_p <= min(0.002, min_adjacent Delta_FV/16)`;
- survival coordinates: freeze `tau_S=0.01` and require uniform agreement on
  the declared time grid.

Every right-hand side must be positive at the deterministic freeze.  If not,
the control is a deterministic HOLD, not permission to widen `tau`.

### P1-4 — `N=6,000,000` is not yet a production sample-size certificate

Section 8 of `notes/off_lattice_doi_thinning_design.md` correctly labels six
million provisional.  Its quarter-margin check evaluates the CP interval at
the nominal expected count; it does not bound the probability that the
random realized count satisfies the quarter-margin rule.  The calculation
also predates the multi-control alpha allocation above.

**Required:** after deterministic Stage B and before MC, choose a single
common `N` (or a fully specified per-control vector) by exact binomial/
multinomial power calculations under the frozen deterministic alternatives.
For every promoted mass and contrast, require at least `0.90` joint power for
both the scientific inequality and the realized quarter-margin precision
condition under the global alpha ledger.  Round upward to the frozen chunk
multiple.

Freeze `N`, a hard maximum `N_max`, and **no optional top-up**.  If the formula
requires more than `N_max`, the pre-run decision is HOLD or claim narrowing.
After any scientific count exists, increasing `N`, changing widths, moving a
cut, or dropping a control is forbidden.

### P1-5 — fold-side controls are not yet mechanically selected

The deterministic design freezes points *on* each fold; MC must validate a
modality change using points on opposite sides.  The phrase “additional
fixed-budget fold-side controls” in the off-lattice note does not define them.

**Required:** using Stage-A values only, before the first Stage-B grid, choose
one predeclared comparison node on each branch (the signed `|t-t_c|=0.75`
node is the natural choice), construct its oriented allocation-plane normal,
and evaluate the symmetric candidate offsets from a frozen set such as
`{0.005,0.010,0.020}`.  Freeze the smallest geometrically admissible offset
whose two mesh-65/97 laws have the declared opposite topology and all
discovery margins.  If no candidate passes, HOLD.  Stage B then confirms the
same four physical weight vectors without moving them.

### P1-6 — pool consistency, resume, and rerun roles are underspecified

“Stability across two pools” needs a gate.  Freeze, for every survival,
mass, window, and contrast estimand, poolwise simultaneous intervals and
require their difference to be no larger than the sum of the allocated
poolwise radii plus a predeclared numerical rounding allowance.  Pool 1 and
pool 2 are independent scientific samples; their exact-ID rerun is only a
reproducibility check and must never be pooled as extra data.

The chunk ledger must be append-only and keyed by exact trajectory-ID ranges.
Operational retries may replace a failed/incomplete chunk only under a logged
fixed rule; scientific counts may not be inspected before deciding to retry.
All final claims must be reconstructible from integer chunk counts and raw
event-time hashes.

### P1-7 — no production chains or frozen auditors exist

The current off-lattice file is explicitly a scalar POC, and no Stage-B
anisotropic producer exists.  Neither can be promoted by changing a flag.

Create separate chains, leaving existing frozen files untouched:

```text
notes/positive_b_stage_b_validation_protocol.md
code/positive_b_stage_b_validation.py
code/test_positive_b_stage_b_validation.py
artifacts/data/positive_b_stage_b_validation_manifest.json
code/audit_positive_b_stage_b_validation.py
code/test_audit_positive_b_stage_b_validation.py

notes/off_lattice_doi_thinning_production_protocol.md
code/off_lattice_doi_thinning_production.py          (or pinned compiled core)
code/test_off_lattice_doi_thinning_production.py
artifacts/data/off_lattice_doi_thinning_manifest.json
code/audit_off_lattice_doi_thinning_result.py
code/test_audit_off_lattice_doi_thinning_result.py
```

Each auditor and its adversarial tests must be frozen before its scientific
result exists.  Both chains need full start/end pin snapshots, exact result
schemas, finite structural HOLD rows, two-process reproducibility, final-byte
rehashing, and failure-atomic promotion.

### P2-1 — “held-out mesh” needs a narrower label

Meshes 113 and 129 are held out for the *new Stage-A-selected allocation
controls* if their control--grid pairs have never been evaluated.  They are
not virgin meshes for the original fixed positive-`B` anchor.  Mesh 97 is
explicitly discovery, and `E128`, `O161`, the enlarged boxes, and `MR+F` are
the genuinely new deterministic configurations.

Use “Stage-B validation matrix” for the whole matrix.  Reserve “held out” for
an exact control--configuration pair whose absence is recorded at the
Stage-B freeze.

### P2-2 — the original bridge-selected positive-`B` anchor is missing from the matrix

The present Stage-B text lists only the Stage-A one-/two-/three-mode
representatives.  Robustness of the already established broad-four-slab
positive-`B` point requires carrying its exact frozen weight vector through
`E128`, `O161`, the box matrix, `MR+F`, and the off-lattice validation.  It may
be deduplicated only if byte-identical to a selected representative.

Otherwise the paper would replace, rather than robustify, the result that
motivated Stage B.

### P2-3 — compute volume and stopping caps are not serialized

The manifests should state the number of grid/control laws, maximum Newton
and Krylov work, memory cap, MC candidates implied by `Lambda`, chunk count,
and no-top-up policy.  This is operational metadata, but it prevents a failed
run from turning into an open-ended search.

## 5. Minimum executable deterministic Stage B

The following package is sufficient for the focused claim; it is intentionally
smaller than a second deterministic solver.

### 5.1 Control set frozen before any Stage-B grid

After a repaired Stage A passes, freeze the union of:

1. the original bridge-selected positive-`B` anchor;
2. the Stage-A one-/two-/three-mode representatives;
3. the six signed fold comparison nodes;
4. four off-fold controls, one on each side of the chosen node on each fold
   branch; and
5. the cusp chart, branch orientations, remote-root identities, and all
   physical parameters.

Exact duplicate weight vectors may be evaluated once but must retain all role
labels.  No geometric or physical control may change after this freeze.

### 5.2 Grid/box matrix

Retain the predeclared configurations:

| label | cells | state count |
|---|---:|---:|
| `O113/Base` | `(113,113,113)` | `1,442,897` |
| `E128/Base` | `(128,128,128)` | `2,097,152` |
| `O129/Base` | `(129,129,129)` | `2,146,689` |
| `O161/Base` | `(161,161,161)` | `4,173,281` |
| `M+` | `(166,129,129)` | `2,762,406` |
| `R+` | `(129,172,129)` | `2,862,252` |
| `MR+` | `(166,172,129)` | `3,683,208` |
| `MR+F` | `(207,215,161)` | `7,165,305` |

The first seven configurations retain the complete cusp, six fold nodes,
anchor, and three phase representatives required by the existing design.  The
new `MR+F` corner must at least carry the cusp, anchor, three phase
representatives, and four off-fold controls.  If an off-fold control is a
promoted phase representative, deduplicate it.

### 5.3 Mandatory deterministic diagnostics

In addition to Sections 7.1--7.4 of the promotion design, every configuration
must serialize and gate:

- exact grid faces/cell counts and cell widths;
- catalyst zeroth/first moments and independent cell-integral reference
  errors;
- disk area, centroid, reflection symmetry, and independent contact-fraction
  reference errors;
- initial mass, installed budget, `Q1=-B*kappa`, `S_t=-f`, differential mass
  balance, event partition closure, state positivity, and tail survival;
- the fixed physical boundary-strip diagnostics in P1-1;
- every stationary bracket/root/type, persistent remote-pair identity, and
  exact representative/fold role;
- all cusp jets, allocation tangents, rank/singular values, determinant
  identity, and finite-difference checks; and
- the expanded uncertainty envelope in P1-2.

Every unavailable scientific value is `null` with a false gate; no `NaN`,
infinity, changed control, or omitted row is allowed.

### 5.4 Deterministic GO/HOLD

`GO-FV-STAGE-B` requires:

1. all physical/conservation gates on every required row;
2. identical retained topology and root identity where the claim requires it;
3. strict odd-sequence convergence or the already frozen roundoff exception;
4. no parity crossing at `E128`;
5. all separate/combined box and `MR+F` differences inside the absolute and
   quarter-margin rules;
6. complete cusp/fold/rank gates with no refit; and
7. two byte-identical full executions plus an independent post-result audit.

Failure of any required row is `HOLD-FV-STAGE-B`.  A pass sets only flags such
as `fv_mesh_alignment_box_robustness_passed=true`; it leaves
`rigorous_FV_continuum_limit=false`, `continuum_cusp_verified=false`, and
`independent_solver_verified=false`.

## 6. Minimum executable off-lattice production design

### 6.1 Frozen scientific controls

Use the exact union

```text
C_MC = {
  original trimodal anchor,
  one-/two-/three-mode representatives,
  two controls on opposite sides of fold branch 1,
  two controls on opposite sides of fold branch 2
}
```

and collapse exact duplicates while preserving role labels.  Depending on
overlap this gives roughly five to eight physical controls.  No control may be
dropped after an event count exists.

For each control, mechanically derive from the audited deterministic result:

- expected retained topology;
- ordered valley cuts and `m` event basins for `m` retained maxima;
- equal-width, ordered, disjoint peak/valley windows;
- FV integrals over exactly those cuts/windows;
- `x_FV`, `E_FV`, `tau_x`, and all signed contrasts; and
- the exact familywise-alpha row and powered `N`.

The algorithms that turn deterministic roots into cuts/windows must be frozen
before deterministic Stage B; only substitution of audited values is allowed
at the MC freeze.

### 6.2 Physical and implementation contract

- Use the same `D`, `gamma`, `m_bar`, `W`, contact radius, bump initial law,
  slab centers/supports, `B=0.01`, and each exact frozen allocation.
- Use unbounded `M,R_parallel`, periodic `R_perp`, exact free transitions, and
  the unsmoothed disk indicator.
- Use `Lambda=0.35` universally, unless every smaller per-control analytic
  bound was frozen and independently audited first.
- Pin the compiled/vectorized engine, compiler, libraries, architecture,
  Philox raw test vectors, distribution-transform fixtures, and separate test
  and scientific ID namespaces.
- Validate the engine against the constant-hazard analytic law, fixed free
  transition fixtures/moments, contact-boundary mutations, the scalar POC on
  small non-scientific fixtures, and path/chunk/order isolation.
- Abort on any rate-bound, sampler-cap, nonfinite-state, duplicate/missing ID,
  chunk-hash, or ledger failure.

### 6.3 Statistical GO/HOLD

`GO-OFF-LATTICE` requires, under the one frozen familywise ledger:

1. simultaneous survival agreement on the declared grid;
2. the correct variable-length basin partition for every control, exact
   integer closure with `S(100)`, every promoted basin lower bound above
   `0.005`, and the realized quarter-margin precision rule;
3. every predeclared peak--valley average-density contrast positive with its
   simultaneous lower bound;
4. agreement of all individual window probabilities, basin masses, survival
   values, and signed contrasts with `x_FV +/- E_FV` under the frozen
   `tau_x`;
5. the expected modality change across both fixed fold-side pairs;
6. the frozen two-pool consistency gates;
7. zero implementation/ledger failures; and
8. an exact-ID reproducibility rerun plus an independent post-result audit.

Any missing control/statement, failed bound, or consumed margin is
`HOLD-OFF-LATTICE`.  There is no top-up, window move, new seed, new control,
or widened tolerance.

A pass sets `independent_unbounded_event_law_validated=true`.  It does not set
`continuum_cusp_verified=true`.

## 7. Pre-registration timing and the true held-out boundary

Use three explicit freezes:

| time | what is allowed to be known | what must be frozen next |
|---|---|---|
| `T0` now | existing designs, pilots, disclosed low-mesh values; no Stage-A scientific result | repaired Stage-A v2 code/protocol/manifest/auditor; unchanged scientific gates |
| `T1` after audited Stage-A PASS, before any Stage-B control--grid evaluation | Stage-A 65/97 cusp/branches/reps only | complete deterministic Stage-B matrix, anchor, fold-side selection, controls, diagnostics, thresholds, `MR+F`, two-process and auditor chain, and algorithms for later MC cuts/windows |
| `T2` after audited deterministic Stage-B PASS, before any production trajectory ID is generated | deterministic Stage-B roots, cuts, window integrals, margins, and `E_FV` | exact MC controls/cuts/windows, alpha ledger, `tau`, powered fixed `N`, `N_max`, no-top-up rule, `Lambda`, seeds/ID ranges/chunks, engine/packages, failure policy, result schema, and auditor chain |
| `T3` | nothing from partial scientific counts may be inspected for design | execute both pools once, apply the frozen analysis once, exact-ID rerun, independent audit |

Precise terminology:

- meshes 65 and 97 are discovery, never held out;
- 113 and 129 may be held out for a newly selected control--grid pair, but not
  for the already run original anchor;
- `E128`, `O161`, enlarged boxes, and `MR+F` are new deterministic validation
  configurations if their absence is recorded at `T1`;
- the small POC paths and their displayed counts are pilots, not held-out
  science;
- true independent MC data are only the production trajectory IDs derived and
  generated after `T2`;
- the two disjoint pools are independent samples; an exact-ID rerun is a
  reproducibility duplicate, not a third sample.

The honest evidence label is **result-informed deterministic design with
held-out configuration pairs, followed by pilot-informed, pre-frozen
independent production Monte Carlo**.  It is not preregistered discovery.

## 8. Compute estimate

### 8.1 Deterministic FV

The seven existing unique configurations contain `19,167,885` state cells
when their state counts are summed.  Evaluating the existing minimum of one
cusp, six fold nodes, and three phase representatives gives 70
grid--control-law rows, or `191,678,850` state-law cells before Newton,
tangent-block, Krylov, and time-scan multipliers.

Carrying the original anchor on all seven grids and nine claim-critical laws
on `MR+F` gives an indicative minimum of

```text
77 seven-grid rows + 9 MR+F rows = 86 grid--law rows
weighted state-law cells per full execution = 275,334,480
two full deterministic executions          = 550,668,960
```

These are workload units, not floating-operation counts.  Cusp Newton steps
and the base-plus-two-tangent augmented system make the real Krylov cost
several times larger.  Before `T1`, run only non-scientific small-grid and
fixed-iteration performance fixtures, then freeze a wall-time/memory cap.
Do not remove grids or controls after a slow scientific row is observed.

At `MR+F`, one binary64 state vector is about 57 MB; several Krylov vectors,
tangents, checkpoints, and operator workspaces make a multi-GB memory budget
appropriate.  Sequential meshes/processes remain the safe default.

### 8.2 Off-lattice

At horizon 100, a rate-`Lambda` candidate process proposes at most an expected
`Lambda*T` candidates before allowing for earlier reaction stopping:

```text
POC rate 0.13       -> up to about 13 candidates/path
universal rate 0.35 -> up to about 35 candidates/path
multiplier          -> 2.692307...
```

At the provisional `N=6,000,000` per control, the universal design budgets up
to about `210,000,000` candidate transitions per control.  For five to eight
deduplicated controls this is approximately `1.05--1.68 billion` transitions
for the scientific run, and `2.10--3.36 billion` including the exact-ID
reproducibility rerun.  The two scientific pools partition `N`; they do not
double it.

The final count may be larger than six million after the global-alpha and
realized-quarter-margin power calculation.  Therefore the manifest should
budget candidate transitions as `sum_c N_c * 0.35 * 100`, not by a fixed wall
clock.  A compiled/vectorized engine is required.  Freeze the final wall-time
estimate only after a non-scientific constant-hazard benchmark using disjoint
test IDs.

## 9. Final GO/HOLD ladder for the paper

### `GO-FV-STAGE-B`

The same FV family passes all mesh, parity, box, fine--large interaction,
physical-law, cusp, fold, topology, and uncertainty gates without refitting.
This is a converged numerical-FV result, not solver independence.

### `GO-OFF-LATTICE`

The independently frozen unbounded continuous process preserves the promoted
survival, masses, window contrasts, and fold-side modality changes under the
global inference contract.  This is independent event-law validation, not a
fourth-jet calculation.

### `GO-FOCUSED-PRR-SCIENCE`

Both GO states above pass, the analytical fixed-finite-`m`/weak-`B` results
remain correctly scoped, and the manuscript claims only a mesh-stable
numerical allocation cusp linked to independently validated continuum-process
modality changes in physical `d=2`.

### `HOLD`

Remain on HOLD if Stage A is not repaired; any required grid/control fails;
parity/box/fine--large uncertainty consumes a margin; the universal/per-control
thinning bound is not proved; any MC statement/control is missing; the global
alpha/no-top-up contract is violated; or the independent process disagrees.

### `HOLD-STRONG-CONTINUUM-CUSP`

Even after both numerical GO states, retain this stronger HOLD unless an
independent deterministic fourth-jet/rank calculation or a rigorous FV jet
error certificate passes.  Do not ask Monte Carlo to answer that question.

## 10. Final verdict

The Stage-B direction is worth executing and remains the shortest route to a
focused PRR paper.  It is not yet executable.  The minimum repair is not a
broader parameter scan: it is a stricter freeze containing the universal
thinning bound, global multi-control inference, physical boundary strips,
`MR+F`, a unique FV uncertainty envelope, mechanically selected fold-side
controls, fixed powered `N` with no top-up, and two independently audited
production chains.

Under that repaired design, a second deterministic solver is optional for the
focused numerical-cusp claim and mandatory only for a stronger
continuum/PDE-cusp fourth-jet claim.
