#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import multiprocessing as mp
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "packages" / "vkcore" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from vkcore.grid2d.one_two_target_gating import (
    GateConfig,
    GATE_ANCHOR_FAMILY_LABELS,
    LGR_STATE_LABELS,
    LR_STATE_LABELS,
    SIDE_GATE_ANCHOR_LABELS,
    SIDE_R_LABELS,
    THREE_FAMILY_LABELS,
    build_case,
    build_committor_gate_mask,
    build_membrane_case_directional,
    build_membrane_case,
    build_start_basin_mask,
    build_x_gate_mask,
    case_metrics_dict,
    committor_diagnostics,
    compute_one_target_window_path_statistics,
    exact_gate_anchor_family_fpt,
    exact_gate_anchor_side_family_fpt,
    exact_lgr_class_fpt,
    exact_lgr_side_class_fpt,
    exact_rollback_class_fpt,
    exact_rollback_side_class_fpt,
    exact_lr_class_fpt,
    exact_lr_side_class_fpt,
    marginalize_gate_anchor_to_npq,
    marginalize_gate_anchor_to_lr,
    marginalize_lgr_to_lr,
    marginalize_side_lgr_to_side_r,
    membrane_edges_to_idx,
    plot_branch_fpt,
    plot_family_fpt,
    plot_first_escape_side_usage,
    plot_four_family_windows,
    plot_geometry_with_gates,
    plot_mc_vs_exact,
    plot_one_target_class_crosswalk,
    plot_one_target_directional_flux,
    plot_one_target_gate_geometry,
    plot_one_target_gate_schematic,
    plot_one_target_gate_scan_families,
    plot_one_target_gate_scan_totals,
    plot_one_target_left_open_split_windows,
    plot_one_target_parameter_phase_map,
    plot_one_target_parameter_sep_map,
    plot_one_target_rollback_window_bars,
    plot_one_target_start_phase_map,
    plot_one_target_side_window_bars,
    plot_one_target_window_occupancy_atlas,
    plot_one_target_window_families,
    plot_phase_v2_flow,
    plot_progress_medians,
    plot_robustness_heatmap,
    plot_scan_family_lines,
    plot_side_usage,
    plot_two_target_extension,
    plot_two_target_phase_atlas,
    plot_unified_mechanism_ladder,
    plot_window_composition,
    run_family_exact,
    run_gate_robustness,
    run_mc,
    save_case_timeseries,
    solve_committor,
    split_membrane_edges_by_side,
    summarize_gate_anchor_family_masses,
    summarize_rollback_class_masses,
    summarize_mc,
    window_fraction_dict,
    window_ranges,
)


REPORT_ROOT = Path(__file__).resolve().parents[1]
NOTES_DIR = REPORT_ROOT / "notes"
RAW_DIR = NOTES_DIR / "source_imports" / "2026-03-16" / "raw"
DATA_DIR = REPORT_ROOT / "artifacts" / "data"
FIG_DIR = REPORT_ROOT / "artifacts" / "figures"
TABLE_DIR = REPORT_ROOT / "artifacts" / "tables"
OUT_DIR = REPORT_ROOT / "artifacts" / "outputs"
SENSITIVITY_DIR = DATA_DIR / "sensitivity"

RAW_ARCHIVE_FILES = [
    "1_2target_机制深化整包.zip",
    "one_two_target_深化报告_cn.pdf",
    "二维_two_target_gating_framework_bundle.zip",
    "two_target_gating_framework_cn.pdf",
    "二维半透膜_gating_game_打包.zip",
    "二维半透膜_gating_game备忘录.pdf",
]

SOURCE_CHAIN = [
    "二维半透膜_gating_game",
    "two_target_gating_framework",
    "one_two_target_deepening_work",
]

DEFAULT_TWO_TARGET_GATE = GateConfig(
    near_ring_radius=2,
    x_out_offset=2,
    x_in_offset=0,
    progress_fracs=(0.33, 0.66),
)
ONE_TARGET_COMMITTOR_QSTARS = (0.3, 0.4, 0.5, 0.6, 0.7)
ONE_TARGET_START_SCAN_MAX_WORKERS = 1
ONE_TARGET_MP_CONTEXT = None
ONE_TARGET_REP_T_MAX = 5000
ONE_TARGET_SCAN_T_MAX = 3200

TWO_TARGET_REP_T_MAX = 5000
TWO_TARGET_SCAN_T_MAX = 2000
TWO_TARGET_MC_WALKERS = 20000
TWO_TARGET_MC_SEED0 = 20260316

TWO_TARGET_CASE_SPECS = {
    "anchor": {"near_dx": 2, "near_dy": 2, "bx": 0.12},
    "clear_instance": {"near_dx": 4, "near_dy": 1, "bx": 0.12},
    "near_mass_loss": {"near_dx": 2, "near_dy": 6, "bx": 0.12},
}

SOURCE_ONE_TARGET_EXPECTATIONS = {
    "sym": {
        "phase": 2,
        "t_peak1": 394,
        "t_valley": 1080,
        "t_peak2": 1696,
    },
    "asym": {
        "phase": 2,
        "t_peak1": 394,
        "t_valley": 1081,
        "t_peak2": 1704,
    },
}

