from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research" / "reports" / "luca_vs_recursion_unified_benchmark"
DATA = REPORT / "artifacts" / "data"
FIG = REPORT / "artifacts" / "figures"
TABLES = REPORT / "artifacts" / "tables"
MANUSCRIPT = REPORT / "manuscript"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_unified_benchmark_assets_exist() -> None:
    required = [
        DATA / "manifest.csv",
        DATA / "runtime_raw.csv",
        DATA / "runtime_summary.json",
        FIG / "unified_runtime_diagnostic.pdf",
        FIG / "unified_runtime_curve.pdf",
        FIG / "unified_speedup_by_workload.pdf",
        FIG / "RING-1T-paper_config_detailed.pdf",
        FIG / "ENC-FIXED_config_detailed.pdf",
        FIG / "ENC-ANY_config_detailed.pdf",
        FIG / "TT-C1_config_detailed.pdf",
        FIG / "TT-LF1_config_detailed.pdf",
        FIG / "REF-S0_config_detailed.pdf",
        TABLES / "unified_runtime_diagnostic_en.tex",
        TABLES / "unified_runtime_curve_en.tex",
        TABLES / "unified_runtime_diagnostic_cn.tex",
        TABLES / "unified_runtime_curve_cn.tex",
        TABLES / "unified_complexity_table.tex",
        TABLES / "unified_solver_map.tex",
        TABLES / "unified_recommendation_en.tex",
        TABLES / "unified_recommendation_cn.tex",
        TABLES / "unified_workload_inventory_en.tex",
        TABLES / "unified_workload_inventory_cn.tex",
        TABLES / "unified_appendix_fairness_en.tex",
        TABLES / "unified_appendix_fairness_cn.tex",
        MANUSCRIPT / "luca_vs_recursion_unified_benchmark_en.tex",
        MANUSCRIPT / "luca_vs_recursion_unified_benchmark_cn.tex",
        REPORT / "README.md",
    ]
    for path in required:
        assert path.exists(), f"missing asset: {path}"


def test_unified_benchmark_summary_consistency() -> None:
    summary = _read_json(DATA / "runtime_summary.json")
    with (DATA / "manifest.csv").open(encoding="utf-8") as fh:
        manifest = list(csv.DictReader(fh))
    with (DATA / "runtime_raw.csv").open(encoding="utf-8") as fh:
        runtime_raw = list(csv.DictReader(fh))

    assert summary["counts"]["manifest_rows"] == len(manifest)
    assert summary["counts"]["runtime_rows"] == len(runtime_raw)
    assert summary["counts"]["pair_rows"] == 12
    assert len(summary["pair_rows"]) == 12
    workload_ids = {row["workload_id"] for row in summary["pair_rows"]}
    assert workload_ids == {"RING-1T-paper", "ENC-FIXED", "ENC-ANY", "TT-C1", "TT-LF1", "REF-S0"}

    diagnostic = [row for row in summary["pair_rows"] if row["task_kind"] == "diagnostic"]
    curve = [row for row in summary["pair_rows"] if row["task_kind"] == "curve"]
    assert len(diagnostic) == 6
    assert len(curve) == 6
    assert any(row["recommended_family"] == "luca_gf" for row in summary["pair_rows"])
    assert any(row["recommended_family"] == "time_recursion" for row in summary["pair_rows"])

    readme = (REPORT / "README.md").read_text(encoding="utf-8")
    report_en = (MANUSCRIPT / "luca_vs_recursion_unified_benchmark_en.tex").read_text(encoding="utf-8")
    report_cn = (MANUSCRIPT / "luca_vs_recursion_unified_benchmark_cn.tex").read_text(encoding="utf-8")
    assert "single active computational-method comparison report" in readme
    assert "Appendix F" in readme
    assert "Appendix B: Detailed GF Derivations" in report_en
    assert "附录 B：GF 家族完整推导" in report_cn
    assert "cross_luca_regime_map" not in readme
    assert "cross_luca_regime_map" not in report_en
    assert "cross_luca_regime_map" not in report_cn
