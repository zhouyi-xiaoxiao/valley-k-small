# Round 70: independent adversarial attack on the Stage-B v4 design

Date: 2026-07-14  
Role: independent, result-blind numerical-analysis, inference, and provenance
attacker; distinct from the Round-69 repairer  
Verdict: **BLOCK-DESIGN / HOLD-EXECUTION**

## 1. Scope and non-execution boundary

This round independently attacks
`notes/positive_b_stage_b_validation_design_v4.md`.  It first read the complete
Round-67 attack and the complete Round-69 positive-regression test, then checked
the v4 document and Round-69 resolution against every requested closure:

- the interval error hull and all downstream consumers;
- the implicit cusp/fold and diagnostic certificate;
- the T0 selector, T1 role radii, and freeze timing;
- the absolute caps and odd-grid contraction gate;
- pool semantics;
- the manifest/auditor no-cycle graph; and
- workload, alpha, power-atom, and rate arithmetic.

No Stage-A object, hidden/canonical scientific result, mesh-65/97 model,
Stage-B FV row, cusp/fold solve, off-lattice trajectory, scientific producer,
scientific auditor, or main entry point was run.  V4, Round 69, the manuscript,
and every scientific file were left unchanged.  The only new executable is a
five-test, science-free counterexample/arithmetic check.

The attacked snapshot is:

| role | repository path | SHA-256 |
|---|---|---|
| Stage-B v4 design | `notes/positive_b_stage_b_validation_design_v4.md` | `e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691` |
| Round-69 v4 resolution | `audits/round_69_stageb_v4_design_resolution.md` | `7972335d11cb55337c248a39967173d548d711dad937bf9dbdfefd9d29f2ef27` |
| Round-69 positive regressions | `code/test_stageb_v4_design_resolution.py` | `b882aaa1737847dd58606140466b9c03572211767ea9ad4c208d7cdb69c20fb2` |
| Round-67 v3 attack | `audits/round_67_stageb_v3_independent_attack.md` | `4f71f9e517ce5d3ca44e403332fb52be37d070e7e546db284cbbed83bf4d6c35` |
| allocation-cusp promotion design | `notes/positive_b_allocation_cusp_promotion_design.md` | `ad072e83004ea3e3b5c3d01a58a872b5aedca74d13400fa04d6f917d4a06d1f5` |
| Round-70 science-free checks | `code/test_stageb_v4_design_round70.py` | `bf91141021375fd583fc1e85a75c6c931fd966637ad628c8b5bd84b632262d20` |

## 2. Executive decision

V4 genuinely closes the Round-67 interval-hull defect.  Its scalar envelope
contains both endpoint errors; the complete six-variable cusp--fold system
propagates cusp uncertainty; the saved-field radius formula is mathematically
usable; the absolute-cap table is restored; pool wording no longer claims
equivalence; the no-cycle graph is directed correctly; and all requested
integer, rational, and rate calculations recompute.

V4 nevertheless cannot receive `GO-DESIGN`.  Its literal odd-mesh Boolean gate
admits a noncontracting fine-grid jump whenever the *coarser* difference alone
is at the roundoff floor.  A finite allocation-weight counterexample passes the
full `E_abs` envelope and the printed odd-grid OR gate while violating the
stated contraction rule.  This can promote a false mesh-stability claim and is
therefore P0.

The T0 selector is also not yet byte-unique.  V4 uses an undefined candidate
displacement, leaves the secant/orientation/scale operands in prose, and calls
`down64`/`up64` without defining their exact directed semantics while Section
4.1 separately requires round-to-nearest after every operation.  Different
future selector implementations can therefore choose different saved controls
or role radii while claiming to implement Section 4.  That is P1.

The independent ledger is:

