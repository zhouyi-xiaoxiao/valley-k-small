# Mixed Neumann--periodic sector regularity and positive-time contour bound

Date: 2026-07-17

Status: **ROUND-11 IDEAL FIXED-BOX ANALYTICAL CLOSURE / COMPLEX CONVENTION
ERRATUM APPLIED / TWO INDEPENDENT PROOF AUDITS COMPLETE / NEUTRAL FIXTURE
1482/1482 PASS / SOURCE-BOUND RESIDUAL COMPOSITION OPEN / COMPLETE C2 FALSE**

## 0. Purpose and nonclaim boundary

Round 10 proved the one-sided free Scharfetter--Gummel residual for the ideal
analytic refinement family.  The remaining analytical premise selected there
was a mixed Neumann--periodic complex-sector `H2` estimate, with enough
spectral-parameter control to make the positive-time Dunford integral
explicit.

This note proves that ideal fixed-box premise and separates it from the
source-binding obligations that are still open.  The key observation is that
the physical sharp contact field is a bounded zero-order multiplier.  It
changes neither the operator domain nor the mixed-boundary `H2` regularity.
No derivative of the contact indicator is taken.

The note does **not** prove:

- the source-bound map and cut-layer constants in the Round-9 killing
  residual;
- containment of the ideal member by a production interval member;
- a complete reconstructed-resolvent rate for the physical source family;
- C2, C3, root transfer, F0--F3, positive-budget science, release, or
  submission eligibility.

The quantitative resolvent and positive-time estimates in Sections 7--8 are
therefore conditional compositions.  They identify the exact remaining
inputs and show that no additional complex-sector or contour-growth
obstruction is hidden after those inputs are supplied.

The scope is physical `d=2`, so the quotient box has dimension three.  This
restriction is essential when the killing residual uses
`H2(Omega_L) -> L-infinity(Omega_L)`.  No dimension-uniform claim is made.

## 1. Complex convention erratum for Round 10

The authoritative convention in
`notes/continuum_research_program_v2.md` is

\[
 \langle u,v\rangle_H=\int_{\Omega_L}\overline u\,v\,\pi\,dx,
 \qquad
 \mathfrak a(u,v)=
 \int_{\Omega_L}(\nabla\overline u)^T\mathbf D\nabla v\,\pi\,dx.
 \tag{1.1}
\]

Thus the **first** factor is conjugated.  The frozen Round-10 note instead
contains one sentence saying that the second factor is conjugated and writes
the corresponding conjugated residual display.  Those frozen bytes are
retained because their mathematical estimates and neutral fixture concern
absolute values and real probes.  Under the authoritative convention, the
correct face identity is

\[
 R_{h,\mathrm{free}}(u;v_h)
 =\sum_e\overline{E_e(u)}(v_{e,+}-v_{e,-}),
 \tag{1.2}
\]

not `sum E_e(u) conjugate(v_+-v_-)`.  The two expressions are complex
conjugates.  Consequently every Cauchy--Schwarz bound, every real numerical
row, the vertex constant-mode obstruction, and the `O(h)`/`O(sqrt(h))`
orders in Round 10 remain unchanged.  All complex arguments below use
Eq. (1.1).

This is a convention erratum, not a new acceptance claim for Round 10.

## 2. Fixed-box operator

Let

\[
 \Omega_L=I_z\times I_\parallel\times\mathbb T_W,
 \qquad
 \mathbf D=\operatorname{diag}(D/2,2D,2D),
 \qquad D>0.
 \tag{2.1}
\]

On this fixed box, use the restriction of the globally normalized reversible
density

\[
 \pi(z,r,y)=Z^{-1}
 \exp\!\left[
  -\frac{\gamma(z-\bar z)^2}{D}
  -\frac{\gamma r^2}{4D}\right],
 \qquad Z=\frac{2\pi DW}{\gamma}.
 \tag{2.2}
\]

It is not renormalized to unit mass on the artificial box:

\[
 M_L:=\int_{\Omega_L}\pi\,dx<1
 \tag{2.2a}
\]

