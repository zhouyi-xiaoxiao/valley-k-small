# Strict-continuum research program v2 for encounter multimodality

Date: 2026-07-14  
Status: **GO-DESIGN / HOLD-CONTINUUM-CLAIM / no positive-budget execution**

Last C1-route update: 2026-07-17.

## 0. Purpose, authority, and hard boundary

This note turns Section 7 of `continuum_next_stage_path.md` into a proof and
verification contract.  It does not report a continuum limit.  Its purpose is
to state exactly which continuum object the finite-volume chain must approach,
which qualitative and quantitative convergence statements are needed, how
artificial-box error enters, and how a componentwise observable error would
transfer a finite-volume root certificate to the continuum law.

Two logically separate results must remain separate.

1. The accepted exact-`m` theorem fixes finite `d>=2`, finite `m`, a compact
   positive-time window, and all geometric and probabilistic data; then takes
   the narrow-slab parameter small and only afterwards the Doi budget small.
   It proves a complete finite-window stationary signature in that sequential
   regime.  It is pointwise in `d,m`, uses saturated contact asymptotically,
   supplies no useful lower bound on `B0(epsilon)`, and supplies no event-mass
   floor.
2. The program below concerns the separate broad-patch, physical-`d=2`,
   finite-parameter numerical family.  It asks for a certified spatial and
   box limit at inputs frozen elsewhere.  It neither follows from nor modifies
   the exact-`m` theorem.

This file is therefore not authority to:

- read or run any prospective positive-`B`/F1 result;
- select or alter a control, budget, mesh, box, time window, or root tube;
- modify the manuscript, any Round-160 artifact, or frozen theorem bytes;
- call mesh agreement, two-box agreement, or off-lattice agreement a theorem;
- claim a cusp, a global mode count, physical `d=3`, or an event-mass floor.

The current decision is `GO` for local theorem/design work and `HOLD` for every
strict-continuum scientific sentence.

## 1. Intended theorem, stated before its ingredients

Let `C` be the finite set of already frozen controls and let the budget be a
single separately frozen input.  This note does not record their values.  For
control `c`, write

\[
 F_{\infty,c}(t)=\frac{f_{\infty,c}(t)}{B}
 =\langle V_c,q_{\infty,c}(t)\rangle
 \tag{1.1}
\]

when `B>0`.  At `B=0`, the right-hand side defines the free-exposure
observable directly; no division by zero is used.  Let `F_{h,L,c}` denote the
corresponding rate-defined finite-volume observable on an artificial box of
size `L` and mesh/alignment label `h`.

For physical `d=2`, the dimensional ledger is fixed as

\[
 [F]=L^{-2},\qquad [\partial_t^rF]=L^{-2}T^{-r}
 \quad(r=0,1,2).
 \tag{1.1a}
\]

| Quantity | Physical dimension |
|---|---|
| `F`, `E_{*,0}`, `epsilon_0` | `L^-2` |
| `partial_t F`, `E_{*,1}`, `epsilon_1`, `eta_*`, `zeta_*`, `rho_h` | `L^-2 T^-1` |
| `partial_t^2 F`, `E_{*,2}`, `epsilon_2`, `kappa_*` | `L^-2 T^-2` |
| root time and root displacement | `T` |

The strict-continuum deliverable is a componentwise, computable inequality

\[
 \max_{c\in\mathcal C}\sup_{t\in[\tau,T]}
 \left|\partial_t^rF_{h,L,c}(t)
       -\partial_t^rF_{\infty,c}(t)\right|
 \le E_{{\rm space},r}(h,L)
    +E_{{\rm box},r}(L)
    +E_{{\rm eval},r}(h,L),
 \quad r=0,1,2.
 \tag{1.2}
\]

Here:

- `E_space` is the finite-volume-to-reflecting-box error;
- `E_box` is the reflecting-box-to-natural-decay error;
- `E_eval` includes semigroup truncation, time anchoring, interval arithmetic,
  and roundoff, but not spatial or box error; and
- every term is computed from frozen inputs without using a favorable observed
  topology or choosing a subsequence.

A single `C2` norm may be reported only after fixed dimensional scale factors
for orders `r=0,1,2` have been declared.  Root transfer uses the three physical
unit bounds in (1.2), not an unscaled sum of quantities with different units.

Qualitative convergence to zero is an intermediate theorem.  A strict
continuum mode claim needs the finite, computable right-hand side of (1.2) to
fit inside independently certified root margins.

## 2. The target continuum object

### 2.1 Natural-decay quotient

The physical dimension is fixed at `d=2`.  Gate C0 must fix

\[
 D>0,\qquad \gamma>0,\qquad W>0.
 \tag{2.0}
\]

The exact transverse quotient is

\[
 \Omega_\infty=\mathbb R_z\times\mathbb R_{r_\parallel}
                 \times\mathbb T_W,
 \qquad x=(z,r_\parallel,r_\perp).
 \tag{2.1}
\]

Set

\[
 \mathbf D=\operatorname{diag}(D/2,2D,2D),\qquad
 b=(-\gamma(z-\bar z),-\gamma r_\parallel,0).
 \tag{2.2}
\]

The forward free operator is

\[
 \mathcal Lq=-\nabla\!\cdot(bq)
              +\nabla\!\cdot(\mathbf D\nabla q).
 \tag{2.3}
\]

There is no reflecting face in either unbounded coordinate.  “Natural decay”
means the closed weighted-space realization below; it is not an informal
pointwise boundary condition at infinity.  The transverse coordinate is
periodic.

The normalized reversible density is

\[
 \pi(x)=Z^{-1}\exp\!\left[-\frac{\gamma(z-\bar z)^2}{D}
                     -\frac{\gamma r_\parallel^2}{4D}\right],
 \tag{2.4}
\]

uniform in `r_perp`.  Work first with density ratios in

