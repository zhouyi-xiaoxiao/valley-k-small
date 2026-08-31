# Continuum C1 SG manufactured-form diagnostic: round 1

Date: 2026-07-17

Status: **PASS SINGLE-AXIS NEUTRAL MANUFACTURED DIAGNOSTIC / 8 MUTATION SENTINELS PASS / HOLD C1 MOSCO / NOT AN INDEPENDENT GO**

## Exact reviewed bytes

- fixture generator SHA-256:
  `7695a29fe8903ed2fffbc268c8924d09985c34baf52046d981824f0f14963085`;
- static/recomputation tests SHA-256:
  `968d398842907ecd62e15e64d90e3aebd9cd43c015b6dbc70d725be34a49101e`;
- adversarial tests SHA-256:
  `8903426df2afcde016f2c5f74038c928fdcc9a46f8d4f761bcc4cf47d89cc759`;
- result artifact SHA-256:
  `d5acdad670656cccc974d40f56bac33292a1ae7a462acedb7588eb572147b9cc`.

The local baseline is `py_compile` PASS, Ruff PASS, 12/12 static tests PASS,
8/8 mutation-sentinel tests PASS, and 20/20 combined tests PASS.  The fixture
reads no control, killing, budget, root, peak, or basin result.  Its receipt is
`PASS_NEUTRAL_MANUFACTURED_FIXTURE_ONLY_C1_MOSCO_STILL_OPEN`.

Three parallel read-only reviews examined the mathematics, production API,
and adversarial surface.  They materially changed the fixture, but they ran
inside the same local continuation and therefore do not count as a fresh
independent executor or a C1 acceptance.

## Exact one-dimensional object

The tested physical axis is the cell-centred reflecting midpoint coordinate
on the frozen base box.  With axis diffusion `d_z=D/2`, the dimensionless OU
potential is

\[
 \Phi(z)=\frac{\gamma(z-\bar z)^2}{D}
        =\frac{\gamma(z-\bar z)^2}{2d_z}.
\]

For cell width `h`, centres `z_i`, and
`B(s)=s/(exp(s)-1)`, the independently reconstructed rates, masses and edge
conductances are

\[
 q_{i,i+1}=\frac{d_z}{h^2}B(\Phi_{i+1}-\Phi_i),\qquad
 \widetilde m_i=h e^{-\Phi_i},
\]

\[
 g_h=\frac{\int_I\pi(z)\,dz}{\sum_i\widetilde m_i},\qquad
 m_i=g_h\widetilde m_i,
\]

\[
 c_{i+1/2}=m_iq_{i,i+1}=m_{i+1}q_{i+1,i},\qquad
 \mathfrak a_h(u,u)=\sum_i c_{i+1/2}(u_{i+1}-u_i)^2.
\]

Each production stationary-mass and forward/reverse conductance interval
contains the independently evaluated 256-bit MPFR value.  The fixture does
not use independent interval centres as exact truths: those centres need not
retain exact detailed balance even when the two outward intervals overlap.

The gauge target is the restricted full-space Gaussian mass on the fixed box,
not an automatic normalization to one.  Its binary64 export rounds to one
because the omitted tail is below binary64 resolution, while the 256-bit
quantity used by the calculation remains strictly less than one.

## Identification-map boundary

The fixture now freezes its own projection unambiguously as

\[
 (P_h^{\rm avg}u)_i=
 \frac{\int_{C_i}u\pi}{\int_{C_i}\pi}.
\]

Thus `P_h J_h=I` is exact for piecewise constants, while weighted adjointness
is only asymptotic because `m_i` is not literally `integral_C_i pi`.  The
alternative

\[
 (P_h^{\rm adj}u)_i=m_i^{-1}\int_{C_i}u\pi
\]

has exact adjointness but only asymptotic `P_h J_h=I`.  Either can support a
varying-Hilbert-space proof, but the complete C1 contract has not yet selected
and proved one.  The artifact therefore records
`c1_contract_map_choice_closed=false`.

## Numerical findings and the boundary-order correction

The production-box table uses seven frozen grids from 17 through 1025 cells,
closed-form Gaussian polynomial moments, and exact weighted cell averages.
On the last pair it observes:

- about order 2 for energy and norm-identification errors;
- about order 1 for the `J_h P_h` projection error; and
- order `1.09061` for the full-cell density-ratio error.

At 1025 cells,

\[
 \left\|\pi_h^{\rm pc}/\pi-1\right\|_\infty
 =0.13074234611923943.
\]

This is still too large to support a C1 promotion.  More importantly, the
apparent order-2 energy table is not the generic reflecting-form rate.  The
form domain is weighted `H1`; Neumann traces constrain the operator domain,
not every form-domain function.  For a generic smooth function,

\[
 \mathfrak a_h(u_h,u_h)=\mathfrak a_I(u,u)
 -\frac h2 d_z\{\pi(\ell)|u'(\ell)|^2
                 +\pi(r)|u'(r)|^2\}+O(h^2).
\]

The frozen physical box has a linear-test boundary coefficient of only
`5.139886785834496e-21`, so accessible grids mask the asymptotic order-1 term.
The artifact now labels this as pre-asymptotic rather than promoting a false
second-order theorem.

An exact flat-density sentinel on `[-1,1]` makes the missing boundary half
cells visible.  For `pi=1/2`, `d=1`, and `u(x)=x`, it proves on every frozen
power-of-two grid

\[
 E_h=1-h/2,\qquad E-E_h=h/2,
\]

\[
 \|u\|_H^2-\|u_h\|_{H_h}^2=h^2/12,
 \qquad \|J_hP_hu-u\|_H^2=h^2/12.
\]

This gives exact orders 1, 2, and 1 respectively.  A separate cubic fixture
has zero derivatives at both physical-box endpoints, so its observed second
order is consistent with the boundary-term cancellation and is not used to
describe the full form domain.

## Adversarial mutations reproduced

The eight-test attack layer confirms that the diagnostic exposes:

1. reversal of the target potential sign and factors `1/2` or `2` in its
   scale, even after total-mass gauging;
2. interchange of `B(delta Phi)` and `B(-delta Phi)`;
3. retention of raw masses instead of the declared restricted-mass gauge;
4. point sampling substituted for the exact weighted cell projection;
5. interchange of the two possible projection denominators;
6. use of `D` instead of the midpoint-axis diffusion `D/2`;
7. directed-edge factor-of-two errors and an erroneous reflecting wrap; and
8. attempted scope promotion after deleting nonlinear coverage.

These are mutation sentinels, not a general semantic verifier.  Full C1 still
needs a frozen three-axis alignment vector, relative-coordinate and periodic
fixtures, at least one mixed/non-diagonal form, vertex-dual endpoint tests,
and sharp-contact cell-average attacks.

## Proof route opened, not closed

For the fixed one-dimensional free OU form, a credible Mosco sublemma can now
be pursued.  Define `I_h v_h` to be linear between adjacent cell centres and
constant on the two boundary half cells.  The exact quadratic-potential SG
identity gives, uniformly on a fixed box,

\[
 \frac{h c_{i+1/2}}{d_z\pi(y_{i+1/2})}=1+O(h^2).
\]

Consequently one should prove a two-sided energy comparison between
`a_h(v_h,v_h)` and `a_I(I_hv_h,I_hv_h)`, together with

\[
 \|I_hv_h-J_hv_h\|_{L^2(\pi)}^2
 \le C h^2\mathfrak a_h(v_h,v_h).
\]

Compactness and weak lower semicontinuity would then give the liminf, while
centre samples of smooth functions plus an `H1` density/diagonal argument
would give recovery.  The constants, map bounds, weak-convergence definition,
and chosen `P_h` still have to be written and independently audited before
even this one-dimensional free-form sublemma can be marked proved.

## Unchanged HOLD boundary

This round does not establish arbitrary-sequence liminf or recovery, all
declared alignments, the tensor product, periodic wrapping, vertex half
volumes, sharp-contact killing consistency, actual controls, strong
resolvent/functional-calculus convergence, positive-time observables, any C2
rate, box exhaustion, root transfer, F0, or release eligibility.  Complete C1
and PRR submission remain HOLD; positive-budget scientific values were not
read.
