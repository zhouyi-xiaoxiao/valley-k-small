# Round 18 independent PDE-theory re-audit

Date: 2026-07-13  
Reviewer role: independent adversarial re-audit after Round 15  
Primary files:

- `notes/pde_mixed_jet_theorem.md`
- `audits/round_15_pde_theory_attack.md`

No theorem file was edited during this audit.

## 1. Verdict

### Mathematical verdict

**PASS for the central theorem, with two local statement/proof repairs.**

I found no sign error, missing factor of (B), wrong transpose, wrong generator,
or failed cusp determinant in the core chain

\[
 \text{free exposure}
 \xrightarrow{\;O(B)\text{ mixed jets}\;}
 \text{weak-killing Doi fold/cusp/rank}.
\]

The bounded reflected quotient semigroup, positive-time mixed jets,
first/second sensitivity equations, observable direct terms, compact-time
Dyson/Cauchy estimate, factorized cusp discriminant, contraction argument,
and Weyl transfer all survive independent re-derivation.

Two local defects should be repaired before the note is treated as final:

1. Corollary 5.5 does not currently state enough hypotheses to conclude that
   the intervening minima are *nondegenerate*.
2. The (O(B^2)) mixed-jet remainder is true, but its written proof appeals to
   a real-variable estimate rather than displaying the required complex-tube
   Dyson-tail estimate.

Neither defect invalidates Theorem 4.1 or Corollaries 5.2--5.4.

### PRR verdict

**HOLD.**  This re-audit does not change the release boundary.  The theory is
a sound conditional continuum bridge, but it does not certify (B=0.6), a
finite-grid PDE cusp, a long-time global modal count, or a physical-(d=3)
numerical transition.

## 2. Severity ledger

| Severity | Count | Meaning |
|---|---:|---|
| P0 | 0 | No fatal defect in the central theorem chain |
| P1 | 2 | Local proof/hypothesis repairs required before final citation |
| P2 | 3 | Scope/notation clarifications |

## 3. Generator, space, and boundary audit

### 3.1 Forward sign and invariant density: PASS

With

\[
 \mathbf D=\operatorname{diag}(D/2,2D,\ldots,2D),\qquad
 b=(-\gamma(z-m),-\gamma r_\parallel,0,\ldots,0),
\]

the stated density satisfies

\[
 \mathbf D\nabla\log\pi
 =(-\gamma(z-m),-\gamma r_\parallel,0,\ldots,0)=b.
\]

For (q=\pi u), direct expansion gives

\[
 \mathcal L(\pi u)=\nabla\!\cdot(\pi\mathbf D\nabla u)
 =\pi\,\pi^{-1}\nabla\!\cdot(\pi\mathbf D\nabla u).
\]

The forward no-flux condition becomes

\[
 (bq-\mathbf D\nabla q)\cdot n
 =-\pi(\mathbf D\nabla u)\cdot n=0,
\]

so the weighted Neumann form and the sign of the mass identity are correct.
The diffusion and drift coefficients also remain correct after passing from
two walkers to midpoint/relative coordinates.

### 3.2 Analytic semigroup and discontinuous potential: PASS

On the bounded product domain, (pi) is bounded above and below.  Therefore
(M_\pi) is a bounded similarity between the weighted self-adjoint Neumann
generator and the forward (L^2(dx)) generator, with

\[
 \|M_\pi\|\|M_\pi^{-1}\|
 \le \sqrt{\pi_{\max}/\pi_{\min}}.
\]

The contact indicator and fixed patches are bounded multiplication
operators.  Bounded perturbation preserves the generator domain and
analyticity.  Positivity and mass decrease are asserted only for real
(B\ge0) and nonnegative simplex weights, which is the correct scope.

The complex-time Dyson series is also valid on (operatorname{Re}z>0): every
free factor is contractive in the weighted space and the (n)-th term is
bounded by ((B|z|\|V\|_\infty)^n/n!).  This independently justifies the
complex disks used later; the argument does not require applying an adjoint
generator to the sharp indicator.

### 3.3 (q_0\in L^2) and the (t=0) boundary: PASS

Analytic-semigroup smoothing gives

\[
 T_{B,w}(t)q_0\in\bigcap_{r\ge0}D(A_{B,w}^r),\qquad t>0,
\]

even when (q_0\notin D(\mathcal L)).  The note consistently restricts cusp
jets and uniform constants to ([\tau,T]) with (\tau>0).  It does not claim a
jet or boundary compatibility at (t=0).

The unbounded corollary uses the correct stronger density space
(L^2(\pi^{-1}dx)).  Under the unweighted dual pairing, its observable norm is
indeed (|V|_{L^2(\pi dx)}).

## 4. Sensitivity and observable audit

### 4.1 First and second state sensitivities: PASS

Since

\[
 \partial_{\theta_i}A=-BM_{U_i},\qquad
 \partial_{\theta_i\theta_j}A=0,
\]

