# 1D Ring Two-Walker Encounter With Shortcut

This report focuses on **1D ring encounter** for two independent lazy walkers.
It contains:

- Robust numerical verification of appendix Eq. (A1) == Eq. (A8).
- Exact first-encounter computation on 1D ring with directed shortcut.
- Shortcut scan showing when encounter FPT becomes double-peaked (under fixed diagnostic window).
- Fixed-site encounter companion study under drift-pair scan (K=2 parity coarse-grained diagnostics).

## Reproduce

```bash
.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py

cd reports/ring_two_walker_encounter_shortcut
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_two_walker_encounter_shortcut_cn.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_two_walker_encounter_shortcut_en.tex
```

## Continuous Optimize Loop

```bash
cd reports/ring_two_walker_encounter_shortcut
../../.venv/bin/python code/continuous_optimize_loop.py --rounds 2
```

Per round:
- rerun report code generation,
- rebuild CN + EN PDFs,
- run `py_compile`,
- run `code/check_encounter_consistency.py` (including table/snippet vs JSON/CSV consistency),
- run `pytest -q tests/test_ring_two_walker_encounter_shortcut.py`,
- refresh `research/docs/RESEARCH_SUMMARY.md` via `python3 scripts/reportctl.py summary`,
- if LaTeX fails, auto-clean (`latexmk -C`) and retry once.

## Outputs

- PDFs: `ring_two_walker_encounter_shortcut_{cn,en}.pdf`
- Reviewer addendum archive (for traceability):
  - `inputs/reviewer_addendum/addendum_beta_scan_compare_old_new.csv`
  - `inputs/reviewer_addendum/addendum_beta_scan_timescale_detector.csv`
  - `inputs/reviewer_addendum/addendum_onset_scaling.png`
  - `inputs/reviewer_addendum/addendum_peakcount_vs_beta.png`
  - `inputs/reviewer_addendum/addendum_t2_old_vs_new.png`
  - `inputs/reviewer_addendum/addendum_recompute_encounter_beta_scan.py`
  - `inputs/reviewer_addendum/ring_two_walker_encounter_shortcut_addendum_cn.pdf`
- Data:
  - `data/a1a8_validation.json`
  - `data/encounter_beta_scan.csv`
  - `data/encounter_beta_scan_timescale.csv`
  - `data/encounter_beta_scan_compare_detectors.csv`
  - `data/encounter_onset_refine.csv`
  - `data/encounter_onset_sensitivity.csv`
  - `data/encounter_onset_agreement.csv`
  - `data/encounter_onset_n_scan.csv`
  - `data/case_summary.json`
  - `data/fixedsite_drift_scan.csv`
  - `data/fixedsite_summary.json`
- Tables:
  - `tables/a1a8_test_table.tex`
  - `tables/encounter_scan_table.tex`
  - `tables/encounter_n_scan_table.tex`
  - `tables/encounter_key_metrics.tex`
  - `tables/encounter_shortcut_rep_case.tex`
  - `tables/fixedsite_example_table.tex`
  - `tables/fixedsite_phase_summary.tex`
  - `tables/fixedsite_parity_note_cn.tex`
  - `tables/fixedsite_parity_note_en.tex`
  - `tables/encounter_consistency_summary_cn.tex`
  - `tables/encounter_consistency_summary_en.tex`
  - `tables/encounter_nscan_summary_cn.tex`
  - `tables/encounter_nscan_summary_en.tex`
- Figures:
  - `figures/a1a8_contour_convergence.pdf`
  - `figures/a1a8_radius_invariance.pdf`
  - `figures/encounter_ring_geometry.pdf`
  - `figures/encounter_shortcut_rep_case.pdf`
  - `figures/encounter_fpt_overlay.pdf`
  - `figures/encounter_shortcut_decomp.pdf`
  - `figures/encounter_shortcut_share.pdf`
  - `figures/encounter_mass_balance.pdf`
  - `figures/encounter_beta_phase.pdf`
  - `figures/encounter_peakcount_vs_beta.pdf`
  - `figures/encounter_t2_old_vs_new.pdf`
  - `figures/encounter_onset_refine.pdf`
  - `figures/encounter_onset_sensitivity.pdf`
  - `figures/encounter_onset_agreement.pdf`
  - `figures/encounter_onset_n_scan.pdf`
  - `figures/encounter_onset_scaling.pdf`
  - `figures/encounter_onset_source_window.pdf`
  - `figures/encounter_fixedsite_examples.pdf`
  - `figures/encounter_fixedsite_parity_compare.pdf`
  - `figures/encounter_fixedsite_gphase.pdf`
- Checks/loop artifacts:
  - `outputs/consistency_check.json`
  - `outputs/loop/summary.json`
