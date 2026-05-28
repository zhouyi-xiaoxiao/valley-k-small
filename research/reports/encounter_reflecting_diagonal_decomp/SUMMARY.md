# Reflecting Encounter Diagonal Decomposition Ratio Scan

This bounded scan uses the fixed-total-mobility convention
`Q1 = 2*q0*rho/(1+rho)` and `Q2 = 2*q0/(1+rho)`.

Each case records the full encounter distribution `f_E(t)`, the
diagonal-position contributions `f_k(t)`, survival, distribution mean,
mass-balance error, and shape classification from `vkcore.peaks`.

Scientific guardrail: a curve is called `double_peak` only when the
shared classifier returns `double_peak`. Otherwise the reported labels
are `unimodal`, `shoulder`, or `local_bump`.

## Validation

- cases: 28
- max mass-balance error: 3.574e-16
- max diagonal decomposition error: 0.000e+00

## Shape Classes by rho

| rho | classes |
|---:|---|
| 0.1 | unimodal: 4 |
| 0.2 | unimodal: 4 |
| 0.5 | unimodal: 4 |
| 1 | unimodal: 4 |
| 2 | unimodal: 4 |
| 5 | unimodal: 4 |
| 10 | unimodal: 4 |

## Shape Classes by Initial Pair

| start | classes |
|---|---|
| (0, 6) | unimodal: 7 |
| (6, 0) | unimodal: 7 |
| (1, 5) | unimodal: 7 |
| (5, 1) | unimodal: 7 |

## Mechanism Pointers

Dominant early and late position columns in
`data/encounter_ratio_scan_metrics.csv` summarize the largest
diagonal contributions in windows around `t1` and, when present,
`t2`. Mechanism claims should be made from those `f_k(t)` windows
or from the case heatmaps, not from the mean curve alone.

## Generated Outputs

- `data/encounter_ratio_scan_config.csv`
- `data/encounter_ratio_scan_metrics.csv`
- `tables/encounter_shape_classification.csv`
- `figures/encounter_fpt_by_ratio.pdf`
- `figures/encounter_diag_contrib_heatmap_case_<id>.pdf`
- `outputs/case_<id>_f_total.csv`
- `outputs/case_<id>_diag_contrib.csv`
