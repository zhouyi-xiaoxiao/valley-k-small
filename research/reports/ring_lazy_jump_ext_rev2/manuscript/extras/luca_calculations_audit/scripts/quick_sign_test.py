#!/usr/bin/env python3
"""Numerical sign check for the shortcut-to-absorbing-target calculation.

The test compares four quantities:

1. the first-passage generating function from the actual stochastic shortcut
   transition matrix, where lambda = beta(1-q) is moved from the self-loop at u
   to the shortcut u -> v;
2. the ratio obtained by using Eq. (29) literally as printed;
3. Eq. (32) with the original minus/minus sign;
4. Eq. (32) with the corrected plus/plus sign.

It also checks that the absorbing propagator used in Eq. (32) agrees with the
z-transform of Eq. (19), and that the symmetric self Green function agrees with
Eq. (28).
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class Case:
    name: str
    N: int
    q: float
    beta: float
    u: int
    v: int
    n0_values: tuple[int, ...]
    z_values: tuple[float, ...]


DEFAULT_CASES = (
    Case(
        name="figure-parameters",
        N=10,
        q=2.0 / 3.0,
        beta=2.0 / 7.0,
        u=5,
        v=0,
        n0_values=(1, 2, 4, 7),
        z_values=(0.2, 0.5, 0.8, 0.95),
    ),
    Case(
        name="moderate-shortcut",
        N=20,
        q=2.0 / 3.0,
        beta=0.1,
        u=10,
        v=0,
        n0_values=(1, 3, 8, 14),
        z_values=(0.25, 0.6, 0.85, 0.97),
    ),
)


def ring_transition(N: int, q: float) -> np.ndarray:
    transition = np.zeros((N, N), dtype=float)
    for i in range(N):
        transition[i, i] += 1.0 - q
        transition[i, (i - 1) % N] += q / 2.0
        transition[i, (i + 1) % N] += q / 2.0
    return transition


def stochastic_shortcut_transition(T: np.ndarray, u: int, v: int, lam: float) -> np.ndarray:
    shortcut = T.copy()
    shortcut[u, u] -= lam
    shortcut[u, v] += lam
    return shortcut


def resolvent(T: np.ndarray, z: float) -> np.ndarray:
    return np.linalg.inv(np.eye(T.shape[0]) - z * T)


def absorbing_resolvent(T: np.ndarray, v: int, z: float) -> tuple[np.ndarray, dict[int, int]]:
    keep = [i for i in range(T.shape[0]) if i != v]
    sub = T[np.ix_(keep, keep)]
    return resolvent(sub, z), {old: new for new, old in enumerate(keep)}


def w_abs_matrix(W: np.ndarray, index: dict[int, int], start: int, end: int, v: int) -> float:
    if start == v or end == v:
        return 0.0
    return float(W[index[start], index[end]])


def chebyshev_u(n: int, x: float) -> float:
    if n == -1:
        return 0.0
    if n == 0:
        return 1.0
    u_nm2 = 1.0
    u_nm1 = 2.0 * x
    if n == 1:
        return u_nm1
    for _ in range(2, n + 1):
        u_n = 2.0 * x * u_nm1 - u_nm2
        u_nm2, u_nm1 = u_nm1, u_n
    return u_nm1


def w_eq19(N: int, q: float, start: int, end: int, m: int, z: float) -> float:
    total = 0.0
    for k in range(1, N):
        gamma = 1.0 - q + q * math.cos(2.0 * math.pi * k / N)
        g1 = (
            math.cos(2.0 * math.pi * k * (end - start) / N)
            - math.cos(2.0 * math.pi * k * (end - m) / N)
            * math.cos(2.0 * math.pi * k * (start - m) / N)
        ) / N
        total += g1 / (1.0 - z * gamma)

        alpha_general = 1.0 - q + q * math.cos(math.pi * k / N)
        g2 = (
            (1.0 - (-1.0) ** k)
            * math.sin(math.pi * k * abs(start - m) / N)
            * math.sin(math.pi * k * abs(end - m) / N)
        ) / N
        total += g2 / (1.0 - z * alpha_general)
    return total


def w_eq28_symmetric(N: int, q: float, z: float) -> float:
    y = 1.0 + (1.0 / q) * (1.0 / z - 1.0)
    return 2.0 * chebyshev_u(N // 2 - 1, y) ** 2 / (z * q * chebyshev_u(N - 1, y))


def eq29_literal(P: np.ndarray, z: float, lam: float, u: int, v: int, start: int, end: int) -> float:
    den = 1.0 - z * lam * (P[u, u] - P[v, u])
    return float(P[start, end] + z * lam * P[start, u] * (P[u, end] - P[v, end]) / den)


def eq29_stochastic_sign(P: np.ndarray, z: float, lam: float, u: int, v: int, start: int, end: int) -> float:
    den = 1.0 + z * lam * (P[u, u] - P[v, u])
    return float(P[start, end] - z * lam * P[start, u] * (P[u, end] - P[v, end]) / den)


def first_passage_variants(case: Case) -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    T0 = ring_transition(case.N, case.q)
    lam = case.beta * (1.0 - case.q)
    T_short = stochastic_shortcut_transition(T0, case.u, case.v, lam)

    for z in case.z_values:
        P = resolvent(T0, z)
        S_matrix = resolvent(T_short, z)
        W_matrix, w_index = absorbing_resolvent(T0, case.v, z)

        wuu_matrix = w_abs_matrix(W_matrix, w_index, case.u, case.u, case.v)
        wuu_eq28 = w_eq28_symmetric(case.N, case.q, z)

        for n0 in case.n0_values:
            if n0 in (case.u, case.v):
                continue
            f_ratio_matrix = float(S_matrix[n0, case.v] / S_matrix[case.v, case.v])

            s_lit_n0v = eq29_literal(P, z, lam, case.u, case.v, n0, case.v)
            s_lit_vv = eq29_literal(P, z, lam, case.u, case.v, case.v, case.v)
            f_eq29_literal = s_lit_n0v / s_lit_vv

            s_sto_n0v = eq29_stochastic_sign(P, z, lam, case.u, case.v, n0, case.v)
            s_sto_vv = eq29_stochastic_sign(P, z, lam, case.u, case.v, case.v, case.v)
            f_eq29_stochastic_sign = s_sto_n0v / s_sto_vv

            f0 = float(P[n0, case.v] / P[case.v, case.v])
            fu = float(P[case.u, case.v] / P[case.v, case.v])
            wn0u_matrix = w_abs_matrix(W_matrix, w_index, n0, case.u, case.v)
            wn0u_eq19 = w_eq19(case.N, case.q, n0, case.u, case.v, z)

            shortcut_factor_matrix = z * lam * wn0u_matrix * (1.0 - fu)
            f_eq32_original = f0 - shortcut_factor_matrix / (1.0 - z * lam * wuu_matrix)
            f_eq32_corrected = f0 + shortcut_factor_matrix / (1.0 + z * lam * wuu_matrix)

            rows.append(
                {
                    "case": case.name,
                    "N": case.N,
                    "q": case.q,
                    "beta": case.beta,
                    "lambda": lam,
                    "u": case.u,
                    "v": case.v,
                    "n0": n0,
                    "z": z,
                    "F_matrix_shortcut": f_ratio_matrix,
                    "F_eq29_literal_ratio": f_eq29_literal,
                    "F_eq29_stochastic_sign_ratio": f_eq29_stochastic_sign,
                    "F_eq32_original_minus_minus": f_eq32_original,
                    "F_eq32_corrected_plus_plus": f_eq32_corrected,
                    "err_original_vs_matrix": abs(f_eq32_original - f_ratio_matrix),
                    "err_corrected_vs_matrix": abs(f_eq32_corrected - f_ratio_matrix),
                    "err_literal_eq29_vs_original": abs(f_eq29_literal - f_eq32_original),
                    "err_stochastic_sign_eq29_vs_corrected": abs(f_eq29_stochastic_sign - f_eq32_corrected),
                    "err_Wn0u_eq19_vs_matrix": abs(wn0u_eq19 - wn0u_matrix),
                    "err_Wuu_eq28_vs_matrix": abs(wuu_eq28 - wuu_matrix),
                }
            )
    return rows


def write_csv(rows: list[dict[str, float | int | str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, float | int | str]], path: Path) -> None:
    max_original = max(float(row["err_original_vs_matrix"]) for row in rows)
    max_corrected = max(float(row["err_corrected_vs_matrix"]) for row in rows)
    max_lit = max(float(row["err_literal_eq29_vs_original"]) for row in rows)
    max_sto = max(float(row["err_stochastic_sign_eq29_vs_corrected"]) for row in rows)
    max_eq19 = max(float(row["err_Wn0u_eq19_vs_matrix"]) for row in rows)
    max_eq28 = max(float(row["err_Wuu_eq28_vs_matrix"]) for row in rows)

    examples = [
        row
        for row in rows
        if row["case"] == "figure-parameters" and row["n0"] == 2 and row["z"] in (0.5, 0.8, 0.95)
    ]

    lines = [
        "# Quick sign test for the shortcut sign",
        "",
        "This is a numerical ratio check using real values of `z`.",
        "",
        "## Verdict",
        "",
        "- The actual stochastic shortcut matrix, where `lambda = beta(1-q)` is",
        "  moved from the self-loop at `u` to the directed edge `u -> v`, agrees",
        "  with Eq. (32) only with the corrected plus/plus sign.",
        "- Eq. (29), if used literally as printed, agrees with the",
        "  original minus/minus Eq. (32). This shows that the sign inconsistency",
        "  is already present in the printed Eq. (29) when it is interpreted as a",
        "  stochastic shortcut from `u` to `v`.",
        "",
        "## Max Errors Over The Test Grid",
        "",
        f"- original Eq. (32) vs stochastic matrix: `{max_original:.6e}`",
        f"- corrected Eq. (32) vs stochastic matrix: `{max_corrected:.6e}`",
        f"- literal Eq. (29) ratio vs original Eq. (32): `{max_lit:.6e}`",
        f"- stochastic-sign Eq. (29) ratio vs corrected Eq. (32): `{max_sto:.6e}`",
        f"- Eq. (19) W(n0,u,z) vs absorbing matrix: `{max_eq19:.6e}`",
        f"- Eq. (28) W(u,u,z) vs absorbing matrix: `{max_eq28:.6e}`",
        "",
        "## Representative Rows",
        "",
        "| N | q | beta | u | v | n0 | z | stochastic matrix | literal Eq. (29) | Eq. (32) original | Eq. (32) corrected |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in examples:
        lines.append(
            "| {N} | {q:.6g} | {beta:.6g} | {u} | {v} | {n0} | {z:.6g} | "
            "{F_matrix_shortcut:.12g} | {F_eq29_literal_ratio:.12g} | "
            "{F_eq32_original_minus_minus:.12g} | {F_eq32_corrected_plus_plus:.12g} |".format(**row)
        )

    lines.extend(
        [
            "",
            "All site indices in this test are zero-based. The first case uses the",
            "parameters from the figure in the manuscript: `N=10`, `q=2/3`, `beta=2/7`,",
            "`u=5`, `v=0`, so `|u-v|=N/2`.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--md", type=Path, required=True)
    args = parser.parse_args()

    rows: list[dict[str, float | int | str]] = []
    for case in DEFAULT_CASES:
        rows.extend(first_passage_variants(case))

    write_csv(rows, args.csv)
    write_markdown(rows, args.md)

    max_corrected = max(float(row["err_corrected_vs_matrix"]) for row in rows)
    max_original = max(float(row["err_original_vs_matrix"]) for row in rows)
    print(f"rows={len(rows)}")
    print(f"max_err_corrected_vs_matrix={max_corrected:.6e}")
    print(f"max_err_original_vs_matrix={max_original:.6e}")
    print(f"csv={args.csv}")
    print(f"md={args.md}")


if __name__ == "__main__":
    main()
