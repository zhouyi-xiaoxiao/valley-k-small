from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_TOOLS = ROOT / "platform" / "tools" / "repo"
if str(REPO_TOOLS) not in sys.path:
    sys.path.insert(0, str(REPO_TOOLS))

from report_registry import load_registry


def test_only_one_active_compare_report_in_registry() -> None:
    ids = {item["id"] for item in load_registry()}
    assert "luca_vs_recursion_unified_benchmark" in ids
    assert "cross_luca_regime_map" not in ids


def test_legacy_compare_materials_are_gone() -> None:
    legacy_paths = [
        ROOT / "research" / "reports" / "cross_luca_regime_map",
        ROOT / "research" / "reports" / "grid2d_two_target_double_peak" / "manuscript" / "extras" / "method_comparison_cn.tex",
        ROOT / "research" / "reports" / "grid2d_two_target_double_peak" / "manuscript" / "extras" / "method_comparison_en.tex",
        ROOT / "research" / "reports" / "grid2d_two_target_double_peak" / "notes" / "method_comparison_cn.md",
        ROOT / "research" / "reports" / "grid2d_two_target_double_peak" / "notes" / "method_comparison_en.md",
        ROOT / "research" / "reports" / "grid2d_two_target_double_peak" / "code" / "compare_numeric_methods.py",
        ROOT / "research" / "reports" / "grid2d_two_target_double_peak" / "code" / "luca_fast_case.py",
        ROOT / "research" / "reports" / "grid2d_reflecting_bimodality" / "code" / "benchmark_aw_exact.py",
    ]
    for path in legacy_paths:
        assert not path.exists(), f"legacy compare material still present: {path}"
