# Round 102: adversarial PRR strategy audit after the allocation-cusp HOLD

Date: 2026-07-14  
Evidence snapshot: 2026-07-14T06:34:26Z  
Audit mode: read-only scientific-strategy attack  
Scientific computation run in this audit: **NONE**  
Files changed by this audit: this report only

## 0. Executive decision

| decision surface | verdict | reason |
|---|---|---|
| submit the current manuscript to *Physical Review Research* now | **NO-GO** | the manuscript's decisive finite-`B` cusp gate has an audited scientific `HOLD`, while the fixed-control and off-lattice evidence are not yet sufficient for the revised claim |
| continue the Round-92 cusp-centered `SEND-2D` route | **KILL FOR THIS MANUSCRIPT** | Round 92 made an independently accepted low-grid allocation cusp a necessary conjunct; that conjunct is false under the frozen experiment, so its Stage-B and MC descendants cannot be instantiated honestly |
| preserve the allocation result | **ARCHIVE AS VALID HOLD** | the result and independent audit are internally valid; the failure is a scientific discovery `HOLD`, not a corrupted run and not evidence that no cusp exists |
| retune the homotopy tolerance or line search and call the rerun confirmation | **NO-GO** | that would be result-informed repair of a frozen discovery gate and would destroy the clean discovery/confirmation separation |
| build a new fixed-control PRR route | **CONDITIONAL GO-DESIGN / HOLD-EXECUTION** | the accepted fixed-finite-`(d,m)` theorem plus a robust finite-`B`, physical-`d=2` realization and genuinely independent off-lattice validation can form a coherent PRR paper without a cusp |
| make positive-`B` physical `d=3` a submission gate | **NO-GO** | it is not needed for the focused theorem-plus-`d=2` paper and would add a large, weakly connected burden |
| pursue a new allocation-cusp study later | **PARK AS A SEPARATE PROSPECTIVE PROJECT** | a fresh continuation/validation protocol could be scientifically worthwhile, but it is not the highest-information-gain route to this paper |

The recommended paper is therefore no longer a finite-budget catastrophe
paper. Its defensible spine is:

```text
constructive fixed-finite-(d,m) exposure-clock theorem
  + robust finite-B physical-d=2 trimodal realization at one unchanged control
  + preferably one same-budget/same-support lower-modality comparator
  + powered unbounded off-lattice event-law validation
  = conditional PRR-ready mechanism-and-realization paper
```

Without the comparator, the paper may still be viable if it consistently says
**construction**, **design**, or **realization**, but the finite-`B` word
**control** becomes weak. Without deterministic robustness or off-lattice
validation, the package is closer to a strong specialized PRE/JCP paper than
to an authoritative PRR contribution.

## 1. Scope, journal standard, and evidence boundary

This audit answers five questions:

1. What does `HOLD_SCIENCE_AUDIT_VALID` do to the current PRR spine?
2. Should the allocation cusp be repaired, abandoned, or merely recorded?
3. What is the highest-information-gain next scientific work?
4. Is the existing Stage-B design plus off-lattice Monte Carlo sufficient?
5. What more general analytical statement can raise the paper above a single
   numerical example without overclaiming?

The current APS description says that PRResearch papers should make a
high-quality, significant contribution, interest readers connected to
physics, and form an authoritative and substantive addition to the
literature. Its author guidance also says that a paper must stand on its own;
essential evidence cannot be hidden in Supplemental Material. These are the
relevant standards, not a requirement that the paper contain a cusp:

- <https://journals.aps.org/prresearch/about>
- <https://journals.aps.org/prresearch/authors>

This report did not rerun the allocation discovery, any FV grid, a PDE solve,
Monte Carlo, plotting, or LaTeX. It treats every existing result as evidence
with its recorded scope and does not edit a result, theorem, protocol, or
manuscript claim surface.

## 2. Frozen evidence read by this audit

