# Exact rational modal-selector design

Date: 2026-07-14  
Stage: **science-free B0 selector method**  
Decision: **PASS finite rational LPs / HOLD continuum coefficient certificate / HOLD F0 control compatibility / NO positive-B authorization**

## 0. Purpose and hard boundary

This note defines a deterministic replacement for the solver-native tie
handling in the exploratory modal-certificate LP.  The implementation is

```text
code/modal_certificate_exact_selector.py
```

and its tests are

```text
code/test_modal_certificate_exact_selector.py.
```

The producer imports only the Python standard library.  It does not import or
execute the continuum kernel, NumPy, SciPy, HiGHS, a killed generator, a
positive-budget finite-volume row, or an off-lattice process.  It enumerates
vertices of three finite LPs whose coefficients are frozen finite decimal
strings.

The word **exact** in this note has one narrow meaning:

> every input decimal is interpreted as an exact rational number, and every
> linear solve, feasibility residual, objective comparison, and tie break in
> that finite rational LP is exact.

It does **not** mean that the source binary64 quadrature values are exact or
outward interval enclosures of the continuum derivatives.  Therefore this
artifact cannot close the full-window box-and-complement gate in Theorem 3.1
and cannot authorize positive-`B` work.

## 1. Pinned source boundary

At the implementation freeze used for the method result, the relevant inputs
were:

| object | SHA-256 | role |
|---|---|---|
| `code/modal_certificate_lp_poc.py` | `4920411d65f85653cdec16da206a19d7a8eb42610b6d01936ceae41ec3a6ae6e` | exploratory source of the LP convention only |
| `scratch/modal_certificate_lp_poc_result.json` | `6f04ef4c618677d6d26b80cd04e3d4f8c9918fd50a649cfc0dd0bf064ccce604` | exploratory comparison values only |
| `notes/modal_certificate_theory_and_prr_redirect.md` | `38dde114552d0cea69f714d7493d3cb6715e1b4ed436431045a50a57360326be` | theorem and claim boundary |
| `notes/positive_b_fixed_control_robustness_design_v1.md` | `891b49a3b9efbfa93c27c09e4f585a088b40f079c3ff5642536764f1523698d7` | already frozen F0 controls to which compatibility must be checked |

The frozen coefficient decimals are the shortest round-trip decimal
representations of the ordinary binary64 values

```text
a_lj = sign_l d_lj / max_j |d_lj|
```

obtained from the already explored `FourPatchContinuum(PRIMARY,
broad_parameters())` calculation at the listed B0 checkpoints.  The selector
producer itself never recomputes those values.  Recomputing the quadrature at
run time would make “exact selector” depend again on environment and floating
solver bytes, which this design deliberately avoids.

## 2. Frozen rationalized coefficient tables

Every row below is already sign-adjusted: a feasible positive margin requires
`a_l dot w >= rho`.  The row scale is stored separately so that the artifact
can report the reconstructed raw signed margin `sigma_l a_l dot w`.

### `m1`

```text
times   = (5.5, 12.0)
scales  = (0.2674801474024189,
           0.11213730751238601)
rows    = ((-0.6593397434471837, 1.0,
             0.04057643049449547, 4.293408212312281e-05),
           ( 0.005908164154451627, 1.0,
            -0.5316894021563535, -0.4412050300032699))
floor   = 0.03 exactly
table SHA-256 = 20f8ed31ab95a20f14b66a42325cebe0991f265a886cf28374ad568328065afc
```

### `m2`

```text
times   = (2.0, 5.5, 16.0, 35.0)
scales  = (0.554048268115002,
           0.2674801474024188,
           0.06072999278484658,
           0.005587099274431895)
rows    = (( 1.0, 1.1603546024409161e-05,
              1.3855853269321413e-12, 1.9616636844203973e-22),
           ( 0.6593397434471842, -1.0,
             -0.040576430494495476, -4.2934082123122815e-05),
           (-0.0004475615149088995, -0.5744836141548475,
             -0.7637944413288659, 1.0),
           ( 1.339325051000316e-06, 0.046511727711955726,
              1.0, 0.7262071720607719))
floor   = 0.03 exactly
table SHA-256 = bf2b117a3cbfdcc712030abcc353631f3dd366f539f51152234ab2713f05168c
```

### `m3`

