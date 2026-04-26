# Grid2D One Target — Base

**Status: WIP scaffold (not yet started).** This is the **mother report** for the `grid2d_one_target_*` sub-series. It defines the shared problem setup, notation, and conventions used by the four sibling reports listed below.

## Why this exists

The sibling reports (`exit_timing`, `valley_peak_budget`, `window_measures`, plus `grid2d_one_two_target_gating` which compares one- vs two-target) all assume the same base 2D-grid single-target FPT problem but each focuses on a different observable. Without a base report, every sibling has to re-derive the setup and notation. This base report consolidates the shared front matter and is the canonical citation for the single-target setup.

## Sibling reports (one_target sub-series)

- `grid2d_one_target_exit_timing` — exit-timing distribution
- `grid2d_one_target_valley_peak_budget` — valley/peak mass budget
- `grid2d_one_target_window_measures` — fixed-window measures (mass, percentile, tail)
- `grid2d_one_two_target_gating` — gating effect of adding a second target (uses base + extends)

## Intended scope

- **Problem setup**: single absorbing target on a finite 2D-grid; choose between reflecting / periodic boundary; start position protocol; T grid convention.
- **Notation**: target placement $\mathbf{x}^\star$, start $\mathbf{x}_0$, FPT $\tau$, lattice constants, time discretisation.
- **Estimator conventions**: which AW / recursion / MC variants are used, and when each is the reference.
- **Reproducibility conventions**: shared seed scheme, result-file layout, figure-style policy.

## TODO before this report is real

- [ ] Decide whether this should live under `research/docs/` as a methods note instead of a report (no manuscript output of its own — purely a shared front matter)
- [ ] If kept as a report: draft `manuscript/grid2d_one_target_base_{en,cn}.tex` containing only the shared setup
- [ ] Have each sibling report's manuscript cite this base report's setup section instead of re-deriving
- [ ] Replace this README with one matching the style of `cross_luca_regime_map/README.md`
