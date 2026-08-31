# Continuum and multidimensional theory skeleton for heterogeneous catalytic encounters

## 1. Claim boundary and evidence language

This note fixes the continuum model and the analytical obligations for the
encounter paper.  It deliberately separates three levels of statement.

- **[T] Theorem/identity.**  A statement that is either an exact algebraic
  identity, a standard PDE consequence under explicitly listed hypotheses, or
  a theorem that the paper must prove.
- **[C] Conjecture/theorem target.**  A model-specific asymptotic statement for
  which a proof, including a remainder estimate, is not yet present.
- **[N] Numerical evidence.**  A finite-state, finite-grid, or continuation
  result.  Numerical evidence can test a theorem's assumptions and falsify a
  conjecture, but it is not a proof of a continuum limit.

The defensible target contribution is not the first encounter-time
distribution, the first bimodal first-passage density, the first heterogeneous
reaction model, or the first Green-function reduction.  Those ingredients are
already represented in the literature listed in Section 12.  The intended
increment is narrower and testable:

> In the declared finite CTMC and lattice models, spatially patterned
> reactivity along the encounter manifold selects dynamically distinct streams
> whose channel weights and conditional time laws generate a computable
> finite-grid modality fold. A controlled finite-radius continuum realization,
> with a uniform error bound over the mode-forming window, remains a **[C]**
> theorem target rather than a present result.

No phrase such as "first-ever bimodality" or "first general theory of
heterogeneous reactions" should appear in the manuscript.

## 2. Two walkers in physical dimension \(d\)

### 2.1 Joint Fokker--Planck equation

Let \(X_i(t)\in\Omega_i\subset\mathbb R^d\) satisfy

\[
 dX_i=b_i(X_i)\,dt+\sqrt{2D_i}\,dW_i,
 \qquad D_i>0,\quad i=1,2,
\]

with independent Brownian motions.  Before reaction, the joint density
\(p(x_1,x_2,t)\) on \(\Omega_1\times\Omega_2\) obeys

\[
 \partial_t p=\mathcal L_0p-K(x_1,x_2)p,
\]

\[
 \mathcal L_0p
 =-\nabla_{x_1}\!\cdot(b_1p)-\nabla_{x_2}\!\cdot(b_2p)
  +D_1\Delta_{x_1}p+D_2\Delta_{x_2}p.                 \tag{2.1}
\]

For a reflecting outer boundary, the probability currents

\[
 J_i=b_i p-D_i\nabla_{x_i}p
\]

satisfy \(J_i\cdot n_i=0\).  More general mobility tensors can be used, but
the scalar-diffusivity case is the canonical model because it admits an exact
decoupling of relative and centre diffusion.

### 2.2 Relative, diffusion-decoupling, and catalytic coordinates

Set

\[
 D_r=D_1+D_2,\qquad
 D_c=\frac{D_1D_2}{D_1+D_2},                           \tag{2.2}
\]

\[
 r=X_1-X_2,\qquad
 R=\frac{D_2X_1+D_1X_2}{D_1+D_2}.                     \tag{2.3}
\]

The diffusion-decoupling coordinate \(R\) need not be the physical location at
which a catalyst reads the pair.  We therefore declare an independent affine
catalytic coordinate

\[
 C_\eta=\eta X_1+(1-\eta)X_2,\qquad 0\leq\eta\leq1.   \tag{2.3a}
\]

Using the inverse transformation below gives the exact relation

\[
 C_\eta=R+\left(\eta-\frac{D_2}{D_r}\right)r.         \tag{2.3b}
\]

Thus \(C_{D_2/D_r}=R\) is the unique affine catalytic coordinate whose noise
decouples from the relative noise.  The physical midpoint convention used by
the bounded two-dimensional calculations is instead

\[
 C_{1/2}=\frac{X_1+X_2}{2}
 =R+\frac{D_1-D_2}{2D_r}r.                            \tag{2.3c}
\]

Inside the Doi contact tube, this distinction is quantitatively bounded by

\[
 \lvert C_{1/2}-R\rvert
 \leq \frac{|D_1-D_2|}{2D_r}\,a
 \qquad\text{whenever }|r|<a.                         \tag{2.3d}
\]

The inverse transformation and gradients are

\[
 x_1=R+\frac{D_1}{D_r}r,qquad
 x_2=R-\frac{D_2}{D_r}r,                              \tag{2.4}
\]

\[
 \nabla_{x_1}=\nabla_r+\frac{D_2}{D_r}\nabla_R,qquad
 \nabla_{x_2}=-\nabla_r+\frac{D_1}{D_r}\nabla_R.      \tag{2.5}
\]

Substitution gives the exact cancellation

\[
 D_1\Delta_{x_1}+D_2\Delta_{x_2}
 =D_r\Delta_r+D_c\Delta_R.                            \tag{2.6}
\]

Thus, if \(q(R,r,t)=p(x_1,x_2,t)\),

\[
 \partial_tq
 =-\nabla_r\!\cdot(uq)-\nabla_R\!\cdot(v_cq)
   +D_r\Delta_rq+D_c\Delta_Rq
   -K\!\left(C_\eta(R,r),r\right)q,                   \tag{2.7}
\]

where

\[
 u=b_1(x_1)-b_2(x_2),\qquad
 v_c=\frac{D_2b_1(x_1)+D_1b_2(x_2)}{D_r}.             \tag{2.8}
\]

**[T] Coordinate-decoupling identity.**  Equations (2.4)--(2.7) follow by a
linear change of variables with unit absolute Jacobian.  For constant drifts,
the relative and centre noises are independent.  The drifts can still couple
\(r\) and \(R\), and the transformed domain

\[
 \mathcal D=\{(R,r):R+D_1r/D_r\in\Omega_1,
                    R-D_2r/D_r\in\Omega_2\}           \tag{2.9}
\]

usually has a coupled boundary.  Independence in free space must therefore
not be promoted to independence in a bounded domain.

For the more general scalar coordinate \(C_\eta=\eta x_1+(1-\eta)x_2\),
the mixed second-order tensor is

\[
 2\{\eta D_1-(1-\eta)D_2\}\,\nabla_r\!\cdot\nabla_{C_\eta}.
\]

It vanishes if and only if \(\eta=D_2/(D_1+D_2)\).  In the
\((r,C_\eta)\) coordinates the remaining centre diffusivity is
\(D_\eta=D_1\eta^2+D_2(1-\eta)^2\); for the midpoint the mixed coefficient is
\(D_1-D_2\).  Keeping the decoupled \((r,R)\) coordinates, as in Eq. (2.7),
moves this coupling into the slanted sink support
\(C_\eta(R,r)\) instead.  With constant anisotropic diffusion tensors
\(A_1,A_2\), a scalar \(\eta\) removes mixed
diffusion if and only if

\[
 \eta A_1=(1-\eta)A_2,                                 \tag{2.10}
\]

so the tensors must be proportional.  Position-dependent diffusivities
generally reintroduce mixed and first-order terms.

