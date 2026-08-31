# Theorem-proof stress report: direct finite-mode construction and weak-budget transfer

Date: 2026-07-13  
Role: independent proof reconstruction and adversarial stress test  
Edit boundary: this report is additive.  It does not edit the manuscript,
the two theorem notes, any numerical result, or the frozen positive-budget
chain.

## 1. Executive result

The two analytical statements used as the manuscript's spine survive a fresh
equation-by-equation attack in their **scoped** form:

1. for every prescribed fixed finite number of target times, an
   epsilon-dependent physical-(d=2,3) OU slab family has at least that many
   local maxima after first fixing sufficiently small positive epsilon and then
   taking sufficiently small positive budget; and
2. on every compact positive-time window, the budget-normalized Doi density
   converges to the free-exposure observable through every fixed finite
   time/control jet at order (O(B)), with quantitative local persistence
   conditions for modes, folds, cusps, and projected control rank.

I found no counterexample to either statement and no missing hypothesis that
invalidates the theorem as reconstructed from the detailed notes.  The
mathematical severity is therefore

| Class | Open count | Meaning |
| --- | ---: | --- |
| P0 mathematical contradiction | 0 | no false theorem or reversed limit found |
| P1 mathematical proof gap | 0 | no gap that blocks the scoped conclusions found |
| P1 formal-evidence gap | 1 | the main theorems are not Lean-formalized |
| P2 publication precision | 2 | the manuscript theorem block should be made self-contained; Lean scope should be stated explicitly |

The P1 formal-evidence finding does **not** downgrade the paper proof to a
conjecture.  It does mean that the current repository cannot honestly call the
fixed-finite-mode or weak-budget theorem Lean-verified.  Existing Lean modules
explicitly disclaim precisely these analytic steps.

This theory is a defensible analytical spine, but it is not by itself a PRR
scientific release argument.  Its small-(B) result is local in time and
qualitative in the admissible budget, while its finite-mode construction makes
the relative contact probability asymptotically one near the designed peaks.
A same-family finite-parameter allocation cusp/fold region, event-mass floor,
mesh/box continuation, and independent killed-process solver remain the
decisive promotion gates.

## 2. Snapshot and sources actually audited

| Source | SHA-256 | Role |
| --- | --- | --- |
| `manuscript/encounter_multimodal_prr.tex` | `f3bf7cb11b7657bc65cdcbb3b9f7fcc15e3b799c072177d2daaeb738401c89ed` | integrated theorem statements and Appendix |
| `notes/pde_mixed_jet_theorem.md` | `3fc37bafc6320556322e80daa2c56bad9fd4b19e1856100caa8adf92341a8007` | full weak-budget proof |
| `notes/direct_physical_multimode_theorem.md` | `7493499883ba41ce043c3535e1ca3d6c7a4c5de0cce9e575e261b4f8da9c2974` | full direct finite-mode proof |
| `FormalLean/EncounterDesign.lean` in the companion formal tree | `fa45ceb3c40e7c9769d4f7d6ab5aa1495e89a361c675b89f362dfc11798b8330` | finite design algebra only |
| `FormalLean/EncounterContinuum.lean` in the companion formal tree | `ae23060be3166c392eab2d8a0a5af5dcd1d3a4adf2a8b912fd8a0c2161e538b4` | coordinate/GIG/capacity algebra only |

The previous Round 18/19, Round 23, and Round 29/30 audits were treated as
claims to re-test, not as proof that the current snapshot was correct.

## 3. Exact quantifier reconstruction

The direct theorem is valid with the following order.  Writing
(mathcal W) for a compact subset of the open (m)-simplex, its logical form
is

\[
\begin{split}
&\text{for each }d\in\{2,3\},\text{ each fixed finite }m,
\text{ and each admissible fixed data set},\\
&\exists\epsilon _0>0\;\forall\epsilon\in(0,\epsilon _0)
\;\exists B_0(\epsilon)>0\;\forall B\in(0,B_0(\epsilon))
\;\forall w\in\mathcal W:\quad \mathsf P_{m}(B,\epsilon,w).
\end{split}
\]

Here the fixed data include

- (D_0,gamma,W,\rho,s_0,u_0,a,z_0,\bar z);
- (r_{\parallel,0},r_{\perp,0},\Sigma_{\perp,0});
- (s_0^2<D_0/\gamma), (u_0^2<4D_0/\gamma),
  (0<a<W/2), and (\Sigma_{\perp,0}\succ0);
