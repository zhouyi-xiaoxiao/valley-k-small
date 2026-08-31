# Verified semigroup enclosure for the full-window modal certificate

Date: 2026-07-14  
Status: **GO-METHOD / HOLD-PRODUCTION-INTEGRATION / HOLD-F1-SCIENCE**  
Scope: numerical method, small synthetic chains, and the already known
historical control only; **no prospective LP control was evaluated at positive
budget**.

## 1. Decision

The reference enclosure should be a structure-preserving **uniformization**
calculation in the induced `l1` norm, with:

1. the killed generator defined from nonnegative off-diagonal rates and killing,
   rather than trusting a rounded stored diagonal;
2. directed-MPFR Poisson weights and an explicit Poisson-tail bound;
3. a binary64 sparse-action, reduction, coefficient, underflow, and time ledger;
4. contraction-based accumulation of state error over sequential chunks; and
5. separately enclosed generator actions and pairwise scalar reductions for
   `F'`, `F''`, `F'''`, `M_2`, and `M_3`.

This resolves the **method-existence** part of the numerical P0: there is now a
concrete fail-closed route whose proof uses the same sub-Markov `l1` contraction
as the finite-window certificate.  It does not authorize F1.  The current
matrix-free FV evaluator does not yet implement this rate-defined/outward
kernel, the exact-rational control intervals, or the production JSON ledger.

Reference prototype:

| file | SHA-256 |
|---|---|
| `code/verified_uniformization_enclosure.py` | `a4646f946b891133c972f62cd36a1cb177516793050c2b6e520cffceb57782ed` |
| `code/test_verified_uniformization_enclosure.py` | `6b842112f71bf88d8447a88ccba21ef1d9cbe89676912e80789e7ce964acbe34` |
| `notes/submarkov_interval_certificate_design.md` | `65a9cc177396f925bddbd8cc8ef36515de2e1c0f763fa6694aad38488430f335` |

## 2. Exact target and rounded centre

For one finite FV configuration, define the mathematical row generator from
the rate stencil:

\[
 q_{ij}=r_{ij}\ge 0\quad(i\ne j),\qquad
 q_{ii}=-\sum_{j\ne i}r_{ij}-d_i,\qquad d_i\ge0.
\]

The rates and killing can initially be exact dyadic values represented by
binary64 inputs, or intervals enclosing the exact FV coefficients.  The key
point is that the diagonal is the **mathematical sum above**.  It is not an
independently rounded byte which is later assumed to make the row sum
nonpositive.

The prototype builds a binary64 centre `Qhat` with the diagonal rounded toward
minus infinity and returns

\[
 \delta_Q\ge\|(Q-\widehat Q)^T\|_1
 =\|Q-\widehat Q\|_\infty.
\]

Both the target and centre are killed generators.  For a rate
`lambda >= max_i(-Qhat_ii)`, define

\[
 P=I+Q/\lambda,\qquad \widehat P=\operatorname{fl}(I+\widehat Q/\lambda).
\]

Then `P` is row-substochastic and

\[
 \delta_P\ge\|(P-\widehat P)^T\|_1
 \le {\delta_Q\over\lambda}+\delta_{P,\mathrm{coeff}},
\]

where the second term encloses binary64 construction of the centre.  The
prototype computes the latter exactly with dyadic `Fraction` arithmetic.  A
production tensor implementation must derive the same bound from the bounded
rate stencil without materializing millions of rational objects.

### 2.1 Why the existing diagonal cannot simply be accepted

A method-only check of the already known historical `N=33` control formed the
current explicit CSR generator (`35,937` states, `247,203` nonzeros).  An
ordinary binary64 row reduction reported:

```text
maximum row sum       = 2.876171523169546e-15
rows reported positive = 19,786
```

More importantly, the exact-dyadic preflight rejected the first genuinely
positive exact row sum.  Thus the present `expm_multiply` operator is useful as
an approximation, but its stored diagonal is not a valid premise for the exact
sub-Markov certificate.  Rebuilding the diagonal from rates plus killing gave

```text
delta_Q = 1.7741884350552795e-15
```

and the centre then passed the exact structural preflight.  This is a numerical
proof issue, not a change of the physical model.

## 3. Uniformization state enclosure

For column state `p'=Q^T p`, exact uniformization gives

\[
 e^{hQ^T}p
 =\sum_{j=0}^\infty w_j(x)(P^T)^jp,
 \qquad x=\lambda h,
 \qquad w_j(x)=e^{-x}{x^j\over j!}.
\]

Let `xhat_j` be the binary64 recurrence using `Phat^T`, and suppose

