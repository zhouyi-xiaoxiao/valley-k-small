# P1 Split Baseline (20260217T000835Z)

## ring_valley_dst --help snapshots

### bimodality_flux_scan.py

```text
usage: bimodality_flux_scan.py [-h] [--N N] [--K K] [--n0 N0]
                               [--target TARGET] --sc-src SC_SRC [--rho RHO]
                               [--max-steps MAX_STEPS] [--eps-stop EPS_STOP]
                               [--dst [DST ...]] [--dst-min DST_MIN]
                               [--dst-max DST_MAX] [--min-height MIN_HEIGHT]
                               [--second-rel-height SECOND_REL_HEIGHT]
                               [--second-frac SECOND_FRAC] [--min-sep MIN_SEP]
                               [--require-valley] [--valley-frac VALLEY_FRAC]
                               [--n-examples N_EXAMPLES]
                               [--max-t-plot MAX_T_PLOT] [--aw-check]
                               [--run-id RUN_ID] [--no-latest]

Deterministic bimodality scan via time-domain flux (master equation), with
optional AW spot-check.

options:
  -h, --help            show this help message and exit
  --N N
  --K K
  --n0 N0
  --target TARGET
  --sc-src SC_SRC       paper shortcut source (src)
  --rho RHO
  --max-steps MAX_STEPS
  --eps-stop EPS_STOP
  --dst [DST ...]       explicit dst list (paper)
  --dst-min DST_MIN
  --dst-max DST_MAX
  --min-height MIN_HEIGHT
  --second-rel-height SECOND_REL_HEIGHT
                        Fig.3 rule: second peak must be >= this fraction of
                        the highest
  --second-frac SECOND_FRAC
  --min-sep MIN_SEP     minimum separation (t2-t1); default 2*K
  --require-valley      enable valley depth check
  --valley-frac VALLEY_FRAC
                        require valley <= frac*min(peak heights)
  --n-examples N_EXAMPLES
  --max-t-plot MAX_T_PLOT
  --aw-check            compute AW curves for example dsts and plot overlay
  --run-id RUN_ID
  --no-latest
```

### dst_shortcut_usage_mc.py

```text
usage: dst_shortcut_usage_mc.py [-h] [--N N] [--K K] [--n0 N0]
                                [--target TARGET]
                                [--shortcut-offset SHORTCUT_OFFSET]
                                [--sc-src SC_SRC] [--rho RHO]
                                [--max-steps MAX_STEPS]
                                [--delta-frac DELTA_FRAC]
                                [--min-height MIN_HEIGHT]
                                [--second-rel-height SECOND_REL_HEIGHT]
                                [--early-t2-max EARLY_T2_MAX]
                                [--run-id RUN_ID] [--dst [DST ...]]
                                [--dst-min DST_MIN] [--dst-max DST_MAX]
                                [--n-mc-dsts N_MC_DSTS] [--mc-all-bimodal]
                                [--n-walkers N_WALKERS] [--seed SEED]
                                [--batch-size BATCH_SIZE]
                                [--max-t-plot MAX_T_PLOT] [--no-latest]

Fix (N,K) and paper start/target; vary shortcut destination dst; run AW exact
+ MC crossing stats near 2nd peak.

options:
  -h, --help            show this help message and exit
  --N N
  --K K
  --n0 N0
  --target TARGET       paper target; default N/2
  --shortcut-offset SHORTCUT_OFFSET
                        paper: src = n0 + offset
  --sc-src SC_SRC       paper shortcut source; default wrap(n0+offset)
  --rho RHO
  --max-steps MAX_STEPS
  --delta-frac DELTA_FRAC
  --min-height MIN_HEIGHT
  --second-rel-height SECOND_REL_HEIGHT
  --early-t2-max EARLY_T2_MAX
                        classification threshold for early vs late second peak
                        (early: t2 <= threshold); default 2*K
  --run-id RUN_ID
  --dst [DST ...]       explicit dst list (paper)
  --dst-min DST_MIN
  --dst-max DST_MAX
  --n-mc-dsts N_MC_DSTS
                        number of representative dsts for MC (when --dst not
                        set)
  --mc-all-bimodal      run MC for all dst that satisfy the bimodal (Fig.3)
                        rule in the scan (only when --dst is not set)
  --n-walkers N_WALKERS
  --seed SEED
  --batch-size BATCH_SIZE
  --max-t-plot MAX_T_PLOT
  --no-latest
```