```text
times   = (2.0, 5.0, 6.5, 11.0, 17.0, 35.0)
scales  = (0.554048268115002,
           0.22974144714713002,
           0.23845731109916096,
           0.12927504142810492,
           0.05394093798151121,
           0.005587099274431895)
rows    = (( 1.0, 1.1603546024409161e-05,
              1.3855853269321413e-12, 1.9616636844203973e-22),
           ( 1.0, -0.9594096685761585,
             -0.016418201193845627, -6.59128259330763e-06),
           (-0.3631544024050941, 1.0,
              0.18552572414898608, 0.0009189373821381621),
           ( 0.012342182682642163, 1.0,
             -0.8041490975383898, -0.2763202566199642),
           (-0.0002487340322843361, -0.46177069114264063,
             -0.9464871578663434, 1.0),
           ( 1.339325051000316e-06, 0.046511727711955726,
              1.0, 0.7262071720607719))
floor   = 0.03 exactly
table SHA-256 = 0f76d711b8ff65999e17c2281e14ad0311c7877a37887c9e342345657fc68377
```

The table hashes are hashes of canonical compact JSON containing the decimal
strings and metadata, not hashes of a floating array.

## 3. Exact selector

For one table with `L` checkpoint rows, define five variables

```text
x = (w0,w1,w2,w3,rho).
```

The LP is

```text
maximize rho
subject to a_l dot w - rho >= 0,  l=0,...,L-1,
           w_j >= 3/100,             j=0,...,3,
           w0+w1+w2+w3 = 1,
           rho unrestricted.
```

There are four affine degrees of freedom after imposing the simplex equality.
The implementation enumerates every combination of four active inequalities,
adjoins the simplex equality, and solves the resulting `5 x 5` system by
Gauss--Jordan elimination over `Fraction`.  Singular active sets are recorded.
Every nonsingular solution is then checked against **all** checkpoint and
floor inequalities using exact residuals.  Duplicate vertices from degenerate
active sets are removed by their exact five-component rational tuple.

The weight domain is compact and the primary optimum is finite because
`rho <= min_l a_l dot w`.  A linear functional attains its maximum at a
vertex.  Therefore comparing the enumerated exact vertex values proves the
primary optimum of the finite rational LP.  Among all vertices with maximum
`rho`, the implementation chooses the exact lexicographically smallest tuple
`(w0,w1,w2,w3)`.  Sequential minimization of linear coordinates over the
primary-optimal face ends at a vertex, so this vertex comparison is the
declared deterministic equivalent of sequential secondary LPs.  No
solver-native tie is consulted.

## 4. Failure contract

The selector fails closed with distinct statuses:

| status | meaning |
|---|---|
| `HOLD_CHECKPOINT_SCALE_ZERO` | at least one exact frozen row scale is zero |
| `HOLD_RATIONALIZED_COEFFICIENT_TABLE_INVALID` | malformed decimals, negative scale, wrong shape/order, or a row whose exact max norm is not one |
| `HOLD_RATIONALIZED_SIMPLEX_FLOOR_INFEASIBLE` | four times the exact floor exceeds one |
| `HOLD_RATIONALIZED_NO_FEASIBLE_VERTEX` | no enumerated exact vertex satisfies all constraints |
| `HOLD_RATIONALIZED_OPTIMUM_NONPOSITIVE` | the exact unrestricted-`rho` optimum is zero or negative |
| `PASS_EXACT_RATIONALIZED_SELECTOR` | the finite rational LP has a strictly positive exact optimum |

The top-level method artifact remains

```text
HOLD_METHOD_ONLY_NOT_A_CONTINUUM_OR_F0_CONTROL_CERTIFICATE
```

even when every internal finite LP status is PASS.  Process success and
scientific/publication release are intentionally separate.

## 5. Method-only B0 result

The exact enumeration produced:

| control | exact-selector weights (decimal display only) | exact normalized `rho` (decimal display) | smallest reconstructed raw signed margin | active sets / unique feasible vertices |
|---|---|---:|---:|---:|
| `m1` | `(0.03, 0.91, 0.03, 0.03)` | `0.88099041195984484681` | `0.09879189274140475529` | `15 / 7` |
| `m2` | `(0.54202430138820495306, 0.03, 0.04824505083766303958, 0.37973064777413200736)` | `0.32540424848060426430` | `0.001818065840583040156` | `70 / 11` |
| `m3` | `(0.40162853586287734295, 0.27618163146059300905, 0.03, 0.29218983267652964800)` | `0.13616273641487362346` | `0.001424914662273619541` | `210 / 16` |

