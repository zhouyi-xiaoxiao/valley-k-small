# Round 03, reviewer A: remediation recheck

Date: 2026-07-11

Verdict: **PASS within the declared GIG-screening scope**

All four findings in `reviewer_a.md` are substantively resolved. During this
recheck I found one new large-\(AB\) failure in the first log-normalization
revision; the remediation replaced the invalid unconditional \(B\to0\)
fallback by separate small- and large-argument branches. I independently
falsified that repair against 100-digit quadrature/Bessel values and found no
remaining discrepancy in the stated parameter family or the new stress
domain.

The audited working-tree base remains
`3531353a515160b09899199a9257e7455a654b22`. The relevant rechecked snapshots
were:

- manuscript: `60ac24a5ed2b277049ad9361c44b9db944d14f8f825fbcedea2bc99bf1e62091`;
- `notes/gig_fold_derivation.md`:
  `76b4bd28531950f014340f81cf18c65c166576b8c322cef87d1cb1b76e75048b`;
- `notes/multid_gig_channel_design.md`:
  `986ff7d7d46a4040f97cf2d808a18f66252fc8c58d861cd3d4a6ef77088a9501`;
- `code/validate_gig_fold.py`:
  `3fcb7240c2f113589017d8bd2251c5d1dd8889980ce562bba75da2dc68084292`;
- `code/validate_multid_gig_design.py`:
  `be7a750ad6eb66745ebc8591096d8bbee2571a9e2b4221571c68620a77355aad`;
- `artifacts/data/gig_fold_summary.json`:
  `5802066c97a757cf651b809f166674a643046f6f5669f2677ed1e5d054e7ed1c`;
- `artifacts/data/multid_gig_design_summary.json`:
  `4cf5c5b9aea62c28a6294f0d65be8e7915d34197aa4bed7892930b3732a6e059`;
- focused tests: `test_encounter_gig_fold.py`
  `365126eb570d4a4440d2ea3d1746b59f1be95908a9c0b34f19a6a1191ea4bd5`
  and `test_encounter_multid_gig_design.py`
  `513abb1d07719a259a81bb345d2508223d55645c7e63fd50eafc6d331e2a51f6`.

The report, code, tests, and artifacts are untracked in an already dirty
working tree, so these hashes identify the actual rechecked files more
precisely than the base commit.

## Finding-by-finding disposition

### F1 — PASS: CTMC comparison modes are continuous semigroup-derivative roots

The revised implementation brackets sign changes only on a deterministic
grid, then solves

\[
\alpha e^{Tt}T b_j=0
\]

with Brent's method, verifies negative curvature, records a dimensionless
first-derivative residual, and selects the largest detected
negative-curvature maximum (`validate_gig_fold.py:392-484`). The artifact is
generated from this routine (`:1079-1084,1141-1151`), not from the old sampled
argmax.

An independent implementation using raw `expm_multiply`, \(Qb_j\), and
\(Q^2b_j\), followed by a separate bounded optimizer, reproduced:

| channel | derivative root | second derivative | scaled first residual | optimizer difference |
|---|---:|---:|---:|---:|
| near | `32.1534061543058` | `-3.816148507521187e-6` | `1.65e-15` | `1.08e-7` |
| far | `196.1458700069696` | `-7.728636606794438e-7` | `1.96e-14` | `2.65e-6` |

The saved mode times differ from those independent roots by only
`9.24e-14` and `3.04e-12`. The resulting errors are
`0.1759202035` and `0.0813479529`, hence `17.6%` and `8.1%` at the precision
printed in the manuscript. The revised text states both the root method and
values (`manuscript/encounter_modality_jcp.tex:831-840`), and the regression
explicitly rejects the old `32.0`/`196.0` grid values
(`tests/test_encounter_gig_fold.py:87-108`).

### F2 — PASS: the \(B=0\) normalizability condition is explicit and enforced

The manuscript now states

\[
Z=A^{1-\nu}\Gamma(\nu-1)\quad\text{only for }\nu>1,
\]

