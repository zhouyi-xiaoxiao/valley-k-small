# Theorem program: conserved-reactivity design of multimodal encounter times

## 0. Purpose, evidence language, and non-overlap

This note originated as the mathematical program for a possible Physical
Review Research paper on spatially designed encounter-time multimodality.  The
direct physical fixed-finite-mode theorem and compact-time weak-budget
mixed-jet bridge are proved in the companion theorem notes.  The stronger
exact-`m` complete-topology theorem and fixed-epsilon weak-budget Doi transfer
are independently accepted by Rounds 118 and 120; the migrated reader-facing
proof and theorem-first source bytes independently passed Round 149.  The
active numerical gates are the still-incomplete science-free interval F0, all 36
same-budget one-/two-/three-mode physical-2D F1 rows, and the independent
common-observable F3 event law.  One historical fixed-control physical-2D
finite-volume point has positive event mass on two odd meshes, but it is not a
continuum or allocation-cusp result; allocation-v6 is a terminal negative
branch.  Positive-budget physical `d=3` is optional unless used in the
headline.

Every substantive result or theorem target is assigned one of the following
evidence levels.

- **PROVED**: a proof is given here or the statement follows directly from a
  stated standard theorem under the displayed hypotheses.
- **NUMERICALLY VERIFIED---REDUCED**: a finite-dimensional or floating-point
  calculation has tested the statement for a declared reduced family; this is
  not a continuum result.
- **CONTINUUM-KERNEL CONFIRMATION**: exact free kernels pass declared
  quadrature/root checks, but no interval root proof or finite-budget killed
  PDE is implied.
- **NUMERICALLY VERIFIED---CONTINUUM**: the declared refinement and independent-
  method gates pass for a continuum model; this remains numerical evidence.
- **IMPLEMENTATION SMOKE PASS**: software invariants and independent local
  references pass, without a continuum scientific claim.
- **CONJECTURAL**: this is a theorem target whose model-specific estimate has
  not yet been proved.
- **MATHEMATICAL NO-GO**: an explicit counterexample or regularity obstruction
  forbids the corresponding stronger statement.
- **PROJECT GATE FAILED**: a predeclared empirical or numerical falsification
  gate failed; the corresponding project headline must be removed or redesigned.

The existing DPMA manuscript already contains a rank-one response formula for
an arbitrary finite CTMC, a conditional finite-CTMC fold classification, the
generic fold powers, and a nondegenerate cusp in its particular localized-
delivery geometry.  Therefore this project must not claim the first rank-one
response identity, the first finite-CTMC fold theorem, the first cusp, or the
first use of a catastrophe normal form in a first-passage problem.

The non-overlapping theorem chain proposed here is instead:

1. fixed-budget **multi-rate projected-jet controllability** for several
   spatial killing amplitudes;
2. a sufficient, constructive **exact-\(m\)-mode theorem** for separated
   encounter channels on a declared compact positive-time window;
3. a model-specific continuum realization estimate, strong enough in the
   relevant derivative jet to transfer modes, folds, and, when required, a
   budget-constrained cusp.

The first item is exact constrained linear algebra once the continuum
semigroup derivatives exist.  The channel-dominance lemma and its application
to arbitrary finite GIG mixtures are proved below.  A stronger direct physical
route is now proved in `direct_physical_multimode_theorem.md`: for each fixed
finite integer dimension `d>=2` and each fixed finite mode count, sharply
localized OU exposure clocks dominate their cross channels, and the mixed-jet
weak-budget theorem transfers the modes to the exact physical Doi quotient
after sequential limits.  The statement is pointwise, not uniform, in `d`
and makes no `d -> infinity` or cross-dimensional budget claim.  The accepted
v2 posterior-sector theorem additionally excludes all extra stationary points
on the declared window.  This does not remove the finite-parameter numerical
and observability gates.

---

## 1. Conserved-reactivity continuum encounter model

### 1.1 Configuration-space dynamics

Fix a physical dimension \(d\geq 1\).  Let
\(\Omega_i\subset\mathbb R^d\) be bounded, connected domains with
\(C^{2,\alpha}\) boundary.  Before reaction, the two particles obey reflecting
diffusions with constant diffusivities \(D_i>0\) and drifts
\(b_i\in C^{1,\alpha}(\overline\Omega_i;\mathbb R^d)\).  On

\[
\mathcal D=\Omega_1\times\Omega_2,
\]

write \(\mathcal A_0\) for the forward no-flux Fokker--Planck operator.  We
assume that \(\mathcal A_0\) generates a positive analytic semigroup on
\(X=L^2(\mathcal D)\), with the usual consistent realization on
\(L^1(\mathcal D)\).

Let

\[
r=x_1-x_2,
\qquad
C_\eta=\eta x_1+(1-\eta)x_2,
\qquad 0\leq\eta\leq1.
\]

Choose a fixed contact profile \(\chi_a(r)\in L^\infty\),
\(0\leq\chi_a\leq1\), supported in \(|r|<a\), and fixed nonnegative centre
profiles \(\psi_j\in L^\infty\), \(j=1,\ldots,n\).  The spatial reaction
basis is

\[
\Psi_j(x_1,x_2)=\chi_a(x_1-x_2)\psi_j(C_\eta),
\qquad
K_u=\sum_{j=1}^n u_j\Psi_j,
\qquad u_j\geq0.                                      \tag{1.1}
\]

Only the amplitudes \(u_j\) vary.  The supports are fixed.  This restriction
is essential for the bounded-operator differentiability used below.

Define the killed generator, state, total reaction-time density, and channel
fluxes by

\[
\mathcal A(u)=\mathcal A_0-M_{K_u},
\qquad
q(t;u)=e^{t\mathcal A(u)}q_0,                         \tag{1.2}
\]

\[
f(t;u)=\langle \mathbf1,M_{K_u}q(t;u)\rangle,
\qquad
f_j(t;u)=u_j\langle\mathbf1,M_{\Psi_j}q(t;u)\rangle, \tag{1.3}
\]

