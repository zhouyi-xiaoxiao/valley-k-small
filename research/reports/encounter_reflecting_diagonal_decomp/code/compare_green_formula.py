#!/usr/bin/env python3
"""Compare encounter PGFs from absorbing and Green-renewal formulas."""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


REPORT_DIR = Path(__file__).resolve().parents[1]
ROOT = REPORT_DIR.parents[2]
MEAN_VALIDATION_CODE = ROOT / "research" / "reports" / "encounter_reflecting_mean_validation" / "code"
for path in (MEAN_VALIDATION_CODE,):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from reflecting_encounter import build_joint_transition  # noqa: E402
from reflecting_encounter import build_reflecting_lazy_transition  # noqa: E402
from reflecting_encounter import diagonal_indices  # noqa: E402
from reflecting_encounter import fixed_total_mobility  # noqa: E402
from reflecting_encounter import state_index  # noqa: E402
from reflecting_encounter import transient_indices  # noqa: E402


DATA_DIR = REPORT_DIR / "data"
OUTPUTS_DIR = REPORT_DIR / "outputs"
NOTES_DIR = REPORT_DIR / "notes"


@dataclass(frozen=True)
class ComparisonCase:
    case_id: str
    L: int
    x1_0: int
    x2_0: int
    q0: float
    rho: float


@dataclass(frozen=True)
class FormulaComparison:
    case: ComparisonCase
    Q1: float
    Q2: float
    z: complex
    absorbing_channels: np.ndarray
    green_channels: np.ndarray

    @property
    def absorbing_total(self) -> complex:
        return complex(np.sum(self.absorbing_channels))

    @property
    def green_total(self) -> complex:
        return complex(np.sum(self.green_channels))

    @property
    def abs_error(self) -> float:
        return float(abs(self.absorbing_total - self.green_total))

    @property
    def rel_error(self) -> float:
        return float(self.abs_error / (1.0 + abs(self.green_total)))

    @property
    def max_channel_abs_error(self) -> float:
        return float(np.max(np.abs(self.absorbing_channels - self.green_channels)))


CASES = (
    ComparisonCase("L5_edge_to_edge_rho2", L=5, x1_0=0, x2_0=4, q0=0.35, rho=2.0),
    ComparisonCase("L7_inner_pair_rho1", L=7, x1_0=1, x2_0=5, q0=0.35, rho=1.0),
)

Z_VALUES = (0.10 + 0.00j, 0.40 + 0.00j, 0.75 + 0.00j, 0.50 + 0.20j)


def ensure_dirs() -> None:
    for path in (DATA_DIR, OUTPUTS_DIR, NOTES_DIR):
        path.mkdir(parents=True, exist_ok=True)


def absorbing_chain_channels(P: np.ndarray, L: int, x1_0: int, x2_0: int, z: complex) -> np.ndarray:
    """Return channel PGFs using z alpha (I - z M)^(-1) R."""

    transient = transient_indices(L)
    targets = diagonal_indices(L)
    start = state_index(L, x1_0, x2_0)
    start_matches = np.where(transient == start)[0]
    if start_matches.size != 1:
        raise ValueError("start state must be transient and appear once")

    M = P[np.ix_(transient, transient)]
    R = P[np.ix_(transient, targets)]
    alpha = np.zeros(M.shape[0], dtype=complex)
    alpha[int(start_matches[0])] = 1.0
    row = np.linalg.solve((np.eye(M.shape[0], dtype=complex) - z * M).T, alpha).T
    return z * row @ R


def green_renewal_channels(P: np.ndarray, L: int, x1_0: int, x2_0: int, z: complex) -> np.ndarray:
    """Return target-channel PGFs from the multi-target Green renewal equation.

    With row-stochastic convention and target set E, the unabsorbed Green
    function G(z)=(I-zP)^(-1) satisfies G[start,E] = F[start,E] G[E,E].
    """

    targets = diagonal_indices(L)
    start = state_index(L, x1_0, x2_0)
    if start in set(int(idx) for idx in targets):
        raise ValueError("start state must not be an encounter state")

    G = np.linalg.inv(np.eye(P.shape[0], dtype=complex) - z * P)
    start_to_targets = G[start, targets]
    target_to_targets = G[np.ix_(targets, targets)]
    return np.linalg.solve(target_to_targets.T, start_to_targets.T).T


