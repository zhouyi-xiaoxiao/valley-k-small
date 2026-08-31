# Source-bound map, cut-layer, and killing-residual lemma

Date: 2026-07-17

Status: **IDEAL SOURCE-BOUND THEOREM CANDIDATE / TWELVE REFINEMENT TAILS /
SYMBOLIC CONSTANTS ONLY / PRODUCTION SAME-MEMBER AND COMPLETE C2 FALSE**

## 0. Purpose and exact nonclaim boundary

Rounds 10 and 11 close, respectively, the ideal one-sided free residual and
the fixed-box mixed Neumann--periodic sector/contour arguments.  Their
remaining quantitative inputs are the map estimate and the sharp-contact
killing residual in Round 9.  This note derives those inputs for the twelve
genuine ideal refinement sequences from the frozen density, gauge, map, and
contact sources.

The conclusion is a theorem about the **ideal formula-defined tails**.  It is
not a correlated production receipt.  In particular, it does not show that
one common ideal mass/rate/flux/gauge/map/killing member is contained in the
saved production intervals.  The Round-170 outer receipt authenticates the
control-free killing geometry only.  It contains no concrete control,
positive budget, or full killed operator.

No numerical value is assigned to any theorem constant below.  All
complete-C0/C1/C2/C3, production, same-member, science, release, and
submission claims remain false.

The exact byte authorities are:

| role | report-relative path | SHA-256 |
|---|---|---|
| genuine twelve-sequence authority | `artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json` | `1f7bc61ac37444c0fdb2c0b74924a4b81ed8e6d6ab70c794ebe3401156b5bee9` |
| finite configuration anchors | `artifacts/data/physical_configuration_family_control_free_v1.json` | `063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084` |
| global reference density | `artifacts/data/continuum_c1_reference_density_source_v1.json` | `7b890d727ad0b229557de1841ae82befb8d8f83e79edc6b5348b277c3024e575` |
| ideal mass/flux/map/gauge formulae | `artifacts/data/continuum_c1_ideal_formula_source_v1.json` | `f31b637b659483102d787da7263cd45c72829b3fce3df2ff9100066dec94c2be` |
| product/contact factorization | `artifacts/data/continuum_c1_factorization_source_v1.json` | `70cb49e63c496d489887c764c812671b03a7352d5752f6663c377734739a1dca` |
| killing-geometry authority | `artifacts/data/physical_killing_geometry_source_v1.json` | `5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669` |
| Round-170 geometry outer receipt | `artifacts/data/physical_production_killing_geometry_two_repeat_outer_receipt_v1.json` | `d635dfb7dd24fc15731dfd69e20264a5515c3bf82b92569a58cd2bed3264fcd9` |
| Round-4 map theorem note | `notes/continuum_c1_free_form_and_functional_bridge_candidate.md` | `17b987d5090618e5346f81217afed7e57daccf878d4b93b8402724b3e002a562` |
| Round-4 audit | `audits/continuum_c1_refinement_functional_bridge_round4_20260717.md` | `6ccdcd76a4049e198d13ae45d86570c17d7876a4ef28de8fb3fed0ea1b513134` |
| Round-9 residual-route note | `notes/continuum_c2_qf2_checkerboard_and_residual_route_candidate.md` | `4b20189814c763816ea707630ff098c98995afd7d3207808225a320a742508c2` |
| Round-9 audit | `audits/continuum_c2_qf2_checkerboard_residual_route_round9_20260717.md` | `ed1f15c20c93db274989827dae9ccf5f3d36d5d80e1c9ba90052de8edf18b260` |
| Round-10 free-residual note | `notes/continuum_c2_one_sided_free_sg_residual_candidate.md` | `ba3d41da0f16ab4ceb0f2f0c8eceeb29214b0b5b765c9300f373a3513bb21fc4` |
| Round-10 audit | `audits/continuum_c2_one_sided_free_sg_residual_round10_20260717.md` | `c00351acc5ff3be67cbb579ccab768e8e226bd29bc730f5d9acb15c5dcc3163d` |
| Round-11 sector note | `notes/continuum_c2_mixed_neumann_periodic_sector_h2_candidate.md` | `4339385e8489984701aabedbd4ab0a28d69db5b2ffd7e2d1c91d1d4ba63564d9` |
| Round-11 audit | `audits/continuum_c2_mixed_neumann_periodic_sector_h2_round11_20260717.md` | `d3b0aca6203999ba18f08a380847f7253e41fc72272d28f4c4fcde92dbb89a2c` |

