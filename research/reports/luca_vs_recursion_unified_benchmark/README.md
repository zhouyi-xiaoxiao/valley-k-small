# Luca vs Recursion — Unified Benchmark

**Status: WIP scaffold (not yet started).** Directory layout is in place; no code, manuscript, or notes have been written. Populate this README with real content as the report takes shape.

## Intended scope (working title; refine when work begins)

A unified head-to-head benchmark between the **Luca defect-reduced** and **(dense / sparse) recursion** estimators for full-FPT distributions, intended to consolidate the scattered comparisons currently spread across `cross_luca_regime_map`, `exact_recursion_method_guide`, and related ring/grid reports.

## Relationship to existing reports

- `research/reports/cross_luca_regime_map/` — fixed-horizon regime map; this benchmark would extend that to a unified evaluation harness.
- `research/reports/exact_recursion_method_guide/` — methodology reference for the recursion side.

Cross-link or supersede those once scope solidifies.

## Layout

- `code/` — empty
- `manuscript/` — empty (only stale `*.fdb_latexmk` build leftovers)
- `notes/` — empty
- `artifacts/` — empty placeholder subdirs (`data/`, `figures/`, `outputs/`, `tables/`)

## TODO before this report is real

- [ ] Define the benchmark protocol: which lattices, which T grid, which fairness criterion
- [ ] Land code under `code/` (manifest builder + runner + plot/table generators)
- [ ] Draft `manuscript/luca_vs_recursion_unified_benchmark_{en,cn}.tex`
- [ ] Replace this README with a real one matching the style of `cross_luca_regime_map/README.md` (Key policy → Current snapshot → Outputs → Reproduce)
