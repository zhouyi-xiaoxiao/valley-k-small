# G1d single-segment finite-budget fold confirmation protocol

Date frozen: 2026-07-13  
Status: **prospective confirmation protocol, conditional on the pinned G1c artifact**

## Scope

G1d may confirm at most one finite-grid fold on the frozen G1c physical family.
It cannot verify the continuum limit, select another segment after seeing the
result, map the full phase boundary, or pass the project/PRR gate.

The deterministic post-result selection rule in
`audits/round_24_g1c_topology_manual_review.md` chooses

\[
 w(\lambda)=(0.2,0.1\lambda,0.8-0.1\lambda),
 \qquad 0\leq\lambda\leq1,                                \tag{1}
\]

because its G1c interpolated seed has the largest minimum catalyst weight.
The starting guess is fixed at \((t,\lambda)=(10.5,0.68)\).

## Numerical solve

Use the unchanged \(65\times65\times49\) cell-centred quotient, physical
budget \(B=0.6\), transport, contact quadrature, initial law, and patch
profiles from G1c.  At each Newton iterate assemble the arbitrary-weight
killed generator exactly.  Propagate the state and its exact control
sensitivity with the block system

\[
 {d\over dt}\binom q{s_\lambda}
 =\begin{pmatrix}A^T&0\\A_\lambda&A^T\end{pmatrix}
  \binom q{s_\lambda},
 \qquad(q,s_\lambda)(0)=(q_0,0).                          \tag{2}
\]

For \(v_0=K\), \(v_{r+1}=Av_r\), and

\[
 v'_{0}=K_\lambda,
 \qquad v'_{r+1}=A_\lambda v_r+Av'_r,                    \tag{3}
\]

evaluate

\[
 f^{(r)}=q^Tv_r,
 \qquad \partial_\lambda f^{(r)}
 =s_\lambda^Tv_r+q^Tv'_r.                                \tag{4}
\]

Newton solves \(f_t=f_{tt}=0\) with the exact Jacobian

\[
 \begin{pmatrix}f_{tt}&f_{t\lambda}\\
 f_{ttt}&f_{tt\lambda}\end{pmatrix}.                     \tag{5}
\]

No finite-difference derivative may be used inside the solve.  A centered
finite-difference check at two decreasing steps is required afterward as an
independent diagnostic.

## Frozen acceptance gates

The finite-grid fold confirmation passes only if all of the following hold:

1. Newton converges inside \(t\in[8,14]\), \(\lambda\in[0.45,0.9]\), in at
   most 12 iterations.
2. Scaled residuals satisfy
   \(|tf_t/f|\leq10^{-9}\) and
   \(|t^2f_{tt}/f|\leq10^{-9}\).
3. All three catalyst weights are at least \(0.02\).
4. The dimensionless nondegeneracy margins satisfy
   \(|t^3f_{ttt}/f|\geq10^{-3}\) and
   \(|t f_{t\lambda}/f|\geq10^{-3}\).
5. The determinant of (5), after row/column dimensionless scaling, has
   magnitude at least \(10^{-4}\).
6. At \(\lambda_*\pm0.02\), a local time screen on \([3,18]\) with spacing
   \(0.02\), followed by exact root refinement, gives one-versus-three simple
   roots of \(f_t\); the three-root side alternates maximum--minimum--maximum.
7. Centered control derivatives at steps \(10^{-3}\) and \(5\times10^{-4}\)
   approach the exact \(f_{t\lambda}\) and \(f_{tt\lambda}\); the finer-step
   relative error is at most \(2\times10^{-4}\).
8. Fixed-budget, positivity, generator reconstruction, mass balance, initial
   mass, and contact-safe initial-law gates pass with the unchanged G1c
   tolerances.

If any gate fails, the status is `FAIL_G1D_FOLD_CONFIRMATION`.  Passing status
is `PASS_FINITE_GRID_FOLD_ONLY`; `continuum_verified` and
`project_gate_passed` remain false in either case.

## Evidence limits

This is a result-informed confirmation of a candidate found by G1c.  It does
not count as a preregistered discovery.  It runs one mesh and one finite-box
method, has no odd/even extrapolation, and does not establish a cusp or
trimodality.  A passing result authorizes a separately frozen convergence
campaign, not a manuscript claim of a physical continuum fold.
