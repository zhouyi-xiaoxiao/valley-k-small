# Source Import Manifest

This report archives six original files exactly as received on 2026-03-16 under `raw/`:

1. `1_2target_机制深化整包.zip`
2. `one_two_target_深化报告_cn.pdf`
3. `二维_two_target_gating_framework_bundle.zip`
4. `two_target_gating_framework_cn.pdf`
5. `二维半透膜_gating_game_打包.zip`
6. `二维半透膜_gating_game备忘录.pdf`

## Source chain

The archived files belong to one mechanism-development chain:

1. `二维半透膜_gating_game`
   - establishes the gate language and the phase-v2 viewpoint;
   - introduces the one-target membrane four-family intuition and the two-target extension sketch.
2. `two_target_gating_framework`
   - upgrades the no-corridor two-target setting into a gate-lifted exact/MC framework;
   - shows that the late peak is dominated by `F_no_return`, not `F_rollback`.
3. `one_two_target_deepening_work`
   - unifies one-target and two-target into the same `peak1 -> valley -> peak2` mechanism narrative;
   - adds one-target `q*` sensitivity, side-aware leak splitting, the 63-point `(d,dy)` atlas, and the representative progress/side-usage summaries.

## Canonicalization rule

- `raw/` preserves the original files verbatim.
- `notes/phase_v2_rules.md` and `notes/framework_promotion.md` are the derived repo-native notes that summarize the mechanism ladder without reading the bundles at runtime.
- `artifacts/` contains the regenerated canonical figures, tables, data, representative case bundles, and verification outputs used by the new report.
- `manuscript/` is the only canonical source for the new bilingual PDFs.
- the runtime builder `code/one_two_target_gating_report.py` no longer reads zip members or copies source PDFs into outputs; it rebuilds everything from shared code under `packages/vkcore/src/vkcore/grid2d/one_two_target_gating/`.
