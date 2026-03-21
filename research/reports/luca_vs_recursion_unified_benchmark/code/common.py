from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[4]
PACKAGE_SRC = ROOT / "packages" / "vkcore" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

REPORT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = REPORT_DIR / "data"
FIG_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"
OUT_DIR = REPORT_DIR / "outputs"

FAMILY_LUCA = "luca_gf"
FAMILY_TIME = "time_recursion"

FAMILY_LABELS = {
    FAMILY_LUCA: "Luca / generating-function family",
    FAMILY_TIME: "Time-domain recursion family",
}

FAMILY_LABELS_CN = {
    FAMILY_LUCA: "Luca / 生成函数家族",
    FAMILY_TIME: "时域递推家族",
}


@dataclass(frozen=True)
class MethodSpec:
    method_family: str
    solver_variant: str
    diagnostic_horizon: int
    curve_horizon: int


@dataclass(frozen=True)
class WorkloadSpec:
    workload_id: str
    source_report: str
    model_family: str
    geometry_kind: str
    title_en: str
    title_cn: str
    note_en: str
    note_cn: str
    state_size: int
    defect_pairs: int
    target_count: int
    common_error_horizon_diagnostic: int
    common_error_horizon_curve: int
    config: Dict[str, Any]
    display_params: Dict[str, Any]
    config_figure_id: str
    historical_source: str
    methods: Dict[str, MethodSpec]


