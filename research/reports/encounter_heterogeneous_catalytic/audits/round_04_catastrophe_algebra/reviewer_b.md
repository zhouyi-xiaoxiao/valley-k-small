# Round 04 reviewer B — catastrophe algebra, transversality, and modality logic

Date: 2026-07-11  
Verdict: **pass; no open B0, B1, B2, or B3 findings**  
Audited Git base: `3531353a515160b09899199a9257e7455a654b22`  

Working-tree snapshot hashes:

- `manuscript/encounter_modality_jcp.tex`:
  `bc451a4b8e0a572fb8b1a37f333e79f12e5b2d8078b0439f83c600522906d357`;
- `notes/continuum_multid_theory.md`:
  `ce677ab77ba9ae5cec11c3589eb7418612af26ab075b7f33d506a667104a51db`;
- `code/validate_gig_fold.py`:
  `3fcb7240c2f113589017d8bd2251c5d1dd8889980ce562bba75da2dc68084292`;
- `code/validate_2d_matched_fold.py`:
  `21beed4e592517bb956f8924e8fcb3a483bc3debc234c1b5882b90a3ab1b654d`;
- `code/validate_2d_trimodal.py`:
  `42141c66d36d17158dc6aa45916f72434a69e7d927c6466c8072212d5ce194ff`;
- `tests/test_encounter_gig_fold.py`:
  `365126eb570d4a4440d2ea3d1746b59f1be95908a9c0b34f19a6a1191ea4bd5b`;
- `tests/test_encounter_2d_matched_fold.py`:
  `f742fcfc6a7feff3c49054bfb48f2c066d326205a5a23766a6352b8b0b142837`;
- `artifacts/data/gig_fold_summary.json`:
  `5802066c97a757cf651b809f166674a643046f6f5669f2677ed1e5d054e7ed1c`;
- `artifacts/data/finite_radius_2d_fold_metrics.json`:
  `957dc15df054b79be7cd81e7bc835775451c1f2eeb46b56f6151a0d8bfe70a93`;
- `artifacts/data/finite_radius_2d_trimodal_metrics.json`:
  `5e2fba97796b1beeb6ab37d64cc9fe0b698d31f91e9340193d9d8740e68cf8b0`;
- `tests/test_encounter_2d_trimodal_artifacts.py`:
  `d33b8b69712bc553b9207921844b789fe9f3ed95cc86e6493b87462d0bd240ef`;
- `FormalLean/Encounter.lean`:
  `d2c11759c831228eb6641f3944d1d860c34615982d15b883e6d029f0a670e754`;
- formal-package `README.md`:
  `c89e6ecccceadf2a95c3c1e787890ff6a884eb7636230da26c524ad4b129ec61`.

The Git hash is a base commit rather than a complete immutable snapshot because
the report is untracked in an already dirty working tree. I did not read or rely
on Reviewer A's Round 04 report. I changed no manuscript, theory note, code,
test, artifact, notebook, manifest, or Lean source; this report is my only
write.

## Executive assessment

The fold/cusp algebra is internally consistent and the claim boundaries are
appropriate. The two-channel determinant and weight formula include the needed
distinct-slope and convex-weight restrictions. A positive three-channel
simplex solve is correctly presented only as a candidate double stationary
point; the new invertible positive counterexample demonstrates that it does not
imply either third-derivative nondegeneracy or parameter transversality. The
cusp is formulated at the correct derivative order for `F=f_t`, and its
two-control rank condition is the correct versality condition.

Both physical fold calculations differentiate the state, killed generator, and
killing observable. Independent centered differences reproduce the 1D and 2D
parameter derivatives, while direct determinants reproduce the reported fold
Jacobians. The local normal form has the correct sign convention, factor
`1/2`, square-root separation coefficient, and `3/2` prominence coefficient.
The newly added ratio gates test the coefficients, not merely fitted slopes,
and pass at the smallest held-out offsets.

The trimodality logic is also kept separate from catastrophe terminology. A
cusp can create only one critical-point pair; it does not by itself establish
three modes. The paper requires five alternating simple critical points,
positive prominence, channel attribution, and tail control, and describes the
M2D-T result as a four-grid finite-state mechanism certificate rather than a
continuum cusp or phase boundary.

