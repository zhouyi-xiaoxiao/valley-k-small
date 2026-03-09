# Luca Fast Case (Constructed Benchmark)

## 1. Goal
Construct a reproducible setup where Luca/Giuggioli defect-reduced inversion is faster than all comparison methods in this benchmark file.

## 2. Configuration
- Grid: `N=41` (reflecting boundaries).
- Start/targets (0-based): start=[20, 20], m1=[28, 20], m2=[12, 12].
- Motion: `q=0.2`, local-bias `delta=0.2`.
- Local-bias sites: `1` (single-site defect setup).
- Time windows: `t_max_main=12000`, `t_max_aw=80`.

## 3. Runtime

| Method | Runtime (s) |
|---|---:|
| Luca defect-reduced AW | 0.0231 |
| Linear MFPT/splitting | 0.0499 |
| Sparse exact recursion | 0.1715 |
| Dense recursion | 1.6848 |
| Full AW/Cauchy | 25.3149 |

Winner: **Luca defect** (`0.0231s`).

## 4. Accuracy Checks

| Comparison | L1 error | Linf error |
|---|---:|---:|
| Dense vs Sparse (main horizon) | 1.783e-14 | 1.999e-18 |
| Full AW vs Sparse (AW horizon) | 2.135e-10 | 2.680e-12 |
| Luca vs Sparse (AW horizon) | 2.135e-10 | 2.680e-12 |

## 5. Why Luca Is Fast Here
- Defect pairs = `2`, defect nodes = `5`, while transient size is `n_T=1679`.
- This pushes the defect solve core to a tiny system compared with full AW's dense solve scale.
- At the same time, long main-horizon recursion (`t_max_main`) makes sparse/dense iteration less competitive.

## 6. Figures
- Configuration (same visual family as external detailed config): `figures/luca_fast_case_config_detailed.pdf`
- FPT overlay: `figures/luca_fast_case_fpt_overlay.pdf`
- Runtime bar: `figures/luca_fast_case_runtime.pdf`

## 7. Artifacts
- JSON summary: `data/luca_fast_case.json`