## 3. Finite-radius reaction models

Point co-location is not a mesh-independent reaction prescription in physical
dimension \(d\ge2\).  The primary continuum model must use a physical reaction
radius \(a>0\).

### 3.1 Doi volume sink

Let \(C_j\) be a catalytic patch in the declared \(C_\eta\)-space, and let
\(\kappa_j(C_\eta)\ge0\) be its intrinsic volume-reaction rate.  Define

\[
 K_a^{(\eta)}(R,r)=\sum_{j=1}^m K_{a,j}^{(\eta)}(R,r),
\]

\[
 K_{a,j}^{(\eta)}(R,r)
 =\kappa_j(C_\eta(R,r))\,\mathbf 1_{C_j}(C_\eta(R,r))\,
  \mathbf 1_{\{|r|<a\}}.                              \tag{3.1}
\]

The channel-resolved density and survival are

\[
 f_j(t)=\int_{\mathcal D}K_{a,j}^{(\eta)}(R,r)q(R,r,t)\,dR\,dr,
 \qquad
 S(t)=\int_{\mathcal D}q(R,r,t)\,dR\,dr.              \tag{3.2}
\]

**[T] Mass balance.**  Under reflecting outer boundaries and sufficient
regularity,

\[
 -S'(t)=\sum_{j=1}^m f_j(t).                           \tag{3.3}
\]

This is an exact identity, not merely a discretization diagnostic.  A numerical
scheme must reproduce its discrete analogue to solver tolerance.

The bounded reflecting calculations in this report set \(\eta=1/2\) and
evaluate the support directly in the original particle coordinates.  The GIG
screening calculation sets \(\eta=D_2/D_r\), for which \(C_\eta=R\), because
that special free-space coordinate factorizes the relative and centre noises.
The Green-operator identities themselves require only a declared joint-space
sink and therefore apply to either convention; the GIG factorization is not an
identity for the midpoint sink when \(D_1\ne D_2\).

The natural Doi Damköhler number is

\[
 \mathrm{Da}_{\rm Doi}=\frac{\kappa a^2}{D_r}.         \tag{3.4}
\]

Consequently, a radius study at fixed physical reaction regime scales
\(\kappa\propto a^{-2}\); holding a per-grid-site killing probability fixed is
not a continuum comparison.

### 3.2 Radiation/Robin alternative

Alternatively, remove \(|r|<a\) and impose partial absorption on the contact
surface \(\Sigma_a=\{|r|=a\}\).  Let \(n_{\mathcal D}\) denote the outward
normal of the admissible domain \(|r|>a\), pointing into the excluded contact
ball.  The radiation law is

\[
 J_r\cdot n_{\mathcal D}
 =\sum_j\kappa_{s,j}(R,\omega)\mathbf 1_{C_j}(R)q,
 \qquad \omega=r/|r|,                                 \tag{3.5}
\]

where \(J_r=uq-D_r\nabla_rq\).  The corresponding channel flux is

\[
 f_j(t)=\int_{C_j}\int_{\mathbb S^{d-1}}
 \kappa_{s,j}(R,\omega)q(R,a\omega,t)
 a^{d-1}\,d\omega\,dR.                               \tag{3.6}
\]

The surface Damköhler number is

\[
 \mathrm{Da}_{\rm rad}=\frac{\kappa_s a}{D_r}.        \tag{3.7}
\]

Doi and radiation models are not identical at fixed bare parameters.  Their
small-target outer solutions can be matched by equating effective
reactivities; this equivalence, and its domain of validity, is developed for
generalized reaction models by Isaacson, Mauro, and Newby (2016).

## 4. Channel flux, Laplace resolvent, and reaction-support Green operator

Let \(\mathsf H=L^2(\mathcal D)\), let \(\mathcal L_0\) be the reflecting
forward generator, and write the Doi killing operator as

\[
 V=\Gamma^*\mathsf K\Gamma.                            \tag{4.1}
\]

Here \(\Gamma\) restricts a function to a declared volume-reaction support,
\(\Gamma^*\) extends by zero, and \(\mathsf K\) is a bounded nonnegative
multiplication operator on that support.  It may have a kernel; zero-rate
channels and zero-rate subsets are allowed.  The killed generator is

\[
 \mathcal T=\mathcal L_0-V.                            \tag{4.2}
\]

For \(\operatorname{Re}s\) larger than the spectral bound, define

\[
 \mathcal R_0(s)=(s-\mathcal L_0)^{-1},\qquad
 \mathcal G(s)=\Gamma\mathcal R_0(s)\Gamma^*.          \tag{4.3}
\]

The Laplace-transformed state and channel fluxes are

\[
 \widetilde q(s)=(s-\mathcal T)^{-1}q_0,
\]

\[
 \widetilde f_j(s)
 =\langle \mathbf1,\mathsf K_j\Gamma
          (s-\mathcal T)^{-1}q_0\rangle.              \tag{4.4}
\]

**[T] Inverse-free restricted-Green resolvent identity.**  Put
\(\mathsf M=I+\mathcal G\mathsf K\).  If the displayed bounded operators and
inverse exist in the stated volume-reaction spaces, then

\[
 (s-\mathcal T)^{-1}
 =\mathcal R_0
  -\mathcal R_0\Gamma^*
   \mathsf K\mathsf M^{-1}
   \Gamma\mathcal R_0.                                \tag{4.5}
\]

Equivalently, if \(u=\Gamma\mathcal R_0q_0\), the restricted transformed state
\(x\) and reaction density \(y\) are

\[
 x=\Gamma\widetilde q=\mathsf M^{-1}u,
 \qquad
 y=\mathsf Kx=\mathsf K\mathsf M^{-1}u.              \tag{4.6}
\]

No inverse of \(\mathsf K\) is required.  If \(\mathsf K\) is boundedly
invertible on the chosen support, the push-through identity gives the optional
corollary

\[
 \mathsf K(I+\mathcal G\mathsf K)^{-1}
 =(\mathsf K^{-1}+\mathcal G)^{-1}.
\]

For finitely many lattice hotspots, \(\Gamma=U^*\) and
\(\mathsf K=\operatorname{diag}(\kappa_1,\ldots,\kappa_m)\), so (4.5) reduces
to the exact finite-dimensional Woodbury formula used by the CTMC code.  For a
Robin boundary, the analogous reduction lives in trace spaces and is expressed
through boundary Green or Dirichlet-to-Neumann operators; treating the trace as
a bounded \(L^2\) restriction without qualification is not rigorous.

For a physical parameter \(\theta\),

\[
 \partial_\theta(s-\mathcal T)^{-1}
 =(s-\mathcal T)^{-1}\mathcal T_\theta
  (s-\mathcal T)^{-1},                                \tag{4.7}
\]

with additional observable terms if \(\mathsf K_j\) also depends on
\(\theta\).  Equation (4.7) supplies an exact sensitivity check against
automatic or finite differences.