two applications of the product rule give

\[
 \partial_ts_i=As_i-BU_iq,
\]

and

\[
 \partial_ts_{ij}=As_{ij}-BU_is_j-BU_js_i.
\]

There is no missing (B), factor two, or diagonal exception when (i=j): in
that case the two displayed source terms correctly combine to
(-2BU_is_i).

### 4.2 Direct observable terms: PASS

Differentiating (f_B=B\langle V_w,q\rangle) gives exactly

\[
 \partial_i f_B
 =B(\langle U_i,q\rangle+\langle V_w,s_i\rangle),
\]

and

\[
 \partial_{ij}f_B
 =B(\langle U_i,s_j\rangle+\langle U_j,s_i\rangle
      +\langle V_w,s_{ij}\rangle).
\]

The same identities commute with every positive-time derivative.  In
particular, the note includes all (t^4) and (t^1,t^2,t^3)-by-control terms
needed by a cusp Jacobian.

A finite-dimensional independent check using a three-state symmetric Markov
generator, affine diagonal killing, and Duhamel sensitivities gave an absolute
error (1.43\times10^{-13}) between the analytic control derivative and a
centered finite difference.

## 5. Dyson/Cauchy and weak-budget audit

### 5.1 Main (B^{-1}f_B-G=O(B)) theorem: PASS

In the weighted representation,

\[
 \|T_{B,w}(z)-T_0(z)\|
 \le e^{B|z|\|V_w\|_\infty}-1.
\]

Transforming back introduces the similarity constant once, because
multiplication by (V_w) commutes with (M_\pi).  Pairing against the outer
observable then gives the stated (v_{2,\delta}\kappa_\pi) factor; no second
(kappa_\pi) is missing.

For (t\in[\tau,T]), the disk (|z-t|\le\tau/2) satisfies
(operatorname{Re}z\ge\tau/2) and (|z|\le3T/2).  Time and control Cauchy
estimates therefore give precisely

\[
 r!\alpha!(2/\tau)^r\delta^{-|\alpha|}
 v_{2,\delta}\kappa_\pi
 [e^{(3/2)Bv_{\infty,\delta}T}-1]\|q_0\|_2.
\]

The conversion to (BC_{r,\alpha}) uses the valid inequality
(e^{Bx}-1\le Bxe^{B_0x}).  A three-state numerical stress check produced
(|F_B-G|/B=0.3211,0.3245,0.3262,0.3271,0.3276) for
(B=0.08,0.04,0.02,0.01,0.005), consistent with the stated first-order
limit.

### 5.2 First correction: sign and order PASS

The first Duhamel term is

\[
 -B\int_0^t
 \langle V_w,T_0(t-s)M_{V_w}T_0(s)q_0\rangle\,ds,
\]

so the minus sign in (4.13) is correct.  The remaining Dyson tail starts at
(n=2) and is (O(B^2)).

### P1.1: the mixed-jet (O(B^2)) proof must display a complex-tail bound

Lines 490--512 state (4.14) only for real (t,w).  Lines 515--517 then say
that applying Cauchy to (4.14) yields every mixed-jet (O(B^2)) estimate.
Cauchy's theorem cannot be applied to a bound stated only on the real set.

The conclusion is nevertheless correct and locally repairable.  Define the
complex remainder by the (n\ge2) Dyson tail and state, on the same complex
time disk and control tube,

\[
 |\mathcal R_{2,B}(z,\zeta)|
 \le v_{2,\delta}\kappa_\pi
 \left[e^{Bv_{\infty,\delta}|z|}
 -1-Bv_{\infty,\delta}|z|\right]\|q_0\|_2.
\]

Multivariable Cauchy then gives the claimed (O(B^2)) mixed-jet remainder.
This repair does not alter Theorem 4.1.

## 6. Factorized cusp audit

### 6.1 Factorization and derivative order: PASS

Under the stated tensor generator and product initial law,

\[
 g_j(t)=a_j(t)c_d(t)
\]

and the fourth-order Leibniz formula is correct.  The common relative factor
contains all relative coordinates in both physical (d=2) and (d=3).

### 6.2 Null vector, (Delta'), and tangent rank: PASS

At a rank-two zero of

\[
 \mathscr D=(g'^T;g''^T;g'''^T),
\]

(mathscr Dw_*=0) is exactly
(G_t=G_{tt}=G_{ttt}=0).  Positivity and
(mathbf1^Tw_*=1) place the candidate strictly inside the budget simplex.

Differentiating (Delta=\det(g'^T;g''^T;g'''^T)) leaves only

\[
 \Delta'=\det(g'^T;g''^T;g''''^T),
\]

because the other two determinants have repeated rows.  Right multiplication
by ([P,w_*]) gives

\[
 (g''''{}^Tw_*)\det(g'^TP;g''^TP)
 =\det[P,w_*]\Delta'.
\]

