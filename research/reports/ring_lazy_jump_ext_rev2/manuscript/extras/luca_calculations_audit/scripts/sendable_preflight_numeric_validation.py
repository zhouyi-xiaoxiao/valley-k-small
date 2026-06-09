#!/usr/bin/env python3
"""Pre-send numerical validation for the corrected calculation packet.

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


def absorbing_propagator_series(
    transition: np.ndarray,
    target: int,
    start: int,
    end: int,
    tmax: int,
) -> np.ndarray:
    values = np.zeros(tmax + 1, dtype=float)
    if start == target or end == target:
        return values
    transient, index = absorbing_submatrix(transition, target)
    vec = np.zeros(transient.shape[0], dtype=float)
    vec[index[start]] = 1.0
    end_idx = index[end]
    for t in range(tmax + 1):
        values[t] = float(vec[end_idx])
        if t < tmax:
            vec = vec @ transient
    return values


def first_passage_pmf_series(
    transition: np.ndarray,
    target: int,
    start: int,
    tmax: int,
) -> np.ndarray:
    values = np.zeros(tmax + 1, dtype=float)
    if start == target:
        values[0] = 1.0
        return values
    transient, index = absorbing_submatrix(transition, target)
    keep = [i for i in range(transition.shape[0]) if i != target]
    hit_column = transition[keep, target]
    vec = np.zeros(transient.shape[0], dtype=float)
    vec[index[start]] = 1.0
    for t in range(1, tmax + 1):
        values[t] = float(vec @ hit_column)
        vec = vec @ transient
    return values


def h_series_from_killed_return(
    *,
    n_sites: int,
    q: float,
    beta: float,
    u: int,
    v: int,
    tmax: int,
) -> np.ndarray:
    base = ring_transition(n_sites, q)
    wuu = absorbing_propagator_series(base, v, u, u, tmax)
    lam = beta * (1.0 - q)
    h = np.zeros(tmax + 1, dtype=float)
    h[0] = beta * (1.0 - q) / q
    for n in range(1, tmax + 1):
        h[n] = -lam * sum(float(wuu[j]) * float(h[n - 1 - j]) for j in range(n))
    return h


def hard_route_convolution_pmf(
    *,
    n_sites: int,
    q: float,
    beta: float,
    start: int,
    u: int,
    v: int,
    tmax: int,
) -> np.ndarray:
    base = ring_transition(n_sites, q)
    f0_start = first_passage_pmf_series(base, v, start, tmax)
    f0_u = first_passage_pmf_series(base, v, u, tmax)
    w_start_u = absorbing_propagator_series(base, v, start, u, tmax)
    h = h_series_from_killed_return(n_sites=n_sites, q=q, beta=beta, u=u, v=v, tmax=tmax)

    out = np.zeros(tmax + 1, dtype=float)
    for t in range(1, tmax + 1):
        total = float(f0_start[t])
        for tp in range(t):
            inner = float(h[tp])
            for tt in range(tp + 1):
                inner -= float(f0_u[tp - tt]) * float(h[tt])
            total += q * float(w_start_u[t - 1 - tp]) * inner
        out[t] = total
    return out


def hard_route_convolution_components(
    *,
    n_sites: int,
    q: float,
    beta: float,
    start: int,
    u: int,
    v: int,
    tmax: int,
) -> dict[str, np.ndarray]:
    base = ring_transition(n_sites, q)
    f0_start = first_passage_pmf_series(base, v, start, tmax)
    f0_u = first_passage_pmf_series(base, v, u, tmax)
    w_start_u = absorbing_propagator_series(base, v, start, u, tmax)
    h = h_series_from_killed_return(n_sites=n_sites, q=q, beta=beta, u=u, v=v, tmax=tmax)
    h0 = float(h[0])

    baseline = np.zeros(tmax + 1, dtype=float)
    delta_h0 = np.zeros(tmax + 1, dtype=float)
    delta_hplus = np.zeros(tmax + 1, dtype=float)
    fu_h0 = np.zeros(tmax + 1, dtype=float)
    fu_hplus = np.zeros(tmax + 1, dtype=float)

    for t in range(1, tmax + 1):
        baseline[t] = float(f0_start[t])
        delta_h0[t] = q * h0 * float(w_start_u[t - 1])
        delta_hplus[t] = q * sum(float(w_start_u[t - 1 - tp]) * float(h[tp]) for tp in range(1, t))
        fu_h0[t] = -q * h0 * sum(float(w_start_u[t - 1 - tp]) * float(f0_u[tp]) for tp in range(t))
        total_hplus = 0.0
        for tp in range(t):
            total_hplus += float(w_start_u[t - 1 - tp]) * sum(
                float(f0_u[tp - tt]) * float(h[tt]) for tt in range(1, tp + 1)
            )
        fu_hplus[t] = -q * total_hplus

    total = baseline + delta_h0 + delta_hplus + fu_h0 + fu_hplus
    return {
        "baseline": baseline,
        "delta_h0": delta_h0,
        "delta_hplus": delta_hplus,
        "fu_h0": fu_h0,
        "fu_hplus": fu_hplus,
        "total": total,
    }


def eq14_killed_propagator_formula(
    *,
    n_sites: int,
    q: float,
    start: int,
    end: int,
    target: int,
    t: int,
    corrected: bool,
) -> float:
    total = 0.0
    for r in range(1, n_sites):
        gamma_r = 1.0 - q + q * math.cos(2.0 * math.pi * r / n_sites)
        total += math.cos(2.0 * math.pi * r * (end - start) / n_sites) * (gamma_r**t) / n_sites

    for k in range(1, n_sites):
        odd_weight = 1.0 - ((-1.0) ** k)
        a_k = odd_weight * math.sin(abs(start - target) * math.pi * k / n_sites) * math.sin(math.pi * k / n_sites)
        alpha_k = 1.0 - q + q * math.cos(math.pi * k / n_sites)
        total += a_k * (alpha_k**t) / (n_sites**2 * (1.0 - math.cos(math.pi * k / n_sites)))
        if abs(a_k) < 1.0e-14:
            continue
        for r in range(1, n_sites):
            gamma_r = 1.0 - q + q * math.cos(2.0 * math.pi * r / n_sites)
            denom = math.cos(math.pi * k / n_sites) - math.cos(2.0 * math.pi * r / n_sites)
            if abs(denom) < 1.0e-14:
                raise ArithmeticError(f"unexpected nonzero singular term: N={n_sites} k={k} r={r}")
            bracket = (gamma_r**t - alpha_k**t) if corrected else (alpha_k**t - gamma_r**t)
            total += (
                a_k
                * math.cos(2.0 * math.pi * r * (end - target) / n_sites)
                * bracket
                / (n_sites**2 * denom)
            )
    return float(total)


def validate_eq14_and_orthogonality() -> dict[str, object]:
    max_eq14_corrected = 0.0
    max_eq14_printed = 0.0
    max_orthogonality = 0.0
    rows: list[dict[str, object]] = []
    orth_rows: list[dict[str, object]] = []

    for n_sites, q in ((10, 2.0 / 3.0), (12, 0.41), (100, 2.0 / 3.0)):
        target = n_sites // 2
        starts = (0, 1, n_sites // 3)
        ends = (0, 2, target, (target + 1) % n_sites)
        base = ring_transition(n_sites, q)
        tmax = 16 if n_sites < 100 else 8

        for start in starts:
            if start == target:
                continue
            for end in ends:
                exact = absorbing_propagator_series(base, target, start, end, tmax)
                for t in range(tmax + 1):
                    corrected = eq14_killed_propagator_formula(
                        n_sites=n_sites,
                        q=q,
                        start=start,
                        end=end,
                        target=target,
                        t=t,
                        corrected=True,
                    )
                    printed = eq14_killed_propagator_formula(
                        n_sites=n_sites,
                        q=q,
                        start=start,
                        end=end,
                        target=target,
                        t=t,
                        corrected=False,
                    )
                    err_corrected = abs(corrected - float(exact[t]))
                    err_printed = abs(printed - float(exact[t]))
                    max_eq14_corrected = max(max_eq14_corrected, err_corrected)
                    max_eq14_printed = max(max_eq14_printed, err_printed)
                    rows.append(
                        {
                            "N": n_sites,
                            "q": q,
                            "target": target,
                            "start": start,
                            "end": end,
                            "t": t,
                            "exact_absorbing": float(exact[t]),
                            "corrected_eq14": corrected,
                            "printed_order_eq14": printed,
                            "err_corrected": err_corrected,
                            "err_printed_order": err_printed,
                        }
                    )

        for a_mod in range(1, n_sites):
            for b_mod in range(1, n_sites):
                cos_sum = sum(
                    math.cos(2.0 * math.pi * k * a_mod / n_sites)
                    * math.cos(2.0 * math.pi * k * b_mod / n_sites)
                    for k in range(1, n_sites)
                )
                sin_sum = sum(
                    (1.0 - ((-1.0) ** k))
                    * math.sin(math.pi * k * abs(a_mod) / n_sites)
                    * math.sin(math.pi * k * abs(b_mod) / n_sites)
                    for k in range(1, n_sites)
                )
                rhs = 0.5 * n_sites * ((1.0 if a_mod == b_mod else 0.0) + (1.0 if a_mod == n_sites - b_mod else 0.0))
                err_cos = abs(cos_sum - (rhs - 1.0))
                err_sin = abs(sin_sum - rhs)
                max_orthogonality = max(max_orthogonality, err_cos, err_sin)
                if err_cos > 1.0e-10 or err_sin > 1.0e-10:
                    orth_rows.append(
                        {
                            "N": n_sites,
                            "a": a_mod,
                            "b": b_mod,
                            "cos_sum": cos_sum,
                            "sin_sum": sin_sum,
                            "rhs_delta": rhs,
                            "err_cos": err_cos,
                            "err_sin": err_sin,
                        }
                    )

    return {
        "rows": rows,
        "orthogonality_fail_rows": orth_rows,
        "max_err_eq14_corrected_vs_absorbing": max_eq14_corrected,
        "max_err_eq14_printed_order_vs_absorbing": max_eq14_printed,
        "max_err_orthogonality_identities": max_orthogonality,
    }


def validate_hard_route_time_convolution() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    max_err = 0.0
    max_component_err = 0.0
    max_component_vs_hard_err = 0.0
    cases = (
        (10, 2.0 / 3.0, 4.0 / 7.0, 1, 5, 30),
        (12, 0.41, 0.35, 2, 7, 36),
        (20, 2.0 / 3.0, 0.04, 2, 10, 70),
        (100, 2.0 / 3.0, 0.04, 0, 5, 160),
    )
    for n_sites, q, beta, start, u, tmax in cases:
        v = (u + n_sites // 2) % n_sites
        base = ring_transition(n_sites, q)
        shortcut = stochastic_shortcut_transition(base, u, v, beta, q)
        direct = first_passage_pmf_series(shortcut, v, start, tmax)
        hard = hard_route_convolution_pmf(
            n_sites=n_sites,
            q=q,
            beta=beta,
            start=start,
            u=u,
            v=v,
            tmax=tmax,
        )
        components = hard_route_convolution_components(
            n_sites=n_sites,
            q=q,
            beta=beta,
            start=start,
            u=u,
            v=v,
            tmax=tmax,
        )
        for t in range(tmax + 1):
            err = abs(float(hard[t]) - float(direct[t]))
            component_sum = float(components["total"][t])
            component_err = abs(component_sum - float(direct[t]))
            component_vs_hard_err = abs(component_sum - float(hard[t]))
            max_err = max(max_err, err)
            max_component_err = max(max_component_err, component_err)
            max_component_vs_hard_err = max(max_component_vs_hard_err, component_vs_hard_err)
            rows.append(
                {
                    "N": n_sites,
                    "q": q,
                    "beta": beta,
                    "start": start,
                    "u": u,
                    "v": v,
                    "t": t,
                    "direct_shortcut_pmf": float(direct[t]),
                    "hard_route_convolution_pmf": float(hard[t]),
                    "eq57_group1_baseline": float(components["baseline"][t]),
                    "eq57_group2_delta_h0": float(components["delta_h0"][t]),
                    "eq57_group3_delta_hplus": float(components["delta_hplus"][t]),
                    "eq57_group4_fu_h0": float(components["fu_h0"][t]),
                    "eq57_group5_fu_hplus": float(components["fu_hplus"][t]),
                    "eq57_five_group_sum": component_sum,
                    "err": err,
                    "err_eq57_five_group_sum": component_err,
                    "err_eq57_five_group_sum_vs_hard_route": component_vs_hard_err,
                }
            )
    return {
        "rows": rows,
        "max_err_hard_route_convolution_vs_direct_pmf": max_err,
        "max_err_eq57_five_group_sum_vs_direct_pmf": max_component_err,
        "max_err_eq57_five_group_sum_vs_hard_route": max_component_vs_hard_err,
    }


def validate_kernel_expansion_identities() -> float:
    def a_plus_sum(t: int, x: float, s: float) -> float:
        return sum((x ** (t - 1 - c)) * (s ** (c - 1)) for c in range(1, t))

    def a_plus_display(t: int, x: float, s: float) -> float:
        if abs(s - x) < 1.0e-14:
            return (t - 1) * (s ** (t - 2)) if t >= 2 else 0.0
        return (s ** (t - 1) - x ** (t - 1)) / (s - x)

    def b_zero_sum(t: int, x: float, y: float) -> float:
        return sum((x ** (t - 1 - b)) * (y ** (b - 1)) for b in range(1, t))

    def b_zero_display(t: int, x: float, y: float) -> float:
        if abs(x - y) < 1.0e-14:
            return (t - 1) * (x ** (t - 2)) if t >= 2 else 0.0
        return (x ** (t - 1) - y ** (t - 1)) / (x - y)

    def b_plus_sum(t: int, x: float, y: float, s: float) -> float:
        total = 0.0
        for b in range(1, t):
            for c in range(1, t - b):
                a = t - 1 - b - c
                total += (x**a) * (y ** (b - 1)) * (s ** (c - 1))
        return total

    def b_plus_display(t: int, x: float, y: float, s: float) -> float:
        if abs(x - y) < 1.0e-14:
            if abs(s - x) < 1.0e-14:
                return sum((t - 1 - c) * (x ** (t - 2 - c)) * (s ** (c - 1)) for c in range(1, t - 1))
            return ((s ** (t - 1) - x ** (t - 1)) / ((s - x) ** 2)) - ((t - 1) * (x ** (t - 2)) / (s - x))
        return (
            (x ** (t - 1)) / ((x - y) * (x - s))
            + (y ** (t - 1)) / ((y - x) * (y - s))
            + (s ** (t - 1)) / ((s - x) * (s - y))
        )

    max_err = 0.0
    triples = (
        (0.23, 0.51, 0.81),
        (0.91, 0.42, 0.17),
        (-0.15, 0.37, 0.73),
    )
    for t in range(1, 18):
        for x, y, s in triples:
            max_err = max(max_err, abs(a_plus_sum(t, x, s) - a_plus_display(t, x, s)))
            max_err = max(max_err, abs(a_plus_sum(t, x, x) - a_plus_display(t, x, x)))
            max_err = max(max_err, abs(b_zero_sum(t, x, y) - b_zero_display(t, x, y)))
            max_err = max(max_err, abs(b_zero_sum(t, x, x) - b_zero_display(t, x, x)))
            max_err = max(max_err, abs(b_plus_sum(t, x, y, s) - b_plus_display(t, x, y, s)))
            max_err = max(max_err, abs(b_plus_sum(t, x, x, s) - b_plus_display(t, x, x, s)))
    return max_err


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
        at_or_above_actual = int(row["clear_at_or_above_beta_c_count"])
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
                    "beta_c_threshold": beta_c,
                    "beta_below_threshold": float(beta) < beta_c - 1.0e-12,
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
        below = [r for r in group if bool(r["beta_below_threshold"])]
        above = [r for r in group if not bool(r["beta_below_threshold"])]
        min_yes = math.nan
        max_yes = math.nan
        last_no_before_yes = math.nan
        first_no_after_yes = math.nan
        if yes:
            min_yes = min(float(r["beta"]) for r in yes)
            max_yes = max(float(r["beta"]) for r in yes)
            earlier_no = [
                r
                for r in group
                if float(r["beta"]) < min_yes and not bool(r["clear_double_peak"])
            ]
            if earlier_no:
                last_no_before_yes = float(earlier_no[-1]["beta"])
            later_no = [r for r in group if float(r["beta"]) > max_yes and not bool(r["clear_double_peak"])]
            if later_no:
                first_no_after_yes = float(later_no[0]["beta"])
        rows.append(
            {
                "n0_paper": int(n0),
                "target_paper": int(group[0]["target_paper"]),
                "sc_src_paper": int(group[0]["sc_src_paper"]),
                "sc_dst_paper": int(group[0]["sc_dst_paper"]),
                "beta_c_threshold": float(group[0]["beta_c_threshold"]),
                "any_clear_double_peak": bool(any(bool(r["clear_double_peak"]) for r in group)),
                "last_beta_no_before_clear": last_no_before_yes,
                "min_beta_clear_double_peak": min_yes,
                "max_beta_clear_double_peak": max_yes,
                "first_beta_no_after_clear": first_no_after_yes,
                "clear_below_beta_c_count": sum(1 for r in below if bool(r["clear_double_peak"])),
                "clear_at_or_above_beta_c_count": sum(1 for r in above if bool(r["clear_double_peak"])),
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


def write_empty_csv(path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()


def main() -> None:
    outdir = AUDIT_DIR / "send_preflight_numeric_validation_20260607"
    outdir.mkdir(parents=True, exist_ok=True)

    resolvent_checks = validate_resolvent_and_closed_form()
    eq14_checks = validate_eq14_and_orthogonality()
    hard_route_checks = validate_hard_route_time_convolution()
    kernel_expansion_err = validate_kernel_expansion_identities()
    pole_checks = validate_poles()
    peak_checks = validate_double_peaks()

    write_csv(outdir / "resolvent_closed_form_checks.csv", resolvent_checks["rows"])  # type: ignore[arg-type]
    write_csv(outdir / "eq14_killed_propagator_checks.csv", eq14_checks["rows"])  # type: ignore[arg-type]
    if eq14_checks["orthogonality_fail_rows"]:
        write_csv(outdir / "orthogonality_identity_failures.csv", eq14_checks["orthogonality_fail_rows"])  # type: ignore[arg-type]
    else:
        write_empty_csv(
            outdir / "orthogonality_identity_failures.csv",
            ["N", "a", "b", "cos_sum", "sin_sum", "rhs_delta", "err_cos", "err_sin"],
        )
    write_csv(outdir / "hard_route_convolution_checks.csv", hard_route_checks["rows"])  # type: ignore[arg-type]
    write_csv(outdir / "pole_checks.csv", pole_checks["rows"])  # type: ignore[arg-type]
    write_csv(outdir / "double_peak_metrics.csv", peak_checks["metrics_rows"])  # type: ignore[arg-type]
    write_csv(outdir / "double_peak_summary.csv", peak_checks["summary"])  # type: ignore[arg-type]

    summary = {
        "max_err_corrected_plus_vs_direct": resolvent_checks["max_err_corrected_plus_vs_direct"],
        "max_err_closed_form_vs_direct": resolvent_checks["max_err_closed_form_vs_direct"],
        "max_err_eq14_corrected_vs_absorbing": eq14_checks["max_err_eq14_corrected_vs_absorbing"],
        "max_err_eq14_printed_order_vs_absorbing": eq14_checks["max_err_eq14_printed_order_vs_absorbing"],
        "max_err_orthogonality_identities": eq14_checks["max_err_orthogonality_identities"],
        "orthogonality_failure_rows": len(eq14_checks["orthogonality_fail_rows"]),  # type: ignore[arg-type]
        "max_err_hard_route_convolution_vs_direct_pmf": hard_route_checks[
            "max_err_hard_route_convolution_vs_direct_pmf"
        ],
        "max_err_eq57_five_group_sum_vs_direct_pmf": hard_route_checks[
            "max_err_eq57_five_group_sum_vs_direct_pmf"
        ],
        "max_err_eq57_five_group_sum_vs_hard_route": hard_route_checks[
            "max_err_eq57_five_group_sum_vs_hard_route"
        ],
        "max_err_kernel_expansion_identities": kernel_expansion_err,
        "min_s1_minus_gamma1": pole_checks["min_s1_minus_gamma1"],
        "min_alpha1_minus_s1": pole_checks["min_alpha1_minus_s1"],
        "max_denominator_residual": pole_checks["max_denominator_residual"],
        "max_denominator_normalized_residual": pole_checks["max_denominator_normalized_residual"],
        "double_peak_matches_email_claim": peak_checks["matches_email_claim"],
        "beta_c": peak_checks["beta_c"],
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    def fmt_beta(value: object) -> str:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return "--"
        if math.isnan(numeric):
            return "--"
        return f"{numeric:.3f}"

    lines = [
        "# Sendable preflight numerical validation",
        "",
        f"- corrected plus/plus formula vs direct matrix: {summary['max_err_corrected_plus_vs_direct']:.6e}",
        f"- compact closed form vs direct matrix: {summary['max_err_closed_form_vs_direct']:.6e}",
        f"- corrected Eq. (14) killed propagator vs absorbing matrix: {summary['max_err_eq14_corrected_vs_absorbing']:.6e}",
        f"- old reversed-bracket Eq. (14) killed propagator vs absorbing matrix: {summary['max_err_eq14_printed_order_vs_absorbing']:.6e}",
        f"- orthogonality identities max residual: {summary['max_err_orthogonality_identities']:.6e}",
        f"- hard-route time convolution vs direct shortcut PMF: {summary['max_err_hard_route_convolution_vs_direct_pmf']:.6e}",
        f"- Eq. (57) five-group sum vs direct shortcut PMF: {summary['max_err_eq57_five_group_sum_vs_direct_pmf']:.6e}",
        f"- Eq. (57) five-group sum vs hard-route convolution: {summary['max_err_eq57_five_group_sum_vs_hard_route']:.6e}",
        f"- kernel-to-fully-expanded identities: {summary['max_err_kernel_expansion_identities']:.6e}",
        f"- min(s1-gamma1) over sampled betas: {summary['min_s1_minus_gamma1']:.6e}",
        f"- min(alpha1-s1) over sampled betas: {summary['min_alpha1_minus_s1']:.6e}",
        f"- max denominator residual at spectral s1: {summary['max_denominator_residual']:.6e}",
        f"- max normalized denominator residual at spectral s1: {summary['max_denominator_normalized_residual']:.6e}",
        f"- double-peak summary matches email claim: {summary['double_peak_matches_email_claim']}",
        f"- beta_c reference value for the N=100 scan: {summary['beta_c']:.6f}",
        "",
        "Clear double-peak sampled beta brackets:",
        "",
        "n0 | no before | first clear | last clear | no after | clear at beta>=beta_c",
        "-- | --------- | ----------- | ---------- | -------- | ----------------------",
    ]
    for row in peak_checks["summary"]:  # type: ignore[index]
        lines.append(
            " | ".join(
                [
                    str(row["n0_paper"]),
                    fmt_beta(row["last_beta_no_before_clear"]),
                    fmt_beta(row["min_beta_clear_double_peak"]),
                    fmt_beta(row["max_beta_clear_double_peak"]),
                    fmt_beta(row["first_beta_no_after_clear"]),
                    str(row["clear_at_or_above_beta_c_count"]),
                ]
            )
        )
    lines.extend(
        [
            "",
            "These are sampled-grid brackets, not analytic threshold proofs.",
            "",
            "Outputs:",
            "",
            "- resolvent_closed_form_checks.csv",
            "- eq14_killed_propagator_checks.csv",
            "- orthogonality_identity_failures.csv",
            "- hard_route_convolution_checks.csv",
            "- pole_checks.csv",
            "- double_peak_metrics.csv",
            "- double_peak_summary.csv",
            "- summary.json",
        ]
    )
    (outdir / "README.md").write_text("\n".join(lines), encoding="utf-8")

    checks = [
        summary["max_err_corrected_plus_vs_direct"] < 1.0e-12,
        summary["max_err_closed_form_vs_direct"] < 1.0e-12,
        summary["max_err_eq14_corrected_vs_absorbing"] < 1.0e-12,
        summary["max_err_eq14_printed_order_vs_absorbing"] > 1.0e-4,
        summary["max_err_orthogonality_identities"] < 1.0e-10,
        int(summary["orthogonality_failure_rows"]) == 0,
        summary["max_err_hard_route_convolution_vs_direct_pmf"] < 1.0e-12,
        summary["max_err_eq57_five_group_sum_vs_direct_pmf"] < 1.0e-12,
        summary["max_err_eq57_five_group_sum_vs_hard_route"] < 1.0e-12,
        summary["max_err_kernel_expansion_identities"] < 1.0e-12,
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
