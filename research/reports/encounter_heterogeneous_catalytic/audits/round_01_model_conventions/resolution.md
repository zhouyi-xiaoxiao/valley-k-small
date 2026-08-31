# Round 01 resolution — model definitions and numerical conventions

Date: 2026-07-11  
Status: **PASS WITH DECLARED CAVEATS**  
Submission gate: **reopened for Round 01; later rounds remain open**

The two independent reviews agreed on one B0 model-identity error, two B1
description/control errors, and two bounded omissions. The remediation does
not assert that midpoint and diffusivity-weighted catalyst coordinates are
equivalent. It declares the physical model, exposes their difference, and
keeps the free-space GIG coordinate as a separate analytical screen.

## Finding-by-finding disposition

### B0: weighted analytical centre versus arithmetic midpoint in 2D code

Resolved by a model split rather than a relabeling.

- The general physical catalyst coordinate is now
  \(C_\eta=\eta X_1+(1-\eta)X_2\), with exact identity
  \(C_\eta=R+(\eta-D_2/(D_1+D_2))r\).
- Every promoted bounded 2D validator explicitly passes `centre_weight=0.5`;
  the manuscript calls this the physical midpoint model.
- The diffusivity-selected value \(\eta=D_2/(D_1+D_2)\) is used only for the
  free-space relative/centre GIG factorization and as a distinct sensitivity
  comparator.
- `validate_2d_centre_coordinate.py` changes only \(\eta\). On `9x5`, the
  patterned endpoint changes `bimodal -> shoulder`; on `11x7` and `13x9`, both
  conventions remain bimodal but use different masks. All six separately
  budget-matched homogeneous controls are unimodal. Thus the repository now
  contains an executable counterexample to coordinate equivalence.
- Seven new Lean theorems prove the affine decomposition, weighted
  specialization, midpoint shift, and contact-radius bounds without new
  axioms.

The B0 is closed because model identity is now consistent from theory through
API, manifests, validators, manuscript, notebook, tests, and formal algebra.

### B1: reflecting solver misidentified as finite volume

Resolved by correcting the method identity and narrowing the claim. The
reflecting pair solver is documented as a boundary-node nearest-neighbour
lattice CTMC with uniform node invariant measure, omitted outward jumps, and
binary node masks. The manuscript explicitly says it is not a cell-centred
finite-volume scheme and treats every result from it as a finite-state
mechanism certificate. A future cell-averaged finite-volume/Robin convergence
study remains an open continuum obligation, not a hidden implementation claim.

### B1: control examples presented as a one-factor hierarchy

Resolved. The four bounded families have immutable IDs and a full parameter
table:

- `M2D-E`: matched endpoint family;
- `M2D-F`: matched fold family;
- `M2D-C`: separate mechanism/adverse examples;
- `M2D-T`: separate three-patch trimodality family.

The control section and caption now state that M2D-C is not a factorial
ablation of M2D-E or M2D-F. Conclusions remain family-specific.

### B2: missing relative drift in multidimensional GIG construction

Resolved. The reference construction and manifest now state `u=0`,
`D1=D2=1/2`, `ell=1`, `Dc=1/4`, and `|v_c|=0.1`; hence `B=0.01` follows from
the declared model. The artifact was regenerated.

### B2: missing time-zero conditioning in the synchronous chain

Resolved. The manuscript and theory note state that `alpha` is live mass
conditioned on surviving any time-zero reaction check, no `n=0` atom is
included, and the first reported flux is at step one. The production starts
away from a catalytic state, so saved curves are unchanged.

## Revalidation evidence

- All affected 2D generators were rerun after declaring `centre_weight=0.5`:
  finite radius, mechanisms, matched endpoints, matched fold, and trimodality.
- Centre-coordinate artifact/core tests: `11 passed`; two independent
  executions gave byte-identical JSON/CSV/PDF/PNG and semantically identical
  NPZ arrays.
- Focused manuscript/notebook/coordinate/pipeline tests: `18 passed` after
  excluding only the deliberately stale aggregate-manifest hash checks.
- Executed notebook: 17 code cells, zero error outputs, nine passing claim
  rows, and explicit `coordinate equivalence=false` / `continuum robustness=false`.
- Manuscript: 20 pages, 12 figures, zero undefined references, undefined
  citations, overfull boxes, or missing files.
- Lean: `lake build` completed 3109 jobs; theorem count is 100; the affine
  coordinate additions are sorry-free; axiom reports contain only `propext`,
  `Classical.choice`, and `Quot.sound`.
- Core row/column, mass/flux, fold-sensitivity, and contact-support regression
  checks retained the passed reviewer results.

## Commands

```text
PYTHONPATH=packages/vkcore/src .venv/bin/python \
  research/reports/encounter_heterogeneous_catalytic/code/validate_2d_centre_coordinate.py

PYTHONPATH=packages/vkcore/src .venv/bin/python -m pytest -q \
  tests/test_encounter_2d.py \
  tests/test_encounter_2d_centre_coordinate_artifacts.py \
  tests/test_encounter_publication_notebook.py \
  tests/test_encounter_manuscript.py \
  tests/test_encounter_publication_pipeline.py \
  -k 'not child_manifests_record_hashed_outputs and not aggregate_manifest_has_no_self_hash_and_covers_all_layers'

PYTHONPATH=packages/vkcore/src .venv/bin/python \
  research/reports/encounter_heterogeneous_catalytic/code/compile_manuscript.py

# In the local non-OneDrive Lean mirror:
lake build
lake env lean EncounterContinuumAxioms.lean
```

## Retained caveats

Round 01 does not certify a continuum reflecting discretization, invariance
under catalytic-coordinate choice, a converged 2D fold location, a continuum
trimodality region, or a Doi--Robin match. Those claims are absent or expressly
withheld. The aggregate publication manifest is intentionally rebuilt only
after all ten audit rounds, so its temporary hash staleness is tracked under
Round 08 rather than counted as a Round 01 scientific failure.
