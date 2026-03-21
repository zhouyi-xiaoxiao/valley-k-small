# 2D Two-Walker Encounter With Shortcut

This report extends the bimodality workflow to two independent walkers on a reflecting 2D lattice with directed shortcuts.

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report grid2d_two_walker_encounter_shortcut -- \
  python3 code/two_walker_encounter_report.py
python3 scripts/reportctl.py build --report grid2d_two_walker_encounter_shortcut --lang cn
python3 scripts/reportctl.py build --report grid2d_two_walker_encounter_shortcut --lang en
```

## Canonical Paths
- PDFs: `research/reports/grid2d_two_walker_encounter_shortcut/manuscript/grid2d_two_walker_encounter_shortcut_cn.pdf`, `research/reports/grid2d_two_walker_encounter_shortcut/manuscript/grid2d_two_walker_encounter_shortcut_en.pdf`
- Data: `research/reports/grid2d_two_walker_encounter_shortcut/artifacts/data/a1a8_validation.json`, `research/reports/grid2d_two_walker_encounter_shortcut/artifacts/data/encounter_beta_scan.csv`, `research/reports/grid2d_two_walker_encounter_shortcut/artifacts/data/case_summary.json`
- Tables: `research/reports/grid2d_two_walker_encounter_shortcut/artifacts/tables/`
- Figures: `research/reports/grid2d_two_walker_encounter_shortcut/artifacts/figures/`

## Notes
- The report keeps the appendix Eq. (A1) vs Eq. (A8) verification alongside the main encounter scan.
- Public-facing references should use `artifacts/` and `manuscript/`, not report-root compatibility links.
