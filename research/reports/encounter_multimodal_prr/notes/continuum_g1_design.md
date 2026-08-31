# Continuum G1 design audit: exact quotient, physical budget, and fold gate

Date: 2026-07-13  
Status: **design accepted for a finite predeclared discovery run; no continuum result exists yet**

## 1. Decision and claim boundary

G1 should not refine the old four-dimensional boundary-node encounter model.
Its state-count budget, sharp centre-selected masks, upwind transport, and
nonconverged fold coordinate are exactly the effects that G1 is meant to
remove.  The new calculation should instead use an exact symmetry quotient of
a continuum two-particle process.

The accepted primary model is two equal-diffusivity particles on the physical
cylinder

\[
  \mathcal C_d=\mathbb R\times\mathbb T_W^{d-1},
\]

with identical longitudinal Ornstein--Uhlenbeck confinement and free
transverse diffusion.  Catalytic patches are smooth longitudinal slabs,
invariant under common transverse translation.  Integrating out that common
translation gives an exact PDE in one longitudinal midpoint coordinate and
the full \(d\)-dimensional relative coordinate: physical dimension \(d\)
becomes PDE dimension \(d+1\).  For G1, \(d=2\), so the continuum solver is
three-dimensional rather than the old four-dimensional product solver.

This quotient has a real restriction: it describes transversely invariant
catalytic slabs, not arbitrary localized \(d\)-dimensional catalyst disks.  A
claim about arbitrary localized patches would again require a \(2d\)-dimensional
solver or a different exact symmetry.  G1 may establish a continuum fold for
the slab family only.

## 2. Old-code reuse audit

The old code is useful as tested algebra and as a source of failure cases, but
not as the continuum spatial discretization.

| Existing component | Decision | Reason / permitted use |
| --- | --- | --- |
| `packages/vkcore/src/vkcore/encounter2d.py::RectangularGrid2D` | rewrite | Boundary-node CTMC grid, duplicated endpoints, omitted outward jumps, and no finite-volume cell measure. |
| `reflecting_advection_diffusion_generator_2d` | rewrite | First-order upwind rates produced large cell Péclet errors in the old study; it is not a Scharfetter--Gummel FV operator. |
| `build_doi_encounter_2d` and `DoiEncounter2D` | rewrite | Builds the full two-walker product space, uses binary centre/contact masks, and has no exact quotient or cell-averaged smooth support. |
| `DoiCatalyticPatch` | rewrite | Represents circular, piecewise-constant patches.  G1 uses normalized one-dimensional smooth slab profiles. |
| `bilinear_initial_distribution_2d` and `contact_safe_initial_distribution_2d` | rewrite | They approximate point masses on the old product grid and change support with resolution.  G1 uses one fixed smooth continuum initial law and its exact cell integrals. |
| `PeriodicGrid2D` | reuse conventions only | Its nonduplicated cell-centre periodic indexing is sound, but it is hard-coded to a 2D torus rather than the mixed line--torus quotient. |
| `periodic_circular_cell_fractions` | do not use for evidence | Midpoint supersampling is acceptable for exploration but not for the G1 interface-convergence certificate.  The new contact fractions need deterministic error-controlled circle--rectangle integration. |
| `solve_periodic_doi_mean_time` | reference check only | Correctly uses relative diffusivity \(D_1+D_2\), but eliminates every centre coordinate and computes a mean, not a patterned reaction-time density. |
| `_fold_quantities`, `_state_and_sensitivity`, and `_solve_fold` in `validate_2d_matched_fold.py` | extract algebra into new report code | Generator actions, augmented exponential sensitivity, dimensionless residuals, and held-out normal-form tests are reusable after removing hard-coded grids, budgets, and output paths.  The old report-private module should not be imported directly. |
| `budget_projected_optimum` and Duhamel cross-checks in `validate_modality_susceptibility.py` | reuse algebra/tests after extraction | Useful later for G2.  They do not supply the new continuum spatial gradient by themselves. |
| `vkcore.morphology` | reuse only as a secondary label | G1 is certified by isolated roots and derivative signs.  A detector/classifier cannot establish the fold. |
| `vkcore.provenance`, publication plotting helpers, manifests | reuse directly | These are model-independent infrastructure. |

