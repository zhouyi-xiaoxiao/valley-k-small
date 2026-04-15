#!/usr/bin/env python3
"""Build data/figures/tables for 2D two-walker encounter with shortcut."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPORT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = REPORT_DIR / "data"
FIG_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"
OUT_DIR = REPORT_DIR / "outputs"


@dataclass(frozen=True)
class A1A8Case:
    name: str
    N: int
    q: float
    z: complex
    n: int
    n0: int
    m0: int
    contour_tol: float = 1e-12


@dataclass(frozen=True)
class EncounterConfig:
    N: int = 11
    q: float = 0.72
    bias1: tuple[float, float] = (0.22, 0.22)
    bias2: tuple[float, float] = (-0.22, -0.22)
    start1: tuple[int, int] = (2, 2)
    start2: tuple[int, int] = (8, 8)
    shortcut1_src: tuple[int, int] = (2, 2)
    shortcut1_dst: tuple[int, int] = (7, 7)
    shortcut2_src: tuple[int, int] = (8, 8)
    shortcut2_dst: tuple[int, int] = (3, 3)
    shortcut2_scale: float = 0.10
    t_max_scan: int = 600
    t_max_case: int = 900


def ensure_dirs() -> None:
    for path in (DATA_DIR, FIG_DIR, TABLE_DIR, OUT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def moving_average(y: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return y.astype(np.float64, copy=True)
    w = int(window)
    if w % 2 == 0:
        w += 1
    pad = w // 2
    y_pad = np.pad(y.astype(np.float64, copy=False), (pad, pad), mode="edge")
    kernel = np.ones(w, dtype=np.float64) / float(w)
    out = np.convolve(y_pad, kernel, mode="valid")
    return out[: y.size]


def strict_local_maxima(y: np.ndarray) -> np.ndarray:
    if y.size < 3:
        return np.zeros(0, dtype=np.int64)
    return np.where((y[1:-1] > y[:-2]) & (y[1:-1] >= y[2:]))[0] + 1


def half_width_at_half_max(f: np.ndarray, mode: int) -> float:
    if mode <= 0 or mode >= len(f):
        return 0.0
    peak = float(f[mode])
    if peak <= 0.0:
        return 0.0
    thr = 0.5 * peak
    left = int(mode)
    right = int(mode)
    while left > 1 and f[left - 1] >= thr:
        left -= 1
    while right < len(f) - 1 and f[right + 1] >= thr:
        right += 1
    return 0.5 * float(right - left)


def detect_two_peak_metrics(
    f: np.ndarray,
    *,
    smooth_window: int = 11,
    t_ignore: int = 4,
    min_sep: int = 4,
    min_ratio: float = 0.20,
    max_valley_ratio: float = 0.92,
) -> dict[str, float | int | bool | None]:
    fs = moving_average(f, smooth_window)
    peaks = strict_local_maxima(fs)
    if peaks.size == 0:
        return {
            "has_two": False,
            "is_bimodal": False,
            "t1": None,
            "t2": None,
            "tv": None,
            "h1": None,
            "h2": None,
            "valley": None,
            "peak_ratio": 0.0,
            "valley_ratio": 1.0,
            "sep_peaks": 0.0,
        }

    mask = (peaks >= t_ignore) & (fs[peaks] >= 0.01 * float(np.max(fs)))
    peaks = peaks[mask]
    best: tuple[float, int, int, float, float, float, float] | None = None

    for i in range(peaks.size - 1):
        p1 = int(peaks[i])
        for j in range(i + 1, peaks.size):
            p2 = int(peaks[j])
            if p2 - p1 < min_sep:
                continue
            h1 = float(fs[p1])
            h2 = float(fs[p2])
            if h1 <= 0.0 or h2 <= 0.0:
                continue
            ratio = min(h1, h2) / max(h1, h2)
            valley = float(np.min(fs[p1 : p2 + 1]))
            valley_ratio = valley / max(h1, h2)
            score = ratio * float(p2 - p1)
            if best is None or score > best[0]:
                best = (score, p1, p2, h1, h2, valley, valley_ratio)

    if best is None:
        return {
            "has_two": False,
            "is_bimodal": False,
            "t1": None,
            "t2": None,
            "tv": None,
            "h1": None,
            "h2": None,
            "valley": None,
            "peak_ratio": 0.0,
            "valley_ratio": 1.0,
            "sep_peaks": 0.0,
        }

    _, p1, p2, h1, h2, valley, valley_ratio = best
    tv = int(p1 + np.argmin(fs[p1 : p2 + 1]))
    peak_ratio = min(h1, h2) / max(h1, h2)
    hw1 = half_width_at_half_max(fs, p1)
    hw2 = half_width_at_half_max(fs, p2)
    denom = hw1 + hw2
    sep_peaks = float(abs(p2 - p1) / denom) if denom > 0.0 else 0.0
    is_bimodal = bool(sep_peaks >= 1.0)

    return {
        "has_two": True,
        "is_bimodal": is_bimodal,
        "t1": int(p1),
        "t2": int(p2),
        "tv": int(tv),
        "h1": h1,
        "h2": h2,
        "valley": valley,
        "peak_ratio": float(peak_ratio),
        "valley_ratio": float(valley_ratio),
        "sep_peaks": float(sep_peaks),
    }


# -----------------------------------------------------------------------------
# A1/A8 validation (1D periodic lattice)
# -----------------------------------------------------------------------------


def alpha_k(N: int, q: float) -> np.ndarray:
    k = np.arange(N, dtype=np.float64)
    return 1.0 + q * (np.cos(2.0 * np.pi * k / float(N)) - 1.0)


def h_k(N: int, n: int, n0: int) -> np.ndarray:
    k = np.arange(N, dtype=np.float64)
    phase = 2.0 * np.pi * k * float(n - n0) / float(N)
    return np.exp(1j * phase) / float(N)


def p_tilde_from_modes(N: int, q: float, n: int, n0: int, z: complex) -> complex:
    a = alpha_k(N, q)
    h = h_k(N, n, n0)
    return np.sum(h / (1.0 - z * a))


def rhs_a8(case: A1A8Case) -> complex:
    a = alpha_k(case.N, case.q)
    h1 = h_k(case.N, case.n, case.n0)
    h2 = h_k(case.N, case.n, case.m0)
    denom = 1.0 - case.z * np.outer(a, a)
    return np.sum(np.outer(h2, h1) / denom)


def choose_contour_radius(N: int, q: float, z: complex) -> tuple[float, float, float]:
    a = alpha_k(N, q)
    r_in = float(abs(z) * np.max(np.abs(a)))
    nz = a[np.abs(a) > 0.0]
    r_out = float(np.min(1.0 / np.abs(nz)))
    if not (r_in < r_out):
        raise ValueError(f"No valid annulus: r_in={r_in:.6g}, r_out={r_out:.6g}")
    r = float(np.sqrt(r_in * r_out))
    return r_in, r_out, r


def lhs_contour(case: A1A8Case, M: int, r: float) -> complex:
    theta = 2.0 * np.pi * np.arange(M, dtype=np.float64) / float(M)
    u = r * np.exp(1j * theta)
    a = alpha_k(case.N, case.q)
    h1 = h_k(case.N, case.n, case.n0)
    h2 = h_k(case.N, case.n, case.m0)

    p1 = np.sum(h1[None, :] / (1.0 - u[:, None] * a[None, :]), axis=1)
    p2 = np.sum(h2[None, :] / (1.0 - (case.z / u)[:, None] * a[None, :]), axis=1)
    return np.mean(p1 * p2)


def lhs_adaptive(case: A1A8Case, r: float, tol: float | None = None) -> tuple[complex, int, float]:
    target_tol = case.contour_tol if tol is None else float(tol)
    M = 16
    i_prev = lhs_contour(case, M=M, r=r)

    while M <= 8192:
        M2 = M * 2
        i_cur = lhs_contour(case, M=M2, r=r)
        err = abs(i_cur - i_prev)
        if err <= target_tol * (1.0 + abs(i_cur)):
            return i_cur, M2, err
        M = M2
        i_prev = i_cur

    return i_prev, M, err


def run_a1a8_validation() -> dict[str, object]:
    cases = [
        A1A8Case("R1_real_small", N=16, q=0.30, z=0.40 + 0.0j, n=3, n0=0, m0=5),
        A1A8Case("R2_complex", N=12, q=0.35, z=0.30 + 0.10j, n=4, n0=1, m0=7),
        A1A8Case("R3_edge_q0", N=20, q=0.0, z=0.55 + 0.0j, n=6, n0=6, m0=6),
        A1A8Case("R4_small_z", N=18, q=0.40, z=0.05 + 0.20j, n=9, n0=2, m0=11),
    ]

    rows: list[dict[str, object]] = []

    for case in cases:
        r_in, r_out, r = choose_contour_radius(case.N, case.q, case.z)
        lhs, m_used, trap_err = lhs_adaptive(case, r=r)
        rhs = rhs_a8(case)
        rel_err = abs(lhs - rhs) / (1.0 + abs(rhs))

        rows.append(
            {
                "name": case.name,
                "N": case.N,
                "q": case.q,
                "z_re": float(np.real(case.z)),
                "z_im": float(np.imag(case.z)),
                "n": case.n,
                "n0": case.n0,
                "m0": case.m0,
                "r_in": r_in,
                "r_out": r_out,
                "r_used": r,
                "M_used": int(m_used),
                "trap_err_est": float(trap_err),
                "lhs_re": float(np.real(lhs)),
                "lhs_im": float(np.imag(lhs)),
                "rhs_re": float(np.real(rhs)),
                "rhs_im": float(np.imag(rhs)),
                "rel_err": float(rel_err),
            }
        )

    # Diagnostics on first case: convergence vs M, radius invariance.
    diag_case = cases[0]
    _, _, r_star = choose_contour_radius(diag_case.N, diag_case.q, diag_case.z)
    rhs_diag = rhs_a8(diag_case)

    m_grid = [16, 32, 64, 128, 256, 512, 1024]
    conv_rows: list[dict[str, float]] = []
    prev_val: complex | None = None
    for m in m_grid:
        val = lhs_contour(diag_case, M=m, r=r_star)
        abs_err_rhs = float(abs(val - rhs_diag))
        self_err = float("nan") if prev_val is None else float(abs(val - prev_val))
        conv_rows.append({"M": float(m), "abs_err_rhs": abs_err_rhs, "self_err": self_err})
        prev_val = val

    r_in, r_out, _ = choose_contour_radius(diag_case.N, diag_case.q, diag_case.z)
    radius_list = np.linspace(r_in * 1.15, r_out * 0.90, 8)
    radius_rows: list[dict[str, float]] = []
    for r in radius_list:
        val, m_used, _ = lhs_adaptive(diag_case, r=float(r), tol=5e-13)
        radius_rows.append(
            {
                "r": float(r),
                "M_used": float(m_used),
                "abs_err_rhs": float(abs(val - rhs_diag)),
                "rel_err": float(abs(val - rhs_diag) / (1.0 + abs(rhs_diag))),
            }
        )

    payload: dict[str, object] = {
        "cases": rows,
        "diagnostics": {
            "diag_case": {
                "name": diag_case.name,
                "N": diag_case.N,
                "q": diag_case.q,
                "z_re": float(np.real(diag_case.z)),
                "z_im": float(np.imag(diag_case.z)),
                "n": diag_case.n,
                "n0": diag_case.n0,
                "m0": diag_case.m0,
                "r_star": r_star,
                "r_in": r_in,
                "r_out": r_out,
            },
            "convergence": conv_rows,
            "radius_invariance": radius_rows,
        },
    }

    (DATA_DIR / "a1a8_validation.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_a1a8_table(rows)
    plot_a1a8_convergence(conv_rows)
    plot_a1a8_radius(radius_rows)
    return payload


def write_a1a8_table(rows: Iterable[dict[str, object]]) -> None:
    lines: list[str] = []
    lines.append("\\begin{tabular}{lcccccc}")
    lines.append("\\toprule")
    lines.append("Case & $(N,q)$ & $z$ & $M$ & $r$ & $|LHS-RHS|$ & rel.err \\\\")
    lines.append("\\midrule")
    for row in rows:
        case_name = str(row["name"]).replace("_", "\\_")
        z_text = f"{row['z_re']:.2f}{'+' if row['z_im'] >= 0 else '-'}{abs(row['z_im']):.2f}i"
        abs_err = abs((row["lhs_re"] + 1j * row["lhs_im"]) - (row["rhs_re"] + 1j * row["rhs_im"]))
        lines.append(
            f"{case_name} & ({row['N']},{row['q']:.2f}) & ${z_text}$ & {int(row['M_used'])} & "
            f"{row['r_used']:.3f} & {abs_err:.2e} & {row['rel_err']:.2e} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    (TABLE_DIR / "a1a8_test_table.tex").write_text("\n".join(lines), encoding="utf-8")


def plot_a1a8_convergence(conv_rows: list[dict[str, float]]) -> None:
    M = np.array([int(r["M"]) for r in conv_rows], dtype=np.int64)
    err_rhs = np.array([r["abs_err_rhs"] for r in conv_rows], dtype=np.float64)
    err_self = np.array([r["self_err"] for r in conv_rows], dtype=np.float64)

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.semilogy(M, err_rhs, "o-", lw=1.6, label=r"$|I_M-\mathrm{RHS}|$")
    ax.semilogy(M[1:], err_self[1:], "s--", lw=1.2, label=r"$|I_M-I_{M/2}|$")
    ax.set_xlabel("contour nodes M")
    ax.set_ylabel("absolute error")
    ax.set_title("A1/A8 contour convergence")
    ax.grid(alpha=0.30, which="both")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "a1a8_contour_convergence.pdf")
    plt.close(fig)


def plot_a1a8_radius(radius_rows: list[dict[str, float]]) -> None:
    r = np.array([row["r"] for row in radius_rows], dtype=np.float64)
    rel = np.array([row["rel_err"] for row in radius_rows], dtype=np.float64)

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.semilogy(r, rel, "o-", lw=1.6)
    ax.set_xlabel("contour radius r")
    ax.set_ylabel("relative error")
    ax.set_title("A1/A8 radius invariance in admissible annulus")
    ax.grid(alpha=0.30, which="both")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "a1a8_radius_invariance.pdf")
    plt.close(fig)


# -----------------------------------------------------------------------------
# 2D two-walker encounter with shortcut
# -----------------------------------------------------------------------------


def build_transition_matrix(
    N: int,
    q: float,
    *,
    bias_xy: tuple[float, float] = (0.0, 0.0),
    shortcut_src: tuple[int, int] | None = None,
    shortcut_dst: tuple[int, int] | None = None,
    beta: float = 0.0,
) -> np.ndarray:
    S = N * N
    P = np.zeros((S, S), dtype=np.float64)
    bx, by = bias_xy

    base = np.array([q / 4.0 + bx / 2.0, q / 4.0 - bx / 2.0, q / 4.0 + by / 2.0, q / 4.0 - by / 2.0], dtype=np.float64)
    base = np.clip(base, 0.0, None)
    if float(np.sum(base)) <= 0.0:
        base[:] = q / 4.0
    else:
        base *= q / float(np.sum(base))

    pe, pw, pn, ps = (float(base[0]), float(base[1]), float(base[2]), float(base[3]))

    def idx(x: int, y: int) -> int:
        return y * N + x

    for y in range(N):
        for x in range(N):
            i = idx(x, y)
            stay = 1.0 - q
            for nx, ny, p in ((x + 1, y, pe), (x - 1, y, pw), (x, y + 1, pn), (x, y - 1, ps)):
                if 0 <= nx < N and 0 <= ny < N:
                    P[i, idx(nx, ny)] += p
                else:
                    stay += p

            if shortcut_src is not None and shortcut_dst is not None and (x, y) == shortcut_src:
                shift = min(max(beta * (1.0 - q), 0.0), stay)
                stay -= shift
                P[i, idx(shortcut_dst[0], shortcut_dst[1])] += shift

            P[i, i] += stay

    return P


def first_encounter_any(
    N: int,
    P1: np.ndarray,
    P2: np.ndarray,
    start1: tuple[int, int],
    start2: tuple[int, int],
    t_max: int,
) -> tuple[np.ndarray, np.ndarray]:
    S = N * N
    J = np.zeros((S, S), dtype=np.float64)
    i1 = start1[1] * N + start1[0]
    i2 = start2[1] * N + start2[0]
    J[i1, i2] = 1.0

    f = np.zeros(t_max + 1, dtype=np.float64)
    surv = np.zeros(t_max + 1, dtype=np.float64)
    surv[0] = 1.0

    for t in range(1, t_max + 1):
        # NumPy/BLAS can emit spurious matmul runtime warnings on some macOS builds;
        # keep explicit finite checks to guard correctness.
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            J = P1.T @ J @ P2
        if not np.isfinite(J).all():
            raise FloatingPointError("non-finite value detected in encounter propagation")
        hit = float(np.trace(J))
        f[t] = hit
        np.fill_diagonal(J, 0.0)
        surv[t] = float(np.sum(J))

    return f, surv


def first_encounter_shortcut_decomp(
    N: int,
    P1_with: np.ndarray,
    P1_noedge: np.ndarray,
    P1_edge_only: np.ndarray,
    P2: np.ndarray,
    start1: tuple[int, int],
    start2: tuple[int, int],
    t_max: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    S = N * N
    J0 = np.zeros((S, S), dtype=np.float64)
    J1 = np.zeros((S, S), dtype=np.float64)
    i1 = start1[1] * N + start1[0]
    i2 = start2[1] * N + start2[0]
    J0[i1, i2] = 1.0

    f_total = np.zeros(t_max + 1, dtype=np.float64)
    f_no = np.zeros(t_max + 1, dtype=np.float64)
    f_yes = np.zeros(t_max + 1, dtype=np.float64)

    for t in range(1, t_max + 1):
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            J0_next = P1_noedge.T @ J0 @ P2
            J1_next = P1_with.T @ J1 @ P2 + P1_edge_only.T @ J0 @ P2
        if not np.isfinite(J0_next).all() or not np.isfinite(J1_next).all():
            raise FloatingPointError("non-finite value detected in shortcut decomposition propagation")

        h0 = float(np.trace(J0_next))
        h1 = float(np.trace(J1_next))
        f_no[t] = h0
        f_yes[t] = h1
        f_total[t] = h0 + h1

        np.fill_diagonal(J0_next, 0.0)
        np.fill_diagonal(J1_next, 0.0)
        J0 = J0_next
        J1 = J1_next

    return f_total, f_no, f_yes


def build_shortcut_split(
    N: int,
    q: float,
    beta: float,
    bias_xy: tuple[float, float],
    src: tuple[int, int],
    dst: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    P_with = build_transition_matrix(
        N,
        q,
        bias_xy=bias_xy,
        shortcut_src=src,
        shortcut_dst=dst,
        beta=beta,
    )
    P_base = build_transition_matrix(N, q, bias_xy=bias_xy)

    S = N * N
    i_src = src[1] * N + src[0]
    i_dst = dst[1] * N + dst[0]

    shift = max(float(P_with[i_src, i_dst] - P_base[i_src, i_dst]), 0.0)
    P_edge_only = np.zeros((S, S), dtype=np.float64)
    P_edge_only[i_src, i_dst] = shift

    P_noedge = P_with.copy()
    P_noedge[i_src, i_dst] -= shift

    return P_with, P_noedge, P_edge_only, shift


def phase_from_metrics(metrics: dict[str, float | int | bool | None]) -> int:
    if not bool(metrics["has_two"]):
        return 0
    if bool(metrics["is_bimodal"]):
        return 2
    return 1


def run_encounter_experiments() -> dict[str, object]:
    cfg = EncounterConfig()
    betas = np.linspace(0.0, 0.60, 13)

    scan_rows: list[dict[str, object]] = []
    series_cache: dict[float, np.ndarray] = {}

    for beta in betas:
        beta_f = float(beta)
        P1 = build_transition_matrix(
            cfg.N,
            cfg.q,
            bias_xy=cfg.bias1,
            shortcut_src=cfg.shortcut1_src,
            shortcut_dst=cfg.shortcut1_dst,
            beta=beta_f,
        )
        P2 = build_transition_matrix(
            cfg.N,
            cfg.q,
            bias_xy=cfg.bias2,
            shortcut_src=cfg.shortcut2_src,
            shortcut_dst=cfg.shortcut2_dst,
            beta=cfg.shortcut2_scale * beta_f,
        )
        f, surv = first_encounter_any(cfg.N, P1, P2, cfg.start1, cfg.start2, cfg.t_max_scan)
        metrics = detect_two_peak_metrics(f)

        row = {
            "beta": beta_f,
            "phase": int(phase_from_metrics(metrics)),
            "t1": metrics["t1"],
            "t2": metrics["t2"],
            "tv": metrics["tv"],
            "sep_peaks": float(metrics.get("sep_peaks", 0.0)),
            "peak_ratio": float(metrics["peak_ratio"]),
            "valley_ratio": float(metrics["valley_ratio"]),
            "mass_tmax": float(np.sum(f)),
            "survival_tmax": float(surv[-1]),
            "is_bimodal": bool(metrics["is_bimodal"]),
            "has_two": bool(metrics["has_two"]),
        }
        scan_rows.append(row)
        series_cache[beta_f] = f

    # Representative case: prefer a clear double-peak in mid beta range.
    rep_beta = 0.40
    if not any(abs(float(r["beta"]) - rep_beta) < 1e-12 and bool(r["has_two"]) for r in scan_rows):
        clear_rows = [r for r in scan_rows if bool(r["is_bimodal"])]
        if clear_rows:
            rep_beta = float(clear_rows[0]["beta"])

    # Build detailed representative outputs.
    P1_rep, P1_noedge, P1_edge_only, shift = build_shortcut_split(
        cfg.N,
        cfg.q,
        rep_beta,
        cfg.bias1,
        cfg.shortcut1_src,
        cfg.shortcut1_dst,
    )
    P2_rep = build_transition_matrix(
        cfg.N,
        cfg.q,
        bias_xy=cfg.bias2,
        shortcut_src=cfg.shortcut2_src,
        shortcut_dst=cfg.shortcut2_dst,
        beta=cfg.shortcut2_scale * rep_beta,
    )

    f_rep, surv_rep = first_encounter_any(cfg.N, P1_rep, P2_rep, cfg.start1, cfg.start2, cfg.t_max_case)
    f_total, f_no, f_yes = first_encounter_shortcut_decomp(
        cfg.N,
        P1_rep,
        P1_noedge,
        P1_edge_only,
        P2_rep,
        cfg.start1,
        cfg.start2,
        cfg.t_max_case,
    )

    rep_metrics = detect_two_peak_metrics(f_rep)

    overlay_betas = [0.0, 0.20, rep_beta, 0.55]
    overlay_series: dict[str, list[float]] = {}
    for b in overlay_betas:
        f = series_cache.get(float(b))
        if f is None:
            P1 = build_transition_matrix(
                cfg.N,
                cfg.q,
                bias_xy=cfg.bias1,
                shortcut_src=cfg.shortcut1_src,
                shortcut_dst=cfg.shortcut1_dst,
                beta=float(b),
            )
            P2 = build_transition_matrix(
                cfg.N,
                cfg.q,
                bias_xy=cfg.bias2,
                shortcut_src=cfg.shortcut2_src,
                shortcut_dst=cfg.shortcut2_dst,
                beta=cfg.shortcut2_scale * float(b),
            )
            f, _ = first_encounter_any(cfg.N, P1, P2, cfg.start1, cfg.start2, cfg.t_max_case)
        overlay_series[f"beta_{b:.2f}"] = f.tolist()

    # Save scan table/CSV/JSON.
    with (DATA_DIR / "encounter_beta_scan.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "beta",
                "phase",
                "t1",
                "t2",
                "tv",
                "sep_peaks",
                "peak_ratio",
                "valley_ratio",
                "mass_tmax",
                "survival_tmax",
                "is_bimodal",
            ]
        )
        for r in scan_rows:
            writer.writerow(
                [
                    r["beta"],
                    r["phase"],
                    r["t1"],
                    r["t2"],
                    r["tv"],
                    r["sep_peaks"],
                    r["peak_ratio"],
                    r["valley_ratio"],
                    r["mass_tmax"],
                    r["survival_tmax"],
                    int(bool(r["is_bimodal"])),
                ]
            )

    write_encounter_scan_table(scan_rows)

    t = np.arange(cfg.t_max_case + 1, dtype=np.int64)
    with (OUT_DIR / "encounter_rep_fpt.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["t", "f_total", "f_shortcut_no", "f_shortcut_yes", "survival"])
        for i in range(t.size):
            writer.writerow([int(t[i]), f_total[i], f_no[i], f_yes[i], surv_rep[i] if i < surv_rep.size else ""])

    case_payload: dict[str, object] = {
        "config": {
            "N": cfg.N,
            "q": cfg.q,
            "bias1": list(cfg.bias1),
            "bias2": list(cfg.bias2),
            "start1": list(cfg.start1),
            "start2": list(cfg.start2),
            "shortcut1": {"src": list(cfg.shortcut1_src), "dst": list(cfg.shortcut1_dst)},
            "shortcut2": {"src": list(cfg.shortcut2_src), "dst": list(cfg.shortcut2_dst), "scale": cfg.shortcut2_scale},
        },
        "representative": {
            "beta": rep_beta,
            "metrics": rep_metrics,
            "shortcut_shift": shift,
            "mass_tmax": float(np.sum(f_rep)),
            "survival_tmax": float(surv_rep[-1]),
        },
        "scan": scan_rows,
    }
    (DATA_DIR / "case_summary.json").write_text(json.dumps(case_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # Plot outputs.
    plot_encounter_geometry(cfg, rep_beta)
    plot_encounter_overlay(cfg, overlay_series)
    plot_shortcut_decomp(f_total, f_no, f_yes, rep_metrics, rep_beta)
    plot_encounter_phase(scan_rows)

    return {
        "scan": scan_rows,
        "representative_beta": rep_beta,
        "representative_metrics": rep_metrics,
    }


def plot_encounter_geometry(cfg: EncounterConfig, rep_beta: float) -> None:
    N = cfg.N
    fig, ax = plt.subplots(figsize=(5.8, 5.2))
    base = np.zeros((N, N), dtype=np.float64)
    ax.imshow(base, origin="lower", cmap=plt.matplotlib.colors.ListedColormap(["#f5f1e8"]))

    ax.set_xticks(np.arange(-0.5, N, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, N, 1), minor=True)
    ax.grid(which="minor", color="#c9c0ae", linewidth=0.4)

    sx1, sy1 = cfg.shortcut1_src
    dx1, dy1 = cfg.shortcut1_dst
    sx2, sy2 = cfg.shortcut2_src
    dx2, dy2 = cfg.shortcut2_dst

    ax.annotate(
        "",
        xy=(dx1, dy1),
        xytext=(sx1, sy1),
        arrowprops=dict(arrowstyle="->", lw=2.0, color="#7b1fa2"),
        zorder=6,
    )
    ax.annotate(
        "",
        xy=(dx2, dy2),
        xytext=(sx2, sy2),
        arrowprops=dict(arrowstyle="->", lw=1.5, color="#1e88e5", alpha=0.8),
        zorder=6,
    )

    ax.scatter([cfg.start1[0]], [cfg.start1[1]], c="#e53935", marker="s", s=70, label="walker A start", zorder=8)
    ax.scatter([cfg.start2[0]], [cfg.start2[1]], c="#0d47a1", marker="D", s=70, label="walker B start", zorder=8)

    ax.text(cfg.start1[0] + 0.35, cfg.start1[1] + 0.35, "A", color="#b71c1c", fontsize=10, weight="bold")
    ax.text(cfg.start2[0] + 0.35, cfg.start2[1] + 0.35, "B", color="#0d47a1", fontsize=10, weight="bold")

    ax.text(dx1 + 0.15, dy1 + 0.25, "A shortcut dst", color="#6a1b9a", fontsize=8)
    ax.text(dx2 + 0.15, dy2 + 0.25, "B shortcut dst", color="#1565c0", fontsize=8)

    ax.set_xlim(-0.5, N - 0.5)
    ax.set_ylim(-0.5, N - 0.5)
    ax.set_aspect("equal")
    ax.set_title(f"2D two-walker encounter setup (beta={rep_beta:.2f})")
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    ax.legend(loc="upper left", fontsize=8, frameon=True)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_geometry.pdf")
    plt.close(fig)


def plot_encounter_overlay(cfg: EncounterConfig, overlay_series: dict[str, list[float]]) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    colors = {
        "beta_0.00": "#333333",
        "beta_0.20": "#1e88e5",
        "beta_0.40": "#e53935",
        "beta_0.55": "#8e24aa",
    }

    for key, values in overlay_series.items():
        y = np.array(values, dtype=np.float64)
        t = np.arange(y.size, dtype=np.int64)
        ys = moving_average(y, 11)
        ax.plot(t, y, color=colors.get(key, "#777777"), lw=0.8, alpha=0.20)
        ax.plot(t, ys, color=colors.get(key, "#777777"), lw=1.6, label=key.replace("beta_", r"$\beta$="))

    ax.set_xlim(0, cfg.t_max_case)
    ax.set_xlabel("t")
    ax.set_ylabel(r"$f_{enc}(t)$")
    ax.set_title("Encounter FPT vs shortcut strength")
    ax.grid(alpha=0.28)
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_fpt_overlay.pdf")
    plt.close(fig)


def plot_shortcut_decomp(
    f_total: np.ndarray,
    f_no: np.ndarray,
    f_yes: np.ndarray,
    rep_metrics: dict[str, float | int | bool | None],
    rep_beta: float,
) -> None:
    t = np.arange(f_total.size, dtype=np.int64)

    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    ax.plot(t, moving_average(f_total, 11), color="#111111", lw=1.8, label="total")
    ax.plot(t, moving_average(f_no, 11), color="#1976d2", lw=1.4, label="no shortcut used")
    ax.plot(t, moving_average(f_yes, 11), color="#8e24aa", lw=1.4, label="shortcut used")

    if rep_metrics["t1"] is not None and rep_metrics["t2"] is not None:
        t1 = int(rep_metrics["t1"])
        t2 = int(rep_metrics["t2"])
        ax.axvline(t1, color="#444444", lw=1.0, ls="--", alpha=0.65)
        ax.axvline(t2, color="#444444", lw=1.0, ls="--", alpha=0.65)

    ax.set_xlim(0, min(220, f_total.size - 1))
    ax.set_xlabel("t")
    ax.set_ylabel(r"$f_{enc}(t)$")
    ax.set_title(f"Shortcut channel decomposition (beta={rep_beta:.2f})")
    ax.grid(alpha=0.28)
    ax.legend(loc="upper right", fontsize=9)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_shortcut_decomp.pdf")
    plt.close(fig)


def plot_encounter_phase(scan_rows: list[dict[str, object]]) -> None:
    beta = np.array([float(r["beta"]) for r in scan_rows], dtype=np.float64)
    phase = np.array([int(r["phase"]) for r in scan_rows], dtype=np.int64)
    sep_peaks = np.array([float(r["sep_peaks"]) for r in scan_rows], dtype=np.float64)
    peak_ratio = np.array([float(r["peak_ratio"]) for r in scan_rows], dtype=np.float64)
    valley_ratio = np.array([float(r["valley_ratio"]) for r in scan_rows], dtype=np.float64)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.4, 5.8), sharex=True, gridspec_kw={"height_ratios": [3.0, 1.0]})

    ax1.plot(beta, sep_peaks, "o-", color="#2e7d32", lw=1.8, label="separation")
    ax1.plot(beta, peak_ratio, "s-", color="#d81b60", lw=1.3, label="peak ratio")
    ax1.plot(beta, valley_ratio, "^-", color="#1e88e5", lw=1.2, label="valley ratio")
    ax1.axhline(1.0, color="#2e7d32", lw=1.0, ls="--", alpha=0.75)
    ax1.set_ylabel("metric")
    ax1.set_title("Separation and secondary diagnostics vs shortcut strength")
    ax1.grid(alpha=0.25)
    ax1.legend(loc="upper right", fontsize=9)

    cmap = {0: "#cfd8dc", 1: "#90caf9", 2: "#ef9a9a"}
    colors = [cmap[int(v)] for v in phase]
    ax2.bar(beta, np.ones_like(beta), width=0.035, color=colors, edgecolor="#444444", linewidth=0.6)
    ax2.set_yticks([])
    ax2.set_xlabel(r"shortcut strength $\beta$")
    ax2.set_xlim(float(beta.min()) - 0.03, float(beta.max()) + 0.03)
    ax2.set_title("phase: 0 no pair, 1 paired but not separated, 2 paired and separated", fontsize=9)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_beta_phase.pdf")
    plt.close(fig)


def write_encounter_scan_table(scan_rows: Iterable[dict[str, object]]) -> None:
    lines: list[str] = []
    lines.append("\\begin{tabular}{cccccccc}")
    lines.append("\\toprule")
    lines.append(r"$\beta$ & phase & $t_1$ & $t_2$ & sep & peak ratio & valley ratio & separated \\")
    lines.append("\\midrule")
    for r in scan_rows:
        t1 = "-" if r["t1"] is None else str(int(r["t1"]))
        t2 = "-" if r["t2"] is None else str(int(r["t2"]))
        lines.append(
            f"{float(r['beta']):.2f} & {int(r['phase'])} & {t1} & {t2} & {float(r['sep_peaks']):.3f} & "
            f"{float(r['peak_ratio']):.3f} & {float(r['valley_ratio']):.3f} & {int(bool(r['is_bimodal']))} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    (TABLE_DIR / "encounter_scan_table.tex").write_text("\n".join(lines), encoding="utf-8")


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------


def main() -> None:
    ensure_dirs()
    a1a8_payload = run_a1a8_validation()
    encounter_payload = run_encounter_experiments()

    summary = {
        "a1a8_cases": len(a1a8_payload["cases"]),
        "encounter_scan_points": len(encounter_payload["scan"]),
        "representative_beta": encounter_payload["representative_beta"],
    }
    (OUT_DIR / "run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[ok] built report assets")
    print(f"  data: {DATA_DIR}")
    print(f"  figures: {FIG_DIR}")
    print(f"  tables: {TABLE_DIR}")


if __name__ == "__main__":
    main()
