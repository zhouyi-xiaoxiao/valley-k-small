# Encounter continuum Round-9 delta handoff

Date: 2026-07-17

Archive: `encounter_continuum_round9_delta_20260717.tar.gz`

- exact size: `52262` bytes;
- SHA-256:
  `20652b6a8c1299b4c26dbcd5eef3dbb4dffe09d020ba5369b7d08fc950d98b10`;
- member count: 8 unique relative paths;
- prerequisite: the verified Round-8 delta has already been applied;
- this README is outside the archive, avoiding a self-referential hash.

## Members and scope

The archive contains only:

1. `research/docs/RESEARCH_SUMMARY.md`;
2. `research/reports/encounter_multimodal_prr/README.md`;
3. `research/reports/encounter_multimodal_prr/notes/REMOTE_CODEX_HANDOFF_20260715.md`;
4. `research/reports/encounter_multimodal_prr/notes/continuum_c2_qf2_checkerboard_and_residual_route_candidate.md`;
5. `research/reports/encounter_multimodal_prr/audits/continuum_c2_qf2_checkerboard_residual_route_round9_20260717.md`;
6. `research/reports/encounter_multimodal_prr/code/continuum_c2_qf2_checkerboard_obstruction_v1.py`;
7. `research/reports/encounter_multimodal_prr/artifacts/data/continuum_c2_qf2_checkerboard_obstruction_v1.json`; and
8. `research/reports/encounter_multimodal_prr/code/test_continuum_c2_qf2_checkerboard_obstruction_v1.py`.

Every member is an ordinary relative path with no absolute path or `..`
traversal.  The archive contains no control, budget, production centre, result,
scratch, virtual environment, cache, PDF, manuscript, prior archive, or
positive C2 receipt.  No network access was used to build or audit it.

The theorem-first manuscript remains unchanged at seven main plus twenty-four
Supplemental physical pages.  Round 9 proves a negative result about one
standard QF2 implementation and selects a conditional replacement route.  It
does not close complete C1, C2, C3, production binding, release, or submission.

## Frozen hashes and verdict

```text
theory    4b20189814c763816ea707630ff098c98995afd7d3207808225a320a742508c2
audit     ed1f15c20c93db274989827dae9ccf5f3d36d5d80e1c9ba90052de8edf18b260
builder   ca53c6e33c631e115d38d857110d8eaf47a86205d5f3db6ca93529d0b633bdd9
artifact  40f7c0689343eef0aca0b17a2bc95183cbf8fdca073a6d9a0d4ae1fbaa53c9bf
test      039ba8721ab161c694b34c355517b8a960facb19e89048cfdeabbe5f69b96bbb
```

An independent exact-byte mathematical audit checks the periodic formulas,
the endpoint-half-mass Neumann times Neumann times periodic extension,
asynchronous spacings, exact residual identities, and nonclaim boundary.  It
reports `P0=P1=P2=0`.  This is a local adversarial review, not external referee
acceptance.

## Receiving-Mac procedure

Allow OneDrive to finish syncing both files.  From their directory, verify:

```bash
shasum -a 256 encounter_continuum_round9_delta_20260717.tar.gz
stat -f '%z bytes' encounter_continuum_round9_delta_20260717.tar.gz
tar -tzf encounter_continuum_round9_delta_20260717.tar.gz
```

The digest, size, and eight-member list must match this sidecar.  Preserve any
divergent local edits, then extract over the same repository root:

```bash
tar -xzf encounter_continuum_round9_delta_20260717.tar.gz -C /absolute/path/to/valley-k-small
```

From the repository root, verify the frozen files and run:

```bash
shasum -a 256 research/reports/encounter_multimodal_prr/notes/continuum_c2_qf2_checkerboard_and_residual_route_candidate.md
shasum -a 256 research/reports/encounter_multimodal_prr/audits/continuum_c2_qf2_checkerboard_residual_route_round9_20260717.md
python3 research/reports/encounter_multimodal_prr/code/continuum_c2_qf2_checkerboard_obstruction_v1.py --check
python3 research/reports/encounter_multimodal_prr/code/test_continuum_c2_qf2_checkerboard_obstruction_v1.py
```

Expected results are a check-mode PASS with `output_not_written=true` and
`SUMMARY 90/90 PASS`.  These exact results were reproduced once more from a
clean temporary extraction after overlaying the verified Round-7, Round-8,
and Round-9 deltas.  Finish with:

```bash
python3 scripts/reportctl.py validate-registry
python3 scripts/reportctl.py validate-archives
python3 scripts/reportctl.py check-docs-paths
python3 scripts/reportctl.py validate-science-rules
```

The next continuum task is to prove the one-sided free SG/control-volume
residual and source-bound mixed-boundary complex-sector `H2` regularity.  Do
not restore the refuted standard tensor-`Q1` all-pairs `O(h)` premise or treat
the neutral fixture as production evidence.
