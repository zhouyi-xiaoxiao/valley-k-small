# grid2d_one_two_target_gating

Canonical bilingual report and repo-native subsystem for the March 16 one-/two-target gating line.

It absorbs three historical source layers into the current repository framework:
- `二维半透膜_gating_game`
- `two_target_gating_framework`
- `one_two_target_deepening_work`

The six original files remain archived under `research/reports/grid2d_one_two_target_gating/notes/source_imports/2026-03-16/raw/`, but runtime generation no longer reads those bundles.

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report grid2d_one_two_target_gating -- \
  python3 code/one_two_target_gating_report.py
python3 scripts/reportctl.py build --report grid2d_one_two_target_gating --lang cn
python3 scripts/reportctl.py build --report grid2d_one_two_target_gating --lang en
```

The canonical report run also regenerates the one-target sensitivity sweeps and the
left-open-vs-membrane exit split under `artifacts/data/sensitivity/`.

## Canonical Paths
- Shared implementation: `packages/vkcore/src/vkcore/grid2d/one_two_target_gating/`
- Data: `research/reports/grid2d_one_two_target_gating/artifacts/data/`
- Outputs: `research/reports/grid2d_one_two_target_gating/artifacts/outputs/`
- Figures: `research/reports/grid2d_one_two_target_gating/artifacts/figures/`
- Tables: `research/reports/grid2d_one_two_target_gating/artifacts/tables/`
- PDFs: `research/reports/grid2d_one_two_target_gating/manuscript/grid2d_one_two_target_gating_cn.pdf`, `research/reports/grid2d_one_two_target_gating/manuscript/grid2d_one_two_target_gating_en.pdf`

## Coverage
- one-target shared-symmetric baseline with gate-free rollback as the main discrete mechanism
- one-target gate anchor families `N/P/Q` as membrane first-leak timing diagnostics
- one-target left-open vs membrane exit decomposition for peak1 / valley / peak2
- one-target sensitivity scans over corridor width, global bias, and corridor push strengths
- full integer `X_g` scan and `(x_s, y_s)` start-position scans
- top/bottom first-leak splitting at the canonical `X_g^*`
- two-target coarse 4-family / fine 5-family decomposition
- representative geometry, branch, and family figures for `anchor`, `clear_instance`, and `near_mass_loss`
