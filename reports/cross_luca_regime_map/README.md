# Luca Regime Map

Standalone cross-report benchmark for fixed-horizon full-FPT fairness.

## Key policy
- Main full-FPT winner metric: `Sparse exact` vs `Luca defect-reduced`.
- `Linear MFPT` is reference only.
- `Full AW` and `Dense recursion` are appendix sanity anchors only.
- Cross-family claims use ratio metric `R=sparse/luca`; do not mix absolute seconds.

## Current snapshot
- Median `R`: `0.0005`
- Luca-win probability `P(R>1)`: `0.000`
- Regime statement: No Luca winning region under fixed-T full-FPT fairness.

## Outputs
- Data: `data/manifest.csv`, `data/runtime_raw.csv`, `data/runtime_summary.json`
- Figures:
  - `figures/regime_winner_heatmap_two_target.pdf`
  - `figures/regime_winner_heatmap_reflecting.pdf`
  - `figures/regime_speedup_scatter_all.pdf`
  - `figures/regime_speedup_box_by_T.pdf`
  - `figures/regime_estimation_error_anchor.pdf`
  - `figures/regime_config_examples.pdf`
- Tables: `tables/regime_summary_by_bin.tex`, `tables/regime_anchor_baselines.tex`
- Reports: `cross_luca_regime_map_en.tex`, `cross_luca_regime_map_cn.tex` (+ compiled PDFs)

## Reproduce
```bash
.venv/bin/python reports/cross_luca_regime_map/code/build_manifest.py
.venv/bin/python reports/cross_luca_regime_map/code/run_regime_scan.py
.venv/bin/python reports/cross_luca_regime_map/code/plot_regime_figures.py
.venv/bin/python reports/cross_luca_regime_map/code/write_regime_report.py

cd reports/cross_luca_regime_map
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir cross_luca_regime_map_en.tex
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir cross_luca_regime_map_cn.tex
```
