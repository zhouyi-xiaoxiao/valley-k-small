# 2D Two-Target 数值方法比较报告（C1 配置）

## 1. 研究目标
在 `2d_two_target_double_peak` 的同一模型设定下，对比五种常用数值路线：
1. 时间域 sparse exact 递推（当前主脚本用法）
2. 时间域 dense 递推（显式 transient 矩阵 Q）
3. 生成函数 AW/Cauchy-FFT 反演（离散 PGF 反演）
4. Giuggioli defect-reduced AW（局部缺陷降阶反演）
5. 线性方程法（只求 MFPT 与 splitting，不求整条 FPT 曲线）

重点比较维度：`FPT 曲线精度`、`MFPT 偏差`、`运行时间`、`适用场景`。

## 2. 实验设置
- 网格与边界：`N=31`，四边反射。
- 运动参数：`q=0.2`，局部 bias 强度 `delta=0.2`。
- 几何：C1（balanced double peak）。
- 起点/目标（0-based）：start=[14, 14], m1=[21, 14], m2=[6, 6]。
- 主比较时域上限：`t_max_main=6000`，停止阈值 `surv_tol=1e-13`。
- AW 参数：`t_max_aw=800`，`oversample=2`，`r_pow10=8.0`，对应 `m=2048`。
- 说明：AW 行仅对 `1..t_max_aw` 的时间窗做反演，不等同于全时域求和后的 MFPT。

## 3. 方法流程（逐步）
### 3.1 Sparse exact 递推（主方法）
1. 在全状态空间上做一步转移更新。
2. 读取本步落在 `m1,m2` 的质量，记为 `f1(t), f2(t)`。
3. 将 `m1,m2` 位置概率清零，继续下一步。
4. 得到 `f_any(t)=f1(t)+f2(t)` 与 `S(t)`。

### 3.2 Dense 递推（Q 矩阵）
1. 构造 transient 子矩阵 `Q` 与吸收向量 `r1,r2`。
2. 用 `u_t = u_{t-1} Q` 推进；每步 `f_i(t)=u_{t-1} r_i`。
3. 与 sparse 递推数学等价，但每步成本更高。

### 3.3 AW/Cauchy-FFT 反演
1. 用 `F_i(z)= z α (I-zQ)^(-1) r_i` 计算 PGF。
2. 在圆周 `z_k = r exp(i2πk/m)` 采样。
3. 通过 FFT 取系数，恢复 `f_i(t)`。
4. 总曲线 `f_any=f1+f2`。

### 3.4 Giuggioli defect-reduced AW
1. 将局部异质性写成 defect 对（与无缺陷基底比较得到）。
2. 每个 `z_k` 上用 Woodbury/defect 小系统恢复关键 propagator。
3. 用两目标 renewal 2x2 方程求 `F_1(z_k), F_2(z_k)`，再 FFT 反演。

### 3.5 线性方程（MFPT/splitting）
1. 解 `(I-Q)m=1` 得 MFPT。
2. 解 `(I-Q)u_i=r_i` 得 splitting 概率 `p_i`。
3. 不输出整条 FPT，但 MFPT 最稳健。

## 4. 结果对比
### 4.1 运行时间

| 方法 | 运行时间 (s) |
|---|---:|
| Sparse exact 递推 | 0.0551 |
| Dense 递推 (Q) | 0.0910 |
| AW/Cauchy 反演 | 35.8544 |
| AW defect-reduced (Giuggioli) | 57.3882 |
| 线性方程 (MFPT/splitting) | 0.0184 |

### 4.2 与 sparse exact 的分布误差

| 对比项 | L1 误差 | L∞ 误差 |
|---|---:|---:|
| Dense vs Sparse (到共同步长) | 9.212e-15 | 1.924e-18 |
| AW vs Sparse (1..t_max_aw) | 9.912e-10 | 1.426e-12 |
| AW-defect vs Sparse (1..t_max_aw) | 9.912e-10 | 1.426e-12 |

### 4.3 关键统计量

| 方法 | mass_any | tail | MFPT(截断/精确) | 峰1 | 峰2 |
|---|---:|---:|---:|---:|---:|
| Sparse exact | 0.850786 | 0.149214 | 1583.479 | 35 | 284 |
| Sparse exact (1..t_max_aw) | 0.297030 | 0.702970 | 111.653 | 35 | 284 |
| Dense recursion | 0.850786 | 0.149214 | 1583.479 | 35 | 284 |
| AW inversion | 0.297030 | 0.702970 | 111.653 | 35 | 284 |
| AW defect-reduced | 0.297030 | 0.702970 | 111.653 | 35 | 284 |
| 线性方程 (精确) | 1.000000 | 0.000000 | 3011.214 | - | - |

### 4.4 Giuggioli 缺陷规模（本案例）

- local bias sites = `317`，defect pairs = `632`，defect nodes = `326`。

### 4.5 截断导致的 MFPT 偏差（sparse exact）

| t_max | 吸收质量 | 尾部质量 | MFPT 截断值 | 相对误差(对线性方程) |
|---:|---:|---:|---:|---:|
| 300 | 0.116714 | 0.883286 | 19.294 | -99.359% |
| 600 | 0.241807 | 0.758193 | 73.099 | -97.572% |
| 1200 | 0.389579 | 0.610421 | 203.559 | -93.240% |
| 2400 | 0.581766 | 0.418234 | 540.034 | -82.066% |
| 6000 | 0.850786 | 0.149214 | 1583.479 | -47.414% |

## 5. 结论（本场景）
1. `FPT 曲线形状`：sparse exact 与 dense recursion 基本一致，dense 仅作为验证基线。
2. `效率`：sparse exact 仍是本 C1 配置最稳健高效的整曲线基线；AW 路线主要成本来自 z 域线性求解。
3. `Giuggioli defect-reduced`：在本配置已可复现同窗分布，但由于 defect 规模不小，速度优势不一定出现。
4. `MFPT`：长尾显著时，截断求和低估明显；线性方程法给出最稳健 MFPT。
5. `实务建议`：
   - 需要完整双峰曲线：优先 sparse exact；
   - 只要 MFPT/splitting：优先线性方程；
   - 需要变换域分析或频繁多 t 查询：可用 AW；若缺陷很少（M<<N）再考虑 defect-reduced AW。

## 6. 产物与复现
- 数值摘要：`data/method_comparison_c1.json`
- 截断扫描表：`data/method_comparison_c1_truncation.csv`
- 曲线对比图：`figures/method_compare_c1_fpt_overlay.pdf`
- 运行时间图：`figures/method_compare_c1_runtime.pdf`
- 复现命令：
```bash
.venv/bin/python reports/grid2d_two_target_double_peak/code/compare_numeric_methods.py
```
