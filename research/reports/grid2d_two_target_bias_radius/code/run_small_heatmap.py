#!/usr/bin/env python3
"""Run a bounded 2D two-target bias-radius heatmap scan."""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

REPO_ROOT = Path(__file__).resolve().parents[4]
VKCORE_SRC = REPO_ROOT / "packages" / "vkcore" / "src"
if str(VKCORE_SRC) not in sys.path:
    sys.path.insert(0, str(VKCORE_SRC))

import matplotlib.pyplot as plt
import numpy as np

from vkcore.grid2d.two_target_bias_radius import (
    ChannelDecomposition,
    NearTargetCandidate,
    TransitionKernel,
    build_reflecting_kernel,
    exact_near_far_decomposition,
    near_target_candidates,
    validation_errors,
)
from vkcore.peaks import classify_distribution_shape

REPORT_DIR = Path(__file__).resolve().parents[1]
FIGURE_DIR = REPORT_DIR / "artifacts" / "figures"
DATA_DIR = REPORT_DIR / "artifacts" / "data"
OUTPUT_DIR = REPORT_DIR / "artifacts" / "outputs"
TABLE_DIR = REPORT_DIR / "artifacts" / "tables"

ROW_ERR_MAX = 1e-12
MASS_ERR_MAX = 1e-10
DECOMP_ERR_MAX = 1e-10


@dataclass(frozen=True)
class ScanCase:
    case_id: str
    Lx: int
    Ly: int
    q: float
    bias_strength: float
    bias_direction: str
    start: tuple[int, int]
    far_target: tuple[int, int]
    near: NearTargetCandidate
    t_max: int


@dataclass(frozen=True)
class CaseResult:
    case: ScanCase
    kernel: TransitionKernel
    decomp: ChannelDecomposition
    errors: dict[str, float]
    classification: str
    metrics: dict[str, float | int | None]

    @property
    def score(self) -> float:
        return float(self.metrics.get("score") or 0.0)


def _ensure_dirs() -> None:
    for path in (FIGURE_DIR, DATA_DIR, OUTPUT_DIR, TABLE_DIR):
        path.mkdir(parents=True, exist_ok=True)


def _build_cases() -> list[ScanCase]:
    Lx = 15
    Ly = 9
    q = 0.70
    bias_direction = "E"
    theta = 0.0
    start = (2, 4)
    far_target = (12, 4)
    radii = [2.0, 3.0, 4.0, 5.0]
    b_values = [0.00, 0.04, 0.08, 0.12, 0.16]
    t_max = 180

    candidates = near_target_candidates(
        Lx=Lx,
        Ly=Ly,
        start=start,
        radii=radii,
        thetas=[theta],
        bias_direction=bias_direction,
        exclude=[far_target],
    )
    by_radius = {round(c.r_requested, 12): c for c in candidates}

    cases: list[ScanCase] = []
    for r in radii:
        near = by_radius.get(round(r, 12))
        if near is None:
            raise RuntimeError(f"missing theta=0 near-target candidate for r={r}")
        for b in b_values:
            cases.append(
                ScanCase(
                    case_id=f"theta0_r{int(r):02d}_b{int(round(100 * b)):03d}",
                    Lx=Lx,
                    Ly=Ly,
                    q=q,
                    bias_strength=b,
                    bias_direction=bias_direction,
                    start=start,
                    far_target=far_target,
                    near=near,
                    t_max=t_max,
                )
            )
    return cases


def _run_case(case: ScanCase) -> CaseResult:
    kernel = build_reflecting_kernel(
        Lx=case.Lx,
        Ly=case.Ly,
        q=case.q,
        bias_strength=case.bias_strength,
        bias_direction=case.bias_direction,
        absorbing=[case.near.coord, case.far_target],
    )
    decomp = exact_near_far_decomposition(
        kernel=kernel,
        start=case.start,
        near_target=case.near.coord,
        far_target=case.far_target,
        t_max=case.t_max,
    )
    errors = validation_errors(kernel, decomp)
    if errors["nonnegative_min_probability"] < -1e-15:
        raise AssertionError(f"{case.case_id}: negative transition probability: {errors}")
    if errors["row_stochasticity_error"] >= ROW_ERR_MAX:
        raise AssertionError(f"{case.case_id}: row-stochasticity failed: {errors}")
    if errors["mass_balance_error"] >= MASS_ERR_MAX:
        raise AssertionError(f"{case.case_id}: mass balance failed: {errors}")
    if errors["decomposition_error"] >= DECOMP_ERR_MAX:
        raise AssertionError(f"{case.case_id}: near/far decomposition failed: {errors}")

    shape = classify_distribution_shape(decomp.f_total)
    return CaseResult(
        case=case,
        kernel=kernel,
        decomp=decomp,
        errors=errors,
        classification=shape.classification,
        metrics=shape.metrics,
    )