and separates the positive stationary point \(A/\nu\), valid for \(\nu>0\),
from the mode of a normalized density
(`manuscript/encounter_modality_jcp.tex:629-634`). The derivation note says the
same (`notes/gig_fold_derivation.md:78-98`).

Both numerical implementations reject \(B=0,\nu\le1\):
`GIGChannel.__post_init__` at `validate_gig_fold.py:78-91` and the vectorized
normalizer at `validate_multid_gig_design.py:89-100`. Independent calls with
\(\nu=1,0.5,-2\) all raised `ValueError`; \(B=0,\nu=3.5\) agreed with
\((1-\nu)\log A+\log\Gamma(\nu-1)\) to `2.1e-17`.

### F3 — PASS: the distance map states and enforces its physical feasibility domain

The manuscript now gives the general map

\[
|z_j-R_0|=\sqrt{4D_c(A_j-A_{\rm rel})},
\qquad A_j\ge A_{\rm rel}=\ell^2/(4D_r),
\]

and specializes it to \(Bm_j^2+pm_j\ge1/4\), including the minimum-mode
thresholds and the fact that all tested clocks satisfy them
(`manuscript/encounter_modality_jcp.tex:1334-1343`). The multidimensional note
records the same condition and says the validator enforces it
(`notes/multid_gig_channel_design.md:70-98`).

The constructor checks positivity and \(A_j\ge1/4\) before taking a square
root, raising a descriptive `ValueError` otherwise
(`validate_multid_gig_design.py:130-150`). Independent tests at
\(m_{\min}(1\pm10^{-10})\) in all four dimensions accepted the upper point
and rejected the lower point. The reproduced thresholds were:

```text
d=1  0.124921972503933
d=2  0.09996003196803827
d=3  0.08331019803633488
d=4  0.07141400011596577
```

Zero and negative modes were also rejected. The saved summary exposes both
the feasibility equation and all four thresholds.

### F4 — PASS: the drift cross factor and its role in weights are explicit

The manuscript now fixes the sign convention and prints

\[
\exp\!\left[
\frac{\ell u}{2D_r}
+\frac{(z-R_0)\cdot v_c}{2D_c}
\right],
\]

stating that it cancels from a normalized conditional shape but contributes
to the physical, channel-dependent splitting amplitude
(`manuscript/encounter_modality_jcp.tex:605-611`). It repeats the consequence
for physical realization of the designed weights (`:1355-1360`). Both theory
notes make the same distinction
(`notes/gig_fold_derivation.md:46-68`;
`notes/multid_gig_channel_design.md:114-120`).

An independent vector-valued expansion gave a residual of
`1.11e-16` between the two Gaussian exponents and
\(-A/t-Bt+\ell u/(2D_r)+\delta\cdot v_c/(2D_c)\). The signs and interpretation
are therefore correct.

## Log-normalization and log-sum-exp adversarial recheck

### Large-\(AB\) regression found and closed

The first revision treated every non-finite `kve` result as a small-\(B\)
event and substituted the \(B=0\) normalizer. This was false when
\(x=2\sqrt{AB}\) was large enough for SciPy's `kve` to return `nan`. For
\((A,B,\nu)=(10^{12},10^6,3/2)\), \(x=2\times10^9\), the correct value is

```text
log Z = -2000000013.243145615...
```

whereas that intermediate revision returned `-13.243145615...`.

The current code closes the failure in both scalar and vectorized paths:

- for \(x\ge10^5\), it evaluates
  \(\log(e^xK_\alpha(x))\) with four terms of the DLMF 10.40.2
  large-\(x\) expansion;
- only an unresolved \(x<10^{-6}\), \(\nu>1\) evaluation may use the
  \(B\to0\) limit;
- every unresolved intermediate case raises rather than silently changing
  asymptotic regime
  (`validate_gig_fold.py:44-112`;
  `validate_multid_gig_design.py:54-121`).

