# Direct fixed-dimension/fixed-mode theorem for weakly reactive OU slab families

Date: 2026-07-13  
Status: **audited theorem for an epsilon-dependent slab family; manuscript use
requires the scope restrictions in Sections 5--6**

## 1. Why this route is stronger than a GIG realization bridge

The reduced GIG construction proves a useful separated-clock theorem, but the
new encounter paper does not need to approximate those particular clocks.
The physical Ornstein--Uhlenbeck (OU) quotient already contains an exact
family of sharply localized exposure clocks.  For each **fixed finite** number
of desired clocks, normalized catalyst slabs placed along the deterministic
midpoint trajectory generate one clock near each chosen time.  Their
cross-derivatives are exponentially small in a narrow-noise limit.  A direct
channel-dominance argument then gives the prescribed finite number of modes in
an epsilon-dependent continuum encounter family.  The mixed-jet weak-budget
theorem transfers those modes to the Doi reaction-time density after fixing
the geometry parameter and then taking the installed budget sufficiently
small.

This note states the direct theorem and records the limits that must remain
visible.  It does not claim that one fixed configuration supports unboundedly
many modes, a result uniform as the number of modes tends to infinity, a
usable lower bound on the allowed budget, or the numerical verification
required for the finite-parameter model used in the manuscript.

## 2. Exact slab family

Fix any finite integer physical dimension \(d\ge2\) and the slab geometry

\[
  (Z,R_\parallel,R_\perp)
  \in \mathbb R\times\mathbb R\times\mathbb T_W^{d-1}.
\]

The transverse diagonal-translation quotient is exact: Haar invariance gives

\[
 \int_{\mathbb T_W^{d-1}}\!\int_{\mathbb T_W^{d-1}}
 h(y_1-y_2)\,dy_1dy_2
 =W^{d-1}\int_{\mathbb T_W^{d-1}}h(r_\perp)\,dr_\perp.
\]

This identity avoids introducing a global torus midpoint coordinate and
explains the centre-space normalization below.

Take \(D_0>0\), \(\gamma>0\), and \(z_0\ne\bar z\).  The midpoint follows

\[
  dZ_t=-\gamma(Z_t-\bar z)\,dt+\varepsilon\sqrt{D_0}\,dW_t,
  \qquad Z_0\sim N(z_0,\varepsilon^2s_0^2),                 \tag{2.1}
\]

so

\[
  \mu(t)=\bar z+(z_0-\bar z)e^{-\gamma t},
  \qquad
  \operatorname{Var}Z_t=\varepsilon^2s^2(t),               \tag{2.2}
\]

\[
  s^2(t)=s_0^2e^{-2\gamma t}
  +\frac{D_0}{2\gamma}(1-e^{-2\gamma t}).                  \tag{2.3}
\]

To remove an ambiguity in the relative factor, use the equal-diffusivity
two-walker quotient

\[
 \begin{aligned}
 dR_{\parallel,t}&=-\gamma R_{\parallel,t}\,dt
             +2\varepsilon\sqrt{D_0}\,dW_{\parallel,t},\\
 dR_{\perp,t}&=2\varepsilon\sqrt{D_0}\,dW_{\perp,t}
             \pmod W .
 \end{aligned}                                             \tag{2.4}
\]

Assume independence of \(Z_0\), \(R_{\parallel,0}\), and \(R_{\perp,0}\),
with

\[
 R_{\parallel,0}\sim
 N(r_{\parallel,0},\varepsilon^2u_0^2),\qquad
 R_{\perp,0}\sim\text{a wrapped Gaussian with mean }r_{\perp,0}
 \text{ and covariance }\varepsilon^2\Sigma_{\perp,0}.    \tag{2.5}
\]

Here \(s_0,u_0>0\),
\(r_{\perp,0}\in\mathbb T_W^{d-1}\), and
\(\Sigma_{\perp,0}\in\mathbb R^{(d-1)\times(d-1)}\) is positive definite.
For each
fixed \(\varepsilon>0\), the full initial density belongs to the reversible
weighted density space \(X_{\pi_\varepsilon}=L^2(\pi_\varepsilon^{-1})\)
used by the unbounded semigroup theorem provided

\[
 s_0^2<\frac{D_0}{\gamma},\qquad
 u_0^2<\frac{4D_0}{\gamma}.                                \tag{2.6}
\]

