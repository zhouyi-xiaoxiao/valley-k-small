# Grid2D One vs Two Target — Gating

**Status: active preregistered Isambard-AI validation; no scientific result
claimed yet.** Tracking: [#8](https://github.com/zhouyi-xiaoxiao/valley-k-small/issues/8).

## Scientific question

This report compares one-target and two-target first-passage processes on a
reflecting `64 x 48` grid.  Its primary finite-horizon estimand is the paired
drop in target-1 hit probability after adding target 2.  The frozen campaign
varies 15 target-2 geometries and six quenched-field amplitudes.  Two walk
streams share each disorder field; inference averages those streams first and
uses the field as the independent block.

This report is a companion to `grid2d_two_target_double_peak`, but a shoulder,
local bump, or gating effect is not called a `double_peak` unless the separate
quantitative classifier says so.  Mean first-passage time alone is never used
as evidence for distribution shape.

## Current execution state

The v3 Isambard-AI chain is frozen and queued under account `brics.b5dj`:

- environment job `5788353`;
- eight-cell canary array `5788354` and reducer `5788356`;
- 5,760-cell production array `5788357` and reducer `5788358`;
- independent raw-cell/max-|t| secondary job `5789031`, with embedded
  dependency `afterok:5788358`.

The secondary analysis must rediscover all 5,760 canonical JSON/NPZ pairs,
reconstruct all 2,880 disorder-block means, and independently validate 480
Slurm allocations before calculating the 75-member simultaneous surface.

A separate 23,040-cell, four-GPU full-node v4 expansion is under append-only
r2 review.  It is not authorized for submission until the v3 primary and
secondary integrity gates pass.  The initial v4 implementation is retained as
audit evidence and cannot be used for pooled inference because its field
smoothing mode drifted from the frozen v3 ensemble.

## Model and integrity conventions

- Reflecting boundary means attempted-outside-stays.
- Absorption stops the trajectory immediately.
- One-target and two-target channels use paired common random numbers within
  each field/stream condition.
- Every result checks nonnegative counts, hit/unresolved mass balance, exact
  target-channel decomposition, manifest identity, and raw sidecar hashes.
- Production arrays are fail closed: missing, duplicate, partial, failed, or
  unaccounted cells never enter inference.
- Compute reservations are upper bounds; actual node hours come from Slurm
  elapsed-time and resource receipts.

## Layout

- `code/` — GPU runner, field/manifest builders, Slurm wrappers, reducers,
  secondary analysis, validators, and adversarial tests.
- `notes/` — preregistration, field/manifest contracts, payload inventories,
  Slurm design decisions, independent audits, and submission receipts.
- `artifacts/data/` — frozen field packs and campaign manifests.
- `artifacts/outputs/` — local submission state and fetched runtime results.
- `manuscript/` — reserved for English/Chinese sources after numerical gates
  pass; currently no manuscript result exists.

## Publication boundary

Queued or completed compute is not itself a result.  Figures, tables, and
manuscript claims require successful canary, production, raw reconstruction,
Slurm accounting, independent replay, and statistical readback.  This report
is scientifically separate from `encounter_multimodal_prr` and cannot supply
off-lattice F3 evidence for that paper.
