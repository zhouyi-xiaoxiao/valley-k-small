# Fixed-box one-dimensional free-OU Mosco sublemma candidate

Date: 2026-07-17

Status: **REPAIRED PROOF CANDIDATE / FRESH INDEPENDENT AUDIT OPEN / COMPLETE C1 FALSE**

This note isolates the smallest theorem-bearing part of Gate C1.  It contains
no control, killing, budget, reaction-time observable, box exhaustion, or root
statement.  Its only target is the free one-dimensional cell-centred
Scharfetter--Gummel form on one fixed reflecting interval.

## 1. Continuum form and scalar convention

All Hilbert spaces and forms in this note are real.  The optional complexified
version is sesquilinear: the second derivative factor is conjugated and every
quadratic edge term is an absolute square.  A complex bilinear reading is
forbidden because it would not define a nonnegative form.

Fix a bounded interval `I=[ell,r]`, axis diffusion `d>0`, OU stiffness
`gamma>0`, and mean `mu` in the interior.  Put

\[
 \Phi(x)=\frac{\gamma(x-\mu)^2}{2d},\qquad
 \pi(x)=C e^{-\Phi(x)},\qquad
 C=\sqrt{\frac{\gamma}{2\pi d}}.
\]

The restricted mass is

\[
 M_I=\int_I\pi(x)\,dx.
\]

No conditional renormalization is made.  The Hilbert space and free
reflecting form are

\[
 H=L^2(I,\pi dx),
 \qquad
 \mathfrak a(u,v)=\int_I d\,u'(x)v'(x)\pi(x)\,dx,
 \qquad D(\mathfrak a)=H^1(I).
\]

Because `pi` is smooth and strictly positive on the fixed compact interval,
weighted and unweighted `L2` and `H1` norms are equivalent.  The Neumann
condition belongs to the associated operator domain; it is not imposed on
the form domain.

For the physical midpoint axis, `d=D/2`, so
`Phi=gamma*(z-zbar)^2/D`.  For the physical relative-parallel axis, `d=2D`,
so `Phi=gamma*r_parallel^2/(4D)`.  These factors must not be interchanged.

## 2. Discrete form and fixed gauge

For `N>=3`, set

\[
 h=(r-\ell)/N,\qquad x_i=\ell+(i+1/2)h,
 \quad i=0,\ldots,N-1.
\]

Let

\[
 B(s)=\frac{s}{e^s-1},\qquad B(0)=1,
 \qquad \Delta_i=\Phi(x_{i+1})-\Phi(x_i).
\]

The **ideal analytic** row-generator rates are

\[
 q_{i,i+1}=\frac d{h^2}B(\Delta_i),\qquad
 q_{i+1,i}=\frac d{h^2}B(-\Delta_i),
\]

with zero exterior flux.  Define

\[
 \widetilde m_i=h e^{-\Phi(x_i)},\qquad
 g_h=\frac{M_I}{\sum_i\widetilde m_i},\qquad
 m_i=g_h\widetilde m_i.
\]

Then `sum_i m_i=M_I` exactly.  The Hilbert space is

\[
 H_h=\ell^2(m),\qquad
 \langle u,v\rangle_h=\sum_i m_i u_i v_i.
\]

The Bernoulli identity `B(-s)=exp(s)B(s)` gives exact detailed balance and
the undirected conductance

\[
 c_{i+1/2}=m_iq_{i,i+1}=m_{i+1}q_{i+1,i}.
\]

The discrete free form is therefore

\[
 \mathfrak a_h(u,v)=
 \sum_{i=0}^{N-2}c_{i+1/2}(u_{i+1}-u_i)(v_{i+1}-v_i).
\]

There is no additional factor `1/2` because each undirected edge is listed
once.

