# A sharper explicit lower bound for B0(eps) via the direct (flat) Dyson route

**Status: complete derivation with verified numerical evaluations (2026-08-14).**
**Target file of the baseline being sharpened:** `b0_quantitative_bound.tex` (same directory).
**Manuscript:** `../jpa/encounter_multimodal_jpa.tex` (Theorem B.1 = `thm:mixed-jet`, Appendix A = analytic realizations, Appendix C = full proof and margin inventory).

---

## 0. Summary of the result

The proven baseline threshold is

    B0 >= (2/(3 v_inf T)) * ln(1 + M / (v_* kappa_pi ||q0||_X)),
    M = min(tau*mu1/2, tau^2*mu2/8),

whose anchor value is 3.03e-707 (log10 = -706.5184), destroyed by the weighted-norm
factor ||q0||_{X_pi} = exp[gamma (z0-zbar)^2/(eps^2 D0)] * sqrt(J_perp) ~ e^{1600.5}.

This draft derives, by a **direct Dyson expansion in the flat (forward, probabilistic)
pairing** combined with a **complex-time Cauchy estimate of shrunken, eps-scaled radius
r0**, the new proven bound (Theorem 1 + Corollary 1, Section 8)

    B0 >= B0_new := ln(1 + Mhat / (khat * v_inf * e^Pi)) / (v_eff * (T + r0)),
    v_eff = khat * (1 + delta_v) * v_inf,
    Mhat = min(r0*mu1, r0^2*mu2/2),
    r0 = (eps / (gamma * yhat)) * sqrt(D0 * tau / 2),   yhat = max(|z0-zbar|, max_j |chat_j - zbar|),

in which **no weighted norm appears at all**: `khat` and `e^Pi` are explicit O(1)
constants (at the anchor khat = 1.111659, e^Pi = 1.2958249, delta_v = 0).  The
price is the Cauchy radius r0 ~ eps in place of tau/2 — a polynomial-in-eps
cost replacing the e^{1600} loss.

Evaluations (Sections 9-11, mpmath, verified against the baseline inventory):

    anchor  (eps=0.10, m=2): B0_new = 8.6414719e-15   log10 = -14.063412   (baseline -706.5184)
    point A (eps=0.05, m=2): B0_new = 2.4141087e-54   log10 = -53.617243   (baseline < -2780)
    point B (eps=0.10, m=3): B0_new = 2.5073946e-7    log10 =  -6.6007773

The anchor improvement is 692.5 orders of magnitude.  The remaining gap to the
empirical threshold ~7.6 is dominated by the intrinsic endpoint-slope margin
mu1 = 1.55e-11 (= e^{-30.4} window-opening factor), which any margin-inventory
argument pays.

Asymptotic exponent along the anchor family: log B0_new(eps) = -c_B/eps^2 + O(log(1/eps))
with **c_B = D_L^2/(2 S_*^2) = 0.303757**, replacing the baseline c_B = 16.27681
(of which 16 came from the weighted norm and is now gone, and 0.02695 came from
the v_* factor in the denominator, also gone); the two-point scaling check in
Section 10 confirms the new rate to three digits (39.55 observed vs 39.58
predicted decades between eps = 0.1 and 0.05).

Sections 1-8: derivation.  Sections 9-11: anchor + two secondary evaluations
(numbers produced by the script `b0_dyson_numerics.py`, run log quoted).
Section 12: honest discussion of the weakest steps.

---

## Table of contents

1. Setting, notation, and standing hypotheses
2. Why the baseline pays e^{1600}, and the two pillars of the repair
3. The flat Dyson representation of the observable remainder
4. Lemma 1: pointwise domination of complex-time Gaussian kernels
5. Lemma 2: per-leg kernel data for the three coordinate blocks
6. Lemma 3: node and initial-law penalty absorption (complete squares)
7. Proposition 1: the assembled chain bound for the n-th Dyson term
8. Theorem 1 and Corollary 1: derivative bounds and the new threshold
9. Anchor evaluation (eps = 0.1, m = 2)
10. Secondary point A (eps = 0.05, same geometry)
11. Secondary point B (m = 3, targets (0.8, 1.6, 2.8), eps = 0.1)
12. Honest assessment: weakest steps and remaining conservatism

---

## 1. Setting, notation, and standing hypotheses

We work on the unbounded natural-decay quotient `Q_inf = R_z x R_{r_par} x T_W^{d-1}`
(manuscript Eq. (A.1)), with the free forward operator (A.2)-(A.3)

    L q = -div(b q) + div(D grad q),   D = diag(eps^2 D0/2, 2 eps^2 D0, ..., 2 eps^2 D0),
    b(x) = (-gamma (z - zbar), -gamma r_par, 0, ..., 0),

i.e. the diffusion matrix of the SDE system (C.1)-(C.3): the midpoint Z has
noise eps*sqrt(D0) (FP diffusion coefficient eps^2 D0/2), the longitudinal
relative coordinate has noise 2 eps sqrt(D0) (coefficient 2 eps^2 D0), the
transverse relative block is Brownian on the torus with the same coefficient.
Throughout, x = (z, r_par, r_perp).

Killing field (C.14): K_{B,w,eps} = B V_{w,eps},

    V_{w,eps}(z, r) = W^{-(d-1)} * chi_a(r) * phi_w(z),
    phi_w(z) = sum_j w_j phi_{j,eps}(z),
    phi_{j,eps}(z) = N(z - chat_j ; eps^2 rho^2),   chat_j := mu(t_j),

with `N(u; V) = exp(-u^2/(2V))/sqrt(2 pi V)`, `chi_a` the minimum-image
contact-ball indicator, and mu(t) = zbar + (z0-zbar) e^{-gamma t}.

Initial law (C.4)-(C.6): a product probability density

    q0 = N(z - z0; eps^2 D0/(2 gamma)) x N(r_par - r_par0; eps^2 u0^2) x WN(r_perp - r_perp0; eps^2 Sigma_perp0),

with the standing weighted-space inequalities u0^2 < 4 D0/gamma (and the midpoint
variance equal to the stationary one).  At the anchor r_par0 = 0, r_perp0 = 0,
u0^2 = 2 D0/gamma, Sigma_perp0 = I.

Observables.  With T0(t) = e^{tL} the free (unkilled) forward semigroup and
E0 the law of the unkilled process started from q0,

    G(t)   = <V, e^{tL} q0>       = E0[ V(X_t) ],
    F_B(t) = <V, e^{t(L - B V)} q0> = E0[ V(X_t) exp(-B A_t) ],   A_t := int_0^t V(X_s) ds,

