# Timing Observables for `grid2d_one_target_exit_timing`

This note records the exact timing observables used in the companion report.

## Baseline Geometry

The report fixes the symmetric one-target corridor-only soft-bias baseline:

- `Lx = 60`, `Wy = 15`
- `start = (7, 7)`, `target = (58, 7)`
- corridor band `C = {(x, y): 5 <= y <= 9}`
- membrane span on the upper/lower corridor interfaces for `5 <= x <= 54`
- global drift `bx = -0.08`
- local corridor bias:
  - `delta_core = 0.8` on `5 <= x <= 54`, `5 <= y <= 9`
  - `delta_open = 0.0` on the left/right corridor openings
- symmetric membrane permeability continuation:
  - `kappa_c2o = kappa_o2c = kappa`
  - `kappa in {0, 0.00025, 0.0005, 0.00075, 0.0010, 0.00125, 0.0015, 0.00175, 0.0020, 0.0025, 0.0030, 0.0040, 0.0050, 0.0060}`

## Hitting-Time Windows

For each `kappa`, the exact first-passage pmf `f(t)` is recomputed, then the three windows are defined by the repo-native rule:

1. detect two credible peaks on the smoothed `f(t)`
2. define the valley as the minimum between the two peaks
3. use the common half-width

```text
half = max(8, min(26, floor((t_peak2 - t_peak1) / 7)))
```

and form the three windows:

```text
peak1  = [t_peak1 - half,  t_peak1 + half]
valley = [t_valley - half, t_valley + half]
peak2  = [t_peak2 - half,  t_peak2 + half]
```

## Event Definitions

Let `T` be the first-passage time to the target.

### 1. Corridor-exit time `tau_out`

Define the outside set

```text
O = complement of the corridor band C
```

within the transient state space. Then

```text
tau_out = inf { t >= 1 : X_t in O }.
```

This is the first time the walker leaves the corridor band, regardless of whether this happens through the left opening or by crossing a membrane.

Important consequence:

- when `kappa = 0`, `tau_out` can still be nonzero, because the left opening remains available
- therefore `tau_out` is a broader detour observable than membrane crossing

### 2. Membrane-crossing time `tau_mem`

Let `E_mem^(c->o)` be the set of directed corridor-to-outside membrane edges. Then

```text
tau_mem = inf { t >= 1 : (X_{t-1}, X_t) in E_mem^(c->o) }.
```

This event only records genuine membrane crossings.

Important consequence:

- when `kappa = 0`, `tau_mem` is identically absent
- therefore `tau_mem` isolates the membrane-assisted part of the slow branch

## Exact Quantities

For a window `W`, the report computes:

### Joint first-event density

```text
P(tau = t, T in W)
```

for `tau = tau_out` or `tau_mem`.

### Window-conditioned density and CDF

```text
P(tau = t | T in W),
P(tau <= t | T in W).
```

### Window-conditioned event probability

```text
P(tau < T | T in W).
```

This is the total mass of the conditional density.

### Mean event time and relative timing ratio

```text
E[tau | tau < T, T in W],
E[tau | tau < T, T in W] / E[T | T in W].
```

The ratio indicates whether the event tends to occur early or late relative to the typical hitting time in that same window.

## Early / Late / No-Exit Split

For each window `W`, the report first computes `E[T | T in W]` and then uses the window-specific threshold

```text
tau <= 0.5 * E[T | T in W]   -> early
tau >  0.5 * E[T | T in W]   -> late
```

The three-way split is therefore:

- `early_mass`
- `late_mass`
- `no_exit_mass = 1 - P(tau < T | T in W)`

By construction,

```text
early_mass + late_mass + no_exit_mass = 1
```

for every `(kappa, window, observable)`.

## Exact Recursion Sketch

The implementation uses a reusable helper in

- `packages/vkcore/src/vkcore/grid2d/one_two_target_gating/one_target.py`

and combines:

1. a no-event forward recursion

```text
alpha_t(i) = P(X_t = i, T > t, tau > t)
```

2. a backward window committor

```text
beta_t(i) = P(T in W | X_t = i, T > t)
```

3. a one-step event flux into either
   - an event state set (`tau_out`)
   - or a directed event-edge set (`tau_mem`)

The resulting exact first-event density is then normalized by `P(T in W)` to obtain the plotted window-conditioned CDFs and timing ratios.
