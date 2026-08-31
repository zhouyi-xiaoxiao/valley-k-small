# Round 17: independent weak-budget/free-exposure artifact audit

Date: 2026-07-13  
Auditor role: independent adversarial numerical/mathematical audit  
Production-edit rule: no production code, manifest, protocol, or result artifact was modified

## Verdict

- **Declared artifact scope: PASS.**  The saved calculation supports a
  result-informed, fixed-mesh, zero-budget derivative design diagnostic.
- **Continuum/finite-budget/PRR promotion: HOLD.**  It does not establish a
  positive-`B` Doi cusp, mesh convergence, a continuum cusp, a continuously
  exhaustive simplex statement, trimodality, an independent PDE solver, or a
  passed project gate.
- Severity counts: **P0 = 0, P1 = 0, P2 = 0**.

The safe headline is:

> On the fixed `65 x 65 x 49` finite-volume quotient, the `B=0`
> free-exposure derivative has a nondegenerate interior cusp and a nearby
> local maximum--minimum--maximum stationary-root pattern.

The words “continuum cusp,” “finite-budget cusp,” and “trimodal phase” are not
supported by this artifact.

## Audited inventory and hashes

| item | SHA-256 | audit result |
|---|---|---|
| `artifacts/data/continuum_weak_budget_design_manifest.json` | `b912aa5d9d6cd21601bab8ec847670b28934a20887319872571ed014622d5949` | matches saved result provenance |
| `code/continuum_weak_budget_design.py` | `7fa9ea6114328736c89739459c293aefa9311514764ec3cfe4f0ceb5a1875201` | matches saved result provenance |
| `artifacts/data/continuum_weak_budget_design_result.json` | `dcbfb9c9ccee4378a8ceeebe00be01de0bf5c5db7914b83032333e066439369f` | audited result |
| `code/test_continuum_weak_budget_design.py` | `1d13b6cfcfbf80426610b9d77c0c0349d765b5c5b06cfb70c6afae8af3f79492` | audit-pinned here |
| `notes/weak_budget_design_protocol.md` | `fdde0374ee931337875574443ebdfe9b2fffb914923dac779c1ea16f6712be57` | matches saved result provenance |
| pinned G1a artifact | `a0a1894dbe6dd37bad6973ca6f3dd29b651441f7b911a5406186bb86a18fd3c3` | matches manifest and result |
| pinned G1a producer | `e0322b212e466b1b640f5adcf30d67d119d2f6fe4cc622eb532082b6cd251701` | matches manifest and result |

The formal rerun used the repository `.venv` (Python 3.12.13, NumPy 2.5.1,
SciPy 1.18.0).  Its JSON was exactly equal to the saved result after removing
only the deliberately variable `provenance.generated_utc` field.  In
particular, the channel-curve digest reproduced as
`e91e25145232c092c162e6d39a95cff74c79402d9134f56a076b849061ae2e68`.

## Mathematical-definition audit

For the row-generator convention used by the code, write

\[
 Q_B=Q_0-BV_w,
 \qquad
 f_B(t)=p_0e^{tQ_B}\,B V_w\mathbf 1.
\]

Then the product rule at `B=0` gives

\[
 \left.\partial_B f_B(t)\right|_{B=0}
 =p_0e^{tQ_0}V_w\mathbf 1=:H_w(t).
\]

There is no omitted semigroup-sensitivity term at first order because that
term is multiplied by the explicit terminal factor `B`.  For a right
observable vector `v`,

\[
 \partial_t^n\bigl(p_0e^{tQ_0}v\bigr)
 =p_0e^{tQ_0}Q_0^n v,
\]

so the producer's generator-action orientation and derivative order are
correct.  At `B=0`, the free generator, initial law, and each channel
observable factor as a Kronecker sum/product.  Hence

\[
 h_j^{(n)}(t)=\sum_{q=0}^{n}{n\choose q}
 a_j^{(q)}(t)c^{(n-q)}(t)
\]

