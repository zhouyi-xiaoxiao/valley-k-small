# Round-83 allocation-cusp v5 implementer freeze report

Date: 2026-07-14  
Status: **HOLD-INDEPENDENT-PRERUN; no mesh-65/97 launch authorization**

## 1. Freeze decision

The repaired allocation-cusp v5 package meets the implementer freeze criteria. The implementer adversarial ledger has `P0 = 0`, `P1 = 0`, and `P2 = 0` open findings. This is not scientific execution approval: an independent pre-run attack must still accept these exact bytes before any mesh 65 or 97 command can be authorized. No Stage-A discovery result, reproducibility evidence, replica, or independent-audit artifact exists.

## 2. Closed defects

- Killed-generator diagnostics now expose primitive midpoint/contact extrema and sums plus both free-generator diagonal sums. Producer and auditor independently rebuild both Scharfetter-Gummel traces and the killed trace.
- The stationary scan serializes and reconstructs all 691 grid rows, the exact 70-row projection, extrema/error aggregates, endpoint signs, and every grid-aligned bracket.
- Every error, residual, norm, singular value, absolute mismatch, drift, and event mass accepted by a gate is a native finite nonnegative number.
- The parent rechecks the exact allowed output/staging boundary before and after every replica. Rollback removes only an inode owned by the current invocation; foreign/replaced files survive failure.
- Formal parent and replicas use `-I -S -B`, a harmless environment allowlist, no `PYTHON*` import injection, and no `DYLD_*`/`LD_*` loader injection. Four local runtime modules are descriptor-bound to exact manifest-pinned bytes and preloaded same-name modules fail closed.
- Before any third-party path is appended, every formal process verifies the Python executable/framework, exact stdlib tree, actual NumPy/SciPy wheel-`RECORD` bytes, complete NumPy/SciPy and optional `.libs` import trees (including all `pyc`, unrecorded files, and symlink metadata), native-extension closures, exact NumPy build configuration, and 13 signed arm64e dyld subcache CodeDirectory hashes.
- `-B` is not misrepresented as blocking bytecode reads. An unchecked-hash forged `pyc` regression proves that such bytecode executes under `-B` and that the exact import-tree closure detects the same-path mutation.
- The pinned legacy Stage-A scaffold now delays only its bridge import. This removes pytest collection pollution without changing any physical parameter, solver, algebra, seed, guard, or result semantics; explicit formal-module preloading remains rejected.

## 3. Runtime trust boundary

The interpreter and the stdlib modules needed to compute the first hash are an explicit bootstrap root of trust. The stdlib closure is a reproducibility/drift attestation, not hostile-interpreter prevention. The stronger pre-third-party claim is limited to the frozen NumPy/SciPy/import-tree/native closure verified before `sys.path` is extended. The scientific window also retains the explicit no-concurrent-writer/no-OneDrive-replacement contract.

## 4. Validation evidence

| check | result |
|---|---|
| one-process combined allocation collection | 97/97 PASS, exit 0 |
| discovery + Round-50/61/74/80 + auditor group | 86/86 PASS, exit 0 |
| Stage-A group | 11/11 PASS, exit 0 |
| converted Round-80 regression module | 25/25 PASS, exit 0 |
| independent auditor subset | 8/8 PASS inside the 86-test group |
| Ruff format check | 10 files already formatted |
| Ruff lint | all checks passed |
| Python bytecode compilation | all 10 target modules compiled |
| formal entry smoke | isolated cells-7 algebra only; PASS; no scientific output |
| output boundary after all tests | five scientific/evidence/audit paths and two promotion staging paths absent |

The 97-test collection originally exposed a reproducible test-order failure: module-level Stage-A collection preloaded `continuum_g1_smoke`, which the formal loader correctly rejected. The import-timing-only Stage-A repair closed that CI issue. The same 97-test command then passed without weakening the fail-closed loader.

## 5. Stage-A byte-diff scope

The Stage-A source change is deliberately mechanical and import-only:

1. remove the module-level `import continuum_broad_patch_b0_bridge as bridge`;
2. add a cached `bridge_module()` using `importlib.import_module` on first algebra execution;
3. obtain that identical bridge at the start of `build_small_grid_model`; and
4. replace the non-runtime `factors` annotation with `Any`.

All original calls to `parameters_from_manifest` and `build_fv_factors` and all downstream calculations are unchanged. Because no scientific Stage-A run exists and the new Stage-A bytes are directly pinned by the rebuilt manifest, this does not alter or post-fit a scientific result.

## 6. Frozen hash roots

