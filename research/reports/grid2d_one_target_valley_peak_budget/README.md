# grid2d_one_target_valley_peak_budget

Short companion note for the symmetric one-target membrane baseline, focused on:
- keeping the configuration plot together with a merged two-curve overview and enlarged co-located budget bars
- comparing the valley window against `peak2` through exact region-level time budgets
- compressing the old `\tau_out` / `\tau_mem` timing summaries into direct valley-vs-peak2 comparisons while bringing `peak1` back as a control

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report grid2d_one_target_valley_peak_budget -- \
  .venv/bin/python code/build_valley_peak_budget_report.py
python3 scripts/reportctl.py build --report grid2d_one_target_valley_peak_budget --lang cn
python3 scripts/reportctl.py build --report grid2d_one_target_valley_peak_budget --lang en
```

## Canonical Paths
- Figures: `research/reports/grid2d_one_target_valley_peak_budget/artifacts/figures/`
- Data: `research/reports/grid2d_one_target_valley_peak_budget/artifacts/data/`
- PDFs:
  - `research/reports/grid2d_one_target_valley_peak_budget/manuscript/grid2d_one_target_valley_peak_budget_cn.pdf`
  - `research/reports/grid2d_one_target_valley_peak_budget/manuscript/grid2d_one_target_valley_peak_budget_en.pdf`

## Notes
- This report is a short follow-up to `grid2d_one_target_exit_timing`.
- The overview now keeps only `\kappa=0` and `\kappa=0.0040` in one merged curve panel.
- The overview figure now uses a left geometry panel plus a right merged comparison panel: representative curves and enlarged valley / `peak2` stacked budget bars share the same time axis, with `target funnel` folded into a merged outer/right-side share.
- The new figures add exact outside-time budgets and membrane post-crossing time-budget proxies, with `peak1` restored as a control in the timing panels.
