# Round 06 G1a false-positive hardening resolution

Date: 2026-07-13  
Scope: `continuum_g1_smoke.py`, its focused tests, the necessary G1 design
contract, and the regenerated G1a JSON only  
Disposition: **resolved at the G1a foundation stage**

## Claim boundary

This round hardens operator, geometry, budget, and initialization evidence.  It
does not run a fold continuation or a mesh/box convergence study.  The emitted
artifact therefore remains

- `stage = G1a_pre_fold_foundations`;
- `continuum_verified = false`; and
- explicit that it is not a cusp, trimodality, continuum-fold, or PRR result.

The default artifact is schema version 3 and passes all 42 foundation and
smoke gates.  This PASS means only that later discovery code has a fail-closed
foundation to consume.

## P1-A: translated normalized catalyst profiles

The previous checks could be fooled by rolling every width-0.08 catalyst
profile by two longitudinal cells.  Each profile retained unit mass and the
global installed budget, so budget-only gates passed despite a materially
different catalyst field.

Resolution:

1. `bump_cell_masses_reference` evaluates normalized bump cell masses by an
   independent fixed 192-point Gauss rule.  It does not call the production
   `bump_cell_masses` routine.
2. All three catalyst profiles now persist and gate their zeroth moment,
   cell-centre first moment, maximum per-cell reference error, and relative
   L1 reference error.
3. All three initial marginals use the same independent contract, including a
   wrapped local reference and circular moment for the periodic transverse
   marginal.
4. Production patch quadrature error estimates are now an explicit gate at
   `1e-11`; merely persisting them is no longer sufficient.

Adversarial replay on the 17 x 19 x 17 test grid:

```text
translated_patches FAIL
failed gates:
  patch_profile_first_moments
  patch_profile_reference_per_cell
  patch_profile_reference_l1
```

Importantly, `patchwise_integrals` still passes in this replay.  The new local
profile certificate, rather than a coincidental budget change, causes the
failure.

A separate wrapped-initial translation replay fails
`initial_reconstructed_moments`, `initial_profile_first_moments`,
`initial_profile_reference_per_cell`, and `initial_profile_reference_l1` while
the total `initial_mass` gate remains true.

## P1-B: negative but unit-sum control endpoint

The previous midpoint-only evaluation could be fooled by replacing the lower
endpoint with `(-0.04, 0.34, 0.70)`.  It still sums to one and the theta=0.5
field remains nonnegative, but the declared control segment includes a
nonphysical endpoint.

Resolution:

1. Both endpoint weight sums and componentwise minima are persisted and gated.
2. Endpoint minima of the assembled longitudinal reactivity and full killing
   field are persisted and gated.
3. Endpoint simplex membership supplies a convexity certificate for every
   admissible theta in `[0, 1]`; current-theta nonnegativity is reported as a
   separate, insufficient condition.
4. The design note explicitly makes no positivity claim for extrapolation
   outside `[0, 1]`.

Adversarial replay:

```text
negative_endpoint FAIL
failed gates:
  endpoint_weight_nonnegative
  endpoint_kappa_nonnegative
  endpoint_killing_nonnegative
  affine_control_line_certified

endpoint component minima = [-0.04, 0.05]
endpoint kappa minima     = [-0.1194854059455315, 0.0]
endpoint killing minima   = [-0.1194854059455315, 0.0]
current kappa/killing minima at theta=0.5 = 0.0 / 0.0
```

Thus a positive sampled midpoint can no longer conceal a nonphysical endpoint.

## Independent main-operator transport sentinel

The main assembled sparse generator now exposes 12 selected asymmetric rate
comparisons: interior and reflecting-boundary inward rates for `z` and
`r_parallel`, plus interior and periodic-wrap rates for `r_perp`.  Expected
values use an independently evaluated Bernoulli function and the frozen
analytic diffusion/drift coefficients, not the one-dimensional production
builder.

Swapping the midpoint and relative diffusion coefficients produces:

```text
transport_swap FAIL
failed gate: main_transport_rate_reference
maximum absolute rate error = 0.44019534816117134
maximum relative rate error = 5.517318043881429
```

The unmutated default has 12/12 comparisons with zero reported absolute and
relative error.

## Reusable foundation contract and frozen input

`foundation_diagnostics(model)` and `foundation_gates(model, diagnostics)` are
now the single public source of the complete G1a foundation evidence.  The
smoke payload calls these functions directly, so a later discovery runner can
reuse all gates rather than copy a stale subset.

Schema 3 also persists the full physical parameter tuple, both endpoint
vectors, the nonperiodic and periodic box bounds, grid shape, theta, and time
window/point count.  This makes the numerical evidence self-describing and
prevents an apparently identical artifact from silently using a different
configuration.

## Default artifact evidence

Artifact:
`research/reports/encounter_multimodal_prr/artifacts/data/continuum_g1_smoke.json`

```text
schema_version = 3
stage = G1a_pre_fold_foundations
continuum_verified = false
status = PASS
gate count = 42
failed gates = []
maximum patch quadrature estimate = 7.623362755469945e-14
maximum catalyst per-cell reference error = 4.9960036108132044e-15
maximum catalyst relative L1 reference error = 7.712580574192823e-15
maximum initial per-cell reference error = 3.552713678800501e-15
maximum initial relative L1 reference error = 4.884981308350662e-15
transport samples = 12
maximum transport absolute/relative error = 0.0 / 0.0
sha256 = a0a1894dbe6dd37bad6973ca6f3dd29b651441f7b911a5406186bb86a18fd3c3
```

Two consecutive default generations returned the same SHA-256 digest.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q \
  research/reports/encounter_multimodal_prr/code/test_continuum_g1_smoke.py
.................. [100%]

.venv/bin/ruff check \
  research/reports/encounter_multimodal_prr/code/continuum_g1_smoke.py \
  research/reports/encounter_multimodal_prr/code/test_continuum_g1_smoke.py
All checks passed!

.venv/bin/ruff format --check \
  research/reports/encounter_multimodal_prr/code/continuum_g1_smoke.py \
  research/reports/encounter_multimodal_prr/code/test_continuum_g1_smoke.py
2 files already formatted
```

The 18 focused tests include direct independence of the bump reference and
fail-closed mutations for contact translation, catalyst normalization bias,
translation of all catalyst patches, a negative unit-sum endpoint, wrapped
initial-profile translation, and swapped main transport diffusion
coefficients.

## Remaining boundary

Round 06 closes the identified G1a false positives.  Promotion to a continuum
or journal-level result still requires the predeclared fold discovery,
odd/even mesh and box convergence, third-order fold-jet convergence,
held-out topology/observability checks, and a certified late-time tail.  None
of those later gates is implied by this artifact.
