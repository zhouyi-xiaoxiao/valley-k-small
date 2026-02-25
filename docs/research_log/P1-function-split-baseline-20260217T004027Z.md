# P1 Function Split Baseline (20260217T004027Z)

## Help Snapshots

### .venv/bin/python reports/grid2d_reflecting_bimodality/code/reflecting_bimodality_pipeline.py --help
```text
usage: reflecting_bimodality_pipeline.py [-h] [--cases CASES]
                                         [--mc-samples MC_SAMPLES]
                                         [--mc-bin-width MC_BIN_WIDTH]
                                         [--mc-smooth-window MC_SMOOTH_WINDOW]
                                         [--peak-smooth-window PEAK_SMOOTH_WINDOW]
                                         [--aw-oversample AW_OVERSAMPLE]
                                         [--aw-rpow10 AW_RPOW10]
                                         [--png-dpi PNG_DPI]
                                         [--heat-quantile HEAT_QUANTILE]
                                         [--heat-floor-ratio HEAT_FLOOR_RATIO]
                                         [--heat-view-pad HEAT_VIEW_PAD]

Reflecting-boundary bimodality pipeline

options:
  -h, --help            show this help message and exit
  --cases CASES         Comma-separated case IDs (default: all).
  --mc-samples MC_SAMPLES
  --mc-bin-width MC_BIN_WIDTH
  --mc-smooth-window MC_SMOOTH_WINDOW
  --peak-smooth-window PEAK_SMOOTH_WINDOW
  --aw-oversample AW_OVERSAMPLE
  --aw-rpow10 AW_RPOW10
  --png-dpi PNG_DPI
  --heat-quantile HEAT_QUANTILE
  --heat-floor-ratio HEAT_FLOOR_RATIO
  --heat-view-pad HEAT_VIEW_PAD
```

### .venv/bin/python reports/grid2d_blackboard_bimodality/code/blackboard_bimodality_pipeline.py --help
```text
usage: blackboard_bimodality_pipeline.py [-h] [--cases CASES]
                                         [--mc-samples MC_SAMPLES]
                                         [--mc-bin-width MC_BIN_WIDTH]
                                         [--mc-smooth-window MC_SMOOTH_WINDOW]
                                         [--peak-smooth-window PEAK_SMOOTH_WINDOW]
                                         [--aw-oversample AW_OVERSAMPLE]
                                         [--aw-rpow10 AW_RPOW10]
                                         [--png-dpi PNG_DPI]
                                         [--heat-quantile HEAT_QUANTILE]
                                         [--heat-floor-ratio HEAT_FLOOR_RATIO]
                                         [--heat-view-pad HEAT_VIEW_PAD]

Reflecting-boundary bimodality pipeline

options:
  -h, --help            show this help message and exit
  --cases CASES         Comma-separated case IDs (default: all).
  --mc-samples MC_SAMPLES
  --mc-bin-width MC_BIN_WIDTH
  --mc-smooth-window MC_SMOOTH_WINDOW
  --peak-smooth-window PEAK_SMOOTH_WINDOW
  --aw-oversample AW_OVERSAMPLE
  --aw-rpow10 AW_RPOW10
  --png-dpi PNG_DPI
  --heat-quantile HEAT_QUANTILE
  --heat-floor-ratio HEAT_FLOOR_RATIO
  --heat-view-pad HEAT_VIEW_PAD
```

### .venv/bin/python reports/grid2d_blackboard_bimodality/code/z_scan.py --help
```text
```

### .venv/bin/python reports/grid2d_blackboard_bimodality/code/screenshot_scan.py --help
```text
```

## Existing Artifact Snapshot

