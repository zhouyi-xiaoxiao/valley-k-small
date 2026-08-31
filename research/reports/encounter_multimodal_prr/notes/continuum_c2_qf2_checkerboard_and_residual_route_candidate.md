# QF2 checkerboard obstruction and regular-solution residual route

Date: 2026-07-17

Status: **EXACT STANDARD-TENSOR-Q1 ALL-PAIR OBSTRUCTION PROVED / REGULAR-
SOLUTION RESIDUAL ROUTE CANDIDATE / FREE RESIDUAL AND SECTOR H2 PREMISES OPEN /
C2 FALSE / C3 FALSE**

## 0. Purpose, predecessor, and nonclaim boundary

The Round-7 note
`continuum_c2_quantitative_positive_time_route_candidate.md` is retained at
its audited SHA-256
`25119e492cc8714e0804dded9bd4921070062309f441a96b3e0878c87ffa0314`.
It correctly labelled QF1--QF2 and the complex-sector estimate as open.  Its
QF2 Eq. (4.4), however, left the reconstruction/flux mechanism unspecified.
This successor attacks the most natural implementation: the standard
tensor-product conforming `Q1` interpolant together with an all-discrete-pairs
`O(h)` comparison to the lumped finite-volume graph form.

That implementation is false.  An exact checkerboard family gives a defect of
order `h^-2`, whereas the proposed right-hand side is only order `h^-1` after
normalization.  The failure is transverse mass lumping, not the sharp contact
indicator.

This note therefore replaces the critical path

```text
all-pairs vanishing form defect
  -> abstract Strang perturbation
```

by the narrower candidate

```text
one-sided residual on a regular continuum resolvent solution
  -> discrete sector stability
  -> reconstructed complex-sector resolvent rate
  -> the already audited positive-time Dunford transfer.
```

The exact counterexample does not refute every conforming reconstruction,
frequency-filtered or form-preserving maps, mass-lumped reconstructed forms,
or one-sided residual consistency.  The replacement route is not yet proved.
No production source, control, budget, result, root, or release payload was
used to select it.

## 1. The all-pairs claim under attack

Let the mesh energy norm be

\[
 \|v_h\|_{1,h}^2=\|v_h\|_h^2+
                    \mathfrak a_h(v_h,v_h).
 \tag{1.1}
\]

For the standard nodal tensor-product `Q1` interpolant `I_h`, the natural
all-pairs realization of Round-7 QF2 would be

\[
 \left|\mathfrak a_h(u_h,v_h)
  -\mathfrak a(I_hu_h,I_hv_h)\right|
 \le C h\|u_h\|_{1,h}\|v_h\|_{1,h}
 \tag{1.2}
\]

with one mesh-independent `C`.  In one dimension the graph energy and the
piecewise-linear continuum energy can agree exactly.  Equation (1.2) assumes
that this exactness tensorizes with a vanishing defect.  It does not.

## 2. Exact periodic checkerboard calculation

Take the unit `d`-torus, an even integer `N`, `h=N^-1`, constant density, and
unit diffusion.  Index the periodic vertices by `j in Z_N^d` and define

\[
 v_j=(-1)^{j_1+\cdots+j_d}.
 \tag{2.1}
\]

With every undirected edge counted once,

\[
 \|v\|_h^2=h^d\sum_j|v_j|^2=1,
 \qquad
 \mathfrak a_h(v,v)=h^{d-2}\sum_j\sum_{k=1}^d
   |v_{j+e_k}-v_j|^2=4d h^{-2}.
 \tag{2.2}
\]

On a mesh cube, put `xi_k=(x_k-j_kh)/h`.  Multilinearity and the alternating
vertex signs give the exact factorization

\[
 I_hv(x)=v_j\prod_{k=1}^d(1-2\xi_k).
 \tag{2.3}
\]

Since

\[
 \int_0^1(1-2\xi)^2d\xi=\frac13,
 \tag{2.4}
\]

one obtains

\[
 \|I_hv\|_{L^2}^2=3^{-d},
 \qquad
 \mathfrak a(I_hv,I_hv)
 =4d\,3^{-(d-1)}h^{-2}.
 \tag{2.5}
\]

Thus the exact defect is

\[
 D_h=4d\left(1-3^{-(d-1)}\right)h^{-2}.
 \tag{2.6}
\]

Substituting `u_h=v_h=v` into Eq. (1.2) forces

