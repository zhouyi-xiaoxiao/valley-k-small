#!/usr/bin/env python3
"""Pre-send numerical validation for the corrected Luca calculation packet.

This script checks the claims made in the sendable corrected notes/email:

- the corrected plus/plus first-passage formula agrees with the direct finite
  stochastic shortcut matrix;
- the compact Chebyshev closed form agrees with the same finite-matrix
  resolvent in the N=100, q=2/3, u=6 -> v=56 setup;
- the dominant transient eigenvalue satisfies gamma_1 < s_1 < alpha_1 on a
  representative beta grid, and solves the corrected denominator equation;
- the N=100 double-peak range quoted in the email is reproduced by the same
  finite-time peak classifier used in the local sweep.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np


AUDIT_DIR = Path(__file__).resolve().parents[1]


def t_cheb(n: int, y: float) -> float:
    if n < 0:
        raise ValueError(f"negative T index: {n}")
    if n == 0:
        return 1.0
    if n == 1:
        return y
    a, b = 1.0, y
    for _ in range(2, n + 1):
        a, b = b, 2.0 * y * b - a
    return b


def u_cheb(n: int, y: float) -> float:
    if n == -1:
        return 0.0
    if n < -1:
        raise ValueError(f"negative U index: {n}")
    if n == 0:
        return 1.0
    if n == 1:
        return 2.0 * y
    a, b = 1.0, 2.0 * y
    for _ in range(2, n + 1):
        a, b = b, 2.0 * y * b - a
    return b


def ring_transition(n_sites: int, q: float) -> np.ndarray:
    transition = np.zeros((n_sites, n_sites), dtype=float)
    for i in range(n_sites):
        transition[i, i] += 1.0 - q
        transition[i, (i - 1) % n_sites] += q / 2.0
        transition[i, (i + 1) % n_sites] += q / 2.0
    return transition


def stochastic_shortcut_transition(transition: np.ndarray, u: int, v: int, beta: float, q: float) -> np.ndarray:
    shortcut = transition.copy()
    lam = beta * (1.0 - q)
    shortcut[u, u] -= lam
    shortcut[u, v] += lam
    return shortcut


def resolvent(transition: np.ndarray, z: float) -> np.ndarray:
    return np.linalg.inv(np.eye(transition.shape[0]) - z * transition)


def absorbing_submatrix(transition: np.ndarray, target: int) -> tuple[np.ndarray, dict[int, int]]:
    keep = [i for i in range(transition.shape[0]) if i != target]
    return transition[np.ix_(keep, keep)], {old: new for new, old in enumerate(keep)}


def w_abs_matrix(w_resolvent: np.ndarray, index: dict[int, int], start: int, end: int, target: int) -> float:
    if start == target or end == target:
        return 0.0
    return float(w_resolvent[index[start], index[end]])


def direct_first_passage_ratio(n_sites: int, q: float, beta: float, u: int, v: int, start: int, z: float) -> float:
    base = ring_transition(n_sites, q)
    shortcut = stochastic_shortcut_transition(base, u, v, beta, q)
    s_res = resolvent(shortcut, z)
    return float(s_res[start, v] / s_res[v, v])


def corrected_plus_formula(n_sites: int, q: float, beta: float, u: int, v: int, start: int, z: float) -> float:
    base = ring_transition(n_sites, q)
    p_res = resolvent(base, z)
    absorbing, index = absorbing_submatrix(base, v)
    w_res = resolvent(absorbing, z)
    lam = beta * (1.0 - q)
    f0 = float(p_res[start, v] / p_res[v, v])
    fu = float(p_res[u, v] / p_res[v, v])
    w_nu = w_abs_matrix(w_res, index, start, u, v)
    w_uu = w_abs_matrix(w_res, index, u, u, v)
    return f0 + z * lam * w_nu * (1.0 - fu) / (1.0 + z * lam * w_uu)


def closed_form_antipodal(n_sites: int, q: float, beta: float, rho: int, z: float) -> float:
    half = n_sites // 2
    y = 1.0 + (1.0 / z - 1.0) / q
    a = q / (beta * (1.0 - q))
    numerator = a * t_cheb(half - rho, y) + u_cheb(rho - 1, y) + u_cheb(half - rho - 1, y)
    denominator = a * t_cheb(half, y) + u_cheb(half - 1, y)
    return numerator / denominator


def shifted_rho(n_sites: int, start: int, target: int) -> int:
    rho = (start - target) % n_sites
    if rho > n_sites // 2:
        rho = n_sites - rho
    return int(rho)


def transient_matrix(n_sites: int, q: float, beta: float, u: int, v: int) -> np.ndarray:
    base = ring_transition(n_sites, q)
    shortcut = stochastic_shortcut_transition(base, u, v, beta, q)
    absorbing, _ = absorbing_submatrix(shortcut, v)
    return absorbing


def dominant_s(n_sites: int, q: float, beta: float, u: int, v: int) -> float:
    eigvals = np.linalg.eigvals(transient_matrix(n_sites, q, beta, u, v))
    return float(max(abs(ev) for ev in eigvals))


def denominator_residual(n_sites: int, q: float, beta: float, s_value: float) -> float:
    half = n_sites // 2
    y = (s_value - (1.0 - q)) / q
    a = q / (beta * (1.0 - q))
    return a * t_cheb(half, y) + u_cheb(half - 1, y)


def denominator_normalized_residual(n_sites: int, q: float, beta: float, s_value: float) -> float:
    half = n_sites // 2
    y = (s_value - (1.0 - q)) / q
    a = q / (beta * (1.0 - q))
    term_a = a * t_cheb(half, y)
    term_u = u_cheb(half - 1, y)
    return abs(term_a + term_u) / (abs(term_a) + abs(term_u) + 1.0)


def validate_resolvent_and_closed_form() -> dict[str, float]:
    n_sites = 100
    q = 2.0 / 3.0
    u = 5
    v = 55
    betas = (0.01, 0.03, 0.04, 0.06)
    starts = tuple(range(0, 6))
    z_values = (0.2, 0.5, 0.8, 0.95)

    max_plus = 0.0
    max_closed = 0.0
    rows: list[dict[str, float | int]] = []
    for beta in betas:
        for start in starts:
            rho = shifted_rho(n_sites, start, v)
            for z in z_values:
                direct = direct_first_passage_ratio(n_sites, q, beta, u, v, start, z)
                plus = corrected_plus_formula(n_sites, q, beta, u, v, start, z)
                closed = closed_form_antipodal(n_sites, q, beta, rho, z)
                err_plus = abs(plus - direct)
                err_closed = abs(closed - direct)
                max_plus = max(max_plus, err_plus)
                max_closed = max(max_closed, err_closed)
                rows.append(
                    {
                        "beta": beta,
                        "n0_paper": start + 1,
                        "rho": rho,
                        "z": z,
                        "direct": direct,
                        "corrected_plus": plus,
                        "closed_form": closed,
                        "err_plus": err_plus,
                        "err_closed": err_closed,
                    }
                )
    return {
        "rows": rows,
        "max_err_corrected_plus_vs_direct": max_plus,
        "max_err_closed_form_vs_direct": max_closed,
    }


def validate_poles() -> dict[str, float | list[dict[str, float]]]:
    n_sites = 100
    q = 2.0 / 3.0
    u = 5
    v = 55
    betas = (0.001, 0.005, 0.01, 0.03, 0.04, 0.06, 0.2, 0.5, 1.0)
    gamma1 = 1.0 - q + q * math.cos(2.0 * math.pi / n_sites)
    alpha1 = 1.0 - q + q * math.cos(math.pi / n_sites)
    rows = []
    min_s_minus_gamma = math.inf
    min_alpha_minus_s = math.inf
    max_den_residual = 0.0
    max_den_normalized_residual = 0.0
    for beta in betas:
        s_value = dominant_s(n_sites, q, beta, u, v)
        den_res = abs(denominator_residual(n_sites, q, beta, s_value))
        den_norm = denominator_normalized_residual(n_sites, q, beta, s_value)
        min_s_minus_gamma = min(min_s_minus_gamma, s_value - gamma1)
        min_alpha_minus_s = min(min_alpha_minus_s, alpha1 - s_value)
        max_den_residual = max(max_den_residual, den_res)
        max_den_normalized_residual = max(max_den_normalized_residual, den_norm)
        rows.append(
            {
                "beta": beta,
                "s1": s_value,
                "gamma1": gamma1,
                "alpha1": alpha1,
                "s1_minus_gamma1": s_value - gamma1,
                "alpha1_minus_s1": alpha1 - s_value,
                "denominator_residual": den_res,
                "denominator_normalized_residual": den_norm,
            }
        )
    return {
        "rows": rows,
        "min_s1_minus_gamma1": min_s_minus_gamma,
        "min_alpha1_minus_s1": min_alpha_minus_s,
        "max_denominator_residual": max_den_residual,
        "max_denominator_normalized_residual": max_den_normalized_residual,
    }


def validate_double_peaks() -> dict[str, object]:
    n_sites = 100
    q = 2.0 / 3.0
    beta_c = 2.0 * q / ((1.0 - q) * n_sites)
    betas = default_beta_grid(0.08, 0.002, beta_c)
    metrics = compute_double_peak_metrics(
        n_sites=n_sites,
        q=q,
        n0_values=(1, 2, 3, 4, 5, 6),
        target_paper=56,
        sc_src_paper=6,
        sc_dst_paper=56,
        betas=betas,
    )
    summary = transition_summary(metrics)
    summary_by_n0 = {int(row["n0_paper"]): row for row in summary}
    expected = {
        1: (True, 0.03, 0),
        2: (True, 0.03, 0),
        3: (True, 0.03, 0),
        4: (False, math.nan, 0),
        5: (False, math.nan, 0),
        6: (False, math.nan, 0),
    }
    matches_claim = True
    for n0, (any_expected, max_expected, at_or_above_expected) in expected.items():
        row = summary_by_n0[n0]
        any_actual = bool(row["any_clear_double_peak"])
        max_actual = float(row["max_beta_clear_double_peak"])
        at_or_above_actual = int(row["clear_at_or_above_luca_count"])
        if any_actual != any_expected or at_or_above_actual != at_or_above_expected:
            matches_claim = False
        if math.isnan(max_expected):
            if not math.isnan(max_actual):
                matches_claim = False
        elif abs(max_actual - max_expected) > 1.0e-12:
            matches_claim = False
    return {
        "metrics_rows": metrics,
        "summary": summary,
        "matches_email_claim": matches_claim,
        "beta_c": beta_c,
    }


def default_beta_grid(beta_max: float, step: float, beta_c: float) -> list[float]:
    vals = list(np.arange(0.0, beta_max + 0.5 * step, step, dtype=float))
    vals.extend([0.001, 0.005, 0.01, beta_c, 0.75 * beta_c, 1.25 * beta_c])
    return sorted({round(float(x), 10) for x in vals if 0.0 <= float(x) <= beta_max})


def paper_to0(x_paper: int, n_sites: int) -> int:
    return ((int(x_paper) - 1) % int(n_sites))


def exact_first_absorption_pmf(
    *,
    n_sites: int,
    q: float,
    beta: float,
    n0_paper: int,
    target_paper: int,
    sc_src_paper: int,
    sc_dst_paper: int,
    tmax: int = 12000,
    survival_eps: float = 1.0e-13,
) -> tuple[np.ndarray, float]:
    start = paper_to0(n0_paper, n_sites)
    target = paper_to0(target_paper, n_sites)
    sc_src = paper_to0(sc_src_paper, n_sites)
    sc_dst = paper_to0(sc_dst_paper, n_sites)
    stay = 1.0 - q
    move_each = q / 2.0
    shortcut_p = beta * stay

    dist = np.zeros(n_sites, dtype=float)
    dist[start] = 1.0
    values = np.zeros(tmax, dtype=float)
    steps = 0
    for t in range(tmax):
        nxt = stay * dist
        nxt += move_each * np.roll(dist, 1)
        nxt += move_each * np.roll(dist, -1)

        mass_at_source = float(dist[sc_src])
        if mass_at_source != 0.0 and shortcut_p != 0.0:
            nxt[sc_src] -= mass_at_source * shortcut_p
            nxt[sc_dst] += mass_at_source * shortcut_p

        if float(nxt.min()) < 0.0:
            nxt = np.maximum(nxt, 0.0)

        values[t] = float(nxt[target])
        nxt[target] = 0.0
        dist = nxt
        steps = t + 1
        if float(dist.sum()) < survival_eps:
            break
    return values[:steps].copy(), float(dist.sum())


def strict_local_peaks(f: np.ndarray, *, hmin: float) -> list[tuple[int, float]]:
    out: list[tuple[int, float]] = []
    for idx, value in enumerate(np.asarray(f, dtype=float)):
        left = float(f[idx - 1]) if idx > 0 else 0.0
        right = float(f[idx + 1]) if idx + 1 < len(f) else 0.0
        if float(value) > left and float(value) > right and float(value) >= hmin:
            out.append((idx + 1, float(value)))
    return out


def detect_peaks_paper(f: np.ndarray, *, hmin: float, second_rel_height: float) -> list[tuple[int, float]]:
    peaks = strict_local_peaks(f, hmin=hmin)
    if not peaks:
        return []
    hmax = max(height for _, height in peaks)
    threshold = float(second_rel_height) * hmax
    return [(time, height) for time, height in peaks if height >= threshold]


def first_two_peaks_and_valley(f: np.ndarray, peaks_paper: list[tuple[int, float]]) -> tuple[int | None, int | None, int | None]:
    if not peaks_paper:
        return None, None, None
    t1 = int(peaks_paper[0][0])
    if len(peaks_paper) < 2:
        return t1, None, None
    t2 = int(peaks_paper[1][0])
    if t2 - t1 < 2:
        return t1, None, t2
    segment = np.asarray(f, dtype=float)[t1 : (t2 - 1)]
    if segment.size == 0:
        return t1, None, t2
    return t1, t1 + int(np.argmin(segment)) + 1, t2


def analyze_curve(
    f: np.ndarray,
    *,
    hmin: float = 1.0e-12,
    second_rel_height: float = 0.01,
    min_peak_separation: int = 10,
) -> dict[str, object]:
    peaks = detect_peaks_paper(f, hmin=float(hmin), second_rel_height=float(second_rel_height))
    t1, tv, t2 = first_two_peaks_and_valley(f, peaks)
    h1 = float(f[t1 - 1]) if t1 is not None else math.nan
    h2 = float(f[t2 - 1]) if t2 is not None else math.nan
    hv = float(f[tv - 1]) if tv is not None else math.nan
    peak_sep = (int(t2) - int(t1)) if (t1 is not None and t2 is not None) else math.nan
    hmax = max(h1, h2) if (not math.isnan(h1) and not math.isnan(h2)) else math.nan
    hmin_peak = min(h1, h2) if (not math.isnan(h1) and not math.isnan(h2)) else math.nan
    h2_over_h1 = (h2 / h1) if (not math.isnan(h1) and h1 > 0.0 and not math.isnan(h2)) else math.nan
    valley_ratio = (hv / hmax) if (not math.isnan(hv) and hmax > 0.0) else math.nan
    visual_rho = (hv / hmin_peak) if (not math.isnan(hv) and hmin_peak > 0.0) else math.nan
    paper_double_peak = len(peaks) >= 2
    clear_double_peak = bool(
        paper_double_peak
        and not math.isnan(peak_sep)
        and peak_sep >= int(min_peak_separation)
        and not math.isnan(h2_over_h1)
        and 0.1 <= h2_over_h1 <= 10.0
        and not math.isnan(visual_rho)
        and visual_rho <= 0.8
    )
    return {
        "n_peaks": int(len(peaks)),
        "paper_double_peak": bool(paper_double_peak),
        "clear_double_peak": bool(clear_double_peak),
        "t1": t1,
        "tv": tv,
        "t2": t2,
        "h1": h1,
        "hv": hv,
        "h2": h2,
        "h2_over_h1": h2_over_h1,
        "valley_ratio": valley_ratio,
        "visual_rho": visual_rho,
        "peak_separation": peak_sep,
    }


def compute_double_peak_metrics(
    *,
    n_sites: int,
    q: float,
    n0_values: tuple[int, ...],
    target_paper: int,
    sc_src_paper: int,
    sc_dst_paper: int,
    betas: list[float],
) -> list[dict[str, object]]:
    beta_c = 2.0 * q / ((1.0 - q) * n_sites)
    rows = []
    for n0_paper in n0_values:
        for beta in betas:
            f, survival = exact_first_absorption_pmf(
                n_sites=n_sites,
                q=q,
                beta=float(beta),
                n0_paper=int(n0_paper),
                target_paper=target_paper,
                sc_src_paper=sc_src_paper,
                sc_dst_paper=sc_dst_paper,
                tmax=12000,
                survival_eps=1.0e-13,
            )
            metrics = analyze_curve(f)
            rows.append(
                {
                    "N": int(n_sites),
                    "K": 2,
                    "q": float(q),
                    "rho": 1.0,
                    "n0_paper": int(n0_paper),
                    "target_paper": int(target_paper),
                    "sc_src_paper": int(sc_src_paper),
                    "sc_dst_paper": int(sc_dst_paper),
                    "beta": float(beta),
                    "p_shortcut": float(beta) * (1.0 - q),
                    "luca_beta_c": beta_c,
                    "beta_below_luca": float(beta) < beta_c - 1.0e-12,
                    "mass": float(np.sum(f)),
                    "survival_tail": float(survival),
                    "tmax_used": int(f.size),
                    **metrics,
                }
            )
    return rows


def transition_summary(rows_in: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for n0 in sorted({int(r["n0_paper"]) for r in rows_in}):
        group = sorted([r for r in rows_in if int(r["n0_paper"]) == n0], key=lambda r: float(r["beta"]))
        yes = [r for r in group if bool(r["clear_double_peak"])]
        below = [r for r in group if bool(r["beta_below_luca"])]
        above = [r for r in group if not bool(r["beta_below_luca"])]
        first_no_after_yes = math.nan
        if yes:
            max_yes = max(float(r["beta"]) for r in yes)
            later_no = [r for r in group if float(r["beta"]) > max_yes and not bool(r["clear_double_peak"])]
            if later_no:
                first_no_after_yes = float(later_no[0]["beta"])
        rows.append(
            {
                "n0_paper": int(n0),
                "target_paper": int(group[0]["target_paper"]),
                "sc_src_paper": int(group[0]["sc_src_paper"]),
                "sc_dst_paper": int(group[0]["sc_dst_paper"]),
                "luca_beta_c": float(group[0]["luca_beta_c"]),
                "any_clear_double_peak": bool(any(bool(r["clear_double_peak"]) for r in group)),
                "max_beta_clear_double_peak": max(float(r["beta"]) for r in yes) if yes else math.nan,
                "first_beta_no_after_clear": first_no_after_yes,
                "clear_below_luca_count": sum(1 for r in below if bool(r["clear_double_peak"])),
                "clear_at_or_above_luca_count": sum(1 for r in above if bool(r["clear_double_peak"])),
                "grid_points": int(len(group)),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    outdir = AUDIT_DIR / "send_preflight_numeric_validation_20260607"
    outdir.mkdir(parents=True, exist_ok=True)

    resolvent_checks = validate_resolvent_and_closed_form()
    pole_checks = validate_poles()
    peak_checks = validate_double_peaks()

    write_csv(outdir / "resolvent_closed_form_checks.csv", resolvent_checks["rows"])  # type: ignore[arg-type]
    write_csv(outdir / "pole_checks.csv", pole_checks["rows"])  # type: ignore[arg-type]
    write_csv(outdir / "double_peak_metrics.csv", peak_checks["metrics_rows"])  # type: ignore[arg-type]
    write_csv(outdir / "double_peak_summary.csv", peak_checks["summary"])  # type: ignore[arg-type]

    summary = {
        "max_err_corrected_plus_vs_direct": resolvent_checks["max_err_corrected_plus_vs_direct"],
        "max_err_closed_form_vs_direct": resolvent_checks["max_err_closed_form_vs_direct"],
        "min_s1_minus_gamma1": pole_checks["min_s1_minus_gamma1"],
        "min_alpha1_minus_s1": pole_checks["min_alpha1_minus_s1"],
        "max_denominator_residual": pole_checks["max_denominator_residual"],
        "max_denominator_normalized_residual": pole_checks["max_denominator_normalized_residual"],
        "double_peak_matches_email_claim": peak_checks["matches_email_claim"],
        "beta_c": peak_checks["beta_c"],
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# Sendable preflight numerical validation",
        "",
        f"- corrected plus/plus formula vs direct matrix: {summary['max_err_corrected_plus_vs_direct']:.6e}",
        f"- compact closed form vs direct matrix: {summary['max_err_closed_form_vs_direct']:.6e}",
        f"- min(s1-gamma1) over sampled betas: {summary['min_s1_minus_gamma1']:.6e}",
        f"- min(alpha1-s1) over sampled betas: {summary['min_alpha1_minus_s1']:.6e}",
        f"- max denominator residual at spectral s1: {summary['max_denominator_residual']:.6e}",
        f"- max normalized denominator residual at spectral s1: {summary['max_denominator_normalized_residual']:.6e}",
        f"- double-peak summary matches email claim: {summary['double_peak_matches_email_claim']}",
        "",
        "Outputs:",
        "",
        "- resolvent_closed_form_checks.csv",
        "- pole_checks.csv",
        "- double_peak_metrics.csv",
        "- double_peak_summary.csv",
        "- summary.json",
    ]
    (outdir / "README.md").write_text("\n".join(lines), encoding="utf-8")

    checks = [
        summary["max_err_corrected_plus_vs_direct"] < 1.0e-12,
        summary["max_err_closed_form_vs_direct"] < 1.0e-12,
        summary["min_s1_minus_gamma1"] > 0.0,
        summary["min_alpha1_minus_s1"] > 0.0,
        summary["max_denominator_normalized_residual"] < 1.0e-9,
        bool(summary["double_peak_matches_email_claim"]),
    ]
    print(json.dumps(summary, indent=2))
    print(f"outdir={outdir}")
    if not all(checks):
        raise SystemExit("preflight numerical validation failed")


if __name__ == "__main__":
    main()
