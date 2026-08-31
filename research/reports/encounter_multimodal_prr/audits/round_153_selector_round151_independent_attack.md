# Round 153: selector-v2 Round-151 independent orphan-lock attack

Date: 2026-07-14  
Reviewer: fresh independent concurrency auditor  
Decision: **ACCEPT THE ROUND-151 EXACT BYTES FOR THE DECLARED COOPERATIVE MACOS PROCESS-LIFETIME BOUNDARY / WITHDRAW ROUND-147 P1 / HOLD SECOND-POSIX PORTABILITY AND ALL SCIENCE**  
Findings: **P0 = 0, P1 = 0, P2 = 2**

## 1. Scope and exclusions

This was a read-only audit of the final selector source and the Round-144/145
isolation test after the Round-151 harness repair.  It examined the
`SPAWNED`, capability-pipe `FIONREAD`, `SIGSTOP`,
`waitpid(WUNTRACED | WNOHANG)`, `STOPPED`, parent-death, `flock`, and cleanup
protocols.  The selector and test bytes were not changed.

Only small, science-free process-lifetime fixtures were executed.  This round
did not read a prospective control, evaluate positive budget, run F0, F1, F2,
or F3, execute the 8M synthetic resource gate, or inspect a scientific result.
Acceptance is limited to the source's declared cooperative-public-API threat
model on the tested macOS runtime; hostile same-UID mutation remains outside
that model.

## 2. Exact bytes reviewed and executed

Runtime: repository Python 3.12.13, macOS 26.5.2 build 25F84, arm64.

| object | SHA-256 |
| --- | --- |
| `code/f1_to_f2_common_observable_selector_v2.py` | `b80e720a0a88df053b3e9133582a0a27c31d513b3bb091da006f520a4e3bace6` |
| `code/test_f1_to_f2_common_observable_selector_v2.py` | `ed951bbe0c58084d49067e7941084e1bef9f9e215cb3162e195506aefd6230ba` |
| `code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py` | `e4c88f44f02e92deed9fbe4be742cdf03519d4811196e2413b0f3fd2b42b1345` |
| `code/test_f1_to_f2_common_observable_selector_v2_round139_independent.py` | `76ba6cb1b990fc632528e4cff5a9739242b9de87108d371e09c1ccca026c6b77` |
| `code/test_f1_to_f2_common_observable_selector_v2_round140_repair.py` | `1dfbf2fd7a72caa9afef120b0ef79df9759f5fc2bdd60105ea854cfaf8699f2f` |
| `code/test_f1_to_f2_common_observable_selector_v2_round143_certificate_repair.py` | `c8464e35c98dcfccc5ff726483bede774db58ce7512dc5f442f93031298aacdc` |
| `code/test_f1_to_f2_common_observable_selector_v2_round144_isolation_closure.py` | `0e3817e6bd138cd9caea7ee001f95e59cf506a75677f3abe36a1e346e577322e` |
| `audits/round_151_selector_orphan_test_race_repair.md` | `38173fcf06c2a582067495b9cb17ee943c1725b3bcae627967a25fbc3d6ad689` |

`ruff check --no-cache` passed on the selector and the repaired isolation test.

## 3. Static concurrency result

### 3.1 There is no parent-to-worker lock-ownership gap

The parent obtains `LOCK_EX | LOCK_NB` before creating the worker and passes
that already-locked descriptor in `pass_fds`.  The child therefore owns a
reference to the same open file description from process creation; it does not
need to reach Python code before the lock can survive parent death.  The worker
then independently checks the inherited descriptor's type, owner, link count,
device, and inode against the fixed lock path and reasserts `LOCK_EX` on that
same open file description.

The parent deliberately does not call `LOCK_UN`.  Its `finally` closes only
its reference.  A live worker's reference continues to hold the lock, and the
lock is released when the last reference closes at worker exit.  The
`register_at_fork` cleanup closes both tracked capability-pipe ends and any
tracked lock descriptor in unrelated fork children, preventing such children
from extending the worker lifetime accidentally.

Consequently, the Round-147 inference of a child-reassertion ownership gap is
incorrect for these bytes.  A child that has been created with the lock file
descriptor already retains the lock even before `_validate_inherited_worker_lock`
runs.

### 3.2 The repaired readiness barrier closes the Round-147 false-positive race

The source writes exactly 32 capability bytes before invoking the intercepted
`subprocess.run`, closes the writer, and passes the read descriptor only to the
real worker.  In the test wrapper, no process other than that worker reads the
descriptor.  The worker calls `_validate_inherited_worker_lock` before its
first capability read.  Thus `FIONREAD == 0` establishes all facts relevant to
this lock test: the real selector interpreter reached the worker path,
successfully validated/reasserted the inherited lock, and consumed the
capability bytes.