\[
 H=L^2(\Omega_\infty,\pi\,dx),\qquad q=\pi u,
 \tag{2.5}
\]

equivalently with densities in `X_pi=L2(pi^{-1}dx)`.

All Hilbert spaces, forms, and generators in the primary contract are real.
If a later argument uses the complexification, the convention is

\[
 \langle u,v\rangle_H=\int_{\Omega_\infty}\overline{u}v\,\pi\,dx,
\]

with the first factor conjugated in every continuum and discrete form.  In
particular, the complexified diffusion and killing terms are
`(grad conjugate(u))^T D grad(v)` and `conjugate(u)*v`; a complex bilinear
square is never used as a positivity argument.

### 2.2 Killing field and closed form

For the broad frozen patch family, the target observable is

\[
 V_c(z,r)=W^{-1}\mathbf1_{\{\rho(r)<a\}}
                  \sum_j w_j^{(c)}\phi_j(z),
 \qquad 0<a<W/2,
 \tag{2.6}
\]

where every `phi_j` is a fixed, bounded, nonnegative, unit-integral compact
patch, `rho` uses the minimum image on the torus, and every frozen control
satisfies

\[
 w_j^{(c)}\ge0,\qquad \sum_jw_j^{(c)}=1.
 \tag{2.6a}
\]

The sharp contact indicator is retained; a smoothed contact surface would
define a different model.  No moving-support or shape derivative is part of
this program.

For a fixed nonnegative budget `B`, define the symmetric nonnegative form

\[
 \mathfrak a_{\infty,c}(u,v)
 =\int_{\Omega_\infty}(\nabla u)^T\mathbf D\nabla v\,\pi\,dx
  +B\int_{\Omega_\infty}V_cuv\,\pi\,dx
 \tag{2.7}
\]

on the weighted-`H1` closure of the explicit algebraic form core

\[
 \mathcal C
 =C_c^\infty(\mathbb R^2)
   \otimes C^\infty(\mathbb T_W).
 \tag{2.7a}
\]

The torus factor is periodic by definition.  Because `V_c` is bounded, adding
the killing term does not change this form domain.  Let `H_infty,c>=0` be its
self-adjoint operator.  In density variables the killed forward generator is

\[
 A_{\infty,c}=\mathcal L-BM_{V_c},\qquad
 q_{\infty,c}(t)=e^{tA_{\infty,c}}q_0.
 \tag{2.8}
\]

The initial datum must be frozen as part of the model contract and satisfy

\[
 q_0\in X_\pi,\qquad q_0\ge0,\qquad
 \int_{\Omega_\infty}q_0\,dx=1.
 \tag{2.8a}
\]

The compact initial bump used by the broad family meets these conditions.
Every probabilistic and coupling bound below uses this unit-mass convention.
A future subprobability convention would require an explicit mass
`M0=integral q0` in C0 and a factor `M0` on every expectation, exit, and
observable bound; it is not silently allowed by this version.  The observable
and its positive-time derivatives are safely written on the state side as

\[
 F_{\infty,c}^{(r)}(t)
 =(-1)^r\langle V_c,H_{\infty,c}^{\,r}
          e^{-tH_{\infty,c}}u_0\rangle_H,
 \quad u_0=q_0/\pi,\quad r=0,1,2.
 \tag{2.9}
\]

Equation (2.9) does not apply the generator to the discontinuous contact
indicator.  The restriction `tau>0` is essential because
`||H^r exp(-tH)||` grows like `t^{-r}` near zero.

### 2.3 Proposition C0-A (proved operator-realization sublemma)

Under (2.0)--(2.8a), let

\[
 \mathcal V=\overline{\mathcal C}^{\|\cdot\|_{\mathcal V}},
 \qquad
 \|u\|_{\mathcal V}^2
 =\|u\|_H^2+
   \int_{\Omega_\infty}(\nabla u)^T\mathbf D\nabla u\,\pi\,dx.
 \tag{2.10}
\]

Then the following statements hold.

1. The normalizing constant and reversible identity are

   \[
    Z=\frac{2\pi D W}{\gamma},
    \qquad \mathbf D\nabla\log\pi=b.
    \tag{2.11}
   \]

2. For every fixed frozen control `c` and `B>=0`, the form
   `a_infty,c` is densely defined, closed, symmetric, nonnegative, and
   Dirichlet on the same domain `V`.  More precisely,

   \[
    \|u\|_{\mathcal V}^2
    \le \|u\|_H^2+\mathfrak a_{\infty,c}(u,u)
    \le (1+B\|V_c\|_\infty)\|u\|_{\mathcal V}^2.
    \tag{2.12}
   \]

   Thus bounded sharp-contact killing changes neither the form domain nor the
   natural-decay condition.

3. The first representation theorem supplies a unique nonnegative
   self-adjoint operator `H_infty,c`; `exp(-t H_infty,c)` is a symmetric
   sub-Markov contraction semigroup and is analytic for positive time.  The
   map

   \[
    U:H\longrightarrow X_\pi,\qquad Uu=\pi u,
    \qquad \|Uu\|_{X_\pi}=\|u\|_H,
    \tag{2.13}
   \]

   is unitary, and

   \[
    A_{\infty,c}=U(-H_{\infty,c})U^{-1}
   \tag{2.14}
   \]

   is the form-associated natural-decay realization of `L-B M_Vc`; its
   action agrees with the algebraic expression on the core (2.7a).  No
   separate essential-self-adjointness claim for the minimal core operator is
   needed or made here.

4. For `u0 in H`, `r=0,1,2`, and `t in [tau,T]`, (2.9) is well defined and

   \[
    \sup_{t\in[\tau,T]}|F_{\infty,c}^{(r)}(t)|
    \le \|V_c\|_H C_r(\tau)\|u_0\|_H,
    \quad C_0(\tau)=1,
    \quad C_r(\tau)=\left(\frac{r}{e\tau}\right)^r\ (r=1,2).
    \tag{2.15}
   \]

