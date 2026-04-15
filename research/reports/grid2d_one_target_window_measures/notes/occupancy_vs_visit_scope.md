# Occupancy vs Visit Scope

This report isolates one technical point from the canonical gating report:

1. `occupancy share` is a time-weighted window-conditioned distribution.
2. `ever-visit probability` is a path-event probability.
3. The two agree with Monte Carlo only when Monte Carlo estimates the same observable.

The geometry and baseline parameters are inherited from the symmetric single-target case in
`research/reports/grid2d_one_two_target_gating/`.
