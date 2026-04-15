# 2D Reflecting-Boundary Bimodality Report

This report is the canonical reflecting-boundary counterpart of `grid2d_bimodality`. Shared implementation lives under `packages/vkcore/src/vkcore/grid2d/reflecting_blackboard/`.

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report grid2d_reflecting_bimodality -- \
  python3 code/reflecting_bimodality_pipeline.py
python3 scripts/reportctl.py build --report grid2d_reflecting_bimodality --lang cn
python3 scripts/reportctl.py build --report grid2d_reflecting_bimodality --lang en
```

## Canonical Paths
- Config summary: `research/reports/grid2d_reflecting_bimodality/code/config/cases_reflecting_summary.json`
- Full configs: `research/reports/grid2d_reflecting_bimodality/code/config/`
- Metrics: `research/reports/grid2d_reflecting_bimodality/artifacts/data/*_metrics.json`
- Figures: `research/reports/grid2d_reflecting_bimodality/artifacts/figures/`
- PDFs: `research/reports/grid2d_reflecting_bimodality/manuscript/grid2d_reflecting_bimodality_cn.pdf`, `research/reports/grid2d_reflecting_bimodality/manuscript/grid2d_reflecting_bimodality_en.pdf`

## Notes
- Representative cases in the manuscript are R1/R7/C3/R6/NB4/NB5/S1/S2.
- Public-facing references should use the canonical `artifacts/` and `manuscript/` paths rather than compatibility links like `data/` or `figures/`.