The Lean statements faithfully certify only the exact algebraic kernel. They do
not encode convex admissibility, a Taylor-remainder theorem, a physical-model
fold, numerical roots, or trimodality, and the README now says so explicitly.

## Severity inventory

| Severity | Open findings | Assessment |
|---|---:|---|
| B0 | 0 | No incorrect headline conclusion or invalid catastrophe algebra found. |
| B1 | 0 | No error affecting the fold, cusp, or trimodality mechanism claim found. |
| B2 | 0 | No missing validation gate or materially overbroad claim remains in this scope. |
| B3 | 0 | No open notation, provenance, or claim-map defect remains. |

One audit-time hygiene issue was corrected before this snapshot was frozen: the
2D fold JSON field that contains the actual mixed derivative
`f_{tt theta}` was renamed from the ambiguous `f_tttheta` to `f_tt_theta`.
The underlying expression and Jacobian were already correct. The regenerated
artifact uses the unambiguous key, and the regression test rejects the old key.
This is therefore recorded as a resolved observation, not an open finding.

Two late audit-time text issues were likewise closed before the snapshot was
frozen. The trimodality gate now distinguishes existence of at least three
resolved modes from an exact global root/mode count: only the latter is said to
require interval-exhaustive isolation. This removes a transient contradiction
with the explicitly non-exhaustive M2D-T certificate. The inline mathematical
delimiters in the accompanying multi-channel screening paragraph were also
restored. Neither remains open.

## 1. Two-channel elimination and the weight feasibility domain

**Anchors**

- `manuscript/encounter_modality_jcp.tex:639-663`;
- `notes/continuum_multid_theory.md:622-669`;
- `code/validate_gig_fold.py:230-278`;
- `FormalLean/Encounter.lean:29-89`;
- `tests/test_encounter_gig_fold.py:110-126`.

Writing `d_i=g_i'(t)` and `q_i=g_i''(t)`, the two fold equations are

\[
w d_1+(1-w)d_2=0,\qquad wq_1+(1-w)q_2=0.
\]

Eliminating `w` gives `d_1q_2-d_2q_1=0`. If `d_1 != d_2`, the first equation
has the unique solution

\[
w=-\frac{d_2}{d_1-d_2}=\frac{d_2}{d_2-d_1}.
\]

For real slopes, strict convex feasibility `0<w<1` is equivalent to
`d_1 d_2<0`; the manuscript's direct range check is therefore complete. The
determinant alone is insufficient in the degenerate case `d_1=d_2=0`, and both
the text and Lean converse keep the distinct-slope assumption. The Lean forward
determinant theorem legitimately includes endpoint weights, but the claim map
does not confuse that algebraic extension with physical convex admissibility.

Substituting `g_i'=g_i a_i` and `g_i''=g_i(a_i^2+b_i)` cancels the positive
factor `g_1g_2` and gives exactly the displayed GIG equation
`a_1(a_2^2+b_2)-a_2(a_1^2+b_1)=0`.

## 2. Three-channel simplex necessity and its logical limit

**Anchors**

- `manuscript/encounter_modality_jcp.tex:694-716`;
- `notes/continuum_multid_theory.md:745-783`;
- `tests/test_encounter_gig_fold.py:210-226`.

For a fixed-shape convex mixture, normalization plus `f_t=f_tt=0` necessarily
gives the displayed `3 x 3` simplex system. It does not imply that the matrix is
invertible, that the solution is positive, or that the stationary point is a
generic fold; those are separate questions.

The explicit jet counterexample is valid. For

\[
M=\begin{pmatrix}1&1&1\\1&-1&0\\1&0&-1\end{pmatrix},
\qquad w=(1/3,1/3,1/3)^T,
\]

`det M=3`, all weights are strictly positive, and `Mw=(1,0,0)^T`. Choosing
all three third-derivative jets equal to zero gives
`f_{ttt}=sum_i w_i g_i'''=0`. Thus positivity and invertibility of the
simplex solve do not supply fold nondegeneracy. A declared one-parameter
direction must additionally satisfy `f_{t theta} != 0`. The paper now states
both gates before making any fold claim.