### second_peak_scan.py

```text
usage: second_peak_scan.py [-h] [--run-id RUN_ID] [--N N] [--K K] [--n0 N0]
                           [--target TARGET] [--rho RHO]
                           [--max-steps MAX_STEPS] [--min-height MIN_HEIGHT]
                           [--second-rel-height SECOND_REL_HEIGHT]
                           [--shortcut-offset SHORTCUT_OFFSET]
                           [--sc-src SC_SRC] [--n-examples N_EXAMPLES]
                           [--n-no-second-examples N_NO_SECOND_EXAMPLES]
                           [--no-curves] [--no-latest]
                           [--scan {shortcut-dst,target}] [--dst [DST ...]]
                           [--dst-min DST_MIN] [--dst-max DST_MAX]
                           [--dst-step DST_STEP]
                           [--target-list [TARGET_LIST ...]]
                           [--target-min TARGET_MIN] [--target-max TARGET_MAX]
                           [--target-step TARGET_STEP]
                           [--sc-dst-fixed SC_DST_FIXED]
                           [--max-t-plot MAX_T_PLOT]

Scan second-peak height while fixing start node n0, using AW inversion
(exact). Default: N=100, K=6, n0=1, target=N/2, source=n0+5, scan shortcut
destination.

options:
  -h, --help            show this help message and exit
  --run-id RUN_ID       run identifier; default is a timestamp
  --N N
  --K K
  --n0 N0               start node n0 (paper indexing, 1..N)
  --target TARGET       absorbing target (paper indexing, 1..N)
  --rho RHO
  --max-steps MAX_STEPS
  --min-height MIN_HEIGHT
  --second-rel-height SECOND_REL_HEIGHT
  --shortcut-offset SHORTCUT_OFFSET
                        source = wrap(n0 + offset)
  --sc-src SC_SRC       override shortcut source (paper)
  --n-examples N_EXAMPLES
                        number of example curves in the gallery plot
  --n-no-second-examples N_NO_SECOND_EXAMPLES
                        include up to this many non-bimodal examples
  --no-curves           do not save full A(t) curves to npz
  --no-latest           do not update top-level *_results.* and figure PDFs
  --scan {shortcut-dst,target}
                        what to scan: shortcut destination or absorbing target
  --dst [DST ...]       explicit shortcut destinations (paper)
  --dst-min DST_MIN
  --dst-max DST_MAX
  --dst-step DST_STEP
  --target-list [TARGET_LIST ...]
                        explicit targets (paper)
  --target-min TARGET_MIN
  --target-max TARGET_MAX
  --target-step TARGET_STEP
  --sc-dst-fixed SC_DST_FIXED
                        when scanning targets: keep shortcut destination fixed
                        (paper); default is wrap(target+1).
  --max-t-plot MAX_T_PLOT
                        time horizon shown in the example overlay plot
```

### second_peak_shortcut_usage_mc.py

```text
usage: second_peak_shortcut_usage_mc.py [-h] [--cases [CASES ...]]
                                        [--run-id RUN_ID]
                                        [--n-walkers N_WALKERS] [--seed SEED]
                                        [--rho RHO] [--max-steps MAX_STEPS]
                                        [--delta-frac DELTA_FRAC]
                                        [--min-height MIN_HEIGHT]
                                        [--second-rel-height SECOND_REL_HEIGHT]
                                        [--mc-n-jobs MC_N_JOBS] [--n0 N0]
                                        [--shortcut-offset SHORTCUT_OFFSET]
                                        [--max-t-plot MAX_T_PLOT]
                                        [--no-latest]

Paper-setting Monte Carlo: shortcut crossings conditioned on first-passage
times near the 2nd peak. Uses AW-inverted exact A(t) to locate peaks.

options:
  -h, --help            show this help message and exit
  --cases [CASES ...]   cases as 'N,K' (default: 50,4 70,6 100,6 100,8)
  --run-id RUN_ID
  --n-walkers N_WALKERS
  --seed SEED
  --rho RHO
  --max-steps MAX_STEPS
  --delta-frac DELTA_FRAC
                        window half-width relative to (t2-t1)
  --min-height MIN_HEIGHT
  --second-rel-height SECOND_REL_HEIGHT
  --mc-n-jobs MC_N_JOBS
  --n0 N0               paper start node n0
  --shortcut-offset SHORTCUT_OFFSET
  --max-t-plot MAX_T_PLOT
  --no-latest
```

