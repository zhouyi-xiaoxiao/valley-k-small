# grid2d_membrane_near_target

New 2D extension report covering:
- one-target corridor with symmetric/asymmetric semi-permeable membranes;
- no-corridor two-target setting with one target near the start.

## Generate data and figures
```bash
cd reports/grid2d_membrane_near_target
../../.venv/bin/python code/membrane_near_target_report.py
```

## Build PDFs
Chinese:
```bash
cd reports/grid2d_membrane_near_target
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_membrane_near_target_cn.tex
```

English:
```bash
cd reports/grid2d_membrane_near_target
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_membrane_near_target_en.tex
```

## Key outputs
- `data/summary.json`
- `data/two_target_candidate_scans.csv`
- `figures/membrane_*`
- `figures/two_target_*`
- `tables/*.tex`
- `outputs/*_fpt.csv`