This is the only discrete operator to which the Mosco candidate applies.  The
current production builder stores outward binary64 intervals for the
**ungauged** primitives `tilde m_i` and the directed rates.  Those intervals do
not by themselves contain the gauge-fixed masses `m_i` or common
conductances `c_{i+1/2}` when `g_h` is not one.  Its downstream kernel also
selects a centre independently from each forward, backward, and raw-mass
interval; those unrelated centres need not share one exact conductance and are
not asserted to be exactly reversible.  Therefore no fixed-precision
production-centre sequence is used in an `h -> 0` argument, and the current raw
containment check is not a production bridge for this form.  Before C1/C4
composition, a verified evaluator must apply the same gauge with outward
enclosure and contain the ideal analytic form member at every finite `h`; that
additional width belongs to `E_eval`.  A theorem for a different single-valued
production selection would require a common edge conductance and an additional
relative perturbation `epsilon_h -> 0`; preserving second-order edge
consistency would require `epsilon_h=O(h^2)`.

## 3. Identification maps

Let `C_i=[ell+ih,ell+(i+1)h]` and

\[
 M_i=\int_{C_i}\pi(x)\,dx.
\]

Use piecewise-constant reconstruction

\[
 (J_hv)(x)=v_i\quad(x\in C_i).
\]

For this theorem candidate, choose the exact-adjoint map

\[
 (P_hu)_i=\frac1{m_i}\int_{C_i}u(x)\pi(x)\,dx.
\]

Then

\[
 \langle J_hv,u\rangle_H=\langle v,P_hu\rangle_{H_h}
\]

holds exactly.  This choice differs from the literal weighted cell average
with denominator `M_i`; the manufactured diagnostic currently uses that
average and records the distinction explicitly.

To keep the two maps distinct, write

\[
 (A_hu)_i=\frac1{M_i}\int_{C_i}u(x)\pi(x)\,dx.
\]

For functions with point values, reserve a third symbol for centre sampling,

\[
 (S_hu)_i=u(x_i).
\]

Unlike `A_h` and `P_h`, `S_h` is not defined on all of `H` and is used only for
smooth recovery functions.

Then `A_h` is the literal weighted cell average, whereas
`P_h=diag(rho_h)A_h` is the exact adjoint of `J_h`.

The map claims needed here reduce to the uniform cell-mass estimate

\[
 \rho_{h,i}:=\frac{M_i}{m_i}=1+O(h^2).
 \tag{3.1}
\]

Uniformly means that there are `h_0>0` and `K_mass<infinity`, depending only
on the fixed interval and frozen OU parameters, such that
`max_i|rho_{h,i}-1|<=K_mass*h^2` for `0<h<=h_0`.

Indeed,

\[
 \|J_hv\|_H^2=\sum_iM_i|v_i|^2,
 \qquad
 P_hJ_hv=(\rho_{h,i}v_i)_i.
\]

More precisely,

\[
 \|J_h\|=\|P_h\|=\sqrt{\max_i\rho_{h,i}},\qquad
 \|A_h\|=\sqrt{\max_i\rho_{h,i}^{-1}},
\]

and

\[
 \|P_hJ_h-I\|_{H_h\to H_h}
 =\max_i|\rho_{h,i}-1|=O(h^2).
\]

If `E_h=J_hA_h` is weighted conditional expectation onto the cellwise
constants and `rho_h^pc|_{C_i}=rho_{h,i}`, then

\[
 A_hJ_h=I,\qquad J_hA_h=E_h,\qquad
 P_hJ_h=\operatorname{diag}(\rho_h),qquad
 J_hP_h=\rho_h^{pc}E_h.
\]

Weighted conditional expectations give `E_hu -> u` strongly in `H`, while
(3.1) gives `J_hP_hu -> u` for every fixed `u in H`.  This is pointwise strong
convergence, not operator-norm convergence: `E_h-I` has norm one whenever the
cellwise-constant subspace is proper.

For the Mosco statement, freeze the varying-space convergence convention:

- `v_h -> u` strongly means `J_hv_h -> u` strongly in `H`;
- `v_h -> u` weakly means `J_hv_h -> u` weakly in `H`.

