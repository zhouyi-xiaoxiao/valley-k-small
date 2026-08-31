# Fixed-box free-form extensions and positive-time functional bridge candidate

Date: 2026-07-17

Status: **RESULT-BLIND PROOF CANDIDATE / ABSTRACT FUNCTIONAL BRIDGE CLOSED SUBJECT TO AUDIT / FULL GEOMETRIC C1 NOT YET ACCEPTED / COMPLETE C1 FALSE**

## 0. Purpose and nonclaim boundary

This note is a successor layer to the hash-frozen one-dimensional candidate
`continuum_c1_fixed_1d_free_ou_mosco_candidate.md` (SHA-256
`11a3015cbaa38cd58d763052adf3858ad055f121cc83669aaeeb462252d35e79`).
It does not alter those audited bytes.  It does four things:

1. closes two expository gaps left by the fixed-1D proof review;
2. states the missing refinement and rate contract for the relative OU,
   periodic, and vertex-dual axes;
3. gives the finite-tensor and bounded-killing route needed on a fixed box;
4. proves a self-contained varying-space functional-calculus bridge for
   `lambda^r exp(-t lambda)`, `r=0,1,2`, uniformly on positive times.

No control/result payload, positive-budget topology, production centre,
root margin, continuum rate, or box-exhaustion conclusion is used here.  The
current twelve-row configuration source contains finite meshes, not an
`h -> 0` refinement family.  The vertex-dual endpoint rate formula below is
implemented by the current local axis builder, but is not yet frozen as an
independently accepted mathematical C0 source.  Consequently this note is a
candidate contract, not a complete-C1 promotion.

All spaces and forms are real.  Optional complexification conjugates the
first factor in inner products and forms.

## 1. Two clarifications to the fixed-1D lemma

The preceding fixed-1D note proves Mosco liminf for every weakly convergent
sequence and constructs a diagonal recovery sequence for every `u in H1(I)`.
For completeness, if `u` is outside `H1(I)`, then the extended continuum form
has value `+infinity`.  Choose `v_h=A_hu`.  Since

\[
 J_hA_hu=E_hu\longrightarrow u
 \quad\hbox{strongly in }L^2(I,\pi dx),
\]

the recovery requirement is automatic:

\[
 \limsup_h \mathfrak a_h(v_h,v_h)\le +\infty.
\]

The variational resolvent step can also be made explicit.  For `alpha>0`,
let `u_h` minimize

\[
 F_h(v)=\mathfrak a_h(v,v)+\alpha\|v\|_h^2
       -2\langle P_hf,v\rangle_h.
\]

Exact adjointness gives
`<P_hf,v>_h=<f,J_hv>`.  Liminf and recovery identify every weak cluster
point with the unique continuum minimizer `u`.  If `z_h` is a recovery
sequence for `u`, the recovery limsup, the liminf inequality, and norm
consistency first give

\[
 b_h(z_h,z_h)\longrightarrow b(u,u).
\]

The Euler identities then give

\[
 b_h(u_h,u_h)=\langle f,J_hu_h\rangle\to b(u,u),
 \qquad
 b_h(u_h,z_h)=\langle f,J_hz_h\rangle\to b(u,u),
\]

where `b_h=a_h+alpha<.,.>_h`.  Hence

\[
 b_h(u_h-z_h,u_h-z_h)\longrightarrow0.
\]

Uniform boundedness of `J_h` then yields `J_hu_h -> u` strongly.  Uniqueness
of the weak cluster point promotes the subsequence argument to the full mesh
family.  These clarifications change no formula or scoped conclusion in the
predecessor note.

## 2. Prospective fixed-box refinement and rate contract

Fix

\[
 \Omega_L=I_z\times I_r\times\mathbb T_W,
 \qquad
 \pi(z,r,y)=\pi_z(z)\pi_r(r)W^{-1},
\]

where

\[
 \pi_a(x)=C_a e^{-\Phi_a(x)},\qquad
 \Phi_a(x)=\frac{\gamma_a(x-\mu_a)^2}{2d_a},
 \quad a\in\{z,r\}.
\]

For the encounter quotient,

\[
 (d_z,\gamma_z,\mu_z)=(D/2,\gamma,\bar z),
 \qquad
 (d_r,\gamma_r,\mu_r)=(2D,\gamma,0),
 \qquad d_y=2D.
\]

The fixed-box parameter substitution assumes

