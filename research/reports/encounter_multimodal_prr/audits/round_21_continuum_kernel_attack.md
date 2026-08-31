# Round 21: independent continuum-kernel attack

Date: 2026-07-13  
Role: independent mathematical, numerical, and promotion-gate audit  
Production-edit rule: the frozen producer and JSON were read but not modified

## 1. Frozen inputs

| item | SHA-256 |
| --- | --- |
| `scratch/continuum_free_exposure_exploration.py` | `3eae6d3216f58d669554450e13b2720c6fed56de7d8b1dc8698f2b5b6e98f3a0` |
| `scratch/continuum_free_exposure_exploration_result.json` | `1b23fc6f91f002fb3f1396708c96e9e0056e4df66e0120928bd386da95e3c1f7` |
| `notes/continuum_free_exposure_exploration.md` | `59cfc6f8275de7129f987e45994b994634eacbdd74b28a5ec9ffdce212cd66af` |
| `audits/round_20_continuum_free_exposure_self_audit.md` | `4195fdee44f6a9c1067d9048048bef442f5b4b2ea70aa90f582cf140cb92ded4` |

The JSON embeds the frozen producer hash.  Its four promotion flags remain
false, so the new P0 below is a manuscript-promotion blocker rather than a
provenance or false-label failure of the scratch artifact.

## 2. Verdict

**PASS for the physical $d=2$ free-kernel formula, the redesigned
positive-weight cusp, and the existence of five alternating simple critical
points.  FAIL/HOLD for observable trimodality and any PRR promotion.**

The independent recomputation found no sign, normalization, Jacobian,
derivative-order, null-vector, or rank defect.  It did find a decisive omitted
acceptance check: the two valleys in the selected five-root curve are only
$0.10005\%$ and $0.02276\%$ below the smaller neighboring peaks.  The
predeclared project floor requires each valley to be at most $85\%$ of that
peak.  This design is topologically trimodal but not observably trimodal under
the project's own definition.

| severity | open count | disposition |
| --- | ---: | --- |
| P0 | 1 | observable-trimodality / manuscript-promotion gate fails |
| P1 | 0 | no additional unacknowledged major kernel or numerical defect |
| P2 | 0 | no independent precision or governance defect |

Open formal-certification and finite-$B$ tasks are listed separately in
Section 9; they are already excluded by the producer's evidence label and are
not double-counted as implementation defects here.

## 3. Independent physical derivation

Let the two identical particles have longitudinal coordinates $x_1,x_2$
and periodic transverse coordinates $y_1,y_2\in\mathbb T_W$.  Put

\[
 z={x_1+x_2\over2},\qquad r_\parallel=x_1-x_2,
 \qquad r_\perp=y_1-y_2\pmod W.
\]

Starting from two particle generators with diffusivity $D$ and identical
longitudinal OU drift, direct substitution gives

\[
 \mathcal L_z={D\over2}\partial_{zz}
   -\gamma(z-m)\partial_z,
 \qquad
 \mathcal L_{r_\parallel}=2D\partial_{r_\parallel r_\parallel}
   -\gamma r_\parallel\partial_{r_\parallel},
 \qquad
 \mathcal L_{r_\perp}=2D\partial_{r_\perp r_\perp}.
\]

Thus the producer's three diffusion coefficients are correct.  For a generic
OU generator

\[
 \kappa\partial_{xx}-\gamma(x-m)\partial_x,
\]

the transition mean and variance are

\[
 m+(x_0-m)e^{-\gamma t},\qquad
 {\kappa\over\gamma}(1-e^{-2\gamma t}),
\]

which also matches the implementation.

Let each compact longitudinal patch profile \(\phi_j\) integrate to one.  A
transversely uniform slab with full installed budget $B$ must be

\[
 \kappa_{B,w}(z)={B\over W}\sum_j w_j\phi_j(z),
 \qquad \sum_jw_j=1,
\]

because integrating over $z$ and the common transverse period gives $B$.
Consequently the free response per unit **full** budget contains exactly one
factor $1/W$:

\[
 g_j(t)={1\over W}\,\mathbb E[\phi_j(Z_t)]
       \Pr\{R_t\in\mathcal C_2\}=:a_j(t)c_2(t).
\]

The producer places this factor in the midpoint clock.  Since the frozen
value is $W=1$, this normalization cannot be tested numerically from the
reported numbers; the algebraic derivation is essential.  In physical
dimension $d$, the corresponding full-budget slab factor is
$W^{-(d-1)}$, not $1/W$.

For disk contact $x^2+y^2<a^2$, write
$x=a\sin\vartheta$, $h=a\cos\vartheta$.  If $q_t(y)$ is the wrapped
relative-transverse density, then

\[
 c_2(t)=\int_{-\pi/2}^{\pi/2}
 a\cos\vartheta\;p_\parallel(a\sin\vartheta,t)
 \left(\int_{-h}^{h}q_t(y)\,dy\right)d\vartheta.
\]

