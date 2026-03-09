from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "ring_two_walker_encounter_shortcut"
DATA = REPORT / "artifacts" / "data"
FIGURES = REPORT / "artifacts" / "figures"
TABLES = REPORT / "artifacts" / "tables"
OUTPUTS = REPORT / "artifacts" / "outputs"
MANUSCRIPT = REPORT / "manuscript"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_report_module():
    module_path = REPORT / "code" / "two_walker_ring_encounter_report.py"
    spec = importlib.util.spec_from_file_location("two_walker_ring_encounter_report", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_ring_two_walker_assets_exist() -> None:
    required = [
        DATA / "a1a8_validation.json",
        DATA / "case_summary.json",
        DATA / "encounter_beta_scan.csv",
        DATA / "encounter_beta_scan_timescale.csv",
        DATA / "encounter_beta_scan_compare_detectors.csv",
        DATA / "encounter_onset_refine.csv",
        DATA / "encounter_onset_sensitivity.csv",
        DATA / "encounter_onset_agreement.csv",
        DATA / "encounter_onset_n_scan.csv",
        DATA / "fixedsite_drift_scan.csv",
        DATA / "fixedsite_summary.json",
        FIGURES / "encounter_fpt_overlay.pdf",
        FIGURES / "encounter_shortcut_decomp.pdf",
        FIGURES / "encounter_shortcut_share.pdf",
        FIGURES / "encounter_mass_balance.pdf",
        FIGURES / "encounter_onset_refine.pdf",
        FIGURES / "encounter_onset_sensitivity.pdf",
        FIGURES / "encounter_onset_agreement.pdf",
        FIGURES / "encounter_onset_n_scan.pdf",
        FIGURES / "encounter_onset_scaling.pdf",
        FIGURES / "encounter_onset_source_window.pdf",
        FIGURES / "encounter_peakcount_vs_beta.pdf",
        FIGURES / "encounter_t2_old_vs_new.pdf",
        FIGURES / "encounter_fixedsite_parity_compare.pdf",
        TABLES / "a1a8_test_table.tex",
        TABLES / "encounter_scan_table.tex",
        TABLES / "encounter_n_scan_table.tex",
        TABLES / "fixedsite_example_table.tex",
        TABLES / "fixedsite_parity_note_cn.tex",
        TABLES / "fixedsite_parity_note_en.tex",
        OUTPUTS / "run_summary.json",
        OUTPUTS / "encounter_rep_fpt.csv",
    ]
    for path in required:
        assert path.exists(), f"missing artifact: {path}"


def test_ring_two_walker_summary_consistency() -> None:
    run_summary = _read_json(OUTPUTS / "run_summary.json")
    case_summary = _read_json(DATA / "case_summary.json")
    fixedsite_summary = _read_json(DATA / "fixedsite_summary.json")
    detector_cfg = case_summary["config"]["detector"]
    fixedsite_detector_cfg = fixedsite_summary["config"]["detector"]

    with (DATA / "encounter_beta_scan.csv").open(encoding="utf-8") as fh:
        scan_rows = list(csv.DictReader(fh))

    assert run_summary["encounter_scan_points"] == len(scan_rows)
    assert run_summary["a1a8_cases"] >= 4
    assert run_summary["fixedsite_scan_points"] >= 25
    assert run_summary["onset_n_scan_points"] >= 4
    assert run_summary["onset_n_scan_valid"] >= 1
    n_scan_median = run_summary.get("onset_n_scan_median")
    assert n_scan_median is None or 0.0 <= float(n_scan_median) <= 0.30
    assert detector_cfg["mode"] == "timescale"
    assert detector_cfg["trace"] == "bar_f"
    assert detector_cfg["time_map"] == "identity"
    assert int(detector_cfg["smooth_window"]) == 11
    assert int(detector_cfg["t_ignore"]) == int(case_summary["config"]["t_ignore"])
    assert int(detector_cfg["t_end"]) == 400
    assert abs(float(detector_cfg["min_ratio"]) - 0.20) <= 1e-12
    assert abs(float(detector_cfg["max_valley_ratio"]) - 0.90) <= 1e-12
    assert abs(float(detector_cfg["peak_prominence_rel"]) - 0.01) <= 1e-12
    assert detector_cfg["peak_ratio_def"] == "R_peak=min(g_t1,g_t2)/max(g_t1,g_t2)"
    assert detector_cfg["valley_ratio_def"] == "R_valley=g_tv/max(g_t1,g_t2)"
    assert detector_cfg["directed_ratio_def"] == "R_dir=g_t2/g_t1"
    assert detector_cfg["directed_ratio_role"] == "diagnostic_only_not_used_in_phase_thresholds"
    assert detector_cfg["selection_rule"] == "t2=argmax_{tau>t1} score(tau)"
    assert detector_cfg["valley_interior_rule"] == "require_tau_minus_t1>=2_for_strict_interior_valley"
    assert detector_cfg["score_formula"] == "score=(tau-t1)*R_peak/(R_valley+1e-12)"
    assert abs(float(detector_cfg["tie_tol"]) - 1e-12) <= 1e-24
    assert detector_cfg["tie_break"] == "larger_tau -> smaller_R_valley -> larger_R_peak"
    assert fixedsite_detector_cfg["mode"] == "timescale"
    assert fixedsite_detector_cfg["trace"] == "bar_tilde_f"
    assert fixedsite_detector_cfg["time_map"] == "t=2m"
    assert "tilde_f(m)=f(2m-1)+f(2m)" in str(fixedsite_detector_cfg["coarse_rule"])
    assert int(fixedsite_detector_cfg["smooth_window"]) == 9
    assert int(fixedsite_detector_cfg["t_ignore_pair"]) == 18
    assert int(fixedsite_detector_cfg["min_sep_pair"]) == 8
    assert abs(float(fixedsite_detector_cfg["min_ratio"]) - 0.10) <= 1e-12
    assert abs(float(fixedsite_detector_cfg["max_valley_ratio"]) - 0.90) <= 1e-12
    assert abs(float(fixedsite_detector_cfg["peak_prominence_rel"]) - 0.01) <= 1e-12
    assert fixedsite_detector_cfg["peak_ratio_def"] == "R_peak=min(g_t1,g_t2)/max(g_t1,g_t2)"
    assert fixedsite_detector_cfg["valley_ratio_def"] == "R_valley=g_tv/max(g_t1,g_t2)"
    assert fixedsite_detector_cfg["directed_ratio_def"] == "R_dir=g_t2/g_t1"
    assert fixedsite_detector_cfg["directed_ratio_role"] == "diagnostic_only_not_used_in_phase_thresholds"
    assert fixedsite_detector_cfg["selection_rule"] == "t2=argmax_{tau>t1} score(tau)"
    assert fixedsite_detector_cfg["valley_interior_rule"] == "require_tau_minus_t1>=2_for_strict_interior_valley"
    assert fixedsite_detector_cfg["score_formula"] == "score=(tau-t1)*R_peak/(R_valley+1e-12)"
    assert abs(float(fixedsite_detector_cfg["tie_tol"]) - 1e-12) <= 1e-24
    assert fixedsite_detector_cfg["tie_break"] == "larger_tau -> smaller_R_valley -> larger_R_peak"
    assert fixedsite_detector_cfg["t_end_policy"] == "no_extra_cutoff"

    onset = case_summary["onset"]
    coarse = onset["coarse_beta"]
    refined = onset["refined_beta"]
    median = onset["sensitivity"]["beta_median"]

    assert coarse is None or 0.0 <= float(coarse) <= 0.30
    assert refined is None or 0.0 <= float(refined) <= 0.30
    assert median is None or 0.0 <= float(median) <= 0.30
    agree50 = onset["sensitivity"].get("beta_agreement_50")
    agree75 = onset["sensitivity"].get("beta_agreement_75")
    assert agree50 is None or 0.0 <= float(agree50) <= 0.30
    assert agree75 is None or 0.0 <= float(agree75) <= 0.30
    if agree50 is not None and agree75 is not None:
        assert float(agree50) <= float(agree75)
    n_scan_rows = onset["n_scan_rows"]
    n_scan_summary = onset["n_scan_summary"]
    assert len(n_scan_rows) >= 4
    assert int(n_scan_summary["count_total"]) == len(n_scan_rows)
    assert int(n_scan_summary["count_with_onset"]) >= 1
    assert any(int(row["N"]) == 101 for row in n_scan_rows)
    for row in n_scan_rows:
        assert int(row["N"]) >= 20
        onset_beta = row.get("onset_beta")
        onset_source = str(row.get("onset_source", "main"))
        onset_search_max_beta = row.get("onset_search_max_beta")
        if onset_beta is not None:
            onset_val = float(onset_beta)
            assert onset_search_max_beta is not None
            assert 0.0 <= onset_val <= float(onset_search_max_beta)
        if onset_source == "main":
            assert row.get("onset_beta_window") is not None
            assert row.get("onset_beta_ext") is None
        elif onset_source == "extended":
            assert row.get("onset_beta_window") is None
            assert row.get("onset_beta_ext") is not None
            assert onset_beta is not None and float(onset_beta) > 0.30
        elif onset_source == "none":
            assert onset_beta is None
            assert row.get("onset_beta_window") is None
            assert row.get("onset_beta_ext") is None
        else:
            pytest.fail(f"unexpected onset_source: {onset_source}")
        assert 0.0 <= float(row["clear_fraction"]) <= 1.0
        assert 0.0 <= float(row["rep_peak_ratio"]) <= 1.0
        assert 0.0 <= float(row["rep_valley_ratio"]) <= 1.0

    n_scan_table = (TABLES / "encounter_n_scan_table.tex").read_text(encoding="utf-8")
    scan_table = (TABLES / "encounter_scan_table.tex").read_text(encoding="utf-8")
    fixedsite_table = (TABLES / "fixedsite_example_table.tex").read_text(encoding="utf-8")
    fixedsite_note_cn = (TABLES / "fixedsite_parity_note_cn.tex").read_text(encoding="utf-8")
    fixedsite_note_en = (TABLES / "fixedsite_parity_note_en.tex").read_text(encoding="utf-8")
    report_cn_tex = (MANUSCRIPT / "ring_two_walker_encounter_shortcut_cn.tex").read_text(encoding="utf-8")
    report_en_tex = (MANUSCRIPT / "ring_two_walker_encounter_shortcut_en.tex").read_text(encoding="utf-8")
    assert "onset source" in n_scan_table
    assert "\\beta_{\\max}" in n_scan_table
    assert "peak balance ratio (min/max)" in scan_table
    assert "peak balance ratio ($\\bar{\\tilde f}$, min/max)" in fixedsite_table
    assert "R_{\\mathrm{peak}}(\\tau)=\\frac{\\min\\{g_{t_1},g_{\\tau}\\}}{\\max\\{g_{t_1},g_{\\tau}\\}}" in report_cn_tex
    assert "R_{\\mathrm{peak}}(\\tau)=\\frac{\\min\\{g_{t_1},g_{\\tau}\\}}{\\max\\{g_{t_1},g_{\\tau}\\}}" in report_en_tex
    assert "t_v=\\arg\\min_{t_1<t<t_2} g_t" in report_cn_tex
    assert "t_v=\\arg\\min_{t_1<t<t_2} g_t" in report_en_tex
    assert "统一只保留满足 $\\tau-t_1\\ge2$ 的候选峰对" in report_cn_tex
    assert "We keep only candidates with $\\tau-t_1\\ge2$" in report_en_tex
    assert "R_{\\mathrm{dir}}=\\frac{g_{t_2}}{g_{t_1}}" in report_cn_tex
    assert "R_{\\mathrm{dir}}=\\frac{g_{t_2}}{g_{t_1}}" in report_en_tex
    assert (
        "若分数在数值容差内并列（$|\\Delta\\mathrm{score}|\\le10^{-12}$），按“更晚 $\\tau$ "
        "$\\rightarrow$ 更小 $R_{\\mathrm{valley}}$ $\\rightarrow$ 更大 $R_{\\mathrm{peak}}$”的顺序确定唯一 $t_2$。"
        in report_cn_tex
    )
    assert (
        "If scores tie within numerical tolerance ($|\\Delta\\mathrm{score}|\\le10^{-12}$), we break ties by larger "
        "$\\tau$, then smaller $R_{\\mathrm{valley}}$, then larger $R_{\\mathrm{peak}}$."
        in report_en_tex
    )
    assert (
        "R_{\\mathrm{peak}}(\\tau)=\\frac{\\min\\{\\bar f(t_1),\\bar f(\\tau)\\}}{\\max\\{\\bar f(t_1),\\bar f(\\tau)\\}}"
        not in report_cn_tex
    )
    assert (
        "R_{\\mathrm{peak}}(\\tau)=\\frac{\\min\\{\\bar f(t_1),\\bar f(\\tau)\\}}{\\max\\{\\bar f(t_1),\\bar f(\\tau)\\}}"
        not in report_en_tex
    )
    assert "t_v=\\arg\\min_{t_1<t<t_2} \\bar f(t)" not in report_cn_tex
    assert "t_v=\\arg\\min_{t_1<t<t_2} \\bar f(t)" not in report_en_tex
    assert "\\text{fixed-site K=2：在 }g_m=\\bar{\\widetilde f}(m)\\text{ 的 parity 索引上运行同一选峰器，仅施加 }" in report_cn_tex
    assert "\\text{fixed-site K=2: run the same selector on parity index }m\\text{ of }g_m=\\bar{\\widetilde f}(m)," in report_en_tex
    assert "\\text{报告时间统一按 }t=2m\\text{ 映射回原时钟。}" in report_cn_tex
    assert "\\text{ no extra }t_{\\mathrm{end}}\\text{ cutoff, and reported times use }t=2m." in report_en_tex
    assert "fixed-site K=2 分支在 parity 索引上额外要求 $\\tau-t_1\\ge\\mathrm{min\\_sep\\_pair}$" in report_cn_tex
    assert "fixed-site K=2 branch applies the additional parity-index constraint $\\tau-t_1\\ge\\mathrm{min\\_sep\\_pair}$" in report_en_tex
    assert "记 $g$ 为检测轨迹（anywhere: $g=\\bar f$；fixed-site K=2: $g=\\bar{\\widetilde f}$" in report_cn_tex
    assert "Let $g$ denote the detector trace (anywhere: $g=\\bar f$; fixed-site K=2: $g=\\bar{\\widetilde f}$" in report_en_tex
    assert "$R_{\\mathrm{dir}}$ 仅作为方向性诊断展示（不参与 phase 阈值判别）" in report_cn_tex
    assert "$R_{\\mathrm{dir}}=g_{t_2}/g_{t_1}$ 可大于 1，该量不进入 phase 阈值判别。" in report_cn_tex
    assert "$R_{\\mathrm{dir}}$ is reported only as a directional diagnostic (not used in phase thresholds)." in report_en_tex
    assert (
        "$R_{\\mathrm{dir}}=g_{t_2}/g_{t_1}$ may exceed 1, and this directional ratio is not used in phase thresholds."
        in report_en_tex
    )
    assert "同时 $R_{\\mathrm{dir}}$ 与晚峰方向一致" not in report_cn_tex
    assert "consistent directed ratio $R_{\\mathrm{dir}}$" not in report_en_tex
    assert "\\input{\\TabDir/fixedsite_parity_note_cn.tex}" in report_cn_tex
    assert "\\input{\\TabDir/fixedsite_parity_note_en.tex}" in report_en_tex
    assert "157/169=0.929" not in report_cn_tex
    assert "157/169=0.929" not in report_en_tex
    phase_summary = fixedsite_summary["phase_summary"]
    clear_count = int(phase_summary["count_clear"])
    total_points = int(phase_summary["total_points"])
    ratio_token = f"{clear_count}/{total_points}={clear_count / total_points:.3f}"
    assert ratio_token in fixedsite_note_cn
    assert ratio_token in fixedsite_note_en
    assert "该分支沿用主文同一 timescale 选峰口径" in fixedsite_note_cn
    assert "This branch uses the same timescale selector as the main scan" in fixedsite_note_en
    assert "$g_m=\\bar{\\widetilde f}(m)$" in fixedsite_note_cn
    assert "$g_m=\\bar{\\widetilde f}(m)$" in fixedsite_note_en
    assert "在首遇分布中 $f(0)=0$，因此 $\\widetilde f(0)=f(0)=0$，检测从 $m\\ge1$ 开始。" in fixedsite_note_cn
    assert "候选峰对统一要求 $\\tau-t_1\\ge 2$" in fixedsite_note_cn
    assert (
        "For first-passage traces, $f(0)=0$, so $\\widetilde f(0)=f(0)=0$ and diagnostics effectively start at $m\\ge1$."
        in fixedsite_note_en
    )
    assert "candidate peak pairs require $\\tau-t_1\\ge 2$" in fixedsite_note_en
    assert (
        "$\\mathrm{score}(\\tau)=\\frac{(\\tau-t_1)\\,R_{\\mathrm{peak}}(\\tau)}"
        "{R_{\\mathrm{valley}}(\\tau)+10^{-12}}$"
        in fixedsite_note_cn
    )
    assert (
        "$\\mathrm{score}(\\tau)=\\frac{(\\tau-t_1)\\,R_{\\mathrm{peak}}(\\tau)}"
        "{R_{\\mathrm{valley}}(\\tau)+10^{-12}}$"
        in fixedsite_note_en
    )
    assert "若 $|\\Delta\\mathrm{score}|\\le10^{-12}$" in fixedsite_note_cn
    assert "If $|\\Delta\\mathrm{score}|\\le10^{-12}$" in fixedsite_note_en
    assert "$R_{\\mathrm{peak}}=\\min/\\max$" in fixedsite_note_cn
    assert "$R_{\\mathrm{dir}}=g_{t_2}/g_{t_1}$ 仅作方向性诊断（可大于 1，不参与 phase 阈值）" in fixedsite_note_cn
    assert "更晚 $\\tau$ $\\rightarrow$ 更小谷比 $\\rightarrow$ 更大峰平衡比" in fixedsite_note_cn
    assert "无额外 $t_{\\mathrm{end}}$ 截断" in fixedsite_note_cn
    assert "$R_{\\mathrm{peak}}=\\min/\\max$" in fixedsite_note_en
    assert (
        "$R_{\\mathrm{dir}}=g_{t_2}/g_{t_1}$ as a directional diagnostic only (it may exceed 1 and does not enter phase thresholds)"
        in fixedsite_note_en
    )
    assert "larger $\\tau\\rightarrow$smaller valley ratio$\\rightarrow$larger peak balance" in fixedsite_note_en
    assert "no extra $t_{\\mathrm{end}}$ cutoff" in fixedsite_note_en
    for raw_line in fixedsite_table.splitlines():
        line = raw_line.strip()
        if not line or "&" not in line or not line.endswith("\\\\") or line.startswith("\\"):
            continue
        cells = [c.strip() for c in line[:-2].split("&")]
        if len(cells) < 7:
            continue
        t1_cell, t2_cell = cells[3], cells[4]
        peak_cell, valley_cell = cells[5], cells[6]
        if t1_cell == "-" or t2_cell == "-":
            assert peak_cell == "--"
            assert valley_cell == "--"
    for raw_line in scan_table.splitlines():
        line = raw_line.strip()
        if not line or "&" not in line or not line.endswith("\\\\") or line.startswith("\\"):
            continue
        cells = [c.strip() for c in line[:-2].split("&")]
        if len(cells) < 7:
            continue
        t1_cell, t2_cell = cells[2], cells[3]
        peak_cell, valley_cell = cells[4], cells[5]
        if t1_cell == "-" or t2_cell == "-":
            assert peak_cell == "--"
            assert valley_cell == "--"
    if any(str(row.get("onset_source", "main")) == "extended" for row in n_scan_rows):
        assert "\\texttt{extended}" in n_scan_table

    rep = case_summary["representative"]
    metrics = rep["metrics"]
    assert bool(metrics["has_two"])
    assert bool(metrics["is_bimodal"])
    assert int(metrics["t1"]) < int(metrics["t2"])
    assert 0.0 < float(metrics["peak_ratio"]) <= 1.0
    assert 0.0 < float(metrics["peak_ratio_dir"]) <= 1.0
    assert 0.0 <= float(metrics["valley_ratio"]) <= 1.0
    assert int(metrics["n_peaks"]) >= 2
    h1 = float(metrics["h1"])
    h2 = float(metrics["h2"])
    expected_peak_ratio = min(h1, h2) / max(h1, h2)
    expected_peak_ratio_dir = h2 / h1
    assert abs(float(metrics["peak_ratio"]) - expected_peak_ratio) <= 1e-12
    assert abs(float(metrics["peak_ratio_dir"]) - expected_peak_ratio_dir) <= 1e-12
    assert float(rep["beta0_rel_maxdiff"]) <= 1e-12
    onset_scaling = case_summary.get("onset_scaling", {})
    assert float(onset_scaling["r2"]) >= 0.95
    share = rep["shortcut_share"]
    assert int(share["window_half_width"]) >= 0
    assert share["t_switch_share50"] is None or int(share["t_switch_share50"]) >= int(metrics["t1"])
    for key in ("share_t1_window", "share_tv_window", "share_t2_window", "cum_share_tmax"):
        value = share.get(key)
        assert value is None or 0.0 <= float(value) <= 1.0

    # Exact solver should conserve almost all mass by the reported horizon.
    mass_tmax = float(rep["mass_tmax"])
    survival_tmax = float(rep["survival_tmax"])
    assert 0.99 <= mass_tmax <= 1.000001
    assert 0.0 <= survival_tmax <= 0.01

    with (OUTPUTS / "encounter_rep_fpt.csv").open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) >= 2
    for key in ("shortcut_share_inst", "shortcut_share_cum"):
        assert key in rows[0]

    detector = fixedsite_summary["config"]["detector"]
    assert detector["mode"] == "timescale"
    assert detector["trace"] == "bar_tilde_f"
    assert detector["time_map"] == "t=2m"
    assert "tilde_f(m)=f(2m-1)+f(2m)" in detector["coarse_rule"]
    assert int(detector["smooth_window"]) == 9
    assert int(detector["t_ignore_pair"]) == 18
    assert int(detector["min_sep_pair"]) == 8
    assert abs(float(detector["min_ratio"]) - 0.10) <= 1e-12
    assert abs(float(detector["max_valley_ratio"]) - 0.90) <= 1e-12
    for block_name in ("examples", "scan"):
        block = fixedsite_summary.get(block_name, [])
        assert isinstance(block, list)
        for row in block:
            for key in ("t1", "t2", "tv"):
                value = row.get(key)
                if value is not None:
                    assert int(value) % 2 == 0
            t1_val = row.get("t1")
            t2_val = row.get("t2")
            tv_val = row.get("tv")
            if t1_val is not None and t2_val is not None:
                assert int(t1_val) < int(t2_val)
            if t1_val is not None and t2_val is not None and tv_val is not None:
                assert int(t1_val) < int(tv_val) < int(t2_val)


