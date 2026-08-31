# One-sided free Scharfetter--Gummel residual on the quotient box

Date: 2026-07-17

Status: **IDEAL-ANALYTIC THEOREM CANDIDATE / TWO LOCAL MATHEMATICAL AUDITS
PASS / SHARP GLOBAL HALF ORDER / COMPLETE C2 FALSE**

## 1. Purpose and claim boundary

Round 9 refuted the standard tensor-product `Q1`, all-discrete-pairs
implementation of the proposed quantitative form comparison.  That negative
result does not apply when the first argument is a regular continuum
resolvent solution.  This note proves the corresponding one-sided
control-volume residual for the ideal analytic free generator.

The result is deliberately narrower than C2.  It proves no source-bound
killing estimate, no sector regularity, no complex contour bound, no
production interval member, no positive-budget science, and no reaction-time
claim.  In particular, it does not change the theorem-first PRR manuscript.

The main conclusion is

\[
 |R_{h,\mathrm{free}}(u;v_h)|
 \le C h^{1/2}\|u\|_{H^2(\Omega_L)}\|v_h\|_{1,h},
 \tag{1.1}
\]

for the declared cell-centred, vertex-dual, periodic-base, and
periodic-half-shift alignment families, with asynchronous spacings and
`h=max_k h_k`.  The function `u` must belong to the free operator domain, so
it has the declared Neumann and periodic traces.  Bare `H2` without those
boundary conditions is not sufficient.

The exponent in (1.1) is generically sharp for the current exact-adjoint map
on a vertex-dual OU axis.  A constant continuum solution already rules out
every uniform exponent greater than `1/2`.  Thus additional smoothness cannot
repair the loss; a better rate would require a different comparison map or an
explicit endpoint correction.

All Hilbert products below are complex sesquilinear when complexified.  The
second factor is conjugated.  Real notation is used where it avoids clutter.

## 2. One-axis flux form

Let `I=[ell,r]`, let `d>0`, and let

\[
 \pi(x)=C e^{-\Phi(x)},\qquad
 A u=-\pi^{-1}(d\pi u')'.
 \tag{2.1}
\]

For an OU axis, `Phi` is quadratic.  The continuum free form is

\[
 \mathfrak a(u,v)=\int_I d u'\overline{v'}\,\pi dx.
 \tag{2.2}
\]

On either reflected mesh, let `C_i` be the actual control volume, `m_i` the
gauged ideal discrete mass, and

\[
 (P_hu)_i=\frac1{m_i}\int_{C_i}u\pi dx.
 \tag{2.3}
\]

This is the exact adjoint of piecewise-constant reconstruction.  It is not
the literal physical cell average unless `m_i` equals the physical cell
mass.

Write `c_e` for the common conductance on an interior edge `e=(i,i+1)` and
`s_e` for the control-volume face between the two nodes.  For

\[
 u\in D(A)=\{u\in H^2(I):u'(\ell)=u'(r)=0\},
 \tag{2.4}
\]

cellwise integration of (2.1) gives the exact identity

\[
 \langle P_hAu,v_h\rangle_h
 =\sum_e F_e(u)(\overline v_{i+1}-\overline v_i),
 \qquad F_e(u)=d\pi(s_e)u'(s_e).
 \tag{2.5}
\]

The exterior fluxes vanish because of (2.4).  Hence

\[
 R_h(u;v_h)
 =\mathfrak a_h(P_hu,v_h)-\langle P_hAu,v_h\rangle_h
 =\sum_e E_e(u)(\overline v_{i+1}-\overline v_i),
 \tag{2.6}
\]

where

\[
 E_e(u)=c_e\{(P_hu)_{i+1}-(P_hu)_i\}-F_e(u).
 \tag{2.7}
\]

Weighted Cauchy--Schwarz reduces the theorem to the face-dual estimate

\[
 |R_h(u;v_h)|
 \le
 \left(\sum_e\frac{|E_e(u)|^2}{c_e}\right)^{1/2}
 \mathfrak a_h(v_h,v_h)^{1/2}.
 \tag{2.8}
\]

The fixed-box weight is smooth and bounded above and below.  All unlabelled
constants below may depend on the fixed interval and frozen OU parameters,
but not on the mesh size or alignment shift.

