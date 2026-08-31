# Allocation-cusp v6 independent post-result audit protocol

Date: 2026-07-14  
Status: **HOLD-INDEPENDENT-PRERUN; no mesh-65/97 launch authorization**

## 1. Boundary and no-cycle chain

This v6 protocol, auditor, and adversarial tests were prepared without opening
or creating any of the seven scientific/evidence/replica/audit/staging paths. They do
not authorize the first scientific launch: a fresh independent pre-run audit
must close the repaired package before any mesh 65 or 97 execution.

This protocol is intentionally not pinned by the discovery manifest.  The
manifest pins the producer, ordinary/Round-50/Round-61/Round-74/Round-80/Round-85
tests, scientific protocol, direct runtime dependencies, and the attacked
reports through the independent Round-84 finding.
The independent auditor
hard-codes only the externally frozen manifest SHA-256; this protocol records
the complete forward chain.  Therefore no file hashes itself directly or
indirectly.

| role | SHA-256 |
|---|---|
| discovery v6 manifest | `2e1223f6206c6ebc4adc5c11ed67672afdc55f68e90f725cf8b6930bb67b9948` |
| discovery runner | `b32260ad18abd3f159b7cac1dcd600be2507ff2a89cf60712c5c6f66ccbd70da` |
| ordinary discovery tests | `1b68eb77b087b18bb5136950482e7cbb5d12194cc3d6fd57f9cc8dfaf77ea722` |
| Round-50 regression tests | `073976ff5aa213cccd6b5d5f5442a1aa90229b28c0d9a124d4a3476a6f51b27d` |
| Round-61 regression tests | `10ddf64e29eecea182f15281b5f030c419ce589db29f536f9f72951a82bfd225` |
| Round-74 regression tests | `b593da1f93465469f50aacf7f6adc1b68a77a63df95547e9a1b0663c4d1427eb` |
| Round-80 regression tests | `25c7b4ba6e81bfc407c159194314f6295b0443d770ed61f11b4123c343b8c0ae` |
| Round-85 repair regressions | `60665c7edaa3cd5a85213415529c43ccd38c69a6390186075bff3c109bc341a9` |
| discovery protocol v6 | `3c56b307bed70c52152c31764aa84020b7c45770ea656e00fe1d54d47b51ab2b` |
| Stage-A algebra scaffold | `0bebbc97249d0aa0653923d44f11403a2f75d5a45794e89845d93ee74ae1b861` |
| Stage-A algebra tests | `c2370dfc69e1e775b486a8a9653f1877d2a28a5003999507ce65017bfcecc065` |
| promotion design | `ad072e83004ea3e3b5c3d01a58a872b5aedca74d13400fa04d6f917d4a06d1f5` |
| Round-36 design attack | `62c42f1220bd0eeaf9810be5ef2e7cf7f1ff0035b39354838a41cfdda84dd394` |
| Round-44 scaffold attack | `0a4edd23d3230c642fe8c5d9aa04ccd559ef5c8f24482643dffe5ff919b0c289` |
| Round-50 pre-run attack | `059e3f33b9a8e32cfe2e4ca26d1916dceac61b9fb53d89c77cdfdeb4a568829d` |
| Round-61 pre-run attack | `db1137c980113e09c5dba54efdad65903febb4c0c8b81e532743f890b11b48e0` |
| Round-74 pre-run attack | `ad70a82f8e406e9dae265283ead98d5e33355a3a27a0966d09f2fef7b766c96e` |
| Round-80 pre-run attack | `b27d3cb188a48bae08181bbfdadfaf0eea211dce1b9375485c6433a3bd8dbbcf` |
| Round-84 independent finding | `49d8163e749f909d25d48ad5634f60e285308ab3507c237ef6e9569e05ff6862` |
| positive-B v2 manifest | `955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c` |
| positive-B v2 protocol | `f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00` |
| positive-B v2 producer | `adb9434daeccca721ab9c1014f194e0cf9c5c6d0bf092d31e050c040b4b94da8` |
| B0 bridge result | `6a18e668401ae5776eebd7bd58c7bd553838db21998efdba2865cea094ae207b` |
| B0 bridge manifest | `263d4bd5e95f4cf477916948f2e4bbf3cd99066ac9dc9a9ab5726f2030a6f1e8` |
| B0 bridge producer | `d1d68667f5cbb9c8363a94f2f9ea22540f841065e02696f669beca9758e3a233` |
| finite-volume dependency | `7fa9ea6114328736c89739459c293aefa9311514764ec3cfe4f0ceb5a1875201` |
| grid dependency | `e0322b212e466b1b640f5adcf30d67d119d2f6fe4cc622eb532082b6cd251701` |
| continuum runtime dependency | `a553092f3d8bbf50fdf0124a3ea36ba32947c3b339cfcc0265a1cd7f6bc2d4da` |
| independent v6 auditor | `38b7822efce5ddd3b0220549a94a259f393c44150f66a61140f9b58029bf23f0` |
| independent auditor tests | `f2f38f04892d652cef9b88849cfb059defe7d3b3468ad4de86c66f333a2bd8fa` |

