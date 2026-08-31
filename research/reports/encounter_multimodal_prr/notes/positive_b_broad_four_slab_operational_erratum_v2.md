# Positive-budget broad four-slab operational erratum v2

Date: 2026-07-14  
Scope: serialization-only repair before any held-out result was observed

## Failed first execution

The first frozen two-process execution terminated during publication of the
first replica. Both held-out mesh calculations had completed, but the
canonical JSON validator rejected a NumPy `bool_` gate scalar at
`heldout_mesh_rows[0].gates.survival_positive`. No canonical result and no
reproducibility-evidence file were created. The failure is operational and
must not be interpreted as a scientific PASS or HOLD.

The pre-execution pins were:

- manifest SHA-256:
  `01b435c834cec9e7bfde2069b19fcdcaa4e06178ccfe0d4b6082f0705dfd5805`;
- producer SHA-256:
  `0c70ffb4a9034772928e2fa95d2ca79ef33754e5aa4157a2f101e15cb312b003`;
- test SHA-256:
  `ee784d1cf6cc4e7ee66968deb8f3421394f697eebee3a50f783533aa469a8f78`;
- protocol SHA-256:
  `f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00`.

## Minimal repair

The scientific inputs, selected budget, weights, geometry, held-out meshes,
scan, gates, tolerances, and PASS/HOLD rule remain byte-for-byte unchanged in
meaning. The producer now converts only native Python Boolean and NumPy
Boolean gate scalars to native JSON Boolean values; integers, floats, strings,
nulls, and other truthy objects are rejected. The same normalization is used
for tail, per-mesh, and cross-mesh gate mappings.

One regression test reproduces the NumPy-comparison scalar and verifies both
canonical serialization and fail-closed rejection of non-Boolean values. The
formal preflight count therefore changes from 15 to 16. This erratum is added
as a new frozen pin. No feasibility or held-out numerical value was used to
make the repair.

The v2 formal execution must start from two absent canonical outputs, use the
updated externally supplied manifest SHA-256, and again run two fresh full
subprocess replicas. Only byte-identical replicas may be promoted.
