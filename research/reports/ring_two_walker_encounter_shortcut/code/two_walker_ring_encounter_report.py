#!/usr/bin/env python3
"""Build data/figures/tables for 1D ring two-walker encounter with shortcut."""

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

TIMESCALE_SCORE_FORMULA = "score=(tau-t1)*R_peak/(R_valley+1e-12)"
TIMESCALE_TIE_BREAK = "larger_tau -> smaller_R_valley -> larger_R_peak"
TIMESCALE_TIE_TOL = 1e-12
VALLEY_INTERIOR_MIN_SEP = 2
PEAK_RATIO_DEF = "R_peak=min(g_t1,g_t2)/max(g_t1,g_t2)"
VALLEY_RATIO_DEF = "R_valley=g_tv/max(g_t1,g_t2)"
DIRECTED_RATIO_DEF = "R_dir=g_t2/g_t1"
DIRECTED_RATIO_ROLE = "diagnostic_only_not_used_in_phase_thresholds"
PEAK_SELECTION_RULE = "t2=argmax_{tau>t1} score(tau)"
VALLEY_INTERIOR_RULE = "require_tau_minus_t1>=2_for_strict_interior_valley"
PEAK_PROMINENCE_REL = 0.01
FIXEDSITE_COARSE_RULE = "tilde_f(0)=f(0); tilde_f(m)=f(2m-1)+f(2m)"
FIXEDSITE_TIME_MAP = "t=2m"


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
class RingEncounterConfig:
    N: int = 101
    q: float = 0.70
    g1: float = 0.70
    g2: float = -0.40
    n0: int = 5
    m0: int = 55
    shortcut_src: int = 5
    shortcut_dst: int = 70
    t_max_scan: int = 1400
    t_max_case: int = 1600
    t_ignore: int = 80
    beta_scan_min: float = 0.0
    beta_scan_max: float = 0.30
    beta_scan_points: int = 16
    beta_refine_half_width: float = 0.05
    beta_refine_step: float = 0.005
    peak_window_end: int = 400


@dataclass(frozen=True)
class FixedSiteDriftConfig:
    N: int = 30
    q: float = 0.70
    n0: int = 5
    m0: int = 12
    delta: int = 0
    t_max: int = 900
    # Denser grid than the initial coarse 7x7 map for more stable phase occupancy estimates.
    g_grid: tuple[float, ...] = (-0.90, -0.75, -0.60, -0.45, -0.30, -0.15, 0.00, 0.15, 0.30, 0.45, 0.60, 0.75, 0.90)


@dataclass(frozen=True)
class OnsetNScanConfig:
    # Ring-size robustness check around the default N=101 baseline.
    N_grid: tuple[int, ...] = (81, 101, 121, 141)
    rep_beta: float = 0.20
    t_max_min: int = 900
    t_max_max: int = 1800
    # If no clear onset appears inside the nominal [0, 0.30] window, extend once.
    onset_extension_max: float = 0.50
    onset_extension_step: float = 0.02


def build_anywhere_timescale_detector_config(
    cfg: RingEncounterConfig,
    *,
    smooth_window: int = 11,
    min_ratio: float = 0.20,
    max_valley_ratio: float = 0.90,
) -> dict[str, object]:
    return {
        "mode": "timescale",
        "trace": "bar_f",
        "time_map": "identity",
        "smooth_window": int(smooth_window),
        "t_ignore": int(cfg.t_ignore),
        "t_end": int(cfg.peak_window_end),
        "min_ratio": float(min_ratio),
        "max_valley_ratio": float(max_valley_ratio),
        "peak_prominence_rel": float(PEAK_PROMINENCE_REL),
        "peak_ratio_def": PEAK_RATIO_DEF,
        "valley_ratio_def": VALLEY_RATIO_DEF,
        "directed_ratio_def": DIRECTED_RATIO_DEF,
        "directed_ratio_role": DIRECTED_RATIO_ROLE,
        "selection_rule": PEAK_SELECTION_RULE,
        "valley_interior_rule": VALLEY_INTERIOR_RULE,
        "score_formula": TIMESCALE_SCORE_FORMULA,
        "tie_tol": float(TIMESCALE_TIE_TOL),
        "tie_break": TIMESCALE_TIE_BREAK,
    }


def build_fixedsite_timescale_detector_config(
    *,
    smooth_window_pair: int,
    t_ignore_pair: int,
    min_sep_pair: int,
    min_ratio_pair: float,
    max_valley_ratio_pair: float,
) -> dict[str, object]:
    return {
        "mode": "timescale",
        "trace": "bar_tilde_f",
        "coarse_rule": FIXEDSITE_COARSE_RULE,
        "time_map": FIXEDSITE_TIME_MAP,
        "smooth_window": int(smooth_window_pair),
        "t_ignore_pair": int(t_ignore_pair),
        "min_sep_pair": int(min_sep_pair),
        "min_ratio": float(min_ratio_pair),
        "max_valley_ratio": float(max_valley_ratio_pair),
        "peak_prominence_rel": float(PEAK_PROMINENCE_REL),
        "peak_ratio_def": PEAK_RATIO_DEF,
        "valley_ratio_def": VALLEY_RATIO_DEF,
        "directed_ratio_def": DIRECTED_RATIO_DEF,
        "directed_ratio_role": DIRECTED_RATIO_ROLE,
        "selection_rule": PEAK_SELECTION_RULE,
        "valley_interior_rule": VALLEY_INTERIOR_RULE,
        "score_formula": TIMESCALE_SCORE_FORMULA,
        "tie_tol": float(TIMESCALE_TIE_TOL),
        "tie_break": TIMESCALE_TIE_BREAK,
        "t_end_policy": "no_extra_cutoff",
    }