- distinct target times in one compact positive-time window;
- the contact-interior margin for the deterministic relative path on fixed
  neighborhoods of all target times; and
- a positive lower weight bound on (\mathcal W).

The property (\mathsf P_m) is **one unique nondegenerate maximum in each of
(m) named disjoint (O(\epsilon)) intervals**, and hence at least (m)
maxima.  It is not an exact global root count.  The catalyst centres are tied
to the chosen target times, the slab widths and initial/noise scales depend on
epsilon, and the family depends on (m).  There is no interchange of the
epsilon and (B) limits.

The weak-budget theorem has a different, simpler order.  For fixed domain or
fixed epsilon in the weighted unbounded problem, fixed compact positive-time
window, fixed compact control set with a complex tube, and fixed finite jet
orders (r,\alpha),

\[
 \sup_{[\tau,T]\times\Theta}
 |\partial_t^r\partial_\theta^\alpha(F_B-G)|\le C_{r,\alpha}B
 \quad(0\le B\le B_{\max}).
\]

The constant may depend very badly on epsilon; the direct theorem invokes this
statement only after epsilon has been fixed.

## 4. Direct finite-mode theorem: independent derivation

### 4.1 OU variances and weighted initial law

For

\[
 dZ=-\gamma(Z-\bar z)dt+\epsilon\sqrt{D_0}\,dW,
\]

the variance coefficient is

\[
 s^2(t)=s_0^2e^{-2\gamma t}
 +\frac{D_0}{2\gamma}(1-e^{-2\gamma t}).
\]

For the relative longitudinal process with noise coefficient
(2\epsilon\sqrt{D_0}), it is

\[
 u_0^2e^{-2\gamma t}
 +\frac{2D_0}{\gamma}(1-e^{-2\gamma t}).
\]

Thus the invariant variance coefficients are respectively
(D_0/(2\gamma)) and (2D_0/\gamma).  Direct integration of
(q_0^2/\pi_\epsilon) gives the strict and mean-independent thresholds

\[
 s_0^2<D_0/\gamma,\qquad u_0^2<4D_0/\gamma.
\]

These conditions are pointwise in epsilon.  The norm can grow exponentially
as epsilon decreases because (z_0\ne\bar z), but finiteness for every fixed
epsilon is all that the sequential theorem uses.

### 4.2 Exact factorization and resource normalization

The equal-diffusivity midpoint and relative coordinates are independent under
the declared product initial law and independent Brownian drivers.  The
relative noise coefficient (2\epsilon\sqrt{D_0}) and midpoint coefficient
(\epsilon\sqrt{D_0}) have the correct factors.

The normalized longitudinal Gaussian integrates to one.  Multiplication by
(W^{-(d-1)}) makes each slab have unit integral over the complete centre
space.  The installed centre-space catalyst amount is therefore (B), while
the full killing is the product with the disk/sphere contact indicator.  This
is consistent with the budget definition; it is deliberately not the integral
of the killing over all relative coordinates.

The exact free channel is

\[
 g_{j,\epsilon}(t)=
 \frac{c_{d,\epsilon}(t)}
 {W^{d-1}\sqrt{2\pi}\epsilon S(t)}
 \exp\!\left[-\frac{(\mu(t_j)-\mu(t))^2}
 {2\epsilon^2S^2(t)}\right].
\]

No probabilistic normalization of (G=\sum_jw_jg_j) is asserted or needed.

### 4.3 Contact tail

On the fixed union of target neighborhoods, the deterministic relative mean
has a positive contact-interior margin.  The wrapped Gaussian covariance is
(\epsilon^2\Sigma_R(t)), with a uniformly positive coefficient matrix and
bounded time derivatives on that compact positive-time set.  Differentiating
the image-sum density any fixed number of times contributes only polynomial
powers of (\epsilon^{-1}).  The complement of the contact ball remains a
fixed positive torus distance from the mean, so Gaussian tails give

\[
 \sup_{I_*}|\partial_t^r(c_{d,\epsilon}-1)|
 \le C_r\epsilon^{-N_r}e^{-q/\epsilon^2}.
\]

