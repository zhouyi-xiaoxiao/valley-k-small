# Small Two-Target Ring Scan

This bounded scan uses exact propagation on a small grid of periodic 1D ring
two-target first-passage problems. Each case was validated for nonnegative
row-stochastic transitions, mass balance, and target-channel decomposition.

The shape labels come from the shared peak classifier. In particular, a curve is
called `double_peak` only when the classifier returns `double_peak`; weaker
late-time structures remain `shoulder` or `local_bump`.

## Outputs

- Metrics CSV: `ring_two_target/artifacts/data/small_scan_metrics.csv`
- Representative case CSVs: `ring_two_target/artifacts/outputs/small_scan_cases/`
- Representative figures: `ring_two_target/artifacts/figures/small_scan/`

## Validation Summary

- Scanned cases: 240
- Max row-stochasticity error: 0.000e+00
- Max mass-balance error: 4.545e-16
- Max target-channel decomposition error: 0.000e+00

## Shape Counts

- `unimodal`: 170
- `shoulder`: 26
- `local_bump`: 10
- `double_peak`: 34

## Representative Cases

| classification | case_id | targets | drift | beta | early dominant | late dominant | R_peak | R_valley |
|---|---|---:|---:|---:|---|---|---:|---:|
| unimodal | `031_unimodal_L31_x0_a30_20_gm0p6_b0p00` | (30,20) | -0.6 | 0.0 | target1 | target1 | 0 | 1 |
| shoulder | `221_shoulder_L51_x13_a17_34_gm0p6_b0p00` | (17,34) | -0.6 | 0.0 | target1 | target2 | 0.0161 | 0.000188 |
| local_bump | `037_local_bump_L31_x0_a30_20_gp0p3_b0p00` | (30,20) | 0.3 | 0.0 | target1 | target2 | 0.0286 | 0.00442 |
| double_peak | `159_double_peak_L51_x0_a50_30_gp0p6_b0p00` | (50,30) | 0.6 | 0.0 | target1 | target2 | 0.16 | 9.69e-05 |

## Interpretation Guardrail

The scan identifies representative shapes and their target-channel budgets.
A mechanism claim should use the channel evidence in the representative CSVs
and figures. The scan alone should not be used to infer a mechanism without
checking which target channel dominates the early and late portions of the
distribution.