### Reflecting R1 files
```text
reports/grid2d_reflecting_bimodality/config/R1_dual_corridor_U_top.json
reports/grid2d_reflecting_bimodality/data/R1_metrics.json
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R1_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R1_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/env/case_R1_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_R1_env.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R1_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R1_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R1_fig3_panel_zoomtest.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R1_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R1_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R1_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R1_fpt.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R1_proof.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R1_proof.png
reports/grid2d_reflecting_bimodality/figures/paths/case_R1_paths_fast.pdf
reports/grid2d_reflecting_bimodality/figures/paths/case_R1_paths_fast.png
reports/grid2d_reflecting_bimodality/figures/paths/case_R1_paths_slow.pdf
reports/grid2d_reflecting_bimodality/figures/paths/case_R1_paths_slow.png
```

### Blackboard Z/S files
```text
reports/grid2d_blackboard_bimodality/data/S_metrics.json
reports/grid2d_blackboard_bimodality/data/Z_metrics.json
reports/grid2d_blackboard_bimodality/data/Z_scan.json
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_S_channel_decomp.pdf
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_S_channel_decomp.png
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_Z_channel_decomp.pdf
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_Z_channel_decomp.png
reports/grid2d_blackboard_bimodality/figures/env/case_S_env.pdf
reports/grid2d_blackboard_bimodality/figures/env/case_S_env.png
reports/grid2d_blackboard_bimodality/figures/env/case_Z_env.pdf
reports/grid2d_blackboard_bimodality/figures/env/case_Z_env.png
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_S_fig3_panel.pdf
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_S_fig3_panel.png
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_Z_fig3_panel.pdf
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_Z_fig3_panel.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_S_diagnostic.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_S_diagnostic.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_S_fpt.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_S_fpt.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_S_proof.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_S_proof.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_Z_diagnostic.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_Z_diagnostic.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_Z_fpt.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_Z_fpt.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_Z_proof.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_Z_proof.png
reports/grid2d_blackboard_bimodality/figures/paths/case_S_paths_fast.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_S_paths_fast.png
reports/grid2d_blackboard_bimodality/figures/paths/case_S_paths_slow.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_S_paths_slow.png
reports/grid2d_blackboard_bimodality/figures/paths/case_Z_paths_fast.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_Z_paths_fast.png
reports/grid2d_blackboard_bimodality/figures/paths/case_Z_paths_slow.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_Z_paths_slow.png
reports/grid2d_blackboard_bimodality/outputs/screenshot_scan.json
```

## Metrics Key Sets

### reports/grid2d_reflecting_bimodality/data/R1_metrics.json
```text
top_keys= ['absorption_prob', 'aw', 'case_id', 'mc', 'metrics', 'name', 'params']
metrics_keys= ['bimodal', 'early_window', 'gap', 'h1', 'h2', 'h2_over_h1', 'hv', 'late_window', 'method', 'min_gap', 'min_sep', 'passes', 'peak_ratio', 'smooth_window', 't_p1', 't_p2', 't_v', 'valley_depth', 'valley_ratio']
```

### reports/grid2d_blackboard_bimodality/data/Z_metrics.json
```text
top_keys= ['absorption_prob', 'aw', 'case_id', 'mc', 'metrics', 'name', 'params']
metrics_keys= ['bimodal', 'early_window', 'gap', 'h1', 'h2', 'h2_over_h1', 'hv', 'late_window', 'method', 'min_gap', 'min_sep', 'passes', 'peak_ratio', 'smooth_window', 't_p1', 't_p2', 't_v', 'valley_depth', 'valley_ratio']
```

### reports/grid2d_blackboard_bimodality/data/S_metrics.json
```text
top_keys= ['absorption_prob', 'aw', 'case_id', 'mc', 'metrics', 'name', 'params']
metrics_keys= ['bimodal', 'early_window', 'gap', 'h1', 'h2', 'h2_over_h1', 'hv', 'late_window', 'method', 'min_gap', 'min_sep', 'passes', 'peak_ratio', 'smooth_window', 't_p1', 't_p2', 't_v', 'valley_depth', 'valley_ratio']
```