## 3. Cell-centred reflected OU axis: first order

Let

\[
 x_i=\ell+(i+\tfrac12)h,
 \qquad C_i=[\ell+ih,\ell+(i+1)h].
 \tag{3.1}
\]

For the face `y_j=ell+jh`, put

\[
 U_i=\int_{C_i}u\pi dx,
 \qquad s_j=\Phi(x_j)-\Phi(x_{j-1})=h\Phi'(y_j).
 \tag{3.2}
\]

The last equality is exact for a quadratic potential.  The ideal masses and
conductance are

\[
 m_i=g_hh e^{-\Phi(x_i)},
 \qquad
 c_j=\frac{g_hd}{h}e^{-\Phi(x_{j-1})}B(s_j)
     =\frac{g_hd}{h}e^{-\Phi(x_j)}B(-s_j),
 \tag{3.3}
\]

where `B(s)=s/(exp(s)-1)`.  Substitution of (2.3) into (3.3) cancels the
global gauge exactly:

\[
 F_j^h:=c_j\{(P_hu)_j-(P_hu)_{j-1}\}
 =\frac d{h^2}\{B(-s_j)U_j-B(s_j)U_{j-1}\}.
 \tag{3.4}
\]

Thus no separate `rho-1` or `g_h/C-1` error is needed in this proof.

Set `f=pi*u` and define

\[
 D_hf(y)=\frac1{h^2}
 \left\{\int_y^{y+h}f-\int_{y-h}^yf\right\},
 \qquad
 M_hf(y)=\frac1{2h}\int_{y-h}^{y+h}f.
 \tag{3.5}
\]

The Bernoulli identities

\[
 B(-s)-B(s)=s,
 \qquad
 a(s):=\frac{B(-s)+B(s)}2=\frac{s}{2}\coth\frac{s}{2}
 \tag{3.6}
\]

turn (3.4) into the exact formula

\[
 \frac{F_j^h}{d}
 =a(s_j)D_hf(y_j)+\Phi'(y_j)M_hf(y_j).
 \tag{3.7}
\]

The continuum flux has the matching representation

\[
 \frac{F_j(u)}d=\pi(y_j)u'(y_j)
 =f'(y_j)+\Phi'(y_j)f(y_j).
 \tag{3.8}
\]

The difference quotient in (3.5) is a triangular average of `f'`:

\[
 D_hf(y)=\int_{-h}^h
 \frac{h-|t|}{h^2}f'(y+t)dt.
 \tag{3.9}
\]

For `I_j=(y_j-h,y_j+h)`, one-dimensional integral remainders and
Cauchy--Schwarz give

\[
 |D_hf(y_j)-f'(y_j)|
 \le C h^{1/2}\|f''\|_{L^2(I_j)},
 \tag{3.10}
\]

\[
 |M_hf(y_j)-f(y_j)|
 \le C h^{1/2}\|f'\|_{L^2(I_j)},
 \qquad
 |D_hf(y_j)|
 \le C h^{-1/2}\|f'\|_{L^2(I_j)}.
 \tag{3.11}
\]

Since `s_j=O(h)` uniformly and `a(s_j)-1=O(h^2)`, (3.7)--(3.11)
imply