is exact for this discrete quotient.  The midpoint observable contains the
required `1 / transverse_width` factor; the frozen width equals one.  Since
each midpoint patch integrates to one and the control weights sum to one,
this is the derivative per unit full installed budget.

## Cusp, positive null weight, fourth derivative, and unfolding

The producer solves a strict sign bracket for the row-normalized version of

\[
 D(t)=\det\bigl[h_j^{(r)}(t)\bigr]_{r=1,2,3;\,j=1,2,3}.
\]

Row normalization has a strictly positive denominator and therefore cannot
create or change a determinant zero.  At the reported root:

- `t_* = 9.447750380547092`;
- bracket values are `0.06172107301896969` and
  `-0.05030318593895972`;
- the raw determinant is `-4.593964033862178e-18`;
- raw derivative-matrix singular values are
  `(0.05190531871476075, 0.014649409133730598,
  6.042217842193655e-15)`, so the first three derivative rows have rank two,
  not rank one;
- the reported positive affine null weight is
  `(0.34413181348516925, 0.2642370731628536,
  0.39163111335197714)`.

As an independent null-vector check, I did not use the producer's SVD.  I
solved the first two derivative equations together with `sum(w)=1`.  This gave

`(0.3441318134851854, 0.2642370731627879,
0.39163111335202666)`,

with maximum difference `6.573e-14` from the saved weight and residuals
`(1.735e-18, -4.337e-18, -3.735e-15)` against the three derivative rows.
The density per unit budget is positive (`0.16618063735017263`).  The scaled
`H'`, `H''`, and `H'''` residuals are at most `1.694e-11`, while
`t_*^4 H'''' / H = -17.396960403479653`, decisively nonzero.

In coordinates `(w_left,w_middle)` with
`w_right=1-w_left-w_middle`, the independently reconstructed raw unfolding
matrix is exactly the saved matrix,

\[
 J=
 \begin{pmatrix}
 -0.07048712873303015 & -0.02090579292405239\\
  0.006760467110317259 & -0.015440720346713621
 \end{pmatrix},
\]

with `det(J)=0.0012297049682876808`.  Its dimensionless singular-value ratio
is `0.45621977875602643`, its row-angle sine is
`0.9922766558739565`, and its rank is two.  Thus the two control directions
unfold `(H',H'')` transversely.

The frozen inward step gives the three roots
`8.3664995667` (maximum), `9.4477503805` (minimum), and
`10.7079212861` (maximum).  I scanned the entire declared interval
`[0.5,80]`, not just the local cusp window, for this exact off-grid perturbed
weight.  These are the only sign-changing stationary roots.  There is no
unreported remote third maximum in the current geometry.

## Derivative-order and factorization cross-checks

The saved low-grid reference forms the full `17 x 19 x 13 = 4199` state
Kronecker generator and compares all three channels, derivative orders zero
through four, at times `0,1,5,10`.  The maximum absolute and scaled differences
are respectively

- `7.806635112656002e-15`;
- `7.804865014231881e-15`.

This is a valid algebraic/order/scaling check, but it shares the component
generator assembly, `expm_multiply`, and generator-action helper with the
factorized calculation.  It must **not** be described as an independent PDE
solver.

To attack the remaining circularity risk, I added an audit-only value route:
it evaluates only `p_z exp(tQ_z) phi_j` and `p_r exp(tQ_r) chi`, never consumes
the stored generator-action jet columns, and differentiates an 11-point time
stencil.  At stencil spacing `0.2`, the maximum channelwise relative errors
against orders zero through four were

`(1.96e-16, 4.31e-12, 8.68e-12, 3.45e-7, 4.28e-8)`.

The expected roundoff/truncation tradeoff appeared when the stencil was
halved repeatedly.  This independent value-only check rules out an order
shift, a missing binomial coefficient, and a row/column generator sign error
at the reported cusp.  It does not convert the calculation into an
independent spatial discretization.

## Complete frozen-simplex screen

The enumeration is complete for the declared sampled control grid:

\[
 \#\{(i,j,k)\in\mathbb Z_{\ge0}^3:i+j+k=100\}
 ={102\choose2}=5151.
\]

Using a separately written audit counter on the recomputed channel curves, I
recovered exactly:

| sampled maxima | controls |
|---:|---:|
| 1 | 4696 |
| 2 | 455 |

No retained density mask was noncontiguous, no control was empty, and no
internal near-zero derivative segment was skipped.  A second full 5151-control
scan at `dt=0.005` reproduced the same histogram for derivative zero
tolerances `5e-14`, `5e-13`, and `5e-12`.

This verifies only the declared finite screen.  It does not prove that every
control in the continuous simplex has at most two modes, nor does it prove
interval-exhaustive root counts between time samples.  Most importantly, the
current geometry has **two sampled modes at most** and is not a trimodality
result.  The alternative centres near `(0.37,0.61,0.85)` remain explicitly
unfrozen, result-informed scratch and were not used as evidence here.

## Evidence timing, negative flags, and fail-closed behavior

The manifest, protocol, result, producer docstring, and tests consistently
state
`RESULT_INFORMED_REPRODUCTION_NOT_PREREGISTERED_DISCOVERY`.  The known cusp,
current-geometry maximum mode count, and excluded alternative geometry are all
listed under `known_before_freeze`; no prospective-discovery language remains
in this artifact.

The required flags are preserved both in the manifest and result:

- `continuum_verified = false`;
- `project_gate_passed = false`;
- `finite_B_Doi_cusp_verified = false`.

Three audit-only mutations were rejected before calculation:

1. relabeling the evidence as preregistered discovery;
2. changing `continuum_verified` to true;
3. changing the pinned G1a artifact hash.

The legacy `continuum_...` filename is not used as a scientific claim.  All
substantive text calls the object a discrete/fixed finite-volume quotient and
keeps the continuum flag false.

## Reproducibility checks

The following checks passed:

```text
pytest -q -p no:cacheprovider code/test_continuum_weak_budget_design.py
..... [100%]

ruff check code/continuum_weak_budget_design.py \
  code/test_continuum_weak_budget_design.py
All checks passed!

ruff format --check code/continuum_weak_budget_design.py \
  code/test_continuum_weak_budget_design.py
2 files already formatted
```

The full producer rerun returned

```text
status=PASS_RESULT_INFORMED_WEAK_BUDGET_DESIGN_DIAGNOSTIC
cusp=t=9.44775038055, weights=[0.34413181348516925,
0.2642370731628536, 0.39163111335197714], scaled_f4=-17.397
simplex=controls=5151, max_modes=2
```

## What this evidence can and cannot support

### Supported now

- the exact free-exposure factorization for the declared finite-volume
  quotient;
- a positive interior `B=0` derivative cusp with `H'=H''=H'''=0`,
  `H'''' != 0`, and rank-two two-control unfolding;
- the local bimodal side of that discrete cusp;
- the stated `0.01` sampled-simplex histogram and its audit-only
  `dt=0.005` sensitivity check;
- a concrete target for a separately proved small-positive-budget
  persistence theorem.

### Not supported now

- a cusp for any declared positive installed budget, including `B=0.6`;
- a continuum cusp or mesh-converged mixed jet;
- odd/even mesh stability or a verified discretization error bound;
- an independent finite-element, spectral, or PDE solver result;
- an exhaustive assertion over continuous time or the continuous weight
  simplex;
- trimodality in the current geometry, or any claim based on the excluded
  alternative geometry;
- a physical 3D transition or a passed PRR-level project gate.

## Release decision

No production fix is required for the artifact's declared scope.  The
artifact may be cited as an audited **design diagnostic**, with the negative
flags and result-informed label retained verbatim.  PRR promotion remains on
hold until positive-`B` persistence is quantified, the cusp/mode margins are
mesh-refined and independently solved, and any trimodality statement has five
alternating simple critical points plus the declared prominence/mass/tail
margins.