SOURCE_TWO_TARGET_EXPECTATIONS = {
    "anchor": {
        "phase": 2,
        "p_far": 0.6760085327508798,
        "t_peak2": 469,
        "sep_gate_coarse": 2.493150684931507,
        "late_family_coarse": "F_no_return",
    },
    "clear_instance": {
        "phase": 2,
        "p_far": 0.6502638910530909,
        "t_peak2": 471,
        "sep_gate_coarse": 2.379947229551451,
        "late_family_coarse": "F_no_return",
    },
    "near_mass_loss": {
        "phase": 1,
        "p_far": 0.9112623182462092,
        "t_peak2": 470,
        "sep_gate_coarse": 2.2290076335877864,
        "late_family_coarse": "F_no_return",
    },
}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def _json_ready(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {str(key): _json_ready(value) for key, value in payload.items()}
    if isinstance(payload, (list, tuple)):
        return [_json_ready(value) for value in payload]
    if isinstance(payload, np.ndarray):
        return payload.tolist()
    if isinstance(payload, (np.floating, np.integer, np.bool_)):
        return payload.item()
    return payload


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(_json_ready(payload), ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: Sequence[dict[str, Any]], fieldnames: Sequence[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def cleanup_stale_outputs() -> None:
    for name in [
        "source_one_two_target_深化报告_cn.pdf",
        "source_two_target_gating_framework_cn.pdf",
        "source_二维半透膜_gating_game备忘录.pdf",
        "one_target_qstar_recheck.csv",
        "one_target_xgate_scan_recheck.csv",
        "one_target_recheck.csv",
        "one_target_gate_scan_recheck.csv",
    ]:
        path = OUT_DIR / name
        if path.exists():
            path.unlink()
    for path in [
        DATA_DIR / "one_target_qstar_sensitivity.csv",
        DATA_DIR / "one_target_representative_summary.csv",
        DATA_DIR / "one_target_side_window_fractions_q05.csv",
        DATA_DIR / "one_target_window_fractions_q05.csv",
        DATA_DIR / "one_target_xgate_representative_summary.csv",
        DATA_DIR / "one_target_xgate_scan.csv",
        DATA_DIR / "one_target_window_fractions_xg_star.csv",
        DATA_DIR / "one_target_side_window_fractions_xg_star.csv",
        DATA_DIR / "one_target_gate_representative_summary.csv",
        DATA_DIR / "one_target_window_families_xg_star.csv",
        DATA_DIR / "one_target_side_window_families_xg_star.csv",
        DATA_DIR / "one_target_representative_summary.csv",
        DATA_DIR / "one_target_tb_scan.csv",
        DATA_DIR / "one_target_dir_scan.csv",
        DATA_DIR / "one_target_gate_window_families_xg_star.csv",
        DATA_DIR / "one_target_rollback_window_families.csv",
        DATA_DIR / "one_target_phase0_examples.csv",
        DATA_DIR / "one_target_symmetry_control.csv",
        FIG_DIR / "gating_game_one_target_gate_schematic.pdf",
        FIG_DIR / "gating_game_one_target_gate_schematic.png",
        FIG_DIR / "one_target_peak2_qstar_sensitivity.pdf",
        FIG_DIR / "one_target_peak2_qstar_sensitivity.png",
        FIG_DIR / "one_target_realset_geometry.pdf",
        FIG_DIR / "one_target_realset_geometry.png",
        FIG_DIR / "one_target_state_bookkeeping.pdf",
        FIG_DIR / "one_target_state_bookkeeping.png",
        FIG_DIR / "one_target_xgate_scan_peak2.pdf",
        FIG_DIR / "one_target_xgate_scan_peak2.png",
        FIG_DIR / "one_target_xgate_totals.pdf",
        FIG_DIR / "one_target_xgate_totals.png",
        FIG_DIR / "one_target_xgate_window_decomposition.pdf",
        FIG_DIR / "one_target_xgate_window_decomposition.png",
        FIG_DIR / "one_target_start_phase_maps.pdf",
        FIG_DIR / "one_target_start_phase_maps.png",
        FIG_DIR / "one_target_start_sep_maps.pdf",
        FIG_DIR / "one_target_start_sep_maps.png",
        FIG_DIR / "one_target_gate_geometry.pdf",
        FIG_DIR / "one_target_gate_geometry.png",
        FIG_DIR / "one_target_gate_scan_families.pdf",
        FIG_DIR / "one_target_gate_scan_families.png",
        FIG_DIR / "one_target_gate_scan_totals.pdf",
        FIG_DIR / "one_target_gate_scan_totals.png",
        FIG_DIR / "one_target_window_families.pdf",
        FIG_DIR / "one_target_window_families.png",
        FIG_DIR / "one_target_class_crosswalk.pdf",
        FIG_DIR / "one_target_class_crosswalk.png",
        FIG_DIR / "one_target_tb_phase_map.pdf",
        FIG_DIR / "one_target_tb_phase_map.png",
        FIG_DIR / "one_target_tb_sep_map.pdf",
        FIG_DIR / "one_target_tb_sep_map.png",
        FIG_DIR / "one_target_dir_phase_map.pdf",
        FIG_DIR / "one_target_dir_phase_map.png",
        FIG_DIR / "one_target_dir_sep_map.pdf",
        FIG_DIR / "one_target_dir_sep_map.png",
        FIG_DIR / "one_target_rollback_window_bars.pdf",
        FIG_DIR / "one_target_rollback_window_bars.png",
        FIG_DIR / "one_target_start_family_map.pdf",
        FIG_DIR / "one_target_start_family_map.png",
        FIG_DIR / "one_target_start_sep_map.pdf",
        FIG_DIR / "one_target_start_sep_map.png",
        FIG_DIR / "one_target_start_phase_map.pdf",
        FIG_DIR / "one_target_start_phase_map.png",
        FIG_DIR / "one_target_start_leak_balance_map.pdf",
        FIG_DIR / "one_target_start_leak_balance_map.png",
        FIG_DIR / "one_target_directional_window_flux.pdf",
        FIG_DIR / "one_target_directional_window_flux.png",
        FIG_DIR / "one_target_directional_window_occupancy_atlas.pdf",
        FIG_DIR / "one_target_directional_window_occupancy_atlas.png",
        FIG_DIR / "one_target_left_open_vs_membrane_windows.pdf",
        FIG_DIR / "one_target_left_open_vs_membrane_windows.png",
        TABLE_DIR / "one_target_xgate_peak2.tex",
        TABLE_DIR / "one_target_representative.tex",
        TABLE_DIR / "one_target_gate_scan_summary.tex",
        TABLE_DIR / "one_target_phase0_loss_summary.tex",
        TABLE_DIR / "one_target_left_open_summary.tex",
    ]:
        if path.exists():
            path.unlink()


def latex_escape(text: Any) -> str:
    s = str(text)
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in repl.items():
        s = s.replace(old, new)
    return s


def fmt_num(value: Any, digits: int = 3) -> str:
    if value in ("", None):
        return "-"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return latex_escape(value)
    if np.isnan(number):
        return "-"
    if abs(number) >= 100:
        return f"{number:.0f}"
    if abs(number) >= 10:
        return f"{number:.1f}"
    return f"{number:.{digits}f}"


def fmt_pct(value: Any, digits: int = 1) -> str:
    if value in ("", None):
        return "-"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return latex_escape(value)
    if np.isnan(number):
        return "-"
    return f"{100.0 * number:.{digits}f}\\%"


def write_tabular(path: Path, headers: Sequence[str], rows: Sequence[Sequence[str]], align: str) -> None:
    lines = [rf"\begin{{tabular}}{{{align}}}", r"\toprule"]
    lines.append(" & ".join(headers) + r" \\")
    lines.append(r"\midrule")
    for row in rows:
        lines.append(" & ".join(row) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    write_text(path, "\n".join(lines))


def idx(x: int, y: int, lx: int) -> int:
    return int(y) * int(lx) + int(x)


def first_true_index(mask: np.ndarray) -> int | None:
    if not bool(np.any(mask)):
        return None
    return int(np.argmax(mask))


ONE_TARGET_BASE_ARGS = dict(
    Lx=60,
    Wy=15,
    bx=-0.08,
    corridor_halfwidth=2,
    wall_margin=5,
    delta_core=1.0,
    delta_open=0.55,
    start_x=7,
    target_x=58,
)
ONE_TARGET_PARAM_VALUES = [
    0.00,
    0.00025,
    0.0005,
    0.00075,
    0.0010,
    0.00125,
    0.0015,
    0.00175,
    0.0020,
    0.0025,
    0.0030,
    0.0035,
    0.0040,
    0.0045,
    0.0050,
]
ONE_TARGET_CASE_TITLES = {
    "sym_shared": "shared symmetric baseline",
    "tb_asym_balanced": "top/bottom balanced asymmetry",
    "dir_asym_easy_out_balanced": "directional easy-out / hard-return",
    "dir_asym_easy_in_balanced": "directional hard-out / easy-return",
}
ONE_TARGET_REP_ANCHORS = {
    "tb_asym_balanced": (0.0020, 0.0005),
    "dir_asym_easy_out_balanced": (0.0020, 0.0005),
    "dir_asym_easy_in_balanced": (0.0005, 0.0020),
}


def _base_start_target() -> tuple[tuple[int, int], tuple[int, int]]:
    y_mid = int((int(ONE_TARGET_BASE_ARGS["Wy"]) - 1) // 2)
    return (int(ONE_TARGET_BASE_ARGS["start_x"]), y_mid), (int(ONE_TARGET_BASE_ARGS["target_x"]), y_mid)


def _augment_one_target_case(case: dict[str, Any], *, case_name: str, case_style: str, display_name: str) -> dict[str, Any]:
    payload = dict(case)
    payload["case_name"] = case_name
    payload["case_style"] = case_style
    payload["display_name"] = display_name
    if "kappa_top" not in payload:
        payload["kappa_top"] = float(payload.get("kappa_c2o", 0.0))
    if "kappa_bottom" not in payload:
        payload["kappa_bottom"] = float(payload.get("kappa_c2o", 0.0))
    if "kappa_c2o" not in payload:
        payload["kappa_c2o"] = float(payload.get("kappa_top", 0.0))
    if "kappa_o2c" not in payload:
        payload["kappa_o2c"] = float(payload.get("kappa_top", 0.0))
    return payload


def _build_one_target_case_from_spec(
    spec: dict[str, Any],
    *,
    start: tuple[int, int] | None = None,
    target: tuple[int, int] | None = None,
    t_max_total: int = ONE_TARGET_REP_T_MAX,
) -> dict[str, Any]:
    kwargs = {
        **ONE_TARGET_BASE_ARGS,
        "start": start,
        "target": target,
    }
    style = str(spec["style"])
    if style == "tb":
        case = build_membrane_case(
            **kwargs,
            kappa_top=float(spec["kappa_top"]),
            kappa_bottom=float(spec["kappa_bottom"]),
            t_max_total=int(t_max_total),
        )
    elif style == "dir":
        case = build_membrane_case_directional(
            **kwargs,
            kappa_c2o=float(spec["kappa_c2o"]),
            kappa_o2c=float(spec["kappa_o2c"]),
            t_max_total=int(t_max_total),
        )
    else:
        raise ValueError(f"unsupported one-target style: {style}")
    return _augment_one_target_case(
        case,
        case_name=str(spec["case"]),
        case_style=style,
        display_name=str(spec["display_name"]),
    )


def build_one_target_cases() -> dict[str, dict[str, Any]]:
    kwargs = dict(ONE_TARGET_BASE_ARGS)
    return {
        "sym": build_membrane_case(**kwargs, kappa_top=0.002, kappa_bottom=0.002),
        "asym": build_membrane_case(**kwargs, kappa_top=0.002, kappa_bottom=0.0),
    }


def one_target_committor_control(case: dict[str, Any], q_star: float) -> dict[str, Any]:
    lx = int(case["Lx"])
    wy = int(case["Wy"])
    n_states = int(lx) * int(wy)
    set_a = build_start_basin_mask(Lx=lx, Wy=wy, start_x=int(case["start"][0]), y_mid=int(case["y_mid"]))
    set_b = np.zeros(n_states, dtype=bool)
    target_idx = idx(int(case["target"][0]), int(case["target"][1]), lx)
    set_b[target_idx] = True
    q_values = solve_committor(
        n_states=n_states,
        src_idx=case["src_idx"],
        dst_idx=case["dst_idx"],
        probs=case["probs"],
        set_A=set_a,
        set_B=set_b,
    )
    membrane_idx_edges = membrane_edges_to_idx(membrane_edges=case["membrane_edges"], lx=lx)
    f_lr, surv = exact_lr_class_fpt(
        n_states=n_states,
        start_idx=idx(case["start"][0], case["start"][1], lx),
        src_idx=case["src_idx"],
        dst_idx=case["dst_idx"],
        probs=case["probs"],
        target_idx=target_idx,
        set_A=set_a,
        q_values=q_values,
        q_star=q_star,
        membrane_idx_edges=membrane_idx_edges,
        t_max=len(case["f_total"]) - 1,
        surv_tol=1.0e-12,
    )
    windows = window_ranges(case["res"].t_peak1, case["res"].t_valley, case["res"].t_peak2, len(case["f_total"]))
    return {
        "f_lr": f_lr,
        "surv": surv,
        "windows": windows,
        "window_props": window_fraction_dict(f_lr, windows, list(LR_STATE_LABELS)),
        "q_values": q_values,
        "set_A": set_a,
        "q_star": float(q_star),
    }


def one_target_gate_anchor_exact(
    case: dict[str, Any],
    *,
    x_gate: int,
    gate_mask: np.ndarray | None = None,
    t_max: int | None = None,
) -> dict[str, Any]:
    lx = int(case["Lx"])
    wy = int(case["Wy"])
    n_states = int(lx) * int(wy)
    start_idx = idx(case["start"][0], case["start"][1], lx)
    target_idx = idx(case["target"][0], case["target"][1], lx)
    set_a = build_start_basin_mask(Lx=lx, Wy=wy, start_x=int(case["start"][0]), y_mid=int(case["y_mid"]))
    gate_mask = build_x_gate_mask(Lx=lx, Wy=wy, X_g=int(x_gate), gate_mode="line") if gate_mask is None else np.asarray(gate_mask, dtype=bool)
    membrane_idx_edges = membrane_edges_to_idx(membrane_edges=case["membrane_edges"], lx=lx)
    run_t_max = int(len(case["f_total"]) - 1 if t_max is None else t_max)
    f_family, surv = exact_gate_anchor_family_fpt(
        n_states=n_states,
        start_idx=start_idx,
        src_idx=case["src_idx"],
        dst_idx=case["dst_idx"],
        probs=case["probs"],
        target_idx=target_idx,
        set_A=set_a,
        gate_mask=gate_mask,
        membrane_idx_edges=membrane_idx_edges,
        t_max=run_t_max,
        surv_tol=1.0e-12,
    )
    f_npq = marginalize_gate_anchor_to_npq(f_family)
    f_lr = marginalize_gate_anchor_to_lr(f_family)
    windows = window_ranges(case["res"].t_peak1, case["res"].t_valley, case["res"].t_peak2, len(case["f_total"]))
    top_edges, bottom_edges = split_membrane_edges_by_side(
        membrane_edges=case["membrane_edges"],
        wall_span=case["wall_span"],
        lx=lx,
    )
    f_side, _ = exact_gate_anchor_side_family_fpt(
        n_states=n_states,
        start_idx=start_idx,
        src_idx=case["src_idx"],
        dst_idx=case["dst_idx"],
        probs=case["probs"],
        target_idx=target_idx,
        gate_mask=gate_mask,
        top_idx_edges=top_edges,
        bottom_idx_edges=bottom_edges,
        t_max=run_t_max,
        surv_tol=1.0e-12,
    )
    totals = summarize_gate_anchor_family_masses(f_family)
    return {
        "x_gate": int(x_gate),
        "f_family": f_family,
        "f_npq": f_npq,
        "f_lr": f_lr,
        "f_side": f_side,
        "surv": surv,
        "windows": windows,
        "family_window_props": window_fraction_dict(f_family, windows, list(GATE_ANCHOR_FAMILY_LABELS)),
        "npq_window_props": window_fraction_dict(f_npq, windows, list(THREE_FAMILY_LABELS)),
        "lr_window_props": window_fraction_dict(f_lr, windows, list(LR_STATE_LABELS)),
        "side_window_props": window_fraction_dict(f_side, windows, list(SIDE_GATE_ANCHOR_LABELS)),
        "set_A": set_a,
        "gate_mask": gate_mask,
        "totals": totals,
    }


def one_target_rollback_exact(
    case: dict[str, Any],
    *,
    t_max: int | None = None,
) -> dict[str, Any]:
    lx = int(case["Lx"])
    wy = int(case["Wy"])
    n_states = int(lx) * int(wy)
    start_idx = idx(case["start"][0], case["start"][1], lx)
    target_idx = idx(case["target"][0], case["target"][1], lx)
    set_a = build_start_basin_mask(Lx=lx, Wy=wy, start_x=int(case["start"][0]), y_mid=int(case["y_mid"]))
    membrane_idx_edges = membrane_edges_to_idx(membrane_edges=case["membrane_edges"], lx=lx)
    run_t_max = int(len(case["f_total"]) - 1 if t_max is None else t_max)
    f_lr, surv = exact_rollback_class_fpt(
        n_states=n_states,
        start_idx=start_idx,
        src_idx=case["src_idx"],
        dst_idx=case["dst_idx"],
        probs=case["probs"],
        target_idx=target_idx,
        set_A=set_a,
        membrane_idx_edges=membrane_idx_edges,
        t_max=run_t_max,
        surv_tol=1.0e-12,
    )
    top_edges, bottom_edges = split_membrane_edges_by_side(
        membrane_edges=case["membrane_edges"],
        wall_span=case["wall_span"],
        lx=lx,
    )
    f_side, _ = exact_rollback_side_class_fpt(
        n_states=n_states,
        start_idx=start_idx,
        src_idx=case["src_idx"],
        dst_idx=case["dst_idx"],
        probs=case["probs"],
        target_idx=target_idx,
        set_A=set_a,
        top_idx_edges=top_edges,
        bottom_idx_edges=bottom_edges,
        t_max=run_t_max,
        surv_tol=1.0e-12,
    )
    windows = window_ranges(case["res"].t_peak1, case["res"].t_valley, case["res"].t_peak2, len(case["f_total"]))
    totals = summarize_rollback_class_masses(f_lr)
    return {
        "f_lr": f_lr,
        "f_side": f_side,
        "surv": surv,
        "windows": windows,
        "lr_window_props": window_fraction_dict(f_lr, windows, list(LR_STATE_LABELS)),
        "side_window_props": window_fraction_dict(f_side, windows, list(SIDE_R_LABELS)),
        "totals": totals,
    }


def one_target_line_vs_halfspace_control(case: dict[str, Any], *, x_gate: int) -> dict[str, Any]:
    lx = int(case["Lx"])
    src_x = np.asarray(case["src_idx"], dtype=np.int64) % lx
    dst_x = np.asarray(case["dst_idx"], dtype=np.int64) % lx
    start_left = int(case["start"][0]) < int(x_gate)
    no_skip_across_gate = bool(np.all(~((src_x < int(x_gate)) & (dst_x > int(x_gate)))))
    if start_left and no_skip_across_gate:
        return {
            "line": None,
            "halfspace": None,
            "max_family_abs_diff": 0.0,
            "max_lr_abs_diff": 0.0,
            "max_side_abs_diff": 0.0,
            "max_total_abs_diff": 0.0,
            "total_diffs": {
                "no_leak_total": 0.0,
                "pre_gate_leak_total": 0.0,
                "post_gate_leak_total": 0.0,
                "rollback_total": 0.0,
                "leak_total": 0.0,
            },
        }

    line_mask = build_x_gate_mask(Lx=int(case["Lx"]), Wy=int(case["Wy"]), X_g=int(x_gate), gate_mode="line")
    halfspace_mask = build_x_gate_mask(Lx=int(case["Lx"]), Wy=int(case["Wy"]), X_g=int(x_gate), gate_mode="halfspace")
    line = one_target_gate_anchor_exact(case, x_gate=x_gate, gate_mask=line_mask)
    halfspace = one_target_gate_anchor_exact(case, x_gate=x_gate, gate_mask=halfspace_mask)
    family_diff = float(np.max(np.abs(np.asarray(line["f_family"]) - np.asarray(halfspace["f_family"]))))
    lr_diff = float(np.max(np.abs(np.asarray(line["f_lr"]) - np.asarray(halfspace["f_lr"]))))
    side_diff = float(np.max(np.abs(np.asarray(line["f_side"]) - np.asarray(halfspace["f_side"]))))
    totals = {
        key: abs(float(line["totals"][key]) - float(halfspace["totals"][key]))
        for key in ("no_leak_total", "pre_gate_leak_total", "post_gate_leak_total", "rollback_total", "leak_total")
    }
    return {
        "line": line,
        "halfspace": halfspace,
        "max_family_abs_diff": family_diff,
        "max_lr_abs_diff": lr_diff,
        "max_side_abs_diff": side_diff,
        "max_total_abs_diff": max(totals.values()) if totals else 0.0,
        "total_diffs": totals,
    }


def _one_target_case_build_spec(case_name: str, case: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "case": case_name,
        "style": str(case["case_style"]),
        "display_name": str(case["display_name"]),
        "target_x": int(case["target"][0]),
        "target_y": int(case["target"][1]),
        "base_start_x": int(case["start"][0]),
        "base_start_y": int(case["start"][1]),
    }
    if str(case["case_style"]) == "tb":
        payload["kappa_top"] = float(case["kappa_top"])
        payload["kappa_bottom"] = float(case["kappa_bottom"])
    else:
        payload["kappa_c2o"] = float(case["kappa_c2o"])
        payload["kappa_o2c"] = float(case["kappa_o2c"])
    return payload


def _build_one_target_case_from_payload(
    payload: dict[str, Any],
    *,
    start: tuple[int, int] | None = None,
    target: tuple[int, int] | None = None,
    t_max_total: int = ONE_TARGET_REP_T_MAX,
) -> dict[str, Any]:
    spec = {
        "case": str(payload["case"]),
        "style": str(payload["style"]),
        "display_name": str(payload.get("display_name", payload["case"])),
    }
    if str(payload["style"]) == "tb":
        spec["kappa_top"] = float(payload["kappa_top"])
        spec["kappa_bottom"] = float(payload["kappa_bottom"])
    else:
        spec["kappa_c2o"] = float(payload["kappa_c2o"])
        spec["kappa_o2c"] = float(payload["kappa_o2c"])
    return _build_one_target_case_from_spec(spec, start=start, target=target, t_max_total=t_max_total)


def _one_target_start_scan_spec(case_name: str, case: dict[str, Any], *, x_gate: int) -> dict[str, Any]:
    return {**_one_target_case_build_spec(case_name, case), "x_gate": int(x_gate)}


def _compute_one_target_parameter_scan_row(payload: dict[str, Any]) -> dict[str, Any]:
    case = _build_one_target_case_from_payload(payload, t_max_total=ONE_TARGET_SCAN_T_MAX)
    x_gate = int(payload["x_gate"])
    rollback_exact = one_target_rollback_exact(case)
    gate_exact = one_target_gate_anchor_exact(case, x_gate=x_gate)
    peak2_lr = rollback_exact["lr_window_props"]["peak2"]
    peak2_gate = gate_exact["npq_window_props"]["peak2"]
    dominant_lr = max(peak2_lr, key=peak2_lr.get)
    dominant_gate = max(peak2_gate, key=peak2_gate.get)
    row = {
        "scan_type": str(payload["scan_type"]),
        "phase": int(case["res"].phase),
        "t_peak1": None if case["res"].t_peak1 is None else int(case["res"].t_peak1),
        "t_valley": None if case["res"].t_valley is None else int(case["res"].t_valley),
        "t_peak2": None if case["res"].t_peak2 is None else int(case["res"].t_peak2),
        "valley_over_max": None if case["res"].valley_over_max is None else float(case["res"].valley_over_max),
        "sep_peaks": float(case["res"].sep_peaks),
        "rollback_total": float(rollback_exact["totals"]["rollback_total"]),
        "no_leak_total": float(rollback_exact["totals"]["no_leak_total"]),
        "leak_total": float(rollback_exact["totals"]["leak_total"]),
        "peak2_dominant_rollback_class": dominant_lr,
        "peak2_dominant_rollback_frac": float(peak2_lr[dominant_lr]),
        "peak2_dominant_gate_family": dominant_gate,
        "peak2_dominant_gate_frac": float(peak2_gate[dominant_gate]),
        **{label: float(peak2_lr[label]) for label in LR_STATE_LABELS},
        **{label: float(peak2_gate[label]) for label in THREE_FAMILY_LABELS},
    }
    if str(payload["scan_type"]) == "tb":
        row["kappa_top"] = float(payload["kappa_top"])
        row["kappa_bottom"] = float(payload["kappa_bottom"])
    else:
        row["kappa_c2o"] = float(payload["kappa_c2o"])
        row["kappa_o2c"] = float(payload["kappa_o2c"])
    return row


def _compute_one_target_gate_scan_row(payload: dict[str, Any]) -> dict[str, Any]:
    case = _build_one_target_case_from_payload(
        payload,
        start=(int(payload["base_start_x"]), int(payload["base_start_y"])),
        target=(int(payload["target_x"]), int(payload["target_y"])),
        t_max_total=ONE_TARGET_SCAN_T_MAX,
    )
    x_gate = int(payload["x_gate"])
    gate_exact = one_target_gate_anchor_exact(case, x_gate=x_gate)
    peak2_family = gate_exact["npq_window_props"]["peak2"]
    dominant_family = max(peak2_family, key=peak2_family.get)
    return {
        "case": str(payload["case"]),
        "display_name": str(payload["display_name"]),
        "style": str(payload["style"]),
        "X_g": x_gate,
        **{label: float(peak2_family[label]) for label in THREE_FAMILY_LABELS},
        "dominant_family": dominant_family,
        "dominant_family_frac": float(peak2_family[dominant_family]),
        "dominant_lr": max(gate_exact["lr_window_props"]["peak2"], key=gate_exact["lr_window_props"]["peak2"].get),
        "no_leak_total": float(gate_exact["totals"]["no_leak_total"]),
        "pre_gate_leak_total": float(gate_exact["totals"]["pre_gate_leak_total"]),
        "post_gate_leak_total": float(gate_exact["totals"]["post_gate_leak_total"]),
        "rollback_total": float(gate_exact["totals"]["rollback_total"]),
        "leak_total": float(gate_exact["totals"]["leak_total"]),
    }


def _select_balanced_rep_row(
    rows: Sequence[dict[str, Any]],
    *,
    x_key: str,
    y_key: str,
    anchor_x: float,
    anchor_y: float,
    predicate,
) -> dict[str, Any]:
    candidates = [row for row in rows if predicate(row) and float(row[x_key]) > 0.0 and float(row[y_key]) > 0.0]
    if not candidates:
        raise RuntimeError("no candidate rows available for representative selection")
    phase2 = [row for row in candidates if int(row["phase"]) >= 2]
    pool = phase2 if phase2 else candidates
    return min(
        pool,
        key=lambda row: (
            abs(float(row[x_key]) - float(anchor_x)) + abs(float(row[y_key]) - float(anchor_y)),
            -int(row["phase"]),
            -float(row["sep_peaks"]),
        ),
    )


def _build_one_target_canonical_cases(tb_scan_rows: Sequence[dict[str, Any]], dir_scan_rows: Sequence[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    sym_case = _build_one_target_case_from_spec(
        {
            "case": "sym_shared",
            "style": "dir",
            "display_name": ONE_TARGET_CASE_TITLES["sym_shared"],
            "kappa_c2o": 0.002,
            "kappa_o2c": 0.002,
        }
    )
    sym_case["kappa_top"] = 0.002
    sym_case["kappa_bottom"] = 0.002

    tb_row = _select_balanced_rep_row(
        tb_scan_rows,
        x_key="kappa_top",
        y_key="kappa_bottom",
        anchor_x=ONE_TARGET_REP_ANCHORS["tb_asym_balanced"][0],
        anchor_y=ONE_TARGET_REP_ANCHORS["tb_asym_balanced"][1],
        predicate=lambda row: float(row["kappa_top"]) > float(row["kappa_bottom"]),
    )
    dir_out_row = _select_balanced_rep_row(
        dir_scan_rows,
        x_key="kappa_c2o",
        y_key="kappa_o2c",
        anchor_x=ONE_TARGET_REP_ANCHORS["dir_asym_easy_out_balanced"][0],
        anchor_y=ONE_TARGET_REP_ANCHORS["dir_asym_easy_out_balanced"][1],
        predicate=lambda row: float(row["kappa_c2o"]) > float(row["kappa_o2c"]),
    )
    dir_in_row = _select_balanced_rep_row(
        dir_scan_rows,
        x_key="kappa_c2o",
        y_key="kappa_o2c",
        anchor_x=ONE_TARGET_REP_ANCHORS["dir_asym_easy_in_balanced"][0],
        anchor_y=ONE_TARGET_REP_ANCHORS["dir_asym_easy_in_balanced"][1],
        predicate=lambda row: float(row["kappa_c2o"]) < float(row["kappa_o2c"]),
    )

    return {
        "sym_shared": sym_case,
        "tb_asym_balanced": _build_one_target_case_from_spec(
            {
                "case": "tb_asym_balanced",
                "style": "tb",
                "display_name": ONE_TARGET_CASE_TITLES["tb_asym_balanced"],
                "kappa_top": float(tb_row["kappa_top"]),
                "kappa_bottom": float(tb_row["kappa_bottom"]),
            }
        ),
        "dir_asym_easy_out_balanced": _build_one_target_case_from_spec(
            {
                "case": "dir_asym_easy_out_balanced",
                "style": "dir",
                "display_name": ONE_TARGET_CASE_TITLES["dir_asym_easy_out_balanced"],
                "kappa_c2o": float(dir_out_row["kappa_c2o"]),
                "kappa_o2c": float(dir_out_row["kappa_o2c"]),
            }
        ),
        "dir_asym_easy_in_balanced": _build_one_target_case_from_spec(
            {
                "case": "dir_asym_easy_in_balanced",
                "style": "dir",
                "display_name": ONE_TARGET_CASE_TITLES["dir_asym_easy_in_balanced"],
                "kappa_c2o": float(dir_in_row["kappa_c2o"]),
                "kappa_o2c": float(dir_in_row["kappa_o2c"]),
            }
        ),
    }


def _compute_one_target_start_scan_row_batch(payload: dict[str, Any]) -> list[dict[str, Any]]:
    target = (int(payload["target_x"]), int(payload["target_y"]))
    base_start = (int(payload["base_start_x"]), int(payload["base_start_y"]))
    start_y = int(payload["start_y"])
    x_gate = int(payload["x_gate"])
    rows: list[dict[str, Any]] = []

    for start_x in range(int(ONE_TARGET_BASE_ARGS["Lx"])):
        if (start_x, start_y) == target:
            continue
        scan_case = _build_one_target_case_from_payload(
            payload,
            start=(int(start_x), int(start_y)),
            target=target,
            t_max_total=ONE_TARGET_SCAN_T_MAX,
        )
        rows.append(
            {
                "case": str(payload["case"]),
                "display_name": str(payload["display_name"]),
                "style": str(payload["style"]),
                "base_start_x": base_start[0],
                "base_start_y": base_start[1],
                "target_x": target[0],
                "target_y": target[1],
                "x_gate": int(x_gate),
                "start_x": int(start_x),
                "start_y": int(start_y),
                "phase": int(scan_case["res"].phase),
                "t_peak1": None if scan_case["res"].t_peak1 is None else int(scan_case["res"].t_peak1),
                "t_valley": None if scan_case["res"].t_valley is None else int(scan_case["res"].t_valley),
                "t_peak2": None if scan_case["res"].t_peak2 is None else int(scan_case["res"].t_peak2),
                "valley_over_max": None if scan_case["res"].valley_over_max is None else float(scan_case["res"].valley_over_max),
                "sep_peaks": float(scan_case["res"].sep_peaks),
            }
        )
    return rows


def build_one_target_start_scan_rows(case_name: str, case: dict[str, Any], *, x_gate: int) -> list[dict[str, Any]]:
    spec = _one_target_start_scan_spec(case_name, case, x_gate=x_gate)
    payloads = [{**spec, "start_y": int(start_y)} for start_y in range(int(ONE_TARGET_BASE_ARGS["Wy"]))]
    rows: list[dict[str, Any]] = []
    max_workers = min(len(payloads), ONE_TARGET_START_SCAN_MAX_WORKERS)
    if max_workers <= 1:
        for payload in payloads:
            rows.extend(_compute_one_target_start_scan_row_batch(payload))
    else:
        with ProcessPoolExecutor(max_workers=max_workers, mp_context=ONE_TARGET_MP_CONTEXT) as executor:
            for batch in executor.map(_compute_one_target_start_scan_row_batch, payloads):
                rows.extend(batch)
    rows.sort(key=lambda row: (str(row["case"]), int(row["start_y"]), int(row["start_x"])))
    return rows


def _summarize_phase0_examples(start_rows: Sequence[dict[str, Any]], *, case_name: str) -> list[dict[str, Any]]:
    case_rows = [row for row in start_rows if str(row["case"]) == case_name]
    phase0_rows = [row for row in case_rows if int(row["phase"]) == 0]
    if not phase0_rows:
        return []
    base_start = (int(case_rows[0]["base_start_x"]), int(case_rows[0]["base_start_y"]))
    target = (int(case_rows[0]["target_x"]), int(case_rows[0]["target_y"]))
    onset = min(
        phase0_rows,
        key=lambda row: (
            abs(int(row["start_y"]) - base_start[1]),
            int(row["start_x"]),
            abs(int(row["start_y"]) - base_start[1]),
        ),
    )
    offaxis_pool = [row for row in phase0_rows if abs(int(row["start_y"]) - base_start[1]) >= 2]
    offaxis = min(
        offaxis_pool if offaxis_pool else phase0_rows,
        key=lambda row: (
            abs(abs(int(row["start_y"]) - base_start[1]) - 2),
            int(row["start_x"]),
            abs(int(row["start_y"]) - base_start[1]),
        ),
    )
    target_adjacent_pool = [
        row for row in phase0_rows if int(row["start_y"]) == base_start[1] and int(row["start_x"]) < target[0]
    ]
    target_adjacent = max(target_adjacent_pool if target_adjacent_pool else phase0_rows, key=lambda row: int(row["start_x"]))
    return [
        {"case": case_name, "label": "A", "description": "phase-0 onset on the centerline", **{k: onset[k] for k in ("start_x", "start_y", "phase", "sep_peaks")}},
        {"case": case_name, "label": "B", "description": "off-axis phase-0 loss near the target", **{k: offaxis[k] for k in ("start_x", "start_y", "phase", "sep_peaks")}},
        {"case": case_name, "label": "C", "description": "target-adjacent phase-0 collapse", **{k: target_adjacent[k] for k in ("start_x", "start_y", "phase", "sep_peaks")}},
    ]


def build_one_target_datasets() -> dict[str, Any]:
    x_gate_star = int((int(ONE_TARGET_BASE_ARGS["start_x"]) + int(ONE_TARGET_BASE_ARGS["target_x"])) // 2)
    representative_rows: list[dict[str, Any]] = []
    gate_scan_rows: list[dict[str, Any]] = []
    gate_window_rows: list[dict[str, Any]] = []
    rollback_window_rows: list[dict[str, Any]] = []
    side_rows: list[dict[str, Any]] = []
    start_scan_rows: list[dict[str, Any]] = []
    committor_control_rows: list[dict[str, Any]] = []
    equivalence_rows: list[dict[str, Any]] = []
    verification_rows: list[dict[str, Any]] = []
    phase0_rows: list[dict[str, Any]] = []

    tb_payloads = [
        {
            "scan_type": "tb",
            "case": f"tb_{i}_{j}",
            "style": "tb",
            "display_name": "top/bottom scan",
            "kappa_top": float(kappa_top),
            "kappa_bottom": float(kappa_bottom),
            "x_gate": x_gate_star,
        }
        for i, kappa_top in enumerate(ONE_TARGET_PARAM_VALUES)
        for j, kappa_bottom in enumerate(ONE_TARGET_PARAM_VALUES)
    ]
    dir_payloads = [
        {
            "scan_type": "dir",
            "case": f"dir_{i}_{j}",
            "style": "dir",
            "display_name": "directional scan",
            "kappa_c2o": float(kappa_c2o),
            "kappa_o2c": float(kappa_o2c),
            "x_gate": x_gate_star,
        }
        for i, kappa_c2o in enumerate(ONE_TARGET_PARAM_VALUES)
        for j, kappa_o2c in enumerate(ONE_TARGET_PARAM_VALUES)
    ]

    tb_workers = min(len(tb_payloads), ONE_TARGET_START_SCAN_MAX_WORKERS)
    if tb_workers <= 1:
        tb_scan_rows = [_compute_one_target_parameter_scan_row(payload) for payload in tb_payloads]
    else:
        with ProcessPoolExecutor(max_workers=tb_workers, mp_context=ONE_TARGET_MP_CONTEXT) as executor:
            tb_scan_rows = list(executor.map(_compute_one_target_parameter_scan_row, tb_payloads))
    dir_workers = min(len(dir_payloads), ONE_TARGET_START_SCAN_MAX_WORKERS)
    if dir_workers <= 1:
        dir_scan_rows = [_compute_one_target_parameter_scan_row(payload) for payload in dir_payloads]
    else:
        with ProcessPoolExecutor(max_workers=dir_workers, mp_context=ONE_TARGET_MP_CONTEXT) as executor:
            dir_scan_rows = list(executor.map(_compute_one_target_parameter_scan_row, dir_payloads))
    tb_scan_rows.sort(key=lambda row: (float(row["kappa_bottom"]), float(row["kappa_top"])))
    dir_scan_rows.sort(key=lambda row: (float(row["kappa_o2c"]), float(row["kappa_c2o"])))

    cases = _build_one_target_canonical_cases(tb_scan_rows, dir_scan_rows)
    sym_shared = cases["sym_shared"]
    tb_sym_control = _build_one_target_case_from_spec(
        {
            "case": "tb_sym_control",
            "style": "tb",
            "display_name": "top/bottom symmetric control",
            "kappa_top": 0.002,
            "kappa_bottom": 0.002,
        }
    )
    committor_control = one_target_committor_control(sym_shared, q_star=0.5)
    sym_shared_gate = one_target_gate_anchor_exact(sym_shared, x_gate=x_gate_star)
    sym_shared_rollback = one_target_rollback_exact(sym_shared)
    tb_sym_gate = one_target_gate_anchor_exact(tb_sym_control, x_gate=x_gate_star)
    tb_sym_rollback = one_target_rollback_exact(tb_sym_control)
    symmetry_control = {
        "case_a": "sym_shared",
        "case_b": "tb_sym_control",
        "x_gate": int(x_gate_star),
        "max_npq_abs_diff": float(np.max(np.abs(np.asarray(sym_shared_gate["f_npq"]) - np.asarray(tb_sym_gate["f_npq"])))),
        "max_lr_abs_diff": float(np.max(np.abs(np.asarray(sym_shared_rollback["f_lr"]) - np.asarray(tb_sym_rollback["f_lr"])))),
        "max_side_abs_diff": float(np.max(np.abs(np.asarray(sym_shared_rollback["f_side"]) - np.asarray(tb_sym_rollback["f_side"])))),
        "max_total_abs_diff": max(
            abs(float(sym_shared_gate["totals"]["no_leak_total"]) - float(tb_sym_gate["totals"]["no_leak_total"])),
            abs(float(sym_shared_gate["totals"]["pre_gate_leak_total"]) - float(tb_sym_gate["totals"]["pre_gate_leak_total"])),
            abs(float(sym_shared_gate["totals"]["post_gate_leak_total"]) - float(tb_sym_gate["totals"]["post_gate_leak_total"])),
            abs(float(sym_shared_rollback["totals"]["rollback_total"]) - float(tb_sym_rollback["totals"]["rollback_total"])),
        ),
    }

    scan_dominant_counts: dict[str, dict[str, int]] = {}
    directional_stats: dict[str, dict[str, dict[str, Any]]] = {}
    for case_name, case in cases.items():
        gate_exact = one_target_gate_anchor_exact(case, x_gate=x_gate_star)
        rollback_exact = one_target_rollback_exact(case)
        peak2_gate = gate_exact["npq_window_props"]["peak2"]
        peak2_lr = rollback_exact["lr_window_props"]["peak2"]
        side_peak2 = rollback_exact["side_window_props"]["peak2"]
        representative_rows.append(
            {
                "case": case_name,
                "display_name": str(case["display_name"]),
                "style": str(case["case_style"]),
                "role": "standard" if case_name == "sym_shared" else "comparison",
                "x_gate": int(x_gate_star),
                "phase": int(case["res"].phase),
                "t_peak1": int(case["res"].t_peak1),
                "t_valley": int(case["res"].t_valley),
                "t_peak2": int(case["res"].t_peak2),
                "valley_over_max": float(case["res"].valley_over_max),
                "sep_peaks": float(case["res"].sep_peaks),
                "kappa_top": float(case.get("kappa_top", np.nan)),
                "kappa_bottom": float(case.get("kappa_bottom", np.nan)),
                "kappa_c2o": float(case.get("kappa_c2o", np.nan)),
                "kappa_o2c": float(case.get("kappa_o2c", np.nan)),
                "peak2_dominant_gate_family": max(peak2_gate, key=peak2_gate.get),
                "peak2_dominant_gate_frac": float(max(peak2_gate.values())),
                "peak2_dominant_rollback_class": max(peak2_lr, key=peak2_lr.get),
                "peak2_dominant_rollback_frac": float(max(peak2_lr.values())),
                **{label: float(peak2_gate[label]) for label in THREE_FAMILY_LABELS},
                **{label: float(peak2_lr[label]) for label in LR_STATE_LABELS},
                "no_leak_total": float(rollback_exact["totals"]["no_leak_total"]),
                "leak_total": float(rollback_exact["totals"]["leak_total"]),
                "rollback_total": float(rollback_exact["totals"]["rollback_total"]),
                **{label: float(side_peak2[label]) for label in SIDE_R_LABELS},
            }
        )
        for window_name, props in gate_exact["npq_window_props"].items():
            gate_window_rows.append({"case": case_name, "x_gate": int(x_gate_star), "window": window_name, **props})
        for window_name, props in rollback_exact["lr_window_props"].items():
            rollback_window_rows.append({"case": case_name, "window": window_name, **props})
        for window_name, props in rollback_exact["side_window_props"].items():
            side_rows.append({"case": case_name, "window": window_name, **props})

        stats = compute_one_target_window_path_statistics(case, Lx=int(case["Lx"]), windows=rollback_exact["windows"])
        if stats:
            directional_stats[case_name] = stats

        case_scan_rows: list[dict[str, Any]] = []
        dominant_counts = {label: 0 for label in THREE_FAMILY_LABELS}
        scan_payloads = [{**_one_target_case_build_spec(case_name, case), "x_gate": int(x_gate)} for x_gate in range(int(case["start"][0]) + 2, int(case["target"][0]))]
        scan_workers = min(len(scan_payloads), ONE_TARGET_START_SCAN_MAX_WORKERS)
        if scan_workers <= 1:
            case_scan_rows = [_compute_one_target_gate_scan_row(payload) for payload in scan_payloads]
        else:
            with ProcessPoolExecutor(max_workers=scan_workers, mp_context=ONE_TARGET_MP_CONTEXT) as executor:
                case_scan_rows = list(executor.map(_compute_one_target_gate_scan_row, scan_payloads))
        case_scan_rows.sort(key=lambda row: int(row["X_g"]))
        for row in case_scan_rows:
            dominant_counts[str(row["dominant_family"])] += 1
            gate_scan_rows.append(row)
            eq = one_target_line_vs_halfspace_control(case, x_gate=int(row["X_g"]))
            equivalence_rows.append(
                {
                    "case": case_name,
                    "X_g": int(row["X_g"]),
                    "max_family_abs_diff": float(eq["max_family_abs_diff"]),
                    "max_lr_abs_diff": float(eq["max_lr_abs_diff"]),
                    "max_side_abs_diff": float(eq["max_side_abs_diff"]),
                    "max_total_abs_diff": float(eq["max_total_abs_diff"]),
                }
            )
        scan_dominant_counts[case_name] = dominant_counts

        verification_rows.append(
            {
                "case": case_name,
                "phase": int(case["res"].phase),
                "sep_peaks": float(case["res"].sep_peaks),
                "peak2_dominant_gate_family": max(peak2_gate, key=peak2_gate.get),
                "peak2_dominant_rollback_class": max(peak2_lr, key=peak2_lr.get),
                "rollback_total": float(rollback_exact["totals"]["rollback_total"]),
                "peak2_L0R1_plus_L1R1": float(peak2_lr["L0R1"] + peak2_lr["L1R1"]),
                "x_gate_scan_P_min": min(float(r["P"]) for r in case_scan_rows),
                "x_gate_scan_P_max": max(float(r["P"]) for r in case_scan_rows),
                "x_gate_scan_Q_min": min(float(r["Q"]) for r in case_scan_rows),
                "x_gate_scan_Q_max": max(float(r["Q"]) for r in case_scan_rows),
                "x_gate_scan_rollback_min": min(float(r["rollback_total"]) for r in case_scan_rows),
                "x_gate_scan_rollback_max": max(float(r["rollback_total"]) for r in case_scan_rows),
            }
        )

        start_scan_rows.extend(build_one_target_start_scan_rows(case_name, case, x_gate=x_gate_star))

    for q_star in ONE_TARGET_COMMITTOR_QSTARS:
        control = one_target_committor_control(sym_shared, q_star=q_star)
        peak2 = control["window_props"]["peak2"]
        committor_control_rows.append(
            {
                "case": "sym_shared",
                "q_star": float(q_star),
                "window": "peak2",
                "L0R0": float(peak2["L0R0"]),
                "L0R1": float(peak2["L0R1"]),
                "L1R0": float(peak2["L1R0"]),
                "L1R1": float(peak2["L1R1"]),
                "dominant": max(peak2, key=peak2.get),
            }
        )

    for case_name in cases:
        phase0_rows.extend(_summarize_phase0_examples(start_scan_rows, case_name=case_name))

    return {
        "canonical_cases": cases,
        "representative_rows": representative_rows,
        "gate_scan_rows": gate_scan_rows,
        "gate_window_rows": gate_window_rows,
        "rollback_window_rows": rollback_window_rows,
        "side_rows": side_rows,
        "start_scan_rows": start_scan_rows,
        "phase0_rows": phase0_rows,
        "committor_control_rows": committor_control_rows,
        "equivalence_rows": equivalence_rows,
        "verification_rows": verification_rows,
        "tb_scan_rows": tb_scan_rows,
        "dir_scan_rows": dir_scan_rows,
        "directional_stats": directional_stats,
        "symmetry_control": symmetry_control,
        "schematic_payload": {
            "case": sym_shared,
            "q_values": committor_control["q_values"],
            "set_A": committor_control["set_A"],
            "q_star": 0.5,
        },
        "summary": {
            "x_gate_star": int(x_gate_star),
            "x_gate_scan_min": int(ONE_TARGET_BASE_ARGS["start_x"]) + 2,
            "x_gate_scan_max": int(ONE_TARGET_BASE_ARGS["target_x"]) - 1,
            "standard_case": "sym_shared",
            "comparison_cases": [
                "tb_asym_balanced",
                "dir_asym_easy_out_balanced",
                "dir_asym_easy_in_balanced",
            ],
            "representative_selection_rule": (
                "prefer phase-2 interior points nearest to fixed balanced anchors, "
                "with tie-breaks by phase, separation, and parameter distance"
            ),
            "scan_dominant_family_counts": scan_dominant_counts,
            "equivalence_max_abs_diff": max(float(row["max_family_abs_diff"]) for row in equivalence_rows),
            "symmetry_control": symmetry_control,
            "start_phase_counts": {
                case_name: {
                    str(phase): sum(1 for row in start_scan_rows if row["case"] == case_name and int(row["phase"]) == phase)
                    for phase in sorted({int(r["phase"]) for r in start_scan_rows if r["case"] == case_name})
                }
                for case_name in cases
            },
            "tb_phase0_count": int(sum(int(row["phase"]) == 0 for row in tb_scan_rows)),
            "dir_phase0_count": int(sum(int(row["phase"]) == 0 for row in dir_scan_rows)),
            "representatives": {
                row["case"]: {
                    "phase": int(row["phase"]),
                    "sep_peaks": float(row["sep_peaks"]),
                    "rollback_total": float(row["rollback_total"]),
                }
                for row in representative_rows
            },
        },
    }


def write_two_target_case_payload(
    *,
    case_name: str,
    case: Any,
    exact: Any,
    mc_summary: Any,
    committor_audit: dict[str, Any],
) -> None:
    case_data_dir = DATA_DIR / "representatives" / case_name
    case_fig_dir = FIG_DIR / "representatives" / case_name
    ensure_dir(case_data_dir)
    ensure_dir(case_fig_dir)

    plot_geometry_with_gates(case, exact, case_fig_dir / f"{case_name}_geometry_gates.pdf")
    plot_branch_fpt(case, case_fig_dir / f"{case_name}_branch_fpt.pdf")
    plot_family_fpt(case, exact, case_fig_dir / f"{case_name}_family_fpt_coarse.pdf", coarse=True)
    plot_family_fpt(case, exact, case_fig_dir / f"{case_name}_family_fpt_fine.pdf", coarse=False)
    plot_window_composition(case, exact, case_fig_dir / f"{case_name}_window_composition.pdf")
    plot_side_usage(case, mc_summary, case_fig_dir / f"{case_name}_side_usage.pdf")

    save_case_timeseries(case, exact, case_data_dir / f"{case_name}_timeseries.csv")
    write_json(case_data_dir / f"{case_name}_metrics.json", case_metrics_dict(case, exact, mc_summary))
    write_json(case_data_dir / f"{case_name}_committor_audit.json", committor_audit)

    family_rows: list[dict[str, Any]] = []
    for label, value in zip(["N_direct", "N_detour", "F_clean", "F_linger", "F_rollback"], exact.masses_fine):
        family_rows.append({"level": "fine", "family": label, "mass": float(value)})
    for label, value in zip(["N_direct", "N_detour", "F_no_return", "F_rollback"], exact.masses_coarse):
        family_rows.append({"level": "coarse", "family": label, "mass": float(value)})
    write_csv(case_data_dir / f"{case_name}_family_masses.csv", family_rows, ["level", "family", "mass"])

    window_rows: list[dict[str, Any]] = []
    for window_name, frac in exact.peak_window_frac_fine.items():
        for family_idx, family in enumerate(["N_direct", "N_detour", "F_clean", "F_linger", "F_rollback"]):
            window_rows.append(
                {
                    "level": "fine",
                    "window": window_name,
                    "family": family,
                    "fraction": float(frac[family_idx]),
                }
            )
    for window_name, frac in exact.peak_window_frac_coarse.items():
        for family_idx, family in enumerate(["N_direct", "N_detour", "F_no_return", "F_rollback"]):
            window_rows.append(
                {
                    "level": "coarse",
                    "window": window_name,
                    "family": family,
                    "fraction": float(frac[family_idx]),
                }
            )
    write_csv(case_data_dir / f"{case_name}_window_fractions.csv", window_rows, ["level", "window", "family", "fraction"])

    event_fieldnames = ["family", "n", "mass_mc", "mass_exact", "abs_err", "t_escape_med"]
    progress_fields = sorted(
        {key for row in mc_summary.events_rows for key in row.keys() if key.startswith("t_x")},
        key=lambda key: int(key.split("_x", 1)[1].split("_", 1)[0]),
    )
    event_fieldnames.extend(progress_fields)
    event_fieldnames.append("t_hit_med")
    event_rows = []
    for row in mc_summary.events_rows:
        payload = {key: row.get(key, "") for key in event_fieldnames}
        event_rows.append(payload)
    write_csv(case_data_dir / f"{case_name}_mc_events.csv", event_rows, event_fieldnames)
    write_csv(case_data_dir / f"{case_name}_mc_side_usage.csv", mc_summary.side_rows, ["family", "lower", "center", "upper"])

def build_two_target_grid_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for d in range(2, 11):
        for dy in range(0, 7):
            case = build_case(name=f"d{d}_dy{dy}_bx+0.12", near_dx=d, near_dy=dy, bx=0.12, t_max=TWO_TARGET_SCAN_T_MAX)
            exact = run_family_exact(case, DEFAULT_TWO_TARGET_GATE, t_max=len(case.f_total) - 1)
            peak1_name = exact.peak_windows[0][0]
            peak2_name = exact.peak_windows[-1][0]
            rows.append(
                {
                    "d": int(d),
                    "dy": int(dy),
                    "phase": int(case.phase),
                    "p_near": float(case.p_near),
                    "p_far": float(case.p_far),
                    "window1_name": peak1_name,
                    "windowL_name": peak2_name,
                    "window1_N_direct": float(exact.peak_window_frac_coarse[peak1_name][0]),
                    "windowL_F_no_return": float(exact.peak_window_frac_coarse[peak2_name][2]),
                    "windowL_F_rollback": float(exact.peak_window_frac_coarse[peak2_name][3]),
                    "late_family": exact.late_family_coarse,
                    "sep_mode": float(case.sep_mode),
                    "sep_gate_coarse": float(exact.sep_gate_coarse),
                    "peak_ratio": None if case.peak_ratio is None else float(case.peak_ratio),
                    "valley_over_max": None if case.valley_over_max is None else float(case.valley_over_max),
                    "t_peak1": None if case.t_peak1 is None else int(case.t_peak1),
                    "t_valley": None if case.t_valley is None else int(case.t_valley),
                    "t_peak2": None if case.t_peak2 is None else int(case.t_peak2),
                }
            )
    return rows


def build_two_target_scan_rows(*, x_name: str, x_values: Iterable[int], fixed_name: str, fixed_value: int, bx: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for x_value in x_values:
        kwargs = {"near_dx": fixed_value, "near_dy": fixed_value, "bx": bx}
        kwargs["near_dx" if x_name == "d" else "near_dy"] = int(x_value)
        kwargs["near_dx" if fixed_name == "d" else "near_dy"] = int(fixed_value)
        case = build_case(
            name=f"{x_name}{x_value}_{fixed_name}{fixed_value}_bx{bx:+.2f}",
            near_dx=int(kwargs["near_dx"]),
            near_dy=int(kwargs["near_dy"]),
            bx=bx,
            t_max=TWO_TARGET_SCAN_T_MAX,
        )
        exact = run_family_exact(case, DEFAULT_TWO_TARGET_GATE, t_max=len(case.f_total) - 1)
        peak2_name = exact.peak_windows[-1][0]
        rows.append(
            {
                x_name: int(x_value),
                "phase": int(case.phase),
                "p_near": float(case.p_near),
                "p_far": float(case.p_far),
                "sep_mode": float(case.sep_mode),
                "N_direct": float(exact.masses_coarse[0]),
                "N_detour": float(exact.masses_coarse[1]),
                "F_no_return": float(exact.masses_coarse[2]),
                "F_rollback": float(exact.masses_coarse[3]),
                "early_family": exact.early_family_coarse,
                "late_family": exact.late_family_coarse,
                "sep_gate": float(exact.sep_gate_coarse),
                "peak2_no_return_frac": float(exact.peak_window_frac_coarse[peak2_name][2]),
            }
        )
    return rows


def build_two_target_datasets() -> dict[str, Any]:
    representative_rows: list[dict[str, Any]] = []
    validation_rows: list[dict[str, Any]] = []
    verification_rows: list[dict[str, Any]] = []
    case_metrics_rows: list[dict[str, Any]] = []
    progress_rows: list[dict[str, Any]] = []
    side_rows: list[dict[str, Any]] = []
    representative_case_payloads: list[tuple[Any, Any]] = []

    case_outputs: dict[str, dict[str, Any]] = {}
    for seed_offset, (case_name, spec) in enumerate(TWO_TARGET_CASE_SPECS.items()):
        case = build_case(name=case_name, near_dx=spec["near_dx"], near_dy=spec["near_dy"], bx=spec["bx"], t_max=TWO_TARGET_REP_T_MAX)
        exact = run_family_exact(case, DEFAULT_TWO_TARGET_GATE, t_max=len(case.f_total) - 1)
        comm = committor_diagnostics(case)
        mc_raw = run_mc(case, DEFAULT_TWO_TARGET_GATE, n_walkers=TWO_TARGET_MC_WALKERS, seed=TWO_TARGET_MC_SEED0 + seed_offset, t_max=TWO_TARGET_SCAN_T_MAX)
        mc_summary = summarize_mc(case, exact, mc_raw)
        representative_case_payloads.append((case, mc_summary))
        case_outputs[case_name] = {"case": case, "exact": exact, "mc_summary": mc_summary, "comm": comm}

        peak1_name = exact.peak_windows[0][0]
        peak2_name = exact.peak_windows[-1][0]
        representative_rows.append(
            {
                "case": case_name,
                "phase": int(case.phase),
                "p_near": float(case.p_near),
                "p_far": float(case.p_far),
                "t_peak1": int(case.t_peak1) if case.t_peak1 is not None else None,
                "t_valley": int(case.t_valley) if case.t_valley is not None else None,
                "t_peak2": int(case.t_peak2) if case.t_peak2 is not None else None,
                "valley_over_max": None if case.valley_over_max is None else float(case.valley_over_max),
                "sep_mode": float(case.sep_mode),
                "sep_gate_coarse": float(exact.sep_gate_coarse),
                "N_direct": float(exact.masses_coarse[0]),
                "N_detour": float(exact.masses_coarse[1]),
                "F_no_return": float(exact.masses_coarse[2]),
                "F_rollback": float(exact.masses_coarse[3]),
                "peak1_N_direct": float(exact.peak_window_frac_coarse[peak1_name][0]),
                "peak2_F_no_return": float(exact.peak_window_frac_coarse[peak2_name][2]),
                "peak2_F_rollback": float(exact.peak_window_frac_coarse[peak2_name][3]),
                "F_no_return_gt_N_direct": first_true_index(exact.family_flux_coarse[:, 2] > exact.family_flux_coarse[:, 0]),
                "far_total_gt_near_total": first_true_index(case.f_far > case.f_near),
                "rollback_gt_detour": first_true_index(exact.family_flux_coarse[:, 3] > exact.family_flux_coarse[:, 1]),
                "mc_max_abs_err": float(np.max(mc_summary.family_abs_err)),
            }
        )
        validation_rows.append(
            {
                "name": case_name,
                "q_far_start": float(comm["q_far_start"]),
                "p_far": float(case.p_far),
                "q_far_gap_vs_p_far": float(comm["consistency_gap_vs_p_far"]),
                "closure_max_abs": float(exact.closure_max_abs),
                "mc_max_family_abs_err": float(np.max(mc_summary.family_abs_err)),
            }
        )
        source = SOURCE_TWO_TARGET_EXPECTATIONS[case_name]
        verification_rows.append(
            {
                "case": case_name,
                "source_phase": int(source["phase"]),
                "recomputed_phase": int(case.phase),
                "source_p_far": float(source["p_far"]),
                "recomputed_p_far": float(case.p_far),
                "q_far_start": float(comm["q_far_start"]),
                "q_far_gap_vs_p_far": float(comm["consistency_gap_vs_p_far"]),
                "source_t_peak2": int(source["t_peak2"]),
                "recomputed_t_peak2": int(case.t_peak2) if case.t_peak2 is not None else None,
                "source_sep_gate_coarse": float(source["sep_gate_coarse"]),
                "recomputed_sep_gate_coarse": float(exact.sep_gate_coarse),
                "source_late_family_coarse": source["late_family_coarse"],
                "late_family_coarse": exact.late_family_coarse,
                "peak2_F_no_return_frac": float(exact.peak_window_frac_coarse[peak2_name][2]),
                "peak2_F_rollback_frac": float(exact.peak_window_frac_coarse[peak2_name][3]),
                "closure_max_abs": float(exact.closure_max_abs),
                "mc_branch_near": float(mc_summary.branch_near_mc),
                "mc_branch_far": float(mc_summary.branch_far_mc),
                "mc_max_family_abs_err": float(np.max(mc_summary.family_abs_err)),
            }
        )
        case_metrics_rows.append(case_metrics_dict(case, exact, mc_summary))
        for row in mc_summary.events_rows:
            progress_rows.append({"case": case_name, **row})
        for row in mc_summary.side_rows:
            side_rows.append({"case": case_name, **row})
        write_two_target_case_payload(
            case_name=case_name,
            case=case,
            exact=exact,
            mc_summary=mc_summary,
            committor_audit=comm,
        )

    grid_rows = build_two_target_grid_rows()
    scan_dy_rows = build_two_target_scan_rows(x_name="dy", x_values=range(0, 7), fixed_name="d", fixed_value=2, bx=0.12)
    scan_d_rows = build_two_target_scan_rows(x_name="d", x_values=range(2, 11), fixed_name="dy", fixed_value=2, bx=0.12)
    robustness_rows = run_gate_robustness(case_outputs["anchor"]["case"], ring_vals=[1, 2, 3], out_offsets=[1, 2, 3])

    phase_counts: dict[str, int] = {}
    phase_ge_1_rows = []
    for row in grid_rows:
        phase_key = str(int(row["phase"]))
        phase_counts[phase_key] = phase_counts.get(phase_key, 0) + 1
        if int(row["phase"]) >= 1:
            phase_ge_1_rows.append(row)

    late_purity = np.asarray([float(row["windowL_F_no_return"]) for row in phase_ge_1_rows], dtype=np.float64)
    late_families = sorted({str(row["late_family"]) for row in phase_ge_1_rows})
    sep_gate_vals = np.asarray([float(row["sep_gate_coarse"]) for row in phase_ge_1_rows], dtype=np.float64)

    return {
        "representative_rows": representative_rows,
        "validation_rows": validation_rows,
        "verification_rows": verification_rows,
        "case_metrics_rows": case_metrics_rows,
        "progress_rows": progress_rows,
        "side_rows": side_rows,
        "grid_rows": grid_rows,
        "scan_dy_rows": scan_dy_rows,
        "scan_d_rows": scan_d_rows,
        "robustness_rows": robustness_rows,
        "representative_case_payloads": representative_case_payloads,
        "summary": {
            "grid_points": len(grid_rows),
            "phase_counts": phase_counts,
            "phase_ge_1_points": len(phase_ge_1_rows),
            "late_family_all_phase_ge_1": late_families[0] if len(late_families) == 1 else "mixed",
            "late_f_no_return_range": [float(np.min(late_purity)), float(np.max(late_purity))],
            "late_f_no_return_mean": float(np.mean(late_purity)),
            "sep_gate_coarse_range": [float(np.min(sep_gate_vals)), float(np.max(sep_gate_vals))],
        },
    }


def write_report_figures(one_target: dict[str, Any], two_target: dict[str, Any]) -> None:
    plot_phase_v2_flow(FIG_DIR / "gating_game_phase_v2_flow.pdf")
    schematic = one_target["schematic_payload"]
    if schematic is None:
        raise RuntimeError("missing one-target schematic payload")
    plot_one_target_gate_geometry(
        FIG_DIR / "one_target_gate_geometry.pdf",
        case=schematic["case"],
        x_gate=int(one_target["summary"]["x_gate_star"]),
    )
    plot_one_target_class_crosswalk(FIG_DIR / "one_target_class_crosswalk.pdf")
    rep_lookup = {row["case"]: row for row in one_target["representative_rows"]}
    tb_markers = [
        ("S", 0.002, 0.002, "#1b5e20"),
        ("B", float(rep_lookup["tb_asym_balanced"]["kappa_top"]), float(rep_lookup["tb_asym_balanced"]["kappa_bottom"]), "#b71c1c"),
    ]
    dir_markers = [
        ("S", 0.002, 0.002, "#1b5e20"),
        ("Eout", float(rep_lookup["dir_asym_easy_out_balanced"]["kappa_c2o"]), float(rep_lookup["dir_asym_easy_out_balanced"]["kappa_o2c"]), "#b71c1c"),
        ("Ein", float(rep_lookup["dir_asym_easy_in_balanced"]["kappa_c2o"]), float(rep_lookup["dir_asym_easy_in_balanced"]["kappa_o2c"]), "#0d47a1"),
    ]
    plot_one_target_parameter_phase_map(
        one_target["tb_scan_rows"],
        FIG_DIR / "one_target_tb_phase_map.pdf",
        x_key="kappa_top",
        y_key="kappa_bottom",
        x_label=r"$\kappa_{\mathrm{top}}$",
        y_label=r"$\kappa_{\mathrm{bottom}}$",
        title="Top/bottom membrane scan: phase map",
        marker_points=tb_markers,
    )
    plot_one_target_parameter_sep_map(
        one_target["tb_scan_rows"],
        FIG_DIR / "one_target_tb_sep_map.pdf",
        x_key="kappa_top",
        y_key="kappa_bottom",
        x_label=r"$\kappa_{\mathrm{top}}$",
        y_label=r"$\kappa_{\mathrm{bottom}}$",
        title="Top/bottom membrane scan: separation map",
        marker_points=tb_markers,
    )
    plot_one_target_parameter_phase_map(
        one_target["dir_scan_rows"],
        FIG_DIR / "one_target_dir_phase_map.pdf",
        x_key="kappa_c2o",
        y_key="kappa_o2c",
        x_label=r"$\kappa_{c\to o}$",
        y_label=r"$\kappa_{o\to c}$",
        title="Same-membrane directional scan: phase map",
        marker_points=dir_markers,
    )
    plot_one_target_parameter_sep_map(
        one_target["dir_scan_rows"],
        FIG_DIR / "one_target_dir_sep_map.pdf",
        x_key="kappa_c2o",
        y_key="kappa_o2c",
        x_label=r"$\kappa_{c\to o}$",
        y_label=r"$\kappa_{o\to c}$",
        title="Same-membrane directional scan: separation map",
        marker_points=dir_markers,
    )
    plot_one_target_gate_scan_families(one_target["gate_scan_rows"], FIG_DIR / "one_target_gate_scan_families.pdf")
    plot_one_target_gate_scan_totals(one_target["gate_scan_rows"], FIG_DIR / "one_target_gate_scan_totals.pdf")
    plot_one_target_rollback_window_bars(one_target["rollback_window_rows"], FIG_DIR / "one_target_rollback_window_bars.pdf")
    plot_one_target_window_families(one_target["gate_window_rows"], FIG_DIR / "one_target_window_families.pdf")
    plot_one_target_side_window_bars(one_target["side_rows"], FIG_DIR / "one_target_side_window_bars.pdf")
    plot_one_target_start_phase_map(one_target["start_scan_rows"], FIG_DIR / "one_target_start_phase_map.pdf")
    directional_case_blocks = [
        (str(one_target["canonical_cases"][case_name]["display_name"]), one_target["canonical_cases"][case_name], one_target["directional_stats"].get(case_name, {}))
        for case_name in ["sym_shared", "dir_asym_easy_out_balanced", "dir_asym_easy_in_balanced"]
        if case_name in one_target["canonical_cases"]
    ]
    plot_one_target_window_occupancy_atlas(
        FIG_DIR / "one_target_directional_window_occupancy_atlas.pdf",
        Lx=int(schematic["case"]["Lx"]),
        case_blocks=directional_case_blocks,
    )
    plot_one_target_directional_flux(
        FIG_DIR / "one_target_directional_window_flux.pdf",
        case_blocks=[(label, stats) for label, _, stats in directional_case_blocks],
    )
    plot_one_target_gate_schematic(
        FIG_DIR / "one_target_committor_control_geometry.pdf",
        case=schematic["case"],
        q_values=schematic["q_values"],
        basin_mask=schematic["set_A"],
        q_star=float(schematic["q_star"]),
    )
    plot_two_target_extension(FIG_DIR / "gating_game_two_target_extension.pdf")
    plot_unified_mechanism_ladder(FIG_DIR / "unified_mechanism_ladder.pdf")

    plot_two_target_phase_atlas(two_target["grid_rows"], FIG_DIR / "two_target_dx_dy_phase_purity.pdf")
    plot_scan_family_lines(two_target["scan_dy_rows"], x_col="dy", title="Two-target scan at d=2, bx=0.12", out_path=FIG_DIR / "two_target_scan_dy_d2_bx0p12.pdf")
    plot_scan_family_lines(two_target["scan_d_rows"], x_col="d", title="Two-target scan at dy=2, bx=0.12", out_path=FIG_DIR / "two_target_scan_d_dy2_bx0p12.pdf")
    plot_progress_medians(two_target["progress_rows"], FIG_DIR / "two_target_progress_medians.pdf")
    plot_first_escape_side_usage(two_target["side_rows"], FIG_DIR / "two_target_first_escape_side_usage.pdf")
    plot_mc_vs_exact(two_target["representative_case_payloads"], FIG_DIR / "two_target_mc_vs_exact.pdf")
    plot_robustness_heatmap(two_target["robustness_rows"], FIG_DIR / "two_target_anchor_gate_robustness.pdf")


def run_auxiliary_script(script_name: str, *args: str) -> None:
    cmd = [sys.executable, str(REPORT_ROOT / "code" / script_name), *args]
    subprocess.run(cmd, cwd=str(REPORT_ROOT), check=True)


def build_left_open_split_datasets() -> dict[str, Any]:
    run_auxiliary_script("one_target_sensitivity_scan.py", "--scan", "all")
    run_auxiliary_script("one_target_left_open_split.py")

    cases_rows = read_csv(SENSITIVITY_DIR / "one_target_left_open_split_cases.csv")
    window_rows_raw = read_csv(SENSITIVITY_DIR / "one_target_left_open_split_windows.csv")
    event_rows = read_csv(SENSITIVITY_DIR / "one_target_left_open_split_events.csv")

    case_labels = {
        "width_h2_bx_m0p08": "baseline ($h=2$, $b_x=-0.08$)",
        "width_h4_bx_m0p08": "wide corridor ($h=4$, $b_x=-0.08$)",
        "width_h0_bx_m0p04": "narrow weak-drag ($h=0$, $b_x=-0.04$)",
        "delta_core_p1p00_open_p0p80": r"strong corridor push ($\delta_c=1.0$, $\delta_o=0.8$)",
        "delta_core_p0p80_open_p0p00": r"weak corridor push ($\delta_c=0.8$, $\delta_o=0.0$)",
    }
    table_labels = {
        "width_h2_bx_m0p08": "baseline",
        "width_h4_bx_m0p08": "wide corridor",
        "width_h0_bx_m0p04": "narrow weak-drag",
        "delta_core_p1p00_open_p0p80": "strong corridor push",
        "delta_core_p0p80_open_p0p00": "weak corridor push",
    }
    figure_case_ids = [
        "width_h2_bx_m0p08",
        "width_h4_bx_m0p08",
        "delta_core_p0p80_open_p0p00",
    ]
    summary_case_ids = [
        "width_h2_bx_m0p08",
        "width_h4_bx_m0p08",
        "width_h0_bx_m0p04",
        "delta_core_p1p00_open_p0p80",
        "delta_core_p0p80_open_p0p00",
    ]

    def _f(row: dict[str, str], key: str) -> float:
        return float(row[key])

    def _i(row: dict[str, str], key: str) -> int:
        return int(row[key])

    window_rows: list[dict[str, Any]] = []
    for row in window_rows_raw:
        payload = dict(row)
        payload["display_name"] = case_labels.get(str(row["case_id"]), str(row["case_id"]))
        window_rows.append(payload)

    phase_summary: dict[str, dict[str, float]] = {}
    for phase in sorted({int(row["phase"]) for row in cases_rows}):
        phase_rows = [row for row in cases_rows if int(row["phase"]) == phase]
        if not phase_rows:
            continue
        phase_summary[str(phase)] = {
            "count": float(len(phase_rows)),
            "late_left_only_mean": float(np.mean([_f(row, "late_left_only") for row in phase_rows])),
            "late_mem_only_mean": float(np.mean([_f(row, "late_mem_only") for row in phase_rows])),
            "late_both_mean": float(np.mean([_f(row, "late_both") for row in phase_rows])),
            "late_none_mean": float(np.mean([_f(row, "late_none") for row in phase_rows])),
            "late_tau_left_prob_mean": float(np.mean([_f(row, "late_tau_left_prob") for row in phase_rows])),
            "late_tau_mem_prob_mean": float(np.mean([_f(row, "late_tau_mem_prob") for row in phase_rows])),
        }

    baseline_window_rows = [row for row in window_rows if str(row["case_id"]) == "width_h2_bx_m0p08"]
    summary_rows = []
    for case_id in summary_case_ids:
        row = next(row for row in cases_rows if str(row["case_id"]) == case_id)
        summary_rows.append(
            {
                "case_id": case_id,
                "display_name": case_labels.get(case_id, case_id),
                "table_name": table_labels.get(case_id, case_id),
                "phase": _i(row, "phase"),
                "sep_peaks": _f(row, "sep_peaks"),
                "t_peak2": _i(row, "t_peak2"),
                "late_left_only": _f(row, "late_left_only"),
                "late_mem_only": _f(row, "late_mem_only"),
                "late_both": _f(row, "late_both"),
                "late_tau_left_prob": _f(row, "late_tau_left_prob"),
                "late_tau_mem_prob": _f(row, "late_tau_mem_prob"),
            }
        )

    return {
        "cases_rows": cases_rows,
        "window_rows": window_rows,
        "event_rows": event_rows,
        "figure_rows": [row for row in window_rows if str(row["case_id"]) in figure_case_ids],
        "figure_case_ids": figure_case_ids,
        "summary_rows": summary_rows,
        "baseline_window_rows": baseline_window_rows,
        "phase_summary": phase_summary,
    }


def write_tables(one_target: dict[str, Any], two_target: dict[str, Any], left_open: dict[str, Any]) -> None:
    def _param_text(row: dict[str, Any]) -> str:
        if str(row["style"]) == "tb":
            return rf"$(\kappa_{{top}},\kappa_{{bottom}})=({fmt_num(row['kappa_top'],4)},{fmt_num(row['kappa_bottom'],4)})$"
        return rf"$(\kappa_{{c\to o}},\kappa_{{o\to c}})=({fmt_num(row['kappa_c2o'],4)},{fmt_num(row['kappa_o2c'],4)})$"

    write_tabular(
        TABLE_DIR / "one_target_representative.tex",
        ["case", "role", "parameters", "phase", "sep", "peak2 rollback", "peak2 gate", "rollback"],
        [
            [
                latex_escape(row["display_name"]),
                latex_escape(row["role"]),
                _param_text(row),
                latex_escape(row["phase"]),
                fmt_num(row["sep_peaks"]),
                latex_escape(row["peak2_dominant_rollback_class"]),
                latex_escape(row["peak2_dominant_gate_family"]),
                fmt_pct(row["rollback_total"]),
            ]
            for row in one_target["representative_rows"]
        ],
        "lllrrllr",
    )

    gate_scan_lookup: dict[str, list[dict[str, Any]]] = {}
    for row in one_target["gate_scan_rows"]:
        gate_scan_lookup.setdefault(str(row["case"]), []).append(row)
    write_tabular(
        TABLE_DIR / "one_target_gate_scan_summary.tex",
        ["case", "scan range", "dom. $N$", "$P$ range", "$Q$ range", "rollback range"],
        [
            [
                latex_escape(one_target["canonical_cases"][case_name]["display_name"]),
                latex_escape(f"{one_target['summary']['x_gate_scan_min']}..{one_target['summary']['x_gate_scan_max']}"),
                latex_escape(one_target["summary"]["scan_dominant_family_counts"][case_name]["N"]),
                (
                    f"{fmt_pct(min(float(row['P']) for row in gate_scan_lookup[case_name]),1)}--{fmt_pct(max(float(row['P']) for row in gate_scan_lookup[case_name]),1)}"
                ),
                (
                    f"{fmt_pct(min(float(row['Q']) for row in gate_scan_lookup[case_name]),1)}--{fmt_pct(max(float(row['Q']) for row in gate_scan_lookup[case_name]),1)}"
                ),
                (
                    f"{fmt_pct(min(float(row['rollback_total']) for row in gate_scan_lookup[case_name]),1)}--{fmt_pct(max(float(row['rollback_total']) for row in gate_scan_lookup[case_name]),1)}"
                ),
            ]
            for case_name in sorted(one_target["summary"]["scan_dominant_family_counts"])
        ],
        "llrrrr",
    )

    phase0_lookup: dict[str, dict[str, tuple[int, int]]] = {}
    for row in one_target["phase0_rows"]:
        phase0_lookup.setdefault(str(row["case"]), {})[str(row["label"])] = (int(row["start_x"]), int(row["start_y"]))
    write_tabular(
        TABLE_DIR / "one_target_phase0_loss_summary.tex",
        ["case", "phase-0 onset", "off-axis loss", "target-adjacent collapse", "phase counts"],
        [
            [
                latex_escape(one_target["canonical_cases"][case_name]["display_name"]),
                latex_escape(str(phase0_lookup.get(case_name, {}).get("A", "-"))),
                latex_escape(str(phase0_lookup.get(case_name, {}).get("B", "-"))),
                latex_escape(str(phase0_lookup.get(case_name, {}).get("C", "-"))),
                latex_escape(
                    "/".join(
                        f"{phase}:{count}"
                        for phase, count in sorted(one_target["summary"]["start_phase_counts"][case_name].items(), key=lambda item: int(item[0]))
                    )
                ),
            ]
            for case_name in one_target["canonical_cases"]
        ],
        "lllll",
    )

    write_tabular(
        TABLE_DIR / "two_target_representative.tex",
        ["case", "phase", "$P_{near}$", "$P_{far}$", "$t_{p1}$", "$t_v$", "$t_{p2}$", "sep$_{gate}$"],
        [
            [
                latex_escape(row["case"]),
                latex_escape(row["phase"]),
                fmt_num(row["p_near"]),
                fmt_num(row["p_far"]),
                latex_escape(row["t_peak1"]),
                latex_escape(row["t_valley"]),
                latex_escape(row["t_peak2"]),
                fmt_num(row["sep_gate_coarse"]),
            ]
            for row in two_target["representative_rows"]
        ],
        "lrrrrrrr",
    )

    write_tabular(
        TABLE_DIR / "two_target_validation.tex",
        ["case", "$q_{far}(start)$", "$P_{far}$", "gap", "closure", "MC err"],
        [
            [
                latex_escape(row["name"]),
                fmt_num(row["q_far_start"], 6),
                fmt_num(row["p_far"], 6),
                fmt_num(row["q_far_gap_vs_p_far"], 6),
                fmt_num(row["closure_max_abs"], 6),
                fmt_num(row["mc_max_family_abs_err"], 6),
            ]
            for row in two_target["validation_rows"]
        ],
        "lrrrrr",
    )

    write_tabular(
        TABLE_DIR / "phase_counts.tex",
        ["phase", "count"],
        [[latex_escape(k), latex_escape(v)] for k, v in sorted(two_target["summary"]["phase_counts"].items(), key=lambda item: int(item[0]))],
        "rr",
    )

    write_tabular(
        TABLE_DIR / "verification_one_target.tex",
        ["case", "phase", "sep", "peak2 rollback share", "$P$ range", "$Q$ range", "rollback range"],
        [
            [
                latex_escape(one_target["canonical_cases"][str(row["case"])]["display_name"]),
                latex_escape(row["phase"]),
                fmt_num(row["sep_peaks"]),
                fmt_pct(row["peak2_L0R1_plus_L1R1"]),
                f"{fmt_pct(row['x_gate_scan_P_min'],1)}--{fmt_pct(row['x_gate_scan_P_max'],1)}",
                f"{fmt_pct(row['x_gate_scan_Q_min'],1)}--{fmt_pct(row['x_gate_scan_Q_max'],1)}",
                f"{fmt_pct(row['x_gate_scan_rollback_min'],1)}--{fmt_pct(row['x_gate_scan_rollback_max'],1)}",
            ]
            for row in one_target["verification_rows"]
        ],
        "lrrrrrr",
    )

    write_tabular(
        TABLE_DIR / "one_target_left_open_summary.tex",
        ["case", "phase", "sep", "$t_{p2}$", "left", "mem", "both", "$\\Pr(\\tau_l)$", "$\\Pr(\\tau_m)$"],
        [
            [
                row["table_name"],
                latex_escape(row["phase"]),
                fmt_num(row["sep_peaks"]),
                latex_escape(row["t_peak2"]),
                fmt_pct(row["late_left_only"]),
                fmt_pct(row["late_mem_only"]),
                fmt_pct(row["late_both"]),
                fmt_pct(row["late_tau_left_prob"]),
                fmt_pct(row["late_tau_mem_prob"]),
            ]
            for row in left_open["summary_rows"]
        ],
        "lrrrrrrrr",
    )

    write_tabular(
        TABLE_DIR / "verification_two_target.tex",
        ["case", "source $P_{far}$", "recheck $P_{far}$", "$q_{far}(start)$ gap", "late family", "MC err"],
        [
            [
                latex_escape(row["case"]),
                fmt_num(row["source_p_far"], 6),
                fmt_num(row["recomputed_p_far"], 6),
                fmt_num(row["q_far_gap_vs_p_far"], 6),
                latex_escape(row["late_family_coarse"]),
                fmt_num(row["mc_max_family_abs_err"], 4),
            ]
            for row in two_target["verification_rows"]
        ],
        "lrrrrr",
    )


def write_flat_data_exports(one_target: dict[str, Any], two_target: dict[str, Any]) -> None:
    write_csv(
        DATA_DIR / "one_target_representative_summary.csv",
        one_target["representative_rows"],
        [
            "case",
            "display_name",
            "role",
            "style",
            "x_gate",
            "phase",
            "t_peak1",
            "t_valley",
            "t_peak2",
            "valley_over_max",
            "sep_peaks",
            "kappa_top",
            "kappa_bottom",
            "kappa_c2o",
            "kappa_o2c",
            "peak2_dominant_gate_family",
            "peak2_dominant_gate_frac",
            "peak2_dominant_rollback_class",
            "peak2_dominant_rollback_frac",
            *THREE_FAMILY_LABELS,
            *LR_STATE_LABELS,
            "no_leak_total",
            "leak_total",
            "rollback_total",
            *SIDE_R_LABELS,
        ],
    )
    write_csv(
        DATA_DIR / "one_target_tb_scan.csv",
        one_target["tb_scan_rows"],
        [
            "scan_type",
            "kappa_top",
            "kappa_bottom",
            "phase",
            "t_peak1",
            "t_valley",
            "t_peak2",
            "valley_over_max",
            "sep_peaks",
            "rollback_total",
            "no_leak_total",
            "leak_total",
            "peak2_dominant_rollback_class",
            "peak2_dominant_rollback_frac",
            "peak2_dominant_gate_family",
            "peak2_dominant_gate_frac",
            *LR_STATE_LABELS,
            *THREE_FAMILY_LABELS,
        ],
    )
    write_csv(
        DATA_DIR / "one_target_dir_scan.csv",
        one_target["dir_scan_rows"],
        [
            "scan_type",
            "kappa_c2o",
            "kappa_o2c",
            "phase",
            "t_peak1",
            "t_valley",
            "t_peak2",
            "valley_over_max",
            "sep_peaks",
            "rollback_total",
            "no_leak_total",
            "leak_total",
            "peak2_dominant_rollback_class",
            "peak2_dominant_rollback_frac",
            "peak2_dominant_gate_family",
            "peak2_dominant_gate_frac",
            *LR_STATE_LABELS,
            *THREE_FAMILY_LABELS,
        ],
    )
    write_csv(
        DATA_DIR / "one_target_gate_scan.csv",
        one_target["gate_scan_rows"],
        [
            "case",
            "display_name",
            "style",
            "X_g",
            *THREE_FAMILY_LABELS,
            "dominant_family",
            "dominant_family_frac",
            "dominant_lr",
            "no_leak_total",
            "pre_gate_leak_total",
            "post_gate_leak_total",
            "rollback_total",
            "leak_total",
        ],
    )
    write_csv(
        DATA_DIR / "one_target_gate_window_families_xg_star.csv",
        one_target["gate_window_rows"],
        ["case", "x_gate", "window", *THREE_FAMILY_LABELS],
    )
    write_csv(
        DATA_DIR / "one_target_rollback_window_families.csv",
        one_target["rollback_window_rows"],
        ["case", "window", *LR_STATE_LABELS],
    )
    write_csv(
        DATA_DIR / "one_target_side_window_families_xg_star.csv",
        one_target["side_rows"],
        ["case", "window", *SIDE_R_LABELS],
    )
    write_csv(
        DATA_DIR / "one_target_start_scan.csv",
        one_target["start_scan_rows"],
        [
            "case",
            "display_name",
            "style",
            "base_start_x",
            "base_start_y",
            "target_x",
            "target_y",
            "x_gate",
            "start_x",
            "start_y",
            "phase",
            "t_peak1",
            "t_valley",
            "t_peak2",
            "valley_over_max",
            "sep_peaks",
        ],
    )
    write_csv(
        DATA_DIR / "one_target_phase0_examples.csv",
        one_target["phase0_rows"],
        ["case", "label", "description", "start_x", "start_y", "phase", "sep_peaks"],
    )
    write_csv(
        DATA_DIR / "one_target_line_vs_halfspace_control.csv",
        one_target["equivalence_rows"],
        ["case", "X_g", "max_family_abs_diff", "max_lr_abs_diff", "max_side_abs_diff", "max_total_abs_diff"],
    )
    write_csv(
        DATA_DIR / "one_target_symmetry_control.csv",
        [one_target["symmetry_control"]],
        ["case_a", "case_b", "x_gate", "max_npq_abs_diff", "max_lr_abs_diff", "max_side_abs_diff", "max_total_abs_diff"],
    )
    write_csv(
        DATA_DIR / "one_target_committor_control_peak2.csv",
        one_target["committor_control_rows"],
        ["case", "q_star", "window", "L0R0", "L0R1", "L1R0", "L1R1", "dominant"],
    )

    write_csv(
        DATA_DIR / "two_target_representative_summary.csv",
        two_target["representative_rows"],
        [
            "case",
            "phase",
            "p_near",
            "p_far",
            "t_peak1",
            "t_valley",
            "t_peak2",
            "valley_over_max",
            "sep_mode",
            "sep_gate_coarse",
            "N_direct",
            "N_detour",
            "F_no_return",
            "F_rollback",
            "peak1_N_direct",
            "peak2_F_no_return",
            "peak2_F_rollback",
            "F_no_return_gt_N_direct",
            "far_total_gt_near_total",
            "rollback_gt_detour",
            "mc_max_abs_err",
        ],
    )
    write_csv(
        DATA_DIR / "validation_summary.csv",
        two_target["validation_rows"],
        ["name", "q_far_start", "p_far", "q_far_gap_vs_p_far", "closure_max_abs", "mc_max_family_abs_err"],
    )
    write_csv(
        DATA_DIR / "case_metrics.csv",
        two_target["case_metrics_rows"],
        list(two_target["case_metrics_rows"][0].keys()),
    )
    write_csv(
        DATA_DIR / "two_target_d_dy_grid_scan.csv",
        two_target["grid_rows"],
        [
            "d",
            "dy",
            "phase",
            "p_near",
            "p_far",
            "window1_name",
            "windowL_name",
            "window1_N_direct",
            "windowL_F_no_return",
            "windowL_F_rollback",
            "late_family",
            "sep_mode",
            "sep_gate_coarse",
            "peak_ratio",
            "valley_over_max",
            "t_peak1",
            "t_valley",
            "t_peak2",
        ],
    )
    write_csv(
        DATA_DIR / "scan_dy_d2_bx0p12.csv",
        two_target["scan_dy_rows"],
        ["dy", "phase", "p_near", "p_far", "sep_mode", "N_direct", "N_detour", "F_no_return", "F_rollback", "early_family", "late_family", "sep_gate", "peak2_no_return_frac"],
    )
    write_csv(
        DATA_DIR / "scan_d_dy2_bx0p12.csv",
        two_target["scan_d_rows"],
        ["d", "phase", "p_near", "p_far", "sep_mode", "N_direct", "N_detour", "F_no_return", "F_rollback", "early_family", "late_family", "sep_gate", "peak2_no_return_frac"],
    )
    write_csv(
        DATA_DIR / "anchor_gate_robustness.csv",
        two_target["robustness_rows"],
        ["near_ring_radius", "x_out_offset", "early_family_fine", "late_family_fine", "early_family_coarse", "late_family_coarse", "sep_gate_coarse", "peak2_F_no_return_frac", "mass_F_rollback", "mass_F_no_return"],
    )

    progress_fieldnames = ["case", "family", "n", "mass_mc", "mass_exact", "abs_err", "t_escape_med"]
    progress_extra = sorted(
        {key for row in two_target["progress_rows"] for key in row.keys() if key.startswith("t_x")},
        key=lambda key: int(key.split("_x", 1)[1].split("_", 1)[0]),
    )
    progress_fieldnames.extend(progress_extra)
    progress_fieldnames.append("t_hit_med")
    progress_rows = [{key: row.get(key, "") for key in progress_fieldnames} for row in two_target["progress_rows"]]
    write_csv(DATA_DIR / "two_target_progress_stage_medians.csv", progress_rows, progress_fieldnames)
    write_csv(DATA_DIR / "two_target_far_side_usage.csv", two_target["side_rows"], ["family", "lower", "center", "upper", "case"])

    for case_name in TWO_TARGET_CASE_SPECS:
        case_dir = DATA_DIR / "representatives" / case_name
        src_events = case_dir / f"{case_name}_mc_events.csv"
        dst_events = DATA_DIR / f"two_target_{case_name}_mc_events.csv"
        dst_events.write_text(src_events.read_text(encoding="utf-8"), encoding="utf-8")
        src_side = case_dir / f"{case_name}_mc_side_usage.csv"
        dst_side = DATA_DIR / f"two_target_{case_name}_mc_side_usage.csv"
        dst_side.write_text(src_side.read_text(encoding="utf-8"), encoding="utf-8")


def write_outputs(one_target: dict[str, Any], two_target: dict[str, Any], analysis_summary: dict[str, Any]) -> None:
    write_json(DATA_DIR / "analysis_summary.json", analysis_summary)
    write_json(
        DATA_DIR / "source_lineage.json",
        {
            "source_chain": SOURCE_CHAIN,
            "archived_files": RAW_ARCHIVE_FILES,
            "raw_dir": str(RAW_DIR.relative_to(REPO_ROOT)),
            "canonical_report": "grid2d_one_two_target_gating",
            "canonical_modules": [
                "vkcore.grid2d.one_two_target_gating.one_target",
                "vkcore.grid2d.one_two_target_gating.two_target",
                "vkcore.grid2d.one_two_target_gating.phase_v2",
                "vkcore.grid2d.one_two_target_gating.plotting",
            ],
        },
    )
    verification_summary = {
        "source_chain": SOURCE_CHAIN,
        "one_target": {
            "representatives": one_target["verification_rows"],
            "symmetry_control": one_target["symmetry_control"],
            "max_peak2_rollback_share": max(float(row["peak2_L0R1_plus_L1R1"]) for row in one_target["verification_rows"]),
            "max_line_halfspace_abs_diff": max(float(row["max_family_abs_diff"]) for row in one_target["equivalence_rows"]),
        },
        "two_target": {
            "representatives": two_target["verification_rows"],
            "max_p_far_gap": max(abs(float(row["source_p_far"]) - float(row["recomputed_p_far"])) for row in two_target["verification_rows"]),
            "max_sep_gate_gap": max(abs(float(row["source_sep_gate_coarse"]) - float(row["recomputed_sep_gate_coarse"])) for row in two_target["verification_rows"]),
            "max_mc_family_abs_err": max(float(row["mc_max_family_abs_err"]) for row in two_target["verification_rows"]),
        },
    }
    write_json(DATA_DIR / "verification_summary.json", verification_summary)
    write_csv(OUT_DIR / "one_target_recheck.csv", one_target["verification_rows"], list(one_target["verification_rows"][0].keys()))
    write_csv(
        OUT_DIR / "one_target_gate_scan_recheck.csv",
        one_target["gate_scan_rows"],
        list(one_target["gate_scan_rows"][0].keys()),
    )
    write_csv(
        OUT_DIR / "one_target_line_vs_halfspace_control.csv",
        one_target["equivalence_rows"],
        list(one_target["equivalence_rows"][0].keys()),
    )
    write_csv(
        OUT_DIR / "one_target_committor_control.csv",
        one_target["committor_control_rows"],
        ["case", "q_star", "window", "L0R0", "L0R1", "L1R0", "L1R1", "dominant"],
    )
    write_csv(
        OUT_DIR / "one_target_symmetry_control.csv",
        [one_target["symmetry_control"]],
        list(one_target["symmetry_control"].keys()),
    )
    write_csv(OUT_DIR / "two_target_recheck.csv", two_target["verification_rows"], list(two_target["verification_rows"][0].keys()))


def build_report() -> None:
    ensure_dir(DATA_DIR)
    ensure_dir(FIG_DIR)
    ensure_dir(TABLE_DIR)
    ensure_dir(OUT_DIR)
    cleanup_stale_outputs()

    one_target = build_one_target_datasets()
    two_target = build_two_target_datasets()
    left_open = build_left_open_split_datasets()

    analysis_summary = {
        "one_target": one_target["summary"],
        "one_target_left_open_vs_membrane": {
            "phase_summary": left_open["phase_summary"],
            "baseline_peak_windows": {
                str(row["window"]): {
                    "none": float(row["none"]),
                    "left_only": float(row["left_only"]),
                    "mem_only": float(row["mem_only"]),
                    "both": float(row["both"]),
                }
                for row in left_open["baseline_window_rows"]
            },
        },
        "two_target": two_target["summary"],
    }

    write_flat_data_exports(one_target, two_target)
    write_report_figures(one_target, two_target)
    plot_one_target_left_open_split_windows(
        left_open["figure_rows"],
        FIG_DIR / "one_target_left_open_vs_membrane_windows.pdf",
        case_order=left_open["figure_case_ids"],
    )
    write_tables(one_target, two_target, left_open)
    write_outputs(one_target, two_target, analysis_summary)


def main() -> int:
    build_report()
    print("rebuilt canonical one-/two-target gating report artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