The Hilbert convention is the authoritative Round-11 convention

\[
 \langle u,v\rangle_H=\int_{\Omega_f}\overline u\,v\,\pi\,dx .
 \tag{0.1}
\]

Thus the first factor is conjugated.  Absolute-value estimates are unchanged
by the opposite convention used in one frozen Round-10 sentence.

## 1. Fixed boxes and the twelve uniform refinement tails

For a source row \(f\), write

\[
 \Omega_f=I_{M,f}\times I_{R,f}\times\mathbb T_W,
 \qquad h_f(n)=\max\{h_{M,f}(n),h_{R,f}(n),h_{Y,f}(n)\}.
 \tag{1.1}
\]

The genuine-family authority gives, exactly,

\[
 h_{a,f}(n)=h_{a,f}(0)2^{-n},
 \qquad h_f(n)=h_f(0)2^{-n}.
 \tag{1.2}
\]

Cell-centred cells have side \(h_{a,f}(n)\).  A vertex-dual endpoint
cell has side \(h_{a,f}(n)/2\), and its representative is the endpoint.
A wrapped periodic cell is one connected torus cell of side
\(h_{Y,f}(n)\), even though it is stored as two chart segments.

There are only twelve rows.  Hence

\[
 H_*=\max_f h_f(0)<\infty,\qquad
 h_f(n)\le H_*2^{-n}
 \tag{1.3}
\]

uniformly.  Every maximum over \(f\) below is therefore a maximum over a
finite frozen set, not over an undeclared continuum of boxes.

The globally normalized, unconditioned density is

\[
 \pi(M,R,Y)=Z^{-1}
 \exp\!\left[-\Phi_M(M)-\Phi_R(R)\right],
 \quad
 Z=\frac{2\pi_{\rm circ}DW}{\gamma},
 \tag{1.4}
\]

\[
 \Phi_M(M)=\frac{\gamma(M-\bar M)^2}{D},
 \qquad
 \Phi_R(R)=\frac{\gamma R^2}{4D}.
 \tag{1.5}
\]

Here \(\pi_{\rm circ}\) denotes the circle constant.  The restriction of
\(\pi\) to \(\Omega_f\) is not divided by its box mass.

## 2. Cell oscillation and the tensor \(\rho\) bound

For \(a\in\{M,R\}\), let \(x_{a,i}\) be the declared representative,
\(\nu_{a,i}=|C_{a,i}|\), and

\[
 \mu_{a,i}=\nu_{a,i}e^{-\Phi_a(x_{a,i})},\qquad
 I_{a,i}=\int_{C_{a,i}}e^{-\Phi_a(x)}\,dx,\qquad
 r_{a,i}=\frac{I_{a,i}}{\mu_{a,i}}.
 \tag{2.1}
\]

Define the source-bound gradient envelopes

\[
 L_{M,f}=\sup_{I_{M,f}}|\Phi'_M|
 =\frac{2\gamma}{D}
   \max_{x\in\partial I_{M,f}}|x-\bar M|,
 \tag{2.2}
\]

\[
 L_{R,f}=\sup_{I_{R,f}}|\Phi'_R|
 =\frac{\gamma}{2D}
   \max_{x\in\partial I_{R,f}}|x|.
 \tag{2.3}
\]

For every declared ordinary or dual cell,
\(|x-x_{a,i}|\le h_{a,f}(n)/2\).  This includes the endpoint half
cells.  Therefore

