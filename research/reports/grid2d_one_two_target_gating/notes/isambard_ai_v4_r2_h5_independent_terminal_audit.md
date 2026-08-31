# Independent H5 post-release terminal audit — 2026-07-27

## Scope and disposition

This audit covers only the append-only H5 files in the local dirty/untracked
working tree.  No remote synchronization or Slurm submission was performed.

`status=REVIEW_HOLD_NO_SUBMISSION`

`authorizes_execution=false`

## H4 timing defect reproduced

The frozen H4 release sbatch queries `sacct` only for the upstream combined
job.  While the H4 release job itself is still running, it calls the H4
finalizer, which can write a persistent true scientific-release receipt.  The
receipt remains true if the release job subsequently terminates unsuccessfully.
This is a terminal-ordering defect rather than a defect in H4's scientific
recomputation.

## H5 repair evidence

- The H5 release job invokes only the provisional producer.  The producer
  contains no true scientific-release value and emits a content-addressed,
  O_EXCL candidate whose outer and nested authority booleans are false.
- The independent terminal controller performs one login-node `sacct` query,
  accepts only one exact release-parent row at `COMPLETED/0:0`, and closes job
  identity, job name, account, partition, work directory, exact submit line,
  elapsed time, node count, and the complete expected TRES key/value contract.
- Nonterminal states return retry-safe WAIT/exit 75 without polling, sleeping,
  reading the candidate, or writing authority.  Every terminal failure is
  rejected before candidate discovery.
- After terminal success, the controller reopens the exact release submission
  and runtime receipt, canonical combined artifacts, v3/replay authorities and
  submission receipts, H4 runtime bindings, and the frozen H4/H5 manifests.
- The full H4 primary, surface, heterogeneity, authorization, combined-CSV,
  and combined-terminal computations are rerun.  The entire provisional tree
  must be byte-identical under canonical JSON serialization; a modified
  candidate remains inadmissible even after an attacker updates its filename
  SHA-256.
- The terminal receipt and final authority are independently
  content-addressed.  The final path binds all five job IDs, the terminal
  receipt hash, and the final object hash.  Stable per-job-tuple `flock`, a
  locked uniqueness recheck, and O_EXCL prevent both overwrite and concurrent
  divergent-hash authority creation; an exact repeated audit is read-only and
  idempotent.
- The submit entry exposes exactly eight stages.  `terminal_audit` launches the
  local controller directly, never calls `sbatch`, and consumes zero Slurm
  node-hours.

## Local verification

The frozen base/H1/H2/H3/H4 suites were rerun together with H5 under Python
3.12, NumPy 2.0.2, and SciPy 1.14.1:

```text
base  14/14 PASS
H1    20/20 PASS
H2    13/13 PASS
H3    10/10 PASS
H4    24/24 PASS
H5    27/27 PASS
total 108/108 PASS
```

H5 killing tests cover `PENDING`, `RUNNING`, `FAILED`, `TIMEOUT`,
`NODE_FAIL`, `OUT_OF_MEMORY`/`OOM`, `CANCELLED`, and nonzero completion; a
candidate that exists before terminal failure; duplicate or forged `sacct`
rows; wrong job, script/job name, account, partition, work directory, submit
line, TRES, elapsed time, and node count; a modified-and-rehashed candidate;
O_EXCL/idempotent terminal and final writes; concurrent divergent final writes
with exactly one accepted authority; exact eight-stage DAG structure; and the
zero-node-hour, no-poll login controller boundary.

All H5 Python files pass `py_compile`; the H5 release sbatch passes `bash -n`.
The H4 builder verifies all 97 frozen H4 members and preserves the frozen H4
payload-manifest SHA-256
`441032dda489ce206b3ddec09925b53184e036248e7b393d2120ea1a5dbd47cf`.

The H5 payload manifest content-addresses the complete frozen H4 payload, the
H4 manifest itself, both H5 notes, and every H5 code, sbatch, builder, and test
file.  Because this report is a manifest member, its text intentionally does
not contain the resulting H5 manifest SHA-256, which would be circular.

The first seven Slurm phases have a total reservation ceiling of `1024.1667`
node-hours.  The eighth login-node terminal audit adds `0` Slurm node-hours and
has a 1,800-second per-invocation walltime cap.
