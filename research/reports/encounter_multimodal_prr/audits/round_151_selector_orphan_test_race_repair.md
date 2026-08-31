# Round 151: selector-v2 orphan-test race repair and exact-byte replay

Date: 2026-07-14  
Implementer/reviewer: concurrency repair and independent replay agent  
Decision: **ACCEPT ROUND-146 ORPHAN-LOCK BEHAVIOUR ON THE TESTED MACOS RUNTIME / WITHDRAW ROUND-147 P1 AS A HARNESS FALSE POSITIVE / HOLD F0 AND F1 SCIENCE**  
Findings: **P0 = 0, P1 = 0, P2 = 1**

## 1. Scope and science boundary

This round diagnosed the intermittent Round-147 parent-death result, repaired
only the parent-death test protocol, and replayed the synthetic selector
certificate/resource surface.  It did not read a prospective control, evaluate
positive budget, run F0/F1/F2/F3 science, generate trajectories, or change any
manuscript, README, frozen claim hash, or selector implementation byte.

The acceptance below is therefore limited to the current selector process
lifetime behaviour on macOS 26.5.2 arm64.  It is not a scientific acceptance
and is not a cross-platform POSIX certificate.

## 2. Root cause: the test reported a PID before it had a stopped orphan

The Round-147 test wrapper performed this sequence:

```text
Popen(actual selector worker)
kill(worker_pid, SIGSTOP)
print(worker_pid)                 # outer test treated this as ready
communicate(input=request)
```

`kill(..., SIGSTOP)` only queues/delivers a signal; it is not a stopped-state
handshake.  The outer test killed the first parent as soon as it read the PID,
without checking that the worker was still resident and in `T` state.  On the
failing schedules, the supposed orphan was already absent.  A second parent
then correctly acquired the released lock, but the test labelled its worker an
overlap.

A 30-run pre-repair diagnostic separated the two states explicitly.  It
inspected `ps`, `lsof`, and a fresh nonblocking `flock` attempt after killing
the parent:

```text
confirmed T-state worker                  27 / 30
T-state worker retained worker.lock       27 / 27
fresh flock while T-state orphan lived    blocked 27 / 27

worker never observed stopped              3 / 30
worker.lock fd present in those cases       0 / 3
fresh flock in those cases                 acquired 3 / 3

true second-worker overlap with resident orphan   0
```

This falsifies Round 147's inferred parent-to-worker ownership gap.  The
selector source already uses one inherited open file description, and the
resident child kept that description and its lock after parent death in every
confirmed-orphan observation.

A first development attempt that waited for one `SIGSTOP` produced 19 passes
and one ready timeout in 20 invocations.  Further inspection showed that on
macOS the signal could be sent at the `posix_spawn`/exec boundary: a signal-only
barrier was still not a reliable proof that the real selector worker had begun
its authorization path.  This was a harness ready failure, not an invariant
failure, and it left zero internal workers.

## 3. Minimal repair

The selector source was deliberately left unchanged.  Only
`test_f1_to_f2_common_observable_selector_v2_round144_isolation_closure.py`
was repaired.

The final wrapper now uses two explicit reports and a real worker-side progress
barrier:

1. immediately after `Popen`, report `SPAWNED <pid>` so the outer `finally`
   block always knows which child to kill, even if later setup fails;
2. observe the inherited capability pipe with `FIONREAD`; the parent wrote
   exactly 32 bytes before spawn, and the count reaches zero only after the
   actual selector interpreter has executed the worker path, validated the
   inherited lock, and consumed the capability;
3. deliver `SIGSTOP` and require `waitpid(pid, WUNTRACED | WNOHANG)` to report
   `WIFSTOPPED` with `SIGSTOP`, retrying only until a two-second deadline;
4. only then report `STOPPED <pid>`; and
5. independently confirm `T` state and resident command identity before
   killing the first parent and launching the second.

The two-phase report also closes a cleanup defect in discarded intermediate
harnesses: a failure after spawn but before stop confirmation can no longer
hide the child PID from `finally`.

## 4. Exact bytes tested

Runtime: repository Python 3.12.13, macOS 26.5.2 build 25F84, arm64, 24 GiB
physical memory.

| object | SHA-256 |
| --- | --- |
| `code/f1_to_f2_common_observable_selector_v2.py` | `b80e720a0a88df053b3e9133582a0a27c31d513b3bb091da006f520a4e3bace6` |
| `code/test_f1_to_f2_common_observable_selector_v2.py` | `ed951bbe0c58084d49067e7941084e1bef9f9e215cb3162e195506aefd6230ba` |
| `code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py` | `e4c88f44f02e92deed9fbe4be742cdf03519d4811196e2413b0f3fd2b42b1345` |
| `code/test_f1_to_f2_common_observable_selector_v2_round139_independent.py` | `76ba6cb1b990fc632528e4cff5a9739242b9de87108d371e09c1ccca026c6b77` |
| `code/test_f1_to_f2_common_observable_selector_v2_round140_repair.py` | `1dfbf2fd7a72caa9afef120b0ef79df9759f5fc2bdd60105ea854cfaf8699f2f` |
| `code/test_f1_to_f2_common_observable_selector_v2_round143_certificate_repair.py` | `c8464e35c98dcfccc5ff726483bede774db58ce7512dc5f442f93031298aacdc` |
| `code/test_f1_to_f2_common_observable_selector_v2_round144_isolation_closure.py` | `0e3817e6bd138cd9caea7ee001f95e59cf506a75677f3abe36a1e346e577322e` |

