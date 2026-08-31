# v4-r2 H3 authority amendment

H3 is append-only over the frozen H2 payload. No H2, H1, or base member is
modified. H3 preserves H2's global `JobIDRaw` bijection, raw checkpoint/tail
replay, pack-heterogeneity diagnostics, combined submission reverse binding,
and terminal Slurm release gate.

H3 closes the remaining primary-inference authority defect. For both v3 and
v4, it selects the frozen `(target2_x,target2_y)=(32,24)` amplitude `0.00`
and `0.20` cells from the manifest, reads their raw integer NPZ sidecars,
recomputes each walk-stream gating probability, averages paired walk streams
inside each disorder block, computes the paired block effects and Student-t
interval, applies the frozen `[-0.002,0.002]` ROPE, and derives the decision.
The complete reducer `primary` object and `evidence_decision` must match this
independent reconstruction. A forged `positive_change`, `negative_change`,
`practical_equivalence`, `inconclusive`, statistic, or ROPE value is fatal.

H3 also closes the live host-runtime mismatch. Every H3 Slurm script executes
`module load cray-python/3.11.7`, requires the loaded-module token and exact
host version `3.11.7`, and records the absolute host interpreter. Scientific
Python continues to run only in the SHA-pinned SIF and must report exact Python
`3.12.11`. The runtime receipt binds both interpreters, the module token, SIF
path, SIF SHA-256, phase, and `SLURM_JOB_ID`.

Until the H3 payload and its killing tests pass an independent review, H3 is
`REVIEW_HOLD_NO_SUBMISSION` and must not be synced or submitted.
