#!/usr/bin/env python3
"""Bounded mobility-ratio scan for reflecting two-walker encounters."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REPORT_DIR = Path(__file__).resolve().parents[1]
ROOT = REPORT_DIR.parents[2]
MEAN_VALIDATION_CODE = ROOT / "research" / "reports" / "encounter_reflecting_mean_validation" / "code"
VKCORE_SRC = ROOT / "packages" / "vkcore" / "src"
for path in (MEAN_VALIDATION_CODE, VKCORE_SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from reflecting_encounter import EncounterCase  # noqa: E402
from reflecting_encounter import DiagonalDecompositionResult  # noqa: E402
from reflecting_encounter import assert_diagonal_thresholds  # noqa: E402
from reflecting_encounter import validate_diagonal_case  # noqa: E402
from vkcore.peaks import classify_distribution_shape  # noqa: E402


DATA_DIR = REPORT_DIR / "data"
OUTPUTS_DIR = REPORT_DIR / "outputs"
FIGURES_DIR = REPORT_DIR / "figures"
TABLES_DIR = REPORT_DIR / "tables"

RHO_VALUES = (0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0)
L = 7
Q0 = 0.35
INITIAL_PAIRS = ((0, L - 1), (L - 1, 0), (1, 5), (5, 1))
WINDOW_RADIUS = 3


@dataclass(frozen=True)
class ScanCase:
    case_id: str
    L: int
    x1_0: int
    x2_0: int
    q0: float
    rho: float

    def encounter_case(self) -> EncounterCase:
        return EncounterCase(L=self.L, x1_0=self.x1_0, x2_0=self.x2_0, q0=self.q0, rho=self.rho)


def ensure_dirs() -> None:
    for path in (DATA_DIR, OUTPUTS_DIR, FIGURES_DIR, TABLES_DIR):
        path.mkdir(parents=True, exist_ok=True)


def iter_scan_cases() -> list[ScanCase]:
    cases: list[ScanCase] = []
    for pair_idx, (x1, x2) in enumerate(INITIAL_PAIRS):
        for rho in RHO_VALUES:
            rho_label = str(rho).replace(".", "p")
            cases.append(
                ScanCase(
                    case_id=f"p{pair_idx:02d}_rho{rho_label}",
                    L=L,
                    x1_0=x1,
                    x2_0=x2,
                    q0=Q0,
                    rho=float(rho),
                )
            )
    return cases


def write_config_csv(cases: Iterable[ScanCase], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["case_id", "L", "x1_0", "x2_0", "q0", "rho"])
        writer.writeheader()
        for case in cases:
            writer.writerow(
                {
                    "case_id": case.case_id,
                    "L": case.L,
                    "x1_0": case.x1_0,
                    "x2_0": case.x2_0,
                    "q0": case.q0,
                    "rho": case.rho,
                }
            )


def contribution_window(result: DiagonalDecompositionResult, center_t: int | None) -> np.ndarray:
    if center_t is None:
        return np.zeros(result.case.L, dtype=float)
    matches = np.where(result.times == int(center_t))[0]
    if matches.size == 0:
        return np.zeros(result.case.L, dtype=float)
    center_idx = int(matches[0])
    lo = max(0, center_idx - WINDOW_RADIUS)
    hi = min(result.times.size - 1, center_idx + WINDOW_RADIUS)
    return np.sum(result.f_by_position[lo : hi + 1, :], axis=0)


def dominant_positions(values: np.ndarray, *, n: int = 3) -> str:
    if values.size == 0 or float(np.sum(values)) <= 0.0:
        return ""
    order = np.argsort(values)[::-1]
    return ";".join(f"{int(k)}:{float(values[k]):.6e}" for k in order[:n] if values[k] > 0.0)


def write_case_outputs(case_id: str, result: DiagonalDecompositionResult) -> tuple[Path, Path]:
    total_path = OUTPUTS_DIR / f"case_{case_id}_f_total.csv"
    diag_path = OUTPUTS_DIR / f"case_{case_id}_diag_contrib.csv"

    with total_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["t", "f_total", "survival_before", "survival_after"])
        writer.writeheader()
        for i, t in enumerate(result.times):
            writer.writerow(
                {
                    "t": int(t),
                    "f_total": f"{result.f_total[i]:.16e}",
                    "survival_before": f"{result.survival[i]:.16e}",
                    "survival_after": f"{result.survival[i + 1]:.16e}",
                }
            )

    with diag_path.open("w", newline="", encoding="utf-8") as fh:
        fields = ["t", "f_total", *[f"k_{k}" for k in range(result.case.L)]]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for i, t in enumerate(result.times):
            row = {"t": int(t), "f_total": f"{result.f_total[i]:.16e}"}
            row.update({f"k_{k}": f"{result.f_by_position[i, k]:.16e}" for k in range(result.case.L)})
            writer.writerow(row)

    return total_path, diag_path


def plot_fpt_by_ratio(rows: list[dict[str, object]], results: dict[str, DiagonalDecompositionResult], path: Path) -> None:
    pairs = list(dict.fromkeys((int(row["x1_0"]), int(row["x2_0"])) for row in rows))
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.8), sharex=False, sharey=False, constrained_layout=True)
    cmap = plt.get_cmap("viridis")
    rho_min = min(RHO_VALUES)
    rho_max = max(RHO_VALUES)

    for ax, pair in zip(axes.ravel(), pairs, strict=True):
        pair_rows = [row for row in rows if (int(row["x1_0"]), int(row["x2_0"])) == pair]
        for row in pair_rows:
            result = results[str(row["case_id"])]
            z = (np.log10(float(row["rho"])) - np.log10(rho_min)) / (np.log10(rho_max) - np.log10(rho_min))
            ax.plot(
                result.times,
                result.f_total,
                lw=1.35,
                color=cmap(z),
                label=f"rho={float(row['rho']):g}, {row['classification']}",
            )
        ax.set_title(f"start={pair}")
        ax.set_xlabel("time t")
        ax.set_ylabel("f_E(t)")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=7, loc="upper right")

    fig.suptitle("Reflecting encounter FPT by mobility ratio")
    fig.savefig(path)
    plt.close(fig)


def plot_heatmap(case_id: str, result: DiagonalDecompositionResult, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 3.8), constrained_layout=True)
    mesh = ax.imshow(
        result.f_by_position.T,
        origin="lower",
        aspect="auto",
        interpolation="nearest",
        extent=[float(result.times[0]), float(result.times[-1]), -0.5, result.case.L - 0.5],
        cmap="magma",
    )
    ax.set_xlabel("time t")
    ax.set_ylabel("encounter position k")
    ax.set_title(
        f"{case_id}: start=({result.case.x1_0},{result.case.x2_0}), rho={result.case.rho:g}"
    )
    ax.set_yticks(range(result.case.L))
    fig.colorbar(mesh, ax=ax, label="f_k(t)")
    fig.savefig(path)
    plt.close(fig)


def metrics_row(case: ScanCase, result: DiagonalDecompositionResult) -> dict[str, object]:
    classification = classify_distribution_shape(result.f_total)
    m = classification.metrics
    t1 = None if m["t1"] is None else int(m["t1"])
    t2 = None if m["t2"] is None else int(m["t2"])
    tv = None if m["tv"] is None else int(m["tv"])

    early_window = contribution_window(result, t1)
    late_window = contribution_window(result, t2)
    return {
        "case_id": case.case_id,
        "L": case.L,
        "x1_0": case.x1_0,
        "x2_0": case.x2_0,
        "q0": case.q0,
        "rho": case.rho,
        "Q1": result.Q1,
        "Q2": result.Q2,
        "mean_distribution": result.mean,
        "mass_balance_error": result.mass_balance_error,
        "diagonal_decomposition_error": result.decomposition_error,
        "tail_mass": result.tail_mass,
        "classification": classification.classification,
        "t1": "" if t1 is None else t1,
        "t2": "" if t2 is None else t2,
        "tv": "" if tv is None else tv,
        "R_peak": m["R_peak"],
        "R_valley": m["R_valley"],
        "peak_separation": m["peak_separation"],
        "score": m["score"],
        "candidate_peaks": ";".join(str(p) for p in classification.candidate_peaks),
        "dominant_early_positions": dominant_positions(early_window),
        "dominant_late_positions": dominant_positions(late_window),
    }


def write_metrics_csv(rows: list[dict[str, object]], path: Path) -> None:
    fields = [
        "case_id",
        "L",
        "x1_0",
        "x2_0",
        "q0",
        "rho",
        "Q1",
        "Q2",
        "mean_distribution",
        "mass_balance_error",
        "diagonal_decomposition_error",
        "tail_mass",
        "classification",
        "t1",
        "t2",
        "tv",
        "R_peak",
        "R_valley",
        "peak_separation",
        "score",
        "candidate_peaks",
        "dominant_early_positions",
        "dominant_late_positions",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            formatted = dict(row)
            for key in (
                "q0",
                "rho",
                "Q1",
                "Q2",
                "mean_distribution",
                "mass_balance_error",
                "diagonal_decomposition_error",
                "tail_mass",
                "R_peak",
                "R_valley",
                "score",
            ):
                formatted[key] = f"{float(row[key]):.16e}"
            writer.writerow(formatted)


def write_summary(rows: list[dict[str, object]], path: Path, summary_json: dict[str, object]) -> None:
    by_rho: dict[float, Counter[str]] = defaultdict(Counter)
    by_pair: dict[tuple[int, int], Counter[str]] = defaultdict(Counter)
    for row in rows:
        by_rho[float(row["rho"])][str(row["classification"])] += 1
        by_pair[(int(row["x1_0"]), int(row["x2_0"]))][str(row["classification"])] += 1

    lines = [
        "# Reflecting Encounter Diagonal Decomposition Ratio Scan",
        "",
        "This bounded scan uses the fixed-total-mobility convention",
        "`Q1 = 2*q0*rho/(1+rho)` and `Q2 = 2*q0/(1+rho)`.",
        "",
        "Each case records the full encounter distribution `f_E(t)`, the",
        "diagonal-position contributions `f_k(t)`, survival, distribution mean,",
        "mass-balance error, and shape classification from `vkcore.peaks`.",
        "",
        "Scientific guardrail: a curve is called `double_peak` only when the",
        "shared classifier returns `double_peak`. Otherwise the reported labels",
        "are `unimodal`, `shoulder`, or `local_bump`.",
        "",
        "## Validation",
        "",
        f"- cases: {summary_json['cases']}",
        f"- max mass-balance error: {summary_json['max_mass_balance_error']:.3e}",
        f"- max diagonal decomposition error: {summary_json['max_diagonal_decomposition_error']:.3e}",
        "",
        "## Shape Classes by rho",
        "",
        "| rho | classes |",
        "|---:|---|",
    ]
    for rho in RHO_VALUES:
        counts = by_rho[float(rho)]
        classes = ", ".join(f"{name}: {counts[name]}" for name in sorted(counts))
        lines.append(f"| {rho:g} | {classes} |")

    lines.extend(["", "## Shape Classes by Initial Pair", "", "| start | classes |", "|---|---|"])
    for pair in INITIAL_PAIRS:
        counts = by_pair[pair]
        classes = ", ".join(f"{name}: {counts[name]}" for name in sorted(counts))
        lines.append(f"| {pair} | {classes} |")

    lines.extend(
        [
            "",
            "## Mechanism Pointers",
            "",
            "Dominant early and late position columns in",
            "`data/encounter_ratio_scan_metrics.csv` summarize the largest",
            "diagonal contributions in windows around `t1` and, when present,",
            "`t2`. Mechanism claims should be made from those `f_k(t)` windows",
            "or from the case heatmaps, not from the mean curve alone.",
            "",
            "## Generated Outputs",
            "",
            "- `data/encounter_ratio_scan_config.csv`",
            "- `data/encounter_ratio_scan_metrics.csv`",
            "- `tables/encounter_shape_classification.csv`",
            "- `figures/encounter_fpt_by_ratio.pdf`",
            "- `figures/encounter_diag_contrib_heatmap_case_<id>.pdf`",
            "- `outputs/case_<id>_f_total.csv`",
            "- `outputs/case_<id>_diag_contrib.csv`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    cases = iter_scan_cases()
    write_config_csv(cases, DATA_DIR / "encounter_ratio_scan_config.csv")

    rows: list[dict[str, object]] = []
    results: dict[str, DiagonalDecompositionResult] = {}
    for case in cases:
        result = validate_diagonal_case(case.encounter_case())
        assert_diagonal_thresholds(result)
        write_case_outputs(case.case_id, result)
        plot_heatmap(case.case_id, result, FIGURES_DIR / f"encounter_diag_contrib_heatmap_case_{case.case_id}.pdf")
        row = metrics_row(case, result)
        rows.append(row)
        results[case.case_id] = result

    metrics_path = DATA_DIR / "encounter_ratio_scan_metrics.csv"
    table_path = TABLES_DIR / "encounter_shape_classification.csv"
    write_metrics_csv(rows, metrics_path)
    write_metrics_csv(rows, table_path)
    plot_fpt_by_ratio(rows, results, FIGURES_DIR / "encounter_fpt_by_ratio.pdf")

    max_mass = max(float(row["mass_balance_error"]) for row in rows)
    max_decomp = max(float(row["diagonal_decomposition_error"]) for row in rows)
    if max_mass >= 1e-10:
        raise AssertionError(f"scan mass-balance error {max_mass:.3e} >= 1e-10")
    if max_decomp >= 1e-10:
        raise AssertionError(f"scan diagonal decomposition error {max_decomp:.3e} >= 1e-10")

    summary_json = {
        "cases": len(rows),
        "rho_values": list(RHO_VALUES),
        "initial_pairs": [list(pair) for pair in INITIAL_PAIRS],
        "max_mass_balance_error": max_mass,
        "max_diagonal_decomposition_error": max_decomp,
        "class_counts": dict(Counter(str(row["classification"]) for row in rows)),
        "metrics_csv": "data/encounter_ratio_scan_metrics.csv",
        "classification_table": "tables/encounter_shape_classification.csv",
        "fpt_figure": "figures/encounter_fpt_by_ratio.pdf",
        "heatmap_count": len(rows),
    }
    (REPORT_DIR / "outputs" / "ratio_scan_summary.json").write_text(
        json.dumps(summary_json, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_summary(rows, REPORT_DIR / "SUMMARY.md", summary_json)
    print(json.dumps(summary_json, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
