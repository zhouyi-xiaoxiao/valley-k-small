# Grid2D GPU v3 secondary R4 independent source audit

Date: 2026-07-27 (Asia/Shanghai)

Auditor role: independent non-author review

Audited root (strictly read-only):

`/Users/ae23069/.codex/isambard_artifacts/grid2d_gpu_v3_secondary_r4`

Author seal:

`/Users/ae23069/.codex/isambard_artifacts/grid2d_gpu_v3_secondary_r4_author_seal/GRID2D_GPU_V3_SECONDARY_R4_AUTHOR_SEAL_20260727.md`

## Decision

**HOLD — do not sync, submit, publish, or use R4 to unlock the full-node H13
campaign.**

R4 correctly repairs the producer-expression arithmetic on the analyzer path,
closes the payload inventory, isolates the batch runtime, retains file
descriptors during each verifier invocation, and uses
`renameat2(RENAME_NOREPLACE)`. It nevertheless does not close the requested
publication transaction. Three deterministic killing fixtures expose two
independent paths by which an apparent five-file final result can be produced
without being the analyzed scientific result.

No staging, preflight, or submit contract is authorized while this HOLD
remains.

## Frozen anchors and inventory

- R4 payload-manifest SHA-256:
  `e02ac46aa968ff725f83b08a759b81cfea37197dca710c42544f78ecac0387af`
- R4 contract SHA-256:
  `c90ebc92958c1ddb82aa0f54919a32f8e0c3ca64c7ea90dbf7c97dc20da232b4`
- frozen R1 analyzer SHA-256:
  `c2a9a05c04376f5040bdea46cb8674184deeb536197bd884188059f576dc8501`
- author-seal SHA-256:
  `b4b7853d35fb15f2483e025f9583bb732f5135b885573077c68be94ac2b354fd`
- frozen R3 independent-audit SHA-256:
  `329fee6703080d8eff69fdc015eb3b0f21f2026378b1612a658106cc6efeb453`
- SHA-256 of the sorted eleven-file `shasum` ledger:
  `263310350b9c916a48dc8bcb6e1465d4bf6c18d40b637d4763a48afa17694344`

The package contains exactly the ten ordered manifest members plus the
manifest itself. Every member is a regular single-link file. There is no
symlink, hardlink, unexpected source, bytecode file, or unlisted member.
The observed payload, contract, and frozen-R1 hashes equal the author-seal
anchors. R3's supplied frozen anchors remain unchanged.

The locally fetched v3 result hashes also match the R4 contract:

- reduction JSON:
  `9576b601e52eeb9d6eae6c99cbb52d241050c9bc0714628d5f3e267ceed99984`
- reduction CSV:
  `698cc32633d7e24f47eb09555d1c3e0fc3b259b1faa13ce69c8d59d14f9f30eb`
- sacct receipt:
  `e2723dea5263c912830189abb056ecd2e722db74f678ebb8eb996e118859360c`

The cell-0 fixture independently gives:

- exact counts: `999787`, `258731`, `1000000`
- producer expression:
  `0x1.7b6bb1290257cp-1`
- single-division expression:
  `0x1.7b6bb1290257dp-1`
- distance: exactly one binary64 ULP
- JSON value: bit-identical to the producer expression

## Evidence that passed

1. All 15 packaged author tests pass under isolated Python startup:
   `Ran 15 tests ... OK`.
2. The six R4 killing tests separately pass: wide-ULP rejection, runtime extra
   rejection, retained staging-dirfd parent-swap containment, retained file-FD
   name-replacement detection, no-replace final collision, and static
   clean/absolute/isolated batch assertions.
3. The 388,493-ULP R3 fixture is rejected. The analyzer recomputes
   `(one_hits / walkers) - (two_target1_hits / walkers)` from the same captured
   JSON/NPZ counts and admits only a producer/single-division distance in
   `{0, 1}`.
4. The payload loader performs descriptor-relative `O_NOFOLLOW` traversal,
   hashes and executes frozen R1 from manifest-verified bytes, rejects a
   runtime extra member, and applies an exact one-ULP adapter only after the
   producer pair is validated.
5. The batch uses `/bin/bash`, `--export=NIL`, absolute tools,
   Apptainer `--cleanenv`, and `/usr/bin/python3 -I -B`. The analyzer,
   verifier, test, and preflight programs are compiled from launcher-captured
   payload bytes rather than invoked by their package path.
6. Within one verifier invocation, four data FDs remain open, the receipt is
   written and read through one FD, file-name probes are rebound to the
   retained file inodes, and final-name collisions fail through
   `RENAME_NOREPLACE`.
7. `bash -n` accepts the packaged sbatch script.

## P0 findings

### P0-1 — final readback can authorize fabricated scientific content

`verify_gpu_gating_v3_secondary_r4.py` does not independently recompute the
ledger floats from its recorded integer counts. It requires
`numerator == one_hits - two_hits` and checks only that the two supplied float
fields have their supplied ULP distance. It never requires:

```text
producer == (one_hits / walkers) - (two_hits / walkers)
single_division == (one_hits - two_hits) / walkers
```

It also accepts arbitrary syntactically valid raw hashes, validates the core
CSV only by physical row count, and accepts a minimal core JSON without the
75 frozen contrasts, input receipts, method block, bootstrap result, or
pinned upstream inventory. Self-asserted booleans and self-consistent hashes
inside a newly constructed authorization JSON are sufficient.

