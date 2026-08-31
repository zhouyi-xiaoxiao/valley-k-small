# Round 15 PDE mixed-jet and weak-reaction theory attack

Date: 2026-07-13  
Scope: exact physical-\(d=2\)/\(d=3\) quotient Doi PDE, continuum
time/control jets, weak-reaction transfer, and numerical-theorem boundary  
Primary output: `notes/pde_mixed_jet_theorem.md`

## 1. Verdict

### Mathematical verdict

**PASS, with a narrower theorem than the original global bridge target.**

For the bounded reflected-OU x periodic quotient with fixed patches and sharp
contact indicator, the following are rigorously available:

1. an analytic positive killed semigroup on \(L^2\);
2. arbitrary positive-time mixed time/control differentiability;
3. exact first and second simplex sensitivity PDEs, including every direct
   observable derivative;
4. exact fold/cusp time-control jets without differentiating the indicator;
5. a uniform finite-window theorem
   \[
   B^{-1}f_B(t,w)=\langle V_w,e^{t\mathcal L}q_0\rangle+O(B)
   \]
   through every fixed mixed jet, with an explicit Dyson/Cauchy constant;
6. quantitative mode/fold/cusp persistence and a Weyl projected-rank lower
   bound whenever the leading free-exposure mixture has declared margins.

This is a model-specific continuum bridge and applies without a dimensional
change in the proof to the exact slab quotients in physical \(d=2\) and
\(d=3\).

### PRR verdict

**HOLD.**  The theorem removes the basic PDE differentiability obstruction and
provides a substantially easier analytical route than a global GIG-to-Doi
approximation.  It does not yet close the PRR gate because:

- no quantitatively nondegenerate free-exposure fold/cusp/multimode design has
  been established for the frozen physical patches;
- no resulting numerical value \(B_*>0\) has been computed;
- the current \(B=0.6\) has not been shown to lie below \(B_*\);
- absolute early event mass vanishes as \(B\downarrow0\);
- the fixed-time expansion does not certify the long tail; and
- no SG/FEM \(C^1\) fold/cusp estimator or physical-\(d=3\) calculation exists.

The bounded-perturbation and Dyson ingredients are standard.  They become a
publishable analytical contribution only when paired with a nontrivial
physical free-exposure singularity, quantitative resource-tangent rank, and
an observable interval of nonzero \(B\).

## 2. Materials read completely

- `manuscript/encounter_multimodal_prr.tex`
- `notes/theorem_program.md`
- `notes/continuum_g1_design.md`
- `notes/research_contract.md`
- `audits/round_10_novelty_and_positioning.md`
- `audits/round_12_predecessor_overlap_audit.md`

The analysis preserves their common boundaries: the GIG theorem is reduced,
the exact quotient is a new slab testbed rather than a refinement of M2D-F,
and finite software gates are not continuum theorems.

## 3. Adversarial regularity tests

### Test 3.1: \(q_0\in L^2\), not \(D(\mathcal L)\)

**PASS after restricting to \(t\ge\tau>0\).**  Analytic semigroup smoothing
puts \(e^{tA}q_0\) in every generator-power domain for positive time.  There is
no justified cusp jet at \(t=0\), and the constants necessarily deteriorate
as powers of \(\tau^{-1}\).  The new theorem states this explicitly.

### Test 3.2: discontinuous contact indicator

**PASS for time/amplitude derivatives; FAIL for a naive adjoint formula.**
The indicator is bounded multiplication, so it is an admissible zero-order
perturbation.  It need not belong to \(D(A^*)\).  Consequently

\[
 f^{(r)}=B\langle V_w,A^rq\rangle
\]

is justified for \(t>0\), whereas moving \(A^r\) onto \(V_w\) is generally
not.  No spatial \(C^\infty\) claim across the contact interface is made.

### Test 3.3: forward/backward sign and reflecting boundary

**PASS.**  The note uses the forward convention

\[
 \mathcal Lq=-\nabla\cdot(bq)+\nabla\cdot(\mathbf D\nabla q),
 \quad (bq-\mathbf D\nabla q)\cdot n=0.
\]

The reversible substitution \(q=\pi u\) converts this to a weighted backward
Neumann generator.  It also gives the correct mass identity
\(-d\int q/dt=B\int V_wq\).  Every sensitivity inherits the same homogeneous
boundary conditions because the parameter perturbation is zero order.

### Test 3.4: direct observable derivative

**PASS.**  The first sensitivity contains