where <.,.> is the FLAT (Lebesgue) pairing of a bounded function against an L^1
density; the second identity is Feynman-Kac for the bounded killing potential BV
(manuscript Eq. (C.26) with the B factored out).  F_B = f_{B,eps,w}/B is exactly
the budget-rescaled Doi density of the baseline proposition.

Norms and margins (identical to the baseline, Eqs. (b0-margins), (b0-constants)):

    v_inf = ||V_{w,eps}||_inf,
    mu2 = min_i min_{U_i} |G''| > 0,   mu1 = min_{I \ union int U_i} |G'| > 0,

for an admissible root-tube system U_1, ..., U_{2m-1} on I = [tau, T].
NOTE: v_* and ||q0||_X are *not used anywhere* in this draft.  kappa_pi = 1 on
Q_inf and never appears either.

Standing hypotheses (all inherited from the baseline proposition, none added):
(H1) the fixed eps has the certified free-clock signature on I (m nondegenerate
maxima, m-1 nondegenerate minima, alternating, no stationary endpoint);
(H2) an admissible root-tube system with margins mu1, mu2 > 0;
(H3) q0 as above (a probability density on Q_inf; membership in X_pi holds and
is used ONLY qualitatively, see Section 3);
(H4) V_{w,eps} bounded, nonnegative, of the product Gaussian-slab form above.

One new (checkable, purely geometric) smallness condition on the Cauchy radius
r0 appears as (R1)-(R3) in Section 8; at all three evaluation points it holds
with large slack.

## 2. Why the baseline pays e^{1600}, and the two pillars of the repair

The baseline chain (Theorem B.1) is: Dyson expansion **in the self-adjoint
representation** on L^2(pi dx), operator bound with every free factor
contractive there, then the observable pairing by Cauchy-Schwarz,

    |<V, (e^{z(L-BV)} - e^{zL}) q0>| <= v_* kappa_pi (e^{B v_inf |z|} - 1) ||q0||_X,

followed by a time-Cauchy estimate on the disk |z - t| <= tau/2.  The
Cauchy-Schwarz step is where the weighted norm ||q0||_{X_pi} = ||q0/pi||_{L^2(pi)}
enters; since q0 is centred z0 = 4 while pi is centred zbar = 0 with variance
O(eps^2), that norm is e^{gamma(z0-zbar)^2/(eps^2 D0)} ~ e^{1600}.  The
weighted pairing is needed there because the *complex-time* free semigroup is
well behaved only in the self-adjoint representation: on flat L^1 or L^infty the
complex-time Ornstein-Uhlenbeck semigroup is not a bounded operator family (the
complexified drift displaces mass by an imaginary amount growing linearly in the
starting point, and the flat operator norm diverges).  This is the known failure
of analyticity of the OU semigroup on Lebesgue spaces, and it is the *only*
reason the baseline retreats to X_pi.

The repair rests on two observations.

**Pillar 1 (flat probabilistic pairing at real time).**  At real time the
remainder needs no weighted norm at all: since 0 <= 1 - e^{-B A_t} and
A_t <= v_inf t pathwise,

    0 <= G(t) - F_B(t) = E0[ V(X_t) (1 - e^{-B A_t}) ] <= (e^{B v_inf t} - 1) G(t),

by expanding the exponential and bounding every interior potential factor by
v_inf while keeping the final V(X_t) exact.  All constants are O(1).  The
whole difficulty is the two *time derivatives* required by the signature
argument.

**Pillar 2 (complex-time Cauchy with an eps-scaled radius).**  Derivatives are
recovered by Cauchy's estimate on a disk |z - t| <= r0, but with r0 chosen
proportional to eps.  The point: the flat-pairing Dyson chains CAN be bounded at
complex time, because every leg of a chain either starts from the initial law q0
or from a potential node V, and both confine the starting point y to an
O(eps)-neighbourhood of an O(1) centre (z0 or a slab centre chat_j).  The
imaginary-displacement penalty of a complex leg of duration zeta is
exp[+(Im e^{-gamma zeta})^2 (y - zbar)^2 / (eps^2 Re v(zeta))] — the e^{1600}
mechanism — but with |Im z| <= r0 = O(eps) the total penalty over any chain is
O(1), *uniformly in the chain order n*, because the per-leg penalties are linear
in the leg durations and the durations sum to |z|.  The Cauchy factors become
r! / r0^r = O(eps^{-r}) instead of r! (2/tau)^r: a polynomial-in-eps price
replacing the exponential one.

A final structural device (Section 3) avoids ever needing *operator* bounds on
flat complex semigroups: the weighted-space theory of Appendix A is kept as a
purely *qualitative* tool (it guarantees that z -> F_B(z) - G(z) is analytic on
the half-plane and that the Dyson series converges to it), while every
*quantitative* estimate is performed on the explicit finite-dimensional complex
Gaussian integrals of the flat representation, which agree with the weighted
pairings by the identity theorem.

---

## 3. The flat Dyson representation of the observable remainder

### 3.1 The remainder and its half-plane analyticity

Define, for complex z with Re z > 0,

    D(z) := <V, (e^{zL} - e^{z(L - BV)}) q0>.

By Proposition A.1 of the manuscript (`prop:supp-analytic`), in the
self-adjoint representation q = pi u the free generator G_sa is nonpositive
self-adjoint on L^2(pi dx), and G_sa - B M_V is self-adjoint and bounded above
(V bounded).  Spectral calculus therefore defines e^{z G_sa} and
e^{z(G_sa - B M_V)} for every Re z > 0, both analytic operator families of
norm <= e^{c Re z} there (c = 0 for the free one); conjugating by the unitary
pi-multiplication gives the analytic families e^{zL}, e^{z(L-BV)} on
X_pi = L^2(pi^{-1} dx).  Since q0 in X_pi (the strict variance inequalities
(C.4)-(C.6)) and the pairing with V in L^2(pi dx) \cap L^inf is continuous,
z -> D(z) is analytic on the open right half-plane {Re z > 0}, and
D(t) = G(t) - F_B(t) for real t > 0.  This is the ONLY use of the weighted
space in this derivation, and it is norm-free: no quantitative constant of the
X_pi theory (in particular neither ||q0||_X nor v_*) is invoked.

### 3.2 The Dyson series and its termwise flat form