A deterministic killing fixture used all 5,760 ledger rows with counts
`one_hits=1`, `two_target1_hits=0`, and `walkers=1`, but recorded both
producer and single-division as `0x0.0p+0`. The true value is
`0x1.0000000000000p+0`. The fixture supplied arbitrary raw hashes and a
one-column 75-row CSV. R4 accepted and published it:

`KILLING_FIXTURE_ACCEPTED PASS_R4_NOREPLACE_PUBLICATION_COMMIT`

This is not a cosmetic readback omission. The receipt says
`published_result_authorized: true`, so the final authority boundary can be
crossed without the v3 reduction, raw-cell replay, or max-|t| result.

Required repair: make the final verifier reconstruct every ledger float from
counts bit-for-bit, bind every ledger raw hash and cell id to the frozen
upstream inventory, validate the exact core schema and all 75 rows, recompute
or independently bind the bootstrap/statistical result to pinned inputs, and
reject any authorization/core field or member outside the exact schema.

### P0-2 — analyzer-to-verifier staging identity is reopened by name

The analyzer opens and retains a staging directory FD while writing its four
members, but closes that FD before returning. The batch then launches the
verifier as a separate process. The verifier opens
`args.staging_name` from the output parent by name. No inode identity produced
by the analyzer crosses this process boundary.

Therefore the whole analyzed staging directory can be renamed away and
replaced after the analyzer exits but before the verifier opens it. P0-1
provides a concrete replacement directory that the final verifier accepts.
The bundled parent-swap test is narrower: it proves that a directory already
opened by one process remains contained, but it does not cover the gap between
the two `secure_python` invocations in the sbatch script.

Required repair: make analysis, receipt construction, and publication one
process/descriptor transaction, or transfer an authenticated retained
descriptor plus analyzer-produced inode/byte commitments across the process
boundary without reopening the staging directory by name. Add a killing test
that swaps the complete staging directory after analysis and before
verification.

### P0-3 — a source-name swap at rename leaves an invalid visible final directory

Immediately before publication, `_bind_names()` verifies the five entries
inside the retained staging directory FD. `renameat2`, however, acts on the
source *name* in the parent FD. R4 does not prove at the rename call that this
source name still identifies the retained staging directory inode.

A deterministic hook renamed the retained staging directory aside immediately
before `_rename_noreplace`, installed a different five-file directory at the
staging name, retained an apparent R4 authorization and receipt, and corrupted
the core CSV. `renameat2(RENAME_NOREPLACE)` atomically moved the replacement
directory to the final name. The post-rename inode check detected the attack
and raised:

`VerificationError: published directory inode drift`

but the invalid final directory remained visible with exactly five apparent
publication members, including `secondary_max_t_r4.json` and
`verification_receipt_r4.json`:

`INVALID_FINAL_LEFT_VISIBLE True ... b'CORRUPTED\n'`

Thus the post-rename check diagnoses the failure only after the claimed
no-invalid-final boundary has already been crossed. There is no quarantine or
fail-closed recovery.

Required repair: bind the source directory entry to the retained inode as part
of the publication primitive or redesign publication so an unverified source
name can never become the final name. A failed post-rename inode check must
not leave a final directory carrying apparent authorization. Add this exact
source-name replacement fixture and verify zero visible final authority at
every crash/failure point.

## P1 findings

### P1-1 — the claimed bit-exact JSON/producer equality uses numeric equality

The analyzer compares:

`reported == producer`

rather than comparing binary64 bits or `float.hex()`. A coherent targeted
fixture with zero hit difference and JSON `gating_probability_drop=-0.0`
was accepted against a recomputed producer of `+0.0`:

`SIGNED_ZERO_ACCEPTED -0x0.0p+0 0x0.0p+0`

The pinned real data are non-negative and the observed cell-0 value is
correct, so this does not alter the current cell-0 result. It does contradict
the contract and authorization statement that the JSON value is bit-exact.

Required repair: compare the JSON and producer binary64 encodings, and add
signed-zero plus non-finite killing fixtures.

### P1-2 — the SIF digest is checked before later path-based execution

The batch hashes the container path once, then each `secure_python` call gives
Apptainer the path again. The preflight and batch do not retain and bind the
same SIF file descriptor/identity through all executions. The preflight's
container hash also lacks before/after identity stability and immutable
owner/mode checks.

Required repair: prove the public SIF is immutable and stable for the whole
job, or execute a private immutable snapshot whose bytes/identity are bound to
the recorded digest. Add a container-name replacement killing test or an
equivalent immutable-mount proof.

## Operational gate

The author seal explicitly says that live SSH timed out and does not claim a
live remote preflight. This independent audit was forbidden to sync or submit,
so no remote write or submission was attempted. Even if
`PASS_R4_READ_ONLY_OPERATIONAL_PREFLIGHT` is later obtained, it cannot override
the source-level P0 findings above.

## Required R5 exit gates

R5 must be a new append-only sibling and must not modify R3 or R4. Before
another independent review it must:

1. reject the fabricated counts/float/raw-hash/core fixture from P0-1;
2. make the final verifier independently bind all 5,760 cells, all 75
   contrasts, frozen input receipts, and max-|t| results;
3. eliminate the analyzer/verifier complete-directory swap window;
4. eliminate the rename source-name swap or guarantee that no failed
   publication leaves a visible final authorization/receipt pair;
5. compare JSON/producer binary64 encodings, including signed zero;
6. bind the SIF identity used by every Python execution to the frozen digest;
7. pass the original 15 tests plus the four new killing fixtures above;
8. receive a new author seal and a distinct non-author GO;
9. only then stage a new remote root and run a read-only live operational
   preflight before submission.

Until those gates pass, R4 and all dependent H13/full-node execution remain
blocked.