Indeed, these are exactly the conditions that the initial variances be less
than twice the corresponding stationary variances.  The wrapped transverse
density is in \(L^2\) against the uniform torus invariant measure for every
fixed \(\varepsilon>0\).  These conditions are not needed to evaluate the
free kernels, but they are needed when invoking the existing Doi mixed-jet
theorem on the unbounded cylinder.  No estimate below is uniform in the
weighted norm as \(\varepsilon\downarrow0\).

For a fixed width parameter \(\rho>0\), use normalized longitudinal catalyst
profiles

\[
  \phi_{j,\varepsilon}(z)
  =\frac{1}{\sqrt{2\pi}\varepsilon\rho}
    \exp\!\left[-\frac{(z-c_j)^2}{2\varepsilon^2\rho^2}\right]. \tag{2.7}
\]

The full centre-space slab profile is
\(\phi_{j,\varepsilon}(z)/W^{d-1}\).  Hence every patch has unit
centre-space integral and

\[
  \kappa_{B,w,\varepsilon}(z)=\frac{B}{W^{d-1}}
  \sum_{j=1}^m w_j\phi_{j,\varepsilon}(z),
  \qquad w_j\geq0,\quad\sum_jw_j=1,                         \tag{2.8}
\]

has the same physical installed amount \(B\) for every control.  If the local
killing field has unit \(T^{-1}\), then \([B]=L^dT^{-1}\); equal numerical
values of this dimensional budget are not compared across dimensions without
a separately declared nondimensionalization.  Assume
\(0<a<W/2\), interpret transverse differences by the minimum-image convention,
and set

\[
 \chi_a(R)=\mathbf 1_{\{|R|_{\rm mi}<a\}},\qquad
 K_{B,w,\varepsilon}(Z,R)
 =\chi_a(R)\kappa_{B,w,\varepsilon}(Z).                    \tag{2.9}
\]

Thus this is an embedded minimum-image \(d\)-ball, with its boundary away from
the torus cut locus.  The catalyst is a longitudinal slab,
uniform in the transverse common-centre coordinates; it is not a localized
patch of arbitrary shape.

Independence of midpoint and relative motion gives the exact free-exposure
clocks

\[
  g_{j,\varepsilon}(t)
  =c_{d,\varepsilon}(t)a_{j,\varepsilon}(t),                \tag{2.10}
\]

where \(c_{d,\varepsilon}(t)=\Pr(|R_t|_{\rm mi}<a)\) and Gaussian convolution
gives

\[
  a_{j,\varepsilon}(t)
  =\frac{1}{W^{d-1}\sqrt{2\pi}\,\varepsilon S(t)}
   \exp\!\left[-\frac{(c_j-\mu(t))^2}
                       {2\varepsilon^2S^2(t)}\right],       \tag{2.11}
\]

\[
  S^2(t)=s^2(t)+\rho^2.                                    \tag{2.12}
\]

The normalized free-exposure mixture is

\[
  G_\varepsilon(t;w)=\sum_{j=1}^m w_jg_{j,\varepsilon}(t). \tag{2.13}
\]

## 3. Assumptions on the encounter factor

Choose a compact time interval \(I=[\tau,T]\subset(0,\infty)\).  Since
\(z_0\ne\bar z\),

\[
 \mu'(t)=-\gamma(z_0-\bar z)e^{-\gamma t}
\]

is bounded away from zero on \(I\), so \(\mu\) is strictly monotone there.
Choose distinct target times

\[
  \tau<t_1<\cdots<t_m<T.                                  \tag{3.1}
\]

For (2.4), the minimum-image deterministic relative trajectory is

\[
 r_*(t)=(r_{\parallel,0}e^{-\gamma t},r_{\perp,0}).
\]

Choose a compact union \(I_*\) of pairwise disjoint closed neighborhoods of
the target times, contained in \((\tau,T)\), and assume that this deterministic
trajectory lies strictly inside the contact ball there:

\[
  \sup_{t\in I_*}|r_*(t)|_{\rm mi}\leq a-\eta               \tag{3.2}
\]