5. If (2.8a) holds, then `q_infty,c(t)>=0`,
   `F_infty,c(t)>=0`, and the exact integrated mass identity is

   \[
    \int_{\Omega_\infty}q_{\infty,c}(t)\,dx
    +B\int_0^tF_{\infty,c}(s)\,ds=1.
    \tag{2.16}
   \]

**Proof.**  The two Gaussian integrals and the normalized torus measure give
(2.11), and direct differentiation gives the reversible identity component
by component.  The free energy form is closed by the definition of
`V`; adding bounded nonnegative multiplication preserves closedness,
equivalent form norms, and the Dirichlet property, proving (2.12).  The first
representation theorem and the standard Dirichlet-form correspondence give
the self-adjoint sub-Markov semigroup.  Equation (2.13) is an immediate norm
   identity.  Integration by parts on `C` identifies the form-associated
   realization in (2.14).  The spectral theorem gives

\[
 \|H_{\infty,c}^{\,r}e^{-tH_{\infty,c}}\|
 \le \sup_{\lambda\ge0}\lambda^re^{-\tau\lambda}
 =\left(\frac{r}{e\tau}\right)^r
 \tag{2.17}
\]

for `r=1,2`, while contraction gives `r=0`; Cauchy--Schwarz proves (2.15).
Finally, Gaussian cutoffs show that the constant function `1` lies in
`V`.  Testing the weak evolution with `1` removes the gradient term and
gives `d integral(q)/dt=-B F`; positivity follows from the sub-Markov
property, and integration from zero proves (2.16).  This proves C0-A.

C0-A is a genuine continuum operator theorem, but it is only one sublemma of
gate C0.  It does **not** freeze the concrete model bytes, prove the finite-
volume form or identification maps, establish C1, supply a computable C2/C3
error, or promote any stationary topology claim.

## 3. Artificial reflecting boxes are approximants, not the target

Choose a nested family

\[
 \Omega_L=I_z^L\times I_r^L\times\mathbb T_W,
 \qquad I_z^L\uparrow\mathbb R,\quad I_r^L\uparrow\mathbb R,
 \tag{3.1}
\]

whose faces remain a declared positive distance from the supports of `q0`
and all `V_c`.  On the four artificial longitudinal faces impose zero
probability flux.  In density-ratio variables this is weighted Neumann.  Let
`H_L,c` be the operator associated with (2.7) restricted to `Omega_L` and this
boundary condition.

The bounded-box semigroup theorem already proves that each `H_L,c` is a valid
analytic killed Doi model.  It does **not** prove that it approximates
`H_infty,c`.  The strict track must establish both:

1. qualitative exhaustion, such as Mosco/strong-resolvent convergence
   `H_L,c -> H_infty,c`; and
2. the computable derivative-observable bound `E_box,r(L)` in (1.2).

Reflecting and natural-decay boundaries must never be described as the same
physical condition.  The reflection is allowed only as an approximation whose
effect is explicitly bounded.

## 4. Rate-defined finite-volume object

### 4.1 Discrete state and form

For every box and declared alignment, let `T_h,L` be the control-volume tensor
mesh family.  The baseline, refinement, and box rows are cell-centred; the
declared nonperiodic alignment variants may instead use vertex-centred dual
control volumes with half volumes at the reflecting endpoints; and the
periodic axis has both base and half-cell-shift variants.  The two
unbounded-coordinate approximants use Scharfetter--Gummel face rates; exterior
box fluxes are zero and periodic faces wrap exactly.

The convergence object is the **ideal analytic SG scheme**: exact real
exponentials, Bernoulli factors, globally gauged reversible masses, and one
common conductance per undirected edge.  The production field literally named
`stationary_mass` is instead the ungauged representative quadrature primitive
`tilde_mu_h,i=|C_i|*exp[-Phi(x_i^rep)]`; it is not `integral_C_i pi` and is not
a box-normalized probability.

A separate authenticated fixed-row source now encloses the physical cell
integrals.  Another reconstructs the formula-defined common edge fluxes,
directed rates, and factorized `rho`.  Their builders and independently written
validators use the same pinned `gmpy2`/MPFR backend and apply only to the fixed
level-zero rows.  They are neither backend independence nor one correlated
same-member containment receipt.  The production-centre matrix therefore
remains an evaluator expansion point, not the object of the `h -> 0` theorem.
The correlated production gauge/application bridge is still open, and its
discrepancy belongs to `E_eval`, not `E_space`.

Let `Q_h,L^0` be the free **row** generator, `pi_h,i>0` its reversible cell
mass, and `k_h,c,i=B V_h,c,i` the nonnegative cell-averaged killing.  The free
graph is connected, its off-diagonal rates obey `q_ij>=0`, and therefore its
positive reversible mass is unique up to one global scalar.  Thus

\[
 \pi_{h,i}q_{ij}=\pi_{h,j}q_{ji},\qquad
 \sum_jq_{ij}=0,
 \tag{4.1}
\]

for the free operator, and

\[
 Q_{h,L,c}=Q_{h,L}^0-\operatorname{diag}k_{h,c}
 \tag{4.2}
\]

has nonpositive row sums.  If `p'=Q^T p` and `u_i=p_i/pi_h,i`, detailed
balance gives `u'=Q u`.  The discrete nonnegative form is

\[
 \begin{split}
 \mathfrak a_{h,L,c}(u,v)
  ={}&\frac12\sum_{i,j}\pi_{h,i}q_{ij}
        (u_i-u_j)(v_i-v_j)\\
    &+\sum_i\pi_{h,i}k_{h,c,i}u_iv_i,
 \end{split}
 \tag{4.3}
\]

