# Observable four-patch exact-continuum result

## Evidence boundary

**Status: formal result-informed confirmation, not preregistered discovery.**

The four centres, narrow widths, approximate cusp, and one passing inward
step were known before the protocol was frozen. The formal calculation is
valuable because it applies a predeclared candidate grid and selection rule,
uses direct continuum kernels rather than a state grid, and checks the
project's quantitative observability floors. It is not an interval proof, a
finite-\(B\) killed-Doi result, or a passed project/publication gate.

Frozen files:

| file | SHA-256 |
| --- | --- |
| producer code/continuum_observable_four_patch.py | a553092f3d8bbf50fdf0124a3ea36ba32947c3b339cfcc0265a1cd7f6bc2d4da |
| tests code/test_continuum_observable_four_patch.py | c3a2c11c71daf9fcb04e1db9e7c4e489a515d7dfbbb51bc470d310d0c3f76243 |
| protocol notes/observable_four_patch_protocol.md | cbfb6fbe7b69fb66f3b25f7bcde404929a53cf1e8d2045c5fa037fe0fa8432a1 |
| manifest artifacts/data/continuum_observable_four_patch_manifest.json | 1c79fcb31abbc622cee20e915d60f55337376d7555c1c25dab210b3cc5976a69 |
| result artifacts/data/continuum_observable_four_patch_result.json | 4a929cdaf915a9b6180acc0c272a16ae77087d097f2d078b6483c6c9b320a9fc |

## Main result

For physical \(d=2\) on
\(\mathbb R\times\mathbb T_1\), with \(D=0.002\), longitudinal OU
stiffness \(0.1\), mean \(0.95\), disk-contact radius \(0.16\), initial
half-width \(0.004\), and patch half-width \(0.008\), the four centres are

\[
 (0.35,0.60,0.75,0.90).
\]

On the affine budget slice \(w_0=0.28\), the direct continuum clock bank has
a nondegenerate cusp at

\[
 t_c=13.328031989459639
\]

with weights

\[
 w_c=(0.28,\ 0.2301948478196556,\ 0.2093239647769527,\
       0.2804811874033918).
\]

Its scaled fourth derivative is

\[
 {t_c^4F^{(4)}(t_c)\over F(t_c)}
 =-42.81178483244579,
\]

and the dimensionless unfolding singular-value ratio is
\(0.2564052360511239\). The largest scaled residual in
\(F',F'',F'''\) is \(1.10\times10^{-12}\).

The strict inward normal on the fixed-\(w_0\) slice is

\[
 d=(0,\ 0.357362931876667,\ -0.933965596218893,\
       0.576602664342226).
\]

Its first unfolding projection is numerically zero, while the product of its
second-row projection and the cubic normal-form coefficient is negative, so
the sign is the cusp-inward sign fixed by the protocol.

## Frozen selection rule chose step 0.11

The formal run considered only
\(s=0.02,0.03,\ldots,0.20\). Ten steps, \(0.11\) through \(0.20\),
passed every observability and root gate. The frozen lexicographic rule first
maximizes the smallest catalyst weight, so it selected

\[
 s_*=0.11,\qquad
 w_*=(0.28,\ 0.2695047703260889,\ 0.1065877491928744,\
       0.3439074804810367).
\]

This is important evidence against post-result choice: the known hint was
\(s=0.15\), but the frozen rule selected \(0.11\).

The five refined roots and density values are:

| type | time | density | scaled second derivative |
| --- | ---: | ---: | ---: |
| maximum | 3.204037879399 | 0.205485676850 | -7.61780717 |
| minimum | 5.085467473831 | 0.137014856945 | 12.83424002 |
| maximum | 8.688467026035 | 0.240579863273 | -5.94378375 |
| minimum | 13.328031989460 | 0.200031534136 | 4.41494712 |
| maximum | 22.660102216665 | 0.238831447697 | -2.05960947 |

The quantitative observability ratios are

\[
 {\min(P_1,P_2,P_3)\over\max(P_1,P_2,P_3)}
 =0.8541266673541315,
\]

and

\[
 {V_1\over\min(P_1,P_2)}=0.6667854375339219,
 \qquad
 {V_2\over\min(P_2,P_3)}=0.8375426940831652.
\]

Thus the peak-height floor \(0.10\) and both valley ceilings \(0.85\)
pass. The smaller valley margin is \(0.0124573059\), so the second valley is
observable but not excessively far from the declared ceiling.

## Independent and convergence checks

The primary Cauchy calculation was attacked with an audit-only real
Taylor-jet implementation that did not import the producer. It recovered

- \(t_c=13.3280319894655\);
- \(w_c\) to the displayed precision;
- scaled \(F^{(4)}=-42.8117848284\); and
- unfolding ratio \(0.2564052360515\).

A second producer-free real-derivative calculation at the selected absolute
weights recovered all five root times within \(1.1\times10^{-12}\), and
reproduced the two valley ratios and peak ratio to the displayed digits.

Across the coarse, primary, and fine continuum configurations:

- the largest coarse/fine cusp-time spread is
  \(1.43\times10^{-11}\);
- the largest weight spread, including the dependent fourth weight, is
  \(1.05\times10^{-14}\);
- the primary/fine scaled-fourth-derivative difference is
  \(8.84\times10^{-9}\); and
- the selected absolute weights have identical five-root observability
  metrics on the fine configuration to floating-point precision.

The half-chord disk integral agrees with an 80-node by 512-angle polar disk
quadrature at \(t=1,5,13,25\); the maximum relative discrepancy is
\(6.61\times10^{-15}\). Direct-product Cauchy jets and the factorwise
Leibniz construction agree at order \(10^{-13}\), and the Cauchy first jet
agrees with the closed real derivative at order \(10^{-16}\).

The complete formal run was repeated to a temporary path. The two JSON files
are byte-identical and have the same SHA-256 shown above. All ten focused
tests and Ruff checks pass.

## Claim boundary and next work

The result artifact deliberately states:

- continuum_verified=false;
- finite_B_Doi_verified=false;
- project_gate_passed=false; and
- observable_free_exposure_confirmation_passed=true.

The first three flags remain false because floating-point agreement is not an
interval certificate, the weak-budget theorem does not provide a numerical
positive-\(B\) radius here, no killed-Doi solver has been run at this
geometry, and physical \(d=3\) remains open.

A broader patch variant with half-width \(0.08\) and initial half-width
\(0.02\) was learned before this run and is explicitly excluded in the
manifest. It may be more convenient for later SG/FEM work, but it requires a
separate producer/protocol/manifest/result chain and must not replace or be
merged silently with the narrow-patch confirmation.