The sign and orientation in (4.23) are correct.  An independent random
algebraic check satisfied this identity to (2.22\times10^{-15}).

The cusp Jacobian uses exactly one additional time derivative and the two
projected control rows.  No (g'''{}^TP) rank condition is missing.

## 7. Quantitative persistence and Weyl audit

### 7.1 Contraction lemma: PASS

Conditions (5.2)--(5.3) imply

\[
 \|I-A_0^{-1}DH\|\le\frac12.
\]

Furthermore,

\[
 \|x-A_0^{-1}H(x)-x_0\|
 \le r/2+\varepsilon_0/\mu\le r,
\]

so the Newton-like map is a contraction from the closed ball into itself.
The displacement (2\varepsilon_0/\mu) and singular-value floor
(mu/2) follow.  The fold and cusp maps request exactly the mixed derivatives
provided by Theorem 4.1.

### 7.2 Weyl scaling: PASS

The rank estimate is correctly stated for the normalized density (F_B).
For the physical density (f_B=BF_B), the raw projected response is (BR_B),
so its absolute singular values vanish linearly while its normalized
conditioning may remain finite.  Round 15 correctly refuses to conflate
those statements.

### P1.2: Corollary 5.5 overstates nondegenerate minima

Lines 817--823 assume endpoint derivative margins, negative curvature on peak
intervals, and separator sign margins.  Those hypotheses robustly produce
nondegenerate maxima.  Opposite derivative signs between peaks guarantee at
least one intervening local minimum, but they do **not** exclude a degenerate
minimum such as a higher-order flat crossing.

Two safe repairs are available:

1. add disjoint valley intervals with positive-curvature margins and endpoint
   derivative signs; or
2. retain the existing assumptions but replace “nondegenerate Doi maxima and
   intervening minima” by “nondegenerate Doi maxima and at least one
   intervening local minimum.”

This does not affect fold/cusp persistence, which already has an invertible
Jacobian hypothesis.

## 8. Dimension and scope audit

### 8.1 Physical (d=2) and (d=3): PASS for the exact slab quotient

The proof only uses a bounded product domain, positive diagonal diffusion,
reversible OU drift, periodic transverse relative coordinates, and bounded
fixed killing.  Adding one relative torus coordinate changes the contact disk
to a sphere but not the functional-analytic proof.  The note correctly says
that transversely localized patches break this exact quotient and require the
fuller configuration space.

### 8.2 Long time, finite budget, and discretization: scope correctly closed

The note explicitly excludes:

- a conclusion at (B=0.6);
- a uniform (t=O(B^{-1})) or full-density limit;
- a global modal count without a tail theorem;
- a GIG approximation;
- a Scharfetter--Gummel/FEM (C^1) cusp estimator; and
- a completed physical-(d=3) computation.

These exclusions are essential and are consistently preserved in Round 15.

## 9. P2 clarifications

1. **Simplex-interior ball.**  Corollaries 5.2--5.3 should say explicitly that
   the persistence ball is chosen inside the real simplex chart.  Strict
   positivity of (w_*) makes this possible, so it is not an added
   mathematical assumption.
2. **Rank dimension.**  Corollary 5.4 should state (J\ge3), or more generally
   that the tangent dimension is at least two, before using (sigma_2) of a
   two-row projected matrix.
3. **Componentwise-to-operator constants.**  When an actual (B_*) is
   computed, the scalar Cauchy bounds must be assembled into vector and
   Jacobian operator norms with the appropriate finite-dimensional factors.
   The present qualitative (O(B)) transfer remains valid, but a numerical
   certificate cannot insert scalar constants directly as
   (\varepsilon_0,\varepsilon_1).

## 10. Final gate decision

| Claim | Re-audit result |
|---|---|
| Reflected OU/free generator and no-flux sign | **PASS** |
| Analytic semigroup for (q_0\in L^2), (t\ge\tau>0) | **PASS** |
| Bounded indicator perturbation | **PASS** |
| First/second sensitivity PDEs | **PASS** |
| Direct observable derivatives | **PASS** |
| Main compact-time (F_B-G=O(B)) mixed-jet theorem | **PASS** |
| First correction and scalar (O(B^2)) remainder | **PASS** |
| Mixed-jet (O(B^2)) written proof | **LOCAL REPAIR** |
| Factorized cusp determinant and (Delta') identity | **PASS** |
| Quantitative fold/cusp persistence | **PASS** |
| Weyl projected-rank transfer | **PASS** |
| Nondegenerate intervening minima under Cor. 5.5 as written | **LOCAL REPAIR** |
| Physical (d=2/3) exact-slab applicability | **PASS** |
| PRR release | **HOLD** |

The defensible high-level conclusion is therefore unchanged: the PDE note
contains a real, rigorous weak-budget continuum theorem, but the repository
still needs finite-(B) continuation, continuum numerical error control, and
the 3D transition before the new manuscript can make a PRR-level physical
claim.
