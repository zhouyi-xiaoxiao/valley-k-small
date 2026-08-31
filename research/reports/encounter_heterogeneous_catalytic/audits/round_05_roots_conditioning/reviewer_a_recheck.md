# Round 05 final recheck — Reviewer A

Date: 2026-07-11  
Scope: final regression and closure check following the Round-05 corrections  
Verdict: **PASS — no B0/B1; all three B2 findings are closed; the single B3 hardening recommendation remains optional**

## Final focused regression

I reran the exact focused selection recorded in `reviewer_a.md` after regeneration
of the numerical artifacts, figures, notebook, manuscript, child manifests, and
aggregate publication manifest:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -q -p no:cacheprovider \
  tests/test_fpt.py tests/test_morphology.py \
  tests/test_encounter_gig_fold.py \
  tests/test_encounter_2d_artifacts.py \
  tests/test_encounter_2d_matched_control_artifacts.py \
  tests/test_encounter_2d_matched_fold.py \
  tests/test_encounter_2d_matched_fold_artifacts.py \
  tests/test_encounter_2d_trimodal_artifacts.py \
  tests/test_encounter_2d_centre_coordinate_artifacts.py \
  tests/test_encounter_2d_capacity_artifacts.py \
  tests/test_encounter_3d_artifacts.py \
  tests/test_encounter_multid_gig_design.py \
  tests/test_encounter_manuscript.py \
  tests/test_encounter_publication_pipeline.py
```

Result: **exit code 0; all collected tests passed**.

The requested suite was described as 56 tests. The current repository collects
**57 tests** for the same file selection because the publication-pipeline file
now includes the additional fail-closed Lean integrity regression. The collected
counts are:

| test file | count |
|---|---:|
| `test_fpt.py` | 4 |
| `test_morphology.py` | 10 |
| `test_encounter_gig_fold.py` | 8 |
| `test_encounter_2d_artifacts.py` | 2 |
| `test_encounter_2d_matched_control_artifacts.py` | 3 |
| `test_encounter_2d_matched_fold.py` | 5 |
| `test_encounter_2d_matched_fold_artifacts.py` | 2 |
| `test_encounter_2d_trimodal_artifacts.py` | 4 |
| `test_encounter_2d_centre_coordinate_artifacts.py` | 3 |
| `test_encounter_2d_capacity_artifacts.py` | 3 |
| `test_encounter_3d_artifacts.py` | 3 |
| `test_encounter_multid_gig_design.py` | 4 |
| `test_encounter_manuscript.py` | 2 |
| `test_encounter_publication_pipeline.py` | 4 |
| **Total** | **57/57 passed** |

Thus the original 56-test target passes, and the newly added 57th formal-integrity
gate passes as well.

## B2 closure audit

### B2-1 closed — resolved modality is separated from strict stationary-point count

The matched-control validator now states that the comparison is a
resolution-class transition and that the homogeneous controls retain small
strict secondary maxima (`code/validate_2d_matched_homogeneous.py:11-16`). It
computes sign-changing exact-semigroup roots with generator actions and Brent
refinement (`code/validate_2d_matched_homogeneous.py:155-215`), stores strict
stationary points and both patterned/homogeneous secondary-peak ratios
(`code/validate_2d_matched_homogeneous.py:300-350`), and labels the classifier
semantics explicitly.

The regression requires, on all five grids,

- two strict patterned maxima and two strict homogeneous maxima;
- a homogeneous second/primary ratio strictly between 0 and 3%; and
- a patterned ratio above 3% and above its matched homogeneous value
  (`tests/test_encounter_2d_matched_control_artifacts.py:27-55`).

The manuscript reports that patterning promotes a subthreshold transport clock
to a resolved mode rather than creating the mathematical second maximum
(`manuscript/encounter_modality_jcp.tex:931-957`). The centre-coordinate section
and caption use the same resolved/strict distinction
(`manuscript/encounter_modality_jcp.tex:1053-1081`). This closes the causal and
terminological ambiguity without weakening the resolved-morphology result.

### B2-2 closed — finite scans are reported as detected, not exhaustive

The 2D fold endpoint paragraph now says that the scan retains every **detected
sign-changing** stationary point. It also states directly that the finite scan
does not certify the absence of tangential or narrower roots between sampled
times (`manuscript/encounter_modality_jcp.tex:1016-1027`).

The trimodal validator/note/manuscript consistently use “detected” for the five
simple roots and preserve the explicit non-exhaustiveness boundary. The saved
cross-grid key and regression likewise say
`all_four_have_five_detected_alternating_roots`. Therefore neither the endpoint
nor trimodal finite scan is presented as an interval theorem. The independently
recomputed root and curvature margins in `reviewer_a.md` remain unchanged.

### B2-3 closed — 3D capacity is a coupled-path check, not a certified double limit

The 3D artifact now records
`fixed_chi_radius_and_grid_limits_separated = False` and
`continuum_capacity_coefficient_certified = False`, while retaining
`coupled_path_is_continuum_compatible = True`
(`code/validate_3d_capacity.py:286-345`). The regression enforces these exact
claim boundaries (`tests/test_encounter_3d_artifacts.py:34-62`).

The manuscript says that $a/h$ stays approximately constant, calls the 0.114%
slope agreement continuum-compatible finite-grid evidence, and explicitly
denies a separated double-limit certification
(`manuscript/encounter_modality_jcp.tex:1285-1312`). The numerical fit remains
useful; only the unjustified continuum-certification interpretation has been
removed.

## Aggregate and formal-integrity closure

The refreshed `publication_pipeline.manifest.json` passes all four publication
pipeline tests, including all child-output hashes and aggregate source/formal/
output hashes (`tests/test_encounter_publication_pipeline.py:63-93`). The current
aggregate records 77 source files, four formal-evidence reports, and 98 outputs.

The new fail-closed formal regression also passes. It requires:

- formal-integrity status `pass`;
- 46 legacy plus 54 encounter-specific theorems, 100 total;
- all 10 declared Lean modules; and
- four axiom reports whose theorem counts sum to 100
  (`tests/test_encounter_publication_pipeline.py:96-124`).

The pipeline runs a static Lean integrity stage before the Lean build and four
axiom-driver stages, and rejects forbidden markers or incomplete formal evidence
(`code/run_publication_pipeline.py:326-416,522-560`). This closes the prior
manifest-only pipeline state and makes the formal layer fail closed.

## Final disposition

Round 05 is closed with:

- **B0: 0**
- **B1: 0**
- **B2: 3 found, 3 resolved**
- **B3: 1 optional hardening item** — archive dimensionless fold conditioning,
  fit-window sensitivity, and exact-tail derivative margins directly in the
  scientific JSON artifacts.

No remaining root-isolation, fold-conditioning, tail, fit-selection, or
capacity-convergence issue blocks the finite-model mechanism package. The
continuum promotion tasks identified in the original report remain future work,
not defects in the now-explicit finite-evidence claims.
