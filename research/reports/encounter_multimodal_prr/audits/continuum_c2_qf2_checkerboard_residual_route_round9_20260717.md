# Round 9 audit: QF2 checkerboard obstruction and residual-route repair

Date: 2026-07-17

Status: **STANDARD TENSOR-Q1 ALL-PAIR ROUTE REFUTED / EXACT FIXTURE PASS /
REGULAR-SOLUTION RESIDUAL ROUTE CONDITIONAL / C2 FALSE / C3 FALSE**

## 1. Audited successor

The frozen theory successor is

- `notes/continuum_c2_qf2_checkerboard_and_residual_route_candidate.md`;
- 608 lines, 17,472 bytes;
- SHA-256
  `4b20189814c763816ea707630ff098c98995afd7d3207808225a320a742508c2`.

It does not edit or silently supersede the audited Round-7 bytes.  Instead, it
resolves an ambiguity in the open QF2 obligation by attacking the standard
tensor-product nodal `Q1` all-discrete-pairs implementation.  That
implementation is false.  The successor then formulates a one-sided
regular-continuum-solution residual route that remains conditional.

## 2. Exact checkerboard obstruction

For an even periodic grid on the unit `d`-torus, constant density, unit
diffusion, and

```text
v_j=(-1)^(j_1+...+j_d),
```

the exact lumped discrete quantities are

\[
 \|v\|_h^2=1,
 \qquad \mathfrak a_h(v,v)=4d h^{-2}.
\]

On every cell, the standard tensor-`Q1` interpolant factorizes as

\[
 I_hv=\pm\prod_{k=1}^d(1-2\xi_k).
\]

Since the squared one-dimensional factor integrates to `1/3`,

\[
 \|I_hv\|_2^2=3^{-d},
 \qquad
 \mathfrak a(I_hv,I_hv)=4d\,3^{-(d-1)}h^{-2}.
\]

Consequently an all-pairs estimate

\[
 |\mathfrak a_h(u_h,v_h)-
   \mathfrak a(I_hu_h,I_hv_h)|
 \le C h\|u_h\|_{1,h}\|v_h\|_{1,h}
\]

would require

\[
 C\ge
 \frac{4d(1-3^{-(d-1)})}{h(h^2+4d)}
 \sim\frac{1-3^{-(d-1)}}h.
\]

For the physical quotient dimension `d=3`, the exact defect is
`32/(3h^2)` and the required constant grows as `8/(9h)`.

## 3. Declared mixed boundary alignment

The theorem note separately verifies that the obstruction persists for the
actual vertex-dual Neumann times vertex-dual Neumann times periodic alignment.
Endpoint half masses sum exactly to one; the alternating one-dimensional
piecewise-linear interpolant has `L2` norm squared `1/3`; and both its graph and
continuum one-dimensional energies equal `4/h^2`.  Tensor spectator masses
therefore reproduce the factor `3^{-(d-1)}` exactly.

For asynchronous even spacings `h_k`, the graph and continuum energies are

\[
 4\sum_kh_k^{-2},
 \qquad
 4\,3^{-(d-1)}\sum_kh_k^{-2},
\]

so the required constant still diverges as `1/h` for `h=max_k h_k`.  This
constant-density/unit-diffusion mixed-boundary calculation is a mathematical
obstruction to the standard reconstruction; it is not presented as an exact
variable-weight production SG calculation.

## 4. Exact neutral fixture

The final fixture files are:

| role | path | SHA-256 |
|---|---|---|
| builder | `code/continuum_c2_qf2_checkerboard_obstruction_v1.py` | `ca53c6e33c631e115d38d857110d8eaf47a86205d5f3db6ca93529d0b633bdd9` |
| canonical artifact | `artifacts/data/continuum_c2_qf2_checkerboard_obstruction_v1.json` | `40f7c0689343eef0aca0b17a2bc95183cbf8fdca073a6d9a0d4ae1fbaa53c9bf` |
| independent test | `code/test_continuum_c2_qf2_checkerboard_obstruction_v1.py` | `039ba8721ab161c694b34c355517b8a960facb19e89048cfdeabbe5f69b96bbb` |

The artifact contains twelve exact rows for `d=1,2,3` and
`N=2,4,8,16`.  The test independently integrates the tensor-`Q1` polynomial
coefficients rather than calling the builder's closed-form routine.  It also
checks two byte-identical clean builds, no-overwrite behavior, canonical JSON,
the frozen artifact hash, exact enumeration counts, increasing scaled lower
bounds, and all scope flags.

