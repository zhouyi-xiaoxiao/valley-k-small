# lazy_jump_ext

This extension folder is isolated from the original report. All new scripts, data, figures, and PDFs live here under `research/reports/ring_lazy_jump_ext/`.

## Structure
- `code/`: pipelines and sweep scripts (beta/N scans, MC class sweeps, tail diagnostics)
- `data/`, `figures/`, `tables/`: report assets and case-level outputs
- `outputs/`: generated CSV/PNG/PDF outputs from the sweeps
- `sections/`: LaTeX section files for the bilingual extension
- `ring_lazy_jump_ext_cn.tex`, `ring_lazy_jump_ext_en.tex`: main Chinese/English report sources
- `build/`: LaTeX auxiliary files

## Reproduce the outputs
Run all commands from this folder.

### 1) Beta sweep (exact AW)
```
python code/beta_sweep_peaks_tail.py \
  --N 100 --Ks 2 4 --q 0.6666666667 --rho 1.0 --mode lazy_selfloop \
  --beta-min 0.0 --beta-max 0.2 --beta-num 21 \
  --outdir outputs/beta_sweep_N100
```

### 2) Choose beta
```
python code/choose_beta.py \
  --csv outputs/beta_sweep_N100/beta_sweep_metrics_N100.csv \
  --Ks 2 4 --macro_ratio 10 --hv_over_max 0.6 --min_h2_over_h1 0.05 \
  --fallback_beta 0.02 \
  --out outputs/selected_beta.txt
```

### 3) Fix beta and sweep N (exact AW)
```
python code/N_sweep_peaks_tail.py \
  --K 2 4 --beta 0.01 --q 0.6666666667 --rho 1.0 --mode lazy_selfloop \
  --N-min 50 --N-max 300 --N-step 2 --only-even \
  --outdir outputs/N_sweep_beta_selected
```

### 4) MC beta sweep (class composition)
```
python code/mc_sweep_beta_classes.py \
  --N 100 --Ks 2 4 --q 0.6666666667 --rho 1.0 --mode lazy_selfloop \
  --betas 0.001 0.005 0.01 0.02 0.03 \
  --n-walkers 200000 --seed 0 \
  --outdir outputs/mc_beta_sweep_N100
```

### 5) MC N sweep (fixed beta)
```
python code/mc_sweep_N_classes.py \
  --beta 0.01 --Ks 2 4 --q 0.6666666667 --rho 1.0 --mode lazy_selfloop \
  --N-min 50 --N-max 300 --N-step 10 --only-even \
  --n-walkers 200000 --seed 0 \
  --outdir outputs/mc_N_sweep_beta_selected
```

### 6) Tail diagnostics
```
python code/tail_diagnostics.py \
  --N 100 --K 2 --beta 0.01 --q 0.6666666667 --rho 1.0 --mode lazy_selfloop \
  --max-steps-aw 12000 --outdir outputs/tail_diag
python code/tail_diagnostics.py \
  --N 100 --K 4 --beta 0.01 --q 0.6666666667 --rho 1.0 --mode lazy_selfloop \
  --max-steps-aw 12000 --outdir outputs/tail_diag
```

### 7) Optional: overlay all-beta exact curves
```
python code/plot_aw_all_betas.py \
  --N 100 --Ks 2 4 --q 0.6666666667 --rho 1.0 --mode lazy_selfloop \
  --beta-min 0.0 --beta-max 0.2 --beta-num 21 \
  --out outputs/beta_sweep_N100/aw_all_betas_N100.png
```

## Build the PDFs
```
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_jump_ext_cn.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_jump_ext_en.tex
```

## Recommended parameter defaults
- `N=100`, `K={2,4}`, `q=2/3`, `rho=1.0`, `mode=lazy_selfloop`
- beta grid: `beta-min=0.0`, `beta-max=0.2`, `beta-num=21`
- N grid: `N-min=50`, `N-max=300`, `N-step=2` (exact); `N-step=10` (MC)
- MC: `n-walkers=200000`, `seed=0`
- AW: `max-steps-aw=4000` (sweep), `max-steps-aw=12000` (tail diagnostics)

## Expected key outputs
- `outputs/beta_sweep_N100/beta_sweep_metrics_N100.csv`
- `outputs/beta_sweep_N100/peak_heights_vs_beta_N100.png`
- `outputs/beta_sweep_N100/peak_times_vs_beta_N100.png`
- `outputs/beta_sweep_N100/tail_gamma_vs_beta_N100.png`
- `outputs/beta_sweep_N100/aw_all_betas_N100.png`
- `outputs/N_sweep_beta_selected/N_sweep_metrics_beta0.01.csv`
- `outputs/mc_beta_sweep_N100/mc_beta_sweep_classes_N100.csv`
- `outputs/mc_N_sweep_beta_selected/mc_N_sweep_classes_beta0.01.csv`
- `ring_lazy_jump_ext_cn.pdf`, `ring_lazy_jump_ext_en.pdf`
