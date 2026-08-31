# Round 03 G1a resolution

Date: 2026-07-13  
Scope: pre-fold foundations only; no discovery, continuation, fold, mesh
extrapolation, or PRR continuum claim was run.

## 1. Resolution verdict

**RESOLVED / G1a PRE-FOLD FOUNDATIONS PASS**

All P1 and P2 findings in round_03_g1_smoke_attack.md have been addressed.
The later budget-semantic P0 also supersedes the earlier interpretation:
\(\mathcal B\) is now the full installed centre-space budget, not a
per-transverse-measure budget.

The machine-readable result is deliberately stage-scoped:

- stage: G1a_pre_fold_foundations
- status: PASS
- continuum_verified: false
- schema_version: 2

This PASS does not authorize a discovery or continuum-fold claim. It certifies
only that the pre-fold operator, geometry, budget, initial law, semigroup, and
time-jet foundations pass the new discriminating smoke gates.

## 2. Files changed

- code/continuum_g1_smoke.py
- code/test_continuum_g1_smoke.py
- notes/continuum_g1_design.md
- artifacts/data/continuum_g1_smoke.json
- audits/round_03_resolution.md

No manuscript, README, registry, discovery, or publication-pipeline file was
changed.

## 3. Budget-semantic P0

### Problem

The earlier code treated \(\mathcal B\) as the longitudinal catalyst integral
per unit transverse measure, so the full installed amount scaled as
\(W^{d-1}\mathcal B\). That makes comparisons across transverse widths or
dimensions use different installed resources.

### Resolution

The design now defines \(\mathcal B\) as the full installed centre-space
budget:

$$
\kappa_{\boldsymbol w}(z)
=\frac{\mathcal B}{W^{d-1}}\sum_jw_j\phi_j(z),
\qquad
\int_{\mathcal C_d}\kappa_{\boldsymbol w}\,dc=\mathcal B.
$$

The current physical-\(d=2\) code uses

$$
\kappa=(\mathcal B/W)\sum_jw_j\phi_j.
$$

PilotParameters.integrated_budget was renamed installed_budget. The model
reports both:

- full physical_budget \(=W\int\kappa dz\);
- per_transverse_integral \(=\int\kappa dz\).

The \(W=2\) regression now requires full budget \(0.6\) and per-transverse
integral \(0.3\). The theta-endpoint and derivative gates use the same
full-budget convention.

## 4. Contact placement and local reference

### Problem

Total disk area and a small aggregate quadrature estimate could not detect a
translated or permuted contact mask. Rolling the mask by three transverse
cells previously preserved every gate while changing the reaction density.

### Resolution

The production circle--rectangle routine remains the split adaptive QUADPACK
calculation. It is now checked per cell against an independent reference that:

1. integrates horizontal rather than vertical circle chords;
2. uses fixed order-128 Gauss--Legendre quadrature;
3. applies \(y=a\sin\vartheta\), removing the square-root endpoint
   singularity;
4. does not call the production circle_rectangle_area routine.

The payload now persists and gates:

- maximum per-cell fraction discrepancy;
- relative \(L^1\) area discrepancy;
- disk centroid in both coordinates;
- parallel and perpendicular reflection errors;
- the independent reference order.

On the saved \(25^3\) smoke:

- maximum per-cell error:
  \(2.89\times10^{-15}\);
- relative \(L^1\) area error:
  \(1.37\times10^{-15}\);
- maximum centroid magnitude:
  \(5.96\times10^{-17}\);
- maximum reflection discrepancy:
  \(3.11\times10^{-15}\).

QUADPACK's abserr is now consistently named contact_area_error_estimate,
not an error bound. The design note likewise requires a persisted estimate
plus an independent local reference comparison.

### Mutation result

Rolling the contact matrix by three transverse cells now gives:

    status = FAIL
    failed gates =
      contact_reference_per_cell
      contact_reference_l1
      contact_centroid
      contact_reflections

The original false positive is therefore rejected.

## 5. Patchwise and endpoint budget checks

### Problem

Only the aggregate budget at \(\theta=0.5\) was checked. Because the near and
far weights are equal there, multiplying their integrals by \(1.2\) and
\(0.8\) cancelled at the tested control while producing \(13\%\) endpoint
errors.

### Resolution

The payload now persists and gates:

- all three individual patch integrals;
- their quadrature error estimates;
- full installed budgets at \(\theta=0\) and \(\theta=1\);
- endpoint relative errors;
- the full-budget derivative
  \(W\int\partial_\theta\kappa dz\);
- its error scaled by installed budget.

On the saved smoke:

- maximum patch integral error:
  \(4.44\times10^{-16}\);
- maximum endpoint budget relative error:
  \(3.70\times10^{-16}\);
- scaled budget derivative error:
  \(1.24\times10^{-16}\).

### Mutation result