## grid2d reflecting/blackboard pre-fix status

### reports/grid2d_reflecting_bimodality/code/reflecting_bimodality_pipeline.py --help

```text
/opt/homebrew/Cellar/python@3.12/3.12.12_2/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python: can't open file '/Users/ae23069/Library/CloudStorage/OneDrive-UniversityofBristol/Desktop/valley-k-small/reports/grid2d_reflecting_bimodality/code/reflecting_bimodality_pipeline.py --help': [Errno 2] No such file or directory
```

### reports/grid2d_blackboard_bimodality/code/blackboard_bimodality_pipeline.py --help

```text
/opt/homebrew/Cellar/python@3.12/3.12.12_2/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python: can't open file '/Users/ae23069/Library/CloudStorage/OneDrive-UniversityofBristol/Desktop/valley-k-small/reports/grid2d_blackboard_bimodality/code/blackboard_bimodality_pipeline.py --help': [Errno 2] No such file or directory
```

### reports/grid2d_blackboard_bimodality/code/z_scan.py --help

```text
/opt/homebrew/Cellar/python@3.12/3.12.12_2/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python: can't open file '/Users/ae23069/Library/CloudStorage/OneDrive-UniversityofBristol/Desktop/valley-k-small/reports/grid2d_blackboard_bimodality/code/z_scan.py --help': [Errno 2] No such file or directory
```

### reports/grid2d_blackboard_bimodality/code/screenshot_scan.py --help

```text
/opt/homebrew/Cellar/python@3.12/3.12.12_2/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python: can't open file '/Users/ae23069/Library/CloudStorage/OneDrive-UniversityofBristol/Desktop/valley-k-small/reports/grid2d_blackboard_bimodality/code/screenshot_scan.py --help': [Errno 2] No such file or directory
```

## Key latest outputs snapshot (filename-level)

### reports/ring_valley_dst/data

```text
reports/ring_valley_dst/data/second_peak_dst_shortcut_usage/latest/analysis_summary.tex
reports/ring_valley_dst/data/second_peak_dst_shortcut_usage/latest/exact_curves_selected.npz
reports/ring_valley_dst/data/second_peak_dst_shortcut_usage/latest/manifest.json
reports/ring_valley_dst/data/second_peak_dst_shortcut_usage/latest/mc.csv
reports/ring_valley_dst/data/second_peak_dst_shortcut_usage/latest/results.json
reports/ring_valley_dst/data/second_peak_dst_shortcut_usage/latest/scan.csv
reports/ring_valley_dst/data/second_peak_dst_shortcut_usage/latest/scope_summary.tex
reports/ring_valley_dst/data/second_peak_dst_shortcut_usage/latest/selected_table.tex
```

### reports/ring_valley_dst/figures

```text
reports/ring_valley_dst/figures/second_peak_dst_shortcut_usage/latest/exact_selected_cases.pdf
reports/ring_valley_dst/figures/second_peak_dst_shortcut_usage/latest/manifest.json
reports/ring_valley_dst/figures/second_peak_dst_shortcut_usage/latest/pcross_relationships.pdf
reports/ring_valley_dst/figures/second_peak_dst_shortcut_usage/latest/peak2_vs_dst.pdf
reports/ring_valley_dst/figures/second_peak_dst_shortcut_usage/latest/peak_times_vs_dst.pdf
reports/ring_valley_dst/figures/second_peak_dst_shortcut_usage/latest/second_peak_crossing_fractions.pdf
```

### reports/grid2d_reflecting_bimodality/data