The auditor must not import `positive_b_allocation_cusp_discovery`.  Its test
suite contains a source-level guard for both import spellings.

## 2. Independently reconstructed checks

Using one stable `O_NOFOLLOW` capture of canonical JSON plus frozen files, the
auditor independently checks

1. the manifest hash and every report-relative pinned-file hash;
2. the bounded runtime provenance: exact Python executable/framework bytes,
   the stdlib tree including existing `pyc` and symlink metadata, every actual
   NumPy/SciPy wheel-`RECORD` file, the exact NumPy/SciPy and optional `.libs`
   import trees including unrecorded files and `__pycache__`, native-extension
   closures, exact NumPy build configuration, all signed arm64e dyld subcache
   CodeDirectory hashes, and the bounded 98-image non-system Mach-O closure;
   the auditor independently rebuilds install names, lexical/resolved paths,
   sizes, hashes, `LC_RPATH`s, recursive dependencies, and the exact
   13/93/94/98 phase sets rather than trusting manifest rows;
3. duplicate-key rejection and exact canonical bytes for result and evidence,
   plus the two-process hash/exit/status/byte-identity chain;
4. exact scope, timing, limitations, claims, and recursive schemas for every
   preflight, not-run, homotopy, cusp, mesh, branch, control, and phase
   PASS/HOLD variant;
5. frozen-budget, trust-box, chart-weight, model-diagnostic, and
   `density = B * density_per_budget` identities at every applicable cusp,
   homotopy, fold, control, scan, and tail row;
6. frozen FV spacings, normalization/contact/quadrature/row-sum factor gates;
   midpoint/contact killing primitives; independently reconstructed SG and
   periodic generator traces; exact killed-operator trace and installed
   budget; all 691 scan rows; the exact 70-row projection; every aggregate,
   endpoint, and sign-change bracket; every `all_bracketed_roots` entry and
   every comparison-node scan, and their positivity, survival, state,
   generator, mass, and budget laws;
7. cusp Jacobian scaling, singular values, determinant factorization,
   derivative-audit implications, and exact cusp gates;
8. exact greedy comparison-node selection and cusp-anchored global root order,
   origin brackets, predecessor/successor lineage, adjacent drift, and HOLD on
   birth, death, crossing, replacement, unmatched lineage, or excess drift;
9. individual basin masses from successive minimum survivals, basin
   cardinality, final state/survival, the four exact score margins, top-three
   advancement, and representative membership; and
10. mesh-97 cusp-centred direct phase formulas, complete pin/lexical snapshots,
   the first-child five-path absence record, and the exact allowed path/stage
   boundary revalidated at each replica launch.

The test suite includes both an honest preflight HOLD and a complete synthetic
scientific PASS with both meshes, both branches, all comparison scans, 32
screened controls, nine advanced controls, and three representatives.  Any
unknown, missing, or inconsistent nested field fails closed.

The Python interpreter and the stdlib modules needed to compute the first hash
are an explicit bootstrap root of trust.  The stdlib closure is therefore a
reproducibility/drift attestation, not hostile-stdlib prevention.  In contrast,
the NumPy/SciPy import-tree, `RECORD`, native-extension, and signed-dyld bytes
are checked before any third-party path is added by each formal `-I -S -B`
process. The exact non-system image sets are then checked at the pure runner,
post-manifest-validation, and full-stack checkpoints. The one 93-to-94
transition is fixed to `signed_dyld_cache_provenance.platform.mac_ver` loading
`pyexpat`; it is not hidden in the pure runner phase. `-I` requires active
per-process hash randomization and ignores `PYTHONHASHSEED`; no fixed-hash claim
is made, and every unordered boundary is explicitly sorted. `-B` prevents
cache writes but is not treated as preventing reads of a forged valid `pyc`;
the exact import-tree closure is the control for that case. These controls are
reproducibility witnesses under the no-concurrent-writer contract, not a claim
to prevent a malicious same-UID process.

Any structural discrepancy yields `HOLD_AUDIT`.  A scientifically valid
`HOLD_DISCOVERY` yields `HOLD_SCIENCE_AUDIT_VALID`: audit integrity passed but
science did not.  Only integrity plus `PASS_DISCOVERY_LOW_MESH_ONLY` yields
`PASS_AUDIT_DISCOVERY_LOW_MESH_ONLY` and process exit 0.

## 3. Filesystem boundary and producer-reported quantities not recomputed