for every finite strict truncation of the two Gaussian axes.  This convention
is required to compare the same continuum member, map, and global gauge used
by C0/C1.  Renormalizing on the box would replace `pi` by `pi/M_L`,
equivalently `Z` by `Z_L=Z M_L`; no such rescaling is made.  That would define
a different finite-box Hilbert normalization.  On the fixed box there are
positive finite constants

\[
 0<\pi_-\le\pi\le\pi_+<\infty,
 \qquad
 \pi\in W^{2,\infty}(\Omega_L).
 \tag{2.3}
\]

Work in the complexification

\[
 H_L=L^2(\Omega_L,\pi\,dx)
 \tag{2.4}
\]

with Eq. (1.1).  Let

\[
 \mathcal V_L=
 \{u\in H^1(\Omega_L):
   u\text{ is periodic in }y\},
 \tag{2.5}
\]

where periodicity is understood in the trace sense.  Define the free form

\[
 \mathfrak a_0(u,v)=
 \int_{\Omega_L}
  (\nabla\overline u)^T\mathbf D\nabla v\,\pi\,dx
 \tag{2.6}
\]

on `V_L`, and let `H_0>=0` be its associated self-adjoint operator.

For a real simplex control `c`, set

\[
 V_c(z,r,y)=W^{-1}\chi_D(r,y)
 \sum_{j=1}^4w_j^{(c)}\phi_j(z),
 \qquad
 w_j^{(c)}\ge0,\quad \sum_jw_j^{(c)}=1.
 \tag{2.7}
\]

The patches are bounded and nonnegative, and the contact indicator is sharp.
Hence

\[
 0\le V_c\le V_*,
 \qquad
 V_*:=W^{-1}\max_j\|\phi_j\|_\infty,
 \tag{2.8}
\]

uniformly over the complete real simplex.  For a fixed budget `B>=0`, put

\[
 K_c=BV_c,\qquad K_*:=BV_*,
 \qquad H_c=H_0+M_{K_c}.
 \tag{2.9}
\]

All constants below may depend on the fixed box, `D`, `gamma`, `pi_-/pi_+`,
`B`, and `V_*`, but not on `c`, the mesh, the declared alignment, or the
complex spectral parameter.

## 3. Mixed-boundary `H2` graph domain

Define

\[
 H^2_{\mathrm{NP}}(\Omega_L)=
 \left\{
 \begin{array}{l}
 u\in H^2(\Omega_L):\
 \partial_z u=0\text{ on }\partial I_z,\
 \partial_r u=0\text{ on }\partial I_\parallel,\\
 u\text{ and }\partial_yu\text{ have matching periodic traces}
 \end{array}
 \right\}.
 \tag{3.1}
\]

Because the density and diagonal diffusion are strictly positive, the two
Neumann conditions in Eq. (3.1) are equivalent to the conormal conditions
`pi D grad(u) dot n=0`.

### Proposition 3.1 (free graph domain)

The free form operator satisfies

\[
 D(H_0)=H^2_{\mathrm{NP}}(\Omega_L)
 \tag{3.2}
\]

and there is a finite fixed-box constant `C_NP` such that

\[
 \|u\|_{H^2(\Omega_L)}
 \le C_{\mathrm{NP}}
 \{\|H_0u\|_{H_L}+\|u\|_{H_L}\},
 \qquad u\in D(H_0).
 \tag{3.3}
\]

#### Proof

In algebraic form,

\[
 H_0u=
 -\pi^{-1}\nabla\!\cdot(\pi\mathbf D\nabla u)
 =-\operatorname{tr}(\mathbf D\nabla^2u)
   -(\mathbf D\nabla\log\pi)\!\cdot\nabla u.
 \tag{3.4}
\]

First consider

\[
 L_{\mathbf D}=-\operatorname{tr}(\mathbf D\nabla^2)
 \tag{3.5}
\]

with the boundary conditions in Eq. (3.1).  Cosines on each reflected
interval and complex exponentials on the torus form a complete orthogonal
basis.  Mode by mode,

\[
 1+|\xi|^4
 \le C_{\mathbf D,L}
 \{1+(\xi^T\mathbf D\xi)^2\}.
 \tag{3.6}
\]

Parseval therefore gives

