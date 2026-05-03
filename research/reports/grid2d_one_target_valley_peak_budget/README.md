# Grid2D One Target — Valley/Peak Budget

**Status: 3-page short report. Manuscript landed; code and notes still pending.**
Tracking: [#6](https://github.com/zhouyi-xiaoxiao/valley-k-small/issues/6).

## Sub-series

Part of the `grid2d_one_target_*` sub-series. See `grid2d_one_target_base`
for shared problem setup, notation, and conventions; this report focuses on
**valley/peak budget observables** specifically.

## Scope

Valley/peak "budget" analysis for the single-target 2D-grid FPT distribution
under a permeable membrane. The report compares the three windows
`peak1`, `valley`, `peak2` along two complementary axes:

1. **Normalized observables** — relative timing ratio
   `E[τ | τ < T, T ∈ W] / E[T | T ∈ W]`, the outside-time share, and the
   membrane-crossing probability `P(τ_mem < T | T ∈ W)`.
2. **Absolute budgets** (in expected step counts) — the *outside budget*
   (pre-hit steps spent outside the corridor band) and the *post-crossing
   budget* (steps remaining after the first membrane crossing and before
   target hit).

The headline finding: at fixed control parameters, **the valley-vs-peak2
separation is dominated by the outside budget rather than by normalized exit
timing**, and the membrane permeability `κ` acts primarily by enlarging the
post-crossing budget rather than by raising the crossing probability.

## Outputs

- Manuscript: `manuscript/grid2d_one_target_valley_peak_budget_{en,cn}.tex`
  (+ PDFs, 3 pages each).
- Figures: `artifacts/figures/fig{1,2,3}_*.{pdf,png}` (3 figures).
- Build artefacts: `manuscript/build/` (auxiliary; not committed).

## Layout

- `code/` — generation scripts (currently absent; the `__pycache__` traces
  the prior pipeline that produced the figures, source not yet recommitted).
- `manuscript/` — `.tex` sources + compiled PDFs (en/cn).
- `notes/` — empty.
- `artifacts/` — `figures/` (PNG + PDF) and the `_fig1_vector_build/`
  scaffold for re-rendering the geometry diagram as vector PDF.

## Reproduce

From `manuscript/`:

```bash
latexmk -xelatex -interaction=nonstopmode -auxdir=build -emulate-aux-dir \
  -cd grid2d_one_target_valley_peak_budget_en.tex
latexmk -xelatex -interaction=nonstopmode -auxdir=build -emulate-aux-dir \
  -cd grid2d_one_target_valley_peak_budget_cn.tex
```

`manuscript/figures` is a symlink to `../artifacts/figures` so
`\includegraphics{figures/fig...}` resolves.

## TODO

- [ ] Recover or rewrite the figure-generation scripts under `code/`.
- [ ] Replace `figures/fig*.pdf` (currently sips-rasterised from PNG) with
      vector PDFs from the original matplotlib pipeline.
- [ ] Cross-reference the related sub-series: `grid2d_one_target_exit_timing`,
      `grid2d_one_target_window_measures`, `grid2d_one_two_target_gating`.
