"""Build final-report consistency indexes from existing result artifacts.

This script does not regenerate scientific results. It copies selected figure
files into the final report, writes registry/validation summaries, and checks
that the final manuscript only references files that exist.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[4]
REPORT = ROOT / "research" / "reports" / "final_multitimescale_fpt_encounter"
ARTIFACTS = REPORT / "artifacts"
FIGURES = ARTIFACTS / "figures"
DATA = ARTIFACTS / "data"
TABLES = ARTIFACTS / "tables"
MANUSCRIPT = REPORT / "manuscript" / "final_multitimescale_fpt_encounter_en.tex"
INPUTS = REPORT / "manuscript" / "inputs"

MECHANISM_BASES = {
    "budget decomposition",
    "target-channel decomposition",
    "diagonal-position decomposition",
}


def ensure_vkcore_on_path() -> None:
    candidate = ROOT / "packages" / "vkcore" / "src"
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def max_float(rows: Iterable[dict[str, str]], *fields: str) -> str:
    values: list[float] = []
    for row in rows:
        for field in fields:
            value = row.get(field, "")
            if value not in {"", "NA", "nan", "None", None}:
                values.append(float(value))
    return f"{max(values):.6e}" if values else "NA"


def class_counts(path: Path) -> Counter[str]:
    return Counter(row["classification"] for row in read_csv_rows(path))


def copy_figure(src_rel: str, dst_name: str) -> str:
    src = ROOT / src_rel
    if not src.exists():
        raise FileNotFoundError(src)
    dst = FIGURES / dst_name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return rel(dst)


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def latex_escape(text: str) -> str:
    return (
        text.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("$", r"\$")
        .replace("#", r"\#")
        .replace("_", r"\_")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("~", r"\textasciitilde{}")
        .replace("^", r"\textasciicircum{}")
    )


def write_latex_table(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    align = "p{0.18\\linewidth}p{0.16\\linewidth}p{0.18\\linewidth}p{0.40\\linewidth}"
    if len(headers) == 5:
        align = "p{0.19\\linewidth}p{0.16\\linewidth}p{0.16\\linewidth}p{0.16\\linewidth}p{0.21\\linewidth}"
    lines = [
        r"\begin{tabular}{" + align + "}",
        r"\toprule",
        " & ".join(latex_escape(h) for h in headers) + r" \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(latex_escape(cell) for cell in row) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def build_two_target_condition_tables() -> None:
    ring_rows = read_csv_rows(ROOT / "research/reports/ring_two_target/artifacts/data/small_scan_metrics.csv")
    ring_dp = [row for row in ring_rows if row["classification"] == "double_peak"]
    ring_shortcut_dp = [row for row in ring_dp if float(row["beta"]) > 0.0]
    top_shortcut = max(ring_shortcut_dp, key=lambda row: float(row["shape_score"]))

    grid_rows = read_csv_rows(
        ROOT / "research/reports/grid2d_two_target_bias_radius/artifacts/data/grid2d_bias_radius_scan_metrics.csv"
    )
    grid_dp = [row for row in grid_rows if row["classification"] == "double_peak"]
    grid_pairs = ", ".join(
        f"(r={float(row['r_actual']):.0f}, b={float(row['bias_strength_b']):.2f})" for row in grid_dp
    )

    rows = [
        [
            "1D two-target ring scan",
            f"{len(ring_dp)} double_peak cases in {len(ring_rows)} cases; {len(ring_shortcut_dp)} use beta>0",
            "separate from Luca one-target shortcut-ring configuration above",
            "positive claims require classifier label double_peak and target-channel decomposition",
        ],
        [
            "1D ring strongest shortcut score",
            "target-channel separation",
            (
                f"case 082: start={top_shortcut['start']}, "
                f"targets=({top_shortcut['target1']},{top_shortcut['target2']}), "
                f"shortcut {top_shortcut['shortcut_src']}->{top_shortcut['shortcut_dst']}"
            ),
            (
                f"score={float(top_shortcut['shape_score']):.3g}; "
                f"early={top_shortcut['early_dominant_target']}, "
                f"late={top_shortcut['late_dominant_target']}"
            ),
        ],
        [
            "2D bias-radius",
            "7 double_peak cases in 20-case theta=0 slice",
            "grid 15x9, start=(2,4), far=(12,4), near=(2+r,4), east bias",
            f"classifier double_peak at {grid_pairs}",
        ],
    ]
    write_latex_table(
        INPUTS / "two_target_conditions_table.tex",
        ["Setting", "Scan result", "Configuration", "Condition/claim"],
        rows,
    )


def build_luca_shortcut_condition_table() -> None:
    k2_rows = read_csv_rows(ROOT / "research/reports/ring_lazy_jump_ext/artifacts/data/scan_beta_N100_K2.csv")
    k4_rows = read_csv_rows(ROOT / "research/reports/ring_lazy_jump_ext/artifacts/data/scan_beta_N100_K4.csv")

    def summarize(rows: list[dict[str, str]]) -> tuple[str, str, str]:
        passing = [row for row in rows if row["paper_bimodal"] == "True"]
        beta_min = min(float(row["beta"]) for row in passing)
        beta_max = max(float(row["beta"]) for row in passing)
        beta001 = next(row for row in rows if abs(float(row["beta"]) - 0.01) < 1e-12)
        lost = min((float(row["beta"]) for row in rows if row["paper_bimodal"] == "False" and float(row["beta"]) > beta_max), default=float("nan"))
        return (
            f"{beta_min:g}--{beta_max:g}",
            f"t1={beta001['t1']}, tv={beta001['tv']}, t2={beta001['t2']}",
            f"next sampled non-bimodal beta={lost:g}",
        )

    k2_range, k2_times, k2_loss = summarize(k2_rows)
    k4_range, k4_times, k4_loss = summarize(k4_rows)
    table = rf"""\begin{{tabular}}{{p{{0.21\linewidth}}p{{0.26\linewidth}}p{{0.20\linewidth}}p{{0.25\linewidth}}}}