No old file needs modification.  The future implementation should be
report-owned until the continuum operator has passed its tests; only then
should a genuinely generic module be promoted into `vkcore`.

## 3. Physical two-particle process

### 3.1 Geometry and SDE

Write a particle position as \((X_i,Y_i)\), where
\(X_i\in\mathbb R\) is longitudinal and
\(Y_i\in\mathbb T_W^{d-1}\) is transverse.  The fixed unreacted transport is

\[
 \begin{aligned}
  dX_i &= -\gamma(X_i-m)\,dt+\sqrt{2D}\,dW_i^{\parallel},\\
  dY_i &= \sqrt{2D}\,dW_i^{\perp}\pmod W,
  \qquad i=1,2,
 \end{aligned}
 \tag{3.1}
\]

with independent Brownian motions, \(D>0\), and \(\gamma>0\).  Equal
diffusivities and the same OU stiffness are deliberate G1 hypotheses, not
innocent simplifications: they make the physical midpoint the
diffusion-decoupling coordinate and remove mixed derivatives.

Define

\[
 z=\frac{X_1+X_2}{2},\qquad
 r_\parallel=X_1-X_2,\qquad
 r_\perp=Y_1-Y_2\pmod W.
\tag{3.2}
\]

The longitudinal map has unit absolute Jacobian, with
\(X_1=z+r_\parallel/2\) and \(X_2=z-r_\parallel/2\).  In the transverse
directions, use \((Y_2,r_\perp)\); this is a Haar-measure-preserving change of
variables on the torus.  Integrating the forward equation over \(Y_2\) removes
the common-coordinate and mixed common--relative derivatives by periodicity.
Thus the marginal closes whenever transport and killing are independent of
the common translation; uniformity of the initial common coordinate is a
convenient pilot choice, not a mathematical requirement for closure.

### 3.2 Exact quotient PDE

Let \(q(z,r,t)\) be the normalized density after integrating over the common
transverse translation, with

\[
 r=(r_\parallel,r_\perp)
 \in\mathbb R\times\mathbb T_W^{d-1}.
\]

The exact killed Fokker--Planck equation is

\[
\boxed{
 \begin{aligned}
 \partial_t q={}&
  \frac D2\,\partial_{zz}q
  +\gamma\,\partial_z\!\left[(z-m)q\right]\\
 &+2D\,\partial_{r_\parallel r_\parallel}q
  +\gamma\,\partial_{r_\parallel}\!\left[r_\parallel q\right]
  +2D\,\Delta_{\mathbb T_W^{d-1}}q
  -K_{\boldsymbol w}(z,r)q .
 \end{aligned}}
\tag{3.3}
\]

Thus the midpoint diffusivity is \(D_c=D/2\) and the relative diffusivity is
\(D_r=2D\).  There are no hidden products of one-dimensional encounter laws:
the contact condition below is the true \(d\)-dimensional ball in the relative
coordinate.

The exact boundary conditions are periodicity in every component of
\(r_\perp\) and natural decay/zero probability flux as
\(|z|+|r_\parallel|\to\infty\).  The numerical box uses zero flux at its
artificial longitudinal boundaries, but this is a truncation, not a physical
reflecting wall, and must pass the box-enlargement gate in Section 8.

### 3.3 Contact sphere

For the representative of \(r_\perp\) in
\([-W/2,W/2)^{d-1}\), set

\[
 \rho(r)^2=r_\parallel^2+
 \sum_{k=2}^{d}\delta_W(r_k)^2,
 \qquad
 \delta_W(s)=\min_{n\in\mathbb Z}|s+nW|.
\tag{3.4}
\]

The Doi contact set is

\[
 \mathcal A_a=\{r:\rho(r)<a\},
 \qquad 0<a<W/2.
\tag{3.5}
\]

The strict inequality \(a<W/2\) keeps the contact ball away from the torus
cut locus.  On the chosen fundamental cell the reactive set is therefore one
ordinary Euclidean disk for \(d=2\) and one ordinary sphere for \(d=3\), not
overlapping periodic copies.

### 3.4 Smooth initial law

Use the fixed normalized bump