The scientific and audit windows require no concurrent writer and no OneDrive
replacement/relink/restore.  Inputs are captured through lexical `lstat`,
`O_NOFOLLOW`, stable descriptors, exact bytes, and device/inode/mode/size/mtime
metadata.  At audit start both canonical inputs must be ordinary regular files,
both hidden replicas and the append-only audit output must be absent, and no
stale canonical or audit artifact is silently deleted.  The writer records the
device/inode it created; snapshot drift rolls back only that exact owned inode.
An unowned or replaced output survives a failed audit.

The auditor does **not** recompute matrix exponentials, exclude an
even-multiplicity root wholly inside one `0.05` scan interval, rerun cusp/fold
Newton solves, or rebuild the complete finite-volume matrices.  It does
independently rebuild their analytic generator traces and checks all serialized
diagnostics, algebraic identities, thresholds, and implications.  Thus a pass
is independent post-result contract/algebra auditing, not an independent
solver, continuum proof, held-out confirmation, manuscript confirmation, or
publication gate.

## 4. Frozen commands

Before any separately authorized scientific launch, from the repository root,
the one combined 106-test command (the original 97 plus nine Round-85
regressions) is:

```bash
.venv/bin/python -m ruff format --check \
  research/reports/encounter_multimodal_prr/code/positive_b_allocation_cusp_discovery.py \
  research/reports/encounter_multimodal_prr/code/audit_positive_b_allocation_cusp_discovery_result.py \
  research/reports/encounter_multimodal_prr/code/positive_b_allocation_cusp_stage_a.py \
  research/reports/encounter_multimodal_prr/code/test_positive_b_allocation_cusp_discovery*.py \
  research/reports/encounter_multimodal_prr/code/test_audit_positive_b_allocation_cusp_discovery_result.py \
  research/reports/encounter_multimodal_prr/code/test_positive_b_allocation_cusp_stage_a.py

.venv/bin/python -m ruff check \
  research/reports/encounter_multimodal_prr/code/positive_b_allocation_cusp_discovery.py \
  research/reports/encounter_multimodal_prr/code/audit_positive_b_allocation_cusp_discovery_result.py \
  research/reports/encounter_multimodal_prr/code/positive_b_allocation_cusp_stage_a.py \
  research/reports/encounter_multimodal_prr/code/test_positive_b_allocation_cusp_discovery*.py \
  research/reports/encounter_multimodal_prr/code/test_audit_positive_b_allocation_cusp_discovery_result.py \
  research/reports/encounter_multimodal_prr/code/test_positive_b_allocation_cusp_stage_a.py

.venv/bin/python -m py_compile \
  research/reports/encounter_multimodal_prr/code/positive_b_allocation_cusp_discovery.py \
  research/reports/encounter_multimodal_prr/code/audit_positive_b_allocation_cusp_discovery_result.py \
  research/reports/encounter_multimodal_prr/code/positive_b_allocation_cusp_stage_a.py \
  research/reports/encounter_multimodal_prr/code/test_positive_b_allocation_cusp_discovery*.py \
  research/reports/encounter_multimodal_prr/code/test_audit_positive_b_allocation_cusp_discovery_result.py \
  research/reports/encounter_multimodal_prr/code/test_positive_b_allocation_cusp_stage_a.py

.venv/bin/python -m pytest -p no:cacheprovider -q \
  research/reports/encounter_multimodal_prr/code/test_positive_b_allocation_cusp_discovery.py \
  research/reports/encounter_multimodal_prr/code/test_positive_b_allocation_cusp_discovery_round50.py \
  research/reports/encounter_multimodal_prr/code/test_positive_b_allocation_cusp_discovery_round61.py \
  research/reports/encounter_multimodal_prr/code/test_positive_b_allocation_cusp_discovery_round74.py \
  research/reports/encounter_multimodal_prr/code/test_positive_b_allocation_cusp_discovery_round80.py \
  research/reports/encounter_multimodal_prr/code/test_positive_b_allocation_cusp_discovery_round85.py \
  research/reports/encounter_multimodal_prr/code/test_audit_positive_b_allocation_cusp_discovery_result.py \
  research/reports/encounter_multimodal_prr/code/test_positive_b_allocation_cusp_stage_a.py
```

Only after a separately authorized two-replica run has promoted a canonical
result and evidence may the append-only auditor run exactly once:

```bash
.venv/bin/python \
  research/reports/encounter_multimodal_prr/code/audit_positive_b_allocation_cusp_discovery_result.py
```

The append-only output is
`artifacts/data/positive_b_allocation_cusp_discovery_independent_audit.json`.
Exit 0 means both audit integrity and low-mesh discovery passed.  Exit 2 means
either an honest scientific HOLD or an audit HOLD; inspect `release_status` and
`failed_checks` to distinguish them.  An operational failure publishes no
audit artifact.
