# PDE mixed-jet theorem for the exact quotient Doi model

Date: 2026-07-13  
Status: **proved continuum functional-analytic layer; conditional weak-reaction
persistence; no claim at the current finite budget or for the SG discretization**

## 0. Result in one paragraph

For the bounded exact quotient used by G1, the reflected OU/free-diffusion
forward operator is similar to a nonpositive self-adjoint weighted Neumann
operator.  It therefore generates an analytic semigroup on \(L^2\).  The sharp
contact indicator and fixed catalyst patches enter only through bounded
multiplication, so the killed semigroup is analytic in time and entire in the
finite patch amplitudes.  For \(q_0\in L^2\), every time/control mixed jet exists
on \([\tau,T]\), \(\tau>0\), including the complete cusp jet.  The first and
second simplex sensitivity equations and all direct observable terms are
given below.  In addition, if \(K_{B,w}=BV_w\), then

\[
 B^{-1}f_B(t,w)=\langle V_w,e^{t\mathcal L}q_0\rangle+O(B)
\]

uniformly on compact positive-time/control sets, through any prescribed finite
mixed jet.  An explicit Dyson/Cauchy bound is proved.  Consequently, a
quantitatively nondegenerate mode, fold, cusp, or projected-rank lower bound of
the **free-exposure mixture** persists in the Doi density for all sufficiently
small \(B>0\).  This is a genuine model-specific continuum bridge in every
fixed finite integer physical dimension \(d\ge2\), but it is a local
finite-time weak-reaction theorem.  It is pointwise, not uniform, in \(d\).  It
does not show that the frozen value \(B=0.6\) is small enough, does not provide
a GIG approximation, does not control the \(t=O(B^{-1})\) tail, and does not
supply a Scharfetter--Gummel/FEM jet error estimator.

## 1. Exact bounded quotient and forward convention

Fix a finite integer physical dimension \(d\ge2\) and set

\[
 \mathcal Q_d=I_z\times I_\parallel\times\mathbb T_W^{d-1},
 \qquad I_z=(z_-,z_+),\quad I_\parallel=(r_-,r_+).
\]

For integrable \(h\), diagonal Haar invariance gives the exact transverse
quotient identity

\[
 \int_{\mathbb T_W^{d-1}}\!\int_{\mathbb T_W^{d-1}}
 h(y_1-y_2)\,dy_1dy_2
 =W^{d-1}\int_{\mathbb T_W^{d-1}}h(r_\perp)\,dr_\perp.
\]

No global transverse midpoint coordinate is required.

Here the symmetry quotient is exact, while the finite intervals and their
reflecting faces define the bounded-box Doi model used by the numerical
solver.  They are not the natural-decay boundaries of the unbounded physical
cylinder.  Corollary 2.2 below records the corresponding unbounded
weighted-space result and its stronger initial-data requirement.

The quotient has dimension \(d+1\).  Write

\[
 x=(z,r_\parallel,r_\perp),\qquad
 \mathbf D=\operatorname{diag}(D/2,2D,\ldots,2D),
\]

\[
 b(x)=(-\gamma(z-m),-\gamma r_\parallel,0,\ldots,0).
\]

The **forward** free Fokker--Planck operator is

\[
 \mathcal L q=-\nabla\!\cdot(bq)+\nabla\!\cdot(\mathbf D\nabla q).
 \tag{1.1}
\]

At the two nonperiodic pairs of faces its domain imposes zero probability
flux,

\[
 (bq-\mathbf D\nabla q)\cdot n=0,
 \tag{1.2}
\]

and every transverse coordinate is periodic.  This sign convention gives

\[
 \partial_tq=\mathcal Lq-BV_wq,
 \qquad -\frac{d}{dt}\int_{\mathcal Q_d}q=B\int_{\mathcal Q_d}V_wq.
 \tag{1.3}
\]

Let \(0<a<W/2\), so that the minimum-image contact set is an embedded
\(d\)-ball, and let

\[
 \chi_a(r)=\mathbf1_{\{\rho(r)<a\}},\qquad
 V_j(z,r)=W^{-(d-1)}\chi_a(r)\phi_j(z),
 \tag{1.4}
\]

where each fixed nonnegative patch satisfies

\[
 \phi_j\in L^\infty(I_z),\qquad \int_{I_z}\phi_j(z)\,dz=1.
\]

Smooth compact bumps are used in G1, but \(L^\infty\) is enough for the
theorems below.  For \(w\in\Delta_{J-1}\),

\[
 V_w=\sum_{j=1}^Jw_jV_j,\qquad
 K_{B,w}=BV_w,\qquad B\ge0.
 \tag{1.5}
\]

Thus the full installed centre-space amount is \(B\).  If the local killing
field has unit \(T^{-1}\), then \([B]=L^dT^{-1}\); the theorem makes no
cross-dimensional comparison at a common numerical value of this dimensional
budget.  The contact indicator
is discontinuous, but \(M_{V_w}\) is a bounded multiplication operator on
\(L^2(\mathcal Q_d)\).  No shape or moving-support derivative is considered.

Assume

\[
 q_0\in L^2(\mathcal Q_d),\qquad q_0\ge0,\qquad \int q_0=1.
 \tag{1.6}
\]

The finite measure of \(\mathcal Q_d\) makes the last integral meaningful.
The initial datum need not lie in \(D(\mathcal L)\), and no compatibility at
the reflecting boundary is imposed at \(t=0\).

## 2. Analytic-semigroup theorem