| evidence | SHA-256 | role in this decision |
|---|---|---|
| `artifacts/data/positive_b_allocation_cusp_discovery_result.json` | `47ad903f5d2f62cfdaf842219b1edc85f62089ce942663f67a89cc8be4ab5986` | frozen allocation discovery result |
| `artifacts/data/positive_b_allocation_cusp_discovery_independent_audit.json` | `5a31dad6c153119c5b20549f7ba324045dd4ce78a7cbb1da715fa3d1f65841c2` | independent integrity/science disposition |
| `audits/round_92_prr_scientific_spine_independent_audit.md` | `e1d69da67ae34b24cd3e74708aecc2fc3609fcdb396349c5d644394e77a0de52` | pre-result conditional PRR route |
| `notes/positive_b_stage_b_validation_design_v5.md` | `136085075ad23fc22a40cf03725c9151f11ff356cff4f6f39e5c5fbb24317ddd` | Stage-B one-way dependency and evidence design |
| `code/positive_b_stage_b_t0_external_attestation_v2.json` | `2572938fad9fdb74e4a0d8053651601af7359fa7df2ce47747ffd4fbb57fbb43` | T0 infrastructure attestation |
| `audits/round_96_stageb_t0_production_attestation_independent_validation.md` | `6604d2f50e914210c9ccb488a0b4885f09276c250a778883136e55275b7599ce` | independent T0 acceptance; science remains unauthorized |
| `notes/direct_physical_multimode_theorem.md` | `2b35d1b1053045220b29975d30f8b3c842d33273ca46de86b8cf7798c26a9c3d` | accepted analytical backbone |
| `audits/round_90_general_dimension_exact_claim_surface_freeze.md` | `6f8fefe18602ae244db30a8d8ef10351961734d08bce5b9e4a34b781b80e11d4` | exact general-dimension claim freeze |
| `audits/round_91_general_dimension_exact_freeze_independent_attack.md` | `fe6b9e40e6cbb808ca0d4907fa9b0e6eb7e70db383d64ab7b7312ddb9988bded` | independent theorem/claim-surface acceptance |
| `artifacts/data/positive_b_broad_four_slab_result.json` | `51e8eb4bdb652124865d0c39e6f36b99d13ed61578b161e0f75b142cada49401` | existing finite-`B` physical-`d=2` anchor |
| `audits/round_59_positive_b_canonical_result_closure.md` | `c7825396ed44ac50017b599a6a4b1a43f8f0f531db5173f1b88a67fa9011a72f` | accepted scope of that anchor |
| `notes/off_lattice_doi_thinning_design.md` | `349541a954e665d0a68b3989e6f38f5edc725b00f77e4811147c1de262fc7961` | independent-process design |
| `audits/round_37_off_lattice_design_attack.md` | `1ba9b37898bfb17d66bbaae0f6ec2a976966a6e33e6bebf73919c68f679828dd` | design acceptance with production hold |
| `code/off_lattice_doi_compiled_core.cpp` | `4f6810bf82445f85339cbe87d3e7bbf8e4144bdd1b8ddbe3c68daa273414d895` | snapshot of compiled method core at audit time |
| `manuscript/encounter_multimodal_prr.tex` | `1c17be4ac1223fa769166cc13c4b551a1cf7925ae59a61a81021657421305c5b` | current, unrebaselined manuscript |

The compiled-core observations below apply to the pinned snapshot. Later code
work does not retroactively change this audit; it must receive its own
scientific-production audit before use.

## 3. What the allocation `HOLD` means—and what it does not mean

The result is unambiguous at the protocol level:

- the small explicit-CSR preflight passed with maximum error
  `2.220446049250313e-16`;
- mesh `65^3` reached a converged `B=0` cusp seed in six iterations, with
  maximum scaled residual `5.764603304412123e-11`;
- at `B=0.0025`, the frozen homotopy stopped with `line_search_failed`, maximum
  scaled residual `1.354737396982097e-10`, against the frozen `1e-10` solve
  tolerance;
- mesh `65^3` therefore returned `HOLD_DISCOVERY` with reason
  `homotopy_failed`;
- mesh `97^3` was correctly `NOT_RUN_AFTER_HOLD`;
- no cusp, folds, remote pair, stationary scan, or publication claim was
  produced; and
- the independent audit found all integrity checks valid, no failed audit
  checks, but `scientific_result_passed=false` and
  `release_status=HOLD_SCIENCE_AUDIT_VALID`.

