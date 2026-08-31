# Round 147: selector-v2 orphan-lock independent recheck

Date: 2026-07-14  
Reviewer: independent science-free concurrency and resource auditor  
Decision: **REJECT ROUND-146 ORPHAN-LOCK CLOSURE / HOLD SELECTOR ACCEPTANCE / HOLD F0 / HOLD F1**  
Findings: **P0 = 0, P1 = 1, P2 = 0**

## 1. Scope and science boundary

This round rechecked the exact repaired selector bytes named by Round 146.  It
was restricted to synthetic certificate, process-lifetime, and resource
fixtures.  It did not read a prospective control, evaluate positive budget,
run a physical semigroup row, execute F1/F2/F3, generate an event-law sample,
or inspect a scientific selector output.

The 8,000,000-trial command below is the selector's declared
`SYNTHETIC_RESOURCE_FIXTURE`.  Its pass is a method/resource result only and
cannot override a failed worker-lifetime invariant.

## 2. Frozen bytes actually tested

| object | SHA-256 |
| --- | --- |
| `code/f1_to_f2_common_observable_selector_v2.py` | `b80e720a0a88df053b3e9133582a0a27c31d513b3bb091da006f520a4e3bace6` |
| `code/test_f1_to_f2_common_observable_selector_v2.py` | `ed951bbe0c58084d49067e7941084e1bef9f9e215cb3162e195506aefd6230ba` |
| `code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py` | `e4c88f44f02e92deed9fbe4be742cdf03519d4811196e2413b0f3fd2b42b1345` |
| `code/test_f1_to_f2_common_observable_selector_v2_round139_independent.py` | `76ba6cb1b990fc632528e4cff5a9739242b9de87108d371e09c1ccca026c6b77` |
| `code/test_f1_to_f2_common_observable_selector_v2_round140_repair.py` | `1dfbf2fd7a72caa9afef120b0ef79df9759f5fc2bdd60105ea854cfaf8699f2f` |
| `code/test_f1_to_f2_common_observable_selector_v2_round143_certificate_repair.py` | `c8464e35c98dcfccc5ff726483bede774db58ce7512dc5f442f93031298aacdc` |
| `code/test_f1_to_f2_common_observable_selector_v2_round144_isolation_closure.py` | `f6808dfcd56ff2fa0735850fad34efed6f433389c5952dbede2e4f89331fac90` |

The source and the two Round-146-listed repair-test hashes match Round 146
exactly.  The additional hashes above make the 142-test replay surface
explicit.

Runtime was repository Python 3.12.13 on macOS 26.5.2 arm64.  The pre-resource
snapshot reported 24 GiB physical memory and 34% system-wide free memory.

## 3. Full regression replay

From the repository root, with bytecode and pytest cache writes disabled:

```text
env PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p \
  .venv/bin/python -m pytest -q -p no:cacheprovider \
  research/reports/encounter_multimodal_prr/code/test_f1_to_f2_common_observable_selector_v2.py \
  research/reports/encounter_multimodal_prr/code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py \
  research/reports/encounter_multimodal_prr/code/test_f1_to_f2_common_observable_selector_v2_round139_independent.py \
  research/reports/encounter_multimodal_prr/code/test_f1_to_f2_common_observable_selector_v2_round140_repair.py \
  research/reports/encounter_multimodal_prr/code/test_f1_to_f2_common_observable_selector_v2_round143_certificate_repair.py \
  research/reports/encounter_multimodal_prr/code/test_f1_to_f2_common_observable_selector_v2_round144_isolation_closure.py
```

Observed result:

```text
142 passed
real 44.75 s
user 25.67 s
sys   2.82 s
```

This aggregate green result is not sufficient: the parent-death test below is
schedule-sensitive and fails under isolated repetition on the same bytes.

## 4. Parent-death/orphan invariant: reproducible intermittent failure

The initial targeted command ran the normal two-parent invariant followed by
the orphan invariant:

```text
env PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p \
  .venv/bin/python -m pytest -q -p no:cacheprovider \
  research/reports/encounter_multimodal_prr/code/test_f1_to_f2_common_observable_selector_v2_round144_isolation_closure.py::test_round145_two_parents_never_have_two_resident_power_workers \
  research/reports/encounter_multimodal_prr/code/test_f1_to_f2_common_observable_selector_v2_round144_isolation_closure.py::test_round145_orphan_worker_retains_lock_after_parent_death
```

The normal two-parent check passed.  The orphan check failed at line 394 with:

```text
AssertionError: second parent spawned a worker while the orphan was resident
```

A single immediate retry passed.  Five further isolated repetitions produced
four passes and one failure with the same assertion.  Across the seven
targeted orphan invocations in this round, the outcome was therefore:

```text
passes    5
failures  2
```

The test deliberately stops the first worker before killing its parent.  A
second parent must remain blocked until that stopped orphan is killed.  Seeing
the second parent spawn a worker violates the claimed one-resident-worker
invariant, even though most schedules pass.

The source reasserts `flock` inside the child only after the child starts its
authorization path.  The observed schedule is consistent with an unsynchronized
parent-to-worker lock-ownership gap on this runtime; this is an inference, not
a complete root-cause proof.  The empirical invariant failure is sufficient to
hold acceptance.

## 5. Synthetic 8M resource replay

The resource state was adequate for the declared small-memory fixture, so it
was replayed once despite the independent concurrency HOLD:

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
maximum child peak RSS         55,492,608 bytes
process maximum RSS            55,541,760 bytes
wall time                      17.31 seconds
swaps                          0
schedule kind                  SYNTHETIC_RESOURCE_FIXTURE
positive_budget_evaluated      false
```

After the command, system-wide free memory was 36%.  Process inspection after
the failed targeted runs and again after the 8M replay found no live
`--internal-cp-worker` or `--internal-power-worker` belonging to this selector.
Thus cleanup passed in the observed runs, but cleanup does not repair the
overlap window detected above.

## 6. Finding and required closure

### [P1] The orphan-lock closure is schedule-dependent on macOS

Round 146 states that a second parent remains blocked while a stopped orphan
retains the inherited lock.  Exact-byte isolated replay falsified that statement
in 2 of 7 targeted schedules.  A passing 142-test aggregate and a passing 8M
fixture therefore cannot accept the current source.

Required closure:

1. remove the parent-to-worker ownership gap with a platform-robust lifetime
   mechanism rather than relying on a child reassertion that may not yet have
   executed;
2. freeze a new source hash and add a deterministic handshake/ownership fixture
   that covers death before and after child authorization;
3. stress the injected `SIGSTOP`/parent-death path repeatedly on macOS and at
   least one second POSIX platform, while asserting a maximum of one resident
   worker and zero leftovers; and
4. obtain a fresh independent exact-byte recheck before attaching the 8M
   resource result to any accepted selector record.

## 7. Final boundary

```text
Round-146 listed hashes                      MATCH
142-test aggregate                           PASS, NOT DECISIVE
normal two-parent concurrency                PASS
parent-death/orphan lock invariant           FAIL INTERMITTENTLY (2/7 TARGETED)
zero residual selector workers               PASS IN OBSERVED CLEANUPS
8M synthetic resource fixture                PASS (68/68, 0 swaps)
selector implementation-stage acceptance     HOLD
F0 / F1 / positive-budget science            NOT AUTHORIZED / NOT RUN
```

