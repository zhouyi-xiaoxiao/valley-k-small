# Round 67: independent adversarial attack on the Stage-B v3 design

Date: 2026-07-14  
Role: independent result-blind numerical-analysis, inference, and provenance
attacker; distinct from the Round-65 repairer  
Verdict: **BLOCK-DESIGN / HOLD-EXECUTION**

## 1. Scope and non-execution boundary

This round independently attacks
`notes/positive_b_stage_b_validation_design_v3.md`.  It does not accept the
Round-65 self-audit as evidence.  The audit recomputes the 120-row matrix,
workload arithmetic, alpha ledger, power-atom count, and local-mode statement
cardinalities, then attacks the deterministic-error envelopes, implicit-root
certificates, Stage-A-to-Stage-B substitution, off-fold saved-object rule,
mesh-stability gates, inference semantics, and one-way hash graphs.

No mesh, finite-volume model, Stage-A candidate, cusp/fold solve, off-lattice
trajectory, scientific producer, or scientific auditor was run.  The only new
executable is a four-test, science-free arithmetic/counterexample check.  The
v3 design itself was not modified.

The attacked snapshot is:

| role | repository path | SHA-256 |
|---|---|---|
| Stage-B v3 design | `notes/positive_b_stage_b_validation_design_v3.md` | `0c7119870e173bfbe5042b3f1c19c7c5851061940cab66e7e0dab98f54becd58` |
| Round-62 v2 attack | `audits/round_62_stageb_v2_independent_attack.md` | `b72472e721a12c6d19e007273d6dd347430643f737d0168c2022010891a531b1` |
| Round-65 v3 self-audit | `audits/round_65_stageb_v3_design_repair.md` | `fcbb84e25073f00b5f76075cfacaf0c13a7cb788b8124020eff481a773c40bfb` |
| allocation-cusp promotion design | `notes/positive_b_allocation_cusp_promotion_design.md` | `ad072e83004ea3e3b5c3d01a58a872b5aedca74d13400fa04d6f917d4a06d1f5` |
| Round-67 small checks | `code/test_stageb_v3_design_round67.py` | `fc17fbbd5e648a6b8629fb07d6030931c3dcaa820466851f6a88e84b28317342` |

The Stage-A v2 protocol/manifest snapshot used by Round 62 had hashes
`fa26995c0af9824dbba7231ace4fc08cef9664cb3bd09021a5cb90c1eed393e0`
and
`492922112d14ee62f610cfc3508f7286ff7d64ab28e5b7ea7b3fdff041ad78eb`,
respectively.  Stage-A repair work was live during this audit, so no mutable
in-progress Stage-A file is promoted here.  The relevant interface fact is
stable: neither the frozen v2 interface nor the in-progress v3 repair supplies
seven role-specific scalar cusp/fold trust radii of the kind assumed by Stage-B
v3 Section 6.2.

## 2. Executive decision

V3 correctly repairs several Round-62 defects.  In particular, it separates
eight unchanged physical controls from seven grid-specific implicit estimands,
runs all 15 roles on all eight configurations, deletes the unsupported
off-lattice fold-transition claim, gives `m=1` no synthetic contrast, restricts
off-fold selection to already saved Stage-A objects, closes the integer/rational
cardinalities, and states acyclic Stage-B and MC manifest/auditor graphs.

It is nevertheless not a GO design.  The central `E_FV` formula in both the
implicit and fixed-control paths is not an error envelope: it takes the maximum
of an observed grid difference and endpoint algorithmic errors instead of
combining the endpoint uncertainties.  A finite counterexample allows a true
grid/reference difference of `0.26` while v3 reports `E_FV=0.10`.  Because this
same underestimated quantity enters deterministic margins, MC--FV containment,
and the promoted numerical-cusp/event-law claims, a false scientific GO is
possible.