def ensure_dirs() -> None:
    for path in (DATA_DIR, FIG_DIR, TABLE_DIR, OUT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def finite_clamp(value: float, low: float, high: float, *, name: str) -> float:
    v = float(value)
    if not np.isfinite(v):
        raise ValueError(f"{name} must be finite, got {value!r}")
    return min(max(v, low), high)


def scaled_index(idx: int, N_from: int, N_to: int) -> int:
    if N_to <= 0:
        raise ValueError(f"N_to must be positive, got {N_to}")
    if N_from <= 0:
        raise ValueError(f"N_from must be positive, got {N_from}")
    return int(np.round(float(idx % N_from) * float(N_to) / float(N_from))) % int(N_to)


def repair_stochastic_row(row: np.ndarray, *, tol: float = 1e-12) -> None:
    """Repair tiny stochastic-row drift caused by invalid/rounded probabilities."""
    cleaned = np.where(np.isfinite(row), row, 0.0).astype(np.float64, copy=False)
    if np.any(cleaned < 0.0):
        # Keep tiny numerical negatives from propagating.
        if float(np.min(cleaned)) < -tol:
            cleaned = np.clip(cleaned, 0.0, None)
        else:
            cleaned = np.where(cleaned < 0.0, 0.0, cleaned)

    total = float(np.sum(cleaned))
    if total <= tol:
        raise FloatingPointError("degenerate transition row after stochastic repair")

    if abs(total - 1.0) > tol:
        cleaned = cleaned / total
    row[:] = cleaned


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


def valley_between_peaks(fs: np.ndarray, t1: int, t2: int) -> tuple[int, float]:
    """Find valley index/value between two peaks, preferring strict interior (t1, t2)."""
    if fs.size == 0:
        return 0, 0.0

    lo = max(0, min(int(t1), int(t2)))
    hi = min(fs.size - 1, max(int(t1), int(t2)))
    if hi <= lo:
        return lo, float(fs[lo])

    # Prefer strict interior to stay consistent with the report definition.
    if hi - lo >= 2:
        segment = fs[lo + 1 : hi]
        arg = int(np.argmin(segment))
        tv = lo + 1 + arg
        return tv, float(segment[arg])

    # Fallback for adjacent peaks: closed interval avoids empty slices.
    segment = fs[lo : hi + 1]
    arg = int(np.argmin(segment))
    tv = lo + arg
    return tv, float(segment[arg])


def parity_coarse_grain_k2(y: np.ndarray) -> np.ndarray:
    """K=2 parity coarse graining: out[0]=f(0), out[m]=f(2m-1)+f(2m) for m>=1."""
    if y.size <= 1:
        return y.astype(np.float64, copy=True)
    m = (y.size - 1) // 2
    out = np.zeros(m + 1, dtype=np.float64)
    out[0] = float(y[0])
    for i in range(1, m + 1):
        out[i] = float(y[2 * i - 1] + y[2 * i])
    return out


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


def write_a1a8_table(rows: Iterable[dict[str, object]]) -> None:
    lines: list[str] = []
    lines.append("\\begin{tabular}{lcccccc}")
    lines.append("\\toprule")
    lines.append(r"Case & $(N,q)$ & $z$ & $M$ & $r$ & $|LHS-RHS|$ & rel.err \\")
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


# -----------------------------------------------------------------------------
# 1D ring encounter model
# -----------------------------------------------------------------------------


def build_ring_transition(
    N: int,
    q: float,
    g: float,
    *,
    shortcut_src: int,
    shortcut_dst: int,
    beta: float,
) -> np.ndarray:
    if int(N) <= 0:
        raise ValueError(f"N must be positive, got {N}")

    q_safe = finite_clamp(q, 0.0, 1.0, name="q")
    g_safe = finite_clamp(g, -1.0, 1.0, name="g")
    beta_safe = finite_clamp(beta, 0.0, 1.0, name="beta")
    src = int(shortcut_src) % int(N)
    dst = int(shortcut_dst) % int(N)

    P = np.zeros((N, N), dtype=np.float64)
    p_plus = q_safe * (1.0 + g_safe) / 2.0
    p_minus = q_safe * (1.0 - g_safe) / 2.0
    p_stay = 1.0 - q_safe

    for i in range(N):
        P[i, i] += p_stay
        P[i, (i + 1) % N] += p_plus
        P[i, (i - 1) % N] += p_minus

        if i == src:
            shift = min(max(beta_safe * (1.0 - q_safe), 0.0), P[i, i])
            P[i, i] -= shift
            P[i, dst] += shift

        repair_stochastic_row(P[i])

    return P


def first_encounter_any(P1: np.ndarray, P2: np.ndarray, n0: int, m0: int, t_max: int) -> tuple[np.ndarray, np.ndarray]:
    N = P1.shape[0]
    P1T = P1.T
    J = np.zeros((N, N), dtype=np.float64)
    J[n0 % N, m0 % N] = 1.0

    f = np.zeros(t_max + 1, dtype=np.float64)
    surv = np.zeros(t_max + 1, dtype=np.float64)
    surv[0] = 1.0

    for t in range(1, t_max + 1):
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            J = P1T @ J @ P2
        if not np.isfinite(J).all():
            raise FloatingPointError("non-finite value detected in encounter propagation")

        f[t] = float(np.trace(J))
        np.fill_diagonal(J, 0.0)
        surv[t] = float(np.sum(J))

    return f, surv


def first_encounter_relative_chain(
    N: int,
    q1: float,
    g1: float,
    q2: float,
    g2: float,
    r0: int,
    t_max: int,
) -> np.ndarray:
    """Shortcut-free baseline: reduce to relative coordinate R_t=(X_t-Y_t) mod N."""
    p1_stay = 1.0 - q1
    p1_plus = q1 * (1.0 + g1) / 2.0
    p1_minus = q1 * (1.0 - g1) / 2.0
    p2_stay = 1.0 - q2
    p2_plus = q2 * (1.0 + g2) / 2.0
    p2_minus = q2 * (1.0 - g2) / 2.0

    p1 = {-1: p1_minus, 0: p1_stay, 1: p1_plus}
    p2 = {-1: p2_minus, 0: p2_stay, 1: p2_plus}
    p_delta: dict[int, float] = {}
    for s1, a in p1.items():
        for s2, b in p2.items():
            d = int(s1 - s2)
            p_delta[d] = p_delta.get(d, 0.0) + float(a * b)

    p = np.zeros(N, dtype=np.float64)
    p[int(r0) % N] = 1.0
    f = np.zeros(t_max + 1, dtype=np.float64)

    for t in range(1, t_max + 1):
        p_next = np.zeros_like(p)
        for d, prob in p_delta.items():
            p_next += float(prob) * np.roll(p, int(d))
        f[t] = float(p_next[0])
        p_next[0] = 0.0
        p = p_next

    return f


def first_encounter_fixed_site(
    P1: np.ndarray,
    P2: np.ndarray,
    n0: int,
    m0: int,
    delta: int,
    t_max: int,
) -> tuple[np.ndarray, np.ndarray]:
    """First meeting time at a fixed site delta: X_t=Y_t=delta."""
    N = P1.shape[0]
    P1T = P1.T
    d = int(delta) % N
    J = np.zeros((N, N), dtype=np.float64)
    J[n0 % N, m0 % N] = 1.0

    f = np.zeros(t_max + 1, dtype=np.float64)
    surv = np.zeros(t_max + 1, dtype=np.float64)
    surv[0] = 1.0

    for t in range(1, t_max + 1):
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            J = P1T @ J @ P2
        if not np.isfinite(J).all():
            raise FloatingPointError("non-finite value detected in fixed-site encounter propagation")

        f[t] = float(J[d, d])
        J[d, d] = 0.0
        surv[t] = float(np.sum(J))

    return f, surv


def first_encounter_shortcut_decomp(
    P_with: np.ndarray,
    P_noedge: np.ndarray,
    P_edge_only: np.ndarray,
    P2: np.ndarray,
    n0: int,
    m0: int,
    t_max: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    N = P_with.shape[0]
    P_with_T = P_with.T
    P_noedge_T = P_noedge.T
    P_edge_only_T = P_edge_only.T
    J0 = np.zeros((N, N), dtype=np.float64)
    J1 = np.zeros((N, N), dtype=np.float64)
    J0[n0 % N, m0 % N] = 1.0

    f_total = np.zeros(t_max + 1, dtype=np.float64)
    f_no = np.zeros(t_max + 1, dtype=np.float64)
    f_yes = np.zeros(t_max + 1, dtype=np.float64)

    for t in range(1, t_max + 1):
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            J0_next = P_noedge_T @ J0 @ P2
            J1_next = P_with_T @ J1 @ P2 + P_edge_only_T @ J0 @ P2
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


def first_fixed_shortcut_decomp(
    P_with: np.ndarray,
    P_noedge: np.ndarray,
    P_edge_only: np.ndarray,
    P2: np.ndarray,
    n0: int,
    m0: int,
    delta: int,
    t_max: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    N = P_with.shape[0]
    P_with_T = P_with.T
    P_noedge_T = P_noedge.T
    P_edge_only_T = P_edge_only.T
    d = int(delta) % N
    J0 = np.zeros((N, N), dtype=np.float64)
    J1 = np.zeros((N, N), dtype=np.float64)
    J0[n0 % N, m0 % N] = 1.0

    f_total = np.zeros(t_max + 1, dtype=np.float64)
    f_no = np.zeros(t_max + 1, dtype=np.float64)
    f_yes = np.zeros(t_max + 1, dtype=np.float64)

    for t in range(1, t_max + 1):
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            J0_next = P_noedge_T @ J0 @ P2
            J1_next = P_with_T @ J1 @ P2 + P_edge_only_T @ J0 @ P2
        if not np.isfinite(J0_next).all() or not np.isfinite(J1_next).all():
            raise FloatingPointError("non-finite value detected in fixed-site shortcut decomposition propagation")

        h0 = float(J0_next[d, d])
        h1 = float(J1_next[d, d])
        f_no[t] = h0
        f_yes[t] = h1
        f_total[t] = h0 + h1

        J0_next[d, d] = 0.0
        J1_next[d, d] = 0.0
        J0 = J0_next
        J1 = J1_next

    return f_total, f_no, f_yes


def build_shortcut_split(
    N: int,
    q: float,
    g: float,
    *,
    shortcut_src: int,
    shortcut_dst: int,
    beta: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    P_with = build_ring_transition(
        N,
        q,
        g,
        shortcut_src=shortcut_src,
        shortcut_dst=shortcut_dst,
        beta=beta,
    )
    P_base = build_ring_transition(
        N,
        q,
        g,
        shortcut_src=shortcut_src,
        shortcut_dst=shortcut_dst,
        beta=0.0,
    )

    shift = max(float(P_with[shortcut_src, shortcut_dst] - P_base[shortcut_src, shortcut_dst]), 0.0)
    P_edge_only = np.zeros_like(P_with)
    P_edge_only[shortcut_src, shortcut_dst] = shift

    P_noedge = P_with.copy()
    P_noedge[shortcut_src, shortcut_dst] -= shift
    return P_with, P_noedge, P_edge_only, shift


def empty_peak_metrics() -> dict[str, float | int | bool | None]:
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
        "peak_ratio_dir": 0.0,
        "valley_ratio": 1.0,
        "n_peaks": 0,
    }


def detect_two_peak_metrics(
    f: np.ndarray,
    *,
    smooth_window: int = 11,
    t_ignore: int = 80,
    min_sep: int = 40,
    min_ratio: float = 0.20,
    max_valley_ratio: float = 0.90,
) -> dict[str, float | int | bool | None]:
    fs = moving_average(f, smooth_window)
    peaks = strict_local_maxima(fs)
    if peaks.size == 0:
        return empty_peak_metrics()

    mask = (peaks >= t_ignore) & (fs[peaks] >= 0.01 * float(np.max(fs)))
    peaks = peaks[mask]
    best: tuple[float, int, int, float, float, int, float, float] | None = None

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
            tv, valley = valley_between_peaks(fs, p1, p2)
            valley_ratio = valley / max(h1, h2)
            score = ratio * float(p2 - p1)
            if best is None or score > best[0]:
                best = (score, p1, p2, h1, h2, tv, valley, valley_ratio)

    if best is None:
        return empty_peak_metrics()

    _, p1, p2, h1, h2, tv, valley, valley_ratio = best
    peak_ratio = min(h1, h2) / max(h1, h2)
    is_bimodal = bool(peak_ratio >= min_ratio and valley_ratio <= max_valley_ratio)

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
        "peak_ratio_dir": float(h2 / h1) if h1 > 0.0 else 0.0,
        "valley_ratio": float(valley_ratio),
        "n_peaks": int(peaks.size),
    }


def select_timescale_t2(
    fs: np.ndarray,
    t1: int,
    candidate_peaks: np.ndarray,
    *,
    eps: float = 1e-12,
    min_sep: int = 1,
    tie_tol: float = TIMESCALE_TIE_TOL,
) -> tuple[int, int, float, float, float] | None:
    """Select a late-timescale partner peak for t1 using score~sep*balance/valley.

    Valley is defined on strict interior (t1, t2), so candidates must satisfy t2-t1>=2.

    Tie-break policy (deterministic):
    1) prefer larger t2 (later timescale),
    2) then smaller valley ratio,
    3) then larger peak ratio.
    """
    best: tuple[float, int, int, float, float, float] | None = None
    t1i = int(t1)
    min_sep_i = max(int(min_sep), VALLEY_INTERIOR_MIN_SEP)
    h1 = float(fs[t1i])
    if h1 <= 0.0:
        return None

    for p in candidate_peaks:
        t2 = int(p)
        if t2 <= t1i:
            continue
        if t2 - t1i < min_sep_i:
            continue
        h2 = float(fs[t2])
        if h2 <= 0.0:
            continue
        tv, valley = valley_between_peaks(fs, t1i, t2)
        peak_ratio = min(h1, h2) / max(h1, h2)
        valley_ratio = valley / max(h1, h2)
        score = float(t2 - t1i) * peak_ratio / float(valley_ratio + eps)
        item = (score, t2, tv, peak_ratio, valley_ratio, valley)
        if best is None:
            best = item
            continue

        better = item[0] > best[0] + float(tie_tol)
        if not better and abs(item[0] - best[0]) <= float(tie_tol):
            # Stable multi-peak selection: keep the later-timescale partner.
            if item[1] > best[1]:
                better = True
            elif item[1] == best[1]:
                if item[4] < best[4] - float(tie_tol):
                    better = True
                elif abs(item[4] - best[4]) <= float(tie_tol) and item[3] > best[3] + float(tie_tol):
                    better = True
        if better:
            best = item

    if best is None:
        return None
    return best[1], best[2], best[3], best[4], best[5]


def detect_two_peak_metrics_timescale(
    f: np.ndarray,
    *,
    smooth_window: int = 11,
    t_ignore: int = 80,
    t_end: int = 400,
    min_ratio: float = 0.20,
    max_valley_ratio: float = 0.90,
    peak_prominence_rel: float = PEAK_PROMINENCE_REL,
    tie_tol: float = TIMESCALE_TIE_TOL,
) -> dict[str, float | int | bool | None]:
    """Canonical detector for multi-peak windows: first prominent peak + best late partner."""
    fs = moving_average(np.asarray(f, dtype=np.float64), int(smooth_window))
    peaks = strict_local_maxima(fs)
    if peaks.size == 0:
        return empty_peak_metrics()

    ref = float(np.max(fs))
    mask = (peaks >= int(t_ignore)) & (peaks <= int(t_end)) & (fs[peaks] >= float(peak_prominence_rel) * ref)
    peaks = peaks[mask]
    if peaks.size < 2:
        out = empty_peak_metrics()
        out["n_peaks"] = int(peaks.size)
        return out

    t1 = int(peaks[0])
    selected = select_timescale_t2(fs, t1, peaks[1:], tie_tol=float(tie_tol))
    if selected is None:
        out = empty_peak_metrics()
        out["n_peaks"] = int(peaks.size)
        out["t1"] = t1
        return out

    t2, tv, peak_ratio, valley_ratio, valley = selected
    h1 = float(fs[t1])
    h2 = float(fs[t2])
    is_bimodal = bool(peak_ratio >= float(min_ratio) and valley_ratio <= float(max_valley_ratio))
    return {
        "has_two": True,
        "is_bimodal": is_bimodal,
        "t1": int(t1),
        "t2": int(t2),
        "tv": int(tv),
        "h1": h1,
        "h2": h2,
        "valley": float(valley),
        "peak_ratio": float(peak_ratio),
        "peak_ratio_dir": float(h2 / h1) if h1 > 0.0 else 0.0,
        "valley_ratio": float(valley_ratio),
        "n_peaks": int(peaks.size),
    }


def phase_from_metrics(metrics: dict[str, float | int | bool | None]) -> int:
    if not bool(metrics["has_two"]):
        return 0
    if bool(metrics["is_bimodal"]):
        return 2
    return 1


def detect_two_peak_metrics_k2_coarse(
    f: np.ndarray,
    *,
    smooth_window: int = 9,
    t_ignore_pair: int = 18,
    min_sep_pair: int = 8,
    min_ratio: float = 0.10,
    max_valley_ratio: float = 0.90,
    peak_prominence_rel: float = PEAK_PROMINENCE_REL,
    tie_tol: float = TIMESCALE_TIE_TOL,
) -> dict[str, float | int | bool | None]:
    fg = parity_coarse_grain_k2(f)
    fs = moving_average(fg, int(smooth_window))
    p = strict_local_maxima(fs)
    if p.size == 0:
        return empty_peak_metrics()

    p = p[(p >= t_ignore_pair) & (fs[p] >= float(peak_prominence_rel) * float(np.max(fs)))]
    if p.size < 2:
        out = empty_peak_metrics()
        out["n_peaks"] = int(p.size)
        return out

    p1 = int(p[0])
    selected = select_timescale_t2(
        fs,
        p1,
        p[1:],
        min_sep=max(int(min_sep_pair), 1),
        tie_tol=float(tie_tol),
    )
    if selected is None:
        out = empty_peak_metrics()
        out["n_peaks"] = int(p.size)
        out["t1"] = int(2 * p1)
        return out

    p2, tv, peak_ratio, valley_ratio, valley = selected
    h1 = float(fs[p1])
    h2 = float(fs[p2])
    is_bimodal = bool(peak_ratio >= min_ratio and valley_ratio <= max_valley_ratio)

    return {
        "has_two": True,
        "is_bimodal": is_bimodal,
        "t1": int(2 * p1),
        "t2": int(2 * p2),
        "tv": int(2 * tv),
        "h1": h1,
        "h2": h2,
        "valley": valley,
        "peak_ratio": float(peak_ratio),
        "peak_ratio_dir": float(h2 / h1) if h1 > 0.0 else 0.0,
        "valley_ratio": float(valley_ratio),
        "n_peaks": int(p.size),
    }


def beta_token(beta: float) -> str:
    return f"{float(beta):.6f}"


def first_bimodal_beta(rows: Iterable[dict[str, object]]) -> float | None:
    for row in rows:
        if bool(row.get("is_bimodal")):
            return float(row["beta"])
    return None


def first_beta_at_fraction(beta: np.ndarray, frac: np.ndarray, threshold: float) -> float | None:
    if beta.size == 0 or frac.size == 0:
        return None
    idx = np.where(frac >= float(threshold))[0]
    if idx.size == 0:
        return None
    return float(beta[int(idx[0])])


def build_refine_beta_grid(
    cfg: RingEncounterConfig,
    coarse_onset: float | None,
) -> tuple[float, float, np.ndarray]:
    """Build the refinement beta grid.

    If coarse scan misses bimodality entirely, keep the refinement on full
    [beta_scan_min, beta_scan_max] to avoid missing edge onsets.
    """
    if coarse_onset is None:
        refine_min = float(cfg.beta_scan_min)
        refine_max = float(cfg.beta_scan_max)
    else:
        center = float(coarse_onset)
        refine_min = max(float(cfg.beta_scan_min), center - float(cfg.beta_refine_half_width))
        refine_max = min(float(cfg.beta_scan_max), center + float(cfg.beta_refine_half_width))

    refine_step = float(cfg.beta_refine_step)
    refine_betas = np.round(np.arange(refine_min, refine_max + 0.5 * refine_step, refine_step), 6)
    if refine_betas.size == 0:
        fallback = 0.5 * (float(cfg.beta_scan_min) + float(cfg.beta_scan_max))
        refine_betas = np.array([fallback], dtype=np.float64)
    return refine_min, refine_max, refine_betas


def write_encounter_scan_table(scan_rows: Iterable[dict[str, object]]) -> None:
    lines: list[str] = []
    lines.append("\\begin{tabular}{ccccccc}")
    lines.append("\\toprule")
    lines.append(r"$\beta$ & phase & $t_1$ & $t_2$ & peak balance ratio (min/max) & valley ratio & bimodal \\")
    lines.append("\\midrule")
    for r in scan_rows:
        t1 = "-" if r["t1"] is None else str(int(r["t1"]))
        t2 = "-" if r["t2"] is None else str(int(r["t2"]))
        has_pair = r["t1"] is not None and r["t2"] is not None
        peak_text = f"{float(r['peak_ratio']):.3f}" if has_pair else "--"
        valley_text = f"{float(r['valley_ratio']):.3f}" if has_pair else "--"
        lines.append(
            f"{float(r['beta']):.2f} & {int(r['phase'])} & {t1} & {t2} & {peak_text} & "
            f"{valley_text} & {int(bool(r['is_bimodal']))} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    (TABLE_DIR / "encounter_scan_table.tex").write_text("\n".join(lines), encoding="utf-8")


def write_onset_n_scan_table(rows: Iterable[dict[str, object]]) -> None:
    def fmt_num(value: object, digits: int = 3) -> str:
        if value is None:
            return "--"
        return f"{float(value):.{digits}f}"

    def fmt_source(source: object) -> str:
        tag = str(source or "main")
        if tag not in {"main", "extended", "none"}:
            tag = "none"
        return f"\\texttt{{{tag}}}"

    def fmt_onset_cell(row: dict[str, object]) -> str:
        source = str(row.get("onset_source", "main"))
        onset_val = row.get("onset_beta")
        if onset_val is None:
            max_beta = row.get("onset_search_max_beta")
            return f">{fmt_num(max_beta)}" if max_beta is not None else "--"
        text = fmt_num(onset_val)
        if source == "extended":
            return f"{text}\\textsuperscript{{*}}"
        return text

    lines: list[str] = []
    lines.append("\\begin{tabular}{cccccccc}")
    lines.append("\\toprule")
    lines.append(
        r"$N$ & onset $\beta^\dagger$ & onset source & $\beta_{\max}$ & clear frac & phase@0.20 & peak@0.20 & valley@0.20 \\"
    )
    lines.append("\\midrule")
    for row in rows:
        lines.append(
            f"{int(row['N'])} & {fmt_onset_cell(row)} & {fmt_source(row.get('onset_source'))} & "
            f"{fmt_num(row.get('onset_search_max_beta'))} & {fmt_num(row.get('clear_fraction'))} & "
            f"{int(row['rep_phase'])} & {fmt_num(row.get('rep_peak_ratio'))} & {fmt_num(row.get('rep_valley_ratio'))} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    (TABLE_DIR / "encounter_n_scan_table.tex").write_text("\n".join(lines), encoding="utf-8")


def write_fixed_cases_table(case_rows: Iterable[dict[str, object]]) -> None:
    lines: list[str] = []
    lines.append("\\begin{tabular}{lcccccc}")
    lines.append("\\toprule")
    lines.append(
        "Case & $(g_1,g_2)$ & phase & $t_1\\,(=2m)$ & $t_2\\,(=2m)$ & "
        "peak balance ratio ($\\bar{\\tilde f}$, min/max) & valley ratio ($\\bar{\\tilde f}$) \\\\"
    )
    lines.append("\\midrule")
    for row in case_rows:
        t1 = "-" if row["t1"] is None else str(int(row["t1"]))
        t2 = "-" if row["t2"] is None else str(int(row["t2"]))
        has_pair = row["t1"] is not None and row["t2"] is not None
        peak_text = f"{float(row['peak_ratio']):.3f}" if has_pair else "--"
        valley_text = f"{float(row['valley_ratio']):.3f}" if has_pair else "--"
        lines.append(
            f"{row['name']} & ({float(row['g1']):.2f},{float(row['g2']):.2f}) & {int(row['phase'])} & "
            f"{t1} & {t2} & {peak_text} & {valley_text} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    (TABLE_DIR / "fixedsite_example_table.tex").write_text("\n".join(lines), encoding="utf-8")


def write_fixedsite_phase_summary_table(phase_counts: dict[int, int], total_points: int) -> None:
    lines: list[str] = []
    lines.append("\\begin{tabular}{lcc}")
    lines.append("\\toprule")
    lines.append("Phase class & Count & Fraction \\\\")
    lines.append("\\midrule")
    for phase, label in ((0, "single"), (1, "weak"), (2, "clear")):
        count = int(phase_counts.get(phase, 0))
        frac = 0.0 if total_points <= 0 else float(count) / float(total_points)
        lines.append(f"{label} ({phase}) & {count} & {frac:.3f} \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    (TABLE_DIR / "fixedsite_phase_summary.tex").write_text("\n".join(lines), encoding="utf-8")


def write_fixedsite_parity_note_snippets(phase_counts: dict[int, int], total_points: int) -> None:
    clear_count = int(phase_counts.get(2, 0))
    frac_clear = 0.0 if total_points <= 0 else float(clear_count) / float(total_points)
    ratio_text = "--" if total_points <= 0 else f"{clear_count}/{total_points}={frac_clear:.3f}"
    cn_note = (
        f"其中 clear 占比为 ${ratio_text}$（脚本自动汇总）。"
        "该 fixed-site 基准刻意选在漂移主导区；K=2 奇偶粗粒化用于抑制 odd/even 微结构，"
        "使 clear 判定反映“分离时间尺度”而非 parity 伪峰。"
        "在首遇分布中 $f(0)=0$，因此 $\\widetilde f(0)=f(0)=0$，检测从 $m\\ge1$ 开始。"
        "与主文一致，候选峰对统一要求 $\\tau-t_1\\ge 2$（确保 $t_v(\\tau)=\\arg\\min_{t_1<t<\\tau}g_t$ 在开区间有定义）。"
        "该分支沿用主文同一 timescale 选峰口径：检测轨迹取 $g_m=\\bar{\\widetilde f}(m)$，"
        "首峰 + score 选 $t_2$（$R_{\\mathrm{peak}}(\\tau)=\\frac{\\min\\{g_{t_1},g_{\\tau}\\}}{\\max\\{g_{t_1},g_{\\tau}\\}}$，"
        "$R_{\\mathrm{peak}}=\\min/\\max$（即 $R_{\\mathrm{peak}}(t_2)$），"
        "$R_{\\mathrm{dir}}=g_{t_2}/g_{t_1}$ 仅作方向性诊断（可大于 1，不参与 phase 阈值），"
        "$\\mathrm{score}(\\tau)=\\frac{(\\tau-t_1)\\,R_{\\mathrm{peak}}(\\tau)}{R_{\\mathrm{valley}}(\\tau)+10^{-12}}$）；"
        "若 $|\\Delta\\mathrm{score}|\\le10^{-12}$，并列按“更晚 $\\tau$ $\\rightarrow$ 更小谷比 $\\rightarrow$ 更大峰平衡比”打破；"
        "在 parity 索引上施加 $\\tau-t_1\\ge\\mathrm{min\\_sep\\_pair}$，无额外 $t_{\\mathrm{end}}$ 截断，并按 $t=2m$ 回映。"
    )
    en_note = (
        f"The clear fraction is ${ratio_text}$ (auto-synced from generated scan data). "
        "This fixed-site benchmark is intentionally drift-dominated; K=2 parity coarse graining suppresses "
        "odd-even micro-structure so classification tracks separated time scales rather than parity artifacts. "
        "For first-passage traces, $f(0)=0$, so $\\widetilde f(0)=f(0)=0$ and diagnostics effectively start at $m\\ge1$. "
        "As in the main text, candidate peak pairs require $\\tau-t_1\\ge 2$ so "
        "$t_v(\\tau)=\\arg\\min_{t_1<t<\\tau}g_t$ is defined on a strict interior interval. "
        "This branch uses the same timescale selector as the main scan: detector trace "
        "$g_m=\\bar{\\widetilde f}(m)$, first peak + score-selected $t_2$ "
        "($R_{\\mathrm{peak}}(\\tau)=\\frac{\\min\\{g_{t_1},g_{\\tau}\\}}{\\max\\{g_{t_1},g_{\\tau}\\}}$, "
        "$R_{\\mathrm{peak}}=\\min/\\max$ (i.e., $R_{\\mathrm{peak}}(t_2)$), "
        "$R_{\\mathrm{dir}}=g_{t_2}/g_{t_1}$ as a directional diagnostic only (it may exceed 1 and does not enter phase thresholds), "
        "$\\mathrm{score}(\\tau)=\\frac{(\\tau-t_1)\\,R_{\\mathrm{peak}}(\\tau)}{R_{\\mathrm{valley}}(\\tau)+10^{-12}}$). "
        "If $|\\Delta\\mathrm{score}|\\le10^{-12}$, tie-break order is larger $\\tau\\rightarrow$smaller valley ratio"
        "$\\rightarrow$larger peak balance. With parity-index constraint "
        "$\\tau-t_1\\ge\\mathrm{min\\_sep\\_pair}$, no extra $t_{\\mathrm{end}}$ cutoff, and $t=2m$ back-mapping."
    )
    (TABLE_DIR / "fixedsite_parity_note_cn.tex").write_text(cn_note + "\n", encoding="utf-8")
    (TABLE_DIR / "fixedsite_parity_note_en.tex").write_text(en_note + "\n", encoding="utf-8")


def compute_shortcut_share_summary(
    f_total: np.ndarray,
    f_yes: np.ndarray,
    rep_metrics: dict[str, float | int | bool | None],
    *,
    smooth_window: int = 11,
    window_half_width: int = 20,
) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    total = np.asarray(f_total, dtype=np.float64)
    yes = np.asarray(f_yes, dtype=np.float64)
    if total.shape != yes.shape:
        raise ValueError("f_total and f_yes must share the same shape")

    inst_share = np.divide(yes, total, out=np.zeros_like(total), where=total > 0.0)
    inst_share_smooth = moving_average(inst_share, int(smooth_window))
    cum_total = np.cumsum(total)
    cum_yes = np.cumsum(yes)
    cum_share = np.divide(cum_yes, cum_total, out=np.zeros_like(cum_total), where=cum_total > 0.0)

    t1_val = rep_metrics.get("t1")
    tv_val = rep_metrics.get("tv")
    t2_val = rep_metrics.get("t2")
    t1 = None if t1_val is None else int(t1_val)
    tv = None if tv_val is None else int(tv_val)
    t2 = None if t2_val is None else int(t2_val)
    half = max(int(window_half_width), 0)

    switch_t: int | None = None
    if t1 is not None:
        start = max(0, min(t1, inst_share_smooth.size - 1))
        idx = np.where(inst_share_smooth[start:] <= 0.5)[0]
        if idx.size > 0:
            switch_t = int(start + int(idx[0]))

    def window_share(center: int | None) -> float | None:
        if center is None or total.size == 0:
            return None
        c = max(0, min(int(center), total.size - 1))
        lo = max(0, c - half)
        hi = min(total.size - 1, c + half)
        mass_total = float(np.sum(total[lo : hi + 1]))
        if mass_total <= 0.0:
            return None
        mass_yes = float(np.sum(yes[lo : hi + 1]))
        return mass_yes / mass_total

    summary: dict[str, object] = {
        "window_half_width": int(half),
        "t_switch_share50": switch_t,
        "share_t1_window": window_share(t1),
        "share_tv_window": window_share(tv),
        "share_t2_window": window_share(t2),
        "inst_share_t1": None if t1 is None else float(inst_share[t1]),
        "inst_share_t2": None if t2 is None else float(inst_share[t2]),
        "cum_share_tmax": float(cum_share[-1]) if cum_share.size > 0 else None,
    }
    return inst_share, cum_share, summary


def extract_prominent_peak_times(
    f: np.ndarray,
    *,
    smooth_window: int = 11,
    t_ignore: int = 80,
    rel_height: float = 0.01,
) -> list[int]:
    fs = moving_average(np.asarray(f, dtype=np.float64), int(smooth_window))
    peaks = strict_local_maxima(fs)
    if peaks.size == 0:
        return []
    ref = float(np.max(fs))
    if ref <= 0.0:
        return []
    peaks = peaks[(peaks >= int(t_ignore)) & (fs[peaks] >= float(rel_height) * ref)]
    return [int(x) for x in peaks.tolist()]


def write_encounter_key_metrics_table(
    *,
    coarse_onset: float | None,
    refined_onset: float | None,
    sensitivity_summary: dict[str, object],
    rep_metrics: dict[str, float | int | bool | None],
    shortcut_share_summary: dict[str, object],
    shift: float,
    mass_tmax: float,
    survival_tmax: float,
    beta0_rel_maxdiff: float | None,
    onset_scaling: dict[str, float | None],
) -> None:
    def fmt_num(value: object, *, digits: int = 3) -> str:
        if value is None:
            return "--"
        return f"{float(value):.{digits}f}"

    def fmt_int(value: object) -> str:
        if value is None:
            return "--"
        return str(int(value))

    lines: list[str] = []
    lines.append("\\begin{tabular}{lc}")
    lines.append("\\toprule")
    lines.append("Metric & Value \\\\")
    lines.append("\\midrule")
    lines.append(f"Coarse onset $\\beta$ & {fmt_num(coarse_onset)} \\\\")
    lines.append(f"Refined onset $\\beta$ & {fmt_num(refined_onset)} \\\\")
    lines.append(
        "Detector onset range & "
        f"[{fmt_num(sensitivity_summary.get('beta_min'))}, {fmt_num(sensitivity_summary.get('beta_max'))}] \\\\"
    )
    lines.append(f"Detector onset median & {fmt_num(sensitivity_summary.get('beta_median'))} \\\\")
    lines.append(f"Agreement crossing ($25\\%$) & {fmt_num(sensitivity_summary.get('beta_agreement_25'))} \\\\")
    lines.append(f"Agreement crossing ($50\\%$) & {fmt_num(sensitivity_summary.get('beta_agreement_50'))} \\\\")
    lines.append(f"Agreement crossing ($75\\%$) & {fmt_num(sensitivity_summary.get('beta_agreement_75'))} \\\\")
    lines.append(
        "Agreement width ($75\\%-25\\%$) & "
        f"{fmt_num(sensitivity_summary.get('beta_agreement_width_25_75'))} \\\\"
    )
    lines.append(
        "Agreement width ($75\\%-50\\%$) & "
        f"{fmt_num(sensitivity_summary.get('beta_agreement_width_50_75'))} \\\\"
    )
    lines.append(
        "Representative peaks $(t_1,t_2)$ & "
        f"({fmt_int(rep_metrics.get('t1'))}, {fmt_int(rep_metrics.get('t2'))}) \\\\"
    )
    lines.append(
        "Peak balance ratio (min/max) / valley ratio & "
        f"{fmt_num(rep_metrics.get('peak_ratio'), digits=3)} / {fmt_num(rep_metrics.get('valley_ratio'), digits=3)} \\\\"
    )
    lines.append(
        "Directed peak ratio $R_\\mathrm{dir}=\\bar f(t_2)/\\bar f(t_1)$ (diagnostic only) & "
        f"{fmt_num(rep_metrics.get('peak_ratio_dir'), digits=3)} \\\\"
    )
    half = shortcut_share_summary.get("window_half_width")
    half_text = "--" if half is None else str(int(half))
    lines.append(
        f"Shortcut share around $t_1$ ($\\pm{half_text}$) & "
        f"{fmt_num(shortcut_share_summary.get('share_t1_window'), digits=3)} \\\\"
    )
    lines.append(
        f"Shortcut share around valley ($\\pm{half_text}$) & "
        f"{fmt_num(shortcut_share_summary.get('share_tv_window'), digits=3)} \\\\"
    )
    lines.append(
        f"Shortcut share around $t_2$ ($\\pm{half_text}$) & "
        f"{fmt_num(shortcut_share_summary.get('share_t2_window'), digits=3)} \\\\"
    )
    lines.append(
        "First $\\le 50\\%$ shortcut-share time & "
        f"{fmt_int(shortcut_share_summary.get('t_switch_share50'))} \\\\"
    )
    lines.append(
        "Cumulative shortcut share at $t_{\\max}$ & "
        f"{fmt_num(shortcut_share_summary.get('cum_share_tmax'), digits=3)} \\\\"
    )
    lines.append(f"Shortcut shift mass & {fmt_num(shift, digits=3)} \\\\")
    lines.append(f"Beta=0 relative-chain max diff & {fmt_num(beta0_rel_maxdiff, digits=3)} \\\\")
    lines.append(f"Onset scaling slope (log-beta vs N) & {fmt_num(onset_scaling.get('slope'), digits=4)} \\\\")
    lines.append(f"Onset scaling $R^2$ & {fmt_num(onset_scaling.get('r2'), digits=3)} \\\\")
    lines.append(f"$\\sum_t f(t)$ at $t_{{\\max}}$ & {mass_tmax:.8f} \\\\")
    lines.append(f"$S(t_{{\\max}})$ & {survival_tmax:.3e} \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    (TABLE_DIR / "encounter_key_metrics.tex").write_text("\n".join(lines), encoding="utf-8")


def write_shortcut_rep_case_table(
    *,
    cfg: RingEncounterConfig,
    rep_beta: float,
    rep_metrics: dict[str, float | int | bool | None],
    prominent_peaks: list[int],
) -> None:
    def fmt_int(value: object) -> str:
        if value is None:
            return "--"
        return str(int(value))

    def fmt_num(value: object, digits: int = 3) -> str:
        if value is None:
            return "--"
        return f"{float(value):.{digits}f}"

    p = [fmt_int(v) for v in prominent_peaks[:3]]
    while len(p) < 3:
        p.append("--")

    lines: list[str] = []
    lines.append("\\begin{tabular}{ll}")
    lines.append("\\toprule")
    lines.append("Field & Value \\\\")
    lines.append("\\midrule")
    lines.append(f"$N$ / $q$ & {cfg.N} / {cfg.q:.2f} \\\\")
    lines.append(f"$(g_1,g_2)$ & ({cfg.g1:.2f}, {cfg.g2:.2f}) \\\\")
    lines.append(f"Starts $(n_0,m_0)$ & ({cfg.n0}, {cfg.m0}) \\\\")
    lines.append(
        f"Shortcut $(\\mathrm{{src}}\\to\\mathrm{{dst}})$ & ({cfg.shortcut_src} $\\to$ {cfg.shortcut_dst}) \\\\"
    )
    lines.append(f"Representative $\\beta$ & {rep_beta:.2f} \\\\")
    lines.append(
        "Detector pair $(t_1,t_2,t_v)$ & "
        f"({fmt_int(rep_metrics.get('t1'))}, {fmt_int(rep_metrics.get('t2'))}, {fmt_int(rep_metrics.get('tv'))}) \\\\"
    )
    lines.append(f"Prominent peaks $(P_1,P_2,P_3)$ & ({p[0]}, {p[1]}, {p[2]}) \\\\")
    lines.append(
        "Peak balance ratio (min/max) / valley ratio & "
        f"{fmt_num(rep_metrics.get('peak_ratio'))} / {fmt_num(rep_metrics.get('valley_ratio'))} \\\\"
    )
    lines.append(
        "Directed peak ratio $R_\\mathrm{dir}=\\bar f(t_2)/\\bar f(t_1)$ (diagnostic only) & "
        f"{fmt_num(rep_metrics.get('peak_ratio_dir'))} \\\\"
    )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    (TABLE_DIR / "encounter_shortcut_rep_case.tex").write_text("\n".join(lines), encoding="utf-8")


def write_auto_narrative_snippets(
    *,
    scan_rows: list[dict[str, object]],
    rep_beta: float,
    rep_metrics: dict[str, float | int | bool | None],
    coarse_onset: float | None,
    refined_onset: float | None,
    refine_min: float,
    refine_max: float,
    refine_step: float,
    sensitivity_summary: dict[str, object],
    mass_tmax: float,
    survival_tmax: float,
    n_scan_rows: list[dict[str, object]],
    n_scan_summary: dict[str, object],
) -> None:
    def fmt_beta(value: object, digits: int = 2, fallback: str = "--") -> str:
        if value is None:
            return fallback
        return f"{float(value):.{digits}f}"

    def fmt_num(value: object, digits: int = 3, fallback: str = "--") -> str:
        if value is None:
            return fallback
        return f"{float(value):.{digits}f}"

    def fmt_int(value: object, fallback: str = "--") -> str:
        if value is None:
            return fallback
        return str(int(value))

    phase1_betas = [float(r["beta"]) for r in scan_rows if int(r["phase"]) == 1]
    phase1_upper = max(phase1_betas) if phase1_betas else None
    clear_onset = first_bimodal_beta(scan_rows)

    t1 = rep_metrics.get("t1")
    t2 = rep_metrics.get("t2")
    peak_ratio = rep_metrics.get("peak_ratio")
    peak_ratio_dir = rep_metrics.get("peak_ratio_dir")
    valley_ratio = rep_metrics.get("valley_ratio")

    beta_min = sensitivity_summary.get("beta_min")
    beta_max = sensitivity_summary.get("beta_max")
    beta_median = sensitivity_summary.get("beta_median")
    beta_50 = sensitivity_summary.get("beta_agreement_50")
    beta_75 = sensitivity_summary.get("beta_agreement_75")
    beta_w = sensitivity_summary.get("beta_agreement_width_25_75")

    n_values = [int(r["N"]) for r in n_scan_rows]
    n_set_text = ",".join(str(v) for v in n_values)
    ext_rows = [
        (int(r["N"]), float(r["onset_beta"]))
        for r in n_scan_rows
        if str(r.get("onset_source")) == "extended" and r.get("onset_beta") is not None
    ]
    main_rows = [
        int(r["N"])
        for r in n_scan_rows
        if str(r.get("onset_source")) == "main" and r.get("onset_beta_window") is not None
    ]
    ext_desc_cn = (
        "；".join(f"$N={n}$ 在扩展扫描下于 $\\beta\\approx{b:.2f}$ 才进入 clear-bimodal" for n, b in ext_rows)
        if ext_rows
        else "本轮未触发扩展区回收 onset"
    )
    ext_desc_en = (
        "; ".join(f"$N={n}$ is recovered only by extension at $\\beta\\approx{b:.2f}$" for n, b in ext_rows)
        if ext_rows
        else "No extension-only onset recovery is needed in this run"
    )
    main_desc_cn = (
        f"$N\\in\\{{{','.join(str(v) for v in sorted(main_rows))}\\}}$ 均在名义窗口内出现 clear onset"
        if main_rows
        else "名义窗口内无 clear onset"
    )
    main_desc_en = (
        f"$N\\in\\{{{','.join(str(v) for v in sorted(main_rows))}\\}}$ all show clear onset inside the nominal window"
        if main_rows
        else "No clear onset appears inside the nominal window"
    )

    cn_lines = [
        "% Auto-generated from data/case_summary.json; do not edit by hand.",
        "\\begin{enumerate}[leftmargin=1.4em]",
        f"  \\item $\\beta\\le{fmt_beta(phase1_upper)}$：phase=1（弱双峰/过渡）；",
        f"  \\item 粗扫描从 $\\beta\\approx{fmt_beta(clear_onset)}$ 起：phase=2（clear bimodal）；",
        (
            f"  \\item 代表点 $\\beta={rep_beta:.2f}$：两峰在 "
            f"$t_1={fmt_int(t1)},\\ t_2={fmt_int(t2)}$，"
            f"峰平衡比 $R_\\mathrm{{peak}}={fmt_num(peak_ratio)}$（min/max），"
            f"有向峰比 $R_\\mathrm{{dir}}={fmt_num(peak_ratio_dir)}$（仅方向性诊断，可大于 1，不参与 phase 阈值），"
            f"谷比 $R_\\mathrm{{valley}}={fmt_num(valley_ratio)}$。"
        ),
        "\\end{enumerate}",
        (
            f"进一步在 $\\beta\\in[{fmt_beta(refine_min)},{fmt_beta(refine_max)}]$ 上做步长 "
            f"${fmt_beta(refine_step, digits=3)}$ 的细扫描，名义 clear-bimodal onset 约为 "
            f"$\\beta\\approx{fmt_beta(refined_onset)}$。"
        ),
        (
            "在检测参数扰动下，首次 onset 区间为 "
            f"$[{fmt_beta(beta_min)},{fmt_beta(beta_max)}]$，中位数约 {fmt_beta(beta_median)}；"
            f"detector-agreement 在 $\\beta\\approx{fmt_beta(beta_50)}$ 首次超过 50\\%，"
            f"在 $\\beta\\approx{fmt_beta(beta_75)}$ 超过 75\\%，"
            f"对应一致性窗宽 $\\Delta\\beta_{{25\\to75}}\\approx{fmt_beta(beta_w)}$。"
        ),
        (
            "质量守恒检查："
            f"$\\sum_t f(t)={mass_tmax:.8f}$，$S(t_{{\\max}})\\approx{survival_tmax:.2e}$。"
        ),
    ]
    (TABLE_DIR / "encounter_consistency_summary_cn.tex").write_text("\n".join(cn_lines), encoding="utf-8")

    en_lines = [
        "% Auto-generated from data/case_summary.json; do not edit by hand.",
        "\\begin{enumerate}[leftmargin=1.4em]",
        f"  \\item $\\beta\\le{fmt_beta(phase1_upper)}$: phase 1 (weak/transition double structure);",
        f"  \\item coarse-onset from $\\beta\\approx{fmt_beta(clear_onset)}$: phase 2 (clear bimodal);",
        (
            f"  \\item representative case $\\beta={rep_beta:.2f}$: peaks at "
            f"$t_1={fmt_int(t1)},\\ t_2={fmt_int(t2)}$, "
            f"peak-balance ratio $R_\\mathrm{{peak}}={fmt_num(peak_ratio)}$ (min/max), "
            f"directed peak ratio $R_\\mathrm{{dir}}={fmt_num(peak_ratio_dir)}$ "
            "(diagnostic only; may exceed 1; not used in phase thresholds), "
            f"valley ratio $R_\\mathrm{{valley}}={fmt_num(valley_ratio)}$."
        ),
        "\\end{enumerate}",
        (
            f"We further refine onset on $\\beta\\in[{fmt_beta(refine_min)},{fmt_beta(refine_max)}]$ with "
            f"step ${fmt_beta(refine_step, digits=3)}$, giving nominal clear-bimodal onset "
            f"$\\beta\\approx{fmt_beta(refined_onset)}$."
        ),
        (
            "Under detector perturbations, first-onset range is "
            f"$[{fmt_beta(beta_min)},{fmt_beta(beta_max)}]$ with median {fmt_beta(beta_median)}; "
            f"detector-agreement first crosses 50\\% at $\\beta\\approx{fmt_beta(beta_50)}$ "
            f"and 75\\% at $\\beta\\approx{fmt_beta(beta_75)}$, "
            f"with agreement width $\\Delta\\beta_{{25\\to75}}\\approx{fmt_beta(beta_w)}$."
        ),
        (
            "Mass-conservation check: "
            f"$\\sum_t f(t)={mass_tmax:.8f}$, $S(t_{{\\max}})\\approx{survival_tmax:.2e}$."
        ),
    ]
    (TABLE_DIR / "encounter_consistency_summary_en.tex").write_text("\n".join(en_lines), encoding="utf-8")

    nscan_cn_lines = [
        "% Auto-generated from data/encounter_onset_n_scan.csv; do not edit by hand.",
        (
            "为避免结论仅依赖单一基准尺寸 $N=101$，我们额外做了 "
            f"$N\\in\\{{{n_set_text}\\}}$ 的 ring-size 稳健性扫描，并按比例缩放 "
            "$(n_0,m_0,\\text{src},\\text{dst})$ 几何位置。"
        ),
        (
            "对每个 $N$，先在名义窗口 $\\beta\\in[0,0.30]$ 上重算 coarse onset 与 clear-bimodal 覆盖率，"
            "并与主文一致使用同一 timescale 选峰口径（首峰 + score 选 $t_2$），"
            "并比较代表点 $\\beta=0.20$ 的 peak/valley 比值；若名义窗口内未出现 clear onset，"
            "则做一次单侧扩展扫描到 $\\beta\\le0.50$（步长 $0.02$）。"
        ),
        (
            f"本轮统计：共 {int(n_scan_summary.get('count_total', 0))} 个 $N$，"
            f"名义窗口内找到 onset 的有 {int(n_scan_summary.get('count_with_onset_window', 0))} 个，"
            f"扩展回收 {int(n_scan_summary.get('count_extended', 0))} 个，"
            f"未检出 {int(n_scan_summary.get('count_none', 0))} 个。"
        ),
        f"扩展回收细节：{ext_desc_cn}。",
        f"窗口内结论：{main_desc_cn}。",
    ]
    (TABLE_DIR / "encounter_nscan_summary_cn.tex").write_text("\n".join(nscan_cn_lines), encoding="utf-8")

    nscan_en_lines = [
        "% Auto-generated from data/encounter_onset_n_scan.csv; do not edit by hand.",
        (
            "To avoid over-reliance on the single baseline size $N=101$, we additionally scan "
            f"$N\\in\\{{{n_set_text}\\}}$ with geometry-scaled $(n_0,m_0,\\mathrm{{src}},\\mathrm{{dst}})$."
        ),
        (
            "For each $N$, we recompute coarse onset and clear-bimodal coverage on the nominal "
            "$\\beta\\in[0,0.30]$ grid using the same timescale selector as the main scan "
            "(first peak + score-selected $t_2$), then compare representative peak/valley ratios at "
            "$\\beta=0.20$; if no clear onset appears, we extend once to $\\beta\\le0.50$ (step $0.02$)."
        ),
        (
            f"Current run summary: {int(n_scan_summary.get('count_total', 0))} size points total, "
            f"{int(n_scan_summary.get('count_with_onset_window', 0))} with nominal-window onset, "
            f"{int(n_scan_summary.get('count_extended', 0))} recovered by extension, "
            f"{int(n_scan_summary.get('count_none', 0))} still unresolved."
        ),
        f"Extension details: {ext_desc_en}.",
        f"Nominal-window conclusion: {main_desc_en}.",
    ]
    (TABLE_DIR / "encounter_nscan_summary_en.tex").write_text("\n".join(nscan_en_lines), encoding="utf-8")


def plot_onset_n_scan(rows: list[dict[str, object]]) -> None:
    if not rows:
        return

    N_vals = np.array([int(r["N"]) for r in rows], dtype=np.int64)
    onset_vals = np.array(
        [np.nan if r.get("onset_beta") is None else float(r["onset_beta"]) for r in rows],
        dtype=np.float64,
    )
    clear_frac = np.array([float(r["clear_fraction"]) for r in rows], dtype=np.float64)
    peak_ratio = np.array([float(r["rep_peak_ratio"]) for r in rows], dtype=np.float64)
    valley_ratio = np.array([float(r["rep_valley_ratio"]) for r in rows], dtype=np.float64)
    onset_source = np.array([str(r.get("onset_source", "main")) for r in rows], dtype=object)

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(6.6, 5.9),
        sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.6]},
    )

    mask = np.isfinite(onset_vals)
    if np.any(mask):
        ax1.plot(N_vals[mask], onset_vals[mask], "-", color="#66bb6a", lw=1.2, alpha=0.9)
    mask_main = mask & (onset_source == "main")
    mask_ext = mask & (onset_source == "extended")
    if np.any(mask_main):
        ax1.plot(
            N_vals[mask_main],
            onset_vals[mask_main],
            "o",
            color="#2e7d32",
            ms=6,
            label="onset inside beta<=0.30 window",
        )
    if np.any(mask_ext):
        ax1.plot(
            N_vals[mask_ext],
            onset_vals[mask_ext],
            "*",
            color="#ef6c00",
            ms=11,
            label="onset found by beta-window extension",
        )
    ax1.plot(N_vals, clear_frac, "s--", color="#1565c0", lw=1.5, label="clear fraction over beta grid")
    ax1.set_ylabel("onset / fraction")
    ax1.set_ylim(-0.02, 1.02)
    ax1.set_title("Ring-size robustness of bimodality onset")
    ax1.grid(alpha=0.25)
    ax1.legend(loc="best", fontsize=8)

    ax2.plot(N_vals, peak_ratio, "o-", color="#d81b60", lw=1.5, label="peak balance ratio @ beta=0.20")
    ax2.plot(N_vals, valley_ratio, "s-", color="#1e88e5", lw=1.4, label="valley ratio @ beta=0.20")
    ax2.axhline(0.20, color="#d81b60", lw=1.0, ls="--", alpha=0.70)
    ax2.axhline(0.90, color="#1e88e5", lw=1.0, ls="--", alpha=0.70)
    ax2.set_xlabel("ring size N")
    ax2.set_ylabel("ratio")
    ax2.grid(alpha=0.25)
    ax2.legend(loc="best", fontsize=8)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_onset_n_scan.pdf")
    plt.close(fig)


def plot_onset_source_window(rows: list[dict[str, object]]) -> None:
    if not rows:
        return

    N_vals = np.array([int(r["N"]) for r in rows], dtype=np.int64)
    onset_vals = np.array(
        [np.nan if r.get("onset_beta") is None else float(r["onset_beta"]) for r in rows],
        dtype=np.float64,
    )
    search_cap = np.array(
        [np.nan if r.get("onset_search_max_beta") is None else float(r["onset_search_max_beta"]) for r in rows],
        dtype=np.float64,
    )
    onset_source = np.array([str(r.get("onset_source", "main")) for r in rows], dtype=object)

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(6.6, 5.5),
        sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.2]},
    )

    nominal_cap = 0.30
    mask_search = np.isfinite(search_cap)
    mask_found = np.isfinite(onset_vals)
    mask_main = mask_found & (onset_source == "main")
    mask_ext = mask_found & (onset_source == "extended")
    mask_none = (onset_source == "none") & mask_search

    if np.any(mask_search):
        ax1.plot(
            N_vals[mask_search],
            search_cap[mask_search],
            "o--",
            color="#1e88e5",
            lw=1.4,
            ms=5,
            label=r"search cap $\beta_{\max}(N)$",
        )
    ax1.axhline(nominal_cap, color="#607d8b", lw=1.1, ls="--", label=r"nominal cap $0.30$")

    if np.any(mask_main):
        ax1.plot(
            N_vals[mask_main],
            onset_vals[mask_main],
            "o",
            color="#2e7d32",
            ms=6,
            label="onset in nominal window",
        )
    if np.any(mask_ext):
        ax1.plot(
            N_vals[mask_ext],
            onset_vals[mask_ext],
            "*",
            color="#ef6c00",
            ms=12,
            label="onset recovered by extension",
        )
    if np.any(mask_none):
        ax1.plot(
            N_vals[mask_none],
            search_cap[mask_none],
            "v",
            color="#616161",
            ms=6,
            label="no onset up to search cap",
        )

    y_upper = nominal_cap + 0.06
    if np.any(mask_search):
        y_upper = max(y_upper, float(np.nanmax(search_cap[mask_search])) + 0.04)
    if np.any(mask_found):
        y_upper = max(y_upper, float(np.nanmax(onset_vals[mask_found])) + 0.04)
    ax1.set_ylim(-0.01, min(1.02, y_upper))
    ax1.set_ylabel("beta")
    ax1.set_title("Onset source and search-window diagnostics across ring sizes")
    ax1.grid(alpha=0.25)
    ax1.legend(loc="best", fontsize=8)

    source_code = np.full(N_vals.shape, 2, dtype=np.float64)
    source_code[onset_source == "main"] = 0.0
    source_code[onset_source == "extended"] = 1.0
    source_code[onset_source == "none"] = 2.0
    ax2.plot(N_vals, source_code, "-", color="#9e9e9e", lw=1.0, alpha=0.75)
    if np.any(onset_source == "main"):
        ax2.plot(
            N_vals[onset_source == "main"],
            source_code[onset_source == "main"],
            "o",
            color="#2e7d32",
            ms=6,
        )
    if np.any(onset_source == "extended"):
        ax2.plot(
            N_vals[onset_source == "extended"],
            source_code[onset_source == "extended"],
            "*",
            color="#ef6c00",
            ms=12,
        )
    if np.any(onset_source == "none"):
        ax2.plot(
            N_vals[onset_source == "none"],
            source_code[onset_source == "none"],
            "v",
            color="#616161",
            ms=6,
        )
    ax2.set_yticks([0, 1, 2], labels=["main", "extended", "none"])
    ax2.set_ylim(-0.45, 2.45)
    ax2.set_xlabel("ring size N")
    ax2.set_ylabel("onset source")
    ax2.grid(alpha=0.25, axis="y")

    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_onset_source_window.pdf")
    plt.close(fig)


def run_onset_n_scan(base_cfg: RingEncounterConfig) -> list[dict[str, object]]:
    scan_cfg = OnsetNScanConfig()
    beta_min = float(base_cfg.beta_scan_min)
    beta_max = float(base_cfg.beta_scan_max)
    betas = np.linspace(beta_min, beta_max, base_cfg.beta_scan_points)
    ext_step = max(float(scan_cfg.onset_extension_step), 1e-6)
    ext_start = beta_max + ext_step
    ext_max = max(beta_max, float(scan_cfg.onset_extension_max))
    ext_betas = (
        np.round(np.arange(ext_start, ext_max + 0.5 * ext_step, ext_step), 6)
        if ext_max >= ext_start
        else np.zeros(0, dtype=np.float64)
    )
    rows: list[dict[str, object]] = []

    for N in scan_cfg.N_grid:
        n = int(N)
        n0 = scaled_index(base_cfg.n0, base_cfg.N, n)
        m0 = scaled_index(base_cfg.m0, base_cfg.N, n)
        src = scaled_index(base_cfg.shortcut_src, base_cfg.N, n)
        dst = scaled_index(base_cfg.shortcut_dst, base_cfg.N, n)
        if dst == src:
            dst = (dst + max(1, n // 3)) % n
        if m0 == n0:
            m0 = (m0 + max(1, n // 2)) % n

        t_ignore = max(30, int(np.round(float(base_cfg.t_ignore) * float(n) / float(base_cfg.N))))
        t_max_scan = int(np.round(float(base_cfg.t_max_scan) * float(n) / float(base_cfg.N)))
        t_max_scan = min(max(t_max_scan, scan_cfg.t_max_min), scan_cfg.t_max_max)
        t_end_scan = int(np.round(float(base_cfg.peak_window_end) * float(n) / float(base_cfg.N)))
        t_end_scan = min(max(t_end_scan, t_ignore + 40), t_max_scan)

        P2 = build_ring_transition(
            n,
            base_cfg.q,
            base_cfg.g2,
            shortcut_src=src,
            shortcut_dst=dst,
            beta=0.0,
        )

        def eval_single_beta(beta_f: float) -> dict[str, object]:
            P1 = build_ring_transition(
                n,
                base_cfg.q,
                base_cfg.g1,
                shortcut_src=src,
                shortcut_dst=dst,
                beta=beta_f,
            )
            f, surv = first_encounter_any(P1, P2, n0, m0, t_max_scan)
            metrics = detect_two_peak_metrics_timescale(
                f,
                smooth_window=11,
                t_ignore=t_ignore,
                t_end=t_end_scan,
                min_ratio=0.20,
                max_valley_ratio=0.90,
                peak_prominence_rel=PEAK_PROMINENCE_REL,
                tie_tol=TIMESCALE_TIE_TOL,
            )
            return {
                "beta": beta_f,
                "phase": int(phase_from_metrics(metrics)),
                "t1": metrics["t1"],
                "t2": metrics["t2"],
                "peak_ratio": float(metrics["peak_ratio"]),
                "valley_ratio": float(metrics["valley_ratio"]),
                "is_bimodal": bool(metrics["is_bimodal"]),
                "mass_tmax": float(np.sum(f)),
                "survival_tmax": float(surv[-1]),
            }

        beta_rows: list[dict[str, object]] = []
        for beta in betas:
            beta_rows.append(eval_single_beta(float(beta)))

        onset_beta_window = first_bimodal_beta(beta_rows)
        onset_beta_ext: float | None = None
        onset_source = "main"
        onset_search_max_beta = beta_max
        if onset_beta_window is None:
            onset_source = "none"
            if ext_betas.size > 0:
                onset_search_max_beta = float(ext_betas[-1])
                for beta in ext_betas:
                    ext_row = eval_single_beta(float(beta))
                    if bool(ext_row["is_bimodal"]):
                        onset_beta_ext = float(ext_row["beta"])
                        onset_source = "extended"
                        onset_search_max_beta = float(ext_row["beta"])
                        break
        onset_beta = onset_beta_window if onset_beta_window is not None else onset_beta_ext

        clear_fraction = float(np.mean([1.0 if bool(r["is_bimodal"]) else 0.0 for r in beta_rows])) if beta_rows else 0.0
        rep_row = min(beta_rows, key=lambda r: abs(float(r["beta"]) - float(scan_cfg.rep_beta)))
        rows.append(
            {
                "N": n,
                "n0": n0,
                "m0": m0,
                "shortcut_src": src,
                "shortcut_dst": dst,
                "t_ignore": t_ignore,
                "t_max_scan": t_max_scan,
                "onset_beta": onset_beta,
                "onset_beta_window": onset_beta_window,
                "onset_beta_ext": onset_beta_ext,
                "onset_source": onset_source,
                "onset_search_max_beta": onset_search_max_beta,
                "clear_fraction": clear_fraction,
                "rep_beta": float(rep_row["beta"]),
                "rep_phase": int(rep_row["phase"]),
                "rep_t1": rep_row["t1"],
                "rep_t2": rep_row["t2"],
                "rep_peak_ratio": float(rep_row["peak_ratio"]),
                "rep_valley_ratio": float(rep_row["valley_ratio"]),
                "rep_mass_tmax": float(rep_row["mass_tmax"]),
                "rep_survival_tmax": float(rep_row["survival_tmax"]),
            }
        )

    with (DATA_DIR / "encounter_onset_n_scan.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "N",
                "n0",
                "m0",
                "shortcut_src",
                "shortcut_dst",
                    "t_ignore",
                    "t_max_scan",
                    "onset_beta",
                    "onset_beta_window",
                    "onset_beta_ext",
                    "onset_source",
                    "onset_search_max_beta",
                    "clear_fraction",
                    "rep_beta",
                    "rep_phase",
                    "rep_t1",
                    "rep_t2",
                "rep_peak_ratio",
                "rep_valley_ratio",
                "rep_mass_tmax",
                "rep_survival_tmax",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row["N"],
                    row["n0"],
                    row["m0"],
                    row["shortcut_src"],
                    row["shortcut_dst"],
                    row["t_ignore"],
                    row["t_max_scan"],
                    row["onset_beta"],
                    row["onset_beta_window"],
                    row["onset_beta_ext"],
                    row["onset_source"],
                    row["onset_search_max_beta"],
                    row["clear_fraction"],
                    row["rep_beta"],
                    row["rep_phase"],
                    row["rep_t1"],
                    row["rep_t2"],
                    row["rep_peak_ratio"],
                    row["rep_valley_ratio"],
                    row["rep_mass_tmax"],
                    row["rep_survival_tmax"],
                ]
            )

    write_onset_n_scan_table(rows)
    plot_onset_n_scan(rows)
    plot_onset_source_window(rows)
    return rows


def plot_ring_geometry(cfg: RingEncounterConfig, rep_beta: float, *, fixed_delta: int | None = 0) -> None:
    N = cfg.N
    theta = 2.0 * np.pi * np.arange(N, dtype=np.float64) / float(N)
    x = np.cos(theta)
    y = np.sin(theta)

    fig, ax = plt.subplots(figsize=(5.8, 5.2))
    ax.plot(np.r_[x, x[0]], np.r_[y, y[0]], color="#666666", lw=1.2)

    # Sparse node markers for readability.
    idx_show = np.arange(0, N, max(1, N // 20))
    ax.scatter(x[idx_show], y[idx_show], s=12, c="#999999", zorder=3)

    n0 = cfg.n0 % N
    m0 = cfg.m0 % N
    src = cfg.shortcut_src % N
    dst = cfg.shortcut_dst % N
    delta = None if fixed_delta is None else int(fixed_delta) % N
    if delta is not None and delta in {n0, m0, src, dst}:
        raise ValueError(
            "fixed-site delta must not overlap with n0/m0/src/dst in geometry plot; "
            f"got delta={delta}, n0={n0}, m0={m0}, src={src}, dst={dst}"
        )

    # Draw exact node positions (no visual offset); overlap like n0==src is intentional.
    ax.scatter([x[n0]], [y[n0]], c="#e53935", marker="s", s=80, zorder=6, label="walker A start")
    ax.scatter([x[m0]], [y[m0]], c="#0d47a1", marker="D", s=80, zorder=6, label="walker B start")
    ax.scatter([x[src]], [y[src]], c="#6a1b9a", marker="o", s=45, zorder=7, label="shortcut src")
    ax.scatter([x[dst]], [y[dst]], c="#8e24aa", marker="o", s=45, zorder=7, label="shortcut dst")
    if delta is not None:
        ax.scatter(
            [x[delta]],
            [y[delta]],
            c="#f57f17",
            marker="*",
            s=120,
            zorder=8,
            label="fixed-site delta",
            edgecolors="#5d4037",
            linewidths=0.5,
        )

    src_pos = np.array([x[src], y[src]], dtype=np.float64)
    dst_pos = np.array([x[dst], y[dst]], dtype=np.float64)
    ax.annotate(
        "",
        xy=(dst_pos[0], dst_pos[1]),
        xytext=(src_pos[0], src_pos[1]),
        arrowprops=dict(arrowstyle="->", lw=2.0, color="#8e24aa"),
        zorder=6,
    )

    # Text labels: if roles share a node, show combined label (e.g., "n0=src").
    role_groups: dict[int, list[tuple[str, str]]] = {
        n0: [("n0", "#b71c1c")],
        m0: [("m0", "#0d47a1")],
    }
    role_groups.setdefault(src, []).append(("src", "#6a1b9a"))
    role_groups.setdefault(dst, []).append(("dst", "#6a1b9a"))
    if delta is not None:
        role_groups.setdefault(delta, []).append(("delta", "#e65100"))

    for idx, tags in role_groups.items():
        base = np.array([x[idx], y[idx]], dtype=np.float64)
        rnorm = np.linalg.norm(base)
        radial = base / rnorm if rnorm > 1e-12 else np.array([1.0, 0.0], dtype=np.float64)
        text_pos = base + 0.10 * radial
        label = "=".join(tag for tag, _ in tags)
        color = tags[0][1] if len(tags) == 1 else "#4e342e"
        ax.text(text_pos[0], text_pos[1], label, color=color, fontsize=9)

    ax.set_aspect("equal")
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.25, 1.25)
    ax.axis("off")
    ax.set_title(f"1D ring encounter geometry (N={N}, beta={rep_beta:.2f})")
    ax.legend(loc="lower left", fontsize=8, frameon=True)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_ring_geometry.pdf")
    plt.close(fig)


def plot_encounter_overlay(cfg: RingEncounterConfig, overlay_series: dict[str, list[float]]) -> None:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.6, 6.0), sharex=False, gridspec_kw={"height_ratios": [1.0, 1.0]})
    colors = {
        "beta_0.00": "#333333",
        "beta_0.12": "#1e88e5",
        "beta_0.20": "#e53935",
        "beta_0.28": "#8e24aa",
    }

    for key, values in overlay_series.items():
        y = np.array(values, dtype=np.float64)
        t = np.arange(y.size, dtype=np.int64)
        ys = moving_average(y, 11)
        c = colors.get(key, "#777777")
        label = key.replace("beta_", r"$\beta$=")
        ax1.plot(t, ys, color=c, lw=1.7, label=label)
        ax2.plot(t, ys, color=c, lw=1.7, label=label)

    ax1.set_xlim(0, cfg.t_max_case)
    ax1.set_ylabel(r"$f_{enc}(t)$")
    ax1.set_title("Full timescale")
    ax1.grid(alpha=0.25)
    ax1.legend(loc="upper right", fontsize=9)

    ax2.set_xlim(cfg.t_ignore, 420)
    ax2.set_xlabel("t")
    ax2.set_ylabel(r"$f_{enc}(t)$")
    ax2.set_title(f"Intermediate/late window (t >= {cfg.t_ignore})")
    ax2.grid(alpha=0.25)

    fig.suptitle("1D ring encounter FPT vs shortcut strength", y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(FIG_DIR / "encounter_fpt_overlay.pdf")
    plt.close(fig)


def plot_shortcut_representative_case(
    cfg: RingEncounterConfig,
    f_rep: np.ndarray,
    rep_metrics: dict[str, float | int | bool | None],
    prominent_peaks: list[int],
    rep_beta: float,
) -> None:
    t = np.arange(f_rep.size, dtype=np.int64)
    ys = moving_average(np.asarray(f_rep, dtype=np.float64), 11)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.8, 6.0), sharex=False, gridspec_kw={"height_ratios": [1.0, 1.0]})

    ax1.plot(t, ys, color="#222222", lw=1.8)
    ax1.set_xlim(0, cfg.t_max_case)
    ax1.set_ylabel(r"$f_{enc}(t)$")
    ax1.set_title("Representative shortcut case: full timescale")
    ax1.grid(alpha=0.25)

    ax2.plot(t, ys, color="#222222", lw=1.8, label="smoothed encounter FPT")
    ax2.set_xlim(cfg.t_ignore, 420)
    ax2.set_xlabel("t")
    ax2.set_ylabel(r"$f_{enc}(t)$")
    ax2.set_title("Intermediate/late window with labeled peaks")
    ax2.grid(alpha=0.25)

    for key, color, label in (
        ("t1", "#d81b60", "t1"),
        ("tv", "#455a64", "tv"),
        ("t2", "#1e88e5", "t2"),
    ):
        val = rep_metrics.get(key)
        if val is None:
            continue
        tt = int(val)
        for ax in (ax1, ax2):
            ax.axvline(tt, color=color, lw=1.0, ls="--", alpha=0.75)
        if 0 <= tt < ys.size:
            ax2.text(tt + 2, ys[tt] * 1.04, label, color=color, fontsize=8)

    for idx, tt in enumerate(prominent_peaks[:3], start=1):
        if tt < 0 or tt >= ys.size:
            continue
        ax2.plot(tt, ys[tt], "o", color="#8e24aa", ms=5)
        ax2.text(tt + 3, ys[tt] * 1.08, f"P{idx}={tt}", color="#6a1b9a", fontsize=8)

    ax2.legend(loc="upper right", fontsize=8)
    fig.suptitle(f"1D ring shortcut representative instance ($\\beta={rep_beta:.2f}$)", y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(FIG_DIR / "encounter_shortcut_rep_case.pdf")
    plt.close(fig)


def plot_shortcut_decomp(
    cfg: RingEncounterConfig,
    f_total: np.ndarray,
    f_no: np.ndarray,
    f_yes: np.ndarray,
    rep_metrics: dict[str, float | int | bool | None],
    rep_beta: float,
) -> None:
    t = np.arange(f_total.size, dtype=np.int64)
    y_total = moving_average(f_total, 11)
    y_no = moving_average(f_no, 11)
    y_yes = moving_average(f_yes, 11)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.6, 6.0), sharex=False, gridspec_kw={"height_ratios": [1.0, 1.0]})

    for ax in (ax1, ax2):
        ax.plot(t, y_total, color="#111111", lw=1.8, label="total")
        ax.plot(t, y_no, color="#1976d2", lw=1.4, label="no shortcut used")
        ax.plot(t, y_yes, color="#8e24aa", lw=1.4, label="shortcut used")
        if rep_metrics["t1"] is not None and rep_metrics["t2"] is not None:
            ax.axvline(int(rep_metrics["t1"]), color="#444444", lw=1.0, ls="--", alpha=0.70)
            ax.axvline(int(rep_metrics["t2"]), color="#444444", lw=1.0, ls="--", alpha=0.70)
        ax.grid(alpha=0.25)

    ax1.set_xlim(0, cfg.t_max_case)
    ax1.set_ylabel(r"$f_{enc}(t)$")
    ax1.set_title("Full timescale")
    ax1.legend(loc="upper right", fontsize=9)

    ax2.set_xlim(cfg.t_ignore, 420)
    ax2.set_xlabel("t")
    ax2.set_ylabel(r"$f_{enc}(t)$")
    ax2.set_title(f"Intermediate/late window (t >= {cfg.t_ignore})")

    fig.suptitle(f"Shortcut channel decomposition (beta={rep_beta:.2f})", y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(FIG_DIR / "encounter_shortcut_decomp.pdf")
    plt.close(fig)


def plot_shortcut_share(
    cfg: RingEncounterConfig,
    inst_share: np.ndarray,
    cum_share: np.ndarray,
    rep_metrics: dict[str, float | int | bool | None],
    rep_beta: float,
    share_summary: dict[str, object],
) -> None:
    t = np.arange(inst_share.size, dtype=np.int64)
    y_inst = moving_average(inst_share, 11)
    y_cum = cum_share

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.6, 6.0), sharex=True, gridspec_kw={"height_ratios": [1.0, 1.0]})
    ax1.plot(t, y_inst, color="#6a1b9a", lw=1.8, label="shortcut-used share (instant, smoothed)")
    ax1.axhline(0.5, color="#444444", lw=1.0, ls="--", alpha=0.80, label="50% share")
    ax1.set_ylabel("instant share")
    ax1.set_ylim(-0.02, 1.02)
    ax1.grid(alpha=0.25)

    switch_t = share_summary.get("t_switch_share50")
    if switch_t is not None:
        ax1.axvline(int(switch_t), color="#2e7d32", lw=1.1, ls=":", alpha=0.85, label="first <=50% switch")

    ax2.plot(t, y_cum, color="#1565c0", lw=1.8, label="shortcut-used share (cumulative)")
    ax2.set_ylabel("cumulative share")
    ax2.set_xlabel("t")
    ax2.set_ylim(-0.02, 1.02)
    ax2.grid(alpha=0.25)
    ax2.set_xlim(0, cfg.t_max_case)

    for ax in (ax1, ax2):
        for key, color, style in (
            ("t1", "#d81b60", "--"),
            ("tv", "#455a64", "--"),
            ("t2", "#1e88e5", "--"),
        ):
            val = rep_metrics.get(key)
            if val is not None:
                ax.axvline(int(val), color=color, lw=1.0, ls=style, alpha=0.70)

    ax1.legend(loc="upper right", fontsize=8)
    ax2.legend(loc="lower right", fontsize=8)
    fig.suptitle(f"Shortcut-used share diagnostics (beta={rep_beta:.2f})", y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(FIG_DIR / "encounter_shortcut_share.pdf")
    plt.close(fig)


def plot_mass_conservation(
    cfg: RingEncounterConfig,
    f_rep: np.ndarray,
    surv_rep: np.ndarray,
    rep_beta: float,
) -> None:
    t = np.arange(f_rep.size, dtype=np.int64)
    cumulative = np.cumsum(np.asarray(f_rep, dtype=np.float64))
    survival = np.asarray(surv_rep, dtype=np.float64)
    residual = np.abs(1.0 - cumulative - survival)

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(6.6, 6.0),
        sharex=True,
        gridspec_kw={"height_ratios": [2.3, 1.0]},
    )

    ax1.plot(t, cumulative, color="#1565c0", lw=1.8, label=r"$\sum_{\tau\leq t} f(\tau)$")
    ax1.plot(t, survival, color="#2e7d32", lw=1.5, label=r"$S(t)$")
    ax1.plot(t, cumulative + survival, color="#6d4c41", lw=1.3, ls="--", label=r"$\sum f + S$")
    ax1.axhline(1.0, color="#444444", lw=1.0, ls=":")
    ax1.set_ylabel("mass components")
    ax1.set_ylim(-0.02, 1.02)
    ax1.grid(alpha=0.25)
    ax1.legend(loc="lower right", fontsize=8)

    ax2.semilogy(t[1:], np.maximum(residual[1:], 1e-16), color="#d81b60", lw=1.6)
    ax2.set_xlabel("t")
    ax2.set_ylabel(r"$|1-\sum f - S|$")
    ax2.grid(alpha=0.25, which="both")
    ax2.set_xlim(0, cfg.t_max_case)

    fig.suptitle(f"Mass-conservation audit for representative case (beta={rep_beta:.2f})", y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(FIG_DIR / "encounter_mass_balance.pdf")
    plt.close(fig)


def plot_encounter_phase(scan_rows: list[dict[str, object]]) -> None:
    beta = np.array([float(r["beta"]) for r in scan_rows], dtype=np.float64)
    phase = np.array([int(r["phase"]) for r in scan_rows], dtype=np.int64)
    peak_ratio = np.array([float(r["peak_ratio"]) for r in scan_rows], dtype=np.float64)
    valley_ratio = np.array([float(r["valley_ratio"]) for r in scan_rows], dtype=np.float64)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.4, 5.8), sharex=True, gridspec_kw={"height_ratios": [3.0, 1.0]})

    ax1.plot(beta, peak_ratio, "o-", color="#d81b60", lw=1.6, label="peak balance ratio (min/max)")
    ax1.plot(beta, valley_ratio, "s-", color="#1e88e5", lw=1.4, label="valley ratio")
    ax1.axhline(0.20, color="#d81b60", lw=1.0, ls="--", alpha=0.7)
    ax1.axhline(0.90, color="#1e88e5", lw=1.0, ls="--", alpha=0.7)
    ax1.set_ylabel("metric")
    ax1.set_title("Bimodality metrics vs shortcut strength")
    ax1.grid(alpha=0.25)
    ax1.legend(loc="upper right", fontsize=9)

    cmap = {0: "#cfd8dc", 1: "#90caf9", 2: "#ef9a9a"}
    colors = [cmap[int(v)] for v in phase]
    ax2.bar(beta, np.ones_like(beta), width=0.015, color=colors, edgecolor="#444444", linewidth=0.6)
    ax2.set_yticks([])
    ax2.set_xlabel(r"shortcut strength $\beta$")
    ax2.set_xlim(float(beta.min()) - 0.01, float(beta.max()) + 0.01)
    ax2.set_title("phase: 0 single, 1 weak double, 2 clear double", fontsize=9)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_beta_phase.pdf")
    plt.close(fig)