\[
 |\Phi_a(x)-\Phi_a(x_{a,i})|
 \le \frac12L_{a,f}h_{a,f}(n),
 \tag{2.4}
\]

\[
 e^{-L_{a,f}h_{a,f}/2}
 \le r_{a,i}\le
 e^{L_{a,f}h_{a,f}/2}.
 \tag{2.5}
\]

Put \(S_a=\sum_i\mu_{a,i}\) and

\[
 \bar r_a=\frac{\sum_i\mu_{a,i}r_{a,i}}{S_a}.
 \tag{2.6}
\]

The same bounds hold for \(\bar r_a\), so

\[
 e^{-L_{a,f}h_{a,f}}
 \le\frac{r_{a,i}}{\bar r_a}
 \le e^{L_{a,f}h_{a,f}}.
 \tag{2.7}
\]

On the periodic axis, \(\Phi_Y=0\), \(S_Y=W\), and its ratio is exactly
one, including wrapped cells.  The global gauge is

\[
 G_h=\frac{M_{L,f}}{S_MS_RS_Y}
     =Z^{-1}\bar r_M\bar r_R,
 \tag{2.8}
\]

where the second equality uses the **global**, unconditioned density and
\(S_Y=W\).  Thus the tensor ratio factorizes exactly:

\[
 \rho_{ijk}
 =\frac{\int_{C_{ijk}}\pi\,dx}{\pi_{h,ijk}}
 =\frac{r_{M,i}}{\bar r_M}
  \frac{r_{R,j}}{\bar r_R}.
 \tag{2.9}
\]

With

\[
 \eta_f(n)=L_{M,f}h_{M,f}(n)+L_{R,f}h_{R,f}(n),
 \qquad
 \Lambda_*=\max_f(L_{M,f}+L_{R,f}),
 \tag{2.10}
\]

one obtains

\[
 \boxed{
 e^{-\eta_f(n)}\le\rho_{ijk}\le e^{\eta_f(n)},\qquad
 \eta_f(n)\le\Lambda_*h_f(n).}
 \tag{2.11}
\]

No midpoint Taylor expansion is used.  Consequently Eq. (2.11) covers
vertex endpoint half cells without pretending that their defect is
second order.

## 3. Exact-adjoint map bounds

Let

\[
 J_hv=\sum_Cv_C{\bf1}_C,\qquad
 (P_hu)_C=\pi_{h,C}^{-1}\int_Cu\pi\,dx,
 \tag{3.1}
\]

and let

\[
 (A_hu)_C=\left(\int_C\pi\,dx\right)^{-1}\int_Cu\pi\,dx,
 \qquad E_h=J_hA_h.
 \tag{3.2}
\]

Then, exactly,

\[
 P_h=J_h^*,\qquad
 P_hJ_h=\operatorname{diag}(\rho),\qquad
 J_hP_h=\rho_h^{pc}E_h.
 \tag{3.3}
\]

Equation (2.11) gives

\[
 \|J_hv\|_H^2
 =\sum_C\rho_C\pi_{h,C}|v_C|^2
 \le e^{\eta_f(n)}\|v\|_h^2,
 \tag{3.4}
\]

\[
 \|J_h\|=\|P_h\|\le e^{\eta_f(n)/2},
 \tag{3.5}
\]

\[
 \|P_hJ_h-I\|_{H_h\to H_h}
 \le e^{\eta_f(n)}-1
 \le\Lambda_*e^{\Lambda_*H_*}h_f(n).
 \tag{3.6}
\]

For completeness, the reconstruction estimate needed by Round 9 is also
quantitative.  Let

\[
 0<\pi_-^*\le\pi\le\pi_+^*<\infty
 \tag{3.7}
\]

on the finite union of the twelve fixed boxes.  Every physical cell, after
lifting a wrapped torus cell, is a convex rectangle of diameter at most
\(\sqrt3h_f(n)\).  The convex-domain Poincare inequality and the minimizing
property of the \(\pi\)-weighted cell mean give

