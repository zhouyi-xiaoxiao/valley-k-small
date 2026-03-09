# 2D Rectangle Bimodality (Two-Target + One-Target Corridor)

This report studies when **non-square rectangular** 2D domains can produce a visible **double peak** in first-passage time
(FPT) distributions, in two settings:

1. **Two targets** placed near the two ends of the rectangle, with a short/long path design to induce two timescales.
   The default build uses **straight one-cell-thick biased streams** on the midline (`--tt-style straight`), so arrows do not turn.
2. **One target** with a **reflecting-wall corridor** and local bias inside the corridor, optionally with global bias outside.

## Outputs
- Main report sources: `grid2d_rect_bimodality_cn.tex`, `grid2d_rect_bimodality_en.tex`
- Main report PDFs: `grid2d_rect_bimodality_cn.pdf`, `grid2d_rect_bimodality_en.pdf`
- Figures: `figures/*.pdf`
- Tables: `tables/*.tex`
- Scan data: `data/*.csv`, `data/*.json`

## Reproduce
```bash
# from repo root (once)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 reports/grid2d_rect_bimodality/code/rect_bimodality_report.py --quick
python3 reports/grid2d_rect_bimodality/code/rect_bimodality_report.py

cd reports/grid2d_rect_bimodality
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_rect_bimodality_cn.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_rect_bimodality_en.tex
```