\[
 \|x_j-\widehat x_j\|_1\le e_j.
\]

Let `nu` be the maximum number of entries in a row of the stored transpose
kernel, `rhat` an outward upper bound on the maximum centre row sum, `u=2^-53`,
`gamma_k=ku/(1-ku)`, and `eta=2^-1074`.  For the pinned CSR accumulation model,

\[
 e_{j+1}\le e_j+
 \delta_P\|\widehat x_j\|_1+
 \gamma_{2\nu}\,\widehat r\,\|\widehat x_j\|_1+
 N(2\nu+1)\eta.
\]

The important feature is the absence of a factor `N` in the relative-error
term: summing all nonnegative incoming contributions gives at most the total
row-substochastic mass.  `N` occurs only in the negligible absolute-underflow
allowance.

Suppose directed computation gives

\[
 w_j\in[\underline w_j,\overline w_j],\qquad
 |w_j-\widehat w_j|\le r_j,qquad
 \sum_{j>K}w_j\le\tau.
\]

For an exact state-mass cap `M` and the sequential binary64 accumulator
`yhat`, the prototype records the outward bound

\[
\begin{split}
 \|e^{hQ^T}p-\widehat y\|_1\le{}&
 \tau M
 +\sum_{j=0}^{K}\overline w_j e_j
 +\sum_{j=0}^{K}r_j\|\widehat x_j\|_1\\
 &+\gamma_{2(K+1)}
   \sum_{j=0}^{K}|\widehat w_j|\|\widehat x_j\|_1
 +N(2K+3)\eta.
\end{split}
\]

All scalar products and sums on the right are themselves formed with one-step
outward multiplication and addition, rather than applying one `nextafter` to a
long expression.

Because the exact semigroup is an `l1` contraction, the output radius becomes
the input radius of the next chunk without amplification.  Chunk endpoints are
exact `Fraction` partitions of the binary64 target time; their sum is checked
for exact equality, so repeated floating subtraction does not create an
unrecorded time displacement.

## 4. Directed Poisson layer

`gmpy2 2.2.1` supplies MPFR directed rounding.  For each exact rational mean
`x`, the prototype computes lower and upper enclosures for `exp(-x)` and then
recurs outward through

\[
 w_{j+1}=w_j{x\over j+1}.
\]

Once `x/(K+2)<1`, the remaining tail is bounded geometrically by

\[
 \sum_{j=K+1}^{\infty}w_j
 \le {\overline w_{K+1}\over 1-\overline x/(K+2)}.
\]

The calculation therefore does not assume that platform `libm exp` is
correctly rounded.  The current reference starts at `j=0` and caps each mean at
`500`; this keeps `exp(-x)` above binary64 underflow while MPFR still supplies
the proof.  A later Fox--Glynn implementation may reduce weight-generation
work or permit larger chunks, but it must retain a directed normalization and
tail ledger.  Fox and Glynn's original algorithm specifically targets
rigorously truncated, overflow/underflow-safe Poisson probabilities for
uniformizable chains: <https://web.stanford.edu/~glynn/papers/1988/FG88.html>.

## 5. Scalar derivatives and local `M_r`

At an enclosed anchor state define

\[
 z_r=(Q^T)^rp,
 \qquad F^{(r)}=k^Tz_r.
\]

For centre actions `zhat_{r+1}=fl(Qhat^T zhat_r)`, the action error obeys

\[
 e^{(z)}_{r+1}\le
 (\|\widehat Q^T\|_1+\delta_Q)e^{(z)}_r
 +\delta_Q\|\widehat z_r\|_1
 +\delta_{\mathrm{sparse},r}.
\]

Here `||Qhat^T||_1` is the maximum exact-dyadic absolute row sum of `Qhat`, and
the sparse roundoff term uses the same `gamma_(2 nu)` construction as the
state recurrence.

The prototype uses an explicit deterministic pairwise tree for every dense dot
and `l1` norm.  With tree depth `ell=ceil(log2 N)`, a dot-product radius uses
`gamma_(ell+1)` times an outward absolute-product sum, plus the absolute
underflow allowance.  If `delta_k` encloses the killing field in `l_infinity`,

\[
 |k^Tz_r-\widehat k^T\widehat z_r|
 \le \|k\|_\infty e^{(z)}_r
      +\delta_k\|\widehat z_r\|_1
      +\delta_{\mathrm{dot},r}.
\]

The local contraction constant is enclosed by

\[
 \widehat M_r^{\,+}
 =(\|\widehat k\|_\infty+\delta_k)
  (\|\widehat z_r\|_1^{+}+e^{(z)}_r).
\]