On X_pi the Dyson-Phillips series (manuscript Eq. (B.5), conjugated back from
the self-adjoint representation by the unitary q = pi u) converges in operator
norm for every fixed z with Re z > 0:

    e^{z(L-BV)} - e^{zL}
      = sum_{n>=1} (-Bz)^n int_{Delta_n} e^{z(1-s_1)L} V e^{z(s_1-s_2)L} V ... V e^{z s_n L} q0-side ds,

with Delta_n = {1 >= s_1 >= ... >= s_n >= 0}, |Delta_n| = 1/n!.  Pairing with V
and using continuity of the pairing,

    D(z) = - sum_{n>=1} (-B z)^n T_n(z),
    T_n(z) := int_{Delta_n} < V, e^{z(1-s_1)L} V e^{z(s_1-s_2)L} V ... V e^{z s_n L} q0 > ds.       (3.1)

**Flat form of T_n.**  Fix n and s in Delta_n, and write the leg durations

    h_0 = 1 - s_1,  h_1 = s_1 - s_2, ..., h_{n-1} = s_{n-1} - s_n,  h_n = s_n,
    sum_{k=0}^n h_k = 1,  zeta_k := z h_k.

For REAL z = t > 0 the integrand of (3.1) is a composition of positive integral
operators (Mehler kernels of the free process) and positive multiplications, so
by Tonelli it equals the absolutely convergent (n+1)-fold configuration
integral

    C_n(t; s) = int ... int  V(x_{n+1}) p_{zeta_0}(x_{n+1}|x_n) V(x_n) p_{zeta_1}(x_n|x_{n-1})
                  ... V(x_1) p_{zeta_n}(x_1|x_0) q0(x_0) dx_0 ... dx_{n+1},              (3.2)