\[
 \|u\|_{H^2}
 \le C_{\mathbf D,L}
 \{\|L_{\mathbf D}u\|_2+\|u\|_2\},
 \qquad
 D(L_{\mathbf D})=H^2_{\mathrm{NP}}(\Omega_L).
 \tag{3.7}
\]

The weighted and unweighted `L2` norms are equivalent by Eq. (2.3).  The
first-order coefficient

\[
 b_0=\mathbf D\nabla\log\pi
 \tag{3.8}
\]

is bounded on the fixed box.  The same mixed Fourier basis and scalar
Young inequality give, for every `epsilon>0`,

\[
 \|\nabla u\|_2
 \le\epsilon\|u\|_{H^2}
     +C_{\epsilon,L}\|u\|_2.
 \tag{3.9}
\]

Equations (3.4), (3.7), and (3.9), with `epsilon` small enough to absorb the
gradient term, prove Eq. (3.3) on `H2_NP`.  They also show that
`b_0 dot grad` is `L_D`-bounded with relative bound zero.

For completeness, take `u in D(H_0)` and put `f=H_0u in H_L`.  The weak form
gives, in distributions,

\[
 L_{\mathbf D}u=f+b_0\!\cdot\nabla u\in L^2(\Omega_L),
 \tag{3.10}
\]

together with the weak conormal conditions on the two interval factors and
the periodic trace condition.  The rectangular Neumann--periodic `L2`
regularity represented by the same cosine/Fourier basis then gives
`u in H2_NP`.  Conversely, every `u in H2_NP` satisfies the weak boundary
conditions, and integration by parts puts it in `D(H_0)` with action
Eq. (3.4).  The absorption estimate above proves the graph bound on this
domain.  This proves Eqs. (3.2)--(3.3).  \(\square\)

The rectangular geometry matters here.  No claim is made for an arbitrary
nonconvex or nonsmooth domain with mixed boundary junctions.

## 4. Sharp bounded killing does not reduce regularity

### Proposition 4.1 (bounded-perturbation domain)

For every declared real control,

\[
 D(H_c)=D(H_0)=H^2_{\mathrm{NP}}(\Omega_L)
 \tag{4.1}
\]

and

\[
 \|u\|_{H^2}
 \le C_{\mathrm{NP}}
 \{\|H_cu\|_{H_L}+(1+K_*)\|u\|_{H_L}\}.
 \tag{4.2}
\]

#### Proof

Multiplication by `K_c` is a bounded self-adjoint nonnegative operator on
`H_L`, with norm at most `K_*`.  The bounded-perturbation theorem gives
Eq. (4.1).  Since `H_0u=H_cu-K_cu`, Eq. (3.3) gives Eq. (4.2).  \(\square\)

Thus the discontinuity across the contact surface creates no interface
condition and no loss of operator-domain `H2` regularity.  It would be an
error to differentiate `chi_D`; the proof never does so.

## 5. Exact sector geometry

Fix

\[
 0<\theta<\frac{\pi}{2},
 \qquad
 \Lambda_\theta=
 \{0\}\cup
 \{\lambda\ne0:|\arg\lambda|\le\pi-\theta\},
 \qquad
 s_\theta=\sin(\theta/2).
 \tag{5.1}
\]

For `a>=0` and nonzero `lambda=rho exp(i phi)` in `Lambda_theta`,

\[
 |a+\lambda|
 \ge s_\theta(a+\rho).
 \tag{5.2}
\]

Indeed,

\[
 \operatorname{Re}\{
 e^{-i\phi/2}(a+\lambda)\}
 =\cos(\phi/2)(a+\rho)
 \ge s_\theta(a+\rho).
 \tag{5.3}
\]

Equation (5.2) follows because the modulus dominates every rotated real
part.  The constant is sharp for the allowed scalar geometry: equality is
approached at `|phi|=pi-theta` and `a=rho`.

This same identity supplies both the continuum spectral bounds and the
discrete rotated coercivity.  At `lambda=0` the claims follow directly with
rotation `omega=1`.  No real-shift estimate is analytically continued without
proof.

## 6. Uniform complex-sector `H2` estimate

Fix `sigma>0`, let

\[
 T_c=H_c+\sigma I,
 \qquad
 u=(T_c+\lambda)^{-1}f,
 \qquad \lambda\in\Lambda_\theta.
 \tag{6.1}
\]