## 3. Cusp derivative order, rank, and discriminant

**Anchors**

- `notes/continuum_multid_theory.md:717-743,776-783`;
- `manuscript/encounter_modality_jcp.tex:705-716`.

The singular equation is `F=f_t=0`. A codimension-two cusp therefore requires

\[
F=F_t=F_{tt}=0,\qquad F_{ttt}\ne0,
\]

which is precisely
`f_t=f_tt=f_ttt=0` with `f_tttt != 0`. The unfolding matrix is the derivative
of `(F,F_t)` with respect to the two controls, hence

\[
\begin{pmatrix}
f_{t\theta_1}&f_{t\theta_2}\\
f_{tt\theta_1}&f_{tt\theta_2}
\end{pmatrix},
\]

and rank two is the correct transversality condition. For
`F=x^3+mu_1 x+mu_2`, a repeated root obeys
`mu_1=-3x^2`, `mu_2=2x^3`; eliminating `x` gives
`4 mu_1^3+27 mu_2^2=0`. Derivative orders, rank, and discriminant are all
consistent.

The manuscript does not claim to have located such a cusp. It uses the cusp
calculus to define the next two-control analytical target and keeps the current
three-patch evidence at finite-grid certificate level.

## 4. Physical fold sensitivities and Jacobians

### 4.1 One-dimensional finite CTMC

**Anchors**

- `manuscript/encounter_modality_jcp.tex:787-818`;
- `notes/gig_fold_derivation.md:151-193`;
- `code/validate_gig_fold.py:502-559`.

For column state `p'=T^T p` and sensitivity
`s'=T^T s+T_theta^T p`, differentiating `f_t=p^T T b` gives

\[
f_{t\theta}=s^TTb+p^TT_\theta b+p^TTb_\theta.
\]

All three terms appear in the implementation. At the archived fold, centered
differences of `f_t(t_*,theta)` with parameter steps
`1e-3, 3e-4, 1e-4` have relative errors
`1.67e-7, 1.48e-8, 1.85e-9` against the augmented-exponential value
`-9.4584861967e-10`. This independently confirms both the sign and inclusion
of the observable derivative.

### 4.2 Matched-budget 2D finite grids

**Anchors**

- `manuscript/encounter_modality_jcp.tex:1005-1041`;
- `notes/finite_radius_2d_matched_fold.md:55-101`;
- `code/validate_2d_matched_fold.py:238-353`;
- `tests/test_encounter_2d_matched_fold.py:26-73`.

With `A(theta)=A_0+theta A_theta` and
`k(theta)=k_0+theta k_theta`, the code uses

\[
f_t=x^TAk,
\quad f_{t\theta}=x_\theta^TAk+x^T(A_\theta k+Ak_\theta),
\]

and

\[
f_{tt\theta}=x_\theta^TA^2k+x^T
\{A_\theta Ak+A(A_\theta k)+A^2k_\theta\}.
\]

Consequently the root Jacobian is

\[
J=\begin{pmatrix}f_{tt}&f_{t\theta}\\
f_{ttt}&f_{tt\theta}\end{pmatrix},
\qquad \det J=-f_{t\theta}f_{ttt}
\]

at a fold. Direct `numpy.linalg.det` evaluation reproduced
`2.208444465961e-9` on `11x7` and `4.446434780797e-10` on `13x9`.
Independent centered differences at `h_theta=3e-5` reproduced
`f_{t theta}` and `f_{tt theta}` with relative errors respectively
`2.77e-8, 9.91e-9` on `11x7` and `1.93e-9, 6.82e-9` on `13x9`.
Centered time differences also reproduced `f_ttt` to `5.3e-9` and `1.1e-8`
relative error at `h_t=3e-4`.

The two fold coordinates are explicitly declared not grid-converged. Their
different `theta_c` values therefore do not undermine the promoted result,
which is a finite-grid local mechanism certificate rather than a continuum
critical parameter.

## 5. Normal-form signs, exponents, and prefactors

**Anchors**

