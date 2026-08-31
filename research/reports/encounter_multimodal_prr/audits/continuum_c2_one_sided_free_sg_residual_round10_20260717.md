# Round 10 audit: one-sided free SG residual and sharp half-order boundary

Date: 2026-07-17

Status: **IDEAL FREE RESIDUAL THEOREM CANDIDATE PASS / MUTATION-PREFLIGHT
P1 REPAIRED / NEUTRAL FIXTURE 137/137 PASS / GLOBAL HALF ORDER SHARP /
COMPLETE C2 FALSE**

## 1. Audited successor

The Round-10 theory successor is

- `notes/continuum_c2_one_sided_free_sg_residual_candidate.md`;
- 614 lines, 15,643 bytes;
- SHA-256
  `ba3d41da0f16ab4ceb0f2f0c8eceeb29214b0b5b765c9300f373a3513bb21fc4`.

It closes the Round-9 one-sided **free** residual premise for the ideal
analytic refinement family.  It does not edit the theorem-first manuscript,
restore the refuted tensor-`Q1` all-pairs route, or assert a complete C2 rate.

Two local mathematical attacks covered complementary parts of the proof.
The first checked the complete cell-centred, periodic, vertex, tensor, and
scope chain.  The second separately attacked the constant-mode lower bound,
the exact spectator mass cancellation, Jensen, and asynchronous scaling.
Both report

```text
P0=0 / P1=0 / P2=0
```

The final note changed only its status line after those attacks.  A final
exact-byte closure check confirmed that this did not change a mathematical or
scope claim.

The first final fixture audit then found one P1 in the mutation harness.  Its
original loop treated every nonzero independent-verifier exit as a successful
mutation rejection.  Invoked with the system Python, the verifier failed at
`import scipy`, yet all 29 mutations could be printed as PASS.  The receipt
was therefore false-positive-capable even though the same suite happened to
exercise the semantic paths under the repository `.venv`.

The repaired harness is fail-closed in three ways:

1. it first requires the unmodified canonical artifact to finish with
   `SUMMARY 107/107 PASS`;
2. every mutation must exit exactly one and contain an explicit validator
   `ERROR` line, with no `SUMMARY`; and
3. traceback, `ModuleNotFoundError`, and `ImportError` markers are forbidden
   as rejection evidence.

Under the repository `.venv`, the repaired suite passes 30/30, counting the
baseline preflight plus 29 mutations.  Under the dependency-incomplete system
Python it now stops at the baseline and cannot print a mutation PASS summary.
The independent auditor rechecked the repaired bytes before final closure.

## 2. Exact one-axis residual identity

For a reflected OU axis, the continuum operator and flux are