\[
 \beta_{\epsilon,x_0}(x)=
 \frac{1}{\epsilon I_0}
 \exp\!\left[-\frac{1}{1-((x-x_0)/\epsilon)^2}\right]
 \mathbf 1_{|x-x_0|<\epsilon},
 \quad
 I_0=\int_{-1}^{1}e^{-1/(1-u^2)}du.
\tag{3.6}
\]

Use its wrapped version for transverse relative coordinates and set

\[
 q_0(z,r)=
 \beta_{\epsilon_z,z_0}(z)
 \beta_{\epsilon_r,r_{\parallel,0}}(r_\parallel)
 \prod_{k=2}^{d}\beta^{\rm per}_{\epsilon_r,r_{k,0}}(r_k).
\tag{3.7}
\]

The full physical initial law is uniform in the common transverse translation.
Cell values must be cell integrals of Eq. (3.7), not nearest-node or bilinear
point approximations.  The support must satisfy

\[
 \inf_{r\in\operatorname{supp}q_0}\rho(r)>a,
\tag{3.8}
\]

so \(f(0)=0\) exactly at every resolution.

## 4. Physical conserved budget and three smooth patches

Let

\[
 \phi_j(z)=\frac{1}{\sigma_j I_0}
 \exp\!\left[-\frac{1}{1-((z-z_j)/\sigma_j)^2}\right]
 \mathbf 1_{|z-z_j|<\sigma_j},
 \qquad \int_{\mathbb R}\phi_j(z)\,dz=1.
\tag{4.1}
\]

For simplex weights \(w_j\ge0\), \(\sum_jw_j=1\), define

\[
 \kappa_{\boldsymbol w}(z)=
 \frac{\mathcal B}{W^{d-1}}
 \sum_{j\in\{N,M,F\}}w_j\phi_j(z),
 \qquad
 K_{\boldsymbol w}(z,r)=
 \mathbf 1_{\mathcal A_a}(r)\kappa_{\boldsymbol w}(z).
\tag{4.2}
\]

The conserved physical catalyst amount is

\[
 \int_{\mathcal C_d}\kappa_{\boldsymbol w}(z)\,dc
 =\mathcal B.
\tag{4.3}
\]

Thus \(\mathcal B\) is the full installed centre-space catalyst amount, held
fixed when \(W\) or the physical dimension changes.  The longitudinal
reactivity integral per unit transverse measure is
\(\mathcal B/W^{d-1}\); it is not a second resource definition.  None of the
following is an admissible substitute:

- an unweighted sum over quotient or two-particle states;
- an integral over the contact configuration space;
- stationary-exposure weighting;
- a mesh-dependent rate chosen to match a reference endpoint.

The contact-volume integral of \(K_{\boldsymbol w}\) is also constant because
the contact geometry is fixed, but it is a consequence, not the resource
definition.

For the first one-control G1 line, predeclare

\[
 \boldsymbol w^{-}=(0.70,0.25,0.05),\qquad
 \boldsymbol w^{+}=(0.05,0.25,0.70),
\]

\[
 \boldsymbol w(\theta)=(1-\theta)\boldsymbol w^{-}
 +\theta\boldsymbol w^{+},\qquad 0\le\theta\le1.
\tag{4.4}
\]

This moves budget only from the near to the far slab while retaining a
positive middle rate.  Its derivative is analytic and mesh independent:

\[
 \partial_\theta\kappa
 =\frac{0.65\mathcal B}{W^{d-1}}(\phi_F-\phi_N),
 \qquad \int\partial_\theta\kappa\,dz=0.
\tag{4.5}
\]

The admissibility certificate is endpoint based but covers the entire
declared affine control segment, not merely the sampled value of \(\theta\):
both endpoint vectors must sum to one and be componentwise nonnegative.
Convexity then proves these properties for every \(\theta\in[0,1]\).  The
implementation must additionally persist the endpoint minima of
\(\kappa_{\boldsymbol w}\) and \(K_{\boldsymbol w}\).  A unit-sum endpoint with
one negative component is a failure even if the currently sampled midpoint
happens to remain nonnegative.  No positivity claim is made for the affine
extension outside the admissible interval \([0,1]\).