where the edge sum uses the nonnegative off-diagonal free rates.  Its operator
is `H_h,L,c=-Q_h,L,c` on `ell2(pi_h)`.  Equivalently, summing once over each
undirected edge uses the single common conductance
`c_{ij}=pi_h,i*q_ij=pi_h,j*q_ji` and no extra factor `1/2`.

### 4.2 Identification with continuum functions

The proof must state its identification maps.  One acceptable choice is the
piecewise-constant reconstruction

\[
 J_hu=\sum_i u_i\mathbf1_{C_i}
 \tag{4.4}
\]

Use the corresponding weighted cell map `P_h`.  Here `C_i` is the actual
control or dual-control volume of the declared row,
including endpoint half volumes and wrapped periodic segments where present;
it is not silently replaced by an equal cell-centred box.

Write the production payload field named `stationary_mass` as
`tilde_pi_h,i`.  It is an ungauged representative quadrature primitive, not a
physical cell mass.  Connectedness leaves one scalar gauge, fixed by

\[
 M_L=\int_{\Omega_L}\pi(x)\,dx,
 \qquad
 g_{h,L}=\frac{M_L}{\sum_i\widetilde\pi_{h,i}},
 \qquad
 \pi_{h,i}=g_{h,L}\widetilde\pi_{h,i}.
 \tag{4.4a}
\]

Detailed balance is unchanged by this rescaling and
`sum_i pi_h,i=M_L`; this is not normalization to one and does not imply
`pi_h,i=integral_C_i pi` cell by cell.  Separately authenticated physical
integrals `M_i^pi=integral_C_i pi` now exist for all twelve fixed rows, but
they do not change the meaning of `tilde_pi_h,i` and do not supply a correlated
gauged production member.  The ideal common conductance is
`c_ij=g_h,L*tilde_pi_h,i*q_ij`.  Outward same-member enclosures of the global
gauge, every gauged mass, every common conductance, the map, and the killing
multiplier are still required before the production bridge can pass.

For the active proof route, “corresponding” is no longer left ambiguous.  Put

\[
 M_i^\pi=\int_{C_i}\pi(x)\,dx,
\]

and reserve `P_h` for the exact-adjoint map

\[
 (P_hu)_i=\pi_{h,i}^{-1}\int_{C_i}u(x)\pi(x)\,dx.
 \tag{4.4b}
\]

The literal weighted cell average is a different map,

\[
 (A_hu)_i=(M_i^\pi)^{-1}\int_{C_i}u(x)\pi(x)\,dx.
 \tag{4.4c}
\]

Put `rho_i=M_i^pi/pi_h,i` and let `E_h=J_hA_h` be the
`pi`-weighted cell conditional expectation.  Then

```text
P_h = J_h^*                      A_h J_h = I
P_h = diag(rho_i) A_h            P_h J_h = diag(rho_i)
J_h A_h = E_h                    J_h P_h = rho_h^pc E_h.
```

These are exact finite-grid identities; neither `P_hJ_h=I` nor
`J_hP_h=E_h` is asserted unless the two cell masses happen to agree.  For
initial density `q_0=pi*u_0`, (4.4b) gives exact physical cell masses
`pi_h,i*(P_hu_0)_i=integral_C_i q_0`.  Representative-point sampling is a
third map,

\[
 (S_hu)_i=u(x_i^{\rm rep}),
 \tag{4.4d}
\]

used only for smooth or continuous recovery functions; it is not defined on
all of `H_L`.  The representative may be a vertex in a dual-volume row, so it
is not globally described as a cell centre.  The immutable machine-readable
C0-v1 candidate predates this denominator decision and remains a stale HOLD;
it must not be edited or re-signed.  With that gauge and map choice,
define the varying density

\[
 \pi_h^{\rm pc}|_{C_i}=\pi_{h,i}/|C_i|
 \tag{4.5}
\]

and let `H_h=ell2(pi_h)`, `H_L=L2(Omega_L,pi dx)`.  A proof may not silently
identify these spaces.  Gate C1 must construct `J_h:H_h->H_L` and
`P_h:H_L->H_h` and verify all of the following axioms, uniformly over the
declared fixed-box alignments:

\[
\begin{aligned}
 &\left\|\frac{\pi_h^{\rm pc}}{\pi}-1\right\|_{L^\infty(\Omega_L)}
       \longrightarrow0,\qquad
 0<c\le\frac{\pi_h^{\rm pc}}{\pi}\le C<\infty,\\
 &\|J_h\|+\|P_h\|\le2+o(1),\qquad
 \|J_hP_hu-u\|_{H_L}\longrightarrow0\quad(u\in H_L),\\
 &\|P_hJ_hv_h-v_h\|_{H_h}
       \le o(1)\|v_h\|_{H_h},\\
 &\left|\|J_hv_h\|_{H_L}^2-\|v_h\|_{H_h}^2\right|
       \le o(1)\|v_h\|_{H_h}^2,\\
 &\left|\langle J_hv_h,u\rangle_{H_L}
       -\langle v_h,P_hu\rangle_{H_h}\right|
       \le o(1)\|v_h\|_{H_h}\|u\|_{H_L}.
\end{aligned}
 \tag{4.5a}
\]

For the exact-adjoint choice (4.4b), the final pairing defect in (4.5a) is
identically zero.  The assertion `J_hP_hu -> u` is pointwise strong for every
fixed `u`; it is not operator-norm convergence, since the cellwise conditional
expectation has an infinite-dimensional orthogonal complement on every finite
grid.

The little-`o` terms in (4.5a) must be explicit functions of `h` in Gate C2.
If a different pair of maps is used, it must satisfy equivalent asymptotic
norm and adjoint properties.  The active C0 discretization of the initial law
is unique.  Define

\[
 p_{0,h,i}=\int_{C_i}q_0(x)\,dx,
 \qquad
 u_{0,h,i}=p_{0,h,i}/\pi_{h,i}=(P_hu_0)_i.
 \tag{4.5b}
\]

