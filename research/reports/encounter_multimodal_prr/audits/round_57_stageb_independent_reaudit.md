# Round 57: independent result-blind Stage-B design re-audit

Date: 2026-07-14  
Role: independent adversarial re-audit of the minimum deterministic/off-lattice
Stage-B design  
Verdict: **HOLD-STAGE-B / GO-AFTER-CONTRACT-REPAIR**

## 1. Scope and non-execution boundary

This round re-audits the design proposed in Round 54.  It did not open a
hidden or canonical positive-`B` result, run a scientific finite-volume mesh,
generate a scientific Monte Carlo path, or modify a producer, manifest,
protocol, result, or manuscript.  The only repository change is this audit.

The following snapshot was read:

| role | repository path | SHA-256 |
|---|---|---|
| attacked Stage-B design | `audits/round_54_stageb_design_attack.md` | `5de663b0db0147a27b7af8901f3ae0a26a72a333ab5f95fbd2610e92e9294265` |
| allocation-cusp promotion design | `notes/positive_b_allocation_cusp_promotion_design.md` | `ad072e83004ea3e3b5c3d01a58a872b5aedca74d13400fa04d6f917d4a06d1f5` |
| off-lattice method design | `notes/off_lattice_doi_thinning_design.md` | `349541a954e665d0a68b3989e6f38f5edc725b00f77e4811147c1de262fc7961` |
| off-lattice POC source | `code/off_lattice_doi_thinning_poc.py` | `90466d074d3b6d302143919d4160beb36109e9686312e3a33670321e4f297e9d` |
| off-lattice POC tests | `code/test_off_lattice_doi_thinning_poc.py` | `986e839ebaa7f5b56d328826312fcce1f1305a2493108e5da8d7558992cc365d` |

These hashes are evidence anchors only.  No scientific entry point from the
snapshot was executed.

## 2. Executive decision

Round 54 gets the high-level evidence architecture right:

1. meshes 65 and 97 remain discovery, not validation;
2. a separately frozen finite-volume Stage B tests mesh, parity, box size, and
   a fine-grid/enlarged-box corner;
3. a later, separately frozen unbounded off-lattice process validates event-law
   observables but not the cusp fourth jet; and
4. the two independent scientific Monte Carlo pools are samples, whereas the
   exact-ID rerun is only a reproducibility duplicate.

The universal thinning bound, cell counts, grid-spacing construction, and
headline candidate-cost multiplier all recompute correctly.  The proposed
familywise type-I allocation also has a valid conservative interpretation.

The design is nevertheless not fail-closed yet.  This re-audit finds two new
P0 defects: the scheduled deterministic rows do not provide an uncertainty
envelope for every off-lattice control, and the proposed `E_FV` is not in fact
an envelope around the declared reference `x_FV`.  It also finds three P1 and
two P2 contract gaps.  These are pre-run design defects and can be repaired
without inspecting any scientific outcome.

New open count beyond the already recorded Round-54 blockers:

```text
P0 = 2
P1 = 3
P2 = 2
```

## 3. Independent recomputations that pass

### 3.1 Universal thinning rate

For nonnegative unit-sum allocations, disjoint midpoint supports give

\[
 \|K_w\|_\infty
 \le {B\max_jw_j\over Ws}e^{1/3}
 \le {0.01\over 1\times0.04}e^{1/3}
 =0.3489031062715224\ldots .
\]

Thus `Lambda=0.35` is a valid result-blind common domination rate.  The
Stage-A simplex floor would even imply `max(w)<=0.91`, but the broader
unit-simplex proof is safer and avoids depending on that numerical gate.  The
candidate-rate multiplier relative to the POC is exactly

```text
0.35 / 0.13 = 2.692307692307692...
```

and the pre-reaction expected candidate count at horizon 100 is bounded by
`0.35*100=35` per path.  The production code must still validate finite,
nonnegative, unit-sum weights and the disjoint-support premise before any
scientific ID is consumed.

### 3.2 Grid counts and the `MR+F` corner

Every state count in Round 54 recomputes:

| label | cells | product |
|---|---:|---:|
| `O113/Base` | `(113,113,113)` | `1,442,897` |
| `E128/Base` | `(128,128,128)` | `2,097,152` |
| `O129/Base` | `(129,129,129)` | `2,146,689` |
| `O161/Base` | `(161,161,161)` | `4,173,281` |
| `M+` | `(166,129,129)` | `2,762,406` |
| `R+` | `(129,172,129)` | `2,862,252` |
| `MR+` | `(166,172,129)` | `3,683,208` |
| `MR+F` | `(207,215,161)` | `7,165,305` |

