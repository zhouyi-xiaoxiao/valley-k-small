# Round 170: production killing-geometry two-repeat outer replay

Date: 2026-07-17

Status: **PASS TWO-REPEAT CLEAN-PROCESS KILLING-GEOMETRY REPLAY ONLY / HOLD CONCRETE KILLING / HOLD SAME-MEMBER OPERATOR / HOLD F0 / HOLD F1 / HOLD CONTINUUM / HOLD RELEASE**

## Exact accepted bytes

- outer runner:
  `code/run_rate_defined_tensor_f0_production_killing_geometry_independent_replay.py`,
  SHA-256
  `1a3cecc0ca323b4744f6056a82c322bb71b75e703aab4cf5b418e515357e9e84`;
- separate-source child:
  `code/rate_defined_tensor_f0_production_killing_geometry_independent.py`,
  SHA-256
  `70942ed70eabd1cca48499d004550670bd12acfe714e4d6ca43308a210f1fb4d`;
- operation model SHA-256:
  `53f709139c380e9512740a6fdabcd7570c1822650817915454ddbd7d7395feb0`;
- complete input-snapshot SHA-256:
  `310539bd1cda2c2aead43a92851f76ce6dfaf7c048e41697d08beb2bd2171ab8`;
- canonical outer receipt:
  `artifacts/data/physical_production_killing_geometry_two_repeat_outer_receipt_v1.json`,
  SHA-256
  `d635dfb7dd24fc15731dfd69e20264a5515c3bf82b92569a58cd2bed3264fcd9`;
- deterministic child semantic receipt SHA-256:
  `e28d5bf63abfcf1f44ace9c701a806f680e43a7964de036bd204963110d95eb2`;
- Round-170 exact-hash cleanup test:
  `code/test_round170_outer_replay_cleanup_exact_hash_audit.py`,
  SHA-256
  `94cf332cac356789ce7ae988692965d9a5d6a4c9b41f391cfdb247da0c638041`.

The outer receipt is canonical JSON and records two serialized child runs with
distinct PIDs, identical 14,732-byte semantic receipts, four equal
origin/stage snapshots per run, empty stderr, successful child exit, and
complete cleanup of the private stages.

## Replayed outer guarantees

For both child runs the receipt records:

- direct-child reap and absent process group;
- independent stdout and stderr EOF;
- closed parent pipe descriptors and selector;
- absent private stage after completion;
- identical pre-copy, post-copy, pre-launch, and post-exit snapshot digests;
- no initial-stream or producer-module import;
- no largest-state tensor allocation; and
- exact containment of all declared control-free contact and profile geometry
  factors by the separate-source same-backend oracle.

The two child observations differ, as required, in nonce, PID, timing, and
resource observations.  Only the deterministic semantic body is required to
be byte-identical.

## Cleanup regression check

The hash-specific Round-170 attack was rerun on these exact bytes:

```text
.venv/bin/python -m pytest -q \
  research/reports/encounter_multimodal_prr/code/test_round170_outer_replay_cleanup_exact_hash_audit.py
.....                                                                    [100%]
5 passed
```

The tests cover both pre-effect and post-effect `close(2)` faults during the
final reread, descriptor-number reuse for the reopened parent directory, no
descriptor leak, and rollback of a publication whose cleanup cannot be
confirmed.

## Exact acceptance boundary

This round closes the Round-169 request for a serialized, two-repeat,
clean-process outer replay of the **control-free factorized killing geometry**.
It does not construct a control row, budget, tensor killing diagonal, or
reconstructed multiplier.  It also does not bind the geometry factors to one
globally gauged stationary member and one common-flux operator.

The receipt itself keeps the following material flags false:

```text
concrete_killing_constructed              = false
single_physical_operator_bound            = false
full_operator_bound                       = false
production_resource_gate                  = false
f0_pass                                   = false
f1_authorized                             = false
continuum_verified                        = false
topology_complete                         = false
resource_promotion_eligible               = false
prr_release_authorized                    = false
```

It additionally records that the sentinel is a same-backend higher-precision
check, not backend independence; complete binary-dependency filesystem closure
and OS network isolation are not claimed.  Round 170 therefore authorizes only
the geometry source for subsequent source-bound bridge work.
