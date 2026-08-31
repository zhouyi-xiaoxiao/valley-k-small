# Round 04 catastrophe-algebra audit — Reviewer A

Date: 2026-07-11  
Reviewer: A (independent algebraic and numerical reproduction)  
Verdict: **core catastrophe algebra passes after an in-turn correction; no B0 or B1, one resolved B2, one open B2 documentation finding, and one B3 hardening item**

## Scope and independence

I audited the fold/cusp/multimode claims against the current manuscript, theory
notes, numerical generators, saved artifacts, tests, and Lean sources.  I did
not read a Round-04 Reviewer-B report and did not edit any scientific source,
test, artifact, or formal proof.

Severity follows `audits/README.md`: B0 blocks submission, B1 requires a
material change of derivation/evidence/framing, B2 is a bounded correction or
required caveat, and B3 is optional hardening.

The central two-channel and physical-fold results survive adversarial checking.
The determinant/weight algebra is correct; both fixed-shape GIG folds are
admissible and nondegenerate; the finite $L=31$ CTMC fold and both finite 2D
folds reproduce; their parameter sensitivities agree with independent central
differences; and the $1/2$ separation and $3/2$ prominence laws have the
correct signs and prefactors.  The manuscript also correctly refuses to infer
trimodality from either a fold or a cusp.

The audit initially found two bounded corrections.  The main thread closed the
scientific one before this report was finalized: the manuscript and continuum
note now say that the three-channel simplex equations locate only a candidate
double stationary point, state the missing third-derivative and unfolding
transversality gates, and preserve the explicit positive counterexample in a
regression test.  One documentation correction remains: the formal claim map
calls the Lean weight theorem “admissible,” although the encoded theorems do
not state or prove $0<w<1$.  The actual numerical GIG folds do pass this
condition, so neither
the resolved scientific finding nor the open formal-map finding invalidates a
reported fold.

## Findings

### F1 — B2, resolved in the current snapshot: the fixed-shape simplex equations are necessary degeneracy equations, not sufficient fold conditions

At the start of this audit, the manuscript said that a positive solution of

\[
\begin{pmatrix}
1&1&1\\
g_1'&g_2'&g_3'\\
g_1''&g_2''&g_3''
\end{pmatrix}w=
\begin{pmatrix}1\\0\\0\end{pmatrix}
\]

“locates a fixed-shape fold.”  That wording was insufficient for the reasons
below.

Let $F=f_t$.  For fixed channel shapes,

\[
F=\sum_i w_i g_i',\qquad
F_t=\sum_i w_i g_i'',\qquad
F_{tt}=\sum_i w_i g_i'''.
\]

The displayed simplex system imposes only $F=F_t=0$.  A nondegenerate fold
along a declared scalar control $s$ additionally needs

\[
F_{tt}=\sum_iw_i g_i'''\ne0,
\qquad F_s\ne0.
\]

For a physical path, $F_s$ must include both weight and shape responses; it
cannot be inferred from positivity of the weights.

The insufficiency is not merely semantic.  At one time $t_0$, choose the
local derivative jets

