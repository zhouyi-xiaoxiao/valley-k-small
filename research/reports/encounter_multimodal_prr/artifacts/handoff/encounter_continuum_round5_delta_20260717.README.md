# Encounter continuum Round-5 delta handoff

Date: 2026-07-17

Archive: `encounter_continuum_round5_delta_20260717.tar.gz`

- exact size: `36193` bytes;
- SHA-256:
  `4212d5a5b9d9f393440841f28d21101e1d8fbc1fe5b4d3292d665b47f5e83086`;
- member count: 5 unique relative paths;
- prerequisite: the verified Round-4 delta has already been applied;
- this README is outside the archive so the archive hash is not
  self-referential.

## Members and purpose

The archive contains only:

1. `research/docs/RESEARCH_SUMMARY.md`;
2. `research/reports/encounter_multimodal_prr/README.md`;
3. `research/reports/encounter_multimodal_prr/notes/REMOTE_CODEX_HANDOFF_20260715.md`;
4. `research/reports/encounter_multimodal_prr/notes/continuum_c1_varying_space_resolvent_mosco_candidate.md`; and
5. `research/reports/encounter_multimodal_prr/audits/continuum_c1_varying_space_resolvent_mosco_round5_20260717.md`.

It contains no executable result, control, scratch, production-centre,
positive-budget, virtual-environment, cache, PDF, or prior archive payload.
All members are ordinary relative paths with no absolute path or `..`
traversal.  No network access was used to create it.

The theory note is 571 lines, 14,490 bytes, with SHA-256
`0b9728535ed0216bc00d5ccb911575dd30bb531422130b2f7e2502a046f134f1`.
Its audit has SHA-256
`9e1cacca6c9c40675f31acbe743bbeccc74aca29b6378a641e1613ae48e55287`.

Two independent main-theorem attacks and one separate tensor/killing attack
on the final theory bytes report `P0=P1=P2=0`.  This is a local,
hash-specific abstract theorem-candidate result, not external referee or
journal acceptance.  Model-specific refinement, production application,
complete C1, C2/C3, release, and submission remain HOLD.

## Receiving-Mac procedure

From the directory containing this sidecar and archive:

```bash
shasum -a 256 encounter_continuum_round5_delta_20260717.tar.gz
stat -f '%z bytes' encounter_continuum_round5_delta_20260717.tar.gz
tar -tzf encounter_continuum_round5_delta_20260717.tar.gz
```

The values must match above.  Preserve any divergent local edits, then extract
over the same repository root:

```bash
tar -xzf encounter_continuum_round5_delta_20260717.tar.gz -C /absolute/path/to/valley-k-small
```

Verify the theorem and audit hashes from the receiving repository root:

```bash
shasum -a 256 research/reports/encounter_multimodal_prr/notes/continuum_c1_varying_space_resolvent_mosco_candidate.md
shasum -a 256 research/reports/encounter_multimodal_prr/audits/continuum_c1_varying_space_resolvent_mosco_round5_20260717.md
python3 scripts/reportctl.py check-docs-paths
python3 scripts/reportctl.py validate-science-rules
```

