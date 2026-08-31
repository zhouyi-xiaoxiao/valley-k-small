# Encounter continuum Round-8 delta handoff

Date: 2026-07-17

Archive: `encounter_continuum_round8_delta_20260717.tar.gz`

- exact size: `64534` bytes;
- SHA-256:
  `cbaa71b2aabd485915cee01016fa5bcda837ae635f0cddfb34796610be205510`;
- member count: 14 unique relative paths;
- prerequisite: the verified Round-7 delta has already been applied;
- this README is outside the archive, avoiding a self-referential hash.

## Members and scope

The archive contains only:

1. `research/docs/RESEARCH_SUMMARY.md`;
2. `research/reports/encounter_multimodal_prr/README.md`;
3. `research/reports/encounter_multimodal_prr/notes/REMOTE_CODEX_HANDOFF_20260715.md`;
4. `research/reports/encounter_multimodal_prr/audits/continuum_c1_symbolic_bridge_neutral_contract_round8_20260717.md`;
5. `research/reports/encounter_multimodal_prr/artifacts/data/continuum_c1_symbolic_bridge_neutral_source_v1.json`;
6. `research/reports/encounter_multimodal_prr/artifacts/data/continuum_c1_symbolic_bridge_neutral_outer_manifest_v1.json`;
7. `research/reports/encounter_multimodal_prr/code/continuum_c1_symbolic_bridge_neutral_operation_model_v1.json`;
8. `research/reports/encounter_multimodal_prr/artifacts/data/continuum_c1_symbolic_bridge_neutral_fixture_v1.json`;
9. `research/reports/encounter_multimodal_prr/code/build_continuum_c1_symbolic_bridge_neutral_fixture_v1.py`;
10. `research/reports/encounter_multimodal_prr/code/validate_continuum_c1_symbolic_bridge_neutral_fixture_v1.py`;
11. `research/reports/encounter_multimodal_prr/code/test_continuum_c1_symbolic_bridge_neutral_fixture_v1.py`;
12. `research/reports/encounter_multimodal_prr/code/test_continuum_c1_symbolic_bridge_neutral_fixture_mutations_v1.py`;
13. `research/reports/encounter_multimodal_prr/artifacts/data/continuum_c1_symbolic_bridge_neutral_fixture_currentness_v1.json`; and
14. `research/reports/encounter_multimodal_prr/code/test_continuum_c1_symbolic_bridge_neutral_fixture_currentness_v1.py`.

Every member is an ordinary relative path with no absolute path or `..`
traversal.  The archive contains no control, budget, result, production-centre,
scratch, virtual-environment, cache, PDF, manuscript, prior archive, formal
symbolic production candidate, or symbolic acceptance receipt payload.  No
network access was used to build or audit it.

The theorem-first manuscript remains unchanged at seven main plus twenty-four
Supplemental physical pages.  Round 8 is a neutral exact-rational
schema/contract fixture.  It does not close complete C0, C1, C2, C3, science
execution, release, or submission.

## Frozen audit and ten-file hashes

The canonical Round-8 audit has SHA-256

```text
981f0b203ea5dd80204b258009e4614061bb5a815dd9fc7e8eefa70d6fce47c3
```

The ten-file closure is:

```text
source       2d038789cef7e863d45775d51fda0023e6082e22228be5314edc3b9185a6b6b6
outer        c196209e09cb7f0d4f51208e2f5c6173d201762bbd73f217110b8604c41158f1
opmodel      0870dd15d1b76933f87761368cb801e8ec186c50472f7686ce11f0d9ab9dee15
artifact     2aa8facd4f820ae4d28af9eadb4acf095e64f68d3742c4816d9f02337413ebee
builder      27a3ed5b4c1066a590463ad43f68bebb60362780edd05903309848b4a0f76718
validator    727ec3bb18a22e098b3e977fbfa17a3be14f09b54ccc707433f7ba559e35523d
static       88ea2b30061856761c3be057ecfb47c565a7a46afb5c46532384145d9d51cdbc
mutations    faabae1c29889f7d0703c63eae860089b19b92a1086bc8d008f2bf5a84ac0284
currentness  6ad86a1b187f39cfdb0baba7f958e30a6a72fdc639a219234565c344629e130b
gate         807065b1e90dcc7fdd2229466648abdc0e5e706477b0f42e8abe4a918d492d89
```

Two independent final read-only reviews report `P0=P1=P2=0` on these exact
bytes.  The audit records the earlier currentness race P1 and its
descriptor-relative repair.  These are local adversarial reviews, not external
referee acceptance.

## Receiving-Mac procedure

Allow OneDrive to finish syncing both files.  From their directory, verify
before extraction:

```bash
shasum -a 256 encounter_continuum_round8_delta_20260717.tar.gz
stat -f '%z bytes' encounter_continuum_round8_delta_20260717.tar.gz
tar -tzf encounter_continuum_round8_delta_20260717.tar.gz
```

The digest, size, and 14-member list must match this sidecar.  Preserve any
divergent local edits, then extract over the same repository root:

```bash
tar -xzf encounter_continuum_round8_delta_20260717.tar.gz -C /absolute/path/to/valley-k-small
```

From that repository root, verify the audit and run the neutral fixture:

```bash
shasum -a 256 research/reports/encounter_multimodal_prr/audits/continuum_c1_symbolic_bridge_neutral_contract_round8_20260717.md
python3 research/reports/encounter_multimodal_prr/code/build_continuum_c1_symbolic_bridge_neutral_fixture_v1.py --expected-operation-model-sha256 0870dd15d1b76933f87761368cb801e8ec186c50472f7686ce11f0d9ab9dee15 --check
python3 research/reports/encounter_multimodal_prr/code/validate_continuum_c1_symbolic_bridge_neutral_fixture_v1.py --expected-operation-model-sha256 0870dd15d1b76933f87761368cb801e8ec186c50472f7686ce11f0d9ab9dee15
python3 research/reports/encounter_multimodal_prr/code/test_continuum_c1_symbolic_bridge_neutral_fixture_v1.py
python3 research/reports/encounter_multimodal_prr/code/test_continuum_c1_symbolic_bridge_neutral_fixture_mutations_v1.py
python3 research/reports/encounter_multimodal_prr/code/test_continuum_c1_symbolic_bridge_neutral_fixture_currentness_v1.py
```

Expected results are 5/5 static tests, 46/46 mutation attacks, 8/8
currentness entries, and both direct entry points PASS.  These exact results
were reproduced once more from a clean temporary extraction of this archive,
not only from the source working directory.  Finish with:

```bash
python3 scripts/reportctl.py validate-registry
python3 scripts/reportctl.py validate-archives
python3 scripts/reportctl.py check-docs-paths
python3 scripts/reportctl.py validate-science-rules
```

The next production task must bind all eleven roles and produce a genuinely
independent acceptance receipt without treating the neutral witnesses as a
model.  The separate continuum task must repair or replace QF2 before proving
the complex-sector rate.