def _metric_value(metrics: dict[str, float | int | None], key: str) -> str:
    value = metrics.get(key)
    if value is None:
        return ""
    if isinstance(value, int):
        return str(value)
    return f"{float(value):.17g}"


def _write_config_csv(cases: list[ScanCase]) -> Path:
    path = DATA_DIR / "grid2d_bias_radius_scan_config.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "case_id",
                "Lx",
                "Ly",
                "q",
                "bias_strength_b",
                "bias_direction",
                "theta_requested",
                "start_x",
                "start_y",
                "near_x",
                "near_y",
                "far_x",
                "far_y",
                "r_requested",
                "r_actual",
                "theta_actual",
                "t_max",
                "boundary_rule",
                "bias_rule",
            ]
        )
        for case in cases:
            writer.writerow(
                [
                    case.case_id,
                    case.Lx,
                    case.Ly,
                    f"{case.q:.17g}",
                    f"{case.bias_strength:.17g}",
                    case.bias_direction,
                    f"{case.near.theta_requested:.17g}",
                    case.start[0],
                    case.start[1],
                    case.near.coord[0],
                    case.near.coord[1],
                    case.far_target[0],
                    case.far_target[1],
                    f"{case.near.r_requested:.17g}",
                    f"{case.near.r_actual:.17g}",
                    f"{case.near.theta_actual:.17g}",
                    case.t_max,
                    "reflecting attempted-outside-stays",
                    "global absolute stay-to-direction shift: p_dir=q/4+b, p_stay=1-q-b",
                ]
            )
    return path


def _write_metrics_csv(results: list[CaseResult]) -> Path:
    path = DATA_DIR / "grid2d_bias_radius_scan_metrics.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "case_id",
                "bias_strength_b",
                "r_requested",
                "r_actual",
                "theta_actual",
                "classification",
                "t1",
                "t2",
                "tv",
                "R_peak",
                "R_valley",
                "score",
                "p_absorbed",
                "p_near",
                "p_far",
                "survival_tail",
                "row_stochasticity_error",
                "nonnegative_min_probability",
                "mass_balance_error",
                "decomposition_error",
            ]
        )
        for result in results:
            decomp = result.decomp
            writer.writerow(
                [
                    result.case.case_id,
                    f"{result.case.bias_strength:.17g}",
                    f"{result.case.near.r_requested:.17g}",
                    f"{result.case.near.r_actual:.17g}",
                    f"{result.case.near.theta_actual:.17g}",
                    result.classification,
                    _metric_value(result.metrics, "t1"),
                    _metric_value(result.metrics, "t2"),
                    _metric_value(result.metrics, "tv"),
                    _metric_value(result.metrics, "R_peak"),
                    _metric_value(result.metrics, "R_valley"),
                    _metric_value(result.metrics, "score"),
                    f"{float(np.sum(decomp.f_total)):.17g}",
                    f"{float(np.sum(decomp.f_near)):.17g}",
                    f"{float(np.sum(decomp.f_far)):.17g}",
                    f"{float(decomp.survival[-1]):.17g}",
                    f"{result.errors['row_stochasticity_error']:.17g}",
                    f"{result.errors['nonnegative_min_probability']:.17g}",
                    f"{result.errors['mass_balance_error']:.17g}",
                    f"{result.errors['decomposition_error']:.17g}",
                ]
            )
    return path


