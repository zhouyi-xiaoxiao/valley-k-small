# Round 12 reviewer A — fixed-budget gradient validation

Date: 2026-07-13

## Independent checks

I inspected `validate_modality_susceptibility.py`, its JSON/CSV outputs, and
Eqs. `modality-susceptibility`--`optimal-redistribution` in the manuscript.
The following independent paths were compared on a frozen 11-state killed
CTMC:

- basis Fréchet derivatives of the matrix exponential;
- a 160-point Gauss--Legendre Duhamel convolution kernel;
- 256 held-out budget-zero five-point derivatives;
- a state-permutation equivariance test;
- the closed-form constrained optimum against 20,000 random feasible unit
  directions.

## Results

- Duhamel/Frechet relative L2 discrepancy: `3.25e-15`.
- Maximum basis-linearity relative discrepancy: `1.11e-12`.
- Maximum held-out five-point relative discrepancy: `2.38e-8`.
- Permutation-equivariance relative discrepancy: `1.15e-15`.
- Best random response / closed-form optimum: `0.933145`, never exceeding the
  optimum.
- Budget and metric-norm residuals are below the declared gates.

At the production finite encounter fold, the near-rate chain-rule derivative
reconstructs the saved log-rate transversality to `6.78e-15` relative error.
The orthogonal fixed-state-sum near/far redistribution has nonzero
transversality `-1.1620967e-5`.

## Boundary review

The artifact correctly withholds finite-amplitude, positivity-constrained,
binary-mask, moving-support, and continuum optimality claims.  No numerical or
algebraic defect was found.