The condition (a<W/2), together with the contact-interior hypothesis, keeps
the contact ball inside one minimum-image chart; nonzero images retain a fixed
separation.  This argument is dimension-stable between the physical disk and
sphere cases.

### 4.4 Own-channel and cross-channel asymptotics

At (t=t_j+\epsilon y),

\[
 \frac{\mu(t_j)-\mu(t_j+\epsilon y)}{\epsilon}
 \to-\mu'(t_j)y
\]

in (C^2) on every fixed (y)-interval.  Since (\mu'(t_j)\ne0), the
rescaled own clock tends to a centred Gaussian (A_j).  A common small
(L_0>0) exists for fixed finite (m) such that all (A_j''<0) on
([-L_0,L_0]), with opposite nonzero endpoint slopes.  Consequently the
unscaled slope and curvature margins are of orders
(\epsilon^{-2}) and (\epsilon^{-3}).

For (i\ne j), strict monotonicity of the midpoint path and distinct target
times give a fixed positive separation
(|\mu(t_i)-\mu(t)|\) on the shrinking (j)-th interval.  Every first or
second time derivative is therefore a polynomial in (\epsilon^{-1}) times
(e^{-q_{ij}/\epsilon^2}).  Fixed finite (m) and
(w_j\ge w_{\min}>0) make these cross terms uniformly smaller than the own
channel margins.

The mixture derivative is then strictly decreasing and changes sign exactly
once on each named interval.  This proves one unique nondegenerate maximum per
interval.  A negative derivative at the right edge of one peak interval and a
positive derivative at the left edge of the next force an interior minimum of
the closed gap.  The proof correctly does not claim that this minimum is
nondegenerate or that no other critical point exists.

### 4.5 Positive-budget transfer

After epsilon is fixed, the Gaussian catalyst is bounded and belongs to the
dual observable space, while the declared initial law belongs to
(X_{\pi_\epsilon}).  The weak-budget theorem gives uniform (C^2) convergence
over the compact weight set.  Endpoint-slope and strict-curvature inequalities
are open under this perturbation, so one unique nondegenerate maximum persists
in every named interval.  This step justifies

\[
 \exists B_0(\epsilon)>0,
\]

but provides no useful lower estimate on that threshold.  In particular, it
does not imply a positive overlap with an experimental event-mass floor.

## 5. Weak-budget theorem: independent derivation

### 5.1 Bounded quotient

Writing (q=\pi u) transforms the forward reflected OU operator to

\[
 \mathcal G=\pi^{-1}\nabla\!\cdot(\pi\mathbf D\nabla),
\]

with weighted Neumann boundary conditions.  Its closed form is nonpositive
and self-adjoint on (L^2(\pi dx)).  On a bounded quotient, multiplication by
pi is a bounded isomorphism to unweighted (L^2).  Bounded killing is a
bounded perturbation, so positive-time analytic smoothing and entire affine
control dependence follow.

The discontinuous contact indicator causes no time-regularity failure because
it is used as a bounded multiplication operator.  The safe time derivative is
(\langle V,A^rq\rangle), not an application of (A^*\) to the indicator.

### 5.2 Unbounded weighted cylinder

On the unbounded OU cylinder, (q=\pi u) is unitary from (L^2(\pi dx)) to
(X_\pi=L^2(\pi^{-1}dx)).  Multiplication by bounded (V) is bounded there,
and the observable satisfies

\[
 |\langle V,q\rangle|
 \le\|V\|_{L^2(\pi dx)}\|q\|_{X_\pi}.
\]

Thus the unbounded result does not import a divergent bounded-box similarity
constant.  The stronger initial-law requirement is both necessary for this
proof route and present in the direct theorem.

### 5.3 Dyson/Cauchy estimate

For complex time with nonnegative real part, self-adjoint nonpositivity gives
(\|e^{z\mathcal G}\|\le1).  The Dyson simplex has volume (1/n!\), hence

\[
 \|T_{B,w}(z)-T_0(z)\|
 \le\kappa_\pi(e^{B|z|\|V_w\|_\infty}-1).
\]

The similarity constant occurs once because the multiplication operator
commutes with multiplication by pi.  Pairing against the outer observable
supplies (v_2), not another similarity constant.  The disk of radius
(\tau/2) about any (t\in[\tau,T]) stays in the right half-plane and has
(|z|\le3T/2).  Time and control Cauchy estimates therefore give the displayed
(O(B)) mixed-jet bound with the stated factorial, radius, and tube factors.

The separately displayed (n\ge2) complex Dyson tail justifies the claimed
(O(B^2)) first-correction remainder through mixed jets.  It does not rely on
a real-axis estimate.

### 5.4 Exact sensitivities and persistence

Differentiating the affine generator gives

\[
 s_{i,t}=As_i-BU_iq,
 \qquad
 s_{ij,t}=As_{ij}-BU_is_j-BU_js_i.
\]

Differentiating the observable adds the direct (U_i) terms.  The cusp
Jacobian requires fourth time order and first control derivatives through
third time order; all are covered on positive-time compact sets.

The contraction criterion in the manuscript is sufficient: its derivative
bound makes (x-A_0^{-1}H_B(x)) a contraction, and its residual bound maps the
closed ball into itself.  It gives a unique zero in that ball and preserves
Jacobian invertibility.  It does not claim global uniqueness.

For the cusp, at the root the determinant factors into the quartic time
derivative and the determinant of the two budget-tangent response rows.  The
Wronskian identity has the correct orientation:

\[
 [g''''{}^Tw_*]\det\!\binom{g'^TP}{g''^TP}
 =\det[P,w_*]\,\Delta'(t_*).
\]

Weyl's inequality is applied to matrices at the same point throughout a
region, so it remains valid at the displaced root.  The raw response for the
physical density is (B R_B); only normalized rank, not absolute response,
can remain nonzero as (B\downarrow0).

## 6. Open findings

### P1-E1: the analytical spine is not Lean-verified

This is a formal-evidence failure, not a mathematical counterexample.

The available companion module `FormalLean/EncounterDesign.lean` says in its
header that it does not prove the (2q-1) roots, their nondegeneracy, or their
persistence under width, boundaries, discretization, or overlap.  The module
`FormalLean/EncounterContinuum.lean` says it does not assert PDE well-posedness,
error bounds, or cusp root counts.  `FormalLean/Encounter.lean` likewise
excludes the analytic bridge and implicit-function reduction.  The axiom
reports are clean for the algebra they actually contain, but those algebraic
lemmas do not imply either theorem audited here.

Consequences:

- `PROVED` is defensible as a conventional mathematical-paper status;
- `LEAN VERIFIED`, `FORMALLY VERIFIED`, or any equivalent project-wide label
  is not defensible for these two main results;
- the current Lean files live in another report tree and are not pinned as a
  report-owned transitive source of the PRR manuscript.

Minimum safe repair, in increasing order of ambition:

1. add a report-owned scope ledger saying exactly which manuscript statements
   have and have not been formalized;
2. formalize the tractable logical last mile in Lean: disjoint interval signs
   plus strict curvature imply one unique nondegenerate maximum per interval;
   uniform (C^2) perturbations preserve those inequalities; and the nested
   quantifier order is epsilon first, then (B);
3. formalize the finite-dimensional cusp determinant, contraction mapping,
   and Weyl assembly used by the manuscript;
4. only if full Lean verification remains a user requirement, formalize or
   import a precise analytic-semigroup/Dyson theorem and a wrapped-Gaussian
   differentiated tail lemma.  Until then, describe the PDE and tail parts as
   human-audited proofs.

The first three tasks are realistic.  Calling the whole PDE theorem Lean-
verified before task 4 would still overstate the evidence.

### P2-T1: the manuscript theorem paragraph is not fully self-contained

The detailed theorem note states all hypotheses, but the manuscript begins by
fixing (D_0,\gamma,W,\rho,s_0,u_0,a,z_0,\bar z) and only later introduces
(r_{\parallel,0},r_{\perp,0},\Sigma_{\perp,0}).  The two weighted-space
inequalities are described as “the fixed-epsilon hypotheses used below,” but
the displayed theorem paragraph does not open with “under the preceding
hypotheses.”

This is unlikely to fool a sympathetic reader, but it is unnecessary referee
friction.  The eventual focused rewrite should give a boxed theorem whose
first sentence explicitly quantifies all initial-law data, cites the two strict
variance inequalities, and says that the target-time/contact condition is an
assumption.  It should display the quantifier order

\[
 \exists\epsilon_0\;\forall\epsilon<\epsilon_0\;
 \exists B_0(\epsilon)\;\forall B<B_0(\epsilon).
\]

### P2-T2: theorem proof provenance is split across three locations

The main statement is in the manuscript, detailed constants and lemmas are in
two Markdown notes, and unrelated-but-adjacent algebra is in another report's
Lean tree.  That is adequate for an internal audit but weak as a submission
proof package.  Before submission, put the full direct theorem and the exact
weak-budget proposition in one paper/Supplement source, with conventional
references for the analytic-semigroup facts and a numbered proof of the
wrapped-Gaussian tail lemma.  Keep Markdown audits as provenance, not as a
mathematical dependency that a referee must discover.

## 7. Attacks that passed

1. The midpoint and relative diffusion factors and invariant variances are
   correct.
2. The Gaussian (L^2(\pi^{-1})) thresholds are strict and correct; means do
   not change them.
3. The catalyst budget is a centre-space integral and is not confused with a
   configuration-space killing integral.
4. Exact midpoint/relative factorization follows from the declared product
   law and independent drivers.
5. The contact-tail derivative estimate has the needed compact-positive-time,
   cut-locus, and covariance hypotheses.
6. Own-channel polynomial margins dominate all fixed-finite cross-channel
   exponential tails uniformly over the declared weight set.
7. Gap endpoint signs prove at least one intervening local minimum without
   overclaiming its nondegeneracy.
8. The positive-(B) transfer is sequential and does not use an epsilon-uniform
   weighted norm.
9. The bounded and unbounded weak-budget proofs use the correct Hilbert spaces
   and observable norms.
10. The mixed-jet estimate includes the direct observable derivatives and all
    time/control orders needed for fold and cusp persistence.
11. The contraction criterion is local and sufficient; it does not smuggle in
    a global root count.
12. The two-row rank condition is imposed only when at least two tangent
    controls exist, and raw response degeneration as (B\to0) is disclosed.
13. No theorem claims a long-time (t=O(B^{-1})) limit, an event-mass floor,
    a fixed geometry for all (m), arbitrary localized patches, or arbitrary
    physical dimension.

## 8. PRR-level judgment and shortest theoretical upgrade

The present analytical spine is **necessary and publishable**, but it is not
alone sufficient for the intended PRR narrative.  Its strongest direct
existence construction deliberately arranges
(c_{d,\epsilon}\to1) near every peak.  Therefore it demonstrates that a true
encounter operator can host any prescribed fixed finite local mode count, but
it does not yet show a nontrivial encounter-driven multimodal phase diagram at
finite physical parameters.

The shortest high-value upgrade is not another abstract existence theorem.  It
is the following same-family chain in physical (d=2):

1. freeze one broad four-slab finite-parameter family;
2. compute the positive-(B) allocation cusp and both adjacent fold sheets
   using the exact tangent equations, not only a scalar budget direction;
3. certify a trimodal region with an absolute event-mass floor and a remote
   persistent max--min pair;
4. continue the complete jet under odd/even mesh and box sequences; and
5. reproduce topology and masses with an unbounded off-lattice killed-process
   method without refitting.

For theory, add one quantitative table connecting the free cusp margins,
mixed-jet errors, and observed finite-(B) margins.  The general estimate may
be very conservative because (\|q_0\|_{X_{\pi_\epsilon}}) can grow
exponentially as epsilon narrows; that is not a defect, but it makes a merely
symbolic (B_0(\epsilon)>0) physically weak.  A localized semigroup estimate
or computer-assisted finite-parameter bound would be much more valuable than
an additional qualitative corollary.

Physical (d=3) can remain theorem plus exact (B=0) kernel evidence in the
first focused paper unless the title promises finite-(B) robustness in both
dimensions.  A later multi-(d) paper should pursue dimension-uniform contact
kernel bounds or capacity/local-time asymptotics rather than duplicate the
finite-volume scan.

## 9. Final decision

- **Scoped mathematical theorem status:** maintain **PROVED**.
- **Lean status of the two main theorems:** **NOT FORMALIZED**.
- **PRR scientific release:** **HOLD**, for the finite-parameter and independent-
  validation gates above, not because the two scoped proofs failed.
- **Safe manuscript action:** retain the current boundaries; in the focused
  rewrite make the theorem quantifiers self-contained and do not add a Lean-
  verification claim.

