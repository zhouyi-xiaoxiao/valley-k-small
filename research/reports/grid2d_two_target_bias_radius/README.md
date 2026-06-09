# Grid2D Two-Target Bias-Radius Scaffold

This WIP report prepares the 2D two-target scan where the start and far target
are fixed and the near target is placed by radius and angle relative to a bias
direction. It intentionally contains only a small exact smoke case; it does not
claim or classify double peaks.

## Model

- State space: rectangular grid `{0,...,Lx-1} x {0,...,Ly-1}`.
- Boundary rule: reflecting attempted-outside-stays. Any move that would leave
  the grid adds its probability to the current state.
- Absorbing set: `{a_near, a_far}`. Absorbing rows are self-loops in the kernel,
  and the exact first-passage recursion removes mass immediately when it lands
  on either target.
- First-passage channels:
  `f_total(t) = f_near(t) + f_far(t)`.

## Bias Rule

The smoke case uses a global bias. Starting from four nearest-neighbour move
probabilities `q/4` and stay probability `1-q`, bias strength `b` moves absolute
probability mass from stay to the global bias direction:

```text
p_bias_direction = q/4 + b
p_other_direction = q/4
p_stay = 1 - q - b
```

The implementation requires `0 <= b <= 1-q`, so all probabilities remain
nonnegative and row sums remain one. Later scans can vary `b` using the same
kernel builder.

## Near-Target Geometry

The start `x0`, far target `a_far`, and bias direction are fixed. For each near
target candidate:

- `r` is the Euclidean distance from `x0` to `a_near`.
- `theta` is the angle of `a_near - x0` measured relative to the bias direction.
- No theta aggregation is performed in this scaffold. Each `(r, theta)` request
  maps to a single rounded grid coordinate, and duplicate or invalid candidates
  are skipped.

## Smoke Outputs

Run:

```bash
python3 research/reports/grid2d_two_target_bias_radius/code/run_smoke.py
```

Expected outputs:

- `artifacts/outputs/smoke_fpt_channels.csv`
- `artifacts/figures/smoke_fpt_channels.pdf`
- `artifacts/data/smoke_summary.json`

The smoke script asserts:

- nonnegative probabilities,
- row-stochasticity error `< 1e-12`,
- mass-balance error `< 1e-10`,
- `f_total = f_near + f_far` error `< 1e-10`.

## Small Heatmap Scan

Run:

```bash
python3 research/reports/grid2d_two_target_bias_radius/code/run_small_heatmap.py
```

This bounded scan fixes `theta=0`, placing each near target along the global
eastward bias direction. It scans a small grid of bias strengths `b` and
near-target distances `r`, then classifies `f_total(t)` with the shared
distribution-shape classifier. The heatmap color is the classifier score,
not a double-peak claim; a row is listed as a double-peak candidate only when
the classifier label is exactly `double_peak`.

Expected outputs:

- `artifacts/data/grid2d_bias_radius_scan_config.csv`
- `artifacts/data/grid2d_bias_radius_scan_metrics.csv`
- `artifacts/data/grid2d_bias_radius_scan_summary.json`
- `artifacts/figures/grid2d_bias_radius_heatmap_theta0.pdf`
- `artifacts/figures/grid2d_representative_fpt_decomp_*.pdf`
- `artifacts/tables/grid2d_double_peak_candidates.csv`
- `notes/SUMMARY.md`
