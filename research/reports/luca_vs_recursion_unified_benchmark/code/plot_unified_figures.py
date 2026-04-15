#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from common import (
    DATA_DIR,
    FIG_DIR,
    TABLE_DIR,
    FAMILY_LABELS,
    FAMILY_LABELS_CN,
    FAMILY_LUCA,
    FAMILY_TIME,
    ensure_dirs,
    workload_order,
    workload_specs,
)
from vkcore.comparison import render_workload_config_figure
from vkcore.comparison import render_runtime_config_overview_figure

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ModuleNotFoundError:  # pragma: no cover - table generation still works without plotting deps
    matplotlib = None
    plt = None


def _load_summary(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _pair_rows(summary: Dict[str, Any], task_kind: str) -> List[Dict[str, Any]]:
    return [row for row in summary["pair_rows"] if row["task_kind"] == task_kind]


def _pair_map(summary: Dict[str, Any]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    out: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for row in summary["pair_rows"]:
        out.setdefault(str(row["workload_id"]), {})[str(row["task_kind"])] = row
    return out


def _plot_runtime_bars(rows: List[Dict[str, Any]], out_path: Path, *, title: str) -> None:
    if plt is None:
        return
    labels = [row["workload_id"] for row in rows]
    luca = np.asarray([float(row["median_seconds_luca"]) for row in rows], dtype=np.float64)
    time_family = np.asarray([float(row["median_seconds_time"]) for row in rows], dtype=np.float64)
    x = np.arange(len(labels), dtype=np.float64)
    w = 0.36

    fig, ax = plt.subplots(figsize=(12.0, 4.8))
    ax.bar(x - w / 2.0, luca, width=w, color="#b45f06", alpha=0.9, label=FAMILY_LABELS[FAMILY_LUCA])
    ax.bar(x + w / 2.0, time_family, width=w, color="#2563eb", alpha=0.9, label=FAMILY_LABELS[FAMILY_TIME])
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("Median runtime (s)")
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.25, which="both")
    ax.legend(frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _plot_speedup(rows: List[Dict[str, Any]], out_path: Path) -> None:
    if plt is None:
        return
    order = {wid: idx for idx, wid in enumerate(workload_order())}
    rows = sorted(rows, key=lambda row: (order.get(row["workload_id"], 999), row["task_kind"]))
    x = np.arange(len(rows), dtype=np.float64)
    y = np.asarray([float(row["speedup_time_over_luca"]) for row in rows], dtype=np.float64)
    colors = ["#b45f06" if row["recommended_family"] == FAMILY_LUCA else "#2563eb" for row in rows]

    fig, ax = plt.subplots(figsize=(12.2, 4.6))
    ax.bar(x, y, color=colors, alpha=0.92)
    ax.axhline(1.0, color="#334155", ls="--", lw=1.2)
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{row['workload_id']}\n{row['task_kind']}" for row in rows], rotation=20, ha="right")
    ax.set_ylabel("time median / luca median")
    ax.set_title("Speed ratio by workload and task")
    ax.grid(axis="y", alpha=0.25, which="both")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _tex_escape(s: Any) -> str:
    return (
        str(s)
        .replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("%", "\\%")
        .replace("&", "\\&")
        .replace("#", "\\#")
    )


def _write_runtime_table(rows: List[Dict[str, Any]], out_path: Path, *, cn: bool) -> None:
    headers = (
        ("workload", "Luca/GF (s)", "time recursion (s)", "effective $T$ (L/T)", "recommended", "$L^1$")
        if not cn
        else ("workload", "Luca/GF (s)", "时域递推 (s)", "有效 $T$ (L/T)", "推荐", "$L^1$")
    )
    lines = [
        "\\begin{tabular}{lrrrrl}",
        "\\toprule",
        " {} & {} & {} & {} & {} & {} \\\\".format(*headers),
        "\\midrule",
    ]
    for row in rows:
        rec = row["recommended_label_cn"] if cn else row["recommended_label_en"]
        lines.append(
            "{} & {:.4g} & {:.4g} & {}/{} & {} & {:.3e} \\\\".format(
                _tex_escape(row["workload_id"]),
                float(row["median_seconds_luca"]),
                float(row["median_seconds_time"]),
                int(row["effective_horizon_luca"]),
                int(row["effective_horizon_time"]),
                _tex_escape(rec),
                float(row["l1_error"]),
            )
        )
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_complexity_table(out_path: Path) -> None:
    rows = [
        (
            "RING-1T-paper",
            "$O(mN)+O(m\\log m)$",
            "$O(TN)$",
            "closed-form single-target PGF plus AW",
        ),
        (
            "ENC-FIXED",
            "$O(mN^3)$",
            "$O(TN^3)$",
            "single-target renewal on the pair chain",
        ),
        (
            "ENC-ANY",
            "$O(mN^3)$",
            "$O(TN^3)$",
            "diagonal target set with $|D|=N$",
        ),
        (
            "TT-C1 / TT-LF1",
            "$O(mM^3)+O(m\\log m)$",
            "$O(T|E|)$",
            "defect-reduced AW vs sparse exact recursion",
        ),
        (
            "REF-S0",
            "$O(mn_T^3)+O(m\\log m)$",
            "$O(T|E|)$",
            "low-defect full AW vs exact recursion",
        ),
    ]
    lines = [
        "\\begin{tabular}{llll}",
        "\\toprule",
        "workload family & Luca/GF family & time recursion family & comment \\\\",
        "\\midrule",
    ]
    for workload, luca, time_family, note in rows:
        lines.append(
            "{} & {} & {} & {} \\\\".format(
                _tex_escape(workload),
                luca,
                time_family,
                _tex_escape(note),
            )
        )
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_solver_map(summary: Dict[str, Any], out_path: Path) -> None:
    diag_rows = sorted(_pair_rows(summary, "diagnostic"), key=lambda row: workload_order().index(row["workload_id"]))
    lines = [
        "\\begin{tabular}{llll}",
        "\\toprule",
        "workload & source report & Luca/GF solver & time solver \\\\",
        "\\midrule",
    ]
    for row in diag_rows:
        lines.append(
            "{} & {} & {} & {} \\\\".format(
                _tex_escape(row["workload_id"]),
                _tex_escape(row["source_report"]),
                _tex_escape(row["solver_variant_luca"]),
                _tex_escape(row["solver_variant_time"]),
            )
        )
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_recommendation_table(summary: Dict[str, Any], out_en: Path, out_cn: Path) -> None:
    en = [
        "\\begin{tabular}{lp{0.66\\linewidth}}",
        "\\toprule",
        "Scenario & Recommendation \\\\",
        "\\midrule",
        "Single-target ring with analytic PGF & Prefer Luca/GF when the closed form already exists and longer windows are needed. \\\\",
        "Shortcut encounter (anywhere/fixed-site) & Prefer time recursion for production figures; use GF when transform-domain renewal validation is itself the task. \\\\",
        "2D two-target, medium/high defect & Prefer time recursion; C1-like cases still punish the defect-reduced AW route. \\\\",
        "2D two-target, ultra-sparse defect & Luca/GF can win; TT-LF1 is the in-repo positive anchor. \\\\",
        "2D reflecting low-defect control & Time recursion still wins on wall time in this repo. \\\\",
        "\\bottomrule",
        "\\end{tabular}",
    ]
    cn = [
        "\\begin{tabular}{lp{0.66\\linewidth}}",
        "\\toprule",
        "场景 & 建议 \\\\",
        "\\midrule",
        "有解析 PGF 的单目标 ring & 当闭式已经可用且需要更长曲线窗口时，更偏向 Luca/GF。 \\\\",
        "shortcut encounter（anywhere/fixed-site） & 主图优先时域递推；只有变换域 renewal 校验本身是交付物时再优先 GF。 \\\\",
        "2D two-target 中/高缺陷 & 优先时域递推；C1 一类案例里 defect-reduced AW 仍然偏贵。 \\\\",
        "2D two-target 极稀疏缺陷 & Luca/GF 可以赢，TT-LF1 是本仓库里的正锚点。 \\\\",
        "2D reflecting 低缺陷控制 & 在本仓库里 wall time 仍然是时域递推更快。 \\\\",
        "\\bottomrule",
        "\\end{tabular}",
    ]
    out_en.write_text("\n".join(en) + "\n", encoding="utf-8")
    out_cn.write_text("\n".join(cn) + "\n", encoding="utf-8")


def _write_workload_inventory(specs: List[Any], out_en: Path, out_cn: Path) -> None:
    def _build(cn: bool) -> str:
        lines = [
            "\\begin{tabular}{lllll}",
            "\\toprule",
            ("workload & model & states & defects & targets \\\\" if not cn else "workload & 模型 & 状态数 & 缺陷对数 & target 数 \\\\"),
            "\\midrule",
        ]
        for spec in specs:
            lines.append(
                "{} & {} & {} & {} & {} \\\\".format(
                    _tex_escape(spec.workload_id),
                    _tex_escape(spec.model_family if not cn else spec.geometry_kind),
                    int(spec.state_size),
                    int(spec.defect_pairs),
                    int(spec.target_count),
                )
            )
        lines.extend(["\\bottomrule", "\\end{tabular}"])
        return "\n".join(lines) + "\n"

    out_en.write_text(_build(False), encoding="utf-8")
    out_cn.write_text(_build(True), encoding="utf-8")


def _write_appendix_fairness_note(summary: Dict[str, Any], out_en: Path, out_cn: Path) -> None:
    diag = next((row for row in summary["aggregates"]["by_task_kind"] if row["task_kind"] == "diagnostic"), None) or {}
    curve = next((row for row in summary["aggregates"]["by_task_kind"] if row["task_kind"] == "curve"), None) or {}
    en = [
        "\\begin{tabular}{ll}",
        "\\toprule",
        "quantity & value \\\\",
        "\\midrule",
        f"diagnostic median $t_{{time}}/t_{{Luca}}$ & {float(diag.get('median_speedup_time_over_luca', 0.0)):.4g} \\\\",
        f"curve median $t_{{time}}/t_{{Luca}}$ & {float(curve.get('median_speedup_time_over_luca', 0.0)):.4g} \\\\",
        "historical policy retained here & embedded appendix only \\\\",
        "external compare report & retired \\\\",
        "\\bottomrule",
        "\\end{tabular}",
    ]
    cn = [
        "\\begin{tabular}{ll}",
        "\\toprule",
        "量 & 数值 \\\\",
        "\\midrule",
        f"diagnostic 中位 $t_{{time}}/t_{{Luca}}$ & {float(diag.get('median_speedup_time_over_luca', 0.0)):.4g} \\\\",
        f"curve 中位 $t_{{time}}/t_{{Luca}}$ & {float(curve.get('median_speedup_time_over_luca', 0.0)):.4g} \\\\",
        "历史 full-tail 公平口径 & 仅以内嵌附录保留 \\\\",
        "外部 compare 报告 & 已退役 \\\\",
        "\\bottomrule",
        "\\end{tabular}",
    ]
    out_en.write_text("\n".join(en) + "\n", encoding="utf-8")
    out_cn.write_text("\n".join(cn) + "\n", encoding="utf-8")


def _primary_ref_labels(row: Dict[str, Any], *, cn: bool) -> str:
    refs = json.loads(str(row.get("primary_refs_json", "[]")))
    if not refs:
        return "---"
    key = "short_cn" if cn else "short_en"
    return "; ".join(_tex_escape(ref.get(key, "")) for ref in refs)


def _write_audit_appendix_table(summary: Dict[str, Any], out_en: Path, out_cn: Path) -> None:
    rows = sorted(_pair_rows(summary, "diagnostic"), key=lambda row: workload_order().index(row["workload_id"]))

    def _build(cn: bool) -> str:
        headers = (
            ("workload", "solver pair", "mathematical object", "paper source", "implementation anchor")
            if not cn
            else ("workload", "求解器配对", "数学对象", "论文来源", "仓库实现锚点")
        )
        lines = [
            "\\begin{tabular}{lp{0.18\\linewidth}p{0.20\\linewidth}p{0.20\\linewidth}p{0.20\\linewidth}}",
            "\\toprule",
            " {} & {} & {} & {} & {} \\\\".format(*headers),
            "\\midrule",
        ]
        for row in rows:
            solver_pair = (
                f"{row['solver_variant_luca']} vs {row['solver_variant_time']}"
                if not cn
                else f"{row['solver_variant_luca']} 对 {row['solver_variant_time']}"
            )
            math_object = row["math_object_cn"] if cn else row["math_object_en"]
            impl = row["implementation_anchor_cn"] if cn else row["implementation_anchor_en"]
            lines.append(
                "{} & {} & {} & {} & {} \\\\".format(
                    _tex_escape(row["workload_id"]),
                    _tex_escape(solver_pair),
                    _tex_escape(math_object),
                    _primary_ref_labels(row, cn=cn),
                    _tex_escape(impl),
                )
            )
        lines.extend(["\\bottomrule", "\\end{tabular}"])
        return "\n".join(lines) + "\n"

    out_en.write_text(_build(False), encoding="utf-8")
    out_cn.write_text(_build(True), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot figures and tables for unified benchmark report.")
    parser.add_argument("--summary", type=str, default=str(DATA_DIR / "runtime_summary.json"))
    args = parser.parse_args()

    ensure_dirs()
    summary = _load_summary(Path(args.summary))
    order = {wid: idx for idx, wid in enumerate(workload_order())}
    diagnostic_rows = sorted(_pair_rows(summary, "diagnostic"), key=lambda row: order.get(row["workload_id"], 999))
    curve_rows = sorted(_pair_rows(summary, "curve"), key=lambda row: order.get(row["workload_id"], 999))
    pair_map = _pair_map(summary)

    if plt is not None:
        _plot_runtime_bars(diagnostic_rows, FIG_DIR / "unified_runtime_diagnostic.pdf", title="Diagnostic-task runtime")
        _plot_runtime_bars(curve_rows, FIG_DIR / "unified_runtime_curve.pdf", title="Curve-task runtime")
        _plot_speedup(summary["pair_rows"], FIG_DIR / "unified_speedup_by_workload.pdf")
        render_runtime_config_overview_figure(
            [{"workload_id": spec.workload_id, "config": spec.config} for spec in workload_specs()],
            diagnostic_rows,
            FIG_DIR / "unified_runtime_config_overview.pdf",
        )

        for spec in workload_specs():
            render_workload_config_figure(
                spec.workload_id,
                spec.config,
                FIG_DIR / f"{spec.workload_id}_config_detailed.pdf",
                speed_info=pair_map.get(spec.workload_id),
            )

    _write_runtime_table(diagnostic_rows, TABLE_DIR / "unified_runtime_diagnostic_en.tex", cn=False)
    _write_runtime_table(curve_rows, TABLE_DIR / "unified_runtime_curve_en.tex", cn=False)
    _write_runtime_table(diagnostic_rows, TABLE_DIR / "unified_runtime_diagnostic_cn.tex", cn=True)
    _write_runtime_table(curve_rows, TABLE_DIR / "unified_runtime_curve_cn.tex", cn=True)
    _write_complexity_table(TABLE_DIR / "unified_complexity_table.tex")
    _write_solver_map(summary, TABLE_DIR / "unified_solver_map.tex")
    _write_recommendation_table(summary, TABLE_DIR / "unified_recommendation_en.tex", TABLE_DIR / "unified_recommendation_cn.tex")
    _write_workload_inventory(workload_specs(), TABLE_DIR / "unified_workload_inventory_en.tex", TABLE_DIR / "unified_workload_inventory_cn.tex")
    _write_appendix_fairness_note(summary, TABLE_DIR / "unified_appendix_fairness_en.tex", TABLE_DIR / "unified_appendix_fairness_cn.tex")
    _write_audit_appendix_table(summary, TABLE_DIR / "unified_audit_appendix_en.tex", TABLE_DIR / "unified_audit_appendix_cn.tex")

    print(
        json.dumps(
            {
                "figures": [
                    str(FIG_DIR / "unified_runtime_config_overview.pdf"),
                    str(FIG_DIR / "unified_runtime_diagnostic.pdf"),
                    str(FIG_DIR / "unified_runtime_curve.pdf"),
                    str(FIG_DIR / "unified_speedup_by_workload.pdf"),
                ]
                + [str(FIG_DIR / f"{spec.workload_id}_config_detailed.pdf") for spec in workload_specs()],
                "tables": [
                    str(TABLE_DIR / "unified_runtime_diagnostic_en.tex"),
                    str(TABLE_DIR / "unified_runtime_curve_en.tex"),
                    str(TABLE_DIR / "unified_complexity_table.tex"),
                    str(TABLE_DIR / "unified_solver_map.tex"),
                    str(TABLE_DIR / "unified_workload_inventory_en.tex"),
                    str(TABLE_DIR / "unified_appendix_fairness_en.tex"),
                    str(TABLE_DIR / "unified_audit_appendix_en.tex"),
                ],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
