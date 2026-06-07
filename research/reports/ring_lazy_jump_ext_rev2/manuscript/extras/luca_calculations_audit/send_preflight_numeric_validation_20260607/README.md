# Sendable preflight numerical validation

- corrected plus/plus formula vs direct matrix: 4.163336e-17
- compact closed form vs direct matrix: 1.110223e-16
- min(s1-gamma1) over sampled betas: 9.870951e-05
- min(alpha1-s1) over sampled betas: 6.633020e-06
- max denominator residual at spectral s1: 1.116295e-08
- max normalized denominator residual at spectral s1: 1.743328e-10
- double-peak summary matches email claim: True

Outputs:

- resolvent_closed_form_checks.csv
- pole_checks.csv
- double_peak_metrics.csv
- double_peak_summary.csv
- summary.json