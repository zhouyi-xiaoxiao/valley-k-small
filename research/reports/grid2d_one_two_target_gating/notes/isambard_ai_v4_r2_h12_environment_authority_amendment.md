# v4-r2 H12 environment-authority amendment

H12 is an append-only successor to immutable H11 SHA-256 `dec7cf087c9cb5ab86cc84afbd6b9da59774c76a5bdc030b09155e0745e356ca`. H7 through H11 and the detached H11 controller SHA-256 `776ef08bd2c54e22bfb4acc3863da37e9c18c0beb7e101e5824777c490732f2f` are frozen.

## H11 P0 finding

H11 submitted with Slurm's inherited environment, used `#!/usr/bin/env bash`, and resolved controller, wrapper, and science executables through inherited `PATH`. A killing replay exported a `BASH_ENV` hook. The hook ran before the first bound wrapper command, while the H11 controller still returned `RELEASED_AFTER_DURABLE_SUBMISSION_RECEIPT` and the science self-test completed. Exact package, wrapper, transaction, scheduler-identity, and accounting receipts therefore did not prove the absence of pre-science injected execution.

## H12 repair

The detached H12 controller verifies the exact closed H12 package and the detached H11 controller anchor, serializes each run root with a kernel lock, and admits only absolute, root-owned, non-writable Slurm executables whose device, inode, size, modification time, mode, owner, and SHA-256 are rechecked before and after every scheduler call. Scheduler commands receive a minimal controller environment.

Every `sbatch` call uses both a bound `#SBATCH --export=NIL` directive and command-line `--export=NIL`. The submitted wrapper starts with `#!/bin/bash`, calls only absolute bootstrap tools, deletes Bash, Python, dynamic-loader, and exported-function injection surfaces, fixes `PATH=/usr/bin:/bin` and the C locale, and starts an exact content-bound Python interpreter with isolated flags `-I -B -E -s`. The controller requires that interpreter and all ancestors be root-owned and non-writable. The local killing harness injects a test-only exact interpreter anchor when emulating Slurm on macOS; no controller CLI or production code path exposes that harness override.

The H12 runtime re-verifies and snapshots the closed H12 package before loading immutable H11 transaction code. Science runs under absolute `/bin/bash --noprofile --norc` with an explicit environment consisting only of passwd-derived identity, fixed locale and path, Slurm/SPANK identity, scheduler-provided GPU identity, and content-bound H11/H12 roots. Production phases source exactly one root-owned, non-writable module-initialization file and record its SHA-256. H12 runtime receipts remain H11 transaction-schema compatible while adding the H12 manifest, isolated-environment status, interpreter anchor, environment key hashes, and module-initialization anchor. Downstream H12 admission requires both the immutable H12 execution envelope and H12-marked runtime receipts before replaying the inherited H11 live-accounting and transaction gates.

The full-node science bytes remain H4 SHA-256 `30df2636b4459a3ff6c91ccb1cd6bca9e9ab7a6017a0bc4a334e4fbf64fc4bbe` and retain `--nodes=1`, `--ntasks=4`, `--gpus=4`, `--gpus-per-task=1`, and `--array=0-479%240`.

H12 authorizes only the three-stage compute campaign `v3_authority -> canary -> production`. With 480 one-node array elements and a two-hour walltime, production has a hard 960 node-hour ceiling; `%240` limits concurrency and each element uses all four requested GPUs. Reducer, replay, combined, release, and terminal remain HOLD for an append-only H13 because the frozen H4 replay/combined validators require legacy `artifacts/submission_h4/*` receipts that the honest H11/H12 controller does not create. H12 does not synthesize those receipts.

`status=H12_ENVIRONMENT_AUTHORITY_CANDIDATE_NO_SUBMISSION`

`authorizes_execution=false`

`authorizes_scientific_release=false`

These flags mean that this candidate does not self-authorize compute or scientific release. They do not make execution mechanically impossible: an independent GO plus the user's external authorization may invoke the detached H12 controller. Any resulting terminal candidate still has no scientific-release authority until a separate scientific review.
