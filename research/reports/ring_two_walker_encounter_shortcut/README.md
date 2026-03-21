# 1D Ring Two-Walker Encounter With Shortcut

This report covers the 1D ring encounter line for two independent lazy walkers, including the fixed-site companion study and the shortcut scan.

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report ring_two_walker_encounter_shortcut -- \
  python3 code/two_walker_ring_encounter_report.py
python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang cn
python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en
```

## Continuous Optimize Loop
```bash
python3 scripts/reportctl.py run --report ring_two_walker_encounter_shortcut -- \
  python3 code/continuous_optimize_loop.py --rounds 2
```

## Canonical Paths
- PDFs: `research/reports/ring_two_walker_encounter_shortcut/manuscript/ring_two_walker_encounter_shortcut_cn.pdf`, `research/reports/ring_two_walker_encounter_shortcut/manuscript/ring_two_walker_encounter_shortcut_en.pdf`
- Reviewer addendum archive: `research/reports/ring_two_walker_encounter_shortcut/manuscript/inputs/reviewer_addendum/`
- Data: `research/reports/ring_two_walker_encounter_shortcut/artifacts/data/`
- Tables: `research/reports/ring_two_walker_encounter_shortcut/artifacts/tables/`
- Figures: `research/reports/ring_two_walker_encounter_shortcut/artifacts/figures/`
- Loop and consistency outputs: `research/reports/ring_two_walker_encounter_shortcut/artifacts/outputs/`

## Notes
- Each optimize round regenerates code outputs, rebuilds CN/EN PDFs, runs consistency checks, runs report tests, and refreshes `research/docs/RESEARCH_SUMMARY.md`.
