#!/usr/bin/env python3
"""Numerical-method comparison for 2D two-target FPT in the C1 setting."""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from two_target_2d_report import (
    build_case_layout,
    build_transition_arrays,
    find_two_peaks,
    make_cases,
    polyline_points,
    run_exact_two_target,
    to0,
)

Coord = Tuple[int, int]


@dataclass(frozen=True)
class AWGrid:
    m: int
    r: float
    oversample: int
    r_pow10: float


def next_pow2(n: int) -> int:
    if n <= 1:
        return 1
    return 1 << (n - 1).bit_length()


def choose_aw_grid(t_max: int, oversample: int, r_pow10: float) -> AWGrid:
    if t_max <= 0:
        raise ValueError("t_max must be positive")
    if oversample <= 1:
        raise ValueError("oversample must be >= 2")
    m = next_pow2(int(oversample * (t_max + 1)))
    r = float(10.0 ** (-float(r_pow10) / float(m)))
    return AWGrid(m=m, r=r, oversample=oversample, r_pow10=r_pow10)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _idx(N: int, xy: Coord) -> int:
    return xy[1] * N + xy[0]


def build_c1_geometry(*, N: int = 31) -> Tuple[Coord, Coord, Coord, Dict[Coord, str], float]:
    start = to0((15, 15))
    m1 = to0((22, 15))
    m2 = to0((7, 7))
    fast_nodes = [to0((15, 15)), to0((22, 15))]
    slow_nodes = [to0((15, 15)), to0((15, 27)), to0((3, 27)), to0((3, 7)), to0((7, 7))]
    fast_path = polyline_points(fast_nodes)
    slow_path = polyline_points(slow_nodes)
    c1 = [c for c in make_cases() if c.case_id == "C1"][0]
    arrow_map, _, _ = build_case_layout(
        N=N,
        fast_path=fast_path,
        slow_path=slow_path,
        w1=c1.w1,
        w2=c1.w2,
        skip2=c1.skip2,
    )
    return start, m1, m2, arrow_map, float(c1.delta)


def build_c1_transition(
    *,
    N: int = 31,
    q: float = 0.2,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Coord, Coord, Coord]:
    start, m1, m2, arrow_map, delta = build_c1_geometry(N=N)
    src_idx, dst_idx, probs = build_transition_arrays(
        N=N,
        q=q,
        delta=delta,
        arrow_map=arrow_map,
    )
    return src_idx, dst_idx, probs, start, m1, m2


def build_transient_system(
    *,
    N: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    start: Coord,
    m1: Coord,
    m2: Coord,
) -> Dict[str, np.ndarray]:
    n_states = N * N
    P = np.zeros((n_states, n_states), dtype=np.float64)
    np.add.at(P, (src_idx, dst_idx), probs)

    i_start = _idx(N, start)
    i_m1 = _idx(N, m1)
    i_m2 = _idx(N, m2)

    mask = np.ones(n_states, dtype=bool)
    mask[i_m1] = False
    mask[i_m2] = False
    trans_idx = np.where(mask)[0]
    n_t = int(trans_idx.size)

    inv = -np.ones(n_states, dtype=np.int64)
    inv[trans_idx] = np.arange(n_t, dtype=np.int64)
    i_start_t = int(inv[i_start])
    if i_start_t < 0:
        raise ValueError("start cannot be an absorbing target")

    Q = P[np.ix_(trans_idx, trans_idx)]
    r1 = P[trans_idx, i_m1].copy()
    r2 = P[trans_idx, i_m2].copy()
    r_any = r1 + r2

    alpha = np.zeros(n_t, dtype=np.float64)
    alpha[i_start_t] = 1.0

    return {
        "Q": Q,
        "r1": r1,
        "r2": r2,
        "r_any": r_any,
        "alpha": alpha,
        "i_start_t": np.array([i_start_t], dtype=np.int64),
    }