Two interpretations are forbidden:

1. **“There is no finite-`B` cusp.”** The frozen solver failed to certify its
   continuation. It did not prove nonexistence.
2. **“The residual was close, so the cusp basically passed.”** The tolerance,
   line search, and stop rule were frozen precisely to prevent this
   post-result reinterpretation.

The correct interpretation is narrower and operationally decisive:

> The audited experiment is valid, but it did not deliver the scientific
> object required by the Round-92 cusp-centered publication route.

Retuning the tolerance, step size, or line search could be legitimate only in
a **new, explicitly result-informed development study**. Such a study would
need a new prospective protocol, a clearly separated confirmation set, and
preferably pseudo-arclength or validated continuation plus an independent
solver. It cannot be relabeled as completion of the frozen discovery.

## 4. The exact logical damage to the Round-92 spine

Round 92 was conditional on a low-grid cusp pass. Its advertised chain was:

```text
accepted general-d theorem
  AND accepted B=0.01 fixed-control anchor
  AND independently accepted low-grid allocation cusp
  AND deterministic Stage-B validation
  AND powered off-lattice validation
  => conditional SEND-2D
```

The third conjunct is false. This is not a local missing figure; it removes
the parent object from which the existing Stage-B roles and MC controls were
supposed to be selected.

The one-way freeze ladder makes the consequence stronger:

```text
T0 selector infrastructure: accepted, science-free
  -> canonical Stage-A result: HOLD, no accepted cusp object
  -> T1 cusp/fold/representative selection: cannot be instantiated
  -> Stage-B 120-row matrix: cannot be instantiated
  -> representative_m1/m2/m3 MC targets: cannot be frozen
  -> existing powered scientific MC experiment: cannot be run honestly
```

Round 96 explicitly says `future T1 = NOT BUILT / NOT AUTHORIZED` and
`scientific execution = NOT AUTHORIZED`. A successful T0 attestation proves
that a loader/selector contract is real; it does not manufacture a scientific
Stage-A object.

Therefore, “fix Stage-B and then run off-lattice MC” is **not** a valid rescue
of this chain. The old Stage-B design is a cusp-validation protocol. It cannot
be silently converted into a fixed-control validation protocol, and its
representative controls cannot be chosen from nonexistent cusp/fold branches.

## 5. What survives the `HOLD`

### 5.1 The analytical theorem survives intact

The accepted theorem remains a substantial result. For every fixed finite
`d >= 2` and fixed finite `m`, it constructs an `m`-slab family such that,
after choosing sufficiently small fixed slab width `epsilon` and then
`0 < B < B0(epsilon)`, the exact Doi reaction-time density has exactly one
nondegenerate local maximum in each of `m` certified disjoint intervals. The
statement is uniform over a compact interior weight set for those fixed
`d,m`.

The allocation `HOLD` does not enter this proof. The theorem's honest limits
also remain:

- no uniformity as `d` or `m` grows;
- no one fixed geometry producing arbitrary `m`;
- no arbitrary localized patch theorem;
- no exclusion of extra extrema outside the certified intervals;
- no numerical value of `B0` for the broad four-slab example;
- no absolute observability floor, because fixed-window event mass is
  `O(B)`; and
- the constructive slabs are transverse-uniform, not a general boundary
  pattern.

### 5.2 The finite-`B` physical-`d=2` anchor survives, but remains fragile

The unchanged broad four-slab control at `B=0.01` passed its recorded
same-solver, fixed-box, two-odd-mesh confirmation. It has five alternating
stationary roots on the declared screen and three event-mass-qualified local
maxima. This result is not invalidated by the failed allocation continuation.

It is not yet a publication-grade independent physical realization:

- both meshes are odd (`113^3` and `129^3`);
- both use the same finite-volume solver and one reflecting box;
- there is no alignment challenge, parity challenge, box enlargement,
  unbounded-domain result, or independent process;
- root evidence is floating-point, not an interval census; and
- the weakest margins are small: the smallest basin mass is only
  `0.0052114278399768565` against a `0.005` floor, while the worst saved
  valley ratio is `0.8467280181266086` against a `0.85` ceiling.