\[
 |F_j^h-F_j(u)|
 \le C h^{1/2}
 \{\|f''\|_{L^2(I_j)}+\|f'\|_{L^2(I_j)}\}.
 \tag{3.12}
\]

The fixed-box conductance estimate gives `c_j>=c_*/h`, and the intervals
`I_j` have overlap at most two.  Therefore

\[
 \sum_{j=1}^{N-1}\frac{|F_j^h-F_j(u)|^2}{c_j}
 \le C h^2\|u\|_{H^2(I)}^2.
 \tag{3.13}
\]

Equations (2.8) and (3.13) prove

\[
 |R_h(u;v_h)|
 \le Ch\|u\|_{H^2(I)}\mathfrak a_h(v_h,v_h)^{1/2}.
 \tag{3.14}
\]

The boundary half strips omitted by the centre-to-centre interpolant in a
generic form-recovery calculation do not create a residual here.  The
control volumes cover the whole interval, the discrete exterior flux is zero,
and the continuum exterior flux is exactly zero by (2.4).

If the Neumann traces in (2.4) are omitted, the exact summation instead has
the extra terms

\[
 -F(\ell)\overline v_0+F(r)\overline v_{N-1}.
 \tag{3.15}
\]

They are not an `O(h)` energy-dual residual.  The operator-domain boundary
condition is therefore essential.

## 4. Periodic free-diffusion axis: first order

On `T_W`, choose either `sigma_h=0` or `sigma_h=h/2`.  The ideal normalized
mass and conductance are

\[
 m_i=\frac hW,
 \qquad c=\frac{d_y}{Wh},
 \qquad (P_hu)_i=\frac1h\int_{C_i}u.
 \tag{4.1}
\]

For a lifted face `b`, define

\[
 D_hu(b)=\frac1{h^2}
 \left\{\int_b^{b+h}u-\int_{b-h}^bu\right\}.
 \tag{4.2}
\]

Then the exact face defect is

\[
 E_b(u)=\frac{d_y}{W}\{D_hu(b)-u'(b)\}.
 \tag{4.3}
\]

The same triangular-kernel estimate as (3.10) yields

\[
 |D_hu(b)-u'(b)|^2
 \le Ch\int_{b-h}^{b+h}|u''(x)|^2dx.
 \tag{4.4}
\]

Periodic patches overlap a uniformly bounded number of times, so

\[
 \sum_b\frac{|E_b(u)|^2}{c}
 \le Ch^2\|u''\|_{L^2(\mathbb T_W)}^2.
 \tag{4.5}
\]

Consequently both periodic shifts satisfy

\[
 |R_h(u;v_h)|
 \le Ch\|u\|_{H^2(\mathbb T_W)}
       \mathfrak a_h(v_h,v_h)^{1/2}.
 \tag{4.6}
\]

For the base mesh, the modular edge crosses the selected coordinate seam.
For the half-shift mesh, the seam lies inside one wrapped cell.  Splitting
that cell into its two stored segments makes the two traces at `0` and `W`
cancel by periodicity.  No seam residual is added, and the constants in
(4.5) are independent of the shift.

The normalization in (4.1) is mandatory.  The axis builder's raw mass `h`
becomes `h/W` through the ideal tensor gauge.  Substituting the raw mass into
`P_h` would make `rho` non-unit and would not prove this theorem.

## 5. Vertex-dual reflected OU axis: sharp half order

Let

\[
 x_i=\ell+ih,
 \qquad
 \nu_0=\nu_N=h/2,
 \qquad \nu_i=h\quad(1\le i\le N-1),
 \tag{5.1}
\]

and let `C_i` be the corresponding endpoint-half or interior-full dual cell.
Put

\[
 M_i=\int_{C_i}\pi,
 \quad
 A_i u=M_i^{-1}\int_{C_i}u\pi,
 \quad
 \rho_i=M_i/m_i,
 \quad
 (P_hu)_i=\rho_iA_i u.
 \tag{5.2}
\]

The ideal axis estimates are

\[
 c_e\asymp h^{-1},
 \qquad
 \frac{hc_e}{d\pi(s_e)}=1+O(h^2),
 \tag{5.3}
\]

\[
 \rho_0=1-\frac{\Phi'(\ell)}4h+O(h^2),
 \qquad
 \rho_N=1+\frac{\Phi'(r)}4h+O(h^2),
 \tag{5.4}
\]

and `rho_i=1+O(h^2)` uniformly over interior vertices.  Decompose the face
defect as

\[
 E_e=E_e^A+E_e^\rho,
 \tag{5.5}
\]

\[
 E_e^A=c_e(A_{i+1}u-A_i u)-d\pi(s_e)u'(s_e),
 \tag{5.6}
\]

\[
 E_e^\rho
 =c_e\{(\rho_{i+1}-1)A_{i+1}u
        -(\rho_i-1)A_i u\}.
 \tag{5.7}
\]

For an interior full dual cell, its weighted average differs from its
unweighted average by at most `C h^2 ||u'||_infinity`.  Differences of
adjacent unweighted dual averages again have the triangular-kernel
representation (3.9).  Equations (5.3), the one-dimensional embedding
`H2 -> C1`, and bounded overlap therefore give

\[
 \sum_{e\ \mathrm{not\ adjacent\ to}\ \partial I}
 \frac{|E_e(u)|^2}{c_e}
 \le Ch^2\|u\|_{H^2(I)}^2.
 \tag{5.8}
\]

Only the two boundary-adjacent faces need the weaker estimate.  The endpoint
half-cell geometry, (5.3)--(5.4), and `H2 -> C1` give

\[
 |E_{1/2}(u)|+|E_{N-1/2}(u)|
 \le C\|u\|_{H^2(I)}.
 \tag{5.9}
\]

Since the inverse of either boundary conductance is `O(h)`, (5.8)--(5.9)
give

\[
 \sum_e\frac{|E_e(u)|^2}{c_e}
 \le Ch\|u\|_{H^2(I)}^2.
 \tag{5.10}
\]

Thus

\[
 |R_h(u;v_h)|
 \le Ch^{1/2}\|u\|_{H^2(I)}
       \mathfrak a_h(v_h,v_h)^{1/2}.
 \tag{5.11}
\]

The endpoint half volumes are not optional.  Their outgoing directed rates
are twice the equal-volume rates, while multiplication by the endpoint half
mass restores the common conductance in (5.3).  Deleting that volume factor
breaks finite-volume balance rather than improving (5.11).

### 5.1 A smooth sharpness obstruction

Take `u=1`.  Then `u` is smooth, satisfies both Neumann traces, and `Au=0`,
but exact adjointness gives

\[
 P_h1=\rho.
 \tag{5.12}
\]

For the first interior vertex, `rho_1=1+O(h^2)`.  Equations (5.3)--(5.4)
therefore imply

\[
 E_{1/2}(1)
 =c_{1/2}(\rho_1-\rho_0)
 \longrightarrow
 \frac{d\pi(\ell)\Phi'(\ell)}4.
 \tag{5.13}
\]

The fixed-box hypothesis places the OU mean strictly inside the interval, so
`Phi'(ell)` is nonzero.  Choose the endpoint spike `v_0=1`, `v_i=0` for
`i>=1`.  Then

\[
 |R_h(1;v_h)|=|E_{1/2}(1)|=\Theta(1),
 \qquad
 \|v_h\|_{1,h}=\Theta(h^{-1/2}).
 \tag{5.14}
\]

It follows that

\[
 \sup_{v_h\ne0}
 \frac{|R_h(1;v_h)|}{\|v_h\|_{1,h}}
 \ge c h^{1/2}.
 \tag{5.15}
\]

No uniform estimate with exponent greater than `1/2` can hold for the
current map and alignment family.  The counterexample is constant, so
`H^{2+s}`, analytic regularity, and mixed derivatives cannot change this
conclusion.

## 6. Exact tensor slicing and asynchronous meshes

Let the quotient box be the product of its two reflected OU axes and one
periodic free-diffusion axis.  The ideal mass, free generator, and maps are
product objects.  For an axis `k` and a spectator multi-index `j_-k`, define
the physical spectator mass and average

\[
 M_{-k,j}=\int_{C_{-k,j}}\pi_{-k},
 \qquad
 \bar u_{k,j}(x_k)
 =\frac1{M_{-k,j}}
   \int_{C_{-k,j}}u(x_k,x_{-k})\pi_{-k}(x_{-k})dx_{-k}.
 \tag{6.1}
\]

Although the full exact-adjoint projection uses discrete spectator masses,

\[
 (P_hu)_{i_k,j}
 =\rho_{-k,j}(P_{k,h}\bar u_{k,j})_{i_k},
 \qquad
 m_{-k,j}\rho_{-k,j}=M_{-k,j}.
 \tag{6.2}
\]

The spectator map defect and global gauge therefore cancel exactly in each
axis form.  If `r_{k,h}` denotes the one-axis residual (2.6), then

\[
 R_{h,\mathrm{free}}(u;v_h)
 =\sum_k\sum_{j_{-k}}M_{-k,j}
 r_{k,h}(\bar u_{k,j};v_{h,j}).
 \tag{6.3}
\]

Equation (6.3) is the tensor mechanism.  There is no tensor-`Q1`
interpolant, no spectator factor `3^{-(d-1)}`, and no all-discrete-pairs
claim.

Physical conditional averaging and Jensen give, for `q=0,1,2`,

\[
 \sum_{j_{-k}}M_{-k,j}
 \|\partial_k^q\bar u_{k,j}\|_{L^2(\pi_k)}^2
 \le\|\partial_k^q u\|_{L^2(\pi)}^2.
 \tag{6.4}
\]

Apply the one-axis bounds to (6.3), use Cauchy--Schwarz in the spectator
index, and use uniform comparability of `M_-k` and `m_-k` for the test energy.
This gives

\[
 |R_{h,\mathrm{free}}(u;v_h)|
 \le C\left(\sum_k h_k^{2\alpha_k}
 \|u\|_{L^2(\Omega_{-k};H^2(I_k))}^2\right)^{1/2}
 \|v_h\|_{1,h},
 \tag{6.5}
\]

where `alpha_k=1` on cell-centred and periodic axes and `alpha_k=1/2` on a
vertex-dual axis.  Ordinary `H2(Omega_L)` is more than sufficient; no mixed
derivative is used in (6.4).

For `h=max_k h_k<=1`, every `h_k^alpha_k<=h^{1/2}`.  Therefore (6.5) proves
(1.1) without any ratio `h_i/h_j`.  The same constant covers asynchronous
families.  The Neumann or periodic operator-domain traces pass to the
spectator averages in (6.1).

Along a synchronous family containing a vertex-dual reflected axis, the
constant-mode obstruction (5.15), tensored with constants in the spectator
directions, proves that the global exponent `1/2` is also sharp.

## 7. Relation to the Round-9 error equation

For the continuum resolvent solution `u` and discrete solution `u_h`, Round 9
established the exact error equation

\[
 \mathfrak b_{h,c,\lambda}(u_h-P_hu,v_h)
 =-R_{h,\mathrm{free}}(u;v_h)
  -B R_{h,\mathrm{kill}}(u;v_h).
 \tag{7.1}
\]

This note closes only the free residual premise in (7.1) for the ideal
analytic member.  Combined with the still-open source-bound killing estimate
and sector `H2` regularity, (1.1) has exactly the conservative half order
needed by the proposed positive-time Dunford route.

The checkerboard obstruction does not recur: the first residual argument is
the regular partial average (6.1), while the arbitrary discrete test is
absorbed by the face-dual Cauchy--Schwarz estimate (2.8).

## 8. What remains open

This theorem candidate does not establish any of the following:

1. a machine-readable production refinement member whose gauged masses and
   common conductances enclose the ideal member at every `h`;
2. source-bound constants for `J_hP_h`, contact cut layers, and reconstructed
   killing;
3. mixed Neumann-periodic `H2` regularity for the shifted complex continuum
   resolvent, uniformly in the control family;
4. rotated discrete sector coercivity, contour constants, or integrable
   resolvent growth;
5. an operator-norm semigroup or positive-time observable rate;
6. C2, C3, F0, production science, release, or submission eligibility.

The current production builder stores outward intervals for ungauged
primitives and may choose unrelated binary64 centres.  This note applies only
to the ideal gauged, exactly reversible analytic form.  Evaluator enclosure
and production binding remain separate obligations.

The next mathematical step is therefore not to strengthen the exponent.  It
is to prove the source-bound mixed-boundary complex-sector `H2` estimate and
freeze its growth along the Dunford contour, while separately constructing a
genuine production member and independent acceptance receipt.

## 9. Freeze statement

```text
cell-centred reflected ideal free residual      = PROVED CANDIDATE, O(h)
periodic base ideal free residual               = PROVED CANDIDATE, O(h)
periodic half-shift ideal free residual         = PROVED CANDIDATE, O(h)
vertex-dual reflected ideal free residual       = PROVED CANDIDATE, O(sqrt(h))
vertex-dual exponent greater than one half      = REFUTED BY CONSTANT MODE
asynchronous tensor residual                    = PROVED CANDIDATE, O(sqrt(h))
extra mixed derivatives required                = FALSE
operator-domain boundary traces required        = TRUE
production interval/evaluator binding           = OPEN
source-bound killing residual                   = OPEN
complex-sector H2 and contour growth             = OPEN
complete C2 / C3 / release                       = FALSE
```
