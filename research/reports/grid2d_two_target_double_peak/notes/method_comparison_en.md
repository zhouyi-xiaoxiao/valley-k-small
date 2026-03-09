# 2D Two-Target Numerical Method Comparison (C1 Configuration)

## 1. Objective
Under the same `2d_two_target_double_peak` model setup, compare five numerical approaches:
1. Time-domain sparse exact recursion (main pipeline method)
2. Time-domain dense recursion (explicit transient matrix `Q`)
3. Luca/Giuggioli defect-reduced inversion (Method C)
4. Full AW/Cauchy-FFT inversion (Method C0 baseline)
5. Linear-system method (MFPT and splitting only; no full FPT curve)

Main comparison axes: `FPT curve accuracy`, `MFPT robustness`, `runtime`, and `practical use cases`.

## 2. Experimental Setup
- Grid and boundary: `N=31`, reflecting on all four sides.
- Motion parameters: `q=0.2`, local-bias strength `delta=0.2`.
- Geometry: C1 (balanced double-peak case).
- Start/targets (0-based): start=[14, 14], m1=[21, 14], m2=[6, 6].
- Main time horizon: `t_max_main=6000`, stop threshold `surv_tol=1e-13`.
- AW parameters: `t_max_aw=800`, `oversample=2`, `r_pow10=8.0`, giving `m=2048`.
- Note: AW is inverted only on `1..t_max_aw`; this is not a full-time MFPT evaluation.

## 3. Method Workflow (Step by Step)
### 3.1 Sparse exact recursion (main method)
1. Propagate one step on the full state space.
2. Read probability mass landing on `m1,m2` at this step as `f1(t), f2(t)`.
3. Set target-site probabilities to zero ("take out") and continue.
4. Obtain `f_any(t)=f1(t)+f2(t)` and `S(t)`.

### 3.2 Dense recursion (Q-matrix)
1. Build transient matrix `Q` and absorption vectors `r1,r2`.
2. Iterate `u_t = u_{t-1} Q`; per step `f_i(t)=u_{t-1} r_i`.
3. Mathematically equivalent to sparse recursion, but with higher per-step cost.

### 3.3 Luca/Giuggioli defect-reduced inversion (Method C)
1. Defect decomposition: `Q = Q0 + U Delta V^T` with defect-pair dimension `M`.
2. Woodbury recovery on selected node sets (`s,m1,m2 -> m1,m2`):
   `P_ST = P0_ST + z P0_SU Delta [I - z P0_VU Delta]^(-1) P0_VT`.
3. Two-target renewal closure (2x2 system):
   `[P_s,m1; P_s,m2] = [[P_m1,m1, P_m2,m1],[P_m1,m2, P_m2,m2]] [F1;F2]`.
4. Solve `F(z)` pointwise on the contour, then FFT-invert to `f_i(t)`.
5. Complexity: `O(m*(C_base(n_T) + M^3) + m log m)`.

### 3.3b Full AW/Cauchy-FFT inversion (Method C0 baseline)
1. Direct PGF solve: `F_i(z)= z alpha (I-zQ)^(-1) r_i`.
2. Sample on `z_k = r exp(i2pi k/m)` and FFT-invert.
3. Complexity: `O(m n_T^3 + m log m)` for dense direct solves.

### 3.4 Linear system (MFPT/splitting)
1. Solve `(I-Q)m=1` for MFPT.
2. Solve `(I-Q)u_i=r_i` for splitting probabilities `p_i`.
3. Does not output full FPT curve, but is most robust for MFPT.

## 4. Results
### 4.1 Runtime

| Method | Runtime (s) |
|---|---:|
| Sparse exact recursion | 0.0561 |
| Dense recursion (Q) | 0.0919 |
| Luca defect-reduced (Method C) | 78.0223 |
| Full AW/Cauchy (Method C0) | 47.2622 |
| Linear system (MFPT/splitting) | 0.0213 |

### 4.2 Distribution errors vs sparse exact baseline

| Comparison | L1 error | Linf error |
|---|---:|---:|
| Dense vs Sparse (common horizon) | 9.212e-15 | 1.924e-18 |
| Luca-defect (C) vs Sparse (1..t_max_aw) | 9.912e-10 | 1.426e-12 |
| Full AW (C0) vs Sparse (1..t_max_aw) | 9.912e-10 | 1.426e-12 |