These are exactly the scalar/state ingredients required by the complement-sign
and root-box-curvature inequalities in
`notes/submarkov_interval_certificate_design.md`.

## 6. Runtime assumptions are gates, not prose

The prototype fail-closes unless it observes:

- IEEE binary64 with 53-bit significand;
- C `FE_TONEAREST` on the pinned macOS runtime;
- preserved subnormal multiplication/addition; and
- preserved subnormals through the actual SciPy CSR kernel.

Every relative bound also carries an absolute `eta` term.  MPFR precision is at
least 96 bits (192 bits in the executed reference), and a Poisson term cap,
nonfinite value, negative nominal probability, structural failure, or tail
failure raises `VerificationFailure`.

## 7. Comparison of the three candidate routes

| route | mathematical possibility | current repository decision |
|---|---|---|
| a posteriori Arnoldi/Krylov defect in `l1` | valid in principle: contraction gives `||e(h)||_1 <= ||e(0)||_1 + integral ||z'-Q^Tz||_1`; potentially much faster for stiff large grids | **secondary accelerator only**; the current code has no outward finite-precision Arnoldi relation, no certified projected exponential/defect integral, and no basis/reduction roundoff ledger |
| uniformization with directed Poisson and scaled chunks | positivity, truncation, coefficient perturbation, and sparse roundoff all live naturally in the same `l1` norm | **reference method selected**; proof prototype and synthetic tests pass, production tensor integration still held |
| rational/resolvent/contour | for `Re(z)>0`, the contraction generator gives a useful resolvent bound; verified residuals could certify shifted solves | **not selected**; no frozen high-order rational/contour error on the full left half-plane, no directed quadrature, and no certified million-state shifted solves/preconditioner |

### 7.1 Why a reported Krylov residual is not yet enough

For computed Arnoldi bytes one would need an outward relation

\[
 Q^TV_m=V_mH_m+h_{m+1,m}v_{m+1}e_m^T+R_m
\]

and a certified integral of the full finite-precision defect.  The usual small
projected residual does not include `R_m`, construction of `V_m`, the projected
matrix exponential, or the quadrature of its absolute value.  Rigorous
defect-based upper bounds do exist in the literature, but they do not make an
ordinary SciPy call self-certifying; see Jawecki, Auzinger, and Koch,
<https://arxiv.org/abs/1809.03369>.  An eventual Krylov implementation should
be checked against this uniformization reference on small and historical
configurations before it may replace it.

### 7.2 Why the current `expm_multiply` tolerance is not a certificate

The existing evaluator follows the Al-Mohy--Higham scaling/Taylor family.  Its
backward-error design is excellent for ordinary numerical work, but the
present certificate needs a saved **forward scalar/state enclosure**, including
all generator and reduction rounding.  The underlying algorithm is described
in <https://doi.org/10.1137/100788860>; replica agreement or a small backward
error alone does not supply the required forward interval.

### 7.3 Why backward Euler/resolvent products are not the fallback

`(I-hQ^T)^(-1)` is positive and contractive, but the Erlang/backward-Euler
approximation is only low order for a fixed deterministic time.  Achieving the
small derivative radii needed here would require too many verified linear
solves.  Higher-order signed/complex rational approximants lose the immediate
sub-Markov `l1` proof and would require a new contour and shifted-solve audit.

## 8. Executed method-only evidence

The tests use one-state death, two-state birth-and-killing, seeded small killed
chains, exact rational dot products, deliberate generator mutations, exact
time partitioning, insufficient Poisson caps, and a mean-500 Poisson tail.

```text
../../../.venv/bin/python -m pytest -q -ra -p no:cacheprovider \
  code/test_verified_uniformization_enclosure.py
12 passed

../../../.venv/bin/python -m ruff check \
  code/verified_uniformization_enclosure.py \
  code/test_verified_uniformization_enclosure.py
All checks passed!

../../../.venv/bin/python -m ruff format --check \
  code/verified_uniformization_enclosure.py \
  code/test_verified_uniformization_enclosure.py
2 files already formatted
```

### 8.1 Historical `N=33` feasibility diagnostic

Only the already known historical control and its existing manifest were used.
No topology, new control, or publication claim was assessed.

