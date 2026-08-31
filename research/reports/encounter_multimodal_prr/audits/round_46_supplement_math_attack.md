# Round 46: independent mathematical attack on the analytical supplement

Date: 2026-07-14  
Target: `manuscript/encounter_multimodal_prr_supplement.tex`  
Mode: equation-by-equation adversarial reconstruction; Round 41 was treated as
an untrusted claim, not as evidence  
Mutation boundary: read-only on the Supplement, main manuscript, theorem notes,
model source, and frozen positive-budget chain.  This audit is the only added
file.

## Verdict

**The two central scoped theorems remain mathematically credible, but the Round
41 claim of a completely self-contained zero-gap Supplement is too strong.**
I found no counterexample to the fixed-finite-mode theorem and no wrong sign,
factor, OU variance, Gaussian threshold, or reversed \(\epsilon\)-then-\(B\)
limit.  I did find two genuine statement/assembly gaps that should be repaired
before this file is treated as submission mathematics:

1. the general state and mixed-jet sections never declare the bounded-domain
   hypothesis on \(q_0\), nor the positivity/unit-mass hypotheses needed for the
   survival-density interpretation; and
2. the fold/cusp contraction paragraph applies a matrix inverse to a map that is
   not square when the previously defined control vector has more coordinates
   than the selected unfolding.  Its subsequent full-row-rank condition also
   does not by itself certify an unspecified two-control cusp slice.

Both gaps have local repairs.  Neither invalidates the direct fixed-finite-\(m\)
theorem once the intended hypotheses and finite-dimensional slices are made
explicit.

| Class | Count | Consequence |
| --- | ---: | --- |
| P0 mathematical contradiction | 0 | no false central theorem or invalid limit order found |
| P1 statement/proof assembly | 2 | repair before calling the Supplement self-contained |
| P2 precision/robustness | 6 | repair before referee-facing release |

Current decision:

- S2 affine sensitivity hierarchy: **PASS**;
- S3 weak-reaction mixed-jet estimate: **PASS after P1.1 is inserted**;
- S3 fold/cusp persistence assembly: **HOLD pending P1.2**;
- S4 fixed-finite-mode theorem: **PASS, scoped and sequential**;
- Round 41 zero-gap verdict: **superseded by this audit**;
- PRR scientific release: **unchanged HOLD**; this audit does not assess or
  promote any finite-parameter numerical result.

## Snapshot and material actually checked

| File | SHA-256 | Use |
| --- | --- | --- |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `23dd99b2e836eb6d1bfd90dc6e8cddaab955fb8725bc09d7436e5ef37e94446d` | attacked source |
| `notes/pde_mixed_jet_theorem.md` | `3fc37bafc6320556322e80daa2c56bad9fd4b19e1856100caa8adf92341a8007` | underlying semigroup/sensitivity note |
| `notes/direct_physical_multimode_theorem.md` | `7493499883ba41ce043c3535e1ca3d6c7a4c5de0cce9e575e261b4f8da9c2974` | underlying direct-theorem note |
| `notes/theorem_proof_stress_report.md` | `3974c6de34713ea56c365bdf37cc12029c0766f163db77d6c8ff17412969f649` | prior claims re-tested |
| `audits/round_41_supplement_theory_package.md` | `699c8a176a0f2ad62a6e57e93f9f5d63d54fe31582183a32e34bfff980397695` | prior PASS attacked |

I also read the quotient/source implementations around
`packages/vkcore/src/vkcore/encounter2d.py` and
`code/positive_b_broad_four_slab.py` only to check coordinate and budget
conventions.  Those finite-grid/broad-slab sources are not evidence for the
narrow-Gaussian continuum theorem, and no such transfer is made below.

## P1 findings

### P1.1: the general state, survival, and bounded mixed-jet theorem omit the hypothesis on \(q_0\)

**Locations:** Supplement lines 138--175, 229--275, 342--353, and 416--445.

The source introduces

\[
 q_{B,w}(t)=e^{tA_{B,w}}q_0,
 \qquad S_B(t)=\langle1,q_{B,w}(t)\rangle,
\]

and later uses \(\|q_0\|_X\), but it never states, for the bounded quotient,
that \(q_0\in L^2(\mathcal Q_d^{\rm box})\).  It states only the stronger
unbounded requirement \(q_0\in X_\pi\).  The sensitivity proof also uses that
the initial law is control-independent without declaring that as a hypothesis.

