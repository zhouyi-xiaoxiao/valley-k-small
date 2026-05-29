# Final Exact Encounter-Analysis Report

## Executive conclusion

Robust F2 double peaks found: 0. The current finite 1D reflecting,
synchronous, co-location-only encounter model does not produce a robust double
peak in the retained Stage 1/2/2b scans. Apparent unusual shapes are classified
as parity artifacts, same-target long tails, or weak target-shift shoulders.

Where do the visible bumps or shoulders appear? Short-distance, strongly
asymmetric mobility cases can show jagged raw peaks from odd/even parity; the
negative control `N=21, start=(6,2), q1=0.02, q2=0.9` is the clearest example.
Slow near-boundary cases such as A/B/C show long tails or shoulders, but the
dominant encounter site does not change (`4->4`, `6->6`, `3->3`). The best
target-shift case `N=31, start=(2,4), q1=0.7, q2=0.2` has a weak site shift
`4->3`, but still no true F2 double peak.

The jagged figure is therefore normal for this synchronous discrete-time
model: it is a parity-comb artifact in raw `f(t)`. The decision curve is `F2`,
which pairs odd/even times before applying the same peak-valley rule used in
the rest of the repository.

## Model and exact absorbing-chain formulation

The model is the finite one-dimensional reflecting lattice with sites `1..N`.
Walker `i` has lazy mobility `q_i`; boundary reflection uses attempted-outside-stays.
The synchronous independent update has joint transition `P = kron(P1, P2)`.
Transient states are off-diagonal ordered pairs `O={(x,y):x!=y}` and encounter
states are diagonal co-locations `D={(k,k)}`. The exact absorbing-chain blocks are
`Q=P[O,O]` and `R=P[O,D]`, so `f_k(t)=alpha Q^(t-1) R[:,k]` and
`f(t)=sum_k f_k(t)`. No Monte Carlo is used.

## Spatial configuration views

The final package now includes the actual spatial layout for A/B/C, the
negative control, and the best target-shift case. Each row shows the physical
one-dimensional reflecting lattice on the left and the ordered state space
`(x,y)` on the right. In the state-space panel, the diagonal is the absorbing
co-location set `D={(k,k)}`.

Figure: `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/figures/final/spatial_configurations.pdf`.

How to read this figure: blue up-triangle is walker 1 start `x0`; orange
down-triangle is walker 2 start `y0`; green square is the dominant encounter
site in the early window; red square is the dominant encounter site in the late
window; purple diamond is the site with the largest positive `Delta_k = C_late-C_early`.
The right panel is the ordered state space, where the diagonal line is the
absorbing set `D` and the inset is a local zoom around the actual start and
dominant encounter sites.

## Operational double-peak rule

A raw second bump is not enough. The final rule first forms the parity-pair
curve `F2[n]=f(2n-1)+f(2n)` to remove odd/even update oscillations. A case is
called a robust F2 double peak only if F2 has at least two true local maxima:
a main peak and a later peak more than two F2 bins later. The later peak must
be at least 5% of the main peak, and the minimum valley between the two peaks
must be at most 80% of the smaller peak. Otherwise the feature is reported as
a shoulder, long tail, target-shift shoulder, or artifact. This is why A/B/C
and the best target-shift case are not called double peaks.

This is aligned with the repository's existing visual double-peak convention
`rho = h_valley/min(h1,h2) <= 0.8`. The encounter-specific part is only the
preprocessing step: synchronous co-location curves can alternate strongly
between odd and even time steps, so the classifier is applied to `F2` rather
than to raw `f(t)` when making the final double-peak claim.

In diagnostic bundles, dashed green/red vertical lines mark the main and late
diagnostic times; `C_k` compares normalized encounter-site mass in early and
late windows; the heatmap shows `log10 f_k(t)` by encounter site and time.
Light gray bands and small inset axes are local zooms for the jagged, shoulder,
or F2-decision regions that are hard to read on the full time axis.

## Mean identities and GF determinant validation

The formula checks close to numerical precision: max `mean_abs_error` is 6.25e-10, max `p_tau_mean_abs_error` is 4.97e-14, and max decomposition error is 0.
The small-`N` Green/determinant validation has max absolute error 3.52e-16.

Tables: `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/results/final_tables/formula_validation.csv`, `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/results/final_tables/gf_validation.csv`.

## Mean first-passage time vs q1/q2: maximum is not universal

The three pilot scans show different extremum structure. Two starts have an
interior maximum in the scanned mobility ratio range, while the boundary-to-boundary
fixed-sum case has an interior minimum and an endpoint maximum. Thus an interior
maximum of mean encounter time is a geometry/start-dependent phenomenon, not a
universal rule.

Figure: `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/figures/final/mean_vs_ratio.pdf`.
Table: `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/results/final_tables/mean_ratio_extrema.csv`.