def ensure_dirs() -> None:
    for path in (DATA_DIR, FIG_DIR, TABLE_DIR, OUT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def workload_specs() -> List[WorkloadSpec]:
    return [
        WorkloadSpec(
            workload_id="RING-1T-paper",
            source_report="ring_lazy_flux",
            model_family="ring_single_target",
            geometry_kind="ring_single_target",
            title_en="1D paper-like single-target shortcut",
            title_cn="1D paper-like 单目标 shortcut",
            note_en="Selfloop shortcut, paper-like geometry, AW vs exact time propagation.",
            note_cn="selfloop shortcut 的 paper-like 几何，比较 AW 与时域精确推进。",
            state_size=100,
            defect_pairs=1,
            target_count=1,
            common_error_horizon_diagnostic=800,
            common_error_horizon_curve=2000,
            config={
                "kind": "ring_single_target",
                "N": 100,
                "q": 2.0 / 3.0,
                "start": 1,
                "target": 50,
                "shortcut_src": 6,
                "shortcut_dst": 51,
                "beta": 0.02,
                "aw_oversample": 16,
                "aw_r_pow10": 18.0,
                "survival_eps": 1e-14,
            },
            display_params={
                "layout": "ring_with_stencil",
                "panel_focus": "single_target_shortcut",
            },
            config_figure_id="RING-1T-paper_config_detailed",
            historical_source="ring_lazy_flux paper-like single-target shortcut benchmark",
            methods={
                FAMILY_LUCA: MethodSpec(FAMILY_LUCA, "ring_analytic_aw", 800, 2000),
                FAMILY_TIME: MethodSpec(FAMILY_TIME, "ring_time_absorption", 800, 2000),
            },
        ),
        WorkloadSpec(
            workload_id="ENC-FIXED",
            source_report="ring_two_walker_encounter_shortcut",
            model_family="ring_encounter_fixed",
            geometry_kind="encounter_fixed",
            title_en="1D fixed-site encounter parity case",
            title_cn="1D fixed-site 相遇 parity 案例",
            note_en="Fixed-site C1 drift example from the encounter report; no shortcut defect in this branch.",
            note_cn="来自 encounter 报告的 fixed-site C1 漂移案例；该分支本身不含 shortcut 缺陷。",
            state_size=30 * 30,
            defect_pairs=0,
            target_count=1,
            common_error_horizon_diagnostic=900,
            common_error_horizon_curve=900,
            config={
                "kind": "encounter_fixed",
                "N": 30,
                "q1": 0.70,
                "g1": 0.90,
                "q2": 0.70,
                "g2": 0.90,
                "n0": 5,
                "m0": 12,
                "delta": 0,
                "shortcut_src": 0,
                "shortcut_dst": 0,
                "beta": 0.0,
                "aw_oversample": 4,
                "aw_r_pow10": 8.0,
            },
            display_params={
                "layout": "ring_pair_single_target",
                "panel_focus": "pair_torus_single_target",
            },
            config_figure_id="ENC-FIXED_config_detailed",
            historical_source="ring encounter fixed-site parity control",
            methods={
                FAMILY_LUCA: MethodSpec(FAMILY_LUCA, "encounter_fixedsite_gf_aw", 900, 900),
                FAMILY_TIME: MethodSpec(FAMILY_TIME, "pair_fixedsite_time_recursion", 900, 900),
            },
        ),
        WorkloadSpec(
            workload_id="ENC-ANY",
            source_report="ring_two_walker_encounter_shortcut",
            model_family="ring_encounter_any",
            geometry_kind="encounter_any",
            title_en="1D anywhere encounter representative shortcut case",
            title_cn="1D anywhere 相遇代表性 shortcut 案例",
            note_en="Representative bimodal case from the ring encounter report.",
            note_cn="来自 ring encounter 报告的代表性双峰案例。",
            state_size=101 * 101,
            defect_pairs=101,
            target_count=101,
            common_error_horizon_diagnostic=420,
            common_error_horizon_curve=800,
            config={
                "kind": "encounter_any",
                "N": 101,
                "q1": 0.70,
                "g1": 0.70,
                "q2": 0.70,
                "g2": -0.40,
                "n0": 5,
                "m0": 55,
                "shortcut_src": 5,
                "shortcut_dst": 70,
                "beta": 0.20,
                "aw_oversample": 4,
                "aw_r_pow10": 8.0,
            },
            display_params={
                "layout": "ring_pair_diagonal_target",
                "panel_focus": "pair_torus_diagonal_targets",
            },
            config_figure_id="ENC-ANY_config_detailed",
            historical_source="ring encounter representative shortcut double-peak case",
            methods={
                FAMILY_LUCA: MethodSpec(FAMILY_LUCA, "encounter_anywhere_gf_aw", 420, 800),
                FAMILY_TIME: MethodSpec(FAMILY_TIME, "pair_time_recursion", 420, 800),
            },
        ),
        WorkloadSpec(
            workload_id="TT-C1",
            source_report="grid2d_two_target_double_peak",
            model_family="grid2d_two_target",
            geometry_kind="two_target_c1",
            title_en="2D two-target C1 practical double-peak case",
            title_cn="2D two-target C1 实务双峰案例",
            note_en="The native C1 comparison uses sparse recursion on a long horizon and Luca on the AW horizon only.",
            note_cn="C1 的原生比较口径是 sparse 走长时窗，而 Luca 只跑 AW 反演时窗。",
            state_size=1679,
            defect_pairs=632,
            target_count=2,
            common_error_horizon_diagnostic=800,
            common_error_horizon_curve=800,
            config={
                "kind": "two_target_c1",
                "N": 31,
                "q": 0.2,
                "delta": 0.2,
                "time_surv_tol": 1e-13,
                "aw_oversample": 2,
                "aw_r_pow10": 8.0,
            },
            display_params={
                "layout": "grid2d_corridor_compare",
                "panel_focus": "fast_vs_slow_corridor_support",
            },
            config_figure_id="TT-C1_config_detailed",
            historical_source="grid2d two-target C1 native practical comparison",
            methods={
                FAMILY_LUCA: MethodSpec(FAMILY_LUCA, "two_target_defect_reduced_aw", 800, 800),
                FAMILY_TIME: MethodSpec(FAMILY_TIME, "two_target_sparse_exact", 1200, 6000),
            },
        ),
        WorkloadSpec(
            workload_id="TT-LF1",
            source_report="grid2d_two_target_double_peak",
            model_family="grid2d_two_target",
            geometry_kind="two_target_lf1",
            title_en="2D Luca-fast constructed sparse-defect case",
            title_cn="2D Luca-fast 构造稀疏缺陷案例",
            note_en="This anchor keeps the original asymmetric native task definition from the LF1 note.",
            note_cn="这个锚点保留 LF1 说明文中的原生非对称任务定义。",
            state_size=1679,
            defect_pairs=2,
            target_count=2,
            common_error_horizon_diagnostic=80,
            common_error_horizon_curve=80,
            config={
                "kind": "two_target_lf1",
                "N": 41,
                "q": 0.2,
                "delta": 0.2,
                "time_surv_tol": 1e-13,
                "aw_oversample": 2,
                "aw_r_pow10": 8.0,
            },
            display_params={
                "layout": "grid2d_sparse_defect",
                "panel_focus": "single_local_bias_site",
            },
            config_figure_id="TT-LF1_config_detailed",
            historical_source="grid2d two-target LF1 sparse-defect positive anchor",
            methods={
                FAMILY_LUCA: MethodSpec(FAMILY_LUCA, "two_target_defect_reduced_aw", 80, 80),
                FAMILY_TIME: MethodSpec(FAMILY_TIME, "two_target_sparse_exact", 12000, 12000),
            },
        ),
        WorkloadSpec(
            workload_id="REF-S0",
            source_report="grid2d_reflecting_bimodality",
            model_family="grid2d_reflecting",
            geometry_kind="reflecting_s0",
            title_en="2D reflecting low-defect S0 control",
            title_cn="2D reflecting 低缺陷 S0 控制案例",
            note_en="Low-defect control where full AW is still feasible and historically close to exact recursion.",
            note_cn="full AW 仍可行、且历史上与精确递推较接近的低缺陷控制案例。",
            state_size=840,
            defect_pairs=9,
            target_count=1,
            common_error_horizon_diagnostic=300,
            common_error_horizon_curve=1200,
            config={
                "kind": "reflecting_s0",
                "case_id": "S0a",
                "aw_oversample": 2,
                "aw_r_pow10": 8.0,
            },
            display_params={
                "layout": "grid2d_reflecting_control",
                "panel_focus": "sticky_plus_barrier",
            },
            config_figure_id="REF-S0_config_detailed",
            historical_source="grid2d reflecting low-defect S0 control",
            methods={
                FAMILY_LUCA: MethodSpec(FAMILY_LUCA, "reflecting_full_aw", 300, 1200),
                FAMILY_TIME: MethodSpec(FAMILY_TIME, "reflecting_exact_recursion", 300, 1200),
            },
        ),
    ]


def manifest_rows() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for spec in workload_specs():
        for task_kind in ("diagnostic", "curve"):
            for method in spec.methods.values():
                effective_horizon = method.diagnostic_horizon if task_kind == "diagnostic" else method.curve_horizon
                row = {
                    "workload_id": spec.workload_id,
                    "task_kind": task_kind,
                    "source_report": spec.source_report,
                    "model_family": spec.model_family,
                    "geometry_kind": spec.geometry_kind,
                    "method_family": method.method_family,
                    "solver_variant": method.solver_variant,
                    "native_horizon": method.diagnostic_horizon,
                    "curve_horizon": method.curve_horizon,
                    "effective_horizon": effective_horizon,
                    "state_size": spec.state_size,
                    "defect_pairs": spec.defect_pairs,
                    "target_count": spec.target_count,
                    "common_error_horizon": (
                        spec.common_error_horizon_diagnostic if task_kind == "diagnostic" else spec.common_error_horizon_curve
                    ),
                    "title_en": spec.title_en,
                    "title_cn": spec.title_cn,
                    "note_en": spec.note_en,
                    "note_cn": spec.note_cn,
                    "config_figure_id": spec.config_figure_id,
                    "historical_source": spec.historical_source,
                    "display_params_json": json.dumps(spec.display_params, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                    "config_json": json.dumps(spec.config, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                }
                rows.append(row)
    return rows


def workload_by_id() -> Dict[str, WorkloadSpec]:
    return {spec.workload_id: spec for spec in workload_specs()}


def workload_order() -> List[str]:
    return [spec.workload_id for spec in workload_specs()]


def group_rows(rows: Iterable[Dict[str, Any]], *keys: str) -> Dict[tuple[Any, ...], List[Dict[str, Any]]]:
    groups: Dict[tuple[Any, ...], List[Dict[str, Any]]] = {}
    for row in rows:
        key = tuple(row[k] for k in keys)
        groups.setdefault(key, []).append(row)
    return groups
