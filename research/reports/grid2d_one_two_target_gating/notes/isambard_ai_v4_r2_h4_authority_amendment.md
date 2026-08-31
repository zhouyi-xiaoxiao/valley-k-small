# v4-r2 H4 fail-closed authority amendment

H4 is an append-only overlay over the frozen H3 payload whose manifest SHA-256
is `df399e156545935ccaa0d5d5a73b8c3f8f32227f8889ffe55b34662630adf1f2`.
No base, H1, H2, or H3 member is modified.

## P0 closure

The H3 terminal finalizer accepted caller-selected combined JSON and CSV paths
and checked only a partial envelope.  Consequently an attacker could delete
`authorization`, `primary`, or `surface`, update the combined JSON SHA-256 and
the release-submission receipt together, and retain an H3 release path.  H4
removes this authority class.

There is exactly one combined JSON/CSV location for a pair of decimal Slurm job
IDs:

```text
artifacts/combined_h4/replay-<replay_job>-combined-<combined_job>/combined_v4_r2_h4.json
artifacts/combined_h4/replay-<replay_job>-combined-<combined_job>/combined_v4_r2_h4.csv
```

Neither the H4 release submission CLI, release sbatch, nor terminal finalizer
accepts a combined path.  Each derives these paths independently.  The H4
combined object has an exact top-level key set and exact key sets for
`authorization`, `submission_binding`, and `csv`; missing and extra keys are
fatal.

At final release H4 reopens the canonical v3 release, v4 replay, replay
submission, and combined submission receipts.  It verifies their paths,
SHA-256 values, schemas, statuses, job/dependency lineage, scripts, exact
`sbatch` argv, and `scontrol` readback.  It recomputes the canonical digest of
both embedded raw-primary/ROPE replay objects and closes the two fixed
reduction CSV paths and SHA-256 values.

The finalizer independently reconstructs the 32-block v3 and 128-block v4
effect matrices from the authorized reduction CSVs, reruns the three primary
analyses, the three fixed-seed max-t surfaces, and the frozen H2 pack
heterogeneity calculation, then applies strict recursive equality to
`primary`, `surface`, and `pack_heterogeneity`.  A PASS label, an outer hash,
or a synchronously rewritten release receipt cannot replace this semantic
reconstruction.  The emitted combined CSV bytes must also equal a fresh
serialization of the independently reconstructed combined surface.

H4 runtime receipts have exact schemas and fully bind host module
`cray-python/3.11.7`, host Python `3.11.7`, absolute host executable, SIF Python
`3.12.11`, CPython implementation, absolute SIF executable, frozen SIF path,
SIF SHA-256, phase, and decimal Slurm job ID.  The v3-authority, replay,
combined, and release authorities reopen and validate their canonical runtime
receipts.

## Execution policy

`status=REVIEW_HOLD_NO_SUBMISSION`

`authorizes_execution=false`

H4 is a local repair and review artifact.  Building or verifying its
content-addressed payload does not authorize synchronization, submission, or
execution on Isambard.