### Theorem 2.1 (analytic killed quotient semigroup)

Let \(X=L^2(\mathcal Q_d)\), and realize \(\mathcal L\) with (1.2) and the
periodic conditions above.  Then:

1. \(\mathcal L\) generates a positive analytic \(C_0\)-semigroup
   \(T_0(t)=e^{t\mathcal L}\) on \(X\), conserving mass on nonnegative
   \(L^1\cap L^2\) data.
2. For every real \(B\ge0\) and \(w\in\Delta_{J-1}\),
   \[
   A_{B,w}=\mathcal L-BM_{V_w},\qquad D(A_{B,w})=D(\mathcal L),
   \tag{2.1}
   \]
   generates a positive, mass-decreasing analytic semigroup
   \(T_{B,w}(t)\).
3. For every \(t>0\), the map \(w\mapsto T_{B,w}(t)\) extends to an entire
   operator-valued function of the complex patch amplitudes.  The map is
   jointly analytic in complex time with positive real part and in those
   amplitudes.
4. For every integer \(r\ge0\),
   \[
   q_{B,w}(t)=T_{B,w}(t)q_0\in D(A_{B,w}^r),\qquad t>0,
   \tag{2.2}
   \]
   and \(\partial_t^rq_{B,w}=A_{B,w}^rq_{B,w}\).  On
   \([\tau,T]\), all finite time/control mixed derivatives are bounded.

#### Proof

The reversible density for the free reflected process is

\[
 \pi(x)=Z^{-1}\exp\!\left[-\frac{\gamma(z-m)^2}{D}
 -\frac{\gamma r_\parallel^2}{4D}\right],
 \tag{2.3}
\]

uniform in the torus coordinates, with normalized transverse factor
\(W^{-(d-1)}\).  Since the domain is bounded,
\(0<\pi_{\min}\le\pi\le\pi_{\max}<\infty\).  Moreover
\(b=\mathbf D\nabla\log\pi\).  If \(q=\pi u\), direct substitution gives

\[
 \mathcal L(\pi u)=\pi\mathcal Gu,
 \qquad
 \mathcal G=\pi^{-1}\nabla\!\cdot(\pi\mathbf D\nabla),
 \tag{2.4}
\]

and (1.2) becomes the weighted Neumann condition
\((\mathbf D\nabla u)\cdot n=0\).  For each fixed finite \(d\), take the
weighted \(H^1\) form domain with periodic traces in all transverse
coordinates and this Neumann convention on the nonperiodic faces.  No
dimension-restricted Sobolev embedding is used.  On \(L^2(\pi dx)\),

\[
 \langle u,\mathcal Gv\rangle_{L^2(\pi)}
 =-\int(\nabla u)^T\mathbf D\nabla v\,\pi dx.
 \tag{2.5}
\]

The closed weighted Neumann form therefore defines a nonpositive
self-adjoint generator \(\mathcal G\).  Its semigroup is analytic and
contractive for complex time with nonnegative real part.  Multiplication by
\(\pi\) is a bounded isomorphism from \(L^2(\pi dx)\) to \(L^2(dx)\), so
\(\mathcal L=M_\pi\mathcal GM_\pi^{-1}\) is an analytic generator.  The form
also gives positivity; integrating (1.1) with (1.2) gives mass conservation.

Since \(V_w\in L^\infty\), \(-BM_{V_w}\) is a bounded operator.  The bounded
perturbation theorem preserves analyticity and the generator domain.
Positivity and mass decrease follow either from the product formula or from
Feynman--Kac for real nonnegative \(V_w\).  The Dyson--Phillips series is
norm-convergent on compact positive-time sectors and is polynomial at each
order in the amplitudes, proving entire parameter dependence.  Analytic
semigroup smoothing gives (2.2).  This completes the proof.  \(\square\)

### Corollary 2.2 (unbounded natural-decay quotient)

Replace \(I_z\times I_\parallel\) by \(\mathbb R^2\), retain the periodic
transverse coordinates, and let \(\pi\) be the Gaussian density (2.3).  On the
density space

\[
 X_\pi=L^2(\pi^{-1}dx),
 \tag{2.6}
\]

the map \(u\mapsto q=\pi u\) is unitary from \(L^2(\pi dx)\).  Therefore all
parts of Theorems 2.1, 3.1, and 4.1 remain valid for
\(q_0\in X_\pi\), with \(\kappa_\pi=1\), and with the observable-dual norm

\[
 \|V\|_{X_\pi^*}=\|V\|_{L^2(\pi dx)}
 \tag{2.7}
\]

in place of the unweighted \(L^2\) norm.  The compactly supported smooth
initial bump used by G1 belongs to \(X_\pi\).  An arbitrary datum that is only
in unweighted \(L^2(\mathbb R^2\times\mathbb T_W^{d-1})\) need not belong to
\(X_\pi\), so the unbounded theorem cannot be claimed under that weaker
assumption without another semigroup argument.

### Regularity boundary

Theorem 2.1 proves **time** regularization in powers of the generator.  The
sharp \(\chi_a\) is not in \(D(\mathcal L^*)\) in general, and the theorem does
not claim global classical spatial smoothness across the contact interface.
In particular, the safe identity is

\[
 \partial_t^rf_B=B\langle V_w,A_{B,w}^rq_{B,w}\rangle,
 \tag{2.8}
\]

not a formal expression obtained by applying \((A_{B,w}^*)^r\) to the
indicator.  All cusp-level statements below are restricted to \(t\ge\tau>0\).

