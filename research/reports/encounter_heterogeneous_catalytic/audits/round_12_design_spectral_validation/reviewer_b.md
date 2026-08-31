# Round 12 reviewer B — spectral production audit and counterexamples

Date: 2026-07-13

## Checks performed

I inspected `validate_spectral_modality.py`, full coefficient output, the
frozen encounter and M2D-T generators, and the two counterexample families.
For each production model the script reconstructs the reversible measure,
checks detailed balance, symmetrizes the killed generator, performs a full
eigendecomposition, groups near-equal rates, sweeps four residue cutoffs, and
reconstructs the density and derivative at every direct critical point.

## Results

- 961-state supercritical encounter model: three direct critical points;
  minimum retained sign variations across `1e-12`--`1e-6` cutoffs is 444,
  above the necessary three.  The early spectral reconstruction is limited by
  cancellation across a multi-decade reversible measure; its worst density
  error is `8.83e-6` and scaled derivative residual `2.29e-6`, both inside the
  conditioning-aware gates.
- 2025-state M2D-T `9x5` model: five direct alternating critical points;
  minimum retained variations is 191, above the necessary five.  Worst density
  error is `4.48e-11` and scaled derivative residual `4.32e-11`.
- Exact four-stage hypoexponential: three residue sign changes but the unique
  positive critical point is `log(4)`, proving non-sufficiency.
- Rank-one killing network: roots at `0.92676432` (max), `2.65921039` (min),
  and `9.17667747` (max), all with scaled derivative residual below `1.2e-13`.

## Interpretation

The large residue counts are not predictions of 444 or 191 modes.  They only
pass a necessary lower-bound gate.  The manuscript states this correctly and
excludes nonreversible/Jordan/continuum extensions.  No open finding remains.
