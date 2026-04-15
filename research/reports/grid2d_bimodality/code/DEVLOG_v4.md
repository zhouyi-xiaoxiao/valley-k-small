# v4 visual audit (post v3 baseline)

Baseline command (v3):

```
MPLCONFIGDIR=reports/grid2d_bimodality/.mplcache \
python3 reports/grid2d_bimodality/code/bimodality_2d_pipeline.py \
  --mc-samples 5000 --t-max 3000 --t-max-aw 2000 --t-max-scan 1500 --fpt-method both \
  --fig-version v3 --plot-style fig3 --png-dpi 300 --mc-bin-width 10 --log-eps 1e-14
```

Observed issues in `figures/v3/` (to fix in v4):
- Environment schematic lacks a stable symbol system (global bias arrow too small, door/barrier not visually distinct).
- Start/target markers are small and not carried consistently into heatmaps.
- Sticky region shading is faint and not labeled; corridor cue is too subtle.
- Heatmaps do not overlay structural elements; no ROI zoom, so local features are hard to read.
- Heatmap color range/LogNorm is ok but the same symbol language is not applied across panels.
- FPT plots show MC as a noisy line; semilog spikes due to near-zero values.
- Legends are crowded, fonts small, line widths thin; not "Fig.3-like".
- Panel layout is cramped; labels/timestamps are not visually anchored.
