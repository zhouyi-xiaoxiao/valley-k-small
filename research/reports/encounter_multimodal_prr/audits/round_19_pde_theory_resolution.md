# Round 19 PDE-theory resolution re-audit

Date: 2026-07-13  
Role: independent resolution audit of the Round 18 findings  
The theorem file was read but not edited.

## 1. Frozen input

- `notes/pde_mixed_jet_theorem.md`
- SHA256:
  `3fc37bafc6320556322e80daa2c56bad9fd4b19e1856100caa8adf92341a8007`
- Prior findings:
  `audits/round_18_pde_theory_reaudit.md`

The input hash matches the requested repaired version.

## 2. Final verdict

**RESOLUTION PASS.**  All two P1 and three P2 findings from Round 18 are
closed.  The repairs do not change or weaken the central analytic-semigroup,
mixed-jet, weak-budget, cusp, or Weyl results.

Severity after resolution:

| Severity | Open count |
|---|---:|
| P0 | 0 |
| P1 | 0 |
| P2 | 0 |

The theory is suitable for integration into the manuscript as a rigorous
conditional continuum theorem.  This is not a release decision for the full
paper: finite-budget continuation, a grid-to-PDE error certificate, and the
physical 3D numerical transition remain open exactly as stated in the note.

## 3. Round 18 resolution matrix

| Round 18 item | Repair inspected | Resolution |
|---|---|---|
| P1.1: real-only remainder bound was insufficient for mixed-jet Cauchy | Equations (4.15)--(4.17) now define the analytic `n >= 2` Dyson tail on the complex time/control neighborhood, bound it there, and then apply multivariable Cauchy | **CLOSED** |
| P1.2: intervening minima were not proved nondegenerate | Corollary 5.5 now freezes separate peak and valley intervals, derivative endpoint margins, negative peak curvature, and positive valley curvature | **CLOSED** |
| P2.1: persistence ball not explicitly inside the simplex | Corollaries 5.2--5.3 require the closed ball to lie in `(tau,T) x Theta-interior` and impose a positive minimum weight | **CLOSED** |
| P2.2: second singular value required tangent dimension at least two | Corollary 5.4 now explicitly assumes `J >= 3` | **CLOSED** |
| P2.3: scalar Cauchy constants were not assembled into vector/operator norms | A new assembly paragraph supplies Euclidean and Frobenius/operator bounds, and Corollary 5.4 gives the explicit `sqrt(2(J-1))` factor | **CLOSED** |

## 4. Detailed repair checks

### 4.1 Complex Dyson-tail repair

The new remainder is exactly the `n >= 2` part of the Dyson expansion of the
normalized density `F_B = <V_w,T_B q_0>`.  Therefore it is analytic jointly
in complex time with positive real part and in the complexified affine
control coordinates.

The stated estimate is the termwise bound

```text
|R_2(z,zeta)|
 <= v_2 kappa [exp(B v_infinity |z|) - 1 - B v_infinity |z|] ||q_0||_2.
```

The outer observable contributes `v_2`; the internal `n` multiplication
operators contribute `v_infinity^n`; and the reversible similarity contributes
`kappa` once.  There is no missing similarity factor or power of `B`.

On the Cauchy disk, `|z| <= 3T/2`.  The resulting equation (4.17) has the
correct factors

```text
r! alpha! (2/tau)^r delta^(-|alpha|)
```

and the final quadratic bound follows from
`exp(x)-1-x <= x^2 exp(x)/2`.  The repair therefore proves the advertised
uniform `O(B^2)` result through every fixed mixed jet; it no longer relies on
a real-axis estimate.

### 4.2 Peak/valley repair

For every peak interval, the repaired assumptions give a positive derivative
at the left endpoint, a negative derivative at the right endpoint, and
strictly negative second derivative throughout after perturbation.  Hence the
derivative is strictly decreasing, has exactly one zero, and that zero is a
nondegenerate maximum.

