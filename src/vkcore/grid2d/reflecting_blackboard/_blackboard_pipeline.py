#!/usr/bin/env python3
"""Compatibility facade for blackboard-style bimodality pipeline."""

from __future__ import annotations

from .cases_blackboard import (
    CONFIG_FILENAMES,
    DIR_MAP,
    CaseDef,
    add_segment,
    build_a,
    build_b,
    build_barriers,
    build_c,
    build_d,
    build_e,
    build_r,
    build_s,
    build_x,
    build_y,
    build_z,
    iter_cases,
)
from .io import write_case_config as _write_case_config
from .model import (
    as_case_geometry as _as_case_geometry,
    case_to_spec as _case_to_spec_generic,
    coord_to_index as _coord_to_index,
    heat_mask_for_case as _heat_mask_for_case,
    heat_view_for_case as _heat_view_for_case,
    slow_mask as _slow_mask,
)
from .pipeline import run_blackboard_pipeline
from .scans import (
    aw_errors as _aw_errors,
    aw_from_exact as _aw_from_exact,
    bin_pmf as _bin_pmf,
    collect_paths as _collect_paths,
    compute_metrics_with_fallback,
    mc_histogram as _mc_histogram,
    mc_params_for_case as _mc_params_for_case_generic,
    mc_times_labels as _mc_times_labels,
    median_time as _median_time,
    metrics_from_peak_indices as _metrics_from_peak_indices,
    pick_representative_path as _pick_representative_path,
    simulate_path as _simulate_path,
    smooth_pmf as _smooth_pmf,
    to_one_based as _to_one_based,
    windowed_peak_indices as _windowed_peak_indices,
)


def _case_to_spec(case: CaseDef):
    return _case_to_spec_generic(
        case,
        dir_map=DIR_MAP,
        build_barriers=build_barriers,
        include_extra_barriers=True,
    )


def _mc_params_for_case(case: CaseDef, args):
    return _mc_params_for_case_generic(case, args, profile="blackboard")


def main() -> None:
    run_blackboard_pipeline()


__all__ = [
    "CONFIG_FILENAMES",
    "DIR_MAP",
    "CaseDef",
    "_as_case_geometry",
    "_aw_errors",
    "_aw_from_exact",
    "_bin_pmf",
    "_case_to_spec",
    "_collect_paths",
    "_coord_to_index",
    "_heat_mask_for_case",
    "_heat_view_for_case",
    "_mc_histogram",
    "_mc_params_for_case",
    "_mc_times_labels",
    "_median_time",
    "_metrics_from_peak_indices",
    "_pick_representative_path",
    "_simulate_path",
    "_slow_mask",
    "_smooth_pmf",
    "_to_one_based",
    "_windowed_peak_indices",
    "_write_case_config",
    "add_segment",
    "build_a",
    "build_b",
    "build_barriers",
    "build_c",
    "build_d",
    "build_e",
    "build_r",
    "build_s",
    "build_x",
    "build_y",
    "build_z",
    "compute_metrics_with_fallback",
    "iter_cases",
    "main",
]


if __name__ == "__main__":
    main()
