# Round 145: independent selector-v2 process-lifetime attack

Date: 2026-07-14  
Role: independent certificate, process-lifetime, and resource attacker  
Decision: **HOLD IMPLEMENTATION-STAGE ACCEPTANCE / HOLD F1 / HOLD POSITIVE B**  
Findings: **P0 = 0, P1 = 1, P2 = 2**

## Frozen candidate

```text
code/f1_to_f2_common_observable_selector_v2.py
29fd0a76816dd0da1f613f73d53feaa244d28161e759b3958fc617cbd532b23d
```

The attack used only small synthetic inputs.  It did not run the production
`N=8,000,000` gate, read prospective controls, evaluate positive budget, run
F1/F2/F3, generate a trajectory, or run Monte Carlo.

## Accepted surfaces

- One thousand genuine special-function endpoint probes across the frozen
  precision rungs passed, while the previous unused-low-bit forgery failed.
- Stable descriptor snapshots bound ordinary source/runtime files.
- Two normally running independent parents were serialized to one real worker.
- The capability writer descriptor was closed across fork.
- Generic schedules were labelled `CALLER_SUPPLIED_UNCLASSIFIED`.
- The focused Round-143/144 suite passed 29 tests.

## P1: parent death released the only worker lock

The parent held the `flock`, but the descriptor was close-on-exec and absent
from the worker's inherited descriptor set.  Killing a stopped parent therefore
released the lock while its orphaned worker remained resident.  A second
cooperating parent could then acquire the lock and spawn another worker.

A deterministic `SIGSTOP`/`SIGKILL` probe reproduced two simultaneous resident
workers: one orphan with parent PID 1 and one newly launched child.  The probe
cleaned both workers before exit.

Required closure: the worker must inherit and validate the already-held lock
descriptor and keep it open for its complete lifetime, or an equivalent
parent-death mechanism must terminate the child before the lock can be reused.

## P2 findings

1. Only the capability writer, not the reader, was registered for fork cleanup.
   This was an FD-lifetime leak but did not prevent pipe EOF or bypass the
   public API.
2. `capture_output=True` buffered worker output before the declared response
   size check.  The schema cap was therefore post-hoc rather than a strict
   streaming allocation cap.

## Disposition

Certificate semantics and normal concurrency were accepted for the frozen
candidate, but the one-resident-worker claim was false under parent death.
Round 146 had to repair that P1 before any new resource record could be
attached to the final source.  This round is not F1 authorization.