\[
 Au=-\pi^{-1}(d\pi u')',
 \qquad F=d\pi u'.
\]

For `u` in the operator domain and the exact-adjoint map

\[
 (P_hu)_i=m_i^{-1}\int_{C_i}u\pi,
\]

cellwise integration gives

\[
 R_h(u;v_h)
 =\sum_e E_e(u)(\overline v_{e,+}-\overline v_{e,-}),
\]

\[
 E_e(u)=c_e\{(P_hu)_{e,+}-(P_hu)_{e,-}\}-F(s_e).
\]

The signs include the two endpoint contributions correctly.  They vanish
only under the Neumann operator-domain traces.  Bare `H2` without those
traces would leave endpoint functionals that do not satisfy the stated
energy-dual rate.

Weighted Cauchy--Schwarz reduces every alignment to

\[
 |R_h(u;v_h)|
 \le\left(\sum_e|E_e(u)|^2/c_e\right)^{1/2}
       \mathfrak a_h(v_h,v_h)^{1/2}.
\]

## 3. Cell-centred exact gauge cancellation

On a cell-centred quadratic-OU axis, substitution of the ideal gauged mass
and common conductance gives the exact face identity

\[
 F_j^h=\frac d{h^2}
 \{B(-s_j)U_j-B(s_j)U_{j-1}\},
 \qquad U_i=\int_{C_i}u\pi.
\]

The global gauge cancels; no separately estimated `rho-1` term is required.
With `f=pi*u`, the Bernoulli identity yields

\[
 F_j^h/d=a(s_j)D_hf+\Phi'(y_j)M_hf,
 \qquad a(s)=\frac{s}{2}\coth(s/2).
\]

Triangular-kernel integral remainders, `a(s)-1=O(h^2)`, the conductance lower
bound `c_j>=c_*/h`, and overlap two give

\[
 \sum_j|F_j^h-F_j|^2/c_j\le Ch^2\|u\|_{H^2}^2.
\]

Therefore the cell-centred ideal residual is `O(h)`.  The generic first-order
boundary defect in the older centre-sampling form-recovery calculation is a
different object and does not contradict this exact control-volume result.

## 4. Periodic base and half shift

The periodic theorem uses the normalized ideal quantities

\[
 m_i=h/W,
 \qquad c=d_y/(Wh),
 \qquad (P_hu)_i=h^{-1}\int_{C_i}u.
\]

Its face defect is the triangular-average derivative error, giving an
`O(h)` energy-dual residual from `H2(T_W)`.  On the half-shift family, the
wrapped cell is split into its two stored segments; periodic traces cancel at
the seam.  The raw builder mass `h` may not be substituted for the normalized
mass `h/W`.

## 5. Vertex-dual upper bound and sharpness

The endpoint half volumes imply

\[
 \rho_0=1-\Phi'(\ell)h/4+O(h^2),
 \qquad
 \rho_N=1+\Phi'(r)h/4+O(h^2),
\]

while interior ratios are `1+O(h^2)` and every conductance is comparable to
`1/h`.  Interior faces contribute `O(h^2)` to the squared face-dual norm.
The two boundary-adjacent face defects are only `O(1)`, so their inverse-
conductance weights contribute `O(h)`.  Hence

\[
 |R_h(u;v_h)|
 \le Ch^{1/2}\|u\|_{H^2}\|v_h\|_{1,h}.
\]

This loss is not a weak proof artefact.  For the smooth constant mode,
`Au=0` but `P_h1=rho`, and

\[
 E_{1/2}(1)\to d\pi(\ell)\Phi'(\ell)/4\ne0.
\]

An endpoint spike has residual `Theta(1)` and norm `Theta(h^(-1/2))`, giving
a dual lower bound `Theta(sqrt(h))`.  Therefore every uniform exponent
greater than one half is false for the current exact-adjoint map and declared
alignment union.  Extra smoothness or mixed derivatives cannot repair a
constant-mode obstruction.

## 6. Tensor slicing and asynchronous spacings

For axis `k`, let `M_-k,j` be the physical spectator-cell mass and let
`bar u_k,j` be the physical conditional average.  The full projection obeys

\[
 P_hu=\rho_{-k,j}P_{k,h}\bar u_{k,j},
 \qquad m_{-k,j}\rho_{-k,j}=M_{-k,j}.
\]

Consequently the tensor residual decomposes exactly as

\[
 R_{h,\mathrm{free}}(u;v_h)
 =\sum_k\sum_jM_{-k,j}
 r_{k,h}(\bar u_{k,j};v_{h,j}).
\]

There is neither a missing nor a duplicated spectator `rho`.  Conditional
Jensen for the pure derivatives `partial_k^q`, `q=0,1,2`, supplies the full
bound without mixed derivatives.  If `h=max_k h_k<=1`, then every first-order
axis term and every vertex half-order term is bounded by `h^(1/2)`.  No
aspect-ratio factor occurs.

The Round-9 checkerboard does not reappear because the first argument is a
regular continuum conditional average, not an arbitrary high-frequency
discrete vector.

## 7. Neutral reproducibility fixture

The final fixture files are:

| role | path | SHA-256 |
|---|---|---|
| builder | `code/continuum_c2_one_sided_free_residual_neutral_fixture_v1.py` | `1dd8984382a7f32a9cee8ffbe63939dbd844292d9e04d387acb0534455ed3f34` |
| canonical artifact | `artifacts/data/continuum_c2_one_sided_free_residual_neutral_fixture_v1.json` | `93364229ec1495f1fbb15f0319bfd85a7da44c4821c2a5b925e1bf8ac1ad80c7` |
| independent verifier | `code/test_continuum_c2_one_sided_free_residual_neutral_fixture_v1.py` | `892842ff7996d1f64961af30d5bf2a64b44bae4522f4c9bc33675aaa4765927b` |
| mutation verifier | `code/test_continuum_c2_one_sided_free_residual_neutral_fixture_mutations_v1.py` | `43011a2b851b014d06536c20ba6fdf9d109b3ad61f1b33743bb163519ac21335` |

The artifact has 396 lines and 15,900 bytes.  It uses 256-bit MPFR
arithmetic and exports deterministic binary64 hexadecimal summaries in
canonical sorted JSON.  The builder rejects overwrite and its check mode
regenerates the exact bytes without writing.

The final executable results are

```text
builder --check       PASS / output_not_written=true
independent verifier  107/107 PASS
mutation verifier      30/30 PASS
Ruff                    PASS
total counted          137/137 PASS
```

The independent verifier recomputes the Gaussian moments, physical masses,
SG conductances, exact-adjoint projections, periodic Fourier residuals, and
vertex endpoint limits without calling the builder's row functions.

Observed smooth-probe orders are diagnostic only:

```text
cell-centred last pair       1.9990379853
periodic base last pair      1.9992178630
periodic half shift          1.9992178630
periodic translation gap    0 exactly in exported bytes
vertex constant last pair   0.5263304794 -> 1/2
```

The roughly second-order smooth cell/periodic rows do not promote the proved
uniform theorem beyond `O(h)`.  The vertex rows, analytic endpoint limit, and
increasing `residual/h^0.75` mutation check enforce the sharp half-order
boundary.

## 8. Scope and verdict

Every complete-C1/C2/C3, production member, production receipt, continuum
rate, science, release, and submission flag is false.  The only positive
artifact flag records neutral one-dimensional scaling verification.  The
fixture contains no control, killing field, budget, reaction time, root,
topology, or production centre.

The audit verdict is

```text
ideal one-sided free residual theorem candidate = ACCEPT
uniform exponent alpha=1/2                      = ACCEPT AND SHARP
neutral reproducibility fixture                 = ACCEPT
production/evaluator binding                    = HOLD
source-bound killing and map constants          = HOLD
complex-sector H2 and contour growth             = HOLD
complete C2 / C3 / release                       = FALSE
```

The honest next continuum step is the mixed Neumann-periodic complex-sector
`H2` graph estimate and its contour growth, followed separately by genuine
production source binding and an independent acceptance receipt.  The
theorem-first manuscript remains unchanged at seven main plus twenty-four
Supplemental physical pages.
