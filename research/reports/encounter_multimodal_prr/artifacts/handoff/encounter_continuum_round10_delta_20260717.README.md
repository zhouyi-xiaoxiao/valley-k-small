# Encounter continuum Round-10 delta handoff

Date: 2026-07-17

Archive: `encounter_continuum_round10_delta_20260717.tar.gz`

- exact size: `60044` bytes;
- SHA-256:
  `82bc2e8c235318e5b75c101b20eb3ec7379abacfa6aad9e03c2afc647e484fa7`;
- member count: 9 unique relative paths;
- prerequisite: the verified Round-9 delta has already been applied;
- this README is outside the archive, avoiding a self-referential hash.

## Members and scope

The archive contains only:

1. `research/docs/RESEARCH_SUMMARY.md`;
2. `research/reports/encounter_multimodal_prr/README.md`;
3. `research/reports/encounter_multimodal_prr/notes/REMOTE_CODEX_HANDOFF_20260715.md`;
4. `research/reports/encounter_multimodal_prr/notes/continuum_c2_one_sided_free_sg_residual_candidate.md`;
5. `research/reports/encounter_multimodal_prr/audits/continuum_c2_one_sided_free_sg_residual_round10_20260717.md`;
6. `research/reports/encounter_multimodal_prr/code/continuum_c2_one_sided_free_residual_neutral_fixture_v1.py`;
7. `research/reports/encounter_multimodal_prr/artifacts/data/continuum_c2_one_sided_free_residual_neutral_fixture_v1.json`;
8. `research/reports/encounter_multimodal_prr/code/test_continuum_c2_one_sided_free_residual_neutral_fixture_v1.py`; and
9. `research/reports/encounter_multimodal_prr/code/test_continuum_c2_one_sided_free_residual_neutral_fixture_mutations_v1.py`.

Every member is an ordinary relative path with no absolute path or `..`
traversal.  The archive contains no control, budget, killing field, production
centre, reaction-time result, root, topology result, PDF, manuscript, prior
archive, scratch tree, virtual environment, or positive C2 receipt.  No
network access was used to build or audit it.

The theorem-first manuscript remains unchanged at seven main plus twenty-four
Supplemental physical pages.  Round 10 closes only the ideal one-sided free
SG residual premise.  Production/evaluator binding, source-bound map and
killing constants, complex-sector regularity, contour growth, complete C2/C3,
release, and submission remain false.

## Frozen hashes and verdict

```text
theory       ba3d41da0f16ab4ceb0f2f0c8eceeb29214b0b5b765c9300f373a3513bb21fc4
audit        c00351acc5ff3be67cbb579ccab768e8e226bd29bc730f5d9acb15c5dcc3163d
builder      1dd8984382a7f32a9cee8ffbe63939dbd844292d9e04d387acb0534455ed3f34
artifact     93364229ec1495f1fbb15f0319bfd85a7da44c4821c2a5b925e1bf8ac1ad80c7
independent  892842ff7996d1f64961af30d5bf2a64b44bae4522f4c9bc33675aaa4765927b
mutations    43011a2b851b014d06536c20ba6fdf9d109b3ad61f1b33743bb163519ac21335
```

The theorem audits report `P0=P1=P2=0`.  The first final fixture audit found
one P1 in the mutation receipt: a missing SciPy import could make every
validator subprocess nonzero and be miscounted as semantic rejection.  The
repaired harness first requires the canonical `107/107` baseline, then
requires return code one plus an explicit validator `ERROR` and forbids
`SUMMARY`, traceback, `ModuleNotFoundError`, and `ImportError` markers for
each mutation.  Final post-repair audit reports `P0=P1=P2=0`.

The accepted ideal rate boundary is:

```text
cell-centred reflected free residual   O(h)
periodic base/half-shift free residual O(h)
vertex-dual reflected free residual    O(sqrt(h))
uniform alpha greater than one half    refuted by smooth constant mode
asynchronous tensor family             O(sqrt(max_k h_k))
```

## Receiving-Mac procedure

Allow OneDrive to finish syncing both files.  From their directory, verify:

```bash
shasum -a 256 encounter_continuum_round10_delta_20260717.tar.gz
stat -f '%z bytes' encounter_continuum_round10_delta_20260717.tar.gz
tar -tzf encounter_continuum_round10_delta_20260717.tar.gz
```

The digest, size, and nine-member list must match this sidecar.  Preserve any
divergent local edits, then extract over the same repository root:

```bash
tar -xzf encounter_continuum_round10_delta_20260717.tar.gz -C /absolute/path/to/valley-k-small
```

From the repository root, verify the frozen files and run:

```bash
shasum -a 256 research/reports/encounter_multimodal_prr/notes/continuum_c2_one_sided_free_sg_residual_candidate.md
shasum -a 256 research/reports/encounter_multimodal_prr/audits/continuum_c2_one_sided_free_sg_residual_round10_20260717.md
.venv/bin/python -I -B research/reports/encounter_multimodal_prr/code/continuum_c2_one_sided_free_residual_neutral_fixture_v1.py --check
.venv/bin/python -I -B research/reports/encounter_multimodal_prr/code/test_continuum_c2_one_sided_free_residual_neutral_fixture_v1.py
.venv/bin/python -I -B research/reports/encounter_multimodal_prr/code/test_continuum_c2_one_sided_free_residual_neutral_fixture_mutations_v1.py
```

Expected results are check-mode PASS with `output_not_written=true`,
`SUMMARY 107/107 PASS`, and `SUMMARY 30/30 PASS`.  The mutation harness is
supposed to stop before its mutation loop if the selected Python lacks SciPy;
such a dependency failure is not a PASS.

These exact results and all six frozen hashes were reproduced from a clean
temporary overlay of the verified Round-7, Round-8, Round-9, and Round-10
deltas.  The temporary tree was removed after the check.

Finish with:

```bash
python3 scripts/reportctl.py validate-registry
python3 scripts/reportctl.py validate-archives
python3 scripts/reportctl.py check-docs-paths
python3 scripts/reportctl.py validate-science-rules
```

The next continuum task is mixed Neumann-periodic complex-sector `H2` graph
regularity and contour growth.  Do not restore the refuted tensor-`Q1`
all-pairs route, upgrade the smooth diagnostic superconvergence into a uniform
second-order theorem, or treat the neutral artifact as production evidence.