The first seven sum to `19,167,885`.  The stated `70`-row workload
`191,678,850`, the stated `77+9` workload `275,334,480`, and its doubled value
`550,668,960` are arithmetically correct for the rows that Round 54 actually
schedules.

The `MR+F` spacing also does what it claims:

```text
coordinate          O161/Base          MR+F
midpoint             2.1/161            2.7/207   (exactly equal)
relative parallel    3.6/161            4.8/215   (relative change about -0.155%)
transverse           1/161              1/161     (exactly equal)
```

The `215` relative cells are the nearest integer to retaining the O161
spacing on a width-4.8 interval.  Thus `MR+F` is a legitimate fine-grid plus
large-box interaction corner.

### 3.3 Type-I error, two pools, and no top-up

The proposed family allocations sum to `0.050`:

```text
0.010 survival
+ 0.015 basin masses and agreements
+ 0.015 contrasts and window agreements
+ 0.010 pool consistency
= 0.050
```

If every final statement and required one-/two-sided tail is enumerated before
scientific IDs exist, Bonferroni division within these families controls the
FWER without requiring independence.  Reusing the same observations for a
pooled estimate and pool-consistency checks does not invalidate that union
bound.  The exact-ID rerun must receive no alpha because it is the same sample,
not new evidence.

The no-top-up rule is also correct.  Retrying a failed chunk with the exact
same trajectory IDs under a frozen operational rule is a recovery action, not
a top-up; allocating new IDs after looking at counts is forbidden.

### 3.4 Held-out timing

The `T1/T2/T3` split is scientifically defensible in principle:

- `T1`: after audited Stage-A discovery and before any Stage-B
  control--configuration evaluation, freeze all physical controls and the
  deterministic validation contract;
- `T2`: after audited deterministic validation and before any production
  trajectory ID exists, instantiate the already frozen window/cut algorithms,
  tolerances, alpha rows, and powered sample sizes; and
- `T3`: execute once without adapting to partial counts.

“Held out” is correctly a property of an exact control--configuration pair,
not a mesh label.  Meshes 65 and 97 are discovery.  A production Monte Carlo
ID is genuinely held out only if it is first generated after the complete
`T2` freeze.

## 4. New severity ledger

### P0-1 — the matrix cannot construct `E_FV` for every MC control

Round 54 defines the off-lattice set `C_MC` to include four controls on
opposite sides of the two fold branches.  It then schedules those four
controls only on `MR+F`.  The first seven configurations carry the cusp, six
on-fold nodes, anchor, and three phase representatives, but not the four
off-fold controls.

This contradicts the requirement that **every** MC estimand have all of these
terms:

```text
O129--O161 refinement
E128--O129 parity
Base--M+/R+/MR+ box changes
MR+--MR+F fine/large refinement
```

For an off-fold control evaluated only at `MR+F`, none of the first three
terms and the coarse `MR+` endpoint of the fourth term exists.  Therefore its
`E_FV` cannot be computed, and parity/box stability of the claimed modality
change is not tested.  On-fold continuation nodes do not substitute for the
distinct off-fold physical allocations.

**Required repair:** every deduplicated physical control in `C_MC` must run on
every configuration used in its envelope.  The simplest fail-closed rule is
to carry all `C_MC` controls over all eight configurations.  Exact duplicates
may be evaluated once only under a predeclared byte-equality rule while all
role labels remain in the result schema.

Without duplicates, adding the four off-fold controls to the first seven
configurations changes the indicative workload to

```text
15 role rows on each of the first seven grids + 9 on MR+F = 114 rows
state-law cells per execution = 352,006,020
two executions               = 704,012,040
```

The manifest must compute the final number from the frozen deduplication map;
it must not retain the smaller Round-54 workload after repairing the matrix.

### P0-2 — the declared `E_FV` is not an envelope about `x_FV`

Round 54 declares `x_FV=q_MR+F` but defines `E_FV` as the maximum of several
local/component differences.  A maximum of edge increments does not
necessarily bound the distance of each validation value from `MR+F`.

