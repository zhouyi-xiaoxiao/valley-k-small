# Quantitative fixed-box C2 positive-time route candidate

Date: 2026-07-17

Status: **RESULT-BLIND THEORY CANDIDATE / CUT-LAYER LEMMA PROVED SUBJECT TO
STATED GEOMETRY / COMPLEX-SECTOR RESOLVENT PREMISE OPEN / C2 RATE FALSE / C3
FALSE**

## 0. Purpose and nonclaim boundary

This note chooses a quantitative route for the fixed-box continuum comparison.
It does not claim that the production family satisfies the route's hypotheses,
and it does not turn qualitative Mosco or strong-resolvent convergence into a
rate.  The prospective target is

\[
 E_{\mathrm{space},r}(h;\tau,T,L)
 \le C_r(\tau,T,L)h^{1/2},
 \qquad r=0,1,2,
 \tag{0.1}
\]

for `0<tau<=t<=T` on one fixed rectangular-periodic quotient box.  Equation
(0.1) is **conditional and presently false as a completion flag**.  It becomes
a theorem only after every premise in Sections 4--6 has a source-bound proof
with computable constants.

The scope is deliberately narrow:

- `h=max(h_M,h_R,h_Y)` and the three spacings may tend to zero
  asynchronously;
- all four cell/vertex and periodic base/shift alignment classes must pass with
  one worst-case constant;
- only a fixed finite control family, or a compact simplex family with uniform
  profile bounds, is covered;
- the ideal globally gauged reversible member is the theorem object;
  production centres and interval widths are not;
- no `t=0` derivative estimate is made;
- fixed-box spatial error is C2, whereas box exhaustion is C3;
- the existing exit-probability argument can contribute only an `r=0` box
  term; differentiated `r=1,2` box terms remain open; and
- `E_eval` is a separate absolute interval ledger and receives no automatic
  power of `h`.

No result, control-value, positive-budget, root, propagation, topology,
scratch, or release payload was used to select this route.

## 1. Fixed-box ideal setting

Use the physical quotient coordinates

\[
 \Omega_L=I_M\times I_R\times\mathbb T_W,
 \qquad x=(M,R,Y),
 \tag{1.1}
\]

with `dx=dM dR dY`, unit longitudinal midpoint-relative Jacobian, and the
Haar quotient normalization fixed in the production-bridge design.  Let the
reference density satisfy, on the fixed box,

\[
 0<\pi_-\le\pi(x)\le\pi_+<\infty,
 \qquad \pi\in W^{1,\infty}(\Omega_L).
 \tag{1.2}
\]

For one admissible control `c`, write

\[
 V_c(M,R,Y)=W^{-1}\chi_D(R,Y)
              \sum_{j=1}^4w_j^{(c)}\phi_j(M),
 \tag{1.3}
\]

where `D` is the geodesic contact disk, `a<W/2`, the weights are nonnegative
with exact sum one, and the four compact profiles are bounded and Lipschitz.
The continuum nonnegative self-adjoint operator `A_c` is associated with

\[
 \mathfrak a_c(u,v)=\mathfrak a_{\rm free}(u,v)
  +B\int_{\Omega_L}V_cu\bar v\,\pi\,dx.
 \tag{1.4}
\]

The mesh Hilbert space has the ideal single-global-gauge masses `pi_{h,x}`.
Its free form uses one common conductance per undirected edge, and its killing
diagonal is `B V_{h,c,x}`, where `V_h` is the exact physical-volume cell
average.  The reconstructed multiplier is

\[
 K_{h,c}^{pc}|_{C_x}=V_{h,c,x}/\rho_x,
 \qquad
 \rho_x=M_x^\pi/\pi_{h,x}.
 \tag{1.5}
\]

The exact isometry from the Round-5 construction is

\[
 G_h=P_hJ_h,
 \qquad U_h=J_hG_h^{-1/2},
 \qquad U_h^*U_h=I.
 \tag{1.6}
\]

