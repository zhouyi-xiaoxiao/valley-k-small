# grid2d_one_target_exit_timing

Companion report for the symmetric one-target membrane baseline, focused on:
- how the double-peak structure changes under symmetric membrane permeability continuation
- when walkers first leave the corridor band
- when walkers first cross the membrane to the outside
- how exact early/late/no-exit timing splits differ between `\tau_out` and `\tau_mem`

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report grid2d_one_target_exit_timing -- \
  ../../../.venv/bin/python code/build_exit_timing_report.py
python3 scripts/reportctl.py build --report grid2d_one_target_exit_timing --lang cn
python3 scripts/reportctl.py build --report grid2d_one_target_exit_timing --lang en
```

## Canonical Paths
- Figures: `research/reports/grid2d_one_target_exit_timing/artifacts/figures/`
- Tables: `research/reports/grid2d_one_target_exit_timing/artifacts/tables/`
- Data: `research/reports/grid2d_one_target_exit_timing/artifacts/data/`
- PDFs:
  - `research/reports/grid2d_one_target_exit_timing/manuscript/grid2d_one_target_exit_timing_cn.pdf`
  - `research/reports/grid2d_one_target_exit_timing/manuscript/grid2d_one_target_exit_timing_en.pdf`

## Notes
- This report is a mechanism-oriented companion to `grid2d_one_target_window_measures`.
- It keeps the same symmetric one-target geometry and corridor-only soft bias, then scans the symmetric membrane permeability `\kappa`.
- The Chinese and English manuscripts are kept in sync and use the same generated figures, tables, and scan outputs.