`FIONREAD == 0` does not claim that the later digest, PPID, and deadline checks
have all completed.  That stronger claim is unnecessary for the orphan-lock
invariant because the lock has already been validated and retained.

After capability consumption, repeated `SIGSTOP` delivery is followed by
`waitpid(pid, WUNTRACED | WNOHANG)`.  `STOPPED` is emitted only if the returned
status is `WIFSTOPPED` with `WSTOPSIG == SIGSTOP`.  The outer test then checks
both `ps` T-state and the exact selector command identity.  This is a genuine
stopped-child handshake, not merely proof that a stop signal was queued.

### 3.3 Failures are not converted to passes

- `SPAWNED <pid>` is emitted immediately after `Popen`, so cleanup knows the
  worker PID even if capability or stop setup fails.
- A worker exit before capability consumption makes `process.poll()` non-null
  and fails.  Unexpected byte counts, readiness timeouts, non-stop wait
  statuses, malformed reports, missing T-state, or command-identity mismatch
  all fail closed.
- The second parent exiting while the orphan should hold the lock fails, as
  does observing any resident worker whose PPID is the second parent.
- `finally` sends `SIGKILL` to a known orphan and kills/waits for both parent
  processes when needed.  Zombies are excluded from the resident-worker count;
  they no longer retain descriptors or execute work.

No swallowed exception or pass-on-timeout path was found.

## 4. Independent executions

### 4.1 Exact repaired pytest node

The exact function
`test_round145_orphan_worker_retains_lock_after_parent_death` was called 25
times in one fresh repository interpreter:

```text
passes       25 / 25
failures      0
real         27.65 s
user          8.81 s
sys          10.39 s
```

### 4.2 Stronger direct lock-state attack

To avoid relying only on process-list sampling, an independent 20-trial probe
used the final `FIONREAD`/`waitpid` readiness sequence, killed the first parent,
and then opened the fixed lock path through a distinct open file description.
It attempted `flock(LOCK_EX | LOCK_NB)` while the reparented worker remained in
T-state, killed the orphan, and retried the same lock operation:

```text
reparented worker remained stopped                    20 / 20
fresh flock blocked while stopped orphan lived       20 / 20
fresh flock acquired after orphan SIGKILL             20 / 20
```

This directly tests the kernel lock state that Round 147 inferred incorrectly.

### 4.3 Full selector regression

The six declared selector test files independently collected 142 tests and
completed with exit code 0:

```text
tests collected     142
tests passed        142
real              39.35 s
user              24.46 s
sys                2.73 s
```

After the direct lock probes, the 25 exact-node repetitions, and the full
suite, exact-command `ps` inspection found zero resident
`--internal-cp-worker` or `--internal-power-worker` processes.  `lsof` found
zero holders of
`/tmp/encounter-selector-v2-special-worker-502/worker.lock`.

## 5. Residual findings

### [P2] The checked-in second-parent observation is sampled, not causal

The repaired readiness sequence for the first worker is causal and closes the
Round-147 race.  The subsequent second-parent assertion, however, observes for
only 0.5 seconds and polls the process table every 10 ms.  It does not receive
an explicit report that the second parent has reached the contested
`flock`, and a sufficiently delayed second-parent import or a very short-lived
overlap could evade that particular assertion.

On this runtime, a separate 12-trial no-contention timing probe reached worker
spawn in 0.08995--0.41541 seconds (median 0.13308 seconds), so all 12 reached
the relevant point within the current window.  More importantly, the
independent fresh-`flock` attack above directly verified the exact bytes and
prevents this test-hardening issue from becoming a P1 for the current macOS
acceptance.  A future test revision should replace the fixed observation
window with an explicit second-parent contention barrier or a direct fresh
nonblocking-lock assertion.

### [P2] A second POSIX implementation has not executed these bytes

The final bytes were not run on Linux or another POSIX kernel.  `SIGSTOP` and
`waitpid(WUNTRACED)` are portable POSIX mechanisms, but `FIONREAD`, `flock`,
and the exact `/bin/ps` status/command interface are platform-sensitive
surfaces.  Cross-kernel empirical acceptance therefore remains open.

## 6. Disposition

```text
Round-151 selector and repaired-test hashes          MATCH
Round-147 pre-stop false-positive race               CLOSED
inherited-open-description lock semantics            SOUND ON REVIEW
exact repaired orphan test                           PASS 25/25
independent fresh-flock orphan attack                PASS 20/20
full selector regression                             PASS 142/142
residual internal workers / lock holders             0 / 0
macOS cooperative process-lifetime boundary          ACCEPT
sampled second-parent checked-in assertion           OPEN P2 HARDENING
second-POSIX replay                                   OPEN P2
F0 / F1 / F2 / F3 / positive-budget science          NOT RUN / NOT AUTHORIZED
```