The compact support of `q_0` must lie inside every declared nonperiodic box;
periodic images are combined before cell integration.  Hence
`sum_i p_0,h,i=1` exactly, with no meshwise renormalization.  Approximate
initial projections may be studied only as a separate C1 perturbation theorem,
not substituted into this C0 model freeze.  The remaining discrete-data
convergence requirement is

\[
 \|J_hV_{h,c}-V_c\|_{H_L}\to0,
 \tag{4.5c}
\]

uniformly over the finite control set.  In particular, for every sequence
`v_h` bounded in `H_h`, the required moving pairing is

\[
 \langle V_{h,c},v_h\rangle_{H_h}
 -\langle V_c,J_hv_h\rangle_{H_L}\longrightarrow0.
 \tag{4.5d}
\]

This moving-pairing condition, not just pointwise coefficient convergence, is
required to pass from operator convergence to the observable.

### 4.3 Killing consistency

The target cell field is the physical-volume average of (2.6), with no
meshwise renormalization.  For the twelve genuine ideal dyadic families, the
Round-173 source-bound candidate proves on a common tail

\[
 \|J_hV_{h,c}-V_c\|_{L^1(\pi)}\le C_1h,
 \qquad
 \|J_hV_{h,c}-V_c\|_{L^2(\pi)}\le C_2h^{1/2},
 \tag{4.6}
\]

plus the smooth-patch quadrature contribution, with explicit symbolic source
constants, including vertex-dual endpoint half cells and wrapped periodic
cells.  The proof uses the strict embedded contact-tube conditions behind the
`4*pi*a*delta` annulus bound and does not differentiate the sharp indicator.
These orders are therefore no longer merely neutral diagnostic targets within
the ideal formula-defined scope.  The constants have not been numerically
evaluated, however, and no correlated production member or complete C2 result
follows.

## 5. Convergence chain

### 5.1 Gate C1: fixed-box qualitative form convergence

Round 174 closes the independently audited composition of these
formula-defined fixed-box premises for the twelve ideal dyadic tails.  That is
an ideal fixed-box C1 closure only.  Project-level and production-level
complete C1 remain false until a correlated level-zero member and the
production gauge/evaluator bridge are accepted.

For each of the twelve fixed boxes and every simplex control and fixed finite
budget, Round 174 proves Mosco convergence of the ideal
analytic form (4.3) to the reflecting-box restriction of (2.7) in the varying
Hilbert spaces defined by `J_h,P_h`.  Production-centre/interval error remains
in the separate finite-grid evaluator ledger.  The composition discharges:

- **liminf:** every sequence with weakly convergent reconstructions and
  bounded discrete energy has a weighted-`H1` limit and no smaller limiting
  energy;
- **recovery:** every form-domain function has a discrete sequence converging
  strongly with no excess limiting energy;
- **measure consistency:** the discrete reversible masses and inner products
  converge to their weighted continuum counterparts;
- **edge consistency:** SG conductances converge to the weighted diffusion
  form on every axis, including boundary half volumes and periodic wraps; and
- **killing consistency:** the bounded cell-average multiplication forms
  converge uniformly over the finite control set and all declared alignments.

The qualitative output is

\[
 J_h(H_{h,L,c}+\lambda)^{-1}P_hg
 \longrightarrow(H_{L,c}+\lambda)^{-1}g,
 \quad \lambda>0.
 \tag{5.1}
\]

Strong-resolvent convergence at one spectral parameter is not by itself the
stated uniform-in-time observable conclusion.  For `r=0,1,2` define

\[
 f_{r,t}(\lambda)=\lambda^r e^{-t\lambda},
 \qquad \lambda\ge0,\quad t\in[\tau,T].
 \tag{5.1a}
\]

Each `f_{r,t}` lies in `C0([0,infinity))`.  Round 174 uses the functional
calculus together with

\[
 \sup_{\lambda\ge0}|f_{r,t}(\lambda)-f_{r,s}(\lambda)|
 \longrightarrow0\quad(t\to s)
 \tag{5.1b}
\]

uniformly for `s,t in [tau,T]`; equivalently, it may use the explicit
equicontinuity bound obtained from
`sup_lambda lambda^(r+1) exp(-tau lambda)<infinity`.  A finite time net then
upgrades pointwise functional-calculus convergence to

\[
 \sup_{t\in[\tau,T]}
 \|J_hf_{r,t}(H_{h,L,c})P_hu_0
       -f_{r,t}(H_{L,c})u_0\|_{H_L}\longrightarrow0.
 \tag{5.1c}
\]

Finally (4.5b)--(4.5d), uniform boundedness of the data, and the moving
pairing give uniform convergence of the scalar observables and their first
two time derivatives.  This is the complete qualitative bridge despite the
sharp contact indicator.  It still supplies no computable rate and cannot be
subtracted from a root margin.

### 5.2 Gate C2: quantitative positive-time observable convergence

One of the following quantitative routes must be completed.

**Route R (resolvent/sectorial).**  Prove a computable resolvent comparison on
an explicit sectorial contour,

\[
 \|J_h(z+H_{h,L,c})^{-1}P_h-(z+H_{L,c})^{-1}\|
 \le\eta_{h,L}(z),
 \tag{5.2}
\]

including projection, discrete-measure, contact cut-cell, patch quadrature,
and boundary-cell terms.  Insert (5.2) into the semigroup functional calculus
for `H^r exp(-tH)`, integrate the contour with `t>=tau`, and obtain a finite
`E_space,r`.

**Route P (parabolic residual/duality).**  Reconstruct the discrete solution,
its first two generator actions, and a conservative flux.  Bound their
space-time residuals in a declared dual norm, solve the corresponding primal
and dual stability estimates after a positive-time split, and enclose the
observable error directly.  The dual observable remains bounded
multiplication; no derivative of the contact indicator may be inserted by
formal integration by parts.