The near/far \(1.2/0.8\) mutation now gives:

    status = FAIL
    failed gates =
      patchwise_integrals
      endpoint_physical_budgets
      budget_derivative_zero

The current-control physical_budget gate intentionally remains true in this
attack, demonstrating that the new independent gates, rather than an altered
midpoint check, reject the cancellation.

## 6. Initial reconstructed moments

### Problem

Mass normalization and contact safety were checked, but the finite-volume
reconstruction's linear and circular first moments were neither reported nor
gated.

### Resolution

The payload now reports:

- reconstructed and declared midpoint means;
- reconstructed and declared relative-parallel means;
- wrapped transverse circular mean;
- signed errors;
- circular resultant magnitude;
- coordinate-specific tolerances.

The predeclared G1a smoke tolerance is explicit:

$$
|\text{moment error}|
\le \frac12(\text{corresponding cell width})+5\times10^{-13}.
$$

This is the rigorous cell-localization scale for the deliberately coarse
piecewise-constant reconstruction, not a continuum accuracy claim. The design
now requires convergence under the later frozen odd/even sequence.

For the saved \(25^3\) smoke:

| Coordinate | Error | Half-cell tolerance |
|---|---:|---:|
| midpoint | \(-0.0120\) | \(0.0420\) |
| relative parallel | \(+0.0442927\) | \(0.0720\) |
| relative perpendicular circular | \(0\) | \(0.0200\) |

All pass honestly; the nonzero coarse-grid offsets remain visible in JSON.

## 7. Dense semigroup and time-jet references

### Problem

The killed mass identities were internally consistent but algebraically
tautological. The jet ranges were not gates and had no independent numerical
reference.

### Resolution

A frozen asymmetric \(4\times5\times6\) operator now supplies:

- sparse expm_multiply versus dense scipy.linalg.expm;
- one-shot versus two-half-step sparse actions;
- an asymmetric six-neighbour Kronecker-order sentinel;
- analytic \(p^TA^nk\), \(n=1,2,3\);
- independent nine-point finite-difference time jets, with dense forward and
  backward propagators.

Saved diagnostics:

| Check | Error |
|---|---:|
| dense versus sparse state | \(4.41\times10^{-15}\) |
| one step versus two half steps | \(5.63\times10^{-16}\) |
| \(f_t\) relative error | \(1.42\times10^{-12}\) |
| \(f_{tt}\) relative error | \(2.72\times10^{-11}\) |
| \(f_{ttt}\) relative error | \(1.74\times10^{-8}\) |

All are fail-closed gates. The main model also gates its killing tensor against
the independently reshaped \(\kappa(z)\bar\chi(r)\) product; the saved maximum
error is exactly zero.

## 8. Wrapped bump, tensor order, and input validation

The test suite now includes:

- a periodic bump centred at \(0.495\) with support crossing the
  \([-0.5,0.5)\) cut;
- unit wrapped mass and circular-mean recovery;
- an asymmetric tensor-neighbour sentinel;
- rejection of nonuniform contact edges;
- strictly increasing bump/SG edge validation;
- an explicit \(W=2\) installed-budget test.

The cut-crossing test recovers circular mean \(0.495\) to roundoff.

## 9. Boundary-layer union

The boundary diagnostic now uses a boolean union mask for the outer layers in
the two nonperiodic coordinates. A corner is counted once, not twice. A
regression test places unit mass in a boundary corner and obtains boundary
mass one. Small grids use clipped layer widths and cannot duplicate first/last
slices.

The boundary-layer value remains a reported smoke diagnostic, not the later
Section 8 box gate. The artifact continues to state that the finite zero-flux
box is not continuum evidence.

## 10. Machine-readable stage and artifact

The JSON schema was advanced to version 2 and contains:

    stage: G1a_pre_fold_foundations
    status: PASS
    continuum_verified: false

It contains 26 named gates, all true. The explicit continuum_verified false
prevents a generic PASS consumer from promoting this smoke to a continuum
fold.

Generated artifact:

    artifacts/data/continuum_g1_smoke.json

SHA-256:

    8162bf2a50ecb10af755084cf838b3e20c848f4e0d50c818b451ff03eeb6b11d

## 11. Verification

Pytest:

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
      -p no:cacheprovider -q \
      research/reports/encounter_multimodal_prr/code/test_continuum_g1_smoke.py

Result:

    11 passed

Ruff:

    .venv/bin/ruff check \
      research/reports/encounter_multimodal_prr/code/continuum_g1_smoke.py \
      research/reports/encounter_multimodal_prr/code/test_continuum_g1_smoke.py

    .venv/bin/ruff format --check \
      research/reports/encounter_multimodal_prr/code/continuum_g1_smoke.py \
      research/reports/encounter_multimodal_prr/code/test_continuum_g1_smoke.py

Result:

    All checks passed
    2 files already formatted

The default smoke script exits zero with status PASS. No discovery calculation
was executed.