The selector source hash is identical to Round 147.  The only changed code
surface is the parent-death test file.

## 5. Targeted repeated replays

The final test bytes were first replayed 100 times in one interpreter to
stress the parent/worker schedule without pytest startup noise:

```text
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
import sys
from pathlib import Path
here = Path('research/reports/encounter_multimodal_prr/code').resolve()
sys.path.insert(0, str(here))
import test_f1_to_f2_common_observable_selector_v2_round144_isolation_closure as t
for index in range(1, 101):
    t.test_round145_orphan_worker_retains_lock_after_parent_death()
    print('PASS', index, flush=True)
PY
```

Observed result: **100 passes, 0 failures, 0 ready timeouts, 0 invariant
failures**.  The final process inspection found no internal selector worker.

The same node was then replayed in 20 fresh pytest processes.  The harness
captured each return code, classified the two relevant failure strings, and
ran `ps` after every invocation:

```text
env PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p .venv/bin/python - <<'PY'
import os, subprocess, sys
from pathlib import Path
root = Path.cwd()
node = ('research/reports/encounter_multimodal_prr/code/'
        'test_f1_to_f2_common_observable_selector_v2_round144_isolation_closure.py::'
        'test_round145_orphan_worker_retains_lock_after_parent_death')
source = str((root / 'research/reports/encounter_multimodal_prr/code/'
              'f1_to_f2_common_observable_selector_v2.py').resolve())
passed = ready_timeouts = invariant_failures = residual_runs = 0
for index in range(1, 21):
    completed = subprocess.run(
        [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', node],
        cwd=root,
        env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
        capture_output=True,
        text=True,
    )
    output = completed.stdout + completed.stderr
    passed += completed.returncode == 0
    ready_timeouts += ('did not report its spawned worker' in output or
                       'did not confirm its stopped worker' in output)
    invariant_failures += 'second parent spawned a worker' in output
    listing = subprocess.check_output(
        ['/bin/ps', '-axo', 'pid=,ppid=,stat=,command='], text=True
    )
    resident = [line for line in listing.splitlines()
                if source in line and '--internal-' in line and 'worker' in line]
    residual_runs += bool(resident)
print(passed, ready_timeouts, invariant_failures, residual_runs)
raise SystemExit(0 if (passed, ready_timeouts, invariant_failures, residual_runs)
                 == (20, 0, 0, 0) else 1)
PY
```

Observed result:

```text
passes                         20 / 20
ready timeouts                  0
resident-orphan invariant failures  0
runs with residual workers      0
real                           61.43 s
user                           10.64 s
sys                             9.87 s
```

Thus the final acceptance surface contains 120 targeted parent-death replays,
all passing.  Discarded development harnesses and the pre-repair diagnostic
are reported above but are not counted as final-byte acceptance tests.

## 6. Full 142-test replay

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

Collection counts were `67 + 17 + 15 + 11 + 17 + 15 = 142`.  Observed result:

```text
142 / 142 passed, exit 0
real 33.64 s
user 24.63 s
sys   2.76 s
```

## 7. Synthetic 8M resource replay

```text
set -o pipefail
/usr/bin/time -l .venv/bin/python -I \
  research/reports/encounter_multimodal_prr/code/f1_to_f2_common_observable_selector_v2.py \
  --synthetic-power-resource-gate | \
  .venv/bin/python -c 'import json,sys; d=json.load(sys.stdin); print(d)'
```

Observed canonical/resource summary:

```text
status                      PASS_SYNTHETIC_SCIENCE_FREE_POWER_RESOURCE_GATE
selector source SHA-256     b80e720a0a88df053b3e9133582a0a27c31d513b3bb091da006f520a4e3bace6
schedule SHA-256            928bef0c45ec7874c83547aaa5021ddf94513739698f41f960da96d308abd42f
N                           8,000,000 (default synthetic fixture)
assertions                  68
PASS / FAIL                 68 / 0
maximum child peak RSS      55,459,840 bytes
process maximum RSS         55,525,376 bytes
wall time                   19.23 seconds
swaps                       0
schedule kind               SYNTHETIC_RESOURCE_FIXTURE
positive_budget_evaluated   false
```

After all targeted, suite, and 8M commands, `ps` found zero live
`--internal-cp-worker`/`--internal-power-worker` processes, and `lsof` found no
holder of `/tmp/encounter-selector-v2-special-worker-502/worker.lock`.

## 8. Residual risk and final boundary

### [P2] Second-POSIX replay remains open

This round explains and closes the macOS false positive with a real
capability-consumption/stopped-state barrier.  It did not run the final bytes
on Linux or another POSIX kernel.  The repaired test uses standard POSIX stop
and wait semantics plus `FIONREAD`, but portability remains an empirical open
item.  This does not reopen the disproved macOS ownership gap; it limits the
scope of the acceptance.

```text
Round-147 claimed implementation defect       WITHDRAWN (test false positive)
selector implementation bytes                 UNCHANGED
confirmed resident orphan retained lock       PASS 27/27 pre-repair diagnostic
final targeted parent-death replays            PASS 120/120
final ready timeouts                           0
final resident-orphan invariant failures       0
final residual internal workers / lock holders 0 / 0
full selector suite                            PASS 142/142
8M synthetic resource fixture                  PASS 68/68, 0 swaps
tested-macOS process-lifetime closure           ACCEPT
second-POSIX portability replay                OPEN P2
F0 / F1 / positive-budget science              NOT AUTHORIZED / NOT RUN
```

