# Phase-v2 Rules

This note is the repo-native derivative of the March 16 `gating_game` memo.

## Core rules

For the canonical report we keep the phase-v2 logic intentionally small:

1. `find_two_peaks` must still identify two credible peaks.
2. A mechanism-aware separation score must split the fast and slow branches in time.

For one-target membranes, the recommended v2 split is:
- `fast = C00`
- `slow = C10 + C01 + C11`

For no-corridor two-target cases, the v2 split is:
- `fast = near branch`
- `slow = far branch`

The shared separation statistic is

\[
\mathrm{sep} = \frac{|t_{\mathrm{mode}}(\mathrm{slow}) - t_{\mathrm{mode}}(\mathrm{fast})|}{hw_{\mathrm{fast}} + hw_{\mathrm{slow}}}.
\]

The canonical threshold is `sep >= 1`.

## Diagnostics that remain useful but are no longer hard phase gates

- `valley/max`
- `peak_balance`
- `peak_ratio`
- `min(Pnear, Pfar)`
- `peak_margin`
- `gate_slack`

These quantities are still exported in the report artifacts because they help interpret failure modes, but they are not the main mechanism criterion anymore.

## Repo promotion

The minimal reusable implementation now lives in:
- `vkcore.grid2d.one_two_target_gating.phase_v2.GateWord`
- `vkcore.grid2d.one_two_target_gating.phase_v2.reduce_gate_word`
- `vkcore.grid2d.one_two_target_gating.phase_v2.gate_sep`
- `vkcore.grid2d.one_two_target_gating.phase_v2.classify_phase_one_target_v2`