Either route must output, separately for `r=0,1,2`,

\[
 E_{{\rm space},r}
 =E_{{\rm operator},r}+E_{{\rm measure},r}
  +E_{{\rm contact},r}+E_{{\rm patch},r}+E_{{\rm initial},r}.
 \tag{5.3}
\]

The constants may grow as a declared power of `tau^{-1}` but must be finite
at the frozen positive `tau`.  A theorem giving only `o(1)`, an unspecified
constant, eigenvalue convergence, or agreement between two meshes fails C2.

### 5.3 Required uniformity

Uniformity is finite and explicit, not asymptotic in model complexity.  Take
the maximum over:

- the fixed physical-`d=2` control set;
- the declared base/shift and slab-alignment variants;
- the declared finite box family; and
- `t in [tau,T]`.

No uniformity in physical dimension, number of patches, arbitrary controls,
`tau downarrow 0`, or an unbounded set of boxes is required or claimed.

## 6. OU box tail and truncation

### 6.1 A computable exit-tail input

For either unbounded OU coordinate write

\[
 dX_t=-\gamma(X_t-\mu)\,dt+\sqrt{2D_X}\,dW_t.
 \tag{6.1}
\]

Here `(mu,D_X)=(bar z,D/2)` for `z` and `(0,2D)` for `r_parallel`.  If the
initial support obeys `|X0-mu|<=R0_X` and the artificial interval contains the
symmetric core `|X-mu|<R_X`, Gate C0 must also verify the strict margin

\[
 R_X>R_{0,X}.
 \tag{6.1a}
\]

Only then does the following argument apply:

\[
 X_t-\mu=e^{-\gamma t}\left[X_0-\mu+\sqrt{2D_X}\,M_t\right],
 \qquad
 \langle M\rangle_t=\Theta_t
 =\frac{e^{2\gamma t}-1}{2\gamma}.
 \tag{6.2}
\]

The reflection principle and a union bound therefore give the conservative
explicit estimate

\[
 \delta_X(L,T)
 :=\Pr\!\left(\sup_{0\le s\le T}|X_s-\mu|\ge R_X\right)
 \le\min\!\left\{1,
 4\exp\!\left[-\frac{(R_X-R_{0,X})^2}
                    {4D_X\Theta_T}\right]\right\}.
 \tag{6.3a}
\]

For an asymmetric interval `(ell_X,u_X)` and initial support
`[x0_X^-,x0_X^+]`, define the side-specific margins

\[
 m_{X,-}=x_{0,X}^- -\ell_X,\qquad
 m_{X,+}=u_X-x_{0,X}^+.
 \tag{6.3b}
\]

The simple sidewise reflection bound below is admissible only when
`ell_X<mu<u_X`, `m_{X,-}>0`, and `m_{X,+}>0`.  Under those conditions,

\[
 \delta_X^{\rm asym}(L,T)
 \le\min\!\left\{1,
 2\exp\!\left[-\frac{m_{X,-}^2}{4D_X\Theta_T}\right]
 +2\exp\!\left[-\frac{m_{X,+}^2}{4D_X\Theta_T}\right]
 \right\}.
 \tag{6.3c}
\]

If the mean is not strictly inside the box or either side margin is
nonpositive, define `delta_X^asym=1`.  A nonpositive margin is never squared
and inserted into an exponential.  A sharper moving-boundary calculation is
optional, but it must retain separate certified left and right margins and
the same fail-closed convention.  The two-coordinate exit probability is
bounded by `delta_z+delta_r`, using either the symmetric or admissible
asymmetric version coordinate by coordinate.  The torus has no box tail.  If
a future initial law is not compactly supported, its explicit outside-core
mass must be added under a separately frozen decomposition.

### 6.2 What the exit tail proves, and what it does not

Couple the unbounded and reflected processes with the same noise until the
first exit.  Because the compact patches and contact observable agree in the
interior and the Feynman--Kac weight lies in `[0,1]`, the applicable bound
(6.3a) or (6.3c) gives the direct zeroth-order bound

\[
 \sup_{t\le T}|F_{L,c}(t)-F_{\infty,c}(t)|
 \le2\|V_c\|_\infty\,[\delta_z(L,T)+\delta_r(L,T)].
 \tag{6.4}
\]

The factor two is intentionally conservative.  Formula (6.4) is not a bound
for the first or second time derivative.  Differentiating the exit event or
applying the adjoint generator to the sharp indicator would be invalid.

Gate C3 therefore requires an additional **positive-time truncation lemma**.
Two acceptable proof routes are:

1. compare boxed and unboxed resolvents with a cutoff equal to one on the
   initial and observable supports, bound cutoff commutators in an OU Gaussian
   collar, and use the same sectorial calculus as Gate C2; or
2. prove killed-kernel/local parabolic derivative bounds after a time split
   of at least a fixed fraction of `tau`, and combine them with the coupled
   exit estimate.

The required output is a computable

\[
 E_{{\rm box},r}(L;\tau,T),\qquad r=0,1,2,
 \tag{6.5}
\]

with (6.4) available for `r=0` and explicit OU Gaussian collar/exit factors in
the `r=1,2` constants.  A bound of the schematic form

\[
 E_{{\rm box},r}
 \le C_r(\tau,T,B,\|V\|_\infty,q_0)
       [\delta_z+\delta_r]^\alpha,
 \quad \alpha>0,
 \tag{6.6}
\]

is acceptable only after `C_r` and `alpha` are proved and computable.  Equation
(6.6) is a target, not a result of this note.

The current broad patches are compact.  If a Gaussian-slab family is ever
substituted, its catalyst tail must be a separate explicit term; it may not be
hidden inside the OU state tail.  Comparing two empirical boxes remains a
diagnostic even when it agrees with (6.3).

## 7. Numerical evaluation error

`E_eval,r` is supplied by the separately audited sub-Markov/verified-semigroup
layer.  It must include:

- rate, killing, initial-mass, and generator interval radii;
- Poisson/Krylov or other semigroup truncation with a proved tail;
- sparse-action, dot-product, and norm roundoff in the frozen addition order;
- time-anchor and interval-cover error; and
- producer/verifier replay disagreement, treated as `HOLD`, not averaged.

This term must be uniform on the declared window and must enclose the exact
ideal finite-volume observable represented by (4.3).  It is insufficient to
propagate only the independently chosen production centres: the verified
operator/rate intervals must contain the ideal analytic SG member itself.
Repeated binary64 agreement, a safety factor without a derivation, or a
verifier that imports producer state does not define `E_eval`.

The final componentwise ledger is

\[
 \varepsilon_r
 =E_{{\rm space},r}+E_{{\rm box},r}+E_{{\rm eval},r},
 \qquad r=0,1,2.
 \tag{7.1}
\]

Each addend retains its source hash, assumptions, and outward-rounded value.
An unknown addend makes `epsilon_r` unknown and returns `HOLD_CONTINUUM_ERROR`.

## 8. Root-tube transfer to a continuum stationary signature

Fix one control.  Suppose the finite-volume interval certificate supplies
ordered peak/valley tubes `B_j=[a_j,b_j]` with pairwise disjoint interiors and
`b_j<a_{j+1}`.  Define the complementary closed gaps by
`R_0=[tau,a_1]`, `R_j=[b_j,a_{j+1}]`, and `R_n=[b_n,T]`.  A tube and its
adjacent gap intentionally share their boundary point.  The coverage validator
uses a canonical half-open serialization to count that point once while still
requiring the tube-boundary and gap-sign enclosures to agree there.  An
uncovered interval, a positive-length overlap, or incompatible shared-endpoint
signs returns `HOLD_INTERVAL_COVERAGE`.

Let the certified finite-volume margins be:

- `eta_*`: the smallest correctly oriented derivative magnitude at every tube
  boundary;
- `kappa_*`: the smallest correctly oriented curvature magnitude throughout
  every tube;
- `zeta_*`: the smallest correctly oriented derivative magnitude throughout
  every complement gap, including the time-window endpoints.

These are outward-rounded physical-unit margins over intervals, not values at
floating roots.  If

\[
 \varepsilon_1<\min\{\eta_*,\zeta_*\},
 \qquad
 \varepsilon_2<\kappa_*,
 \tag{8.1}
\]

then:

1. the continuum derivative has opposite signs at the two boundaries of each
   tube, so a stationary point exists there;
2. continuum curvature retains the certified strict sign throughout the tube,
   so that root is unique and has the same maximum/minimum type;
3. the derivative retains a strict sign on every complementary gap and at
   both endpoints, so no additional stationary point exists; and
4. the ordered complete finite-window stationary signature is identical.

This is the desired strict-continuum topology theorem.  If any inequality in
(8.1) fails, the result is `HOLD`; it is not evidence that the continuum
signature differs.

For a root-time enclosure, let `t_hat_h` be a reported finite-volume root
approximation in one tube, let `F_hat_h` denote its serialized numerical
finite-volume reference, and let the outward-rounded reference residual satisfy

\[
 |\widehat F_{h,L,c}'(\widehat t_h)|\le\rho_h.
 \tag{8.2}
\]

The continuum curvature floor in that tube is
`kappa_cont=kappa_*-epsilon_2>0`, not `kappa_*`.  If the unique continuum root
`t_infinity` and `t_hat_h` lie in the same tube, the mean-value theorem gives

\[
 |t_\infty-\widehat t_h|
 \le\frac{\varepsilon_1+\rho_h}{\kappa_*-\varepsilon_2}.
 \tag{8.3}
\]

Here the evaluator uncertainty between `F_hat_h` and the exact finite-volume
observable is already booked once in `epsilon_1` through `E_eval,1`; it is not
added again to `rho_h`.  The C5 ledger must reject either omission or duplicate
booking.  The residual is zero only when the serialized reference is certified
exactly stationary.  Any separately reported temporal interval radius is added
to (8.3).  Root displacement remains separate from the discrete stationary
signature.

`epsilon_0` is not needed to count and type stationary points, but it is
needed for heights and contrasts.  Basin probabilities and survival require
their own state/time-integral error ledger and tail coverage; they do not
follow from (8.1).

## 9. Executable stage and failure matrix

| Gate | Theorem input | Numerical input | Required output | Fail-closed condition |
|---|---|---|---|---|
| C0 model freeze | exact quotient, form, natural-decay domain, sharp contact, initial-space hypothesis | canonical parameter/control/budget hashes without result values | immutable model contract and dimensional units | any parameter inferred from a favorable run; reflecting box called physical |
| C1 finite-`L` Mosco | liminf, recovery, measure, edge, and killing lemmas | mesh/alignment schemas and exact SG/cell-average definitions | qualitative strong-resolvent and positive-time `C^2`-in-time observable convergence | only pointwise stencils, spectra, or mesh plots |
| C2 spatial rate | quantitative resolvent or residual/duality stability | directed contact/patch/initial/measure errors | `E_space,r`, `r=0,1,2`, uniform over declared variants | unknown constant, missing alignment, no derivative rate |
| C3 box exhaustion | unbounded and boxed forms, OU tail, positive-time derivative truncation lemma | exact box faces and support distances | `E_box,r`, `r=0,1,2` | only two-box agreement; exit probability reused as a derivative bound without proof |
| C4 evaluator | sub-Markov and outward-rounding proof | producer/verifier artifacts and interval cover | `E_eval,r`, replay receipts, full-window coverage | uncovered interval, nonpositive interval margin, replay mismatch, resource failure |
| C5 composition | triangle inequality with matched objects and units | three source ledgers and hashes | `epsilon_0,epsilon_1,epsilon_2` | double counting, omitted term, different generator/box/control bytes |
| C6 topology transfer | root-tube theorem and (8.1) | interval root, curvature, complement, endpoint margins | complete continuum stationary signature on `[tau,T]` | either margin inequality fails, or coverage has an uncovered interval, positive-length overlap, or incompatible shared endpoint |
| C7 independent audit | proof dependency graph and claim map | clean replay without producer imports | signed PASS/HOLD report with exact hashes | auditor repairs in place, changes a frozen input, or promotes a HOLD |

