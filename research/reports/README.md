# Research Reports

每个报告目录都遵循同一骨架：

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

说明：
- `code/` 放报告入口脚本与薄封装。
- `notes/` 放说明、复现笔记、参考材料。
- `manuscript/` 放主文稿与补充文稿。
- `artifacts/` 放图、表、数据和派生产物。
- 报告根目录不再放散落的 `*.tex` / `*.pdf`。
- 根目录上的 `data/figures/tables/outputs` 若出现，属于兼容 symlink。

## 报告索引
- `research/reports/ring_lazy_jump/`
- `research/reports/ring_lazy_jump_ext/`
- `research/reports/ring_lazy_jump_ext_rev2/`
- `research/reports/ring_lazy_flux/`
- `research/reports/ring_valley/`
- `research/reports/ring_valley_dst/`
- `research/reports/ring_deriv_k2/`
- `research/reports/ring_two_target/`
- `research/reports/ring_two_walker_encounter_shortcut/`
- `research/reports/grid2d_bimodality/`
- `research/reports/grid2d_reflecting_bimodality/`
- `research/reports/grid2d_blackboard_bimodality/`
- `research/reports/grid2d_two_target_double_peak/`
- `research/reports/grid2d_two_walker_encounter_shortcut/`
- `research/reports/grid2d_rect_bimodality/`
- `research/reports/grid2d_membrane_near_target/`
- `research/reports/cross_luca_regime_map/`

## 常用命令
- `python3 scripts/reportctl.py list`
- `python3 scripts/reportctl.py resolve --report ring_valley_dst`
- `python3 scripts/reportctl.py run --report ring_valley_dst -- python3 code/bimodality_flux_scan.py --help`
- `python3 scripts/reportctl.py build --report ring_valley_dst --lang cn`
