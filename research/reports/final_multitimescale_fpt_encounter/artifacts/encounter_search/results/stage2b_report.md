# Stage-2b Mechanism-Focused Encounter Analysis

Stage 2b asks whether the Stage-2 shoulders are boundary-induced delayed
channels, same-target long tails, target-shift shoulders, or generic spectral
tails. Double peaks are only claimed when F2 has two true local maxima with
a visible valley.

## Representative Cases

| case | class | t_main | t_late | F2 true double? | JSD | top early k | top late k | target shift score |
|---|---|---:|---:|---|---:|---:|---:|---:|
| A_boundary_1_5 | same_target_tail | 90 | 136 | False | 0.006447 | 4 | 4 | 9.398e-06 |
| B_boundary_1_7 | same_target_tail | 115 | 174 | False | 0.009512 | 6 | 6 | 1.084e-05 |
| C_boundary_1_4 | same_target_tail | 53 | 80 | False | 0.005248 | 3 | 3 | 7.74e-06 |

## Negative Control

- D_negative_control: classified `parity_artifact`; raw/F2 diagnostics stay in `artifacts/encounter_search/figures/stage2b/diagnostics/D_negative_control.pdf`.

## Boundary Null Comparison

- A_boundary_1_5: boundary shoulder score 23.36, best interior 19.48, ratio 1.2; hazard late/early 1.06 vs best interior 0.989; JSD 0.00645 vs best interior 0.0093; max Delta_k 0.0287 vs best interior 0.0281 -> not boundary-specific.
- B_boundary_1_7: boundary shoulder score 17.8, best interior 15.03, ratio 1.18; hazard late/early 1.07 vs best interior 1.02; JSD 0.00951 vs best interior 0.0128; max Delta_k 0.0218 vs best interior 0.0216 -> not boundary-specific.
- C_boundary_1_4: boundary shoulder score 26.29, best interior 23.31, ratio 1.13; hazard late/early 1.06 vs best interior 0.989; JSD 0.00525 vs best interior 0.0063; max Delta_k 0.0307 vs best interior 0.028 -> not boundary-specific.

## Target-Shift Reranking

| rank | class | N | start | q1 | q2 | score | JSD | late mass | max +Delta k | top k changed |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | boundary_long_tail | 31 | (4,1) | 0.2 | 0.9 | 1.467e-03 | 0.0473 | 0.311 | 5 | True |
| 2 | boundary_long_tail | 31 | (1,4) | 0.9 | 0.2 | 1.467e-03 | 0.0473 | 0.311 | 5 | True |
| 3 | boundary_long_tail | 31 | (28,31) | 0.2 | 0.9 | 1.467e-03 | 0.0473 | 0.311 | 27 | True |
| 4 | boundary_long_tail | 31 | (31,28) | 0.9 | 0.2 | 1.467e-03 | 0.0473 | 0.311 | 27 | True |
| 5 | boundary_long_tail | 31 | (28,31) | 0.1 | 0.9 | 1.429e-03 | 0.0404 | 0.335 | 27 | False |
| 6 | boundary_long_tail | 31 | (1,4) | 0.9 | 0.1 | 1.429e-03 | 0.0404 | 0.335 | 5 | False |
| 7 | boundary_long_tail | 31 | (4,1) | 0.1 | 0.9 | 1.429e-03 | 0.0404 | 0.335 | 5 | False |
| 8 | boundary_long_tail | 31 | (31,28) | 0.9 | 0.1 | 1.429e-03 | 0.0404 | 0.335 | 27 | False |
| 9 | target_shift_shoulder | 31 | (2,4) | 0.7 | 0.2 | 1.426e-03 | 0.0537 | 0.315 | 2 | True |
| 10 | target_shift_shoulder | 31 | (4,2) | 0.2 | 0.7 | 1.426e-03 | 0.0537 | 0.315 | 2 | True |
| 11 | target_shift_shoulder | 31 | (28,30) | 0.2 | 0.7 | 1.426e-03 | 0.0537 | 0.315 | 30 | True |
| 12 | target_shift_shoulder | 31 | (30,28) | 0.7 | 0.2 | 1.426e-03 | 0.0537 | 0.315 | 30 | True |
| 13 | boundary_long_tail | 31 | (1,4) | 0.85 | 0.1 | 1.350e-03 | 0.0391 | 0.337 | 5 | False |
| 14 | boundary_long_tail | 31 | (31,28) | 0.85 | 0.1 | 1.350e-03 | 0.0391 | 0.337 | 27 | False |
| 15 | boundary_long_tail | 31 | (4,1) | 0.1 | 0.85 | 1.350e-03 | 0.0391 | 0.337 | 5 | False |

## Spectral Interpretation

- A_boundary_1_5: leading lambda=0.99982753, timescale=5.8e+03, top R-channel k=16. Late behavior is treated as a slow-mode tail unless target-shift metrics separate it.
- B_boundary_1_7: leading lambda=0.99972431, timescale=3.63e+03, top R-channel k=16. Late behavior is treated as a slow-mode tail unless target-shift metrics separate it.
- C_boundary_1_4: leading lambda=0.99982753, timescale=5.8e+03, top R-channel k=16. Late behavior is treated as a slow-mode tail unless target-shift metrics separate it.

Selected target-shift spectral checks:
- target_shift_01: class=boundary_long_tail, leading lambda=0.99746460, timescale=394, top R-channel k=16, mode tail weight=2.56e-05, top k changed=True.
- target_shift_02: class=boundary_long_tail, leading lambda=0.99746460, timescale=394, top R-channel k=16, mode tail weight=2.56e-05, top k changed=True.
- target_shift_03: class=boundary_long_tail, leading lambda=0.99746460, timescale=394, top R-channel k=16, mode tail weight=2.56e-05, top k changed=True.
- target_shift_04: class=boundary_long_tail, leading lambda=0.99746460, timescale=394, top R-channel k=16, mode tail weight=2.56e-05, top k changed=True.
- target_shift_05: class=boundary_long_tail, leading lambda=0.99786765, timescale=468, top R-channel k=26, mode tail weight=9.07e-06, top k changed=False.
- target_shift_06: class=boundary_long_tail, leading lambda=0.99786765, timescale=468, top R-channel k=6, mode tail weight=9.07e-06, top k changed=False.
- target_shift_07: class=boundary_long_tail, leading lambda=0.99786765, timescale=468, top R-channel k=6, mode tail weight=9.07e-06, top k changed=False.
- target_shift_08: class=boundary_long_tail, leading lambda=0.99786765, timescale=468, top R-channel k=6, mode tail weight=9.07e-06, top k changed=False.

## Final Classification

- `same_target_tail`: 15
- `boundary_long_tail`: 8
- `parity_artifact`: 1

## Outputs

- `artifacts/encounter_search/results/stage2b_cases.csv`
- `artifacts/encounter_search/results/stage2b_target_shift.csv`
- `artifacts/encounter_search/results/stage2b_report.md`
- `artifacts/encounter_search/figures/stage2b/diagnostics/`
- `artifacts/encounter_search/figures/stage2b/boundary_vs_interior/`
- `artifacts/encounter_search/figures/stage2b/group_decomposition/`
- `artifacts/encounter_search/figures/stage2b/spectral/`

## Answer Summary

- Robust F2 double peaks found: 0.
- A-C are not promoted to double peaks; they are shoulders/long tails under the F2 rule.
- The target-shift reranking is usually dominated by small JSD values; changed top-k rows are flagged explicitly.
- Group plots distinguish same-k tails from genuine late mass moving to new encounter-site groups.
- Spectral plots report whether the late tail aligns with leading slow modes near lambda=1.