\[
 B\langle U_i,q\rangle+B\langle V_w,s_i\rangle,
\]

and the second sensitivity contains both cross direct terms plus the state
second sensitivity.  A semigroup-only derivative would miss the leading
free-exposure control response and would give the wrong rank as \(B\to0\).

### Test 3.5: cusp order

**PASS.**  The exact cusp map
\((f_t,f_{tt},f_{ttt})\) requires \(f_{tttt}\) and the mixed derivatives
\(f_{t\theta_i},f_{tt\theta_i},f_{ttt\theta_i}\) in its Jacobian.  All are
covered on \([\tau,T]\).  Joint \(C^3\) remains insufficient.

### Test 3.6: fixed-budget rank is basis dependent unless a metric is frozen

**PASS after freezing the tangent metric.**  The theorem chooses
\(P^TMP=I\) and \(\mathbf1^TP=0\).  Rank is basis invariant, but a numerical
smallest singular value is not invariant under arbitrary rescaling of the
simplex coordinates.  Every reported rank floor must therefore include the
metric/basis.

## 4. Weak-reaction theorem attack

### 4.1 Exact expansion

For \(F_B=f_B/B\) and
\(G=\langle V_w,e^{t\mathcal L}q_0\rangle\), the note proves

\[
 F_B=G-B\int_0^t
 \langle V_w,T_0(t-s)V_wT_0(s)q_0\rangle ds+R_{2,B},
\]

with

\[
 |R_{2,B}|\le
 \|V_w\|_2\kappa_\pi
 [e^{B\|V_w\|_\infty t}-1-B\|V_w\|_\infty t]\|q_0\|_2.
\]

The normalized leading error is therefore \(O(B)\), and the displayed
first-correction remainder is \(O(B^2)\).

### 4.2 Mixed-jet uniformity

Cauchy estimates on the positive-time complex disk and a finite-dimensional
complex control tube give, for every fixed \(r,\alpha\),

\[
 \sup_{[\tau,T]\times\Theta}
 |\partial_t^r\partial_\theta^\alpha(F_B-G)|
 \le B C_{r,\alpha}(\tau,T,\delta,B_0).
\]

The constant is written explicitly in the theorem note.  It contains
\((2/\tau)^r\), the control-tube radius, \(L^2/L^\infty\) patch bounds, the
reversible similarity condition number, \(T\), and \(\|q_0\|_2\).  This is
strong enough for the full fold and cusp jets.

### 4.3 Attempted counterexample: control second derivatives

The leading \(G\) is affine in the simplex weights, so its second control
derivative vanishes.  This does not contradict a nonlinear Doi control
response: the theorem correctly gives \(D_\theta^2F_B=O(B)\), and the second
sensitivity PDE supplies its exact value.  No false \(O(1)\) curvature is
claimed in the weak-reaction limit.

### 4.4 Attempted counterexample: full-time normalization

**The stronger statement is false.**  On a bounded irreducible reflected
domain, \(G(t,w)\) approaches a positive stationary exposure and is not a
probability density on \([0,\infty)\).  For each fixed \(B>0\), the killed Doi
density eventually decays and may have total reaction mass one.  The limit is
singular on \(t=O(B^{-1})\).  The explicit bound also becomes order one on
that scale.  Therefore the theorem is intentionally uniform only on fixed
compact time windows.

### 4.5 Attempted substitution: \(B=0.6\)

**Rejected.**  Neither \(B\) alone nor its decimal value is a dimensionless
smallness condition.  The relevant quantity includes
\(B\|V\|_\infty T\) and the persistence margins.  A valid application must
compute a nondimensional \(B_*\) from the explicit jet bound and show a
nonempty overlap between:

\[
 B\le B_* \quad\text{(theoretical persistence)}
\]

and

\[
 B\ge B_{\rm obs} \quad\text{(event-mass/rate observability)}.
\]

No such overlap is presently established, and the existing \(B=0.6\) result
must not be relabelled.

## 5. Quantitative singularity and Weyl attack

The theorem note supplies a contraction-based persistence lemma.  If the
free fold/cusp map has Jacobian smallest singular value \(\mu>0\) on a ball,
and the normalized Doi map has value and derivative errors
\(\varepsilon_0,\varepsilon_1\) satisfying

\[
 \varepsilon_0\le\mu r/2,
 \qquad \varepsilon_1\le\mu/4,
\]

then the Doi singularity is unique in that ball,

\[
 \|x_B-x_0\|\le2\varepsilon_0/\mu,
 \qquad \sigma_{\min}(DH_B(x_B))\ge\mu/2.
\]