\[
 \bar z\in\operatorname{int}I_z,
 \qquad 0\in\operatorname{int}I_r,
 \tag{2.0}
\]

as in the predecessor theorem.  A box violating (2.0) would require a
separate statement rather than being silently covered by parameter reuse.

Every promoted fixed box must carry one of the following explicit refinement
families, with maximum axis spacing tending to zero.

### 2.1 Cell-centred reflecting OU axis

For `N>=3` cells on `[ell,r]`, let `h=(r-ell)/N`,
`x_i=ell+(i+1/2)h`, and `nu_i=h`.  The dual cells are the ordinary cells.
Put

\[
 \widetilde m_i=\nu_i e^{-\Phi(x_i)},\qquad
 g_h=\frac{\int_\ell^r\pi(x)dx}{\sum_i\widetilde m_i},
 \qquad m_i=g_h\widetilde m_i,
\]

and, for every interior edge,

\[
 q_{i,i+1}=\frac d{\nu_i h}B(\Phi_{i+1}-\Phi_i),
 \qquad
 q_{i+1,i}=\frac d{\nu_{i+1}h}B(\Phi_i-\Phi_{i+1}).
 \tag{2.1}
\]

This reduces to the fixed-1D formula `d h^{-2}B`.

### 2.2 Vertex-centred reflecting dual OU axis

For `N>=2` intervals and `N+1` vertices, let `x_i=ell+ih`,
`h=(r-ell)/N`.  The
dual-volume lengths are

\[
 \nu_0=\nu_N=h/2,\qquad \nu_i=h\quad(1\le i\le N-1).
 \tag{2.2}
\]

Use the same mass and rate formulas as (2.1).  In particular the endpoint
outgoing rate contains `nu_0=h/2` and is twice the equal-volume rate with the
same Bernoulli factor.  Exterior rates are zero.  This volume factor is
essential: deleting it breaks finite-volume flux balance.

The Bernoulli identity gives the exact common conductance

\[
 c_{i+1/2}=m_iq_{i,i+1}=m_{i+1}q_{i+1,i}
 =\frac{g_hd}{h}e^{-\Phi(x_i)}B(\Phi_{i+1}-\Phi_i).
 \tag{2.3}
\]

### 2.3 Periodic free-diffusion axis

For `N>=3` cells on `T_W`, put `h=W/N` and choose either
`sigma_h=0` or `sigma_h=h/2`.  With indices modulo `N`, set

\[
 y_i=(i+1/2)h+\sigma_h\pmod W,
 \qquad
 C_i=[ih+\sigma_h,(i+1)h+\sigma_h)\pmod W.
\]

A cell crossing the selected seam is represented by its two wrapped
segments.  Put

\[
 m_i=h/W,\qquad
 q_{i,i+1}=q_{i,i-1}=d_y/h^2,
 \qquad q_{ii}=-2d_y/h^2.
 \tag{2.4}
\]

with the last and first indices adjacent.  The two shifts are the same
mathematical mesh up to torus translation, but both must remain represented
in the finite contract because their contact cut cells differ.

### 2.4 Tensor product and global gauge

Let `m^z,m^r,m^y` be the axis masses above.  Define

\[
 m_{ijk}=m_i^zm_j^rm_k^y.
 \tag{2.5}
\]

The additional ideal product assumption is, explicitly,

\[
 \widetilde m_{ijk}
 =\nu_i^z\nu_j^r h
  e^{-\Phi_z(x_i)-\Phi_r(x_j)}.
 \tag{2.5a}
\]

Applying one global box-mass gauge to (2.5a), Fubini and factorization of the
finite sums give

\[
 g_{h,L}=g_h^z g_h^r/W,
 \qquad
 \sum_{ijk}m_{ijk}=M_zM_r=M_L.
 \tag{2.6}
\]

The free tensor generator is the Kronecker sum of the three axis generators.
An edge parallel to one axis has that axis conductance multiplied by the two
other axis masses.  This is the ideal analytic object only; it is not a
statement about independently rounded production centres.

The twelve current finite configurations do not by themselves instantiate
these refinement sequences.  Before promotion, a machine-readable C1 source
must bind each finite alignment to one of (2.1)--(2.4), define admissible
`N -> infinity` sequences, and bind the ideal rates to the evaluator member.

## 3. Identification maps on every alignment

Let `C_i` denote the actual cell, dual cell, or wrapped periodic cell and put

