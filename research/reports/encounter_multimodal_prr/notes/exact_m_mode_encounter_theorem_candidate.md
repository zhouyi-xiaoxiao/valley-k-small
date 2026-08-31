# Candidate exact-\(m\) theorem for conserved-reactivity encounter clocks

Date: 2026-07-14  
Status: **NEW THEOREM CANDIDATE / NOT YET INDEPENDENTLY AUDITED / NOT A
MANUSCRIPT CLAIM**

## 1. Purpose

The current direct physical theorem constructs at least \(m\) encounter-time
modes for every fixed finite \(d\ge2\) and fixed finite \(m\), but it permits
extra stationary points outside the certified peak boxes.  This note isolates
a stronger subfamily in which the complete finite-window topology can be
determined:

\[
  m\ \hbox{nondegenerate maxima and}\ m-1\ \hbox{nondegenerate minima}.
\]

The additional structure is a constant midpoint variance coefficient.  It
turns the free longitudinal clocks into a common-scale one-dimensional
Gaussian location mixture along a monotone OU mean.  A uniformly positive,
slow encounter factor moves the stationary points but cannot create new ones
when the common scale is sufficiently small.

This is a candidate theorem until its zero-count, slow-factor perturbation,
and weak-budget transfer have passed an independent proof attack.

## 2. Physical subfamily and exact clock reduction

Use the fixed-finite-\(d\) quotient and normalized Gaussian slabs from
`direct_physical_multimode_theorem.md`.  On a compact window
\(I=[\tau,T]\subset(0,\infty)\), let

\[
 dZ_t=-\gamma(Z_t-\bar z)\,dt+\varepsilon\sqrt{D_0}\,dW_t,
 \qquad
 \mu(t)=\bar z+(z_0-\bar z)e^{-\gamma t},
\]

with \(z_0\ne\bar z\).  Impose the stationary midpoint variance coefficient

\[
 s_0^2=\frac{D_0}{2\gamma}.
\]

Then \(s^2(t)=D_0/(2\gamma)\) for every \(t\).  For a fixed slab-width
coefficient \(\rho>0\), set

\[
 S_*^2=\frac{D_0}{2\gamma}+\rho^2,\qquad
 \sigma=\varepsilon S_*.
\]

Choose

\[
 \tau<t_1<\cdots<t_m<T,\qquad c_j=\mu(t_j).
\]

Reverse the spatial coordinate if necessary, so that
\(x(t)\) is a strictly increasing \(C^2\) version of \(\mu(t)\).  Relabel the
centres so that

\[
 c_1<\cdots<c_m,\qquad c_j=x(t_j).
\]

Assume the deterministic relative trajectory remains a fixed distance inside
the contact ball on the **whole** window \(I\), not merely near the target
times.  The Gaussian image argument in Lemma 3.1 of the direct theorem then
gives, for \(r=0,1,2\),

\[
 \sup_{t\in I}
 |\partial_t^r(c_{d,\varepsilon}(t)-1)|
 \le C_r\varepsilon^{-N_r}e^{-q/\varepsilon^2}.
\]

In particular, for all sufficiently small \(\varepsilon\),
\(c_{d,\varepsilon}>0\), while
\(\partial_t\log c_{d,\varepsilon}\) and its first derivative are uniformly
bounded.

For \(w\) in the compact simplex interior

\[
 \mathcal W_{w_*}
 =\{w:\sum_jw_j=1,\ w_j\ge w_*>0\},
\]

the free-exposure mixture is exactly

\[
 G_{\varepsilon,w}(t)
 =\frac{c_{d,\varepsilon}(t)}
 {W^{d-1}\sqrt{2\pi}\,\varepsilon S_*}
 H_{\sigma,w}(x(t)),
\]

where

\[
 H_{\sigma,w}(x)
 =\sum_{j=1}^m w_j
   \exp\!\left[-\frac{(x-c_j)^2}{2\sigma^2}\right].
\]

All allocations retain the same installed reactivity because only the
simplex weights change.

## 3. A transparent stationary-point bound for the pure mixture

### Lemma 3.1 (at most \(2m-1\) stationary points)