If the predeclared line has no topology change on the discovery grid, one
coarse simplex scan with spacing 0.1 is allowed to choose a single interior
bracketing segment.  That segment and all parameters must be written to a
timestamped manifest before any confirmation-grid result is inspected.  No
line, patch, budget, or initial-law retuning is allowed during odd/even
confirmation.

## 5. Conservative Scharfetter--Gummel finite volume architecture

### 5.1 Cell masses and fluxes

Use a tensor-product cell-centred mesh in

\[
 [z_-,z_+]\times[r_-,r_+]\times\mathbb T_W^{d-1}.
\]

Store cell masses \(p_i=q_iV_i\), not nodal densities.  Write every free
coordinate flux as

\[
 J=bq-D_*\partial_xq.
\]

At an interior face between cells \(i\) and \(i+1\), use

\[
 J_{i+1/2}=
 \frac{D_*}{h}
 \left[\mathscr B(-\mathrm{Pe})q_i
       -\mathscr B(\mathrm{Pe})q_{i+1}\right],
\quad
 \mathrm{Pe}=\frac{b_{i+1/2}h}{D_*},
\tag{5.1}
\]

where

\[
 \mathscr B(x)=\frac{x}{e^x-1}
\tag{5.2}
\]

is evaluated with `expm1` and a small-\(x\) series.  The relevant coefficients
are

\[
 (b_z,D_z)=(-\gamma(z-m),D/2),\qquad
 (b_{r_\parallel},D_r)=(-\gamma r_\parallel,2D),
\]

and \((b,D_*)=(0,2D)\) transversely.  Set exterior longitudinal face fluxes
to zero and wrap transverse faces periodically.  The resulting free row
generator \(Q_h\) must have nonnegative off-diagonal entries and zero row
sums to scaled roundoff.

The free operator is a Kronecker sum of one-dimensional SG operators.  G1 may
assemble it as sparse CSR; the interface should also admit tensor/matrix-free
actions because G5 in physical \(d=3\) is a four-dimensional quotient.

### 5.2 Cell-averaged killing without mesh renormalization

For every longitudinal cell compute

\[
 \bar\phi_{j,k}=h_z^{-1}\int_{I_k}\phi_j(z)\,dz
\tag{5.3}
\]

by fixed error-controlled Gauss quadrature.  For every relative cell compute
the deterministic geometric fraction

\[
 \bar\chi_{a,\ell}=|C_\ell|^{-1}
 \int_{C_\ell}\mathbf 1_{\mathcal A_a}(r)\,dr.
\tag{5.4}
\]

In G1 this is a circle--rectangle intersection on
\((r_\parallel,r_\perp)\).  Use an analytic intersection formula or adaptive
deterministic quadrature with a persisted error estimate and an independent
high-order local reference comparison; fixed midpoint supersampling is not
confirmation evidence.  Since the quotient cells are
Cartesian and Eq. (4.2) is separable, the exact cell average factorizes:

\[
 k_{k\ell}(\theta)=
 \bar\chi_{a,\ell}\,
 \frac{\mathcal B}{W^{d-1}}
 \sum_jw_j(\theta)\bar\phi_{j,k}.
\tag{5.5}
\]

Do not renormalize Eq. (5.5) independently on each mesh.  The compact patch
supports lie inside the numerical box, so the cell integrals must instead
satisfy

\[
 W^{d-1}\sum_kh_z\,
 \frac{\mathcal B}{W^{d-1}}
 \sum_jw_j\bar\phi_{j,k}
 =\mathcal B
\tag{5.6}
\]

to the quadrature tolerance for every \(\theta\).

For each of the three catalyst profiles, confirmation must retain the
production quadrature error estimate and compare every cell mass with an
independent fixed-order local Gauss reference that does not call the
production bump integrator.  The zeroth moment, cell-centre first moment,
maximum per-cell error, and relative \(L^1\) error are separate gates.  The
same independent checks apply to all three initial marginals, including the
wrapped transverse bump across the periodic cut.  This prevents a translated
but still normalized set of patches from passing through the global material
budget alone.

### 5.3 Killed semigroup, density, and fold derivatives

With the row convention used in the preceding report,

\[
 A_h(\theta)=Q_h-\operatorname{diag}k_h(\theta),
 \qquad
 \dot p=A_h(\theta)^Tp.
\tag{5.7}
\]