\[
 C\ge C_{\min}(d,h)
 =\frac{4d(1-3^{-(d-1)})}{h(h^2+4d)}
 \sim\frac{1-3^{-(d-1)}}h.
 \tag{2.7}
\]

No mesh-independent constant exists for `d>=2`.

For the physical quotient dimension `d=3`, the exact values are

\[
 \mathfrak a_h(v,v)=12h^{-2},
 \qquad \|I_hv\|_2^2=1/27,
 \qquad \mathfrak a(I_hv,I_hv)=\frac4{3}h^{-2},
 \tag{2.8}
\]

\[
 D_h=\frac{32}{3}h^{-2},
 \qquad C_{\min}(3,h)\sim\frac8{9h}.
 \tag{2.9}
\]

## 3. The actual mixed Neumann-periodic alignment also fails

The periodic torus is the cleanest exact fixture, but the obstruction is not
an artefact of making every axis periodic.  Consider the declared
vertex-dual/vertex-dual/periodic alignment on

\[
 [0,1]\times[0,1]\times\mathbb T_1.
 \tag{3.1}
\]

On each Neumann factor use `N+1` vertices, endpoint masses `h/2`, interior
masses `h`, and the alternating nodal values `(-1)^j`.  On the periodic factor
use the same even-`N` checkerboard.  In every one-dimensional factor:

\[
 \|v\|_{\rm lumped}^2=1,
 \quad \|I_hv\|_{L^2}^2=1/3,
 \quad \mathfrak a_h(v,v)=\mathfrak a(I_hv,I_hv)=4h^{-2}.
 \tag{3.2}
\]

The endpoint half masses are exactly what makes the first identity hold on a
Neumann factor.  Tensorization then gives the same Eqs. (2.2)--(2.9): each
continuum directional energy carries a consistent-mass factor `1/3` from each
spectator axis, while the finite-volume graph form carries lumped spectator
masses equal to one.

More generally, for asynchronous even grids with spacings `h_k`, the two
energies are

\[
 \mathfrak a_h(v,v)=4\sum_{k=1}^d h_k^{-2},
 \qquad
 \mathfrak a(I_hv,I_hv)
 =4\,3^{-(d-1)}\sum_{k=1}^d h_k^{-2}.
 \tag{3.3}
\]

Hence the declared `h=max_k h_k` still makes the required all-pairs constant
diverge at least like `1/h` as every axis refines.  One failing declared
alignment is enough to reject standard tensor `Q1` as the uniform QF2
implementation.  No statement about the cell-centred alignment is needed for
that rejection.

## 4. Sharp boundary of the obstruction

The exact result proves:

```text
standard nodal tensor-Q1 + exact continuum integration
+ all discrete pairs + discrete H1 norm + O(h) defect = false.
```

It also disproves the informal inference that a one-dimensional exact energy
identity retains a vanishing all-pairs defect after finite tensorization.

It does not disprove:

- the separate `L2` reconstruction estimate
  `||I_hv_h-J_hv_h|| <= C h ||v_h||_1h`;
- uniform energy equivalence between the graph form and the `Q1` form;
- a mass-lumped quadrature identity for a reconstructed form;
- a different commuting, filtered, or form-preserving reconstruction;
- consistency when one argument is a projection of a regular continuum
  function; or
- a direct control-volume flux residual.

For the constant periodic model, the sharp unconditional tensor-`Q1` energy
comparison is only

\[
 3^{-(d-1)}\mathfrak a_h(v,v)
 \le \mathfrak a(I_hv,I_hv)
 \le \mathfrak a_h(v,v),
 \tag{4.1}
\]

and the checkerboard attains the lower constant.  Uniform equivalence is
enough for coercivity but not for Eq. (1.2).

## 5. Revised setting and exact residual identity

Return to the fixed physical quotient box and one admissible control `c`.
Let `A_c>=0` and `A_{h,c}>=0` be the continuum and ideal discrete operators,
with forms

\[
 \mathfrak a_c=\mathfrak a_{\rm free}+B\mathfrak k_c,
 \qquad
 \mathfrak a_{h,c}=\mathfrak a_{h,\rm free}+B\mathfrak k_{h,c}.
 \tag{5.1}
\]

Use the exact adjoint maps

\[
 J_h:H_h\to H=L^2(\pi dx),
 \qquad P_h=J_h^*:H\to H_h.
 \tag{5.2}
\]

