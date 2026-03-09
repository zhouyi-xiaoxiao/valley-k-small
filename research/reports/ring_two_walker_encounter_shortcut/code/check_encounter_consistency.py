#!/usr/bin/env python3
"""Key consistency checks for the 1D ring shortcut encounter report."""

from __future__ import annotations

import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPORT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = REPORT_DIR / "data"
FIG_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"
OUT_DIR = REPORT_DIR / "outputs"
EXPECTED_SCORE_FORMULA = "score=(tau-t1)*R_peak/(R_valley+1e-12)"
EXPECTED_TIE_BREAK = "larger_tau -> smaller_R_valley -> larger_R_peak"
EXPECTED_TIE_TOL = 1e-12
EXPECTED_PEAK_PROMINENCE_REL = 0.01
EXPECTED_VALLEY_RATIO_DEF = "R_valley=g_tv/max(g_t1,g_t2)"
EXPECTED_DIRECTED_RATIO_DEF = "R_dir=g_t2/g_t1"
EXPECTED_DIRECTED_RATIO_ROLE = "diagnostic_only_not_used_in_phase_thresholds"
EXPECTED_SELECTION_RULE = "t2=argmax_{tau>t1} score(tau)"
EXPECTED_VALLEY_INTERIOR_RULE = "require_tau_minus_t1>=2_for_strict_interior_valley"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def to_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def approx_equal(a: object, b: object, *, tol: float = 1e-12) -> bool:
    fa = to_float(a)
    fb = to_float(b)
    if fa is None and fb is None:
        return True
    if fa is None or fb is None:
        return False
    return abs(fa - fb) <= tol