For the finite fixed-space channel row \(F=\alpha RUK\),
\(R=(sI-T)^{-1}\), the complete product rule is

\[
 \partial_\theta F
 =\alpha_\theta RUK+\alpha RT_\theta RUK
  +\alpha RU_\theta K+\alpha RUK_\theta.              \tag{4.7a}
\]

At fixed initial law and fixed support, only the second and fourth terms
remain.  Moving a sharp hotspot changes \(U\) and need not define a smooth
parameter on a fixed grid; differentiating only the killed resolvent would
miss the direct observable term.

If the free reflecting generator has a zero mode, \(\mathcal R_0(s)\) diverges
as \(s\downarrow0\).  Splitting probabilities must be evaluated either by a
controlled zero-mode cancellation in (4.5) or directly from the killed solve

\[
 \pi_j=\langle\mathbf1,\mathsf K_j\Gamma
                    (-\mathcal T)^{-1}q_0\rangle.      \tag{4.8}
\]

Equation (4.8) requires the full killed live operator to be transient and
invertible.  If only the initial communicating class is transient, the solve
must instead be restricted to its reachable transient subspace (or use an
explicit Poisson/Drazin formulation).

The finite Green reference implementation is fail-closed near the reflecting
zero mode: it rejects a reconstruction when the maximum of its solve
residuals, condition-number roundoff bounds, killed-equation residual, and
optional direct discrepancy exceeds the declared \(10^{-8}\) tolerance.  It
does not silently switch methods; the direct killed solve is a separate API.

The spectral claim splits at this point.  For a finite CTMC and every
\(s\notin\sigma(L_0)\), ordinary matrix algebra gives

\[
 \det(sI-T)=\det(sI-L_0)\det[I+G(s)K].                 \tag{4.9}
\]

Thus zeros of \(\det(I+GK)\) are candidate killed poles coupled to the reactive
subspace; shared free/dark modes, numerator cancellation, and zero observable
residue must be checked separately.  Negative-half-plane evaluation is a
finite rational-resolvent statement, not a Laplace transform.  For the
continuum operator, the present result is restricted to the right-half-plane
Laplace response.  Pole/residue language outside it requires additional
Fredholm compactness and meromorphic-continuation hypotheses that are not
proved here.

**[T/N] Exact finite spectral fixture.**  The two-site/two-walker model with
co-location selectors and rates \((1/2,1/2)\) has the analytic dark vector
\(v=(0,1,-1,0)^\mathsf T\), for which
\(U^\mathsf Tv=0\) and \(L_0v=Tv=-2v\).  At the coupled killed pole
\(s_*=-5/2\notin\sigma(L_0)\),

\[
 I+G(s_*)K=\frac8{15}\begin{pmatrix}1&1\\1&1\end{pmatrix},
 \qquad r_{\rm ch}=(1/4,-1/4).
\]

The channel residues are individually nonzero and cancel in the total flux.
The accompanying finite-matrix spectral artifact checks these exact values;
it does not extend the continuum operator beyond its right-half-plane result.

## 5. Why two and three dimensions require capacity scaling

The reaction set is a tube around the diagonal \(x_1=x_2\).  Although the
configuration space has dimension \(2d\), the tube has normal dimension \(d\).
It is this codimension that selects the capacity law.

Assume first that a catalytic centre patch has \(O(1)\) physical size and is
away from corners of the transformed outer boundary.  Locally, the singular
part of the relative Green function is

