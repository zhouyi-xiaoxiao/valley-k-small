# Isambard-AI v3 secondary r1 submission receipt

Submission status: queued; scientific result not yet available.

```text
job_id=5789031
dependency=afterok:5788358
remote_root=/home/b5dj/ae23069.b5dj/valley-gating-v3-secondary-r1-20260727
payload_manifest_sha256=acdae65da56e5e7ff2d4de4cf36fe680ec9d5184ed211f7c726b18358d6d5c20
sbatch_sha256=a04b5f67ede9e2323e5628b17b1eab5e0e33143f6001a604674c88332c69224d
remote_submission_receipt_sha256=66fbfd0465f2ff3354663c69296da041effd7bf70d5bcbb9beadddc99eb48454
```

The payload was synchronized only to the new sibling root.  The submitted
sbatch has embedded dependency `afterok:5788358`; `scontrol` readback showed
`PENDING (Dependency)`, the expected command path, and the expected working
directory.  The upstream v3 root was not written by this submission.

The execution package received an independent GO after adversarial checks for
coordinated reducer-summary mutation, exact 5,760 raw JSON/NPZ pairs, the real
seven-key NPZ schema, external hardlinks, 480 Slurm allocations, 2,880
independently reconstructed disorder-block means, and the 75-member joint
max-|t| calculation.

This receipt does not claim `PASS_SECONDARY_MAX_T_R1`.  That status requires
job `5789031` to finish `COMPLETED 0:0`, write only its canonical mode-600 JSON
and CSV outputs, and pass final readback of raw inventory, block reconstruction,
Slurm accounting, and result hashes.