For distinct ordered centres and positive weights,
\(H_{\sigma,w}'\) has at most \(2m-1\) real zeros counted with
multiplicity.

#### Proof

Multiplication by a strictly positive function does not change zeros.  Direct
differentiation gives

\[
 \sigma^2 e^{x^2/(2\sigma^2)}H_{\sigma,w}'(x)
 =\sum_{j=1}^m
 w_j(c_j-x)e^{-c_j^2/(2\sigma^2)}
 e^{c_jx/\sigma^2}.
\]

This is an exponential polynomial

\[
 P_m(x)=\sum_{j=1}^m(a_j+b_jx)e^{\lambda_jx},
 \qquad \lambda_1<\cdots<\lambda_m.
\]

Induct on \(m\).  For \(m=1\), a nonzero affine function times a positive
exponential has at most one zero.  For the induction step, multiply by
\(e^{-\lambda_1x}\), which preserves zeros, and differentiate twice.  The
\(j=1\) affine term disappears, while every remaining term is again an affine
polynomial times an exponential with distinct real exponent.  Generalized
Rolle counting says that if the original function has \(N\) real zeros
counted with multiplicity, its second derivative has at least \(N-2\).
The induction hypothesis bounds the latter by \(2(m-1)-1\), hence
\(N\le2m-1\).  \(\square\)

For fixed separated centres and weights bounded below, the usual
own-component dominance supplies one maximum near every \(c_j\) when
\(\sigma\) is small.  Derivative signs between consecutive peak boxes supply
at least one minimum in every gap.  These are \(2m-1\) distinct stationary
points, so Lemma 3.1 makes the list complete and forces every intervening
root to be simple.

This zero-count fact is classical scale-space/total-positivity territory; it
is not the proposed encounter novelty.  Relevant primary references include
Silverman's Gaussian critical-bandwidth theorem
(JRSS B 43, 97--99, 1981, DOI
`10.1111/j.2517-6161.1981.tb01155.x`) and Carreira-Perpiñán and Williams'
one-dimensional Gaussian-mixture result (LNCS 2695, 625--640, 2003, DOI
`10.1007/3-540-44935-3_44`).

## 4. Stability under the common encounter factor

The pure-mixture zero bound cannot simply be reused after multiplying by a
nonconstant encounter factor.  The required statement is instead a singular
perturbation lemma.

### Lemma 4.1 (slow positive factor preserves the complete topology)

Let \(x\in C^2(I)\) be strictly increasing with
\(\inf_Ix'>0\).  Let \(a_\sigma\in C^2(I)\) be positive and satisfy

\[
 \sup_{\sigma<\sigma_0}
 \left(
 \|\partial_t\log a_\sigma\|_\infty+
 \|\partial_t^2\log a_\sigma\|_\infty
 \right)<\infty.
\]

Fix distinct centres \(c_j=x(t_j)\) in the interior and
\(w\in\mathcal W_{w_*}\).  Uniformly over that compact weight set, for all
sufficiently small \(\sigma>0\),

\[
 F_{\sigma,w}(t)=a_\sigma(t)H_{\sigma,w}(x(t))
\]

has exactly \(m\) nondegenerate maxima and \(m-1\) nondegenerate minima in
\(I\), ordered alternately, and its endpoint derivatives are nonzero.

#### Proof structure

Put

\[
 L_{\sigma,w}(x)=\partial_x\log H_{\sigma,w}(x),\qquad
 b_\sigma(t)=\partial_t\log a_\sigma(t).
\]

Since \(F_{\sigma,w}>0\), its stationary points are exactly the zeros of

\[
 D_{\sigma,w}(t)
 =b_\sigma(t)+x'(t)L_{\sigma,w}(x(t)).
\]

Let \(\Delta=\min_j(c_{j+1}-c_j)>0\).  Partition the spatial window into:

1. \(m\) peak layers of width \(C_{\rm p}\sigma^2|\log\sigma|\)
   around the centres;
2. \(m-1\) crossover layers of width \(C_{\rm v}\sigma^2\) around
   \(v_j=(c_j+c_{j+1})/2\); and
3. their compact complement.

The constants are chosen once, uniformly for \(w_j\ge w_*\).

In a peak layer, all other components are exponentially small relative to
component \(j\), and

\[
 L_{\sigma,w}'(x)=-\sigma^{-2}+o(\sigma^{-2}).
\]

Thus \(D_{\sigma,w}\) is strictly decreasing there, and its endpoint signs
are positive then negative.  It has one simple zero, a maximum, with

\[
 x(t_{j,\sigma}^{\max})-c_j=O(\sigma^2)
\]

uniformly in \(w\).

In the \(j\)-th crossover layer, all nonadjacent components are exponentially
small.  The adjacent posterior weights are bounded away from zero after
choosing \(C_{\rm v}\) using the compact weight-ratio bound.  The identity

\[
 L_{\sigma,w}'(x)
 =\frac{\operatorname{Var}_{\pi_{\sigma,x}}(c)}{\sigma^4}
  -\frac1{\sigma^2}
\]

then gives

\[
 L_{\sigma,w}'(x)
 =\Theta(\Delta_j^2\sigma^{-4})>0.
\]

Consequently \(D_{\sigma,w}\) is strictly increasing through one simple
zero, a minimum.  Its location is \(v_j+O(\sigma^2)\); the bounded
\(b_\sigma\) changes only the \(O(\sigma^2)\) correction.

On the complement, one component is exponentially dominant and the point is
bounded away, on the appropriate scale, from both its centre and the adjacent
crossover.  Hence

\[
 |x'L_{\sigma,w}|\to\infty
\]

uniformly, with the alternating sign dictated by the nearest centre.  The
bounded \(b_\sigma\) cannot cancel it, so there are no other zeros.  Fixed
separation of the endpoint images from \(c_1,c_m\) gives nonzero endpoint
derivatives.  The signs of \(D'\) in the peak and crossover layers give
nondegeneracy and the claimed types.  All dominance estimates are uniform on
\(\mathcal W_{w_*}\).  \(\square\)

The layer proof, rather than ordinary absolute \(C^2\) perturbation, is
essential: valley densities are exponentially small as
\(\sigma\downarrow0\).

## 5. Candidate exact-\(m\) encounter theorem

### Theorem 5.1 (exact \(m\) Doi modes for a fixed finite \((d,m)\))

Fix finite integers \(d\ge2\) and \(m\ge1\), a compact window \(I\), model
parameters, target times, and a nonempty compact simplex-interior allocation
set.  Impose:

1. the stationary midpoint variance coefficient
   \(s_0^2=D_0/(2\gamma)\);
2. normalized Gaussian slabs of width coefficient \(\rho\);
3. a monotone midpoint mean with the target centres on its trajectory; and
4. a deterministic relative trajectory uniformly inside the encounter ball
   on the whole window.

Then there exists \(\varepsilon_0>0\), depending on all fixed data, such that
for every \(0<\varepsilon<\varepsilon_0\) and every admissible \(w\), the exact
continuum free-exposure clock \(G_{\varepsilon,w}\) has precisely

\[
 m\ \hbox{nondegenerate maxima and}\ m-1\ \hbox{nondegenerate minima}
\]

on \(I\), with no endpoint stationary point.

For each fixed such \(\varepsilon\), there exists
\(B_0(\varepsilon)>0\), uniform over the compact weight set, such that the
normalized Doi reaction-time density

\[
 F_{B,\varepsilon,w}=f_{B,\varepsilon,w}/B
\]

has the same complete finite-window stationary signature for every
\(0<B<B_0(\varepsilon)\).

#### Proof

The clock reduction in Section 2 and Lemma 4.1 give the complete
free-exposure topology uniformly over the compact weight set.  The stationary
points are finite, simple, remain in disjoint peak/crossover boxes, and the
endpoint derivatives are uniformly nonzero after \(\varepsilon\) is fixed.
On the compact complement of those boxes, the absolute derivative has a
strictly positive uniform minimum.  The peak and valley curvatures also have
strict signed uniform minima.

For fixed \(\varepsilon>0\), the bounded Gaussian catalysts, weighted-space
initial law, and fixed-finite-\(d\) OU quotient satisfy the existing mixed-jet
weak-reactivity theorem.  Its \(C^2(I)\) convergence

\[
 F_{B,\varepsilon,w}\longrightarrow G_{\varepsilon,w}
\quad(B\downarrow0)
\]

is uniform over the compact allocation set.  Choose \(B_0(\varepsilon)\) so
that the derivative error is smaller than the endpoint/complement margins
and the second-derivative error is smaller than the curvature margins.
The complete box-and-complement certificate then persists: every box contains
one unique typed root and the complement contains none.  \(\square\)

## 6. What would be genuinely new

The Gaussian-mixture zero bound is established mathematics.  The candidate
paper contribution would be the intersection of:

- an exact encounter-process embedding in every fixed finite \(d\ge2\);
- a conserved physical reactivity budget;
- a constructive spatial placement rule along the deterministic transport
  trajectory;
- a complete, rather than at-least, finite-window topology;
- a uniform compact family of allocation weights;
- transfer from free exposure to a positive-budget Doi reaction clock; and
- a separately validated finite-parameter realization with event-law mass.

The theorem gives a structural answer to the spatial-configuration question:
ordered narrow reactivity slabs placed at ordered points of a monotone
transport trajectory act as an asymptotically exact modal basis; allocation
weights tune prominence, while geometry and common scale set modal capacity.

## 7. Scope limits and audit targets

The theorem would still not claim:

- one fixed geometry supports arbitrarily many modes;
- uniformity as \(d\to\infty\), \(m\to\infty\), or
  \(\varepsilon\downarrow0\);
- an explicit usable \(B_0(\varepsilon)\);
- an interchange of the \(\varepsilon\) and \(B\) limits;
- arbitrary localized patch shapes;
- nontrivial approach/separation dynamics as the cause of the modes;
- an event-mass observability floor; or
- exact topology outside the declared finite window.

The sequential order remains: fix finite \((d,m)\), choose the geometry and a
sufficiently small but positive \(\varepsilon\), then choose
\(0<B<B_0(\varepsilon)\).

An independent proof audit must attack at least:

1. zero counting with multiplicities in Lemma 3.1;
2. uniform peak/crossover layer coverage and absence of uncovered transition
   regions in Lemma 4.1;
3. the posterior-variance sign estimates at crossover edges;
4. uniformity over the compact weight set;
5. contact-factor logarithmic derivative bounds on the whole window;
6. endpoint and complement margins;
7. the exact weighted-space hypotheses for the Doi transfer; and
8. every claimed dependency on fixed finite \(d,m,\varepsilon\).

Until that audit passes, this file is a research direction, not evidence.
