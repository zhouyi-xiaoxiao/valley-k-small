# Independent H6 canonical-candidate-byte audit — 2026-07-27

## Scope and disposition

This audit covers only new append-only H6 files in the local dirty/untracked
working tree. No frozen base/H1/H2/H3/H4/H5 member was changed. No remote
synchronization or Slurm submission was performed.

`status=REVIEW_HOLD_NO_SUBMISSION`

`authorizes_execution=false`

## Regression evidence

The H6 killing suite writes real candidate files into isolated provisional
directories, names each file with the SHA-256 of its actual bytes, discovers it
through `discover_candidate`, and then validates it through
`validate_candidate`. Exact producer-canonical bytes pass. Each of the
following semantically equivalent representations is rehashed to a matching
filename and rejected by the H6 raw-byte gate:

- one additional trailing newline;
- insignificant JSON whitespace;
- a different object-key order;
- literal UTF-8 in place of the producer's canonical Unicode escape.

A separate regression changes semantic content and confirms that full-tree
validation fails before the raw-byte gate. The suite also checks reuse of the
H5 exact terminal/TRES and unique terminal-receipt gates, rejection before
candidate discovery on terminal failure, one-query/no-poll/WAIT75/zero-node-
hour controller structure, full H4 recomputation reopening, and concurrent
H6 final writes under per-job flock, locked recheck, and O_EXCL.

## Local verification contract

The frozen base, H1, H2, H3, H4, and H5 suites and the new H6 suite must all
pass after the H6 manifest is frozen. Every Python member must pass
`py_compile`; every shell member must pass `bash -n`; the frozen H4 and H5
manifest builders and the new H6 builder must verify their exact members.

The H6 payload manifest covers every frozen H5 member, the frozen H5 manifest,
both H6 notes, the H6 controller, the H6 payload builder, and the H6 killing
tests. Because this report is a manifest member, its text intentionally omits
the resulting H6 manifest SHA-256 to avoid a circular digest.