\[
 \|E_hu-u\|_H
 \le C_{\rm av}h_f(n)\|\nabla u\|_{L^2(\pi)},
 \quad
 C_{\rm av}
 =\frac{\sqrt3}{\pi_{\rm circ}}
  \left(\frac{\pi_+^*}{\pi_-^*}\right)^{1/2}.
 \tag{3.8}
\]

Since \(E_h\) is an \(H\)-contraction,

\[
 \begin{split}
 \|J_hP_hu-u\|_H
 &\le\|E_hu-u\|_H+
      \|(\rho_h^{pc}-1)E_hu\|_H\\
 &\le C_Ph_f(n)\|u\|_{H^1(\Omega_f)},
 \end{split}
 \tag{3.9}
\]

Here \(H^1(\Omega_f)\) is the ordinary unweighted Sobolev norm.  Both the
gradient term in Eq. (3.8) and the \(H\)-norm in the \(\rho-1\) term must
therefore be converted using
\(\|w\|_{L^2(\pi)}\le\sqrt{\pi_+^*}\|w\|_{L^2}\).
One admissible symbolic choice is consequently

\[
 C_P=\sqrt{\pi_+^*}
 \left(C_{\rm av}+\Lambda_*e^{\Lambda_*H_*}\right).
 \tag{3.10}
\]

Equations (3.5)--(3.10) are source-uniform over the twelve ideal
sequences.  They do not assert operator-norm convergence of \(J_hP_h\) on
all of \(H\); Eq. (3.9) has the necessary \(H^1\) domain.

## 4. Uniform profile bounds without a concrete control

The geometry source defines

\[
 b(s)={\bf1}_{|s|<1}\exp[-(1-s^2)^{-1}],
 \qquad I_b=\int_{-1}^1b(s)\,ds,
 \tag{4.1}
\]

\[
 \phi_j(M)=\frac{b((M-c_j)/q)}{qI_b},
 \tag{4.2}
\]

with common source half-width \(q>0\).  Put

\[
 B_0=\|b\|_\infty,\qquad B_1=\|b'\|_\infty,
 \tag{4.3}
\]

\[
 \Psi_*=\frac{B_0}{qI_b},\qquad
 L_\Psi=\frac{B_1}{q^2I_b}.
 \tag{4.4}
\]

These are finite symbolic constants; they are not numerically evaluated
here.  For every symbolic real simplex vector
\(w_j\ge0,\ \sum_{j=1}^4w_j=1\), define

\[
 \psi=\sum_{j=1}^4w_j\phi_j.
 \tag{4.5}
\]

Then, uniformly over the complete simplex,

