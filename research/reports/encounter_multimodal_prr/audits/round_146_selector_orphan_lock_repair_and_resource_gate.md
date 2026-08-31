# Round 146: selector-v2 orphan-lock repair and final-source resource gate

Date: 2026-07-14  
Role: implementer plus science-free resource-gate operator  
Decision: **CANDIDATE PASS / HOLD INDEPENDENT RECHECK / HOLD F1**

## Frozen repaired bytes

```text
code/f1_to_f2_common_observable_selector_v2.py
b80e720a0a88df053b3e9133582a0a27c31d513b3bb091da006f520a4e3bace6

code/test_f1_to_f2_common_observable_selector_v2_round143_certificate_repair.py
c8464e35c98dcfccc5ff726483bede774db58ce7512dc5f442f93031298aacdc

code/test_f1_to_f2_common_observable_selector_v2_round144_isolation_closure.py
f6808dfcd56ff2fa0735850fad34efed6f433389c5952dbede2e4f89331fac90
```

## Parent-death repair

- The parent passes the already-held lock descriptor in `pass_fds` and names it
  through `ENCOUNTER_SELECTOR_V2_LOCK_FD`.
- The worker verifies that descriptor against the fixed lock path, owner,
  regular-file type, link count, device, and inode, then retains it for the
  complete worker lifetime.
- The parent no longer issues an explicit `LOCK_UN`: closing its descriptor
  cannot unlock the shared open-file description while the worker still holds
  it.
- Both capability-pipe ends are registered for fork cleanup.
- Inverse tests reject an unrelated inherited lock descriptor.
- A deterministic parent-death test stops the real worker, kills its parent,
  verifies that a second parent remains blocked, and releases it only after the
  orphan exits.  Three extra repetitions passed and left no worker behind.

## Tests

```text
focused Round-143/144/145 tests    32 passed
full selector regression          142 passed
ruff format/check                 PASS
```

## Final-source synthetic resource gate

Command, run once from the repository root:

```text
/usr/bin/time -l .venv/bin/python -I \
  research/reports/encounter_multimodal_prr/code/f1_to_f2_common_observable_selector_v2.py \
  --synthetic-power-resource-gate
```

Observed canonical summary:

```text
status                         PASS_SYNTHETIC_SCIENCE_FREE_POWER_RESOURCE_GATE
selector source SHA-256        b80e720a0a88df053b3e9133582a0a27c31d513b3bb091da006f520a4e3bace6
schedule SHA-256               928bef0c45ec7874c83547aaa5021ddf94513739698f41f960da96d308abd42f
N                              8,000,000
assertions                     68
PASS / FAIL                    68 / 0
maximum child peak RSS         55,394,304 bytes
parent maximum RSS             55,459,840 bytes
wall time                      16.41 seconds
swaps                          0
schedule kind                  SYNTHETIC_RESOURCE_FIXTURE
positive_budget_evaluated      false
```

Every receipt bound the same selector source, Python binary, runtime spec, and
schedule hashes.  This is a resource/certificate fixture, not a physical
control or a proxy for F1 outcomes.

## Remaining boundary

The post-hoc subprocess response cap remains a P2 resource-hardening item; a
streaming bounded reader would strengthen it.  More importantly, passing this
fixture does not accept F0, the future 36 F1 rows, the physical semigroup,
full-window topology, or any positive-budget result.  Round 147 is the
independent recheck of these exact repaired bytes.

