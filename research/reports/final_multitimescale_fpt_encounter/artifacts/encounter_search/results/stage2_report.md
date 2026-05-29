# Stage-2 Artifact-Resistant 1D Encounter Search

Stage 2 treats the Stage-1 distance-4, extreme-mobility cases as negative
controls. Ranking is now based on raw peaks, Savitzky-Golay persistence
for windows 7/11/21/31, the parity-pair curve `F2[n]=f(2n-1)+f(2n)`,
a local oscillation index, target-channel attribution, and crossing/bounce
sensitivity checks.

## Scan Summary

- scanned rows: 99840
- N values: 15, 21, 31
- q grid: 0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 0.85, 0.9
- starts: all ordered off-diagonal starts for N=15, N=21, and N=31
- non-artifact rows retained: 50
- weak/artifact rows retained: 20
- figures: `artifacts/encounter_search/figures/stage2/top_nonartifact/` and `artifacts/encounter_search/figures/stage2/negative_controls/`

## 1. Stage-1 Rejections

| Stage-1 rank | N | start | q1 | q2 | final label | reason | raw peaks | F2 peaks | F2 late | oscillation |
|---:|---:|---|---:|---:|---|---|---|---|---:|---:|
| 1 | 21 | (6,2) | 0.02 | 0.9 | artifact | ballistic_short_distance | 4;6;8;10;12 | 4 | 12 | 0.271 |
| 3 | 21 | (2,6) | 0.9 | 0.02 | artifact | ballistic_short_distance | 4;6;8;10;12 | 4 | 12 | 0.271 |
| 25 | 15 | (2,6) | 0.02 | 0.9 | artifact | ballistic_short_distance | 4;6;8;10;12 | 3 | 12 | 0.304 |
| 29 | 21 | (2,6) | 0.02 | 0.9 | artifact | ballistic_short_distance | 4;6;8;10;12 | 3 | 12 | 0.304 |

These controls still show multiple raw peaks, but the F2 peak list has
only one peak. The reported F2-late column is a baseline-shoulder
diagnostic, not an accepted F2 late peak; the Stage-1 interpretation is
rejected when the late feature is only an even/odd comb or
a very short-distance ballistic repeat.

## 2. Robust Double Peaks

No robust double peaks survived the F2/parity filtering in this scan.

## 3. Strongest Robust Shoulders

| rank | N | start | q1 | q2 | score | t_main | t_late | F2 late | reason |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 31 | (1,5) | 0.05 | 0.02 | 155 | 90 | 136 | 136 | none |
| 2 | 31 | (27,31) | 0.02 | 0.05 | 155 | 90 | 136 | 136 | none |
| 3 | 31 | (31,27) | 0.05 | 0.02 | 155 | 90 | 136 | 136 | none |
| 4 | 31 | (5,1) | 0.02 | 0.05 | 155 | 90 | 136 | 136 | none |
| 5 | 31 | (1,7) | 0.1 | 0.02 | 133 | 115 | 174 | 174 | none |
| 6 | 31 | (31,25) | 0.1 | 0.02 | 133 | 115 | 174 | 174 | none |
| 7 | 31 | (7,1) | 0.02 | 0.1 | 133 | 115 | 174 | 174 | none |
| 8 | 31 | (25,31) | 0.02 | 0.1 | 133 | 115 | 174 | 174 | none |
| 9 | 31 | (4,1) | 0.02 | 0.05 | 133 | 53 | 80 | 80 | none |
| 10 | 31 | (1,4) | 0.05 | 0.02 | 133 | 53 | 80 | 80 | none |

## 4. Encounter-Site Attribution

