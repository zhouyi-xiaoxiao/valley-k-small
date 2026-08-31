# Outer-replay cleanup repair: exact-hash pre-audit

Date: 2026-07-16

Status: **IMPLEMENTATION REPAIR PASS / EXACT-HASH ADVERSARIAL TEST PASS / HOLD INDEPENDENT REVIEW / HOLD FORMAL OUTER REPLAY / HOLD ROUND 170**

This record is an implementation-side pre-audit.  It is deliberately not
described as an independent reviewer acceptance and does not authorize the
formal two-repeat replay.

## Frozen candidate

- outer runner SHA-256:
  `1a3cecc0ca323b4744f6056a82c322bb71b75e703aab4cf5b418e515357e9e84`;
- primary outer-runner tests SHA-256:
  `84aa1427881343e59471f6609d6c76fbea5830924aa3bd2147a8845e4044b401`.

The accepted upstream child, operation-model and design pins remain those in
Round 169.  No science-bearing input or output was read or changed.

## Repairs

1. `_read_published_at()` now closes its final reread descriptor through the
   shared confirmed-close primitive.  A close failure is retried and an
   unconfirmed close raises `ReplayHold(HOLD_CLEANUP)` rather than leaking a
   native `OSError` across the replay boundary.
2. The reopened-parent cleanup fixture now identifies the cleanup phase by
   closure/phase evidence.  It no longer assumes that a reopened descriptor
   must have a different integer value; the tested runtime reuses the original
   descriptor number.

## Separate exact-hash attack layer

`code/test_round170_outer_replay_cleanup_exact_hash_audit.py` does not modify
the frozen runner or primary-test candidate.  It pins both candidate hashes
and attacks:

- a final-reread close error before the close effect;
- a final-reread close error reported after the close effect;
- reopened-parent descriptor-number reuse;
- receipt removal and `EBADF` confirmation after the cleanup branch;
- the source-level absence of a bare final-reread `os.close(descriptor)`.

The attack layer passed 5/5 tests.  The combined primary and attack suites
passed 34/34 tests.  `py_compile` and Ruff passed for the candidate and attack
files.

## Commands reproduced

```text
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_run_rate_defined_tensor_f0_production_killing_geometry_independent_replay.py
# 29 passed

.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_round170_outer_replay_cleanup_exact_hash_audit.py
# 5 passed

.venv/bin/python -m pytest -q \
  research/reports/encounter_multimodal_prr/code/test_run_rate_defined_tensor_f0_production_killing_geometry_independent_replay.py \
  research/reports/encounter_multimodal_prr/code/test_round170_outer_replay_cleanup_exact_hash_audit.py
# 34 passed
```

## Remaining gate

A fresh reviewer/process must independently inspect and execute the exact
frozen candidate above.  Only an exact-hash independent GO may authorize a
formal replay in a fresh current-UID mode-0700 directory under `/private/tmp`.
Until that event there is no Round 170 receipt, no concrete-killing promotion,
no F0/F1/F3 promotion, no positive-budget evaluation and no manuscript
release.