def plot_peakcount_vs_beta(timescale_rows: list[dict[str, object]]) -> None:
    if not timescale_rows:
        return
    beta = np.array([float(r["beta"]) for r in timescale_rows], dtype=np.float64)
    n_peaks = np.array([int(r.get("n_peaks", 0)) for r in timescale_rows], dtype=np.int64)
    phase = np.array([int(r["phase"]) for r in timescale_rows], dtype=np.int64)

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(beta, n_peaks, "o-", color="#6a1b9a", lw=1.6, label="peak count in detector window")
    ax.scatter(beta[phase == 2], n_peaks[phase == 2], c="#d81b60", s=28, marker="s", label="clear-bimodal")
    ax.set_xlabel(r"shortcut strength $\beta$")
    ax.set_ylabel("count of prominent peaks")
    ax.set_title("Prominent-peak count vs shortcut strength")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_peakcount_vs_beta.pdf")
    plt.close(fig)


def plot_t2_old_vs_new(
    legacy_rows: list[dict[str, object]],
    timescale_rows: list[dict[str, object]],
) -> None:
    if not legacy_rows or not timescale_rows:
        return
    t2_timescale = {beta_token(float(r["beta"])): r.get("t2") for r in timescale_rows}
    beta: list[float] = []
    t2_legacy: list[float] = []
    t2_time: list[float] = []
    for r in legacy_rows:
        key = beta_token(float(r["beta"]))
        t2_new = t2_timescale.get(key)
        if r.get("t2") is None or t2_new is None:
            continue
        beta.append(float(r["beta"]))
        t2_legacy.append(float(r["t2"]))
        t2_time.append(float(t2_new))

    if not beta:
        return
    beta_arr = np.array(beta, dtype=np.float64)
    legacy_arr = np.array(t2_legacy, dtype=np.float64)
    time_arr = np.array(t2_time, dtype=np.float64)

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(beta_arr, legacy_arr, "o-", color="#1e88e5", lw=1.4, label=r"legacy detector $t_2$")
    ax.plot(beta_arr, time_arr, "s-", color="#d81b60", lw=1.5, label=r"timescale detector $t_2$")
    ax.set_xlabel(r"shortcut strength $\beta$")
    ax.set_ylabel(r"selected $t_2$")
    ax.set_title(r"$t_2$ selection comparison across detectors")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_t2_old_vs_new.pdf")
    plt.close(fig)