For the two-row budget-projected control matrix, Weyl gives

\[
 \sigma_2(R_B)\ge\sigma_2(R_0)-\|R_B-R_0\|_2.
\]

At the displaced cusp there is an additional explicit Lipschitz-displacement
term.  This is a true quantitative lower bound, not merely a rank assertion.

The adversarial scaling boundary is essential: this is the rank matrix for
\(F_B=f_B/B\).  The raw response matrix for \(f_B\) is \(B R_B\).  Its
condition ratio may remain healthy, but its absolute smallest singular value
and event rate vanish linearly with \(B\).

### 5.1 Exact factorization gives a computable cusp discriminant

The free G1 operator, initial law, and killing basis factor into midpoint and
relative parts.  Therefore

\[
 g_j(t)=a_j(t)c_d(t),\qquad
 g_j^{(r)}=\sum_{k=0}^r{r\choose k}a_j^{(k)}c_d^{(r-k)}.
\]

For three patches, define the \(3\times3\) derivative matrix with rows
\(g'^T,g''^T,g'''^T\) and determinant \(\Delta(t)\).  Corollary 4.2 proves a
concrete recipe:

- isolate a rank-two zero \(\Delta(t_*)=0\);
- normalize its null vector \(w_*\) by \(\mathbf1^Tw_*=1\) and require
  \(w_*>0\);
- require \(g''''(t_*)^Tw_*\ne0\); and
- require the two tangent rows \(g'^TP,g''^TP\) to be invertible in the frozen
  metric basis.

These conditions give a nondegenerate interior free-exposure cusp.  The exact
identity

\[
 \det DC_0
 =[g''''^Tw_*]\det
 \begin{pmatrix}g'^TP\\g''^TP\end{pmatrix}
 =\det[P,w_*]\,\Delta'(t_*)
\]

links the scalar determinant crossing to the full cusp Jacobian.  This is the
most useful model-specific spatial-configuration consequence of the semigroup
theory: it reduces the free cusp search to factor clocks and a scalar
determinant without turning an unverified candidate into a theorem.
Determinant magnitudes remain basis scaled; the frozen-metric singular value
is the conditioning certificate.

## 6. Relationship to the reduced GIG theorem

The new leading functions are

\[
 g_j(t)=\langle V_j,e^{t\mathcal L}q_0\rangle,
\]

not GIG clocks.  The weak-\(B\) theorem therefore does **not** close the
manuscript's global GIG-to-Doi target.  It creates a cleaner two-tier route:

1. prove or certify modes/fold/cusp directly in the exact free-exposure
   mixture and transfer them to weak Doi killing; or
2. separately prove a patch/heat-kernel estimate
   \(g_j\approx g_j^{\rm GIG}\), then combine its jet error with the \(O(B)\)
   Dyson error.

Only route 2 transfers the arbitrary-\(m\) GIG theorem.  Route 1 is sufficient
for a strong finite-mode continuum paper and avoids making a global GIG
parametrix the critical path.

For fixed finite \(m\), if the exact \(g_j\) satisfy the channel-dominance
margins, the theorem transfers at least \(m\) local maxima for small \(B\).
There is no uniform-in-\(m\) \(B_*\), event-mass floor, or observability floor.

## 7. Physical-\(d=2\) and \(d=3\) scope

### Exact slab quotient

**PASS in both dimensions.**  The proof uses only:

- a bounded product of two reflected OU coordinates with a torus;
- positive diagonal diffusion;
- the reversible no-flux form;
- bounded fixed killing profiles; and
- finite-dimensional affine amplitudes.

Adding the second transverse relative coordinate in physical \(d=3\) changes
the quotient from three to four PDE coordinates and the contact disk to a
sphere, but does not change the semigroup or perturbation argument.  The
physical normalization remains \(W^{-(d-1)}\).

The reflected-face theorem is for the bounded numerical box.  The note also
proves the natural-decay unbounded quotient in the weighted density space
\(L^2(\pi^{-1}dx)\); the compact G1 initial bump satisfies that stronger
condition.  An arbitrary datum known only to lie in unweighted \(L^2\) is not
covered on the unbounded cylinder.

### Localized physical patches

**Not covered by the exact quotient claim.**  The abstract bounded-domain
semigroup proof can be repeated in the full two-particle configuration space,
but a transversely localized catalyst breaks quotient closure and restores
the larger state dimension.  This note cannot be cited as a symmetry theorem
for localized disks.