### 4.3 Key statistics

| Method | mass_any | tail | MFPT (truncated/exact) | peak1 | peak2 |
|---|---:|---:|---:|---:|---:|
| Sparse exact | 0.850786 | 0.149214 | 1583.479 | 35 | 284 |
| Sparse exact (1..t_max_aw) | 0.297030 | 0.702970 | 111.653 | 35 | 284 |
| Dense recursion | 0.850786 | 0.149214 | 1583.479 | 35 | 284 |
| Luca defect-reduced | 0.297030 | 0.702970 | 111.653 | 35 | 284 |
| Full AW inversion | 0.297030 | 0.702970 | 111.653 | 35 | 284 |
| Linear system (exact) | 1.000000 | 0.000000 | 3011.214 | - | - |

### 4.4 MFPT truncation bias (sparse exact)

| t_max | absorbed mass | tail mass | truncated MFPT | relative error (vs linear-system MFPT) |
|---:|---:|---:|---:|---:|
| 300 | 0.116714 | 0.883286 | 19.294 | -99.359% |
| 600 | 0.241807 | 0.758193 | 73.099 | -97.572% |
| 1200 | 0.389579 | 0.610421 | 203.559 | -93.240% |
| 2400 | 0.581766 | 0.418234 | 540.034 | -82.066% |
| 6000 | 0.850786 | 0.149214 | 1583.479 | -47.414% |

### 4.5 Defect scale and practical impact on C1
- C1 defect profile in this implementation:
  - local-bias sites = `317`
  - defect pairs = `632`
  - defect nodes = `326`
- Complexity-side estimate for solve core in the current implementation (pair-level `M=632`): about `3.2x~3.5x` reduction vs full `n_T` solve.
- Measured wall-clock result on C1: Luca-defect (Method C) is still slower (`78.0s`) than full AW baseline (Method C0, `47.3s`).
- Reason: at this defect size, non-solve overhead (baseline Green evaluations, matrix assembly, constants) dominates enough to offset solve-core reduction.
- If defect support is much sparser (`M << n_T`), the defect-reduced route is still expected to become advantageous.

## 5. Conclusions (for this scenario)
1. `FPT shape`: sparse exact and dense recursion are effectively identical; dense mainly serves as a correctness baseline.
2. `Efficiency`: sparse exact remains the strongest full-curve baseline on this C1 instance.
3. `Method C (Luca-defect)`: distribution accuracy is excellent, but this specific C1 runtime is slower than Method C0 because defect support is not small enough.
4. `MFPT`: with heavy tails, truncation causes severe underestimation; linear-system MFPT is the robust reference.
5. `Practical recommendation`:
   - Need full double-peak FPT curves: use sparse exact recursion.
   - Need MFPT/splitting only: use linear systems.
   - Need transform-domain analysis: use Method C0 as direct baseline; switch to Method C when defect support is truly sparse (`M << n_T`).

## 6. Constructed Luca-Fast Case (LF1)
- Setup: `N=41`, `n_T=1679`, single local-bias site (`M_pairs=2`), `t_max_main=12000`, `t_max_aw=80`.
- Runtime (seconds): Luca `0.0198`, Linear `0.0477`, Sparse `0.1754`, Dense `1.6187`, Full AW `22.8746`.
- In this constructed regime, Luca is the fastest among all five methods.
- Configuration figure (same visual family as external detailed config panels):
  - `figures/luca_fast_case_config_detailed.pdf`
- Runtime figure:
  - `figures/luca_fast_case_runtime.pdf`

## 7. Artifacts and Reproduction
- Numeric summary: `data/method_comparison_c1.json`
- Truncation scan table: `data/method_comparison_c1_truncation.csv`
- FPT overlay figure: `figures/method_compare_c1_fpt_overlay.pdf`
- Runtime bar figure: `figures/method_compare_c1_runtime.pdf`
- Reproduction command:
```bash
.venv/bin/python reports/grid2d_two_target_double_peak/code/compare_numeric_methods.py
```