All quantitative statements below concern this ideal object.  They are not
statements about independently rounded directed rates, independently rounded
axis gauges, or a kernel in which `V` has been incorrectly divided by `rho`.

## 2. Route decision

Three routes were compared.

### Route A: form defect to sectorial resolvents

Prove a quantitative free-form/flux defect, add sharp killing through an
`L2` multiplier estimate and a uniform discrete `L4` inequality, derive a
complex-sector reconstructed-resolvent bound, and integrate the resolvent
bound for `A^r exp(-tA)`.  This is the selected route because it never
differentiates the sharp contact indicator.

### Route B: direct generator residuals

Manufactured smooth solutions and direct residuals are valuable independent
cross-checks for the free stencil.  They are not the main proof route.  For
`r=2`, a naive direct argument easily differentiates the sharp indicator or
silently assumes spatial regularity across its interface that the killed
state need not possess.

### Route C: mollify the contact set

Mollification may prove the geometric layer estimate by a triangle argument.
It cannot replace the target model.  Every such proof must retain a separate
sharp-versus-smooth term and precommit the smoothing rule.  Balancing the
smooth discretization and interface terms normally returns, rather than
improves, the conservative `h^(1/2)` target.

Thus Route A is primary, Route B is an audit, and Route C is at most an
auxiliary lemma.

## 3. Sharp cut-layer lemma

This section gives the one quantitative component that can be proved without
a semigroup theorem.

Assume a shape-regular Cartesian family.  Let `d_h` be the largest transverse
cell diameter, so `d_h<=C_shape h`.  Let `U_h^cut` be the union of transverse
cells meeting the contact boundary.  Then

\[
 U_h^{\rm cut}\subset
 \{(R,Y):\operatorname{dist}((R,Y),\partial D)\le d_h\}.
 \tag{3.1}
\]

For sufficiently small
`d_h<min(a,W/2-a)`, the torus condition `a<W/2` keeps the inner radius
positive and the outer radius below the transverse injectivity radius.  The
two-dimensional tubular set is therefore a nonoverlapping annulus, so

\[
 |U_h^{\rm cut}|
 \le 4\pi a d_h
 \le C_Dh.
 \tag{3.2}
\]

The same bound holds chart-independently if the disk crosses the chosen
coordinate seam.  Multiplying by `|I_M|` and `pi_+` gives

\[
 \mu_\pi(I_M\times U_h^{\rm cut})\le C_{\rm layer}h.
 \tag{3.3}
\]

Let `chi_h^pc` reconstruct the exact physical-volume cell averages of
`chi_D`.  Outside the cut layer it equals `chi_D` almost everywhere, and in
the cut layer both functions lie in `[0,1]`.  Hence

\[
 \|\chi_h^{pc}-\chi_D\|_{L^2(\pi)}
 \le C_{\rm layer}^{1/2}h^{1/2}.
 \tag{3.4}
\]

Let `phi_{j,h}^pc` reconstruct the exact one-dimensional cell averages of the
profiles.  Lipschitz continuity gives

\[
 \|\phi_{j,h}^{pc}-\phi_j\|_{L^\infty}
 \le \operatorname{Lip}(\phi_j)h_M.
 \tag{3.5}
\]

Because the cells are Cartesian and (1.3) factorizes, the product of the
contact and profile averages is exactly the physical-volume average of `V_c`.
Using the simplex sum and decomposing

\[
 \chi_h\Phi_h-\chi_D\Phi
 = (\chi_h-\chi_D)\Phi_h+\chi_D(\Phi_h-\Phi),
\]

Eqs. (3.4)--(3.5) yield, uniformly over the control simplex,

\[
 \|V_{h,c}^{pc}-V_c\|_{L^2(\pi)}
 \le C_{V,\rm cut}h^{1/2}+C_{V,\rm sm}h.
 \tag{3.6}
\]

Suppose the accepted map lemma supplies

\[
 \|\rho_h^{pc}-1\|_{L^\infty}\le C_\rho h,
 \qquad \inf\rho_h^{pc}\ge\tfrac12.
 \tag{3.7}
\]