for some \(\eta>0\).  The scaling in (2.4)--(2.5) makes the relative law a
wrapped Gaussian with mean \(r_*(t)\) and covariance
\(\varepsilon^2\Sigma_R(t)\), where \(\Sigma_R\) and its time derivatives are
bounded on \(I_*\), and \(\Sigma_R(t)\) is uniformly positive definite there.
More explicitly, its longitudinal variance coefficient is

\[
 u_0^2e^{-2\gamma t}
 +\frac{2D_0}{\gamma}(1-e^{-2\gamma t}),
\]

and its transverse covariance coefficient is
\(\Sigma_{\perp,0}+4D_0tI_{d-1}\), before wrapping on the torus.

### Lemma 3.1 (contact-factor tail and time derivatives)

For every fixed integer \(r\ge0\), there are finite constants
\(C_{r,d},N_{r,d},q_d>0\), independent of sufficiently small
\(\varepsilon\), such that

\[
  \sup_{t\in I_*}
  |\partial_t^r(c_{d,\varepsilon}(t)-1)|
  \leq C_{r,d}\varepsilon^{-N_{r,d}}e^{-q_d/\varepsilon^2}. \tag{3.3}
\]

#### Proof

Use product geodesic distance on
\(\mathbb R\times\mathbb T_W^{d-1}\).  The reverse triangle inequality and
the contact-interior margin give

\[
 \inf_{t\in I_*}\inf_{R\notin C_a}
 d_{\rm cyl}(R,r_*(t))\ge\eta.
\]

Write the wrapped transition density as its Gaussian image sum.  Every
Euclidean lift is therefore at least distance \(\eta\) from the mean; no
single chart for the complement of the ball is assumed.  Differentiating one
image \(r\) times in \(t\) produces that Gaussian times a polynomial and a
finite power of \(\varepsilon^{-1}\), with coefficients bounded on \(I_*\).
In max-norm lattice shell \(k\), the number of indices grows only
polynomially in \(k\), while the image distance grows at least linearly.
The resulting fixed-dimensional Gaussian shell majorant is summable and
uniformly justifies termwise differentiation.  Integrating outside the
contact ball gives a polynomial prefactor times
\(\exp[-q_d/\varepsilon^2]\).  The condition \(a<W/2\) is used only to keep
the embedded contact-ball boundary away from the cut locus.  This proves
(3.3), with constants allowed to depend on the fixed finite \(d\).  \(\square\)

Only the weaker consequence is needed below: for \(r=0,1,2\),
\(c_{d,\varepsilon}\to1\) in \(C^2(I_*)\), and it is bounded away from
zero there.  A variant of the mode-existence proof remains valid if a common
encounter factor converges in \(C^2\) to a strictly positive function
\(c_0(t)\), but in that variant the leading local clock and the peak-balancing
weights must include the factor \(c_0(t_j)\).  The statements below use the
specific limit \(c_0\equiv1\) proved in Lemma 3.1.

Set the patch centres prospectively by

\[
  c_j=\mu(t_j).                                            \tag{3.4}
\]

## 4. Local asymptotics and derivative dominance

### Lemma 4.1 (own-channel local limit)

Let \(t=t_j+\varepsilon y\), with \(|y|\leq L\) for fixed \(L\).  Uniformly
on this local window,

\[
  c_j-\mu(t)
  =-\varepsilon\mu'(t_j)y+O(\varepsilon^2),                \tag{4.1}
\]

and therefore

