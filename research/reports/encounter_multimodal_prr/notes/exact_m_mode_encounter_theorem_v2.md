# Exact-\(m\) theorem for conserved-reactivity encounter clocks, version 2

Date: 2026-07-14  
Status: **RIGOROUS REPAIR CANDIDATE / SELF-AUDIT REQUIRED / INDEPENDENT
RE-AUDIT REQUIRED / NOT A MANUSCRIPT CLAIM**

## 1. Purpose, repair boundary, and result

This version preserves
`exact_m_mode_encounter_theorem_candidate.md` byte for byte and replaces its
unproved complement argument.  Round 112 found that at a fixed
\(C\sigma^2\) distance from an adjacent-component crossover, the component
ratio is \(e^{-C\Delta}\), a constant rather than
\(e^{-q/\sigma^2}\).  Exponential single-component dominance therefore
cannot be asserted on the whole complement of a crossover layer.

The repair has four steps.

1. Prove the global \(2m-1\) zero bound for a common-variance Gaussian
   mixture, including finiteness of the real zero set and multiplicities.
2. Construct \(m\) peak roots and \(m-1\) valley roots.  A valley is centred
   at the **weighted equality point**

   \[
   s_j(\sigma,w)=\frac{c_j+c_{j+1}}2
    +\frac{\sigma^2}{c_{j+1}-c_j}
      \log\frac{w_j}{w_{j+1}},
   \]

   and the pure-mixture valley lies at
   \(s_j+O(\sigma^4)\), uniformly on the compact weight set.
3. Prove a quantitative posterior-sector lemma.  It gives a signed lower
   bound for \(|\partial_x\log H|\) on every tail and every inter-root sector,
   including crossover edges where the adjacent ratio is only \(O(1)\).
4. Use peak boxes of width \(O(\sigma^2)\) and valley boxes of width
   \(O(\sigma^4)\).  A positive factor with bounded first two logarithmic time
   derivatives moves peak roots by \(O(\sigma^2)\), moves valley roots by
   \(O(\sigma^4)\), and cannot create a root on the certified complement.

The resulting theorem is:

> For every fixed finite \(d\ge2\), fixed finite \(m\ge1\), compact positive
> time window, and compact simplex-interior allocation family, the declared
> narrow-slab Doi family has exactly \(m\) nondegenerate reaction-time maxima
> and \(m-1\) nondegenerate minima after first taking the slab/noise parameter
> \(\varepsilon>0\) sufficiently small and then taking the installed budget
> \(B>0\) sufficiently small.

The theorem remains pointwise in fixed \(d,m\), sequential in
\(\varepsilon,B\), and nonquantitative in the useful size of \(B\).  Its
relative contact factor is asymptotically saturated on the theorem window;
this is an analytical backbone, not by itself a nontrivial encounter-dynamics
explanation or a PRR-complete result.

## 2. Exact physical reduction and pinned hypotheses

### 2.1 Fixed-finite-dimensional quotient

Fix finite integers \(d\ge2\) and \(m\ge1\), a transverse period \(W>0\), a
contact radius \(0<a<W/2\), and a compact positive time window
\(I=[\tau,T]\subset(0,\infty)\).  Use the exact quotient

\[
 (Z,R_\parallel,R_\perp)
 \in\mathbb R\times\mathbb R\times\mathbb T_W^{d-1}
\]

from `direct_physical_multimode_theorem.md`.  The midpoint obeys

\[
 dZ_t=-\gamma(Z_t-\bar z)\,dt
       +\varepsilon\sqrt{D_0}\,dW_t,
 \qquad
 Z_0\sim N\!\left(z_0,
     \varepsilon^2\frac{D_0}{2\gamma}\right),
 \tag{2.1}
\]

where \(D_0,\gamma>0\) and \(z_0\ne\bar z\).  Hence

\[
 \mu(t)=\bar z+(z_0-\bar z)e^{-\gamma t},
 \qquad
 \operatorname{Var}Z_t
 =\varepsilon^2\frac{D_0}{2\gamma}
 \tag{2.2}
\]

for every \(t\).  This is a constant variance coefficient, not a stationary
mean.

The relative process is

\[
 \begin{aligned}
 dR_{\parallel,t}
   &=-\gamma R_{\parallel,t}\,dt
     +2\varepsilon\sqrt{D_0}\,dW_{\parallel,t},\\
 dR_{\perp,t}
   &=2\varepsilon\sqrt{D_0}\,dW_{\perp,t}\pmod W,
 \end{aligned}
 \tag{2.3}
\]

independent of \(Z\), with

\[
 R_{\parallel,0}\sim
 N(r_{\parallel,0},\varepsilon^2u_0^2),
 \qquad
 R_{\perp,0}\sim
 \text{wrapped }N(r_{\perp,0},\varepsilon^2\Sigma_{\perp,0}).
 \tag{2.4}
\]

Assume

