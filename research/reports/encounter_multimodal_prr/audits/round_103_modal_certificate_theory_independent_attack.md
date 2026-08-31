# Round 103: independent attack on the modal-certificate PRR redirect

Date: 2026-07-14  
Role: independent theorem, numerical-evidence, and publication-spine reviewer  
Decision: **HOLD AS WRITTEN / GO THEORY REPAIR AND PROSPECTIVE FREEZE / NO POSITIVE-B EXECUTION**  
Open findings: **P0 = 2, P1 = 5, P2 = 2**

## 1. Scope, frozen boundary, and reviewed bytes

This audit reviewed but did not edit
`notes/modal_certificate_theory_and_prr_redirect.md`, whose SHA-256 was

```text
5aed52dae446c7d1ed836aea3a53d692e85e93f0e834cb6765924ea4ccd6a04a
```

The mathematical bridge was checked against
`notes/pde_mixed_jet_theorem.md`, SHA-256
`ac0e6cbb34d446d2b9ae2b52c22684ee72da7cadb04d864aacba085dff75f095`.
The exploratory table was reconstructed using the existing unbounded
OU-times-torus free-exposure kernel
`code/continuum_observable_four_patch.py`, SHA-256
`a553092f3d8bbf50fdf0124a3ea36ba32947c3b339cfcc0265a1cd7f6bc2d4da`.

No positive-budget state, allocation finite-volume grid, allocation-v6 mesh,
Stage-B row, killed semigroup, Monte Carlo trajectory, or manuscript claim
surface was evaluated or changed. The only workspace write is this report.
The numerical work in Section 8 below used only the already established
`B=0` analytic free-transition kernel and three finite-dimensional LPs.

