#!/usr/bin/env python3
"""Numerical checks for the pre-shortcut part of the updated calculation.

The checks cover the active manuscript before the shortcut section:
preliminary finite-series identities, no-shortcut first passage, killed
propagator formulae, and Chebyshev compact forms.  The goal is to separate
formulae that are numerically sound from notation/indexing slips that are easy
to miss when reading the TeX.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class CheckResult:
    check: str
    max_error: float
    status: str
    note: str


def t_cheb(n: int, y: float) -> float:
    if n < 0:
        raise ValueError(f"negative Chebyshev T index: {n}")
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
        raise ValueError(f"negative Chebyshev U index: {n}")
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


def absorbing_submatrix(transition: np.ndarray, target: int) -> tuple[np.ndarray, dict[int, int], list[int]]:
    keep = [i for i in range(transition.shape[0]) if i != target]
    index = {old: new for new, old in enumerate(keep)}
    return transition[np.ix_(keep, keep)], index, keep


def q_formula(n_sites: int, q: float, start: int, end: int, time: int) -> float:
    return sum(
        math.cos(2.0 * math.pi * k * (end - start) / n_sites)
        * (1.0 - q + q * math.cos(2.0 * math.pi * k / n_sites)) ** time
        for k in range(n_sites)
    ) / n_sites


def f_time(n_sites: int, q: float, start: int, target: int, time: int) -> float:
    if time == 0:
        return 0.0
    return (
        q
        / n_sites
        * sum(
            (1.0 - (-1.0) ** k)
            * math.sin(abs(target - start) * math.pi * k / n_sites)
            * math.sin(math.pi * k / n_sites)
            * (1.0 - q + q * math.cos(math.pi * k / n_sites)) ** (time - 1)
            for k in range(1, n_sites)
        )
    )


def f_compact_time(n_sites: int, q: float, start: int, target: int, time: int) -> float:
    if time == 0:
        return 0.0
    return sum(
        (2.0 * q / n_sites)
        * math.sin(abs(target - start) * math.pi * (2 * k - 1) / n_sites)
        * math.sin(math.pi * (2 * k - 1) / n_sites)
        * (1.0 - q + q * math.cos(math.pi * (2 * k - 1) / n_sites)) ** (time - 1)
        for k in range(1, n_sites // 2 + 1)
    )


def f_gf_correct_sum(n_sites: int, q: float, start: int, target: int, z: float) -> float:
    return z * sum(
        (2.0 * q / n_sites)
        * math.sin(abs(target - start) * math.pi * (2 * k - 1) / n_sites)
        * math.sin(math.pi * (2 * k - 1) / n_sites)
        / (1.0 - z * (1.0 - q + q * math.cos(math.pi * (2 * k - 1) / n_sites)))
        for k in range(1, n_sites // 2 + 1)
    )


def f_gf_literal_wrong_upper(n_sites: int, q: float, start: int, target: int, z: float) -> float:
    # Literal reading of line 251 after f_k and alpha_k have been defined with
    # the compact odd-mode indexing.  This is intentionally the problematic
    # version.
    return z * sum(
        (2.0 * q / n_sites)
        * math.sin(abs(target - start) * math.pi * (2 * k - 1) / n_sites)
        * math.sin(math.pi * (2 * k - 1) / n_sites)
        / (1.0 - z * (1.0 - q + q * math.cos(math.pi * (2 * k - 1) / n_sites)))
        for k in range(1, n_sites)
    )


def f_gf_cheb(n_sites: int, q: float, start: int, target: int, z: float) -> float:
    d = abs(target - start)
    y = 1.0 + (1.0 / z - 1.0) / q
    return (u_cheb(n_sites - d - 1, y) + u_cheb(d - 1, y)) / u_cheb(n_sites - 1, y)


def g1(n_sites: int, start: int, end: int, target: int, k: int) -> float:
    return (
        math.cos(2.0 * math.pi * k * (end - start) / n_sites)
        - math.cos(2.0 * math.pi * k * (end - target) / n_sites)
        * math.cos(2.0 * math.pi * k * (start - target) / n_sites)
    ) / n_sites


def g2(n_sites: int, start: int, end: int, target: int, k: int) -> float:
    return (
        (1.0 - (-1.0) ** k)
        * math.sin(math.pi * k * abs(start - target) / n_sites)
        * math.sin(math.pi * k * abs(end - target) / n_sites)
    ) / n_sites


def small_g2(n_sites: int, start: int, end: int, target: int, k: int) -> float:
    return (
        2.0
        / n_sites
        * math.sin(math.pi * (2 * k - 1) * abs(start - target) / n_sites)
        * math.sin(math.pi * (2 * k - 1) * abs(end - target) / n_sites)
    )


def w_time_formula(n_sites: int, q: float, start: int, end: int, target: int, time: int) -> float:
    return (
        sum(
            math.cos(2.0 * math.pi * k * (end - start) / n_sites)
            * (1.0 - q + q * math.cos(2.0 * math.pi * k / n_sites)) ** time
            for k in range(1, n_sites)
        )
        / n_sites
        - sum(
            math.cos(2.0 * math.pi * k * (end - target) / n_sites)
            * math.cos(2.0 * math.pi * k * (start - target) / n_sites)
            * (1.0 - q + q * math.cos(2.0 * math.pi * k / n_sites)) ** time
            for k in range(1, n_sites)
        )
        / n_sites
        + sum(
            (1.0 - (-1.0) ** k)
            * math.sin(math.pi * k * abs(start - target) / n_sites)
            * math.sin(math.pi * k * abs(end - target) / n_sites)
            * (1.0 - q + q * math.cos(math.pi * k / n_sites)) ** time
            for k in range(1, n_sites)
        )
        / n_sites
    )


def w_gf_general_sum(n_sites: int, q: float, start: int, end: int, target: int, z: float) -> float:
    total = 0.0
    for k in range(1, n_sites):
        total += g1(n_sites, start, end, target, k) / (
            1.0 - z * (1.0 - q + q * math.cos(2.0 * math.pi * k / n_sites))
        )
        total += g2(n_sites, start, end, target, k) / (
            1.0 - z * (1.0 - q + q * math.cos(math.pi * k / n_sites))
        )
    return total


def w_gf_compact_sum(n_sites: int, q: float, start: int, end: int, target: int, z: float) -> float:
    total = sum(
        g1(n_sites, start, end, target, k)
        / (1.0 - z * (1.0 - q + q * math.cos(2.0 * math.pi * k / n_sites)))
        for k in range(1, n_sites)
    )
    total += sum(
        small_g2(n_sites, start, end, target, k)
        / (1.0 - z * (1.0 - q + q * math.cos(math.pi * (2 * k - 1) / n_sites)))
        for k in range(1, n_sites // 2 + 1)
    )
    return total


def g1_cheb_rhs(n_sites: int, q: float, start: int, end: int, target: int, z: float) -> float:
    y = 1.0 + (1.0 / z - 1.0) / q
    d = abs(end - start)
    a = abs(abs(start - target) - abs(end - target))
    b = (abs(start - target) + abs(end - target)) % n_sites
    numerator = (
        2.0 * t_cheb(n_sites - d, y)
        + 2.0 * t_cheb(d, y)
        - t_cheb(n_sites - a, y)
        - t_cheb(a, y)
        - t_cheb(n_sites - b, y)
        - t_cheb(b, y)
    )
    denominator = 2.0 * z * q * (y * y - 1.0) * u_cheb(n_sites - 1, y)
    return numerator / denominator


def g2_cheb_rhs(n_sites: int, q: float, start: int, end: int, target: int, z: float) -> float:
    y = 1.0 + (1.0 / z - 1.0) / q
    a = abs(abs(start - target) - abs(end - target))
    c = abs(n_sites - abs(start - target) - abs(end - target))
    numerator = (
        t_cheb(n_sites - a, y)
        + t_cheb(n_sites - c, y)
        - t_cheb(c, y)
        - t_cheb(a, y)
    )
    denominator = 2.0 * z * q * (y * y - 1.0) * u_cheb(n_sites - 1, y)
    return numerator / denominator


def w_self_cheb(n_sites: int, q: float, site: int, target: int, z: float) -> float:
    y = 1.0 + (1.0 / z - 1.0) / q
    d = abs(site - target)
    b = (2 * d) % n_sites
    numerator = (
        2.0 * t_cheb(n_sites, y)
        + t_cheb(n_sites - abs(n_sites - 2 * d), y)
        - t_cheb(abs(n_sites - 2 * d), y)
        - t_cheb(n_sites - b, y)
        - t_cheb(b, y)
    )
    denominator = 2.0 * z * q * (y * y - 1.0) * u_cheb(n_sites - 1, y)
    return numerator / denominator


def w_antipodal_cheb(n_sites: int, q: float, z: float) -> tuple[float, float]:
    y = 1.0 + (1.0 / z - 1.0) / q
    first = (t_cheb(n_sites, y) - 1.0) / (
        z * q * (y * y - 1.0) * u_cheb(n_sites - 1, y)
    )
    second = 2.0 * u_cheb(n_sites // 2 - 1, y) ** 2 / (
        z * q * u_cheb(n_sites - 1, y)
    )
    return first, second


def preliminary_identity_errors(n_sites: int) -> tuple[float, float, float, float]:
    pointwise = 0.0
    id1 = 0.0
    id2 = 0.0
    id3 = 0.0
    for m in range(1, n_sites):
        for k in range(1, n_sites):
            left = (1.0 - (-1.0) ** k) * math.sin(abs(m) * math.pi * k / n_sites) * math.sin(
                math.pi * k / n_sites
            )
            right = 0.5 * (
                math.cos((abs(m) - 1) * math.pi * k / n_sites)
                - math.cos((abs(m) + 1) * math.pi * k / n_sites)
                - 0.5
                * (
                    math.cos((n_sites - abs(m) + 1) * math.pi * k / n_sites)
                    + math.cos((n_sites + abs(m) - 1) * math.pi * k / n_sites)
                    - math.cos((n_sites - abs(m) - 1) * math.pi * k / n_sites)
                    - math.cos((n_sites + abs(m) + 1) * math.pi * k / n_sites)
                )
            )
            pointwise = max(pointwise, abs(left - right))

        lhs = sum(
            (1.0 - (-1.0) ** k)
            * math.sin(abs(m) * math.pi * k / n_sites)
            * math.sin(math.pi * k / n_sites)
            / (1.0 - math.cos(math.pi * k / n_sites))
            for k in range(1, n_sites)
        ) / n_sites
        id1 = max(id1, abs(lhs - 1.0))

    for m in range(1, n_sites):
        for r in range(1, n_sites):
            denominator_root = math.cos(2.0 * math.pi * r / n_sites)
            total = 0.0
            for k in range(1, n_sites):
                numerator = (
                    (1.0 - (-1.0) ** k)
                    * math.sin(abs(m) * math.pi * k / n_sites)
                    * math.sin(math.pi * k / n_sites)
                )
                denominator = denominator_root - math.cos(math.pi * k / n_sites)
                if abs(denominator) < 1.0e-12:
                    continue
                total += numerator / denominator
            id2 = max(
                id2,
                abs(total / n_sites - math.cos(2.0 * math.pi * r * abs(m) / n_sites)),
            )

    for m in range(0, n_sites + 1):
        for k in range(1, n_sites):
            factor = 1.0 - (-1.0) ** k
            if factor == 0.0:
                lhs = 0.0
            else:
                lhs = (
                    sum(
                        factor
                        * math.cos(2.0 * math.pi * r * m / n_sites)
                        / (math.cos(math.pi * k / n_sites) - math.cos(2.0 * math.pi * r / n_sites))
                        for r in range(1, n_sites)
                    )
                    / n_sites
                )
            rhs = factor * (
                1.0 / (n_sites * (1.0 - math.cos(math.pi * k / n_sites)))
                - math.sin(math.pi * k * abs(m) / n_sites) / math.sin(math.pi * k / n_sites)
            )
            id3 = max(id3, abs(lhs - rhs))
    return pointwise, id1, id2, id3


def identity_line365_errors(n_sites: int) -> tuple[float, float, float, float, float]:
    direct_first = sum(
        (1.0 - (-1.0) ** k) / (1.0 - math.cos(math.pi * k / n_sites))
        for k in range(1, n_sites)
    )
    direct_second = sum(
        1.0 / (1.0 - math.cos(math.pi * k / n_sites)) for k in range(1, n_sites)
    )
    direct_third = sum(
        (-1.0) ** k / (1.0 - math.cos(math.pi * k / n_sites)) for k in range(1, n_sites)
    )
    return (
        abs(direct_first - n_sites * n_sites / 2.0),
        abs(direct_second - (2 * n_sites * n_sites + 1) / 6.0),
        abs(direct_second - (n_sites * n_sites - 1) / 3.0),
        abs(direct_third - (1 - n_sites * n_sites) / 6.0),
        abs(direct_third + (n_sites * n_sites + 2) / 6.0),
    )


def run_checks() -> list[CheckResult]:
    grids = [(10, 2.0 / 3.0), (12, 0.4)]
    z_values = (0.2, 0.55, 0.9)
    times = range(0, 8)

    prelim_errors = [preliminary_identity_errors(n_sites) for n_sites in (4, 6, 10, 12)]
    prelim_max = max(max(values) for values in prelim_errors)

    line365 = [identity_line365_errors(n_sites) for n_sites in (4, 10, 100)]
    line365_first = max(values[0] for values in line365)
    line365_second_printed = max(values[1] for values in line365)
    line365_second_correct = max(values[2] for values in line365)
    line365_third_printed = max(values[3] for values in line365)
    line365_third_correct = max(values[4] for values in line365)

    max_q = 0.0
    max_f_time = 0.0
    max_f_gf = 0.0
    max_f_literal_wrong = 0.0
    max_w_time = 0.0
    max_w_gf = 0.0
    max_g_cheb = 0.0
    max_w_cheb = 0.0

    for n_sites, q in grids:
        transition = ring_transition(n_sites, q)
        for target in range(n_sites):
            absorbing, index, keep = absorbing_submatrix(transition, target)
            hit_vector = transition[keep, target]
            for start in keep:
                for end in keep:
                    for time in times:
                        max_q = max(
                            max_q,
                            abs(
                                q_formula(n_sites, q, start, end, time)
                                - np.linalg.matrix_power(transition, time)[start, end]
                            ),
                        )
                        max_w_time = max(
                            max_w_time,
                            abs(
                                w_time_formula(n_sites, q, start, end, target, time)
                                - np.linalg.matrix_power(absorbing, time)[index[start], index[end]]
                            ),
                        )
                for time in times:
                    matrix_first_passage = (
                        float(np.linalg.matrix_power(absorbing, time - 1)[index[start], :] @ hit_vector)
                        if time >= 1
                        else 0.0
                    )
                    max_f_time = max(
                        max_f_time,
                        abs(f_time(n_sites, q, start, target, time) - matrix_first_passage),
                        abs(f_compact_time(n_sites, q, start, target, time) - matrix_first_passage),
                    )
                for z in z_values:
                    resolvent = np.linalg.inv(np.eye(n_sites - 1) - z * absorbing)
                    matrix_f_gf = float(z * (resolvent[index[start], :] @ hit_vector))
                    max_f_gf = max(
                        max_f_gf,
                        abs(f_gf_correct_sum(n_sites, q, start, target, z) - matrix_f_gf),
                        abs(f_gf_cheb(n_sites, q, start, target, z) - matrix_f_gf),
                    )
                    max_f_literal_wrong = max(
                        max_f_literal_wrong,
                        abs(f_gf_literal_wrong_upper(n_sites, q, start, target, z) - matrix_f_gf),
                    )
                    for end in keep:
                        matrix_w_gf = float(resolvent[index[start], index[end]])
                        max_w_gf = max(
                            max_w_gf,
                            abs(w_gf_general_sum(n_sites, q, start, end, target, z) - matrix_w_gf),
                            abs(w_gf_compact_sum(n_sites, q, start, end, target, z) - matrix_w_gf),
                        )
                        g1_modal = sum(
                            g1(n_sites, start, end, target, k)
                            / (1.0 - z * (1.0 - q + q * math.cos(2.0 * math.pi * k / n_sites)))
                            for k in range(1, n_sites)
                        )
                        g2_modal = sum(
                            g2(n_sites, start, end, target, k)
                            / (1.0 - z * (1.0 - q + q * math.cos(math.pi * k / n_sites)))
                            for k in range(1, n_sites)
                        )
                        max_g_cheb = max(
                            max_g_cheb,
                            abs(g1_cheb_rhs(n_sites, q, start, end, target, z) - g1_modal),
                            abs(g2_cheb_rhs(n_sites, q, start, end, target, z) - g2_modal),
                        )
                    max_w_cheb = max(
                        max_w_cheb,
                        abs(w_self_cheb(n_sites, q, start, target, z) - float(resolvent[index[start], index[start]])),
                    )
            if n_sites % 2 == 0:
                for site in range(n_sites):
                    antipodal_target = (site + n_sites // 2) % n_sites
                    absorbing2, index2, _ = absorbing_submatrix(transition, antipodal_target)
                    for z in z_values:
                        resolvent2 = np.linalg.inv(np.eye(n_sites - 1) - z * absorbing2)
                        matrix_self = float(resolvent2[index2[site], index2[site]])
                        first, second = w_antipodal_cheb(n_sites, q, z)
                        max_w_cheb = max(max_w_cheb, abs(first - matrix_self), abs(second - matrix_self))

    return [
        CheckResult("Eq. (1)-(4) preliminary identities", prelim_max, "PASS", "Direct sums agree to roundoff."),
        CheckResult("Eq. (8) periodic propagator", max_q, "PASS", "Fourier expression matches T^t."),
        CheckResult("Eq. (9)-(12) first-passage time form", max_f_time, "PASS", "Time-domain formula matches absorbing matrix."),
        CheckResult("Eq. (13) corrected compact GF and Chebyshev RHS", max_f_gf, "PASS", "Use compact upper limit N/2."),
        CheckResult("Eq. (13) literal printed compact upper N-1", max_f_literal_wrong, "FAIL", "Printed compact index is incompatible with f_k, alpha_k definitions."),
        CheckResult("Eq. (16) killed propagator time form", max_w_time, "PASS", "Matches absorbing transition submatrix."),
        CheckResult("Eq. (19)-(20) killed propagator GF sums", max_w_gf, "PASS", "Modal sums match absorbing resolvent."),
        CheckResult("Eq. (21)-(22) Chebyshev modal sums", max_g_cheb, "PASS", "Chebyshev forms match modal sums."),
        CheckResult("Eq. (27)-(28) self Green functions", max_w_cheb, "PASS", "Self and antipodal forms match absorbing resolvent."),
        CheckResult("Line 365 first identity", line365_first, "PASS", "N^2/2 identity is correct."),
        CheckResult("Line 365 second identity as printed", line365_second_printed, "FAIL", "Printed value is off by 1/2."),
        CheckResult("Line 365 second identity corrected", line365_second_correct, "PASS", "Correct value is (N^2-1)/3."),
        CheckResult("Line 365 third identity as printed", line365_third_printed, "FAIL", "Printed value is off by 1/2."),
        CheckResult("Line 365 third identity corrected", line365_third_correct, "PASS", "Correct value is -(N^2+2)/6."),
    ]


def write_csv(results: list[CheckResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check", "max_error", "status", "note"])
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "check": result.check,
                    "max_error": f"{result.max_error:.12e}",
                    "status": result.status,
                    "note": result.note,
                }
            )


def write_markdown(results: list[CheckResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Pre-shortcut formula checks",
        "",
        "These checks compare the active TeX formulae before the shortcut section with direct finite sums or finite transition matrices.",
        "",
        "| Check | Status | Max error | Note |",
        "|---|---:|---:|---|",
    ]
    for result in results:
        lines.append(f"| {result.check} | {result.status} | `{result.max_error:.6e}` | {result.note} |")
    lines.append("")
    lines.append("The failing Eq. (13) row is the literal compact upper limit `N-1` after `f_k` and `alpha_k` have been defined with odd-mode index `k=1,...,N/2`; using `N/2` passes.")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=Path("pre_shortcut_formula_check_results.csv"))
    parser.add_argument("--md", type=Path, default=Path("pre_shortcut_formula_check_report.md"))
    args = parser.parse_args()
    results = run_checks()
    write_csv(results, args.csv)
    write_markdown(results, args.md)
    print(f"results={len(results)}")
    for result in results:
        print(f"{result.status:4s} {result.max_error:.6e} {result.check}")
    print(f"csv={args.csv}")
    print(f"md={args.md}")


if __name__ == "__main__":
    main()
