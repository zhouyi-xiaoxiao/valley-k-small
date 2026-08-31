# Direct continuum free-exposure exploration

## Evidence boundary

**Status: RESULT_INFORMED_EXPLORATION_NOT_FORMAL_EVIDENCE.**

The patch centres, approximate discrete cusp locations, and the promising
five-root structure for the redesigned centres were known before this
calculation. This is therefore an independent mathematical/numerical
cross-check and a design tool for a future frozen study. It is not
preregistered discovery, positive-budget Doi evidence, an interval proof, or a
project-gate pass. No production artifact or manuscript source was changed by
this exploration.

The executable and its generated result are:

- scratch/continuum_free_exposure_exploration.py, SHA-256
  3eae6d3216f58d669554450e13b2720c6fed56de7d8b1dc8698f2b5b6e98f3a0;
- scratch/continuum_free_exposure_exploration_result.json, SHA-256
  1b23fc6f91f002fb3f1396708c96e9e0056e4df66e0120928bd386da95e3c1f7.

The calculation runs in about two minutes in the repository virtual
environment:

~~~bash
.venv/bin/python \
  research/reports/encounter_multimodal_prr/scratch/continuum_free_exposure_exploration.py
~~~

## Main result

The 65-cell longitudinal grid is not responsible for the existence of the
free-exposure cusp. Both geometries possess a nondegenerate positive-weight
cusp in a direct continuum calculation on
\(\mathbb R\times\mathbb T_W\). The spatial redesign is materially better:
its continuum cusp has a nearby five-root
maximum--minimum--maximum--minimum--maximum branch, hence three density
maxima. The current geometry has only the local cusp-created two-maxima
branch.

| geometry | continuum \(t_c\) | cusp weights | scaled \(G^{(4)}\) | unfolding SVD ratio | selected inward topology |
| --- | ---: | --- | ---: | ---: | --- |
| current \((0.48,0.67,0.86)\) | 9.285177622314 | \((0.3447920483,0.2702851497,0.3849228020)\) | -18.12560057 | 0.42913960 | max--min--max (2 maxima) |
| redesigned \((0.37,0.61,0.85)\) | 8.997541071494 | \((0.2990353392,0.3259755118,0.3749891490)\) | -9.19755679 | 0.46706124 | max--min--max--min--max (3 maxima) |

The selected continuum stationary roots are:

| geometry / inward normal step | stationary times and topology |
| --- | --- |
| current / \(0.005\) | 8.204148194 max; 9.285177622 min; 10.546148839 max |
| redesigned / \(0.005\) | 4.168876490 max; 5.391260083 min; 7.031985343 max; 8.997541071 min; 10.403620200 max |

Every reported root above was refined with the directly differentiated
continuum clock, not read from a sampled plot. The largest scaled first-jet
residual is \(4.4\times10^{-13}\). At both cusps the weights are strictly
interior, the fourth derivative is far from zero, and the two resource-tangent
directions are well conditioned.

This confirms the **existence and organizing mechanism** of a continuum
trimodal free-exposure branch for the redesigned spatial configuration. It
does not yet confirm that one fixed absolute weight vector stays trimodal on
all numerical meshes or at finite installed budget.

## Continuum formula

Let

\[
 b(u)=I_b^{-1}\exp[-(1-u^2)^{-1}]\mathbf 1_{|u|<1}
\]

be the normalized compact bump. For the OU generator
\(\kappa\partial_{xx}-\gamma(x-m)\partial_x\), the unbounded transition
density is Gaussian with

\[
 \mu_t(x_0)=m+(x_0-m)e^{-\gamma t},\qquad
 s_t^2={\kappa\over\gamma}(1-e^{-2\gamma t}).
\]

For midpoint initial half-width \(\epsilon_z\), patch half-width \(\sigma\),
and centre \(z_j\), the longitudinal clock is the compact double integral

\[
 a_j(t)={1\over W}
 \int_{-1}^{1}\!\!\int_{-1}^{1}
 b(u)b(v)\,
 p_{\rm OU}\!\left(z_j+\sigma v,t\mid z_0+\epsilon_z u;
                  \kappa={D\over2},m\right)\,du\,dv.
\]

For physical \(d=2\), write \(x=r_\parallel\), \(y=r_\perp\),
\(\omega=2\pi/W\), and let \(\widehat q_k\) be the cosine coefficients of the
initial transverse compact bump. The free probability that the transverse
coordinate lies in \([-h,h]\) is

\[
 H(h,t)={2h\over W}+{4\over W}\sum_{k\ge1}
 \widehat q_k e^{-2D(k\omega)^2t}
 {\sin(k\omega h)\over k\omega}.
\]

Using \(x=a\sin\vartheta\), \(h=a\cos\vartheta\), the exact disk-contact
factor becomes the one-dimensional smooth quadrature

