# Isambard-AI v4 full-node disorder-block expansion

Protocol ID: `grid2d_one_two_target_gating_isambard_ai_v4_fullnode_20260727`

Design status: frozen before observing any v3 production result.  This is an
append-only successor campaign.  It does not alter the submitted v3 payload,
its Slurm chain, or any v3 output.

## Scientific purpose and release rule

The v4 campaign estimates the same frozen geometry-by-amplitude surface with
an independent 128-block disorder pack.  It is released only after the v3
canary, inventory, production reducer, and secondary max-t integrity audits
complete successfully.  Release is unconditional on the sign, magnitude, or
statistical significance of the v3 effects.  A v3 scientific hold is retained
and reported; it is not repaired by selecting a favourable replacement
parameter.

The combined analysis uses all 32 v3 blocks and all 128 v4 blocks (160 blocks
total).  The primary contrast, 75-member simultaneous surface, finite-horizon
tail boundary, amplitude grid, geometry grid, walker count, checkpoints, and
no-early-stopping rule are unchanged.

## Independent field and walk domains

- domain: `64 x 48`, periodic correlated field construction unchanged;
- correlation scale: isotropic `sigma = 4.0`;
- field count: `128`;
- field RNG: NumPy `PCG64`;
- field seed formula: `8202607270000 + 1000003 * field_index`;
- walk streams per field: `0,1`;
- walk seed formula: `12000000000 + 104729 * field_index + 1009 * stream_index`.

The field and walk seed domains are disjoint from v3.  Each generated field
must retain exact zero mean under `math.fsum`, exact maximum absolute contrast
one, and a content hash in the pack sidecar.  A pack or manifest collision
with a v3 hash is a hard failure.

## Frozen campaign size

The campaign is exactly

```text
15 geometries x 6 amplitudes x 128 fields x 2 streams = 23,040 cells.
```

Every cell keeps 1,000,000 walkers, the 80,000-step horizon, checkpoints
`5k,10k,20k,40k,80k`, base holding probability `0.30`, target radius three,
and the v3 fixed-mean and mass-balance tolerances.

## Four-GPU whole-node mapping

One Slurm array contains tasks `0-479` with concurrency cap `%240`.  Every
allocation requests one complete GH200 node (`4` GPUs) and runs four isolated
GPU lanes.  For array task `t`, GPU lane `g=0,1,2,3`, and sequential wave
`k=0,...,11`, the sole cell is

```text
cell_id = t + 480 * (g + 4*k).
```

The map covers `0..23039` exactly once.  Each GPU evaluates twelve cells in
sequence; failure of any lane or cell makes the allocation fail.  The reducer
requires exactly 480 unique successful allocations, tasks `0..479`, 48 exact
cell identities per allocation, and `COMPLETED/0:0` accounting for every
allocation.  Partial results never enter inference.

The requested wall limit is two hours.  This is a reservation ceiling of
`480 allocations x 2 hours x 1 full node = 960 NHR`; it is not a claim of
actual usage.  Actual accounting is taken from Slurm elapsed time and the
full-node resource fraction.  The design intentionally uses full nodes so the
additional allocation buys independent disorder information rather than idle
single-GPU node fractions.

## Statistical analysis

The v4-only and combined v3+v4 analyses both use disorder blocks as the
independent unit after averaging the two walk streams within each block.
They report:

1. the unchanged primary Student-t interval and ROPE classification;
2. the unchanged 75-member field-block max-|t| bootstrap family;
3. tail diagnostics at the six frozen anchor conditions;
4. v3-versus-v4 pack heterogeneity diagnostics fixed before pooling; and
5. exact provenance, result inventory, and Slurm receipts.

For the combined 160-block max-|t| analysis, the seed is `2026072701`, the
resample count is `20,000`, and every bootstrap draw jointly resamples one
160-index vector for all 75 contrasts.  The simultaneous critical value is
the order statistic at `ceil((20000+1)*0.95)`.  No surface member may be
dropped after results are observed.

## Append-only and publication boundary

All v4 scripts, packs, manifests, logs, results, and reductions live in a new
sibling remote root.  The v3 remote root is read-only.  Payload manifests are
hash-pinned before submission, output commits are no-overwrite, and an
independent reducer replay is required before manuscript use.

This expansion strengthens finite-horizon, physical-grid evidence only.  It
does not establish an asymptotic splitting law, strict continuum convergence,
or any result for the separate `encounter_multimodal_prr` paper.