Each primary optimum has one exact optimal vertex after deduplication.  The
JSON artifact serializes the exact numerator and denominator of every weight,
row scale, normalized margin, reconstructed raw signed margin, constraint
residual, F0 comparison, and optimality difference.  Decimal columns above
are readability fields only.

The reconstructed raw signed margin is exact for the internal relation

```text
raw_l = frozen_scale_l * frozen_normalized_row_l dot w.
```

It is not an interval enclosure of the original continuum derivative.

## 6. Compatibility with the already frozen F0 controls

The F0 design defines each mathematical control as the exact dyadic raw
binary64 ratio divided by its exact dyadic sum `S_c`.  The new selector instead
optimizes an exact decimal-rationalized coefficient table with an exact
`3/100` floor.  These are different contracts.

Exact comparison gives:

| control | selector equals F0 `raw/S_c` exactly | F0 control satisfies this selector's exact `3/100` floor | maximum component difference | compatibility verdict |
|---|---|---|---:|---|
| `m1` | no | no | `1.5821e-17` | HOLD |
| `m2` | no | yes | `7.7274e-18` | HOLD |
| `m3` | no | no | `1.5812e-16` | HOLD |

The floor failures for `m1` and `m3` are not retroactive defects in the F0
design: that design already says the nominal `0.03` LP floor is provenance,
while its mathematical controls require only strict positivity and exact unit
sum.  They do show why the exact-decimal selector cannot be called a byte-for-
byte reproduction of the frozen F0 controls.

The compatibility status is therefore

```text
HOLD_F0_CONTROL_COMPATIBILITY_NO_SILENT_REPLACEMENT.
```

There are only two honest downstream choices, both before any positive-`B`
evaluation:

1. amend the F0 v1 control freeze to the exact-selector rational vertices,
   disclose the prior broad-family/historical pilot, and independently audit
   the amendment before creating F1; or
2. retain the existing F0 `raw/S_c` controls, treat the exact selector as a
   method/candidate result only, and do not claim that it selected the frozen
   production controls exactly.

This artifact authorizes neither choice and explicitly sets
`replacement_authorized=false` for every control.  A near-zero difference is
still an exact mismatch and cannot be dismissed by a tolerance.

## 7. Continuum and publication HOLD

The rational vertex proof does not supply an error interval connecting each
frozen decimal coefficient to the true continuum clock derivative.  Without
such simultaneous outward coefficient enclosures, it cannot prove that the
continuum optimum is positive, that the selected rational vertex remains
feasible under coefficient uncertainty, or that a nearby continuum optimizer
has the same active set.  More importantly, checkpoint signs alone do not
supply the uniform curvature and complement-derivative bounds required for an
exact finite-window mode count.

Thus the artifact records:

```text
publication_certificate_status =
  HOLD_CONTINUUM_COEFFICIENTS_NOT_INTERVAL_CERTIFIED
full_window_box_and_complement_certificate_present = false
positive_budget_evaluated = false
authorized_scientific_command = null.
```

A future continuum selector certificate would need outward intervals for all
coefficient rows and scales, a robust lower bound on the optimum across those
intervals, and the separate full-window curvature/complement certificate.  It
must be a new version and independent audit; ordinary quadrature agreement or
more printed digits cannot close this gate.

## 8. Reproduction

From the repository root, the science-free tests are

```bash
./.venv/bin/python -m pytest -q \
  research/reports/encounter_multimodal_prr/code/test_modal_certificate_exact_selector.py
./.venv/bin/python -m ruff check \
  research/reports/encounter_multimodal_prr/code/modal_certificate_exact_selector.py \
  research/reports/encounter_multimodal_prr/code/test_modal_certificate_exact_selector.py
```

The one allowed method-result command is

```bash
PYTHONPATH=research/reports/encounter_multimodal_prr/code \
./.venv/bin/python \
  research/reports/encounter_multimodal_prr/code/modal_certificate_exact_selector.py \
  --execute-method-only-b0 \
  --output research/reports/encounter_multimodal_prr/scratch/modal_certificate_exact_selector_method_only_result.json
```

The producer refuses another output path and refuses overwrite.  Its zero
process exit code means only that all three exact finite rational LPs had
positive optima; the canonical JSON scientific status remains HOLD.
