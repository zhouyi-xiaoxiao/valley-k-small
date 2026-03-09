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

## Key outputs
- `outputs/*_fpt.csv`: per-case FPT series
- `data/scan_bimodality_K2.csv`, `data/scan_bimodality_K4.csv`
- `data/model_configs.csv`, `data/model_configs.json`
- `tables/case_configs.tex`, `tables/case_peaks.tex`