def test_refine_grid_falls_back_to_full_range_when_coarse_onset_missing() -> None:
    mod = _load_report_module()
    cfg = mod.RingEncounterConfig(
        beta_scan_min=0.01,
        beta_scan_max=0.29,
        beta_refine_half_width=0.05,
        beta_refine_step=0.01,
    )

    refine_min, refine_max, refine_betas = mod.build_refine_beta_grid(cfg, coarse_onset=None)

    assert refine_min == 0.01
    assert refine_max == 0.29
    assert refine_betas.size >= 28
    assert abs(float(refine_betas[0]) - 0.01) < 1e-9
    assert abs(float(refine_betas[-1]) - 0.29) < 1e-9


def test_build_ring_transition_repairs_out_of_range_params() -> None:
    mod = _load_report_module()
    P = mod.build_ring_transition(
        N=17,
        q=1.25,
        g=1.40,
        shortcut_src=3,
        shortcut_dst=9,
        beta=2.0,
    )

    assert P.shape == (17, 17)
    assert np.isfinite(P).all()
    assert np.all(P >= 0.0)
    np.testing.assert_allclose(np.sum(P, axis=1), 1.0, atol=1e-12)


def test_build_ring_transition_rejects_non_finite_params() -> None:
    mod = _load_report_module()
    with pytest.raises(ValueError):
        mod.build_ring_transition(N=11, q=float("nan"), g=0.2, shortcut_src=1, shortcut_dst=6, beta=0.3)