Independent 100-digit `mpmath` checks covered
\(p=1.5,2,2.5,3,3.5\) at
\(x=99999,100000,100001,2\times10^9\). The maximum error in
\(\log(e^xK_{1-p}(x))\) was `1.34e-15`, including both sides of the branch
threshold. The original counterexample now returns
`-2000000013.2431457`, an absolute log error `8.9e-8`; the corresponding
\((A,B,p)=(10^{20},0.01,3.5)\) check has error `3.2e-8`.

The fixed-\(B\) multidimensional stress construction
`construction(4, (1e11,))` now returns:

```text
A       = 1.0000000035e20
x       = 2.0000000035e9
log Z   = -2000000076.6103582
log peak density = -15.5391678810
score at target  = 1.73e-18
f''/f at target  = -2.0000000035e-13
```

The peak no longer underflows because of a wrong normalizer. Exact
half-integer checks were added for both the scalar \(K_{1/2}\) and vectorized
\(K_{5/2}\) branches
(`tests/test_encounter_gig_fold.py:57-84`;
`tests/test_encounter_multid_gig_design.py:68-99`).

### Log-sum-exp mixture algebra passes

The revised mixture computes channel log components, their `logsumexp`,
posterior component fractions, \(f'/f\), and \(f''/f\)
(`validate_multid_gig_design.py:179-201`). This is algebraically equivalent to
direct summation but remains defined when raw channel densities have very
different scales.

Independent high-precision checks found:

- for the paper family \(d=4\), clocks \((1,10,100,1000)\), maximum errors in
  `log Z`, log weights, log mixture, score, and second ratio were between
  `1.1e-22` and `5.9e-15`;
- for stress clocks \((1,10^3,10^6)\), log-normalizer/log-weight errors were
  at most `3.2e-12`, and all mixture scores and second ratios remained finite;
- on the fixed family, a direct non-log implementation and the log-sum-exp
  path agreed to binary64 precision; and
- an independent 300,001-point scan over \([10^{-5},10^7]\), using raw Bessel
  normalizers rather than the production log path, again found exactly
  `3,5,7` alternating roots for every two-, three-, and four-channel case in
  all four dimensions, with positive/negative derivative tail signs.

No log-normalization or log-sum-exp error remains in the declared family or
the newly tested stress cases.

## Executed checks

```text
uv run pytest -q \
  tests/test_encounter_gig_fold.py \
  tests/test_encounter_multid_gig_design.py \
  tests/test_encounter_manuscript.py
# 14 passed

PYTHONPATH=packages/vkcore/src uv run python - <<'PY'
# Independently solved alpha exp(Tt) T b_j=0, evaluated Q^2 b_j,
# and cross-checked each maximum with minimize_scalar.
PY

PYTHONPATH=packages/vkcore/src uv run python - <<'PY'
# Compared scalar/vector log normalizers and the large-x branch with
# 100-digit mpmath Bessel values for five orders and four x regimes.
PY

PYTHONPATH=packages/vkcore/src uv run python - <<'PY'
# Compared log weights, log mixture, f'/f, and f''/f with an independent
# mpmath implementation for the paper and stress families.
PY

uv run python - <<'PY'
# Read the saved parameter CSV, independently rebuilt raw Bessel channels,
# scanned 300001 log points on [1e-5,1e7], and Brent-refined all sign changes.
PY
```

The focused tests also verify the regenerated artifact manifests. No
scientific source, artifact, test, or manifest was modified by this reviewer;
this recheck file is the only output.

## Retained not-certified boundary

PASS applies to the exact GIG-family algebra, its numerical implementation,
the continuous CTMC comparison, and the declared finite 12-case
multidimensional screening family. It does not certify:

1. a universal physical exponent \(p=(d+3)/2\) after tangential integration;
2. a uniform finite-patch or reflected-path remainder on a mode-containing
   window;
3. a bounded-domain finite-radius Doi realization of the three- or four-mode
   screening mixtures;
4. physical realization of the inverse-height splitting weights; or
5. interval-certified exclusion of tangent/even-multiplicity derivative
   roots outside the sign-scan roots.

Those limitations remain explicit in the manuscript and artifacts. Within
that boundary, Round 03 Reviewer A is closed with **PASS**.
