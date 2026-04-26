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

## Active Report IDs

The list below is the **canonical order** — `report_registry.yaml`, `RESEARCH_SUMMARY.md` AUTO-INDEX, and downstream consumers all follow it (Ring → Grid2D → Cross).

### Ring series

- `ring_lazy_jump`
- `ring_lazy_jump_ext`
- `ring_lazy_jump_ext_rev2`
- `ring_lazy_flux`
- `ring_valley`
- `ring_valley_dst`
- `ring_deriv_k2`
- `ring_two_target`
- `ring_two_walker_encounter_shortcut`

### Grid2D series

- `grid2d_bimodality`
- `grid2d_reflecting_bimodality`
- `grid2d_blackboard_bimodality`
- `grid2d_two_target_double_peak`
- `grid2d_two_walker_encounter_shortcut`
- `grid2d_rect_bimodality`
- `grid2d_membrane_near_target`

### Cross-method

- `cross_luca_regime_map`

## WIP Scaffold Report IDs

Scope defined, no manuscript yet (registered with `status: wip` in `report_registry.yaml`). Promote to `status: active` when the first `.tex` lands.

- `grid2d_one_target_base` — mother report for the one_target sub-series
- `grid2d_one_target_exit_timing`
- `grid2d_one_target_valley_peak_budget`
- `grid2d_one_target_window_measures`
- `grid2d_one_two_target_gating`
- `exact_recursion_method_guide`

## Common Commands
- `python3 scripts/reportctl.py list`
- `python3 scripts/reportctl.py resolve --report ring_valley_dst`
- `python3 scripts/reportctl.py run --report ring_valley_dst -- python3 code/bimodality_flux_scan.py --help`
- `python3 scripts/reportctl.py build --report ring_valley_dst --lang cn`