def compare_case(case: ComparisonCase, z: complex) -> FormulaComparison:
    Q1, Q2 = fixed_total_mobility(case.q0, case.rho)
    P1 = build_reflecting_lazy_transition(case.L, Q1)
    P2 = build_reflecting_lazy_transition(case.L, Q2)
    P = build_joint_transition(P1, P2)
    absorbing = absorbing_chain_channels(P, case.L, case.x1_0, case.x2_0, z)
    green = green_renewal_channels(P, case.L, case.x1_0, case.x2_0, z)
    return FormulaComparison(case=case, Q1=Q1, Q2=Q2, z=z, absorbing_channels=absorbing, green_channels=green)


def iter_comparisons(cases: Iterable[ComparisonCase] = CASES, z_values: Iterable[complex] = Z_VALUES) -> list[FormulaComparison]:
    return [compare_case(case, z) for case in cases for z in z_values]


def _complex_dict(prefix: str, value: complex) -> dict[str, float]:
    return {f"{prefix}_re": float(np.real(value)), f"{prefix}_im": float(np.imag(value))}


def rows_from_results(results: list[FormulaComparison]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for result in results:
        case = result.case
        row: dict[str, object] = {
            "case_id": case.case_id,
            "L": case.L,
            "x1_0": case.x1_0,
            "x2_0": case.x2_0,
            "q0": case.q0,
            "rho": case.rho,
            "Q1": result.Q1,
            "Q2": result.Q2,
            "z_re": float(np.real(result.z)),
            "z_im": float(np.imag(result.z)),
            "abs_error": result.abs_error,
            "rel_error": result.rel_error,
            "max_channel_abs_error": result.max_channel_abs_error,
        }
        row.update(_complex_dict("absorbing_total", result.absorbing_total))
        row.update(_complex_dict("green_total", result.green_total))
        rows.append(row)
    return rows


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    fields = [
        "case_id",
        "L",
        "x1_0",
        "x2_0",
        "q0",
        "rho",
        "Q1",
        "Q2",
        "z_re",
        "z_im",
        "absorbing_total_re",
        "absorbing_total_im",
        "green_total_re",
        "green_total_im",
        "abs_error",
        "rel_error",
        "max_channel_abs_error",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _format_value(row[key]) for key in fields})


def _format_value(value: object) -> object:
    if isinstance(value, float):
        return f"{value:.16e}"
    return value