def test_detect_two_peak_metrics_timescale_ratio_contract() -> None:
    mod = _load_report_module()
    f = np.zeros(260, dtype=np.float64)
    f[90] = 1.0
    f[140] = 2.0

    metrics = mod.detect_two_peak_metrics_timescale(
        f,
        smooth_window=1,
        t_ignore=80,
        t_end=220,
        min_ratio=0.0,
        max_valley_ratio=1.0,
    )

    assert bool(metrics["has_two"])
    assert int(metrics["t1"]) == 90
    assert int(metrics["t2"]) == 140
    assert abs(float(metrics["peak_ratio"]) - 0.5) <= 1e-12
    assert abs(float(metrics["peak_ratio_dir"]) - 2.0) <= 1e-12


def test_select_timescale_t2_tie_break_prefers_later_timescale() -> None:
    mod = _load_report_module()
    fs = np.full(64, 0.4, dtype=np.float64)
    fs[10] = 1.0
    fs[20] = 0.9
    fs[30] = 0.45

    selected = mod.select_timescale_t2(
        fs,
        10,
        np.array([20, 30], dtype=np.int64),
        min_sep=1,
        tie_tol=1e-12,
    )

    assert selected is not None
    t2, tv, peak_ratio, valley_ratio, _ = selected
    assert int(t2) == 30
    assert int(tv) == 11
    assert abs(float(peak_ratio) - 0.45) <= 1e-12
    assert abs(float(valley_ratio) - 0.4) <= 1e-12


def test_select_timescale_t2_rejects_adjacent_peak_without_interior_valley() -> None:
    mod = _load_report_module()
    fs = np.full(32, 0.4, dtype=np.float64)
    fs[10] = 1.0
    fs[11] = 0.8  # Adjacent to t1; no strict interior valley exists.

    selected = mod.select_timescale_t2(
        fs,
        10,
        np.array([11], dtype=np.int64),
        min_sep=1,
        tie_tol=1e-12,
    )

    assert selected is None