| role | path | SHA-256 |
|---|---|---|
| discovery manifest | `artifacts/data/positive_b_allocation_cusp_discovery_manifest.json` | `a28ae5c17d3a93139a122dbfc1d6890d74fae69bad9bbac950e42c74a20b31d0` |
| discovery runner | `code/positive_b_allocation_cusp_discovery.py` | `8b80898f02b132d6a8e07aec8e8ce6c54fe8930f989d93bb68410dc8eb2d6662` |
| discovery protocol | `notes/positive_b_allocation_cusp_discovery_protocol.md` | `834e382c901d1fb060168ac388641d347a86b4293f346b437bdb0f659850165d` |
| Stage-A scaffold | `code/positive_b_allocation_cusp_stage_a.py` | `0bebbc97249d0aa0653923d44f11403a2f75d5a45794e89845d93ee74ae1b861` |
| Stage-A tests | `code/test_positive_b_allocation_cusp_stage_a.py` | `c2370dfc69e1e775b486a8a9653f1877d2a28a5003999507ce65017bfcecc065` |
| Round-80 regressions | `code/test_positive_b_allocation_cusp_discovery_round80.py` | `faf4f060639c69ca483d78832a5fff4b39aff11f8cddeada9ecaf3626220887c` |
| independent auditor | `code/audit_positive_b_allocation_cusp_discovery_result.py` | `3baac627078ca3f43b25d108df2b089775fdc51ddebe5193310567249b4076ab` |
| independent auditor tests | `code/test_audit_positive_b_allocation_cusp_discovery_result.py` | `f2f38f04892d652cef9b88849cfb059defe7d3b3468ad4de86c66f333a2bd8fa` |
| post-result no-cycle protocol | `notes/positive_b_allocation_cusp_postresult_audit_protocol_v1.md` | `34a30fc3cd1a17074cc4b7286218527a79dc9ca8c1d7734f841ae9e9ed866791` |

The manifest contains the authoritative complete 25-pin map:

| manifest role | report-relative path | SHA-256 |
|---|---|---|
| B0_bridge_manifest | `artifacts/data/continuum_broad_patch_b0_bridge_manifest.json` | `263d4bd5e95f4cf477916948f2e4bbf3cd99066ac9dc9a9ab5726f2030a6f1e8` |
| B0_bridge_producer | `code/continuum_broad_patch_b0_bridge.py` | `d1d68667f5cbb9c8363a94f2f9ea22540f841065e02696f669beca9758e3a233` |
| B0_bridge_result | `artifacts/data/continuum_broad_patch_b0_bridge_result.json` | `6a18e668401ae5776eebd7bd58c7bd553838db21998efdba2865cea094ae207b` |
| continuum_runtime_dependency | `code/continuum_observable_four_patch.py` | `a553092f3d8bbf50fdf0124a3ea36ba32947c3b339cfcc0265a1cd7f6bc2d4da` |
| finite_volume_dependency | `code/continuum_weak_budget_design.py` | `7fa9ea6114328736c89739459c293aefa9311514764ec3cfe4f0ceb5a1875201` |
| grid_dependency | `code/continuum_g1_smoke.py` | `e0322b212e466b1b640f5adcf30d67d119d2f6fe4cc622eb532082b6cd251701` |
| positive_B_v2_manifest | `artifacts/data/positive_b_broad_four_slab_manifest.json` | `955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c` |
| positive_B_v2_producer | `code/positive_b_broad_four_slab.py` | `adb9434daeccca721ab9c1014f194e0cf9c5c6d0bf092d31e050c040b4b94da8` |
| positive_B_v2_protocol | `notes/positive_b_broad_four_slab_protocol.md` | `f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00` |
| promotion_design | `notes/positive_b_allocation_cusp_promotion_design.md` | `ad072e83004ea3e3b5c3d01a58a872b5aedca74d13400fa04d6f917d4a06d1f5` |
| protocol | `notes/positive_b_allocation_cusp_discovery_protocol.md` | `834e382c901d1fb060168ac388641d347a86b4293f346b437bdb0f659850165d` |
| round_36_design_attack | `audits/round_36_allocation_cusp_design_attack.md` | `62c42f1220bd0eeaf9810be5ef2e7cf7f1ff0035b39354838a41cfdda84dd394` |
| round_44_scaffold_attack | `audits/round_44_allocation_cusp_stage_a_code_attack.md` | `0a4edd23d3230c642fe8c5d9aa04ccd559ef5c8f24482643dffe5ff919b0c289` |
| round_50_attack_tests | `code/test_positive_b_allocation_cusp_discovery_round50.py` | `30ecf71b426705efa2b6728048093d2da5b96d507c89edc43883579dc4847dbb` |
| round_50_prerun_attack | `audits/round_50_allocation_discovery_prerun_attack.md` | `059e3f33b9a8e32cfe2e4ca26d1916dceac61b9fb53d89c77cdfdeb4a568829d` |
| round_61_attack_tests | `code/test_positive_b_allocation_cusp_discovery_round61.py` | `10ddf64e29eecea182f15281b5f030c419ce589db29f536f9f72951a82bfd225` |
| round_61_prerun_attack | `audits/round_61_allocation_v2_independent_prerun_attack.md` | `db1137c980113e09c5dba54efdad65903febb4c0c8b81e532743f890b11b48e0` |
| round_74_attack_tests | `code/test_positive_b_allocation_cusp_discovery_round74.py` | `b593da1f93465469f50aacf7f6adc1b68a77a63df95547e9a1b0663c4d1427eb` |
| round_74_prerun_attack | `audits/round_74_allocation_v3_independent_prerun_attack.md` | `ad70a82f8e406e9dae265283ead98d5e33355a3a27a0966d09f2fef7b766c96e` |
| round_80_attack_tests | `code/test_positive_b_allocation_cusp_discovery_round80.py` | `faf4f060639c69ca483d78832a5fff4b39aff11f8cddeada9ecaf3626220887c` |
| round_80_prerun_attack | `audits/round_80_allocation_v4_independent_prerun_attack.md` | `b27d3cb188a48bae08181bbfdadfaf0eea211dce1b9375485c6433a3bd8dbbcf` |
| runner | `code/positive_b_allocation_cusp_discovery.py` | `8b80898f02b132d6a8e07aec8e8ce6c54fe8930f989d93bb68410dc8eb2d6662` |
| stage_a_scaffold | `code/positive_b_allocation_cusp_stage_a.py` | `0bebbc97249d0aa0653923d44f11403a2f75d5a45794e89845d93ee74ae1b861` |
| stage_a_tests | `code/test_positive_b_allocation_cusp_stage_a.py` | `c2370dfc69e1e775b486a8a9653f1877d2a28a5003999507ce65017bfcecc065` |
| tests | `code/test_positive_b_allocation_cusp_discovery.py` | `69ff2b7b781977786fed91769c02037b8ccae2868784f221d5c50530e4baafbc` |