\[
  \varepsilon a_{j,\varepsilon}(t_j+\varepsilon y)
  \longrightarrow
  A_j(y)
  =\frac{1}{W^{d-1}\sqrt{2\pi}S(t_j)}
   \exp\!\left[-\frac{\mu'(t_j)^2y^2}{2S^2(t_j)}\right]    \tag{4.2}
\]

in \(C^2([-L,L])\).  Equivalently, after accounting for time scaling,

\[
  \varepsilon^{r+1}\partial_t^r
  a_{j,\varepsilon}(t_j+\varepsilon y)
  \longrightarrow A_j^{(r)}(y),\qquad r=0,1,2.             \tag{4.3}
\]

The common factor in (2.10) does not change the leading local Gaussian:

\[
  \varepsilon^{r+1}\partial_t^r
  g_{j,\varepsilon}(t_j+\varepsilon y)
  \longrightarrow A_j^{(r)}(y),\qquad r=0,1,2,             \tag{4.4}
\]

under (3.3).  Because \(m\) is fixed and finite, choose one common
\(0<L_0<L\) small enough that \(A_j''(y)<0\) for \(|y|\leq L_0\) for every
\(j\).  At the endpoints,
\(A_j'(-L_0)>0\) and \(A_j'(L_0)<0\).  Thus the own-channel derivative and
negative-curvature margins on

\[
  I_{j,\varepsilon}
  =[t_j-L_0\varepsilon,t_j+L_0\varepsilon]                 \tag{4.5}
\]

are respectively of orders \(\varepsilon^{-2}\) and
\(\varepsilon^{-3}\).
After decreasing the common upper bound on \(\varepsilon\), these intervals
are pairwise disjoint and each lies in the corresponding component of
\(I_*\).

#### Proof

Define

\[
 h_{j,\varepsilon}(y)
 =\frac{c_j-\mu(t_j+\varepsilon y)}{\varepsilon},\qquad
 S_{j,\varepsilon}(y)=S(t_j+\varepsilon y).
\]

Taylor's theorem on the fixed compact \(y\)-interval gives convergence in
\(C^2([-L,L])\),

\[
 h_{j,\varepsilon}\longrightarrow-\mu'(t_j)y,qquad
 S_{j,\varepsilon}\longrightarrow S(t_j)>0.
\]

Substitution into the exact formula (2.11), followed by smooth composition,
proves (4.2) in \(C^2\).  Since

\[
 \partial_y^r\{\varepsilon
 a_{j,\varepsilon}(t_j+\varepsilon y)\}
 =\varepsilon^{r+1}\partial_t^r
 a_{j,\varepsilon}(t_j+\varepsilon y),
\]

this is equivalent to (4.3).  Apply the product rule to
\(g_{j,\varepsilon}=c_{d,\varepsilon}a_{j,\varepsilon}\) and use (3.3) to
obtain (4.4).  The limiting Gaussian has a strictly negative second derivative
on a sufficiently small symmetric interval and the declared endpoint slope
signs.  Uniform \(C^2\) convergence then supplies positive constants
\(\alpha_j,\kappa_j\), independent of small \(\varepsilon\), such that

\[
 \begin{aligned}
  \partial_tg_{j,\varepsilon}(t_j-L_0\varepsilon)
     &\ge \alpha_j\varepsilon^{-2},\\
  \partial_tg_{j,\varepsilon}(t_j+L_0\varepsilon)
     &\le-\alpha_j\varepsilon^{-2},\\
  \sup_{t\in I_{j,\varepsilon}}
  \partial_t^2g_{j,\varepsilon}(t)
     &\le-\kappa_j\varepsilon^{-3}.
 \end{aligned}                                             \tag{4.6}
\]

\(\square\)

### Lemma 4.2 (cross-channel exponential bound)

For \(i\ne j\), strict monotonicity and the positive separation of the target
times give

\[
  \inf_{t\in I_{j,\varepsilon}}|c_i-\mu(t)|\geq d_{ij}>0   \tag{4.7}
\]

for all sufficiently small \(\varepsilon\).  Differentiating (2.11) therefore
gives, for \(r=0,1,2\),

\[
  \sup_{t\in I_{j,\varepsilon}}
  |\partial_t^r g_{i,\varepsilon}(t)|
  \leq C_{ijr}\varepsilon^{-M_r}e^{-q_{ij}/\varepsilon^2}. \tag{4.8}
\]

Exponential cross-channel decay dominates the polynomial own-channel
margins.

#### Proof

Because \(c_i=\mu(t_i)\ne\mu(t_j)=c_j\), continuity on the shrinking interval
allows, for example, \(d_{ij}=|c_i-c_j|/2\) after decreasing
\(\varepsilon_0\).  Formula (2.11) is an \(\varepsilon^{-1}\) prefactor times
the exponential of a smooth function divided by \(\varepsilon^2\).
Differentiating at most twice in time introduces only a fixed polynomial power
of \(\varepsilon^{-1}\).  Lemma 3.1 bounds the common contact factor and its
first two derivatives.  Absorbing all fixed powers into \(M_r\) gives (4.8).
\(\square\)

## 5. The direct physical theorem

### Theorem 5.1 (at least m modes in every fixed finite dimension)

Fix finite integers \(d\ge2\) and \(m\ge1\), all dimension-sized model data,
target times satisfying (3.1), and weights in a compact
simplex-interior set

\[
  w_j\geq w_{\min}>0,\qquad\sum_jw_j=1.                    \tag{5.1}
\]

Assume this set is nonempty, equivalently \(0<w_{\min}\le1/m\).  The finite
dimension, all model parameters, target times, and \(m\) are fixed before
\(\varepsilon\) is varied.

Under (2.1)--(3.4), there exists \(\varepsilon_0>0\), depending on all these
frozen data and on \(w_{\min}\), such that, for every
\(0<\varepsilon<\varepsilon_0\), the exact continuum free-exposure mixture
\(G_\varepsilon(\cdot;w)\) has exactly one nondegenerate local maximum in each
interval \(I_{j,\varepsilon}\), and at least one intervening local minimum
between every consecutive pair.  In particular it has at least \(m\) modes
on \(I\), uniformly over the declared compact weight set.  Extra critical
points outside or between the certified intervals are not excluded.

For every such fixed \(\varepsilon\), there is a
\(B_0(\varepsilon)>0\), uniform over the same weight set, such that the full
Doi reaction-time density \(f_{B,\varepsilon}\) has exactly one nondegenerate
local maximum in each \(I_{j,\varepsilon}\), and hence at least \(m\) modes,
for every \(0<B<B_0(\varepsilon)\).  This conclusion is pointwise in the
fixed finite integers \(d\) and \(m\).  It is not a theorem uniform in either,
a \(d\to\infty\) statement, or a theorem for localized catalyst patches or
arbitrary spatial configurations.

#### Proof

For the \(j\)-th interval, Lemma 4.1 and \(w_j\ge w_{\min}\) give own-channel
endpoint-slope margins at least
\(w_{\min}\alpha_j\varepsilon^{-2}\) and a negative-curvature margin at
least \(w_{\min}\kappa_j\varepsilon^{-3}\).  Lemma 4.2, summed over the fixed
finite set \(i\ne j\), is smaller than half of all these margins for
sufficiently small \(\varepsilon\), uniformly over weights because
\(0\le w_i\le1\).  Consequently

\[
 \begin{aligned}
  \partial_tG_\varepsilon(t_j-L_0\varepsilon;w)&>0,\\
  \partial_tG_\varepsilon(t_j+L_0\varepsilon;w)&<0,\\
  \partial_t^2G_\varepsilon(t;w)&<0
       \quad(t\in I_{j,\varepsilon}).
 \end{aligned}                                             \tag{5.2}
\]

The derivative is strictly decreasing on the interval and changes sign, so
it has exactly one zero there and that zero is a nondegenerate maximum.  At
the right endpoint of \(I_{j,\varepsilon}\) the derivative is negative, while
at the left endpoint of \(I_{j+1,\varepsilon}\) it is positive.  Continuity
and compactness imply that \(G_\varepsilon\) attains a minimum on the closed
gap between those endpoints.  The derivative signs exclude both endpoints,
so at least one minimizer is interior and hence is a local minimum; it need
not be nondegenerate.  This proves the free-exposure statement without
invoking an unstated channel lemma.

For fixed \(\varepsilon>0\), every Gaussian catalyst profile is bounded, the
control set is finite dimensional and compact, and the initial law satisfies
the weighted-space conditions (2.6).  The unbounded fixed-finite-\(d\) OU
quotient therefore falls under Corollary 2.2 of
`pde_mixed_jet_theorem.md`.  Its weak-reactivity mixed-jet estimate gives

\[
 F_{B,\varepsilon}=f_{B,\varepsilon}/B
 \longrightarrow G_\varepsilon
 \quad\hbox{in }C^2(I),\qquad B\downarrow0,                 \tag{5.3}
\]

uniformly over the weight set, with constants allowed to depend on the now
fixed \(\varepsilon\).  The strict inequalities (5.2) persist for all
sufficiently small positive \(B\), proving one unique nondegenerate Doi
maximum in each interval.  Their endpoint derivative signs also preserve at
least one intervening local minimum by the same compact-gap argument.  No
estimate is uniform as
\(\varepsilon\downarrow0\), so this step is taken only after fixing
\(\varepsilon\).  \(\square\)

### Corollary 5.2 (asymptotically comparable peaks)

The limiting own-channel peak coefficient is

\[
  H_j=\{W^{d-1}\sqrt{2\pi}S(t_j)\}^{-1}.                    \tag{5.4}
\]

Choose the normalized weights

\[
  w_j=\frac{H_j^{-1}}{\sum_{i=1}^mH_i^{-1}}
      =\frac{S(t_j)}{\sum_{i=1}^mS(t_i)}.                  \tag{5.5}
\]

Let \(t^*_{j,\varepsilon}\) be the certified maximum in
\(I_{j,\varepsilon}\).  Lemma 4.1, strict local concavity, and the
exponentially small cross channels imply

\[
 \frac{t^*_{j,\varepsilon}-t_j}{\varepsilon}\longrightarrow0,
 \qquad
 \varepsilon G_\varepsilon(t^*_{j,\varepsilon};w)
 \longrightarrow w_jH_j.                                  \tag{5.6}
\]

Thus (5.5) equalizes the leading free-exposure peak heights, and for fixed
finite \(m\) the ratio of the smallest to largest certified peak tends to one
as \(\varepsilon\downarrow0\).

The correct local integral statement is

\[
 \int_{I_{j,\varepsilon}}G_\varepsilon(t;w)\,dt
 \longrightarrow
 w_j\int_{-L_0}^{L_0}A_j(y)\,dy\in(0,\infty).              \tag{5.7}
\]

This is an order-one **free-exposure area**, not probability mass because
\(G_\varepsilon\) is not a normalized density on the full time half-line.
After fixing \(\varepsilon\), (5.3) gives

\[
 \int_{I_{j,\varepsilon}}f_{B,\varepsilon}(t;w)\,dt
 =B\int_{I_{j,\varepsilon}}G_\varepsilon(t;w)\,dt+O(B^2),
 \qquad B\downarrow0.                                     \tag{5.8}
\]

The left side is Doi event mass and is order \(B\) in the sequential limit.
An absolute observability floor still requires a nonempty overlap between a
lower bound on \(B\) and the theorem's upper bound \(B_0(\varepsilon)\).
Neither (5.8) nor its remainder is asserted uniformly in \(\varepsilon\).

## 6. What this theorem does and does not replace

The theorem replaces the **need** for a global GIG-to-physical realization
theorem only for the bounded statement: for each prescribed fixed finite
\(m\), an \(m\)-dependent, epsilon-dependent OU slab family realizes at least
\(m\) physical continuum Doi modes after the sequential limits.  It does not
show that one fixed configuration realizes arbitrary \(m\).  The GIG theorem
remains useful as a transport-independent separated-clock construction and as
design context.

It does not replace the following numerical and physical gates:

1. a resolved finite-parameter \(d=2\) cusp/fold phase portrait, rather than
   only an asymptotic existence family;
2. continuum/box/independent validation of the now-available fixed-control
   positive-budget physical-`d=2` example with declared prominence and event
   mass;
3. an independent solver and box/truncation or analytic-kernel error bounds;
4. a controlled \(d=3\) example;
5. quantitative information on how \(B_0(\varepsilon)\) deteriorates as
   patches narrow or as \(m\) grows.

Further scope restrictions are structural:

6. the catalyst is a longitudinal slab uniform in the transverse
   common-centre directions, not an arbitrary localized \(d\)-dimensional
   patch;
7. the relative deterministic trajectory is deliberately kept inside contact
   near every designed peak, so the theorem embeds the clocks in an exact
   encounter operator but does not attribute the modes to nontrivial
   approach/separation dynamics;
8. the proof certifies at least \(m\) local maxima and does not rule out extra
   early, late, or interstitial extrema; and
9. the current Doi transfer is pointwise in each fixed finite integer
   \(d\ge2\); its constants, dimensional budget, amplitudes, event masses, and
   \(B_0\) are not uniform or compared across dimensions.

The limits \(\varepsilon\downarrow0\) and \(B\downarrow0\) are sequential:
first choose a sufficiently small but fixed physical geometry parameter
\(\varepsilon\), then choose \(B<B_0(\varepsilon)\).  No uniform interchange
of those limits is claimed.  The patch centres, patch widths, and admissible
\(\varepsilon_0\) depend on the prescribed finite \(m\) and target times.
