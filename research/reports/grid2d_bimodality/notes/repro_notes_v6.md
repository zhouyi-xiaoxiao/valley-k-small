# v6 Repro Notes (2D bimodality)

This note is historical context for the v6 plotting pass. The active public interface is still:
- `python3 scripts/reportctl.py run --report grid2d_bimodality -- ...`
- `python3 scripts/reportctl.py build --report grid2d_bimodality --lang <cn|en>`

## Historical v6 Repro Commands
1. Generate data + figures:

```bash
python3 scripts/reportctl.py run --report grid2d_bimodality -- \
  env MPLCONFIGDIR=.mplcache python3 code/bimodality_2d_pipeline.py \
  --cases-json code/config/cases_v3.json \
  --mc-samples 20000 \
  --t-max 3000 \
  --t-max-aw 3000 \
  --t-max-scan 1500 \
  --fpt-method both \
  --fig-version v6 \
  --plot-style fig3v2 \
  --png-dpi 600 \
  --mc-bin-width 5 \
  --mc-smooth-window 7 \
  --peak-smooth-window 7 \
  --log-eps 1e-14
```

2. Build the historical v6 manuscript:

```bash
python3 scripts/reportctl.py run --report grid2d_bimodality -- \
  latexmk -xelatex -interaction=nonstopmode -halt-on-error \
  -auxdir=manuscript/build -emulate-aux-dir manuscript/2d_bimodality_cn_v6.tex
```

## Canonical Pointers
1. Data + figures pipeline: `research/reports/grid2d_bimodality/code/bimodality_2d_pipeline.py`
2. Plotting helpers: `research/reports/grid2d_bimodality/code/viz/`
3. Case geometry: `research/reports/grid2d_bimodality/code/config/cases_v3.json`
4. Current canonical manuscripts: `research/reports/grid2d_bimodality/manuscript/`
5. Current canonical artifacts: `research/reports/grid2d_bimodality/artifacts/`

## Historical v6 TODO

Removed: the v6 plotting wishlist (ROI layout, multi-scale FPT, mixture artifact at `t=tmax`, Candidate B fast-channel display, heatmap LogNorm robustness, typography uniformity, PDF+PNG dual output) is no longer tracked here. Items either landed in the current `code/plot_*` modules or were abandoned in favour of the v7+ direction. Consult `git log -- code/plot_*.py` if you need to trace specific decisions.