For the operator-norm mixed-jet estimate, \(q_0\in X\) is indispensable.  For
the earlier words “reaction-time density” and “survival probability,” one also
needs a nonnegative normalized density.  On the bounded quotient, \(L^2\)
embeds into \(L^1\); on the unbounded quotient, the required embedding follows
from normalized \(\pi\):

\[
 \|q_0\|_{L^1}
 \le \|q_0\|_{L^2(\pi^{-1})}\,\|1\|_{L^2(\pi)}.
\]

Thus the intended result is repairable, but the advertised self-contained
hypothesis list is presently incomplete.

**Required repair.** Before defining the killed state, declare \(\pi\) to be
normalized and state

\[
 \begin{cases}
 q_0\in L^2(\Qbox),&\text{bounded quotient},\\
 q_0\in X_\pi,&\text{unbounded quotient},
 \end{cases}
 \qquad q_0\ge0,\quad \langle1,q_0\rangle=1,
\]

with \(q_0\) independent of \(w,\theta,B\).  If the analytic theorem is meant
for signed/complex data as well, state it first for arbitrary \(q_0\in X\),
then separately impose nonnegativity and unit mass only for the probabilistic
interpretation.  Say that mass balance is classical for \(t>0\) (and holds in
the integrated/a.e. sense from \(t=0\)).

### P1.2: the fold/cusp contraction map is dimensionally undefined until a control slice is frozen

**Locations:** Supplement lines 541--589; compare the vector control definition
at lines 192--203.

Earlier, \(\theta\in\mathbb R^{J-1}\).  The contraction statement sets
\(A_0=DH_0(x_0)\) and uses \(A_0^{-1}\), which requires a square map.  It then
says:

- for a fold, use two equations with variables \((t,\theta)\); and
- for a cusp, use three equations with variables
  \((t,\theta_1,\theta_2)\).

The fold map is \(\mathbb R^J\to\mathbb R^2\) under the existing meaning of
\(\theta\), and therefore has no inverse unless \(J-1=1\).  The cusp wording
implicitly selects two coordinates, but no two-plane is frozen.  Moreover,
full row rank of the subsequent matrix

\[
 R_B\in\mathbb R^{2\times(J-1)}
\]

does not imply that an arbitrary preselected two-column minor is nonsingular.
For example, a rank-two matrix can have its first two columns collinear.  Hence
the displayed Weyl condition on the full matrix does not, as written, complete
the invertibility proof for the unspecified three-variable cusp map.

**Required repair.** Freeze the unfolding before defining \(H_B\):

- for a fold, choose one dimensionless unit tangent \(e\) and write
  \(\theta=\bar\theta+e\lambda\), \(x=(t,\lambda)\);
- for a cusp, choose a fixed dimensionless isometric embedding
  \(E:\mathbb R^2\to\mathbb R^{J-1}\), write
  \(\theta=\bar\theta+E\xi\), and set \(x=(t,\xi_1,\xi_2)\); and
- use the restricted response \(R_B(x)E\) in the cusp rank/Weyl hypothesis,
  or explicitly choose \(E\) from a nonzero minor and then prove a uniform
  lower bound for that same frozen slice.

At a cusp root the repaired Jacobian determinant is, up to the declared column
orientation,

\[
 (F_B)_{tttt}\det\!\left[
 \begin{array}{c}
  \nabla_\theta(F_B)_t E\\
  \nabla_\theta(F_B)_{tt} E
 \end{array}\right].
\]

The existing mixed-jet theorem supplies all entries, and the contraction proof
then works verbatim.  This finding affects only the finite-dimensional
fold/cusp persistence assembly, not the \(O(B)\) semigroup theorem itself.

## P2 findings

### P2.1: define the complex control tube with a genuine Cauchy margin

**Locations:** Supplement lines 397--414 and 447--485.

“A complex polydisc tube of radius \(\delta\)” is not defined.  If it means the
open \(\delta\)-neighborhood of \(\Theta\), the closed Cauchy circle of radius
\(\delta\) about a boundary-near real point lies only in the closure.  Entire
affine dependence makes the current estimate recoverable by a limiting
argument, but that argument is absent and the exact factor
\(\delta^{-|\alpha|}\) should not depend on a convention left implicit.