The asymptotic norm equivalence above makes these definitions compatible with
the discrete norms.  The liminf must hold for every weakly convergent
sequence, and recovery must supply one strongly convergent sequence for every
`u in H`.

## 4. Consistency lemmas to freeze

Let `kappa=gamma/d`, let `y_{i+1/2}=ell+(i+1)h`, and put

\[
 s_i=\Phi'(y_{i+1/2})h=\Delta_i.
\]

For the quadratic OU potential, direct algebra gives

\[
 \frac{h c_{i+1/2}}{d\pi(y_{i+1/2})}
 =\frac{g_h}{C}
   e^{-\kappa h^2/8}
   \frac{s_i}{2\sinh(s_i/2)},
 \tag{4.1}
\]

where the last factor is one at `s_i=0`.  Composite midpoint consistency on a
fixed interval gives `g_h/C=1+O(h^2)`.  Since `sup_i |s_i|=O(h)`, there exist
`h_0>0` and a finite fixed-box constant `K_edge` such that, for
`0<h<=h_0`, (4.1) yields

\[
 \sup_i\left|
 \frac{h c_{i+1/2}}{d\pi(y_{i+1/2})}-1
 \right|\le K_{\rm edge}h^2.
 \tag{4.2}
\]

The same Taylor argument, with the strictly positive lower bound of `pi` on
the fixed box, gives a possibly different constant `K_mass` in (3.1).  It
also gives only

\[
 \left\|\frac{\pi_h^{pc}}{\pi}-1\right\|_{L^\infty(I)}=O(h),
 \qquad \pi_h^{pc}|_{C_i}=m_i/h.
 \tag{4.3}
\]

For an auditable derivation rather than a bare Taylor assertion, define

\[
 F_h(a)=\frac1h\int_{-h/2}^{h/2}
        e^{-at-\kappa t^2/2}\,dt,\qquad
 a_i=\kappa(x_i-\mu),qquad
 w_i=\frac{e^{-\Phi(x_i)}}{\sum_j e^{-\Phi(x_j)}}.
\]

Then the following identities are exact:

\[
 \frac{g_h}{C}=\sum_iw_iF_h(a_i),
 \qquad
 \rho_{h,i}=\frac{F_h(a_i)}{\sum_jw_jF_h(a_j)}.
 \tag{4.4}
\]

Uniformly for `a` in the fixed compact range,

\[
 F_h(a)=1+\frac{a^2-\kappa}{24}h^2+O(h^4),
 \tag{4.5}
\]

which proves (3.1).  For the centre-to-centre interval around face
`y_{i+1/2}`, put `a_hat_i=kappa*(y_{i+1/2}-mu)` and
`G_{h,i}=F_h(a_hat_i)`.  Its continuum interpolation coefficient is

\[
 \frac d{h^2}\int_{x_i}^{x_{i+1}}\pi
 =\frac{d\pi(y_{i+1/2})}{h}G_{h,i}.
\]

Thus the exact edge comparison ratio is

\[
 \lambda_{h,i}
 =\frac{c_{i+1/2}}
 {d h^{-2}\int_{x_i}^{x_{i+1}}\pi}
 =\frac{E_{h,i}}{G_{h,i}},
 \qquad
 E_{h,i}=\frac{h c_{i+1/2}}{d\pi(y_{i+1/2})},
 \tag{4.6}
\]

and (4.1), (4.5) give `max_i|lambda_{h,i}-1|=O(h^2)`.
Cell-mass second order, edge-ratio second order, and piecewise-density first
order must not be conflated.

## 5. Interpolant and liminf candidate

For `v_h in H_h`, define `I_hv_h` to be linear between adjacent centres and
constant on `[ell,x_0]` and `[x_{N-1},r]`.  Then

\[
 \mathfrak a(I_hv_h,I_hv_h)
 =\sum_{i=0}^{N-2}
 \frac{d(v_{i+1}-v_i)^2}{h^2}
 \int_{x_i}^{x_{i+1}}\pi(x)\,dx.
 \tag{5.1}
\]