- `manuscript/encounter_modality_jcp.tex:671-692,1540-1569`;
- `code/validate_gig_fold.py:585-675`;
- `code/validate_2d_matched_fold.py:385-470`;
- `tests/test_encounter_gig_fold.py:129-150`;
- `tests/test_encounter_2d_matched_fold.py:46-73`.

For

\[
F=f_t=a\mu+\frac b2x^2+o(|\mu|+x^2),
\]

the two-root side is `-2a mu/b>0`, and

\[
x_\pm=\pm\sqrt{-2a\mu/b},\qquad
S=2\sqrt{|-2a/b|}\,|\mu|^{1/2}.
\]

Let `c=sqrt(-2a mu/b)`. Since `a mu=-bc^2/2`,

\[
\left|\int_{-c}^{c}\left(a\mu+\frac b2x^2\right)dx\right|
=\frac{2|b|}{3}c^3
=\frac{2|b|}{3}|-2a/b|^{3/2}|\mu|^{3/2}.
\]

Thus the factor `1/2`, the separation exponent `1/2`, the prominence exponent
`3/2`, and both prefactors in code and manuscript agree.

Independent reconstruction from the archived derivatives gave:

| certificate | separation coefficient | prominence coefficient |
|---|---:|---:|
| 1D physical CTMC | `5.5540305790` | `3.5021814378e-9` |
| 2D `11x7` | `17.0113277023` | `3.2054086938e-3` |
| 2D `13x9` | `10.0088763728` | `4.9789797585e-4` |

These values reproduce the stored coefficients to displayed precision. At the
two smallest held-out offsets, actual/predicted `(separation,prominence)` ratios
are `(1.000115,1.001059)` and `(1.000230,1.002119)` in 1D;
`(0.999406,0.998599)` and `(0.998517,0.996505)` on `11x7`; and
`(0.999941,1.000328)` and `(0.999853,1.000820)` on `13x9`. The regression
gates therefore validate the leading coefficients in addition to the log-log
slopes.

## 6. Trimodality logic and claim boundary

**Anchors**

- `manuscript/encounter_modality_jcp.tex:705-716,1156-1213`;
- `notes/continuum_multid_theory.md:778-800`;
- `notes/finite_radius_2d_trimodality.md:1-105`;
- `code/validate_2d_trimodal.py:188-334`;
- `tests/test_encounter_2d_trimodal_artifacts.py:17-65`.

A fold or cusp changes the critical-point count by two. Starting from a remote
mode does not automatically supply the additional minimum/maximum structure
needed for three modes. The paper correctly requires five alternating simple
positive-time critical points, positive peak/valley margins, and tail control.

The M2D-T calculation evaluates exact finite-matrix derivative actions,
brackets all detected sign changes to `t=2000`, refines them with fresh
matrix-exponential evaluations, checks nonzero curvature and max/min ordering,
audits the off-root logarithmic slope for missed tangencies, and requires a
strictly decreasing post-peak tail. Across four grids the recorded order is
`max-min-max-min-max`; the maximum root residual is `1.87e-15`, the minimum
root curvature is above `6.6e-6`, the minimum off-root absolute log slope is
above `0.0119`, and survival at `t=2000` is below `4.22e-11`. The three maxima
are independently attributed to near, middle, and far nonnegative Doi fluxes.

This remains a floating-point finite-grid root audit, not interval arithmetic
on `(0,infinity)`. The manuscript's wording is calibrated accordingly: it says
"five detected simple roots" and explicitly withholds a cell-averaged
continuum theorem and trimodality phase boundary. The regenerated JSON makes
the same boundary machine-readable with
`exhaustive_positive_time_root_count_claimed=false`. No cusp is inferred from
the three-channel simplex or from the finite-grid example.

## 7. Lean claim fidelity

**Anchors**

- `FormalLean/Encounter.lean:29-163`;
- formal-package `README.md:55,73-80,87-99`;
- `manuscript/encounter_modality_jcp.tex:1613-1624`.

The exact theorem count is `100`; the three `Encounter*.lean` modules contain
`54` of those declarations. No `sorry`, `admit`, or `native_decide` occurs in
the formal source. The encounter axiom reports list only `propext`,
`Classical.choice`, and `Quot.sound`.