For the even compact initial transverse bump,

\[
 \int_{-h}^{h}q_t(y)\,dy
 ={2h\over W}+{4\over W}\sum_{k\ge1}
 \widehat q_k e^{-2D(2\pi k/W)^2t}
 {\sin(2\pi kh/W)\over 2\pi k/W}.
\]

This reproduces the producer's disk Jacobian, zero Fourier mode, factor four,
and transverse decay rate.  As an additional check not using this Fourier
interval representation, I evaluated the same interval probabilities by a
wrapped-normal image sum of Gaussian CDF differences and obtained the same
continuum clocks and cusp.

## 4. Independent numerical route

The main recomputation did not import the producer.  It used:

- independent normalized Gauss--Legendre rules for the initial and patch
  bumps;
- a wrapped-normal image-CDF evaluation of the transverse interval
  probability;
- real-axis Chebyshev interpolation for orders one through four; and
- a second real Taylor-jet implementation in which product, reciprocal,
  logarithm, and exponential series were propagated analytically through the
  OU density.  This second route used no complex Cauchy circle.

The Taylor-jet check used 104-point bump/patch rules, a 180-point contact-angle
rule, and 40 transverse modes.  Its redesigned cusp was

\[
 t_c=8.997541071499517,
\]

with positive affine null weights

\[
 w=(0.2990353392,\;0.3259755118,\;0.3749891490).
\]

The saved and independent headline values agree as follows.

| quantity | saved JSON | independent real Taylor jets | absolute difference |
| --- | ---: | ---: | ---: |
| $t_c$ | 8.997541071494128 | 8.997541071499517 | $5.39\times10^{-12}$ |
| scaled $G^{(4)}$ | -9.197556793222137 | -9.197556792718570 | $5.04\times10^{-10}$ |
| unfolding SVD ratio | 0.467061238714062 | 0.467061238715460 | $1.40\times10^{-12}$ |
| determinant derivative | $-2.410234540881\times10^{-7}$ | $-2.410234540736\times10^{-7}$ | $1.45\times10^{-17}$ |

The independent derivative-matrix singular values were

\[
 (4.26892867\times10^{-2},\;1.82884052\times10^{-2},
  \;7.36\times10^{-18}),
\]

so the cusp matrix has rank two.  The dimensionless unfolding matrix was

\[
 \begin{pmatrix}
 -3.44001839&-2.86664918\\
  4.05642812&-8.22039401
 \end{pmatrix},
\]

with row-angle sine $0.97220346$.  The fourth jet and unfolding rank are
well separated from zero at floating-point precision.

## 5. Cauchy-jet and root checks

The producer's direct-product Cauchy jets and factorwise Leibniz jets differ
by at most $2.83\times10^{-14}$ at the redesigned cusp.  Changing bump,
patch, contact, Fourier, Cauchy-sample, and Cauchy-radius settings shifts
$t_c$ by at most $4.54\times10^{-10}$ and the weights by at most
$2.20\times10^{-11}$.  More decisively, the independent real Taylor jets in
Section 4 reproduce $G^{(4)}$ and the determinant derivative without using
Cauchy differentiation.  No derivative-order or aliasing symptom was found.

At the producer's inward weight

\[
 (0.3022362396163318,\;0.3221343873741756,
   \;0.3756293730094926),
\]

independent analytic real-axis derivatives give:

| root | saved time | independent time | type | scaled second derivative |
| ---: | ---: | ---: | --- | ---: |
| 1 | 4.168876490443854 | 4.168876490450309 | maximum | -0.3132003856 |
| 2 | 5.391260082734694 | 5.391260082731593 | minimum | 0.0957372089 |
| 3 | 7.031985343402768 | 7.031985343404908 | maximum | -0.0545612776 |
| 4 | 8.997541071493622 | 8.997541071499780 | minimum | 0.0448371191 |
| 5 | 10.403620199717961 | 10.403620199711398 | maximum | -0.0850338108 |

The producer's sign-changing-root route is therefore correct for these five
simple roots.  A real-derivative scan found no additional sign-changing root
on the screened compact interval.  Direct spot checks give positive
derivative from $t=0.02$ through $0.5$ and negative derivative from the
last maximum through $t=200$, with the expected $e^{-\gamma t}$ tail
sign.  These checks do **not** constitute interval-exhaustive root isolation:
a sign scan cannot by itself exclude an unresolved tangential double root,
and the asymptotic tail sign has not been enclosed analytically.

## 6. P0: the three peaks fail the observability gate

The saved five critical-point densities are

\[
\begin{array}{c|ccccc}
\text{type}&P_1&V_1&P_2&V_2&P_3\\\hline
\text{density}
&0.1457059188&0.1453894738&0.1455350777
&0.1454481102&0.1454812205.
\end{array}
\]

Using the definition in `notes/research_contract.md`, the adjacent valley
ratios are

