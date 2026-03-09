# 2D Reflecting-Boundary Bimodality Report

This report mirrors `reports/grid2d_bimodality/` but replaces all periodic boundaries with reflecting boundaries and adds reflecting-boundary constructions (R1--R7 plus C3), minimal-lane variants (MB1--MB3), boundary-belt cases (NB1--NB5), and soft-track cases without internal barriers (S1/S2). The pipeline produces exact recursion, AW inversion, MC overlays, heatmaps, path densities, and channel decompositions. The main text highlights R1/R7/C3/R6/NB4/NB5/S1/S2 as representative cases.

The report-side script is a thin wrapper. Core pipeline code lives in:
- `src/vkcore/grid2d/reflecting_blackboard/`
- `pipeline.py`: orchestration and case loop
- `cases_reflecting.py`: case builders and case registry
- `model.py` / `scans.py` / `plots.py` / `io.py`: shared implementation blocks
- `_reflecting_pipeline.py`: compatibility facade (re-exports only)

## Contents
- Report sources: `grid2d_reflecting_bimodality_cn.tex`, `grid2d_reflecting_bimodality_en.tex`
- Config summary: `config/cases_reflecting_summary.json`
- Metrics (peak/valley + AW + MC): `data/*_metrics.json`
- Environment schematics: `figures/env/case_*_env.pdf`, legend in `figures/env/symbol_legend.pdf`
- Heatmap panels: `figures/fig3_panels/case_*_fig3_panel.pdf`, concept sketch `figures/fig3_panels/channel_cartoon.pdf`
- Path densities: `figures/paths/case_*_paths_fast.pdf`, `figures/paths/case_*_paths_slow.pdf`
- FPT plots: `figures/fpt/case_*_fpt.pdf`, peak/valley zoom `figures/fpt/case_*_proof.pdf`, diagnostics `figures/fpt/case_*_diagnostic.pdf`
- Channel decomposition: `figures/channel_decomp/case_*_channel_decomp.pdf`
- Full configs: `config/R1_dual_corridor_U_top.json` ... `config/R7_membrane_pore_detour.json`, plus `config/C3_local_active_track_detour.json`, `config/MB1_parallel_lanes_slow_lane_is_sticky.json`, `config/MB2_parallel_lanes_slow_lane_has_10_doors.json`, `config/MB3_parallel_lanes_short_sticky_segment.json`, `config/NB1_boundary_layer_short_sticky.json`, `config/NB2_boundary_layer_sticky_strip.json`, `config/NB3_boundary_layer_sticky_strip_bias.json`, `config/NB4_perimeter_clockwise_belt.json`, `config/NB5_perimeter_clockwise_belt_gbias.json`, `config/S1_soft_two_tracks_minbarrier0.json`, `config/S2_soft_two_tracks_turn_y10.json`

## Regenerate configs/metrics/plots
```
python3 reports/grid2d_reflecting_bimodality/code/reflecting_bimodality_pipeline.py
```

Equivalent unified entry:
```
python3 scripts/reportctl.py run --report grid2d_reflecting_bimodality -- python3 code/reflecting_bimodality_pipeline.py --help
```

## Build
```
cd reports/grid2d_reflecting_bimodality
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_reflecting_bimodality_cn.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_reflecting_bimodality_en.tex
```
