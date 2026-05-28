# Reflecting Encounter Mean Validation

This report validates the first exact-computation step for a one-dimensional
two-walker encounter process with reflecting boundaries.

## Model

- Interval: `{0, ..., L-1}`.
- Joint state: `Y_t = (X_t^(1), X_t^(2))`.
- Encounter set: `E = {(k, k): 0 <= k < L}`.
- Encounter time: `tau_E = inf{t >= 0: X_t^(1) = X_t^(2)}`.
- Initial states must satisfy `x1_0 != x2_0`.

Each walker updates synchronously and independently using a lazy nearest-neighbor
transition matrix. For walker `i` at an internal point,

- `P_i(x, x) = 1 - Q_i`
- `P_i(x, x + 1) = Q_i / 2`
- `P_i(x, x - 1) = Q_i / 2`

At the boundary, reflecting means attempted-outside-stays. For example, at
`x = 0`, the attempted left move contributes `Q_i / 2` to `P_i(0, 0)`.

For fixed total mobility the current smoke run uses

```text
Q1 = 2*q0*rho/(1+rho)
Q2 = 2*q0/(1+rho)
```

with only parameter choices satisfying `Q1 <= 1` and `Q2 <= 1`.

## Validation

The joint transition is the product-chain matrix `P1 kron P2`. Diagonal states
are absorbing encounter states. The exact mean first-encounter time is computed
on the transient block `M` using the fundamental matrix

```text
N = (I - M)^(-1)
E[tau_E] = alpha N 1
```

The encounter distribution `f_E(t)` is computed independently by forward
propagation of the transient mass. The validation checks:

- `P1` and `P2` are nonnegative and row-stochastic.
- The joint and absorbing joint matrices are row-stochastic.
- Forward propagation satisfies the mass-balance identity
  `f_E(t) = S(t-1) - S(t)`.
- The distribution mean `sum_t t f_E(t)` matches the fundamental-matrix mean.

## Diagonal-Position Decomposition

The diagonal-position contribution is

```text
f_k(t) = P(tau_E = t, Y_tau = (k, k)).
```

The implementation records these contributions during forward propagation of
the full joint distribution. At each step it propagates to `J_next`, records
`diag(J_next)` as the vector `(f_0(t), ..., f_{L-1}(t))`, sums those entries to
obtain `f_E(t)`, and only then clears the diagonal before continuing. This keeps
the encounter state absorbing without losing the position label of first
encounter.

The required decomposition check is

```text
f_E(t) = sum_k f_k(t)
```

for every recorded time. The smoke run also writes an early contribution window
around the first dominant time. If a later local feature is detected by the
conservative local-maximum rule, it writes a `candidate_late` window as well.
The current representative asymmetric smoke case has no such late local feature,
so no double-peak or late-feature claim is made.

## Outputs

Mean-validation smoke run:

```bash
python research/reports/encounter_reflecting_mean_validation/code/run_smoke.py
```

Generated smoke outputs:

- `artifacts/data/mean_vs_rho_smoke.csv`
- `artifacts/figures/mean_vs_rho_smoke.svg`
- `artifacts/outputs/smoke_summary.json`

Diagonal-decomposition smoke run:

```bash
python research/reports/encounter_reflecting_mean_validation/code/run_diagonal_smoke.py
```

Generated diagonal outputs:

- `artifacts/data/diagonal_asymmetric_f_total.csv`
- `artifacts/data/diagonal_asymmetric_f_by_position.csv`
- `artifacts/data/diagonal_asymmetric_windows.csv`
- `artifacts/figures/diagonal_asymmetric_heatmap.svg`
- `artifacts/outputs/diagonal_smoke_summary.json`
