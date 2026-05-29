# 1D Reflecting Lazy Encounter Exact Pilot

Model: two synchronous independent lazy walkers on sites `1..N`, with
attempted-outside-stays reflecting boundaries and co-location encounter
set `D={(k,k)}`. Computation uses sparse absorbing-chain blocks
`Q=P_joint[O,O]` and `R=P_joint[O,D]`; no Monte Carlo is used.

## Validation

- mean/formula cases: 3
- max `|sum_t t f(t)-mean|`: 6.250e-10
- max `|sum_k p_k tau_k-mean|`: 4.974e-14
- max mass-balance error: 2.567e-16
- GF determinant rows: 4
- max GF absolute error: 3.523e-16

## Mean-Ratio Pilot

- `A_fixed_q2_start_5_1`: 80 ratios; extrema rows: 2
  - global_max;local_max: r=0.42767, mean=51.0852, top p_k tau_k=k=4:6.66714;k=5:6.53363;k=6:5.62153;k=3:5.1864;k=7:4.72577
  - global_min: r=2, mean=38.4629, top p_k tau_k=k=3:4.75538;k=4:4.58835;k=2:4.21751;k=5:4.19555;k=6:3.74965
- `B_fixed_sum_start_7_9`: 80 ratios; extrema rows: 2
  - global_max;local_max: r=1.06, mean=43.1421, top p_k tau_k=k=8:5.26286;k=9:4.84969;k=7:4.78535;k=10:4.14395;k=6:4.06452
  - global_min: r=100, mean=30.7548, top p_k tau_k=k=9:16.3649;k=10:5.44371;k=8:4.89549;k=11:1.83356;k=7:1.03658
- `C_fixed_sum_start_1_15`: 80 ratios; extrema rows: 2
  - global_max: r=0.01, mean=194.223, top p_k tau_k=k=1:91.89;k=2:59.0954;k=3:27.6367;k=4:10.7091;k=5:3.56021
  - global_min;local_min: r=0.94337, mean=138.226, top p_k tau_k=k=8:14.4795;k=7:14.2609;k=9:14.0109;k=6:13.3704;k=10:12.9035

## Shape Pilot

- top cases retained: 30
- figures for the first 10 cases are under `artifacts/encounter_search/results/figures/top10/`.

| rank | label | N | start | q1 | q2 | score | t_main | t_late | JSD | mechanism |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | local_bump | 21 | (6,2) | 0.02 | 0.9 | 2.32 | 4 | 10 | 0.00781 | same_target_multi_path |
| 2 | local_bump | 21 | (16,20) | 0.02 | 0.9 | 2.32 | 4 | 10 | 0.00781 | same_target_multi_path |
| 3 | local_bump | 21 | (2,6) | 0.9 | 0.02 | 2.32 | 4 | 10 | 0.00781 | same_target_multi_path |
| 4 | local_bump | 21 | (20,16) | 0.9 | 0.02 | 2.32 | 4 | 10 | 0.00781 | same_target_multi_path |
| 5 | local_bump | 15 | (6,2) | 0.02 | 0.9 | 2.32 | 4 | 10 | 0.00781 | same_target_multi_path |
| 6 | local_bump | 15 | (10,14) | 0.02 | 0.9 | 2.32 | 4 | 10 | 0.00781 | same_target_multi_path |
| 7 | local_bump | 15 | (2,6) | 0.9 | 0.02 | 2.32 | 4 | 10 | 0.00781 | same_target_multi_path |
| 8 | local_bump | 15 | (14,10) | 0.9 | 0.02 | 2.32 | 4 | 10 | 0.00781 | same_target_multi_path |
| 9 | local_bump | 21 | (2,6) | 0.9 | 0.05 | 1.91 | 4 | 10 | 0.0162 | same_target_multi_path |
| 10 | local_bump | 21 | (6,2) | 0.05 | 0.9 | 1.91 | 4 | 10 | 0.0162 | same_target_multi_path |

The shape labels are pilot-screening labels. `double_peak` is retained
only when the raw feature persists through all Savitzky-Golay windows
and is not dominated by parity contrast; otherwise weaker candidates
are reported as `local_bump`, `shoulder`, or `artifact`.

## Outputs

- `validation_mean.csv`
- `validation_gf.csv`
- `mean_ratio_pilot.csv`
- `top_shape_cases.csv`
- `report.md`
- `artifacts/encounter_search/results/figures/top10/*.pdf`