Then `|rho^{-1}-1|<=2C_rho h`, and boundedness of `V_h` gives

\[
 \boxed{
 \|K_{h,c}^{pc}-V_c\|_{L^2(\pi)}
 \le C_{K,\rm cut}h^{1/2}+C_{K,\rm map}h.}
 \tag{3.8}
\]

This proof takes no derivative of `chi_D`.  It also shows why exact
physical-volume averages matter: point sampling would introduce a different
cut-cell defect that cannot be relabelled as evaluation roundoff.

Equation (3.8) is a mathematical candidate lemma under (1.2), exact
factorization, shape regularity, and (3.7).  Its constants still need to be
instantiated from accepted geometry and map sources before it can enter a C2
receipt.

## 4. Quantitative free and form premises still required

Use the mesh energy norm

\[
 \|v_h\|_{1,h}^2=\|v_h\|_h^2+
                     \mathfrak a_{h,\rm free}(v_h,v_h).
 \tag{4.1}
\]

The following are open obligations, not conclusions of qualitative Mosco
convergence.

### QF1. Uniform coercivity and discrete Sobolev control

For every alignment and asynchronous refinement,

\[
 \|J_hv_h\|_{L^4(\pi)}\le C_S\|v_h\|_{1,h}.
 \tag{4.2}
\]

In quotient dimension three this is the discrete analogue of `H1` embedding
into `L4`.  Its constant must be computed from the fixed box, weight bounds,
and shape regularity, not fitted from observed convergence.

### QF2. Reconstruction and free SG defect

There must be a conforming reconstruction `I_h` and a flux reconstruction such
that, uniformly over all alignments,

\[
 \|I_hv_h-J_hv_h\|_{L^2(\pi)}
 \le C_Jh\|v_h\|_{1,h},
 \tag{4.3}
\]

and the free Scharfetter--Gummel consistency/Strang defect is at most

\[
 C_{\rm free}h\|u_h\|_{1,h}\|v_h\|_{1,h}.
 \tag{4.4}
\]

The worst order is intentionally first order.  Vertex-dual endpoint ratios
are only `O(h)`, and a generic cell-centred boundary half-cell defect must not
be promoted to second order.  The periodic map defect is exactly zero; a
finite tensor product does not change the worst exponent.

### QF3. Quantitative map bounds

The source-bound one-axis estimates must prove

```text
midpoint cell-centred rho defect       = O(h_M^2)
vertex-dual endpoint rho defect        = O(h_axis)
periodic rho defect                    = 0 exactly
finite tensor global G_h-I defect      = O(max_a h_a)
```

with positive lower bounds and constants uniform over base/shift and alignment
classes.  A finite table is not an asymptotic family.

### QF4. Killing-form defect

Equations (3.8) and (4.2) give the principal estimate, with the fixed budget
`B` absorbed into the displayed constants,

\[
 \left|\int(K_{h,c}^{pc}-V_c)
       J_hu_h\overline{J_hv_h}\,\pi dx\right|
 \le (C_{K,\rm cut}h^{1/2}+C_{K,\rm map}h)
       C_S^2\|u_h\|_{1,h}\|v_h\|_{1,h}.
 \tag{4.5}
\]

Replacing `J_h` by `I_h` in the bounded remaining multiplier terms costs
`O(h)` by (4.3).  Thus the sharp contact term, not the free or map term, is the
conservative exponent-limiting contribution:

\[
 |\mathfrak a_{h,c}(u_h,v_h)
   -\mathfrak a_c(I_hu_h,I_hv_h)|
 \le C_{\rm form}h^{1/2}
       \|u_h\|_{1,h}\|v_h\|_{1,h}.
 \tag{4.6}
\]

Equation (4.6) is conditional on QF1--QF3 and on a source-bound version of the
cut-layer lemma.  It is not yet an accepted form estimate.

### QF5. Initial and observable approximation