\[
 {V_1\over\min(P_1,P_2)}=0.9989995272,
 \qquad
 {V_2\over\min(P_2,P_3)}=0.9997724081.
\]

Both must be at most $0.85$.  Equivalently, their relative prominence
depths are only $0.00100047$ and $0.00022759$, whereas the contract
requires at least $0.15$.  The secondary-peak height floor passes
($\min P_i/\max P_i=0.99845786$); the valley-resolution floor fails by a
large margin.

I also checked whether catalyst weights alone could repair the redesigned
geometry.  An independent real-derivative search comprised:

1. a global $0.001$-spaced scan of all 501,501 simplex controls on
   $0.3\le t\le30$;
2. 160,601 global-grid-plus-random controls with extra sampling around the
   five-root pocket; and
3. a $10^{-5}$-spaced local scan of 220,951 controls around that pocket.

The best screened balance occurred at

\[
 w=(0.30242,\;0.32143,\;0.37615),
\]

with independently refined stationary times

\[
 4.140616785, 5.544296868, 6.904995302,
 8.764421093, 10.643568820
\]

and valley ratios

\[
 0.9994424229,\qquad 0.9994500123.
\]

This search is not an interval proof of the global optimum, but it found no
remotely plausible route from approximately $0.9995$ to $0.85$ by moving
weights in the same geometry.  A prospective search must vary spatial
supports (centres and/or widths, subject to the same rate and budget bounds)
and optimize prominence as a primary objective.  It must not optimize a cusp
first and check visibility afterward.

The compact-time weak-budget theorem does not remove this blocker.  Since
$f_B/B\to G$ in the relevant mixed jets as $B\downarrow0$, these valley
ratios remain close to one for sufficiently small $B$.  A $15\%$ valley
depth would require either a more robust free-exposure geometry or a
nonperturbative finite-$B$ mechanism that must be computed and proved
separately.

## 7. Finite-volume comparison audit

No assembly error was found in the comparison path.  Replacing the three
patch profiles and their generator-action columns while retaining the free
midpoint/relative generators is algebraically correct; all three half-widths
are the same in the frozen parameters.  The 65-grid current-geometry row also
reproduces the pinned weak-budget artifact.

The comparison has three strict scope limits:

1. It imports the existing Scharfetter--Gummel/factorized implementation and
   is not an independent PDE solver.
2. Every mesh is odd and each row uses that mesh's own cusp and normal
   direction.  It is not an odd/even study and does not demonstrate one fixed
   absolute control converging pointwise.
3. The zero-order unbounded Gaussian mass outside the old finite box is below
   $3.79\times10^{-9}$ and $2.26\times10^{-9}$, but this is not a
   reflecting-boundary error bound for time/control jets.

The data themselves expose the limitation: the redesigned scaled fourth jet
moves from $-4.92$ on the 65-grid to $-7.87$ on the 113-grid while the
direct value is $-9.20$, and the five-root step topology is nonmonotone.
The producer and note already state these caveats, so this is an open
verification gate rather than a hidden code defect.

## 8. Manuscript decision

**Submission manuscript: NO, not as evidence of observable trimodality or a
passed PRR result.**

The quotient derivation, exact clock factorization, determinant/rank recipe,
and result-informed cusp can enter an internal working draft if every
occurrence is labeled as analytical structure or exploratory topology.  The
five-root curve must carry its two valley ratios and `project_gate_passed =
false`.  It must not be used in the title, abstract, conclusions, phase
diagram, or a displayed “trimodal design” claim until the observability gate
is met prospectively.

## 9. Minimum formal certificate still required

Even after a new observable geometry is found, promotion requires:

1. a prospective freeze of geometry, controls, time window, tolerances, and
   all prominence/mass/rate floors;
2. interval or ball bounds for compact-bump quadrature, the Fourier tail (or
   wrapped-kernel alternative), contact quadrature, and time jets;
3. a unique determinant-root enclosure, an interval-positive affine null
   vector, a nonzero fourth-jet enclosure, and a positive lower bound on the
   second unfolding singular value;
4. disjoint enclosures for all five simple roots, derivative-sign partitions
   between them, early-time and long-time tail signs, curvature margins, and
   the $0.85$ valley ratios;
5. an odd/even finite-volume or FEM campaign that continues the cusp and both
   neighboring fold sheets at fixed physical parameters, plus a genuinely
   independent solver and the contracted $L^1$ comparison;
6. a mixed-jet finite-box/reflection error bound rather than a zero-order
   Gaussian tail diagnostic;
7. an explicit admissible positive budget $B_*>0$, followed by independent
   killed-Doi checks at frozen $B\le B_*$, including event mass and the
   global density tail; and
8. the declared physical-$d=3$ sphere-contact calculation if the PRR story
   continues to claim dimensional generality.

The current frozen files are valuable because they validate the analytical
kernel and reveal the correct geometric mechanism--a local cusp coexisting
with a remote fold pair.  Their more important adversarial lesson is that
topological mode count and experimentally resolvable multimodality are very
different gates.
