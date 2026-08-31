# v4-r2 H6 canonical-candidate-byte amendment

H6 is an append-only terminal-controller overlay over the frozen H5 payload,
whose manifest SHA-256 is
`515fa118d93dcbb7d22844be730e711291a0993560fe5290a82833dd96d84c1d`.
No base, H1, H2, H3, H4, or H5 member is modified.

## Finding

The frozen H5 terminal audit verifies that the sole candidate filename matches
the SHA-256 of its file bytes, parses the JSON strictly, and compares the
parsed candidate and full H4 recomputation with the expected semantic tree.
Those checks do not require the original JSON representation to be the exact
bytes emitted by the frozen H5 producer. An equivalent candidate can therefore
gain a new valid content-addressed filename after an extra newline, whitespace,
key-order, or Unicode-escape representation change.

## H6 byte boundary

H6 retains the frozen H5 provisional producer. After content-addressed
discovery, strict parsing, exact-envelope validation, and full H4 tree
validation, the new login-node terminal controller reconstructs the complete
expected candidate with `provision.candidate_payload(...)`, serializes it with
the producer's `provision.canonical_bytes(...)`, and requires:

```text
candidate_path.read_bytes() == provision.canonical_bytes(expected_candidate)
```

It also requires the discovered filename digest to equal the SHA-256 of those
expected canonical bytes. Representation-only changes fail closed even when
the modified file is renamed to its newly computed SHA-256.

## Preserved terminal-authority boundary

H6 reuses the frozen H5 terminal-state, exact TRES, and immutable terminal
receipt gates. It performs one `sacct` query, returns retry-safe WAIT/exit 75
for nonterminal states, never polls or sleeps, and adds zero Slurm node-hours.
Terminal failures are rejected before candidate discovery. Only after exact
`COMPLETED/0:0` does it create or verify the unique content-addressed terminal
receipt under the per-job `flock`, rerun the full H4 computation, apply the H6
raw-byte gate, and use a separate H6 per-job `flock` plus locked uniqueness
recheck and O_EXCL write for final authority.

## Execution policy

`status=REVIEW_HOLD_NO_SUBMISSION`

`authorizes_execution=false`

H6 is local review evidence only. It does not authorize synchronization,
submission, or execution on Isambard.
