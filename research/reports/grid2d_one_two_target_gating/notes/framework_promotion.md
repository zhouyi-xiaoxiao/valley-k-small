# Framework Promotion

This report is no longer a light summary that copies bundle plots into a new PDF. It promotes the March 16 mechanism work into a repo-native subsystem.

## Promotion chain

1. `二维半透膜_gating_game`
   - supplies the original gate-language sketch, phase-v2 logic, and the one-target / two-target conceptual bridge.
2. `two_target_gating_framework`
   - turns no-corridor two-target into a gate-lifted exact/MC framework with coarse 4-family and fine 5-family views.
3. `one_two_target_deepening_work`
   - unifies both lines, adds one-target `q*` sensitivity and side-aware splitting, and adds two-target atlas / progress / side-usage outputs.

## What was promoted into shared code

- `vkcore.grid2d.one_two_target_gating.one_target`
  - membrane case builder
  - committor solve
  - exact four-family decomposition
  - side-aware top/bottom decomposition
- `vkcore.grid2d.one_two_target_gating.two_target`
  - gate configuration
  - representative case construction
  - exact family decomposition
  - committor audit
  - scan / robustness helpers
  - MC summaries and representative-case exports
- `vkcore.grid2d.one_two_target_gating.phase_v2`
  - gate-word reduction and phase-v2 helpers
- `vkcore.grid2d.one_two_target_gating.plotting`
  - conceptual gating figures
  - one-target summary plots
  - two-target atlas / progress / side-usage plots
  - representative case figure builders

## Canonical build rule

- Raw zips and PDFs are archived only.
- The report build script regenerates:
  - `artifacts/data/*.csv|json`
  - `artifacts/figures/*.png`
  - `artifacts/tables/*.tex`
  - representative case sub-bundles under `artifacts/data/representatives/` and `artifacts/figures/representatives/`
- The bilingual LaTeX manuscripts are built only from those canonical outputs.

## Main mechanism claims preserved by the canonical rebuild

- one-target peak2 remains `L0R1`-dominated over `q*=0.3..0.6`
- symmetric membranes split late leak roughly evenly across top and bottom
- asymmetric membranes suppress the bottom late branch
- two-target phase counts remain `2 / 8 / 53`
- for every phase `>=1` point in the `(d,dy)` atlas, the late coarse leader remains `F_no_return`