For example, the following scalar values satisfy component differences of
only one:

```text
q_O129/Base =  0
q_O161/Base = -1
q_MR+       =  1
q_MR+F      =  2
```

The proposed rule returns `E_FV=1`, yet
`|q_MR+F-q_O161/Base|=3`.  The same-sign accumulation can occur across mesh
and box changes.  Consequently the current rule can understate the empirical
uncertainty, pass a quarter-margin gate incorrectly, and make an FV--MC
agreement interval too narrow.

**Required repair:** for each physical control `c`, scalar estimand `q`, and
one fixed measurable time set `A_c`, use an actual reference-centred envelope,
for example

\[
 E_{FV}(q,c)=\max\left\{
   \max_{g\in\mathcal G_c}|q_g(c;A_c)-q_{MR+F}(c;A_c)|,
   r_{\rm alg}(q,c)
 \right\}.
\]

Here `G_c` contains every required odd/even/base/box configuration and
`r_alg` is the independently converted algebra/root residual.  Keep the
individual edge differences as diagnostics, but do not call their maximum an
envelope.  All configurations must integrate the density over exactly the
same cuts/windows; comparing mesh-specific windows would compare different
estimands.

The `T1` package should freeze the transformation from validated roots to
time sets.  A separately audited deterministic-to-MC freeze at `T2` may
substitute the audited `MR+F` values and recompute every grid integral over
those same time sets.  It may not select a more favorable reference grid or
time set.

### P1-1 — the physical boundary-strip contract is not mechanically defined

The widths `0.10` in midpoint and `0.20` in relative-parallel are sensible,
but neither is an integer number of cells.  For example:

```text
0.10 / h_M = 6.14 cells on O129/Base and 7.67 on O161/Base
0.20 / h_R = 7.17 cells on O129/Base and 8.94 on O161/Base
```

Selecting cells by centre or by any-overlap would therefore produce different
physical strips on different grids.  Round 54 does not freeze the partial-cell
integration convention or the inclusion--exclusion rule at midpoint/relative
strip intersections.

More importantly, the sentence that killed strip mass is no larger than its
“free-law counterpart” is true only when killed and free laws use the **same
reflected process**.  It is not a valid comparison between the reflected FV
process and the unbounded Gaussian OU law: reflection can accumulate mass
near a face.  An unbounded OU tail is a useful smallness diagnostic, not a
rigorous pointwise upper bound for the reflected strip mass.

As a plausibility check only, maximizing the unbounded Gaussian tail over
`0<=t<=100` and the compact initial support gives approximately
`2.62e-13` for the baseline midpoint strips and `3.54e-15` for the baseline
relative strips.  This supports the choice of a loose numerical `1e-6` gate,
but it does not repair the comparison theorem.

**Required repair:** define each physical strip as a measurable subset of the
box and compute, for every FV cell `C_i` carrying mass `p_i`,

\[
 \sum_i p_i {|C_i\cap S|\over |C_i|},
\]

with exact tensor overlap fractions and exact union weights.  Freeze the
saved time set and report all four faces plus the union.  Label the unbounded
OU calculation as a diagnostic, or replace it by a valid same-reflected-law
bound or a rigorous coupling/hitting-probability bound.

### P1-2 — the sample-size rule is not a joint all-gates power certificate

Round 54 asks for at least `0.90` power for each promoted mass or contrast to
meet its scientific inequality and realized precision condition.  The final
decision, however, is a conjunction over many controls, masses, windows,
agreements, survival rows, and two-pool checks.  Per-statement power of `0.90`
does not imply probability `0.90` that the complete experiment passes.  With
`K` independent statements it could be only `0.9^K`; dependence does not
provide a general lower bound that fixes this.

This does not inflate type-I error, but it can make the supposedly powered,
fixed, no-top-up experiment predictably underpowered for its own global GO
gate.

**Required repair:** freeze one common `N` or per-control vector such that,
under the declared deterministic planning alternatives,

```text
P(all mandatory scientific, agreement, precision, and pool gates pass) >= 0.90.
```

Use an exact joint multinomial/binomial calculation where feasible or a
conservative power-failure union bound.  Include the pool split and every
gate that can fail statistically.  Then round up once to the frozen chunk
multiple and forbid optional top-up.  If the required total exceeds `N_max`,
the pre-run result is HOLD or a claim narrowing completed before any
scientific ID exists.

