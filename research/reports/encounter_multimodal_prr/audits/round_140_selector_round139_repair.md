# Round 140: selector-v2 repair of the Round-139 HOLDs

Date: 2026-07-14  
Role: implementer and science-free resource-gate operator  
Repair decision: **CANDIDATE PASS FOR THE ROUND-139 P0 AND TWO P1 FINDINGS**  
Release decision: **HOLD F1 / HOLD POSITIVE B PENDING INDEPENDENT ATTACK AND F0**

## Frozen predecessor

Round 139 attacked selector source SHA-256

```text
118d33446c986c1ca07c129886000a0812550a3976e0d7c7879b9f833fdda5b1
```

and found one P0 and two P1 defects: the numerical worker did not verify the
actual loaded gmpy2/MPFR/GMP/MPC runtime, the public powered-assertion path
retained MPFR pages in its parent, and distinct workers had no aggregate
concurrency limit.  The Round-139 audit remains the authoritative record for
those frozen bytes.  No conclusion from its intentionally green defect
reproducers is treated as an acceptance signal.

## Repair boundary

The repair used only synthetic rational probability inputs.  It did not read a
prospective control, evaluate positive budget, run F0/F1/F2/F3, run a semigroup,
generate a trajectory, or run Monte Carlo.

The candidate source SHA-256 after the repair is

```text
cb236c6bf2c9ee09172d050748d7509db3ed4ca581fce374466618284e31671e
```

## P0 closure: actual runtime at the numerical call edge

Both internal numerical entry points now call `verify_runtime_spec()` after
canonical request parsing and before any CP, binomial-power, or DKW-power
evaluation.  That verifier compares the loaded Python binary, gmpy2 extension
and package, MPFR/GMP/MPC libraries and versions, MPFR context, jsonschema,
and precision/rounding contract to the frozen runtime specification.  A
mismatch returns `HOLD_DEPENDENCY_HASH`; inverse tests replace the verifier by
a forced HOLD and prove that the numerical evaluator receives zero calls.

A PASS response contains and the parent checks all of

```text
selector source SHA-256
Python binary SHA-256
runtime-spec SHA-256
runtime_verified = true
request SHA-256
operation
worker peak RSS
```

The parent rehashes the file identities after worker exit.  Hashing the spec
without checking the loaded runtime is no longer a PASS path.

## P1 closure: complete powered assertions behind terminating workers

The public binomial and DKW decisions now serialize canonical requests to a
fresh `python -I` worker.  The old MPFR evaluators are explicitly private
`*_in_process` functions used only inside the verified child and by numerical
unit oracles.  There is no public in-process production fallback.

`execute_powered_assertion_schedule` requires an exact immutable tuple of 68
exact dataclass records and the frozen family counts

```text
basin_compatibility       12
basin_floor               12
positive_contrast         16
survival_compatibility     6
window_compatibility      22
```

Every assertion crosses the same verified terminating-worker boundary.  Wrong
record, field, numeric, relation, length, or family types fail with a declared
`HOLD_POWER_BOUNDARY` rather than reaching MPFR.

## P1 closure: aggregate worker concurrency

A process-local `BoundedSemaphore(1)` and a user-owned `flock` file shared by
independent parent processes guard every CP and powered-assertion subprocess
launch.  The lock descriptor is opened with close-on-exec and no-follow where
supported; its regular-file type, owner, and link count are checked before
locking.  Threaded inverse tests observed one simultaneous child, and two
independent Python parents held non-overlapping lock intervals.

The first implementation exposed a nested-worker deadlock: an isolated CP
worker called the newly public isolated binomial helper while its parent still
held the aggregate lock.  This was repaired by giving the CP worker private
in-process CP threshold helpers.  The public CP API still launches exactly one
verified worker; only that worker evaluates the private MPFR DAG.

## Verification

Focused regression set:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider \
  code/test_f1_to_f2_common_observable_selector_v2.py \
  code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py \
  code/test_f1_to_f2_common_observable_selector_v2_round139_independent.py \
  code/test_f1_to_f2_common_observable_selector_v2_round140_repair.py

110 passed
```

Formatting and static checks:

```text
.venv/bin/ruff format --check [source and four tests]
5 files already formatted

.venv/bin/ruff check [source and four tests]
All checks passed

.venv/bin/python -m py_compile code/f1_to_f2_common_observable_selector_v2.py
exit 0
```

Real cache-free synthetic production-size resource gate:

```text
/usr/bin/time -l .venv/bin/python -I \
  code/f1_to_f2_common_observable_selector_v2.py \
  --synthetic-power-resource-gate

status                         PASS_SCIENCE_FREE_POWER_RESOURCE_GATE
N                              8,000,000
assertions                     68
PASS / FAIL                    68 / 0
maximum child peak RSS         53,166,080 bytes
parent maximum RSS             53,215,232 bytes
wall time                      13.10 seconds
positive_budget_evaluated      false
```

The certified CP benchmark remains separately covered by the predecessor and
live regression tests; the repair does not replace it with a normal
approximation.

## Candidate test hashes

```text
test_f1_to_f2_common_observable_selector_v2.py
2c25454206c590aae53ee5c612412d69fc89d5ead0326885db794077d4d31747

test_f1_to_f2_common_observable_selector_v2_round131_independent.py
1a0aea91f6e5f045b2468f811292da5e019ee6f5bc3e762e48103dd769c307f8

test_f1_to_f2_common_observable_selector_v2_round139_independent.py
0aa34606224b909457c43b1b0fddeff7bf5e3cc2041ca49dee7c6f9d6bcf9f26

test_f1_to_f2_common_observable_selector_v2_round140_repair.py
04f3c9e590793610dc1caec79577dd1e4c107bc2a763c323b928e9c0ed74efc7
```

## Disposition

Round 140 is an implementer candidate, not independent acceptance.  Freeze the
candidate hash and attack runtime call ordering, private/public reachability,
canonical response binding, malformed-input totality, the 68-family schedule,
thread and cross-process locking, and the N=8m resource path from a fresh
context.  F1 remains unauthorized even if that attack passes because the F0
strict-type and largest-shape resource gates are still open.