The spectral theorem and Eq. (5.2), applied at spectral value `s>=0`, give

\[
 \|u\|_{H_L}
 \le\frac{\|f\|_{H_L}}
 {s_\theta(\sigma+|\lambda|)},
 \tag{6.2}
\]

\[
 \|H_cu\|_{H_L}
 \le s_\theta^{-1}\|f\|_{H_L},
 \tag{6.3}
\]

and

\[
 \|H_c^{1/2}u\|_{H_L}
 \le
 \frac{\|f\|_{H_L}}
 {2s_\theta(\sigma+|\lambda|)^{1/2}}.
 \tag{6.4}
\]

Since the free form is bounded above by the killed form, its form norm and
the ordinary fixed-box `H1` norm are uniformly equivalent.  Combining
Eqs. (4.2) and (6.2)--(6.4) yields

\[
 \boxed{
 \begin{aligned}
 &(\sigma+|\lambda|)\|u\|_{H_L}
 +(\sigma+|\lambda|)^{1/2}\|u\|_{H^1}\\
 &\hspace{35mm}
 +\|u\|_{H^2}
 \le C_{\mathrm{reg}}(\theta,\sigma,L,K_*)\|f\|_{H_L},
 \end{aligned}}
 \tag{6.5}
\]

where one admissible displayed dependence is

\[
 C_{\mathrm{reg}}
 =\frac{C_L}{s_\theta}
 \left(1+\frac{1+K_*}{\sigma}\right).
 \tag{6.6}
\]

Here `C_L` is computable from the fixed-box norm equivalences and
`C_NP`.  The exact numerical value has not yet been bound to the production
source files.  Equation (6.5), rather than an observed convergence slope, is
the ideal mixed-boundary sector-regularity theorem.

The `H2` term is uniformly bounded but need not decay for arbitrary `L2`
right-hand sides as `|lambda|` grows.  Claiming
`||u||_H2=O(|lambda|^-1)` would be false at this data regularity.

## 7. Discrete sector stability and the conditional resolvent rate

Let `H_{h,c}>=0` be any declared ideal discrete self-adjoint operator.  Use
maps satisfying

\[
 P_h=J_h^*
 \tag{7.0}
\]

under the first-factor-conjugated convention, and define

\[
 \|v_h\|_{1,h}^2=
 \|v_h\|_h^2+\mathfrak a_{h,\mathrm{free}}(v_h,v_h).
 \tag{7.0a}
\]

Write

\[
 \mathfrak b_{h,c,\lambda}(p,q)
 =\mathfrak a_{h,c}(p,q)
  +(\sigma+\lambda)\langle p,q\rangle_h.
 \tag{7.1}
\]

With nonzero `lambda=rho exp(i phi)` and

\[
 \omega_\lambda=e^{-i\phi/2},
 \tag{7.2}
\]

the first-factor-conjugated convention gives the exact identity

\[
 \operatorname{Re}\{
 \omega_\lambda\mathfrak b_{h,c,\lambda}(v_h,v_h)\}
 =\cos(\phi/2)
 \{\mathfrak a_{h,c}(v_h,v_h)
   +(\sigma+\rho)\|v_h\|_h^2\}.
 \tag{7.3}
\]

Consequently

\[
 \operatorname{Re}\{
 \omega_\lambda\mathfrak b_{h,c,\lambda}(v_h,v_h)\}
 \ge s_\theta
 \{\mathfrak a_{h,c}(v_h,v_h)
   +(\sigma+\rho)\|v_h\|_h^2\}.
 \tag{7.4}
\]

At `lambda=0`, take `omega_0=1`.  This closes the abstract
rotated-coercivity premise uniformly in the mesh, alignment, and control.  It
does not bind the actual production rates.

Now make the still-open source assumptions explicit.  Suppose one accepted
source family supplies constants `C_free`, `C_kill`, `C_P`, and `C_J` such
that, with `alpha=1/2`,

\[
 |R_{h,\mathrm{free}}(u;v_h)|
 \le C_{\mathrm{free}}h^\alpha
      \|u\|_{H^2}\|v_h\|_{1,h},
 \tag{7.5}
\]