| scan_id | description | kind | r | q1 | q2 | mean |
| --- | --- | --- | --- | --- | --- | --- |
| A_fixed_q2_start_5_1 | start=(5,1), q2=0.5, r=q1/q2 | global_max;local_max | 0.427671 | 0.213836 | 0.5 | 51.0852 |
| A_fixed_q2_start_5_1 | start=(5,1), q2=0.5, r=q1/q2 | global_min | 2 | 1 | 0.5 | 38.4629 |
| B_fixed_sum_start_7_9 | start=(7,9), q1+q2=1, r=q1/q2 | global_max;local_max | 1.06003 | 0.514569 | 0.485431 | 43.1421 |
| B_fixed_sum_start_7_9 | start=(7,9), q1+q2=1, r=q1/q2 | global_min | 100 | 0.990099 | 0.00990099 | 30.7548 |
| C_fixed_sum_start_1_15 | start=(1,15), q1+q2=1, r=q1/q2 | global_max | 0.01 | 0.00990099 | 0.990099 | 194.223 |
| C_fixed_sum_start_1_15 | start=(1,15), q1+q2=1, r=q1/q2 | global_min;local_min | 0.943373 | 0.485431 | 0.514569 | 138.226 |

## Why Stage-1 double peaks were artifacts

Stage 1 ranked raw curves and therefore promoted short-distance parity combs.
The representative negative control keeps multiple raw peaks at alternating times,
but the parity-pair curve `F2[n]=f(2n-1)+f(2n)` collapses the feature to a single
peak. These cases are rejected as parity or ballistic-short-distance artifacts,
not as genuine double peaks.

Figure: `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/figures/final/stage1_artifact_raw_vs_f2.pdf`.
Table: `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/results/final_tables/artifact_rejection.csv`.

## Stage-2/2b result: no robust F2 double peaks

In the Stage-2b case table plus the top-30 target-shift table, robust F2 double peaks found: 0.
Across the current reflecting synchronous co-location model, the observed unusual
shapes are better classified as parity artifacts, same-target long tails, or weak
target-shift shoulders. This report does not claim a robust double peak.

Table: `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/results/final_tables/mechanism_classification.csv`.

## Same-target long-tail cases A/B/C

Cases A, B, and C are not double peaks. Their top encounter site is unchanged
between early and late windows, and the boundary-null controls do not show a large
boundary-specific amplification. They are therefore reported as same-target long
tails with weak boundary influence, not boundary-induced delayed channels.

Figure: `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/figures/final/same_target_tail_ABC.pdf`.
Boundary comparison: `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/figures/final/boundary_vs_interior_summary.pdf`.

## Weak target-shift case and responsible k sites

The clearest target-shift shoulder in the retained Stage-2b list is
`N=31, start=(2,4), q1=0.7, q2=0.2`. It is a weak target-shift shoulder,
not a double peak. Its early/late encounter-site distributions shift enough
to change the top site and produce a modest JSD, but F2 still lacks two true
local maxima separated by a visible valley.

For this case: top k 4->3, JSD=0.0537, max positive Delta at k=2, target-shift score=0.00143.

Figure: `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/figures/final/best_target_shift.pdf`.

## Spectral interpretation: late tail as generic slow-mode relaxation

The spectral checks show leading eigenvalues close to one and slow tail-channel
weights that are not cleanly aligned with a new dominant encounter site. For A,
the leading mode has lambda=0.99982753 and top R-channel k=16, while the early/late top encounter site remains k=4. For the weak target-shift case, the site shift is
visible in `C_k`, but the curve still reads as slow-mode relaxation plus modest
redistribution, not as a separate second-peak mechanism.

Figure: `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/figures/final/spectral_A_and_target_shift.pdf`.

## Final scientific conclusion and limitations

Final conclusion: no robust F2 double peak was found in the current reflecting
synchronous co-location model. The weird shapes observed in Stage 1, Stage 2,
and Stage 2b are parity artifacts, same-target long tails, or weak target-shift
shoulders. The conclusion is limited to the scanned finite 1D reflecting model,
the synchronous lazy update rule, and co-location-only encounters; it does not
rule out stronger effects under different boundary conditions, crossing absorption,
higher dimensions, or different mobility/start regimes.

## Reproducibility

Install dependencies with Python 3.11 and run the final packaging command:

```bash
python3.11 -m venv .local/encounter-py311
.local/encounter-py311/bin/python -m pip install -r requirements.txt
PYTHONPATH=research/reports/final_multitimescale_fpt_encounter/code .local/encounter-py311/bin/python -m encounter_search.finalize
PYTHONPATH=research/reports/final_multitimescale_fpt_encounter/code .local/encounter-py311/bin/python -m pytest tests/test_encounter_search.py tests/test_encounter_reflecting_mean_validation.py tests/test_encounter_green_formula_comparison.py -q
```

One command to reproduce the final outputs from existing Stage 1/2/2b inputs:

```bash
PYTHONPATH=research/reports/final_multitimescale_fpt_encounter/code .local/encounter-py311/bin/python -m encounter_search.finalize
```