Those narrow margins make this anchor the highest-information-gain object to
attack next. If it fails parity/alignment/box tests, expensive MC and renewed
cusp work should stop.

### 5.3 The off-lattice method survives as a design, not as evidence

The transition-exact unbounded Doi-thinning construction is mathematically
well motivated and attacks the most important shared FV failure modes: spatial
grid, finite reflecting box, and grid/contact alignment. The existing design
and Round-37 attack nevertheless remain `PASS WITH PRODUCTION HOLD`.

At the evidence snapshot, the compiled C++ core labels itself a method-only
core and exposes a constant-hazard path. It does not by itself supply the
broad four-slab spatial hazard, frozen scientific controls/windows, power,
production sample count, seed/chunk ledger, or scientific result. Even a fully
working compiled engine would not validate cusp jets, cusp rank, folds, or
absence of modes; MC can validate only predeclared event-law probabilities,
survival, basin masses, and local fixed-window contrasts.

## 6. Priority findings

Counts: **P0 = 1, P1 = 3, P2 = 2**.

| ID | priority | finding | consequence | required disposition |
|---|---:|---|---|---|
| R102-P0-1 | P0 | Round 92 requires an accepted allocation cusp, but the frozen result is an audited scientific `HOLD`; no canonical cusp/fold object exists | old T1, Stage-B, representative-control, and MC descendants are scientifically undefined | kill the cusp-centered route for this manuscript; archive the result and start a separately named fixed-control route |
| R102-P1-1 | P1 | the surviving `B=0.01` anchor lacks parity, alignment, box, interval-root, and independent-process closure and has narrow mass/valley margins | it can be a lead candidate, not yet the authoritative finite-`B` realization required for PRR | run a newly frozen fixed-control robustness campaign before any powered MC |
| R102-P1-2 | P1 | the existing off-lattice scientific controls/windows depend on Stage-B representatives that do not exist; the pinned compiled core is method-only | no scientifically interpretable MC campaign can presently be launched | build a new fixed-control F0–F3 freeze chain and a broad-hazard production engine; precompute `N` and prohibit sequential top-up |
| R102-P1-3 | P1 | one trimodal allocation does not by itself demonstrate finite-budget **control** by spatial allocation, and the theorem has no quantitative `B0` link to `B=0.01` | title/abstract language can outrun evidence; theory and example may look juxtaposed rather than causally linked | add a prospectively frozen same-budget/same-support lower-modality comparator if using “control”; otherwise use “construction/design/realization” and explicitly separate theorem from example |
| R102-P2-1 | P2 | the manuscript does not foreground the most general proof idea: separated exposure channels plus a `C^2` persistence margin | the contribution can read as OU/slab-specific despite a reusable mechanism | extract and independently audit an abstract channel-dominance lemma, without enlarging the current theorem's domain unless proved |
| R102-P2-2 | P2 | the current manuscript still lists the positive-`B` cusp as `NOT RUN`, keeps cusp-centered submission language, and inherits inconsistent `d=3`/continuous-density-`L1` expectations | the document is not false about a pass, but its decision ledger and proposed release claim are stale | after route authorization, rebaseline the claim surface; keep `d=3` supplemental and replace any `L1` language by the actual fixed-window probability statement |

These findings do **not** allege that the theorem, the fixed-control result, or
the allocation audit is invalid. They identify a broken publication logic and
the minimum work needed to replace it.

## 7. Recommended PRR spine

### 7.1 The scientific question

The strongest general question is not “does this particular numerical family
have a cusp?” It is:

> Under what spatial configurations does encounter dynamics generate several
> separated exposure-time channels, and when do those channels survive finite
> reaction strength as observable local modes of the reaction-time law?

That question directly connects geometry, stochastic dynamics, reaction
kinetics, and modality. It is broader than catastrophe localization and it is
answered at three complementary levels:

1. a constructive theorem for arbitrary fixed finite `d,m`;
2. a finite-parameter physical-`d=2` realization at nonzero `B`; and
3. a grid-free, unbounded off-lattice process validation of the observable
   event-law features.

