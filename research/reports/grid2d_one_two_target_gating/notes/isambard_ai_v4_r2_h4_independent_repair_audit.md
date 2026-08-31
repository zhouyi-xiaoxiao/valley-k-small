# Independent H4 GPU-gating repair audit — 2026-07-27

## Scope and disposition

This audit covers only the append-only H4 files in the local dirty/untracked
working tree.  No remote synchronization or Slurm submission was performed.

`status=REVIEW_HOLD_NO_SUBMISSION`

`authorizes_execution=false`

## Independent H3 finding reproduced

Inspection of `finalize_gpu_gating_v4_r2_h3.py` confirmed that the caller could
select arbitrary combined JSON and CSV paths.  The finalizer checked the H3
envelope, CSV hash/row count, combined and release submission bindings, a
minimal runtime envelope, and terminal `sacct`, but did not require exact H3
combined keys, reopen the v3/v4 replay authority, recompute raw-primary
digests, or independently close `primary`, `surface`, and
`pack_heterogeneity`.  A combined object with those scientific branches
removed therefore remained admissible if its outer SHA and release receipt
were updated together.

## H4 repair evidence

- Combined JSON/CSV paths are a pure function of decimal replay and combined
  job IDs; neither path is accepted as release input.
- Combined, authorization, submission-binding, CSV, v3 receipt, v4 replay,
  submission, and runtime objects use exact-key checks.
- Canonical v3/v4 receipts are reopened by path and SHA.  Required status and
  authorization booleans are checked, and raw-primary replay digests are
  recomputed from the complete embedded replay objects.
- Canonical v3 and v4 reduction CSV paths and SHA-256 values are derived from
  reopened upstream authority rather than from the combined PASS object.
- Primary, ROPE, fixed-seed max-t surface, pack heterogeneity, and combined CSV
  bytes are independently recomputed before release.
- Runtime validation covers exact host module/version/executable, SIF Python
  version/implementation/executable, frozen SIF path/SHA, phase, and Slurm job.
- The final output path is also derived from replay, combined, and release job
  IDs.

## Local verification

The frozen base/H1/H2/H3 suites were rerun together with H4 under Python 3.12,
NumPy 2.0.2, and SciPy 1.14.1:

```text
base  14/14 PASS
H1    20/20 PASS
H2    13/13 PASS
H3    10/10 PASS
H4    24/24 PASS
total 81/81 PASS
```

H4 killing tests reject arbitrary combined paths; deletion of authorization,
primary, surface, and CSV path; mutation of ROPE, primary statistics,
raw-primary digest, heterogeneity, and CSV path; and the synchronized forged
combined-SHA/release-receipt attack.  They also reject every required host/SIF
runtime identity mutation.  All H4 Python files pass `py_compile`; all seven
H4 sbatch files pass `bash -n` and statically contain the pinned host-module and
SIF runtime probe.

Frozen payload manifest SHA-256 values remained:

```text
base c6c77f62d05fb17c25160723f87324654041c2de484c3f4e12b2bf92bb8af404
H1   29949d276b04e6ebecdba3a3e0891a8f0ad6895cf6857822956395bff0eac76e
H2   1dd32b6c5a1786b3e1c2d0d587c0e4219ab894b96f132c94c391804f9e970aec
H3   df399e156545935ccaa0d5d5a73b8c3f8f32227f8889ffe55b34662630adf1f2
```

The H4 payload manifest content-addresses this report and every H4 authority
member.  Because the report is itself a manifest member, its text intentionally
does not contain the resulting H4 manifest SHA (which would be circular).