\[
 c_2(t)=\int_{-\pi/2}^{\pi/2}
 a\cos\vartheta\;\bar p_\parallel(a\sin\vartheta,t)\;
 H(a\cos\vartheta,t)\,d\vartheta,
\]

where \(\bar p_\parallel\) is the OU transition density averaged over the
initial relative-parallel compact bump, now with \(\kappa=2D\) and mean zero.
Thus the continuum channel is

\[
 g_j(t)=a_j(t)c_2(t).
\]

This removes the \(65\times65\times49\) state discretization altogether. It
uses only compact Gauss--Legendre quadratures and a rapidly convergent torus
Fourier sum.

### Direct time jets

The transition kernels are analytic for \(\Re t>0\). For a Cauchy circle of
radius \(\rho<t\), the script evaluates orders zero through four from

\[
 g_j^{(n)}(t)\simeq {n!\over M\rho^n}\sum_{\ell=0}^{M-1}
 g_j(t+\rho e^{2\pi i\ell/M})e^{-2\pi i n\ell/M}.
\]

It independently differentiates \(a_j\), \(c_2\), and their direct product,
then checks the Leibniz identity

\[
 g_j^{(n)}=\sum_{q=0}^n{n\choose q}a_j^{(q)}c_2^{(n-q)}.
\]

Across the final computations, the maximum direct-product versus Leibniz
difference and the imaginary Cauchy residual are of order \(10^{-13}\).

For three catalysts, the root of

\[
 \Delta(t)=\det[g'(t),g''(t),g'''(t)]^T
\]

gives the candidate time. The normalized right null vector gives the budget
weights. The script then checks positivity, \(g^{(4)}(t_c)^Tw\ne0\), and the
rank-two resource-tangent unfolding. This is exactly the finite-dimensional
recipe in notes/pde_mixed_jet_theorem.md, now evaluated without a spatial
grid.

## Internal numerical convergence

Three independent quadrature/Cauchy configurations were used:

| level | bump / patch order | contact-angle order | torus modes | Cauchy samples / radius |
| --- | ---: | ---: | ---: | ---: |
| coarse | 48 / 48 | 64 | 16 | 32 / 0.55 |
| primary | 80 / 80 | 96 | 24 / 0.55 |
| fine | 112 / 112 | 144 | 32 / 0.42 |

The largest coarse-to-fine cusp-time difference is
\(4.6\times10^{-10}\); the largest weight difference is
\(2.2\times10^{-11}\). Primary-to-fine differences are smaller. These tiny
changes are numerical self-consistency evidence, not certified error bounds:
no interval or ball arithmetic is used.

## Finite-volume comparison

The direct continuum answer was compared with the existing factorized
Scharfetter--Gummel/finite-volume free clocks. The first row below reproduces
the current 65-grid weak-budget artifact. The larger meshes are an
exploratory refinement, not the frozen odd/even verification campaign.

### Current geometry

| mesh | \(t_c\) | weights | scaled \(G^{(4)}\) | unfolding ratio |
| --- | ---: | --- | ---: | ---: |
| \(65,65,49\) | 9.447750380 | \((0.344132,0.264237,0.391631)\) | -17.39696 | 0.45622 |
| \(81,81,65\) | 9.450809938 | \((0.349678,0.263279,0.387043)\) | -18.03238 | 0.44841 |
| \(97,97,81\) | 9.377867865 | \((0.345926,0.266927,0.387148)\) | -17.92383 | 0.44152 |
| \(113,113,97\) | 9.356921969 | \((0.346053,0.267542,0.386406)\) | -18.00572 | 0.43825 |
| direct continuum | 9.285177622 | \((0.344792,0.270285,0.384923)\) | -18.12560 | 0.42914 |

### Redesigned geometry

| mesh | \(t_c\) | weights | scaled \(G^{(4)}\) | unfolding ratio |
| --- | ---: | --- | ---: | ---: |
| \(65,65,49\) | 8.692585389 | \((0.295669,0.326155,0.378176)\) | -4.91891 | 0.40693 |
| \(81,81,65\) | 8.847777103 | \((0.304208,0.323618,0.372173)\) | -6.63130 | 0.42460 |
| \(97,97,81\) | 8.897707314 | \((0.299773,0.325111,0.375115)\) | -7.35777 | 0.43984 |
| \(113,113,97\) | 8.928599198 | \((0.300242,0.325071,0.374686)\) | -7.87124 | 0.44692 |
| direct continuum | 8.997541071 | \((0.299035,0.325976,0.374989)\) | -9.19756 | 0.46706 |

The mesh sequence is not monotone because compact patch and sharp disk
interfaces align differently with successive cell grids. Nevertheless the
fine values move toward the direct continuum values. At
\((113,113,97)\), both cusp times are within \(0.78\%\) of the direct result;
the redesigned weight error is \(1.21\times10^{-3}\) in max norm.

