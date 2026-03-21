# Research Reports

所有报告统一遵循同一 v2 骨架：

```text
research/reports/<report_id>/
  README.md
  code/
  notes/
  manuscript/
    <report_id>_cn.tex | <report_id>_en.tex | <report_id>.tex
    <report_id>_cn.pdf | <report_id>_en.pdf | <report_id>.pdf
    inputs/
    sections/
    extras/
    build/
  artifacts/
    figures/
    tables/
    data/
    outputs/
```

## Rules
- `code/` 存放报告入口脚本
- `notes/` 存放说明、复现笔记与补充材料
- `manuscript/` 存放主文稿、补充文稿与 LaTeX build 目录
- `artifacts/` 存放 figures、tables、data、outputs
- 报告根目录只允许 `README.md` 作为顶层常规文件
- 报告根目录不再保留 loose `*.tex` or `*.pdf`
- 对外 README / 手册中的命令统一优先写成 `python3 scripts/reportctl.py run/build ...`
- 对外 README / 手册中的路径统一显式写成 `research/reports/<report_id>/manuscript/...` 或 `research/reports/<report_id>/artifacts/...`

## Active Report IDs
- `ring_lazy_jump`
- `ring_lazy_jump_ext`
- `ring_lazy_jump_ext_rev2`
- `ring_lazy_flux`
- `ring_valley`
- `ring_valley_dst`
- `ring_deriv_k2`
- `ring_two_target`
- `ring_two_walker_encounter_shortcut`
- `grid2d_bimodality`
- `grid2d_reflecting_bimodality`
- `grid2d_blackboard_bimodality`
- `grid2d_two_target_double_peak`
- `grid2d_two_walker_encounter_shortcut`
- `grid2d_rect_bimodality`
- `grid2d_membrane_near_target`
- `grid2d_one_two_target_gating`
- `luca_vs_recursion_unified_benchmark`

## Computational Comparison Line
- The only active computational-method comparison report is `luca_vs_recursion_unified_benchmark`.
- Scientific reports may still contain brief local comparison remarks, but no separate comparison PDFs or method-comparison notes remain active elsewhere.

## Current Mechanism Integration
- `grid2d_one_two_target_gating` is the canonical repo-native integration point for the March 16 gating line.
- Its raw zips and PDFs remain archived under `notes/source_imports/2026-03-16/raw/`, but the report build now regenerates figures, tables, scans, representative-case bundles, and PDFs from shared code under `packages/vkcore/src/vkcore/grid2d/one_two_target_gating/`; the one-target main text now fixes a shared symmetric baseline, separates top/bottom asymmetry from same-membrane directional asymmetry, uses gate-free rollback `L0R0/L0R1/L1R0/L1R1` as the main discrete mechanism, keeps the real-set x-gate `G_{X_g}={x=X_g}` only as a timing anchor for `N/P/Q`, and keeps committor only as appendix control.

## Common Commands
- `python3 scripts/reportctl.py list`
- `python3 scripts/reportctl.py resolve --report ring_valley_dst`
- `python3 scripts/reportctl.py run --report ring_valley_dst -- python3 code/bimodality_flux_scan.py --help`
- `python3 scripts/reportctl.py build --report ring_valley_dst --lang cn`