Then

\[
 S_h(t)=\mathbf1^Tp(t),\qquad
 f_h(t,\theta)=p(t)^Tk_h(\theta),
\tag{5.8}
\]

and

\[
 f_t=p^TAk,\quad
 f_{tt}=p^TA^2k,\quad
 f_{ttt}=p^TA^3k.
\tag{5.9}
\]

Because \(Q_h\) is fixed and \(k_h\) is affine in \(\theta\),

\[
 A_\theta=-\operatorname{diag}k_\theta.
\]

Obtain \(p_\theta\) from the same augmented exponential used in the old fold
audit,

\[
 \frac d{dt}
 \begin{pmatrix}p\\p_\theta\end{pmatrix}
 =
 \begin{pmatrix}A^T&0\\A_\theta^T&A^T\end{pmatrix}
 \begin{pmatrix}p\\p_\theta\end{pmatrix},
\tag{5.10}
\]

and include both the semigroup and observable derivatives in
\(f_{t\theta}\) and \(f_{tt\theta}\).  Solve

\[
 f_t(t_c,\theta_c)=f_{tt}(t_c,\theta_c)=0
\tag{5.11}
\]

with analytic Jacobian

\[
 D_{(t,\theta)}(f_t,f_{tt})=
 \begin{pmatrix}
 f_{tt}&f_{t\theta}\\
 f_{ttt}&f_{tt\theta}
 \end{pmatrix}.
\tag{5.12}
\]

The nondegeneracy determinant at the fold is

\[
 -f_{t\theta}f_{ttt}\ne0.
\tag{5.13}
\]

Sampled density peaks may guide discovery, but only Eqs. (5.11)--(5.13),
held-out root isolation, and cross-grid convergence can certify G1.

## 6. Minimum local pilot

The following nondimensional parameter set is frozen for the first discovery
run.  It is chosen so that the deterministic OU midpoint reaches the three
patch centres on separated time scales while the relative mean enters the
contact radius between the first two clocks.

| Quantity | Pilot value |
| --- | ---: |
| physical dimension | \(d=2\) |
| particle diffusivity | \(D=0.0045\) |
| OU stiffness / mean | \(\gamma=0.1\), \(m=0.95\) |
| transverse circumference | \(W=1\) |
| contact radius | \(a=0.16\) |
| midpoint start / bump half-width | \(z_0=0.14\), \(\epsilon_z=0.02\) |
| relative start | \((r_{\parallel,0},r_{\perp,0})=(-0.35,0)\) |
| relative bump half-width | \(\epsilon_r=0.02\) in each component |
| patch centres | \((z_N,z_M,z_F)=(0.48,0.67,0.86)\) |
| patch half-widths | \(\sigma_N=\sigma_M=\sigma_F=0.08\) |
| full installed centre-space budget | \(\mathcal B=0.6\) |
| quotient box | \(z\in[-0.25,1.85]\), \(r_\parallel\in[-1.8,1.8]\), \(r_\perp\in[-0.5,0.5)\) |
| discovery time window | \(t\in[0,80]\); extend the root/tail audit to \(t=200\) |
| discovery mesh | \((N_z,N_{r_\parallel},N_{r_\perp})=(65,65,49)\), 207,025 cells |

The initial support is contact-safe because
\(|r_\parallel|\ge0.33>a\).  The deterministic midpoint times for the near,
middle, and far centres are approximately \(5.44\), \(10.62\), and
\(21.97\), while the deterministic relative mean reaches \(|r|=a\) at
approximately \(7.83\).  The normalized bump has
\(I_0\simeq0.4439938162\), so a pure-patch local peak rate is approximately
\(6.21\).  These values are design diagnostics, not evidence that a fold must
exist.

The discovery run evaluates the predeclared line in Eq. (4.4), isolates every
sign-changing root of \(f_t\) on the declared window, and searches for an
interior fold.  No G1 claim may be made from the discovery mesh.  If the line
fails, the one permitted coarse simplex scan is performed as specified in
Section 4; if that also contains no interior topology boundary, this parameter
set is a No-Go and must be redesigned before any refinement campaign.

## 7. Odd/even refinement design

After an interior fold line is frozen, use two independent parity sequences:

| Level | even \((N_z,N_{r_\parallel},N_{r_\perp})\) | odd \((N_z,N_{r_\parallel},N_{r_\perp})\) |
| ---: | ---: | ---: |
| 1 | \((64,64,48)\) | \((65,65,49)\) |
| 2 | \((80,80,64)\) | \((81,81,65)\) |
| 3 | \((96,96,80)\) | \((97,97,81)\) |
| 4 | \((112,112,96)\) | \((113,113,97)\) |

The finest odd grid has 1,238,593 cells.  On it, the patch support width spans
about 8.6 longitudinal cells, the contact diameter spans about 10.0
longitudinal-relative cells and 31 transverse-relative cells, and the maximum
box-wide SG Péclet numbers are approximately 0.99 in \(z\) and 0.64 in
\(r_\parallel\).  Coarser levels are convergence data, not resolved continuum
evidence.

For a scalar observable \(x_h\), fit each parity sequence separately to

\[
 x_h=x_\infty+c\eta_h^p,
 \qquad
 \eta_h=\max\left\{
 \frac{h_z}{\sigma},\frac{h_{r_\parallel}}{a},
 \frac{h_{r_\perp}}{a}\right\},
\tag{7.1}
\]

using all four levels and a leave-coarsest-out check.  Do not impose second
order: the sharp contact interface can reduce the observed order.  A usable
fit must have stable extrapolants and \(0.8\le p\le2.5\); otherwise the
sequence is not asymptotic and G1 does not pass.

## 8. Quantitative G1 acceptance gates

All gates are evaluated with the same frozen physical parameters and fold
path.

### 8.1 Operator and quadrature gates

1. Free SG off-diagonal rates are nonnegative and scaled row-sum error is
   below \(10^{-12}\).  Selected asymmetric interior, reflecting-boundary,
   and periodic-wrap rates in each of \(z,r_\parallel,r_\perp\) must also agree
   with independently evaluated analytic SG/periodic rates to \(10^{-12}\)
   absolutely and relatively; this is the sentinel for swapped midpoint and
   relative diffusion/drift coefficients.
2. Patch integrals and Eq. (5.6) have relative error below \(10^{-10}\) for
   every tested mesh and \(\theta\); no meshwise budget fitting is permitted.
   Every stored production patch-quadrature error estimate must separately be
   below \(10^{-11}\).  For every catalyst patch, the zeroth moment error is
   below \(10^{-10}\), the first-moment error is at most half a cell, and the
   independent per-cell and relative \(L^1\) errors are below
   \(2\times10^{-10}\).
3. The contact cell-fraction routine supplies a deterministic error estimate,
   and doubling its internal quadrature order changes \((t_c,\theta_c)\) by
   less than \(0.1\%\).
4. The initial cell masses are nonnegative, sum to one within \(10^{-12}\),
   reproduce the declared first moments, and have exactly zero contact mass.
   At the deliberately coarse G1a smoke stage, the reconstructed linear and
   circular first-moment errors must be reported and may not exceed one half
   of the corresponding cell width.  Confirmation evidence must show their
   convergence under the frozen odd/even refinements; the half-cell smoke
   tolerance is not a continuum accuracy claim.  Each of the three marginal
   bump profiles must also satisfy the independent zeroth/first-moment,
   per-cell, and relative \(L^1\) checks in item 2, including circular moments
   and a wrapped local reference for \(r_\perp\).
5. The killed operator satisfies the discrete mass identity and the maximum
   observed mass-balance error is below \(10^{-9}\).
6. On a small operator, sparse exponential actions agree with dense `expm`;
   on every confirmation grid, one-shot and two-half-step exponential actions
   agree below \(10^{-10}\) relatively for the state and augmented sensitivity
   at the fold.  The latter is a semigroup consistency check, not an
   independent physical solver.
7. Both endpoint weight sums equal one to \(10^{-14}\), all endpoint
   components, endpoint \(\kappa\), and endpoint killing values are
   nonnegative to \(10^{-14}\), and the convex endpoint certificate covers
   every admissible \(\theta\in[0,1]\).  Current-control nonnegativity is
   reported separately and cannot substitute for this line certificate.

### 8.2 Fold and observability gates