| rank | attribution | top early k | top late k | JSD bits | Delta top |
|---:|---|---:|---:|---:|---|
| 1 | same_target_multi_path | 4 | 4 | 0.00645 | k=4:-0.0375642;k=6:0.0286856;k=7:0.0125739;k=3:-0.012256;k=2:0.00912226 |
| 2 | same_target_multi_path | 28 | 28 | 0.00645 | k=28:-0.0375642;k=26:0.0286856;k=25:0.0125739;k=29:-0.012256;k=30:0.00912226 |
| 3 | same_target_multi_path | 28 | 28 | 0.00645 | k=28:-0.0375642;k=26:0.0286856;k=25:0.0125739;k=29:-0.012256;k=30:0.00912226 |
| 4 | same_target_multi_path | 4 | 4 | 0.00645 | k=4:-0.0375642;k=6:0.0286856;k=7:0.0125739;k=3:-0.012256;k=2:0.00912226 |
| 5 | same_target_multi_path | 6 | 6 | 0.00951 | k=6:-0.0444802;k=7:-0.0264324;k=9:0.021788;k=8:0.0203592;k=5:-0.0138081 |
| 6 | same_target_multi_path | 26 | 26 | 0.00951 | k=26:-0.0444802;k=25:-0.0264324;k=23:0.021788;k=24:0.0203592;k=27:-0.0138081 |
| 7 | same_target_multi_path | 6 | 6 | 0.00951 | k=6:-0.0444802;k=7:-0.0264324;k=9:0.021788;k=8:0.0203592;k=5:-0.0138081 |
| 8 | same_target_multi_path | 26 | 26 | 0.00951 | k=26:-0.0444802;k=25:-0.0264324;k=23:0.021788;k=24:0.0203592;k=27:-0.0138081 |
| 9 | same_target_multi_path | 3 | 3 | 0.00525 | k=5:0.0306661;k=3:-0.0285512;k=4:-0.0174557;k=6:0.0063587;k=1:0.00436915 |
| 10 | same_target_multi_path | 3 | 3 | 0.00525 | k=5:0.0306661;k=3:-0.0285512;k=4:-0.0174557;k=6:0.0063587;k=1:0.00436915 |
| 11 | same_target_multi_path | 29 | 29 | 0.00525 | k=27:0.0306661;k=29:-0.0285512;k=28:-0.0174557;k=26:0.0063587;k=31:0.00436915 |
| 12 | same_target_multi_path | 29 | 29 | 0.00525 | k=27:0.0306661;k=29:-0.0285512;k=28:-0.0174557;k=26:0.0063587;k=31:0.00436915 |
| 13 | same_target_multi_path | 3 | 3 | 0.0064 | k=3:-0.0269502;k=6:0.0219278;k=4:-0.019529;k=7:0.0171813;k=2:-0.0105513 |
| 14 | same_target_multi_path | 3 | 3 | 0.0064 | k=3:-0.0269502;k=6:0.0219278;k=4:-0.019529;k=7:0.0171813;k=2:-0.0105513 |
| 15 | same_target_multi_path | 29 | 29 | 0.0064 | k=29:-0.0269502;k=26:0.0219278;k=28:-0.019529;k=25:0.0171813;k=30:-0.0105513 |

## 5. Crossing And Bounce Survival

| rank | crossing survives | crossing label | bounce survives | bounce label |
|---:|---|---|---|---|
| 1 | True | robust_shoulder | True | robust_shoulder |
| 2 | True | robust_shoulder | True | robust_shoulder |
| 3 | True | robust_shoulder | True | robust_shoulder |
| 4 | True | robust_shoulder | True | robust_shoulder |
| 5 | True | robust_shoulder | True | robust_shoulder |
| 6 | True | robust_shoulder | True | robust_shoulder |
| 7 | True | robust_shoulder | True | robust_shoulder |
| 8 | True | robust_shoulder | True | robust_shoulder |
| 9 | True | robust_shoulder | True | robust_shoulder |
| 10 | True | robust_shoulder | True | robust_shoulder |
| 11 | True | robust_shoulder | True | robust_shoulder |
| 12 | True | robust_shoulder | True | robust_shoulder |
| 13 | True | robust_shoulder | True | robust_shoulder |
| 14 | True | robust_shoulder | True | robust_shoulder |
| 15 | True | robust_shoulder | True | robust_shoulder |

## Output Files

- `artifacts/encounter_search/results/stage2_shape_cases.csv`
- `artifacts/encounter_search/results/stage2_artifacts.csv`
- `artifacts/encounter_search/results/stage2_report.md`
- `artifacts/encounter_search/figures/stage2/top_nonartifact/`
- `artifacts/encounter_search/figures/stage2/negative_controls/`

## Notes

- `target_mixture` requires `JSD>=0.05` bits and a changed top encounter site.
- `same_target_multi_path` requires the dominant `f_k(t)` channel itself to pass the robust F2 feature test.
- Rows with features that vanish under both crossing absorption and bounce reflection are demoted to `weak` with `artifact_reason=crossing_sensitive`.