This is a coherent PRR narrative because each layer answers a different
referee objection. The theorem establishes general mechanism; deterministic
numerics establish a finite-budget physical realization; off-lattice MC shows
that the reported features are not artifacts of the FV box/grid.

### 7.2 Claim ceiling for the revised paper

If the proposed evidence package passes, the maximum safe headline is:

> Spatially separated exposure clocks construct at least `m` reaction-time
> modes in every fixed finite dimension in the weak-killing regime. For one
> unchanged physical-`d=2`, `B=0.01` four-slab configuration, three
> event-mass-qualified finite-window modes are stable under declared FV
> parity/alignment/box challenges, and predeclared event-law contrasts are
> preserved by an unbounded off-lattice Doi process.

If a same-budget/same-support comparator also passes a deterministic interval
census, add:

> Redistributing the same total reactivity changes the verified finite-window
> modal structure.

Do not call the revised result a cusp, phase portrait, global exact mode count,
continuum/PDE cusp, or positive-`B` `d=3` result.

### 7.3 “Control” versus “realization”

There are two viable naming branches:

- **With a comparator:** “spatial control” is justified if deterministic
  evidence, at unchanged budget/support, certifies different finite-window
  modal structures for two frozen allocations.
- **Without a comparator:** use “spatial design,” “construction,” or
  “realization.” A single successful allocation demonstrates possibility, not
  controlled change.

Off-lattice MC cannot establish absence of an extra mode. The lower-modality
comparator therefore requires a deterministic interval derivative census on
the full declared time window; MC can confirm its positive features but not
its unimodality or exact count.

## 8. The analytical upgrade with the best generality-to-effort ratio

The current theorem is already sufficient as the paper's rigorous backbone.
The most valuable theoretical improvement is not a uniform-in-`d,m` theorem
or a new positive-`B` `d=3` calculation. It is to extract the proof's reusable
logic as a **separated exposure-channel persistence criterion**.

Let the normalized weak-killing density be

```text
H_B(t;theta) = f_B(t;theta)/B
```

and let the leading exposure profile be

```text
G(t;theta) = sum_{j=1}^m w_j g_j(t;theta).
```

For pairwise disjoint intervals `I_j=[a_j,b_j]`, suppose there are positive
margins `eta_j,kappa_j` such that

```text
G'(a_j) >= eta_j,
G'(b_j) <= -eta_j,
sup_{t in I_j} G''(t) <= -kappa_j.
```

If weak-killing estimates give, separately at the derivative orders that are
used,

```text
||H_B'-G'||_{L-infinity(I_j)} < eta_j,
||H_B''-G''||_{L-infinity(I_j)} < kappa_j,
```

for every `j`, then `H_B'` has opposite signs at the two endpoints and is
strictly decreasing throughout `I_j`. Hence it has exactly one zero in each
`I_j`, and that zero is a nondegenerate local maximum. This yields at least
`m` modes. A componentwise channel-dominance condition can certify the three
margins by making the `j`th self-channel dominate the cross-channel `C^2`
tails on `I_j`.

This lemma isolates the real geometry-to-modality mechanism:

```text
spatial configuration
  -> separated occupation/exposure clocks
  -> derivative and curvature margins
  -> C^2 weak-killing persistence
  -> multiple reaction-time modes
```

It can be stated abstractly for any process for which the normalized
weak-killing expansion and the channel margins are actually proved. The
current OU slab theorem is then a constructive verification of those
hypotheses, not evidence for an unproved claim about arbitrary diffusions or
arbitrary patches.

Required safeguards before using this as a manuscript theorem or corollary:

1. write the exact norms, parameter set, time intervals, and strict constants;
2. prove the normalized `C^2` convergence uniformly on those compact
   intervals and over the declared compact weight interior;
3. show explicitly how the existing slab construction supplies the margins;
4. retain pointwise fixed-finite-`d,m` quantifiers; and
5. independently audit the new statement against the proof bytes.

