# Grid2D GPU v3 secondary R3 independent source audit

Date: 2026-07-27 (Asia/Shanghai)

Auditor role: independent non-author review

Audited root (strictly read-only):

`/Users/ae23069/.codex/isambard_artifacts/grid2d_gpu_v3_secondary_r3`

## Decision

**HOLD — do not sync, submit, publish, or treat R3 output as authority.**

R3 materially repairs the missing frozen-R1 member and binds scientific input
hashing, parsing, frozen-R1 replay, and inference to immutable bytes read from
`O_NOFOLLOW` descriptors. Its existing nine author tests pass. It nevertheless
fails the requested fail-closed boundary under deterministic killing fixtures:
the frozen-R1 float shim is not restricted to the intended 0/1-ULP domain,
publication paths are re-used by name after validation, the batch runtime
inherits executable Python/Bash/path state, and readback plus directory
publication are not one no-replace descriptor-anchored transaction.

No exact staging/submit/readback recipe is authorized while this HOLD remains.

## Frozen anchors and inventory

- External payload-manifest SHA-256:
  `710a4ed1180beb3211f43a804f29837459d52ccb3c012ba5ac6b04e04ae77e87`
- Contract SHA-256:
  `fb5840d5c9e6c82d387ea8c9bf575800308215a872fe8993773e541d39e3183c`
- Frozen R1 analyzer SHA-256:
  `c2a9a05c04376f5040bdea46cb8674184deeb536197bd884188059f576dc8501`

All three observed hashes exactly match the independently supplied anchors.
The audited root contained exactly ten regular single-link files: the nine
ordered manifest members plus the externally anchored manifest itself. It
contained no symlink or hardlinked file. The source root was not modified by
the audit.

## Evidence that passed

1. The nine bundled author tests passed in an isolated temporary clone:
   `Ran 9 tests ... OK`.
2. Missing payload members, symlink inputs, and hardlink inputs fail closed.
3. The cell-0 restore race cannot change the already captured snapshot metric.
   Frozen R1 is compiled from the captured R1 bytes; its JSON/NPZ replay consumes
   `SnapshotPath` bytes, and a NumPy path reopen is rejected.
4. JSON/NPZ hit-count mismatch is rejected exactly.
5. Raw cell directories enforce exact JSON/NPZ pairs and exact cell-directory
   inventory.
6. Independent validation of the locally fetched pinned reduction passed:
   2,880 block values, 5,760 inventory cells, 480 task rows, 480 unique
   allocations, all `COMPLETED|0:0`, and inventory digest
   `cfeb3466f8760dcfec2f8edc9babfcf249cc8b054a307059417a1261c2579646`.
7. The pinned fetched inputs match the contract:
   - reduction JSON:
     `9576b601e52eeb9d6eae6c99cbb52d241050c9bc0714628d5f3e267ceed99984`
   - reduction CSV:
     `698cc32633d7e24f47eb09555d1c3e0fc3b259b1faa13ce69c8d59d14f9f30eb`
   - sacct receipt:
     `e2723dea5263c912830189abb056ecd2e722db74f678ebb8eb996e118859360c`
8. A valid output fixture is accepted only with exactly five files, directory
   mode `0700`, and file mode `0600`. Extra directories, wrong file modes, and
   core-only partial output are rejected. The core pair is explicitly marked
   non-authoritative.
9. `bash -n` accepts the R3 batch script.

## P0 findings

### P0-1 — the targeted float shim accepts far more than 1 ULP

`_ValidatedProducerFloat.__eq__` compares the frozen-R1 single-division value
to an attached expected value but never constrains the distance between the
reported producer expression and the single-division expression.

A coherent killing fixture used exact counts
`one_hits=999999`, `two_target1_hits=999998`, and `walkers=1000000`, with
matching JSON probabilities, matching JSON/NPZ counts, consistent histograms,
paired outcomes, checkpoints, hashes, provenance, and all other frozen-R1
gates. R3 accepted it:

- producer expression: `0x1.0c6f7a0b00000p-20`
- single division: `0x1.0c6f7a0b5ed8dp-20`
- accepted distance: **388,493 ULP**

The shim runs for every cell. R3 has no pre-authorization condition that each
cell's distance belongs to the intended narrow set `{0, 1}`. Recording the
distance in a ledger is not a fail-closed bound.

Required repair: recompute the producer expression from the same captured
integer counts and require JSON bit equality; keep single division as ledger
evidence only; require a frozen allowed ULP set or upper bound of 1; apply any
frozen-R1 equality adapter only to the exact validated pair.

### P0-2 — fixed-root output validation is not bound to later writes

`_validate_output_directory` validates a path and resolves its parent, then
returns a `Path`. `_exclusive`, subsequent readback, verifier invocation,
fsync, and rename re-open names through the filesystem.

A deterministic fixture validated an empty hidden staging directory, renamed
it away, replaced the validated name with a symlink to a directory outside the
fixed root, then called `_exclusive`. R3 successfully created the output in the
outside directory.

Required repair: open and retain trusted root, output-parent, staging, and
final-parent directory descriptors; traverse with `openat` plus `O_NOFOLLOW`;
perform every create/read/fsync/inventory operation relative to those
descriptors; compare retained inode identities; never return to a validated
path string.