\[
 G(r,r')\sim-\frac{1}{2\pi D_r}\log|r-r'|+H
 \quad(d=2),                                          \tag{5.1}
\]

\[
 G(r,r')\sim\frac{1}{4\pi D_r|r-r'|}+H
 \quad(d=3).                                          \tag{5.2}
\]

### 5.1 Two-dimensional logarithmic capacity

Let \(aK\) be a small cross-section in relative space and let
\(\operatorname{cap}_{\log}K\) denote logarithmic capacity, normalized so that
the unit disk has capacity one.  Then

\[
 \operatorname{cap}_{\log}(aK)
 =a\operatorname{cap}_{\log}K,                        \tag{5.3}
\]

but the effective conductance is inverse-logarithmic rather than proportional
to \(a\):

\[
 k_{\rm eff}^{(2)}(a)
 \simeq
 \frac{2\pi D_r}
 {\log\!\left(\ell/[a\operatorname{cap}_{\log}K]\right)
   +\beta_{\rm int}+2\pi D_r H}.                      \tag{5.4}
\]

Here \(\ell\) is a macroscopic length, \(H\) is the regular part determined by
the domain, drift, and centre location, and \(\beta_{\rm int}\) is the
intrinsic-reaction impedance.  For a circular radiation target in a circular
outer matching problem,

\[
 \beta_{\rm int}^{\rm rad}=\frac{D_r}{\kappa_s a}.
\]

For a circular Doi disk with
\(\lambda=a\sqrt{\kappa/D_r}\), the corresponding local benchmark is

\[
 \beta_{\rm int}^{\rm Doi}
 =\frac{I_0(\lambda)}{\lambda I_1(\lambda)}.           \tag{5.5}
\]

Equations (5.4)--(5.5) are matching benchmarks, not a claim that a bounded,
driven, heterogeneous encounter problem is radially symmetric.  The regular
part and stationary weight along the catalytic centre patch must be retained.

### 5.2 Three-dimensional Newtonian capacity

Use the convention

\[
 \operatorname{Cap}_{N}(B_a)=4\pi a.
\]

For a perfectly absorbing small target,

\[
 k_{\rm eff}^{(3)}(a)
 \simeq D_r\operatorname{Cap}_{N}(aK)
 =aD_r\operatorname{Cap}_{N}(K).                      \tag{5.6}
\]

For a sphere, useful infinite-space calibration formulas are

\[
 k_{\rm rad}^{(3)}
 =4\pi D_ra\frac{\mathrm{Da}_{\rm rad}}
                    {1+\mathrm{Da}_{\rm rad}},        \tag{5.7}
\]

\[
 k_{\rm Doi}^{(3)}
 =4\pi D_ra\left(1-\frac{\tanh\lambda}{\lambda}\right),
 \qquad \lambda=\sqrt{\mathrm{Da}_{\rm Doi}}.        \tag{5.8}
\]

In general \(d\ge3\), Newtonian capacity scales as \(a^{d-2}\).  In \(d=1\),
a point has non-negligible hitting behavior and no logarithmic
renormalization is needed.  If the centre patch shrinks together with the
relative radius, the entire set is small in the \(2d\)-dimensional
configuration space; then (5.4)--(5.6) cannot be applied as a purely normal
capacity law without a separate matched-asymptotic analysis.

**[C] Capacity-uniform channel limit.**  After scaling the intrinsic rate at
fixed Damköhler number, each channel flux should converge to a limit governed
by the appropriate logarithmic/Newtonian capacity and the regular part of the
restricted Green operator.  A proof must be uniform over the parameter
neighborhood used to continue the modality fold.

## 6. Geometry-to-channel GIG law

### 6.1 Free short-time derivation

For constant drifts in free space, the coordinate transform gives independent
processes

\[
 dr=u\,dt+\sqrt{2D_r}\,dW_r,
 \qquad
 dR=v_c\,dt+\sqrt{2D_c}\,dW_c.                        \tag{6.1}
\]

In the one-dimensional closing geometry, let \(\ell>0\) be the initial gap and
let \(u>0\) be the closing speed.  The relative first-contact density is

\[
 h_r(t)=\frac{\ell}{\sqrt{4\pi D_rt^3}}
 \exp\!\left[-\frac{(\ell-ut)^2}{4D_rt}\right].       \tag{6.2}
\]

The centre density at a narrow catalyst centered at \(z\in\mathbb R^d\) is

\[
 p_c(z,t)=\frac{1}{(4\pi D_ct)^{d/2}}
 \exp\!\left[-\frac{|z-R_0-v_ct|^2}{4D_ct}\right].    \tag{6.3}
\]

Multiplication, with all time-independent factors absorbed into \(A>0\), gives

\[
 g(t)=A\,t^{-p}\exp(-a/t-bt),                         \tag{6.4}
\]

\[
 p=\frac{d+3}{2},\qquad
 a=\frac{\ell^2}{4D_r}+\frac{|z-R_0|^2}{4D_c},
 \qquad
 b=\frac{u^2}{4D_r}+\frac{|v_c|^2}{4D_c}.             \tag{6.5}
\]

For the one-dimensional centre coordinate, \(p=2\), which is the early-channel
law already used in the report.  A drift-dominated effective one-dimensional
trip to a distant catalyst has \(p=3/2\), the inverse-Gaussian power.

For \(d\ge2\), (6.2) is replaced by the first-hitting flux to the finite contact
surface.  Locally, its normal short-time factor is still of
\(t^{-3/2}\exp(-a_r/t-b_rt)\) type; the total power changes according to how
many tangential and centre coordinates are localized or integrated over.
Therefore \(p=(d+3)/2\) is the narrow-centre-patch screening value, not a
universal exponent for every patch geometry.

### 6.2 Normalization and mode

For \(a>0,b>0\),

\[
 Z(a,b,p)=\int_0^\infty t^{-p}e^{-a/t-bt}\,dt
 =2\left(\frac{a}{b}\right)^{(1-p)/2}
 K_{1-p}(2\sqrt{ab}).                                 \tag{6.6}
\]

For \(b=0\) and \(p>1\),

\[
 Z(a,0,p)=a^{1-p}\Gamma(p-1).                         \tag{6.7}
\]

The normalized density \(g=Z^{-1}t^{-p}e^{-a/t-bt}\) has mode

\[
 t_{\rm mode}
 =\frac{-p+\sqrt{p^2+4ab}}{2b}
 =\frac{2a}{p+\sqrt{p^2+4ab}},\qquad b>0,             \tag{6.8}
\]

and the continuous zero-drift limit is

\[
 t_{\rm mode}=a/p.                                    \tag{6.9}
\]

**[T] GIG algebra.**  Equations (6.6)--(6.9) are exact for the stated GIG
family.

**[C] Encounter-channel asymptotics.**  For a specified patch scaling and
before reflected paths contribute, the conditional channel density should
equal (6.4) times \(1+\varepsilon(t,a,L)\), with a remainder controlled in a
window containing the predicted mode.  Reflected/image paths generally create
a sum of GIG-like contributions, not a single global GIG law.  Until a uniform
remainder is proved, the GIG result is a screening approximation.

## 7. Two-channel modality fold

Let \(g_1,g_2\) be normalized conditional channel densities and

\[
 f(t;w)=wg_1(t)+(1-w)g_2(t),\qquad 0<w<1.             \tag{7.1}
\]

A fold in the critical points of \(f\) satisfies

\[
 f_t=0,\qquad f_{tt}=0.                                \tag{7.2}
\]

Eliminating \(w\) yields

\[
 \boxed{\;g_1'g_2''-g_2'g_1''=0\;},                  \tag{7.3}
\]

\[
 \boxed{\;w_*=-\frac{g_2'}{g_1'-g_2'}\;}.            \tag{7.4}
\]

Admissibility requires \(g_1'\ne g_2'\) and \(0<w_*<1\).  For

\[
 g_i=C_it^{-p_i}e^{-a_i/t-b_it},
\]

define

\[
 A_i=(\log g_i)'=a_i/t^2-b_i-p_i/t,
\]

\[
 B_i=(\log g_i)''=-2a_i/t^3+p_i/t^2.                 \tag{7.5}
\]

Then \(g_i'=g_iA_i\), \(g_i''=g_i(A_i^2+B_i)\), and
the GIG fold equation is

\[
 A_1(A_2^2+B_2)-A_2(A_1^2+B_1)=0.                    \tag{7.6}
\]

**[T] Fixed-shape fold algebra.**  Equations (7.3)--(7.6) are exact under the
denominator and differentiability assumptions.  They locate a fold only for a
mixture whose shapes are held fixed while \(w\) varies.

For a physical parameter \(\theta\), channel weights and shapes generally vary
together.  The actual fold must therefore be solved in the full model:

\[
 f_t(t_*,\theta_*)=f_{tt}(t_*,\theta_*)=0,            \tag{7.7}
\]

with nondegeneracy

\[
 f_{ttt}(t_*,\theta_*)\ne0,
 \qquad
 f_{t\theta}(t_*,\theta_*)\ne0.                      \tag{7.8}
\]

Writing \(a_*=f_{t\theta}\), \(b_*=f_{ttt}\), the local normal form is

\[
 f_t=a_*\Delta\theta+\frac{b_*}{2}\Delta t^2
 +o(|\Delta\theta|+|\Delta t|^2).                    \tag{7.9}
\]

On the side where \(-2a_*\Delta\theta/b_*>0\),

\[
 \Delta t_\pm
 =\pm\sqrt{-\frac{2a_*}{b_*}\Delta\theta}
  +o(|\Delta\theta|^{1/2}),                           \tag{7.10}
\]

so the critical-point separation has the square-root law

\[
 t_+-t_-
 =2\sqrt{-\frac{2a_*}{b_*}\Delta\theta}
  +o(|\Delta\theta|^{1/2}).                           \tag{7.11}
\]

The associated local maximum-to-minimum prominence scales as
\(|\Delta\theta|^{3/2}\).

**[T] Generic-fold implication.**  Equations (7.9)--(7.11) follow from a
Taylor expansion plus (7.8).  What remains model-specific is proving the
existence of \((t_*,\theta_*)\), smooth parameter dependence, and the absence
of unresolved nearby critical points.

## 8. Cusp and triple-mode extension

With two physical controls \(\theta=(\theta_1,\theta_2)\), a cusp of the
critical-point equation \(F=f_t=0\) satisfies

\[
 f_t=f_{tt}=f_{ttt}=0,
 \qquad f_{tttt}\ne0,                                 \tag{8.1}
\]

and the unfolding must have rank two:

\[
 \operatorname{rank}
 \begin{pmatrix}
 f_{t\theta_1}&f_{t\theta_2}\\
 f_{tt\theta_1}&f_{tt\theta_2}
 \end{pmatrix}=2.                                     \tag{8.2}
\]

After smooth coordinate changes, the derivative has the cusp form

\[
 F(x;\mu_1,\mu_2)=x^3+\mu_1x+\mu_2+\text{higher order}. \tag{8.3}
\]

The discriminant \(4\mu_1^3+27\mu_2^2=0\) gives the two fold branches.

For three normalized channels,

\[
 f=\sum_{i=1}^3w_i g_i,\qquad w_i>0,\quad \sum_iw_i=1, \tag{8.4}
\]

a candidate double stationary point requires a positive simplex solution of

\[
 \begin{pmatrix}
 1&1&1\\ g_1'&g_2'&g_3'\\ g_1''&g_2''&g_3''
 \end{pmatrix}
 \begin{pmatrix}w_1\\w_2\\w_3\end{pmatrix}
 =\begin{pmatrix}1\\0\\0\end{pmatrix}.             \tag{8.5}
\]

Equation (8.5) enforces only \(f_t=f_{tt}=0\).  It is a nondegenerate fold
only after separately checking

\[
 \sum_iw_i g_i'''(t_*)\ne0,
 \qquad f_{t\theta}(t_*,\theta_*)\ne0.              \tag{8.5a}
\]

Here \(\theta\) is a declared one-dimensional unfolding direction.  The
distinction is logical, not cosmetic: the invertible jet matrix with
\(g'=(1,-1,0)\), \(g''=(1,0,-1)\), and
\(w=(1/3,1/3,1/3)\) solves (8.5), while choosing all three third derivatives
zero gives \(f_{ttt}=0\) and therefore no generic fold.  Positivity and
invertibility of the simplex system do not imply catastrophe nondegeneracy.

A cusp additionally imposes \(\sum_iw_i g_i'''=0\), together with (8.1)--(8.2).

A cusp alone does **not** prove trimodality.  It changes the number of local
critical points by two.  A genuinely triple-modal density must have at least
five simple positive-time critical points with alternating maximum/minimum
signs, or it must combine the cusp-created pair with a remote maximum/minimum
pair that persists.  Existence of at least three resolved modes requires five
certified alternating simple roots, positive prominence margins, and tail
control.  Only a theorem asserting the exact global root or mode count also
requires interval-exhaustive isolation on \((0,\infty)\); the finite M2D-T
certificate below deliberately withholds that stronger claim.

**[N] Constructive multi-channel screening.**  The explicit construction in
`notes/multid_gig_channel_design.md` chooses isolated modes
\(m_j\in\{1,10,100,1000\}\), sets \(a_j=bm_j^2+pm_j\), and balances isolated
peak heights with \(w_j\propto g_j(m_j)^{-1}\).  Analytic-derivative root
isolation finds two, three, and four resolved modes for every tested
\(d=1,2,3,4\).  This establishes a constructive GIG screening family, not a
finite-radius bounded-domain trimodal region.

**[N] Physical three-channel finite-grid certificate.**  The separate M2D-T
family in `notes/finite_radius_2d_trimodality.md` has five detected
sign-changing simple derivative roots of alternating type and three
channel-attributed maxima on four bounded
finite-radius midpoint-CTMC grids. The classifier resolves the three maxima on
the three finer grids and calls the coarsest a shoulder. This verifies strict
multi-clock structure in all four declared finite models and resolved
trimodality in three. A cell-averaged continuum trimodal region, continuation of its
two bounding folds, and a genuine centre-patterned cusp remain research
targets; they are not consequences of either the finite-grid certificate or
the free-space GIG construction.

## 8A. Finite spectral necessity and its no-go boundaries

For a finite killed model with a real diagonalizable spectral expansion,
group repeated decay rates and remove zero residues:

\[
 f(t)=\sum_{j=1}^n a_j e^{-\lambda_jt},
 \qquad 0<\lambda_1<\cdots<\lambda_n.                 \tag{8A.1}
\]

Reversibility is a sufficient condition because detailed balance makes the
killed generator similar to a symmetric matrix. Applying the classical
generalized Descartes rule to

\[
 f'(t)=-\sum_j\lambda_j a_j e^{-\lambda_jt}           \tag{8A.2}
\]

after setting (x=e^{-t}) yields:

**[T] Spectral sign-variation corollary.** The number of positive-time zeros
of (f'), counted with multiplicity, is at most the number (V(a)) of sign
changes in the ordered residue sequence. Hence (m) nondegenerate interior
modes require (V(a)\ge2m-1).

This is a classical necessary corollary, not a new theorem and not a
sufficient condition. The exact counterexample

\[
 4e^{-t}-12e^{-2t}+12e^{-3t}-4e^{-4t}
 =4e^{-t}(1-e^{-t})^3                              \tag{8A.3}
\]

has three sign changes but one positive critical point. Nor can patch count,
channel labels, or killing rank bound the number of modes: two separated
12-stage Erlang transport branches can feed one rapidly killed state and
produce a maximum--minimum--maximum pattern. Nonreversible complex spectra,
Jordan terms, and continuum infinite expansions are outside (8A.1) unless
their additional hypotheses are proved.

## 8B. Fixed-budget modality susceptibility and inverse design

For a finite row generator (T(k)=L-\operatorname{diag}k) and
(f(t;k)=\alpha e^{T(k)t}k), let (k_\epsilon=k+\epsilon h) and
(H=-\operatorname{diag}h). Duhamel differentiation gives the exact identity

\[
 D_k f_t[h]
 =\alpha D e^{Tt}[H]Tk+\alpha e^{Tt}(Hk+Th),          \tag{8B.1}
\]

\[
 D e^{Tt}[H]=\int_0^t e^{T(t-s)}H e^{Ts}\,ds.        \tag{8B.2}
\]

Writing (D_kf_t[h]=g^Th), the componentwise gradient is

\[
 g_i=(\alpha e^{Tt}T)_i-k_i(\alpha e^{Tt})_i
 -\int_0^t(\alpha e^{T(t-s)})_i(e^{Ts}Tk)_i\,ds.     \tag{8B.3}
\]

For budget (c^Th=0) and norm (h^TMh=1), define

\[
 \lambda_B=\frac{c^TM^{-1}g}{c^TM^{-1}c},\qquad
 \widetilde g=g-\lambda_Bc.                          \tag{8B.4}
\]

**[T] Local fixed-budget optimum.** If \(\widetilde g\ne0\), the maximizing
infinitesimal redistribution is

\[
 h_*=\frac{M^{-1}\widetilde g}
 {\sqrt{\widetilde g^TM^{-1}\widetilde g}},          \tag{8B.5}
\]

and the maximum response is
(\sqrt{\widetilde g^TM^{-1}\widetilde g}). At a double stationary point,
this projected gradient is the fixed-budget fold-transversality test. For a
two-control cusp, the projected (f_t) and (f_{tt}) gradients must be
linearly independent on the budget tangent space.

The continuum analogue follows formally for bounded multiplication
perturbations of a positive analytic semigroup. Sharp moving masks are not
operator-norm smooth, and zero baseline rates, positivity, box constraints,
binary supports, and finite-amplitude geometry require constrained or shape
optimization. Equation (8B.5) is therefore an exact local finite-state design
result, not a continuum global optimum.

## 9. A general large-separation route to bimodality

The abstract explanation should be stated independently of one geometry.  Let

\[
 f_L=w_{E,L}g_{E,L}+w_{B,L}g_{B,L}+\varepsilon_L,      \tag{9.1}
\]

where \(E\) and \(B\) denote early and late channels.  A proof-ready
two-channel persistence proposition can assume:

1. \(w_{E,L}\to w_E\in(0,1)\) and \(w_{B,L}\to w_B\in(0,1)\);
2. \(g_{E,L}\to g_E\) in \(C^2\) near a nondegenerate \(O(1)\) maximum;
3. after centering by \(m_L=O(L)\) and scaling by
   \(\sigma_L=O(\sqrt L)\), the late channel converges in \(C^2\) to a
   density with a nondegenerate maximum;
4. each channel and \(\varepsilon_L\), together with their first two
   derivatives, are smaller than explicit derivative-sign margins in the
   other channel's peak neighborhood and in a separating interval.

**[T] Conditional two-mode persistence.**  Under these assumptions, the
intermediate value theorem and stability of nondegenerate critical points give
two local maxima and at least one intervening local minimum for all sufficiently
large \(L\).

**[C] Model-specific obligation.**  The paper must derive assumptions 1--4
from the encounter generator, Green operator, and GIG/capacity asymptotics.
Peak separation alone is insufficient.  The proof needs channel weights,
widths, heights, cross-channel derivative bounds, and a controlled remainder.
Mathematical bimodality should also be distinguished from observational
resolution: a local maximum may persist while its height becomes negligible.

The (C^2) hypotheses above preserve already simple critical points. They do
not transfer a nondegenerate fold. For
(H=(f_t,f_{tt})), a generic fold has

\[
 \det D_{(t,\theta)}H=-f_{t\theta}f_{ttt}\ne0.        \tag{9.2}
\]

Thus a unique nearby nondegenerate fold follows, for example, from joint local
(C^3) convergence of (f_h(t,\theta)). More minimally, the implicit-function
argument needs (C^1) convergence of (H_h), including the specific time and
parameter derivatives entering its Jacobian; the two statements are not
equivalent. Mere (C^2) density convergence is insufficient: (f=\theta
t+t^3/3) and
(f_n=f+2n^{-3}\sin(nt)) satisfy (f_n\to f) in (C^2), but the nearby
double stationary point ((0,-2/n^2)) of every (f_n) has
(f_{n,ttt}=0). Model-specific continuum work must therefore control the
first three time derivatives and parameter Duhamel derivatives uniformly near
the fold.

## 10. Separating boundary transport from patterned reactivity

Several known mechanisms can produce multiple first-passage time scales.  The
paper must identify which part is transport and which part is reaction
selection.

| Mechanism | What prior work already establishes | Required control | Allowed conclusion |
|---|---|---|---|
| Direct versus reflected/boundary exploration | Confinement can strongly reshape encounter/FPT densities and create separated clocks | Move the far catalyst from the wall to the interior; compare reflecting, periodic, and enlarged domains | The boundary supplies or shifts a transport clock |
| Spatial disorder in hopping rates | Disorder can itself produce bimodal FPT densities | Keep motion fixed and homogenize reactivity | Any remaining bimodality is transport/disorder driven |
| Heterogeneous surface or patch reactivity | Position-dependent Robin reactivity and patch-interaction matrices are established | Keep transport fixed; compare patterned, homogeneous, single-patch, and co-located-patch reactions | In the declared finite matched families, patterning changes channel selection and can cross the operational resolved-modality boundary; a continuum boundary remains a theorem target |
| Multiple lattice targets/defects | Exact defect/Green reductions and multiple FPT peaks are established | Compare full product generator with the same transport and reaction channels removed one at a time | The new result is not the reduction method or the existence of peaks |

The decisive numerical design is a factorial ablation:

1. boundary transport + patterned reactivity;
2. boundary transport + homogeneous reactivity;
3. interior transport clock + patterned reactivity;
4. interior transport clock + homogeneous reactivity.

Channel-resolved fluxes, splitting probabilities, and numerically located
folds from finite-matrix semigroup derivative evaluations must be reported for
all four, not only total-density plots.  If bimodality
persists with an interior far patch, the claim can emphasize heterogeneous
reaction-channel selection beyond a boundary artifact.  If it requires the
wall, the honest claim is an interaction between boundary-generated transport
and patterned reactivity.

## 11. Theorem, conjecture, and numerical-evidence ledger

### 11.1 Theorem/identity layer

The following can be stated as exact results once their hypotheses are written
in the manuscript.

1. Relative/centre coordinate transform and mixed-diffusion cancellation,
   (2.4)--(2.10).
2. Doi and Robin channel mass balance, (3.3) and (3.6).
3. Reaction-support resolvent reduction and sensitivities, (4.5)--(4.8).
4. Standard logarithmic/Newtonian capacity laws under the stated small-target
   hypotheses, with literature attribution rather than novelty language.
5. GIG normalization and mode, (6.6)--(6.9).
6. Two-channel fold elimination and algebraic weight formula with a separate
   explicit \(0<w<1\) admissibility gate, generic-fold square-root law, and
   cusp rank conditions, Sections 7--8.
7. Abstract two-mode persistence under explicit derivative-dominance
   assumptions, Section 9.
8. Classical spectral sign-variation corollary for finite real-diagonalizable
   killed models, with explicit non-sufficiency and rank-one counterexamples,
   Section 8A.
9. Finite-state Fréchet--Duhamel modality gradient and its fixed-budget local
   optimizer, Section 8B.
10. Nondegenerate fold persistence under joint local (C^3) convergence, and
    the explicit counterexample showing density (C^2) convergence is
    insufficient, Section 9.

### 11.2 Conjecture/theorem-target layer

1. A uniform GIG approximation for each encounter channel in a mode-containing
   time window.
2. A capacity-renormalized two-dimensional limit uniform near the physical
   fold.
3. Verification of the large-separation derivative-dominance assumptions for
   the canonical driven encounter family.
4. Persistence and location of the physical fold under grid refinement and
   Doi--Robin matching.
5. Existence of a robust three-channel cusp/trimodal region.
6. Operator-norm/shape-differentiable continuum modality susceptibility with
   positivity and finite-amplitude patch constraints.
7. Joint (C^3) convergence of a cell-averaged Doi/Robin family and its
   budget-projected control derivative near the fold.

### 11.3 Current numerical-evidence layer

The repository currently has distinct numerical artifacts for these claims:

- the finite-state CTMC/GIG fold calculation in
  `artifacts/data/gig_fold_summary.json` and its continuation tables;
- the exact finite-state modality-gradient cross-checks and projected optimum
  in `artifacts/data/modality_susceptibility_summary.json` and
  `modality_susceptibility_directions.csv`;
- full production-model reversible spectral decompositions, coefficient
  threshold sweeps, the hypoexponential non-sufficiency example, and the
  rank-one bimodal counterexample in
  `artifacts/data/spectral_modality_summary.json` and
  `spectral_modality_coefficients.csv`;
- the four-grid M2D-C separated-boundary branch in
  `artifacts/data/finite_radius_2d_metrics.json`; all four declared grids are
  classified bimodal, but the `9x5` tail misses its strict certification gate
  and is retained as conditional rather than promoted to verified. Its `11x7`
  curve is reused by the control artifact and is not independent evidence;
- the remaining M2D-C mechanism, interior-patch, homogeneous, and boundary controls in
  `artifacts/data/finite_radius_2d_control_metrics.json` and
  `finite_radius_2d_interior_metrics.json`;
- the M2D-F fixed-budget continuation in
  `artifacts/data/finite_radius_2d_fold_metrics.json`: homogeneous and
  patterned endpoints are respectively resolved-unimodal and
  resolved-bimodal on all five endpoint grids, while three odd grids have
  nondegenerate local folds and the expected `1/2` and `3/2` exponents. The
  state-count critical controls span `0.261563`; product-control-volume
  controls span `0.383672`. Their nonmonotonicity and budget sensitivity rule
  out a converged or budget-independent continuum critical value;
- the M2D-E exact within-grid integrated-killing-budget comparison, in which patterned reactivity
  is resolved-bimodal on four finer grids and a shoulder on the coarsest while
  its matched homogeneous control is resolved-unimodal on all five grids;
  detected sign changes Brent-refined with finite-matrix semigroup derivative
  evaluations on the declared windows retain secondary maxima in both classes, in
  `artifacts/data/finite_radius_2d_matched_control.json`;

  For this midpoint-coordinate family, the exact unit-square contact-tube
  volume at finite radius is
  
  \[
  V_T(a)=\int_{|r|\le a}(1-|r_x|)(1-|r_y|)\,dr
  =\pi a^2-\frac83a^3+\frac12a^4.
  \]
  
  When every catalyst disk has boundary clearance at least (a/2), the
  continuum Lebesgue-volume counterpart of the discrete state-sum match gives
  
  \[
  \bar\kappa_h(a)=
  \frac{\pi a^2[\pi\sum_j\kappa_j\rho_j^2]}{V_T(a)}.
  \]
  
  At (a=0.13) this is (2.169402271). Independent mask-count refinements
  (25\times19,49\times37,81\times61,161\times121) give respectively
  (1.95858,2.06542,2.09023,2.13269), approaching that finite-radius
  reference. The five dynamics grids are therefore an exact within-grid
  counterfactual, not a converged continuum budget calculation;
- the M2D-T bounded three-patch certificate, including five detected
  sign-changing roots
  Brent-refined with finite-matrix semigroup derivative evaluations on the
  declared horizon for each of four grids, resolved trimodality on the
  three finer grids, a coarse three-maximum shoulder, channel attribution, and
  a (t=2000) tail audit, in
  `artifacts/data/finite_radius_2d_trimodal_metrics.json` and
  `finite_radius_2d_trimodal_roots.csv`;
- radius/capacity diagnostics in
  `artifacts/data/finite_radius_2d_capacity_metrics.json`;
- the exact translation-invariant three-dimensional relative-coordinate
  quotient, matrix-free grid convergence, Doi effective-radius slope, and
  fixed-rate reaction-volume limit in
  `artifacts/data/finite_radius_3d_capacity_metrics.json`.

These artifacts establish finite-model behavior only.  They must not be cited
as proof of the continuum conjectures until convergence rates, fixed physical
dimensionless parameters, and Doi--Robin matching are completed.

## 12. Prior-art anchors and exact DOI list

The references below define the novelty boundary.  They should be cited for
what they establish, not presented as incidental background.

1. F. Le Vot, S. B. Yuste, E. Abad, and D. S. Grebenkov, *First-encounter
   time of two diffusing particles in confinement*, Phys. Rev. E **102**,
   032118 (2020), [doi:10.1103/PhysRevE.102.032118](https://doi.org/10.1103/PhysRevE.102.032118).
   This supplies full one-dimensional confined encounter-time laws.
2. F. Le Vot, S. B. Yuste, E. Abad, and D. S. Grebenkov, *First-encounter
   time of two diffusing particles in two- and three-dimensional confinement*,
   Phys. Rev. E **105**, 044119 (2022),
   [doi:10.1103/PhysRevE.105.044119](https://doi.org/10.1103/PhysRevE.105.044119).
   This blocks any novelty claim based only on studying the full encounter
   distribution in higher-dimensional confinement.
3. L. Giuggioli, S. Pérez-Becker, and D. P. Sanders, *Encounter times in
   overlapping domains: application to epidemic spread in a population of
   territorial animals*, Phys. Rev. Lett. **110**, 058103 (2013),
   [doi:10.1103/PhysRevLett.110.058103](https://doi.org/10.1103/PhysRevLett.110.058103).
4. L. Giuggioli, *Exact spatiotemporal dynamics of confined lattice random
   walks in arbitrary dimensions: a century after Smoluchowski and Pólya*,
   Phys. Rev. X **10**, 021045 (2020),
   [doi:10.1103/PhysRevX.10.021045](https://doi.org/10.1103/PhysRevX.10.021045).
5. L. Giuggioli and S. Sarvaharman, *Spatio-temporal dynamics of random
   transmission events: from information sharing to epidemic spread*,
   J. Phys. A **55**, 375005 (2022),
   [doi:10.1088/1751-8121/ac8587](https://doi.org/10.1088/1751-8121/ac8587).
   This is especially close prior art because it treats heterogeneous reactive
   locations, splitting probabilities, and transmission efficiency.
6. S. Sarvaharman and L. Giuggioli, *Particle-environment interactions in
   arbitrary dimensions: a unifying analytic framework to model diffusion
   with inert spatial heterogeneities*, Phys. Rev. Research **5**, 043281
   (2023),
   [doi:10.1103/PhysRevResearch.5.043281](https://doi.org/10.1103/PhysRevResearch.5.043281).
7. L. Giuggioli, S. Sarvaharman, D. Das, D. Marris, and T. Kay,
   *Multi-target search in bounded and heterogeneous environments: a lattice
   random walk perspective*, in *Target Search Problems* (2024),
   [doi:10.1007/978-3-031-67802-8_5](https://doi.org/10.1007/978-3-031-67802-8_5).
   It includes lattice radiation boundaries, multi-target formulas, and an
   example of multiple first-passage peaks.
8. D. S. Grebenkov, *Spectral theory of imperfect diffusion-controlled
   reactions on heterogeneous catalytic surfaces*, J. Chem. Phys. **151**,
   104108 (2019),
   [doi:10.1063/1.5115030](https://doi.org/10.1063/1.5115030).
   This establishes spectral/operator treatment of heterogeneous Robin
   reactivity.
9. D. S. Grebenkov and M. J. Ward, *The effective reactivity for capturing
   Brownian motion by partially reactive patches on a spherical surface*,
   Multiscale Model. Simul. **24**, 660--692 (2026),
   [doi:10.1137/25M180562X](https://doi.org/10.1137/25M180562X).
   This is a direct benchmark for patch capacity, interaction Green matrices,
   and effective reactivity.
10. J. Holehouse and S. Redner, *First passage on disordered intervals*,
    Phys. Rev. E **109**, L032102 (2024),
    [doi:10.1103/PhysRevE.109.L032102](https://doi.org/10.1103/PhysRevE.109.L032102).
    It explicitly demonstrates disorder-induced bimodal first-passage
    distributions.
11. T. Guérin, M. Dolgushev, O. Bénichou, and R. Voituriez, *Universal
    kinetics of imperfect reactions in confinement*, Commun. Chem. **4**, 157
    (2021),
    [doi:10.1038/s42004-021-00591-2](https://doi.org/10.1038/s42004-021-00591-2).
12. A. Godec and R. Metzler, *Universal proximity effect in target search
    kinetics in the few-encounter limit*, Phys. Rev. X **6**, 041037 (2016),
    [doi:10.1103/PhysRevX.6.041037](https://doi.org/10.1103/PhysRevX.6.041037).
13. A. Godec and R. Metzler, *First passage time statistics for two-channel
    diffusion*, J. Phys. A **50**, 084001 (2017),
    [doi:10.1088/1751-8121/aa5204](https://doi.org/10.1088/1751-8121/aa5204).
    These two papers establish direct/indirect time-scale separation and
    explicit two-channel first-passage theory.
14. M. Doi, *Stochastic theory of diffusion-controlled reaction*, J. Phys. A
    **9**, 1479--1495 (1976),
    [doi:10.1088/0305-4470/9/9/009](https://doi.org/10.1088/0305-4470/9/9/009).
15. S. A. Isaacson, *A convergent reaction-diffusion master equation*,
    J. Chem. Phys. **139**, 054101 (2013),
    [doi:10.1063/1.4816377](https://doi.org/10.1063/1.4816377).
16. S. A. Isaacson, A. J. Mauro, and J. Newby, *Uniform asymptotic
    approximation of diffusion to a small target: generalized reaction
    models*, Phys. Rev. E **94**, 042414 (2016),
    [doi:10.1103/PhysRevE.94.042414](https://doi.org/10.1103/PhysRevE.94.042414).
    These references support the Doi volume model, convergent discretization,
    and calibrated Doi--radiation comparison.

## 13. Derivation checkpoints and Lean/numerical bridges

| ID | Analytical checkpoint | Lean bridge | Numerical bridge / falsifier |
|---|---|---|---|
| D1 | Re-derive (2.4)--(2.10), including Jacobian, drift signs, and transformed no-flux boundary | Linear-algebra identity for scalar diffusivities; state clearly that PDE boundary regularity is outside the current formalization | Compare transformed and product-space generators entry by entry; covariance Monte Carlo for free motion |
| D2 | Prove Doi and Robin mass balance with channel decomposition | Finite-matrix row-sum/killing identity | At every stored time verify `sum(channel flux) = total flux = -dS/dt`; verify integrated mass plus tail |
| D3 | Establish the operator domains for (4.5), separately for volume and trace reactions | Finite-dimensional Woodbury and explicit \(2\times2\) inverse/determinant | Full resolvent versus restricted Green solve over complex \(s\), including derivatives, \(s\downarrow0\), dark modes, and numerator cancellation |
| D4 | Derive 2D matched asymptotics with log capacity and domain regular part; derive 3D capacity coefficient | Only elementary scaling identities unless functional analysis is separately formalized | Fixed \(\mathrm{Da}\), fixed physical geometry, at least four grids/radii; fit against \(1/[\log(\ell/a)+\beta]\) in 2D and \(a\) in 3D; reject fixed per-site killing comparisons |
| D5 | Match Doi and radiation intrinsic impedances at equal effective reactivity | Algebraic matching formula | Independent Doi-volume and Robin-boundary solvers; compare flux curves, splitting weights, fold location, and convergence with \(a\) |
| D6 | Derive the GIG action \(a\), drift penalty \(b\), power \(p\), and patch-width correction; obtain a mode-window remainder | GIG mode solves \(bt^2+pt-a=0\); positivity and zero-drift limit | Finite-matrix CTMC and independently discretized PDE channels versus predictions over distance, drift, dimension, and patch width; measure relative errors in mode, width, weight, and derivatives, not only peak location |
| D7 | Prove fixed-shape fold elimination and physical-fold normal form | Determinant/weight theorem; truncated normal-form roots and square-root separation | Locate a fold candidate with finite-matrix semigroup/resolvent derivative evaluations; pseudo-arclength continuation; held-out points on both sides; \(1/2\) separation and \(3/2\) prominence slopes |
| D8 | Establish smooth parameter dependence and exclude extra nearby critical points | Finite exponential-mixture derivative identities | Interval/root isolation for all critical points; time-horizon and tail certificates; precision and conditioning sweeps |
| D9 | Derive cusp conditions (8.1)--(8.3) and simplex candidate equation (8.5) | Polynomial cusp normal form; simplex positivity plus separate third-derivative and unfolding-transversality gates | Two-parameter continuation of fold curves; compute cusp rank and fourth derivative; interval-certified five-critical-point test before any global trimodal claim |
| D10 | Prove the abstract large-separation persistence proposition and then verify its hypotheses for the encounter model | Sign-preservation lemma on compact intervals may be formalized; continuum asymptotics remain outside scope | Fixed-local-geometry size family; channel \(C^2\) convergence, weights, widths, cross-channel derivatives, valley and peak-height scaling |
| D11 | Separate boundary clock from reaction pattern using the factorial design in Section 10 | Not a Lean obligation | Boundary/interior, patterned/homogeneous, one-patch/co-located, zero/reversed drift, equal/reversed mobility controls with identical classifier and tail rules |
| D12 | State an explicit theorem-coverage table in the manuscript | `lake build`, axiom report, and exact source-to-claim mapping | Never label a floating-point result as Lean verified; preserve hashes, tolerances, versions, and commands for every artifact |

The paper is analytically ready only when each [C] item used in a headline claim
has either been promoted to [T] with a proof and explicit assumptions or
retained as a clearly labelled numerical/conjectural statement.  A successful
Lean build verifies only the formalized algebraic implications; it does not
verify the PDE model, asymptotic remainder, numerical continuation, or
continuum convergence unless those objects are separately formalized.