A numerical lower bound for `B0` at the broad four-slab parameters would be a
valuable bridge, but it is **not a minimum PRR gate** if the paper clearly says
that the theorem and `B=0.01` computation are complementary rather than a
theorem-certified instance. Attempt it only if an explicit semigroup/remainder
bound can be obtained without displacing the robustness and MC work. Never
infer `B0 > 0.01` from the numerical anchor.

## 9. Highest-information-gain next experiment: fixed-control robustness

The next scientific object should be a new protocol, provisionally named
`positive_b_fixed_control_robustness_v1`. It is **not Stage-B v6**, because it
has no cusp, fold, continuation branch, or Stage-A representative roles.

### 9.1 New one-way freeze chain

```text
F0: freeze controls, grid/box challenges, selectors, gates, output schema,
    MC-window construction rule, and kill rules; run only synthetic tests
F1: run and independently audit deterministic FV robustness
F2: from the accepted F1 object, mechanically freeze off-lattice windows,
    contrasts, E_FV, alpha, power, N, seeds, chunks, and two pool IDs
F3: run the powered off-lattice experiment once and independently audit it
```

No F0 selector may inspect new F1 science. No F2 rule may inspect MC output.
No sample-size top-up, target movement, window widening, control replacement,
or threshold relaxation is permitted after the relevant freeze.

### 9.2 Minimal deterministic matrix

The existing Stage-B configuration family can be reused as a pre-existing
challenge design, but not its cusp roles:

| label | role |
|---|---|
| `O113/Base`, `O129/Base`, `O161/Base` | odd refinement |
| `E128/Base` | parity and contact/grid-alignment challenge |
| `M+`, `R+` | separate directional box enlargements |
| `MR+` | combined box enlargement |
| `MR+F` | fine combined-box challenge |

F0 must verify that `E128/Base` really changes the relevant contact/grid
alignment rather than merely the cell count. If it does not, F0 must add an
explicit, prospectively frozen origin or half-cell alignment shift; this
decision cannot be made after F1 output is seen.

For the fixed anchor this is eight logical control–configuration rows, rather
than the old 15 roles × 8 configurations = 120 rows. If one comparator is
frozen, it becomes 16 rows. The complete interval-envelope and no-subset rules
from Stage-B are useful, but the new protocol must pin them directly rather
than importing a scientifically inapplicable cusp design by implication.

The anchor must remain byte-identical to the accepted `B=0.01` four-slab
control. No weight, budget, support, time window, or geometry refit is allowed.

### 9.3 Deterministic pass conditions

At minimum, require for every declared configuration:

1. five alternating simple roots with `max-min-max-min-max` topology on the
   frozen finite window for the anchor;
2. interval-certified root isolation, endpoint derivative signs, curvature
   signs, and no unexamined derivative interval on the declared window;
3. all peak-ratio, valley-ratio, prominence, and basin-mass thresholds to pass
   after applying the complete all-configuration FV error envelope;
4. a contraction-or-floor refinement rule across `O113/O129/O161`;
5. parity, separate-box, combined-box, and `MR+--MR+F` topology agreement;
6. acceptable boundary-layer mass and box-response diagnostics;
7. event-mass partition closure, survival monotonicity, and killed-mass
   balance; and
8. identical controls and common declared time/basin definitions.

For a lower-modality comparator, certify its full declared-window topology by
interval derivative exclusion. A scan that merely finds fewer roots is not an
absence certificate.

The existing absolute Stage-B caps—`0.05` root time, `0.02` peak/valley ratio,
`0.001` basin mass, and `0.01` survival—are reasonable starting values because
they predate this result. F0 must decide whether they are scientifically
appropriate and then freeze them. They must not be relaxed after F1.

### 9.4 Why this comes before MC or a new cusp solve

This matrix directly attacks the two narrowest observed margins and the main
shared numerical weaknesses at a small fraction of the old 120-row Stage-B
burden. It can falsify the finite-`B` realization before millions of
off-lattice trajectories are spent. A new cusp solve, by contrast, can succeed
while leaving the already-known physical anchor's parity/box weakness
untouched.

## 10. Minimal powered off-lattice package

Off-lattice production starts only after F1 passes and F2 is frozen. The
minimum scientific package is:

1. a compiled, transition-exact OU engine with the actual broad four-slab
   position-dependent Doi hazard, a proved homogeneous dominating rate, and
   no hazard clipping;