def _write_candidate_table(results: list[CaseResult]) -> Path:
    path = TABLE_DIR / "grid2d_double_peak_candidates.csv"
    candidates = [r for r in results if r.classification == "double_peak"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["case_id", "b", "r", "theta", "t1", "t2", "tv", "R_peak", "R_valley", "score"])
        for result in sorted(candidates, key=lambda item: item.score, reverse=True):
            writer.writerow(
                [
                    result.case.case_id,
                    f"{result.case.bias_strength:.17g}",
                    f"{result.case.near.r_actual:.17g}",
                    f"{result.case.near.theta_actual:.17g}",
                    _metric_value(result.metrics, "t1"),
                    _metric_value(result.metrics, "t2"),
                    _metric_value(result.metrics, "tv"),
                    _metric_value(result.metrics, "R_peak"),
                    _metric_value(result.metrics, "R_valley"),
                    _metric_value(result.metrics, "score"),
                ]
            )
    return path


def _plot_heatmap(results: list[CaseResult]) -> Path:
    b_values = sorted({r.case.bias_strength for r in results})
    r_values = sorted({r.case.near.r_actual for r in results})
    score = np.full((len(r_values), len(b_values)), np.nan, dtype=np.float64)
    label_by_case = {(r.case.near.r_actual, r.case.bias_strength): r for r in results}
    for iy, rv in enumerate(r_values):
        for ix, bv in enumerate(b_values):
            score[iy, ix] = label_by_case[(rv, bv)].score

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    max_score = float(np.nanmax(score))
    im = ax.imshow(score, origin="lower", aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(b_values)), [f"{b:.2f}" for b in b_values])
    ax.set_yticks(range(len(r_values)), [f"{r:.0f}" for r in r_values])
    ax.set_xlabel("bias strength b")
    ax.set_ylabel("near-target distance r (theta=0)")
    ax.set_title("Grid2D bias-radius scan: distribution-shape score", fontsize=12)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("classifier score = separation * R_peak / max(R_valley, 1e-12)")

    for iy, rv in enumerate(r_values):
        for ix, bv in enumerate(b_values):
            result = label_by_case[(rv, bv)]
            marker = "D" if result.classification == "double_peak" else ""
            norm_score = result.score / max(max_score, 1e-12)
            ax.text(
                ix,
                iy,
                marker or f"{result.score:.1f}",
                ha="center",
                va="center",
                color="black" if norm_score > 0.72 else "white",
                fontsize=8,
            )

    fig.tight_layout()
    path = FIGURE_DIR / "grid2d_bias_radius_heatmap_theta0.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def _representatives(results: list[CaseResult]) -> list[CaseResult]:
    ordered = sorted(results, key=lambda item: (item.classification == "double_peak", item.score), reverse=True)
    picked: list[CaseResult] = []
    seen: set[str] = set()
    for result in ordered:
        if result.case.case_id in seen:
            continue
        picked.append(result)
        seen.add(result.case.case_id)
        if len(picked) >= 3:
            break
    return picked