### P0-3 — inherited runtime and module search paths can execute unanchored code

The batch script uses `#!/usr/bin/env bash`, unqualified tools, inherited
`PATH`, and `python3 -B`. It does not clear `BASH_ENV`, `ENV`, `PYTHONPATH`,
`PYTHONHOME`, user-site state, `APPTAINERENV_*`, or loader variables.

Deterministic fixtures showed:

- inherited `BASH_ENV` executes before the batch body;
- inherited `PYTHONPATH/sitecustomize.py` executes before Python code;
- a `numpy.py` beside the invoked script shadows real NumPy;
- a sourceless `numpy.pyc` is imported even with `-B` and
  `PYTHONDONTWRITEBYTECODE=1`.

The shell inventory check occurs before later Python invocations, while the
runtime `_load_payload` accepts an extra unlisted file. A race can therefore
insert a shadow module after the shell check, execute it before R3 validation,
and leave the manifest members themselves unchanged. The running R3 analyzer
and verifier are also reopened by Python after the earlier shell hash check;
their executing bytes are not the same descriptor snapshot later recorded by
the analyzer.

Required repair: an absolute trusted shell/interpreter/tool chain, a clean
allow-listed environment, isolated Python startup, explicit rejection of
source and sourceless shadow modules and bytecode, and a launcher that executes
the already hashed analyzer/verifier bytes rather than reopening their paths.

### P0-4 — receipt creation and final publication are not one no-replace transaction

The verifier snapshots four data files, validates those bytes, then creates a
receipt by name. A killing fixture replaced the core CSV after all four reads
but before receipt creation. The first verification returned
`PASS_R3_READBACK_READY_FOR_ATOMIC_PUBLISH` and wrote a receipt whose recorded
core CSV hash no longer matched the staging file. The later post-move
re-verification catches this particular mutation, but a crash or adversarial
swap leaves a visible directory containing authorization plus receipt before
the final check completes.

The batch script publishes with ordinary:

`mv -- "${STAGING_DIR}" "${FINAL_DIR}"`

A deterministic final-name race created `FINAL_DIR` immediately before this
command. `mv` returned zero and nested the staging directory inside the
pre-existing final directory. There is no `renameat2(RENAME_NOREPLACE)` or
equivalent descriptor-relative no-replace primitive.

Required repair: create the receipt from the retained four-file snapshots,
write and read it back on retained descriptors, re-check exact staging
inventory and inode identities, then publish the whole directory with a
descriptor-relative no-replace rename. Define fail-closed recovery for every
crash point and ensure no invalid final directory can carry apparent
authorization.

## P1 findings

### P1-1 — runtime loader is not independently closed-inventory

`_load_payload` verifies the ordered manifest members but does not enumerate
and reject an extra physical member. The batch script has a separate shell
file-list check, but the two checks are separated by a race window and do not
share directory descriptors.

### P1-2 — container/runtime identity is a path, not a digest

The SIF is checked only as readable and non-symlink:

`/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif`

Its digest, regular-file identity, and the Python/NumPy runtime identity are
not pinned into the contract or publication receipt.

### P1-3 — live remote operational viability is unproven

The Clifton certificate is currently valid for exactly twelve hours
(`2026-07-27T18:30:47` through `2026-07-28T06:30:47`). Live SSH to
`b5dj.aip2.isambard` nevertheless timed out during banner exchange at
`ai.login.isambard.ac.uk`. The official service page reported
Isambard-AI Phase 2 as having no known issues, so this appears to be a current
network/login route failure rather than certificate expiry.

Consequently the hard-coded secondary root, upstream root, SIF, `sbatch`,
account `brics.b5dj`, partition `workq`, and log directory could not be
re-read live. Prior local receipts support the account/partition/upstream
history, but they are not a current operational proof.

## P2 findings

1. `isbard doctor --ssh-timeout 30` emits an uncaught Python
   `subprocess.TimeoutExpired` traceback instead of a bounded diagnostic.
2. The receipt carries the secondary job number only inside
   `publication_name`; it has no explicit secondary `slurm_job_id` or terminal
   `COMPLETED|0:0` evidence.
3. The batch script assumes the hard-coded `logs` directory already exists;
   Slurm must open the output/error paths before the script can create it.

## Required R4 exit gates

R4 must be a new sibling root and must not modify R3. Before independent
review, it must:

1. reject the 388,493-ULP fixture and accept only frozen producer distances
   in `{0, 1}`;
2. retain directory/file descriptors across validation, write, receipt, and
   publish operations;
3. start Bash, Python, tools, and the container from absolute anchored paths
   under a clean allow-listed environment;
4. reject `PYTHONPATH`, `BASH_ENV`, path shadowing, and source/sourceless
   bytecode injection;
5. write/read the receipt from the exact four captured output snapshots;
6. publish only with a descriptor-relative no-replace directory rename and
   prove crash/recovery behavior;
7. pass the original nine tests plus at least five independent killing
   fixtures;
8. complete a live read-only remote operational preflight before any sync or
   submission.