1. The fold is interior: \(0.15<\theta_c<0.85\), \(0<t_c<80\), and its
   continuation does not approach a positivity boundary.
2. The dimensionless residuals

   \[
   |f_t|t_c/f<10^{-8},\qquad |f_{tt}|t_c^2/f<10^{-8}
   \]

   hold on every confirmation level.
3. \(f_{ttt}\) and \(f_{t\theta}\) retain fixed nonzero signs, and their
   extrapolated uncertainty intervals exclude zero by at least a factor of
   ten.
4. Held-out points on both sides of the fold recover the correct no-pair / one
   min--max-pair topology.  Near-fold separation and prominence agree with the
   \(1/2\) and \(3/2\) normal-form predictions before any wide-range regression.
5. At one frozen supercritical control at least 0.05 from the fold, the
   secondary peak is at least 10% of the main peak and the intervening valley
   is at most 85% of the smaller adjacent peak.  All relevant derivative roots
   are isolated rather than inferred from sampled plots.
6. The derivative scan extends at least to \(t=200\) and then to a certified
   monotone spectral tail, so an uninspected late root cannot change the
   reported morphology.  Because the SG OU operator is designed to satisfy
   discrete detailed balance and diagonal killing preserves reversibility,
   this certificate should use a residual-validated principal eigenpair and a
   bound on the derivative contribution of the remaining spectrum; a negative
   value at one arbitrary stopping time is not a tail proof.

### 8.3 Mesh and box gates

1. Within each parity sequence, the relative change from level 3 to level 4 is
   below 1% for both \(t_c\) and \(\theta_c\).
2. Odd and even extrapolants disagree by less than 1% for both fold
   coordinates.
3. The finest-level and extrapolated disagreements are below 5% for
   \(f_{ttt}\), \(f_{t\theta}\), and the projected fold determinant.
4. The fitted orders and extrapolants pass Eq. (7.1) and the
   leave-coarsest-out stability check.  Oscillation without a stable parity
   limit is failure, not an uncertainty bar.
5. Repeating the two finest levels on a box enlarged by at least 20% in both
   nonperiodic coordinates, at matched local spacing and without refitting,
   changes fold coordinates by less than 0.2% and jets by less than 1%.
6. Up to the complete fold/held-out audit horizon, mass in the outer two
   longitudinal cell layers is below \(10^{-8}\) of survival mass.  Failure
   indicates an artificial reflecting-return clock.

## 9. G1 Go/No-Go decision

### GO

G1 supplies **continuum-consistent finite-window numerical evidence** only if
every gate in Section 8 passes and both parity sequences approach one interior,
nondegenerate, physically observable fold under the same material budget.
Passing G1 authorizes G2 cusp continuation and G3 independent Brownian/Robin
validation.  It does not by itself establish a discretization-to-continuum
theorem, continuum root transfer, a cusp, trimodality, arbitrary-mode
construction, or a localized-patch theorem.  The stronger label **Continuum
Verified** is reserved for the separate C0--C7 program, including computable
`r = 0, 1, 2` error bounds and strict root-margin transfer inequalities under
one hash-bound contract.

### NO-GO

G1 is a No-Go if any of the following occurs:

- no interior topology boundary exists in the bounded discovery protocol;
- the fold moves to a simplex boundary as the mesh is refined;
- odd and even sequences approach different values or do not enter an
  asymptotic regime;
- \(f_{ttt}\) or \(f_{t\theta}\) vanishes in the extrapolated limit;
- a different contact quadrature, physical box, or exact budget evaluation
  changes the fold beyond the gates;
- the secondary mode never reaches the predeclared observability floor;
- the apparent late mode is generated by the artificial zero-flux truncation.

A No-Go leaves the earlier finite-model PRE result intact.  It forbids using
this family as the PRR continuum bridge; it should not be repaired by silently
retuning a confirmation mesh.

## 10. Remaining mathematical and physical risks

These risks are unresolved until the corresponding evidence exists.

1. **A midpoint on a fully periodic space is not globally single-valued.**
   One cannot set both the relative coordinate and arithmetic midpoint on
   \(\mathbb T^d\) without choosing lifts, a double cover, or twisted boundary
   conditions.  The line--torus cylinder avoids this by using a real
   longitudinal midpoint and never using a transverse midpoint.  Replacing the
   cylinder by a fully periodic box would invalidate Eq. (3.3).
