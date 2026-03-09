# lazy_jump_ext_rev2 (v2 revision)

## Quick start
Run commands from `reports/ring_lazy_jump_ext_rev2/`.

```
make fig2
make sensitivity
make pdf
```

## Export real inputs for Fig.1
The figure uses a standardized JSON + f(t) CSV. The export script tries to locate real outputs under
`outputs/mc_beta_sweep_N100/cases/` and derives windows for each K (K=2 and K=4). `--ref-k` controls
the legacy shared `bin_intervals` field used for overlap-mode annotations.

```
python3 code/export_fig2_inputs.py --beta 0.01 --N 100 --ref-k 4 \
  --out-json data/fig2_bins_bars_beta0.01.json \
  --out-ft data/ft_beta0.01.csv
```

If real data are missing, the script will generate runnable examples. Replace them by rerunning the
export after producing MC cases (`*.cond_by_t.csv`, `*.exact.npz`).
Add `--quiet` to silence fallback warnings (the source is still tracked in JSON meta).

Note: if `cond_by_t.csv` has masked class probabilities (NaN), the exporter falls back to the
window-level summary for that window. The source is recorded in `meta.proportion_source` inside
`data/fig2_bins_bars_beta0.01.json`.
Window definition (per K): `delta = max(1, floor(delta_frac * (t2 - t1)))` with `delta_frac=0.05`,
and windows are `[t1-Δ, t1+Δ]`, `[tv-Δ, tv+Δ]`, `[t2-Δ, t2+Δ]` from each K’s `summary.json`.

## Fig.1 generation

```
python3 code/validate_fig2_json.py --input data/fig2_bins_bars_beta0.01.json \
  --schema data/fig2_bins_bars.schema.json
python3 code/plot_fig2_overlap_binbars.py --input-json data/fig2_bins_bars_beta0.01.json \
  --ft-csv data/ft_beta0.01.csv \
  --out figures/fig2_overlap_binbars_beta0.01_x1350.pdf \
  --xlim 1 1350
```

Default output stacks panels (top $K=2$, bottom $K=4$), each co-locating $f(t)$ and windowed class bars.

To switch back to a single-axis overlay:
```
--layout overlap
```

To force a common x-axis range across panels (e.g. full $t$ range):
```
--xlim 1 4000
```

To pick which K is shown by the stacked bars (overlap layout) or which panels to keep (stacked layout):
```
--bar-k K=2   # or K=4, or both
```

The window indicators are stacked bars (four colors) aligned to each window, matching Fig.14 style.
By default the bars span the full y-axis height (set `--band-y0` / `--band-h` to change).
The report refers to this figure as Fig.1; the file name stays `fig2_overlap_binbars_beta0.01_x1350.pdf`.

To show uncertainty bars (requires `outputs/sensitivity/mc_uncertainty.csv`):

```
python3 code/plot_fig2_overlap_binbars.py --input-json data/fig2_bins_bars_beta0.01.json \
  --ft-csv data/ft_beta0.01.csv \
  --out figures/fig2_overlap_binbars_beta0.01_x1350.pdf \
  --xlim 1 1350 \
  --show-ci
```

## Sensitivity analysis

```
make sensitivity
```

Outputs:
- `outputs/sensitivity/threshold_sweep.csv`
- `outputs/sensitivity/threshold_sweep_heatmap.pdf`
- `outputs/sensitivity/bin_shift_summary.csv`
- `outputs/sensitivity/bin_shift_plot.pdf` (shift + width modes)
- `outputs/sensitivity/mc_uncertainty.csv`
- `outputs/sensitivity/mc_uncertainty_plot.pdf`
Sensitivity note: when `cond_by_t.csv` has missing class probabilities, window-level proportions
are used to impute those times so the shift/width tests are still evaluable.
Threshold sensitivity note: the heatmap aggregates all available betas found under
`outputs/mc_beta_sweep_N100/cases/` by default. To restrict betas, pass
`--beta-list 0.005,0.01,0.02` to `code/sensitivity_thresholds.py`.

## Build the v2 report

```
make pdf
```

## Notes on replacing example inputs
If the export script generated examples, replace them with real data by ensuring the following
files exist under `outputs/mc_beta_sweep_N100/cases/` for `K=2,4`:
- `*.cond_by_t.csv` (per-time class probabilities)
- `*.exact.npz` (exact f(t) array)
- `*.summary.json` (window centers/Delta)

Then rerun `make fig2` and `make sensitivity`.