## 3. Fixed-budget coordinates and sensitivity PDEs

### 3.1 Frozen tangent basis

Because the patches are normalized, the budget tangent space is

\[
 \mathsf T=\{h\in\mathbb R^J:\mathbf1^Th=0\}.
 \tag{3.1}
\]

Fix a control metric \(M\succ0\), and once and for all choose
\(P\in\mathbb R^{J\times(J-1)}\) such that

\[
 \mathbf1^TP=0,\qquad P^TMP=I_{J-1}.
 \tag{3.2}
\]

Near an interior \(w_*\), use

\[
 w(\theta)=w_*+P\theta.
 \tag{3.3}
\]

This freezes the scale in which singular values are reported.  The elementary
basis \(e_i-e_J\) is also valid, but its singular values are not comparable to
those from another basis unless the metric transformation is included.

Write

\[
 U_i=V_{Pe_i}=\sum_{j=1}^JP_{ji}V_j,
 \qquad A=A_{B,w(\theta)}.
 \tag{3.4}
\]

### Theorem 3.1 (first and second simplex sensitivities)

Let \(q=q_{B,w(\theta)}\), \(s_i=\partial_{\theta_i}q\), and
\(s_{ij}=\partial_{\theta_i}\partial_{\theta_j}q\).  They are the unique mild
solutions, with the same no-flux and periodic boundary conditions, of

\[
 \begin{aligned}
 \partial_tq&=Aq,&q(0)&=q_0,\\
 \partial_ts_i&=As_i-BU_iq,&s_i(0)&=0,\\
 \partial_ts_{ij}&=As_{ij}-BU_is_j-BU_js_i,&s_{ij}(0)&=0.
 \end{aligned}
 \tag{3.5}
\]

For \(t>0\) these equations may be differentiated in time to every finite
order in \(X\).  If

\[
 f_B(t,\theta)=B\langle V_{w(\theta)},q(t,\theta)\rangle,
 \tag{3.6}
\]

where \(\langle g,q\rangle=\int_{\mathcal Q_d}gq\,dx\), then

\[
 \partial_{\theta_i}f_B
 =B\{\langle U_i,q\rangle+\langle V_w,s_i\rangle\},
 \tag{3.7}
\]

\[
 \partial_{\theta_i\theta_j}f_B
 =B\{\langle U_i,s_j\rangle+\langle U_j,s_i\rangle
       +\langle V_w,s_{ij}\rangle\}.
 \tag{3.8}
\]

The first term in (3.7), and the first two terms in (3.8), are direct
derivatives of the reaction observable.  Omitting them is incorrect.

#### Proof

Differentiate the norm-convergent Duhamel formula with respect to the affine
parameters.  Since \(\partial_{\theta_i}A=-BM_{U_i}\) and
\(\partial_{\theta_i\theta_j}A=0\), the product rule gives (3.5).
Differentiating (3.6) gives (3.7)--(3.8).  Joint analyticity from Theorem 2.1
justifies commutation with time derivatives for \(t>0\).  \(\square\)

### 3.2 Exact mixed time/control jets

Put \(q^{(r)}=\partial_t^rq=A^rq\),
\(s_i^{(r)}=\partial_t^rs_i\), and
\(s_{ij}^{(r)}=\partial_t^rs_{ij}\).  For every \(r\ge0\) and \(t>0\),

\[
 \partial_t^rf_B=B\langle V_w,q^{(r)}\rangle,
 \tag{3.9}
\]

\[
 \partial_{\theta_i}\partial_t^rf_B
 =B\{\langle U_i,q^{(r)}\rangle+\langle V_w,s_i^{(r)}\rangle\},
 \tag{3.10}
\]

\[
 \partial_{\theta_i\theta_j}\partial_t^rf_B
 =B\{\langle U_i,s_j^{(r)}\rangle+\langle U_j,s_i^{(r)}\rangle
       +\langle V_w,s_{ij}^{(r)}\rangle\}.
 \tag{3.11}
\]

Thus \(r=4\) is available for \(f_{tttt}\), and \(r=1,2,3\) with one control
derivative gives the complete cusp jet.  Second control sensitivities are
available for Hessian and continuation diagnostics even though the minimal
cusp-persistence jet needs only first control derivatives.

## 4. Uniform weak-reaction mixed-jet theorem

Define the normalized Doi density and free-exposure mixture by

\[
 F_B(t,\theta)=B^{-1}f_B(t,w(\theta))\qquad(B>0),
 \tag{4.1}
\]

\[
 G(t,\theta)=\langle V_{w(\theta)},T_0(t)q_0\rangle
 =\sum_{j=1}^Jw_j(\theta)g_j(t),
 \quad g_j(t)=\langle V_j,T_0(t)q_0\rangle.
 \tag{4.2}
\]

This \(G\) is an exact continuum free-exposure mixture.  It is not assumed to
be GIG.

Let

\[
 \kappa_\pi=\|M_\pi\|_{L^2(\pi)\to L^2}
             \|M_\pi^{-1}\|_{L^2\to L^2(\pi)}
 \le\sqrt{\pi_{\max}/\pi_{\min}}.
 \tag{4.3}
\]

Fix a compact real control set \(\Theta\) and a complex polydisc radius
\(\delta>0\) around it.  On the resulting complex tube \(\Theta_\delta\), set