```text
P0 = 1
P1 = 1
P2 = 0

design status    = BLOCK-DESIGN
execution status = HOLD-EXECUTION
science status   = NOT RUN / NOT INSPECTED

AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

## 3. Closures independently verified

### 3.1 Round-67 interval-hull counterexample is closed

V4 constructs

```text
I_g = [down64(qhat_g-r_g),up64(qhat_g+r_g)]
E_FV = up64 max_g max(abs(L_g-U_ref),abs(U_g-L_ref)).
```

For

```text
qhat_g=0.00, qhat_ref=0.10, r_g=r_ref=0.08,
```

the two intervals are `[-0.08,0.08]` and `[0.02,0.18]`; the discrepancy upper
bound is `0.26`.  Thus both endpoint errors enter.  The reference-centred
`C_FV`, coordinatewise vector form, all-401-time curve form, absolute caps,
quarter margins, tolerance transforms, MC containment, and power implications
are normatively routed through this repaired object.  The old v3 maximum is
explicitly forbidden.  Round-67 P0-1 is conceptually closed.

### 3.2 Implicit cusp/fold error propagation is conceptually closed

Every fold is now a six-variable joint system containing the cusp equations,
fold equations, and `t_F-t_C-sigma*a=0`.  V4 requires:

```text
rho_inv, eps_J, gamma, K_up,
rho_lin, eps_F, eta_up, L_up, r_NK,
and an interval-Newton/Krawczyk unique-root inclusion.
```

The joint cusp projection must lie inside the standalone cusp box, the fold
projection supplies the fold coordinate interval, and every promoted output is
interval-evaluated over the certified root box with direct evaluation error
added.  This is a valid high-level closure of the missing correction-solve,
`F/J`, cusp-to-fold, and output-propagation links from Round 67.  Exact directed
operation semantics still need the P1 repair below before implementation.

### 3.3 Saved-field role-radius formula is mathematically sound

The formula

```text
rho_i = down64(min(1/128,b_i/4,s_i/4))
```

uses only the saved global box and seven saved seed coordinates.  It does not
require nonexistent upstream scalar trust radii.  Before rounding ambiguity,
`rho_i<=b_i/4` keeps a ball strictly inside the global box, and
`rho_i+rho_j<=d(z_i,z_j)/2` separates every pair.  Positive radii and an
outward pairwise-disjointness check are mandatory.  This closes the upstream
field-availability part of Round-67 P1-2.

### 3.4 Absolute caps are restored

The v4 table exactly retains the eight required caps:

```text
time                         0.05
allocation weight L_inf     0.005
peak/valley ratio            0.02
event-basin mass             0.001
final survival               0.01
scaled fourth derivative     0.50
singular value/ratio         0.01
dimensionless curvature      0.02.
```

Thresholded quantities use all eight interval endpoints and require
`E_FV<=min(E_abs,d/4)`; unthresholded coordinates use `E_abs` directly.  A
large scientific margin therefore cannot bypass an absolute cap.

### 3.5 Pool semantics and no-cycle graph are repaired

The pool check is now explicitly a powered same-generator regression
diagnostic.  Each pool separately must be compatible with the common target;
the difference interval must contain zero and meet its precision rule.  V4
sets `pool_statistical_equivalence_verified=false` and expressly says that the
difference interval need not be contained in an equivalence region.  No
equivalence claim remains.

The freeze graph is also acyclic at the declared level.  The selector package
precedes the Stage-A read; `M_B` is frozen before `A_B`; `M_B` never pins
`A_B`; and the external protocol records the manifest/auditor/test hashes.
The MC chain repeats the same order for `M_MC` and `A_MC`.  This closes the
Round-67 freeze-vocabulary defect, subject to making the selector itself exact.

### 3.6 Workload, alpha, power, and rate recompute

The eight state counts sum to

```text
26,333,190.
```

With eight fixed and seven implicit roles on every configuration:

```text
logical rows                          = 15*8 = 120
base-state cells / complete row pass  = 15*26,333,190
                                       = 394,997,850
