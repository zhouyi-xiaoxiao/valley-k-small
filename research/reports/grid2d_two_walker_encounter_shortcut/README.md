# 2D Two-Walker Encounter With Shortcut

This report extends the existing bimodality workflow to **two walkers** on a 2D reflecting lattice with directed shortcuts.
It includes:

- A robust numerical routine verifying equivalence between appendix Eq. (A1) and Eq. (A8).
- Exact time-domain first-encounter computation for two independent walkers.
- A shortcut-strength scan showing when the encounter FPT becomes double-peaked.

## Reproduce

```bash
python3 reports/grid2d_two_walker_encounter_shortcut/code/two_walker_encounter_report.py

cd reports/grid2d_two_walker_encounter_shortcut
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_two_walker_encounter_shortcut_cn.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_two_walker_encounter_shortcut_en.tex
```

## Outputs

- Main PDFs:
  - `grid2d_two_walker_encounter_shortcut_cn.pdf`
  - `grid2d_two_walker_encounter_shortcut_en.pdf`
- Data:
  - `data/a1a8_validation.json`
  - `data/encounter_beta_scan.csv`
  - `data/case_summary.json`
- Tables:
  - `tables/a1a8_test_table.tex`
  - `tables/encounter_scan_table.tex`
- Figures:
  - `figures/a1a8_contour_convergence.pdf`
  - `figures/a1a8_radius_invariance.pdf`
  - `figures/encounter_geometry.pdf`
  - `figures/encounter_fpt_overlay.pdf`
  - `figures/encounter_shortcut_decomp.pdf`
  - `figures/encounter_beta_phase.pdf`