\[
 v_{\infty,\delta}
 =\sup_{\zeta\in\Theta_\delta}
   \|V_{w(\zeta)}\|_{L^\infty},\qquad
 v_{2,\delta}
 =\sup_{\zeta\in\Theta_\delta}
   \|V_{w(\zeta)}\|_{L^2}.
 \tag{4.4}
\]

These constants are finite because the control space is finite dimensional.

### Theorem 4.1 (uniform mixed-jet weak-reaction bridge)

Let \(0<\tau\le T<\infty\), \(0\le B\le B_0\), \(r\ge0\), and let
\(\alpha\) be any finite control multi-index.  Then \(F_B\) has a continuous
extension to \(B=0\), equal to \(G\), and

\[
 \boxed{
 \begin{aligned}
 &\sup_{(t,\theta)\in[\tau,T]\times\Theta}
 \left|
 \partial_t^r\partial_\theta^\alpha(F_B-G)
 \right|\\
 &\quad\le
 r!\,\alpha!\left(\frac2\tau\right)^r
 \delta^{-|\alpha|}v_{2,\delta}\kappa_\pi
 \left[
 e^{(3/2)Bv_{\infty,\delta}T}-1
 \right]
 \|q_0\|_2.
 \end{aligned}}
 \tag{4.5}
\]

In particular,

\[
 \sup|\partial_t^r\partial_\theta^\alpha(F_B-G)|
 \le B C_{r,\alpha}(\tau,T,\delta,B_0),
 \tag{4.6}
\]

where the explicit \(B\)-independent constant is

\[
 \begin{aligned}
 C_{r,\alpha}={}&r!\,\alpha!\left(\frac2\tau\right)^r
 \delta^{-|\alpha|}v_{2,\delta}\kappa_\pi
 \frac{3T}{2}v_{\infty,\delta}\\
 &\times
 e^{(3/2)B_0v_{\infty,\delta}T}\|q_0\|_2.
 \end{aligned}
 \tag{4.7}
\]

The estimate simultaneously covers the mode jet, fold jet, cusp jet, and any
fixed collection of second-control sensitivities.

#### Proof

In the weighted representation, the Dyson series for complex time
\(z\) with \(\operatorname{Re}z\ge0\) is

\[
 e^{z(\mathcal G-BV_w)}
 =e^{z\mathcal G}+\sum_{n=1}^\infty(-Bz)^n
 \int_{\Delta_n}e^{z(1-s_1)\mathcal G}V_w
 \cdots V_we^{zs_n\mathcal G}\,ds.
 \tag{4.8}
\]

Every free factor is a contraction and \(\operatorname{vol}\Delta_n=1/n!\).
After transforming back to \(L^2(dx)\),

\[
 \|T_{B,w}(z)-T_0(z)\|_{2\to2}
 \le\kappa_\pi\{e^{B|z|\|V_w\|_\infty}-1\}.
 \tag{4.9}
\]

The important point is that multiplication by \(V_w\) commutes with
\(M_\pi\), so the similarity constant appears once, not once per Dyson
factor.  Therefore the complex-bilinear extension of

\[
 R_B(z,\zeta)
 =\langle V_{w(\zeta)},
   [T_{B,w(\zeta)}(z)-T_0(z)]q_0\rangle
 \tag{4.10}
\]

obeys, on the control tube,

\[
 |R_B(z,\zeta)|\le v_{2,\delta}\kappa_\pi
 \{e^{Bv_{\infty,\delta}|z|}-1\}\|q_0\|_2.
 \tag{4.11}
\]

For \(t\in[\tau,T]\), the complex disk \(|z-t|\le\tau/2\) lies in the open
right half-plane and has \(|z|\le3T/2\).  Cauchy's estimate in this disk and
in each control polydisc gives (4.5).  Finally
\(e^{Bx}-1\le Bxe^{B_0x}\) gives (4.6)--(4.7).  \(\square\)

### 4.2 First Dyson correction and explicit remainder

For real \(t\ge0\), define

\[
 \mathcal H_w(t)=\int_0^t
 \langle V_w,T_0(t-s)M_{V_w}T_0(s)q_0\rangle\,ds.
 \tag{4.12}
\]

Then

\[
 F_B(t,w)=G(t,w)-B\mathcal H_w(t)+\mathcal R_{2,B}(t,w),
 \tag{4.13}
\]

with

\[
 |\mathcal R_{2,B}(t,w)|
 \le \|V_w\|_2\kappa_\pi
 \left[e^{B\|V_w\|_\infty t}-1-B\|V_w\|_\infty t\right]
 \|q_0\|_2.
 \tag{4.14}
\]

Thus the displayed first correction has an \(O(B^2)\) remainder for real
time.  To control its mixed jets, let \(z\) be complex with
\(\operatorname{Re}z>0\) and
\(\zeta\in\Theta_\delta\), define the analytic remainder directly by the
\(n\ge2\) Dyson tail,

\[
 \begin{aligned}
 \mathcal R_{2,B}(z,\zeta)
 ={}&\left\langle V_{w(\zeta)},M_\pi
 \sum_{n=2}^{\infty}(-Bz)^n
 \int_{\Delta_n}
 e^{z(1-s_1)\mathcal G}V_{w(\zeta)}
 \cdots V_{w(\zeta)}e^{zs_n\mathcal G}\,ds\,
 M_\pi^{-1}q_0\right\rangle .
 \end{aligned}
 \tag{4.15}
\]

The same contraction and similarity argument as in (4.9) gives, throughout
the complex time disk and control tube,