def _plot_decomposition(result: CaseResult) -> Path:
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    decomp = result.decomp
    ax.plot(decomp.t, decomp.f_total, color="#111111", lw=2.0, label="total")
    ax.plot(decomp.t, decomp.f_near, color="#1f77b4", lw=1.8, label="near channel")
    ax.plot(decomp.t, decomp.f_far, color="#d95f02", lw=1.8, label="far channel")
    ax.set_xlabel("time step t")
    ax.set_ylabel("first-passage probability")
    ax.set_title(
        (
            f"{result.case.case_id}: {result.classification}, score={result.score:.3g}; "
            f"b={result.case.bias_strength:.2f}, r={result.case.near.r_actual:.0f}, theta=0"
        ),
        fontsize=10,
    )
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    text = (
        f"x0={result.case.start}, near={result.case.near.coord}, far={result.case.far_target}\n"
        f"p_near={np.sum(decomp.f_near):.3f}, p_far={np.sum(decomp.f_far):.3f}, tail={decomp.survival[-1]:.1e}"
    )
    ax.text(
        0.98,
        0.96,
        text,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#cccccc", "alpha": 0.9},
    )
    fig.tight_layout()
    path = FIGURE_DIR / f"grid2d_representative_fpt_decomp_{result.case.case_id}.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def _write_summary(
    *,
    results: list[CaseResult],
    config_path: Path,
    metrics_path: Path,
    heatmap_path: Path,
    representative_paths: list[Path],
    candidate_path: Path,
) -> Path:
    max_row = max(r.errors["row_stochasticity_error"] for r in results)
    min_prob = min(r.errors["nonnegative_min_probability"] for r in results)
    max_mass = max(r.errors["mass_balance_error"] for r in results)
    max_decomp = max(r.errors["decomposition_error"] for r in results)
    n_double = sum(1 for r in results if r.classification == "double_peak")
    top = max(results, key=lambda r: r.score)

    lines = [
        "# Grid2D Bias-Radius Small Heatmap Summary",
        "",
        "This bounded scan fixes `theta=0`, so near targets lie along the global eastward bias direction. The heatmap should not be read as evidence that distance alone explains the distribution shape; it is a fixed-angle slice over `(b, r)`.",
        "",
        "## Heatmap Meaning",
        "",
        "The heatmap color is the conservative distribution-shape classifier score `peak_separation * R_peak / max(R_valley, 1e-12)` computed from `f_total(t)`. A higher score indicates a stronger candidate two-peak separation by that metric, but a case is only called `double_peak` when the classifier label is exactly `double_peak`.",
        "",
        "## Fixed Setup",
        "",
        f"- Grid: `{top.case.Lx} x {top.case.Ly}`",
        f"- Start: `{top.case.start}`",
        f"- Far target: `{top.case.far_target}`",
        f"- Bias direction: `{top.case.bias_direction}`",
        "- Boundary: reflecting attempted-outside-stays",
        "- Bias rule: global absolute stay-to-direction shift `p_dir=q/4+b`, `p_stay=1-q-b`",
        "- Theta handling: fixed `theta=0`; no aggregation over theta",
        "",
        "## Validation",
        "",
        f"- cases: `{len(results)}`",
        f"- double_peak-labeled cases: `{n_double}`",
        f"- minimum transition probability: `{min_prob:.17g}`",
        f"- max row-stochasticity error: `{max_row:.17g}`",
        f"- max mass-balance error: `{max_mass:.17g}`",
        f"- max near/far decomposition error: `{max_decomp:.17g}`",
        "",
        "## Outputs",
        "",
        f"- config: `{config_path.relative_to(REPORT_DIR)}`",
        f"- metrics: `{metrics_path.relative_to(REPORT_DIR)}`",
        f"- heatmap: `{heatmap_path.relative_to(REPORT_DIR)}`",
        f"- double-peak candidate table: `{candidate_path.relative_to(REPORT_DIR)}`",
    ]
    for path in representative_paths:
        lines.append(f"- representative decomposition: `{path.relative_to(REPORT_DIR)}`")

    path = REPORT_DIR / "SUMMARY.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    _ensure_dirs()
    cases = _build_cases()
    results = [_run_case(case) for case in cases]

    config_path = _write_config_csv(cases)
    metrics_path = _write_metrics_csv(results)
    candidate_path = _write_candidate_table(results)
    heatmap_path = _plot_heatmap(results)
    representative_paths = [_plot_decomposition(result) for result in _representatives(results)]
    summary_path = _write_summary(
        results=results,
        config_path=config_path,
        metrics_path=metrics_path,
        heatmap_path=heatmap_path,
        representative_paths=representative_paths,
        candidate_path=candidate_path,
    )

    validation: dict[str, Any] = {
        "cases": len(results),
        "max_row_stochasticity_error": max(r.errors["row_stochasticity_error"] for r in results),
        "min_probability": min(r.errors["nonnegative_min_probability"] for r in results),
        "max_mass_balance_error": max(r.errors["mass_balance_error"] for r in results),
        "max_decomposition_error": max(r.errors["decomposition_error"] for r in results),
        "double_peak_cases": sum(1 for r in results if r.classification == "double_peak"),
        "heatmap": str(heatmap_path.relative_to(REPO_ROOT)),
        "metrics": str(metrics_path.relative_to(REPO_ROOT)),
        "summary": str(summary_path.relative_to(REPO_ROOT)),
    }
    (DATA_DIR / "grid2d_bias_radius_scan_summary.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, sort_keys=True))


if __name__ == "__main__":
    main()
