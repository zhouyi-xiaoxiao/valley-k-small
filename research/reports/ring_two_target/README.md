# two_target_ring

Two-target lazy ring report (Chinese + English).

## Structure
- `code/`: data generation scripts
- `outputs/`: FPT time series CSVs
- `data/`: scan tables and model configs
- `tables/`: LaTeX tables for the report
- `ring_two_target_cn.tex`: Chinese report
- `ring_two_target_en.tex`: English report
- `build/`: LaTeX aux files

## Reproduce
Run from this folder:

```
python3 code/two_target_report.py
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_two_target_cn.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_two_target_en.tex
```

For a lightweight exact target-channel decomposition check without running the scan:

```
python3 code/channel_decomposition.py
```

For the bounded small scan of representative classified shapes:

```
python3 code/run_small_scan.py
```

## Key outputs
- `outputs/*_fpt.csv`: per-case FPT series
- `artifacts/outputs/representative_channel_decomposition.csv`: representative exact
  total and target-channel first-passage series
- `artifacts/figures/representative_channel_decomposition.pdf`: readable representative
  target-channel decomposition plot
- `artifacts/data/small_scan_metrics.csv`: bounded small-scan metrics and validation
  errors for every scanned case
- `artifacts/outputs/small_scan_cases/`: representative classified case CSVs
- `artifacts/figures/small_scan/`: representative classified decomposition plots
- `notes/small_scan_summary.md`: short findings summary with guardrails
- `data/scan_bimodality_K2.csv`, `data/scan_bimodality_K4.csv`
- `data/model_configs.csv`, `data/model_configs.json`
- `tables/case_configs.tex`, `tables/case_peaks.tex`