\[
 |\mathcal R_{2,B}(z,\zeta)|
 \le v_{2,\delta}\kappa_\pi
 \left[
 e^{Bv_{\infty,\delta}|z|}
 -1-Bv_{\infty,\delta}|z|
 \right]\|q_0\|_2.
 \tag{4.16}
\]

Multivariable Cauchy therefore yields

\[
 \begin{aligned}
 &\sup_{[\tau,T]\times\Theta}
 |\partial_t^r\partial_\theta^\alpha\mathcal R_{2,B}|\\
 &\quad\le
 r!\alpha!\left(\frac2\tau\right)^r\delta^{-|\alpha|}
 v_{2,\delta}\kappa_\pi
 \left[
 e^{(3/2)Bv_{\infty,\delta}T}
 -1-\frac32Bv_{\infty,\delta}T
 \right]\|q_0\|_2\\
 &\quad\le
 \frac{B^2}{2}\,
 r!\alpha!\left(\frac2\tau\right)^r\delta^{-|\alpha|}
 v_{2,\delta}\kappa_\pi
 \left(\frac32v_{\infty,\delta}T\right)^2
 e^{(3/2)B_0v_{\infty,\delta}T}\|q_0\|_2.
 \end{aligned}
 \tag{4.17}
\]

The final inequality uses \(e^x-1-x\le x^2e^x/2\) for \(x\ge0\).  Hence the
first-correction remainder is uniformly \(O(B^2)\) through every fixed mixed
jet, now from a bound on the required complex neighborhood rather than only
on the real set.

### 4.3 What the theorem says about control derivatives

Since \(G\) is affine in \(w\),

\[
 D_\theta G[h]=\langle V_{Ph},T_0q_0\rangle,
 \qquad D_\theta^kG=0\quad(k\ge2).
 \tag{4.18}
\]

Theorem 4.1 implies

\[
 D_\theta F_B=D_\theta G+O(B),\qquad
 D_\theta^2F_B=O(B)
 \tag{4.19}
\]

uniformly through the desired time derivatives.  This agrees with the exact
sensitivity PDEs and is useful for checking implementations.

### Corollary 4.2 (factorized three-patch cusp determinant)

Assume the free generator and initial law factor exactly as

\[
 \mathcal L=\mathcal L_z\otimes I+I\otimes\mathcal L_r,
 \qquad q_0=q_{z,0}\otimes q_{r,0},
 \tag{4.20}
\]

where \(\mathcal L_r\) contains every relative coordinate.  This is the frozen
G1 quotient structure.  Define

\[
 a_j(t)=W^{-(d-1)}
 \langle\phi_j,e^{t\mathcal L_z}q_{z,0}\rangle,
 \qquad
 c_d(t)=\langle\chi_a,e^{t\mathcal L_r}q_{r,0}\rangle.
 \tag{4.21}
\]

Then every exact free-exposure clock factorizes:

\[
 g_j(t)=a_j(t)c_d(t),
 \qquad
 g_j^{(r)}(t)=
 \sum_{k=0}^r {r\choose k}a_j^{(k)}(t)c_d^{(r-k)}(t).
 \tag{4.22}
\]

For \(J=3\), regard \(g=(g_1,g_2,g_3)^T\) as a column vector and put

