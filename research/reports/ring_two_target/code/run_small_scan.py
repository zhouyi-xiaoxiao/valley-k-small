#!/usr/bin/env python3
"""Bounded small scan for exact two-target first-passage channel structure."""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from pathlib import Path
import sys
import warnings

import numpy as np


def _ensure_vkcore_on_path() -> None:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "packages" / "vkcore" / "src"
        if candidate.exists():
            sys.path.insert(0, str(candidate))
            return


_ensure_vkcore_on_path()

from vkcore.peaks import PeakClassification, classify_distribution_shape  # noqa: E402
from vkcore.plot_style import apply_research_plot_style  # noqa: E402
from vkcore.ring.two_target import (  # noqa: E402
    RingTwoTargetConfig,
    RingTwoTargetResult,
    exact_two_target_fpt,
    save_decomposition_csv,
    validate_result,
)


SHAPE_ORDER = ("unimodal", "shoulder", "local_bump", "double_peak")


def bounded_configs(max_steps: int, eps_survival: float) -> list[RingTwoTargetConfig]:
    configs: list[RingTwoTargetConfig] = []
    for L in (31, 51):
        target_pairs = [
            (L // 2, L // 2 + 1),
            (L - 2, L // 2),
            (L // 3, 2 * L // 3),
            (L - 1, (L // 2 + 5) % L),
        ]
        for start in (0, 7, 13):
            for target1, target2 in target_pairs:
                if start in {target1, target2}:
                    continue
                for drift in (-0.6, -0.3, 0.0, 0.3, 0.6):
                    for beta in (0.0, 0.03):
                        shortcut_src = None
                        shortcut_dst = None
                        if beta > 0:
                            shortcut_src = (start + 5) % L
                            if shortcut_src in {target1, target2}:
                                shortcut_src = (start + 6) % L
                            shortcut_dst = target2
                        configs.append(
                            RingTwoTargetConfig(
                                L=L,
                                K=2,
                                q=2.0 / 3.0,
                                drift=drift,
                                beta=beta,
                                shortcut_src=shortcut_src,
                                shortcut_dst=shortcut_dst,
                                start=start,
                                target1=target1,
                                target2=target2,
                                max_steps=max_steps,
                                eps_survival=eps_survival,
                            )
                        )
    return configs


def series_metrics(values: np.ndarray, t: np.ndarray) -> dict[str, float | int]:
    mass = float(np.sum(values))
    peak_t = int(t[int(np.argmax(values))]) if values.size else 0
    peak_height = float(np.max(values)) if values.size else 0.0
    mean_t = float(np.sum(t * values) / mass) if mass > 0 else float("nan")
    return {
        "mass": mass,
        "peak_t": peak_t,
        "peak_height": peak_height,
        "mean_t": mean_t,
    }


def dominant_target(m1: float, m2: float, *, tol: float = 1e-14) -> str:
    if abs(m1 - m2) <= tol:
        return "tie"
    return "target1" if m1 > m2 else "target2"


def split_channel_dominance(result: RingTwoTargetResult, classification: PeakClassification) -> dict[str, float | str | int]:
    metrics = classification.metrics
    tv = metrics.get("tv")
    if tv is None:
        split_t = int(result.t[int(np.argmax(result.f_total))])
    else:
        split_t = int(tv)

    early = result.t <= split_t
    late = result.t > split_t
    early1 = float(np.sum(result.f_target1[early]))
    early2 = float(np.sum(result.f_target2[early]))
    late1 = float(np.sum(result.f_target1[late]))
    late2 = float(np.sum(result.f_target2[late]))
    return {
        "split_t": split_t,
        "early_target1_mass": early1,
        "early_target2_mass": early2,
        "late_target1_mass": late1,
        "late_target2_mass": late2,
        "early_dominant_target": dominant_target(early1, early2),
        "late_dominant_target": dominant_target(late1, late2),
    }


def case_id(index: int, cfg: RingTwoTargetConfig, label: str) -> str:
    return (
        f"{index:03d}_{label}_L{cfg.L}_x{cfg.start}_"
        f"a{cfg.target1}_{cfg.target2}_g{cfg.drift:+.1f}_b{cfg.beta:.2f}"
    ).replace("+", "p").replace("-", "m").replace(".", "p")


def row_for_case(
    index: int,
    cfg: RingTwoTargetConfig,
    result: RingTwoTargetResult,
    classification: PeakClassification,
    errors: dict[str, float],
) -> dict[str, object]:
    total_metrics = series_metrics(result.f_total, result.t)
    target1_metrics = series_metrics(result.f_target1, result.t)
    target2_metrics = series_metrics(result.f_target2, result.t)
    shape_metrics = classification.metrics
    dominance = split_channel_dominance(result, classification)
    label = classification.classification

    row: dict[str, object] = {
        "case_id": case_id(index, cfg, label),
        "classification": label,
        "L": cfg.L,
        "K": cfg.K,
        "q": cfg.q,
        "drift": cfg.drift,
        "beta": cfg.beta,
        "start": cfg.start,
        "target1": cfg.target1,
        "target2": cfg.target2,
        "shortcut_src": "" if cfg.shortcut_src is None else cfg.shortcut_src,
        "shortcut_dst": "" if cfg.shortcut_dst is None else cfg.shortcut_dst,
        "steps": int(result.t[-1]),
        "survival_final": float(result.survival[-1]),
        "row_stochasticity_error": errors["row_stochasticity_error"],
        "mass_balance_error": errors["mass_balance_error"],
        "decomposition_error": errors["channel_decomposition_error"],
        "shape_t1": shape_metrics.get("t1"),
        "shape_t2": shape_metrics.get("t2"),
        "shape_tv": shape_metrics.get("tv"),
        "R_peak": shape_metrics.get("R_peak"),
        "R_valley": shape_metrics.get("R_valley"),
        "peak_separation": shape_metrics.get("peak_separation"),
        "shape_score": shape_metrics.get("score"),
        "total_mass": total_metrics["mass"],
        "total_peak_t": total_metrics["peak_t"],
        "total_peak_height": total_metrics["peak_height"],
        "total_mean_t": total_metrics["mean_t"],
        "target1_mass": target1_metrics["mass"],
        "target1_peak_t": target1_metrics["peak_t"],
        "target1_peak_height": target1_metrics["peak_height"],
        "target1_mean_t": target1_metrics["mean_t"],
        "target2_mass": target2_metrics["mass"],
        "target2_peak_t": target2_metrics["peak_t"],
        "target2_peak_height": target2_metrics["peak_height"],
        "target2_mean_t": target2_metrics["mean_t"],
    }
    row.update(dominance)
    return row


def write_metrics_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("no scan rows to write")
    with path.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def representative_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    reps: list[dict[str, object]] = []
    for label in SHAPE_ORDER:
        candidates = [row for row in rows if row["classification"] == label]
        if not candidates:
            continue
        if label == "unimodal":
            chosen = max(candidates, key=lambda row: float(row["total_peak_height"]))
        else:
            chosen = max(candidates, key=lambda row: float(row["shape_score"] or 0.0))
        reps.append(chosen)
    return reps[:5]


def plot_representative(path: Path, result: RingTwoTargetResult, row: dict[str, object]) -> None:
    import matplotlib.pyplot as plt

    apply_research_plot_style()
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    for label, values, color in [
        ("total", result.f_total, "black"),
        ("target1 channel", result.f_target1, "#1f77b4"),
        ("target2 channel", result.f_target2, "#d62728"),
    ]:
        mask = values > 0
        ax.plot(result.t[mask], values[mask], label=label, color=color)

    ax.set_yscale("log")
    ax.set_xlabel("first-passage time t")
    ax.set_ylabel("probability")
    ax.set_title(f"{row['classification']}: {row['case_id']}")
    ax.legend(frameon=False)
    ax.text(
        0.98,
        0.96,
        f"early: {row['early_dominant_target']}, late: {row['late_dominant_target']}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def write_summary(
    path: Path,
    rows: list[dict[str, object]],
    reps: list[dict[str, object]],
    metrics_csv: Path,
    figure_dir: Path,
    case_dir: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = {label: sum(1 for row in rows if row["classification"] == label) for label in SHAPE_ORDER}
    max_mass = max(float(row["mass_balance_error"]) for row in rows)
    max_decomp = max(float(row["decomposition_error"]) for row in rows)
    max_row = max(float(row["row_stochasticity_error"]) for row in rows)

    lines = [
        "# Small Two-Target Ring Scan",
        "",
        "This bounded scan uses exact propagation on a small grid of periodic 1D ring",
        "two-target first-passage problems. Each case was validated for nonnegative",
        "row-stochastic transitions, mass balance, and target-channel decomposition.",
        "",
        "The shape labels come from the shared peak classifier. In particular, a curve is",
        "called `double_peak` only when the classifier returns `double_peak`; weaker",
        "late-time structures remain `shoulder` or `local_bump`.",
        "",
        "## Outputs",
        "",
        f"- Metrics CSV: `{metrics_csv.relative_to(path.parents[2])}`",
        f"- Representative case CSVs: `{case_dir.relative_to(path.parents[2])}/`",
        f"- Representative figures: `{figure_dir.relative_to(path.parents[2])}/`",
        "",
        "## Validation Summary",
        "",
        f"- Scanned cases: {len(rows)}",
        f"- Max row-stochasticity error: {max_row:.3e}",
        f"- Max mass-balance error: {max_mass:.3e}",
        f"- Max target-channel decomposition error: {max_decomp:.3e}",
        "",
        "## Shape Counts",
        "",
    ]
    lines.extend(f"- `{label}`: {counts[label]}" for label in SHAPE_ORDER)
    lines.extend(["", "## Representative Cases", ""])
    lines.append(
        "| classification | case_id | targets | drift | beta | early dominant | late dominant | R_peak | R_valley |"
    )
    lines.append("|---|---|---:|---:|---:|---|---|---:|---:|")
    for row in reps:
        lines.append(
            "| {classification} | `{case_id}` | ({target1},{target2}) | {drift} | {beta} | "
            "{early_dominant_target} | {late_dominant_target} | {R_peak:.3g} | {R_valley:.3g} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation Guardrail",
            "",
            "The scan identifies representative shapes and their target-channel budgets.",
            "A mechanism claim should use the channel evidence in the representative CSVs",
            "and figures. The scan alone should not be used to infer a mechanism without",
            "checking which target channel dominates the early and late portions of the",
            "distribution.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-steps", type=int, default=2500)
    parser.add_argument("--eps-survival", type=float, default=1e-10)
    args = parser.parse_args()

    report_dir = Path(__file__).resolve().parents[1]
    metrics_csv = report_dir / "artifacts" / "data" / "small_scan_metrics.csv"
    case_dir = report_dir / "artifacts" / "outputs" / "small_scan_cases"
    figure_dir = report_dir / "artifacts" / "figures" / "small_scan"
    summary_md = report_dir / "notes" / "small_scan_summary.md"

    rows: list[dict[str, object]] = []
    results_by_case: dict[str, RingTwoTargetResult] = {}
    failures: list[str] = []

    configs = bounded_configs(args.max_steps, args.eps_survival)
    for index, cfg in enumerate(configs, start=1):
        try:
            with warnings.catch_warnings():
                # Some Accelerate-backed NumPy builds warn on sparse zero-heavy
                # matmul while still returning finite stochastic propagation.
                warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*matmul.*")
                result = exact_two_target_fpt(cfg)
            errors = validate_result(result)
            classification = classify_distribution_shape(result.f_total)
            row = row_for_case(index, cfg, result, classification, errors)
            rows.append(row)
            results_by_case[str(row["case_id"])] = result
        except Exception as exc:  # noqa: BLE001 - report all failed scan cases.
            failures.append(f"{index}: {asdict(cfg)} -> {exc}")

    if failures:
        for failure in failures:
            print(f"FAILED {failure}")
        raise SystemExit(f"{len(failures)} scanned cases failed validation")

    write_metrics_csv(metrics_csv, rows)
    reps = representative_rows(rows)
    for row in reps:
        case_name = str(row["case_id"])
        result = results_by_case[case_name]
        save_decomposition_csv(case_dir / f"{case_name}.csv", result)
        plot_representative(figure_dir / f"{case_name}.pdf", result, row)

    write_summary(summary_md, rows, reps, metrics_csv, figure_dir, case_dir)

    counts = {label: sum(1 for row in rows if row["classification"] == label) for label in SHAPE_ORDER}
    print(f"scanned_cases={len(rows)}")
    print(f"failed_cases={len(failures)}")
    print(
        "classification_counts="
        + ",".join(f"{label}:{counts[label]}" for label in SHAPE_ORDER)
    )
    print(f"max_mass_balance_error={max(float(row['mass_balance_error']) for row in rows):.17g}")
    print(f"max_decomposition_error={max(float(row['decomposition_error']) for row in rows):.17g}")
    print(f"metrics_csv={metrics_csv}")
    print(f"representative_case_dir={case_dir}")
    print(f"representative_figure_dir={figure_dir}")
    print(f"summary={summary_md}")


if __name__ == "__main__":
    main()
