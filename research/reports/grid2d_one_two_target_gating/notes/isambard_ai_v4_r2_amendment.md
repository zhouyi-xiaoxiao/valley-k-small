# Isambard-AI v4-r2 reflect-disorder amendment

Protocol ID: `grid2d_one_two_target_gating_isambard_ai_v4_r2_20260727`

This amendment is append-only.  It does not alter the initial v4 payload
manifest (`3752b36338c732483b0aa739331abbff0e9999be8f4c83ad34461d65ef856485`),
its 16 members, or its `wrap` disorder pack.  That initial pack is retained as
an unpooled sensitivity design only.

The publication expansion uses a newly generated 128-field pack with the same
`scipy.ndimage.gaussian_filter(..., sigma=4, mode="reflect", truncate=4.0)`
construction as frozen v3.  It keeps the previously frozen independent field
seed domain `8202607270000 + 1000003*i`, walk seed domain
`12000000000 + 104729*i + 1009*s`, exact `math.fsum` zero, exact maximum
absolute contrast one, 64x48 domain, 15 geometries, six amplitudes, two walk
streams, 1,000,000 walkers and 80,000-step horizon.

The v4-only max-|t| bootstrap is frozen to `PCG64(2026072700)`, 20,000 joint
field-block resamples.  The pooled 32+128 analysis is permitted only after the
fixed v3 release verifier and independent v4 raw replay have written
hash-pinned, no-overwrite PASS receipts.  Its bootstrap remains
`PCG64(2026072701)`, 20,000 joint resamples, with the 19,001st ordered maximum
as its 95% critical value.  The primary contrast is `(32,24), 0.20-0.00`; both
v4-only `n=128` and pooled `n=160`, df 159 Student-t intervals and the frozen
ROPE `[-0.002,0.002]` are reported.

The remote root is the new sibling
`/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727`.  Production is
not released until fixed jobs 5788357, 5788358 and 5789031 have completed and
the v3 release receipt passes, then a four-lane hardware canary proves four
distinct GPU UUIDs/PCI addresses/CUDA-visible assignments.  Dynamic `afterok`
dependencies and `scontrol` readback are recorded by the hash-pinned submit
helper.  All raw/reduction/replay outputs are no-overwrite and exact-inventory.

The full-node map remains `cell=t+480*(g+4*k)` for tasks `0..479`, lanes
`g=0..3`, waves `k=0..11`.  Extended Slurm accounting must prove one node,
four allocated/requested GPUs, 48 exact cells per allocation, `COMPLETED/0:0`,
positive `ElapsedRaw`, and records actual full-node NHR as the sum of allocation
elapsed seconds divided by 3600.  The 960 NHR figure remains a reservation
ceiling, not actual usage.