def plot_onset_scaling(n_scan_rows: list[dict[str, object]]) -> dict[str, float | None]:
    pairs = [
        (float(r["N"]), float(r["onset_beta"]))
        for r in n_scan_rows
        if r.get("onset_beta") is not None and float(r["onset_beta"]) > 0.0
    ]
    if len(pairs) < 2:
        return {"slope": None, "intercept": None, "r2": None}

    N_vals = np.array([p[0] for p in pairs], dtype=np.float64)
    b_vals = np.array([p[1] for p in pairs], dtype=np.float64)
    y = np.log(b_vals)
    slope, intercept = np.polyfit(N_vals, y, 1)
    y_hat = slope * N_vals + intercept
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - float(np.mean(y))) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0.0 else 1.0

    N_line = np.linspace(float(np.min(N_vals)), float(np.max(N_vals)), 200)
    b_fit = np.exp(slope * N_line + intercept)

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(N_vals, b_vals, "o", color="#d81b60", label="observed onset")
    ax.plot(N_line, b_fit, "-", color="#1e88e5", lw=1.5, label=r"log-linear fit: $\log\beta=aN+b$")
    ax.set_xlabel("ring size N")
    ax.set_ylabel(r"onset $\beta$")
    ax.set_title("Onset scaling across ring size")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8)
    ax.text(
        0.03,
        0.05,
        f"slope={slope:.4f}, R$^2$={r2:.3f}",
        transform=ax.transAxes,
        fontsize=8,
        bbox={"boxstyle": "round,pad=0.20", "facecolor": "#ffffff", "alpha": 0.85, "edgecolor": "#cccccc"},
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_onset_scaling.pdf")
    plt.close(fig)

    return {"slope": float(slope), "intercept": float(intercept), "r2": float(r2)}


def plot_onset_sensitivity(sensitivity_rows: list[dict[str, object]], nominal_onset: float | None) -> None:
    values = np.array(
        [float(r["onset_beta"]) for r in sensitivity_rows if r["onset_beta"] is not None],
        dtype=np.float64,
    )
    if values.size == 0:
        return

    unique_vals, counts = np.unique(np.round(values, 3), return_counts=True)

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.bar(unique_vals, counts, width=0.004, color="#90caf9", edgecolor="#1e88e5")
    if nominal_onset is not None:
        ax.axvline(float(nominal_onset), color="#d81b60", lw=1.8, ls="--", label="nominal onset")

    ax.set_xlabel(r"first clear-bimodal $\beta$")
    ax.set_ylabel("count across detector settings")
    ax.set_title("Onset robustness under detector variations")
    ax.grid(alpha=0.25, axis="y")
    if nominal_onset is not None:
        ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_onset_sensitivity.pdf")
    plt.close(fig)


def plot_onset_agreement(
    refine_betas: np.ndarray,
    agreement_fraction: np.ndarray,
    *,
    nominal_onset: float | None,
    onset_50: float | None,
    onset_75: float | None,
) -> None:
    if refine_betas.size == 0 or agreement_fraction.size == 0:
        return

    fig, ax = plt.subplots(figsize=(6.6, 4.3))
    ax.plot(refine_betas, agreement_fraction, "o-", color="#1565c0", lw=1.7, ms=4.0, label="clear-bimodal agreement")
    ax.fill_between(refine_betas, 0.0, agreement_fraction, color="#90caf9", alpha=0.35)
    ax.axhline(0.50, color="#2e7d32", lw=1.0, ls="--", alpha=0.75, label="50% agreement")
    ax.axhline(0.75, color="#6d4c41", lw=1.0, ls=":", alpha=0.75, label="75% agreement")

    if nominal_onset is not None:
        ax.axvline(float(nominal_onset), color="#d81b60", lw=1.4, ls="--", label="nominal onset")
    if onset_50 is not None:
        ax.axvline(float(onset_50), color="#2e7d32", lw=1.2, ls="--", alpha=0.85, label="beta@50%")
    if onset_75 is not None:
        ax.axvline(float(onset_75), color="#6d4c41", lw=1.2, ls=":", alpha=0.90, label="beta@75%")

    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel(r"shortcut strength $\beta$")
    ax.set_ylabel("fraction of detector settings")
    ax.set_title("Detector-agreement curve for clear bimodality")
    ax.grid(alpha=0.25)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_onset_agreement.pdf")
    plt.close(fig)


def plot_onset_refine(
    refine_rows: list[dict[str, object]],
    *,
    coarse_onset: float | None,
    nominal_onset: float | None,
) -> None:
    if not refine_rows:
        return

    beta = np.array([float(r["beta"]) for r in refine_rows], dtype=np.float64)
    phase = np.array([int(r["phase"]) for r in refine_rows], dtype=np.int64)
    peak_ratio = np.array([float(r["peak_ratio"]) for r in refine_rows], dtype=np.float64)
    valley_ratio = np.array([float(r["valley_ratio"]) for r in refine_rows], dtype=np.float64)
    is_bimodal = np.array([int(bool(r["is_bimodal"])) for r in refine_rows], dtype=np.int64)

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(6.6, 5.9),
        sharex=True,
        gridspec_kw={"height_ratios": [3.0, 1.3]},
    )

    ax1.plot(beta, peak_ratio, "o-", color="#d81b60", lw=1.5, label="peak balance ratio (min/max)")
    ax1.plot(beta, valley_ratio, "s-", color="#1e88e5", lw=1.4, label="valley ratio")
    ax1.axhline(0.20, color="#d81b60", lw=1.0, ls="--", alpha=0.70)
    ax1.axhline(0.90, color="#1e88e5", lw=1.0, ls="--", alpha=0.70)
    if coarse_onset is not None:
        ax1.axvline(float(coarse_onset), color="#6d4c41", lw=1.2, ls=":", label="coarse onset")
    if nominal_onset is not None:
        ax1.axvline(float(nominal_onset), color="#2e7d32", lw=1.4, ls="--", label="refined onset")
    ax1.set_ylabel("metric")
    ax1.set_title("Dense onset refinement around bimodality transition")
    ax1.grid(alpha=0.25)
    ax1.legend(loc="upper right", fontsize=8)

    phase_cmap = {0: "#cfd8dc", 1: "#90caf9", 2: "#ef9a9a"}
    phase_colors = [phase_cmap[int(v)] for v in phase]
    ax2.scatter(beta, phase, c=phase_colors, s=28, edgecolors="#333333", linewidths=0.5)
    ax2.plot(beta, phase, color="#444444", lw=0.9, alpha=0.65)
    ax2.scatter(beta[is_bimodal == 1], phase[is_bimodal == 1], c="#b71c1c", s=14, marker="x", label="clear-bimodal")
    ax2.set_ylim(-0.2, 2.2)
    ax2.set_yticks([0, 1, 2])
    ax2.set_ylabel("phase")
    ax2.set_xlabel(r"shortcut strength $\beta$")
    ax2.grid(alpha=0.25)
    ax2.legend(loc="lower right", fontsize=8)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_onset_refine.pdf")
    plt.close(fig)


