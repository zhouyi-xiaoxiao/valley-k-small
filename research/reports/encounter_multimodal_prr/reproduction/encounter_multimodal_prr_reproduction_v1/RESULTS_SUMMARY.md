# Robustness-results summary

This file is a compact reading guide to the machine-readable records under
`artifacts/data/exact_m_prr_upgrade/robustness/`.  Values below are descriptive
diagnostics, not preregistered hypothesis tests.

## Covariance-aware reclassification (formal definition used in the article)

All 201 stored classifier records (112 W1 cells, 43 W2 probes, 26 robustness
records, the 18 production rows, W4, and W5; 606 local maxima) were re-judged
with the covariance-aware prominence statistic
`sigma_prom^2 = sum_j (A_peak,j - A_base,j)^2 C_j / (N dt)^2`, where
`A_peak,j` and `A_base,j` are the edge-normalized Gaussian kernel weights of
the peak bin and of the selected contour-base bin, `C_j` the raw bin counts,
`N` the walker count and `dt` the bin width; the acceptance rule is unchanged
(`z >= 5` and prominence `>= 5%` of the window maximum).  This is the
statistic defined in the article.  The peak-only convention
`sigma_peak^2 = sum_j A_peak,j^2 C_j / (N dt)^2` under which the records were
first written is superseded; it inflates `z` of counted maxima by factors
1.00--1.55.  Three of the 606 maxima flip, all in the W2 column `m=3`,
`eps=0.20` (`B = 0.125, 0.210, 0.273`; `z` falls from 5.8--6.1 to 4.2--4.4),
so that column has no certified crossing at 10^6 walkers.  The legacy fields
`status="bisected"`, `b0=0.2816`, `b0_bracket=[0.2726, 0.2909]` stored for
that chain in `w2_b0_empirical/B0_empirical.json` are superseded by
`covariance_aware_reclassification.json` (`w2_chains`,
`new_status="no_certified_crossing_at_1e6_walkers"`).  The W1 final map is
unchanged (0 of 96 cells), every other W2 bracket-defining verdict is
unchanged, and all 700 W3 replica verdicts are reproduced bit-for-bit and
unchanged (`w3_jitter/covariance_aware_recheck.json`).  Source:
`artifacts/data/exact_m_prr_upgrade/covariance_aware_reclassification.json`
and `covariance_aware_reclassification_summary.txt`.

## Stored-count classifier sensitivity

The primary sensitivity grid used smoothing bandwidth
`h = 0.03, 0.04, 0.05` and relative-prominence floor
`r = 0.03, 0.05, 0.07`, with the five-sigma condition retained (the four
sensitive cells are the same under the peak-only and the covariance-aware
statistic).
Four of the 96 final W1 cells changed mode count somewhere on this 3 by 3
grid: the `m=3` cells `(eps,B)=(0.05,4)`, `(0.075,4)`, `(0.10,4)`, and
`(0.175,0.5)`.  The principal `m=3`, `m=5`, and `d=3` anchors retained their
reported mode counts throughout the wider grid `h=0.02,...,0.08` and
`r=0,0.01,0.03,0.05,0.07,0.10`.

W2 probes were deliberately concentrated near the baseline decision
boundaries.  The following ranges are geometric midpoints of brackets that
are supported by the stored probes, across the nine primary classifier
settings.  They are not fresh bisections or extrapolations.

| m | eps | bracketed midpoint range | censored settings |
|---:|---:|---:|:---|
| 2 | 0.05 | 6.16884--7.17884 | 3/9 right-censored above 8 |
| 2 | 0.10 | 6.16884--7.82858 | 3/9 right-censored above 8 |
| 2 | 0.15 | none | 9/9 right-censored above 8 |
| 2 | 0.20 | none | 9/9 right-censored above 8 |
| 3 | 0.05 | 4.15454--5.18736 | 4/9 left-censored below 4.08759 |
| 3 | 0.10 | 3.08442--3.62850 | 3/9 right-censored above 3.66802 |
| 3 | 0.15 | 1.55058--1.55058 | 3/9 below 1.41421; 3/9 above 1.68179 |
| 3 | 0.20 | none | 9/9 no certified crossing (covariance-aware) |

The declared baseline classifier is `h=0.04`, `r=0.05`.  Its brackets and
midpoints are stored in `classifier_sensitivity.json` (peak-only convention)
and, under the covariance-aware statistic, in the `sensitivity_new_rule`
block of `covariance_aware_reclassification.json`; the two agree for every
row above except `(3, 0.20)`, where the peak-only file records a superseded
bracket `0.162105--0.281630`.  Operational
threshold values are classifier-dependent by construction; the sensitivity
table should accompany, not replace, the declared baseline definition.

## Independent seeds

Three independent deterministic streams, each with one million walkers, gave:

| configuration | mode counts | maximum common-index peak span | kill-fraction range |
|:---|:---|---:|:---|
| m3 anchor, eps=0.10, B=1 | 3,3,3 | 0.02 | 0.776153--0.776589 |
| m3 threshold lower side, B=3.50 | 3,3,3 | 0 | 0.980694--0.981178 |
| m3 threshold upper side, B=3.64 | 2,2,2 | 0 | 0.982581--0.982689 |
| m3 phase-boundary passing side, eps=0.175, B=0.5 | 3,3,3 | 0.10 | 0.408590--0.408817 |
| m3 phase-boundary failing side, eps=0.175, B=1 | 2,2,2 | 0 | 0.638291--0.638861 |
| m5 anchor, eps=0.10, B=1 | 5,5,5 | 0.02 | 0.551580--0.552851 |

## Time-step halving

Each side used 500,000 walkers.  The 0.1-wide comparison-bin `z` values use
independent deterministic streams; `max|z|` is a diagnostic maximum over the
usable bins and is not multiplicity-adjusted.

| configuration | modes, dt / dt/2 | max peak shift | kill-fraction change | max abs z |
|:---|:---:|---:|:---|---:|
| m3 interior anchor | 3 / 3 | 0.02 | 0.775462 to 0.776370 | 3.271 |
| m3 operational threshold, B=3.57 | 2 / 2 | 0 | 0.981864 to 0.982380 | 2.592 |
| m3 phase boundary, eps=0.175, B=0.5 | 3 / 2 | not defined after mode loss | 0.408044 to 0.409030 | 2.612 |
| m5 interior anchor | 5 / 5 | 0.02 | 0.551458 to 0.551476 | 1.939 |

The phase-boundary flip is retained rather than hidden.  At `dt=0.001`, the
third-peak prominence is 0.0145723 (7.32 percent of the global maximum and
7.49 covariance-aware sigmas), so it passes both criteria.  At `dt=0.0005`,
the candidate prominence is 0.00829782 (4.23 percent and 4.24
covariance-aware sigmas): it fails both the five-sigma criterion and the
five-percent relative floor (under the superseded peak-only convention these
read 10.29 and 5.89 sigmas).  Thus the
interior anchors preserve mode count under halving, while the deliberately
boundary-adjacent case is classifier-sensitive.  No global time-step-stability
claim is supported or made.

