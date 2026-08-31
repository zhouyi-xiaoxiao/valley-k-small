# Isambard AI v4-r2 H13 secondary-R5 authority runbook

Date: 2026-07-27 (Asia/Shanghai)

## Decision

**HOLD / UNSEALED / DO NOT SYNC OR SUBMIT.**

H13 is an append-only replacement scaffold for the H12 launch boundary. It
cannot authorize any Isambard job until all secondary-R5 placeholders are
replaced from an independently audited R5 publication, the complete H13
payload is sealed, and the detached H13 controller is independently hashed.

There is intentionally no
`notes/isambard_ai_v4_r2_h13_payload.sha256`. The controller pin remains
`__H13_PAYLOAD_SHA_PENDING__`, and both the controller and authority verifier
raise a fail-closed error while any R5 schema, status, key set, or member name
is pending.

## Frozen ancestors and rejected authority

- H12 payload manifest:
  `bcc487d9910dd6cb5732f26ca18caecd20b7a24844083fd61b89c361fdae0e0a`
- Detached H12 controller:
  `e3824df1224d28e4dd7e0a436b619fc6b3c22ecaefa829146d9e081946421421`
- H13 does not modify any H12, H11, or H4 member.
- Secondary R3 is **not** an H13 authority. Its independent HOLD audit is
  `notes/grid2d_gpu_v3_secondary_r3_independent_hold_audit_20260727.md`,
  SHA-256
  `329fee6703080d8eff69fdc015eb3b0f21f2026378b1612a658106cc6efeb453`.

R3 remains rejected because independent killing fixtures proved an
unbounded producer-float adapter, fixed-root path escape, executable/module
injection, verifier TOCTOU, and replace-by-name publication races. Copying an
R3 receipt or changing its status text must never satisfy H13.

Secondary R4 is also **not** an H13 authority. Its rejected author anchors are
payload manifest
`e02ac46aa968ff725f83b08a759b81cfea37197dca710c42544f78ecac0387af`
and contract
`c90ebc92958c1ddb82aa0f54919a32f8e0c3ca64c7ea90dbf7c97dc20da232b4`.
Its independent HOLD audit is
`notes/grid2d_gpu_v3_secondary_r4_independent_hold_audit_20260727.md`,
SHA-256
`7f18217760ace67d8d545e986ec0d67a4e63a355b348c5c05d1d967e08c02e75`.
Independent killing fixtures found that R4 final readback did not recompute
producer and single-division identities from raw counts or bind raw/upstream
inventory, so forged counts could pass. They also found a cross-process
directory-reopen swap between analyzer and verifier. R4 schema, status,
receipt, or payload values cannot satisfy the R5 placeholders.

H12 is also not currently runnable as scientific authority: its authority
chain still depends on absent H1/H4 release state, and the inherited H4
verifier uses a hard-coded root that does not follow H12's immutable package
snapshot.

## H13 repair boundary

The unsealed scaffold currently provides:

1. a detached controller entrypoint pinned to
   `/opt/cray/pe/python/3.11.7/bin/python3.11`, SHA-256
   `9270f0548999f7c4fa66df1c4fd4ec6a7edfc54ff5b8bd881d89a2cc891f6b94`,
   and requiring isolated mode before controller code is imported;
2. root-owned, absolute Slurm tools, a clean allow-listed control
   environment, held-before-receipt submission, durable recovery, and one
   `--export=NIL` boundary;
3. no Lmod dependency in any H13 phase;
4. absolute `/usr/bin/apptainer` and `/usr/bin/srun`, absolute `/bin/bash`,
   and container Python launched with `-I -B -E -s`;
5. an in-memory Python launcher fed through standard input: it reads each
   local entrypoint and sibling module once from the H13 manifest using
   retained directory descriptors, compiles those exact bytes, and supplies
   a manifest-only import hook. It neither adds `code/` to `sys.path` nor
   reopens a script by pathname;
