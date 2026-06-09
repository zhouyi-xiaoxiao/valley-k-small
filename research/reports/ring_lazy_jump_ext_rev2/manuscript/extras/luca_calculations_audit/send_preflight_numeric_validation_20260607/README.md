# Sendable preflight numerical validation

- corrected plus/plus formula vs direct matrix: 4.163336e-17
- compact closed form vs direct matrix: 1.110223e-16
- corrected Eq. (14) killed propagator vs absorbing matrix: 1.176836e-14
- old reversed-bracket Eq. (14) killed propagator vs absorbing matrix: 2.000000e-01
- orthogonality identities max residual: 6.339373e-13
- hard-route time convolution vs direct shortcut PMF: 6.938894e-18
- Eq. (57) five-group sum vs direct shortcut PMF: 5.204170e-18
- Eq. (57) five-group sum vs hard-route convolution: 5.204170e-18
- kernel-to-fully-expanded identities: 2.664535e-15
- min(s1-gamma1) over sampled betas: 9.870951e-05
- min(alpha1-s1) over sampled betas: 6.633020e-06
- max denominator residual at spectral s1: 1.116295e-08
- max normalized denominator residual at spectral s1: 1.743328e-10
- double-peak summary matches email claim: True
- beta_c reference value for the N=100 scan: 0.040000

Clear double-peak sampled beta brackets:

n0 | no before | first clear | last clear | no after | clear at beta>=beta_c
-- | --------- | ----------- | ---------- | -------- | ----------------------
1 | 0.001 | 0.002 | 0.030 | 0.032 | 0
2 | 0.001 | 0.002 | 0.030 | 0.032 | 0
3 | 0.000 | 0.001 | 0.030 | 0.032 | 0
4 | -- | -- | -- | -- | 0
5 | -- | -- | -- | -- | 0
6 | -- | -- | -- | -- | 0

These are sampled-grid brackets, not analytic threshold proofs.

Outputs:

- resolvent_closed_form_checks.csv
- eq14_killed_propagator_checks.csv
- orthogonality_identity_failures.csv
- hard_route_convolution_checks.csv
- pole_checks.csv
- double_peak_metrics.csv
- double_peak_summary.csv
- summary.json