where \(q_0\geq0\), \(\int_{\mathcal D}q_0=1\).  Under no-flux outer
boundaries,

\[
-\frac{d}{dt}\int_{\mathcal D}q(t;u)=f(t;u)
\]

whenever the displayed derivative is defined.

**Evidence: PROVED.**  Positivity follows from bounded nonnegative killing as
a perturbation of the positive semigroup, and mass balance follows by
integrating the forward equation.  This is a model definition and standard
semigroup identity, not a novelty claim.

### 1.2 Physical conserved-reactivity constraint

Define the installed centre-space reactivity field and catalyst costs by

\[
\kappa_u(c)=\sum_{j=1}^n u_j\psi_j(c),
\qquad
c_j=\int_{\mathcal C_\eta}\psi_j(c)\,dc>0,
\qquad
\mathcal C(u)=c^Tu.                                   \tag{1.4}
\]

Here

\[
\mathcal C_\eta
=\{\eta x_1+(1-\eta)x_2:(x_1,x_2)\in\mathcal D\}
\subset\mathbb R^d
\]

is the physical centre domain, with Lebesgue measure in the installed-catalyst
coordinate.  Thus \(\mathcal C(u)=\int_{\mathcal C_\eta}\kappa_u(c)\,dc\)
measures installed centre-space catalyst, not a configuration-space exposure
volume.

For a fixed physical budget \(B>0\), the admissible amplitude simplex is

\[
\mathcal U_B=\{u\in[0,\infty)^n:c^Tu=B\}.             \tag{1.5}
\]

At an interior point \(u\in\mathcal U_B\), its tangent space is

\[
T_u\mathcal U_B=\{h\in\mathbb R^n:c^Th=0\}.           \tag{1.6}
\]

The definition in (1.4) is a centre-space continuum integral.  It is not an
unweighted number-of-grid-states constraint.  In general it is also not equal,
even up to a common factor, to

\[
\int_{\mathcal D}K_u(x_1,x_2)\,dx_1dx_2
=\sum_{j=1}^n u_j\int_{\mathcal D}
\chi_a(x_1-x_2)\psi_j(C_\eta)\,dx_1dx_2.               \tag{1.7}
\]

Boundary clipping, the centre--relative coordinate map, and a
centre-dependent feasible contact cross-section can make the factors in (1.7)
depend on \(j\).  Equality with a common multiple of (1.4) is a special
factorization property that must be proved for the chosen geometry.  A
different installed-material cost may replace (1.4), but it must be declared
before discretization and its quadrature must converge to that same
centre-space functional.

**Evidence: PROVED as a definition.**  The physical appropriateness of a
particular cost for a chemical realization is a separate modeling question.

---

## 2. Continuum response derivatives and projected-jet controllability

### 2.1 Bounded-amplitude response

For \(h\in\mathbb R^n\), put

\[
K_h=\sum_{j=1}^n h_j\Psi_j,
\qquad
\mathcal B_h=-M_{K_h}.
\]

Bounded perturbation theory gives

\[
D_u e^{t\mathcal A(u)}[h]
=\int_0^t e^{(t-s)\mathcal A(u)}\mathcal B_h
e^{s\mathcal A(u)}\,ds.                              \tag{2.1}
\]

Consequently,

\[
\begin{split}
D_uf(t;u)[h]
={}&\langle\mathbf1,M_{K_h}e^{t\mathcal A(u)}q_0\rangle\\
&+\left\langle\mathbf1,M_{K_u}
\int_0^t e^{(t-s)\mathcal A(u)}\mathcal B_h
e^{s\mathcal A(u)}q_0\,ds\right\rangle .             \tag{2.2}
\end{split}
\]

The first term is the direct derivative of the reaction observable.  It may
not be omitted.  Analytic smoothing implies that, for every \(\tau>0\), the
map \((t,u)\mapsto f(t;u)\) is smooth on
\([\tau,\infty)\times\operatorname{int}\mathcal U_B\), and time
differentiation may be applied to (2.2).

**Evidence: PROVED.**  Equation (2.1) is the bounded-perturbation Duhamel
formula.  Equation (2.2) is its product rule with the observable derivative.
It extends the scalar finite-state response to several fixed continuum
reaction profiles, but it is not a shape derivative for moving sharp patches.

### 2.2 Projected multi-jet map

Choose \(q\) time-jet observables

\[
Y_a(u)=\partial_t^{r_a}f(t_a;u),
\qquad a=1,\ldots,q,                                  \tag{2.3}
\]

where \(t_a\geq\tau>0\) and \(r_a\geq1\).  Let
\(G\in\mathbb R^{q\times n}\) be their control Jacobian,

\[
G_{aj}=\partial_{u_j}Y_a(u).                           \tag{2.4}
\]

Let \(M\succ0\) define the local control norm
\(\|h\|_M^2=h^TMh\).  Project the rows of \(G\) off the budget covector by

\[
\widetilde G
=G-\frac{(GM^{-1}c)c^T}{c^TM^{-1}c}.                  \tag{2.5}
\]

Then \(\widetilde GM^{-1}c=0\), and \(Gh=\widetilde Gh\) for every
\(h\in T_u\mathcal U_B\).

### Theorem 2.1: fixed-budget projected-jet controllability

**Evidence: PROVED.**  Suppose \(u\in\operatorname{int}\mathcal U_B\),
\(q\leq n-1\), and

\[
\operatorname{rank}\widetilde G=q.                   \tag{2.6}
\]

Then every infinitesimal target jet \(y\in\mathbb R^q\) is attained by a
budget-preserving perturbation.  The unique perturbation of minimum
\(M\)-norm is

\[
h_*(y)=M^{-1}\widetilde G^T
(\widetilde GM^{-1}\widetilde G^T)^{-1}y.             \tag{2.7}
\]

It obeys

