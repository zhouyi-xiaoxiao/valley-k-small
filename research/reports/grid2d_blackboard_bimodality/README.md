# 2D Blackboard-Style Bimodality Report

This report is the canonical blackboard-wall variant of the 2D bimodality line. Shared implementation lives under `packages/vkcore/src/vkcore/grid2d/reflecting_blackboard/`.

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report grid2d_blackboard_bimodality -- \
  python3 code/blackboard_bimodality_pipeline.py --cases Z,S
python3 scripts/reportctl.py run --report grid2d_blackboard_bimodality -- \
  python3 code/z_scan.py
python3 scripts/reportctl.py build --report grid2d_blackboard_bimodality --lang cn
python3 scripts/reportctl.py build --report grid2d_blackboard_bimodality --lang en
```

## Canonical Paths
- Shared pipeline package: `packages/vkcore/src/vkcore/grid2d/reflecting_blackboard/`
- Configs: `research/reports/grid2d_blackboard_bimodality/code/config/`
- Figures: `research/reports/grid2d_blackboard_bimodality/artifacts/figures/`
- Metrics: `research/reports/grid2d_blackboard_bimodality/artifacts/data/Z_metrics.json`, `research/reports/grid2d_blackboard_bimodality/artifacts/data/S_metrics.json`
- Scan output: `research/reports/grid2d_blackboard_bimodality/artifacts/data/Z_scan.json`
- Screenshot scan output: `research/reports/grid2d_blackboard_bimodality/artifacts/outputs/screenshot_scan.json`
- PDFs: `research/reports/grid2d_blackboard_bimodality/manuscript/grid2d_blackboard_bimodality_cn.pdf`, `research/reports/grid2d_blackboard_bimodality/manuscript/grid2d_blackboard_bimodality_en.pdf`

## Notes
- Case Z is the main wall-endpoint benchmark used in the manuscript.
- Case S follows the same naming convention and output layout.
- Exploratory configs remain in the repo, but public reading should start from the canonical manuscript and `artifacts/`.