Three further P1 defects remain: the nonlinear/diagnostic certificate omits
required error propagation; the `T1` match-radius/selector transformation is
not instantiable or byte-unique from the frozen upstream interface; and v3
silently drops the absolute error caps and odd-mesh convergence gate of the
promotion design.  Three P2 ambiguities should be repaired in the same version.

The independent open ledger is:

```text
P0 = 1
P1 = 3
P2 = 3

design status    = BLOCK-DESIGN
execution status = HOLD-EXECUTION
science status   = NOT RUN / NOT INSPECTED

AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

## 3. Independent checks that pass

### 3.1 Role matrix and base-state-cell arithmetic

The eight state counts independently recompute as:

```text
113^3       = 1,442,897
128^3       = 2,097,152
129^3       = 2,146,689
161^3       = 4,173,281
166*129*129 = 2,762,406
129*172*129 = 2,862,252
166*172*129 = 3,683,208
207*215*161 = 7,165,305
sum          = 26,333,190
```

There are exactly eight fixed roles and seven implicit roles on every one of
the eight configurations:

```text
logical rows                             = (8+7)*8 = 120
base-state cells per complete row pass   = 15*26,333,190
                                           = 394,997,850
two nominal complete row passes          = 789,995,700
```

The labels are now honest: these are base-state cells, not FLOPs, Krylov
actions, augmented vectors, bytes, or wall time.  Requiring separate resource
caps and retaining null HOLD rows after a cap hit is correct.

### 3.2 Alpha ledger, power primitives, and `m=1`

The primitive scientific statement counts are exactly:

```text
basins                    = 3+1+2+3 = 9
windows                   = 5+1+3+5 = 14
positive local contrasts = 4+0+2+4 = 10
```

The `m=1` representative has one basin, one stationary-root window, and an
empty contrast array.  V3 does not use a dummy zero, contract-zero contrast,
absence test, or global exact-mode-count claim.  This closes Round-62 P0-2 by
honest claim deletion.

The alpha arithmetic closes exactly in rational arithmetic:

```text
12  * (1/1200)  = 1/100
78  * (1/5200)  = 3/200
84  * (1/5600)  = 3/200
116 * (1/11600) = 1/100
total             1/20 = 0.05
```

The pool-consistency family count is `8 + (13+14)*2*2 = 116`.  The underlying
pool-level power primitives are exactly

```text
2 * (4 survival processes + 9 basins + 4 S(100) + 14 windows) = 62.
```

Pooled views, contrasts, closure, and consistency are functions of these
primitives and should not be counted as additional independent random atoms.
The dependence-agnostic union-bound architecture is valid once the gates it is
asked to imply are themselves repaired.

### 3.3 Object classes, off-fold boundary, and maximum claim

The eight fixed controls and seven grid-specific implicit solutions now have
different schemas and byte semantics.  “No refit” correctly means unchanged
equations, role identity, and physical inputs, not identical cusp/fold solution
bytes across grids.

The off-fold selector no longer constructs or evaluates a new 65/97 candidate.
It may only use membership-consistent objects already stored in the audited
Stage-A candidate, mesh-65, mesh-97, and branch collections.  Missing coverage
is `HOLD-T1`.  This is the right high-level repair to Round-62 P0-3, subject to
the exact-transform defects in P1-2 below.

The off-lattice set is only the unchanged anchor and the three phase
representatives.  The four off-fold controls remain deterministic FV
challenges.  The explicit false flags correctly prevent a continuum/PDE cusp,
off-lattice fold, fourth jet, unimodal-side absence, or global exact mode-count
claim.

### 3.4 Universal thinning rate and directed hash graphs

The worst-case rate recomputes as

```text
(0.01/0.04)*(1+2^-48)*exp(1/3)
  = 0.3489031062715236 < 0.35,