\[
(g_1',g_2',g_3')=(1,-1,0),\qquad
(g_1'',g_2'',g_3'')=(1,0,-1),\qquad
g_1'''=g_2'''=g_3'''=0.
\]

The simplex matrix has determinant $3$, and its unique solution is the
strictly positive $w=(1/3,1/3,1/3)$.  Thus the published system is satisfied
exactly, but $F_{tt}=0$, so the point is not a fold.  Scaling the jets by an
arbitrarily small positive number and using smooth local bump perturbations of
positive baseline densities realizes the same counterexample within smooth
normalized channel families.

The same distinction applies to the two-channel formula.  The manuscript's
wording that a fold “satisfies” the equations is correct
(`manuscript/encounter_modality_jcp.tex:639-652`), and the actual GIG validator
does separately compute the third derivative and weight transversality
(`code/validate_gig_fold.py:230-251`).  The equations alone, however, produce
only a candidate until those two nondegeneracy checks are imposed.

This matters for the cusp boundary: a cusp deliberately satisfies
$F=F_t=F_{tt}=0$, so it is a direct counterexample to calling every positive
simplex solution a fold.  The cusp equations themselves are correct:

\[
f_t=f_{tt}=f_{ttt}=0,\quad f_{tttt}\ne0,\quad
\operatorname{rank}
\begin{pmatrix}
f_{t\theta_1}&f_{t\theta_2}\\
f_{tt\theta_1}&f_{tt\theta_2}
\end{pmatrix}=2,
\]

as stated at `notes/continuum_multid_theory.md:717-743`.

**Current resolution.**  This finding is closed.  The revised manuscript now
calls Eq. (three-channel) only a candidate double stationary point and requires
both $\sum_iw_i g_i'''(t_*)\ne0$ and transverse
$f_{t\theta}(t_*)\ne0$
(`manuscript/encounter_modality_jcp.tex:694-713`).  The continuum note now gives
the same gates and the explicit invertible positive counterexample
(`notes/continuum_multid_theory.md:745-776`).  The counterexample is also an
executable regression at `tests/test_encounter_gig_fold.py:183-199`.

### F2 — B2: the Lean claim map overstates convex-weight admissibility

The formal README maps “two-channel fold elimination, admissible weight,
converse” to three theorems
(`research/reports/ring_lazy_jump_ext_rev2/code/formal_lean/README.md:55`).
The source is narrower:

- `two_channel_fold_weight` assumes only $d_1\ne d_2$ and proves the algebraic
  quotient (`FormalLean/Encounter.lean:67-74`);
- `two_channel_fold_converse` proves that the quotient zeros the two affine
  equations (`FormalLean/Encounter.lean:76-88`);
- neither theorem contains $0<w<1$, a sign condition, or a third-derivative
  hypothesis; and
- the module itself says convexity restrictions are not needed for its algebra
  (`FormalLean/Encounter.lean:33-36`).

The algebraic converse is correct.  For example,

\[
(d_1,d_2,e_1,e_2)=(2,-3,4,-6)
\]

has zero determinant, gives $w=3/5$, and zeros both mixture equations.  But
the converse does not prove physical admissibility.  With distinct slopes,

\[
0<w_*<1 \quad\Longleftrightarrow\quad d_1d_2<0.
\]

The exceptional case $d_1=d_2=0$, $e_1=1$, $e_2=-1$, $w=1/2$
also zeros both equations while $F_w=d_1-d_2=0$; it is an algebraic
degeneracy, not a weight-transverse fold.  This illustrates why denominator
nonvanishing and convex admissibility should not be conflated.

The formal scope boundary is otherwise unusually good.  The module explicitly
excludes the model-specific Taylor remainder and catastrophe/implicit-function
bridge (`FormalLean/Encounter.lean:14-19`), and the normal-form module proves
the truncated-kernel gap and prominence constants exactly
(`FormalLean/NormalForm.lean:73-124`).  No `sorry`, `admit`, or
`native_decide` occurs in the inspected formal sources; the saved
`encounter_axioms_report_20260711.txt` records only Lean's standard logical
dependencies.  No cusp theorem is encoded, which is consistent with the
declared scope.

**Required resolution.**  Change the README claim-map phrase to “algebraic
weight formula and converse,” or add a theorem proving strict convexity from
opposite nonzero channel slopes.  If the latter route is chosen, keep
third-derivative nondegeneracy and the model-specific Taylor bridge as separate
obligations.

### F3 — B3: regression-gate the normal-form prefactors, not only the exponents

The numerical evidence already passes a stronger test than the committed
regressions demand.  The 1D continuation stores both theoretical prefactors
(`code/validate_gig_fold.py:560-573`), but
`tests/test_encounter_gig_fold.py:116-123` asserts only the fitted exponents.
The 2D continuation stores the predicted half-separation but not the theoretical
prominence prefactor (`code/validate_2d_matched_fold.py:385-452`), while
`tests/test_encounter_2d_matched_fold.py:44-62` again checks only slopes and
monotonicity.

For

\[
F=f_t=a\mu+\frac b2x^2,\qquad
\delta=\sqrt{-2a\mu/b},
\]

the full predictions on the pair-bearing side are

\[
\Delta t=2\sqrt{-2a/b}\,\mu^{1/2},\qquad
\mathcal P=\frac{2|b|}{3}
\left(-\frac{2a}{b}\right)^{3/2}\mu^{3/2}.
\]

My independent smallest-step comparisons were:

| model | μ | theoretical separation coefficient | theoretical prominence coefficient | measured/predicted separation | measured/predicted prominence |
|---|---:|---:|---:|---:|---:|
| finite 1D CTMC | $10^{-3}$ | 5.5540305790 | $3.502181438\times10^{-9}$ | 1.000115 | 1.001059 |
| finite 2D $11\times7$ | $2\times10^{-4}$ | 17.0113277023 | 0.003205408694 | 0.999406 | 0.998599 |
| finite 2D $13\times9$ | $2\times10^{-4}$ | 10.0088763728 | 0.000497897976 | 0.999941 | 1.000328 |

Thus there is no detected sign or factor-of-two error.  Persisting these ratios
would nevertheless guard the exact constants more effectively than a log--log
slope alone, especially because a wrong multiplicative constant leaves both
universal exponents unchanged.

**Suggested hardening.**  Store the theoretical 2D prominence coefficient and
assert convergence of both separation and prominence ratios at the smallest
two continuation steps.  Add the analogous ratio assertion to the 1D test.

## Independent algebraic and numerical checks

### Two-channel elimination, converse, admissibility, and GIG root count

Writing $d_i=g_i'$ and $e_i=g_i''$, direct elimination from

\[
wd_1+(1-w)d_2=0,\qquad we_1+(1-w)e_2=0
\]

gives

\[
d_1e_2-d_2e_1=0,\qquad
w=-\frac{d_2}{d_1-d_2}.
\]

Conversely, the determinant and $d_1\ne d_2$ give both equations exactly.
The manuscript formulas and the Lean converse therefore pass.  The strict
simplex condition is equivalent to opposite nonzero slopes, and the remaining
fixed-shape fold gate is $wg_1'''+(1-w)g_2'''\ne0$.

For the declared early/late GIG pair, clearing the positive density factors and
$t^6$ reduces the determinant to the degree-six rational polynomial

\[
\begin{aligned}
P(t)={}&\frac{2159409375}{98}
-\frac{56552175}{98}t
-\frac{126171513}{15680}t^2
+\frac{181659}{5600}t^3\\
&-\frac{5311251}{11200000}t^4
+\frac{21303}{8000000}t^5
+\frac{45927}{4000000000}t^6.
\end{aligned}
\]

An exact-rational Sturm sequence has sign variations
$V(0^+)=3$ and $V(+\infty)=1$, hence exactly two positive roots.  They are
$28.0410937447543$ and $157.527847347136$, matching the validator.  Both
weights are interior, and both third derivatives and weight-transverse slopes
are nonzero:

| $t_*$ | $w_*$ | $f_t$ | $f_{tt}$ | $f_{ttt}$ | $f_{tw}=g_1'-g_2'$ |
|---:|---:|---:|---:|---:|---:|
| 28.0410937447543 | $3.672348776\times10^{-5}$ | 0.0 | $-9.10\times10^{-24}$ | $2.99703\times10^{-9}$ | $-2.17533\times10^{-4}$ |
| 157.527847347136 | 0.8780596892 | $4.24\times10^{-22}$ | $7.94\times10^{-23}$ | $-4.49350\times10^{-9}$ | $-1.96038\times10^{-5}$ |

This exact root count is specific to the declared rational GIG parameters.  The
generic `fixed_shape_folds` sign-change scan is not, by itself, an exhaustive
root-count algorithm for arbitrary user-supplied channels.

### Physical fold Jacobian and transversality

For the two-equation system $H=(f_t,f_{tt})$, the Jacobian at a fold is

\[
D_{(t,\theta)}H=
\begin{pmatrix}
f_{tt}&f_{t\theta}\\
f_{ttt}&f_{tt\theta}
\end{pmatrix},\qquad
\det D H=-f_{t\theta}f_{ttt}=-ab.
\]

Thus the manuscript's $a\ne0,b\ne0$ conditions are exactly the nonsingular
Jacobian condition, not merely heuristic diagnostics.  Direct recomputation
gave:

| model | $t_*$ | $\theta_*$ | $a=f_{t\theta}$ | $b=f_{ttt}$ | $-ab$ |
|---|---:|---:|---:|---:|---:|
| finite 1D $L=31$ | 37.0749586401533 | -9.67536358534634 | $-9.458486197\times10^{-10}$ | $2.452986106\times10^{-10}$ | $2.320153522\times10^{-19}$ |
| finite 2D $11\times7$ | 18.0995322971052 | 0.0138103512626833 | $2.826418446\times10^{-4}$ | $-7.813579299\times10^{-6}$ | $2.208444466\times10^{-9}$ |
| finite 2D $13\times9$ | 16.5807587454233 | 0.255892008347189 | $7.461846225\times10^{-5}$ | $-5.958893613\times10^{-6}$ | $4.446434781\times10^{-10}$ |

The 1D values reproduce
`manuscript/encounter_modality_jcp.tex:799-813` and the implementation at
`code/validate_gig_fold.py:462-534`.  The 2D values reproduce the manuscript at
`manuscript/encounter_modality_jcp.tex:979-998` and the analytic Jacobian at
`code/validate_2d_matched_fold.py:298-353`.

I also differentiated independently in the physical parameter.  At central
step $h=10^{-4}$, the relative discrepancies in $f_{t\theta}$ were
$1.85\times10^{-9}$ (1D), $3.09\times10^{-7}$ ($11\times7$), and
$2.53\times10^{-8}$ ($13\times9$).  For the 2D $f_{tt\theta}$ entries,
the discrepancies were $1.10\times10^{-7}$ and $1.97\times10^{-8}$.
These checks independently validate the augmented-state sensitivity formulas,
including the parameter derivative of the observable.

### Normal-form signs, exponents, and constants

The side condition $-2a\mu/b>0$ and the root formula in
`manuscript/encounter_modality_jcp.tex:677-692` are correct.  In the 1D example
$a<0,b>0$, so positive $\mu$ creates a maximum followed by a minimum.  In both
2D examples $a>0,b<0$, so positive $\mu$ creates a minimum followed by a
maximum.  The absolute prominence formula above handles both orientations.

The independently reproduced fitted exponents are

- 1D: $0.5009544$ and $1.5087696$;
- 2D $11\times7$: $0.4933144$ and $1.4842971$; and
- 2D $13\times9$: $0.4993246$ and $1.5038544$.

Together with the prefactor ratios in F3, these checks falsify sign,
factor-of-two, and $2^{3/2}$ versus $2^{5/2}$ mistakes.  The exact truncated
normal-form prominence constant is also proved in
`FormalLean/NormalForm.lean:82-124`; that proof does not establish the
model-specific Taylor remainder, as the formal scope correctly states.

### Cusp, three-channel simplex, and actual multimodality

For $F=f_t$, the stated cusp conditions have the correct derivative order:
$F=F_t=F_{tt}=0$, $F_{ttt}=f_{tttt}\ne0$.  The rank matrix uses
$(F_{\theta_j},F_{t\theta_j})$, exactly as required for a two-parameter versal
unfolding.  The normal form $x^3+\mu_1x+\mu_2$ has repeated roots on
$4\mu_1^3+27\mu_2^2=0$, so the sign in the note is correct.

No numerical cusp, fourth-derivative certificate, rank-two certificate, or Lean
cusp theorem exists in the audited repository.  This is not an overclaim: the
theory note explicitly calls the centre-patterned cusp a research target
(`notes/continuum_multid_theory.md:793-800`), and the manuscript withholds a
converged cusp (`manuscript/encounter_modality_jcp.tex:1427-1430`).

The logical distinction from actual trimodality is handled correctly.  The
theory note requires five alternating simple positive-time critical points,
tail control, and positive margins (`notes/continuum_multid_theory.md:778-783`).
The separate finite M2D-T family reports five alternating sign-change roots and
three channel-attributed maxima on four grids
(`manuscript/encounter_modality_jcp.tex:1106-1158`).  Even if an undetected
additional root pair existed, the five verified sign-changing roots already
establish at least three interior local maxima in each declared finite model;
they do not establish a continuum trimodal region or a cusp.  The manuscript
states that boundary accurately.

## Reproduction record

The final current-state checks were:

```text
uv run pytest -q -p no:cacheprovider \
  tests/test_encounter_gig_fold.py \
  tests/test_encounter_2d_matched_fold.py \
  tests/test_encounter_2d_trimodal_artifacts.py

................. [100%]
```

I additionally:

1. imported the two validators without invoking their artifact-writing `main`
   functions and independently reran `fixed_shape_folds`,
   `locate_physical_fold`, `physical_continuation`, `_build_family`,
   `_solve_fold`, and `_scaling_rows`;
2. compared augmented sensitivities with direct central parameter differences
   over $h=10^{-3},3\times10^{-4},10^{-4},3\times10^{-5},10^{-5}$;
3. derived the fixed-shape GIG determinant polynomial over exact rationals and
   counted its positive roots with a rational Sturm sequence;
4. evaluated exact-rational two- and three-channel counterexamples;
5. recomputed theoretical separation and prominence prefactors directly from
   $a$ and $b$, rather than trusting fitted intercepts;
6. checked the current GIG manifest source/output hashes (zero mismatches); and
7. inspected the Lean theorem statements, formal scope header, axiom report,
   and proof-placeholder scan.

A fresh full Lean rebuild was not counted as an independent pass in this review:
the local checkout lacked the prebuilt mathlib cache and began a full dependency
build.  The committed source-level audit and same-date saved axiom report pass,
but a clean cached `lake build` remains part of the submission-wide provenance
gate already stated by the manuscript.

## Passed claims

| Claim | Result |
|---|---|
| Two-channel determinant and weight elimination | Passed exactly |
| Converse under $g_1'\ne g_2'$ | Passed exactly; convexity is a separate condition |
| Exactly two positive determinant roots for the declared GIG pair | Passed by rational Sturm count |
| Both saved GIG candidates are interior and nondegenerate | Passed |
| Physical parameter changes generator and observable | Passed implementation audit |
| Fold Jacobian/transversality for the finite 1D CTMC | Passed reproduction and finite-difference check |
| Fold Jacobian/transversality for both finite 2D grids | Passed reproduction and finite-difference check |
| Pair-bearing side and max/min orientation | Passed in all three folds |
| $1/2$ separation exponent and prefactor | Passed |
| $3/2$ prominence exponent and prefactor | Passed |
| Cusp derivative order, unfolding rank, and discriminant | Passed algebraically |
| Cusp does not imply trimodality | Correctly stated |
| Three finite-grid modes require five alternating roots | Correctly stated and numerically exhibited |
| Continuum fold/cusp/trimodality boundaries | Correctly withheld |
| Three-channel simplex sufficiency caveat | Initially failed; revised text and counterexample regression now pass |
| Focused artifacts/tests/manifests | 17 tests passed; GIG manifest hashes matched |

## Not-certified boundary

This review does **not** certify:

- a physical or continuum cusp;
- numerical rank two or nonzero fourth derivative at any encounter-model cusp;
- a cell-averaged continuum trimodal region or its two bounding fold curves;
- grid convergence of the 2D fold location (the manuscript correctly reports
  the $0.242$ control shift);
- an interval-certified exhaustive root count for arbitrary channel mixtures;
- a general-$d$ multimodality theorem;
- the model-specific Taylor remainder or implicit-function reduction from the
  full encounter density to the polynomial normal forms; or
- a fresh clean-machine Lean build in this reviewer process.

## Acceptance conditions for Round 04

The scientific catastrophe-algebra finding is closed in the current snapshot.
Round 04's remaining required documentation action is:

1. correcting the Lean claim map so it does not attribute $0<w<1$ to the
   current algebraic theorems, or adding an explicit convex-admissibility
   theorem.

The remaining optional hardening is:

1. regression-gating the already successful 1D and 2D normal-form prefactor
   ratios.

No reported finite fold, exponent, prefactor, or finite-grid trimodality result
needs withdrawal on the evidence examined here.