The valley argument is the sign-reversed analogue: strictly positive second
derivative makes the derivative strictly increasing between its negative and
positive endpoint values.  It yields exactly one nondegenerate minimum.

The strict error inequalities against all four frozen margins correctly
transfer these conclusions from `G` to `F_B`, and multiplication by positive
`B` leaves their locations and types unchanged for `f_B`.

### 4.3 Interior persistence repair

The fold and cusp corollaries now choose their closed contraction balls inside
the positive-time, simplex-interior chart and explicitly require
`inf min_j w_j > 0`.  The contraction fixed point therefore cannot leave the
physical budget simplex.  This closes the prior domain ambiguity without
changing Lemma 5.1.

### 4.4 Norm-assembly and rank repair

The new bounds use

```text
||vector error||_2 <= sqrt(sum component_error^2)
||matrix error||_2 <= ||matrix error||_F
```

which are the correct finite-dimensional conversions.  For the two-row rank
matrix, an entrywise bound `E_R` gives
`epsilon_R <= sqrt(2(J-1)) E_R`.  With `J >= 3`, the second singular value is
well-defined and Weyl's inequality applies exactly as written.

## 5. Regression audit of the central theorem

The repairs leave the following chain intact:

1. The forward reflected OU/free operator remains similar to the nonpositive
   self-adjoint weighted Neumann generator.
2. The sharp contact indicator remains a bounded multiplication perturbation.
3. For `q_0 in L2`, all required time/control jets remain restricted to
   positive times `t >= tau > 0`.
4. The first and second sensitivity PDEs retain the correct `-B U_i` source
   terms and all direct observable derivatives.
5. The main equation (4.5) still proves `F_B-G = O(B)` through every fixed
   compact-time mixed jet.
6. The factorized cusp equations remain unchanged except for consistent
   renumbering.  The null-vector, fourth-time derivative, tangent-rank, and
   determinant identities are intact.
7. Lemma 5.1 and the fold/cusp contraction argument are unchanged; the new
   norm assembly only makes their numerical use explicit.
8. The raw response matrix for `f_B` is still `B R_B`, so the note preserves
   the distinction between normalized conditioning and vanishing absolute
   response.

No new claim at `B=0.6`, on the `t = O(B^-1)` tail, for a GIG approximation,
for SG/FEM continuum convergence, or for a completed physical-3D calculation
was introduced.

## 6. Formula and text integrity

Checks performed on the repaired file:

- all display equation tags are unique and sequential:
  `(1.1)--(1.6)`, `(2.1)--(2.8)`, `(3.1)--(3.11)`,
  `(4.1)--(4.26)`, `(5.1)--(5.13)`, `(6.1)`, and `(7.1)`;
- every in-text numbered equation reference resolves to an existing tag;
- display-math delimiters are balanced;
- no ASCII control character is present;
- section and theorem headings remain ordered; and
- the repaired factorization proof points to the new equation numbers
  `(4.22)--(4.26)` consistently.

The long operator formula in (4.15) is unambiguous: inside the weighted
representation, each `V_w` denotes its multiplication operator, consistently
with the notation used in (4.8).

## 7. Manuscript integration decision

**YES: integrate the theorem into the manuscript.**  The manuscript may use
the following bounded claim:

> On every fixed positive-time window, the exact quotient Doi encounter-time
> density divided by the reaction budget converges to the exact free-exposure
> mixture through the full finite fold/cusp mixed jet at rate `O(B)`.  A
> quantitatively nondegenerate free-exposure mode, fold, cusp, or projected
> rank margin therefore persists for all sufficiently small positive budgets.

The manuscript must retain the accompanying exclusions:

- no present certification that `B=0.6` is below the persistence threshold;
- no global-in-time density or modal-count conclusion;
- no finite-grid-to-continuum cusp certificate;
- no automatic GIG bridge; and
- no completed physical-3D transition.

With those boundaries, the repaired PDE theory is internally consistent and
ready for manuscript integration.
