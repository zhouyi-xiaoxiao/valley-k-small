# RESEARCH SUMMARY

最后更新: 2026-04-27

## 仓库定位
- 本仓库研究随机游走首达时间分布中的双峰、谷值、shortcut 机制与跨模型对比。
- `research/` 是研究主树，包含报告、研究文档与历史归档。
- `platform/` 承载网站、schema、自动化与 agent handoff 工具。
- `scripts/reportctl.py` 是唯一 Python CLI 入口。

## 当前主线
- Ring 系列:
  - `ring_lazy_flux`, `ring_lazy_jump*`, `ring_valley*`, `ring_two_target`, `ring_two_walker_encounter_shortcut`
  - 关注 lazy / non-lazy ring、shortcut 注入方式、峰谷判据与双峰窗口
- Grid2D 系列:
  - `grid2d_*`
  - 关注 corridor、rectangular geometry、two-target、reflecting / blackboard 等结构下的 valley 与 bimodality
- Cross-model:
  - `cross_luca_regime_map`
  - 关注跨模型 regime map、公平比较与 transfer 条件

## 建议阅读顺序
1. `research/reports/README.md`
2. `research/reports/report_registry.yaml`
3. 目标报告目录下的 `README.md`、`notes/`、`manuscript/`
4. 若需要交付或 agent 消费，再看 `platform/README.md`

## 研究与平台入口
- 人类阅读:
  - `research/docs/README.md`
  - `research/reports/README.md`
  - `platform/README.md`
- agent 入口:
  - `AGENTS.md`
  - `platform/skills/valley-k-small-continuation/`

## 常用命令
- `python3 scripts/reportctl.py list`
- `python3 scripts/reportctl.py resolve --report ring_valley_dst`
- `python3 scripts/reportctl.py build --report ring_valley_dst --lang cn`
- `python3 scripts/reportctl.py summary`
- `python3 scripts/reportctl.py doctor`
- `python3 scripts/reportctl.py agent-sync`
- `python3 scripts/reportctl.py agent-pack`

## 最新进展（手动追加）
- 仓库已收敛为 canonical 结构：`research/`、`platform/`、`packages/`、`scripts/`、`tests/`。
- 根目录兼容入口正在被移除，agent handoff 改为通过生成包输出到 `.local/deliverables/agent_pack/v1`。
- 文档、测试与 CLI 正在同步切换到单一 `reportctl` 表面。