6. a single-descriptor, `openat`/`O_NOFOLLOW`, single-link reader for payload
   members and imported authority inputs;
7. live exact-one-row `sacct -X` binding for the secondary R5 job, requiring
   `COMPLETED`, `0:0`, and positive elapsed time;
8. a three-job-only dependency chain:
   `v3_authority_h13 -> canary -> production`;
9. a production array fixed at `0-479%240`, one node, four tasks, four GPUs,
   one GPU per task, 48 cells per array element, 23,040 cells total, and a
   two-hour limit. Its maximum allocation ceiling is 960 node-hours. Reducer
   and every later phase remain unauthorized.

These controls are scaffold evidence only. They do not authorize execution
while the contract and manifest remain pending.

## Local scaffold validation

- `code/test_isambard_ai_gating_v4_r2_h13.py`: 11/11 tests pass.
- All three H13 sbatch files pass `bash -n`.
- Direct `-I` execution of the authority, canary, and production Python
  entrypoints originally failed because isolated mode excludes the sibling
  `code/` directory. The H13 manifest-only in-memory launcher is the scaffold
  repair without adding a path or weakening isolated startup; its synthetic
  sibling-import, injection, and source-drift killing tests pass.
- H7 through H12 regression: 73/74 tests pass. The one error is the existing
  H10 test
  `test_fake_slurm_sbatch_receipt_crash_unique_recovery_and_chain`, which
  invokes its controller while `H10_SHA` is still
  `__H10_PIN_PENDING__`. H7, H8, H9, H11, and H12 are fully passing; the H10
  error is a legacy test-fixture setup defect, not an H13 release result.
- Frozen H12 manifest and detached controller hashes remain exactly
  `bcc487d9910dd6cb5732f26ca18caecd20b7a24844083fd61b89c361fdae0e0a`
  and
  `e3824df1224d28e4dd7e0a436b619fc6b3c22ecaefa829146d9e081946421421`.

## R5 evidence required before sealing

An independent R5 GO report must provide, as literal immutable values:

- the R5 payload-manifest SHA-256 and closed ordered member inventory;
- exact R5 release schema and status;
- exact independent-audit schema and status;
- exact top-level key sets for both JSON objects;
- exact publication member names and order;
- the release member name and independent-audit member name;
- an explicit Slurm job id and a publication directory name ending in that
  job id;
- exact SHA-256 for every publication member;
- reverse bindings among publication name, job id, member hashes, release,
  audit, and live terminal accounting;
- passing evidence for all R3 and R4 killing fixtures, including 388,493-ULP
  rejection, environment/module injection rejection, descriptor-anchored
  output, no-replace publication, crash recovery, raw-count recomputation,
  raw/upstream inventory binding, and a single-process retained-directory-FD
  analysis-to-publication transaction;
- a live read-only Isambard preflight for account, partition, container,
  scheduler executables, roots, and certificate validity.

If any value is inferred, missing, mutable, path-only, or not independently
GO-audited, H13 stays HOLD.

## Versioned future authority CLI

The fixed H13 controller-to-authority prefix is:

1. H13 payload-manifest SHA-256;
2. `h13-secondary-authority-cli-v1`;
3. exact R5 release schema;
4. exact R5 release status;
5. exact R5 audit schema;
6. exact R5 audit status;
7. exact secondary Slurm job id;
8. exact publication directory name.

The controller then injects an immutable live-accounting path and SHA-256 as
positions 9 and 10. Remaining arguments must repeat this exact group, in the
frozen publication order:

```text
--secondary-member-name MEMBER_NAME
--secondary-member ABSOLUTE_RUN_ROOT_MEMBER_PATH
--secondary-member-sha256 MEMBER_SHA256
```

The tail must identify:

```text
--secondary-release-member RELEASE_MEMBER_NAME
--secondary-audit-member AUDIT_MEMBER_NAME
```

