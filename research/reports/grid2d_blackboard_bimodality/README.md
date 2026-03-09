# 2D Blackboard-Style Bimodality Report

This report follows the figure/layout style of `research/reports/grid2d_bimodality/` and `research/reports/grid2d_reflecting_bimodality/`, and currently focuses on the single case where the start/target are placed at the wall endpoints (case Z).

Report-side scripts are thin wrappers. Core pipeline code lives in:
- `packages/vkcore/src/vkcore/grid2d/reflecting_blackboard/`
- `pipeline.py`: orchestration and case loop
- `cases_blackboard.py`: case builders and case registry
- `model.py` / `scans.py` / `plots.py` / `io.py`: shared implementation blocks
- `_blackboard_pipeline.py`: compatibility facade (re-exports only)

## Quick reproduce
From repo root:

```
source .venv/bin/activate
python3 reports/grid2d_blackboard_bimodality/code/blackboard_bimodality_pipeline.py --cases Z,S
python3 reports/grid2d_blackboard_bimodality/code/z_scan.py
cd reports/grid2d_blackboard_bimodality
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_blackboard_bimodality_cn.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_blackboard_bimodality_en.tex
```

Equivalent unified entry:
```
python3 scripts/reportctl.py run --report grid2d_blackboard_bimodality -- python3 code/blackboard_bimodality_pipeline.py --help
```

## Configs
Note: A/B/C and other exploratory configs are still in the repo but are not included in the current report.
- `research/reports/grid2d_blackboard_bimodality/config/A_geometry_U_detour.json`
- `research/reports/grid2d_blackboard_bimodality/config/B_parallel_lanes_doors.json`
- `research/reports/grid2d_blackboard_bimodality/config/C_wall_loop_conveyor.json`
- `research/reports/grid2d_blackboard_bimodality/config/Z_screenshot_wall_endpoints.json`
- `research/reports/grid2d_blackboard_bimodality/config/S_small_rect_endpoints.json`

## Screenshot scan
- `python3 reports/grid2d_blackboard_bimodality/code/screenshot_scan.py`
- Output: `research/reports/grid2d_blackboard_bimodality/outputs/screenshot_scan.json`
- Internals: implemented in `packages/vkcore/src/vkcore/grid2d/reflecting_blackboard/_screenshot_scan.py` using shared `model/scans/io` helpers.

## Outputs
- Figures: `research/reports/grid2d_blackboard_bimodality/figures/`
  - Environment: `env/case_Z_env.pdf`, `env/symbol_legend.pdf`
  - Fig3 panels (heatmaps): `fig3_panels/case_Z_fig3_panel.pdf`, `fig3_panels/channel_cartoon.pdf`
  - Paths: `paths/case_Z_paths_fast.pdf`, `paths/case_Z_paths_slow.pdf`
  - FPT: `fpt/case_Z_fpt.pdf`, `fpt/case_Z_proof.pdf`, `fpt/case_Z_diagnostic.pdf`
  - Channel mix: `channel_decomp/case_Z_channel_decomp.pdf`
- Case S figure sets follow the same naming pattern (`case_S_*`).
- Data: `research/reports/grid2d_blackboard_bimodality/data/Z_metrics.json`, `research/reports/grid2d_blackboard_bimodality/data/S_metrics.json`, `research/reports/grid2d_blackboard_bimodality/data/Z_scan.json`

## Report
- `research/reports/grid2d_blackboard_bimodality/grid2d_blackboard_bimodality_cn.pdf`
- `research/reports/grid2d_blackboard_bimodality/grid2d_blackboard_bimodality_en.pdf`