2. **Unequal diffusivities break the G1 decoupling.**  For \(D_1\ne D_2\), the
   physical midpoint produces mixed midpoint--relative diffusion.  Using the
   diffusivity-weighted centre removes that mixed term but changes the
   physical catalyst coordinate.  Neither substitution is allowed in G1.
3. **The quotient requires exact transverse symmetry of the operator and
   sink.**  A localized transverse catalyst, common-coordinate-dependent
   transport, or a transverse wall breaks the marginal closure and restores
   missing coordinates.  A nonuniform initial common-coordinate law can still
   be marginalized on the torus, but G1 deliberately uses the simpler uniform
   ensemble.  The manuscript must call the patches slabs.
4. **The contact sphere must remain away from the torus cut locus.**  The
   condition \(a<W/2\) is structural.  At or beyond it, minimum-image contact
   is nonsmooth and periodic copies overlap.
5. **The material budget is a modelling choice, not an exposure budget.**
   Equation (4.3) measures installed catalyst.  It does not equal integrated
   pathwise hazard, splitting probability, steady flux, or stationary-weighted
   exposure.  Claims must be phrased accordingly.
6. **A sharp contact indicator lowers spatial regularity.**  Analyticity in
   time for \(t>0\) does not guarantee a second-order spatial fold jet.  The
   observed order must be measured; contact quadrature and parity convergence
   are essential.  A smoothed-contact sensitivity may be reported only as a
   separate model control.
7. **The unbounded exact process is represented by a reflected numerical
   truncation.**  OU tail estimates help choose the box but do not rule out
   artificial late returns.  The box gate is mandatory.
8. **The discovery clocks are heuristic.**  Deterministic OU crossing times do
   not imply density modes because contact and midpoint are stochastic and the
   killing process biases surviving paths.  Only the killed PDE can decide.
9. **Simplex continuation can be ill-conditioned.**  A fold with tiny
   \(f_{t\theta}\), tiny reaction probability, or a barely visible new peak is
   mathematically real but not a PRR-quality physical result.  The
   nondegeneracy and observability floors prevent this promotion.
10. **G1 does not prove the arbitrary-mode theorem.**  Even a converged slab
    fold supplies one continuum modality boundary.  Quantitative transfer of
    the reduced GIG construction and a sufficient channel-dominance remainder
    remain G4 obligations.
11. **A slab realization may be judged too engineered.**  The exact quotient
    buys dimensional tractability by imposing transverse invariance.  G3/G5
    should therefore include an off-lattice process and, if computationally
    possible, one localized-patch control to demonstrate that the effect is not
    solely a slab symmetry artifact.
12. **A continuum fold requires third-order joint convergence.**  Converged
    density curves or peak labels alone are insufficient.  G1 must converge
    \((f_t,f_{tt})\) and the relevant derivatives through
    \(f_{ttt}\) and \(f_{t\theta}\).  A later cusp requires the separate
    fourth-order G2 gates.

## 11. Future implementation order

No implementation file is authorized by this note itself.  When work begins,
the smallest auditable sequence is:

1. implement normalized bump integrals, error-controlled contact fractions,
   and physical-budget tests;
2. implement one-dimensional SG operators and manufactured/equilibrium tests;
3. assemble the \(d=2\) quotient operator and verify mass balance and initial
   contact safety;
4. run only the 207,025-cell discovery calculation and freeze an interior fold
   line if one exists;
5. run the odd/even sequence and box audit;
6. write a machine-readable G1 manifest containing an explicit stage name,
   a separate continuum-verification boolean, and every gate, including failed
   attempts, before any PRR claim is added to the manuscript.

The G1a implementation exposes the reusable `foundation_diagnostics(model)`
and `foundation_gates(model, diagnostics)` interface.  Every discovery or fold
runner must consume that full interface rather than copying a subset of gates.
The payload must persist the complete physical parameter tuple, both control
endpoints, box, grid, sampled control, and time window.  Until the mesh/fold
sections pass, its stage remains `G1a_pre_fold_foundations` and
`continuum_verified` remains false.