2. fixed trajectory fixtures and scalar/compiled parity tests, including
   contact-edge, zero/near-zero hazard, accept/reject, censoring, counter/RNG,
   and malformed-input HOLD cases;
3. byte-pinned physical controls, horizon, basin boundaries, windows, and
   positive local contrasts derived by the frozen F2 rule;
4. the complete deterministic `E_FV` envelope carried into MC acceptance, not
   merely point differences;
5. familywise alpha allocation, precomputed effect sizes, precomputed powered
   `N`, master seed, counter domain, chunk ledger, and two independent pool
   identifiers;
6. each pool separately passing the common target, plus the predefined pool
   regression diagnostic;
7. one execution at the frozen `N`, with no sequential top-up; and
8. an independent result audit that distinguishes process evidence from cusp,
   density-derivative, or absence claims.

For the trimodal anchor, MC should target positive quantities that it can
actually estimate: survival at frozen times, basin masses, fixed-window
probabilities, and positive peak-versus-valley window contrasts. Acceptance
requires lower confidence bounds above the predeclared positive floors and
compatibility with the deterministic FV envelope.

If powered `N` exceeds the already proposed ceiling of 50 million trajectories
or is operationally infeasible, the PRR cross-method route is `HOLD`; do not
weaken the effect, window, alpha family, or confidence rule after seeing that
answer.

## 11. Go/no-go and kill criteria

### 11.1 Current decisions

- **Current PRR submission:** `NO-GO`.
- **Round-92 allocation-cusp route:** `KILL FOR CURRENT MANUSCRIPT`.
- **New fixed-control route:** `GO-DESIGN / HOLD-EXECUTION`.
- **New cusp research:** `PARK`; it does not block the fixed-control route.

### 11.2 Fixed-control route kill criteria

Kill the fixed-control PRR route, without post-result repair, if any of the
following occurs:

1. the anchor loses the required five-root alternating topology on any
   predeclared parity/alignment/box/refinement configuration;
2. the complete FV envelope crosses the `0.005` basin-mass floor, `0.85`
   valley ceiling, prominence requirement, or any other frozen threshold;
3. odd-grid differences neither contract nor lie under the frozen floor;
4. interval root isolation or full-window derivative coverage fails;
5. boundary-layer/box diagnostics fail or the combined-box/fine challenge is
   incompatible with the smaller boxes;
6. the off-lattice powered `N` is infeasible or exceeds the frozen cap;
7. either MC pool fails a required positive contrast, basin-mass, survival, or
   FV-containment gate;
8. MC requires a sample top-up, target/window change, or threshold relaxation;
   or
9. a current primary-literature novelty audit shows that the theorem plus
   cross-method physical realization is not a substantive addition.

Consequences should be predeclared:

- deterministic anchor failure → stop MC and write a theorem-focused paper
  for a specialized venue, or redesign geometry in a future prospective study;
- MC failure after deterministic pass → do not claim grid-independent physical
  realization; reassess a narrower PRE/JCP paper;
- comparator failure → remove finite-`B` “control” language, but the
  realization paper may survive if all anchor gates pass;
- abstract channel lemma not accepted → retain the already accepted direct
  theorem; this improvement is valuable but not a route-kill criterion;
- no quantitative `B0` for `B=0.01` → keep theorem and numerical example
  explicitly separate; this is not by itself a kill.

### 11.3 Conditions for `SEND-2D`

The revised paper becomes `SEND-2D` only if all of the following are true:

1. the accepted theorem and its exact claim surface remain independently
   green;
2. F1 deterministic fixed-control robustness passes every frozen grid, parity,
   alignment, box, interval, topology, mass, and uncertainty gate;
3. F3 powered off-lattice validation passes once at the frozen `N`;
4. if “control” appears in title/abstract, the same-budget/same-support
   comparator passes its deterministic full-window topology gate;
5. the manuscript is rewritten around exposure clocks and a robust finite-`B`
   realization, with all cusp-centered release claims removed;
6. `d=3` is theorem/supplement context, not an unperformed positive-`B`
   headline;