Fix `sigma>0` and put `A_{c,sigma}=A_c+sigma I` and
`A_{h,c,sigma}=A_{h,c}+sigma I`.  For a complex sector parameter `lambda`,
let

\[
 u=(A_{c,\sigma}+\lambda)^{-1}f,
 \qquad
 u_h=(A_{h,c,\sigma}+\lambda)^{-1}P_hf.
 \tag{5.3}
\]

Choose the comparison value

\[
 w_h=P_hu.
 \tag{5.4}
\]

This choice removes a potential mass-consistency error exactly:

\[
 \langle P_hu,v_h\rangle_h=\langle u,J_hv_h\rangle_H.
 \tag{5.5}
\]

Assuming `u` lies in the operator domain of the free part, define the one-sided
free residual

\[
 R_{h,\rm free}(u;v_h)
 =\mathfrak a_{h,\rm free}(P_hu,v_h)
  -\langle P_hA_{\rm free}u,v_h\rangle_h.
 \tag{5.6}
\]

Similarly define

\[
 R_{h,\rm kill}(u;v_h)
 =\mathfrak k_{h,c}(P_hu,v_h)
  -\langle P_h(V_cu),v_h\rangle_h.
 \tag{5.7}
\]

Applying `P_h` to the continuum resolvent equation and using Eq. (5.5) gives
the exact error equation

\[
 \mathfrak b_{h,c,\lambda}(u_h-P_hu,v_h)
 =-R_{h,\rm free}(u;v_h)-B R_{h,\rm kill}(u;v_h),
 \tag{5.8}
\]

where

\[
 \mathfrak b_{h,c,\lambda}(p,q)
 =\mathfrak a_{h,c}(p,q)+(\sigma+\lambda)\langle p,q\rangle_h.
 \tag{5.9}
\]

Equation (5.8) compares only a regular continuum solution with the discrete
scheme.  It makes no all-discrete-pairs `Q1` claim.

## 6. Killing residual without a discrete L4 inequality

Let `V_{h,c}` be the exact physical-volume cell average and

\[
 \rho_h^{pc}=M^\pi_h/\pi_h,
 \qquad K_{h,c}^{pc}=V_{h,c}^{pc}/\rho_h^{pc}.
 \tag{6.1}
\]

The exact reconstructed form identity gives

\[
 \mathfrak k_{h,c}(P_hu,v_h)
 =\int K_{h,c}^{pc}(J_hP_hu)\overline{J_hv_h}\,\pi dx,
 \tag{6.2}
\]

whereas adjointness gives

\[
 \langle P_h(V_cu),v_h\rangle_h
 =\int V_cu\overline{J_hv_h}\,\pi dx.
 \tag{6.3}
\]

Therefore

\[
 \begin{split}
 |R_{h,\rm kill}(u;v_h)|
 &\le \bigl[
  \|K_{h,c}^{pc}\|_\infty
  \|J_hP_hu-u\|_{L^2(\pi)}\\
 &\qquad
  +\|K_{h,c}^{pc}-V_c\|_{L^2(\pi)}
   \|u\|_{L^\infty}
 \bigr]\|J_hv_h\|_{L^2(\pi)}.
 \end{split}
 \tag{6.4}
\]

Suppose source-bound map and geometry lemmas prove

\[
 \|J_hP_hu-u\|_2\le C_Ph\|u\|_{H^1},
 \qquad \|K_{h,c}^{pc}\|_\infty\le C_K,
 \tag{6.5}
\]

\[
 \|K_{h,c}^{pc}-V_c\|_2
 \le C_{K,\rm cut}h^{1/2}+C_{K,\rm map}h.
 \tag{6.6}
\]

In quotient dimension three, `H2` embeds continuously into `L-infinity` on
the fixed box.  Uniform boundedness of `J_h` then yields

\[
 |R_{h,\rm kill}(u;v_h)|
 \le C_{\rm kill}h^{1/2}\|u\|_{H^2}\|v_h\|_{1,h}.
 \tag{6.7}
\]

This is the key route change.  Only the continuum resolvent solution needs
`L-infinity` control.  The arbitrary discrete test needs only its `L2` norm,
so QF1's discrete `L4` estimate is not required for Eq. (6.7).  No derivative
of the sharp indicator is taken.

Equations (6.5)--(6.6) remain source-bound obligations.  The Round-7 neutral
cut-layer fixture is not a production constant, and the Round-8 neutral
symbolic fixture is not a production member binding.