For the first implementation, freeze enough regularity to prove explicit
rates, for example `u_0 in H1` for the production initialization.  Merely
knowing `u_0 in L2` gives qualitative projection convergence but no presently
proved algebraic rate for the actual initialization path.  A later proof may
weaken this if the exact `U_h^*` initialization is source-bound.

For a smooth observable, require its declared projection error.  For the sharp
event observable, Eq. (3.4) supplies the natural `O(h^(1/2))` `L2` term.  These
input/output errors must be added once, not hidden in the semigroup constant.

## 5. Complex-sector reconstructed-resolvent obligation

The fixed rectangular-periodic weighted Neumann problem must supply a
control-uniform quantitative regularity statement.  A sufficient package is:

1. weighted `H2` regularity for the continuum resolvent with bounded sharp
   zero-order potential;
2. computable coercivity and continuity constants for the complex-shifted
   forms;
3. the flux/reconstruction and projection defects in Section 4; and
4. uniformity over the finite control/alignment set and over asynchronous
   refinement.

Fix a harmless shift `sigma>0` and set

\[
 A_{c,\sigma}=A_c+\sigma I,
 \qquad A_{h,c,\sigma}=A_{h,c}+\sigma I.
 \tag{5.1}
\]

For a contour sector `Gamma_{theta,sigma}` staying a fixed angle from the
positive spectrum, the required quantitative result is

\[
 \left\|
 U_h(z-A_{h,c,\sigma})^{-1}U_h^*
 -(z-A_{c,\sigma})^{-1}
 \right\|
 \le C_{\rm sec}(z,L)h^{1/2},
 \qquad z\in\Gamma_{\theta,\sigma}.
 \tag{5.2}
\]

The range-complement term is part of (5.2): because `U_hU_h^*` is not the
identity, a proof must estimate the projection of the continuum resolvent into
the moving piecewise-constant range.  Compactness alone gives no computable
rate.

A Strang argument based on (4.6) is the preferred proof mechanism for (5.2).
Real-shift norm-resolvent control is a useful intermediate result, but it is
not by itself the declared quantitative bridge for `r=1,2`.  The complex
sector estimate and the growth of `C_sec(z,L)` must be explicit and audited.

This is the principal unresolved analytical step.

## 6. Positive-time contour transfer

Once (5.2) is proved, positive-time generator powers require no spatial
derivative of the contact indicator.  Orient a Dunford contour around the
positive spectrum and use

\[
 A_c^re^{-tA_c}
 =\frac{e^{\sigma t}}{2\pi i}
   \int_{\Gamma_{\theta,\sigma}}
   (z-\sigma)^re^{-tz}
   (z-A_{c,\sigma})^{-1}\,dz,
 \qquad r=0,1,2.
 \tag{6.1}
\]

The identical formula holds on the mesh.  Combining (5.2) and (6.1) yields

\[
 \sup_{t\in[\tau,T]}
 \|U_hA_{h,c}^re^{-tA_{h,c}}U_h^*
      -A_c^re^{-tA_c}\|
 \le \mathcal C_r(\tau,T,L)h^{1/2},
 \tag{6.2}
\]

where the auditable constant is the explicit contour integral

\[
 \mathcal C_r(\tau,T,L)
 =\frac1{2\pi}\sup_{t\in[\tau,T]}
   \int_{\Gamma_{\theta,\sigma}}
   e^{\sigma t}|z-\sigma|^re^{-t\operatorname{Re}z}
   C_{\rm sec}(z,L)|dz|.
 \tag{6.3}
\]

The contour and sector growth must make (6.3) finite.  The present note does
not guess a power of `tau^{-1}`; it requires the constant to be evaluated from
the proved `C_sec` bound.

The original maps satisfy `J_h=U_hG_h^(1/2)` and
`P_h=G_h^(1/2)U_h^*`.  On `[tau,T]`, spectral calculus bounds
`||A_h^r exp(-tA_h)||`, so the `G_h-I=O(h)` map correction is lower order than
`h^(1/2)`.  This translation is valid only after the quantitative QF3 bound is
accepted.