## 自动索引（由脚本生成）
<!-- AUTO-INDEX:START -->
| report | pdfs | tex |
| --- | --- | --- |
| `research/reports/ring_lazy_jump` | `research/reports/ring_lazy_jump/manuscript/ring_lazy_jump_cn.pdf`, `research/reports/ring_lazy_jump/manuscript/ring_lazy_jump_en.pdf` | `research/reports/ring_lazy_jump/manuscript/ring_lazy_jump_cn.tex`, `research/reports/ring_lazy_jump/manuscript/ring_lazy_jump_en.tex` |
| `research/reports/ring_lazy_jump_ext` | `research/reports/ring_lazy_jump_ext/manuscript/ring_lazy_jump_ext_cn.pdf`, `research/reports/ring_lazy_jump_ext/manuscript/ring_lazy_jump_ext_en.pdf` | `research/reports/ring_lazy_jump_ext/manuscript/ring_lazy_jump_ext_cn.tex`, `research/reports/ring_lazy_jump_ext/manuscript/ring_lazy_jump_ext_en.tex` |
| `research/reports/ring_lazy_jump_ext_rev2` | `research/reports/ring_lazy_jump_ext_rev2/manuscript/ring_lazy_jump_ext_rev2_cn.pdf`, `research/reports/ring_lazy_jump_ext_rev2/manuscript/ring_lazy_jump_ext_rev2_en.pdf`, `research/reports/ring_lazy_jump_ext_rev2/manuscript/extras/fig2_overlap_binbars_beta0.01_x1350_description_en.pdf` | `research/reports/ring_lazy_jump_ext_rev2/manuscript/ring_lazy_jump_ext_rev2_cn.tex`, `research/reports/ring_lazy_jump_ext_rev2/manuscript/ring_lazy_jump_ext_rev2_en.tex` |
| `research/reports/ring_lazy_flux` | `research/reports/ring_lazy_flux/manuscript/ring_lazy_flux_cn.pdf`, `research/reports/ring_lazy_flux/manuscript/ring_lazy_flux_en.pdf` | `research/reports/ring_lazy_flux/manuscript/ring_lazy_flux_cn.tex`, `research/reports/ring_lazy_flux/manuscript/ring_lazy_flux_en.tex` |
| `research/reports/ring_valley` | `research/reports/ring_valley/manuscript/ring_valley_en.pdf` | `research/reports/ring_valley/manuscript/ring_valley_en.tex` |
| `research/reports/ring_valley_dst` | `research/reports/ring_valley_dst/manuscript/ring_valley_dst_cn.pdf`, `research/reports/ring_valley_dst/manuscript/ring_valley_dst_en.pdf` | `research/reports/ring_valley_dst/manuscript/ring_valley_dst_cn.tex`, `research/reports/ring_valley_dst/manuscript/ring_valley_dst_en.tex` |
| `research/reports/ring_deriv_k2` | `research/reports/ring_deriv_k2/manuscript/ring_deriv_k2_en.pdf`, `research/reports/ring_deriv_k2/manuscript/extras/note_k2.pdf`, `research/reports/ring_deriv_k2/manuscript/extras/note_rewire_lazy.pdf` | `research/reports/ring_deriv_k2/manuscript/ring_deriv_k2_en.tex`, `research/reports/ring_deriv_k2/manuscript/extras/note_k2.tex`, `research/reports/ring_deriv_k2/manuscript/extras/note_rewire_lazy.tex` |
| `research/reports/ring_two_target` | `research/reports/ring_two_target/manuscript/ring_two_target_cn.pdf`, `research/reports/ring_two_target/manuscript/ring_two_target_en.pdf` | `research/reports/ring_two_target/manuscript/ring_two_target_cn.tex`, `research/reports/ring_two_target/manuscript/ring_two_target_en.tex` |
| `research/reports/ring_two_walker_encounter_shortcut` | `research/reports/ring_two_walker_encounter_shortcut/manuscript/ring_two_walker_encounter_shortcut_cn.pdf`, `research/reports/ring_two_walker_encounter_shortcut/manuscript/ring_two_walker_encounter_shortcut_en.pdf` | `research/reports/ring_two_walker_encounter_shortcut/manuscript/ring_two_walker_encounter_shortcut_cn.tex`, `research/reports/ring_two_walker_encounter_shortcut/manuscript/ring_two_walker_encounter_shortcut_en.tex` |
| `research/reports/grid2d_bimodality` | `research/reports/grid2d_bimodality/manuscript/grid2d_bimodality_cn.pdf`, `research/reports/grid2d_bimodality/manuscript/grid2d_bimodality_en.pdf` | `research/reports/grid2d_bimodality/manuscript/grid2d_bimodality_cn.tex`, `research/reports/grid2d_bimodality/manuscript/grid2d_bimodality_en.tex` |
| `research/reports/grid2d_reflecting_bimodality` | `research/reports/grid2d_reflecting_bimodality/manuscript/grid2d_reflecting_bimodality_cn.pdf`, `research/reports/grid2d_reflecting_bimodality/manuscript/grid2d_reflecting_bimodality_en.pdf` | `research/reports/grid2d_reflecting_bimodality/manuscript/grid2d_reflecting_bimodality_cn.tex`, `research/reports/grid2d_reflecting_bimodality/manuscript/grid2d_reflecting_bimodality_en.tex` |
| `research/reports/grid2d_blackboard_bimodality` | `research/reports/grid2d_blackboard_bimodality/manuscript/grid2d_blackboard_bimodality_cn.pdf`, `research/reports/grid2d_blackboard_bimodality/manuscript/grid2d_blackboard_bimodality_en.pdf` | `research/reports/grid2d_blackboard_bimodality/manuscript/grid2d_blackboard_bimodality_cn.tex`, `research/reports/grid2d_blackboard_bimodality/manuscript/grid2d_blackboard_bimodality_en.tex` |
| `research/reports/grid2d_two_target_double_peak` | `research/reports/grid2d_two_target_double_peak/manuscript/grid2d_two_target_double_peak_cn.pdf`, `research/reports/grid2d_two_target_double_peak/manuscript/grid2d_two_target_double_peak_en.pdf`, `research/reports/grid2d_two_target_double_peak/manuscript/extras/method_comparison_cn.pdf`, `research/reports/grid2d_two_target_double_peak/manuscript/extras/method_comparison_en.pdf` | `research/reports/grid2d_two_target_double_peak/manuscript/grid2d_two_target_double_peak_cn.tex`, `research/reports/grid2d_two_target_double_peak/manuscript/grid2d_two_target_double_peak_en.tex`, `research/reports/grid2d_two_target_double_peak/manuscript/extras/method_comparison_cn.tex`, `research/reports/grid2d_two_target_double_peak/manuscript/extras/method_comparison_en.tex` |
| `research/reports/grid2d_two_walker_encounter_shortcut` | `research/reports/grid2d_two_walker_encounter_shortcut/manuscript/grid2d_two_walker_encounter_shortcut_cn.pdf`, `research/reports/grid2d_two_walker_encounter_shortcut/manuscript/grid2d_two_walker_encounter_shortcut_en.pdf` | `research/reports/grid2d_two_walker_encounter_shortcut/manuscript/grid2d_two_walker_encounter_shortcut_cn.tex`, `research/reports/grid2d_two_walker_encounter_shortcut/manuscript/grid2d_two_walker_encounter_shortcut_en.tex` |
| `research/reports/grid2d_rect_bimodality` | `research/reports/grid2d_rect_bimodality/manuscript/grid2d_rect_bimodality_cn.pdf`, `research/reports/grid2d_rect_bimodality/manuscript/grid2d_rect_bimodality_en.pdf` | `research/reports/grid2d_rect_bimodality/manuscript/grid2d_rect_bimodality_cn.tex`, `research/reports/grid2d_rect_bimodality/manuscript/grid2d_rect_bimodality_en.tex` |
| `research/reports/grid2d_membrane_near_target` | `research/reports/grid2d_membrane_near_target/manuscript/grid2d_membrane_near_target_cn.pdf`, `research/reports/grid2d_membrane_near_target/manuscript/grid2d_membrane_near_target_en.pdf` | `research/reports/grid2d_membrane_near_target/manuscript/grid2d_membrane_near_target_cn.tex`, `research/reports/grid2d_membrane_near_target/manuscript/grid2d_membrane_near_target_en.tex` |
| `research/reports/cross_luca_regime_map` | `research/reports/cross_luca_regime_map/manuscript/cross_luca_regime_map_cn.pdf`, `research/reports/cross_luca_regime_map/manuscript/cross_luca_regime_map_en.pdf`, `research/reports/cross_luca_regime_map/manuscript/extras/cross_luca_regime_map_cn_smoke.pdf`, `research/reports/cross_luca_regime_map/manuscript/extras/cross_luca_regime_map_en_smoke.pdf` | `research/reports/cross_luca_regime_map/manuscript/cross_luca_regime_map_cn.tex`, `research/reports/cross_luca_regime_map/manuscript/cross_luca_regime_map_en.tex`, `research/reports/cross_luca_regime_map/manuscript/extras/cross_luca_regime_map_cn_smoke.tex`, `research/reports/cross_luca_regime_map/manuscript/extras/cross_luca_regime_map_en_smoke.tex` |
| `research/reports/grid2d_one_target_base` | - | - |
| `research/reports/grid2d_one_target_exit_timing` | - | - |
| `research/reports/grid2d_one_target_valley_peak_budget` | - | - |
| `research/reports/grid2d_one_target_window_measures` | - | - |
| `research/reports/grid2d_one_two_target_gating` | - | - |
| `research/reports/exact_recursion_method_guide` | - | - |
<!-- AUTO-INDEX:END -->
