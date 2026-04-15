# v5 visual audit (post v4 baseline)

Baseline command (v4):

```
MPLCONFIGDIR=reports/grid2d_bimodality/.mplcache \
python3 reports/grid2d_bimodality/code/bimodality_2d_pipeline.py \
  --mc-samples 5000 --t-max 3000 --t-max-aw 2000 --t-max-scan 1500 --fpt-method both \
  --fig-version v4 --plot-style fig3 --png-dpi 600 --mc-bin-width 10 --mc-smooth-window 5 \
  --peak-smooth-window 5 --log-eps 1e-14
```

Observed issues (from v4 output and user feedback):
- Environment figures are too small with excessive margins; labels overlap and symbol language is not dominant.
- Slow path plots are visually smeared (too many points without turning-point sparsification); fast/slow are not clearly separated.
- Heatmaps lack strong ROI handling; vmin/vmax selection leads to washed-out contrast in early times; inset grid detail is insufficient.
- FPT plots are compressed and legends overlap; not full-width or publication-grade layout.
- Mechanism clarity: no unwrapped periodic view for A/C; distances for wrap/short path not annotated.
