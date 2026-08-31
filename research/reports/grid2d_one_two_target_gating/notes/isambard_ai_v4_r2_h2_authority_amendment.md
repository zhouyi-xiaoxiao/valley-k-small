# v4-r2 H2 authority amendment

H2 is append-only over the frozen H1 payload. It does not modify or replace
any H1/base member. H2 closes the P0 scientific and allocation-authority gaps
before any new submission can be authorized.

The H2 v3 and v4 replayers independently read every raw integer NPZ sidecar,
reconstruct every checkpoint from the first-passage histograms, reconstruct
the disorder-block metrics, and compare the resulting tail gate and complete
`evidence_decision` with the reducer. A valid but failed tail gate is committed
as `HOLD_STAGE_A2_160K`; it never authorizes pooled inference or the next H2
hardware stage.

Every array receipt must prove a global bijection between the array-form
`JobID` and allocation-unique decimal `JobIDRaw`. Production requires exactly
480 unique allocations; the v3 canary requires exactly eight. Reusing one
allocation ID across different tasks is a hard failure even if all task suffixes
are present.

All Python scientific work runs in the SHA-pinned container and requires
Python 3.10 or newer. Every Slurm phase writes a host/container runtime probe.
The pack-heterogeneity contract is frozen in a separate JSON member before
results exist. Final pooled release additionally requires a receipt that
reverse-binds the combined job's submission receipt, `SLURM_JOB_ID`, exact
script path/hash/argv/readback, and a terminal `sacct` receipt.

Until the H2 payload builds, its tests pass, and an independent review clears
all H2 members, H2 status is `REVIEW_HOLD_NO_SUBMISSION`.
