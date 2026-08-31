# Constructive multi-peak channel designs in physical dimension (d)

## Status and claim boundary

This note gives an explicit analytical **screening construction** for two,
three, and four reaction-time modes in dimensions (d=1,2,3,4), together with
full numerical derivative-root isolation for the declared parameter family.
It answers the design question “where should separated catalytic opportunities
be placed if their free-motion channel clocks are to occur at prescribed
times?”

It is not a bounded-domain continuum theorem.  The derivation uses the
free-space, narrow-centre-patch GIG channel approximation.  Reflections,
finite-patch averaging, channel competition, and the physical realization of
the designed splitting weights remain separate obligations.  The finite-radius
2D calculations elsewhere in this report validate the two-channel mechanism,
not the three- or four-channel construction in this note.

## 1. Channel law and prescribed mode

For a localized centre patch in physical dimension (d), use

\[
 g_j(t)=Z_j^{-1}t^{-p}\exp(-a_j/t-bt),
 \qquad p=\frac{d+3}{2},\quad a_j,b>0,
\]

with

\[
 Z_j=2\left(\frac{a_j}{b}\right)^{(1-p)/2}
 K_{1-p}(2\sqrt{a_jb}).
\]

The log derivative is

\[
 A_j(t)=\frac{a_j}{t^2}-\frac{p}{t}-b.
\]

Hence the mode solves (bt^2+pt-a_j=0).  Given a desired isolated
mode (m_j>0), choose

\[
 \boxed{a_j=b m_j^2+p m_j.}                         \tag{1}
\]

Then (A_j(m_j)=0) exactly.  This is the basic geometry-to-clock design
equation; it does not require numerical optimization.

## 2. Mapping the clock to a catalyst location

For equal particle diffusivities (D_1=D_2=1/2),

\[
 D_r=D_1+D_2=1,\qquad D_c=\frac{D_1D_2}{D_1+D_2}=\frac14.
\]

Take initial relative gap (ell=1), zero relative drift, and centre drift
speed (|v_c|=0.1).  The free-motion actions become

\[
 a_j=\frac{ell^2}{4D_r}
     +\frac{|z_j-R_0|^2}{4D_c}
     =\frac14+|z_j-R_0|^2,
 \qquad
 b=\frac{|v_c|^2}{4D_c}=0.01.
\]

Putting the catalyst centres on the drift ray gives the explicit spatial rule

\[
 \boxed{|z_j-R_0|=\sqrt{b m_j^2+p m_j-\frac14}.}     \tag{2}
\]

The action prescription is algebraically valid for every positive mode, but a
real catalyst location additionally requires

\[
 a_j\ge a_{\rm rel}=\frac{\ell^2}{4D_r},
 \qquad b m_j^2+p m_j\ge\frac14                 \tag{2a}
\]

in this reference geometry.  Thus

\[
 m_j\ge m_{\min}(p)
 =\frac{-p+\sqrt{p^2+b}}{2b}.
\]

For (d=1,2,3,4), these lower limits are respectively (0.12492197),
(0.09996003), (0.08331020), and (0.07141400).  All validated targets
satisfy (m_j\ge1).  The validator enforces (2a) before taking a square root.

The construction extends to any direction or rotational copy having the same
distance in isotropic free space.  In a bounded or anisotropic domain, the
regular Green part and directional transport break that degeneracy, so
distance alone is no longer sufficient.

## 3. A non-optimized observability weight

Let (h_j=g_j(m_j)) be the isolated peak height.  Define

\[
 \boxed{w_j=\frac{h_j^{-1}}{\sum_k h_k^{-1}}.}       \tag{3}
\]

Then (w_j>0), (sum_jw_j=1), and

\[
 w_jh_j=\left(\sum_k h_k^{-1}\right)^{-1}
\]

for every channel.  Thus the isolated weighted peak heights are exactly equal.
Equation (3) is a transparent design rule, not a fitted optimum.  In a full
reaction model the (w_j) must be produced by patch volumes, intrinsic rates,
and transport-dependent splitting probabilities; equality of bare catalyst
budgets does not imply (3).  In particular, the time-independent drift cross
factor from the GIG action expansion is position- and direction-dependent and
must be included in that physical amplitude matching.

## 4. Why separated clocks can yield (m) modes

Let (f=\sum_{j=1}^m w_jg_j), with the target modes ordered and widely
separated.  A proof-ready persistence statement uses disjoint peak
neighbourhoods (I_j) and separator intervals (J_j).  If, in each (I_j),
the (j)-th channel and its first two derivatives dominate the sum of all
cross-channel derivatives by a margin smaller than the nondegenerate curvature
of (g_j), then (f) has a stable maximum in (I_j).  If the derivative has
opposite signs at the two ends of every (J_j), the intermediate value theorem
supplies an intervening minimum.  These derivative-margin hypotheses imply at
least (m) maxima and (m-1) minima.

The GIG tails make those cross-channel terms small when the actions and modes
are sufficiently separated.  Establishing a uniform explicit separation
threshold for arbitrary (m) is an analytical theorem target.  The numerical
study below checks the derivative roots directly for one constructive family.

## 5. Validated family

The generator
`code/validate_multid_gig_design.py` uses

\[
 (m_1,m_2)=(1,10),\quad
 (m_1,m_2,m_3)=(1,10,100),\quad
 (m_1,m_2,m_3,m_4)=(1,10,100,1000)
\]

for each (d=1,2,3,4).  It evaluates the normalized densities and their
analytic first and second derivatives, brackets every sampled sign change on a
240,000-point logarithmic time grid, refines roots with Brent's method, checks
the alternating curvature signs, and audits both time tails.

In all 12 dimension/channel-count cases, the finite scan found the expected
(2m-1) sign-changing simple roots on the audited interval, alternating

\[
 \text{maximum},\text{minimum},\ldots,\text{minimum},\text{maximum}.
\]

The weakest peak-to-adjacent-valley ratio is greater than (1.9), and the
largest scaled derivative residual at a refined root is below
(2\times10^{-10}).  The construction therefore realizes two, three, and
four resolved modes in every tested dimension.  This is stronger than merely
plotting multiple humps, but it remains floating-point root isolation rather
than an interval-arithmetic proof that tangential roots are absent.

Evidence:

- `artifacts/data/multid_gig_design_parameters.csv`;
- `artifacts/data/multid_gig_design_roots.csv`;
- `artifacts/data/multid_gig_design_cases.csv`;
- `artifacts/data/multid_gig_design_summary.json`;
- `artifacts/figures/multid_gig_channel_design.pdf`;
- `artifacts/data/multid_gig_design.manifest.json`.

## 6. What this changes in the research programme

The general explanation is now constructive:

1. choose desired reaction clocks (m_j);
2. convert clocks to GIG actions with (1);
3. convert actions to catalyst distances with (2), corrected by the domain's
   regular Green part in a confined problem;
4. choose patch strengths to approach the splitting weights (3);
5. locate folds and cusps by continuing physical patch parameters in the full
   killed generator, not by varying abstract weights after the fact.

For the current paper, the two-channel finite-radius 2D fold remains the
physical headline.  The three- and four-mode construction belongs in the
general-design section or Supplement with the word “screening” retained.  A
future higher-dimensional paper should replace the GIG approximation by a
capacity-renormalized restricted Green operator and verify that the derivative
dominance margins persist under finite-radius, boundary, and grid limits.