## 7. Free residual obligation replacing all-pairs QF2

The revised free obligation is the one-sided estimate

\[
 |R_{h,\rm free}(u;v_h)|
 \le C_{\rm free,res}h^\alpha
       \|u\|_{H^2}\|v_h\|_{1,h},
 \qquad \alpha\ge\frac12,
 \tag{7.1}
\]

uniformly over all declared alignment and asynchronous-refinement families.
An `O(h)` estimate is preferred, but `alpha=1/2` is sufficient for the
conservative target.

The proposed proof mechanism is control-volume integration of
`A_free u`, followed by face-wise comparison of exact weighted fluxes with the
ideal Scharfetter--Gummel flux applied to `P_hu`.  It must handle separately:

- cell-centred Neumann boundary half strips;
- vertex-dual endpoint half volumes;
- periodic base and half-cell shifts;
- the one global gauge and the quantitative `rho` defect;
- asynchronous tensor spacings without importing an aspect-ratio-dependent
  constant; and
- exact spectator-axis mass factors.

Equation (7.1) is open.  In particular, it must be checked whether `H2`
regularity alone controls the required face-flux traces for the exact SG
stencil.  If a proof needs `H^{2+s}` or an operator-domain graph norm, that
stronger regularity must be stated and propagated into the sector constant;
it may not be silently obtained from positive time before the resolvent rate
itself has been proved.

## 8. Complex-sector regularity and stability premises

Let

\[
 \Lambda_\theta
 =\{\lambda\ne0:|\arg\lambda|\le\pi-\theta\},
 \qquad 0<\theta<\pi/2.
 \tag{8.1}
\]

The continuum premise is a control-uniform estimate on the fixed box,

\[
 \|(A_{c,\sigma}+\lambda)^{-1}f\|_{H^2}
 \le C_{\rm reg}(\lambda,L)\|f\|_2,
 \qquad \lambda\in\Lambda_\theta,
 \tag{8.2}
\]

for the weighted mixed Neumann-periodic realization with bounded sharp
zero-order killing.  The precise polynomial growth or decay of
`C_reg(lambda,L)` must be proved.

The discrete premise is rotated sector coercivity: for a phase
`omega(lambda)` of unit modulus,

\[
 \operatorname{Re}\{\omega(\lambda)
  \mathfrak b_{h,c,\lambda}(v_h,v_h)\}
 \ge c_\theta\bigl[
  \mathfrak a_{h,c}(v_h,v_h)
  +(\sigma+|\lambda|)\|v_h\|_h^2\bigr],
 \tag{8.3}
\]

with `c_theta>0` independent of the mesh, alignment, and declared control.
Self-adjoint nonnegative discrete forms make this plausible, but the exact
contour convention and constants must be frozen rather than inferred from a
real-shift calculation.

Combining Eqs. (5.8), (6.7), (7.1), and (8.3) would give

\[
 \|u_h-P_hu\|_{1,h}
 \le C_\theta(\lambda,L)h^{1/2}\|f\|_2.
 \tag{8.4}
\]

The reconstruction triangle

\[
 \|J_hu_h-u\|_2
 \le \|J_h(u_h-P_hu)\|_2+
      \|J_hP_hu-u\|_2
 \tag{8.5}
\]

then includes the moving-range complement explicitly and yields the desired
conditional operator-norm estimate

\[
 \left\|
 J_h(A_{h,c,\sigma}+\lambda)^{-1}P_h
 -(A_{c,\sigma}+\lambda)^{-1}
 \right\|_{H\to H}
 \le C_{\rm sec}(\lambda,L)h^{1/2}.
 \tag{8.6}
\]

No compactness-only argument supplies Eq. (8.6); every constant in
Eqs. (6.5)--(8.3) must be source-bound.

## 9. Positive-time transfer and sign convention

The Round-7 Dunford step was already audited in its `z-A_{sigma}` convention.
Equation (8.6) is written in the equivalent `A_sigma+lambda` convention, with
`lambda=-z`.  A final proof must perform that substitution explicitly,
preserve the shift factor, and verify the contour orientation.  Once the
resulting `C_sec` has integrable growth, the existing argument gives, for
`r=0,1,2` and `t in [tau,T]` with `tau>0`,