### P1-3 — `T1` and `T2` leave control identity and statement skeleton ambiguous

Round 54 says at `T1` to freeze the controls, but its `T2` row again says to
freeze the “exact MC controls.”  Read literally, that permits a Stage-B result
to change the control union before Monte Carlo.  The intended design appears
stricter, but a production protocol must not rely on intent.

**Required repair:** at `T1`, pin an immutable map

```text
physical control bytes -> all role labels -> expected retained topology
                       -> required basin/window/contrast statement skeleton.
```

At `T2`, only substitute the audited numerical roots, cuts, window widths,
`x_FV`, `E_FV`, tolerances, alpha per enumerated tail, and powered `N`.  A
missing root, changed topology, nonpositive tolerance, or unavailable row is
a global HOLD.  It is not permission to remove a control or statement.

### P2-1 — endpoint and alpha-ledger serialization must be exact

Continuous event times hit a deterministic cut with probability zero, but a
binary64 implementation still needs a unique counting rule.  Freeze half-open
basins/windows, the treatment of `T=100`, and the exact order of every
control, statement, tail, pool, and pooled estimate.  Require integer closure
from those definitions.  This removes hash/reproducibility ambiguity without
changing the inferential mathematics.

### P2-2 — a second deterministic solver is optional only under the narrow claim

Round 54 is correct that a second deterministic solver is not the minimum
addition for the focused claim:

> a mesh/parity/box-stable **finite-volume numerical allocation cusp**, with
> associated finite-resolution event-law features independently preserved by
> the unbounded off-lattice Doi process.

Under that wording, the FV method owns roots, jets, rank, and the numerical
cusp; off-lattice thinning owns only survival, masses, fixed-window
probabilities, and signed finite-resolution contrasts.  Off-lattice evidence
does not certify absence of every additional mode, a fourth jet, or the cusp
Jacobian.

The stronger labels `continuum_cusp_verified` and `PDE_cusp_verified` must
remain false.  If a second FEM/DG/spectral solver is later added, the paper
must also show that solver's own mesh/box convergence and cross-solver
agreement.  Two agreeing discretizations are strong numerical corroboration,
not by themselves a rigorous continuum existence theorem.  A rigorous flag
requires an a posteriori/analytic error certificate controlling the roots,
fourth jet, mixed jets, rank, and determinant.

## 5. Corrected minimum freeze

Before any Stage-B scientific configuration is evaluated, a new package must
pin and independently audit all of the following:

1. the upstream audited Stage-A result and audit;
2. the exact physical-control/role map at `T1`, including all four off-fold
   controls and expected statement skeletons;
3. all eight deterministic configurations and every control--configuration
   row needed by that control's reference-centred envelope;
4. exact physical partial-cell boundary-strip operators and a valid analytic
   diagnostic statement;
5. the same-time-set `x_FV=q_MR+F` and true reference-centred `E_FV` rule;
6. finite structural HOLD rows for any missing value;
7. the `T2` deterministic-to-MC derivation package, with no freedom to alter
   controls or expected topology;
8. `Lambda=0.35`, exact control-specific hazard validation, separate test and
   scientific ID namespaces;
9. one fully enumerated global-alpha ledger over pooled and poolwise claims;
10. a joint all-gates power calculation, exact frozen `N`, `N_max`, chunk
    multiple, and no-top-up rule; and
11. two-process deterministic and two-pool Monte Carlo chains with pre-frozen
    auditors, final-byte rehashing, and failure-atomic promotion.

## 6. Final GO/HOLD

### `HOLD-STAGE-B` now

The current design remains non-executable.  The missing off-fold matrix rows
and non-envelope `E_FV` are P0.  They can leave a required MC comparison
undefined or falsely narrow.  The strip, power, and freeze ambiguities also
prevent a fail-closed manifest.

### `GO-DESIGN` after repair

The route is design-ready only after a new numbered protocol/manifest and
pre-run audit close every Round-54 blocker plus all seven findings above,
without reading a scientific Stage-B or production-MC result.

### Claim scope after eventual scientific passes

`GO-FV-STAGE-B` plus `GO-OFF-LATTICE` can support the focused numerical-cusp
and independently validated event-law statement.  It cannot support a
rigorous continuum/PDE cusp, and it cannot turn fixed-window Monte Carlo
contrasts into a global topology theorem.
