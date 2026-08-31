# Round 144: selector-v2 normal-path isolation closure

Date: 2026-07-14  
Role: implementer / science-free process-isolation repair  
Decision: **NORMAL-PATH CANDIDATE PASS / HOLD INDEPENDENT ATTACK / NO F1**

## Implemented boundary

- A parent holds the fixed user-owned `flock` before launching a numerical
  worker and for the complete normal worker lifetime.
- The capability writer descriptor is registered for fork cleanup during its
  short live interval, and per-PID caches reset after fork.
- A fixed user-owned lock path, deadline, exact worker command, hidden CLI
  capability, runtime verification, and canonical request/response binding
  constrain the cooperative public API.
- Two independent normal parents are tested by counting real resident worker
  processes; the observed maximum is one.
- The module states its threat model explicitly: cooperative use through the
  public API and resource isolation are covered; hostile same-UID importers
  reaching Python private objects are not treated as capability-safe.

## Known boundary before attack

This round did not yet prove that the one-worker invariant survives abrupt
parent death.  It also retained two lower-priority limitations: the capability
reader descriptor was not yet in fork cleanup, and subprocess output limits
were checked after `capture_output` buffering rather than enforced by a
streaming reader.

Round 145 therefore remained mandatory.  No result of the normal-path tests
was allowed to authorize F1.

## Science boundary

Only small synthetic fixtures were used.  No positive-budget value,
prospective control, F0/F1/F2/F3 result, semigroup, trajectory, or Monte Carlo
sample was read or evaluated.