Every absolute member path must also be imported once using controller
`--phase-input RELATIVE_RUN_ROOT_PATH=MEMBER_SHA256`. The controller maps
those paths to immutable `0400` copies inside the per-task
`SLURM_TMPDIR` snapshot. No path outside the H13 run root is accepted as a
phase input.

## Future sealing order

Only after independent R5 GO:

1. replace every R5 placeholder in
   `code/h13_pinned_controller_v4_r2.py` and
   `code/verify_v3_release_for_v4_r2_h13.py`;
2. adapt the generic reverse-binding checks to the exact R5 contract. Do not
   retain a self-referential member-hash condition if the actual R5 release
   excludes its own digest;
3. add killing tests generated from the exact R5 schema and all R5 audit
   fixtures;
4. run H7 through H13 tests and all shell syntax checks;
5. build a new closed H13 payload as H12's exact ordered prefix plus only the
   reviewed H13 append;
6. compute the H13 manifest SHA-256, insert that value into the detached H13
   controller, and hash the final detached controller;
7. independently verify every payload member, both detached-controller
   anchors, file modes, link counts, and closed inventory;
8. stage into a new remote `0700` package root and new `0700` run root, with
   immutable files at `0600`; never overwrite or reuse an H12/R3 package or
   run root;
9. run a fresh read-only preflight and re-check the control-Python,
   container, Slurm-tool, account, and partition anchors;
10. submit only through the detached H13 controller.

## Future submission shape

The exact values below remain placeholders and are not executable
instructions:

```bash
H13_CONTROLLER=/ABSOLUTE/DETACHED/h13_pinned_controller_v4_r2.py
H13_PACKAGE=/ABSOLUTE/NEW/H13/PACKAGE
H13_RUN=/ABSOLUTE/NEW/H13/RUN
H13_SHA=__H13_PAYLOAD_SHA_PENDING__
R5_JOB=__R5_JOB_PENDING__
R5_PUBLICATION=__R5_PUBLICATION_PENDING__

/opt/cray/pe/python/3.11.7/bin/python3.11 -I -B -E -s \
  "$H13_CONTROLLER" submit \
  --package-root "$H13_PACKAGE" \
  --run-root "$H13_RUN" \
  --phase v3_authority_h13 \
  --phase-input artifacts/external/r5/RELATIVE_MEMBER=__MEMBER_SHA_PENDING__ \
  -- \
  "$H13_SHA" \
  h13-secondary-authority-cli-v1 \
  __R5_RELEASE_SCHEMA_PENDING__ \
  __R5_RELEASE_STATUS_PENDING__ \
  __R5_AUDIT_SCHEMA_PENDING__ \
  __R5_AUDIT_STATUS_PENDING__ \
  "$R5_JOB" \
  "$R5_PUBLICATION" \
  --secondary-member-name __MEMBER_NAME_PENDING__ \
  --secondary-member "$H13_RUN/artifacts/external/r5/RELATIVE_MEMBER" \
  --secondary-member-sha256 __MEMBER_SHA_PENDING__ \
  --secondary-release-member __RELEASE_MEMBER_PENDING__ \
  --secondary-audit-member __AUDIT_MEMBER_PENDING__
```

The canary may be submitted only after the authority job has a valid H13
envelope and runtime receipt. Production may be submitted only after the
canary has a valid H13 envelope, runtime receipt, and four-distinct-GPU
receipt. The final candidate receipt still states
`authorizes_execution: false` and `authorizes_scientific_release: false`.

## Certificate boundary

The current Isambard certificate is intentionally short-lived. A 12-hour
certificate limits stolen-credential exposure; it does not limit Slurm job
wall time after a job is accepted. A fresh certificate is required for later
interactive SSH, status, accounting, recovery, or download operations. Never
weaken H13 or pre-submit an unsealed campaign merely to fit inside one
certificate window.
