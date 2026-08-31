# Encounter continuum Round-4 delta handoff

Date: 2026-07-17

Archive: `encounter_continuum_round4_delta_20260717.tar.gz`

- exact size: `1088766` bytes;
- SHA-256:
  `4e080dd9dca0cdd4add891c55c149870ec4c92d9920df955b6715334a0fa2c2c`;
- member count: 28 unique regular-path entries;
- intended repository root: `valley-k-small/`;
- prior Round-3 archive: unchanged and not embedded;
- this README: intentionally outside the archive, so the archive hash is not
  self-referential.

## Scope

This explicit delta contains the Round-4 result-blind C1 refinement/rate
contract, the 706-line free-form/functional-bridge proof candidate, the neutral
free-axis/tensor fixture, its local adversarial audit, the 7-page main and
24-page Supplement working PDFs and sources, the fail-closed compile manifest,
the living freeze guards, the report README, research summary, and remote
handoff note.

It contains no `.venv`, `tmp`, `scratch`, `__pycache__`, `.pyc`, positive-
budget result payload, or previous handoff archive.  The filename
`physical_configuration_family_control_free_v1.json` is an explicitly pinned
control-free geometry/configuration source; it is not a control-value or
result payload.

The archive list was checked as 28/28 unique relative paths with no absolute
member or `..` traversal.  No network access was used to create or verify it.

## Scientific boundary

The central exact hashes are:

- proof candidate:
  `17b987d5090618e5346f81217afed7e57daccf878d4b93b8402724b3e002a562`;
- C1 ideal-refinement contract:
  `93b13d8c6864c54896ff2d71d143856554d8e2de94acd8ba4f43cc3a2534987b`;
- neutral fixture:
  `363814071e06a369b234034f41d347933c893ae0c6efeb543db91e099e88c14c`;
- main PDF:
  `78e2e5169f0397073e4edc3deaad27bf4563f856999eea8468d0e698b51f306a`;
- Supplement PDF:
  `a3716ded14c480188c3504ad86e7318129aa32ada57ada2caf6b7767d26c9cf7`;
- compile manifest:
  `03a9be39a44e16db66f65ff41ce48fcf5ff640702e9f35c16d072d126d4c8e81`.

Final local hash-specific reviews report `P0=P1=P2=0` separately for the
mathematical successor note, machine contract, neutral fixture, and
reader-facing conditional proposition.  This is not external referee or
journal acceptance.  Complete C0/C1, production gauge/application, C2, C3,
root transfer, release, and submission remain HOLD.

## Receiving-Mac procedure

First allow OneDrive to finish syncing both files.  From the directory that
contains this README and archive, verify:

```bash
shasum -a 256 encounter_continuum_round4_delta_20260717.tar.gz
stat -f '%z bytes' encounter_continuum_round4_delta_20260717.tar.gz
tar -tzf encounter_continuum_round4_delta_20260717.tar.gz
```

The hash and size must match this README.  Extract over the same
`valley-k-small` checkout only after preserving any divergent local edits:

```bash
tar -xzf encounter_continuum_round4_delta_20260717.tar.gz -C /absolute/path/to/valley-k-small
```

Then run the focused checks from the receiving repository root:

```bash
.venv/bin/python research/reports/encounter_multimodal_prr/code/build_continuum_c1_ideal_refinement_contract_candidate_v1.py --check
.venv/bin/python research/reports/encounter_multimodal_prr/code/validate_continuum_c1_ideal_refinement_contract_candidate_v1.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c1_ideal_refinement_contract_candidate_v1.py research/reports/encounter_multimodal_prr/code/test_continuum_c1_ideal_refinement_contract_v1_currentness.py research/reports/encounter_multimodal_prr/code/test_continuum_c1_ideal_refinement_contract_adversarial_v1.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_c1_free_axes_tensor_diagnostic.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c1_free_axes_tensor_diagnostic.py research/reports/encounter_multimodal_prr/code/test_continuum_c1_free_axes_tensor_diagnostic_mutations.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/compile_theorem_first_working.py
```

Expected focused counts are 79/79 contract tests and 21/21 neutral-fixture
tests.  The compiler must reproduce the two PDF hashes above and keep
`release_eligible=false`.