```text
states                         35,937
nonzeros                       247,203
lambda                         12.064562872168926
target delta_Q                 1.7741884350552795e-15
total delta_P                  1.846795399724636e-16
exact-Fraction preflight       2.24 s

t=0.5:
  Poisson mean / terms         6.032281436084463 / 39
  propagation wall time        0.0101 s
  state l1 radius              1.9325602351572947e-14
  scalar radii r=0..3          8.20e-14, 2.14e-12, 5.20e-11, 1.26e-9

t=35:
  Poisson mean / terms         422.2597005259124 / 615
  propagation wall time        0.114 s
  state l1 radius              8.398977312689668e-13
  scalar radii r=0..3          3.56e-12, 8.61e-11, 2.08e-9, 5.01e-8
```

The `M_r` upper bounds at `t=0.5` reproduce the prior method-diagnostic
magnitudes (`M_1=7.3702`, `M_2=22.4420`, `M_3=105.8917`) after outward padding.
This is a consistency check only.

Historical rates read without changing a control were:

| cubic cells | `lambda` | `35 lambda` |
|---:|---:|---:|
| 33 | `12.064562872168926` | `422.2597005259124` |
| 65 | `41.18376980152154` | `1441.431943053254` |
| 113 | `119.09178809484058` | `4168.21258331942` |

For a chunk with mean `x`, work is `O((x+tail_width) nnz(Q))` and storage is
`O(N+nnz(Q))`; over sequential anchors the leading number of transition
actions is approximately `lambda*T` plus one Poisson-tail width per anchor.
The tiny `N=33` timing must not be linearly advertised as a production
benchmark.  Nevertheless, `35 lambda` in the low thousands on the historical
meshes shows that the method is not automatically impossible.  The 12-grid,
36-row F1 workload and the `7,165,305`-state `MR+F` row still require a
matrix-free benchmark and frozen resource ceiling.

## 9. Production integration contract

Before any positive-budget LP control is evaluated, F0 must implement and
independently attack all of the following:

1. **Rate-defined tensor kernel.** Generate off-diagonal SG/FV rates and
   killing intervals directly; derive the diagonal and `delta_Q` outward.
   Never certify the old independently rounded diagonal by a tolerant row-sum
   comparison.
2. **Target coefficient intervals.** Enclose exact-rational control weights,
   support integrals, contact fractions, initial law, cell volumes, and every
   rate.  Feed their induced operator radius into `delta_Q`/`delta_P`.
3. **Matrix-free nonnegative action.** Implement `Phat^T x` on the tensor
   factors with a frozen maximum incoming degree and a proved operation count.
   The small explicit CSR prototype is the oracle, not the production storage
   format.
4. **Initial-state certificate.** Save an `l1` interval and an exact mass cap
   for the normalized FV initial law.  `exact_mass_cap=1` is an assertion that
   needs its own source hash.
5. **Deterministic reductions.** Use the explicit pairwise tree (or a stronger
   independently proved reducer) for every scalar and norm.  A library `sum`
   with undocumented order is insufficient.
6. **Machine-readable ledger.** For every anchor save exact time numerator and
   denominator, rate, chunk means, `K`, MPFR precision/runtime hashes, tail,
   coefficient, sparse-action, weight, accumulation, state, generator-action,
   dot, `M_r`, and final interval margins.
7. **Mutation suite.** Flip Metzler signs, make one row super-stochastic,
   understate `delta_Q`, lower `lambda`, corrupt a Poisson endpoint/tail,
   change rounding mode, flush subnormals, omit a time subinterval, and exceed
   term/depth/resource caps.  Every mutation must return the frozen HOLD code.
8. **Scaled benchmarks.** Pass synthetic exact chains, explicit small FV
   matrices, the historical `N=33` oracle, at least one larger historical
   matrix-free row, and an independent implementation audit.  Freeze maximum
   wall time, memory, Poisson terms, anchors, and output radius before F1.

The production solver may use a certified Krylov path as an accelerator only
if it saves a complete defect ledger and the frozen selector chooses it before
any prospective-control value is read.  Uniformization remains the reference
fallback and small-grid oracle.

## 10. Gate result

```text
sub-Markov state/error derivation                  PASS
directed Poisson/tail construction                 PASS
binary64 sparse/reduction/underflow ledger         PASS IN PROTOTYPE
exact-rational time closure                        PASS
generator-action/scalar/M_r enclosure              PASS IN PROTOTYPE
synthetic and historical-method diagnostics        PASS
ordinary stored FV diagonal as exact killed Q      FAIL (rebuild required)
production tensor/rational-control integration     OPEN P0 FOR F1
36-row / largest-grid resource feasibility         OPEN P1
prospective positive-budget LP evaluation          NOT AUTHORIZED
```

The numerical route is now specific enough to implement without choosing a
new tolerance after seeing F1.  The scientific gate remains closed until the
production integration, schema, mutations, scaled benchmark, and independent
audit pass.