\[
c^Th_*(y)=0,
\qquad
Gh_*(y)=y.                                             \tag{2.8}
\]

**Proof.**  The rank assumption makes the Gram matrix in (2.7) positive
definite.  Equation (2.5) gives the budget identity in (2.8), while
\(Gh=\widetilde Gh\) on the tangent space gives the jet identity.  The
Lagrange equations for minimizing \(h^TMh/2\) subject to
\(Gh=y\) and \(c^Th=0\) yield (2.7).  Strict convexity gives uniqueness.

For \(q=1\), (2.7) reduces to the previously derived scalar projected-gradient
direction.  The new content is simultaneous control of several derivatives,
possibly at several candidate modal times.  The linear-algebra theorem does
not assert that a particular physical patch family satisfies (2.6).

**Model rank evidence: CONJECTURAL.**  A PRR claim requires either an analytic
rank proof for the chosen channel geometry or an independently certified lower
bound on the smallest singular value of
\(\widetilde GM^{-1/2}\), stable under continuum refinement.

---

## 3. A sufficient channel-dominance lemma

### Lemma 3.1: local mode persistence under derivative dominance

**Evidence: PROVED.**  Let

\[
F(t)=\sum_{j=1}^m H_j(t),
\qquad H_j\in C^2((0,\infty)),                         \tag{3.1}
\]

and let \(I_j=[\ell_j,r_j]\) be pairwise disjoint and ordered.  Suppose that
for each \(j\) there are \(\eta_j,\kappa_j>0\) such that

\[
H_j'(\ell_j)\geq2\eta_j,
\qquad
H_j'(r_j)\leq-2\eta_j,                                \tag{3.2}
\]

\[
H_j''(t)\leq-2\kappa_j
\quad (t\in I_j),                                     \tag{3.3}
\]

and the cross-channel terms satisfy

\[
\sum_{i\ne j}|H_i'(\ell_j)|\leq\eta_j,
\qquad
\sum_{i\ne j}|H_i'(r_j)|\leq\eta_j,                  \tag{3.4}
\]

\[
\sup_{t\in I_j}\sum_{i\ne j}|H_i''(t)|
\leq\kappa_j.                                         \tag{3.5}
\]

Then \(F\) has exactly one critical point in each \(I_j\), and that point is
a nondegenerate local maximum.  Between every consecutive pair
\(I_j,I_{j+1}\), \(F\) has at least one local minimum.  Hence \(F\) has at
least \(m\) modes.