## 8. Numerical-transfer attack

### P0.1 No SG/FEM mixed-jet estimator exists

The current solver has excellent algebraic and local-reference gates, but
there is no proved bound

\[
 \|H_h-H\|_{C^1}\le E_h
 \quad\text{or}\quad
 \|C_h-C\|_{C^1}\le E_h
\]

for the continuum fold/cusp maps.  In particular, no result controls the
fourth time derivative and mixed third-time/first-control derivative through
the sharp cut-cell killing interface.

**Consequence:** stable grids, a zero residual of the discrete generator, and
agreement of two discrete exponential actions do not prove a nearby PDE cusp.

### P0.2 No convergence rate may be invented

The sharp indicator lowers spatial regularity.  The rate could depend on
interface alignment and the norm used.  Until a theorem is proved, neither
second order nor any other \(h^p\) rate may be inserted into a continuum
certificate.  An empirical parity extrapolation is numerical evidence only.

### P1.1 A practical certification path remains

A future proof could combine a conforming variational discretization or
verified FV residual estimator, analytic-semigroup smoothing away from zero,
cut-cell quadrature bounds, sensitivity residuals, and a
Newton--Kantorovich/radii-polynomial root certificate.  This is a research
plan, not an accomplished estimator.

## 9. Effect on the prior novelty and overlap gates

| Prior gate | Round 15 effect |
|---|---|
| Exact continuum mixed-jet differentiability | **CLOSED for the exact bounded quotient** |
| Direct observable sensitivity terms | **CLOSED** |
| Abstract conditional fold/cusp persistence | **CLOSED quantitatively** |
| Model-specific projected rank lower bound | **OPEN until a positive free-exposure margin is established** |
| Physical 2D cusp/fold manifold | **OPEN** |
| Applicability at \(B=0.6\) | **OPEN** |
| Finite-grid-to-PDE cusp certificate | **OPEN** |
| Physical 3D controlled transition | **OPEN** |
| Arbitrary-\(m\) physical GIG transfer | **OPEN** |

Thus Round 15 materially advances P0.4 of Round 10 and gate 4 of Round 12,
but does not by itself change `release_eligible=false`.

## 10. Recommended next decision

The highest-information next calculation is not another killed-\(B=0.6\)
line scan.  It is a prospectively frozen full-simplex analysis of the exact
free-exposure clocks \(g_j(t)\):

1. compute/isolate their complete positive-time derivative structure;
2. test the full two-dimensional budget simplex for a fold/cusp and a remote
   pair;
3. record scaled margins, \(\mu\), projected \(s_*\), prominence, separator
   signs, and window event exposure;
4. insert those numbers into the explicit bound to obtain a rigorous, even if
   conservative, \(B_*\); and
5. only on success, continue from weak \(B\) toward an observable finite
   budget with continuum and independent-method gates.

Outcomes:

- **If a well-conditioned free cusp and a nonempty
  \([B_{\rm obs},B_*]\) exist:** this is a credible analytical continuum bridge
  and a strong basis for the physical 2D/3D program.
- **If a cusp exists but the interval is empty:** retain the theorem, but use
  validated finite-\(B\) continuation rather than claiming weak-reaction
  observability.
- **If the free simplex has no topology boundary:** the weak-\(B\) route is a
  no-go for this frozen patch family; redesign prospectively or redirect to a
  finite-mode JCP/PRE result.

## 11. Final decision

- PDE analytic-semigroup and mixed-jet theorem: **PROVED**.
- Weak-\(B\) continuum exposure-to-Doi bridge: **PROVED on compact positive-time
  windows**.
- Conditional fold/cusp/mode and Weyl-rank transfer: **PROVED**.
- Current physical \(B=0.6\) continuum claim: **NOT PROVED**.
- Long-time/global-density and event-mass claim: **NOT PROVED**.
- SG/FEM continuum root certification: **OPEN**.
- PRR release status: **HOLD**.

### Severity ledger

- **P0:** no certified free-exposure cusp/rank margin, no admissible bound at
  \(B=0.6\), no finite-grid-to-PDE mixed-jet estimator, and no physical 3D
  transition.  These remain release blockers.
- **P1:** the compact-time weak-\(B\) result has an event-mass/long-tail gap;
  the unbounded quotient requires \(q_0\in L^2(\pi^{-1}dx)\); and the
  determinant recipe still requires a prospectively certified candidate.
- **P2:** no mathematical wording defect remains in the two Round 15 files.
  Standard semigroup references are supporting citations, not novelty claims.