def plot_fixedsite_examples(cfg: FixedSiteDriftConfig, coarse_series: dict[str, np.ndarray]) -> None:
    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(6.8, 6.0),
        sharex=False,
        gridspec_kw={"height_ratios": [1.0, 1.0]},
    )
    colors = {
        "C0": "#333333",
        "C1": "#e53935",
        "C2": "#1e88e5",
        "C3": "#8e24aa",
    }

    for name, y in coarse_series.items():
        t = 2 * np.arange(y.size, dtype=np.int64)
        c = colors.get(name, "#777777")
        ax1.plot(t, y, lw=1.7, color=c, label=name)
        ax2.plot(t, y, lw=1.7, color=c, label=name)

    ax1.set_xlim(0, cfg.t_max)
    ax1.set_ylabel(r"$\tilde f_\delta(m)$")
    ax1.set_title("Fixed-site encounter examples (K=2 parity coarse-grained)")
    ax1.grid(alpha=0.25)
    ax1.legend(loc="upper right", fontsize=8)

    ax2.set_xlim(20, 260)
    ax2.set_xlabel("t")
    ax2.set_ylabel(r"$\tilde f_\delta(m)$")
    ax2.set_title("Early/intermediate window")
    ax2.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_fixedsite_examples.pdf")
    plt.close(fig)