Numerical evidence can validate hypotheses, constants, and arithmetic ledgers.
It cannot replace the form-convergence, derivative-stability, or root-transfer
theorems.  Conversely, a convergence theorem with no computable finite-mesh
bound cannot validate the current finite calculation.

## 10. Adversarial audit sequence

The continuum track should use fresh labels rather than consume or overwrite
the existing numbered audit chain.

1. **C-A model attack:** check forward/backward signs, quotient factors,
   dimensional budget, natural-decay versus reflection, initial weighted
   space, and support/interior assumptions.
2. **C-B form attack:** independently derive detailed balance and (4.3), test
   half volumes and periodic shifts, and seek a sequence that violates either
   Mosco condition.
3. **C-C quantitative attack:** recompute every constant, stress the sharp
   cut-cell layer and worst alignment, and verify the `tau^{-r}` dependence.
4. **C-D truncation attack:** check the OU transformation and exit bound,
   attack asymmetry and support distances, and reject any unproved derivative
   use of (6.4).
5. **C-E topology attack:** mutate tube endpoints, signs, curvature,
   complement coverage, units, and one error addend; every mutation must hold.
6. **C-F reproducibility/editorial attack:** rebuild from canonical hashes,
   verify no prospective result was used to set a constant, and trace every
   continuum sentence to C1--C6.

An implementation or resource failure blocks promotion but is not a negative
physical result.  A mathematical counterexample blocks the affected theorem
gate and requires a new version; it may not be patched silently in an audit.

## 11. What stays out of the current PRR manuscript

The audited ideal fixed-box composition may be stated at that exact scope.
Until the correlated production member and the remaining C0--C7 gates pass,
none of the following enters the current PRR main text as a production-backed
or unbounded-continuum result:

- production-contained or evaluator-level SG/Mosco/resolvent convergence;
- a computable `C2` continuum error;
- an unbounded-domain finite-volume limit;
- an exact continuum one-/two-/three-mode assignment for the broad controls;
- positive-budget F1 outputs, prospective weights, or a useful budget claim;
- continuum basin mass, survival, or independent-process agreement;
- physical-`d=3`, cusp, phase-diagram, or global-time topology claims.

Before completion, the strongest allowed numerical phrase remains
“continuum-consistent numerical evidence,” with the precise mesh/alignment/box
scope stated.  The accepted exact-`m` theorem may remain at its audited
sequential narrow-noise/weak-budget scope, but it must not be used as if it
closed C1--C7 for the broad family.

## 12. Next concrete work products

The next authorized local theory products, in order, are:

1. implement result-blind, parameterized, candidate-native producers and
   verifiers for roles 8--10, including their complete transitive code/data
   closure and exact operation DAG; split the raw primitive from the current
   legacy role-9 dependency or declare and verify the true execution order;
2. rebuild the predecessor candidate, obtain a genuinely external commitment
   to its member/method/parameter/policy bytes, and only then execute fresh
   ordered roles 8--10;
3. freeze the complete executed outer manifest and operation model,
   independently stream the exact-DAG identities, and issue a distinct
   correlated level-`n=0` acceptance receipt for one common physical-integral/
   raw-flux/gauge/map/killing member;
4. close project-level C1 by joining that receipt to the accepted ideal
   twelve-family fixed-box composition;
5. numerically evaluate and audit the Round-173 symbolic constants, including
   the initial-projection term, and compose the same-member C2 ledger;
6. prove computable `r=1,2` positive-time box truncation, retaining the current
   exit estimate only as the `r=0` input;
7. freeze the complete `E_space+E_box+E_eval` machine ledger and mutation
   attacks; and
8. perform componentwise root transfer only after all preceding margins pass.

No positive-`B` propagation is needed for these steps.

## 13. Exact present boundary

```text
accepted exact-m theorem                         = unchanged
strict continuum operator target                 = fixed
C0-v3 semantic/well-definedness candidate        = PASS AT DECLARED SCOPE; COMPLETE C0 OPEN
12 genuine ideal dyadic refinement families      = PASS ROUND 172
fixed-row physical axis-cell integrals           = AUTHENTICATED SAME-BACKEND SOURCE ONLY
fixed-row formula raw common flux/rates           = AUTHENTICATED SAME-BACKEND SOURCE ONLY
ideal source-bound map/cut/killing inputs         = PASS CANDIDATE ROUND 173
ideal fixed-box C1 composition                    = PASS ROUND 174; IDEAL THEOREM SCOPE ONLY
predecessor-authority structural candidate        = PASS ROUND 177; B04 PREPARED ONLY
candidate-native method/provenance closure        = OPEN B06
external predecessor commitment                   = ABSENT
fresh ordered roles 8--10 replay                  = NOT PERFORMED
production level-zero correlated same member      = OPEN
project/production complete fixed-L C1            = OPEN
computable positive-time C2 spatial error         = OPEN
first/second derivative box truncation            = OPEN C3
verified finite-volume evaluation error           = separate open F0 dependency
broad-family continuum stationary signature       = HOLD
positive-B/F1 execution                            = NOT PERFORMED / NOT AUTHORIZED
release/submission                                 = HOLD
```

The program succeeds only when a common, fully outward-rounded error ledger
fits strictly inside the predeclared finite-volume derivative and curvature
margins for every promoted control.  Anything weaker remains valuable
convergence evidence, but not a strict continuum theorem.
