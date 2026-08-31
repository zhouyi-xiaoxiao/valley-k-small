# Relative/centre GIG screening and the physical modality fold

## Evidence boundary

This note separates two statements that must not be conflated.

1. The relative/centre calculation gives a leading free-motion, narrow-patch
   approximation for conditional reaction channels.  It is useful for
   predicting modes and screening mixture folds, but no uniform remainder
   bound is claimed here.
2. The reported physical fold is located directly in the finite `L=31`
   independent-clock killed CTMC.  Its time derivatives and parameter
   transversality are matrix-exponential identities, not finite differences.

There is no lattice-to-continuum convergence claim in this artifact.

## Relative and centre coordinates

Let walker 1 start to the left of walker 2 and close the initial separation
`d>0`.  In the interior Brownian approximation,

\[
D_r=D_1+D_2,\qquad
D_c=\frac{D_1D_2}{D_1+D_2},
\]

and, with the diffusivity-weighted centre coordinate,

\[
c=\frac{D_2X+D_1Y}{D_1+D_2},\qquad
v_c=\frac{D_2v_1+D_1v_2}{D_1+D_2}.
\]

Equivalently, take the initial relative displacement to be `-d` along the
closing axis and write `w=v1-v2>0` for the closing speed.  The joint first-encounter
time/location density at encounter position `z` is

\[
j(z,t)=
\frac{d}{\sqrt{4\pi D_rt^3}}
\exp\!\left[-\frac{(d-wt)^2}{4D_rt}\right]
\frac{1}{\sqrt{4\pi D_ct}}
\exp\!\left[-\frac{(z-c_0-v_ct)^2}{4D_ct}\right].
\]

Evaluating this density over a narrow early catalytic patch centred at `z_E`
gives, up to a time-independent capture factor,

\[
g_E(t)\propto t^{-2}\exp(-A_E/t-B_Et),
\]

\[
A_E=\frac{d^2}{4D_r}+\frac{(z_E-c_0)^2}{4D_c},\qquad
B_E=\frac{w^2}{4D_r}+\frac{v_c^2}{4D_c}.
\]

Direct expansion identifies that factor as

\[
\exp\!\left[\frac{dw}{2D_r}
+\frac{(z_E-c_0)v_c}{2D_c}\right].
\]

It cancels from the normalized conditional time shape for one channel, but it
depends on catalyst position and drift direction.  It must therefore be
absorbed into a physical channel's splitting amplitude rather than omitted
when comparing or designing mixture weights.

For a drift-dominated late trip over distance `d_B`, the leading law is the
inverse-Gaussian density

\[
g_B(t)\propto t^{-3/2}\exp(-A_B/t-B_Bt),\qquad
A_B=\frac{d_B^2}{4D_2},\quad B_B=\frac{v_2^2}{4D_2}.
\]

The common normalized family

\[
g(t;A,B,\nu)=\frac{t^{-\nu}e^{-A/t-Bt}}{Z(A,B,\nu)}
\]

has

\[
Z=2(A/B)^{(1-\nu)/2}K_{1-\nu}(2\sqrt{AB})\quad(B>0),
\]

and `Z=A^(1-nu) Gamma(nu-1)` when `B=0` and `nu>1`.  Its mode is

\[
t_m=\frac{2A}{\nu+\sqrt{\nu^2+4AB}},
\]

with the continuous zero-drift limit `t_m=A/nu`.  Consequently the boundary
mode approaches `d_B/v_2` in the large-Peclet regime and equals
`d_B^2/(6D_2)` at zero drift.

For the canonical lattice rates, the interior mapping uses

\[
D_1=0.35,\quad D_2=0.10,\quad v_1=0.21,\quad v_2=0.06.
\]

The predicted joint early and boundary modes are compared with, but not fitted
to, the finite-CTMC channel maxima detected and Brent-refined within the
declared search horizon.

## Fixed-shape GIG fold

For

\[
f(t;p)=p g_1(t)+(1-p)g_2(t),
\]

eliminating `p` from `f_t=f_tt=0` gives

\[
g_1'g_2''-g_2'g_1''=0,\qquad
p_*=-\frac{g_2'}{g_1'-g_2'}.
\]

For `g=C t^(-nu) exp(-A/t-Bt)`, define

\[
a=(\log g)'=A/t^2-B-\nu/t,
\]

\[
b=(\log g)''=-2A/t^3+\nu/t^2,
\]

\[
c=(\log g)'''=6A/t^4-2\nu/t^3.
\]

Then

\[
g'=ga,\qquad g''=g(a^2+b),\qquad
g'''=g(a^3+3ab+c).
\]

The numerical artifact enumerates both admissible GIG folds and verifies the
two derivative residuals, `f_ttt != 0`, and weight transversality
`partial_p f_t=g_1'-g_2' != 0`.  These folds are screening boundaries only:
the channel shapes and weights of the killed CTMC depend jointly on physical
parameters.

## Physical CTMC fold

For the two-walker generator `L0`, catalytic selectors `U`, and rates `K`,

\[
T=L_0-UKU^T,\qquad b=UK\mathbf 1,\qquad
f(t,\theta)=\alpha e^{T(\theta)t}b(\theta).
\]

The physical control is

\[
\theta=\log(\kappa_{\mathrm{near}}/\kappa_{\mathrm{far}}),
\]

with the far rate fixed.  Changing `theta` changes the killed generator and
the observable, so both splitting weights and conditional channel shapes
respond.  Exact time derivatives are

\[
\partial_t^n f=\alpha e^{Tt}T^n b.
\]

For the parameter sensitivity, let the column state satisfy

\[
p'=T^Tp,\qquad s'=T^Ts+T_\theta^Tp,\qquad s(0)=0.
\]

The pair `(p,s)` is propagated by one augmented matrix exponential.  It gives

\[
f_{t\theta}=
s^T Tb+p^T T_\theta b+p^T T b_\theta.
\]

At the reported root the dimensionless `f_t` and `f_tt` residuals are stored
beside nonzero `f_ttt` and `f_ttheta`.  Splitting probabilities are calculated
without time quadrature from

\[
\alpha(-T)^{-1}UK.
\]

## Local normal form and held-out validation

Near a generic fold,

\[
f_t(t,\theta)=a\,\Delta\theta+\frac{b}{2}\,\Delta t^2+
o(|\Delta\theta|+|\Delta t|^2),
\]

where `a=f_ttheta` and `b=f_ttt`.  In the observed orientation, `a<0` and
`b>0`, so the two critical points exist for `Delta theta>0` and

\[
\Delta t_{\pm}=\pm\sqrt{-2a/b}\,\Delta\theta^{1/2}+o(\Delta\theta^{1/2}).
\]

Their separation therefore scales as `Delta theta^(1/2)`.  Integrating the
quadratic derivative between the new maximum and minimum gives local
prominence

\[
\mathcal P=\frac{2b}{3}\left(-\frac{2a}{b}\right)^{3/2}
\Delta\theta^{3/2}+o(\Delta\theta^{3/2}).
\]

The continuation points used for the log-log checks are not used to locate the
fold.  Negative held-out points show no detected local maximum/minimum pair in
the declared local window; positive points yield two detected derivative sign
changes, Brent-refined using finite-matrix semigroup evaluations.  Coarse
sampled-time extrema and finite-difference derivatives are retained only as
convergence diagnostics against the direct matrix-exponential calculation.