def run_dense_recursion(
    *,
    Q: np.ndarray,
    r1: np.ndarray,
    r2: np.ndarray,
    alpha: np.ndarray,
    t_max: int,
    surv_tol: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    u = alpha.copy()

    f1 = [0.0]
    f2 = [0.0]
    f_any = [0.0]
    surv = [1.0]

    for _ in range(1, t_max + 1):
        # Use dot() instead of '@' here to avoid sporadic BLAS/FPE warnings on some platforms.
        hit1 = float(np.dot(u, r1))
        hit2 = float(np.dot(u, r2))
        u = np.dot(u, Q)
        u = np.maximum(u, 0.0)
        s = float(u.sum())

        f1.append(hit1)
        f2.append(hit2)
        f_any.append(hit1 + hit2)
        surv.append(s)

        if s < surv_tol:
            break

    return (
        np.asarray(f_any, dtype=np.float64),
        np.asarray(f1, dtype=np.float64),
        np.asarray(f2, dtype=np.float64),
        np.asarray(surv, dtype=np.float64),
    )


def run_linear_mfpt(
    *,
    Q: np.ndarray,
    r1: np.ndarray,
    r2: np.ndarray,
    i_start_t: int,
) -> Dict[str, float]:
    n_t = Q.shape[0]
    I = np.eye(n_t, dtype=np.float64)
    A = I - Q
    one = np.ones(n_t, dtype=np.float64)

    m = np.linalg.solve(A, one)
    u1 = np.linalg.solve(A, r1)
    u2 = np.linalg.solve(A, r2)

    return {
        "mfpt_exact": float(m[i_start_t]),
        "p_m1_exact": float(u1[i_start_t]),
        "p_m2_exact": float(u2[i_start_t]),
        "p_sum_exact": float(u1[i_start_t] + u2[i_start_t]),
    }


def run_aw_fft(
    *,
    Q: np.ndarray,
    r1: np.ndarray,
    r2: np.ndarray,
    alpha: np.ndarray,
    t_max_aw: int,
    oversample: int,
    r_pow10: float,
) -> Dict[str, object]:
    grid = choose_aw_grid(t_max=t_max_aw, oversample=oversample, r_pow10=r_pow10)
    m = grid.m
    k = np.arange(m, dtype=np.float64)
    z = grid.r * np.exp(1j * 2.0 * np.pi * k / float(m))

    n_t = Q.shape[0]
    I = np.eye(n_t, dtype=np.complex128)
    Qc = Q.astype(np.complex128, copy=False)
    rhs = np.column_stack([r1, r2]).astype(np.complex128, copy=False)

    F1 = np.zeros(m, dtype=np.complex128)
    F2 = np.zeros(m, dtype=np.complex128)

    for i, zi in enumerate(z):
        A = I - zi * Qc
        sol = np.linalg.solve(A, rhs)
        F1[i] = zi * np.dot(alpha, sol[:, 0])
        F2[i] = zi * np.dot(alpha, sol[:, 1])

    c1 = np.fft.fft(F1) / float(m)
    c2 = np.fft.fft(F2) / float(m)
    t = np.arange(m, dtype=np.float64)
    scale = grid.r ** (-t)
    f1 = (scale * c1).real.astype(np.float64, copy=False)
    f2 = (scale * c2).real.astype(np.float64, copy=False)

    f1 = f1[1 : t_max_aw + 1]
    f2 = f2[1 : t_max_aw + 1]
    f_any = f1 + f2

    # Numerical noise from FFT/roundoff can introduce tiny negative values.
    f1 = np.maximum(f1, 0.0)
    f2 = np.maximum(f2, 0.0)
    f_any = np.maximum(f_any, 0.0)

    return {
        "grid": {
            "m": m,
            "r": grid.r,
            "oversample": grid.oversample,
            "r_pow10": grid.r_pow10,
        },
        "f1": f1,
        "f2": f2,
        "f_any": f_any,
    }


def run_aw_defect_giuggioli(
    *,
    N: int,
    q: float,
    start: Coord,
    m1: Coord,
    m2: Coord,
    arrow_map: Dict[Coord, str],
    delta: float,
    t_max_aw: int,
    oversample: int,
    r_pow10: float,
) -> Dict[str, object]:
    """Two-target AW inversion via defect-reduced propagators (Giuggioli-style)."""

    report_dir = Path(__file__).resolve().parent.parent
    bimodality_code = report_dir.parent / "grid2d_bimodality" / "code"
    if str(bimodality_code) not in sys.path:
        sys.path.insert(0, str(bimodality_code))

    from heterogeneity_determinant import defect_pairs_from_config
    from model_core import LatticeConfig
    from propagator_z_analytic import defect_free_propagator_from_config

    map_dir = {"E": "right", "W": "left", "N": "down", "S": "up"}
    local_bias_arrows = {xy: map_dir[d] for xy, d in arrow_map.items()}

    cfg = LatticeConfig(
        N=N,
        q=q,
        g_x=0.0,
        g_y=0.0,
        boundary_x="reflecting",
        boundary_y="reflecting",
        start=start,
        target=m1,
        local_bias_arrows=local_bias_arrows,
        local_bias_delta=float(delta),
        sticky_sites={},
        barriers_reflect=set(),
        barriers_perm={},
    )

    base = defect_free_propagator_from_config(cfg)
    defects = defect_pairs_from_config(cfg)

    nodes = {start, m1, m2}
    for d in defects:
        nodes.add(d.u)
        nodes.add(d.v)
    nodes_list = sorted(nodes)
    node_index = {n: i for i, n in enumerate(nodes_list)}

    pair_eval = base.prepare_pair_evaluator(nodes_list, nodes_list)
    U = np.array([node_index[d.u] for d in defects], dtype=np.int64)
    V = np.array([node_index[d.v] for d in defects], dtype=np.int64)
    delta_vec = np.array([-d.eta_uv for d in defects], dtype=np.complex128)

    src_idx = np.array([node_index[start], node_index[m1], node_index[m2]], dtype=np.int64)
    dst_idx = np.array([node_index[m1], node_index[m2]], dtype=np.int64)

    grid = choose_aw_grid(t_max=t_max_aw, oversample=oversample, r_pow10=r_pow10)
    m = grid.m
    k = np.arange(m, dtype=np.float64)
    z = grid.r * np.exp(1j * 2.0 * np.pi * k / float(m))

    F1 = np.zeros(m, dtype=np.complex128)
    F2 = np.zeros(m, dtype=np.complex128)

    if len(defects) > 0:
        eye = np.eye(len(defects), dtype=np.complex128)
    else:
        eye = np.zeros((0, 0), dtype=np.complex128)

    for i, zi in enumerate(z):
        P = pair_eval.evaluate(zi)
        if len(defects) > 0:
            P_vu = P[np.ix_(V, U)]
            A = eye - zi * (P_vu * delta_vec[None, :])
            B = P[np.ix_(V, dst_idx)]
            try:
                X = np.linalg.solve(A, B)
            except np.linalg.LinAlgError:
                X = np.linalg.solve(A + 1e-12 * eye, B)
            P_su = P[np.ix_(src_idx, U)]
            ST = P[np.ix_(src_idx, dst_idx)] + zi * ((P_su * delta_vec[None, :]) @ X)
        else:
            ST = P[np.ix_(src_idx, dst_idx)]

        Ps1, Ps2 = ST[0, 0], ST[0, 1]
        P11, P12 = ST[1, 0], ST[1, 1]
        P21, P22 = ST[2, 0], ST[2, 1]
        G = np.array([[P11, P21], [P12, P22]], dtype=np.complex128)
        b = np.array([Ps1, Ps2], dtype=np.complex128)
        try:
            x = np.linalg.solve(G, b)
        except np.linalg.LinAlgError:
            x = np.linalg.solve(G + 1e-12 * np.eye(2, dtype=np.complex128), b)
        F1[i], F2[i] = x[0], x[1]

    c1 = np.fft.fft(F1) / float(m)
    c2 = np.fft.fft(F2) / float(m)
    t = np.arange(m, dtype=np.float64)
    scale = grid.r ** (-t)
    f1 = (scale * c1).real.astype(np.float64, copy=False)
    f2 = (scale * c2).real.astype(np.float64, copy=False)
    f1 = f1[1 : t_max_aw + 1]
    f2 = f2[1 : t_max_aw + 1]
    f_any = f1 + f2
    f1 = np.maximum(f1, 0.0)
    f2 = np.maximum(f2, 0.0)
    f_any = np.maximum(f_any, 0.0)

    return {
        "grid": {
            "m": m,
            "r": grid.r,
            "oversample": grid.oversample,
            "r_pow10": grid.r_pow10,
        },
        "f1": f1,
        "f2": f2,
        "f_any": f_any,
        "defect_pairs": int(len(defects)),
        "defect_nodes": int(len(nodes_list)),
        "local_bias_sites": int(len(local_bias_arrows)),
    }


def summarize_series(f_any: np.ndarray, f1: np.ndarray, f2: np.ndarray, surv: np.ndarray) -> Dict[str, float | int | None]:
    t = np.arange(len(f_any), dtype=np.float64)
    mfpt_trunc = float(np.dot(t, f_any))
    p1 = float(f1.sum())
    p2 = float(f2.sum())
    p_any = float(f_any.sum())
    peak1, peak2 = find_two_peaks(f_any)
    return {
        "steps": int(len(f_any) - 1),
        "mass_any": p_any,
        "mass_m1": p1,
        "mass_m2": p2,
        "survival_tail": float(surv[-1]),
        "mfpt_trunc": mfpt_trunc,
        "peak1": None if peak1 is None else int(peak1),
        "peak2": None if peak2 is None else int(peak2),
    }


def l1_and_max_abs(a: np.ndarray, b: np.ndarray) -> Dict[str, float]:
    n = min(len(a), len(b))
    if n == 0:
        return {"l1": 0.0, "linf": 0.0}
    d = np.abs(a[:n] - b[:n])
    return {"l1": float(d.sum()), "linf": float(d.max())}


def save_truncation_csv(rows: Sequence[Dict[str, float]], out_path: Path) -> None:
    hdr = "t_max,mass_any,survival_tail,mfpt_trunc,mfpt_rel_error"
    lines = [hdr]
    for r in rows:
        lines.append(
            f"{int(r['t_max'])},{r['mass_any']:.12g},{r['survival_tail']:.12g},{r['mfpt_trunc']:.12g},{r['mfpt_rel_error']:.12g}"
        )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_fpt_overlay(
    *,
    out_path: Path,
    f_exact: np.ndarray,
    f_aw: np.ndarray,
    f_aw_defect: np.ndarray,
    f_dense: np.ndarray,
    t_show: int,
) -> None:
    t = np.arange(1, t_show + 1)
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.plot(t, f_exact[1 : t_show + 1], lw=2.0, color="#111111", label="Sparse exact recursion")
    ax.plot(t, f_dense[1 : t_show + 1], lw=1.4, ls="--", color="#1f77b4", label="Dense recursion (Q)")
    ax.plot(t, f_aw[1 : t_show + 1], lw=1.4, ls="-.", color="#d62728", label="AW/Cauchy inversion")
    ax.plot(
        t,
        f_aw_defect[1 : t_show + 1],
        lw=1.4,
        ls=":",
        color="#9467bd",
        label="AW defect-reduced (Giuggioli)",
    )
    ax.set_xlabel("t")
    ax.set_ylabel("FPT pmf")
    ax.set_title("C1: FPT comparison (two-target total)")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_runtime_bar(*, out_path: Path, runtime_rows: Sequence[Tuple[str, float]]) -> None:
    names = [r[0] for r in runtime_rows]
    vals = [r[1] for r in runtime_rows]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    palette = ["#222222", "#4e79a7", "#e15759", "#af7aa1", "#59a14f", "#76b7b2"]
    colors = [palette[i % len(palette)] for i in range(len(vals))]
    bars = ax.bar(x, vals, color=colors)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=12, ha="right")
    ax.set_ylabel("Wall-clock seconds")
    ax.set_title("C1 runtime comparison")
    ax.grid(axis="y", alpha=0.25)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2.0, b.get_height(), f"{v:.2f}s", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def write_report(
    *,
    out_path: Path,
    json_rel: str,
    trunc_csv_rel: str,
    fig_fpt_rel: str,
    fig_runtime_rel: str,
    summary: Dict[str, object],
) -> None:
    cfg = summary["config"]
    rt = summary["runtime_seconds"]
    sparse = summary["sparse_exact"]
    sparse_aw = summary["sparse_exact_on_aw_horizon"]
    dense = summary["dense_recursion"]
    aw = summary["aw_inversion"]
    aw_def = summary["aw_defect_reduced"]
    linear = summary["linear_mfpt"]
    trunc_rows = summary["mfpt_truncation_scan"]
    err_dense = summary["error_dense_vs_sparse"]
    err_aw = summary["error_aw_vs_sparse"]
    err_aw_def = summary["error_aw_defect_vs_sparse"]

    lines: List[str] = []
    lines.append("# 2D Two-Target 数值方法比较报告（C1 配置）")
    lines.append("")
    lines.append("## 1. 研究目标")
    lines.append("在 `2d_two_target_double_peak` 的同一模型设定下，对比五种常用数值路线：")
    lines.append("1. 时间域 sparse exact 递推（当前主脚本用法）")
    lines.append("2. 时间域 dense 递推（显式 transient 矩阵 Q）")
    lines.append("3. 生成函数 AW/Cauchy-FFT 反演（离散 PGF 反演）")
    lines.append("4. Giuggioli defect-reduced AW（局部缺陷降阶反演）")
    lines.append("5. 线性方程法（只求 MFPT 与 splitting，不求整条 FPT 曲线）")
    lines.append("")
    lines.append("重点比较维度：`FPT 曲线精度`、`MFPT 偏差`、`运行时间`、`适用场景`。")
    lines.append("")
    lines.append("## 2. 实验设置")
    lines.append(f"- 网格与边界：`N={cfg['N']}`，四边反射。")
    lines.append(f"- 运动参数：`q={cfg['q']}`，局部 bias 强度 `delta={cfg['delta']}`。")
    lines.append("- 几何：C1（balanced double peak）。")
    lines.append(f"- 起点/目标（0-based）：start={cfg['start_0_based']}, m1={cfg['m1_0_based']}, m2={cfg['m2_0_based']}。")
    lines.append(f"- 主比较时域上限：`t_max_main={cfg['t_max_main']}`，停止阈值 `surv_tol={cfg['surv_tol']}`。")
    lines.append(f"- AW 参数：`t_max_aw={cfg['t_max_aw']}`，`oversample={cfg['aw_oversample']}`，`r_pow10={cfg['aw_r_pow10']}`，对应 `m={aw['aw_grid']['m']}`。")
    lines.append("- 说明：AW 行仅对 `1..t_max_aw` 的时间窗做反演，不等同于全时域求和后的 MFPT。")
    lines.append("")
    lines.append("## 3. 方法流程（逐步）")
    lines.append("### 3.1 Sparse exact 递推（主方法）")
    lines.append("1. 在全状态空间上做一步转移更新。")
    lines.append("2. 读取本步落在 `m1,m2` 的质量，记为 `f1(t), f2(t)`。")
    lines.append("3. 将 `m1,m2` 位置概率清零，继续下一步。")
    lines.append("4. 得到 `f_any(t)=f1(t)+f2(t)` 与 `S(t)`。")
    lines.append("")
    lines.append("### 3.2 Dense 递推（Q 矩阵）")
    lines.append("1. 构造 transient 子矩阵 `Q` 与吸收向量 `r1,r2`。")
    lines.append("2. 用 `u_t = u_{t-1} Q` 推进；每步 `f_i(t)=u_{t-1} r_i`。")
    lines.append("3. 与 sparse 递推数学等价，但每步成本更高。")
    lines.append("")
    lines.append("### 3.3 AW/Cauchy-FFT 反演")
    lines.append("1. 用 `F_i(z)= z α (I-zQ)^(-1) r_i` 计算 PGF。")
    lines.append("2. 在圆周 `z_k = r exp(i2πk/m)` 采样。")
    lines.append("3. 通过 FFT 取系数，恢复 `f_i(t)`。")
    lines.append("4. 总曲线 `f_any=f1+f2`。")
    lines.append("")
    lines.append("### 3.4 Giuggioli defect-reduced AW")
    lines.append("1. 将局部异质性写成 defect 对（与无缺陷基底比较得到）。")
    lines.append("2. 每个 `z_k` 上用 Woodbury/defect 小系统恢复关键 propagator。")
    lines.append("3. 用两目标 renewal 2x2 方程求 `F_1(z_k), F_2(z_k)`，再 FFT 反演。")
    lines.append("")
    lines.append("### 3.5 线性方程（MFPT/splitting）")
    lines.append("1. 解 `(I-Q)m=1` 得 MFPT。")
    lines.append("2. 解 `(I-Q)u_i=r_i` 得 splitting 概率 `p_i`。")
    lines.append("3. 不输出整条 FPT，但 MFPT 最稳健。")
    lines.append("")
    lines.append("## 4. 结果对比")
    lines.append("### 4.1 运行时间")
    lines.append("")
    lines.append("| 方法 | 运行时间 (s) |")
    lines.append("|---|---:|")
    lines.append(f"| Sparse exact 递推 | {rt['sparse_exact']:.4f} |")
    lines.append(f"| Dense 递推 (Q) | {rt['dense_recursion']:.4f} |")
    lines.append(f"| AW/Cauchy 反演 | {rt['aw_inversion']:.4f} |")
    lines.append(f"| AW defect-reduced (Giuggioli) | {rt['aw_defect_reduced']:.4f} |")
    lines.append(f"| 线性方程 (MFPT/splitting) | {rt['linear_mfpt']:.4f} |")
    lines.append("")
    lines.append("### 4.2 与 sparse exact 的分布误差")
    lines.append("")
    lines.append("| 对比项 | L1 误差 | L∞ 误差 |")
    lines.append("|---|---:|---:|")
    lines.append(f"| Dense vs Sparse (到共同步长) | {err_dense['l1']:.3e} | {err_dense['linf']:.3e} |")
    lines.append(f"| AW vs Sparse (1..t_max_aw) | {err_aw['l1']:.3e} | {err_aw['linf']:.3e} |")
    lines.append(f"| AW-defect vs Sparse (1..t_max_aw) | {err_aw_def['l1']:.3e} | {err_aw_def['linf']:.3e} |")
    lines.append("")
    lines.append("### 4.3 关键统计量")
    lines.append("")
    lines.append("| 方法 | mass_any | tail | MFPT(截断/精确) | 峰1 | 峰2 |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    lines.append(
        f"| Sparse exact | {sparse['mass_any']:.6f} | {sparse['survival_tail']:.6f} | {sparse['mfpt_trunc']:.3f} | {sparse['peak1']} | {sparse['peak2']} |"
    )
    lines.append(
        f"| Sparse exact (1..t_max_aw) | {sparse_aw['mass_any']:.6f} | {sparse_aw['survival_tail']:.6f} | {sparse_aw['mfpt_trunc']:.3f} | {sparse_aw['peak1']} | {sparse_aw['peak2']} |"
    )
    lines.append(
        f"| Dense recursion | {dense['mass_any']:.6f} | {dense['survival_tail']:.6f} | {dense['mfpt_trunc']:.3f} | {dense['peak1']} | {dense['peak2']} |"
    )
    lines.append(
        f"| AW inversion | {aw['mass_any']:.6f} | {aw['survival_tail']:.6f} | {aw['mfpt_trunc']:.3f} | {aw['peak1']} | {aw['peak2']} |"
    )
    lines.append(
        f"| AW defect-reduced | {aw_def['mass_any']:.6f} | {aw_def['survival_tail']:.6f} | {aw_def['mfpt_trunc']:.3f} | {aw_def['peak1']} | {aw_def['peak2']} |"
    )
    lines.append(
        f"| 线性方程 (精确) | {linear['p_sum_exact']:.6f} | 0.000000 | {linear['mfpt_exact']:.3f} | - | - |"
    )
    lines.append("")
    lines.append("### 4.4 Giuggioli 缺陷规模（本案例）")
    lines.append("")
    lines.append(
        f"- local bias sites = `{aw_def.get('local_bias_sites')}`，defect pairs = `{aw_def.get('defect_pairs')}`，defect nodes = `{aw_def.get('defect_nodes')}`。"
    )
    lines.append("")
    lines.append("### 4.5 截断导致的 MFPT 偏差（sparse exact）")
    lines.append("")
    lines.append("| t_max | 吸收质量 | 尾部质量 | MFPT 截断值 | 相对误差(对线性方程) |")
    lines.append("|---:|---:|---:|---:|---:|")
    for r in trunc_rows:
        lines.append(
            f"| {int(r['t_max'])} | {r['mass_any']:.6f} | {r['survival_tail']:.6f} | {r['mfpt_trunc']:.3f} | {r['mfpt_rel_error']:.3%} |"
        )
    lines.append("")
    lines.append("## 5. 结论（本场景）")
    lines.append("1. `FPT 曲线形状`：sparse exact 与 dense recursion 基本一致，dense 仅作为验证基线。")
    lines.append("2. `效率`：sparse exact 仍是本 C1 配置最稳健高效的整曲线基线；AW 路线主要成本来自 z 域线性求解。")
    lines.append("3. `Giuggioli defect-reduced`：在本配置已可复现同窗分布，但由于 defect 规模不小，速度优势不一定出现。")
    lines.append("4. `MFPT`：长尾显著时，截断求和低估明显；线性方程法给出最稳健 MFPT。")
    lines.append("5. `实务建议`：")
    lines.append("   - 需要完整双峰曲线：优先 sparse exact；")
    lines.append("   - 只要 MFPT/splitting：优先线性方程；")
    lines.append("   - 需要变换域分析或频繁多 t 查询：可用 AW；若缺陷很少（M<<N）再考虑 defect-reduced AW。")
    lines.append("")
    lines.append("## 6. 产物与复现")
    lines.append(f"- 数值摘要：`{json_rel}`")
    lines.append(f"- 截断扫描表：`{trunc_csv_rel}`")
    lines.append(f"- 曲线对比图：`{fig_fpt_rel}`")
    lines.append(f"- 运行时间图：`{fig_runtime_rel}`")
    lines.append("- 复现命令：")
    lines.append("```bash")
    lines.append(".venv/bin/python reports/grid2d_two_target_double_peak/code/compare_numeric_methods.py")
    lines.append("```")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Compare numerical methods for 2D two-target C1.")
    p.add_argument("--t-max-main", type=int, default=6000)
    p.add_argument("--surv-tol", type=float, default=1e-13)
    p.add_argument("--t-max-aw", type=int, default=800)
    p.add_argument("--aw-oversample", type=int, default=2)
    p.add_argument("--aw-r-pow10", type=float, default=8.0)
    p.add_argument("--trunc-grid", type=str, default="300,600,1200,2400,6000")
    args = p.parse_args()

    report_dir = Path(__file__).resolve().parent.parent
    data_dir = report_dir / "data"
    fig_dir = report_dir / "figures"
    ensure_dir(data_dir)
    ensure_dir(fig_dir)

    N = 31
    src_idx, dst_idx, probs, start, m1, m2 = build_c1_transition(N=N, q=0.2)
    _, _, _, arrow_map_c1, delta_c1 = build_c1_geometry(N=N)

    t0 = time.perf_counter()
    f_any_sparse, f1_sparse, f2_sparse, surv_sparse = run_exact_two_target(
        N=N,
        start=start,
        target1=m1,
        target2=m2,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        t_max=args.t_max_main,
        surv_tol=args.surv_tol,
    )
    t1 = time.perf_counter()
    rt_sparse = t1 - t0

    sys_data = build_transient_system(
        N=N,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        start=start,
        m1=m1,
        m2=m2,
    )
    Q = sys_data["Q"]
    r1 = sys_data["r1"]
    r2 = sys_data["r2"]
    alpha = sys_data["alpha"]
    i_start_t = int(sys_data["i_start_t"][0])

    t0 = time.perf_counter()
    f_any_dense, f1_dense, f2_dense, surv_dense = run_dense_recursion(
        Q=Q,
        r1=r1,
        r2=r2,
        alpha=alpha,
        t_max=args.t_max_main,
        surv_tol=args.surv_tol,
    )
    t1 = time.perf_counter()
    rt_dense = t1 - t0

    t0 = time.perf_counter()
    aw = run_aw_fft(
        Q=Q,
        r1=r1,
        r2=r2,
        alpha=alpha,
        t_max_aw=args.t_max_aw,
        oversample=args.aw_oversample,
        r_pow10=args.aw_r_pow10,
    )
    t1 = time.perf_counter()
    rt_aw = t1 - t0
    f1_aw = np.concatenate(([0.0], aw["f1"]))
    f2_aw = np.concatenate(([0.0], aw["f2"]))
    f_any_aw = np.concatenate(([0.0], aw["f_any"]))
    surv_aw = 1.0 - np.cumsum(f_any_aw)
    surv_aw = np.maximum(surv_aw, 0.0)

    t0 = time.perf_counter()
    aw_def = run_aw_defect_giuggioli(
        N=N,
        q=0.2,
        start=start,
        m1=m1,
        m2=m2,
        arrow_map=arrow_map_c1,
        delta=delta_c1,
        t_max_aw=args.t_max_aw,
        oversample=args.aw_oversample,
        r_pow10=args.aw_r_pow10,
    )
    t1 = time.perf_counter()
    rt_aw_def = t1 - t0
    f1_aw_def = np.concatenate(([0.0], aw_def["f1"]))
    f2_aw_def = np.concatenate(([0.0], aw_def["f2"]))
    f_any_aw_def = np.concatenate(([0.0], aw_def["f_any"]))
    surv_aw_def = 1.0 - np.cumsum(f_any_aw_def)
    surv_aw_def = np.maximum(surv_aw_def, 0.0)

    t0 = time.perf_counter()
    linear = run_linear_mfpt(Q=Q, r1=r1, r2=r2, i_start_t=i_start_t)
    t1 = time.perf_counter()
    rt_linear = t1 - t0

    sparse_sum = summarize_series(f_any_sparse, f1_sparse, f2_sparse, surv_sparse)
    t_aw = min(args.t_max_aw, len(f_any_sparse) - 1)
    sparse_aw_sum = summarize_series(
        f_any_sparse[: t_aw + 1],
        f1_sparse[: t_aw + 1],
        f2_sparse[: t_aw + 1],
        surv_sparse[: t_aw + 1],
    )
    dense_sum = summarize_series(f_any_dense, f1_dense, f2_dense, surv_dense)
    aw_sum = summarize_series(f_any_aw, f1_aw, f2_aw, surv_aw)
    aw_sum["aw_grid"] = aw["grid"]
    aw_def_sum = summarize_series(f_any_aw_def, f1_aw_def, f2_aw_def, surv_aw_def)
    aw_def_sum["aw_grid"] = aw_def["grid"]
    aw_def_sum["defect_pairs"] = int(aw_def["defect_pairs"])
    aw_def_sum["defect_nodes"] = int(aw_def["defect_nodes"])
    aw_def_sum["local_bias_sites"] = int(aw_def["local_bias_sites"])

    err_dense = l1_and_max_abs(f_any_dense, f_any_sparse)
    err_aw = l1_and_max_abs(f_any_aw[1:], f_any_sparse[1 : len(f_any_aw)])
    err_aw_def = l1_and_max_abs(f_any_aw_def[1:], f_any_sparse[1 : len(f_any_aw_def)])

    trunc_list = [int(x.strip()) for x in args.trunc_grid.split(",") if x.strip()]
    trunc_rows: List[Dict[str, float]] = []
    for t_cut in trunc_list:
        f_any_t, f1_t, f2_t, surv_t = run_exact_two_target(
            N=N,
            start=start,
            target1=m1,
            target2=m2,
            src_idx=src_idx,
            dst_idx=dst_idx,
            probs=probs,
            t_max=t_cut,
            surv_tol=0.0,
        )
        s = summarize_series(f_any_t, f1_t, f2_t, surv_t)
        mfpt_exact = linear["mfpt_exact"]
        trunc_rows.append(
            {
                "t_max": float(t_cut),
                "mass_any": float(s["mass_any"]),
                "survival_tail": float(s["survival_tail"]),
                "mfpt_trunc": float(s["mfpt_trunc"]),
                "mfpt_rel_error": float((s["mfpt_trunc"] - mfpt_exact) / mfpt_exact),
            }
        )

    json_out = data_dir / "method_comparison_c1.json"
    trunc_csv_out = data_dir / "method_comparison_c1_truncation.csv"
    fig_fpt_out = fig_dir / "method_compare_c1_fpt_overlay.pdf"
    fig_runtime_out = fig_dir / "method_compare_c1_runtime.pdf"
    report_out = report_dir / "method_comparison_cn.md"

    t_show = min(args.t_max_aw, len(f_any_sparse) - 1, len(f_any_dense) - 1, len(f_any_aw) - 1, len(f_any_aw_def) - 1)
    plot_fpt_overlay(
        out_path=fig_fpt_out,
        f_exact=f_any_sparse,
        f_aw=f_any_aw,
        f_aw_defect=f_any_aw_def,
        f_dense=f_any_dense,
        t_show=t_show,
    )
    plot_runtime_bar(
        out_path=fig_runtime_out,
        runtime_rows=[
            ("Sparse exact", rt_sparse),
            ("Dense recursion", rt_dense),
            ("AW inversion", rt_aw),
            ("AW defect", rt_aw_def),
            ("Linear MFPT", rt_linear),
        ],
    )

    save_truncation_csv(trunc_rows, trunc_csv_out)

    payload: Dict[str, object] = {
        "config": {
            "N": N,
            "q": 0.2,
            "delta": 0.2,
            "case_id": "C1",
            "start_0_based": list(start),
            "m1_0_based": list(m1),
            "m2_0_based": list(m2),
            "t_max_main": args.t_max_main,
            "surv_tol": args.surv_tol,
            "t_max_aw": args.t_max_aw,
            "aw_oversample": args.aw_oversample,
            "aw_r_pow10": args.aw_r_pow10,
        },
        "runtime_seconds": {
            "sparse_exact": rt_sparse,
            "dense_recursion": rt_dense,
            "aw_inversion": rt_aw,
            "aw_defect_reduced": rt_aw_def,
            "linear_mfpt": rt_linear,
        },
        "sparse_exact": sparse_sum,
        "sparse_exact_on_aw_horizon": sparse_aw_sum,
        "dense_recursion": dense_sum,
        "aw_inversion": aw_sum,
        "aw_defect_reduced": aw_def_sum,
        "linear_mfpt": linear,
        "error_dense_vs_sparse": err_dense,
        "error_aw_vs_sparse": err_aw,
        "error_aw_defect_vs_sparse": err_aw_def,
        "mfpt_truncation_scan": trunc_rows,
        "artifacts": {
            "truncation_csv": str(trunc_csv_out.relative_to(report_dir)),
            "fpt_overlay_figure": str(fig_fpt_out.relative_to(report_dir)),
            "runtime_figure": str(fig_runtime_out.relative_to(report_dir)),
            "report_markdown": str(report_out.relative_to(report_dir)),
        },
    }

    json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    write_report(
        out_path=report_out,
        json_rel=str(json_out.relative_to(report_dir)),
        trunc_csv_rel=str(trunc_csv_out.relative_to(report_dir)),
        fig_fpt_rel=str(fig_fpt_out.relative_to(report_dir)),
        fig_runtime_rel=str(fig_runtime_out.relative_to(report_dir)),
        summary=payload,
    )

    print(f"[ok] wrote {json_out}")
    print(f"[ok] wrote {trunc_csv_out}")
    print(f"[ok] wrote {fig_fpt_out}")
    print(f"[ok] wrote {fig_runtime_out}")
    print(f"[ok] wrote {report_out}")


if __name__ == "__main__":
    main()