```

leaving margin `0.001096893728476378`.  The finite/nonnegative/sum checks and
abort-without-clipping rule are appropriate.

The Section-13 Stage-B and MC graphs are acyclic at the stated level: the
scientific manifest pins the design, upstream audited substitution, producer,
and tests but not the independent auditor; the independent auditor hard-codes
the manifest; and an external protocol records the manifest/auditor/test hashes
without a back-edge.  Section 13 therefore closes the main Round-62 hash-cycle
defect, subject only to the wording cleanup in P2-3.

## 4. P0 finding

### P0-1 — `E_FV=max(mesh difference, algorithmic error)` is not an error envelope

The implicit path (v3 lines 416--425) defines, for reported values `q_hat`,

```text
x_FV = q_hat_ref
E_FV = max(max_g abs(q_hat_g-q_hat_ref), max_g r_alg,g),
```

and the fixed-control path repeats the same construction at lines 484--490.
This does not bound
the discrepancy between the uncertain grid and reference estimands because the
errors at the two endpoints can point in opposite directions.

A finite counterexample is:

```text
q_hat_g   = 0.00       r_g   = 0.08
q_hat_ref = 0.10       r_ref = 0.08

current E_FV = max(0.10,0.08,0.08) = 0.10.
```

The admissible values `q_g=-0.08` and `q_ref=0.18` obey both reported error
bounds, yet

```text
abs(q_g-q_ref) = 0.26 > E_FV.
```

`code/test_stageb_v3_design_round67.py` mechanically records this
counterexample.  The issue is not merely conservatism or notation.  The
underestimated `E_FV` is consumed by:

- implicit cusp/fold coordinate and scientific-margin gates;
- fixed-control probability, survival, and contrast margins;
- the `d_M`, `d_D`, and `gamma` tolerance transforms; and
- the MC--FV containment interval.

Thus a result can satisfy every coded v3 inequality even though the certified
grid/reference interval hull and cross-method discrepancy exceed the declared
acceptance set.  This can promote a false finite-volume-stability and
FV--off-lattice-agreement claim.

**Required repair before a new independent design audit:** represent every
deterministic value by an outward interval

```text
I_g = [down64(q_hat_g-r_g), up64(q_hat_g+r_g)].
```

For a true grid-to-reference discrepancy, use the outward interval-difference
hull, equivalently a bound no smaller than

```text
abs(q_hat_g-q_hat_ref) + r_g + r_ref
```

for each `g`.  If the manuscript/MC acceptance interval is intentionally
centred on the *reported* `q_hat_ref`, define that separate centre radius as

```text
max_g max(abs(inf(I_g)-q_hat_ref), abs(sup(I_g)-q_hat_ref)),
```

which includes `r_ref` through the reference row.  Do not use one quantity for
both meanings without proving the conversion.  Rebuild every margin and
containment formula from these interval objects with outward rounding, add
opposite-sign endpoint mutation tests, and independently recompute the complete
gate implication.

## 5. P1 findings

### P1-1 — the implicit-root error certificate is not closed

Section 6.3 (especially lines 384--440) improves on raw residual reporting,
but three necessary links are still missing.

First, `eta=up64(norm_inf(solve(J,F)))` rounds an already approximate linear
solve upward by one binary64 step.  That is not an upper bound on
`||J^{-1}F||`.  The text residual-checks the inverse norm `K`, but does not
residual-check the Newton correction used for `eta` or include interval
evaluation errors in `J` and `F`.

Second, each fold equation contains the numerically solved cusp time `t_C,g`.
The fold certificate treats that input as exact.  An error in `t_C,g` shifts
the third fold equation and the corrected fold root; neither the cusp radius
nor the induced fold-coordinate/diagnostic error is propagated.

Third, the vector envelope is said to be “augmented by the normalized
algebraic coordinate bound,” but the operation is not defined.  It is unclear
whether the bound is added to each endpoint, maximized, or converted through a
specific scaling matrix before the matching metric is applied.  This is
outcome-relevant because it controls the `match_radius/4` gate.

**Required repair:** freeze interval evaluations of `F` and `J`; for an
approximate correction `s`, certify for example

```text
eta_up >= ||s||_inf + K_up*||F-J*s||_inf
```

plus the outward `F/J` evaluation terms.  Either solve cusp and each fold as a
joint certified system or propagate the cusp interval through the fold system
with an explicit sensitivity/interval bound.  Finally, define one exact
coordinate interval-hull formula in the Section-6.2 metric, including the
scaling map and both endpoint errors.  Mutation tests must make each omitted
term cause HOLD.

### P1-2 — the `T1` match/selector transform is not instantiable from the frozen interface

Section 6.2 (v3 lines 353--380) sets the cusp radius to an “exact upstream cusp
trust radius” and
each fold radius to the smaller of an “exact upstream trust radius” and a
saved-seed separation.  The frozen Stage-A v2 interface supplies a global
`9<=t<=18`, `||theta||_infinity<=0.15` trust box and solver limits, not seven
role-specific scalar radii in the v3 matching norm.  The active Stage-A v3
repair also confirms that it does not introduce these seven fields.  There is
therefore no exact upstream value for `T1` to copy, and no frozen rule that
converts the asymmetric global box to such a radius.

The off-fold selector has a related `T0` gap.  Its dot products, norms, rank
ratios, and tie breaks use a “future pinned binary64 implementation.”  Freezing
the implementation only at `T1`, after the Stage-A values are visible, leaves
rounding mode, primitive sequence, FMA policy, norm evaluation, and tie
semantics selectable at the result boundary.  Also, Section 4.1 deliberately
requires three collection copies to share a candidate index and bytes, while
Section 4.3 says two distinct objects sharing a candidate index/byte string are
HOLD; the uniqueness domain is not stated.

The saved-object-only scientific boundary is sound, but the current transform
is not byte-unique or executable.

**Required repair:** before any Stage-A result is opened, either (a) add and
independently audit seven explicit role radii to a new Stage-A manifest, or (b)
define a unique formula deriving them from already frozen boxes and seed
coordinates.  Pin a small selector implementation and tests at `T0`, including
round-to-nearest/ties-to-even, operation order, FMA policy, norm/dot formula,
nonfinite handling, and total-order tie semantics.  State uniqueness per
collection and allow the intentional same-candidate copies across the three
collections.  Re-audit this interface after the upstream Stage-A version is
stable.

### P1-3 — v3 drops the frozen absolute caps and odd-mesh convergence gate

The allocation-cusp promotion design, lines 646--707, requires

```text
E_q <= min(E_abs,q, d_q/4)
```

with fixed absolute caps including cusp/root time `0.05`, allocation weight
`0.005`, scaled fourth derivative `0.50`, singular value/ratio `0.01`, and
dimensionless curvature `0.02`.  It also requires, unless already at the
roundoff floor,

```text
abs(q_161-q_129) < abs(q_129-q_113)
```

for every claimed scalar coordinate and jet.

V3 contains neither the `E_abs` table nor the odd-mesh contraction gate.  It
uses only `E_FV<=d_q/4` for thresholded diagnostics and
`E_FV(r,z)<=match_radius/4` for coordinates; local odd/even/refinement
differences are explicitly diagnostics.  A large scientific margin can
therefore permit a much larger cross-grid change than the predeclared absolute
cap, while the undefined/global trust radius can permit a cusp allocation
shift far exceeding `0.005`.  Three noncontracting odd-mesh values can pass as
long as all remain inside that broad envelope.

This is not the frozen mesh-stability standard that the promotion design says
supports `PASS-FV-ALLOCATION-CUSP`.  It also contradicts Round 65's statement
that the repair retains the relevant physical checks without weakening.

**Required repair:** restore the exact quantity-to-`E_abs` map and the
odd-mesh contraction/roundoff-floor rule for all cusp/fold coordinates and
claimed diagnostics, using the corrected interval envelopes from P0-1.  If the
authors intentionally reject those upstream gates, create a newly numbered
scientific promotion design before execution, justify the weaker criterion,
and narrow “mesh-stable” to the exact finite-grid threshold-robust statement it
actually establishes.

## 6. P2 findings

### P2-1 — pool “consistency” is a non-rejection gate, not an equivalence certificate

Section 9.3, lines 693--696, requires a pool-difference confidence interval to
contain zero and
its half-width to be no larger than the sum of two tolerances.  For a symmetric
interval `[d_hat-h,d_hat+h]`, zero containment gives `abs(d_hat)<=h`.  Together
with `h<=delta`, the interval can still extend to `2*delta`; it is not contained
in `[-delta,delta]` and therefore does not establish equivalence at `delta`.

This does not corrupt the pooled scientific intervals, and the two pools are
generated by the same frozen mechanism, so it is not elevated above P2 here.
Still, the label and GO language should be exact.  Either call it a powered
same-generator regression diagnostic, or freeze an equivalence margin and
require `abs(d_hat)+h<=delta` (with its power implication updated).

### P2-2 — two endpoint/identity typos should not enter an implementation schema

The MC--FV interval is printed with a double comma:

```text
[x_FV-E_FV-tau_q,,x_FV+E_FV+tau_q].
```

The intended two endpoints are mathematically evident, so this is not a P0/P1
by itself.  Replace it by a single comma and serialize named `lower`/`upper`
fields.  Also repair the Section-4.3 “distinct objects share a candidate
index/byte string” wording as specified in P1-2 so intentional cross-collection
copies cannot be mistaken for duplicates.

### P2-3 — the freeze ladder should use the same no-cycle vocabulary as Section 13

Sections 3.1/3.2 say `T1` or `T2` freezes the producer/auditor chain, whereas
Section 13 correctly forbids a scientific manifest from pinning its auditor.
The directed graph is clear enough to pass the main cycle audit, but the freeze
ladder should explicitly say that `T1/T2` freezes the scientific producer and
the external no-cycle audit *protocol*, while the later independent auditor
hard-codes the already frozen manifest.  This removes a future implementation
choice between a cycle and an unpinned auditor.

## 7. Minimum repair and re-audit order

No science is authorized.  The shortest fail-closed order is:

1. replace both `E_FV` formulas by outward interval-hull constructions and
   propagate the correction through every deterministic margin, tolerance,
   MC--FV containment, and power implication;
2. close the Newton-correction, `F/J`, cusp-to-fold, scalar-gradient, and
   coordinate-scaling error certificates;
3. freeze an upstream-compatible seven-role radius interface and a byte-exact
   saved-object selector before Stage-A values can influence implementation;
4. restore the absolute caps and odd-mesh contraction gate, or explicitly
   version and narrow the scientific claim;
5. clean the consistency, endpoint, duplicate-scope, and freeze-graph wording;
6. add mutation tests for opposite endpoint errors, missing cusp propagation,
   absent radii, FMA/tie changes, deleted absolute caps, and noncontracting odd
   sequences; and
7. run a new independent result-blind design attack.

Only after the new audit reports `P0=0` and `P1=0` may the Stage-B
implementation package be frozen.  A successful design re-audit would still
authorize only implementation, not a mesh run or manuscript claim.

## 8. Verification commands and final boundary

The science-free check was run as:

```text
python3 code/test_stageb_v3_design_round67.py
```

Result:

```text
Ran 4 tests
OK
```

The four checks pin the attacked v3 SHA, recompute the matrix/workload, close
the rational alpha and power cardinalities, and exhibit the deterministic
`E_FV` counterexample.  `python3 -m py_compile` also passed.

Final decision:

```text
BLOCK-DESIGN
HOLD-EXECUTION
NOT RUN / NOT INSPECTED
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```
