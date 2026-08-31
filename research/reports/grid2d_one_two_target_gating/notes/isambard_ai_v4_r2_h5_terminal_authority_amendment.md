# v4-r2 H5 post-release terminal-authority amendment

H5 is an append-only overlay over the frozen H4 payload whose manifest SHA-256
is `441032dda489ce206b3ddec09925b53184e036248e7b393d2120ea1a5dbd47cf`.
No base, H1, H2, H3, or H4 member is modified.

## P0 finding

The H4 release sbatch independently verifies the already-terminal combined
job, then calls the H4 finalizer while the release job itself is still
`RUNNING`.  That finalizer can persist
`authorizes_scientific_release=true` before the release job reaches a terminal
state.  A later release-task, node, epilog, or scheduler failure therefore
cannot revoke the previously written true authority.  H5 removes that timing
class by separating provisional computation from terminal authorization.

## Two-phase authority boundary

The seventh Slurm phase is the H5 release job.  It reopens the frozen H4
payload and all canonical H4 scientific authorities, validates the release
submission and pinned runtime receipt, and reruns the full H4 final
computation.  Its only scientific output is an O_EXCL, content-addressed
provisional candidate.  Both the candidate envelope and its nested full
recomputation set `authorizes_scientific_release=false`.  No H5 release-job
source can write true authority.

The eighth phase, `terminal_audit`, is an independent login-node controller,
not a Slurm job.  Each invocation performs one read-only `sacct` query for the
release parent.  `PENDING`, `RUNNING`, and other nonterminal states produce the
canonical `WAIT_RELEASE_NOT_TERMINAL` result and exit 75 without reading the
candidate or writing a terminal receipt or final authority.  The controller
does not poll or sleep; the external operator may rerun it.

A terminal failure, including `FAILED`, `TIMEOUT`, `NODE_FAIL`,
`OUT_OF_MEMORY`/`OOM`, `CANCELLED`, or any nonzero exit code, fails closed even
when a valid provisional candidate already exists.  Terminal success requires
the single exact release parent row to bind:

- `JobIDRaw` and `JobID` to the submitted release job;
- `JobName`, `Account`, `Partition`, `WorkDir`, and the exact `SubmitLine`;
- `COMPLETED/0:0`, positive `ElapsedRaw`, one node, and the exact CPU, memory,
  node, and billing TRES contract in both `AllocTRES` and `ReqTRES`.

Only after that gate does the controller content-address the canonical terminal
receipt, reopen the provisional candidate, release submission/runtime,
canonical combined JSON/CSV, H4 replay and v3 authorities, and both frozen
payloads.  It reruns the full H4 computation and requires exact canonical JSON
equality with the entire provisional tree.  The controller is the sole H5
source that can then create an O_EXCL final object with
`authorizes_scientific_release=true`.  Its directory contains all five Slurm
job IDs; its filename binds both the release-terminal receipt SHA-256 and the
final object's own SHA-256.  Repeating the same successful audit verifies and
returns the existing object without overwriting it.  Stable per-job-tuple
`flock` files serialize the directory-level uniqueness check and O_EXCL write,
so concurrent divergent controllers cannot create two terminal receipts or
two true authorities under different content hashes.

## Eight-stage DAG and reservation ceiling

The explicit stage order is:

```text
v3_authority -> canary -> production -> reducer -> replay -> combined
             -> release -> terminal_audit
```

The first seven Slurm phases retain the following reservation ceiling:

```text
v3 authority     18.0000 node-hours
canary            0.1667 node-hours
production      960.0000 node-hours
reducer           6.0000 node-hours
replay            24.0000 node-hours
combined           8.0000 node-hours
H5 release         8.0000 node-hours
total           1024.1667 node-hours
```

The eighth login-node terminal audit submits no Slurm job and therefore adds
`0` Slurm node-hours.  A single invocation has a hard 1,800-second walltime
cap and never reserves compute nodes.  The total Slurm reservation ceiling
remains `1024.1667` node-hours.

## Execution policy

`status=REVIEW_HOLD_NO_SUBMISSION`

`authorizes_execution=false`

H5 is frozen locally for review.  Building or verifying its content-addressed
payload does not authorize synchronization, submission, or execution on
Isambard.