\[
 |R_{h,\mathrm{kill}}(u;v_h)|
 \le C_{\mathrm{kill}}h^\alpha
      \|u\|_{H^2}\|v_h\|_{1,h},
 \tag{7.6}
\]

\[
 \|J_hP_hu-u\|_{H_L}
 \le C_Ph\|u\|_{H^1},
 \qquad
 \|J_hv_h\|_{H_L}\le C_J\|v_h\|_h.
 \tag{7.7}
\]

Round 10 proves Eq. (7.5) for the ideal analytic member.  Equations
(7.6)--(7.7) are not source-bound at this time.

Let

\[
 u_h=(H_{h,c}+\sigma+\lambda)^{-1}P_hf,
 \qquad e_h=u_h-P_hu.
 \tag{7.8}
\]

With the test vector in the first form argument, exact adjointness and the
continuum resolvent equation give

\[
 \mathfrak b_{h,c,\lambda}(v_h,e_h)
 =-\overline{R_{h,\mathrm{free}}(u;v_h)}
  -B\overline{R_{h,\mathrm{kill}}(u;v_h)}.
 \tag{7.8a}
\]

The conjugates in Eq. (7.8a) are mandatory under Eq. (1.1).  Setting
`v_h=e_h`, rotating, and using Eqs. (7.4)--(7.6) imply

\[
 X_\lambda(e_h)
 \le
 \frac{C_{\mathrm{res}}M_\sigma}{s_\theta}
 h^\alpha\|u\|_{H^2},
 \tag{7.9}
\]

where

\[
 X_\lambda(v_h)^2=
 \mathfrak a_{h,c}(v_h,v_h)
 +(\sigma+\rho)\|v_h\|_h^2,
 \qquad
 M_\sigma=\max\{1,\sigma^{-1/2}\},
 \tag{7.10}
\]

and `C_res=C_free+B C_kill` under the Round-9 normalization.  Therefore

\[
 \|e_h\|_h
 \le
 \frac{C_{\mathrm{res}}M_\sigma}
 {s_\theta(\sigma+\rho)^{1/2}}
 h^\alpha\|u\|_{H^2}.
 \tag{7.11}
\]

For `0<h<=1`, the reconstruction triangle, Eq. (7.7), and Eqs. (6.5),
(7.11), together with `h<=h^(1/2)`, give the conditional operator-norm
estimate

\[
 \boxed{
 \left\|
 J_h(H_{h,c}+\sigma+\lambda)^{-1}P_h
 -(H_c+\sigma+\lambda)^{-1}
 \right\|_{H_L\to H_L}
 \le
 \frac{C_{\mathrm{sec}}h^{1/2}}
 {(\sigma+|\lambda|)^{1/2}}.}
 \tag{7.12}
\]

Every factor in `C_sec` is displayed in Eqs. (6.5)--(7.11).  The constant is
not accepted until Eqs. (7.6)--(7.7) are proved from frozen sources and the
ideal member is tied to the production enclosure.  Equation (7.12) is a
conditional composition, not a current completion flag.

## 8. Dunford contour and explicit positive-time growth

Take the two rays

\[
 \Gamma_\theta^\pm:
 \lambda=\rho e^{\pm i(\pi-\theta)},
 \qquad 0<\rho<\infty,
 \tag{8.1}
\]

with the upper ray oriented from `rho=0` to `rho=infinity` and the lower ray
oriented from `rho=infinity` to `rho=0`.  This orientation is part of the
formula: reversing both rays changes the sign of the integral.  Along either
ray,

\[
 \operatorname{Re}\lambda=-\rho\cos\theta,
 \qquad
 |-\lambda-\sigma|\le\sigma+\rho.
 \tag{8.2}
\]

Because `H_c+sigma>=sigma`, the vanishing-radius connector may be sent to
zero without crossing spectrum; its contribution vanishes.  For
`r=0,1,2`,

\[
 H_c^re^{-tH_c}
 =\frac{e^{\sigma t}}{2\pi i}
 \int_{\Gamma_\theta}
 (-\lambda-\sigma)^r e^{t\lambda}
 (H_c+\sigma+\lambda)^{-1}\,d\lambda.
 \tag{8.3}
\]