## 7. Allowed independent pre-run checks

The following checks are read-only with respect to frozen sources; pytest writes only to its temporary directory because the cache provider and bytecode writes are disabled:

```bash
ROOT=/Users/ae23069/Library/CloudStorage/OneDrive-UniversityofBristol/Desktop/valley-k-small
cd "$ROOT/research/reports/encounter_multimodal_prr"

PYTHONDONTWRITEBYTECODE=1 ../../../.venv/bin/python -m ruff format --check code/positive_b_allocation_cusp_discovery.py code/audit_positive_b_allocation_cusp_discovery_result.py code/positive_b_allocation_cusp_stage_a.py code/test_positive_b_allocation_cusp_discovery*.py code/test_audit_positive_b_allocation_cusp_discovery_result.py code/test_positive_b_allocation_cusp_stage_a.py

PYTHONDONTWRITEBYTECODE=1 ../../../.venv/bin/python -m ruff check code/positive_b_allocation_cusp_discovery.py code/audit_positive_b_allocation_cusp_discovery_result.py code/positive_b_allocation_cusp_stage_a.py code/test_positive_b_allocation_cusp_discovery*.py code/test_audit_positive_b_allocation_cusp_discovery_result.py code/test_positive_b_allocation_cusp_stage_a.py

PYTHONDONTWRITEBYTECODE=1 ../../../.venv/bin/python -m pytest -p no:cacheprovider -q code/test_positive_b_allocation_cusp_discovery.py code/test_positive_b_allocation_cusp_discovery_round50.py code/test_positive_b_allocation_cusp_discovery_round61.py code/test_positive_b_allocation_cusp_discovery_round74.py code/test_positive_b_allocation_cusp_discovery_round80.py code/test_audit_positive_b_allocation_cusp_discovery_result.py code/test_positive_b_allocation_cusp_stage_a.py
```

The independent attack may also parse/re-hash the manifest and inspect source/protocol bytes. It must not invoke `--execute-frozen`, `--execute-replica`, call `run_formal` without complete mocks, or construct/evaluate mesh 65 or 97.

## 8. Remaining scientific boundary

Even a later low-mesh PASS would remain only `PASS_DISCOVERY_LOW_MESH_ONLY`: same solver family, fixed box, meshes 65 and 97, no held-out parity/box/continuum/independent-solver evidence, and no theorem excluding an even-multiplicity root between scan samples. The current decision is earlier and stricter: **HOLD-INDEPENDENT-PRERUN**.