def write_note(path: Path, rows: list[dict[str, object]], summary: dict[str, object]) -> None:
    max_abs = float(summary["max_abs_error"])
    max_channel = float(summary["max_channel_abs_error"])
    lines = [
        "# Encounter Green Formula Comparison",
        "",
        "## Literature Formula and Conventions",
        "",
        "The comparison uses the finite-state Green/renewal identity behind the",
        "multi-target first-passage formalism.  For an unabsorbed row-stochastic",
        "transition matrix `P` and target set `E`,",
        "",
        "```text",
        "G(z) = (I - z P)^(-1)",
        "G[start, E] = F[start, E](z) G[E, E]",
        "F[start, E](z) = G[start, E] G[E, E]^(-1)",
        "F_E(z) = sum_{e in E} F[start, e](z).",
        "```",
        "",
        "This is the multi-target version of the single-target renewal ratio",
        "`F_{a->b}(z)=G[a,b](z)/G[b,b](z)`.  The determinant expressions in the",
        "literature are algebraically equivalent to solving this target-target",
        "linear system for the fully absorbing case.",
        "",
        "Convention match used in this numerical comparison:",
        "",
        "- Boundary: reflecting finite interval with attempted-outside-stays.",
        "- Update: discrete-time synchronous product chain for two independent walkers.",
        "- Laziness: walker `i` has stay probability `1-Q_i` in the interior, plus reflected attempted moves at endpoints.",
        "- Encounter/targets: `E={(k,k): 0<=k<L}` in the joint state space.",
        "- Mobility: `Q1=2*q0*rho/(1+rho)` and `Q2=2*q0/(1+rho)`.",
        "",
        "The published periodic/resetting first-transmission example is not claimed",
        "to be identical to this report's reflecting fixed-total-mobility scan. The",
        "equality claim here is only for the general Green/renewal formula evaluated",
        "with the same unabsorbed reflecting lazy product propagator used by this",
        "codebase.",
        "",
        "## Absorbing-Chain Formula",
        "",
        "Let `M=P[T,T]` be the transient-transient block, `R=P[T,E]` the",
        "transient-to-encounter block, and `alpha` the row vector concentrated at",
        "the non-diagonal start. The existing absorbing-chain generating function is",
        "",
        "```text",
        "F_E(z) = z alpha (I - z M)^(-1) R 1.",
        "```",
        "",
        "The channel-resolved absorbing formula is `z alpha (I-zM)^(-1) R`; summing",
        "over diagonal targets gives the total encounter generating function.",
        "",
        "## Numerical Result",
        "",
        f"- Cases: {summary['case_count']}",
        f"- z values per case: {summary['z_count']}",
        f"- max total absolute error: {max_abs:.3e}",
        f"- max channel absolute error: {max_channel:.3e}",
        "- Output CSV: `data/green_formula_comparison.csv`",
        "- Output JSON: `outputs/green_formula_comparison_summary.json`",
        "",
        "| case_id | z | abs_error | max_channel_abs_error |",
        "|---|---:|---:|---:|",
    ]
    for row in rows:
        z = complex(float(row["z_re"]), float(row["z_im"]))
        z_label = f"{z.real:g}" if abs(z.imag) < 1e-15 else f"{z.real:g}{z.imag:+g}i"
        lines.append(
            f"| {row['case_id']} | {z_label} | {float(row['abs_error']):.3e} | "
            f"{float(row['max_channel_abs_error']):.3e} |"
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- This is a small `L=5`/`L=7` z-domain check, not a large scan.",
            "- It validates exact formula equivalence only under the matched conventions above.",
            "- It does not claim equality to closed forms whose published examples assume periodic boundaries, resetting, partial transmission, or different mobility definitions.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    results = iter_comparisons()
    rows = rows_from_results(results)
    summary = {
        "formula": "multi-target Green renewal",
        "absorbing_formula": "F_E(z)=z alpha (I-zM)^(-1) R 1",
        "case_count": len(CASES),
        "z_count": len(Z_VALUES),
        "max_abs_error": max(float(row["abs_error"]) for row in rows),
        "max_rel_error": max(float(row["rel_error"]) for row in rows),
        "max_channel_abs_error": max(float(row["max_channel_abs_error"]) for row in rows),
        "comparison_csv": "data/green_formula_comparison.csv",
        "theory_note": "notes/green_formula_comparison.md",
        "conventions": {
            "boundary": "reflecting attempted-outside-stays on {0,...,L-1}",
            "update": "synchronous independent product-chain update",
            "lazy": "interior stay probability 1-Q_i",
            "targets": "encounter diagonal E={(k,k)}",
            "mobility": "Q1=2*q0*rho/(1+rho), Q2=2*q0/(1+rho)",
        },
        "limitations": [
            "does not compare to periodic/resetting examples unless their P is substituted",
            "does not modify main propagation code",
        ],
    }
    write_csv(rows, DATA_DIR / "green_formula_comparison.csv")
    (OUTPUTS_DIR / "green_formula_comparison_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_note(NOTES_DIR / "green_formula_comparison.md", rows, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
