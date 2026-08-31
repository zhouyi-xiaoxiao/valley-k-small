# Weak-budget/free-exposure design diagnostic

Status: **result-informed reproduction, not preregistered discovery**.

## Purpose and evidence timing

An exploratory scratch calculation had already exposed a positive three-patch
candidate near `t=9.4478` and weights `(0.3441,0.2642,0.3916)` before this
protocol was written.  The calculation below therefore reproduces and audits
that known candidate.  It must never be presented as a prospectively frozen
discovery, a finite-budget Doi cusp, a continuum result, or a passed PRR
project gate.

The intended mathematical use is narrower and useful: it identifies a clean
target for a future theorem that differentiates the killed semigroup at full
installed budget `B=0`, controls the remainder uniformly on a compact time
window, and then transfers the nondegenerate cusp to sufficiently small
positive `B` and eventually to mesh-refined continuum operators.

## Exact discrete free-exposure factorization

Keep the current G1 geometry and its `65 x 65 x 49` finite-volume mesh fixed.
At `B=0` the quotient generator is the exact discrete Kronecker sum

\[
  L_0=L_z\otimes I+I\otimes L_r,
\]

where `L_z` is the midpoint Scharfetter--Gummel generator and `L_r` is the
relative longitudinal Scharfetter--Gummel/periodic transverse generator.  The
initial law also factors.  For the unit-integral midpoint patch `phi_j` and
the cell-averaged circular contact indicator `chi`, define

\[
 a_j^{(q)}(t)=p_z e^{tL_z}L_z^q\phi_j,
 \qquad
 c^{(q)}(t)=p_r e^{tL_r}L_r^q\chi.
\]

Because the transverse width is one in the frozen model, the response per
unit full installed budget is

\[
 h_j(t)=a_j(t)c(t),\qquad
 h_j^{(n)}(t)=\sum_{q=0}^n {n\choose q}
 a_j^{(q)}(t)c^{(n-q)}(t),\quad 0\le n\le4.
\]

All derivatives are generator actions, not finite differences.  A separate
low-grid calculation forms the full Kronecker generator and compares
`p_0 exp(tL_0)L_0^n(phi_j tensor chi)` with the factorized Leibniz values for
all three patches, orders zero through four, and four selected times.

## Cusp and unfolding checks

Let `H_w=sum_j w_j h_j` for nonnegative weights summing to one.  The known
candidate is reproduced by finding a zero in `[9,10]` of

\[
 D(t)=\det\begin{pmatrix}
 h_1'&h_2'&h_3'\\
 h_1''&h_2''&h_3''\\
 h_1'''&h_2'''&h_3'''
 \end{pmatrix}.
\]

The right null vector is normalized to unit sum and must be strictly positive.
The audit then checks `H'=H''=H'''=0`, `H''''` nonzero, and rank two of the
two-control unfolding matrix made from the first two derivative rows in the
coordinates `(w_left,w_middle)` with `w_right=1-w_left-w_middle`.

For a direct normal-form check, choose the unit control direction perpendicular
to the first unfolding row and sign it so the induced linear-in-time term has
sign opposite to `H''''/6`.  The frozen step `0.005` must yield three nearby
stationary roots with maximum--minimum--maximum topology.  This demonstrates
the local bimodal side of the discrete weak-exposure cusp; it is not a
trimodality result.

## Complete `0.01` weight-simplex screen

Enumerate all 5,151 integer triples `(i,j,k)` with `i+j+k=100`.  On the fixed
time grid `0,0.01,...,80`, count sampled sign-changing stationary roots after
`t=0.5` while enforcing a relative density floor and a relative derivative
zero tolerance.  This is a finite screen, not an interval proof.  The known
current geometry is expected to reach at most two modes; the artifact must not
call that outcome trimodal.

The scratch record also contains a more promising, **unfrozen and excluded**
geometry with centres approximately `(0.37,0.61,0.85)`.  Its apparent remote
maximum plus local cusp-created max--min--max structure may form a trimodal
wedge.  Those numbers are recorded only to prevent rediscovery bias.  They
require a new, separately frozen geometry-design study and are not evidence in
the present artifact.

## Required negative flags and next theorem

Every result must state:

- `continuum_verified=false`;
- `project_gate_passed=false`;
- `finite_B_Doi_cusp_verified=false`.

The next proof obligation is a uniform compact-time expansion

\[
 f_B^{(q)}(t;w)=B H_w^{(q)}(t)+O(B^2),\qquad q=0,1,2,3,4,
\]

with constants compatible with the full installed-budget normalization.
Only after that theorem, finite-positive-`B` numerical continuation,
odd/even mesh refinement, and an independent solver can the present design
diagnostic contribute to a continuum PRR claim.