\[
 \mathscr D(t)=
 \begin{pmatrix}
  g'(t)^T\\
  g''(t)^T\\
  g'''(t)^T
 \end{pmatrix},
 \qquad
 \Delta(t)=\det\mathscr D(t).
 \tag{4.23}
\]

Suppose that for some \(t_*>0\):

1. \(\Delta(t_*)=0\) and \(\operatorname{rank}\mathscr D(t_*)=2\);
2. the one-dimensional nullspace has a vector \(w_*\) normalized by
   \(\mathbf1^Tw_*=1\), with every component strictly positive;
3. \(g''''(t_*)^Tw_*\ne0\); and
4. for the frozen tangent basis \(P\) from (3.2),
   \[
   R_*(t_*)=
   \begin{pmatrix}
    g'(t_*)^TP\\
    g''(t_*)^TP
   \end{pmatrix}
   \tag{4.24}
   \]
   is invertible.

Then the free mixture \(G(t,w)=g(t)^Tw\) has a nondegenerate interior
budget-constrained cusp at \((t_*,w_*)\).  Moreover,

\[
 \Delta'(t_*)=
 \det
 \begin{pmatrix}
  g'(t_*)^T\\
  g''(t_*)^T\\
  g''''(t_*)^T
 \end{pmatrix},
 \tag{4.25}
\]

and the determinant of the cusp Jacobian in coordinates
\((t,\theta_1,\theta_2)\) is

\[
 \det DC_0(t_*,0)
 =
 [g''''(t_*)^Tw_*]\det R_*(t_*)
 =
 \det[P,w_*]\,\Delta'(t_*).
 \tag{4.26}
\]

#### Proof

The tensor-product semigroup and product initial law give (4.22).  The
equation \(\mathscr D(t_*)w_*=0\) is exactly
\(G_t=G_{tt}=G_{ttt}=0\).  Conditions 3--4 are respectively the fourth-time
nondegeneracy and the rank-two budget unfolding, so the cusp Jacobian is
invertible.  Differentiating the determinant in (4.23) produces three terms;
the first two contain repeated rows and vanish, giving (4.25).  Finally,
multiply the matrix in (4.25) on the right by \([P,w_*]\).  Its first two rows
annihilate \(w_*\), so expansion along the final column gives (4.26).
\(\square\)

This is a directly computable spatial-configuration recipe: the longitudinal
patch clocks \(a_j\), common relative-contact clock \(c_d\), and their first
four derivatives determine the candidate without a killed-PDE control scan.
It remains a theorem with hypotheses, not evidence that the frozen three
patches satisfy them.  The zero of \(\Delta\), rank, positive normalized null
vector, fourth derivative, and tangent singular value all require certified
margins.  The numerical value of \(\det R_*\) depends on the frozen metric
basis; invertibility and a metric-normalized singular-value lower bound are
the invariant content.

## 5. Quantitative persistence and rank transfer

All norms in this section are taken after nondimensionalizing time and using
the frozen tangent metric (3.2).  This avoids adding quantities with
incompatible units.

### Lemma 5.1 (quantitative zero persistence)

Let \(H_0:\overline{B_r(x_0)}\to\mathbb R^n\) be \(C^1\), with
\(H_0(x_0)=0\).  Put

\[
 A_0=DH_0(x_0),\qquad \mu=\sigma_{\min}(A_0)>0,
 \tag{5.1}
\]

and assume

\[
 \sup_{B_r(x_0)}\|DH_0-A_0\|_2\le\mu/4.
 \tag{5.2}
\]

If another \(C^1\) map \(H\) on the same closed ball satisfies

\[
 \varepsilon_0=\sup\|H-H_0\|_2\le\mu r/2,
 \qquad
 \varepsilon_1=\sup\|DH-DH_0\|_2\le\mu/4,
 \tag{5.3}
\]

then \(H\) has exactly one zero \(x_H\) in \(\overline{B_r(x_0)}\),

\[
 \|x_H-x_0\|_2\le2\varepsilon_0/\mu,
 \qquad
 \sigma_{\min}(DH(x_H))\ge\mu/2.
 \tag{5.4}
\]

#### Proof

The map \(\Phi(x)=x-A_0^{-1}H(x)\) has Lipschitz constant at most \(1/2\)
on the closed ball by (5.2)--(5.3).  Moreover, for every point in that ball,

\[
 \|\Phi(x)-x_0\|\le\tfrac12r+\varepsilon_0/\mu\le r.
\]

It is therefore a contraction of the ball into itself.  Its unique fixed
point is the asserted zero.  The distance bound follows from the contraction
estimate, and the singular-value bound follows from
\(\|DH(x_H)-A_0\|\le\mu/2\).  \(\square\)

### Scalar-to-vector and scalar-to-operator assembly

Estimate (4.5) is componentwise.  If an \(n\)-component jet map has scalar
component errors bounded by \(E_a\), then the error used as
\(\varepsilon_0\) in Lemma 5.1 is bounded by

\[
 \|H-H_0\|_2
 \le \left(\sum_{a=1}^n E_a^2\right)^{1/2}
 \le \sqrt{n}\max_a E_a.
\]

Likewise, if the \((a,j)\) entry of an \(n\times p\) Jacobian error is
bounded by \(E_{aj}\), then

\[
 \|DH-DH_0\|_2
 \le \|DH-DH_0\|_F
 \le \left(\sum_{a=1}^n\sum_{j=1}^p E_{aj}^2\right)^{1/2}
 \le \sqrt{np}\max_{a,j}E_{aj}.
\]

These assembled Euclidean and operator-norm bounds, rather than a single
scalar Cauchy bound, are the quantities inserted into (5.3).

### Corollary 5.2 (fold transfer)

For a one-control slice, put

\[
 H_0=(G_t,G_{tt}),\qquad H_B=((F_B)_t,(F_B)_{tt}),
 \tag{5.5}
\]

as maps of \(x=(t,\theta)\).  If \(G\) has a nondegenerate fold at \(x_0\),
then

\[
 DH_0(x_0)=
 \begin{pmatrix}
 G_{tt}&G_{t\theta}\\
 G_{ttt}&G_{tt\theta}
 \end{pmatrix}_{x_0}
 \tag{5.6}
\]

is invertible.  Assume \(x_0\) lies in
\((\tau,T)\times\Theta^\circ\), where \(\Theta^\circ\) is the chosen
simplex-interior coordinate chart.  Choose \(r>0\) so that the **closed**
ball \(\overline{B_r(x_0)}\) is contained in this set,
\(\inf_{\overline{B_r(x_0)}}\min_j w_j(\theta)>0\), and (5.2) holds.  The
explicit bounds (4.5) on

\[
 \{G_t,G_{tt},G_{ttt},G_{t\theta},G_{tt\theta}\}
 \tag{5.7}
\]

give \(\varepsilon_0(B),\varepsilon_1(B)=O(B)\).  Every \(B>0\) small enough
for (5.3) has a unique nearby Doi fold, with the displacement and
nondegeneracy bounds (5.4).  Because \(f_B=BF_B\), \(f_B\) has the same fold
location and topology as \(F_B\).

### Corollary 5.3 (cusp transfer)

For two tangent controls, put

\[
 C_0=(G_t,G_{tt},G_{ttt}),\qquad
 C_B=((F_B)_t,(F_B)_{tt},(F_B)_{ttt}),
 \tag{5.8}
\]

as maps of \(x=(t,\theta_1,\theta_2)\).  At a free-exposure cusp,

\[
 DC_0(x_0)=
 \begin{pmatrix}
 G_{tt}&G_{t\theta_1}&G_{t\theta_2}\\
 G_{ttt}&G_{tt\theta_1}&G_{tt\theta_2}\\
 G_{tttt}&G_{ttt\theta_1}&G_{ttt\theta_2}
 \end{pmatrix}_{x_0}
 \tag{5.9}
\]

is invertible exactly when \(G_{tttt}\ne0\) and the two projected control rows
have rank two.  Assume \(x_0\in(\tau,T)\times\Theta^\circ\), and choose
\(r>0\) so that the **closed** ball \(\overline{B_r(x_0)}\) is contained in
this set, \(\inf_{\overline{B_r(x_0)}}\min_jw_j(\theta)>0\), and (5.2)
holds.  The cusp jet in (5.9), controlled by (4.5), supplies the \(C^1\)
error required in Lemma 5.1 after the scalar-to-matrix assembly above.  Hence
every sufficiently small \(B>0\) has a unique nearby nondegenerate Doi cusp.
This transfers one local
max--min pair only; trimodality still requires a remote persistent pair.

### Corollary 5.4 (Weyl lower bound for projected control rank)

Assume \(J\ge3\), so the simplex tangent dimension \(J-1\) is at least two.
Let

\[
 R_0(x)=
 \begin{pmatrix}
 \nabla_\theta G_t\\
 \nabla_\theta G_{tt}
 \end{pmatrix},\qquad
 R_B(x)=
 \begin{pmatrix}
 \nabla_\theta(F_B)_t\\
 \nabla_\theta(F_B)_{tt}
 \end{pmatrix}.
 \tag{5.10}
\]

If on a region \(U\)

\[
 \inf_{x\in U}\sigma_2(R_0(x))=s_*>0,
 \qquad
 \sup_{x\in U}\|R_B(x)-R_0(x)\|_2\le\varepsilon_R(B),
 \tag{5.11}
\]

then Weyl's inequality gives

\[
 \inf_{x\in U}\sigma_2(R_B(x))\ge s_*-\varepsilon_R(B).
 \tag{5.12}
\]

In particular, if (4.5) bounds every entry of the
\(2\times(J-1)\) matrix difference by \(E_R^{\rm sc}(B)\), then the required
operator-norm error may be taken as

\[
 \varepsilon_R(B)\le\sqrt{2(J-1)}\,E_R^{\rm sc}(B).
\]

At a displaced root \(x_B\), if \(R_0\) is \(L_R\)-Lipschitz, then

\[
 \sigma_2(R_B(x_B))
 \ge s_*-\varepsilon_R(B)-2L_R\varepsilon_0(B)/\mu.
 \tag{5.13}
\]

The right-hand side is positive for sufficiently small \(B\).  The raw
control matrix for \(f_B\) is \(BR_B\), so its absolute smallest singular
value is bounded below by \(B\) times (5.12) or (5.13).  The normalized
conditioning can remain finite as \(B\downarrow0\), while the absolute event
rate and absolute control response vanish.  These facts must not be conflated.

### Corollary 5.5 (modes and multiple channels)

Let disjoint closed peak intervals \(I_k=[a_k,b_k]\subset[\tau,T]\) and
valley intervals \(J_k=[c_k,d_k]\subset[\tau,T]\) be ordered so that each
\(J_k\) lies between two adjacent peak intervals.  Suppose, uniformly over
the control set under consideration, that

\[
 \begin{array}{lll}
 G_t(a_k)\ge\eta_{\rm p},&G_t(b_k)\le-\eta_{\rm p},
   &G_{tt}\le-\kappa_{\rm p}\quad\hbox{on }I_k,\\[2mm]
 G_t(c_k)\le-\eta_{\rm v},&G_t(d_k)\ge\eta_{\rm v},
   &G_{tt}\ge\kappa_{\rm v}\quad\hbox{on }J_k,
 \end{array}
\]

for fixed positive margins
\(\eta_{\rm p},\eta_{\rm v},\kappa_{\rm p},\kappa_{\rm v}\).  If the
\(r=1\) instance of (4.5) is smaller than
\(\min(\eta_{\rm p},\eta_{\rm v})\), and the \(r=2\) instance is smaller
than \(\min(\kappa_{\rm p},\kappa_{\rm v})\), then \(F_B\) has exactly one
nondegenerate maximum in every \(I_k\) and exactly one nondegenerate minimum
in every \(J_k\).  The same statement holds for \(f_B=BF_B\) when \(B>0\).
Endpoint or separator signs without the positive-curvature valley margin
would prove only the existence of an intervening critical point, not a
nondegenerate minimum.  This is the continuum analogue of the local
channel-dominance lemma.  It applies to every fixed finite number of patches;
there is no uniform-in-\(J\) observability conclusion.

## 6. Is this a useful continuum bridge?

### What is now proved

The chain

\[
 \text{free continuum exposure with quantitative jet margins}
 \Longrightarrow
 \text{weak-reaction continuum Doi modes/fold/cusp/rank}
 \tag{6.1}
\]

is proved for the exact bounded quotient, with an explicit error.  This is
more model-specific than the abstract Duhamel identity: \(G\) uses the actual
reflected OU/free-diffusion quotient, embedded minimum-image \(d\)-ball contact
indicator, fixed physical patches, and physical budget tangent space.  The
proof is pointwise in every fixed finite \(d\): another dimension adds one
periodic relative coordinate.  The constants, dimensional budget, amplitudes,
and admissible weak-budget threshold may change with \(d\); no uniform-in-\(d\)
or \(d\to\infty\) statement is made.

The result can become a strong continuum theorem if a free-exposure mixture
is proved or certified to have:

1. an observable fold/cusp or separated multiple-mode configuration;
2. explicit derivative, prominence, and separator margins;
3. a positive projected singular-value margin in the frozen metric; and
4. a computed \(B_*>0\) for which (4.5) is below every persistence margin.

### What is not proved

1. **No result at \(B=0.6\).**  The current pilot uses \(B=0.6\).  This note
   neither nondimensionalizes that value into a small parameter nor shows
   \(0.6<B_*\).  The exponential bound is intentionally conservative.
2. **No automatic GIG bridge.**  The functions \(g_j(t)\) in (4.2) are exact
   free exposures, not GIG clocks.  A separate heat-kernel/patch asymptotic
   with its own mixed-jet error is required to replace them by GIG channels.
   If such an error is \(E_{\rm geom}\), the composable bridge is only
   \(CB+E_{\rm geom}\).
3. **No full-time probability-density limit.**  On a bounded irreducible
   reflected domain, \(G(t,w)\) approaches a positive stationary exposure.
   It is not integrable on \([0,\infty)\).  The Doi density eventually decays,
   and for many nontrivial killings its total reaction probability is one for
   every \(B>0\).  Thus the limit is singular on the long scale
   \(t=O(B^{-1})\); (4.5) is only for fixed \(T\).
4. **Event-mass collapse.**  On a fixed window,
   \(\int_\tau^Tf_Bdt=O(B)\).  Normalized shapes and condition ratios can
   persist while absolute event mass, rate, and prominence vanish.  Any fixed
   experimental observability floor imposes a lower bound on \(B\), which
   must overlap the theorem's upper bound \(B_*\).
5. **No global modal count without a tail proof.**  Local modes persist on the
   certified window.  Extra late extrema cannot be excluded without a
   separate spectral/Feynman--Kac tail argument.
6. **No localized-patch quotient.**  The exact reduction still requires
   transverse slab symmetry.  The semigroup argument applies to a full
   localized bounded configuration-space model too, but its state dimension
   and numerical realization are different.

## 7. Numerical transfer remains open

The continuum theorems above do not prove that the current
Scharfetter--Gummel finite-volume jets converge in the norms required by
Lemma 5.1.  In particular, the repository presently has no proved a priori or
a posteriori estimate of the form

\[
 \|H_h-H\|_{C^1(U)}\le E_h
 \quad\text{or}\quad
 \|C_h-C\|_{C^1(U)}\le E_h
 \tag{7.1}
\]

for the fold or cusp maps.  Such an estimator must handle:

- the discontinuous contact indicator and its cut-cell quadrature;
- reflected OU fluxes and periodic wrapping;
- cell-averaged catalyst profiles and the physical budget;
- semigroup and first/second sensitivity actions;
- time derivatives through fourth order;
- the \(\tau^{-r}\)-type deterioration caused by \(q_0\in L^2\) near \(t=0\);
- box truncation if the intended physical process is unbounded; and
- rounding/linear-algebra residuals if a computer-assisted root certificate
  is claimed.

The G1a foundation gates and observed odd/even stability are valuable
diagnostics, but they are not (7.1).  No convergence order is asserted here
for SG or FEM in the presence of the sharp contact interface.  A rigorous
finite-grid-to-PDE fold/cusp certificate remains **OPEN**.

## 8. Evidence classification and publication value

| Statement | Status |
|---|---|
| Analytic reflected-OU quotient semigroup on \(L^2\) | **PROVED** |
| Bounded indicator killing preserves analyticity | **PROVED** |
| First/second simplex sensitivity PDEs and direct terms | **PROVED** |
| All positive-time mixed jets through cusp order | **PROVED** |
| Uniform \(B^{-1}f_B=G+O(B)\) mixed-jet bound | **PROVED** |
| Conditional weak-\(B\) fold/cusp/mode persistence | **PROVED** |
| Conditional Weyl projected-rank lower bound | **PROVED** |
| Required free-exposure cusp/multimode margins for the frozen model | **NOT ESTABLISHED** |
| Applicability to the current \(B=0.6\) | **NOT ESTABLISHED** |
| GIG-to-free-exposure mixed-jet approximation | **OPEN** |
| SG/FEM \(C^1\) fold/cusp estimator | **OPEN** |
| Physical \(d=3\) numerical transition | **NOT RUN** |

The semigroup and Dyson ingredients are standard individually.  The useful
paper-level content is their exact assembly into a physical-budget,
model-specific mixed-jet and quantitative singularity-persistence theorem,
paired with a nontrivial continuum free-exposure cusp/mode certificate.  The
theorem alone does not close the PRR gate; it does provide a substantially
more tractable analytical bridge than a global GIG-to-finite-\(B\) theorem.

## 9. Standard semigroup references

- K.-J. Engel and R. Nagel, *One-Parameter Semigroups for Linear Evolution
  Equations*, especially the bounded-perturbation/Dyson--Phillips framework:
  <https://link.springer.com/book/10.1007/b97696>.
- R. Chill, E. Fašangová, G. Metafune, and D. Pallara, analyticity sectors for
  Ornstein--Uhlenbeck semigroups in invariant-measure spaces:
  <https://academic.oup.com/jlms/article/71/3/703/807644>.

The quotient proof above does not depend on importing a black-box OU formula:
its bounded-domain reversible similarity and weighted Neumann form are shown
explicitly in (2.3)--(2.5).