\[
 u_0>0,
 \qquad u_0^2<\frac{4D_0}{\gamma},
 \qquad \Sigma_{\perp,0}\succ0.
 \tag{2.5}
\]

Together with
\(D_0/(2\gamma)<D_0/\gamma\), these are the weighted-space initial-law
hypotheses used by Corollary 2.2 of `pde_mixed_jet_theorem.md`.  Independence,
the minimum-image contact convention, and every covariance in (2.1)--(2.5)
are part of the theorem, not tacit background.

### 2.2 Orientation and dimensionless longitudinal coordinate

The sign of \(\mu'\) is constant on \(I\).  Let

\[
 \varsigma=\operatorname{sgn}\mu'(t)\in\{-1,1\}
\]

and fix a physical reference length \(\ell_0>0\).  Define the dimensionless,
strictly increasing coordinate

\[
 x(t)=\frac{\varsigma\mu(t)}{\ell_0},
 \qquad \inf_Ix'(t)=v_0>0.
 \tag{2.6}
\]

Choose

\[
 \tau<t_1<\cdots<t_m<T,
 \qquad c_j=x(t_j),
 \qquad c_1<\cdots<c_m.
 \tag{2.7}
\]

The physical catalyst centre is
\(\varsigma\ell_0c_j=\mu(t_j)\).  Thus coordinate reversal transforms the
trajectory and every centre together; the symbol \(c_j\) is never used for
both orientations.

Fix \(\rho>0\), set

\[
 S_*^2=\frac{D_0}{2\gamma}+\rho^2,
 \qquad
 \sigma=\frac{\varepsilon S_*}{\ell_0},
 \tag{2.8}
\]

and work below in the dimensionless \(x,c,\sigma\) variables.  Every
logarithm therefore has a dimensionless argument.  The physical Gaussian
profiles retain width \(\varepsilon\rho\).

### 2.3 Contact and conserved reactivity

Let

\[
 r_*(t)=(r_{\parallel,0}e^{-\gamma t},r_{\perp,0})
\]

be the deterministic relative trajectory.  Impose the whole-window interior
condition

\[
 \sup_{t\in I}|r_*(t)|_{\rm mi}\le a-\eta
 \tag{2.9}
\]

for some \(\eta>0\).  With
\(c_{d,\varepsilon}(t)=\Pr\{|R_t|_{\rm mi}<a\}\), the Gaussian-image lemma in
the direct theorem gives, for \(r=0,1,2\),

\[
 \|\partial_t^r(c_{d,\varepsilon}-1)\|_{L^\infty(I)}
 \le C_{r,d}\varepsilon^{-N_{r,d}}e^{-q_d/\varepsilon^2}.
 \tag{2.10}
\]

For sufficiently small \(\varepsilon\), \(c_{d,\varepsilon}\ge1/2\) and

\[
 \begin{aligned}
 \|\partial_t\log c_{d,\varepsilon}\|_\infty
 &\le2\|\partial_tc_{d,\varepsilon}\|_\infty,\\
 \|\partial_t^2\log c_{d,\varepsilon}\|_\infty
 &\le2\|\partial_t^2c_{d,\varepsilon}\|_\infty
     +4\|\partial_tc_{d,\varepsilon}\|_\infty^2.
 \end{aligned}
 \tag{2.11}
\]

Thus its first two logarithmic derivatives are uniformly bounded and in fact
exponentially small.

For \(w\) in a nonempty compact simplex-interior set

\[
 \mathcal W_{w_*}
 =\left\{w\in\mathbb R^m:
   \sum_{j=1}^mw_j=1,\quad w_j\ge w_*>0\right\},
 \tag{2.12}
\]

use the normalized physical slab profiles

\[
 \phi_{j,\varepsilon}(z)
 =\frac1{\sqrt{2\pi}\varepsilon\rho}
   \exp\!\left[-\frac{(z-\mu(t_j))^2}
                      {2\varepsilon^2\rho^2}\right]
 \tag{2.13}
\]

and killing field

\[
 K_{B,w,\varepsilon}(Z,R)
 =\mathbf1_{\{|R|_{\rm mi}<a\}}
   \frac{B}{W^{d-1}}
   \sum_{j=1}^mw_j\phi_{j,\varepsilon}(Z).
 \tag{2.14}
\]

Every allocation has the same installed centre-space reactivity \(B\).
Writing \(K_{B,w,\varepsilon}=B V_{w,\varepsilon}\) and denoting the
unkilled semigroup and initial law by \(T_0(t)\) and \(q_0\), independence and
Gaussian convolution give the exact unit-budget free-exposure clock

\[
 G_{\varepsilon,w}(t)
 =B^{-1}\mathbb E[K_{B,w,\varepsilon}(Z_t,R_t)]
 =\langle V_{w,\varepsilon},T_0(t)q_0\rangle
 =\frac{c_{d,\varepsilon}(t)}
 {W^{d-1}\sqrt{2\pi}\,\varepsilon S_*}
 H_{\sigma,w}(x(t)),
 \tag{2.15}
\]

where

\[
 H_{\sigma,w}(x)
 =\sum_{j=1}^mw_j
   \exp\!\left[-\frac{(x-c_j)^2}{2\sigma^2}\right].
 \tag{2.16}
\]

The prefactor outside \(H\) is positive.  Only its logarithmic time
derivatives affect stationary points.

## 3. The pure common-variance mixture

Let \(J=x(I)=[\alpha,\beta]\).  Because the target times are interior,

\[
 \alpha<c_1<\cdots<c_m<\beta.
 \tag{3.1}
\]

For \(m\ge2\), define

\[
 \Delta_j=c_{j+1}-c_j,
 \qquad
 \Delta_* =\min_j\Delta_j>0.
 \tag{3.2}
\]

The case \(m=1\) is handled separately and never uses an empty minimum.

Put

\[
 q_j(x)=w_j e^{-(x-c_j)^2/(2\sigma^2)},
 \quad
 \pi_j(x)=\frac{q_j(x)}{H_{\sigma,w}(x)},
 \quad
 \bar c(x)=\sum_j\pi_j(x)c_j.
 \tag{3.3}
\]

The logarithmic slope and its derivative are exactly

\[
 L_{\sigma,w}(x)
 :=\partial_x\log H_{\sigma,w}(x)
 =\frac{\bar c(x)-x}{\sigma^2},
 \tag{3.4}
\]

\[
 L_{\sigma,w}'(x)
 =\frac{\operatorname{Var}_{\pi(x)}(c)}{\sigma^4}
  -\frac1{\sigma^2}.
 \tag{3.5}
\]

### Lemma 3.1 (finite extended-Chebyshev zero bound)

For distinct real centres and positive weights,
\(H_{\sigma,w}'\) has at most \(2m-1\) real zeros counted with
multiplicity.

#### Proof

Multiplication by a positive function preserves zeros and multiplicities, and

\[
 \sigma^2e^{x^2/(2\sigma^2)}H_{\sigma,w}'(x)
 =\sum_{j=1}^m
 w_j(c_j-x)e^{-c_j^2/(2\sigma^2)}e^{c_jx/\sigma^2}.
 \tag{3.6}
\]

It is enough to prove the following statement.  If

\[
 P_m(x)=\sum_{j=1}^m(a_j+b_jx)e^{\lambda_jx},
 \qquad \lambda_1<\cdots<\lambda_m,
 \tag{3.7}
\]

has no identically zero term, then it has at most \(2m-1\) real zeros counted
with multiplicity.

First, the zero set is finite.  After multiplying by
\(e^{-\lambda_1x}\), the first affine term dominates as \(x\to-\infty\),
while the last affine-exponential term dominates as \(x\to+\infty\).  Each
dominating affine function has a fixed sign sufficiently far in its tail.
Thus all zeros lie in a compact interval.  A nonzero real-analytic function
has only finitely many zeros there.

Induct on \(m\).  The claim for \(m=1\) is the affine zero bound.  For
\(m>1\), let \(Q=e^{-\lambda_1x}P_m\).  The first term of \(Q\) is affine and
vanishes after two derivatives.  For \(j\ge2\),

\[
 \frac{d^2}{dx^2}
 \left[(a_j+b_jx)e^{(\lambda_j-\lambda_1)x}\right]
\]

is a nonzero affine polynomial times
\(e^{(\lambda_j-\lambda_1)x}\), and the positive exponents remain distinct.
If a \(C^2\) function has \(N\) real zeros counted with multiplicity, the
generalized Rolle theorem gives at least \(N-2\) zeros of its second
derivative counted with multiplicity: multiplicity drops at each original
root, and ordinary Rolle supplies the roots between distinct ones.  Hence

\[
 N(Q)-2\le N(Q'')\le2(m-1)-1,
\]

so \(N(P_m)=N(Q)\le2m-1\).  Formula (3.6) has
\(b_j=-w_je^{-c_j^2/(2\sigma^2)}\ne0\), so the statement applies. \(\square\)

### Lemma 3.2 (uniform adjacent-pair isolation)

For each fixed finite centre set and compact weight family, there are
\(C_{\rm iso},q_{\rm iso}>0\) such that, for every \(j<m\),

\[
 \sup_{x\in[c_j,c_{j+1}]}
 \frac{\sum_{k\notin\{j,j+1\}}q_k(x)}{q_j(x)+q_{j+1}(x)}
 \le C_{\rm iso}e^{-q_{\rm iso}/\sigma^2}
 \tag{3.8}
\]

for all sufficiently small \(\sigma\), uniformly in \(w\).  On
\([\alpha,c_1]\), component 1 has the analogous isolation bound, and on
\([c_m,\beta]\), component \(m\) does.

#### Proof

For \(x\in[c_j,c_{j+1}]\) and \(k<j\),

\[
 (x-c_k)^2-(x-c_j)^2
 =(c_j-c_k)(2x-c_j-c_k)
 \ge(c_j-c_k)^2.
 \tag{3.9}
\]

For \(k>j+1\), comparison with \(c_{j+1}\) gives the corresponding positive
lower bound.  There are finitely many centres and \(w_k/w_j\le1/w_*\), so
summation gives (3.8).  The two tail estimates follow from the same
difference-of-squares identity. \(\square\)

Consequently, on a gap \([c_j,c_{j+1}]\), the full posterior mean and variance
differ from those of the adjacent two-component posterior by at most
\(C e^{-q/\sigma^2}\), uniformly in \(x,w\).

### Lemma 3.3 (exact pure topology and root locations)

Uniformly for \(w\in\mathcal W_{w_*}\), all sufficiently small \(\sigma>0\)
give exactly \(m\) simple maxima and \(m-1\) simple minima of
\(H_{\sigma,w}\) on \(J\), with nonzero endpoint derivatives.

The \(j\)-th maximum \(p_j(\sigma,w)\) satisfies

\[
 p_j(\sigma,w)=c_j+O(e^{-q/\sigma^2}),
 \qquad
 L'(p_j)=-\sigma^{-2}+o(\sigma^{-2}).
 \tag{3.10}
\]

For \(m\ge2\), the \(j\)-th minimum \(r_j(\sigma,w)\) satisfies

\[
 r_j(\sigma,w)=s_j(\sigma,w)+O(\sigma^4),
 \tag{3.11}
\]

where

\[
 s_j(\sigma,w)
 =\frac{c_j+c_{j+1}}2
  +\frac{\sigma^2}{\Delta_j}\log\frac{w_j}{w_{j+1}},
 \tag{3.12}
\]

and

\[
 L'(r_j)=\frac{\Delta_j^2}{4\sigma^4}
          +O(\sigma^{-2}).
 \tag{3.13}
\]

All big-\(O\) constants are uniform on the compact weight set.

#### Proof

Near \(c_j\), Lemma 3.2 and its one-centre variant give

\[
 \bar c(x)-c_j=O(e^{-q/\sigma^2})
 \tag{3.14}
\]

uniformly for \(|x-c_j|\le A\sigma^2\), for any fixed \(A\).  Hence

\[
 L(x)=\frac{c_j-x}{\sigma^2}
       +O(\sigma^{-2}e^{-q/\sigma^2}),
 \qquad
 L'(x)=-\sigma^{-2}
       +O(\sigma^{-4}e^{-q/\sigma^2}).
 \tag{3.15}
\]

At \(c_j-\sigma^2\) the slope is positive, at
\(c_j+\sigma^2\) it is negative, and \(L'<0\) throughout.  This gives one
simple maximum and (3.10).

For a gap, let \(v_j=(c_j+c_{j+1})/2\),
\(\ell_j=\log(w_j/w_{j+1})\), and let

\[
 h_j=\frac{\log9}{\Delta_j}.
\]

For the isolated adjacent pair, the posterior odds satisfy exactly

\[
 \frac{q_{j+1}(x)}{q_j(x)}
 =\exp\!\left[\frac{\Delta_j(x-s_j)}{\sigma^2}\right].
 \tag{3.16}
\]

Thus at \(x=s_j-h_j\sigma^2\) the adjacent posterior masses are
\((9/10,1/10)\), and at \(x=s_j+h_j\sigma^2\) they are
\((1/10,9/10)\).  Lemma 3.2 changes these values only exponentially.  The full
posterior variance on this crossover interval therefore obeys, after reducing
\(\sigma_0\),

\[
 \operatorname{Var}_{\pi(x)}(c)
 \ge\kappa_0\Delta_*^2
 \tag{3.17}
\]

for one \(\kappa_0>0\) independent of \(j,w,\sigma\).  Hence

\[
 L'(x)\ge\frac{\kappa_v}{\sigma^4}>0
 \tag{3.18}
\]

there, for a uniform \(\kappa_v>0\).  Its left endpoint has
\(L\le-\Delta_j/(5\sigma^2)\) and its right endpoint has
\(L\ge\Delta_j/(5\sigma^2)\), after another harmless reduction of
\(\sigma_0\).  It contains one simple minimum root.

At \(s_j\), the two-component posterior mean equals \(v_j\), so

\[
 L(s_j)=-\frac{\ell_j}{\Delta_j}
         +O(\sigma^{-2}e^{-q/\sigma^2})=O(1)
 \tag{3.19}
\]

uniformly because
\(|\ell_j|\le\log(1/w_*)\).  The mean-value theorem with (3.18) gives
\(|r_j-s_j|=O(\sigma^4)\).  At the root, adjacent posterior masses equal
\(1/2+O(\sigma^2)\); substituting in (3.5) gives (3.13).

We have constructed \(m+(m-1)=2m-1\) distinct simple stationary points.
Lemma 3.1 permits no others and forces the displayed list to be complete.
The fixed endpoint separations \(c_1-\alpha>0\) and
\(\beta-c_m>0\), together with tail isolation, give
\(L(\alpha)>0>L(\beta)\).  For \(m=1\), the peak argument and one-term
identity \(L=(c_1-x)/\sigma^2\) give the full result directly. \(\square\)

## 4. Quantitative complement exclusion for a slow positive factor

The zero count in Lemma 3.1 cannot be applied after multiplication by a
nonconstant factor.  This section supplies the missing full-window estimate.

### Lemma 4.1 (posterior-sector certificate)

Fix any \(K>0\).  There are constants

\[
 A_{\rm p}>0,\quad A_{\rm v}>0,
 \quad C_{\rm p},C_{\rm v},\kappa_{\rm p},\kappa_{\rm v}>0,
 \quad\sigma_K>0,
 \tag{4.1}
\]

depending only on the fixed centre set, \(J\), \(w_*\), and \(K\), such that
for every \(0<\sigma<\sigma_K\) and every admissible \(w\):

1. the peak boxes

   \[
   P_j=[c_j-A_{\rm p}\sigma^2,
        c_j+A_{\rm p}\sigma^2]
   \tag{4.2}
   \]

   and valley boxes

   \[
   V_j=[r_j-A_{\rm v}\sigma^4,
        r_j+A_{\rm v}\sigma^4]
   \tag{4.3}
   \]

   are pairwise disjoint and contained in \((\alpha,\beta)\);
2. on each peak box,

   \[
   |L|\le C_{\rm p},
   \qquad L'\le-\kappa_{\rm p}\sigma^{-2};
   \tag{4.4}
   \]

3. on each valley box,

   \[
   |L|\le C_{\rm v},
   \qquad L'\ge\kappa_{\rm v}\sigma^{-4};
   \tag{4.5}
   \]

4. the box-boundary signs are

   \[
   \begin{array}{c|cc}
   &\text{left boundary}&\text{right boundary}\\ \hline
   P_j&L\ge2K&L\le-2K\\
   V_j&L\le-2K&L\ge2K;
   \end{array}
   \tag{4.6}
   \]

5. on the entire complement of the open boxes,

   \[
   |L(x)|\ge2K,
   \tag{4.7}
   \]

   with alternating signs

   \[
   +\;P_1\;-\;V_1\;+\;P_2\;-\;\cdots\;+\;P_m\;-.
   \tag{4.8}
   \]

For \(m=1\), omit every valley quantity.

#### Proof

Choose \(A_{\rm p}\) so large that \(A_{\rm p}/2\ge2K\).  Formula (3.15)
then proves (4.4), the peak rows of (4.6), and one uniform \(C_{\rm p}\),
because \(L=(c_j-x)/\sigma^2+o(1)\) on a peak box of fixed scaled width.
For the full outer tails, the posterior mean satisfies

\[
 \bar c(x)\in[c_1,c_m],\qquad
 x\le c_1-A_{\rm p}\sigma^2\Rightarrow L(x)\ge A_{\rm p},\qquad
 x\ge c_m+A_{\rm p}\sigma^2\Rightarrow L(x)\le-A_{\rm p}.
\]

This supplies the required signed tail bounds uniformly and without extending
the local expansion (3.15) beyond its stated neighbourhood.

It remains to cover every gap without the false claim of exponential
dominance at a crossover edge.  Fix a gap \([c_j,c_{j+1}]\), suppress \(j\),
and write \(\Delta=c_{j+1}-c_j\), \(s=s_j\), and

\[
 p(x)=\frac{q_{j+1}(x)}{q_j(x)+q_{j+1}(x)}
 =\frac1{1+\exp[-\Delta(x-s)/\sigma^2]}.
 \tag{4.9}
\]

The adjacent-pair mean is \(c_j+\Delta p(x)\).  Lemma 3.2 changes this mean
by at most \(Ce^{-q/\sigma^2}\).

Use the crossover interval

\[
 C_j=[s_j-h_j\sigma^2,s_j+h_j\sigma^2],
 \qquad h_j=\frac{\log9}{\Delta_j}.
 \tag{4.10}
\]

At its left edge, the adjacent ratio is \(1/9\), and at its right edge it is
\(9\).  These are \(O(1)\), not exponentially small.  What matters is that
both posterior masses are bounded below on \(C_j\), so (3.18) gives
\(L'\ge\kappa_v\sigma^{-4}\) throughout it.  Conversely,
\(\operatorname{Var}_\pi(c)\le(c_m-c_1)^2\), so
\(|L'|\le C\sigma^{-4}\) there.  Integration across a valley box of width
\(2A_{\rm v}\sigma^4\) therefore supplies the uniform \(C_{\rm v}\) in
(4.5).

The pure root satisfies \(L(r_j)=0\).  Choose
\(A_{\rm v}\) so large that
\(\kappa_vA_{\rm v}\ge2K\).  Because
\(A_{\rm v}\sigma^4=o(\sigma^2)\), the valley box lies inside \(C_j\).
Integration of (3.18) from \(r_j\) gives (4.5), the valley rows of (4.6), and
\(|L|\ge2K\) on
\(C_j\setminus\operatorname{int}V_j\), with the required negative/positive
signs.

Now consider the left outer sector

\[
 [c_j+A_{\rm p}\sigma^2,
   s_j-h_j\sigma^2].
 \tag{4.11}
\]

Split it at \(c_j+\Delta_j/4\).  On the part nearer \(c_j\), the right
adjacent component and all other components are exponentially small relative
to component \(j\), uniformly until that fixed split point.  Therefore

\[
 \bar c(x)-x
 \le-\tfrac12A_{\rm p}\sigma^2,
 \qquad L(x)\le-A_{\rm p}/2\le-2K.
 \tag{4.12}
\]

On the remaining part, monotonicity of (4.9) and the left crossover edge give
\(p(x)\le1/10\), whereas
\(x-c_j\ge\Delta_j/4\).  Hence the adjacent-pair mean obeys

\[
 c_j+\Delta_jp(x)-x
 \le\frac{\Delta_j}{10}-\frac{\Delta_j}{4}
 =-\frac{3\Delta_j}{20}.
 \tag{4.13}
\]

The exponentially small nonadjacent correction preserves this sign and makes
\(|L|\) diverge like \(\sigma^{-2}\).  This covers the left sector even at
the crossover edge, where the adjacent ratio is exactly \(1/9\).

The symmetric split at \(c_{j+1}-\Delta_j/4\) gives

\[
 L(x)\ge2K
 \tag{4.14}
\]

on the right outer sector
\([s_j+h_j\sigma^2,c_{j+1}-A_{\rm p}\sigma^2]\).  The fixed centre and
endpoint separations make all peak, crossover, and endpoint boxes disjoint
for one common sufficiently small \(\sigma_K\).  Finiteness of \(m\) and the
uniform weight-ratio bound make every constant common to all gaps and
weights.  Equations (4.12)--(4.14), the crossover integration, and the tails
cover every point of \(J\), proving (4.7)--(4.8). \(\square\)

### Theorem 4.2 (slow positive factor preserves exactly \(m\) modes)

Let \(x\in C^2(I)\) be strictly increasing with
\(v_0=\inf_Ix'>0\).  Let \(a_\sigma\in C^2(I)\) be positive and suppose

\[
 M_0:=\sup_{\sigma<\sigma_0}
       \|\partial_t\log a_\sigma\|_\infty<\infty,
 \qquad
 M_1:=\sup_{\sigma<\sigma_0}
       \|\partial_t^2\log a_\sigma\|_\infty<\infty.
 \tag{4.15}
\]

Uniformly for \(w\in\mathcal W_{w_*}\), all sufficiently small \(\sigma>0\)
give exactly \(m\) nondegenerate maxima and \(m-1\) nondegenerate minima of

\[
 F_{\sigma,w}(t)=a_\sigma(t)H_{\sigma,w}(x(t))
 \tag{4.16}
\]

on \(I\), ordered alternately, with nonzero endpoint derivatives.  Relative
to the pure roots in the \(x\) coordinate,

\[
 x(t_{j,\sigma}^{\max})-p_j(\sigma,w)=O(\sigma^2),
 \tag{4.17}
\]

\[
 x(t_{j,\sigma}^{\min})-r_j(\sigma,w)=O(\sigma^4),
 \tag{4.18}
\]

uniformly in \(w\).  In particular, combining (3.11) and (4.18),

\[
 x(t_{j,\sigma}^{\min})
 =s_j(\sigma,w)+O(\sigma^4).
 \tag{4.19}
\]

#### Proof

Set

\[
 b_\sigma=\partial_t\log a_\sigma,
 \qquad
 D_{\sigma,w}(t)
 =\partial_t\log F_{\sigma,w}(t)
 =b_\sigma(t)+x'(t)L_{\sigma,w}(x(t)).
 \tag{4.20}
\]

Because \(F>0\), its stationary points are exactly the zeros of \(D\), and

\[
 D'=b_\sigma'+x''L+(x')^2L'.
 \tag{4.21}
\]

Choose

\[
 K>\frac{M_0+1}{v_0}
 \tag{4.22}
\]

and apply Lemma 4.1.  On the complement of the open root boxes,
\(|x'L|\ge2v_0K>M_0\), with the alternating sign (4.8).  Hence \(D\) has no
complement zero and has the same alternating complement signs.

On a peak box, \(|L|\le C_{\rm p}\) and
\(L'\le-\kappa_{\rm p}\sigma^{-2}\).  Thus

\[
 D'\le M_1+\|x''\|_\infty C_{\rm p}
       -v_0^2\kappa_{\rm p}\sigma^{-2}<0
 \tag{4.23}
\]

for small \(\sigma\).  The boundary signs in (4.6) give one and only one
zero, and at that zero
\(F''=FD'<0\), so it is a nondegenerate maximum.

On a valley box, \(|L|\le C_{\rm v}\) and
\(L'\ge\kappa_{\rm v}\sigma^{-4}\).  Hence

\[
 D'\ge-M_1-\|x''\|_\infty C_{\rm v}
       +v_0^2\kappa_{\rm v}\sigma^{-4}>0.
 \tag{4.24}
\]

Its boundary signs give one and only one zero, with
\(F''=FD'>0\), a nondegenerate minimum.  The endpoint points lie in the
certified tails, so their derivatives are nonzero.

At a slow-factor root in a peak box, \(|L|\le M_0/v_0\).  Integrating the
uniform negative \(L'=\Theta(\sigma^{-2})\) from the pure root gives
(4.17).  Integrating the positive
\(L'=\Theta(\sigma^{-4})\) in a valley box gives (4.18).  All constants in
Lemma 4.1 and (4.15)--(4.24) are uniform in \(w\), proving the uniform
statement. \(\square\)

## 5. Exact-\(m\) Doi theorem and weak-budget transfer

### Theorem 5.1 (exact \(m\) Doi modes for fixed finite \((d,m)\))

Fix all data in Section 2, including:

1. finite \(d\ge2\), finite \(m\ge1\), \(I=[\tau,T]\subset(0,\infty)\),
   \(W>0\), and \(0<a<W/2\);
2. the midpoint OU law (2.1) with constant variance coefficient
   \(D_0/(2\gamma)\) and \(z_0\ne\bar z\);
3. the independent relative law (2.3)--(2.5), including
   \(u_0^2<4D_0/\gamma\) and \(\Sigma_{\perp,0}\succ0\);
4. target times strictly inside \(I\), with every catalyst centre transformed
   consistently with the increasing coordinate (2.6)--(2.7);
5. normalized Gaussian slabs of physical width \(\varepsilon\rho\);
6. the whole-window contact-interior margin (2.9); and
7. the compact allocation set (2.12), with the installed centre-space budget
   (2.14) fixed at \(B\).

Then there is \(\varepsilon_0>0\), depending on all fixed data, such that for
every \(0<\varepsilon<\varepsilon_0\) and every admissible \(w\), the exact
continuum free-exposure clock \(G_{\varepsilon,w}\) has exactly

\[
 m\ \text{nondegenerate maxima and}\
 m-1\ \text{nondegenerate minima}
 \tag{5.1}
\]

on \(I\), ordered alternately, and has no endpoint stationary point.

For each fixed such \(\varepsilon\), there exists
\(B_0(\varepsilon)>0\), uniform over \(w\in\mathcal W_{w_*}\), such that the
**budget-rescaled** Doi reaction-time density

\[
 \mathcal F_{B,\varepsilon,w}(t)
 :=\frac{f_{B,\varepsilon,w}(t)}B
 \tag{5.2}
\]

has the same complete finite-window stationary signature for every
\(0<B<B_0(\varepsilon)\).  Since multiplication by \(B>0\) changes no
stationary point, the same statement holds for the physical reaction density
\(f_{B,\varepsilon,w}\).  The word “rescaled” in (5.2) does not assert that
\(\mathcal F\) integrates to one.

#### Proof

In (2.15), take

\[
 a_\sigma(t)
 =\frac{c_{d,\varepsilon}(t)}
 {W^{d-1}\sqrt{2\pi}\,\varepsilon S_*}.
\]

The scalar denominator has no time derivative, while (2.11) supplies the
uniform logarithmic derivative bounds.  Theorem 4.2 gives (5.1), uniformly in
the compact allocation family.

Fix one such \(\varepsilon>0\).  The root in every peak or valley box is
simple and depends continuously on \(w\) by the implicit-function theorem.
The finite collection of root graphs over compact \(\mathcal W_{w_*}\) is
compact.  The curvature is continuous and nonzero on those graphs, so a
finite subcover supplies root tubes with one uniform signed-curvature margin.
The ordered distance between consecutive root graphs is a positive continuous
function of \(w\), hence has a positive minimum; shrink the tubes below half
that minimum so they are disjoint for every allocation.
On the compact complement of those tubes in
\(I\times\mathcal W_{w_*}\), \(|\partial_tG|\) has a positive minimum.
The two endpoint slopes likewise have positive uniform absolute minima.

For fixed \(\varepsilon\), every Gaussian catalyst is bounded, the initial
law belongs to the weighted space by (2.5), and the fixed-finite-\(d\)
generator satisfies Corollary 2.2 and Theorem 4.1 of
`pde_mixed_jet_theorem.md`.  Therefore

\[
 \sup_{w\in\mathcal W_{w_*}}
 \|\mathcal F_{B,\varepsilon,w}-G_{\varepsilon,w}\|_{C^2(I)}
 \longrightarrow0
 \qquad(B\downarrow0).
 \tag{5.3}
\]

Choose \(B_0(\varepsilon)\) so that the first-derivative error is below the
endpoint and complement margins and the second-derivative error is below the
root-tube curvature margin.  Every tube retains one unique typed root and the
complement retains none. \(\square\)

### Quantifier order

The quantifiers are

\[
 \text{fix }(d,m,\text{all data})
 \;\longrightarrow\;
 0<\varepsilon<\varepsilon_0
 \;\longrightarrow\;
 0<B<B_0(\varepsilon).
 \tag{5.4}
\]

The proof gives neither a useful explicit \(B_0\) nor a lower bound uniform as
\(\varepsilon\downarrow0\).  Valley heights and absolute valley curvatures
are exponentially small, so the existential \(B_0(\varepsilon)\) can be far
below a numerically or experimentally useful budget.

## 6. Encounter significance and novelty ceiling

The theorem is an exact Doi-process embedding, but its whole-window
contact-interior assumption implies

\[
 c_{d,\varepsilon}(t)
 =1+O(\varepsilon^{-N}e^{-q/\varepsilon^2})
 \quad\text{in }C^2(I).
 \tag{6.1}
\]

Thus relative encounter dynamics is an asymptotically saturated common
factor.  It moves the roots within the bounds of Theorem 4.2 but does not
create the modal basis.  The modal basis comes from ordered narrow catalyst
slabs sampled by a monotone, constant-variance midpoint trajectory.

This theorem therefore supports the following statement:

> In an exact fixed-finite-dimensional Doi encounter process, conserved
> allocation among ordered narrow longitudinal catalyst slabs can realize a
> complete prescribed finite mode count in a sequential narrow-noise and weak-
> budget regime.

It does **not** support any of the following statements:

- encounter approach/separation is the cause of the modes;
- the theorem explains a difference between physical dimensions two and
  three;
- one fixed geometry supports arbitrarily many modes;
- the construction works at an observable or useful positive budget;
- Gaussian-mixture zero counting is new;
- multimodal first-passage or heterogeneous reaction-time theory is new; or
- the theorem alone supplies PRR-level significance.

The slow-factor theorem is abstractly valid for a nonconstant positive
encounter factor with uniform logarithmic \(C^2\) bounds.  This note does not
claim a new equal-diffusivity small-noise physical realization in which such a
factor remains nontrivial as \(\varepsilon\downarrow0\).  Instead it retains
the audited model (2.1)--(2.5) and the honest saturated-contact limit (6.1).

PRR promotion still requires a separate finite-parameter result with:

1. contact probability demonstrably different from one on the declared
   window;
2. the same fixed transport, geometry, initial law, supports, and installed
   budget across the compared allocations;
3. a usable common positive budget rather than only existential
   \(B_0(\varepsilon)\);
4. a deterministic full-window root/complement certificate; and
5. independent process-level event-basin mass and survival validation.

## 7. Scope limits

The theorem is not uniform in \(d\), \(m\), or \(\varepsilon\); does not
interchange \(\varepsilon\) and \(B\); does not treat arbitrary localized
patch shapes; does not control topology outside \(I\); and does not provide an
event-mass floor.  The geometry, \(\varepsilon_0\), and
\(B_0(\varepsilon)\) may depend on every fixed datum and on \(m,d\).

For \(m=1\), all gap, separation-minimum, crossover, and valley definitions
are omitted.  The single peak and both endpoint signs follow directly from
the one-component form and Theorem 4.2's peak-box argument.

## 8. Round-112 repair ledger

| Round-112 item | Version-2 disposition |
|---|---|
| P0 false exponential dominance at crossover edge | Replaced by exact adjacent odds, \(O(1)\) edge ratios, posterior-variance crossover bounds, and an exhaustive outer-sector proof in Lemma 4.1. |
| Missing full complement sign bound | Closed by (4.7)--(4.14), covering tails, peak boundaries, both outer gap sectors, crossover-minus-valley sectors, and valley boundaries. |
| Pure zero count did not establish finiteness | Closed by two-tail affine-exponential dominance before generalized Rolle counting. |
| Weighted crossover omitted | Closed by (3.12); pure and slow valleys are both \(s_j+O(\sigma^4)\). |
| Peak and valley shift scales conflated | Closed: slow peak shift is \(O(\sigma^2)\), slow valley shift is \(O(\sigma^4)\). |
| Doi hypotheses implicit | Section 2 and Theorem 5.1 pin contact geometry, covariance, independence, and weighted-space inequalities. |
| Coordinate reversal ambiguity | Closed by the joint orientation transform (2.6)--(2.7). |
| \(m=1\) empty minimum | Closed by a separate one-component clause. |
| Dimensional \(\log\sigma\) | Removed; all longitudinal proof variables are explicitly dimensionless. |
| “normalized” \(f_B/B\) wording | Replaced by “budget-rescaled,” with its mass meaning stated. |
| Encounter significance overread | Section 6 labels saturated contact and keeps nontrivial-contact numerics as a separate PRR gate. |

This file remains a candidate until an independent re-audit checks every
sector inequality, uniform constant, and transfer hypothesis.