**Proof.**  Equations (3.2) and (3.4) give
\(F'(\ell_j)>0>F'(r_j)\).  Equations (3.3) and (3.5) give
\(F''<0\) throughout \(I_j\), so \(F'\) is strictly decreasing and has
exactly one zero there.  At that zero \(F''<0\).  On the separator between
\(I_j\) and \(I_{j+1}\), take the compact gap
\([r_j,\ell_{j+1}]\).  The derivative is negative at its left endpoint and
positive at its right endpoint, so neither endpoint can minimize \(F\) on the
gap.  A minimizer is therefore attained in the interior and is a local minimum
of \(F\).

The lemma is deliberately sufficient, not necessary.  It proves existence of
at least \(m\) modes and makes no global assertion excluding additional modes.
The intervening minima need not be isolated or nondegenerate; either conclusion
would require an additional separator transversality or curvature hypothesis.

---

## 4. Constructive at-least-\(m\) theorem for GIG channels

### 4.1 Channel family

Let \(m_0>0\) be the first target time in physical units and let \(b>0\)
have units of inverse time.  Introduce

\[
\tau=t/m_0,
\qquad
\beta=bm_0.                                            \tag{4.1}
\]

The quantity \(\beta\) is dimensionless.  Since multiplication of a density
by the common Jacobian \(m_0\) does not change its modality, it is enough to
work in \(\tau\).  Fix \(m\in\{1,2,\ldots\}\), \(p>1\), \(\beta>0\), and, for a
separation factor \(R>1\), set

\[
\mu_j=R^{j-1},
\qquad
\mathcal A_j=\beta\mu_j^2+p\mu_j.                    \tag{4.2}
\]

Define normalized dimensionless GIG densities

\[
\gamma_j(\tau)=Z_j^{-1}\tau^{-p}
\exp(-\mathcal A_j/\tau-\beta\tau),
\qquad
Z_j=\int_0^\infty \tau^{-p}
e^{-\mathcal A_j/\tau-\beta\tau}\,d\tau.             \tag{4.3}
\]

Because \(\mathcal A_j>0\) and \(\beta>0\), the exponential factors control
both endpoints, so \(0<Z_j<\infty\).  Thus every \(\gamma_j\) is a probability
density, and the weights defined below are positive and sum to one.

The logarithmic derivative is

\[
(\log\gamma_j)'(\tau)
=\mathcal A_j/\tau^2-p/\tau-\beta,                    \tag{4.4}
\]

so (4.2) makes \(\mu_j\) the unique mode of \(\gamma_j\).  The
corresponding physical modal time is \(m_0\mu_j=m_0R^{j-1}\).  Choose

\[
w_j=\frac{\gamma_j(\mu_j)^{-1}}
{\sum_{k=1}^m \gamma_k(\mu_k)^{-1}}.                  \tag{4.5}
\]

Then the mixture has the same critical points as

\[
H_R(\tau)=\sum_{j=1}^m h_j(\tau),
\qquad
h_j(\tau)=\frac{\gamma_j(\tau)}{\gamma_j(\mu_j)}.    \tag{4.6}
\]

The normalizing Bessel functions cancel from (4.6).

### Theorem 4.1: constructive GIG multimodality

**Evidence: PROVED within the GIG mixture class.**  Under (4.1)--(4.5), there
exists a finite dimensionless threshold

\[
R_{\rm sep}=R_{\rm sep}(m,p,\beta)>1                  \tag{4.7}
\]

such that, for every \(R\geq R_{\rm sep}\),

\[
F_R(\tau)=\sum_{j=1}^m w_j\gamma_j(\tau)             \tag{4.8}
\]

has at least \(m\) nondegenerate local maxima and at least \(m-1\)
intervening local minima.

No assertion is made that these are all the critical points of \(F_R\).
The proof establishes existence only; it does not claim a computed or smallest
valid threshold.

**Proof.**  For a generic channel with prescribed dimensionless mode \(M\), put
\(\mathcal A_M=\beta M^2+pM\),
\(h_M(\tau)=\gamma_M(\tau)/\gamma_M(M)\), and
\(L_M=\log h_M\).  Setting \(x=\tau/M\) in (4.3)--(4.6) gives

\[
\boxed{
\log h_M(Mx)
=-\beta M\left(x+x^{-1}-2\right)
-p\left(\log x+x^{-1}-1\right).
}                                                       \tag{4.9}
\]

Both bracketed functions are nonnegative and vanish only at \(x=1\).  If
\(\tau=M+y\sqrt M\), the following rescaled identities are exact:

\[
\begin{aligned}
\log h_M(M+y\sqrt M)
={}&-\frac{\beta y^2}{1+y/\sqrt M}\\
&-p\left[\log(1+y/\sqrt M)
 +(1+y/\sqrt M)^{-1}-1\right],\\
\sqrt M\,L_M'(M+y\sqrt M)
={}&-y\frac{2\beta+\beta y/\sqrt M+p/M}
               {(1+y/\sqrt M)^2},\\
M L_M''(M+y\sqrt M)
={}&-\frac{2(\beta+p/M)}{(1+y/\sqrt M)^3}
 +\frac{p/M}{(1+y/\sqrt M)^2},\\
M\frac{h_M''}{h_M}
={}&(\sqrt M\,L_M')^2+M L_M''.
\end{aligned}                                          \tag{4.10}
\]

At \(M=1\), Eq. (4.4) gives the strict derivative signs on either side of
the unique mode, while

\[
h_1''(1)=-(2\beta+p)<0.
\]

By continuity there is \(\delta_c>0\) such that \(h_1''<0\) on
\([1-\delta_c,1+\delta_c]\).  Fix once and for all

\[
0<\delta<\min\left\{\frac14,\frac1{\sqrt{2\beta}},
\delta_c\right\}.
\]

Define the positive compact-channel margins

\[
a_1=\min\{h_1'(1-\delta),-h_1'(1+\delta)\}>0,
\qquad
b_1=-\sup_{|\tau-1|\leq\delta}h_1''(\tau)>0.          \tag{4.11}
\]

This treats the fixed channel \(\mu_1=1\) without a large-\(M\) expansion.

For \(|y|\leq\delta\), the denominators in (4.10) stay uniformly away from
zero for all sufficiently large \(M\).  The exact identities therefore imply,
uniformly on that compact \(y\)-interval,

\[
\begin{aligned}
\log h_M(M+y\sqrt M)&=-\beta y^2+O_{p,\beta,\delta}(M^{-1/2}),\\
\sqrt M\,L_M'(M+y\sqrt M)&=-2\beta y
 +O_{p,\beta,\delta}(M^{-1/2}),\\
M L_M''(M+y\sqrt M)&=-2\beta
 +O_{p,\beta,\delta}(M^{-1/2}),\\
M\frac{h_M''}{h_M}(M+y\sqrt M)&=4\beta^2y^2-2\beta
 +O_{p,\beta,\delta}(M^{-1/2}).
\end{aligned}
\]

The error bounds are uniform because the right-hand sides of (4.10) are smooth
functions of \((y,M^{-1/2})\) on a compact set with
\(1+y/\sqrt M\geq1/2\).  Put

\[
\kappa_0=2\beta-4\beta^2\delta^2>0,
\qquad
c_1=\frac12\beta\delta e^{-\beta\delta^2},
\qquad
c_2=\frac14\kappa_0e^{-\beta\delta^2}.
\]

Uniform convergence supplies \(M_*<\infty\) such that, for every
\(M\geq M_*\),

\[
\begin{aligned}
h_M'(M-\delta\sqrt M)&\geq c_1M^{-1/2},\\
h_M'(M+\delta\sqrt M)&\leq-c_1M^{-1/2},\\
\sup_{|\tau-M|\leq\delta\sqrt M}h_M''(\tau)&\leq-c_2M^{-1}.
\end{aligned}                                          \tag{4.12}
\]

Indeed, one first takes \(M_*\) large enough that
\(h_M\geq\tfrac12e^{-\beta\delta^2}\), that the endpoint values of
\(\sqrt M L_M'\) have magnitudes at least \(\beta\delta\), and that
\(M h_M''/h_M\leq-\kappa_0/2\) throughout the interval.  These three bounds
give the displayed constants \(c_1,c_2\).  The restriction
\(\delta<1/\sqrt{2\beta}\) is essential for this construction, since

\[
M\frac{h_M''(M\mathbin{\pm}\delta\sqrt M)}
       {h_M(M\mathbin{\pm}\delta\sqrt M)}
\longrightarrow4\beta^2\delta^2-2\beta.
\]

For a target channel \(M=\mu_j\), set

\[
I_M=[M-\delta\sqrt M,M+\delta\sqrt M].
\]

These intervals are positive because \(M\geq1\) and \(\delta<1/4\).  For two
consecutive centres \(M\) and \(MR\), the gap between the intervals is

\[
M(R-1)-\delta\sqrt M(\sqrt R+1)>0
\]

whenever \(\sqrt R>1+\delta\).  Thus all \(I_{\mu_j}\) are ordered and
disjoint for every sufficiently large \(R\).

It remains to bound every cross-channel derivative uniformly on these moving
intervals.  For a cross-channel centre \(N\), define

\[
Q_N(\tau)=\beta N
\left(\frac{\tau}{N}+\frac{N}{\tau}-2\right)
+p\left(\log\frac{\tau}{N}+\frac{N}{\tau}-1\right),
\qquad h_N(\tau)=e^{-Q_N(\tau)}.
\]

The second bracket is nonnegative, while \(N\) times the first bracket equals
\((\tau-N)^2/\tau\).  Since
\(I_M\subset[M/2,3M/2]\), the following bounds hold for every \(R\geq8\):

- if \(N\leq M/R\), then
  \[
  Q_N(\tau)\geq\beta(\tau-2N)\geq\beta M/4;
  \]
- if \(N\geq MR\), then, using \(R\geq3\),
  \[
  Q_N(\tau)\geq\beta\frac{(N-\tau)^2}{\tau}
  \geq\beta MR^2/6.
  \]

The logarithmic derivative factors grow only polynomially.  With
\(q=N/M\), \(\tau\in I_M\), and \(M\geq1\), the exact derivative formulas give

\[
\begin{aligned}
|L_N'(\tau)|&\leq4\beta q^2+4pq+2p+\beta,\\
|L_N''(\tau)|&\leq16\beta q^2+16pq+4p.
\end{aligned}
\]

Let

\[
D_1=5\beta+6p,
\qquad D_2=16\beta+20p,
\qquad D=\max\{D_1,D_1^2+D_2\}.
\]

For an earlier channel \(q\leq1/R\), uniformly on \(I_M\),

\[
|h_N'(\tau)|\leq D e^{-\beta M/4},
\qquad
|h_N''(\tau)|\leq D e^{-\beta M/4}.
\]

For a later channel \(q\geq R\), uniformly on \(I_M\),

\[
|h_N'(\tau)|\leq Dq^2e^{-\beta MR^2/6},
\qquad
|h_N''(\tau)|\leq Dq^4e^{-\beta MR^2/6}.
\]

These inequalities follow from \(h_N'=h_NL_N'\) and
\(h_N''=h_N[(L_N')^2+L_N'']\).  They make explicit that the derivative
prefactors are polynomial and hence cannot overcome the exponential
separation.

Now fix the finite integer \(m\).  For \(M_j=R^{j-1}\), one has
\(1\leq M_j\leq R^{m-1}\) and every later ratio satisfies
\(q\leq R^{m-1}\).  Summing over at most \(m-1\) cross channels yields a
bound with \(C_m=(m-1)D\) such that, for all \(R\geq8\),

\[
\begin{split}
\max_{1\leq j\leq m}\Bigg\{&
\sqrt{M_j}\sup_{\tau\in I_{M_j}}
 \sum_{i\ne j}|h_{M_i}'(\tau)|,\\
&M_j\sup_{\tau\in I_{M_j}}
 \sum_{i\ne j}|h_{M_i}''(\tau)|\Bigg\}
\leq E_R,
\end{split}
\]

where one may take

\[
E_R=C_mR^{5(m-1)}
\left(e^{-\beta R/4}+e^{-\beta R^2/6}\right)
\longrightarrow0.
\]

For \(j=1\) there is no earlier channel, so this envelope uses only the
later-channel bound and the exact compact margins (4.11).  For \(j\geq2\), one has
\(M_j\geq R\), so the earlier-channel exponential is at most
\(e^{-\beta R/4}\); the displayed power dominates every finite derivative,
ratio, and \(M_j\)-scaling factor.  Thus this is a single envelope valid for
every larger real \(R\), not a finite scan.

Choose \(R_{\rm sep}\) so large that, for every \(R\geq R_{\rm sep}\),
the intervals are disjoint, \(R\geq\max\{8,M_*\}\), and

\[
E_R\leq\frac14\min\{a_1,b_1,c_1,c_2\}.
\]

Such a threshold exists because the explicit envelope above tends to zero.
For \(j=1\), set \(\eta_1=a_1/4\) and \(\kappa_1=b_1/4\).  For \(j\geq2\),
set

\[
\eta_j=\frac{c_1}{4\sqrt{M_j}},
\qquad
\kappa_j=\frac{c_2}{4M_j}.
\]

Equations (4.11)--(4.12) and the cross-channel envelope verify (3.2)--(3.5) for
\(H_j=h_{M_j}\).  Lemma 3.1 therefore gives one nondegenerate local maximum in
each \(I_{M_j}\) and at least one intervening local minimum.  Finally,

\[
F_R(\tau)=
\frac{\sum_{j=1}^m h_{M_j}(\tau)}
     {\sum_{k=1}^m\gamma_k(\mu_k)^{-1}},
\]

so \(F_R\) and \(H_R\) differ by a positive constant and have the same critical
points.  This proves the theorem. \(\square\)

### 4.2 Spatial interpretation and its current boundary

In the narrow-centre, normal-contact screening geometry one uses

\[
p=(d+3)/2,
\qquad
A_j=A_{\rm rel}+|z_j-R_{\rm init}|^2/(4D_c),          \tag{4.13}
\]

Restoring physical time gives
\(A_j=b(m_0\mu_j)^2+p(m_0\mu_j)\), so (4.2) maps desired modal times to
catalyst distances.  The weights in (4.5) map to rate-volume products only
after the transport prefactors and the conserved cost (1.4) are included.

**Evidence: NUMERICALLY VERIFIED---REDUCED for the report-owned GIG pilot.**
The deterministic artifact isolates the intended alternating critical points
for (m=2,\ldots,6) at the declared parameters.  Its finite scans are not an
interval-exhaustive tail proof.

**Evidence: CONJECTURAL for a bounded finite-radius encounter process.**
Theorem 4.1 concerns only the explicit GIG mixture (4.8).  It is not a
continuum Doi theorem, does not control reflected paths or channel competition,
and does not prove that a fixed physical catalyst budget realizes (4.5).

### 4.3 Inverse-height observability boundary

**Evidence: MATHEMATICAL NO-GO for a uniform channel-mass bound from (4.5).**  The
inverse-height rule equalizes the isolated weighted peak heights, but it does
not equalize channel probabilities.  Laplace expansion about a large
dimensionless mode \(M\) gives

\[
\gamma_M(M)
=\sqrt{\frac{\beta}{\pi M}}\,[1+O(M^{-1})].           \tag{4.14}
\]

Consequently, for geometrically separated modes,

\[
w_j\asymp
\frac{\sqrt{\mu_j}}{\sum_{k=1}^m\sqrt{\mu_k}}.        \tag{4.15}
\]

For fixed \(m\) and large \(R\), the earliest-channel mass therefore scales
as

\[
w_1=O\!\left(R^{-(m-1)/2}\right),                     \tag{4.16}
\]

while the last channel carries asymptotically most of the probability.  The
common weighted isolated-peak height also decreases on the scale
\(\mu_m^{-1/2}\).  Thus Theorem 4.1 is an existence theorem, not a theorem of
uniform observability as \(m\) or \(R\) grows.

A physically resolved design must add, and report the dependence on \(m\) and
\(R\) of, constraints such as

\[
w_j\geq w_{\min}>0,
\qquad
w_j\int_{I_j}\gamma_j(\tau)\,d\tau\geq q_{\min}>0,
\qquad
\operatorname{prominence}_j\geq P_{\min}>0.           \tag{4.17}
\]

Possible remedies are to cap the separation ratio, optimize weights subject
to (4.17) instead of imposing exact inverse-height weights, or enlarge/duplicate
the early reactive supports.  Any such remedy must still satisfy the same
physical conserved-reactivity cost and rate bounds.

---

## 5. Exact jet order for modes, folds, and cusps

### 5.1 Persistence of already simple modes

**Evidence: PROVED.**  Let \(f_n\to f\) locally in the jet

\[
\mathcal J_{\rm mode}(f)
=\{f_t,f_{tt}\}.                                      \tag{5.1}
\]

If \(f_t(t_*)=0\) and \(f_{tt}(t_*)\ne0\), then a unique simple critical
point of the same type persists near \(t_*\).  Channel-dominance proofs use
this \(C^2\)-level information plus explicit separator signs and tail bounds.

### 5.2 Fold persistence

Let \(\theta\) be one local coordinate on the budget manifold and set

\[
H(f)=(f_t,f_{tt}).                                     \tag{5.2}
\]

A nondegenerate fold satisfies

\[
f_t=f_{tt}=0,
\qquad
f_{ttt}\ne0,
\qquad
f_{t\theta}\ne0.                                     \tag{5.3}
\]

At the fold,

\[
\det D_{(t,\theta)}H=-f_{t\theta}f_{ttt}\ne0.         \tag{5.4}
\]

**Evidence: PROVED.**  Persistence follows from local \(C^1\) convergence of
\(H(f_n)\) to \(H(f)\).  The exact relevant jet is

\[
\mathcal J_{\rm fold}(f)
=\{f_t,f_{tt},f_{ttt},f_{t\theta},f_{tt\theta}\}.     \tag{5.5}
\]

Full joint \(C^3(t,\theta)\) convergence is sufficient, but it is stronger
than (5.5) and is not literally equivalent to \(C^1\) convergence of \(H\).
The latter is the minimal fold-persistence condition.

### 5.3 Budget-constrained cusp persistence

Let \((\theta_1,\theta_2)\) be two local coordinates on
\(\mathcal U_B\); hence at least three independently variable reaction rates
are required before imposing the one budget constraint.  Put

\[
G(f)=(f_t,f_{tt},f_{ttt}).                             \tag{5.6}
\]

A nondegenerate budget-constrained cusp satisfies

\[
f_t=f_{tt}=f_{ttt}=0,
\qquad
f_{tttt}\ne0,                                         \tag{5.7}
\]

\[
\det
\begin{pmatrix}
f_{t\theta_1}&f_{t\theta_2}\\
f_{tt\theta_1}&f_{tt\theta_2}
\end{pmatrix}
\ne0.                                                  \tag{5.8}
\]

Equivalently, the projected \(f_t\)- and \(f_{tt}\)-control gradients have
rank two on the budget tangent space.  At (5.7)--(5.8),

\[
\det D_{(t,\theta_1,\theta_2)}G
=f_{tttt}
\det
\begin{pmatrix}
f_{t\theta_1}&f_{t\theta_2}\\
f_{tt\theta_1}&f_{tt\theta_2}
\end{pmatrix}
\ne0                                                   \tag{5.9}
\]

up to the immaterial sign determined by row ordering.

**Evidence: PROVED.**  A unique nearby cusp persists under local \(C^1\)
convergence of \(G(f_n)\) to \(G(f)\).  The exact relevant jet is

\[
\begin{split}
\mathcal J_{\rm cusp}(f)=\{&f_t,f_{tt},f_{ttt},f_{tttt},\\
&f_{t\theta_i},f_{tt\theta_i},f_{ttt\theta_i}:
i=1,2\}.
\end{split}                                            \tag{5.10}
\]

Thus full joint \(C^4(t,\theta_1,\theta_2)\) convergence is a simple
sufficient condition.  Joint \(C^3\) convergence is not sufficient for cusp
persistence because it does not control \(f_{tttt}\) or
\(f_{ttt\theta_i}\).

**Evidence: MATHEMATICAL NO-GO for “cusp implies trimodality.”**  A cusp changes the number
of nearby roots of \(f_t\) from one to three and therefore creates only one
additional max--min pair.  A trimodal conclusion requires, in addition, a
remote max--min pair that persists with uniform derivative and prominence
margins.  Equivalently, one must certify at least five alternating simple
critical points.  The cusp conditions (5.7)--(5.8) alone cannot do this.

---

## 6. Model-to-continuum theorem target

### Theorem target 6.1: uniform encounter-to-channel approximation

**Evidence: CONJECTURAL.**  Let \(\varepsilon\downarrow0\) index a declared
joint scaling of contact radius, centre-patch diameter, reaction strength, and
outer-boundary distance.  For each \(\varepsilon\), let the budget
\(B_\varepsilon>0\) be conserved across all compared controls.  A weak-reaction
existence proof may take \(B_\varepsilon\to0\); a theorem at one fixed nonzero
budget is stronger and must not be inferred from that limit.  Let
\(f_\varepsilon(t;u)\) be the reaction-time density of the continuum model
(1.1)--(1.3), with \(u\in\mathcal U_{B_\varepsilon}\).  Let
\(F(\tau;\vartheta)\) be a GIG mixture satisfying Theorem 4.1, where
\(\vartheta\) denotes one or two local budget coordinates.

The required theorem is the existence of:

1. a positive amplitude \(A_\varepsilon\);
2. a budget-preserving realization map
   \(u_\varepsilon(\vartheta)\in\mathcal U_{B_\varepsilon}\);
3. an error \(E_q(\varepsilon)\to0\);

such that on a compact mode-forming window
\(I=[\tau_-,\tau_+]\subset(0,\infty)\), expressed in the same dimensionless
time \(\tau=t/m_0\) as Section 4, and a compact control neighborhood \(V\),

\[
\max_{(r,\alpha)\in\mathfrak J_q}
\sup_{(\tau,\vartheta)\in I\times V}
\left|
\partial_\tau^r\partial_\vartheta^\alpha
\left[m_0A_\varepsilon^{-1}
f_\varepsilon(m_0\tau;u_\varepsilon(\vartheta))
-F(\tau;\vartheta)\right]
\right|
\leq E_q(\varepsilon).                                \tag{6.1}
\]

Here \(\mathfrak J_2\), \(\mathfrak J_3\), and \(\mathfrak J_4\) contain,
respectively, the derivatives listed in
\(\mathcal J_{\rm mode}\), \(\mathcal J_{\rm fold}\), and
\(\mathcal J_{\rm cusp}\).

The theorem must also supply:

- positive lower bounds on every designed channel contribution after the same
  normalization by \(A_\varepsilon\), uniform in \(\varepsilon\) for a fixed
  design; their deterioration with \(m\) and \(R\) must be reported rather
  than hidden;
- derivative-sign margins on the peak and separator intervals;
- a positive prominence or peak-to-valley margin independent of sufficiently
  small \(\varepsilon\);
- tail bounds showing that omitted early or late critical points do not alter
  the claimed at-least-\(m\) statement on the declared time domain;
- convergence of the projected-jet matrix and a lower singular-value bound
  when controllability or cusp rank is claimed.

A proof of (6.1) with \(q=2\), Theorem 4.1, and Lemma 3.1 transfer at least
\(m\) modes to the continuum encounter density.  If (6.1) is proved in the fold
jet, (5.3)--(5.5) transfer a nondegenerate fold.  If it is proved in the cusp
jet, (5.7)--(5.10), together with a persistent remote pair, transfer the cusp
and a genuine trimodal wedge.

### 6.2 Proposed proof route

**2026-07-13 resolution.**  The weak-reaction part of this route is now proved
for the exact reflected quotient without invoking a GIG approximation.  On
each compact positive-time/control window,

\[
 \partial_t^r\partial_\theta^\alpha
 \left[B^{-1}f_B-\langle V_w,e^{t\mathcal L}q_0\rangle\right]=O(B)
\]

through every prescribed finite mixed jet.  Exact first/second sensitivity
PDEs, direct observable terms, quantitative fold/cusp contraction bounds, and
a Weyl projected-rank bound are given in `pde_mixed_jet_theorem.md` and pass
the independent Round 19 audit.  This proves the bridge from a quantitatively
nondegenerate **free-exposure** design to sufficiently small positive Doi
budget.  It does not prove that `B=0.6` is small, control the `t=O(1/B)` tail,
or replace the numerical grid-to-PDE gate.

The still-open GIG realization problem would combine:

1. the Feynman--Kac representation
   \[
   f_j(t)=\mathbb E\!\left[
   u_j\Psi_j(X_t)
   \exp\!\left(-\int_0^tK_u(X_s)\,ds\right)
   \right];
   \]
2. a Duhamel expansion with a uniform remainder in the reaction strength;
3. a local heat-kernel or boundary-flux parametrix for approach to the contact
   manifold;
4. controlled averaging over the finite contact and centre-patch profiles;
5. Gaussian off-boundary estimates for reflected/image paths;
6. differentiation of each bound through the exact jet order required in
   Section 5.

For a fixed finite-radius, arbitrary-Damköhler theorem, the same program is
substantially harder and will generally require capacity-renormalized Green
operators rather than the leading free-space GIG law.

### 6.3 Discretization-to-continuum certification

**Evidence: CONJECTURAL for the model.**  A cell-centred finite-volume or
conforming finite-element family should use cell-averaged contact and catalyst
profiles and a quadrature converging to (1.4).  The required numerical theorem
is an a priori or a posteriori estimate of the form

\[
\|H_h-H\|_{C^1(U)}\leq C h^p
\quad\text{for a fold},                               \tag{6.2}
\]

or

\[
\|G_h-G\|_{C^1(U)}\leq C h^p
\quad\text{for a cusp}.                               \tag{6.3}
\]

Together with a Newton--Kantorovich or radii-polynomial bound, (6.2) or (6.3)
would convert a computed finite-grid root into a certified nearby continuum
root.  Merely observing stable density plots is not sufficient.

**Evidence: NUMERICALLY VERIFIED---REDUCED only for legacy finite models.**  Existing
encounter calculations verify finite-matrix folds, finite-grid multimodality,
and reduced GIG designs.  Their fold locations are not a controlled continuum
sequence and they do not establish (6.1)--(6.3).

---

## 7. No-go statements and mandatory adversarial tests

1. **MATHEMATICAL NO-GO: spectral sign variation is not sufficient.**  A finite exponential
   sum may have the required residue sign changes and still be unimodal.

2. **MATHEMATICAL NO-GO: patch count or killing rank does not bound mode count.**  A
   rank-one killing state can receive several separated transport streams and
   produce a bimodal density.

3. **MATHEMATICAL NO-GO: density \(C^2\) convergence does not transfer a fold.**  For
   \[
   f(t,\theta)=\theta t+t^3/3,
   \qquad
   f_n=f+2n^{-3}\sin(nt),
   \]
   one has \(f_n\to f\) in \(C^2\), while the nearby double stationary point
   of every \(f_n\) is degenerate.

4. **MATHEMATICAL NO-GO: continuum \(C^3\) convergence does not, in general, transfer a
   cusp.**  The cusp Jacobian uses the fourth time derivative and mixed
   third-time/parameter derivatives; the cusp target therefore requires the
   jet (5.10), or full joint \(C^4\) as a convenient sufficient condition.

5. **MATHEMATICAL NO-GO: a moving sharp mask is not a bounded-operator amplitude
   perturbation.**  On \(L^2(\mathbb R)\),
   \[
   K_s=M_{\mathbf1_{[s,s+1]}},
   \qquad
   \|K_s-K_0\|_{L^2\to L^2}=1
   \quad(s\ne0).
   \]
   Hence (2.1) cannot be relabeled as a shape derivative.  Moving patches
   require smooth phase fields, form perturbations, or genuine shape calculus.

6. **MATHEMATICAL NO-GO: a cusp alone does not imply three modes.**  A remote persistent
   max--min pair or a separate second fold is required.

7. **MATHEMATICAL NO-GO: equal installed centre-space catalyst cost does not imply equal
   configuration-space integrated killing, pathwise exposure, splitting
   probabilities, or mean reaction time.**  The cost (1.4) must be defended as
   the conserved physical resource, not as equality of every kinetic
   observable.

8. **MATHEMATICAL NO-GO: a translation-invariant relative-coordinate 3D mean-time quotient
   is not a centre-patterned 3D reaction-time-density realization.**  Spatial
   centre patterning restores the full two-particle state and requires an
   independent solver or Brownian calculation.

9. **MATHEMATICAL NO-GO: the screening exponent \(p=(d+3)/2\) is not universal for all
   patch geometries.**  It corresponds to a narrow-centre patch combined with
   a normal short-time contact flux.  Tangentially extended, boundary-touching,
   or jointly shrinking patches require a separate heat-kernel/capacity
   analysis.

---

## 8. Minimum theorem package for a PRR submission

The mathematically non-overlapping minimum is:

1. **PROVED:** the conserved-reactivity model and continuum Duhamel response;
2. **PROVED:** Theorem 2.1 as an abstract result; **CONJECTURAL** at present is
   the required realized positive projected-rank margin for the final physical
   configuration;
3. **PROVED:** Lemma 3.1 and Theorem 4.1 for arbitrary finite \(m\), with no
   claim of a uniform-in-\(m\) observability floor;
4. **PROVED conditionally in weak reaction:** a direct model-specific
   compact-time PDE mixed-jet estimate and fold/cusp/rank persistence theorem;
   **OPEN numerically:** certified free-exposure margins and a finite-grid-to-
   PDE estimator for the selected physical configuration;
5. **HISTORICAL CONTEXT ONLY:** result-informed physical-2D disk and physical-
   3D sphere free kernels have the saved four-slab shapes, and the unchanged
   broad physical-2D allocation at `B=0.01` has five retained roots and three
   qualified basin masses on odd meshes `N=113,129` in one box and one solver
   family.  Allocation-v6 subsequently ended at
   `HOLD_SCIENCE_AUDIT_VALID`; no cusp/fold promotion survives.
6. **ACTIVE NUMERICAL GATE:** exact-rational same-budget one-/two-/three-mode
   candidates are frozen before their own positive-`B` values.  Round 152
   rejected the first bounded packed directed-action bytes for a large-block
   endpoint-validator P1; Round 154 repaired the defect, and independent Round
   155 accepts the exact repaired bytes only as a bounded implementation
   primitive.  Round 151 accepts the selector process/resource surface on the
   tested macOS runtime, independently confirmed by Round 153.
   Still open are rate-interval composition, production uniformization/jets/
   topology and resources, complete 36-row full-window F1 interval topology,
   parity/alignment/box envelope, second-POSIX selector replay, and powered
   common-observable off-lattice F3 validation.
7. **ACCEPTED ANALYTICAL SPINE:** the exact-`m` physical theorem and fixed-
   epsilon weak-budget mixed-jet transfer are independently accepted in their
   fixed-finite, compact-window, sequential scope by Rounds 118 and 120.  The
   complete migrated paper proof passes Round 149 on its frozen bytes.  A global
   GIG-to-Doi bridge remains optional.

The recommended headline is therefore not “rank-one killing has a fold or a
cusp.”  Those statements overlap the DPMA theory.  The target PRR headline,
available only after the open F0/F1/F3 chain passes, is:

> A conserved spatial reaction budget provides constructive control of
> encounter-time topology: ordered reactive slabs form a finite modal basis,
> weak-reaction mixed jets transfer that design to the Doi law, and frozen
> same-budget allocations realize distinct mode counts in a resolved
> physical-2D encounter process.

At present, the projected-control algebra, Lemma 3.1, the arbitrary-\(m\) GIG
theorem, and the compact-time weak-budget continuum mixed-jet/persistence
theorem are proved analytical layers.  The exact-kernel physical-2D and
physical-3D `B=0` shape confirmations are now numerical layers, not killed-Doi
event-mass results.  The separate broad physical-2D fixed-control killed-Doi
point supplies finite-window event mass only on two same-family odd meshes.
The allocation cusp is a terminal negative branch, not a remaining gate.  The
decisive remaining PRR gates are full-window interval root control for all 36
frozen F1 rows,
parity/alignment/box convergence, and the independent common-observable F3
event law.  Positive-budget `d=3` is required only for a dimensional headline.