No statement extends (6.2) to `t=0`.

## 7. Error ledger and observable target

For declared initial vectors and observables, the fixed-box ideal error has the
structure

\[
 E_{\rm space,r}
 \le E_{\rm semigroup,r}^{(1/2)}
     +E_{\rm map,r}^{(1)}
     +E_{\rm init,r}
     +E_{\rm obs,r}.
 \tag{7.1}
\]

For the sharp contact observable, `E_obs=O(h^(1/2))`; for the first declared
initial path, the intended source-bound target is `E_init=O(h)`.  The resulting
worst exponent is one half.

Production evaluation has a different ledger:

```text
E_space:
  exact ideal globally gauged mesh member versus fixed-box continuum

E_eval:
  outward mass/rate/gauge/killing/initial enclosures,
  production centre versus the contained ideal member,
  and downstream interval propagation/roundoff

E_box:
  fixed box versus unbounded or larger-box continuum
```

These ledgers may be summed only after the production enclosure proves that it
contains the same ideal member used in `E_space`.  Primitive interval widths
are not the final observable `E_eval`, and no width may be counted in both
`E_eval` and `E_space`.

For C3, the honest present boundary is

```text
box r=0: existing exit-probability route may be used after source binding
box r=1: OPEN
box r=2: OPEN
```

An exit probability is not a differentiated box bound.

## 8. Reproducible validation programme

Numerics can attack the proof obligations but cannot replace them.

1. **Geometry fixture.**  Predeclare genuine refinement families for every
   transverse shift/alignment.  Recompute exact/outward contact fractions,
   measure the cut-layer weighted volume and the exact `L2` multiplier defect,
   and verify the source-bound `C sqrt(h)` inequality.  A fitted slope alone is
   not acceptance.
2. **Free manufactured solutions.**  Use smooth functions to verify flux,
   endpoint-half-volume, periodic-wrap, tensor-order, and asynchronous-grid
   residual bounds.  This tests QF2 but says nothing about differentiating the
   sharp killing.
3. **Independent small-grid resolvents.**  Compare the ideal FV resolvent with
   an independently assembled conforming reference on meshes small enough for
   dense diagnostics.  Freeze sector points and tolerances before seeing the
   errors.
4. **Virtual large tensors.**  Keep axis factors and cut geometry factorized;
   stream norms and extrema.  Never allocate the largest three-dimensional
   tensor merely to demonstrate a theorem constant.
5. **Two implementations.**  Use one route for production intervals and a
   separately sourced route for semantic containment.  Same-backend replay is
   useful but must not be labelled independent-backend evidence.
6. **Adversarial mutations.**  Reject at least: point-sampled contact,
   synchronized-only refinement, missing endpoint half volumes, normalized
   periodic raw masses, independent directed-rate endpoints, a product of
   rounded axis gauges, `rho=1`, `K` substituted for the kernel killing,
   a posteriori constant selection, and any `E_eval/E_space` double count.

Observed convergence faster than `h^(1/2)` does not authorize a stronger
theorem.  It may indicate that the selected family has unusually small cut
layers or cancellation.

## 9. Promotion gates

The following flags remain false:

```text
cut_layer_constant_source_bound                  = false
uniform_discrete_L4_inequality_proved            = false
free_quantitative_Strang_defect_proved           = false
weighted_complex_sector_H2_regularity_proved     = false
complex_sector_reconstructed_resolvent_rate      = false
positive_time_r0_r1_r2_C2_rate                   = false
production_ideal_member_bound_to_C2               = false
complete_C1                                      = false
complete_C2                                      = false
complete_C3                                      = false
release_submission_science_execution             = false
```

The next rigorous milestone is not a claimed rate.  It is a small,
source-bound geometry fixture for (3.2)--(3.8), followed by a separate proof of
QF1--QF2 and then the complex-sector estimate (5.2).  Only that sequence can
turn the conservative `h^(1/2)` target into C2 evidence.
