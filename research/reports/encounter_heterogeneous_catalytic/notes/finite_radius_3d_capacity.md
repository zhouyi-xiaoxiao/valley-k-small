# Three-dimensional relative-coordinate Doi capacity

## Exact reduction of the two-walker problem

Let (X_1) and (X_2) be independent Brownian motions on the same flat
three-torus, with diffusivities (D_1) and (D_2).  For a function that
depends only on the relative coordinate (r=X_1-X_2),

\[
 (D_1\Delta_{x_1}+D_2\Delta_{x_2})f(x_1-x_2)
   =(D_1+D_2)\Delta_r f(r).
\]

Thus the translation-invariant six-dimensional pair problem is exactly a
three-dimensional problem with

\[
 D_{\mathrm{rel}}=D_1+D_2.
\]

For a Doi reaction with intrinsic rate (kappa) whenever (|r|<a), the
mean reaction time solves the periodic backward equation

\[
 \left[-D_{\mathrm{rel}}\Delta
       +\kappa\mathbf 1_{\{|r|<a\}}\right]u(r)=1.
\]

This reduction is exact only because the domain and the reaction rule are
translation invariant.  Centre-coordinate catalytic heterogeneity destroys
the quotient and requires the full pair state.

## Effective radius of the Doi sphere

The steady radial capture problem in unbounded three-dimensional space has

\[
 c_{\mathrm{out}}(r)=1-\frac{a_{\mathrm{eff}}}{r},\qquad r>a,
\]

while the regular interior solution is proportional to

\[
 c_{\mathrm{in}}(r)=\frac{\sinh(qr)}{r},
 \qquad q=\sqrt{\kappa/D_{\mathrm{rel}}}.
\]

The interior logarithmic derivative at (a) is

\[
 q\coth(qa)-\frac1a.
\]

Matching both concentration and flux at (r=a), and writing
(z=qa=\sqrt\chi), gives

\[
 \boxed{
 a_{\mathrm{eff}}
   =a\left(1-\frac{\tanh\sqrt\chi}{\sqrt\chi}\right),
 \qquad
 \chi=\frac{\kappa a^2}{D_{\mathrm{rel}}}.}
\]

The corresponding infinite-space capture rate is

\[
 k_{\mathrm{Doi}}=4\pi D_{\mathrm{rel}}a_{\mathrm{eff}}.
\]

For a small target in a periodic volume (V), matched asymptotics therefore
predict

\[
 \langle T\rangle
   =\frac{V}{4\pi D_{\mathrm{rel}}a_{\mathrm{eff}}}
    + C_{\mathrm{torus}}\frac{L^2}{D_{\mathrm{rel}}}
    +o(L^2/D_{\mathrm{rel}}).
\]

The geometry-dependent second term is additive.  Consequently, the clean
finite-volume numerical test is the slope of (langle T\rangle) against
(1/a_{\mathrm{eff}}), not an assertion that the leading term is exact at a
finite radius.

## Reaction-limited small-radius check

At fixed (kappa), (chi\to0) as (a\to0), and

\[
 1-\frac{\tanh\sqrt\chi}{\sqrt\chi}
 =\frac\chi3-\frac{2\chi^2}{15}+O(\chi^3).
\]

Hence

\[
 a_{\mathrm{eff}}\sim\frac{\kappa a^3}{3D_{\mathrm{rel}}},
 \qquad
 k_{\mathrm{Doi}}\sim\kappa\frac{4\pi a^3}{3},
\]

and the mean time obeys the reaction-limited benchmark

\[
 \boxed{
 \langle T\rangle
   \sim\frac{V}{\kappa(4\pi a^3/3)}.}
\]

## Discretization and audit boundary

`vkcore.encounter3d` uses a cell-centred periodic finite-difference
Laplacian.  The spherical indicator is cell averaged by deterministic
subcell midpoint quadrature.  The backward operator is never assembled:
preconditioned conjugate gradients apply the seven-point stencil directly,
and an FFT inverse of the shifted periodic Laplacian supplies the
preconditioner.

The validation therefore establishes the exact relative-coordinate reduction,
fixed-radius convergence of the discrete backward solve, and finite-grid
compatibility with the effective-radius and fixed-(kappa) reaction-limited
scalings for a periodic cube.  On the fixed-chi shrinking-radius path,
`a/h` remains approximately `7.4--7.6`; the radius and mesh limits are thus
coupled rather than separately extrapolated.  The observed `0.114%` slope
agreement is not a certified continuum double-limit coefficient.  The study
also does **not** establish the quotient for centre-dependent catalytic
patches or remove the usual small-target and finite-grid errors.
