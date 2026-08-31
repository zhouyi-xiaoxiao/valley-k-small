# Robustness-results summary

This file is a compact reading guide to the machine-readable records under
`artifacts/data/exact_m_prr_upgrade/robustness/`.  Values below are descriptive
diagnostics, not preregistered hypothesis tests.

## Stored-count classifier sensitivity

The primary sensitivity grid used smoothing bandwidth
`h = 0.03, 0.04, 0.05` and relative-prominence floor
`r = 0.03, 0.05, 0.07`, with the five-Poisson-sigma condition retained.
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
| 3 | 0.20 | 0.162105--0.281630 | none |

The declared baseline classifier is `h=0.04`, `r=0.05`.  Its brackets and
midpoints are stored exactly in `classifier_sensitivity.json`.  Operational
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
10.29 Poisson sigmas), so it passes both criteria.  At `dt=0.0005`, the
candidate prominence is 0.00829782 (4.23 percent and 5.89 sigmas): it passes
the five-sigma criterion but fails the five-percent relative floor.  Thus the
interior anchors preserve mode count under halving, while the deliberately
boundary-adjacent case is classifier-sensitive.  No global time-step-stability
claim is supported or made.