```text
reports/grid2d_reflecting_bimodality/data/C3_metrics.json
reports/grid2d_reflecting_bimodality/data/MB1_metrics.json
reports/grid2d_reflecting_bimodality/data/MB2_metrics.json
reports/grid2d_reflecting_bimodality/data/MB3_metrics.json
reports/grid2d_reflecting_bimodality/data/NB1_metrics.json
reports/grid2d_reflecting_bimodality/data/NB2_metrics.json
reports/grid2d_reflecting_bimodality/data/NB3_metrics.json
reports/grid2d_reflecting_bimodality/data/NB4_metrics.json
reports/grid2d_reflecting_bimodality/data/NB5_metrics.json
reports/grid2d_reflecting_bimodality/data/R1_metrics.json
reports/grid2d_reflecting_bimodality/data/R2_metrics.json
reports/grid2d_reflecting_bimodality/data/R3_metrics.json
reports/grid2d_reflecting_bimodality/data/R4_metrics.json
reports/grid2d_reflecting_bimodality/data/R5_metrics.json
reports/grid2d_reflecting_bimodality/data/R6_metrics.json
reports/grid2d_reflecting_bimodality/data/R7_metrics.json
reports/grid2d_reflecting_bimodality/data/S1_metrics.json
reports/grid2d_reflecting_bimodality/data/S2_metrics.json
reports/grid2d_reflecting_bimodality/data/aw_exact_speed.json
```

### reports/grid2d_reflecting_bimodality/figures

```text
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_C3_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_C3_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_MB1_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_MB1_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_MB2_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_MB2_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_MB3_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_MB3_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_NB1_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_NB1_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_NB2_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_NB2_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_NB3_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_NB3_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_NB4_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_NB4_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_NB5_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_NB5_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R1_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R1_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R2_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R2_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R3_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R3_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R4_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R4_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R5_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R5_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R6_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R6_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R7_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_R7_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_S1_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_S1_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_S2_channel_decomp.pdf
reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_S2_channel_decomp.png
reports/grid2d_reflecting_bimodality/figures/env/case_C3_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_C3_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_MB1_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_MB1_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_MB2_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_MB2_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_MB3_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_MB3_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_NB1_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_NB1_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_NB2_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_NB2_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_NB3_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_NB3_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_NB4_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_NB4_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_NB5_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_NB5_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_R1_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_R1_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_R2_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_R2_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_R3_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_R3_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_R4_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_R4_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_R5_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_R5_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_R6_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_R6_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_R7_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_R7_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_S1_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_S1_env.png
reports/grid2d_reflecting_bimodality/figures/env/case_S2_env.pdf
reports/grid2d_reflecting_bimodality/figures/env/case_S2_env.png
reports/grid2d_reflecting_bimodality/figures/env/symbol_legend.pdf
reports/grid2d_reflecting_bimodality/figures/env/symbol_legend.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_C3_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_C3_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_MB1_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_MB1_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_MB2_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_MB2_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_MB3_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_MB3_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_NB1_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_NB1_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_NB2_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_NB2_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_NB3_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_NB3_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_NB4_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_NB4_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_NB5_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_NB5_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R1_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R1_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R1_fig3_panel_zoomtest.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R2_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R2_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R3_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R3_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R4_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R4_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R5_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R5_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R6_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R6_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R7_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_R7_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_S1_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_S1_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_S2_fig3_panel.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/case_S2_fig3_panel.png
reports/grid2d_reflecting_bimodality/figures/fig3_panels/channel_cartoon.pdf
reports/grid2d_reflecting_bimodality/figures/fig3_panels/channel_cartoon.png
reports/grid2d_reflecting_bimodality/figures/fpt/R1_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/R2_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/R3_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/R4_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/R5_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/R6_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_C3_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_C3_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_C3_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_C3_fpt.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_C3_proof.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_C3_proof.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB1_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB1_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB1_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB1_fpt.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB1_proof.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB1_proof.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB2_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB2_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB2_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB2_fpt.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB2_proof.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB2_proof.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB3_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB3_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB3_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB3_fpt.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB3_proof.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_MB3_proof.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB1_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB1_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB1_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB1_fpt.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB1_proof.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB1_proof.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB2_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB2_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB2_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB2_fpt.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB2_proof.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB2_proof.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB3_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB3_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB3_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB3_fpt.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB3_proof.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB3_proof.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB4_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB4_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB4_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB4_fpt.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB4_proof.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB4_proof.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB5_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB5_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB5_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB5_fpt.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB5_proof.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_NB5_proof.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R1_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R1_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R1_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R1_fpt.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R1_proof.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R1_proof.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R2_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R2_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R2_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R2_fpt.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R2_proof.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R2_proof.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R3_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R3_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R3_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R3_fpt.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R3_proof.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R3_proof.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R4_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R4_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R4_fpt.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R4_fpt.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R4_proof.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R4_proof.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R5_diagnostic.pdf
reports/grid2d_reflecting_bimodality/figures/fpt/case_R5_diagnostic.png
reports/grid2d_reflecting_bimodality/figures/fpt/case_R5_fpt.pdf
```