**Repair.** Define an open set containing every closed \(\delta\)-polydisc
about \(\Theta\) (for example take norms on a \(2\delta\)-tube and apply Cauchy
at radius \(\delta\)), or state the \(\delta'\uparrow\delta\) limiting
argument.  This also makes uniformity over disconnected compact control sets
unambiguous.

### P2.2: write the complete Dyson ordering and separate real positivity from complex analyticity

**Locations:** Supplement lines 342--380 and 447--479.

The ellipsis in Eq. (S32) should explicitly contain the intermediate free
factors.  Define

\[
 \Delta_n=\{1\ge s_1\ge\cdots\ge s_n\ge0\}
\]

and print factors
\(e^{z(s_k-s_{k+1})\mathcal G}\) between successive multipliers.  Otherwise a
literal reading of the displayed product is not the Dyson series used by the
proof.  Also say: positivity and mass decrease hold for real \(t\ge0\), real
nonnegative controls, and real \(B\ge0\); contraction of the free semigroup in
norm holds for complex \(z\) with \(\operatorname{Re}z\ge0\).  Positivity has no
order-theoretic meaning for complex time/control.

### P2.3: make the differentiated wrapped-tail proof chart-independent

**Locations:** Supplement lines 700--749.

The lemma is correct under the printed strict contact-interior margin, but the
sentence that every nonzero image has an “additional fixed separation” is not
the safest torus argument: a nonzero image can be the nearest lift for points
near a fundamental-cell face.  What is invariant and sufficient is the
geodesic inequality

\[
 \inf_{t\in I_*}\inf_{r\notin C_a}
 d_{\mathbb R\times\mathbb T_W^{d-1}}(r,r_*(t))\ge\eta.
\]

This implies that **every** Euclidean lift has distance at least \(\eta\),
regardless of which image is nearest.  The proof should then give uniform lower
and upper covariance-eigenvalue bounds and one displayed differentiated
Gaussian estimate before summing the lattice images.  For \(r\ge1\), explicitly
use

\[
 \int\partial_t^r p_{\epsilon,t}=0,
 \qquad
 \partial_t^r(c_{d,\epsilon}-1)
 =-\int_{C_a^c}\partial_t^r p_{\epsilon,t},
\]

which is the normalization step allowing a tail rather than an integral over
the high-probability contact region.  These additions close the contact-geometry
and normalization attack without changing the lemma.

### P2.4: explicitly parameterize the compact weight set before invoking S3

**Locations:** Supplement lines 844--909.

The positive-\(B\) transfer is uniform over \(\mathcal W\), but S3 is stated in
the \(\theta\)-coordinates of one frozen tangent basis.  The missing bridge is
elementary but should be visible: choose one interior base point and tangent
basis, map \(\mathcal W\) to a compact \(\Theta\subset\mathbb R^{m-1}\), and
choose a complex tube.  Complex tube points need not remain probability
weights; they are used only for analytic Cauchy estimates.  This makes the
single uniform \(B_0(\epsilon)\) a direct application of the stated theorem
rather than an implicit coordinate change.

### P2.5: disambiguate the peak-balance corollary's control set and maximum

**Locations:** Supplement lines 917--956.

The balanced weight vector need not belong to the arbitrary \(\mathcal W\)
fixed in the preceding theorem.  In addition, “the certified maximum” is
ambiguous because the theorem certifies both a free-exposure maximum and a
positive-\(B\) Doi maximum, while the notation \(t^*_{j,\epsilon}\) has no
\(B\)-argument and is inserted into \(G_\epsilon\).

**Repair.** Reapply the theorem to the compact singleton
\(\mathcal W=\{w^{\rm bal}\}\), call the free maximum
\(t^{G,*}_{j,\epsilon}\), and reserve
\(t^{B,*}_{j,\epsilon}\) for the Doi maximum.  After Eq. (S58), state that the
\(O(B^2)\) constant may depend on fixed \(\epsilon\) and that the assertion is
\(B\downarrow0\) **after** fixing \(\epsilon\).  No joint or interchanged limit
is implied.

### P2.6: specify normalization domains and the normalized reversible density

**Locations:** Supplement lines 113--136 and 158--175.

Write \(\int_{I_z}\phi_j=1\) for the box and
\(\int_{\mathbb R}\phi_j=1\) for the unbounded cylinder.  Replace “up to
normalization” for \(\pi\) by a named normalized density before using
\(X_\pi\), its dual, the unitary map, and the \(L^1\) embedding.  The
centre-space budget calculation is otherwise correct:

\[
 \int_{\mathbb R\times\mathbb T_W^{d-1}}
 \frac{B}{W^{d-1}}\sum_jw_j\phi_j(z)\,dz\,dc_\perp=B.
\]

## Equation-by-equation attacks that passed

### S2 sensitivity signs, multiplicities, and direct terms

For the unnormalised multi-index derivative
\(q_\beta=\partial_\theta^\beta q\), differentiating
\(q_t=A(\theta)q\) gives exactly

\[
 (q_\beta)_t=Aq_\beta
 -B\sum_i\beta_iM_{U_i}q_{\beta-e_i}.
\]

There are no missing multinomial factors because the affine generator has only
first derivatives.  For example, a one-control third derivative has source
\(-3BM_Uq_{\theta\theta}\), and \(\beta=(1,1)\) gives the two distinct source
terms printed in the second-order formula.  Differentiating the affine outer
observable gives exactly

\[
 \partial_\theta^\beta f_B
 =B\left(\langle V,q_\beta\rangle
 +\sum_i\beta_i\langle U_i,q_{\beta-e_i}\rangle\right).
\]

Thus the signs, \(\beta_i\) coefficients, and direct observable terms pass.
The safe time derivative \(B\langle V,A^rq(t)\rangle\) is also correct and does
not illegally differentiate the sharp contact indicator with the adjoint.

The projected-response formula passes as well.  Its rows annihilate
\(M^{-1}c\), it agrees with \(G\) on \(c^Th=0\), and the displayed
minimum-\(M\)-norm solution is budget tangent whenever the stated row-rank
hypothesis holds.

### S3 similarity, Dyson orders, and mixed jets

The reversible identity

\[
 \mathcal L(\pi u)=\pi\,\pi^{-1}\nabla\!\cdot(\pi\mathbf D\nabla u)
\]

and the transformed weighted-Neumann boundary condition are correct.  On the
box the similarity condition number is bounded by
\(\sqrt{\pi_{\max}/\pi_{\min}}\); on the unbounded weighted cylinder the map is
unitary, so \(\kappa_\pi=1\).  The observable dual is correctly
\(L^2(\pi\,dx)\).

The complex-time disk \(|z-t|\le\tau/2\) stays in the open right half-plane and
satisfies \(|z|\le3T/2\).  The Dyson simplex volume \(1/n!\) therefore gives the
printed exponential operator bound.  Pairing the difference against the outer
observable introduces \(v_{*,\delta}\) once.  Cauchy then supplies
\(r!(2/\tau)^r\alpha!\delta^{-|\alpha|}\).  The \(n\ge2\) tail obeys

\[
 e^x-1-x\le\tfrac12x^2e^x,
\]

so the first correction really has an \(O(B^2)\) remainder through every fixed
mixed jet.  The expansion sign
\(F_B=G-B\mathcal H_w+O(B^2)\) is correct.

The mode-sign/strict-concavity persistence criterion and the contraction-ball
inequalities are correct once the square slice in P1.2 is supplied.  The Weyl
inequality is also correct for matrices evaluated at the same point uniformly
over the ball.

### S4 OU coefficients, weighted thresholds, and contact factor

The SDE factors match the equal-diffusivity midpoint/relative quotient.  The
variance coefficients are

\[
 s^2(t)=s_0^2e^{-2\gamma t}
 +\frac{D_0}{2\gamma}(1-e^{-2\gamma t}),
\]

\[
 u^2(t)=u_0^2e^{-2\gamma t}
 +\frac{2D_0}{\gamma}(1-e^{-2\gamma t}),
 \qquad
 \Sigma_\perp(t)=\Sigma_{\perp,0}+4D_0tI.
\]

For a Gaussian initial variance \(\epsilon^2v\) against an invariant Gaussian
variance \(\epsilon^2\sigma_\pi^2\), the quadratic exponent in
\(q_0^2/\pi\) is integrable exactly when \(v<2\sigma_\pi^2\).  This reproduces

\[
 s_0^2<D_0/\gamma,
 \qquad u_0^2<4D_0/\gamma.
\]

The strict conditions are also necessary even when the two means coincide; at
equality the quadratic decay cancels and the integral still diverges.  The
wrapped transverse factor is harmless for each fixed \(\epsilon>0\) because the
torus is compact.

Independence of the declared midpoint and relative laws gives the exact product
clock.  Gaussian convolution gives precisely the printed denominator
\(\epsilon S(t)\), exponent, and \(W^{-(d-1)}\) budget factor.  No probability
normalization of \(G_\epsilon\) is required.

### S4 own/cross scaling, uniform weights, and mode persistence

At \(t=t_j+\epsilon y\),

\[
 \epsilon g_{j,\epsilon}\to
 A_j(y)=H_j\exp[-k_j^2y^2/2],
 \qquad k_j=|\mu'(t_j)|/S(t_j).
\]

Since

\[
 A_j''(y)=k_j^2(k_j^2y^2-1)A_j(y),
\]

one may explicitly choose
\(0<L_0<\min_j k_j^{-1}\).  Endpoint slopes then scale as
\(\epsilon^{-2}\) and negative curvature as \(\epsilon^{-3}\).  For
\(i\ne j\), strict monotonicity of \(\mu\) leaves a fixed centre separation on
the shrinking \(j\)-interval, so every first or second derivative is a
polynomial in \(\epsilon^{-1}\) times
\(e^{-q_{ij}/\epsilon^2}\).  Fixed finite \(m\), \(w_j\ge w_{\min}\), and
\(w_i\le1\) give one \(\epsilon_0\) uniform over the declared compact weight
set.

Strict concavity plus opposite endpoint slopes proves exactly one
nondegenerate maximum in each named interval.  The gap endpoint signs prove at
least one interior local minimum without proving its nondegeneracy or excluding
additional extrema.  After fixing \(\epsilon\), the S3 \(C^2\) error is uniform
in \(w\), so a single positive \(B_0(\epsilon)\) preserves all these finite
margins.  The printed nested quantifiers have the correct order and make no
uniform claim as \(\epsilon\downarrow0\).

### Peak and event-mass asymptotics

The balanced weights satisfy

\[
 w_jH_j=
 \frac{1}{W^{d-1}\sqrt{2\pi}\sum_iS(t_i)},
\]

so their leading free-exposure peak heights are equal.  On the scaled local
interval, \(dt=\epsilon\,dy\), which gives a strictly positive order-one
free-exposure area.  For fixed \(\epsilon\),

\[
 f_{B,\epsilon}=B G_\epsilon-B^2\mathcal H+O(B^3),
\]

and hence the printed local event-mass formula
\(\int f=B\int G+O(B^2)\) is correct.  It supplies no positive absolute event
mass as \(B\downarrow0\), exactly as the Supplement states.

## Hidden-scope checks against the model source

1. The continuum theorem's midpoint diffusion \(D/2\) and relative diffusion
   \(2D\) match the quotient kernels used by the repository.
2. The centre-space normalization \(W^{-(d-1)}\) matches the source's division
   by transverse width and its explicit physical-budget reconstruction.
3. The theorem uses narrow Gaussian slabs and Gaussian initial data on an
   unbounded cylinder.  The current positive-budget computation uses a
   different broad finite-box family and a different initial law.  Therefore
   S4 is an existence theorem, not an analytic certification of that numerical
   result.  The Supplement currently respects this boundary.
4. The sharp continuum convention \(|R|_{\rm mi}<a\) versus a closed finite-grid
   contact mask has no continuum probabilistic effect because the Gaussian law
   assigns zero mass to the contact boundary.

## Exact repair order

1. Insert P1.1's state-space and probabilistic initial-data hypotheses before
   any survival/density assertion.
2. Replace the fold/cusp paragraph by the frozen one- and two-dimensional slice
   formulation in P1.2, and apply Weyl to the same restricted response used in
   the cusp Jacobian.
3. Make the Dyson simplex, complex tube, and real-versus-complex statements
   explicit.
4. Expand the contact-tail proof by one chart-independent distance inequality,
   one differentiated Gaussian majorant, and the normalization identity.
5. Insert the \(\mathcal W\to\Theta\) coordinate sentence and repair the
   balanced-peak notation/singleton control set.
6. Recompile and commission another independent mathematical reread.  A clean
   build alone is not an acceptance test for P1.1 or P1.2.

After steps 1--5, I expect the scoped analytical package to pass a conventional
paper-proof gate.  None of these repairs supplies the finite-parameter cusp,
event-mass floor, box/parity convergence, or independent solver required for
the separate PRR scientific-release decision.
