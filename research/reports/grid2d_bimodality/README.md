# 2D Bimodality Report

## Quick reproduce
From repo root:

```
MPLCONFIGDIR=reports/grid2d_bimodality/.mplcache \
python3 reports/grid2d_bimodality/code/bimodality_2d_pipeline.py \
  --cases-json reports/grid2d_bimodality/config/cases.json \
  --mc-samples 30000 \
  --t-max 3000 \
  --t-max-aw 3000 \
  --t-max-scan 1500 \
  --fpt-method both \
  --fig-version main \
  --plot-style fig3v5 \
  --png-dpi 800 \
  --mc-bin-width 2 \
  --mc-smooth-window 5 \
  --peak-smooth-window 9 \
  --log-eps 1e-14 \
  --tune_B 1
cd reports/grid2d_bimodality
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_bimodality_cn.tex
```

## Configs
- `research/reports/grid2d_bimodality/config/cases.json` stores the tuned A/B/C parameters and classification rules.
- `research/reports/grid2d_bimodality/config/cases_v1.json` stores the early A/B/C parameters.
- `research/reports/grid2d_bimodality/config/cases_v3.json` stores explicit geometry lists (barriers/doors/sticky/bias arrows).

## Legacy v1 reproduce (recorded)

```
MPLCONFIGDIR=reports/grid2d_bimodality/.mplcache python3 reports/grid2d_bimodality/code/bimodality_2d_pipeline.py --mc-samples 5000 --t-max 3000 --t-max-scan 1500
```

## Outputs
- Figures: `research/reports/grid2d_bimodality/figures/`
  - Environment: `env/candidate_{A,B,C}_env.pdf`, `env/symbol_legend.pdf`
  - Fig3 panels: `fig3_panels/candidate_{A,B,C}_fig3_panel.pdf`, `fig3_panels/channel_cartoon.pdf`
  - Paths: `paths/candidate_{A,B,C}_paths_fast.pdf`, `paths/candidate_{A,B,C}_paths_slow.pdf`
  - FPT: `fpt/candidate_{A,B,C}_fpt.pdf`, `fpt/bimodality_proof_B.png`, `fpt/bimodality_diagnostic_{B,C}.pdf`
  - Channel mix: `channel_decomp/candidate_{A,B,C}_channel_decomp.pdf`, `channel_decomp/candidate_B_scan.pdf`
  - Unwrapped: `unwrapped/candidate_{A,B,C}_unwrapped.pdf`
  - Gallery: `gallery.html`
- Data: `research/reports/grid2d_bimodality/data/candidate_*_metrics.json`
- Repro artifacts: `candidate_*_aw_input.npz`, `candidate_*_aw_output.npz`, `candidate_*_paths.npz`, `candidate_*_Pt_times.npz`
- Report: `research/reports/grid2d_bimodality/grid2d_bimodality_cn.pdf` (Chinese), `research/reports/grid2d_bimodality/grid2d_bimodality_en.pdf` (English)

## Key results
- Candidate A: periodic wrap-around produces bimodality with two time scales; AW/exact/MC overlap.
- Candidate B (edge corridor + mixed boundary): tuned parameters `g_x=-0.25, g_y=0.40, delta=0.70, L=8, band_rows={59,60}` give visible bimodality (t_p1=33, t_v=220, t_p2=473, h2/h1≈0.989, valley_ratio≈0.060, P_fast≈0.041).
- Candidate B scan: `outputs/scan_B.json` indicates L_min≈6 under current thresholds.
- Candidate C (door + sticky + wrap-around): minimal local-bias sites `n_min=0` already bimodal.

## AW settings
- Default: `t_max_aw=3000`, `oversample=4`, `r_pow10=12.0` (so `r^m = 10^{-12}`).
- Error metrics are recorded per candidate in `data/candidate_*_metrics.json` under the `aw` field.

## Tests
```
python3 reports/grid2d_bimodality/code/tests/test_aw_pgf.py
python3 reports/grid2d_bimodality/code/tests/test_aw_toy_v5.py
```
