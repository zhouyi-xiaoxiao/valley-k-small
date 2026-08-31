# Observable four-patch physical-d=3 continuum confirmation protocol

Date frozen: 2026-07-13  
Evidence timing:
RESULT_INFORMED_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY

## 1. Purpose and known-before-freeze record

This protocol confirms whether the audited four-slab design remains observable
when the contact set is the true three-dimensional sphere on
\(\mathbb R\times\mathbb T_W^2\). It is a separate physical-\(d=3\)
calculation, not a reinterpretation of the physical-\(d=2\) disk result.

Exploration performed before this protocol was frozen had already exposed:

- the same longitudinal parameters and four catalyst slabs used in the
  physical-\(d=2\) study;
- a cusp near \(t=12.80973996\) on the slice \(w_0=0.28\), with weights near
  \((0.28,0.18220,0.20767,0.33013)\);
- a scaled fourth derivative near \(-39.8723\) and dimensionless unfolding
  singular-value ratio near \(0.2403\); and
- the information that the frozen inward-step grid contains observable
  triple-mode candidates, with a likely selected step near \(0.10\).

The evidence is therefore **result-informed confirmation**, not preregistered
discovery. The output is not interval certification, a finite-\(B\) killed-Doi
calculation, an independent PDE solve, or a passed project/publication gate.

## 2. Frozen physical model and exact kernel

Each particle has diffusivity \(D=0.002\). In longitudinal midpoint/relative
and two periodic transverse-relative coordinates,

\[
 \mathcal L_z={D\over2}\partial_{zz}
   -0.1(z-0.95)\partial_z,
 \qquad
 \mathcal L_{r_\parallel}=2D\partial_{r_\parallel r_\parallel}
   -0.1r_\parallel\partial_{r_\parallel},
 \qquad
 \mathcal L_{r_{\perp,k}}=2D\partial_{r_{\perp,k}r_{\perp,k}},\ k=1,2.
\]

The four independent initial coordinates are centred at \(0.14\) for the
midpoint, \(-0.35\) for the longitudinal relative coordinate, and zero for
each of the two transverse relative coordinates. The midpoint, longitudinal
relative coordinate, and each transverse relative coordinate are averaged
independently against the same normalized compact bump of half-width
\(0.004\). The transverse period is \(W=1\). Contact is the true sphere

\[
 r_\parallel^2+r_{\perp,1}^2+r_{\perp,2}^2<0.16^2.
\]

The four transversely uniform catalyst slabs are normalized compact bumps of
half-width \(0.008\), centred at \((0.35,0.60,0.75,0.90)\). Thus the response
per unit full installed budget contains \(1/W^2\):

\[
 g_j(t)={1\over W^2}\,\mathbb E[\phi_j(Z_t)]
 \Pr\{R_t\text{ is in the contact sphere}\}.
\]

For the production calculation, the two periodic heat kernels are expanded in
cosine modes. At fixed \(x=r_\parallel\), their integral over the transverse
disk of radius \(h=\sqrt{a^2-x^2}\) is evaluated exactly mode by mode using

\[
 I_{nm}(h)=
 \begin{cases}
 \pi h^2,&q_{nm}=0,\\
 2\pi h J_1(hq_{nm})/q_{nm},&q_{nm}>0,
 \end{cases}
 \quad q_{nm}=\sqrt{k_n^2+k_m^2}.
\]

Gauss--Legendre quadrature is used only for the remaining longitudinal sphere
coordinate and compact-bump averages.

## 3. Frozen cusp and inward-step scan

The affine slice and cusp equations are exactly those of the physical-\(d=2\)
protocol:

\[
 w_0=0.28,\qquad w_3=1-w_0-w_1-w_2,
\]

with \(f'=f''=f'''=0\). The determinant bracket is \([12,14]\). The cusp must
have strictly positive weights, scaled residuals through order three at most
\(10^{-8}\), nonzero scaled fourth derivative of magnitude at least \(0.5\),
unfolding rank two, and dimensionless unfolding SVD ratio at least \(0.10\).

Only

\[
 s\in\{0.02,0.03,\ldots,0.20\}
\]

may be considered along the signed strict inward normal. The derivative is
screened on \(t=0.1,0.102,\ldots,100\), and sign brackets are refined with
Cauchy jets. Eligibility requires positive normalized weights; exactly five
simple alternating stationary points; smallest-to-largest peak ratio at least
\(0.10\); both valley-to-smaller-neighbour ratios at most \(0.85\); scaled
curvature magnitude at least \(10^{-4}\); scaled root residual at most
\(10^{-9}\); no unresolved zero plateau; and the correct endpoint derivative
signs.

Selection is lexicographic and frozen:

1. maximize the minimum catalyst weight;
2. maximize the worst-valley margin to the \(0.85\) ceiling;
3. maximize the minimum-to-maximum peak ratio; and
4. use the smaller step as the deterministic final tie-break.

## 4. Frozen numerical confirmation and independent representation

The configurations, in the order (initial bump, patch, longitudinal sphere,
positive Fourier modes, Cauchy samples, Cauchy radius), are:

- coarse: \((56,56,56,12,48,0.50)\);
- primary: \((72,72,72,16,64,0.40)\); and
- fine: \((96,96,96,24,80,0.30)\).

Fine-to-primary gates are: cusp-time difference at most \(2\times10^{-8}\),
weight max-norm difference at most \(2\times10^{-8}\), scaled-fourth-
derivative difference at most \(2\times10^{-5}\), and selected fixed-weight
root-time difference at most \(2\times10^{-6}\).

The Fourier--Bessel sphere integral is independently checked at
\(t=1,5,13,25\) using direct spherical coordinates: 36 radial and 40 polar
Gauss--Legendre nodes and 256 equally spaced azimuths. This check evaluates the
pointwise product of the two periodic heat kernels and does not use the Bessel
disk formula. Its maximum relative discrepancy must not exceed
\(5\times10^{-11}\).

## 5. Frozen claim boundary

The result must preserve:

- preregistered_discovery=false;
- continuum_verified=false, because no interval certificate is supplied;
- finite_B_Doi_verified=false;
- independent_PDE_solver_verified=false;
- project_gate_passed=false; and
- observable_d3_free_exposure_confirmation_passed=true only if every frozen
  numerical gate passes.

For this fixed geometry, the separate compact-time weak-budget theorem implies
qualitative persistence for sufficiently small positive \(B\), but this
calculation supplies neither an explicit \(B_0\) nor finite-\(B\) event-mass
evidence. Those remain nonoptional release gates.