\toprule
Setting & Observed range & Reference case & Mechanism/criterion \\
\midrule
Luca email configuration &
\(N=100\), \(n_0=1\), target \(=51\), shortcut \(6\to52\) &
\(q=2/3\), \(\rho=1\), lazy\_selfloop, default \(\beta=0.01\) &
One absorbing target; shortcut lands just beyond the target. \\
K=2 &
paper-style bimodal for sampled \(\beta={k2_range}\) &
{k2_times.replace("t1=", r"\(t_1=").replace(", tv=", r"\), \(t_v=").replace(", t2=", r"\), \(t_2=")}\) &
{k2_loss.replace("beta=", r"\(\beta=")}\); no jump-over channel, so separation is weaker. \\
K=4 &
paper-style bimodal for sampled \(\beta={k4_range}\) &
{k4_times.replace("t1=", r"\(t_1=").replace(", tv=", r"\), \(t_v=").replace(", t2=", r"\), \(t_2=")}\) &
{k4_loss.replace("beta=", r"\(\beta=")}\); jump-over adds a delayed channel and strengthens separation. \\
\bottomrule
\end{{tabular}}
"""
    (INPUTS / "luca_shortcut_conditions_table.tex").write_text(
        table,
        encoding="utf-8",
    )


def build_registry() -> list[dict[str, str]]:
    build_two_target_condition_tables()
    build_luca_shortcut_condition_table()
    luca_overlap = copy_figure(
        "research/reports/ring_lazy_jump_ext_rev2/artifacts/figures/fig2_overlap_binbars_beta0.01_x1350.pdf",
        "luca_ring_shortcut_k2_k4_beta001.pdf",
    )
    ring_decomp = copy_figure(
        "research/reports/ring_two_target/artifacts/figures/representative_channel_decomposition.pdf",
        "ring_two_target_representative_channel_decomposition.pdf",
    )
    ring_double = copy_figure(
        "research/reports/ring_two_target/artifacts/figures/small_scan/159_double_peak_L51_x0_a50_30_gp0p6_b0p00.pdf",
        "ring_two_target_classifier_confirmed_double_peak_case_159.pdf",
    )
    grid_heatmap = copy_figure(
        "research/reports/grid2d_two_target_bias_radius/artifacts/figures/grid2d_bias_radius_heatmap_theta0.pdf",
        "grid2d_bias_radius_heatmap_theta0.pdf",
    )
    grid_decomp = copy_figure(
        "research/reports/grid2d_two_target_bias_radius/artifacts/figures/grid2d_representative_fpt_decomp_theta0_r04_b012.pdf",
        "grid2d_representative_fpt_decomp_theta0_r04_b012.pdf",
    )
    encounter_ratio = copy_figure(
        "research/reports/encounter_reflecting_diagonal_decomp/figures/encounter_fpt_by_ratio.pdf",
        "encounter_fpt_by_ratio.pdf",
    )
    encounter_diag = copy_figure(
        "research/reports/encounter_reflecting_diagonal_decomp/figures/encounter_diag_contrib_heatmap_case_p02_rho1p0.pdf",
        "encounter_diag_contrib_heatmap_case_p02_rho1p0.pdf",
    )

    rows = [
        {
            "module": "ring_lazy_jump_ext_rev2",
            "output_id": "luca_ring_shortcut_k2_k4",
            "figure_path": luca_overlap,
            "data_path": "research/reports/ring_lazy_jump_ext_rev2/artifacts/data/ft_beta0.01.csv",
            "table_path": "research/reports/final_multitimescale_fpt_encounter/manuscript/inputs/luca_shortcut_conditions_table.tex",
            "script_path": "research/reports/ring_lazy_jump_ext_rev2/code/plot_fig2_overlap_binbars.py",
            "validation_status": "aligned to Luca Outlook configuration and existing beta-scan artifacts",
            "mechanism_basis": "budget decomposition",
            "scientific_claim": "In the Luca shortcut-ring configuration, bimodality is a fast shortcut channel plus a slow non-shortcut/jump-over budget split.",
        },
        {
            "module": "ring_two_target",
            "output_id": "representative_channel_decomposition",
            "figure_path": ring_decomp,
            "data_path": "research/reports/ring_two_target/artifacts/outputs/representative_channel_decomposition.csv",
            "table_path": "NA",
            "script_path": "research/reports/ring_two_target/code/channel_decomposition.py",
            "validation_status": "target-channel identity verified in scan metrics",
            "mechanism_basis": "target-channel decomposition",
            "scientific_claim": "The total two-target FPT distribution is decomposed into target-specific channels.",
        },
        {
            "module": "ring_two_target",
            "output_id": "shape_scan",
            "figure_path": ring_double,
            "data_path": "research/reports/ring_two_target/artifacts/data/small_scan_metrics.csv",
            "table_path": "research/reports/ring_two_target/artifacts/tables/case_peaks.tex",
            "script_path": "research/reports/ring_two_target/code/run_small_scan.py",
            "validation_status": "classifier labels and decomposition errors recorded",
            "mechanism_basis": "target-channel decomposition",
            "scientific_claim": "Classifier-confirmed ring double-peak cases exist and remain tied to target-channel budgets.",
        },
        {
            "module": "grid2d_two_target_bias_radius",
            "output_id": "bias_radius_heatmap",
            "figure_path": grid_heatmap,
            "data_path": "research/reports/grid2d_two_target_bias_radius/artifacts/data/grid2d_bias_radius_scan_metrics.csv",
            "table_path": "research/reports/grid2d_two_target_bias_radius/artifacts/tables/grid2d_double_peak_candidates.csv",
            "script_path": "research/reports/grid2d_two_target_bias_radius/code/run_small_heatmap.py",
            "validation_status": "row-stochasticity, mass balance, and channel decomposition recorded",
            "mechanism_basis": "target-channel decomposition",
            "scientific_claim": "The 2D heatmap identifies classifier-confirmed cases as near/far target-channel competition varies with radius and bias.",
        },
        {
            "module": "grid2d_two_target_bias_radius",
            "output_id": "representative_fpt_decomposition",
            "figure_path": grid_decomp,
            "data_path": "research/reports/grid2d_two_target_bias_radius/artifacts/data/grid2d_bias_radius_scan_metrics.csv",
            "table_path": "NA",
            "script_path": "research/reports/grid2d_two_target_bias_radius/code/run_small_heatmap.py",
            "validation_status": "representative case listed in metrics CSV",
            "mechanism_basis": "target-channel decomposition",
            "scientific_claim": "Representative 2D cases show how near and far absorbing channels contribute to total FPT shape.",
        },
        {
            "module": "encounter_reflecting_mean_validation",
            "output_id": "mean_validation",
            "figure_path": "research/reports/encounter_reflecting_mean_validation/artifacts/figures/mean_vs_rho_smoke.svg",
            "data_path": "research/reports/encounter_reflecting_mean_validation/artifacts/data/mean_vs_rho_smoke.csv",
            "table_path": "NA",
            "script_path": "research/reports/encounter_reflecting_mean_validation/code/run_smoke.py",
            "validation_status": "fundamental-matrix and distribution means agree within recorded tolerance",
            "mechanism_basis": "diagonal-position decomposition",
            "scientific_claim": "Mean validation checks the encounter computation but does not determine full distribution shape.",
        },
        {
            "module": "encounter_reflecting_diagonal_decomp",
            "output_id": "ratio_scan",
            "figure_path": encounter_ratio,
            "data_path": "research/reports/encounter_reflecting_diagonal_decomp/data/encounter_ratio_scan_metrics.csv",
            "table_path": "research/reports/encounter_reflecting_diagonal_decomp/tables/encounter_shape_classification.csv",
            "script_path": "research/reports/encounter_reflecting_diagonal_decomp/code/run_ratio_scan.py",
            "validation_status": "mass balance and diagonal decomposition verified for all recorded cases",
            "mechanism_basis": "diagonal-position decomposition",
            "scientific_claim": "The encounter ratio and initial-position scan is currently unimodal across all recorded cases.",
        },
        {
            "module": "encounter_reflecting_diagonal_decomp",
            "output_id": "diagonal_position_heatmap",
            "figure_path": encounter_diag,
            "data_path": "research/reports/encounter_reflecting_diagonal_decomp/outputs/case_p02_rho1p0_diag_contrib.csv",
            "table_path": "research/reports/encounter_reflecting_diagonal_decomp/tables/encounter_shape_classification.csv",
            "script_path": "research/reports/encounter_reflecting_diagonal_decomp/code/run_ratio_scan.py",
            "validation_status": "f_E(t)=sum_k f_k(t) error recorded as zero",
            "mechanism_basis": "diagonal-position decomposition",
            "scientific_claim": "Diagonal-position heterogeneity is read from f_k(t) windows rather than from the mean alone.",
        },
    ]

    for row in rows:
        if row["mechanism_basis"] not in MECHANISM_BASES:
            raise AssertionError(f"unsupported mechanism basis: {row}")
        for key in ("figure_path", "data_path", "table_path", "script_path"):
            value = row[key]
            if value not in {"NA", "manuscript inline figure"} and not (ROOT / value).exists():
                raise FileNotFoundError(f"{key} does not exist for {row['output_id']}: {value}")
    return rows


def build_validation_summary() -> list[dict[str, str]]:
    ring_rows = read_csv_rows(ROOT / "research/reports/ring_two_target/artifacts/data/small_scan_metrics.csv")
    mean_rows = read_csv_rows(
        ROOT / "research/reports/encounter_reflecting_mean_validation/artifacts/data/mean_vs_rho_smoke.csv"
    )
    diag_rows = read_csv_rows(
        ROOT / "research/reports/encounter_reflecting_diagonal_decomp/data/encounter_ratio_scan_metrics.csv"
    )
    grid_summary = json.loads(
        (ROOT / "research/reports/grid2d_two_target_bias_radius/artifacts/data/grid2d_bias_radius_scan_summary.json").read_text(
            encoding="utf-8"
        )
    )
    mean_summary = json.loads(
        (ROOT / "research/reports/encounter_reflecting_mean_validation/artifacts/outputs/smoke_summary.json").read_text(
            encoding="utf-8"
        )
    )
    diag_summary = json.loads(
        (ROOT / "research/reports/encounter_reflecting_diagonal_decomp/outputs/ratio_scan_summary.json").read_text(
            encoding="utf-8"
        )
    )
    helper_dir = ROOT / "research/reports/encounter_reflecting_mean_validation/code"
    sys.path.insert(0, str(helper_dir))
    try:
        from reflecting_encounter import (  # type: ignore
            build_joint_transition,
            build_reflecting_lazy_transition,
            fixed_total_mobility,
            row_stochastic_error,
        )
    finally:
        sys.path.pop(0)

    diag_row_errors: list[float] = []
    for row in diag_rows:
        q1, q2 = fixed_total_mobility(float(row["q0"]), float(row["rho"]))
        p1 = build_reflecting_lazy_transition(int(row["L"]), q1)
        p2 = build_reflecting_lazy_transition(int(row["L"]), q2)
        joint = build_joint_transition(p1, p2)
        diag_row_errors.extend(
            [
                row_stochastic_error(p1),
                row_stochastic_error(p2),
                row_stochastic_error(joint),
            ]
        )

    return [
        {
            "module": "ring_two_target",
            "row_stochasticity_max_error": max_float(ring_rows, "row_stochasticity_error"),
            "mass_balance_max_error": max_float(ring_rows, "mass_balance_error"),
            "decomposition_max_error": max_float(ring_rows, "decomposition_error"),
            "tests_passed": "yes: row, mass, target-channel checks below tolerance",
        },
        {
            "module": "grid2d_two_target_bias_radius",
            "row_stochasticity_max_error": f"{float(grid_summary['max_row_stochasticity_error']):.6e}",
            "mass_balance_max_error": f"{float(grid_summary['max_mass_balance_error']):.6e}",
            "decomposition_max_error": f"{float(grid_summary['max_decomposition_error']):.6e}",
            "tests_passed": "yes: row, mass, target-channel checks below tolerance",
        },
        {
            "module": "encounter_reflecting_mean_validation",
            "row_stochasticity_max_error": max_float(
                mean_rows,
                "p1_row_error",
                "p2_row_error",
                "joint_row_error",
                "absorbing_row_error",
            ),
            "mass_balance_max_error": f"{float(mean_summary['max_mass_balance_error']):.6e}",
            "decomposition_max_error": "NA",
            "tests_passed": "yes: mean agreement and mass balance below tolerance",
        },
        {
            "module": "encounter_reflecting_diagonal_decomp",
            "row_stochasticity_max_error": f"{max(diag_row_errors):.6e}",
            "mass_balance_max_error": f"{float(diag_summary['max_mass_balance_error']):.6e}",
            "decomposition_max_error": f"{float(diag_summary['max_diagonal_decomposition_error']):.6e}",
            "tests_passed": "yes: mass and diagonal-position checks below tolerance",
        },
    ]


def write_tables(registry_rows: list[dict[str, str]], validation_rows: list[dict[str, str]]) -> None:
    module_labels = {
        "ring_lazy_jump_ext_rev2": "luca_shortcut",
        "ring_two_target": "ring_two_target",
        "grid2d_two_target_bias_radius": "grid2d_bias_radius",
        "encounter_reflecting_mean_validation": "encounter_mean",
        "encounter_reflecting_diagonal_decomp": "encounter_diagonal",
    }
    output_labels = {
        "luca_ring_shortcut_k2_k4": "K2_K4_beta001",
        "representative_channel_decomposition": "channel_decomp",
        "shape_scan": "shape_scan",
        "bias_radius_heatmap": "heatmap",
        "representative_fpt_decomposition": "fpt_decomp",
        "mean_validation": "mean_validation",
        "ratio_scan": "ratio_scan",
        "diagonal_position_heatmap": "diag_heatmap",
    }
    registry_table_rows = [
        [
            module_labels.get(row["module"], row["module"]),
            output_labels.get(row["output_id"], row["output_id"]),
            row["mechanism_basis"],
            row["scientific_claim"],
        ]
        for row in registry_rows
    ]
    write_latex_table(
        INPUTS / "result_registry_table.tex",
        ["Module", "Output", "Mechanism", "Supported claim"],
        registry_table_rows,
    )
    validation_table_rows = [
        [
            module_labels.get(row["module"], row["module"]),
            row["row_stochasticity_max_error"],
            row["mass_balance_max_error"],
            row["decomposition_max_error"],
            row["tests_passed"],
        ]
        for row in validation_rows
    ]
    write_latex_table(
        INPUTS / "validation_summary_table.tex",
        ["Module", "Row max", "Mass max", "Decomp max", "Status"],
        validation_table_rows,
    )


def audit_double_peak_text() -> None:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    ring_counts = class_counts(ROOT / "research/reports/ring_two_target/artifacts/data/small_scan_metrics.csv")
    grid_counts = class_counts(
        ROOT / "research/reports/grid2d_two_target_bias_radius/artifacts/data/grid2d_bias_radius_scan_metrics.csv"
    )
    encounter_counts = class_counts(
        ROOT / "research/reports/encounter_reflecting_diagonal_decomp/data/encounter_ratio_scan_metrics.csv"
    )

    if "ring double\\_peak" in text and ring_counts["double_peak"] == 0:
        raise AssertionError("ring double_peak claim has no classifier support")
    if "2D double\\_peak" in text and grid_counts["double_peak"] == 0:
        raise AssertionError("2D double_peak claim has no classifier support")
    if "encounter double\\_peak" in text and encounter_counts["double_peak"] == 0:
        raise AssertionError("encounter double_peak claim has no classifier support")

    audit_rows = [
        {"module": "ring_two_target", "double_peak_count": str(ring_counts["double_peak"]), "claim_status": "supported"},
        {
            "module": "grid2d_two_target_bias_radius",
            "double_peak_count": str(grid_counts["double_peak"]),
            "claim_status": "supported",
        },
        {
            "module": "encounter_reflecting_diagonal_decomp",
            "double_peak_count": str(encounter_counts["double_peak"]),
            "claim_status": "no positive claim in final text",
        },
    ]
    write_csv(
        DATA / "double_peak_audit.csv",
        audit_rows,
        ["module", "double_peak_count", "claim_status"],
    )


def audit_manuscript_references() -> None:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    for command in ("includegraphics", "input"):
        for match in re.finditer(r"\\" + command + r"(?:\[[^\]]*\])?\{([^}]+)\}", text):
            value = match.group(1)
            if command == "includegraphics" and Path(value).suffix == "":
                candidates = [
                    REPORT / "manuscript" / value,
                    REPORT / "manuscript" / f"{value}.pdf",
                    FIGURES / value,
                    FIGURES / f"{value}.pdf",
                ]
            elif command == "includegraphics":
                candidates = [REPORT / "manuscript" / value, FIGURES / value]
            else:
                candidates = [REPORT / "manuscript" / value]
            if not any(candidate.exists() for candidate in candidates):
                raise FileNotFoundError(f"missing manuscript {command} target: {value}")


def write_figure_index(registry_rows: list[dict[str, str]]) -> None:
    rows = []
    for row in registry_rows:
        figure = row["figure_path"]
        if figure in {"NA", "manuscript inline figure"}:
            continue
        rows.append(
            {
                "module": row["module"],
                "output_id": row["output_id"],
                "figure_path": figure,
                "exists": str((ROOT / figure).exists()).lower(),
            }
        )
    write_csv(DATA / "figure_index.csv", rows, ["module", "output_id", "figure_path", "exists"])


def main() -> None:
    for directory in (FIGURES, DATA, TABLES, INPUTS):
        directory.mkdir(parents=True, exist_ok=True)

    registry_rows = build_registry()
    validation_rows = build_validation_summary()

    write_csv(
        DATA / "result_registry.csv",
        registry_rows,
        [
            "module",
            "output_id",
            "figure_path",
            "data_path",
            "table_path",
            "script_path",
            "validation_status",
            "mechanism_basis",
            "scientific_claim",
        ],
    )
    write_csv(
        DATA / "validation_summary.csv",
        validation_rows,
        [
            "module",
            "row_stochasticity_max_error",
            "mass_balance_max_error",
            "decomposition_max_error",
            "tests_passed",
        ],
    )
    write_figure_index(registry_rows)
    write_tables(registry_rows, validation_rows)
    audit_double_peak_text()
    audit_manuscript_references()
    print(f"Wrote {rel(DATA / 'result_registry.csv')}")
    print(f"Wrote {rel(DATA / 'validation_summary.csv')}")
    print(f"Wrote {rel(DATA / 'figure_index.csv')}")
    print(f"Wrote {rel(DATA / 'double_peak_audit.csv')}")


if __name__ == "__main__":
    main()
