# Observable four-patch continuum confirmation protocol

Date frozen: 2026-07-13  
Evidence timing:
RESULT_INFORMED_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY

## 1. Purpose and known-before-freeze record

This protocol confirms, rather than discovers, an exact-continuum
free-exposure design on the physical \(d=2\)
\(\mathbb R\times\mathbb T_W\) slab quotient. Before the protocol and
manifest were written, exploratory work had already exposed:

- physical parameters near \(D=0.002\), \(\gamma=0.1\), OU mean \(0.95\),
  and contact radius \(0.16\);
- initial compact-bump half-width \(0.004\);
- four compact catalyst supports of half-width \(0.008\), centred at
  \((0.35,0.60,0.75,0.90)\);
- a cusp near \(t=13.3280\) on the slice \(w_0=0.28\), with weights near
  \((0.28,0.2302,0.2093,0.2805)\);
- a scaled fourth derivative near \(-42.8\) and an unfolding singular-value
  ratio near \(0.256\); and
- the information that a strict inward step around \(0.15\) can satisfy the
  observability floors.

These facts are recorded to prevent rediscovery language. The result may be
called a **formal result-informed continuum-kernel confirmation**, but not a
preregistered discovery, interval proof, finite-\(B\) Doi result, or passed
project/publication gate.

## 2. Frozen physical model

The two particles have equal single-particle diffusivity \(D=0.002\). In
longitudinal midpoint/relative and periodic transverse-relative coordinates,

\[
 \mathcal L_z={D\over2}\partial_{zz}
   -0.1(z-0.95)\partial_z,
 \qquad
 \mathcal L_{r_\parallel}=2D\partial_{r_\parallel r_\parallel}
   -0.1r_\parallel\partial_{r_\parallel},
 \qquad
 \mathcal L_{r_\perp}=2D\partial_{r_\perp r_\perp}.
\]

The midpoint starts at \(0.14\), the longitudinal relative coordinate at
\(-0.35\), and the transverse relative coordinate at zero. Each is averaged
against the same normalized compact bump

\[
 b(u)=I_b^{-1}\exp[-(1-u^2)^{-1}]\mathbf1_{|u|<1}
\]

with physical half-width \(0.004\).

The transverse period is \(W=1\), and contact is the true disk
\(r_\parallel^2+r_\perp^2<0.16^2\). Each catalyst profile is a normalized
copy of the compact bump with half-width \(0.008\). Because the catalyst is a
transversely uniform slab, the response per unit **full installed budget**
contains \(1/W\):

\[
 g_j(t)={1\over W}\,
 \mathbb E[\phi_j(Z_t)]\,
 \Pr\{R_t\text{ is in the contact disk}\}.
\]

## 3. Frozen affine cusp

The first catalyst weight is fixed:

\[
 w_0=0.28,\qquad
 w_3=1-w_0-w_1-w_2.
\]

The determinant bracket is \([12,14.5]\). For channel jets \(g_j^{(r)}\),
the three cusp equations are written as

\[
 (g_1^{(r)}-g_3^{(r)})w_1
 +(g_2^{(r)}-g_3^{(r)})w_2
 +g_3^{(r)}+w_0(g_0^{(r)}-g_3^{(r)})=0,
 \quad r=1,2,3.
\]

The zero is found from the determinant of this \(3\times3\) affine augmented
matrix. The recovered weights must be strictly positive and sum to one. The
frozen gates are:

- maximum scaled residual in orders one through three: \(10^{-8}\);
- minimum absolute scaled fourth derivative: \(0.5\);
- unfolding rank: two;
- minimum dimensionless unfolding SVD ratio: \(0.10\).

The two slice-tangent directions are
\((0,1,0,-1)\) and \((0,0,1,-1)\). The strict cusp normal is the unit
two-coordinate vector perpendicular to the first unfolding row, signed so
its projection on the second row has sign opposite to \(f^{(4)}/6\).

## 4. Frozen inward-step scan and observability rule

Only these 19 steps may be considered:

\[
 s\in\{0.02,0.03,\ldots,0.20\}.
\]

For each step,

\[
 w(s)=w_{\rm cusp}+s\,d_{\rm inward}.
\]

The exact-real first derivative is screened on
\(t=0.1,0.102,\ldots,100\); every sign bracket is refined using Cauchy jets.
The relative density floor is \(10^{-12}\), and the relative derivative-zero
tolerance is \(5\times10^{-12}\). Every retained root must have scaled
first-derivative residual at most \(10^{-9}\) and absolute scaled curvature
at least \(10^{-4}\).

A candidate is eligible only when all of the following hold:

1. all four weights are strictly positive and sum to one;
2. exactly five roots occur, with topology
   maximum--minimum--maximum--minimum--maximum;
3. the smallest peak is at least \(0.10\) of the largest peak;
4. each valley is at most \(0.85\) of the smaller adjacent peak;
5. no unresolved multi-sample zero plateau occurs; and
6. the derivative is positive at the first screened time and negative at the
   last screened time.

The selection priority is frozen before execution:

1. maximize the minimum catalyst weight;
2. then maximize the worst-valley margin
   \(\min_i(0.85-V_i/\min(P_i,P_{i+1}))\);
3. then maximize the minimum-to-maximum peak ratio; and
4. if still tied, choose the smaller step.

No rule or grid may be changed after reading the formal result.

## 5. Frozen numerical confirmation

The primary calculation uses:

| component | primary value |
| --- | ---: |
| initial-bump Gauss--Legendre order | 104 |
| patch Gauss--Legendre order | 104 |
| contact-angle order | 160 |
| positive transverse Fourier modes | 40 |
| Cauchy samples | 64 |
| Cauchy radius | 0.40 |

The coarse configuration is (72,72,112,28,48,0.50) and the fine
configuration is (136,136,208,52,80,0.30) in the same field order. The
fine-to-primary gates are:

- cusp-time difference at most \(2\times10^{-8}\);
- weight max-norm difference at most \(2\times10^{-8}\);
- scaled-fourth-derivative difference at most \(2\times10^{-5}\);
- selected fixed-weight root-time difference at most \(2\times10^{-6}\).

The disk-contact half-chord integral is checked against a separate
80-radial-node, 512-angle polar disk quadrature at fixed times
\(1,5,13,25\). The maximum relative discrepancy must not exceed
\(2\times10^{-11}\).

## 6. Frozen claim boundary

The result must preserve:

- continuum_verified=false because no interval certificate is supplied;
- finite_B_Doi_verified=false;
- project_gate_passed=false; and
- observable_free_exposure_confirmation_passed=true only if every frozen
  numerical gate passes.

The next nonoptional stages are an independent audit, interval or explicit
remainder bounds, a quantitative positive-\(B\) persistence radius, an
independent killed-Doi solver, and the physical-\(d=3\) calculation.
