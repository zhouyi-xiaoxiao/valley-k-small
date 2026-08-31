# Encounter continuum Round-3 delta bundle

This sidecar describes the portable local bundle
`encounter_continuum_round3_delta_20260717.tar.gz`.

- Status: explicit-file delta for continuation on another Mac; not a full repository snapshot or a Git commit.
- Size: `1,145,814` bytes.
- SHA-256: `f8814e35318fee1058f82c7a181421929484b56a3d0421079da224820a6403dc`.
- Contents: the current manuscript and supplement, continuum C0/C1 notes and audits, frozen evidence artifacts, active verification code, tests, reproducibility requirements, and the remote handoff note.
- Exclusions: no `.venv`, scratch directory, transient result payload, or control payload.

On the target Mac, place the archive in the repository root and verify it before extraction:

```sh
shasum -a 256 research/reports/encounter_multimodal_prr/artifacts/handoff/encounter_continuum_round3_delta_20260717.tar.gz
tar -xzf research/reports/encounter_multimodal_prr/artifacts/handoff/encounter_continuum_round3_delta_20260717.tar.gz
```

Then create a target-local Python 3.12 environment from
`research/reports/encounter_multimodal_prr/code/requirements-reproducibility.txt`,
run `check_reproducibility_environment.py`, and execute the four C0 command-line
checks plus the focused `86/86`, combined strict-continuum `119/119`, and
compile/freeze `29/29` suites listed in `notes/REMOTE_CODEX_HANDOFF_20260715.md`.

The report directory is currently outside the Git index. Therefore a plain
`git pull` on the target Mac will not transfer it. Use this archive, allow the
OneDrive path to synchronize, or deliberately add and commit the report in a
later provenance-controlled step.