### reports/grid2d_blackboard_bimodality/data

```text
reports/grid2d_blackboard_bimodality/data/A_metrics.json
reports/grid2d_blackboard_bimodality/data/B_metrics.json
reports/grid2d_blackboard_bimodality/data/C_metrics.json
reports/grid2d_blackboard_bimodality/data/D_metrics.json
reports/grid2d_blackboard_bimodality/data/E_metrics.json
reports/grid2d_blackboard_bimodality/data/R_metrics.json
reports/grid2d_blackboard_bimodality/data/S_metrics.json
reports/grid2d_blackboard_bimodality/data/X_metrics.json
reports/grid2d_blackboard_bimodality/data/Y_metrics.json
reports/grid2d_blackboard_bimodality/data/Z_metrics.json
reports/grid2d_blackboard_bimodality/data/Z_scan.json
```

### reports/grid2d_blackboard_bimodality/figures

```text
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_A_channel_decomp.pdf
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_A_channel_decomp.png
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_B_channel_decomp.pdf
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_B_channel_decomp.png
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_C_channel_decomp.pdf
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_C_channel_decomp.png
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_D_channel_decomp.pdf
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_D_channel_decomp.png
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_E_channel_decomp.pdf
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_E_channel_decomp.png
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_R_channel_decomp.pdf
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_R_channel_decomp.png
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_S_channel_decomp.pdf
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_S_channel_decomp.png
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_X_channel_decomp.pdf
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_X_channel_decomp.png
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_Y_channel_decomp.pdf
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_Y_channel_decomp.png
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_Z_channel_decomp.pdf
reports/grid2d_blackboard_bimodality/figures/channel_decomp/case_Z_channel_decomp.png
reports/grid2d_blackboard_bimodality/figures/env/blackboard_screenshot.png
reports/grid2d_blackboard_bimodality/figures/env/case_A_env.pdf
reports/grid2d_blackboard_bimodality/figures/env/case_A_env.png
reports/grid2d_blackboard_bimodality/figures/env/case_B_env.pdf
reports/grid2d_blackboard_bimodality/figures/env/case_B_env.png
reports/grid2d_blackboard_bimodality/figures/env/case_C_env.pdf
reports/grid2d_blackboard_bimodality/figures/env/case_C_env.png
reports/grid2d_blackboard_bimodality/figures/env/case_D_env.pdf
reports/grid2d_blackboard_bimodality/figures/env/case_D_env.png
reports/grid2d_blackboard_bimodality/figures/env/case_E_env.pdf
reports/grid2d_blackboard_bimodality/figures/env/case_E_env.png
reports/grid2d_blackboard_bimodality/figures/env/case_R_env.pdf
reports/grid2d_blackboard_bimodality/figures/env/case_R_env.png
reports/grid2d_blackboard_bimodality/figures/env/case_S_env.pdf
reports/grid2d_blackboard_bimodality/figures/env/case_S_env.png
reports/grid2d_blackboard_bimodality/figures/env/case_X_env.pdf
reports/grid2d_blackboard_bimodality/figures/env/case_X_env.png
reports/grid2d_blackboard_bimodality/figures/env/case_Y_env.pdf
reports/grid2d_blackboard_bimodality/figures/env/case_Y_env.png
reports/grid2d_blackboard_bimodality/figures/env/case_Z_env.pdf
reports/grid2d_blackboard_bimodality/figures/env/case_Z_env.png
reports/grid2d_blackboard_bimodality/figures/env/symbol_legend.pdf
reports/grid2d_blackboard_bimodality/figures/env/symbol_legend.png
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_A_fig3_panel.pdf
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_A_fig3_panel.png
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_B_fig3_panel.pdf
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_B_fig3_panel.png
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_C_fig3_panel.pdf
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_C_fig3_panel.png
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_D_fig3_panel.pdf
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_D_fig3_panel.png
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_E_fig3_panel.pdf
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_E_fig3_panel.png
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_R_fig3_panel.pdf
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_R_fig3_panel.png
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_S_fig3_panel.pdf
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_S_fig3_panel.png
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_X_fig3_panel.pdf
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_X_fig3_panel.png
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_Y_fig3_panel.pdf
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_Y_fig3_panel.png
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_Z_fig3_panel.pdf
reports/grid2d_blackboard_bimodality/figures/fig3_panels/case_Z_fig3_panel.png
reports/grid2d_blackboard_bimodality/figures/fig3_panels/channel_cartoon.pdf
reports/grid2d_blackboard_bimodality/figures/fig3_panels/channel_cartoon.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_A_diagnostic.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_A_diagnostic.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_A_fpt.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_A_fpt.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_A_proof.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_A_proof.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_B_diagnostic.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_B_diagnostic.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_B_fpt.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_B_fpt.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_B_proof.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_B_proof.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_C_diagnostic.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_C_diagnostic.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_C_fpt.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_C_fpt.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_C_proof.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_C_proof.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_D_diagnostic.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_D_diagnostic.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_D_fpt.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_D_fpt.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_D_proof.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_D_proof.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_E_diagnostic.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_E_diagnostic.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_E_fpt.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_E_fpt.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_E_proof.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_E_proof.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_R_diagnostic.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_R_diagnostic.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_R_fpt.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_R_fpt.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_R_proof.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_R_proof.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_S_diagnostic.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_S_diagnostic.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_S_fpt.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_S_fpt.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_S_proof.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_S_proof.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_X_diagnostic.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_X_diagnostic.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_X_fpt.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_X_fpt.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_X_proof.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_X_proof.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_Y_diagnostic.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_Y_diagnostic.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_Y_fpt.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_Y_fpt.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_Y_proof.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_Y_proof.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_Z_diagnostic.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_Z_diagnostic.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_Z_fpt.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_Z_fpt.png
reports/grid2d_blackboard_bimodality/figures/fpt/case_Z_proof.pdf
reports/grid2d_blackboard_bimodality/figures/fpt/case_Z_proof.png
reports/grid2d_blackboard_bimodality/figures/paths/case_A_paths_fast.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_A_paths_fast.png
reports/grid2d_blackboard_bimodality/figures/paths/case_A_paths_slow.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_A_paths_slow.png
reports/grid2d_blackboard_bimodality/figures/paths/case_B_paths_fast.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_B_paths_fast.png
reports/grid2d_blackboard_bimodality/figures/paths/case_B_paths_slow.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_B_paths_slow.png
reports/grid2d_blackboard_bimodality/figures/paths/case_C_paths_fast.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_C_paths_fast.png
reports/grid2d_blackboard_bimodality/figures/paths/case_C_paths_slow.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_C_paths_slow.png
reports/grid2d_blackboard_bimodality/figures/paths/case_D_paths_fast.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_D_paths_fast.png
reports/grid2d_blackboard_bimodality/figures/paths/case_D_paths_slow.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_D_paths_slow.png
reports/grid2d_blackboard_bimodality/figures/paths/case_E_paths_fast.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_E_paths_fast.png
reports/grid2d_blackboard_bimodality/figures/paths/case_E_paths_slow.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_E_paths_slow.png
reports/grid2d_blackboard_bimodality/figures/paths/case_R_paths_fast.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_R_paths_fast.png
reports/grid2d_blackboard_bimodality/figures/paths/case_R_paths_slow.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_R_paths_slow.png
reports/grid2d_blackboard_bimodality/figures/paths/case_S_paths_fast.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_S_paths_fast.png
reports/grid2d_blackboard_bimodality/figures/paths/case_S_paths_slow.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_S_paths_slow.png
reports/grid2d_blackboard_bimodality/figures/paths/case_X_paths_fast.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_X_paths_fast.png
reports/grid2d_blackboard_bimodality/figures/paths/case_X_paths_slow.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_X_paths_slow.png
reports/grid2d_blackboard_bimodality/figures/paths/case_Y_paths_fast.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_Y_paths_fast.png
reports/grid2d_blackboard_bimodality/figures/paths/case_Y_paths_slow.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_Y_paths_slow.png
reports/grid2d_blackboard_bimodality/figures/paths/case_Z_paths_fast.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_Z_paths_fast.png
reports/grid2d_blackboard_bimodality/figures/paths/case_Z_paths_slow.pdf
reports/grid2d_blackboard_bimodality/figures/paths/case_Z_paths_slow.png
```
