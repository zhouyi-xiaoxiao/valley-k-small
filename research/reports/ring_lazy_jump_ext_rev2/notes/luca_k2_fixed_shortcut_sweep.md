# Luca K=2 fixed-shortcut sweep

## Meeting question

Check the first-passage distribution for a lazy nearest-neighbour ring with one
directed shortcut:

- `N = 100`
- `K = 2`
- `q = 2/3`
- fixed directed shortcut `u = 6 -> v = 56` in paper indexing
- shortcut rule: `P(u -> v) = beta * (1-q)` and
  `P(u -> u) = (1-beta) * (1-q)`
- start positions `n0 = 1, ..., 6`

The default implementation treats the first-passage target as `v = 56`, which
is the literal endpoint named in the meeting request. The script also supports
`--target-paper <site>` so older target conventions can be rerun without code
changes.

## Test framework

1. Build the exact lazy-ring transition by matrix-free time propagation.
2. For each `(n0, beta)`, compute the first-passage PMF `f(t)` up to
   `tmax = 12000`.
3. Detect local peaks with the report's existing paper-style rule:
   `hmin = 1e-12`, `second_rel_height = 0.01`.
4. Mark a clear double peak only when there are two filtered local peaks,
   their separation is at least `10`, and the inter-peak valley is at most
   `0.9` of the higher peak.
5. Compare the result with Luca's proposed threshold
   `beta_c = 2q / ((1-q)N) = 0.04`.

## Reproduce

Run from the repo root:

```bash
.venv/bin/python research/reports/ring_lazy_jump_ext_rev2/code/luca_k2_fixed_shortcut_sweep.py
```

Main outputs:

- `artifacts/data/luca_k2_fixed_shortcut_config.json`
- `artifacts/data/luca_k2_fixed_shortcut_metrics.csv`
- `artifacts/data/luca_k2_fixed_shortcut_summary.csv`
- `artifacts/data/luca_k2_fixed_shortcut_selected_curves.csv`
- `artifacts/tables/luca_k2_fixed_shortcut_summary.tex`
- `artifacts/figures/luca_k2_fixed_shortcut_double_peak_map.pdf`
- `artifacts/figures/luca_k2_fixed_shortcut_peak_times.pdf`
- `artifacts/figures/luca_k2_fixed_shortcut_representative_fpt.pdf`

## Current readout

With target fixed at `v = 56`, the answer depends on what is meant by
double peak.

- If double peak means two mathematical local maxima, `n0 = 1, 2, 3` still
  have two local maxima above Luca's `beta_c = 0.04`.
- If double peak means a visually clear two-peak shape, using
  `hv / min(h1,h2) <= 0.8`, no case remains double-peaked at or above
  `beta_c`. At `beta=0.04`, the valley is already shallow:
  `hv / min(h1,h2) = 0.887--0.891` for `n0=1,2,3`.
- If an even stronger visual criterion `hv / min(h1,h2) <= 0.6` is used,
  only small beta values qualify, up to about `beta=0.018`.

Thus, under this target convention, Luca's formula is not an exact boundary
for the existence of any two local maxima, but it is supported as a practical
boundary for visually meaningful double peaks. It is also consistent with
Luca's caveat that the formula is not the whole story and that `n0` must enter
the actual condition.