two nominal complete passes           = 789,995,700.
```

The alpha ledger is exactly

```text
12  * 1/1200  = 1/100
78  * 1/5200  = 3/200
84  * 1/5600  = 3/200
116 * 1/11600 = 1/100
sum             1/20 = 0.05.
```

The fourth-family count is `8+(13+14)*2*2=116`, and the underlying power
primitive count is `2*(4+9+4+14)=62`.  Pooled views and the regression
diagnostic are functions of these pool primitives, so they do not create new
independent random atoms.

At high precision, the universal thinning bound is

```text
0.3489031062715236217098695567230565... < 0.35
margin = 0.0010968937284763782901304432769435....
```

These parts pass the independent audit.

## 4. P0 finding

### P0-1 — the roundoff-floor OR branch admits a noncontracting fine-grid jump

V4 Section 8.2 literally requires either

```text
D+(I_O129,I_O113) <= 5e-8
```

or

```text
D+(I_O161,I_O129) < D-(I_O129,I_O113).
```

Only the *coarser* difference appears in the roundoff-floor branch.  Therefore
that branch short-circuits the entire contraction requirement even if the
finer difference is large.

Consider zero-radius intervals for one allocation-weight component:

```text
I_O113 = [0.300,0.300]
I_O129 = [0.300,0.300]
I_O161 = [0.304,0.304]
I_ref  = [0.302,0.302].
```

Then

```text
D+(O129,O113) = 0             <= 5e-8,
D+(O161,O129) = 0.004,
D-(O129,O113) = 0,
```

so the sequence is not contracting, yet the printed OR gate returns true.  The
complete reference-centred envelope is only

```text
E_FV = 0.002 <= E_abs,weight = 0.005,
```

so the separate absolute-cap gate does not reject the row.  Values may be
translated by a common positive constant without changing the counterexample,
and the other weight components can compensate while remaining inside the
simplex.  It is therefore compatible with the physical weight domain.

This directly contradicts v4's sentence “A noncontracting sequence is HOLD”
and Round 69's statement that a noncontracting sequence cannot pass.  The
Round-69 positive test checks only that `0.9-0.4` is not smaller than
`0.4-0.0`; it never evaluates the complete OR with the floor branch, so it
cannot detect this bypass.  The exact counterexample is recorded in
`code/test_stageb_v4_design_round70.py`.

Because `GO-FV-STAGE-B` uses this gate to license the phrase “mesh-stable,” a
false scientific GO is possible.  This is P0, not a cosmetic strengthening.

**Required repair:** require either both adjacent differences to be at the
roundoff floor,

```text
max(D+(O129,O113),D+(O161,O129)) <= 5e-8,
```

or strict certified contraction,

```text
D+(O161,O129) < D-(O129,O113).
```

The mutation test must call the exact production Boolean and reject the finite
counterexample above.  Do not test only the contraction sub-expression.

## 5. P1 finding

### P1-1 — Section 4 is not yet a byte-unique T0 selector contract

V4 correctly moves selector code/tests/protocol before the Stage-A read, but
the mathematical selector it asks that future package to implement is not
fully specified.

In Section 4.3, v4 says to compute a “central chart secant,” orient it “toward
increasing signed branch time,” take the “smaller chart distance,” and then
use “saved candidate displacement `d`.”  It never defines:

- the exact secant operands and subtraction order;
- the exact scalar whose sign orients the tangent, including the tie HOLD;
- the two exact vectors and norm operations entering `ell`; or
- the displacement base, such as `d=theta_candidate-theta_branch`.

Those formulas existed explicitly in v3, but v4 neither reproduces them nor
contains a normative “all unspecified v3 clauses remain in force” import.
Its T0 ladder instead says that future code implements **Section 4 exactly**.
Two implementations can therefore use different plausible branch bases or
orientation operations and select different eligible/ranked saved pairs while
both claiming conformance.

There is a second exactness gap in the same T0 transform.  Section 4.1 requires
round-to-nearest/ties-to-even after every operation, while Section 4.4 calls

```text
rho_i=down64(min(1/128,b_i/4,s_i/4)).
```

V4 never defines `down64` or `up64`, never says whether each subtraction,
division, minimum, and norm is interval-evaluated before the final directed
conversion, and omits the MPFR/directed-transcendental convention that v3 had.
Applying `down64` to an already round-to-nearest intermediate is not the same
contract as evaluating the real expression downward.  One-ulp differences can
change a strict role-ball containment/HOLD boundary; the same ambiguity later
affects interval certificates and the first feasible sample size.

The fact that future source is hashed before Stage-A prevents post-data code
changes, but it does not make an under-specified T0 mathematical transform
unique.  The implementation would be choosing missing design semantics.

**Required repair:** before the selector package is written or audited, create
a new numbered design/addendum that:

1. writes the exact secant, orientation, `ell`, displacement, sign, tie, and
   pair-label equations with a complete displayed operation order;
2. defines `down64`/`up64` mathematically and freezes how every intermediate is
   outward-rounded, including `sqrt`, `log`, and `exp` where used;
3. requires global-box containment as well as pairwise ball disjointness under
   those exact interval operations; and
4. adds mutation fixtures in which changing the displacement base,
   orientation/tie rule, or directed-rounding operation changes selection or
   HOLD, proving that the frozen implementation rejects each change.

## 6. Verification and evidence quality

The following science-free checks passed:

```text
python3 code/test_stageb_v3_design_round67.py
  Ran 4 tests -- OK

python3 code/test_stageb_v4_design_resolution.py
  Ran 6 tests -- OK

python3 code/test_stageb_v4_design_round70.py
  Ran 5 tests -- OK

python3 -m py_compile code/test_stageb_v4_design_round70.py
ruff check code/test_stageb_v4_design_round70.py
  All checks passed
```

The Round-69 v4 test itself is Ruff-clean.  Running Ruff jointly on the
historical Round-67 test also reports one pre-existing import-order issue in
that historical file; it has no scientific effect and is not counted in the
design ledger.

The positive Round-69 test is useful for presence and arithmetic regression,
but it is not adversarial evidence that the full Boolean implications are
sound.  In particular, its “noncontracting” fixture never combines the
contraction expression with the floor exception.  Passing that test therefore
does not rebut P0-1.

## 7. Minimum repair and re-audit order

No science is authorized.  The shortest fail-closed path is:

1. repair the roundoff branch so both adjacent odd-grid differences must be at
   the floor, or else strict interval contraction must hold;
2. make the T0 selector operands, orientation, displacement, and all directed
   arithmetic byte-unique before any Stage-A object is opened;
3. add mutation tests for the exact P0 counterexample and every selector choice;
4. freeze and independently attack the actual selector source/tests/protocol;
   and
5. run another independent result-blind design audit.

Only a later audit with `P0=0` and `P1=0` may return `GO-DESIGN`.  Even that
would authorize selector/implementation work only; it would not by itself
authorize Stage-A, Stage-B, or off-lattice science.

## 8. Final boundary

```text
BLOCK-DESIGN
HOLD-EXECUTION
NOT RUN / NOT INSPECTED
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```
