# Luca quick sign test

This is the numerical test requested in Luca's 2026-06-04 reply.

## Verdict

- The actual stochastic shortcut matrix, where `lambda = beta(1-q)` is
  moved from the self-loop at `u` to the directed edge `u -> v`, agrees
  with Eq. (32) only with the corrected plus/plus sign.
- Luca's Eq. (29), if used literally as printed, agrees with the
  original minus/minus Eq. (32). This shows that the sign inconsistency
  is already present in the printed Eq. (29) when it is interpreted as a
  stochastic shortcut from `u` to `v`.

## Max Errors Over The Test Grid

- original Eq. (32) vs stochastic matrix: `3.669746e-01`
- corrected Eq. (32) vs stochastic matrix: `2.775558e-16`
- literal Eq. (29) ratio vs original Eq. (32): `1.318390e-16`
- stochastic-sign Eq. (29) ratio vs corrected Eq. (32): `5.551115e-17`
- Eq. (19) W(n0,u,z) vs absorbing matrix: `1.043610e-14`
- Eq. (28) W(u,u,z) vs absorbing matrix: `1.687539e-14`

## Representative Rows

| N | q | beta | u | v | n0 | z | stochastic matrix | literal Eq. (29) | Eq. (32) original | Eq. (32) corrected |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 0.666667 | 0.285714 | 5 | 0 | 2 | 0.5 | 0.0440965010385 | 0.0429614433114 | 0.0429614433114 | 0.0440965010385 |
| 10 | 0.666667 | 0.285714 | 5 | 0 | 2 | 0.8 | 0.197025316799 | 0.173752283343 | 0.173752283343 | 0.197025316799 |
| 10 | 0.666667 | 0.285714 | 5 | 0 | 2 | 0.95 | 0.532769134231 | 0.394627514541 | 0.394627514541 | 0.532769134231 |

All site indices in this test are zero-based. The first case uses the
parameters from Luca's figure: `N=10`, `q=2/3`, `beta=2/7`,
`u=5`, `v=0`, so `|u-v|=N/2`.