The same formula holds on the ideal mesh.  If Eq. (7.12) has been
source-bound, then for `t in [tau,T]`, `tau>0`,

\[
 \begin{aligned}
 &\|J_hH_{h,c}^re^{-tH_{h,c}}P_h
       -H_c^re^{-tH_c}\|\\
 &\quad\le
 \frac{C_{\mathrm{sec}}e^{\sigma T}}{\pi}
 h^{1/2}
 \int_0^\infty
 e^{-\tau\rho\cos\theta}
 (\sigma+\rho)^{r-1/2}\,d\rho.
 \end{aligned}
 \tag{8.4}
\]

The integral is explicit.  With

\[
 a=\tau\cos\theta>0,
 \qquad
 p=r+\tfrac12,
 \tag{8.5}
\]

\[
 \int_0^\infty e^{-a\rho}
  (\sigma+\rho)^{r-1/2}\,d\rho
 =
 e^{a\sigma}a^{-p}\Gamma(p,a\sigma),
 \tag{8.6}
\]

where `Gamma(p,x)` is the upper incomplete gamma function.  Thus

\[
 \mathcal C_r(\tau,T,L)
 =
 \frac{C_{\mathrm{sec}}e^{\sigma T+a\sigma}}{\pi}
 a^{-(r+1/2)}
 \Gamma(r+\tfrac12,a\sigma)
 \tag{8.7}
\]

is finite for every frozen `tau>0`, `r=0,1,2`.  In particular, the
conservative small-`tau` growth is at most
`tau^(-(r+1/2))` at fixed `theta`, `sigma`, and `L`.

No estimate extends to `tau=0`.  The exponential factor integrates every
polynomial growth allowed by the sector proof, but it cannot replace a
missing source-bound resolvent comparison.

## 9. What Round 11 closes and what remains open

The ideal fixed-box analysis proves:

```text
free mixed Neumann-periodic graph domain         = H2_NP
bounded sharp killing changes operator domain    = FALSE
control-uniform complex-sector H2 estimate        = PROVED CANDIDATE
rotated discrete coercivity constant              = sin(theta/2)
contour resolvent growth needed after binding     = (sigma+rho)^(-1/2)
positive-time contour integral for r=0,1,2        = EXPLICIT AND FINITE
contact-indicator derivative required             = FALSE
dimension-uniform H2-to-L-infinity claim           = FALSE
```

The following remain open:

```text
Round-9 source-bound map constant                  = OPEN
Round-9 source-bound cut-layer/killing constant    = OPEN
production member contains the same ideal member  = OPEN
independent production acceptance receipt          = OPEN
unconditional reconstructed-resolvent C2 rate      = FALSE
box C3 and differentiated box terms                = OPEN
componentwise root transfer                        = OPEN
F0 / F1 / F2 / F3                                  = OPEN OR UNRUN AS RECORDED
release and submission                             = FALSE
```

The correct next mathematical/source step is not another sector theorem.
It is to instantiate Eqs. (7.6)--(7.7) from the frozen physical geometry,
global gauge, exact-adjoint map, and contact-volume sources, then subject
that composition to an independent source-opening and mutation audit.

## 10. Freeze statement

This note may be promoted from candidate to a local Round-11 analytical
closure only after:

1. an independent proof audit checks the mixed Fourier domain,
   lower-order absorption, bounded-perturbation domain, scalar sector
   geometry, first-factor-conjugated rotation, and contour orientation;
2. a neutral fixture independently checks the scalar sector constant,
   mixed Neumann--periodic principal spectrum, sharp bounded-multiplier
   perturbation ledger, and Eq. (8.6), while explicitly disclaiming PDE
   proof and source binding;
3. mutation tests reject second-factor conjugation, the wrong sector,
   `tau=0`, a differentiated sharp indicator, false `H2` decay, and any
   complete-C2 or production promotion; and
4. all final bytes and direct test receipts are recorded in a separate
   audit.

Until those steps pass, the status remains

```text
ROUND11_ANALYTICAL_CANDIDATE
COMPLETE_C2_FALSE
PRODUCTION_BINDING_FALSE
RELEASE_FALSE
```