7. the paper says fixed-window probability/contrast, not continuous-density
   `L1`, for MC evidence;
8. a current novelty/overlap audit, reproducibility audit, data/code release
   audit, figure audit, and rendered-PDF audit pass; and
9. the abstract, main figures, and main text alone contain the essential
   evidence and limitations.

## 12. Minimal sufficient evidence package for a credible PRR submission

### Already available

1. **Analytical backbone:** the independently accepted fixed-finite-`(d,m)`
   direct physical theorem and exact claim freeze.
2. **Candidate finite-`B` anchor:** one unchanged physical-`d=2`, `B=0.01`
   broad four-slab allocation with three finite-window, event-mass-qualified
   local maxima on two odd same-solver meshes.
3. **Independent-method design:** a mathematically sound unbounded off-lattice
   thinning route, currently under production hold.

### Still required

4. **F0 protocol:** result-independent fixed-control robustness and
   deterministic-to-MC selector freeze.
5. **F1 deterministic result:** full parity/refinement/alignment/box/interval
   closure for the unchanged anchor, with complete FV uncertainty.
6. **Comparator if claiming control:** at least one frozen same-budget,
   same-support allocation with a deterministic full-window lower-modality
   certificate.
7. **F2/F3 off-lattice result:** powered, predeclared unbounded process evidence
   for anchor event-law features, with two pools and independent audit.
8. **Analytical presentation upgrade:** preferably the independently audited
   separated-channel persistence lemma, explicitly specialized by the current
   slab theorem.
9. **Release closure:** current literature/novelty audit; exact claim rebaseline;
   reproducible source/data/code; main-text evidence; and final rendered PDF.

This is the minimum package that plausibly meets PRResearch's “significant,”
“authoritative,” and “substantive” criteria. It is deliberately smaller and
more coherent than adding a new cusp solver, a positive-`B` `d=3` phase
diagram, and a second continuum solver all at once.

## 13. Work order by information gain

1. **Close the route decision now.** Archive the allocation artifact as valid
   `HOLD`; prohibit current-manuscript cusp retuning.
2. **Write and attack F0.** Freeze the one-control eight-configuration matrix,
   optional comparator, interval gates, error envelope, and F1→F2 selector.
3. **Run the anchor robustness matrix first.** This is the cheapest decisive
   scientific attack. Stop immediately on a frozen kill gate.
4. **In parallel, finish method-only compiled off-lattice fixtures and extract
   the channel-dominance lemma.** Neither action consumes scientific MC data.
5. **If F1 passes, freeze F2.** Compute power and `N` without looking at MC.
6. **Run F3 exactly once.** No adaptive top-up or window changes.
7. **Only after F3 passes, rebaseline and rewrite the manuscript.** Lead with
   the mechanism, theorem, physical realization, and independent process
   evidence; move reduced cusp calculations to contextual/supporting roles.
8. **Revisit allocation cusps only as a separate project.** Use a transparent
   development/confirmation split and a new validated-continuation design.

## 14. Final adversarial judgment

The allocation `HOLD` is a serious P0 problem for the **old publication
logic**, but it is not a scientific collapse. The repository already contains
a stronger and more general core than the failed cusp search: a constructive
mechanism for arbitrarily many certified local modes at every fixed finite
dimension and mode count. The most efficient route to PRR is to make that
mechanism the paper's center and use the finite-`B` four-slab example as a
hard, independently validated physical realization.

The old proposal—fixed Stage-B plus off-lattice MC—is not sufficient because
Stage-B's parent cusp object does not exist. A **new** fixed-control robustness
matrix plus powered off-lattice MC can be sufficient, conditional on its
frozen gates passing and on honest naming. Adding one same-budget/same-support
comparator and extracting the separated-channel persistence lemma materially
raises the PRR case. Chasing the near-tolerance cusp continuation, positive-`B`
`d=3`, uniform-in-dimension bounds, or arbitrary patch geometry now would add
work faster than it adds evidential value.

**Final status: `NO-GO SUBMISSION / KILL OLD CUSP SPINE / CONDITIONAL GO NEW
FIXED-CONTROL PRR SPINE`.**