def plot_fixedsite_parity_compare(
    *,
    raw: np.ndarray,
    coarse: np.ndarray,
    label: str,
    t_zoom_max: int = 320,
) -> None:
    """Show why K=2 parity coarse-graining is used for fixed-site diagnostics."""
    t_raw = np.arange(raw.size, dtype=np.int64)
    t_coarse = 2 * np.arange(coarse.size, dtype=np.int64)

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(6.8, 5.8),
        sharex=False,
        gridspec_kw={"height_ratios": [1.1, 1.0]},
    )
    ax1.plot(t_raw, raw, color="#455a64", lw=1.2)
    ax1.set_xlim(0, min(int(t_zoom_max), int(t_raw[-1]) if t_raw.size else int(t_zoom_max)))
    ax1.set_ylabel(r"$f_\delta(t)$")
    ax1.set_title(f"Fixed-site raw K=2 trace ({label})")
    ax1.grid(alpha=0.25)

    ax2.plot(t_coarse, coarse, color="#d81b60", lw=1.5)
    ax2.set_xlim(0, min(int(t_zoom_max), int(t_raw[-1]) if t_raw.size else int(t_zoom_max)))
    ax2.set_xlabel("t")
    ax2.set_ylabel(r"$\tilde f_\delta(m)$")
    ax2.set_title("After parity coarse-graining: odd/even oscillations suppressed")
    ax2.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_fixedsite_parity_compare.pdf")
    plt.close(fig)


def plot_fixedsite_phase_map(cfg: FixedSiteDriftConfig, phase_map: np.ndarray) -> None:
    gvals = np.array(cfg.g_grid, dtype=np.float64)
    extent = [float(gvals.min()), float(gvals.max()), float(gvals.min()), float(gvals.max())]
    cmap = matplotlib.colors.ListedColormap(["#cfd8dc", "#90caf9", "#ef9a9a"])
    bounds = [-0.5, 0.5, 1.5, 2.5]
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots(figsize=(6.0, 5.2))
    im = ax.imshow(
        phase_map,
        origin="lower",
        extent=extent,
        cmap=cmap,
        norm=norm,
        aspect="auto",
    )
    ax.set_xlabel(r"walker A drift $g_1$")
    ax.set_ylabel(r"walker B drift $g_2$")
    ax.set_title("Fixed-site encounter phase map (0 single, 1 weak, 2 clear)")
    ax.set_xticks(gvals)
    ax.set_yticks(gvals)
    ax.grid(color="white", alpha=0.30, linewidth=0.6)
    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1, 2])
    cbar.ax.set_yticklabels(["single", "weak", "clear"])
    fig.tight_layout()
    fig.savefig(FIG_DIR / "encounter_fixedsite_gphase.pdf")
    plt.close(fig)


