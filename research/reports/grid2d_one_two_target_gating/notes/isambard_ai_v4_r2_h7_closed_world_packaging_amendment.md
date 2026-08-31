# v4-r2 H7 closed-world packaging amendment

H7 is an append-only packaging overlay over the frozen H6 payload.  The H6
payload manifest SHA-256 remains
`79a61ac2d24e2ff62e50cbf18fd191007eb535652bcb859dc173ebe0376a7d3b`;
no H6 member bytes are changed.

## Finding

An exact H6-manifest deployment passed all member hashes, all seven payload
builders, all shell syntax checks, and 118 of the 119 base-through-H6 tests on
Isambard-AI.  The remaining base test reads
`artifacts/data/disorder_field_pack_v3.npz`, but that immutable test fixture
was not a member of the H6 payload.  Its frozen SHA-256 is
`d7039cf68cd137729a3931f1265cad2735c67da3c436fc4f71d214f059f0e420`.

## H7 repair

The H7 manifest includes every H6 member, the frozen H6 manifest itself, the
missing v3 field pack, and the new H7 amendment, builder, and killing tests.
The manifest is an exact ordered inventory.  A deployed H7 root is valid only
when its complete regular-file inventory is exactly the H7 members plus the
externally anchored H7 manifest: no extra file or directory, missing file,
symlink, special file, hardlink, byte drift, or non-0600 file mode is
accepted.  The root and all exact parent directories must be real mode-0700
directories.

The H7 manifest digest is intentionally supplied to the closed-world verifier
as an external argument.  It is not embedded in a manifest member, avoiding a
circular self-hash.  Local source checkout permissions are not an execution
authority; the deployment gate normalizes and then verifies every remote file
as mode 0600 without changing its bytes.

## Execution policy

`status=H7_PACKAGING_REPAIR_CANDIDATE_NO_SUBMISSION`

`authorizes_execution=false`

H7 authorizes no Slurm submission by itself.  Submission remains gated on an
independent review, an exact fresh-root closed-world verification, all 119
base-through-H6 tests, the H7 killing suite, and terminal upstream v3 reducer
and secondary evidence.
