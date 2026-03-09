# 2D Two-Target Double-Peak (Reflecting Boundary)

This report studies when a 2D lazy random walk with **two absorbing targets** can produce a visible double peak in
\(F_{n_0\to(m_1;m_2)}(t)\), under reflecting boundaries and local bias corridors.

## Model setup (fixed across cases)
- Grid: `N=31`.
- Boundary: reflecting on all four sides.
- Base walk: `q=0.2` (move), `1-q=0.8` (stay), four directions each `q/4`.
- Local bias rule (same as paper-style local bias): at biased cells, move `20%` of stay probability to one arrow direction.
- Start and targets (1-based coordinates):
  - `n0=(15,15)`
  - `m1=(22,15)`
  - `m2=(7,7)`
- Corridors:
  - Fast: `(15,15)->(22,15)` (east)
  - Slow: `(15,15)->(15,27)->(3,27)->(3,7)->(7,7)`
- Tuned knobs:
  - `w2`: slow corridor width
  - `skip2`: number of early slow-path centerline cells skipped before placing slow bias

## Cases
- C1: `w2=3`, `skip2=2`
- C2: `w2=2`, `skip2=1`
- C3: `w2=2`, `skip2=0`
- C4: `w2=1`, `skip2=1`

## Outputs
- Main report sources: `grid2d_two_target_double_peak_cn.tex`, `grid2d_two_target_double_peak_en.tex`
- Main report PDFs: `grid2d_two_target_double_peak_cn.pdf`, `grid2d_two_target_double_peak_en.pdf`
- Method comparison reports: `method_comparison_cn.md`, `method_comparison_en.md`
- Luca-fast constructed case report: `luca_fast_case_cn.md`
- Method comparison PDFs (detailed math + complexity): `method_comparison_cn.pdf`, `method_comparison_en.pdf`
- Method comparison TeX sources: `method_comparison_cn.tex`, `method_comparison_en.tex`
- Data summary: `data/case_summary.json`
- External sparse testset summary: `data/sparse_testset_results.json`
- Method comparison data: `data/method_comparison_c1.json`, `data/method_comparison_c1_truncation.csv`
- Luca-fast case data: `data/luca_fast_case.json`
- Per-case time series: `outputs/C*_fpt.csv`
- Parameter scan data: `data/scan_w2_skip2.csv`, `data/scan_w2_skip2.json`
- Figures: `figures/*.pdf`
  - Includes `figures/case_C*_env_heatmap.pdf` (environment + three computed conditional occupancy heatmaps).
  - Includes `figures/case_C*_arrowfield.pdf` (large full local-bias arrow-field maps: one red arrow per biased cell).
  - Includes `figures/symbol_legend_panel.pdf` (script-generated symbol legend panel, aligned with all plots).
  - Includes `figures/hazard_grid.pdf` (hazard decomposition: `h=h1+h2`).
  - Includes `figures/phase_w2_skip2.pdf`, `figures/phase_sep_w2_skip2.pdf` (phase/separation maps on `(w2, skip2)` grid).
  - Includes `figures/sparse_testset_fpt_grid.pdf` (overview of sparse testset cases that actually show double peak).
  - Includes `figures/sparse_S02_config_detailed.pdf`, `figures/sparse_S02_env_heatmap.pdf` (detailed config + heatmaps for clear-double case).
  - Includes `figures/sparse_S03_config_detailed.pdf`, `figures/sparse_S03_env_heatmap.pdf` (detailed config + heatmaps for weak-double case).
  - Includes `figures/method_compare_c1_fpt_overlay.pdf`, `figures/method_compare_c1_runtime.pdf` (C1 numerical-method comparison).
  - Includes `figures/luca_fast_case_config_detailed.pdf`, `figures/luca_fast_case_fpt_overlay.pdf`, `figures/luca_fast_case_runtime.pdf` (constructed case where Luca method is fastest).
- Tables: `tables/case_metrics.tex`, `tables/case_mechanism.tex`, `tables/case_separation.tex`, `tables/sparse_testset_configs.tex`, `tables/sparse_testset_metrics.tex`

## Reproduce
```bash
.venv/bin/python reports/grid2d_two_target_double_peak/code/two_target_2d_report.py
.venv/bin/python reports/grid2d_two_target_double_peak/code/compare_numeric_methods.py
.venv/bin/python reports/grid2d_two_target_double_peak/code/luca_fast_case.py

cd reports/grid2d_two_target_double_peak
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_two_target_double_peak_cn.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_two_target_double_peak_en.tex
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir method_comparison_cn.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir method_comparison_en.tex
```