def run_fixedsite_drift_study() -> dict[str, object]:
    cfg = FixedSiteDriftConfig()
    smooth_window_pair = 9
    t_ignore_pair = 18
    min_sep_pair = 8
    min_ratio_pair = 0.10
    max_valley_ratio_pair = 0.90
    cases = [
        ("C0", 0.0, 0.0),
        ("C1", 0.9, 0.9),
        ("C2", 0.7, 0.7),
        ("C3", 0.9, -0.9),
    ]

    coarse_series: dict[str, np.ndarray] = {}
    raw_series: dict[str, np.ndarray] = {}
    case_rows: list[dict[str, object]] = []
    gvals = np.array(cfg.g_grid, dtype=np.float64)
    transition_cache: dict[float, np.ndarray] = {
        float(g): build_ring_transition(cfg.N, cfg.q, float(g), shortcut_src=0, shortcut_dst=0, beta=0.0)
        for g in gvals
    }

    def get_transition(g: float) -> np.ndarray:
        key = float(g)
        cached = transition_cache.get(key)
        if cached is not None:
            return cached
        built = build_ring_transition(cfg.N, cfg.q, key, shortcut_src=0, shortcut_dst=0, beta=0.0)
        transition_cache[key] = built
        return built

    for name, g1, g2 in cases:
        P1 = get_transition(float(g1))
        P2 = get_transition(float(g2))
        f, surv = first_encounter_fixed_site(P1, P2, cfg.n0, cfg.m0, cfg.delta, cfg.t_max)
        raw_series[name] = f
        coarse = parity_coarse_grain_k2(f)
        coarse_series[name] = coarse
        metrics = detect_two_peak_metrics_k2_coarse(
            f,
            smooth_window=smooth_window_pair,
            t_ignore_pair=t_ignore_pair,
            min_sep_pair=min_sep_pair,
            min_ratio=min_ratio_pair,
            max_valley_ratio=max_valley_ratio_pair,
            peak_prominence_rel=PEAK_PROMINENCE_REL,
            tie_tol=TIMESCALE_TIE_TOL,
        )
        case_rows.append(
            {
                "name": name,
                "g1": float(g1),
                "g2": float(g2),
                "phase": int(phase_from_metrics(metrics)),
                "t1": metrics["t1"],
                "t2": metrics["t2"],
                "tv": metrics["tv"],
                "peak_ratio": float(metrics["peak_ratio"]),
                "valley_ratio": float(metrics["valley_ratio"]),
                "mass_tmax": float(np.sum(f)),
                "survival_tmax": float(surv[-1]),
            }
        )

    phase_map = np.zeros((gvals.size, gvals.size), dtype=np.int64)
    scan_rows: list[dict[str, object]] = []

    for iy, g2 in enumerate(gvals):
        for ix, g1 in enumerate(gvals):
            P1 = get_transition(float(g1))
            P2 = get_transition(float(g2))
            f, surv = first_encounter_fixed_site(P1, P2, cfg.n0, cfg.m0, cfg.delta, cfg.t_max)
            metrics = detect_two_peak_metrics_k2_coarse(
                f,
                smooth_window=smooth_window_pair,
                t_ignore_pair=t_ignore_pair,
                min_sep_pair=min_sep_pair,
                min_ratio=min_ratio_pair,
                max_valley_ratio=max_valley_ratio_pair,
                peak_prominence_rel=PEAK_PROMINENCE_REL,
                tie_tol=TIMESCALE_TIE_TOL,
            )
            phase = int(phase_from_metrics(metrics))
            phase_map[iy, ix] = phase
            scan_rows.append(
                {
                    "g1": float(g1),
                    "g2": float(g2),
                    "phase": phase,
                    "t1": metrics["t1"],
                    "t2": metrics["t2"],
                    "tv": metrics["tv"],
                    "peak_ratio": float(metrics["peak_ratio"]),
                    "valley_ratio": float(metrics["valley_ratio"]),
                    "mass_tmax": float(np.sum(f)),
                    "survival_tmax": float(surv[-1]),
                }
            )

    phase_counts = {
        0: int(np.sum(phase_map == 0)),
        1: int(np.sum(phase_map == 1)),
        2: int(np.sum(phase_map == 2)),
    }
    total_points = int(phase_map.size)

    with (DATA_DIR / "fixedsite_drift_scan.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "g1",
                "g2",
                "phase",
                "t1",
                "t2",
                "tv",
                "peak_ratio",
                "valley_ratio",
                "mass_tmax",
                "survival_tmax",
            ]
        )
        for row in scan_rows:
            writer.writerow(
                [
                    row["g1"],
                    row["g2"],
                    row["phase"],
                    row["t1"],
                    row["t2"],
                    row["tv"],
                    row["peak_ratio"],
                    row["valley_ratio"],
                    row["mass_tmax"],
                    row["survival_tmax"],
                ]
            )

    write_fixed_cases_table(case_rows)
    write_fixedsite_phase_summary_table(phase_counts, total_points)
    write_fixedsite_parity_note_snippets(phase_counts, total_points)
    plot_fixedsite_examples(cfg, coarse_series)
    if "C1" in raw_series and "C1" in coarse_series:
        plot_fixedsite_parity_compare(raw=raw_series["C1"], coarse=coarse_series["C1"], label="C1: (g1,g2)=(0.9,0.9)")
    plot_fixedsite_phase_map(cfg, phase_map)

    payload = {
        "config": {
            "N": cfg.N,
            "q": cfg.q,
            "n0": cfg.n0,
            "m0": cfg.m0,
            "delta": cfg.delta,
            "t_max": cfg.t_max,
            "g_grid": list(cfg.g_grid),
            "detector": build_fixedsite_timescale_detector_config(
                smooth_window_pair=smooth_window_pair,
                t_ignore_pair=t_ignore_pair,
                min_sep_pair=min_sep_pair,
                min_ratio_pair=min_ratio_pair,
                max_valley_ratio_pair=max_valley_ratio_pair,
            ),
        },
        "examples": case_rows,
        "phase_summary": {
            "total_points": total_points,
            "count_single": phase_counts[0],
            "count_weak": phase_counts[1],
            "count_clear": phase_counts[2],
            "frac_single": 0.0 if total_points <= 0 else float(phase_counts[0]) / float(total_points),
            "frac_weak": 0.0 if total_points <= 0 else float(phase_counts[1]) / float(total_points),
            "frac_clear": 0.0 if total_points <= 0 else float(phase_counts[2]) / float(total_points),
        },
        "scan": scan_rows,
    }
    (DATA_DIR / "fixedsite_summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def run_ring_encounter() -> dict[str, object]:
    cfg = RingEncounterConfig()
    smooth_window_main = 11
    min_ratio_main = 0.20
    max_valley_ratio_main = 0.90
    detector_cfg_main = build_anywhere_timescale_detector_config(
        cfg,
        smooth_window=smooth_window_main,
        min_ratio=min_ratio_main,
        max_valley_ratio=max_valley_ratio_main,
    )
    betas = np.linspace(cfg.beta_scan_min, cfg.beta_scan_max, cfg.beta_scan_points)

    scan_rows: list[dict[str, object]] = []
    scan_rows_legacy: list[dict[str, object]] = []
    # Cache by beta and keep the longest computed horizon for reuse via slicing.
    encounter_cache: dict[str, tuple[np.ndarray, np.ndarray, int]] = {}
    p1_cache: dict[str, np.ndarray] = {}
    rep_beta = 0.20
    overlay_betas = [0.00, 0.12, rep_beta, 0.28]

    P2 = build_ring_transition(
        cfg.N,
        cfg.q,
        cfg.g2,
        shortcut_src=cfg.shortcut_src,
        shortcut_dst=cfg.shortcut_dst,
        beta=0.0,
    )

    def get_encounter_series(beta: float, t_max: int) -> tuple[np.ndarray, np.ndarray]:
        beta_f = float(beta)
        t_need = int(t_max)
        key = beta_token(beta_f)
        cached = encounter_cache.get(key)
        if cached is not None:
            f_cached, surv_cached, t_cached = cached
            if t_cached >= t_need:
                return f_cached[: t_need + 1], surv_cached[: t_need + 1]

        P1 = p1_cache.get(key)
        if P1 is None:
            P1 = build_ring_transition(
                cfg.N,
                cfg.q,
                cfg.g1,
                shortcut_src=cfg.shortcut_src,
                shortcut_dst=cfg.shortcut_dst,
                beta=beta_f,
            )
            p1_cache[key] = P1
        f, surv = first_encounter_any(P1, P2, cfg.n0, cfg.m0, t_need)
        encounter_cache[key] = (f, surv, t_need)
        return f, surv

    def eval_beta_grid(
        beta_values: Iterable[float],
        *,
        smooth_window: int = 11,
        t_ignore: int = cfg.t_ignore,
        t_end: int | None = None,
        min_ratio: float = 0.20,
        max_valley_ratio: float = 0.90,
        detector_mode: str = "legacy",
    ) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for beta in beta_values:
            beta_f = float(beta)
            f, surv = get_encounter_series(beta_f, cfg.t_max_scan)
            if detector_mode == "timescale":
                metrics = detect_two_peak_metrics_timescale(
                    f,
                    smooth_window=int(smooth_window),
                    t_ignore=int(t_ignore),
                    t_end=int(cfg.peak_window_end if t_end is None else t_end),
                    min_ratio=float(min_ratio),
                    max_valley_ratio=float(max_valley_ratio),
                    peak_prominence_rel=PEAK_PROMINENCE_REL,
                    tie_tol=TIMESCALE_TIE_TOL,
                )
            else:
                metrics = detect_two_peak_metrics(
                    f,
                    smooth_window=int(smooth_window),
                    t_ignore=int(t_ignore),
                    min_ratio=float(min_ratio),
                    max_valley_ratio=float(max_valley_ratio),
                )
            rows.append(
                {
                    "beta": beta_f,
                    "detector_mode": str(detector_mode),
                    "phase": int(phase_from_metrics(metrics)),
                    "t1": metrics["t1"],
                    "t2": metrics["t2"],
                    "tv": metrics["tv"],
                    "peak_ratio": float(metrics["peak_ratio"]),
                    "peak_ratio_dir": float(metrics.get("peak_ratio_dir", 0.0)),
                    "valley_ratio": float(metrics["valley_ratio"]),
                    "n_peaks": int(metrics.get("n_peaks", 0)),
                    "mass_tmax": float(np.sum(f)),
                    "survival_tmax": float(surv[-1]),
                    "is_bimodal": bool(metrics["is_bimodal"]),
                    "has_two": bool(metrics["has_two"]),
                }
            )
        return rows

    # Prefetch figure-critical betas at full horizon to avoid recomputation later.
    for beta in sorted(set(overlay_betas)):
        get_encounter_series(float(beta), cfg.t_max_case)

    # Use timescale detector as the canonical multi-peak selector.
    scan_rows_timescale = eval_beta_grid(
        betas.tolist(),
        detector_mode="timescale",
        t_end=cfg.peak_window_end,
        smooth_window=smooth_window_main,
        min_ratio=min_ratio_main,
        max_valley_ratio=max_valley_ratio_main,
    )
    scan_rows = scan_rows_timescale
    scan_rows_legacy = eval_beta_grid(betas.tolist(), detector_mode="legacy")
    coarse_onset = first_bimodal_beta(scan_rows)

    refine_min, refine_max, refine_betas = build_refine_beta_grid(cfg, coarse_onset)

    refine_rows = eval_beta_grid(
        refine_betas.tolist(),
        detector_mode="timescale",
        t_end=cfg.peak_window_end,
        smooth_window=smooth_window_main,
        min_ratio=min_ratio_main,
        max_valley_ratio=max_valley_ratio_main,
    )
    refined_onset = first_bimodal_beta(refine_rows)

    smooth_grid = [9, 11, 13]
    t_ignore_grid = [60, 80, 100]
    min_ratio_grid = [0.18, 0.20, 0.22]
    valley_cap_grid = [0.85, 0.90, 0.95]
    sensitivity_rows: list[dict[str, object]] = []
    agreement_counts = np.zeros(refine_betas.size, dtype=np.int64)
    agreement_total = 0

    for smooth_window in smooth_grid:
        for t_ignore in t_ignore_grid:
            for min_ratio in min_ratio_grid:
                for valley_cap in valley_cap_grid:
                    setting_hits = np.zeros(refine_betas.size, dtype=np.int64)
                    onset_beta: float | None = None
                    for i_beta, beta in enumerate(refine_betas):
                        beta_f = float(beta)
                        f, _ = get_encounter_series(beta_f, cfg.t_max_scan)
                        metrics = detect_two_peak_metrics_timescale(
                            f,
                            smooth_window=smooth_window,
                            t_ignore=t_ignore,
                            t_end=cfg.peak_window_end,
                            min_ratio=min_ratio,
                            max_valley_ratio=valley_cap,
                            peak_prominence_rel=PEAK_PROMINENCE_REL,
                            tie_tol=TIMESCALE_TIE_TOL,
                        )
                        is_clear = bool(metrics["is_bimodal"])
                        setting_hits[i_beta] = 1 if is_clear else 0
                        if is_clear and onset_beta is None:
                            onset_beta = beta_f

                    agreement_counts += setting_hits
                    agreement_total += 1
                    sensitivity_rows.append(
                        {
                            "smooth_window": int(smooth_window),
                            "t_ignore": int(t_ignore),
                            "min_ratio": float(min_ratio),
                            "max_valley_ratio": float(valley_cap),
                            "onset_beta": onset_beta,
                        }
                    )

    if agreement_total > 0:
        agreement_fraction = agreement_counts.astype(np.float64) / float(agreement_total)
    else:
        agreement_fraction = np.zeros_like(refine_betas, dtype=np.float64)
    onset_25 = first_beta_at_fraction(refine_betas, agreement_fraction, 0.25)
    onset_50 = first_beta_at_fraction(refine_betas, agreement_fraction, 0.50)
    onset_75 = first_beta_at_fraction(refine_betas, agreement_fraction, 0.75)
    agreement_width_25_75 = (
        None
        if onset_75 is None or onset_25 is None
        else float(onset_75) - float(onset_25)
    )
    agreement_width_50_75 = (
        None
        if onset_75 is None or onset_50 is None
        else float(onset_75) - float(onset_50)
    )

    onset_values = np.array(
        [float(r["onset_beta"]) for r in sensitivity_rows if r["onset_beta"] is not None],
        dtype=np.float64,
    )
    if onset_values.size > 0:
        sensitivity_summary: dict[str, object] = {
            "count_valid": int(onset_values.size),
            "count_total": int(len(sensitivity_rows)),
            "beta_min": float(np.min(onset_values)),
            "beta_p10": float(np.quantile(onset_values, 0.10)),
            "beta_median": float(np.median(onset_values)),
            "beta_p90": float(np.quantile(onset_values, 0.90)),
            "beta_max": float(np.max(onset_values)),
            "nominal_refined": refined_onset,
            "beta_agreement_25": onset_25,
            "beta_agreement_50": onset_50,
            "beta_agreement_75": onset_75,
            "beta_agreement_width_25_75": agreement_width_25_75,
            "beta_agreement_width_50_75": agreement_width_50_75,
        }
    else:
        sensitivity_summary = {
            "count_valid": 0,
            "count_total": int(len(sensitivity_rows)),
            "beta_min": None,
            "beta_p10": None,
            "beta_median": None,
            "beta_p90": None,
            "beta_max": None,
            "nominal_refined": refined_onset,
            "beta_agreement_25": onset_25,
            "beta_agreement_50": onset_50,
            "beta_agreement_75": onset_75,
            "beta_agreement_width_25_75": agreement_width_25_75,
            "beta_agreement_width_50_75": agreement_width_50_75,
        }

    P_with, P_noedge, P_edge_only, shift = build_shortcut_split(
        cfg.N,
        cfg.q,
        cfg.g1,
        shortcut_src=cfg.shortcut_src,
        shortcut_dst=cfg.shortcut_dst,
        beta=rep_beta,
    )
    f_rep, surv_rep = get_encounter_series(rep_beta, cfg.t_max_case)
    mass_rep = float(np.sum(f_rep))
    survival_rep = float(surv_rep[-1])
    f_total, f_no, f_yes = first_encounter_shortcut_decomp(
        P_with,
        P_noedge,
        P_edge_only,
        P2,
        cfg.n0,
        cfg.m0,
        cfg.t_max_case,
    )
    rep_metrics = detect_two_peak_metrics_timescale(
        f_rep,
        smooth_window=smooth_window_main,
        t_ignore=cfg.t_ignore,
        t_end=cfg.peak_window_end,
        min_ratio=min_ratio_main,
        max_valley_ratio=max_valley_ratio_main,
        peak_prominence_rel=PEAK_PROMINENCE_REL,
        tie_tol=TIMESCALE_TIE_TOL,
    )
    rep_metrics_timescale = rep_metrics
    rep_metrics_legacy = detect_two_peak_metrics(f_rep, t_ignore=cfg.t_ignore)
    prominent_peaks = extract_prominent_peak_times(
        f_rep,
        smooth_window=smooth_window_main,
        t_ignore=cfg.t_ignore,
        rel_height=0.01,
    )
    inst_share, cum_share, shortcut_share_summary = compute_shortcut_share_summary(
        f_total,
        f_yes,
        rep_metrics,
    )

    overlay_series: dict[str, list[float]] = {}
    for b in overlay_betas:
        f, _ = get_encounter_series(float(b), cfg.t_max_case)
        overlay_series[f"beta_{b:.2f}"] = f.tolist()

    f_beta0, _ = get_encounter_series(0.0, cfg.t_max_case)
    r0 = (cfg.n0 - cfg.m0) % cfg.N
    f_beta0_rel = first_encounter_relative_chain(cfg.N, cfg.q, cfg.g1, cfg.q, cfg.g2, r0, cfg.t_max_case)
    beta0_rel_maxdiff = float(np.max(np.abs(f_beta0 - f_beta0_rel)))

    with (DATA_DIR / "encounter_beta_scan.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["beta", "phase", "t1", "t2", "tv", "peak_ratio", "valley_ratio", "mass_tmax", "survival_tmax", "is_bimodal"])
        for r in scan_rows:
            writer.writerow(
                [
                    r["beta"],
                    r["phase"],
                    r["t1"],
                    r["t2"],
                    r["tv"],
                    r["peak_ratio"],
                    r["valley_ratio"],
                    r["mass_tmax"],
                    r["survival_tmax"],
                    int(bool(r["is_bimodal"])),
                ]
            )

    with (DATA_DIR / "encounter_beta_scan_timescale.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "beta",
                "phase",
                "t1",
                "t2",
                "tv",
                "n_peaks",
                "peak_ratio",
                "peak_ratio_dir",
                "valley_ratio",
                "is_bimodal",
            ]
        )
        for r in scan_rows_timescale:
            writer.writerow(
                [
                    r["beta"],
                    r["phase"],
                    r["t1"],
                    r["t2"],
                    r["tv"],
                    r["n_peaks"],
                    r["peak_ratio"],
                    r["peak_ratio_dir"],
                    r["valley_ratio"],
                    int(bool(r["is_bimodal"])),
                ]
            )

    compare_rows: list[dict[str, object]] = []
    ts_map = {beta_token(float(r["beta"])): r for r in scan_rows_timescale}
    with (DATA_DIR / "encounter_beta_scan_compare_detectors.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "beta",
                "phase_legacy",
                "phase_timescale",
                "n_peaks_timescale",
                "t1_legacy",
                "t2_legacy",
                "t2_timescale",
                "peak_ratio_legacy",
                "peak_ratio_timescale",
                "valley_ratio_legacy",
                "valley_ratio_timescale",
            ]
        )
        for old in scan_rows_legacy:
            key = beta_token(float(old["beta"]))
            new = ts_map.get(key)
            if new is None:
                continue
            row = {
                "beta": float(old["beta"]),
                "phase_legacy": int(old["phase"]),
                "phase_timescale": int(new["phase"]),
                "n_peaks_timescale": int(new.get("n_peaks", 0)),
                "t1_legacy": old.get("t1"),
                "t2_legacy": old.get("t2"),
                "t2_timescale": new.get("t2"),
                "peak_ratio_legacy": float(old["peak_ratio"]),
                "peak_ratio_timescale": float(new["peak_ratio"]),
                "valley_ratio_legacy": float(old["valley_ratio"]),
                "valley_ratio_timescale": float(new["valley_ratio"]),
            }
            compare_rows.append(row)
            writer.writerow(
                [
                    row["beta"],
                    row["phase_legacy"],
                    row["phase_timescale"],
                    row["n_peaks_timescale"],
                    row["t1_legacy"],
                    row["t2_legacy"],
                    row["t2_timescale"],
                    row["peak_ratio_legacy"],
                    row["peak_ratio_timescale"],
                    row["valley_ratio_legacy"],
                    row["valley_ratio_timescale"],
                ]
            )

    with (DATA_DIR / "encounter_onset_refine.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["beta", "phase", "is_bimodal", "t1", "t2", "peak_ratio", "valley_ratio"])
        for r in refine_rows:
            writer.writerow(
                [
                    r["beta"],
                    r["phase"],
                    int(bool(r["is_bimodal"])),
                    r["t1"],
                    r["t2"],
                    r["peak_ratio"],
                    r["valley_ratio"],
                ]
            )

    with (DATA_DIR / "encounter_onset_sensitivity.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["smooth_window", "t_ignore", "min_ratio", "max_valley_ratio", "onset_beta"])
        for r in sensitivity_rows:
            writer.writerow(
                [
                    r["smooth_window"],
                    r["t_ignore"],
                    r["min_ratio"],
                    r["max_valley_ratio"],
                    r["onset_beta"],
                ]
            )

    with (DATA_DIR / "encounter_onset_agreement.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["beta", "clear_fraction", "clear_count", "detector_count"])
        for i_beta, beta in enumerate(refine_betas):
            writer.writerow(
                [
                    float(beta),
                    float(agreement_fraction[i_beta]),
                    int(agreement_counts[i_beta]),
                    int(agreement_total),
                ]
            )

    n_scan_rows = run_onset_n_scan(cfg)
    n_scan_onsets = np.array(
        [float(r["onset_beta"]) for r in n_scan_rows if r.get("onset_beta") is not None],
        dtype=np.float64,
    )
    n_scan_window_onsets = np.array(
        [float(r["onset_beta_window"]) for r in n_scan_rows if r.get("onset_beta_window") is not None],
        dtype=np.float64,
    )
    n_scan_extended_count = int(sum(1 for r in n_scan_rows if str(r.get("onset_source")) == "extended"))
    n_scan_none_count = int(sum(1 for r in n_scan_rows if str(r.get("onset_source")) == "none"))
    if n_scan_onsets.size > 0:
        n_scan_summary: dict[str, object] = {
            "count_total": int(len(n_scan_rows)),
            "count_with_onset": int(n_scan_onsets.size),
            "onset_min": float(np.min(n_scan_onsets)),
            "onset_median": float(np.median(n_scan_onsets)),
            "onset_max": float(np.max(n_scan_onsets)),
            "count_with_onset_window": int(n_scan_window_onsets.size),
            "count_extended": n_scan_extended_count,
            "count_none": n_scan_none_count,
            "onset_window_min": (
                None if n_scan_window_onsets.size == 0 else float(np.min(n_scan_window_onsets))
            ),
            "onset_window_median": (
                None if n_scan_window_onsets.size == 0 else float(np.median(n_scan_window_onsets))
            ),
            "onset_window_max": (
                None if n_scan_window_onsets.size == 0 else float(np.max(n_scan_window_onsets))
            ),
        }
    else:
        n_scan_summary = {
            "count_total": int(len(n_scan_rows)),
            "count_with_onset": 0,
            "onset_min": None,
            "onset_median": None,
            "onset_max": None,
            "count_with_onset_window": int(n_scan_window_onsets.size),
            "count_extended": n_scan_extended_count,
            "count_none": n_scan_none_count,
            "onset_window_min": (
                None if n_scan_window_onsets.size == 0 else float(np.min(n_scan_window_onsets))
            ),
            "onset_window_median": (
                None if n_scan_window_onsets.size == 0 else float(np.median(n_scan_window_onsets))
            ),
            "onset_window_max": (
                None if n_scan_window_onsets.size == 0 else float(np.max(n_scan_window_onsets))
            ),
        }

    onset_scaling = plot_onset_scaling(n_scan_rows)

    write_auto_narrative_snippets(
        scan_rows=scan_rows,
        rep_beta=rep_beta,
        rep_metrics=rep_metrics,
        coarse_onset=coarse_onset,
        refined_onset=refined_onset,
        refine_min=refine_min,
        refine_max=refine_max,
        refine_step=cfg.beta_refine_step,
        sensitivity_summary=sensitivity_summary,
        mass_tmax=mass_rep,
        survival_tmax=survival_rep,
        n_scan_rows=n_scan_rows,
        n_scan_summary=n_scan_summary,
    )

    write_encounter_scan_table(scan_rows)

    t = np.arange(cfg.t_max_case + 1, dtype=np.int64)
    with (OUT_DIR / "encounter_rep_fpt.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "t",
                "f_total",
                "f_shortcut_no",
                "f_shortcut_yes",
                "survival",
                "shortcut_share_inst",
                "shortcut_share_cum",
            ]
        )
        for i in range(t.size):
            writer.writerow(
                [
                    int(t[i]),
                    f_total[i],
                    f_no[i],
                    f_yes[i],
                    surv_rep[i] if i < surv_rep.size else "",
                    inst_share[i] if i < inst_share.size else "",
                    cum_share[i] if i < cum_share.size else "",
                ]
            )

    case_payload: dict[str, object] = {
        "config": {
            "N": cfg.N,
            "q": cfg.q,
            "g1": cfg.g1,
            "g2": cfg.g2,
            "n0": cfg.n0,
            "m0": cfg.m0,
            "shortcut_src": cfg.shortcut_src,
            "shortcut_dst": cfg.shortcut_dst,
            "t_ignore": cfg.t_ignore,
            "detector": detector_cfg_main,
        },
        "onset": {
            "coarse_beta": coarse_onset,
            "refined_beta": refined_onset,
            "refine_min": float(refine_min),
            "refine_max": float(refine_max),
            "refine_step": float(cfg.beta_refine_step),
            "sensitivity": sensitivity_summary,
            "n_scan_summary": n_scan_summary,
            "n_scan_rows": n_scan_rows,
        },
        "representative": {
            "beta": rep_beta,
            "metrics": rep_metrics,
            "metrics_legacy": rep_metrics_legacy,
            "metrics_timescale": rep_metrics_timescale,
            "shortcut_share": shortcut_share_summary,
            "prominent_peaks": prominent_peaks,
            "shortcut_shift": shift,
            "mass_tmax": mass_rep,
            "survival_tmax": survival_rep,
            "beta0_rel_maxdiff": beta0_rel_maxdiff,
        },
        "scan": scan_rows,
        "scan_legacy": scan_rows_legacy,
        "scan_detector_mode": "timescale",
        "scan_timescale": scan_rows_timescale,
        "detector_compare": compare_rows,
        "onset_scaling": onset_scaling,
    }
    (DATA_DIR / "case_summary.json").write_text(json.dumps(case_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    write_encounter_key_metrics_table(
        coarse_onset=coarse_onset,
        refined_onset=refined_onset,
        sensitivity_summary=sensitivity_summary,
        rep_metrics=rep_metrics,
        shortcut_share_summary=shortcut_share_summary,
        shift=shift,
        mass_tmax=mass_rep,
        survival_tmax=survival_rep,
        beta0_rel_maxdiff=beta0_rel_maxdiff,
        onset_scaling=onset_scaling,
    )
    write_shortcut_rep_case_table(
        cfg=cfg,
        rep_beta=rep_beta,
        rep_metrics=rep_metrics,
        prominent_peaks=prominent_peaks,
    )

    plot_ring_geometry(cfg, rep_beta)
    plot_encounter_overlay(cfg, overlay_series)
    plot_shortcut_representative_case(cfg, f_rep, rep_metrics, prominent_peaks, rep_beta)
    plot_shortcut_decomp(cfg, f_total, f_no, f_yes, rep_metrics, rep_beta)
    plot_shortcut_share(cfg, inst_share, cum_share, rep_metrics, rep_beta, shortcut_share_summary)
    plot_mass_conservation(cfg, f_rep, surv_rep, rep_beta)
    plot_encounter_phase(scan_rows)
    plot_peakcount_vs_beta(scan_rows_timescale)
    plot_t2_old_vs_new(scan_rows_legacy, scan_rows_timescale)
    plot_onset_refine(refine_rows, coarse_onset=coarse_onset, nominal_onset=refined_onset)
    plot_onset_sensitivity(sensitivity_rows, refined_onset)
    plot_onset_agreement(
        refine_betas,
        agreement_fraction,
        nominal_onset=refined_onset,
        onset_50=onset_50,
        onset_75=onset_75,
    )

    return {
        "scan": scan_rows,
        "scan_legacy": scan_rows_legacy,
        "scan_timescale": scan_rows_timescale,
        "representative_beta": rep_beta,
        "representative_metrics": rep_metrics,
        "representative_metrics_timescale": rep_metrics_timescale,
        "onset_beta_coarse": coarse_onset,
        "onset_beta_refined": refined_onset,
        "onset_sensitivity": sensitivity_summary,
        "onset_scaling": onset_scaling,
        "onset_n_scan_summary": n_scan_summary,
        "onset_n_scan_rows": n_scan_rows,
        "beta0_rel_maxdiff": beta0_rel_maxdiff,
    }


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------


def main() -> None:
    ensure_dirs()
    a1a8_payload = run_a1a8_validation()
    encounter_payload = run_ring_encounter()
    fixedsite_payload = run_fixedsite_drift_study()

    summary = {
        "a1a8_cases": len(a1a8_payload["cases"]),
        "encounter_scan_points": len(encounter_payload["scan"]),
        "fixedsite_scan_points": len(fixedsite_payload["scan"]),
        "fixedsite_count_single": fixedsite_payload["phase_summary"]["count_single"],
        "fixedsite_count_weak": fixedsite_payload["phase_summary"]["count_weak"],
        "fixedsite_count_clear": fixedsite_payload["phase_summary"]["count_clear"],
        "fixedsite_frac_single": fixedsite_payload["phase_summary"]["frac_single"],
        "fixedsite_frac_weak": fixedsite_payload["phase_summary"]["frac_weak"],
        "fixedsite_frac_clear": fixedsite_payload["phase_summary"]["frac_clear"],
        "representative_beta": encounter_payload["representative_beta"],
        "onset_beta_coarse": encounter_payload["onset_beta_coarse"],
        "onset_beta_refined": encounter_payload["onset_beta_refined"],
        "onset_beta_median": encounter_payload["onset_sensitivity"]["beta_median"],
        "onset_beta_agreement_25": encounter_payload["onset_sensitivity"]["beta_agreement_25"],
        "onset_beta_agreement_50": encounter_payload["onset_sensitivity"]["beta_agreement_50"],
        "onset_beta_agreement_75": encounter_payload["onset_sensitivity"]["beta_agreement_75"],
        "onset_agreement_width_25_75": encounter_payload["onset_sensitivity"]["beta_agreement_width_25_75"],
        "onset_agreement_width_50_75": encounter_payload["onset_sensitivity"]["beta_agreement_width_50_75"],
        "onset_n_scan_points": encounter_payload["onset_n_scan_summary"]["count_total"],
        "onset_n_scan_valid": encounter_payload["onset_n_scan_summary"]["count_with_onset"],
        "onset_n_scan_valid_window": encounter_payload["onset_n_scan_summary"]["count_with_onset_window"],
        "onset_n_scan_extended": encounter_payload["onset_n_scan_summary"]["count_extended"],
        "onset_n_scan_none": encounter_payload["onset_n_scan_summary"]["count_none"],
        "onset_n_scan_median": encounter_payload["onset_n_scan_summary"]["onset_median"],
        "onset_n_scan_window_median": encounter_payload["onset_n_scan_summary"]["onset_window_median"],
    }
    (OUT_DIR / "run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[ok] built 1D ring encounter assets")
    print(f"  data: {DATA_DIR}")
    print(f"  figures: {FIG_DIR}")
    print(f"  tables: {TABLE_DIR}")


if __name__ == "__main__":
    main()
