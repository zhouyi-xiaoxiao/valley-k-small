from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research" / "reports" / "grid2d_one_two_target_gating"
DATA = REPORT / "artifacts" / "data"
FIGURES = REPORT / "artifacts" / "figures"
TABLES = REPORT / "artifacts" / "tables"
MANUSCRIPT = REPORT / "manuscript"
SRC = ROOT / "packages" / "vkcore" / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vkcore.grid2d.one_two_target_gating.phase_v2 import reduce_gate_word


CANONICAL_CASES = {
    "sym_shared",
    "tb_asym_balanced",
    "dir_asym_easy_out_balanced",
    "dir_asym_easy_in_balanced",
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_gating_report_assets_exist() -> None:
    required = [
        DATA / "analysis_summary.json",
        DATA / "verification_summary.json",
        DATA / "one_target_representative_summary.csv",
        DATA / "one_target_tb_scan.csv",
        DATA / "one_target_dir_scan.csv",
        DATA / "one_target_gate_scan.csv",
        DATA / "one_target_gate_window_families_xg_star.csv",
        DATA / "one_target_rollback_window_families.csv",
        DATA / "one_target_side_window_families_xg_star.csv",
        DATA / "one_target_start_scan.csv",
        DATA / "one_target_phase0_examples.csv",
        DATA / "one_target_line_vs_halfspace_control.csv",
        DATA / "one_target_symmetry_control.csv",
        DATA / "one_target_committor_control_peak2.csv",
        DATA / "two_target_representative_summary.csv",
        DATA / "validation_summary.csv",
        DATA / "two_target_d_dy_grid_scan.csv",
        DATA / "representatives" / "anchor" / "anchor_metrics.json",
        FIGURES / "one_target_gate_geometry.pdf",
        FIGURES / "one_target_class_crosswalk.pdf",
        FIGURES / "one_target_tb_phase_map.pdf",
        FIGURES / "one_target_tb_sep_map.pdf",
        FIGURES / "one_target_dir_phase_map.pdf",
        FIGURES / "one_target_dir_sep_map.pdf",
        FIGURES / "one_target_gate_scan_families.pdf",
        FIGURES / "one_target_gate_scan_totals.pdf",
        FIGURES / "one_target_rollback_window_bars.pdf",
        FIGURES / "one_target_window_families.pdf",
        FIGURES / "one_target_side_window_bars.pdf",
        FIGURES / "one_target_start_phase_map.pdf",
        FIGURES / "one_target_directional_window_flux.pdf",
        FIGURES / "one_target_directional_window_occupancy_atlas.pdf",
        FIGURES / "one_target_committor_control_geometry.pdf",
        FIGURES / "representatives" / "anchor" / "anchor_geometry_gates.pdf",
        FIGURES / "representatives" / "anchor" / "anchor_family_fpt_coarse.pdf",
        TABLES / "one_target_representative.tex",
        TABLES / "one_target_gate_scan_summary.tex",
        TABLES / "one_target_phase0_loss_summary.tex",
        TABLES / "two_target_representative.tex",
    ]
    for path in required:
        assert path.exists(), f"missing artifact: {path}"


def test_one_target_representatives_and_scans_are_consistent() -> None:
    rep_rows = _read_csv(DATA / "one_target_representative_summary.csv")
    assert {row["case"] for row in rep_rows} == CANONICAL_CASES
    assert sum(row["role"] == "standard" for row in rep_rows) == 1
    for row in rep_rows:
        total_lr = sum(float(row[key]) for key in ("L0R0", "L0R1", "L1R0", "L1R1"))
        total_npq = sum(float(row[key]) for key in ("N", "P", "Q"))
        assert total_lr == pytest.approx(1.0, abs=1.0e-6)
        assert total_npq == pytest.approx(1.0, abs=1.0e-6)
        assert float(row["no_leak_total"]) + float(row["leak_total"]) == pytest.approx(1.0, abs=1.0e-6)
        assert 0.0 <= float(row["rollback_total"]) <= 1.0
        assert row["peak2_dominant_gate_family"] in {"N", "P", "Q"}
        assert row["peak2_dominant_rollback_class"] in {"L0R0", "L0R1", "L1R0", "L1R1"}

    tb_rows = _read_csv(DATA / "one_target_tb_scan.csv")
    dir_rows = _read_csv(DATA / "one_target_dir_scan.csv")
    assert len(tb_rows) == 225
    assert len(dir_rows) == 225
    for rows, scan_type in (
        (tb_rows, "tb"),
        (dir_rows, "dir"),
    ):
        assert {row["scan_type"] for row in rows} == {scan_type}
        for row in rows:
            total_lr = sum(float(row[key]) for key in ("L0R0", "L0R1", "L1R0", "L1R1"))
            total_npq = sum(float(row[key]) for key in ("N", "P", "Q"))
            assert total_lr == pytest.approx(1.0, abs=1.0e-6)
            assert total_npq == pytest.approx(1.0, abs=1.0e-6)
            assert 0 <= int(row["phase"]) <= 2

    gate_scan_rows = _read_csv(DATA / "one_target_gate_scan.csv")
    assert {row["case"] for row in gate_scan_rows} == CANONICAL_CASES
    x_vals = {int(row["X_g"]) for row in gate_scan_rows}
    assert min(x_vals) == 9
    assert max(x_vals) == 57
    for row in gate_scan_rows:
        total_npq = sum(float(row[key]) for key in ("N", "P", "Q"))
        assert total_npq == pytest.approx(1.0, abs=1.0e-6)
        assert row["dominant_family"] in {"N", "P", "Q"}
        assert row["dominant_lr"] in {"L0R0", "L0R1", "L1R0", "L1R1"}

    control_rows = _read_csv(DATA / "one_target_line_vs_halfspace_control.csv")
    assert len(control_rows) == len(gate_scan_rows)
    for row in control_rows:
        assert float(row["max_family_abs_diff"]) < 1.0e-10
        assert float(row["max_lr_abs_diff"]) < 1.0e-10
        assert float(row["max_side_abs_diff"]) < 1.0e-10
        assert float(row["max_total_abs_diff"]) < 1.0e-10

    symmetry_rows = _read_csv(DATA / "one_target_symmetry_control.csv")
    assert len(symmetry_rows) == 1
    sym = symmetry_rows[0]
    assert sym["case_a"] == "sym_shared"
    assert sym["case_b"] == "tb_sym_control"
    assert float(sym["max_npq_abs_diff"]) < 1.0e-10
    assert float(sym["max_lr_abs_diff"]) < 1.0e-10
    assert float(sym["max_side_abs_diff"]) < 1.0e-10
    assert float(sym["max_total_abs_diff"]) < 1.0e-10


def test_one_target_start_scan_and_phase0_examples_exist() -> None:
    start_rows = _read_csv(DATA / "one_target_start_scan.csv")
    assert {row["case"] for row in start_rows} == CANONICAL_CASES
    assert len(start_rows) == 4 * (60 * 16 - 1)
    for case_name in CANONICAL_CASES:
        case_rows = [row for row in start_rows if row["case"] == case_name]
        assert len(case_rows) == (60 * 16 - 1)
        assert {int(row["x_gate"]) for row in case_rows} == {32}
        for row in case_rows:
            assert 0 <= int(row["phase"]) <= 2
            assert float(row["sep_peaks"]) >= 0.0

    phase0_rows = _read_csv(DATA / "one_target_phase0_examples.csv")
    assert len(phase0_rows) == 12
    assert {row["case"] for row in phase0_rows} == CANONICAL_CASES
    for case_name in CANONICAL_CASES:
        labels = {row["label"] for row in phase0_rows if row["case"] == case_name}
        assert labels == {"A", "B", "C"}

    comm_rows = _read_csv(DATA / "one_target_committor_control_peak2.csv")
    assert len(comm_rows) == 5
    assert {row["case"] for row in comm_rows} == {"sym_shared"}
    assert {float(row["q_star"]) for row in comm_rows} == {0.3, 0.4, 0.5, 0.6, 0.7}


def test_one_target_summary_and_manuscripts_match_new_language() -> None:
    summary = json.loads((DATA / "analysis_summary.json").read_text(encoding="utf-8"))
    one_target = summary["one_target"]
    assert one_target["standard_case"] == "sym_shared"
    assert set(one_target["comparison_cases"]) == {
        "tb_asym_balanced",
        "dir_asym_easy_out_balanced",
        "dir_asym_easy_in_balanced",
    }
    assert one_target["x_gate_star"] == 32
    assert one_target["tb_phase0_count"] >= 0
    assert one_target["dir_phase0_count"] >= 0
    for case_name, counts in one_target["start_phase_counts"].items():
        assert case_name in CANONICAL_CASES
        assert sum(int(v) for v in counts.values()) == (60 * 16 - 1)

    for path in (
        MANUSCRIPT / "grid2d_one_two_target_gating_cn.tex",
        MANUSCRIPT / "grid2d_one_two_target_gating_en.tex",
    ):
        text = path.read_text(encoding="utf-8")
        assert ".png" not in text
        for name in (
            "one_target_gate_geometry.pdf",
            "one_target_class_crosswalk.pdf",
            "one_target_tb_phase_map.pdf",
            "one_target_dir_phase_map.pdf",
            "one_target_start_phase_map.pdf",
            "one_target_rollback_window_bars.pdf",
            "one_target_committor_control_geometry.pdf",
        ):
            assert name in text


def test_two_target_phase_counts_and_late_family_invariants() -> None:
    summary = json.loads((DATA / "analysis_summary.json").read_text(encoding="utf-8"))
    phase_counts = summary["two_target"]["phase_counts"]
    assert phase_counts == {"0": 2, "2": 61}
    assert summary["two_target"]["late_family_all_phase_ge_1"] == "F_no_return"

    rep_rows = _read_csv(DATA / "two_target_representative_summary.csv")
    assert {row["case"] for row in rep_rows} == {"anchor", "clear_instance", "near_mass_loss"}
    for row in rep_rows:
        assert float(row["peak2_F_no_return"]) > float(row["peak2_F_rollback"])


def test_two_target_committor_consistency_remains_tight() -> None:
    validation_rows = _read_csv(DATA / "validation_summary.csv")
    assert len(validation_rows) == 3
    for row in validation_rows:
        assert float(row["q_far_gap_vs_p_far"]) < 1.0e-6
        assert float(row["closure_max_abs"]) < 1.0e-9
        assert float(row["mc_max_family_abs_err"]) < 0.02


def test_phase_v2_gate_word_reduction_smoke() -> None:
    word = reduce_gate_word(["A", "U1", "U1", "Gq", "A", "D2"])
    assert word.used_excursion is True
    assert word.used_rollback is True
    assert word.side == "UD"
    assert word.bin_tag == "both"
    assert word.n_rollbacks == 1
