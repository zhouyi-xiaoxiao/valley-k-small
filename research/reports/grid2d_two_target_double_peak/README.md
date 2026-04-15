# 2D Two-Target Double-Peak

This report studies when a reflecting-boundary 2D lazy walk with two absorbing targets develops a visible double peak. The retired local method-comparison side report is no longer part of the active public surface.

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report grid2d_two_target_double_peak -- \
  python3 code/two_target_2d_report.py
python3 scripts/reportctl.py build --report grid2d_two_target_double_peak --lang cn
python3 scripts/reportctl.py build --report grid2d_two_target_double_peak --lang en
```

## Canonical Paths
- Data summary: `research/reports/grid2d_two_target_double_peak/artifacts/data/case_summary.json`
- Sparse external set summary: `research/reports/grid2d_two_target_double_peak/artifacts/data/sparse_testset_results.json`
- Parameter scans: `research/reports/grid2d_two_target_double_peak/artifacts/data/scan_w2_skip2.csv`, `research/reports/grid2d_two_target_double_peak/artifacts/data/scan_w2_skip2.json`
- Per-case time series: `research/reports/grid2d_two_target_double_peak/artifacts/outputs/C*_fpt.csv`
- Figures: `research/reports/grid2d_two_target_double_peak/artifacts/figures/`
- Tables: `research/reports/grid2d_two_target_double_peak/artifacts/tables/`
- PDFs: `research/reports/grid2d_two_target_double_peak/manuscript/grid2d_two_target_double_peak_cn.pdf`, `research/reports/grid2d_two_target_double_peak/manuscript/grid2d_two_target_double_peak_en.pdf`

## Notes
- Cases C1-C4 are the main manuscript configurations.
- Repository-wide computational comparison now lives only in `research/reports/luca_vs_recursion_unified_benchmark/`.