\[
 0\le\psi\le\Psi_*,
 \qquad |\psi(M)-\psi(M')|\le L_\Psi|M-M'|.
 \tag{4.6}
\]

This is a family-uniform analytical statement, not a concrete control
selection.

## 5. Contact tube: the conditions behind \(4\pi a\delta\)

Let

\[
 D_a=\{(R,Y)\in\mathbb R\times\mathbb T_W:
 R^2+d_{\mathbb T_W}(Y,0)^2\le a^2\},
 \qquad a<W/2.
 \tag{5.1}
\]

For row \(f\), write \(I_{R,f}=(R_{f,-},R_{f,+})\) and define

\[
 m_{R,f}=\min\{-a-R_{f,-},\,R_{f,+}-a\},
 \qquad m_T=W/2-a.
 \tag{5.2}
\]

The exact frozen endpoints satisfy \(m_{R,f}>0\), and the geometry source
satisfies \(m_T>0\).  Set the deliberately strict clearance

\[
 q_f^{\rm tube}
 =\frac12\min\{a,m_T,m_{R,f}\},
 \qquad
 q_*^{\rm tube}=\min_fq_f^{\rm tube}>0.
 \tag{5.3}
\]

For one relative tensor cell, let

\[
 \delta_f(n)=
 \sqrt{h_{R,f}(n)^2+h_{Y,f}(n)^2}
 \le\sqrt2\,h_f(n).
 \tag{5.4}
\]

Restrict to the common refinement tail on which

\[
 h_f(n)\le1,\qquad
 \sqrt2\,h_f(n)\le q_*^{\rm tube}.
 \tag{5.5}
\]

Such a tail exists by Eq. (1.2).  The factor \(1/2\) in Eq. (5.3) makes
all chart and box inequalities strict, even if equality holds in Eq. (5.5).

Let \(\mathcal U_{h,f}\) be the union of relative cells whose closure meets
\(\partial D_a\).  Every point in such a cell is within the cell diameter
of a boundary point, so

\[
 \mathcal U_{h,f}
 \subset\{x:\operatorname{dist}(x,\partial D_a)\le\delta_f(n)\}.
 \tag{5.6}
\]

Conditions (5.3)--(5.5) have three separate roles:

1. \(\delta_f(n)<a\), so the inner radius \(a-\delta_f(n)\) is positive;
2. \(a+\delta_f(n)<W/2\), so the torus tube lies in one minimum-image
   chart and never meets the cut locus; and
3. \(a+\delta_f(n)\) stays strictly inside \(I_{R,f}\).

Only under these conditions is the tube an ordinary Euclidean annulus.
Its area is then

\[
 \begin{split}
 |\mathcal U_{h,f}|
 &\le\pi_{\rm circ}
  \{(a+\delta_f)^2-(a-\delta_f)^2\}\\
 &=4\pi_{\rm circ}a\delta_f(n).
 \end{split}
 \tag{5.7}
\]

Without any one of the three conditions, the bare
\(4\pi_{\rm circ}a\delta\) formula would not be an accepted bound here.
In particular, when \(\delta>a\) the inner disk disappears and that formula
is generally false.  This is why Eq. (5.7) is a tail theorem rather than an
unqualified coarse-grid assertion.

Wrapped periodic cells cause no seam exception.  On the tail, every cut
cell lies in the single contact chart; a seam-wrapped cell is too far from
\(\partial D_a\) to be cut.  Endpoint half cells cause no \(R\)-boundary
exception because the entire tube lies strictly inside the \(R\)-box.

## 6. Physical-volume average of the sharp field

Define the unit-budget symbolic field

\[
 V(M,R,Y)=W^{-1}\psi(M){\bf1}_{D_a}(R,Y).
 \tag{6.1}
\]

The factor \(W^{-1}\) is mandatory.  Let \(Q_{M,h}\) and \(Q_{RY,h}\)
denote physical-volume cell averages.  Rectangular product cells and the
factorization authority give, exactly,

\[
 V_h^{pc}
 =W^{-1}(Q_{M,h}\psi)(Q_{RY,h}{\bf1}_{D_a}).
 \tag{6.2}
\]

This is not a \(\pi\)-weighted average.  By Eq. (4.6),

\[
 |Q_{M,h}\psi-\psi|
 \le L_\Psi h_{M,f}(n)
 \le L_\Psi h_f(n),
 \tag{6.3}
\]

including vertex endpoint half cells.  Since the restricted global density
has box mass at most one,

\[
 \left\|
 W^{-1}(Q_{M,h}\psi-\psi)
 Q_{RY,h}{\bf1}_{D_a}
 \right\|_{L^2(\pi)}
 \le \frac{L_\Psi}{W}h_f(n).
 \tag{6.4}
\]

The contact-average error is zero outside \(\mathcal U_{h,f}\) and at most
one everywhere.  Let

\[
 L_M^*=\max_f|I_{M,f}|.
 \tag{6.5}
\]

Using the globally normalized density only through
\(\pi\le\pi_+^*\), Eqs. (5.4) and (5.7) imply

\[
 \begin{split}
 &\left\|
 W^{-1}\psi
 (Q_{RY,h}{\bf1}_{D_a}-{\bf1}_{D_a})
 \right\|_{L^2(\pi)}\\
 &\quad\le
 \frac{\Psi_*}{W}
 \{\pi_+^*L_M^*\,4\pi_{\rm circ}a\delta_f(n)\}^{1/2}\\
 &\quad\le
 C_{V,\rm cut}h_f(n)^{1/2},
 \end{split}
 \tag{6.6}
\]

where the symbolic constant may be chosen as

\[
 C_{V,\rm cut}
 =\frac{2\,2^{1/4}\Psi_*}{W}
   \{\pi_{\rm circ}a\pi_+^*L_M^*\}^{1/2}.
 \tag{6.7}
\]

Combining Eqs. (6.4) and (6.6),

\[
 \boxed{
 \|V_h^{pc}-V\|_{L^2(\pi)}
 \le C_{V,\rm cut}h_f(n)^{1/2}
    +\frac{L_\Psi}{W}h_f(n).}
 \tag{6.8}
\]

No derivative of the sharp indicator is taken.  The half order comes only
from the square root of the cut-layer volume.

## 7. Reconstructed multiplier

The ideal reconstructed killing multiplier is

\[
 K_h^{pc}=\frac{V_h^{pc}}{\rho_h^{pc}}.
 \tag{7.1}
\]

Equations (2.11), (4.6), and (6.2) give

\[
 \|K_h^{pc}\|_\infty
 \le e^{\Lambda_*H_*}\frac{\Psi_*}{W}
 =:C_K.
 \tag{7.2}
\]

Moreover,

\[
 K_h^{pc}-V
 =(\rho_h^{pc})^{-1}(V_h^{pc}-V)
  +\{(\rho_h^{pc})^{-1}-1\}V.
 \tag{7.3}
\]

Since

\[
 \|(\rho_h^{pc})^{-1}-1\|_\infty
 \le e^{\eta_f(n)}-1
 \le\Lambda_*e^{\Lambda_*H_*}h_f(n),
 \tag{7.4}
\]

Eqs. (6.8) and (7.3) yield

\[
 \boxed{
 \|K_h^{pc}-V\|_{L^2(\pi)}
 \le C_{K,\rm cut}h_f(n)^{1/2}
    +C_{K,\rm map}h_f(n),}
 \tag{7.5}
\]

with the unevaluated symbolic choices

\[
 C_{K,\rm cut}
 =e^{\Lambda_*H_*}C_{V,\rm cut},
 \tag{7.6}
\]

\[
 C_{K,\rm map}
 =e^{\Lambda_*H_*}
  \left\{\frac{L_\Psi}{W}
  +\frac{\Lambda_*\Psi_*}{W}\right\}.
 \tag{7.7}
\]

The use of box mass \(\le1\) in Eq. (7.7) is valid only because
\(\pi\) retains its global probability normalization.  Conditional
renormalization on each box would change the constants and the member.

## 8. Round-9 killing residual

Under the convention (0.1), the exact reconstructed identities are

\[
 \mathfrak k_h(P_hu,v_h)
 =\int_{\Omega_f}K_h^{pc}
   \overline{J_hP_hu}\,J_hv_h\,\pi\,dx,
 \tag{8.1}
\]

\[
 \langle P_h(Vu),v_h\rangle_h
 =\int_{\Omega_f}V\overline u\,J_hv_h\,\pi\,dx.
 \tag{8.2}
\]

Thus

\[
 \begin{split}
 |R_{h,\rm kill}(u;v_h)|
 \le\bigl[
 &\|K_h^{pc}\|_\infty
   \|J_hP_hu-u\|_2\\
 &+\|K_h^{pc}-V\|_2\|u\|_\infty
 \bigr]\|J_hv_h\|_2.
 \end{split}
 \tag{8.3}
\]

In quotient dimension three, the fixed rectangular boxes have a finite
uniform Sobolev constant

\[
 \|u\|_\infty\le C_{\rm emb}\|u\|_{H^2(\Omega_f)}.
 \tag{8.4}
\]

Use Eqs. (3.5), (3.9), (7.2), and (7.5), together with
\(h\le h^{1/2}\) on the tail (5.5).  Then

\[
 \boxed{
 |R_{h,\rm kill}(u;v_h)|
 \le C_{\rm kill}h_f(n)^{1/2}
 \|u\|_{H^2(\Omega_f)}\|v_h\|_{1,h},}
 \tag{8.5}
\]

where one admissible symbolic composition is

\[
 C_{\rm kill}
 =e^{\Lambda_*H_*/2}
 \left[
 C_KC_P+
 C_{\rm emb}\{C_{K,\rm cut}+C_{K,\rm map}\}
 \right].
 \tag{8.6}
\]

Round 9 places a separate budget factor \(B\) in front of this unit-field
residual.  No value of \(B\) is present or selected here.

Equation (8.5), combined with the Round-10 free residual, supplies the two
half-order residual premises used by the conditional Round-11 sector
composition for the ideal source-defined tails.  It does not authenticate
the discrete production rates or promote the conditional Round-11
resolvent display to a production C2 result.

## 9. Adversarial checklist

The proof depends on each of the following, and none may be silently removed:

1. **Vertex endpoints:** dual endpoint cells have half volume, but
   representative distance is still at most \(h/2\); only an \(O(h)\)
   uniform \(\rho\) claim is made.
2. **Wrapped periodic cells:** they are lifted as connected torus cells;
   \(\Phi_Y=0\), their mass ratio is exactly one, and the contact tube is
   kept away from the seam.
3. **Finite-family uniformity:** every constant is a maximum/minimum over
   exactly twelve frozen boxes.
4. **Sharp indicator:** no derivative or trace of
   \({\bf1}_{D_a}\) is used.
5. **Tube formula:** \(4\pi_{\rm circ}a\delta\) is invoked only after
   \(\delta<a\), \(a+\delta<W/2\), and strict \(R\)-box clearance.
6. **Profile:** both \(\Psi_*\) and \(L_\Psi\) follow from the frozen bump
   shape and the real simplex, not from a concrete control.
7. **Normalization:** \(V\) contains \(W^{-1}\), the periodic mass sum is
   \(S_Y=W\), and \(\pi\) is globally normalized without box conditioning.
8. **Map domain:** \(J_hP_h-I\) has an \(O(h)\) bound from \(H^1\) to
   \(L^2(\pi)\), not in operator norm on all of \(L^2(\pi)\).
9. **Production boundary:** the geometry receipt is not a same-member
   mass/rate/flux/gauge/map/killing receipt.

## 10. Exact verdict

This note establishes, for the ideal formula-defined common tail of the
twelve genuine sequences:

```text
rho tensor exp(+/- Lambda h) enclosure             = PROVED SYMBOLICALLY
J and P source-uniform norm bound                   = PROVED SYMBOLICALLY
P J - I operator defect O(h)                        = PROVED SYMBOLICALLY
J P u - u H1-to-L2 defect O(h)                      = PROVED SYMBOLICALLY
profile physical-volume averaging error O(h)        = PROVED SYMBOLICALLY
weighted sharp cut-layer error O(h^(1/2))            = PROVED SYMBOLICALLY
K L-infinity and K-V mixed half/first-order bounds  = PROVED SYMBOLICALLY
Round-9 killing residual O(h^(1/2))                 = PROVED SYMBOLICALLY
```

It does not establish:

```text
numerically evaluated theorem constants             = FALSE
level-zero production correlated containment        = FALSE
production same-member map/killing receipt          = FALSE
concrete control or positive budget                  = FALSE
complete C0 / C1 / C2 / C3                          = FALSE
continuum box exhaustion or root transfer            = FALSE
F0 / F1 / science / release / submission             = FALSE
```

The canonical validator independently reconstructs the exact source hashes,
rational box margins, and common mesh tail.  Its analytical payload is an
exact **string contract** for the displayed inequalities; it is not an
independent numerical backend or a machine proof of the functional analysis.
A separate human mathematical referee remains mandatory after any repair.
Only after that review may this lemma be cited as closing the **ideal
source-bound** Round-11 inputs.  Production C2 remains a separate
correlated-member obligation.