The current PRResearch standard is that a submission should make a
high-quality, significant contribution and be an authoritative and
substantive addition to the literature; it does not require a cusp. See the
[official PRResearch About page](https://journals.aps.org/prresearch/about).

## 2. Executive verdict

The redirect has a sound core:

- alternating derivative signs do give ordered local extrema;
- endpoint and interval-curvature constraints are affine in nonnegative
  allocation weights;
- the maximum-margin checkpoint selector is a linear program;
- the existing exact-continuum mixed-jet theorem transfers strict `C^1`/`C^2`
  margins to sufficiently small positive budget; and
- the displayed exploratory LP weights, roots, ratios, and curvatures are
  numerically reproducible under the stated broad free-exposure kernel.

But the note is not yet a correct PRR spine. Two central inferences overreach:

1. Theorems 2.1 and 2.2 certify extrema **inside selected boxes** but do not
   exclude additional stationary points elsewhere in the declared window.
   Therefore two differently labelled partial certificates do not imply two
   different complete stationary topologies and do not, by themselves, force
   a path to meet the discriminant. Corollary 5.2 is false under the natural
   reading of “certified” used earlier in the note.
2. The maximum future claim says full topology persists under an independent
   off-lattice process. The proposed Monte Carlo can validate positive
   window contrasts, survival, and event probabilities; it cannot certify the
   absence of extra stationary points or an exact one-/two-mode topology.

Both errors are repairable without restoring a cusp. The repair is a complete
deterministic derivative certificate on the entire finite window, including a
signed derivative margin on the complement of all root boxes. The off-lattice
claim must then remain a positive event-law cross-check, not an exact topology
census.

## 3. Theorem 2.1: endpoint signs, platforms, and multiple roots

### 3.1 Literal non-strict-extremum conclusion: correct

Let `a=s_(2k-1)` and `b=s_(2k)`. Since `G'(a)>0`, the left endpoint cannot
maximize `G` on `[a,b]`; values immediately to its right are larger. Since
`G'(b)<0`, the right endpoint cannot maximize it; values immediately to its
left are larger. The extreme-value theorem therefore supplies an interior
maximizer, which is a local maximum. The valley argument is identical with
signs reversed. Disjoint open intervals make the selected extrema distinct.

This proof handles extra zeros and multiple roots. It does not need to choose
one particular zero of `G'`, and it is stronger and cleaner than the current
sentence that “the derivative changes” at an unspecified zero.

### 3.2 Strict or isolated mode conclusion: not implied under `C^1`

Endpoint signs alone allow a flat platform. For example, on `[0,3]`,

```text
G(t) = -(1-t)^2     for t <= 1,
       0            for 1 <= t <= 2,
       -(t-2)^2     for t >= 2.
```

This function is `C^1`, has `G'(0.5)>0` and `G'(2.5)<0`, but its maximum is a
whole plateau. It has non-strict local maxima, not an isolated or
nondegenerate density mode. A multiple zero at which the derivative really
changes sign can likewise be a strict but degenerate maximum.

Therefore Theorem 2.1 is valid only if “local maximum” is explicitly
non-strict. It should not alone be advertised as a robust modal certificate.
There are three precise repairs:

1. rename it an **ordered-extremum lower-bound certificate** and state that
   extrema may be non-strict, nonisolated, or degenerate;
2. add the actual positive-time analyticity/nonconstant hypothesis of the
   exact exposure clocks to rule out an interval platform, while retaining the
   possibility of isolated degenerate extrema; or
3. use Theorem 2.2's uniform curvature margins for every publication-facing
   mode claim.

Theorem 2.2 is otherwise correct after explicitly requiring `G in C^2` and
placing every closed box inside the interior of the positive-time window.
Strict curvature makes `G'` strictly monotone, the endpoint signs give exactly
one zero, and the curvature sign classifies it nondegenerately.

## 4. LP and interval linearization

### 4.1 Checkpoint LP: algebraically correct

For fixed checkpoint times and allocation-independent positive scales,

```text
sign_l * sum_j w_j g_j'(s_l) / sigma_l >= rho
```

is affine in `(w,rho)`. The simplex equality and lower weight bounds are also
linear. The selector is therefore a genuine LP, not a disguised root search
or allocation grid.

Required safeguards are missing from the theorem statement or future failure
contract:

- the example `sigma_l=max_j |g_j'(s_l)|` must be checked strictly positive;
  if every channel derivative vanishes at a checkpoint, normalization is
  undefined and the selector must HOLD;
- with `rho>=0`, an instance with no nonnegative sign margin is infeasible
  rather than having a nonpositive optimum; the output schema must distinguish
  `INFEASIBLE`, `OPTIMUM_ZERO`, and `OPTIMUM_POSITIVE` or remove the lower
  bound on `rho` and test its sign afterward;
- a deterministic secondary objective or exact declared tie-break is required
  when the LP optimum is not unique; and
- the scale bytes, solver bytes/options/tolerances, primal/dual feasibility
  residuals, and independently reconstructed constraints must be frozen.

### 4.2 Curvature enclosures: direction is correct, but must be uniform

If a certified bound obeys

```text
g_j''(t) <= hbar_jk  for every t in P_k,
```

then nonnegative weights give

```text
G_w''(t) <= sum_j w_j hbar_jk.
```

Thus `sum_j w_j hbar_jk <= -kappa_p` is a valid linear peak constraint.
Likewise, certified lower bounds `hunder_jk <= g_j''(t)` yield the linear
valley constraint `sum_j w_j hunder_jk >= kappa_v`. This argument would fail
for signed mixture weights, so simplex nonnegativity is essential.

The enclosure must be a simultaneous outward-rounded bound on the entire
interval, not the maximum of a dense floating-point sample. The same rule
applies to any componentwise interval bounds used for checkpoint derivatives.

### 4.3 Missing full-topology constraint

Peak and valley boxes alone give an **at-least** certificate. To certify an
exact finite-window stationary topology, partition the remainder

```text
R = I minus the interiors of all peak and valley boxes
```

into finitely many closed pieces and require a fixed signed bound on every
piece, for example

```text
q_r G_w'(t) >= eta_0 > 0  for every t in R_r,
```

with the sign `q_r` fixed by the intended alternating topology. Componentwise
interval lower bounds again make these constraints linear in `w`. This
complement certificate excludes every extra root and controls boundary-root
changes. Without it, the LP cannot certify “one” or “two” rather than “at
least one” or “at least two.”

## 5. Positive-budget mixed-jet transfer

### 5.1 Matching part: PASS, conditional on exact margins

The existing mixed-jet theorem gives, for the exact continuum Doi model on a
compact positive-time window and a declared compact control set,

```text
||d_t^r(F_B-G)||_infinity <= E_r^bd(B),  r=1,2,
```

where the explicit bound in its Eq. (4.5) is monotone increasing for `B>=0`.
Consequently:

- `E_1^bd(B)` below every raw endpoint/checkpoint derivative margin preserves
  the signs;
- `E_2^bd(B)` below every raw interval-curvature margin preserves strict
  peak/valley curvature; and
- `E_1^bd(B)` below the new complement derivative margin excludes all extra
  finite-window stationary points.

This exactly matches the accepted mode-persistence corollary. For the three
fixed controls alone no control derivative estimate is needed; `alpha=0`
suffices. A uniform region of allocations requires the compact-control and
complex-tube constants already present in the mixed-jet theorem.

### 5.2 The current `B_cert` definition needs repair

The note writes a supremum over budgets satisfying two inequalities and then
claims that every smaller budget passes. This implication is false for an
arbitrary error function `E_r(B)`. It is valid for the explicit monotone upper
bounds actually proved in the mixed-jet theorem, but that monotonicity and the
theorem's registered range `0<=B<=B_max` must appear in the definition.

A safe formulation is

```text
B_cert = sup { b in [0,B_max] :
               for every beta in [0,b],
               E_1^bd(beta) < rho_* and E_2^bd(beta) < kappa_* }.
```

For the explicit monotone exponential bounds, checking the endpoint `b` is
equivalent. The same definition must include the complement derivative
margin when exact topology, rather than only local boxes, is claimed.

### 5.3 Normalized LP margin is not the transfer margin

The transfer compares quantities with the physical derivative units of
`G'` and `G''`. If the normalized LP optimum is `rho`, the checkpoint sign
margin is

```text
rho_* = min_l sign_l * w^T g'(s_l),
```

not `rho` itself. Equivalently it is bounded below by
`rho*min_l sigma_l`. The independent reconstruction gives:

| target | normalized LP margin | smallest raw checkpoint derivative margin |
|---|---:|---:|
| one maximum | `0.8809904119598448` | `0.09879189274140476` |
| two maxima | `0.32540424848060423` | `0.0018180658405830398` |
| three maxima | `0.13616273641487356` | `0.0014249146622736185` |

The late-time checkpoint controls the two-/three-mode raw margin. The note
correctly says “physical derivative units,” but the exploratory section does
not serialize these raw numbers.

The displayed scaled curvatures are values **at floating-point roots**. They
are neither unscaled `G''` margins nor uniform lower bounds over peak/valley
boxes and therefore cannot be inserted as `kappa_*` in the mixed-jet theorem.
Certified physical-unit interval curvature margins remain missing.

Finally, the bridge is an exact-continuum weak-budget result. It does not
certify `B=0.01`, a finite-volume discretization, or SG convergence. The note
mostly preserves this boundary correctly.

## 6. Theorem 5.1: compactness and finite roots

### 6.1 A separate finite-root assumption is not necessary

For one allocation outside `D_B union E_B`, finiteness follows from the
stated differentiability and compact time interval, once the argument is
written correctly. If infinitely many stationary roots existed, compactness
would give a convergent subsequence `t_n -> t_*`.

- If `t_*` is an endpoint, continuity gives an endpoint stationary root and
  hence membership in `E_B`.
- If `t_*` is interior, continuity gives `F_t(t_*,w)=0`. If
  `F_tt(t_*,w)` were nonzero, the root would be isolated by local strict
  monotonicity/implicit-function reasoning, contradicting accumulation.
  Hence `F_tt(t_*,w)=0`, placing `w` in `D_B`.

Thus every off-discriminant/off-boundary allocation has a finite stationary
list. “Assume finitely many roots” need not be added as an independent
hypothesis.

### 6.2 Parameter-domain and uniform-continuation hypotheses are missing

The note calls `W` merely a connected subset of the simplex and then invokes
the implicit function theorem in `w`. `C^2 on I times W` and that invocation
are not well defined for an arbitrary subset. Require either:

- `W` relatively open in the simplex's affine hull; or
- `F` to extend `C^2` to an open neighborhood of `I times W` in time and
  affine allocation coordinates.

For boundary allocations, use relative charts or make the extension explicit.
Connectedness of `W` is unnecessary because the conclusion is already stated
componentwise.

The proof should then take a compact path image. Avoidance of `E_B` supplies a
uniform nonzero endpoint margin, confining all roots to a common compact
subinterval of `(tau,T)`. The preceding accumulation argument gives a finite
root list. Use disjoint implicit-function boxes around those roots and a
strict nonzero minimum of `|F_t|` on the compact complement to exclude new
roots. These neighborhoods make the ordered, typed root list locally
constant; a finite cover of the path yields the theorem.

With these repairs Theorem 5.1 is correct. The current one-sentence
compactness claim is not a sufficient proof by itself.

## 7. Corollary 5.2 and the discriminant claim

Corollary 5.2 is the main theoretical stop-ship issue. Theorem 2.1 proves only
at least a declared number of extrema; Theorem 2.2 proves exactly one root in
each declared box but says nothing about the complement. A control certified
in one peak box may actually have two or three peaks. Two controls with
different **partial certificate labels** can therefore have the same complete
stationary topology and lie in the same component off the discriminant.

The corollary becomes correct under either of two precise hypotheses:

1. the two endpoint allocations are known independently to have different
   complete finite-window stationary lists; or
2. each endpoint has the full box-plus-complement interval certificate from
   Section 4.3, so its exact root count, order, type, and endpoint signs are
   certified.

Only then does Theorem 5.1 force every joining path to meet
`D_B union E_B`. If endpoint derivative margins are uniform on a particular
path, the crossing cannot be through `E_B` and must be in `D_B`.

The fold sentence also needs the standard full rank/transversality condition.
At `(t_*,w_*)`, `F_t=F_tt=0` and `F_ttt != 0` give a scalar saddle-node in
time only when some allowed allocation tangent has nonzero derivative of
`F_t`; state that tangent and the resulting rank-two Jacobian explicitly.

## 8. Independent reconstruction of the exploratory table

### 8.1 Environment and method

The reconstruction used repository Python `3.12.13`, NumPy `2.5.1`, SciPy
`1.18.0`, the existing broad parameters

```text
patch centres      (0.35,0.60,0.75,0.90)
patch half-width   0.04
initial half-width 0.02
weight floor       0.03
```

and the note's exact checkpoints. Each LP was independently assembled as a
five-variable SciPy-HiGHS problem. A primary-kernel screen used 49,951 times
from `0.1` through `100` at spacing `0.002`, followed by Brent refinement and
Cauchy-jet curvature evaluation. This was a free-exposure calculation only.

### 8.2 LP values: reproduced

The primary LP returned:

| target | reconstructed weights | margin |
|---|---|---:|
| 1 | `(0.03,0.91,0.03,0.03)` | `0.8809904119598448` |
| 2 | `(0.5420243013882049,0.03,0.048245050837663034,0.37973064777413196)` | `0.32540424848060423` |
| 3 | `(0.4016285358628774,0.2761816314605931,0.03,0.2921898326765295)` | `0.13616273641487356` |

These agree with the note to displayed precision. Solving the same LP under
coarse and fine quadrature changed any weight by less than `1.1e-14` and any
reported normalized margin by less than `9e-15`.

### 8.3 Root values: reproduced

The dense primary screen returned:

```text
m=1: 8.26033359929114 max
m=2: 3.20929566018807 max,
     8.54351109665741 min,
     25.26744285992695 max
m=3: 3.22263384705437 max,
     5.44408799952102 min,
     8.11983574509482 max,
     13.98647073720503 min,
     24.65387395089713 max
```

The peak ratios were `1`, `0.618058048440443`, and
`0.6443920067157726`. The trimodal valley ratios were
`0.7623155612510425` and `0.7619538984631168`. Its scaled curvatures were

```text
(-7.3150247770,+10.4280507817,-7.2727418666,+7.7729007238,-2.0500895937).
```

The maximum coarse/primary/fine root-time difference was below `6.4e-13`;
topology and curvature signs agreed. Thus the numerical table is internally
credible and reproducible as floating-point exploration.

The bimodal valley ratio omitted by the legacy formatter is
`0.18692660856554522`; it should be reported in any new selector artifact.

### 8.4 What the reconstruction does not prove

The screen isolates sign-changing roots. It cannot exclude an even-multiplicity
root between samples, and it uses floating quadrature/Fourier truncation rather
than outward-rounded interval enclosures. The note acknowledges that it is not
an interval certificate, but it supplies no durable selector script, manifest,
canonical result, test, or command from which the table itself can be replayed
without reconstruction. The phrase “independent dense root diagnostic” is
also ambiguous: the table is separate from the LP objective, but no
implementation-independent kernel or root evaluator is identified, and the
same section later says it is not an independent solver result.

Before any positive-budget calculation, freeze a standalone free-exposure
selector/result chain with exact environment and kernel pins, candidate
constraints, raw and normalized margins, dual/primal residuals, deterministic
tie breaks, all curvature/complement interval certificates, and complete
one-/two-/three-root formatter support.

## 9. Can this replace the cusp as a PRR spine?

### Current note: no

The alternating-sign lemma and LP are useful but elementary. By themselves
they are not yet an authoritative, substantive PRResearch advance. The
existing accepted fixed-finite-`(d,m)` physical theorem supplies the deep
analytical backbone; the modal-certificate layer can organize that theorem
and select finite controls, but it does not replace the need for a convincing
physical realization.

As written, the note cannot be the PRR spine because the discriminant
corollary uses incomplete certificates, exact finite-window topology is not
certified, no positive-budget result exists for the new controls, and the
maximum future claim assigns an absence/topology conclusion to Monte Carlo.

### Repaired prospective route: conditionally yes

A cusp is not required. This route can be stronger and more general for the
paper's spatial-configuration question if all of the following are completed
without refitting:

1. repair Theorems 2.1 and 5.1 and replace Corollary 5.2 by a full-topology
   version;
2. freeze and independently audit the exact free-exposure LP plus
   box-and-complement interval certificate;
3. freeze the three new controls before **their own** first positive-budget
   evaluation, while disclosing that the broad family and a different
   positive-budget anchor were already known;
4. certify complete declared-window stationary structures with exactly one,
   exactly two, and exactly three maxima at one common installed budget, with
   identical supports/transport/initial law and only weights changed;
5. pass the full mesh/refinement/parity/alignment/box/error-envelope campaign
   for all promoted controls, including curvature, contrast, basin mass,
   survival, and endpoint/complement derivative gates;
6. use the powered unbounded off-lattice method only for predeclared positive
   window contrasts, survival, basin/event probabilities, and FV-envelope
   compatibility—not exact absence or root count;
7. compute an explicit `B_cert` only if the exact mixed-jet bound and certified
   physical margins overlap the intended budget; otherwise state that the
   theorem and finite-`B` realization are complementary, not quantitatively
   linked; and
8. complete a current primary-literature novelty audit covering multimodal
   first-passage/reaction laws, modality of mixtures, shape-constrained convex
   design, and conserved-resource spatial control.

If the lower-modality controls lack full deterministic complement exclusion,
the paper may claim multiple realizations but not redistribution-driven
topology control. If the off-lattice campaign fails, the grid-independent
physical claim fails. If only the exploratory LP survives, the appropriate
ceiling remains a specialized theorem/design paper rather than PRR.

### Required correction to the future reader-facing claim

Replace the statement that full topology persists “under an independent
unbounded off-lattice process” by two separate clauses:

```text
The deterministic interval-certified calculations preserve the declared
finite-window stationary topologies under all frozen numerical challenges.
The independent unbounded process preserves the predeclared positive window
contrasts, survival probabilities, and event-basin probabilities.
```

This says exactly what each method can establish.

## 10. Priority findings

### P0.1 — partial certificates do not imply a discriminant crossing

Corollary 5.2 silently treats the at-least/box certificates as complete
stationary topologies. They do not exclude extra roots. Add a full-window
box-plus-complement derivative certificate or require independently verified
complete stationary lists before invoking Theorem 5.1.

### P0.2 — future claim assigns exact topology preservation to Monte Carlo

The proposed off-lattice estimands can establish positive event-law features,
not the absence of extra modes. Restrict exact topology to deterministic
interval evidence and restrict MC to positive contrasts/probabilities.

### P1.1 — Theorem 2.1 does not guarantee an isolated mode under `C^1`

The literal non-strict local-extremum result is correct, but platforms and
degenerate multiple roots remain. Clarify the conclusion or require
analyticity/curvature; use Theorem 2.2 for robust modes.

### P1.2 — Theorem 5.1 lacks a valid parameter-domain hypothesis and proof

Require a relative-open allocation domain or a `C^2` extension to an open
neighborhood. Derive finite roots by the accumulation contradiction and use a
compact complement plus local implicit-function boxes. No separate finite-root
assumption is needed after this repair.

### P1.3 — `B_cert` and the transfer inputs are underspecified

Use the explicit monotone error upper bounds on `[0,B_max]`, raw derivative
units, certified uniform curvature margins, and a complement margin for exact
topology. The displayed normalized margins and root curvatures are not those
inputs.

### P1.4 — selector and interval evidence are not yet publication artifacts

The table is reproducible but has no pinned selector/result/audit chain,
deterministic degeneracy rule, interval proof, complete formatter, or
implementation-independence record. Freeze and attack this layer before any
new positive-budget run.

### P1.5 — PRR significance remains conditional

The certificate/LP layer is a useful general organization, not sufficient
novelty by itself. A robust same-budget finite-`B` topology change, independent
positive event-law validation, and current literature/overlap audit are still
needed for the official significant/authoritative/substantive standard.

### P2.1 — malformed LaTeX token

The LP line contains literal `,quad` instead of `,\quad` before `rho>=0`.

### P2.2 — exploratory presentation is incomplete/ambiguous

Report the bimodal valley ratio, raw margins, exact grid/configuration, and
distinguish a “separate floating-point diagnostic” from an independent solver.

## 11. Final ledger

```text
Theorem 2.1, non-strict extrema       = PASS AFTER CLARIFICATION
Theorem 2.2, unique boxes             = PASS AFTER EXPLICIT C2/INTERIOR ASSUMPTION
checkpoint LP algebra                 = PASS WITH FAILURE/TIE-BREAK SAFEGUARDS
interval linearization                = PASS ONLY FOR UNIFORM OUTWARD BOUNDS AND w>=0
positive-B mixed-jet transfer         = PASS CONDITIONALLY; B_cert FORMULA NEEDS REPAIR
Theorem 5.1 core topology theorem      = REPAIRABLE; CURRENT PROOF/HYPOTHESES INCOMPLETE
Corollary 5.2 from current certificates= FAIL
exploratory numerical table           = REPRODUCED; NOT CERTIFIED/NOT FROZEN
current PRR spine                      = HOLD
repaired prospective no-cusp spine    = CONDITIONAL GO-DESIGN
positive-budget/allocation execution  = NOT AUTHORIZED BY THIS AUDIT
P0                                     = 2
P1                                     = 5
P2                                     = 2
```
