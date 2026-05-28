# Final Multitimescale FPT and Encounter Report

**Status: consistency layer.** This report indexes the accepted outputs for the
multi-timescale first-passage and two-walker encounter project without
regenerating raw scientific results.

## Scope

The final report connects:

- [`grid2d_one_target_valley_peak_budget`](../grid2d_one_target_valley_peak_budget/)
  for the completed one-target budget-decomposition template,
- [`ring_two_target`](../ring_two_target/) for 1D two-target target-channel
  decomposition and scan outputs,
- [`grid2d_two_target_bias_radius`](../grid2d_two_target_bias_radius/) for the
  2D near/far target heatmap and representative decompositions,
- [`encounter_reflecting_mean_validation`](../encounter_reflecting_mean_validation/)
  for reflecting encounter mean validation,
- [`encounter_reflecting_diagonal_decomp`](../encounter_reflecting_diagonal_decomp/)
  for ratio and initial-position scans with diagonal-position decomposition.

## Consistency Build

Run from the repository root:

```bash
python3 research/reports/final_multitimescale_fpt_encounter/code/build_consistency_layer.py
```

The script copies selected accepted figures into this report and writes:

- `artifacts/data/result_registry.csv`
- `artifacts/data/validation_summary.csv`
- `artifacts/data/figure_index.csv`
- `artifacts/data/double_peak_audit.csv`
- `manuscript/inputs/result_registry_table.tex`
- `manuscript/inputs/validation_summary_table.tex`

It checks that:

- all registry figure/data/table/script paths exist,
- every registry mechanism claim uses one of `budget decomposition`,
  `target-channel decomposition`, or `diagonal-position decomposition`,
- final manuscript `\includegraphics` and `\input` targets exist,
- positive `double_peak` wording is supported by classifier outputs.

## Manuscript

- Main manuscript:
  [`manuscript/final_multitimescale_fpt_encounter_en.tex`](manuscript/final_multitimescale_fpt_encounter_en.tex)

The final report is intentionally evidence-indexed. If any source module changes
its accepted outputs, rerun the consistency script before rebuilding the PDF.

## Build

The report is not currently registered in `reportctl.py list`, so the direct
build command is:

```bash
cd research/reports/final_multitimescale_fpt_encounter/manuscript
latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -auxdir=build -emulate-aux-dir final_multitimescale_fpt_encounter_en.tex
```

## Guardrails

- Do not regenerate raw result files from this report.
- Do not edit underlying scientific computations from this report.
- Do not call an output `double_peak` unless the matching classifier table says
  `double_peak`.
- Do not make mechanism claims outside the three allowed evidence routes:
  budget decomposition, target-channel decomposition, and diagonal-position
  decomposition.