where p_u(x|y) is the (product) transition density of the free process over
time u.  Probabilistically C_n(t;s) = E0[V(X_{t s_n'}) ... V(X_t)] is the
(n+1)-point free exposure correlation (s' the ordered times); this is the
Feynman-Kac / Markov-property identity and needs only real, positive times.

**Complex continuation of the flat form.**  The free process is Gaussian: each
block of p_u has an explicit Mehler kernel (Section 5) which continues
analytically in u to {Re u > 0}, and for Re z > 0 every leg has Re zeta_k > 0
(durations h_k > 0).  Define C_n(z; s) by (3.2) with the continued kernels.
Lemmas 1-3 below produce a bound

    |C_n(z; s)| <= khat v_inf * ( khat (1+delta_v) v_inf )^n * e^{Pi}   (uniform in s)    (3.3)

valid uniformly for z in each closed disk |z - t| <= r0 subject to conditions
(R1)-(R3); in particular the integral (3.2) converges absolutely, uniformly on
the disk, and z -> C_n(z;s) is analytic there (Fubini/Morera on the dominated
integral, the integrand being jointly measurable and analytic in z pointwise).

**Termwise identity.**  For fixed s, the weighted-pairing integrand of (3.1)
and C_n(z; s) are both analytic on the disk (the former as a finite product of
analytic operator-valued maps paired continuously) and agree for real z in
(t - r0, t + r0) by the Tonelli identity above.  By the identity theorem they
agree on the whole disk.  Integrating over Delta_n (justified by (3.3) and
dominated convergence) gives

    T_n(z) = int_{Delta_n} C_n(z; s) ds,      |T_n(z)| <= (1/n!) v_inf (khat v_inf)^n e^{Pi},

and therefore, summing the series (3.1) — with the exact bookkeeping of the
(n+1) leg factors khat and the (1+delta_v) node inflations deferred to
Proposition 1 —

    |D(z)| <= sum_{n>=1} (B|z|)^n |T_n(z)|
           <= khat v_inf e^{Pi} ( exp( B v_eff |z| ) - 1 ),
    v_eff := khat (1 + delta_v) v_inf.                                                    (3.4)

The remainder of the derivation (Sections 4-7) establishes (3.3) with explicit
khat and Pi, and Section 8 converts (3.4) into derivative bounds and the
threshold.

---

## 4. Lemma 1: pointwise domination of complex-time Gaussian kernels

**Lemma 1 (complex Gaussian domination).**
Let s2 in C with Re s2 > 0 (a complex variance), let m = m_R + i m_I in C, and
define the complex Gaussian kernel value

    N_C(x; m, s2) = (2 pi s2)^{-1/2} exp( -(x - m)^2 / (2 s2) ),   x in R,

with the principal branch of the square root (well defined since Re s2 > 0).
Write w := 1/(2 s2) = a - i b with a = Re w > 0.  Then for every lambda in (0,1):

    |N_C(x; m, s2)| <= kappa(lambda, theta) * g_{sig2}(x - m_R) * exp( P_lam * m_I^2 ),   (4.1)

where theta := arg(s2)  (so tan theta = -b/a... see normalization below),

    g_{sig2}(u) = unit-mass real Gaussian density with variance sig2 = 1 / (2 a (1 - lambda)),
    kappa(lambda, theta) = ( (1 - lambda) * cos theta )^{-1/2},
    P_lam = a * ( 1 + (b/a)^2 / lambda ) = a + b^2/(lambda a).

*Proof.*  |N_C| = |2 pi s2|^{-1/2} exp( -Re[ (x-m)^2 w ] ).  With xi := x - m_R,

    (x - m)^2 = xi^2 - m_I^2 - 2 i m_I xi,
    Re[ (x-m)^2 (a - i b) ] = a xi^2 - a m_I^2 - 2 b m_I xi,

so |N_C| = |2 pi s2|^{-1/2} exp( -a xi^2 + 2 b m_I xi + a m_I^2 ).  Young:
2 b m_I xi <= lambda a xi^2 + (b^2/(lambda a)) m_I^2.  Hence

    |N_C| <= |2 pi s2|^{-1/2} exp( -(1-lambda) a xi^2 ) * exp( (a + b^2/(lambda a)) m_I^2 ).

The Gaussian factor equals sqrt(2 pi sig2)/|2 pi s2|^{1/2} * g_{sig2}(xi) with
sig2 = 1/(2 a (1-lambda)).  The normalization ratio:

    sqrt(2 pi sig2) / |2 pi s2|^{1/2} = ( 2 a (1-lambda) |s2| ... ) 

compute with |w| = 1/(2|s2|) and a = |w| cos theta_w, theta_w = -arg s2 = arg w:

    ratio^2 = (2 pi sig2) / (2 pi |s2|) = 1/(2 a (1-lambda) |s2|) = |w| / (a (1-lambda))
            = 1 / ( (1-lambda) cos theta_w ).

Since cos theta_w = cos(arg s2) =: cos theta, the ratio is kappa(lambda, theta).  QED.

*Remarks.*
(i) The lemma is verified numerically in `b0_dyson_numerics.py` (routine
`verify_lemma1`): 10^4 random samples of (s2, m, x, lambda) in the relevant
sector, worst violation ratio <= 1 to double precision (see Section 9 run log).
(ii) Only three consequences are used downstream: |N_C| is dominated by
kappa x (unit-mass real Gaussian in x, centred m_R) x (penalty depending on the
*starting point* only through m_I^2); the variance of the dominating Gaussian is
irrelevant (only its unit mass is used); the penalty coefficient P_lam obeys,
with theta_w = |arg s2|,

    P_lam <= (1 + tan^2 theta / lambda) * cos^2 theta / (2 eps^2 Re v)
          <= (1 + tan^2 theta / lambda) / (2 eps^2 Re v)                                (4.2)

when s2 = eps^2 v.  Derivation of the first line: a = Re(1/(2 eps^2 v))
= Re v / (2 eps^2 |v|^2) and |b| = |Im v| / (2 eps^2 |v|^2), so
P_lam = a (1 + (b/a)^2/lambda) = [1 + tan^2 theta/lambda] * Re v / (2 eps^2 |v|^2)
= [1 + tan^2 theta/lambda] * cos^2 theta / (2 eps^2 Re v); the second line uses
cos^2 theta <= 1.

**Wrapped (torus) version.**  For the transverse block the kernel is the image
sum p^wrap(x|y) = sum_{k in Z} N_C(x - y + kW; 0, s2).  Applying (4.1) to each
image (here m_I = 0, see Section 5: the transverse block has E = 1) gives

    |p^wrap(x|y)| <= kappa(0+, theta) * sum_k g_{sig2}(x - y + kW),

and the dominating image sum has unit mass on any period cell.  No Young step
is needed (lambda -> 0 limit, kappa = (cos theta)^{-1/2}), and no penalty
factor arises.

---

## 5. Lemma 2: per-leg kernel data for the three coordinate blocks

The free transition density factorizes over the blocks.  Over a real duration
u > 0, started at y:

| block  | mean map                          | variance (real u)                              |
|--------|-----------------------------------|------------------------------------------------|
| Z      | zbar + (y - zbar) e^{-gamma u}    | eps^2 v_Z(u),  v_Z(u) = (D0/(2 gamma)) (1 - e^{-2 gamma u}) |
| r_par  | y e^{-gamma u}                    | eps^2 v_P(u),  v_P(u) = (2 D0/gamma) (1 - e^{-2 gamma u})   |
| r_perp | y  (per dim, wrapped mod W)       | eps^2 v_T(u),  v_T(u) = 4 D0 u  (image-summed)              |

(v_Z(inf) = D0/(2gamma) and v_P(inf) = 2 D0/gamma match the stationary
variances (C.4), (C.11); v_T matches Var = 4 eps^2 D0 t.)  Each block kernel is
N_C(x; mean, eps^2 v) with the entire functions E(zeta) := e^{-gamma zeta}
(mean multiplier; E = 1 for r_perp) and v(zeta) as above; these are the unique
analytic continuations in the duration, so the complex-leg kernels of Section 3
are exactly these expressions at zeta = z h, h in (0, 1].

**Lemma 2.**  Let zeta = z h with h in (0,1], z = u + i beta, u > 0.  Write
A := 2 gamma h u >= 0.  Then:

(a) *(positive real part)*  For all three blocks Re v(zeta) > 0.  Indeed
Re(1 - e^{-2 gamma zeta}) = 1 - e^{-A} cos(2 gamma h beta) >= 1 - e^{-A} >= A e^{-A}, so

    Re v_Z >= D0 h u e^{-A},    Re v_P >= 4 D0 h u e^{-A},    Re v_T = 4 D0 h u.

(b) *(argument bound)*  |tan arg v(zeta)| <= beta/u for all three blocks.
For r_perp this is arg v_T = arg z, and |tan arg z| = beta/u.  For the OU
blocks, with kap := beta/u (so that 2 gamma h beta = kap A):

    |Im(1 - e^{-2 gamma zeta})| = e^{-A} |sin(kap A)| <= kap A e^{-A},
    Re(1 - e^{-2 gamma zeta})  >= 1 - e^{-A} >= A e^{-A},

whence |tan arg v| <= (kap A e^{-A})/(A e^{-A}) = kap.  QED(b).

(c) *(imaginary mean-multiplier bound)*  For the OU blocks
(Im E(zeta))^2 = e^{-A} sin^2(gamma h beta) <= gamma^2 h^2 beta^2 e^{-A}.
For r_perp, Im E = 0.

(d) *(penalty-to-variance ratio, linear in h)*  Combining (a), (c) and (4.2):
for the Z block, a leg of duration zeta = z h started at y carries, after
Lemma 1 with parameter lambda, the penalty exponent

    sigma_Z(h) * (y - zbar)^2,
    sigma_Z(h) <= (1 + tan^2 theta / lambda) * gamma^2 h beta^2 / (2 eps^2 D0 u),      (5.1)

and for the r_par block (started at y, on the support of chi: |y| <= a)

    sigma_P(h) * y^2,
    sigma_P(h) <= (1 + tan^2 theta / lambda) * gamma^2 h beta^2 / (8 eps^2 D0 u).      (5.2)

Both are LINEAR in the leg duration fraction h; the e^{-A} factors cancel
exactly between numerator and denominator.  The r_perp block carries no
penalty.

(e) *(uniform kappa)*  With t_theta := beta_max/u_min where beta_max <= r0 and
u_min >= tau - r0 over all disks |z - t| <= r0, t in I, every leg of every
chain obeys |tan arg v| <= t_theta, hence cos theta >= (1 + t_theta^2)^{-1/2}, and the
per-leg domination constant (product over the d+1 scalar blocks, Young applied
only to Z and r_par) is

    kappa_leg <= khat := (1 - lambda)^{-1} (1 + t_theta^2)^{(d+1)/4}.                  (5.3)

*Proof of (e).*  Z and r_par blocks: kappa = ((1-lambda) cos theta)^{-1/2} each;
r_perp blocks ((d-1) of them): kappa = (cos theta)^{-1/2} each; multiply.  QED.

At the anchor (d = 2, lambda = 1/10, r0 = 0.0125, tau = 0.5):
t_theta = 0.025641, khat = 1.111659.

---

## 6. Lemma 3: node and initial-law penalty absorption (complete squares)

After Lemma 1 is applied to every leg of a chain, the surviving y-dependence at
each node is the penalty factor exp[sigma_Z (y_z - zbar)^2 + sigma_P y_par^2]
multiplying V(y) (interior nodes) or q0(y) (the starting point).  These are
absorbed by exact Gaussian algebra.

**Lemma 3a (weighted slab-mixture sup).**  Let sigma >= 0 with
x_sig := 2 eps^2 rho^2 sigma < 1.  Then for each component,

    N(y - c; eps^2 rho^2) e^{sigma (y - zbar)^2}
      = (1 - x_sig)^{-1/2} exp[ sigma (c - zbar)^2 / (1 - x_sig) ]
        * N( y - c(sigma); eps^2 rho^2/(1 - x_sig) ),
    c(sigma) = (c - x_sig zbar) / (1 - x_sig),

an exact complete-square identity (verified symbolically in the numerics
script, routine `verify_lemma3`).  Consequently

    sup_y [ phi_w(y) e^{sigma (y-zbar)^2} ]
      <= (1 - x_sig)^{-1/2} exp[ sigma (cmax - zbar)^2 / (1 - x_sig) ] * S_w(x_sig),   (6.1)

    cmax := max_j |chat_j - zbar|  (attained max over components),
    S_w(x) := sup_y sum_j w_j N( y - chat_j(sigma); eps^2 rho^2/(1-x) ),

and S_w(x_sig) <= (1 + delta_v) * sup_y phi_w(y) = (1 + delta_v) * v_inf W^{d-1} / sup-chi ...
in plain terms: S_w differs from the unweighted mixture sup by a width
inflation (1-x)^{-1/2} and an outward centre shift; delta_v is certified
numerically (grid + Lipschitz slack) and is < 2e-3 at all three evaluation
points, since x_sig < 4e-4 there.

**Lemma 3b (contact node).**  On the support of chi_a, |y_par| <= a, so the
r_par penalty factor obeys e^{sigma_P y_par^2} <= e^{sigma_P a^2}.  The
transverse blocks carry no penalty (Lemma 2(c)).

**Lemma 3c (initial-law integrals).**  For sigma >= 0 with 2 eps^2 v0 sigma < 1
(v0 = D0/(2 gamma)) and 2 eps^2 u0^2 sigma_P < 1:

    int N(y - z0; eps^2 v0) e^{sigma (y - zbar)^2} dy
        = (1 - 2 eps^2 v0 sigma)^{-1/2} exp[ sigma (z0 - zbar)^2 / (1 - 2 eps^2 v0 sigma) ],
    int N(y - 0; eps^2 u0^2) e^{sigma_P y^2} dy
        = (1 - 2 eps^2 u0^2 sigma_P)^{-1/2},

exact Gaussian identities (same verification routine).  The wrapped transverse
initial factor integrates to 1 against the (penalty-free) dominating image sums.

**Budget bookkeeping.**  For a chain of order n with leg fractions h_0..h_n
(sum = 1), sum over legs of (5.1)-(5.2) gives, INDEPENDENTLY of n and of the
h-configuration,

    sum_k sigma_Z(h_k) <= sigma_tot^Z := (1 + t_theta^2/lambda) gamma^2 r0^2 / (2 eps^2 D0 (tau - r0)),
    sum_k sigma_P(h_k) <= sigma_tot^P := sigma_tot^Z / 4.                              (6.2)

Every leg's penalty lands either on an interior node (Lemma 3a/3b with its own
sigma_k, centre bound (cmax - zbar)^2 <= yhat^2) or on the initial law
(Lemma 3c, centre (z0 - zbar)^2 <= yhat^2), with

    yhat := max( |z0 - zbar|, cmax ).

Multiplying the exponential factors and using sum_k sigma_k <= sigma_tot along
with 1/(1 - x_k) <= 1/(1 - x_max):

    (product of all penalty factors) <= e^{Pi},
    Pi := [ sigma_tot^Z * yhat^2 + sigma_tot^P * a^2 ] / (1 - x_max)
          + (1/2) sum_k x_k / (1 - x_max)   [normalization factors (1-x_k)^{-1/2}]
          + (1/2) [ 2 eps^2 v0 sigma_tot^Z + 2 eps^2 u0^2 sigma_tot^P ] / (1 - x_max'),   (6.3)

with x_k = 2 eps^2 rho^2 sigma_k, x_max <= 2 eps^2 rho^2 sigma_tot^Z, and
sum_k x_k <= 2 eps^2 rho^2 sigma_tot^Z; all terms explicit.  The width-inflation
slack delta_v of Lemma 3a inflates the per-node sup and therefore multiplies
the EFFECTIVE potential bound (it enters the exponent of the Dyson series),
while e^{Pi} is a single global factor, independent of the chain order.

---

## 7. Proposition 1: the assembled chain bound for the n-th Dyson term

**Proposition 1.**  Fix t in I, r0 with 0 < r0 < tau (conditions (R1)-(R3)
below), lambda in (0,1), and z with |z - t| <= r0.  Then for every n >= 1 and
every s in Delta_n, the flat chain integral (3.2) obeys

    |C_n(z; s)| <= khat * v_inf * ( khat * (1 + delta_v) * v_inf )^n * e^{Pi},          (7.1)

with khat from (5.3), Pi from (6.3), delta_v from Lemma 3a.  Consequently

    |D(z)| <= khat v_inf e^{Pi} * ( exp( B v_eff |z| ) - 1 ),
    v_eff := khat (1 + delta_v) v_inf,                                                  (7.2)

uniformly on the disk; and since |z| <= T + r0 for every t in I,

    sup_{t in I} sup_{|z - t| <= r0} |D(z)|
        <= E_c(B) := khat v_inf e^{Pi} ( exp( B v_eff (T + r0) ) - 1 ).                 (7.3)

*Proof.*  Write the chain (3.2) with legs j = 1..n+1 of durations
zeta_j = z h_j (h's the consecutive differences of (1, s_1, ..., s_n, 0); sum = 1),
configuration points x_0 (law q0), x_1, ..., x_n (interior V nodes), x_{n+1}
(observable V).  Apply Lemma 1 blockwise to every leg kernel:

    |p_{zeta_j}(x_j | x_{j-1})|
      <= kappa_leg,j * gbar_j(x_j - m_R(x_{j-1}))
         * exp[ sigma_Z(h_j) (x_{j-1,z} - zbar)^2 + sigma_P(h_j) x_{j-1,par}^2 ],

where gbar_j is a product of unit-mass real Gaussians (and unit-cell-mass image
sums for the torus blocks), and kappa_leg,j <= khat by Lemma 2(e).  Insert
these dominations into (3.2) with all V >= 0, q0 >= 0, and integrate from the
final point x_{n+1} inward:

  - x_{n+1}-integral:  int V(x_{n+1}) gbar(x_{n+1} - .) dx_{n+1} <= v_inf * 1.
  - x_j-integral (j = n..1):  int V(x_j) e^{penalty_j(x_j)} gbar(x_j - .) dx_j
        <= sup_x [ V(x) e^{penalty_j(x)} ] * 1
        <= W^{-(d-1)} * sup_y[ phi_w(y) e^{sigma_Z(h_j)(y-zbar)^2} ] * e^{sigma_P(h_j) a^2}
        <= (1 + delta_v) * v_inf * Cnode_j                          [Lemmas 3a, 3b],
    where Cnode_j collects the exponential and normalization factors of (6.1)
    with sigma = sigma_Z(h_j).  (The observable-side sup of the slab mixture,
    W^{-(d-1)} sup phi_w sup chi = v_inf, is the same quantity as the baseline's
    v_inf.)
  - x_0-integral:  int q0(x_0) e^{penalty_1(x_0)} dx_0 = Cinit  [Lemma 3c].

Multiplying: |C_n(z;s)| <= khat^{n+1} v_inf^{n+1} (1+delta_v)^n * prod_j Cnode_j * Cinit,
and prod_j Cnode_j * Cinit <= e^{Pi} by the budget bookkeeping (6.2)-(6.3),
uniformly in n and in the h-configuration.  This is (7.1).

For (7.2): by Section 3.2, |T_n(z)| <= (1/n!) sup_s |C_n(z;s)|, so

    |D(z)| <= sum_{n>=1} (B|z|)^n / n! * khat v_inf e^{Pi} (khat (1+delta_v) v_inf)^n
           = khat v_inf e^{Pi} ( e^{B v_eff |z|} - 1 ).   QED.

---

## 8. Theorem 1 and Corollary 1: derivative bounds and the new threshold

**Radius conditions.**  Fix the Cauchy radius by the closed form

    r0 := (eps / (gamma * yhat)) * sqrt( D0 * tau / 2 ),                                (R0)

and require (all purely geometric, checked at each evaluation point):

    (R1)  r0 <= tau / 2                       [disk stays in the right half-plane
                                               with u >= tau - r0 >= tau/2],
    (R2)  x_max = 2 eps^2 rho^2 sigma_tot^Z < 1/2,  2 eps^2 v0 sigma_tot^Z < 1/2,
          2 eps^2 u0^2 sigma_tot^P < 1/2      [Lemma 3 complete squares valid],
    (R3)  lambda := 1/10  (fixed once; any lambda in (0,1) is admissible).

With (R0), the leading budget term in (6.3) evaluates to

    sigma_tot^Z * yhat^2 = (1 + t_theta^2/lambda) * tau / (4 (tau - r0)),

i.e. about 1/4 * (1 + tau/(tau-r0) corrections): the penalty budget is
manifestly O(1), uniformly in eps, BY CONSTRUCTION of r0.  (r0 is not
optimized; see Section 12.)

**Theorem 1 (weighted-norm-free C^2 transfer).**  Under the standing
hypotheses of Section 1 and (R0)-(R3), for r = 1, 2 and every B > 0:

    sup_{t in I} | d^r/dt^r ( F_B - G )(t) |  <=  r! * r0^{-r} * E_c(B),                (8.1)

with E_c(B) = khat v_inf e^{Pi} ( exp( B v_eff (T + r0) ) - 1 )  from (7.3).

*Proof.*  D = G - F_B is analytic on {Re z > 0} (Section 3.1), which contains
every closed disk |z - t| <= r0, t in I, by (R1).  Cauchy's estimate on that
disk gives |D^{(r)}(t)| <= r! r0^{-r} sup_{|z-t|=r0} |D(z)|, and the sup is
bounded by E_c(B) by Proposition 1 (whose hypotheses hold on the disk by
(R1)-(R3)).  QED.

**Corollary 1 (sharpened explicit budget threshold).**  Assume additionally
the certified margin inventory (H1)-(H2).  Set

    Mhat := min( r0 * mu1 ,  r0^2 * mu2 / 2 ),
    B0_new := ln( 1 + Mhat / ( khat v_inf e^{Pi} ) ) / ( v_eff * (T + r0) ).            (8.2)

Then for every 0 < B < B0_new the budget-rescaled Doi density F_B has exactly
m nondegenerate maxima and m-1 nondegenerate minima on I, ordered alternately,
with no stationary endpoint; hence B0(eps) >= B0_new.

*Proof.*  B < B0_new iff E_c(B) < Mhat, iff both
r0^{-1} E_c(B) < mu1 and 2 r0^{-2} E_c(B) < mu2.  By Theorem 1 these are the
C^1 and C^2 closeness conditions of the baseline proposition's Step 2
(`b0_quantitative_bound.tex`), whose signature argument is purely a real-
variable comparison of F_B against G on the tubes and their complement and is
reused verbatim: on the complement F_B' keeps the sign of G' (|G'| >= mu1 and
the r=1 bound), no endpoint becomes stationary, and on each tube F_B'' keeps
the sign of G'' (|G''| >= mu2 and the r=2 bound) while F_B' changes sign, so
each tube contains exactly one nondegenerate stationary point of the correct
type.  E_c is continuous and strictly increasing in B with E_c(0) = 0, so the
inversion is exact.  QED.

**Comparison with the baseline.**  Structurally,

    baseline:  B0 = (2/(3 v_inf T))     * ln( 1 + M    / (v_* kappa_pi ||q0||_X) ),  M    = min(tau mu1/2, tau^2 mu2/8),
    new:       B0 = (1/(v_eff (T+r0))) * ln( 1 + Mhat / (khat v_inf e^{Pi})     ),  Mhat = min(r0 mu1,   r0^2 mu2/2).

Gains: the denominator of the log argument drops from
v_* ||q0||_X ~ e^{1600.5} * 0.0976 to khat v_inf e^{Pi} = O(1).
Losses: the Cauchy radius shrinks from tau/2 to r0 ~ eps (factor ~ tau/(2 r0)
= 20 at the anchor in Mhat), and the exponential-rate constant worsens from
(3/2) v_inf T to v_eff (T + r0) (a factor ~ (2/3) khat (1+delta_v) (T+r0)/T
~ 0.75, i.e. actually slightly BETTER); both losses are polynomial and
O(1)-bounded.

---

## 9. Anchor evaluation (eps = 0.1, m = 2)

All numbers in Sections 9-11 are produced by `b0_dyson_numerics.py` (mpmath,
dps 40-60; contact factor by adaptive quadrature + Chebyshev interpolation
cross-validated against direct quadrature to <= 1e-28 relative; the complete
run log is `b0_dyson_run.log` in this directory).

**Step 0 — verification gates (run log, top).**
Lemma 1 numerical domination check: worst |LHS/RHS| = 0.99999979 <= 1 over 1e4
random samples.  Lemma 2 penalty/argument bounds: worst ratios 0.99999815 and
0.99999968 <= 1.  Lemma 3 identities: exact to 2.1e-37.  Independent
Proposition-1 spot check (`b0_dyson_chaincheck.py`, vectorized complex-time
quadrature of the FULL Z-block chain integrals for n = 1 and n = 2, at
|z - t| = r0, angles {pi/2, pi, 3pi/2}, extreme leg configurations
h = (0.01, 0.99) etc.): worst |C_n^Z| / assembled bound = 0.105 <= 1.

**Step 1 — baseline reproduction (identical inputs).**
c(tau) = 0.95803212 (baseline 0.958032); c(T) = 0.76529855 (0.765298);
b(tau) = -0.115525 (-0.11552); stationary roots and curvatures

    t* = 0.99914522 (max)  G = 1.46573     G'' = -212.079
    t* = 1.4918212  (min)  G = 5.17105e-5  G'' = +0.058006
    t* = 2.4931614  (max)  G = 1.29083     G'' = -9.42243

(baseline: 0.999145 / 1.491821 / 2.493161, G'' = -212.079 / +5.80060e-2 /
-9.42243); G'(tau) = 1.5471892e-11 (baseline mu1 = 1.54719e-11);
|G'(T)| = 0.5025 (0.5025).  Every displayed digit agrees.

**Step 2 — margins.**  We use the baseline's certified inventory unchanged:
mu1 = 1.54719e-11 (attained at tau), mu2 = 2.9003e-2 (half valley curvature).
Our own tube construction (half-curvature tubes; run log) reproduces
mu1, mu2 and gives B0_new agreeing to 7 significant figures.

**Step 3 — constants of Theorem 1 / Corollary 1** (lambda = 1/10):

    yhat  = 4            (z0 dominates; cmax = 1.4715)
    r0    = (eps/(gamma yhat)) sqrt(D0 tau/2) = 0.0125     [R1: 0.0125 <= 0.25 OK]
    t_theta = r0/(tau - r0) = 0.025641
    khat  = (1-lambda)^{-1} (1 + t_theta^2)^{3/4} = 1.111659
    sigma_tot^Z = 0.016131,  sigma_tot^P = 0.0040328
    x_max = 3.226e-4, x_v0 = 1.613e-4, x_u0 = 1.613e-4    [R2 OK, all < 1/2]
    Pi    = 0.2591475,   e^Pi = 1.2958249
    v_inf = 1.9947114  (grid-certified sup of the slab mixture; baseline 1.994712)
    delta_v = 0 (width inflation lowers the mixture peak), so v_eff = khat v_inf = 2.2174388
    C_pre = khat v_inf e^Pi = 2.8734124

**Step 4 — threshold.**

    r0 mu1        = 1.93399e-13   <-- binds (r = 1, endpoint slope)
    r0^2 mu2 / 2  = 2.26586e-6
    Mhat          = 1.93399e-13

    B0_new = ln(1 + Mhat/C_pre) / (v_eff (T + r0))
           = 8.6414719e-15,     log10 B0_new = -14.063412.

**Comparison with the baseline at the anchor.**

    | quantity                        | baseline               | this draft            |
    |---------------------------------|------------------------|-----------------------|
    | log-argument denominator        | v_* ||q0||_X ~ 10^694  | C_pre = 2.87          |
    | Cauchy radius                   | tau/2 = 0.25           | r0 = 0.0125           |
    | exponential rate (denominator)  | (3/2) v_inf T = 10.47  | v_eff (T+r0) = 7.789  |
    | B0 lower bound                  | 3.03e-707              | 8.64e-15              |
    | log10 B0                        | -706.5184              | -14.0634              |
    | empirical depletion scale       | ~7.6                   | ~7.6                  |

Improvement: 692.5 orders of magnitude.  Remaining conservatism (~15 orders):
the intrinsic endpoint margin mu1 = e^{-30.4} x O(10^2) (window opening
7.79 mixture widths before the first clock), the radius factor r0, and O(10)
bookkeeping — see W3/W4 in Section 12.

---

## 10. Secondary point A (eps = 0.05, same geometry, m = 2)

Signature verified directly: three stationary points, no stationary endpoint
(run log).  Inventory (own tube construction, half-curvature convention,
dps 60; direct-vs-Chebyshev derivative check 9.8e-32 relative):

    t* = 0.99999587 (max)  G = 3.25585    G'' = -1880.08
    t* = 1.4917343  (min)  G = 7.8333e-19 G'' = +1.45697e-14
    t* = 2.4992926  (max)  G = 3.20016    G'' = -92.2246
    tubes: [0.972845,1.02489], [1.04157,2.3159], [2.36346,2.59238]
    mu2 = 7.28486e-15 (half valley curvature; the valley is now e^{-19}-deep)
    mu1 = 3.43243e-50, attained at tau
        (consistency: exponent D_L^2/(2 S_*^2 eps^2) = 121.503, e^{-121.503}
         = 10^{-52.77}, times the polynomial prefactor ~ 5e2 -> 3.4e-50 OK)

Constants: r0 = 0.00625, t_theta = 0.0126582, khat = 1.1112446,
Pi = 0.25430352, e^Pi = 1.2895632, v_inf = 3.9894228 (~ 2x the anchor value,
prop. to 1/eps), delta_v = 0, v_eff = 4.4332247, C_pre = 5.7169232.
[R1: 0.00625 <= 0.25; R2 all < 1e-4.]

    r0 mu1       = 2.14527e-52   <-- binds (r = 1)
    r0^2 mu2 / 2 = 1.42283e-19
    B0_new = 2.4141087e-54,    log10 B0_new = -53.617243.

Baseline comparison at this point: the baseline denominator alone carries
||q0||_X = e^{gamma z0^2/(eps^2 D0)} = e^{6400} = 10^{2779.6}, so its threshold
is below 10^{-2780} before any other factor; the sharpened bound gains
> 2700 orders of magnitude here.

**Scaling check of the exponent constant.**  Predicted decade drop from the
anchor: c_B x (1/0.05^2 - 1/0.1^2) = 0.303757 x 300 = 91.13 nats = 39.58
decades.  Observed: 53.617 - 14.063 = 39.55 decades.  The 0.03-decade
difference is the polynomial prefactor drift — the asymptotic law
log B0_new = -c_B/eps^2 + O(log(1/eps)) with c_B = D_L^2/(2 S_*^2) is
confirmed to three digits by the two evaluation points.

---

## 11. Secondary point B (eps = 0.1, m = 3, targets (0.8, 1.6, 2.8), w uniform)

Slab centres chat = (1.79732, 0.807586, 0.24324); centre gaps 8.1 and 4.6
mixture widths.  Signature verified directly: exactly five stationary points,
alternating, no stationary endpoint (run log):

    t* = 0.79940591 (max)  G = 1.00215     G'' = -216.199
    t* = 1.1221147  (min)  G = 5.48772e-4  G'' = +0.950985
    t* = 1.5979094  (max)  G = 0.915627    G'' = -39.9907
    t* = 2.030737   (min)  G = 0.124476    G'' = +9.84849
    t* = 2.7899767  (max)  G = 0.849232    G'' = -3.42421
    tubes: [0.753896,0.838905], [0.867453,1.44722], [1.48998,1.67673],
           [1.76895,2.19356], [2.3978,2.95482]
    mu2 = 0.475492 (half the shallowest curvature, the first valley)
    mu1 = 1.99525e-4, attained at tau
        (the window now opens only D_L/(ell0 sigma) = 5.13 mixture widths
         before the first clock: D_L = 0.628807, exponent
         D_L^2/(2 S_*^2 eps^2) = 13.180)

Constants (same eps as anchor): r0 = 0.0125, khat = 1.111659, e^Pi =
1.2958249, v_inf = 1.3298078 (max_j w_j = 1/3 lowers the mixture sup),
delta_v = 0, v_eff = 1.4782927, C_pre = 1.9156085.

    r0 mu1       = 2.49406e-6   <-- binds (r = 1)
    r0^2 mu2 / 2 = 3.71478e-5
    B0_new = 2.5073946e-7,    log10 B0_new = -6.6007773.

Here the sharpened bound lands within seven orders of magnitude of the O(1)
empirical depletion scale — the entire remaining gap is the honest endpoint
margin e^{-13.18} times O(10) bookkeeping, consistent with W4.  New exponent
constant for this geometry: c_B = D_L^2/(2 S_*^2) = 0.131799.
---

## 12. Honest assessment: weakest steps and remaining conservatism

**W1 — Fubini / identity-theorem bridge (Section 3.2).**  The step that
equates the weighted-space Dyson term with the flat (n+1)-fold Gaussian chain
integral at complex time is proved by: (real z) Tonelli for positive kernels;
(complex z) analyticity of both sides plus the identity theorem.  Analyticity
of the flat side rests on locally uniform absolute convergence of the
dominated chain integral (Lemma 1 domination), which is established by the
same bounds used for the final estimate — the logic is not circular (the
domination is pointwise and independent of the analyticity claim), but this is
the most technical step of the derivation, and in a journal version it should
be written out with an explicit Morera argument for the (n x dim)-dimensional
parameter integral.  Nothing quantitative depends on it.

**W2 — the margin inventory is double-precision-scanned, not interval
arithmetic.**  Exactly as in the baseline (its "Certification status"
paragraph): mu1, mu2, the stationary roots and the tube edges are computed by
high-precision quadrature + bisection (here: mpmath, dps 40-60, Chebyshev
interpolation of the contact factor cross-validated against direct
quadrature to ~1e-29 relative), reproduced independently for the anchor by the
baseline's two implementations.  This is inherited conservatism-of-status, not
a new weakness of this route.

**W3 — r0 is not optimized and the budget constants are crude.**
The closed form (R0) was chosen for statement cleanliness (penalty budget
= tau/(4(tau - r0)) + small terms, provably O(1)).  Optimizing r0 (and lambda)
per case moves B0_new by a factor ~2-3 only, since the r=1 condition binds and
B0_new is linear in r0 mu1 at these magnitudes.  Similarly, bounding all n+1
interior potential factors by v_inf discards the shape of V beyond its sup;
keeping one exact factor (as Pillar 1 does at r = 0) is possible for r = 1, 2
too but complicates the Cauchy step for negligible gain here.

**W4 — the remaining gap to experiment is the margin inventory itself, not the
transfer machinery.**  B0_new ~ r0 mu1 / (stuff O(10)): with mu1 = |G'(tau)|
~ e^{-D_L^2/(2 S_*^2 eps^2)}, the bound inherits the window-opening factor
(e^{-30.4} = 6.4e-14 at the anchor).  The empirical depletion threshold ~7.6
is O(1) because the physical mechanism does not care about the tiny endpoint
slope: the slope margin is a sufficient-condition artifact of the
sign-preservation proof strategy (any C^1-perturbation argument on I pays it).
Improving beyond this requires a different proof topology (e.g. localizing the
signature argument to sub-windows where |G'| is not uniformly tiny, or a
degree/index argument replacing the uniform complement margin), not a better
semigroup estimate: the semigroup side of the ledger is now O(1)-tight.

**W5 — generality.**  The chain bound uses (i) the product OU/OU/torus-BM
structure of the free process (explicit Mehler kernels), (ii) Gaussian slab
profiles and the compactly supported contact indicator (node confinement),
(iii) a Gaussian initial law.  These are exactly the standing structures of
the theorem's construction, so no generality is lost *for this paper*; but
unlike the baseline's abstract route (any analytic positive semigroup + any
q0 in X_pi), the sharpened route is model-specific by design.  It should be
stated as a proposition about the slab design, not as a replacement for
Theorem B.1.