The final executable result is

```text
builder --check   PASS / output_not_written=true
independent test  90/90 PASS
```

An independent exact-byte audit of the three files reports
`P0=0 / P1=0 / P2=0`.

## 5. Exact scope of the negative result

The obstruction refutes only:

```text
standard periodic or declared vertex-dual mixed-boundary nodal tensor Q1
+ exact continuum integration
+ all discrete pairs in the graph H1 norm
+ a mesh-uniform O(h) defect.
```

It does not refute the separate `L2` reconstruction estimate, uniform
graph/`Q1` energy equivalence, mass-lumped reconstructed forms, filtered or
form-preserving maps, or one-sided residual consistency.  The fixture enforces
these nonclaims with exact Boolean false flags.  It also keeps complete C1,
C2, C3, production evidence, and release false.

## 6. Revised residual identity

For shifted complex resolvents, the successor chooses `w_h=P_hu`, where
`P_h=J_h^*` and `u=(A_{c,sigma}+lambda)^-1 f`.  Exact adjointness cancels the
mass term.  Applying `P_h` to the continuum equation gives

\[
 \mathfrak b_{h,c,\lambda}(u_h-P_hu,v_h)
 =-R_{h,\rm free}(u;v_h)-B R_{h,\rm kill}(u;v_h).
\]

The signs and factor `B` are exact.  The free term is now the one-sided
control-volume residual

\[
 R_{h,\rm free}
 =\mathfrak a_{h,\rm free}(P_hu,v_h)
  -\langle P_hA_{\rm free}u,v_h\rangle_h,
\]

not an all-discrete-pairs conforming-form comparison.

For killing, the identities `rho=M_pi/pi_h` and `K=V/rho` give

\[
 R_{h,\rm kill}
 =\int [K_h^{pc}J_hP_hu-Vu]\overline{J_hv_h}\,\pi dx.
\]

Splitting this into `K_h(J_hP_hu-u)+(K_h-V)u`, using the source-bound map
error, the `O(h^(1/2))` cut-layer multiplier error, and the fixed-box
three-dimensional embedding `H2 -> L-infinity` yields the conditional bound

\[
 |R_{h,\rm kill}(u;v_h)|
 \le C h^{1/2}\|u\|_{H^2}\|v_h\|_{1,h}.
\]

Only the regular continuum solution needs `L-infinity`; the arbitrary
discrete test needs only `L2`.  Thus the revised killing residual does not use
QF1's discrete `L4` inequality.

## 7. Open premises and sector transfer

The following are explicit premises, not conclusions:

- an `O(h^alpha)`, `alpha>=1/2`, free SG residual for `P_hu` on every
  cell/vertex/periodic alignment and asynchronous family;
- a source-bound `J_hP_h` approximation and reconstructed killing error;
- complex-sector weighted mixed-boundary `H2` regularity;
- rotated discrete sector coercivity with frozen contour constants; and
- integrable growth of the reconstructed sector-resolvent constant.

If these hold, the exact error equation and reconstruction triangle include
the moving-range complement and give the conditional operator-norm rate

\[
 \|J_h(A_{h,c,\sigma}+\lambda)^{-1}P_h
 -(A_{c,\sigma}+\lambda)^{-1}\|
 \le C_{sec}(\lambda,L)h^{1/2}.
\]

The note explicitly maps `lambda=-z` before reusing the audited Round-7
`z-A_sigma` Dunford step.  It does not assert the contour rate, extend it to
`t=0`, or infer it from qualitative Mosco convergence.

## 8. Audit verdict and next decision

An independent exact-byte mathematical audit of the frozen 608-line note
checked the periodic formulas, endpoint-half-mass mixed extension,
asynchronous spacings, residual signs, scope flags, and all open-premise
wording.  It reports

```text
theory and scope audit: P0=0 / P1=0 / P2=0
```

This is a local hash-specific audit, not external referee acceptance.

The honest next route is:

```text
prove the one-sided free SG/control-volume residual
  -> prove source-bound mixed-boundary sector H2 regularity
  -> freeze discrete sector coercivity and contour growth
  -> obtain the reconstructed resolvent rate
  -> reuse the positive-time Dunford bridge.
```

QF1 remains a useful independent inequality but is not critical to this
revised killing-residual route.  Complete C1/C2/C3, production binding,
release, and submission remain false.  The theorem-first manuscript remains
unchanged at seven main plus twenty-four Supplemental pages.
