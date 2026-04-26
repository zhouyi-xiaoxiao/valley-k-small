# ring_lazy_jump_ext_rev2

Revision v2 of the lazy jump-over extension report.

## Lineage

- **Predecessor:** `ring_lazy_jump_ext` — original extension; this revision supersedes it.
- **Predecessor's predecessor:** `ring_lazy_jump` — base bimodality study.
- **Successor:** none currently planned. Extend in-place.

## Key policy

- Figure 2 puts $f(t)$ and the windowed class bars on a **single shared axis**, replacing the earlier dual-panel layout. The three windows (peak1 / valley / peak2) are full-height stacked bars.
- Window edges are **explicit and JSON-defined**: per K, `delta = max(1, floor(delta_frac * (t2 - t1)))` with `delta_frac = 0.05`; windows = `[t1-Δ, t1+Δ]`, `[tv-Δ, tv+Δ]`, `[t2-Δ, t2+Δ]` from each K's `summary.json`.
- Threshold sensitivity (β grid, window shift, window width, MC uncertainty) is now a **first-class section** with its own figures, not buried in supplementary material.
- Bar uncertainties come from `outputs/sensitivity/mc_uncertainty.csv`; show with `--show-ci`.

## Outputs

- Manuscript: `manuscript/ring_lazy_jump_ext_rev2_{cn,en}.tex` (+ PDFs)
- Fig.1 (overlap bin-bars): `figures/fig2_overlap_binbars_beta0.01_x1350.pdf`
- Fig.1 inputs: `data/fig2_bins_bars_beta0.01.json`, `data/ft_beta0.01.csv`, schema `data/fig2_bins_bars.schema.json`
- Sensitivity: `outputs/sensitivity/{threshold_sweep,bin_shift,mc_uncertainty}_*.{csv,pdf}`

## Reproduce

Run from this directory:

```bash
make fig2          # Export inputs + plot Fig.1
make sensitivity   # Threshold + window + MC sensitivity
make pdf           # Build CN + EN manuscripts
```

Behind the scenes (see `notes/readme_rev.md` for full flag list):

```bash
python3 code/export_fig2_inputs.py --beta 0.01 --N 100 --ref-k 4 \
  --out-json data/fig2_bins_bars_beta0.01.json \
  --out-ft data/ft_beta0.01.csv
python3 code/plot_fig2_overlap_binbars.py \
  --input-json data/fig2_bins_bars_beta0.01.json \
  --ft-csv data/ft_beta0.01.csv \
  --out figures/fig2_overlap_binbars_beta0.01_x1350.pdf \
  --xlim 1 1350
```

If real MC outputs (`outputs/mc_beta_sweep_N100/cases/*.{cond_by_t.csv,exact.npz,summary.json}`) are absent, the export script generates runnable example data — replace by rerunning after producing real cases.

## Companion docs

- `notes/readme_rev.md` — full workflow + flag reference
- `notes/changelog_v2.md` — v1 → v2 diff
- `notes/revision_notes.md` — 10 numbered "issue → fix → verification" records driving this revision