\[
 \sup_{t\in[\tau,T]}
 \|J_hA_{h,c}^re^{-tA_{h,c}}P_h
      -A_c^re^{-tA_c}\|
 \le C_r(\tau,T,L)h^{1/2}.
 \tag{9.1}
\]

Equation (9.1) remains false as a completion flag until Eqs. (6.5)--(8.3) are
proved on accepted source families.  The exponential factor for `tau>0` can
absorb proved polynomial sector growth; it cannot repair a missing sector
estimate or extend the claim to `t=0`.

## 10. Role of QF1 after the route change

The uniform discrete `L4` inequality remains a legitimate and useful theorem
question.  Uniform lumped/consistent mass equivalence, graph/`Q1` energy
equivalence, and the fixed-domain `H1 -> L4` embedding suggest a route that
does not require a vanishing all-pairs form defect.

It is no longer on the critical path for Eq. (6.7).  The regular-solution
residual uses `H2 -> L-infinity` for `u` and only `L2` for the arbitrary
discrete test.  QF1 would become necessary again if one returned to the
all-discrete-pairs killing estimate in Round-7 Eq. (4.5), or for other
nonlinear/discrete-product estimates.

No source-bound QF1 constant is claimed here.  Boundary half cells, weights,
gauge comparability, and asynchronous tensor norm equivalences still require
their own proof.

## 11. Reproducible exact obstruction fixture

The neutral exact-rational fixture consists of:

```text
code/continuum_c2_qf2_checkerboard_obstruction_v1.py
artifacts/data/continuum_c2_qf2_checkerboard_obstruction_v1.json
code/test_continuum_c2_qf2_checkerboard_obstruction_v1.py
```

Its frozen SHA-256 values are:

```text
builder   ca53c6e33c631e115d38d857110d8eaf47a86205d5f3db6ca93529d0b633bdd9
artifact  40f7c0689343eef0aca0b17a2bc95183cbf8fdca073a6d9a0d4ae1fbaa53c9bf
test      039ba8721ab161c694b34c355517b8a960facb19e89048cfdeabbe5f69b96bbb
```

It enumerates `d=1,2,3` and `N=2,4,8,16` with exact fractions.  A separately
implemented polynomial-coefficient integration in the test agrees with the
builder, two clean builds are byte-identical, overwrite is rejected, and the
final suite passes `90/90`.  An independent exact-byte mathematical audit
reports `P0=P1=P2=0`.

The artifact's only promoted fact is the exact checkerboard obstruction to the
standard periodic nodal tensor-`Q1` all-discrete-pairs `O(h)` route.  It keeps
all of the following false:

```text
all QF2 routes refuted
all conforming reconstructions refuted
regular-solution residual route refuted
formal QF2 replacement proved
complete C1
complete C2
complete C3
production evidence
release/submission/science execution
```

The mixed Neumann-periodic extension in Section 3 is a mathematical argument
in this note, not a silently changed claim inside the periodic fixture.

## 12. Honest decision and next proof obligations

The status after this successor is:

```text
standard tensor-Q1 all-pairs O(h) QF2 implementation = REFUTED EXACTLY
separate L2 reconstruction estimate                  = NOT REFUTED
uniform energy equivalence                            = AVAILABLE ROUTE, CONSTANTS OPEN
QF1 discrete L4                                       = OPEN, NOT CRITICAL TO NEW ROUTE
map approximation (6.5)                               = OPEN SOURCE BINDING
source-bound killing defect (6.6)                     = OPEN SOURCE BINDING
one-sided free residual (7.1)                         = OPEN PRINCIPAL LEMMA
complex-sector H2 regularity (8.2)                    = OPEN PRINCIPAL LEMMA
discrete sector coercivity/contour constants (8.3)    = OPEN
complex-sector reconstructed resolvent rate (8.6)     = FALSE AS COMPLETION FLAG
positive-time r=0,1,2 C2 rate                         = FALSE
complete C1/C2/C3 and release                         = FALSE
```

The next mathematical milestone is not another fitted convergence slope.  It
is a proof of the one-sided free residual and the exact sector regularity
package for the declared mixed boundary/alignment families.  Numerical work
may attack face-flux residuals on manufactured `H2` solutions, but it cannot
replace those lemmas.  Production work remains separate: Round 8 did not bind
the eleven symbolic roles or materialize an independent acceptance receipt.

The theorem-first manuscript remains unchanged at seven main pages plus
twenty-four Supplemental pages.  This note corrects the continuum research
path; it is not a manuscript promotion.