The exact ratio (4.6) implies that, after reducing `h_0` if necessary, there
is a separate constant `K_cmp` such that

\[
 (1-K_{\rm cmp}h^2)\mathfrak a(I_hv_h,I_hv_h)
 \le \mathfrak a_h(v_h,v_h)
 \le(1+K_{\rm cmp}h^2)\mathfrak a(I_hv_h,I_hv_h).
 \tag{5.2}
\]

Put `pi_min=min_I pi>0` and `pi_max=max_I pi`.  If
`delta_i=v_{i+1}-v_i`, the two half-cell pieces adjacent to one interior edge
contribute at most `pi_max*h*|delta_i|^2/12` to the squared reconstruction
difference.  Equation (4.2) gives
`c_{i+1/2}>=d*pi_min/(2h)` for sufficiently small `h`.  Hence

\[
 \|I_hv_h-J_hv_h\|_H^2
 \le \frac{\pi_{\max}}{6d\pi_{\min}}
       h^2\mathfrak a_h(v_h,v_h).
 \tag{5.3}
\]

Now fix an arbitrary sequence `h_n -> 0` and `v_n in H_{h_n}` such that
`J_{h_n}v_n` converges weakly to `u` in `H`.  Set

\[
 L=\liminf_{n\to\infty}\mathfrak a_{h_n}(v_n,v_n).
\]

If `L=infinity`, the liminf inequality is immediate.  Otherwise pass to a
subsequence attaining the finite liminf.  Weak convergence already bounds
`J_{h_n}v_n` in `H`; (3.1) therefore bounds `v_n` in `H_{h_n}`.  Put
`w_n=I_{h_n}v_n`.  Equation (5.3) gives

\[
 \|w_n-J_{h_n}v_n\|_H\longrightarrow0,
\]

while the lower comparison in (5.2) bounds `w_n` in `H1(I)`.  After a further
subsequence, `w_n` converges weakly in `H1(I)`.  The continuous embedding into
`H`, the strong difference above, and uniqueness of the weak `H` limit identify
that limit as `u`; in particular `u in H1(I)`.  Weak lower semicontinuity gives

\[
 \mathfrak a(u,u)
 \le\liminf_n\mathfrak a(w_n,w_n)
 \le\liminf_n\mathfrak a_{h_n}(v_n,v_n)=L,
 \tag{5.4}
\]

where the last comparison uses (5.2) and boundedness of the selected energies,
so the `K_cmp*h_n^2` defect vanishes.  This establishes the candidate liminf
for every weakly convergent sequence, conditional on the consistency estimates
above.

## 6. Recovery candidate and the real boundary order

For $u\in C^3([\ell,r])$, take `v_h=S_hu`.  Then `J_hv_h -> u` strongly
in `H`, (3.1) gives norm consistency, and the uniform centred-difference and
conductance estimates give, with `f=d*pi*|u'|^2`,

\[
 \mathfrak a_h(v_h,v_h)
 =h\sum_{j=1}^{N-1}f(\ell+jh)+O_u(h^2).
\]

The composite trapezoidal formula therefore gives

\[
 \mathfrak a_h(v_h,v_h)\longrightarrow\mathfrak a(u,u).
 \tag{6.1}
\]

The generic leading error is nevertheless first order:

\[
 \mathfrak a_h(v_h,v_h)=\mathfrak a(u,u)
 -\frac h2d\{\pi(\ell)|u'(\ell)|^2
             +\pi(r)|u'(r)|^2\}+O_u(h^2).
 \tag{6.2}
\]

The first-order term records the two boundary half cells omitted by the
centre-to-centre gradient intervals; it is not a Neumann condition on the form
domain.  Only when both endpoint derivatives vanish does this term cancel.
Equation (6.1), not a generic second-order rate, is what recovery requires.

For arbitrary $u\in H^1(I)$, choose $u^k\in C^\infty([\ell,r])$ with

\[
 \|u^k-u\|_H^2+
 \mathfrak a(u^k-u,u^k-u)\longrightarrow0.
\]

For each `k`, let `v_h^k` be the centre samples of `u^k`.  Choose decreasing
thresholds `eta_k -> 0` such that, whenever `h<=eta_k`,

\[
 \|J_hv_h^k-u^k\|_H\le k^{-1},\qquad
 |\mathfrak a_h(v_h^k,v_h^k)-\mathfrak a(u^k,u^k)|\le k^{-1}.
\]

Select `k(h)->infinity` with `h<=eta_{k(h)}` and put
`v_h=v_h^{k(h)}`.  Then `J_hv_h -> u` strongly in `H` and

\[
 \limsup_{h\downarrow0}\mathfrak a_h(v_h,v_h)
 \le\mathfrak a(u,u).
 \tag{6.3}
\]

This is the candidate recovery sequence with its double-index quantifiers
made explicit.

## 7. Candidate theorem and acceptance boundary

Conditional on the elementary fixed-box estimates (3.1), (4.2), (4.3), (5.2),
and (5.3), the preceding arbitrary-sequence liminf and diagonal recovery
arguments establish generalized Mosco convergence of the **ideal analytic**
one-dimensional free cell-centred OU forms to the restricted reflecting OU
form, with strong and weak convergence defined through `J_h`.

There is also a direct conditional resolvent argument that avoids silently
assuming a functional-calculus theorem.  Let $\mathcal L$ and $\mathcal L_h$
denote the nonnegative self-adjoint operators associated with `mathfrak a` and
`mathfrak a_h`, respectively.  Fix `lambda>0` and `f in H`, and let

\[
 u_h=(\mathcal L_h+\lambda)^{-1}P_hf.
\]

It uniquely minimizes

\[
 \mathfrak a_h(v,v)+\lambda\|v\|_{H_h}^2
 -2\langle P_hf,v\rangle_{H_h}.
 \tag{7.1}
\]

Coercivity bounds `u_h`.  The exact identity `P_h=J_h^*`, the liminf result,
and recovery for the continuum minimizer identify every weak cluster point
with $u=(\mathcal L+\lambda)^{-1}f$.  Comparing the minimum values from both
directions then gives convergence of the norms and hence

\[
 J_h(\mathcal L_h+\lambda)^{-1}P_hf
 \longrightarrow(\mathcal L+\lambda)^{-1}f
 \quad\text{strongly in }H.
 \tag{7.2}
\]

This variational outline still needs a fresh line-by-line audit before (7.2)
is accepted.  Moreover, (7.2) alone does not establish the uniform-in-time
convergence of $\mathcal L_h^r e^{-t\mathcal L_h}$ for `r=0,1,2`; that later
bridge still needs an explicit varying-space functional-calculus theorem or a
self-contained resolvent/rational-approximation argument.

This note does not yet mark that theorem accepted.  Before promotion it needs:

1. a fresh line-by-line independent mathematical audit of the repaired bytes,
   including the real/complex convention, arbitrary-sequence liminf,
   double-index recovery, and variational resolvent step;
2. explicit adoption of `P_h=P_h^adj` and the `J_h`-based strong/weak
   definitions in the C1 contract, with the corresponding data approximation;
3. a hash-bound gauge/application layer whose resulting outward intervals
   contain the ideal analytic member on every promoted finite grid, plus a
   proof that F0 encloses that member without treating unrelated interval
   centres as exact; and
4. frozen constants or a clearly qualitative fixed-box existence statement
   for every estimate used above.

Even an accepted version would cover only one free one-dimensional
cell-centred reflecting axis.  Complete C1 additionally requires the relative
OU axis, periodic diffusion, tensorization, vertex-dual alignment, the finite
box/control family, sharp-contact killing and its physical-volume cell
averages, and the functional-calculus bridge to the requested positive-time
observables.  C2, C3, root transfer, positive-budget science, F0, and release
remain outside this note.