\[
 M_i=\int_{C_i}\pi(x)dx,
 \qquad
 \rho_i=M_i/m_i.
\]

Use the same maps as in the C0-v2 source:

\[
 J_hv=\sum_iv_i\mathbf1_{C_i},\qquad
 (P_hu)_i=m_i^{-1}\int_{C_i}u\pi,
 \qquad
 (A_hu)_i=M_i^{-1}\int_{C_i}u\pi.
 \tag{3.1}
\]

Then exactly

\[
 P_h=J_h^*,\quad P_h=\operatorname{diag}(\rho)A_h,
 \quad A_hJ_h=I,\quad J_hA_h=E_h,
 \tag{3.2}
\]

\[
 P_hJ_h=\operatorname{diag}(\rho),
 \qquad J_hP_h=\rho_h^{pc}E_h.
 \tag{3.3}
\]

For a cell-centred OU axis, the predecessor proves
`max_i|rho_i-1|=O(h^2)`.  For a vertex-dual OU axis, composite trapezoidal
consistency gives `g_h/C=1+O(h^2)`.  Interior symmetric dual cells again have
`rho_i=1+O(h^2)`, whereas the two one-sided endpoint half cells generally
have the signed expansions

\[
 \rho_0=1-\frac{\Phi'(\ell)}4h+O(h^2),
 \qquad
 \rho_N=1+\frac{\Phi'(r)}4h+O(h^2).
 \tag{3.4}
\]

Under (2.0), both displayed first-order corrections are positive.  In
particular, their uniform order is only `O(h)`.

Thus the correct uniform vertex-dual claim is `max_i|rho_i-1|=O(h)`, not
second order.  On the periodic axis, `rho_i=1` exactly.  Products of the
axis ratios give the tensor ratio, so for all four alignment classes

\[
 \delta_h:=\|P_hJ_h-I\|=\max_i|\rho_i-1|\longrightarrow0,
 \tag{3.5}
\]

while `J_hP_hu -> u` strongly for each fixed `u`.  No operator-norm
convergence of `J_hP_h` is claimed.

## 4. Vertex-dual and periodic one-axis form lemmas

### 4.1 Vertex-dual reflecting OU

Let `I_hv` be the continuous piecewise-linear interpolant through all
vertices, including the endpoints.  For a quadratic OU potential, (2.3) and
the same midpoint calculation as in the fixed-1D note give

\[
 \max_i\left|
 \frac{c_{i+1/2}}
 {d h^{-2}\int_{x_i}^{x_{i+1}}\pi(x)dx}-1
 \right|\le K_{edge}h^2.
 \tag{4.1}
\]

Therefore

\[
 (1-Kh^2)\mathfrak a(I_hv,I_hv)
 \le \mathfrak a_h(v,v)
 \le(1+Kh^2)\mathfrak a(I_hv,I_hv).
 \tag{4.2}
\]

On each full edge interval, `J_hv` equals the left nodal value on its first
half and the right nodal value on its second half.  The two exact linear-ramp
integrals total `h|v_{i+1}-v_i|^2/12`.  Hence, for sufficiently small `h`,

\[
 \|I_hv-J_hv\|_{L^2(\pi)}^2
 \le C h^2\mathfrak a_h(v,v).
 \tag{4.3}
\]

The arbitrary-sequence liminf proof from the predecessor now applies word
for word.  Smooth nodal samples give recovery because the vertex interpolant
covers the whole interval; unlike the cell-centred case, there are no omitted
boundary half intervals.  An `H1` density/diagonal argument completes the
recovery step.  Equations (3.4), (4.1), and (4.3), rather than a blanket
second-order statement, are the required vertex-dual estimates.

### 4.2 Periodic free diffusion

Let `I_hv` be the periodic piecewise-linear interpolant between consecutive
representatives, including the wrapping edge.  Since `pi_y=1/W`, (2.4) gives
the exact identity

\[
 \mathfrak a_h(v,v)
 =\frac{d_y}{Wh}\sum_i|v_{i+1}-v_i|^2
 =\int_{\mathbb T_W}d_y|(I_hv)'|^2\frac{dy}{W}.
 \tag{4.4}
\]

The same ramp calculation gives (4.3), now with a periodic edge sum.  Periodic
smooth samples and density in `H1(T_W)` give recovery.  All constants are
independent of whether `sigma_h=0` or `h/2`, because the two families differ
only by translation on the torus.

### 4.3 Relative OU axis

The fixed-1D proof was written for arbitrary `d>0`, `gamma>0`, an interior
mean, and a fixed interval.  The relative-parallel axis is therefore the same
lemma with `(d,mu)=(2D,0)`.  This is a parameter substitution, not a new
stencil argument.  The midpoint axis uses `(d,mu)=(D/2,zbar)`.

Subject to an independent audit of this section and an accepted refinement
source, the three one-axis free forms satisfy generalized Mosco convergence
for both nonperiodic alignments and both periodic shifts.

## 5. Finite tensorization candidate

Let `L_{a,h}` and `L_a` be the nonnegative free axis operators.  The one-axis
Mosco conclusions give reconstructed strong resolvent convergence and, by
the functional theorem in Section 7 below,

\[
 J_{a,h}e^{-tL_{a,h}}P_{a,h}u
 \longrightarrow e^{-tL_a}u,
 \qquad t>0.
 \tag{5.1}
\]

For the tensor maps

\[
 J_h=J_{z,h}\otimes J_{r,h}\otimes J_{y,h},
 \qquad
 P_h=P_{z,h}\otimes P_{r,h}\otimes P_{y,h}=J_h^*,
\]

the free Kronecker-sum semigroup factorizes exactly:

\[
 J_he^{-tL_h^0}P_h
 =\bigotimes_{a\in\{z,r,y\}}
   \left(J_{a,h}e^{-tL_{a,h}}P_{a,h}\right).
 \tag{5.2}
\]

Equation (5.1) implies strong convergence of (5.2) first on algebraic simple
tensors and then on the full product Hilbert space by uniform boundedness and
density.  The Laplace formula

\[
 (L_h^0+\alpha)^{-1}
 =\int_0^\infty e^{-\alpha t}e^{-tL_h^0}\,dt
 \tag{5.3}
\]

and dominated convergence give reconstructed strong resolvent convergence of
the free tensor operator.

The domination used here is explicit: for a mesh-independent finite `C`,

\[
 e^{-\alpha t}\|J_he^{-tL_h^0}P_hu\|
 \le C e^{-\alpha t}\|u\|,
\]

and the right-hand side is integrable on `[0,infinity)`.

To call this conclusion generalized Mosco convergence, rather than the
equivalent strong-resolvent route allowed by the research program, the final
proof must either include the generalized Mosco--semigroup equivalence under
(3.2)--(3.5) or pin an exact theorem whose hypotheses have been checked.  No
such citation is silently assumed here.  The direct strong-resolvent result
in (5.3) is the current candidate output.

## 6. Bounded sharp-contact killing as a form perturbation

Fix one bounded nonnegative target field `V_c in L-infinity(Omega_L)`.  Let

\[
 V_{h,c,i}=|C_i|^{-1}\int_{C_i}V_c(x)dx
 \tag{6.1}
\]

be the exact physical-volume cell average, including dual half volumes and
wrapped cells.  On any shape-regular Cartesian refinement with maximum
diameter tending to zero, density of continuous functions gives

\[
 J_hV_{h,c}\longrightarrow V_c
 \quad\hbox{in }L^2(\Omega_L,\pi dx),
 \qquad
 0\le J_hV_{h,c}\le\|V_c\|_\infty.
 \tag{6.2}
\]

This qualitative statement applies to the sharp contact indicator: no
derivative of its circular boundary is taken.  A finite control/alignment set
is handled by taking a finite maximum.  Equation (6.2) supplies no cut-cell
rate; the `O(h^{1/2})` target remains C2 work.

The discrete killing form has an exact reconstructed representation.  Put

\[
 K_h^{pc}|_{C_i}=V_{h,c,i}/\rho_i.
\]

Then

\[
 \sum_i m_iV_{h,c,i}|v_i|^2
 =\int_{\Omega_L}K_h^{pc}|J_hv|^2\pi dx.
 \tag{6.3}
\]

Equations (3.5) and (6.2) give `K_h^pc -> V_c` in measure and in weighted
`L2`, with a common `L-infinity` bound.  If `J_hv_h` converges weakly to `v`,
then

\[
 \sqrt{K_h^{pc}}J_hv_h\rightharpoonup\sqrt{V_c}v,
\]

because multiplication by `sqrt(K_h^pc)` converges strongly on every fixed
`L2` test function.  Weak lower semicontinuity proves the killing liminf.  If
`J_hv_h -> v` strongly, the common bound and convergence in measure give

\[
 \int K_h^{pc}|J_hv_h|^2\pi
 \longrightarrow\int V_c|v|^2\pi.
 \tag{6.4}
\]

Thus any accepted free-form Mosco recovery sequence is also a recovery
sequence after adding the killing form, and the liminf terms add.  This closes
the qualitative bounded-killing perturbation once the free tensor Mosco
version of Section 5 has been accepted.  It does not prove a quantitative
rate or a production interval enclosure.

## 7. Abstract varying-space functional-calculus theorem

Let `L_h>=0` and `L>=0` be self-adjoint on `H_h` and `H`.  Assume

\[
 P_h=J_h^*,\qquad
 \sup_h(\|J_h\|+\|P_h\|)<\infty,
 \qquad
 \delta_h=\|P_hJ_h-I\|\to0,
 \tag{7.1}
\]

and, for one `alpha>0`,

\[
 J_h(L_h+\alpha)^{-1}P_hu
 \longrightarrow(L+\alpha)^{-1}u
 \quad(u\in H).
 \tag{7.2}
\]

Then, for every `f in C_0([0,infinity))`,

\[
 J_hf(L_h)P_hu\longrightarrow f(L)u
 \quad(u\in H).
 \tag{7.3}
\]

### Proof

Write `R_h=(L_h+alpha)^{-1}`, `R=(L+alpha)^{-1}`, and
`Rhat_h=J_hR_hP_h`.  Although compression is not exactly multiplicative,

\[
 \widehat R_h^k
 =J_hR_h(P_hJ_hR_h)^{k-1}P_h.
\]

A telescoping expansion and `||R_h||<=alpha^{-1}` give, for every fixed
`k>=2`,

\[
 \|\widehat R_h^k-J_hR_h^kP_h\|
 \le \|J_h\|\|P_h\|(k-1)\alpha^{-k}
      (1+\delta_h)^{k-2}\delta_h\longrightarrow0.
 \tag{7.4}
\]

Uniformly bounded strong convergence `Rhat_h -> R` implies convergence of
all fixed powers.  Hence (7.3) holds for every zero-constant polynomial in
the resolvent variable.  Under the change of variables
`y=(lambda+alpha)^{-1}`, a function in `C_0([0,infinity))` becomes a
continuous function on `[0,alpha^{-1}]` that vanishes at `y=0`.  Such
functions are uniformly approximated by polynomials with zero constant term.
The spectral theorem and the uniform map bound in (7.1) complete the proof.

The zero-constant approximation is why no false claim
`||J_hP_h-I|| -> 0` is needed.

## 8. Uniform positive-time derivatives

For `r=0,1,2`, set

\[
 f_{r,t}(\lambda)=\lambda^r e^{-t\lambda},
 \qquad t\in[\tau,T],\quad0<\tau\le T<\infty.
\]

Each function lies in `C_0([0,infinity))`, and

\[
 \|f_{r,t}-f_{r,s}\|_\infty
 \le L_r(\tau)|t-s|,
 \qquad
 L_r(\tau)=\left(\frac{r+1}{e\tau}\right)^{r+1}.
 \tag{8.1}
\]

For a fixed `u_0 in H`, (7.3) gives convergence at every point of a finite
time net.  Equation (8.1), the spectral theorem, and the uniform map bounds
control the gaps between net points on both the discrete and continuum sides.
Therefore

\[
 \sup_{t\in[\tau,T]}
 \|J_hf_{r,t}(L_h)P_hu_0-f_{r,t}(L)u_0\|_H
 \longrightarrow0.
 \tag{8.2}
\]

Theorem 7 alone makes no `t=0` claim, because `f_{0,0}=1` is not in `C_0`.
At the single time `t=0`, the additional identification hypothesis
`J_hP_hu_0 -> u_0` gives the `r=0` convergence.  This fact alone does not
extend (8.2) uniformly to `[0,T]`; uniformity down to zero requires a uniform
spectral-tail or compatible graph-norm hypothesis.  For `r=1,2`, domain
regularity and compatible discrete--continuum graph convergence are also
required even to formulate the corresponding initial generator actions.  The
positive-time result above is qualitative and supplies no computable C2 error.

## 9. Moving observable pairings

For any `v_h in H_h`, exact adjointness gives the identity

\[
 \begin{split}
 &\langle V_h,v_h\rangle_h-\langle V,J_hv_h\rangle_H\\
 &\quad=\langle V_h,(I-P_hJ_h)v_h\rangle_h
       +\langle J_hV_h-V,J_hv_h\rangle_H.
 \end{split}
 \tag{9.1}
\]

Thus

\[
 \left|\langle V_h,v_h\rangle_h
       -\langle V,J_hv_h\rangle_H\right|
 \le\left[\delta_h\|V_h\|_h
       +\|J_h\|\|J_hV_h-V\|_H\right]\|v_h\|_h.
 \tag{9.2}
\]

Let `v_h(t)=f_{r,t}(L_h)P_hu_0`.  The spectral bound

\[
 \sup_t\|v_h(t)\|_h
 \le K_r(\tau)\|P_h\|\|u_0\|,
 \qquad
 K_0=1,\quad K_r=(r/(e\tau))^r\ (r\ge1),
 \tag{9.3}
\]

is uniform in `h`.  The hypothesis `J_hV_h -> V` already implies the needed
discrete norm bound.  Indeed, for sufficiently small `h`,

\[
 \|J_hV_h\|_H^2
 =\langle V_h,P_hJ_hV_h\rangle_h
 \ge(1-\delta_h)\|V_h\|_h^2,
 \tag{9.4}
\]

so `sup_h||V_h||_h<infinity`.  Combining (9.2), (9.3), and (8.2) gives

\[
 \sup_{t\in[\tau,T]}\left|
 \langle V_h,f_{r,t}(L_h)P_hu_0\rangle_h
 -\langle V,f_{r,t}(L)u_0\rangle_H
 \right|\longrightarrow0.
 \tag{9.5}
\]

More explicitly, with `v(t)=f_{r,t}(L)u_0`, the left side of (9.5) is at
most

\[
 \begin{split}
 &\left[\delta_h\|V_h\|_h
  +\|J_h\|\|J_hV_h-V\|_H\right]
  K_r(\tau)\|P_h\|\|u_0\|_H\\
 &\qquad+\|V\|_H
  \sup_{t\in[\tau,T]}\|J_hv_h(t)-v(t)\|_H,
 \end{split}
 \tag{9.6}
\]

and every term tends to zero.

After the conventional factor `(-1)^r`, this is the qualitative transfer of
the observable and its first two time derivatives.  A finite declared control
set is handled by a finite maximum.

## 10. What this candidate closes and what remains open

Subject to fresh mathematical review, this note supplies:

- the two missing self-contained lines in the accepted-scope fixed-1D proof;
- the correct `O(h)` endpoint map order for vertex-dual volumes;
- an exact periodic free-form identity for base and half-shift meshes;
- a direct free tensor strong-resolvent route;
- a bounded physical-cell-average killing perturbation argument; and
- a self-contained `C_0` functional-calculus, positive-time-net, and moving-
  pairing bridge for `r=0,1,2`.

It does **not** yet supply:

- a frozen, independently accepted refinement/rate source binding (2.1)--
  (2.6) to every declared mesh family;
- an independently checked generalized Mosco tensorization theorem, rather
  than the direct free strong-resolvent result in Section 5;
- exact control-specific cell averages or a production gauge/application
  enclosure;
- a quantitative cut-cell, spatial, or evaluator error;
- the `r=1,2` box-exhaustion theorem;
- a continuum root-margin certificate; or
- complete C0, complete C1, C2, C3, F0, release, or submission eligibility.

The honest current decision is therefore:

```text
fixed-1D cell-centred free OU lemma        = ACCEPTED SCOPE, TWO CLARIFICATIONS RECORDED
relative-OU parameter extension           = PROOF CANDIDATE
vertex-dual free OU extension              = PROOF CANDIDATE
periodic free diffusion extension          = PROOF CANDIDATE
free tensor strong-resolvent bridge        = PROOF CANDIDATE
sharp bounded killing perturbation         = PROOF CANDIDATE, NEEDS FREE TENSOR MOSCO
abstract C0 functional-calculus bridge     = PROVED HERE, FRESH AUDIT OPEN
uniform r=0,1,2 positive-time pairing      = PROVED HERE, DATA HYPOTHESES OPEN
complete C1                                = HOLD
computable C2/C3 and continuum topology    = HOLD
PRR release                                = HOLD
```
