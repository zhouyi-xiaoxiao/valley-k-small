# grid2d_one_target_window_measures

Explainer report for the symmetric one-target membrane baseline:
- what the window-conditioned occupancy share actually measures
- why `target_funnel` can have low occupancy share but `100%` ever-visit probability
- how the exact quantities relate to Monte Carlo estimators

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report grid2d_one_target_window_measures -- \
  python3 code/build_window_measures_report.py
python3 scripts/reportctl.py build --report grid2d_one_target_window_measures --lang cn
python3 scripts/reportctl.py build --report grid2d_one_target_window_measures --lang en
```

## Canonical Paths
- Figures: `research/reports/grid2d_one_target_window_measures/artifacts/figures/`
- Tables: `research/reports/grid2d_one_target_window_measures/artifacts/tables/`
- Data: `research/reports/grid2d_one_target_window_measures/artifacts/data/`
- PDFs:
  - `research/reports/grid2d_one_target_window_measures/manuscript/grid2d_one_target_window_measures_cn.pdf`
  - `research/reports/grid2d_one_target_window_measures/manuscript/grid2d_one_target_window_measures_en.pdf`

## Notes
- This report is an explanatory companion to `grid2d_one_two_target_gating`.
- It reuses the symmetric single-target baseline and rebuilds the figures from repo-native code.
- The Chinese and English manuscripts are kept in sync and use the same generated figures/tables.
