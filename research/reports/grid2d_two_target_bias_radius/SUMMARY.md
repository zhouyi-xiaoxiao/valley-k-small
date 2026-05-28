# Grid2D Bias-Radius Small Heatmap Summary

This bounded scan fixes `theta=0`, so near targets lie along the global eastward bias direction. The heatmap should not be read as evidence that distance alone explains the distribution shape; it is a fixed-angle slice over `(b, r)`.

## Heatmap Meaning

The heatmap color is the conservative distribution-shape classifier score `peak_separation * R_peak / max(R_valley, 1e-12)` computed from `f_total(t)`. A higher score indicates a stronger candidate two-peak separation by that metric, but a case is only called `double_peak` when the classifier label is exactly `double_peak`.

## Fixed Setup

- Grid: `15 x 9`
- Start: `(2, 4)`
- Far target: `(12, 4)`
- Bias direction: `E`
- Boundary: reflecting attempted-outside-stays
- Bias rule: global absolute stay-to-direction shift `p_dir=q/4+b`, `p_stay=1-q-b`
- Theta handling: fixed `theta=0`; no aggregation over theta

## Validation

- cases: `20`
- double_peak-labeled cases: `7`
- minimum transition probability: `0.14000000000000004`
- max row-stochasticity error: `2.2204460492503131e-16`
- max mass-balance error: `3.7747582837255322e-15`
- max near/far decomposition error: `8.6736173798840355e-19`

## Outputs

- config: `artifacts/data/grid2d_bias_radius_scan_config.csv`
- metrics: `artifacts/data/grid2d_bias_radius_scan_metrics.csv`
- heatmap: `artifacts/figures/grid2d_bias_radius_heatmap_theta0.pdf`
- double-peak candidate table: `artifacts/tables/grid2d_double_peak_candidates.csv`
- representative decomposition: `artifacts/figures/grid2d_representative_fpt_decomp_theta0_r05_b012.pdf`
- representative decomposition: `artifacts/figures/grid2d_representative_fpt_decomp_theta0_r04_b008.pdf`
- representative decomposition: `artifacts/figures/grid2d_representative_fpt_decomp_theta0_r04_b012.pdf`