def require_file(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing file: {path}")
        return
    if path.is_file() and path.stat().st_size <= 0:
        errors.append(f"empty file: {path}")


def fmt_num(value: object, *, digits: int = 3, fallback: str = "--") -> str:
    v = to_float(value)
    if v is None:
        return fallback
    return f"{v:.{digits}f}"


def fmt_int(value: object, *, fallback: str = "--") -> str:
    v = to_int(value)
    if v is None:
        return fallback
    return str(v)


def expect_contains(content: str, fragment: str, *, label: str, errors: list[str]) -> None:
    if fragment not in content:
        errors.append(f"{label} missing fragment: {fragment}")


def expect_not_contains(content: str, fragment: str, *, label: str, errors: list[str]) -> None:
    if fragment in content:
        errors.append(f"{label} should not contain fragment: {fragment}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    required_figures = [
        "a1a8_contour_convergence.pdf",
        "a1a8_radius_invariance.pdf",
        "encounter_ring_geometry.pdf",
        "encounter_shortcut_rep_case.pdf",
        "encounter_fpt_overlay.pdf",
        "encounter_shortcut_decomp.pdf",
        "encounter_shortcut_share.pdf",
        "encounter_mass_balance.pdf",
        "encounter_beta_phase.pdf",
        "encounter_peakcount_vs_beta.pdf",
        "encounter_t2_old_vs_new.pdf",
        "encounter_onset_refine.pdf",
        "encounter_onset_sensitivity.pdf",
        "encounter_onset_agreement.pdf",
        "encounter_onset_n_scan.pdf",
        "encounter_onset_scaling.pdf",
        "encounter_onset_source_window.pdf",
        "encounter_fixedsite_examples.pdf",
        "encounter_fixedsite_parity_compare.pdf",
        "encounter_fixedsite_gphase.pdf",
    ]
    required_tables = [
        "a1a8_test_table.tex",
        "encounter_scan_table.tex",
        "encounter_n_scan_table.tex",
        "encounter_key_metrics.tex",
        "encounter_shortcut_rep_case.tex",
        "fixedsite_example_table.tex",
        "fixedsite_phase_summary.tex",
        "fixedsite_parity_note_cn.tex",
        "fixedsite_parity_note_en.tex",
        "encounter_consistency_summary_cn.tex",
        "encounter_consistency_summary_en.tex",
        "encounter_nscan_summary_cn.tex",
        "encounter_nscan_summary_en.tex",
    ]
    required_json = [
        DATA_DIR / "case_summary.json",
        DATA_DIR / "a1a8_validation.json",
        DATA_DIR / "fixedsite_summary.json",
        OUT_DIR / "run_summary.json",
    ]
    required_tex_markers = [
        (
            REPORT_DIR / "ring_two_walker_encounter_shortcut_cn.tex",
            r"\input{\TabDir/encounter_consistency_summary_cn.tex}",
        ),
        (
            REPORT_DIR / "ring_two_walker_encounter_shortcut_cn.tex",
            r"\input{\TabDir/encounter_nscan_summary_cn.tex}",
        ),
        (
            REPORT_DIR / "ring_two_walker_encounter_shortcut_cn.tex",
            r"\input{\TabDir/fixedsite_parity_note_cn.tex}",
        ),
        (
            REPORT_DIR / "ring_two_walker_encounter_shortcut_en.tex",
            r"\input{\TabDir/encounter_consistency_summary_en.tex}",
        ),
        (
            REPORT_DIR / "ring_two_walker_encounter_shortcut_en.tex",
            r"\input{\TabDir/encounter_nscan_summary_en.tex}",
        ),
        (
            REPORT_DIR / "ring_two_walker_encounter_shortcut_en.tex",
            r"\input{\TabDir/fixedsite_parity_note_en.tex}",
        ),
    ]

    for name in required_figures:
        require_file(FIG_DIR / name, errors)
    for name in required_tables:
        require_file(TABLE_DIR / name, errors)
    for path in required_json:
        require_file(path, errors)
    require_file(DATA_DIR / "encounter_onset_n_scan.csv", errors)
    require_file(DATA_DIR / "encounter_beta_scan_timescale.csv", errors)
    require_file(DATA_DIR / "encounter_beta_scan_compare_detectors.csv", errors)

    for tex_path, marker in required_tex_markers:
        if tex_path.exists():
            content = tex_path.read_text(encoding="utf-8")
            if marker not in content:
                errors.append(f"missing marker {marker} in {tex_path}")
        else:
            errors.append(f"missing file: {tex_path}")

    if errors:
        result = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "passed": False,
            "errors": errors,
            "warnings": warnings,
        }
        (OUT_DIR / "consistency_check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print("[fail] consistency check failed before semantic checks")
        for msg in errors:
            print(f"  - {msg}")
        return 1

    case_summary = load_json(DATA_DIR / "case_summary.json")
    fixedsite_summary = load_json(DATA_DIR / "fixedsite_summary.json")
    run_summary = load_json(OUT_DIR / "run_summary.json")
    scan_rows = list(csv.DictReader((DATA_DIR / "encounter_beta_scan.csv").open(encoding="utf-8")))
    n_scan_rows = list(csv.DictReader((DATA_DIR / "encounter_onset_n_scan.csv").open(encoding="utf-8")))
    key_metrics_tex = (TABLE_DIR / "encounter_key_metrics.tex").read_text(encoding="utf-8")
    summary_cn_tex = (TABLE_DIR / "encounter_consistency_summary_cn.tex").read_text(encoding="utf-8")
    summary_en_tex = (TABLE_DIR / "encounter_consistency_summary_en.tex").read_text(encoding="utf-8")
    nscan_cn_tex = (TABLE_DIR / "encounter_nscan_summary_cn.tex").read_text(encoding="utf-8")
    nscan_en_tex = (TABLE_DIR / "encounter_nscan_summary_en.tex").read_text(encoding="utf-8")
    fixedsite_example_tex = (TABLE_DIR / "fixedsite_example_table.tex").read_text(encoding="utf-8")
    fixedsite_parity_cn_tex = (TABLE_DIR / "fixedsite_parity_note_cn.tex").read_text(encoding="utf-8")
    fixedsite_parity_en_tex = (TABLE_DIR / "fixedsite_parity_note_en.tex").read_text(encoding="utf-8")
    scan_table_tex = (TABLE_DIR / "encounter_scan_table.tex").read_text(encoding="utf-8")
    report_cn_tex = (REPORT_DIR / "ring_two_walker_encounter_shortcut_cn.tex").read_text(encoding="utf-8")
    report_en_tex = (REPORT_DIR / "ring_two_walker_encounter_shortcut_en.tex").read_text(encoding="utf-8")

    representative = case_summary.get("representative", {})
    rep_metrics = representative.get("metrics", {}) if isinstance(representative, dict) else {}
    rep_share = representative.get("shortcut_share", {}) if isinstance(representative, dict) else {}
    onset = case_summary.get("onset", {})
    sensitivity = onset.get("sensitivity", {}) if isinstance(onset, dict) else {}
    onset_summary = onset.get("n_scan_summary", {}) if isinstance(onset, dict) else {}
    detector_mode = str(case_summary.get("scan_detector_mode", ""))
    if detector_mode != "timescale":
        errors.append(f"scan_detector_mode should be timescale, got {detector_mode!r}")
    case_cfg = case_summary.get("config", {})
    if not isinstance(case_cfg, dict):
        errors.append("case_summary config is missing or invalid")
        case_detector_cfg: dict[str, Any] = {}
    else:
        case_detector_raw = case_cfg.get("detector", {})
        case_detector_cfg = case_detector_raw if isinstance(case_detector_raw, dict) else {}
    if not case_detector_cfg:
        errors.append("case_summary config.detector is missing or invalid")
    else:
        if str(case_detector_cfg.get("mode")) != "timescale":
            errors.append(f"case_summary detector mode should be 'timescale', got {case_detector_cfg.get('mode')!r}")
        if str(case_detector_cfg.get("trace")) != "bar_f":
            errors.append(f"case_summary detector trace should be 'bar_f', got {case_detector_cfg.get('trace')!r}")
        if str(case_detector_cfg.get("time_map")) != "identity":
            errors.append(f"case_summary detector time_map should be 'identity', got {case_detector_cfg.get('time_map')!r}")
        if to_int(case_detector_cfg.get("smooth_window")) != 11:
            errors.append(f"case_summary detector smooth_window should be 11, got {case_detector_cfg.get('smooth_window')!r}")
        if to_int(case_detector_cfg.get("t_ignore")) != to_int(case_cfg.get("t_ignore")):
            errors.append(
                "case_summary detector t_ignore should match config.t_ignore, "
                f"got detector={case_detector_cfg.get('t_ignore')!r}, config={case_cfg.get('t_ignore')!r}"
            )
        if to_int(case_detector_cfg.get("t_end")) != 400:
            errors.append(f"case_summary detector t_end should be 400, got {case_detector_cfg.get('t_end')!r}")
        if not approx_equal(case_detector_cfg.get("min_ratio"), 0.20):
            errors.append(f"case_summary detector min_ratio should be 0.20, got {case_detector_cfg.get('min_ratio')!r}")
        if not approx_equal(case_detector_cfg.get("max_valley_ratio"), 0.90):
            errors.append(
                "case_summary detector max_valley_ratio should be 0.90, "
                f"got {case_detector_cfg.get('max_valley_ratio')!r}"
            )
        if str(case_detector_cfg.get("peak_ratio_def")) != "R_peak=min(g_t1,g_t2)/max(g_t1,g_t2)":
            errors.append(
                "case_summary detector peak_ratio_def mismatch: "
                f"{case_detector_cfg.get('peak_ratio_def')!r}"
            )
        if str(case_detector_cfg.get("valley_ratio_def")) != EXPECTED_VALLEY_RATIO_DEF:
            errors.append(
                "case_summary detector valley_ratio_def mismatch: "
                f"{case_detector_cfg.get('valley_ratio_def')!r}"
            )
        if str(case_detector_cfg.get("directed_ratio_def")) != EXPECTED_DIRECTED_RATIO_DEF:
            errors.append(
                "case_summary detector directed_ratio_def mismatch: "
                f"{case_detector_cfg.get('directed_ratio_def')!r}"
            )
        if str(case_detector_cfg.get("directed_ratio_role")) != EXPECTED_DIRECTED_RATIO_ROLE:
            errors.append(
                "case_summary detector directed_ratio_role mismatch: "
                f"{case_detector_cfg.get('directed_ratio_role')!r}"
            )
        if str(case_detector_cfg.get("selection_rule")) != EXPECTED_SELECTION_RULE:
            errors.append(
                "case_summary detector selection_rule mismatch: "
                f"{case_detector_cfg.get('selection_rule')!r}"
            )
        if str(case_detector_cfg.get("valley_interior_rule")) != EXPECTED_VALLEY_INTERIOR_RULE:
            errors.append(
                "case_summary detector valley_interior_rule mismatch: "
                f"{case_detector_cfg.get('valley_interior_rule')!r}"
            )
        if str(case_detector_cfg.get("score_formula")) != EXPECTED_SCORE_FORMULA:
            errors.append(
                "case_summary detector score_formula mismatch: "
                f"{case_detector_cfg.get('score_formula')!r}"
            )
        if not approx_equal(case_detector_cfg.get("tie_tol"), EXPECTED_TIE_TOL):
            errors.append(
                "case_summary detector tie_tol mismatch: "
                f"{case_detector_cfg.get('tie_tol')!r}"
            )
        if not approx_equal(case_detector_cfg.get("peak_prominence_rel"), EXPECTED_PEAK_PROMINENCE_REL):
            errors.append(
                "case_summary detector peak_prominence_rel mismatch: "
                f"{case_detector_cfg.get('peak_prominence_rel')!r}"
            )
        if str(case_detector_cfg.get("tie_break")) != EXPECTED_TIE_BREAK:
            errors.append(
                "case_summary detector tie_break mismatch: "
                f"{case_detector_cfg.get('tie_break')!r}"
            )

    expect_contains(
        fixedsite_example_tex,
        r"$t_1\,(=2m)$",
        label="fixedsite_example_table.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_example_tex,
        r"peak balance ratio ($\bar{\tilde f}$, min/max)",
        label="fixedsite_example_table.tex",
        errors=errors,
    )
    expect_contains(
        scan_table_tex,
        r"peak balance ratio (min/max)",
        label="encounter_scan_table.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"在首遇分布场景里 $f(0)=0$",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"For first-passage traces, $f(0)=0$",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"\widetilde f(m)=f(2m-1)+f(2m)",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"输出时刻按右端点映射 $t=2m$",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"\widetilde f(m)=f(2m-1)+f(2m)",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"reported detector times use the right-endpoint map $t=2m$",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"若未检出第二峰（$t_1,t_2$ 为空），则峰平衡比与谷比在表中记为 ``--''",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"When no second peak is detected ($t_1,t_2$ absent), both ratios are reported as ``--''",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"R_{\mathrm{peak}}(\tau)=\frac{\min\{g_{t_1},g_{\tau}\}}{\max\{g_{t_1},g_{\tau}\}}",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"R_{\mathrm{peak}}(\tau)=\frac{\min\{g_{t_1},g_{\tau}\}}{\max\{g_{t_1},g_{\tau}\}}",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"t_v=\arg\min_{t_1<t<t_2} g_t",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"t_v=\arg\min_{t_1<t<t_2} g_t",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"统一只保留满足 $\tau-t_1\ge2$ 的候选峰对",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"We keep only candidates with $\tau-t_1\ge2$",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"R_{\mathrm{dir}}=\frac{g_{t_2}}{g_{t_1}}",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"R_{\mathrm{dir}}=\frac{g_{t_2}}{g_{t_1}}",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_not_contains(
        report_cn_tex,
        r"R_{\mathrm{peak}}(\tau)=\frac{\min\{\bar f(t_1),\bar f(\tau)\}}{\max\{\bar f(t_1),\bar f(\tau)\}}",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_not_contains(
        report_en_tex,
        r"R_{\mathrm{peak}}(\tau)=\frac{\min\{\bar f(t_1),\bar f(\tau)\}}{\max\{\bar f(t_1),\bar f(\tau)\}}",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_not_contains(
        report_cn_tex,
        r"t_v=\arg\min_{t_1<t<t_2} \bar f(t)",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_not_contains(
        report_en_tex,
        r"t_v=\arg\min_{t_1<t<t_2} \bar f(t)",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"R_{\mathrm{peak}}=R_{\mathrm{peak}}(t_2)",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"R_{\mathrm{peak}}=R_{\mathrm{peak}}(t_2)",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"\frac{(\tau-t_1)\cdot R_{\mathrm{peak}}(\tau)}",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"\frac{(\tau-t_1)\cdot R_{\mathrm{peak}}(\tau)}",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"{R_{\mathrm{valley}}(\tau)+10^{-12}}",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"{R_{\mathrm{valley}}(\tau)+10^{-12}}",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"若分数在数值容差内并列（$|\Delta\mathrm{score}|\le10^{-12}$），则取更晚的 $\tau$",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"若仍并列，则取谷比更小者；再并列则取峰平衡比更大者",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"if scores tie up to numerical tolerance ($|\Delta\mathrm{score}|\le10^{-12}$), choose the larger $\tau$",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"if still tied, choose smaller valley ratio; if still tied, choose larger peak-balance ratio",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"phase/onset 与多峰 score 选峰时，只使用峰平衡比 $R_{\mathrm{peak}}$（min/max）和谷比 $R_{\mathrm{valley}}$",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"For phase/onset and multi-peak score selection, we use $R_{\mathrm{peak}}$ (min/max) together with $R_{\mathrm{valley}}$",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"若分数在数值容差内并列（$|\Delta\mathrm{score}|\le10^{-12}$），按“更晚 $\tau$ $\rightarrow$ 更小 $R_{\mathrm{valley}}$ $\rightarrow$ 更大 $R_{\mathrm{peak}}$”的顺序确定唯一 $t_2$。",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"If scores tie within numerical tolerance ($|\Delta\mathrm{score}|\le10^{-12}$), we break ties by larger $\tau$, then smaller $R_{\mathrm{valley}}$, then larger $R_{\mathrm{peak}}$.",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"$R_{\mathrm{dir}}$ 仅作为方向性诊断展示（不参与 phase 阈值判别）",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"$R_{\mathrm{dir}}=g_{t_2}/g_{t_1}$ 可大于 1，该量不进入 phase 阈值判别。",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"$R_{\mathrm{dir}}$ is reported only as a directional diagnostic (not used in phase thresholds).",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"$R_{\mathrm{dir}}=g_{t_2}/g_{t_1}$ may exceed 1, and this directional ratio is not used in phase thresholds.",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_not_contains(
        report_cn_tex,
        r"同时 $R_{\mathrm{dir}}$ 与晚峰方向一致",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_not_contains(
        report_en_tex,
        r"consistent directed ratio $R_{\mathrm{dir}}$",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"\text{fixed-site K=2：在 }g_m=\bar{\widetilde f}(m)\text{ 的 parity 索引上运行同一选峰器，仅施加 }",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"\text{fixed-site K=2: run the same selector on parity index }m\text{ of }g_m=\bar{\widetilde f}(m),",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"\text{报告时间统一按 }t=2m\text{ 映射回原时钟。}",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"\text{ no extra }t_{\mathrm{end}}\text{ cutoff, and reported times use }t=2m.",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"该分支不额外施加 $t_{\mathrm{end}}$ 截断",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"this branch does not apply an extra $t_{\mathrm{end}}$ cutoff",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_contains(
        report_cn_tex,
        r"fixed-site K=2 分支在 parity 索引上额外要求 $\tau-t_1\ge\mathrm{min\_sep\_pair}$",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_contains(
        report_en_tex,
        r"fixed-site K=2 branch applies the additional parity-index constraint $\tau-t_1\ge\mathrm{min\_sep\_pair}$",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )
    expect_not_contains(
        report_cn_tex,
        r"157/169=0.929",
        label="ring_two_walker_encounter_shortcut_cn.tex",
        errors=errors,
    )
    expect_not_contains(
        report_en_tex,
        r"157/169=0.929",
        label="ring_two_walker_encounter_shortcut_en.tex",
        errors=errors,
    )

    fixed_cfg = fixedsite_summary.get("config", {})
    detector_cfg = fixed_cfg.get("detector", {}) if isinstance(fixed_cfg, dict) else {}
    if not isinstance(detector_cfg, dict):
        errors.append("fixedsite_summary config.detector is missing or invalid")
    else:
        if str(detector_cfg.get("mode")) != "timescale":
            errors.append(f"fixedsite detector mode should be 'timescale', got {detector_cfg.get('mode')!r}")
        if str(detector_cfg.get("trace")) != "bar_tilde_f":
            errors.append(f"fixedsite detector trace should be 'bar_tilde_f', got {detector_cfg.get('trace')!r}")
        if str(detector_cfg.get("time_map")) != "t=2m":
            errors.append(f"fixedsite detector time_map should be 't=2m', got {detector_cfg.get('time_map')!r}")
        coarse_rule = str(detector_cfg.get("coarse_rule", ""))
        if "tilde_f(m)=f(2m-1)+f(2m)" not in coarse_rule:
            errors.append(f"fixedsite coarse_rule missing parity mapping: {coarse_rule!r}")
        if to_int(detector_cfg.get("smooth_window")) != 9:
            errors.append(f"fixedsite smooth_window should be 9, got {detector_cfg.get('smooth_window')!r}")
        if to_int(detector_cfg.get("t_ignore_pair")) != 18:
            errors.append(f"fixedsite t_ignore_pair should be 18, got {detector_cfg.get('t_ignore_pair')!r}")
        if to_int(detector_cfg.get("min_sep_pair")) != 8:
            errors.append(f"fixedsite min_sep_pair should be 8, got {detector_cfg.get('min_sep_pair')!r}")
        if not approx_equal(detector_cfg.get("min_ratio"), 0.10):
            errors.append(f"fixedsite min_ratio should be 0.10, got {detector_cfg.get('min_ratio')!r}")
        if not approx_equal(detector_cfg.get("max_valley_ratio"), 0.90):
            errors.append(f"fixedsite max_valley_ratio should be 0.90, got {detector_cfg.get('max_valley_ratio')!r}")
        if str(detector_cfg.get("peak_ratio_def")) != "R_peak=min(g_t1,g_t2)/max(g_t1,g_t2)":
            errors.append(f"fixedsite peak_ratio_def mismatch: {detector_cfg.get('peak_ratio_def')!r}")
        if str(detector_cfg.get("valley_ratio_def")) != EXPECTED_VALLEY_RATIO_DEF:
            errors.append(f"fixedsite valley_ratio_def mismatch: {detector_cfg.get('valley_ratio_def')!r}")
        if str(detector_cfg.get("directed_ratio_def")) != EXPECTED_DIRECTED_RATIO_DEF:
            errors.append(f"fixedsite directed_ratio_def mismatch: {detector_cfg.get('directed_ratio_def')!r}")
        if str(detector_cfg.get("directed_ratio_role")) != EXPECTED_DIRECTED_RATIO_ROLE:
            errors.append(f"fixedsite directed_ratio_role mismatch: {detector_cfg.get('directed_ratio_role')!r}")
        if str(detector_cfg.get("selection_rule")) != EXPECTED_SELECTION_RULE:
            errors.append(f"fixedsite selection_rule mismatch: {detector_cfg.get('selection_rule')!r}")
        if str(detector_cfg.get("valley_interior_rule")) != EXPECTED_VALLEY_INTERIOR_RULE:
            errors.append(f"fixedsite valley_interior_rule mismatch: {detector_cfg.get('valley_interior_rule')!r}")
        if str(detector_cfg.get("score_formula")) != EXPECTED_SCORE_FORMULA:
            errors.append(f"fixedsite score_formula mismatch: {detector_cfg.get('score_formula')!r}")
        if not approx_equal(detector_cfg.get("tie_tol"), EXPECTED_TIE_TOL):
            errors.append(f"fixedsite tie_tol mismatch: {detector_cfg.get('tie_tol')!r}")
        if not approx_equal(detector_cfg.get("peak_prominence_rel"), EXPECTED_PEAK_PROMINENCE_REL):
            errors.append(f"fixedsite peak_prominence_rel mismatch: {detector_cfg.get('peak_prominence_rel')!r}")
        if str(detector_cfg.get("tie_break")) != EXPECTED_TIE_BREAK:
            errors.append(f"fixedsite tie_break mismatch: {detector_cfg.get('tie_break')!r}")
        if str(detector_cfg.get("t_end_policy")) != "no_extra_cutoff":
            errors.append(f"fixedsite t_end_policy should be 'no_extra_cutoff', got {detector_cfg.get('t_end_policy')!r}")

    fixed_phase_summary = fixedsite_summary.get("phase_summary", {})
    if not isinstance(fixed_phase_summary, dict):
        errors.append("fixedsite_summary phase_summary is missing or invalid")
    else:
        clear_count = to_int(fixed_phase_summary.get("count_clear"))
        total_points = to_int(fixed_phase_summary.get("total_points"))
        if clear_count is None or total_points is None:
            errors.append("fixedsite phase_summary count_clear/total_points missing")
        elif total_points <= 0:
            errors.append(f"fixedsite phase_summary total_points should be positive, got {total_points}")
        else:
            ratio_token = f"{clear_count}/{total_points}={float(clear_count)/float(total_points):.3f}"
            expect_contains(
                fixedsite_parity_cn_tex,
                ratio_token,
                label="fixedsite_parity_note_cn.tex",
                errors=errors,
            )
            expect_contains(
                fixedsite_parity_en_tex,
                ratio_token,
                label="fixedsite_parity_note_en.tex",
                errors=errors,
            )
    expect_contains(
        fixedsite_parity_cn_tex,
        r"该分支沿用主文同一 timescale 选峰口径",
        label="fixedsite_parity_note_cn.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_en_tex,
        r"This branch uses the same timescale selector as the main scan",
        label="fixedsite_parity_note_en.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_cn_tex,
        r"$g_m=\bar{\widetilde f}(m)$",
        label="fixedsite_parity_note_cn.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_cn_tex,
        r"在首遇分布中 $f(0)=0$，因此 $\widetilde f(0)=f(0)=0$，检测从 $m\ge1$ 开始。",
        label="fixedsite_parity_note_cn.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_en_tex,
        r"$g_m=\bar{\widetilde f}(m)$",
        label="fixedsite_parity_note_en.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_en_tex,
        r"For first-passage traces, $f(0)=0$, so $\widetilde f(0)=f(0)=0$ and diagnostics effectively start at $m\ge1$.",
        label="fixedsite_parity_note_en.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_cn_tex,
        r"候选峰对统一要求 $\tau-t_1\ge 2$",
        label="fixedsite_parity_note_cn.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_en_tex,
        r"candidate peak pairs require $\tau-t_1\ge 2$",
        label="fixedsite_parity_note_en.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_cn_tex,
        r"$\mathrm{score}(\tau)=\frac{(\tau-t_1)\,R_{\mathrm{peak}}(\tau)}{R_{\mathrm{valley}}(\tau)+10^{-12}}$",
        label="fixedsite_parity_note_cn.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_en_tex,
        r"$\mathrm{score}(\tau)=\frac{(\tau-t_1)\,R_{\mathrm{peak}}(\tau)}{R_{\mathrm{valley}}(\tau)+10^{-12}}$",
        label="fixedsite_parity_note_en.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_cn_tex,
        r"若 $|\Delta\mathrm{score}|\le10^{-12}$",
        label="fixedsite_parity_note_cn.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_en_tex,
        r"If $|\Delta\mathrm{score}|\le10^{-12}$",
        label="fixedsite_parity_note_en.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_cn_tex,
        r"$R_{\mathrm{peak}}=\min/\max$",
        label="fixedsite_parity_note_cn.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_cn_tex,
        r"更晚 $\tau$ $\rightarrow$ 更小谷比 $\rightarrow$ 更大峰平衡比",
        label="fixedsite_parity_note_cn.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_cn_tex,
        r"$R_{\mathrm{dir}}=g_{t_2}/g_{t_1}$ 仅作方向性诊断（可大于 1，不参与 phase 阈值）",
        label="fixedsite_parity_note_cn.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_cn_tex,
        r"无额外 $t_{\mathrm{end}}$ 截断",
        label="fixedsite_parity_note_cn.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_en_tex,
        r"$R_{\mathrm{peak}}=\min/\max$",
        label="fixedsite_parity_note_en.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_en_tex,
        r"larger $\tau\rightarrow$smaller valley ratio$\rightarrow$larger peak balance",
        label="fixedsite_parity_note_en.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_en_tex,
        r"$R_{\mathrm{dir}}=g_{t_2}/g_{t_1}$ as a directional diagnostic only (it may exceed 1 and does not enter phase thresholds)",
        label="fixedsite_parity_note_en.tex",
        errors=errors,
    )
    expect_contains(
        fixedsite_parity_en_tex,
        r"no extra $t_{\mathrm{end}}$ cutoff",
        label="fixedsite_parity_note_en.tex",
        errors=errors,
    )

    # fixed-site K=2 detector reports t=2m on raw clock, so non-null detector times must be even.
    for block_name in ("examples", "scan"):
        block = fixedsite_summary.get(block_name)
        if not isinstance(block, list):
            errors.append(f"fixedsite_summary[{block_name!r}] should be a list")
            continue
        for idx, row in enumerate(block):
            if not isinstance(row, dict):
                errors.append(f"fixedsite_summary[{block_name!r}][{idx}] should be a dict")
                continue
            for key in ("t1", "t2", "tv"):
                t_val = to_int(row.get(key))
                if t_val is None:
                    continue
                if t_val % 2 != 0:
                    errors.append(
                        f"fixedsite {block_name}[{idx}] has odd {key}={t_val} "
                        "(expected even under t=2m mapping)"
                    )
            t1_row = to_int(row.get("t1"))
            t2_row = to_int(row.get("t2"))
            tv_row = to_int(row.get("tv"))
            if t1_row is not None and t2_row is not None and t1_row >= t2_row:
                errors.append(
                    f"fixedsite {block_name}[{idx}] invalid ordering: t1={t1_row}, t2={t2_row}"
                )
            if (
                t1_row is not None
                and t2_row is not None
                and tv_row is not None
                and not (t1_row < tv_row < t2_row)
            ):
                errors.append(
                    f"fixedsite {block_name}[{idx}] invalid valley placement: "
                    f"t1={t1_row}, tv={tv_row}, t2={t2_row}"
                )

    for raw_line in fixedsite_example_tex.splitlines():
        line = raw_line.strip()
        if not line or "&" not in line or not line.endswith("\\\\") or line.startswith("\\"):
            continue
        cells = [c.strip() for c in line[:-2].split("&")]
        if len(cells) < 7:
            continue
        t1_cell, t2_cell = cells[3], cells[4]
        peak_cell, valley_cell = cells[5], cells[6]
        if t1_cell == "-" or t2_cell == "-":
            if peak_cell != "--" or valley_cell != "--":
                errors.append(
                    "fixedsite example row with missing peak pair must use '--' for peak/valley ratios: "
                    f"{line}"
                )

    for raw_line in scan_table_tex.splitlines():
        line = raw_line.strip()
        if not line or "&" not in line or not line.endswith("\\\\") or line.startswith("\\"):
            continue
        cells = [c.strip() for c in line[:-2].split("&")]
        if len(cells) < 7:
            continue
        t1_cell, t2_cell = cells[2], cells[3]
        peak_cell, valley_cell = cells[4], cells[5]
        if t1_cell == "-" or t2_cell == "-":
            if peak_cell != "--" or valley_cell != "--":
                errors.append(
                    "encounter scan row with missing peak pair must use '--' for peak/valley ratios: "
                    f"{line}"
                )

    is_bimodal = bool(rep_metrics.get("is_bimodal"))
    if not is_bimodal:
        errors.append("representative metrics are not clear-bimodal (expected True)")

    t1 = to_int(rep_metrics.get("t1"))
    t2 = to_int(rep_metrics.get("t2"))
    if t1 is None or t2 is None:
        errors.append("representative peak times t1/t2 are missing")
    elif t1 >= t2:
        errors.append(f"invalid peak ordering: t1={t1}, t2={t2}")

    rep_h1 = to_float(rep_metrics.get("h1"))
    rep_h2 = to_float(rep_metrics.get("h2"))
    rep_peak_ratio = to_float(rep_metrics.get("peak_ratio"))
    rep_peak_ratio_dir = to_float(rep_metrics.get("peak_ratio_dir"))
    if rep_h1 is None or rep_h2 is None or rep_h1 <= 0.0 or rep_h2 <= 0.0:
        errors.append(
            "representative peak heights h1/h2 are missing or non-positive "
            "(needed to verify peak-ratio definitions)"
        )
    else:
        expected_peak_ratio = min(rep_h1, rep_h2) / max(rep_h1, rep_h2)
        expected_peak_ratio_dir = rep_h2 / rep_h1
        if rep_peak_ratio is None or not math.isfinite(rep_peak_ratio):
            errors.append("representative peak_ratio is missing/non-finite")
        elif abs(rep_peak_ratio - expected_peak_ratio) > 1e-12:
            errors.append(
                "representative peak_ratio mismatch: "
                f"got {rep_peak_ratio:.12g}, expected min/max={expected_peak_ratio:.12g}"
            )
        if rep_peak_ratio_dir is None or not math.isfinite(rep_peak_ratio_dir):
            errors.append("representative peak_ratio_dir is missing/non-finite")
        elif abs(rep_peak_ratio_dir - expected_peak_ratio_dir) > 1e-12:
            errors.append(
                "representative peak_ratio_dir mismatch: "
                f"got {rep_peak_ratio_dir:.12g}, expected h2/h1={expected_peak_ratio_dir:.12g}"
            )

    share_t1 = to_float(rep_share.get("share_t1_window"))
    share_t2 = to_float(rep_share.get("share_t2_window"))
    if share_t1 is None or share_t2 is None:
        errors.append("shortcut share window metrics are missing")
    elif not (share_t1 > share_t2):
        errors.append(
            f"channel handoff inconsistency: share_t1_window={share_t1:.4f}, share_t2_window={share_t2:.4f}"
        )

    mass_tmax = to_float(representative.get("mass_tmax"))
    survival_tmax = to_float(representative.get("survival_tmax"))
    if mass_tmax is None or survival_tmax is None:
        errors.append("mass/survival diagnostics are missing")
    else:
        residue = abs((mass_tmax + survival_tmax) - 1.0)
        if not math.isfinite(residue) or residue > 5e-6:
            errors.append(
                f"mass conservation drift too large: |mass+survival-1|={residue:.3e}"
            )

    if not approx_equal(run_summary.get("onset_beta_coarse"), onset.get("coarse_beta")):
        errors.append("run_summary onset_beta_coarse mismatches case_summary onset.coarse_beta")
    if not approx_equal(run_summary.get("onset_beta_refined"), onset.get("refined_beta")):
        errors.append("run_summary onset_beta_refined mismatches case_summary onset.refined_beta")
    encounter_scan_points = to_int(run_summary.get("encounter_scan_points"))
    if encounter_scan_points is not None and encounter_scan_points != len(scan_rows):
        errors.append(
            f"run_summary encounter_scan_points={encounter_scan_points} but csv rows={len(scan_rows)}"
        )

    count_total = len(n_scan_rows)
    count_with_onset = sum(1 for row in n_scan_rows if row.get("onset_beta"))
    count_with_window = sum(1 for row in n_scan_rows if row.get("onset_beta_window"))
    count_extended = sum(1 for row in n_scan_rows if row.get("onset_source") == "extended")
    count_none = sum(1 for row in n_scan_rows if row.get("onset_source") == "none")

    summary_checks = [
        ("count_total", count_total),
        ("count_with_onset", count_with_onset),
        ("count_with_onset_window", count_with_window),
        ("count_extended", count_extended),
        ("count_none", count_none),
    ]
    for key, expected in summary_checks:
        got = to_int(onset_summary.get(key))
        if got is None:
            errors.append(f"n_scan_summary missing key: {key}")
        elif got != expected:
            errors.append(f"n_scan_summary[{key}]={got} but csv-derived value is {expected}")

    if to_float(onset_summary.get("onset_window_median")) is None and count_with_window > 0:
        warnings.append("onset_window_median is missing despite available nominal-window onsets")

    phase1_betas: list[float] = []
    clear_betas: list[float] = []
    for row in scan_rows:
        beta = to_float(row.get("beta"))
        phase = to_int(row.get("phase"))
        if beta is None or phase is None:
            continue
        if phase == 1:
            phase1_betas.append(beta)
        if phase == 2:
            clear_betas.append(beta)
    phase1_upper = max(phase1_betas) if phase1_betas else None
    clear_onset = min(clear_betas) if clear_betas else None

    rep_beta = to_float(representative.get("beta"))
    peak_ratio = to_float(rep_metrics.get("peak_ratio"))
    valley_ratio = to_float(rep_metrics.get("valley_ratio"))
    share_tv = to_float(rep_share.get("share_tv_window"))
    share_half = to_int(rep_share.get("window_half_width"))
    share_switch = to_int(rep_share.get("t_switch_share50"))
    share_cum = to_float(rep_share.get("cum_share_tmax"))
    shift_mass = to_float(representative.get("shortcut_shift"))
    peak_ratio_dir = to_float(rep_metrics.get("peak_ratio_dir"))
    beta0_rel_maxdiff = to_float(representative.get("beta0_rel_maxdiff"))
    onset_scaling = case_summary.get("onset_scaling", {})
    onset_scaling_slope = to_float(onset_scaling.get("slope")) if isinstance(onset_scaling, dict) else None
    onset_scaling_r2 = to_float(onset_scaling.get("r2")) if isinstance(onset_scaling, dict) else None

    key_metric_expectations = [
        f"Coarse onset $\\beta$ & {fmt_num(onset.get('coarse_beta'), digits=3)}",
        f"Refined onset $\\beta$ & {fmt_num(onset.get('refined_beta'), digits=3)}",
        "Detector onset range & "
        f"[{fmt_num(sensitivity.get('beta_min'), digits=3)}, {fmt_num(sensitivity.get('beta_max'), digits=3)}]",
        f"Detector onset median & {fmt_num(sensitivity.get('beta_median'), digits=3)}",
        f"Agreement crossing ($25\\%$) & {fmt_num(sensitivity.get('beta_agreement_25'), digits=3)}",
        f"Agreement crossing ($50\\%$) & {fmt_num(sensitivity.get('beta_agreement_50'), digits=3)}",
        f"Agreement crossing ($75\\%$) & {fmt_num(sensitivity.get('beta_agreement_75'), digits=3)}",
        "Agreement width ($75\\%-25\\%$) & "
        f"{fmt_num(sensitivity.get('beta_agreement_width_25_75'), digits=3)}",
        "Agreement width ($75\\%-50\\%$) & "
        f"{fmt_num(sensitivity.get('beta_agreement_width_50_75'), digits=3)}",
        f"Representative peaks $(t_1,t_2)$ & ({fmt_int(t1)}, {fmt_int(t2)})",
        "Peak balance ratio (min/max) / valley ratio & "
        f"{fmt_num(peak_ratio, digits=3)} / {fmt_num(valley_ratio, digits=3)}",
        "Directed peak ratio $R_\\mathrm{dir}=\\bar f(t_2)/\\bar f(t_1)$ (diagnostic only) & "
        f"{fmt_num(peak_ratio_dir, digits=3)}",
        f"Shortcut share around $t_1$ ($\\pm{fmt_int(share_half)}$) & {fmt_num(share_t1, digits=3)}",
        f"Shortcut share around valley ($\\pm{fmt_int(share_half)}$) & {fmt_num(share_tv, digits=3)}",
        f"Shortcut share around $t_2$ ($\\pm{fmt_int(share_half)}$) & {fmt_num(share_t2, digits=3)}",
        f"First $\\le 50\\%$ shortcut-share time & {fmt_int(share_switch)}",
        f"Cumulative shortcut share at $t_{{\\max}}$ & {fmt_num(share_cum, digits=3)}",
        f"Shortcut shift mass & {fmt_num(shift_mass, digits=3)}",
        f"Beta=0 relative-chain max diff & {fmt_num(beta0_rel_maxdiff, digits=3)}",
        f"Onset scaling slope (log-beta vs N) & {fmt_num(onset_scaling_slope, digits=4)}",
        f"Onset scaling $R^2$ & {fmt_num(onset_scaling_r2, digits=3)}",
    ]
    if mass_tmax is not None:
        key_metric_expectations.append(f"$\\sum_t f(t)$ at $t_{{\\max}}$ & {mass_tmax:.8f}")
    if survival_tmax is not None:
        key_metric_expectations.append(f"$S(t_{{\\max}})$ & {survival_tmax:.3e}")
    for fragment in key_metric_expectations:
        expect_contains(key_metrics_tex, fragment, label="encounter_key_metrics.tex", errors=errors)

    summary_en_expectations = [
        f"$\\beta\\le{fmt_num(phase1_upper, digits=2)}$: phase 1",
        f"coarse-onset from $\\beta\\approx{fmt_num(clear_onset, digits=2)}$: phase 2",
        f"representative case $\\beta={fmt_num(rep_beta, digits=2)}$: peaks at $t_1={fmt_int(t1)},\\ t_2={fmt_int(t2)}$",
        f"peak-balance ratio $R_\\mathrm{{peak}}={fmt_num(peak_ratio)}$ (min/max)",
        (
            f"directed peak ratio $R_\\mathrm{{dir}}={fmt_num(peak_ratio_dir)}$ "
            "(diagnostic only; may exceed 1; not used in phase thresholds)"
        ),
        f"valley ratio $R_\\mathrm{{valley}}={fmt_num(valley_ratio)}$.",
        f"We further refine onset on $\\beta\\in[{fmt_num(onset.get('refine_min'), digits=2)},{fmt_num(onset.get('refine_max'), digits=2)}]$ "
        f"with step ${fmt_num(onset.get('refine_step'), digits=3)}$, giving nominal clear-bimodal onset "
        f"$\\beta\\approx{fmt_num(onset.get('refined_beta'), digits=2)}$.",
        f"first-onset range is $[{fmt_num(sensitivity.get('beta_min'), digits=2)},{fmt_num(sensitivity.get('beta_max'), digits=2)}]$ "
        f"with median {fmt_num(sensitivity.get('beta_median'), digits=2)};",
        f"50\\% at $\\beta\\approx{fmt_num(sensitivity.get('beta_agreement_50'), digits=2)}$",
        f"75\\% at $\\beta\\approx{fmt_num(sensitivity.get('beta_agreement_75'), digits=2)}$",
        f"$\\Delta\\beta_{{25\\to75}}\\approx{fmt_num(sensitivity.get('beta_agreement_width_25_75'), digits=2)}$.",
    ]
    if mass_tmax is not None and survival_tmax is not None:
        summary_en_expectations.append(
            f"Mass-conservation check: $\\sum_t f(t)={mass_tmax:.8f}$, $S(t_{{\\max}})\\approx{survival_tmax:.2e}$."
        )
    for fragment in summary_en_expectations:
        expect_contains(summary_en_tex, fragment, label="encounter_consistency_summary_en.tex", errors=errors)

    summary_cn_expectations = [
        f"$\\beta\\le{fmt_num(phase1_upper, digits=2)}$：phase=1",
        f"粗扫描从 $\\beta\\approx{fmt_num(clear_onset, digits=2)}$ 起：phase=2",
        f"代表点 $\\beta={fmt_num(rep_beta, digits=2)}$：两峰在 $t_1={fmt_int(t1)},\\ t_2={fmt_int(t2)}$",
        f"峰平衡比 $R_\\mathrm{{peak}}={fmt_num(peak_ratio)}$（min/max）",
        f"有向峰比 $R_\\mathrm{{dir}}={fmt_num(peak_ratio_dir)}$（仅方向性诊断，可大于 1，不参与 phase 阈值）",
        f"谷比 $R_\\mathrm{{valley}}={fmt_num(valley_ratio)}$。",
        f"进一步在 $\\beta\\in[{fmt_num(onset.get('refine_min'), digits=2)},{fmt_num(onset.get('refine_max'), digits=2)}]$ 上做步长 "
        f"${fmt_num(onset.get('refine_step'), digits=3)}$ 的细扫描，名义 clear-bimodal onset 约为 "
        f"$\\beta\\approx{fmt_num(onset.get('refined_beta'), digits=2)}$。",
        f"首次 onset 区间为 $[{fmt_num(sensitivity.get('beta_min'), digits=2)},{fmt_num(sensitivity.get('beta_max'), digits=2)}]$，"
        f"中位数约 {fmt_num(sensitivity.get('beta_median'), digits=2)}；",
        f"$\\beta\\approx{fmt_num(sensitivity.get('beta_agreement_50'), digits=2)}$ 首次超过 50\\%",
        f"$\\beta\\approx{fmt_num(sensitivity.get('beta_agreement_75'), digits=2)}$ 超过 75\\%",
        f"$\\Delta\\beta_{{25\\to75}}\\approx{fmt_num(sensitivity.get('beta_agreement_width_25_75'), digits=2)}$。",
    ]
    if mass_tmax is not None and survival_tmax is not None:
        summary_cn_expectations.append(f"质量守恒检查：$\\sum_t f(t)={mass_tmax:.8f}$，$S(t_{{\\max}})\\approx{survival_tmax:.2e}$。")
    for fragment in summary_cn_expectations:
        expect_contains(summary_cn_tex, fragment, label="encounter_consistency_summary_cn.tex", errors=errors)

    n_values = [to_int(row.get("N")) for row in n_scan_rows]
    n_values = [n for n in n_values if n is not None]
    n_set_text = ",".join(str(v) for v in n_values)
    ext_rows: list[tuple[int, float]] = []
    main_rows: list[int] = []
    for row in n_scan_rows:
        n = to_int(row.get("N"))
        if n is None:
            continue
        source = str(row.get("onset_source", "main"))
        onset_beta = to_float(row.get("onset_beta"))
        onset_beta_window = to_float(row.get("onset_beta_window"))
        if source == "extended" and onset_beta is not None:
            ext_rows.append((n, onset_beta))
        if source == "main" and onset_beta_window is not None:
            main_rows.append(n)
    ext_desc_cn = (
        "；".join(f"$N={n}$ 在扩展扫描下于 $\\beta\\approx{b:.2f}$ 才进入 clear-bimodal" for n, b in ext_rows)
        if ext_rows
        else "本轮未触发扩展区回收 onset"
    )
    ext_desc_en = (
        "; ".join(f"$N={n}$ is recovered only by extension at $\\beta\\approx{b:.2f}$" for n, b in ext_rows)
        if ext_rows
        else "No extension-only onset recovery is needed in this run"
    )
    main_desc_cn = (
        f"$N\\in\\{{{','.join(str(v) for v in sorted(main_rows))}\\}}$ 均在名义窗口内出现 clear onset"
        if main_rows
        else "名义窗口内无 clear onset"
    )
    main_desc_en = (
        f"$N\\in\\{{{','.join(str(v) for v in sorted(main_rows))}\\}}$ all show clear onset inside the nominal window"
        if main_rows
        else "No clear onset appears inside the nominal window"
    )

    nscan_en_expectations = [
        f"$N\\in\\{{{n_set_text}\\}}$",
        (
            f"Current run summary: {count_total} size points total, {count_with_window} with nominal-window onset, "
            f"{count_extended} recovered by extension, {count_none} still unresolved."
        ),
        f"Extension details: {ext_desc_en}.",
        f"Nominal-window conclusion: {main_desc_en}.",
    ]
    for fragment in nscan_en_expectations:
        expect_contains(nscan_en_tex, fragment, label="encounter_nscan_summary_en.tex", errors=errors)

    nscan_cn_expectations = [
        f"$N\\in\\{{{n_set_text}\\}}$",
        (
            f"本轮统计：共 {count_total} 个 $N$，名义窗口内找到 onset 的有 {count_with_window} 个，"
            f"扩展回收 {count_extended} 个，未检出 {count_none} 个。"
        ),
        f"扩展回收细节：{ext_desc_cn}。",
        f"窗口内结论：{main_desc_cn}。",
    ]
    for fragment in nscan_cn_expectations:
        expect_contains(nscan_cn_tex, fragment, label="encounter_nscan_summary_cn.tex", errors=errors)

    passed = not errors
    result = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
    }
    (OUT_DIR / "consistency_check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if passed:
        print("[ok] consistency checks passed")
        print(
            "  representative handoff:"
            f" share_t1_window={share_t1:.3f}, share_t2_window={share_t2:.3f}"
        )
        print(
            "  n-scan counts:"
            f" total={count_total}, nominal={count_with_window}, extended={count_extended}, none={count_none}"
        )
        return 0

    print("[fail] consistency checks failed")
    for msg in errors:
        print(f"  - {msg}")
    if warnings:
        print("[warn]")
        for msg in warnings:
            print(f"  - {msg}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