The finite-box omission probability under the corresponding unbounded free
kernels is below \(3.8\times10^{-9}\) for the midpoint and
\(2.3\times10^{-9}\) for the longitudinal relative coordinate over
\(0<t\le40\), even after maximizing over the extreme initial-support points.
This strongly suggests that the visible cusp shift is grid/interface error,
not reflection at the remote box faces. This tail check is an inference, not
a mixed-jet reflecting-boundary error theorem.

### The thin-wedge warning

The redesigned 65-grid has five alternating roots at its own cusp-normal step
\(5\times10^{-5}\), reproducing the earlier scratch observation. At step
\(0.002\) it has only three roots because the remote minimum/maximum pair has
already annihilated. In the direct continuum calculation the order is
reversed: steps through \(0.001\) have only the local three roots, while steps
\(0.002\) and \(0.005\) have five roots. The 97-grid has five roots at steps
\(0.001\) and \(0.002\); the 113-grid has five at \(0.002\). The 81-grid has
only three at the five screened steps.

Therefore the correct conclusion is:

1. a trimodal wedge exists in the direct continuum redesigned model;
2. a corresponding wedge is visible on several finite-volume meshes;
3. the coarse-grid cusp shift is wider than the thinnest wedge, so one fixed
   absolute weight vector is not yet pointwise mesh-stable; and
4. formal evidence must continue the **cusp and both neighboring fold sheets**
   across odd/even meshes, rather than refining one hand-picked control.

## Generalization to physical \(d=3\) and higher dimension

The method extends without a tensor state grid. Put \(m=d-1\) for the number
of periodic transverse relative coordinates. The initial transverse density
has Fourier coefficients \(\widehat q_k\), \(k\in\mathbb Z^m\), and each mode
decays as

\[
 \exp[-2D|2\pi k/W|^2t].
\]

At a fixed longitudinal separation \(x\), contact restricts the transverse
coordinates to an \(m\)-ball of radius
\(h(x)=\sqrt{a^2-x^2}\). Its Fourier transform is explicit:

\[
 \int_{|y|<h}e^{i\xi\cdot y}\,dy
 =(2\pi)^{m/2}h^m\,
 {J_{m/2}(|\xi|h)\over(|\xi|h)^{m/2}},
\]

with the continuous \(k=0\) value equal to the \(m\)-ball volume. Hence
\(c_d(t)\) is a one-dimensional longitudinal quadrature plus an
\(m\)-dimensional Fourier sum. For physical \(d=3\), \(m=2\) and the disk
transform uses \(J_1\). The catalyst clocks still factor as
\(g_j(t)=a_j(t)c_d(t)\), and the same \(3\times3\) cusp determinant applies.

This is the more general and publishable analytical route: spatial
configuration enters through a few compact longitudinal clocks \(a_j\),
dimension/contact geometry enters through one common factor \(c_d\), and
modality boundaries are finite determinant/rank conditions rather than
brute-force killed-PDE scans.

For more than three patches, the same clock bank can map the fold/cusp
discriminant inside the conserved simplex. Higher modality can be organized
either by multiple separated cusps/folds or by higher \(A_k\) degeneracies.
With only three patches, a local cusp creates at most a max--min--max triple;
the redesigned trimodality occurs because that local triple coexists with a
separate earlier maximum/minimum pair. That distinction should be explicit
in any PRR claim.

## Recommended frozen follow-up

The direct continuum result is strong enough to justify a new prospectively
frozen study, but not to promote this scratch result directly into the paper.
The next study should:

1. freeze the redesigned centres \((0.37,0.61,0.85)\), half-width \(0.08\),
   quadrature orders, Fourier truncation, Cauchy circles, determinant bracket,
   cusp margins, and fold-sheet continuation region before execution;
2. certify the determinant root, positive null weight, fourth jet, unfolding
   singular value, and all five stationary roots with interval/ball
   arithmetic or explicit quadrature/Fourier remainder bounds;
3. use the direct continuum formula as the primary \(B=0\) calculation and
   reserve odd/even SG/FEM meshes for an independent solver cross-check;
4. continue the cusp and both fold sheets under mesh refinement, recording
   Hausdorff distance of the discriminant curves in simplex coordinates;
5. combine the certified margins with the compact-time weak-budget theorem to
   obtain a quantitative admissible \(B>0\), then verify it with two
   independent killed-PDE solvers; and
6. run the \(d=3\) sphere-contact Fourier--Bessel calculation with no geometry
   retuning, followed by a frozen positive-budget \(d=3\) check.

For journal strategy, the strongest package is not “another numerical
trimodal example.” It is:

> a conserved-reactivity spatial design principle in which continuum
> free-exposure clocks reduce the modality discriminant to explicit
> determinant/rank conditions, a redesigned physical 2D geometry realizes a
> cusp plus a remote fold pair, weak-budget analysis transfers the structure
> to Doi encounter times, and the same formula predicts the 2D-to-3D change.

That combination is plausibly PRR-level. The present exploration establishes
the first and most uncertain design step, while leaving the positive-budget,
certified-error, independent-solver, and \(d=3\) gates honestly open.