`two_channel_fold_determinant`, `two_channel_fold_weight`, and
`two_channel_fold_converse` match the algebra and keep the distinct-slope
condition where it is required. The README explicitly leaves strict convex
admissibility and model-specific nondegeneracy outside those theorems.

The Lean fold kernel is `B x^2-A delta` with positive `A,B,delta`. After
orienting the physical two-root side, the manuscript normal form maps to it by
`A=|a|` and `B=|b|/2` up to multiplication of the zero equation by `-1`.
The proved roots and gap therefore have exactly the manuscript coefficient.
The package certifies only the exact truncated polynomial algebra. It does not
prove Taylor remainder control, the physical fold's existence, or persistence
of roots in the full density; both README and manuscript state those exclusions.

The Lean package does not formalize the cusp classification or the M2D-T root
audit, and the manuscript does not say that it does. Its compact phrase
"quadratic normal form" is supported by the claim map and the explicit scope
paragraph that follows it.

## Independent commands and results

From the repository root:

```bash
uv run pytest -q \
  tests/test_encounter_gig_fold.py \
  tests/test_encounter_2d_matched_fold.py \
  tests/test_encounter_2d_matched_fold_artifacts.py \
  tests/test_encounter_2d_trimodal_artifacts.py
```

Result: **19 passed**.

The sensitivity audit imported the two validation modules directly, recomputed
each fold, and compared analytic columns with centered differences:

```bash
uv run python - <<'PY'
# For each fold, evaluate q(theta+h), q(theta-h) with sensitivity=False.
# Compare (f_t+ - f_t-)/(2h) to f_ttheta and
#         (f_tt+ - f_tt-)/(2h) to f_tt_theta.
# Also compare numpy.linalg.det(J) with the archived determinant.
PY
```

The numerical errors and determinants are reported in Sec. 4 above. The
prefactor audit independently reconstructed the coefficients from only `a` and
`b`, then divided each held-out observable by its normal-form prediction; the
ratios are reported in Sec. 5.

The publication helper copied the formal package byte-for-byte to the isolated
local workspace
`/Users/ae23069/.local-build/valley-k-small/encounter_formal_pipeline` and
linked its dependency directory to the repository's shared local Mathlib
cache. From that workspace:

```bash
lake --no-ansi --verbose build
rg -n '^theorem ' FormalLean/*.lean | wc -l
rg -n '^theorem ' FormalLean/Encounter*.lean | wc -l
rg -n '\bsorry\b|\badmit\b|native_decide' FormalLean/ || true
```

An independent serial audit then repeated the build and ran the live drivers
from `/Users/ae23069/.local-build/valley-k-small/formal_lean`:

```bash
lake --no-ansi build
lake env lean EncounterAxioms.lean
lake env lean EncounterContinuumAxioms.lean
lake env lean EncounterDesignAxioms.lean
```

Result: the warm build exited zero with
`Build completed successfully (3109 jobs)`; `FormalLean` built at job
`3108/3109`, and the default target completed at `3109/3109`. An earlier
cache-repair pass reached the `FormalLean` target but was not counted as a pass
because 12 Mathlib dependency targets logged failures. The same source and
toolchain then completed cleanly after those cached outputs settled. Static
counts are `100` total theorem declarations and `54` in the three
`Encounter*.lean` modules, with no forbidden proof-bypass token. The three
encounter axiom reports have respectively `14`, `28`, and `12` theorem rows;
all `54` list only `[propext, Classical.choice, Quot.sound]`. An independent
serial repetition also exited zero at `3109/3109`; its live encounter axiom
drivers returned `14/28/12` rows, parser error lists `[]`, and exact semantic
matches to the three saved reports.

## Final recommendation

Accept Round 04 on the audited snapshot. The catastrophe-theory language is
now correctly conditional on nondegeneracy and transversality, coefficient
tests go beyond exponent fitting, trimodality is not inferred from a cusp or a
simplex solve, and the formal verification claims stay within the theorems
actually encoded. No further scientific change is required by this review.
