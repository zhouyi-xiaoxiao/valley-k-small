from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import numpy as np

from vkcore.grid2d.bimod_legacy_imports import (
    distributions_at_times,
    exact_fpt,
    hist_pmf,
    plot_cartoon_channels,
    plot_symbol_legend_v12,
)
from vkcore.grid2d.model_core_reflecting import spec_to_internal

from . import io as io_helpers
from . import model as model_helpers
from . import plots as plot_helpers
from . import scans as scan_helpers
from .cases_blackboard import CONFIG_FILENAMES as CONFIG_FILENAMES_BLACKBOARD
from .cases_blackboard import DIR_MAP as DIR_MAP_BLACKBOARD
from .cases_blackboard import build_barriers as build_barriers_blackboard
from .cases_blackboard import iter_cases as iter_cases_blackboard
from .cases_reflecting import CONFIG_FILENAMES as CONFIG_FILENAMES_REFLECTING
from .cases_reflecting import DIR_MAP as DIR_MAP_REFLECTING
from .cases_reflecting import build_barriers as build_barriers_reflecting
from .cases_reflecting import iter_cases as iter_cases_reflecting

REPO_ROOT = Path(__file__).resolve().parents[4]
REPORT_DIR_REFLECTING = REPO_ROOT / "reports" / "grid2d_reflecting_bimodality"
REPORT_DIR_BLACKBOARD = REPO_ROOT / "reports" / "grid2d_blackboard_bimodality"


def _build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--cases", type=str, default="", help="Comma-separated case IDs (default: all).")
    parser.add_argument("--mc-samples", type=int, default=30000)
    parser.add_argument("--mc-bin-width", type=int, default=2)
    parser.add_argument("--mc-smooth-window", type=int, default=5)
    parser.add_argument("--peak-smooth-window", type=int, default=9)
    parser.add_argument("--aw-oversample", type=int, default=4)
    parser.add_argument("--aw-rpow10", type=float, default=12.0)
    parser.add_argument("--png-dpi", type=int, default=800)
    parser.add_argument("--heat-quantile", type=float, default=0.05)
    parser.add_argument("--heat-floor-ratio", type=float, default=1e-7)
    parser.add_argument("--heat-view-pad", type=int, default=2)
    return parser


def run_cases(
    *,
    cases: Iterable,
    args: argparse.Namespace,
    report_dir: Path,
    dir_map: dict[str, str],
    build_barriers,
    config_filenames: dict[str, str],
    include_extra_barriers: bool,
    mc_profile: str,
) -> None:
    fig_dirs = io_helpers.ensure_report_dirs(report_dir)

    plot_symbol_legend_v12(outpath=fig_dirs["env"] / "symbol_legend.pdf", dpi=args.png_dpi)
    plot_cartoon_channels(outpath=fig_dirs["fig3_panels"] / "channel_cartoon.pdf", dpi=args.png_dpi)

    seed_base = 2026

    for idx, case in enumerate(cases):
        prefix = f"case_{case.case_id}"
        case_geom = model_helpers.as_case_geometry(
            case,
            dir_map=dir_map,
            build_barriers=build_barriers,
            include_extra_barriers=include_extra_barriers,
        )
        spec = model_helpers.case_to_spec(
            case,
            dir_map=dir_map,
            build_barriers=build_barriers,
            include_extra_barriers=include_extra_barriers,
        )
        cfg = spec_to_internal(spec)

        io_helpers.write_case_config(
            case,
            report_dir / "config",
            config_filenames=config_filenames,
            build_barriers=build_barriers,
            include_extra_barriers=include_extra_barriers,
        )

        f_exact, p_abs = exact_fpt(cfg, t_max=case.t_max)
        t = np.arange(1, len(f_exact) + 1)
        f_aw, aw_params = scan_helpers.aw_from_exact(
            f_exact,
            t_max=len(f_exact),
            oversample=args.aw_oversample,
            r_pow10=args.aw_rpow10,
        )
        aw_err = scan_helpers.aw_errors(f_aw, f_exact)

        metrics, metrics_mode = scan_helpers.compute_metrics_with_fallback(
            f_exact,
            t_max=case.t_max,
            peak_smooth_window=args.peak_smooth_window,
            min_gap=20,
        )
        t_p1 = int(metrics["t_p1"])
        t_v = int(metrics["t_v"])
        t_p2 = int(metrics["t_p2"])

        slow_mask = model_helpers.slow_mask(case)
        mc_samples, mc_bin_width, mc_smooth_window, mc_smooth_window_slow = scan_helpers.mc_params_for_case(
            case,
            args,
            profile=mc_profile,
        )
        mc_times, mc_labels, mc_stats, neighbors, cum_probs = scan_helpers.mc_times_labels(
            cfg,
            slow_mask=slow_mask,
            n_walkers=mc_samples,
            max_steps=case.t_max,
            seed=seed_base + idx * 17,
        )

        tail_start = max(int(t_p2 + 50), int(t_v + 30), 200)
        tail_bin_width = max(mc_bin_width * 4, 8)
        tail_smooth_window = max(mc_smooth_window * 3, mc_smooth_window + 12)
        mc_centers, mc_binned = scan_helpers.mc_histogram(
            mc_times,
            t_max=case.t_max,
            bin_width=mc_bin_width,
            smooth_window=mc_smooth_window,
            tail_start=tail_start,
            tail_bin_width=tail_bin_width,
            tail_smooth_window=tail_smooth_window,
            censor=True,
            n_total=int(mc_times.size),
        )
        if mc_smooth_window_slow is None:
            mc_smooth_window_slow = max(mc_smooth_window * 2 + 1, 11)

        fast_times = mc_times[mc_labels == 0]
        slow_times = mc_times[mc_labels == 1]
        f_fast, _ = hist_pmf(fast_times, case.t_max)
        f_slow, _ = hist_pmf(slow_times, case.t_max)
        p_fast = float(np.mean(mc_labels == 0))
        p_slow = float(np.mean(mc_labels == 1))

        heatmaps = distributions_at_times(cfg, [t_p1, t_v, t_p2], conditional=True)

        rng = np.random.default_rng(seed_base + 1000 + idx * 11)
        slow_mask_path = slow_mask.copy()

        def sample_func(rng_local):
            return scan_helpers.simulate_path(
                cfg,
                neighbors=neighbors,
                cum_probs=cum_probs,
                slow_mask=slow_mask_path,
                max_steps=min(case.t_max, 12000),
                rng=rng_local,
            )

        med_fast = scan_helpers.median_time(mc_times, mc_labels, 0)
        med_slow = scan_helpers.median_time(mc_times, mc_labels, 1)
        rep_fast = scan_helpers.pick_representative_path(
            sample_func,
            label=0,
            target_time=med_fast or 0,
            rng=rng,
            max_attempts=8000,
        )
        rep_slow = scan_helpers.pick_representative_path(
            sample_func,
            label=1,
            target_time=med_slow or 0,
            rng=rng,
            max_attempts=8000,
        )

        fast_path = scan_helpers.to_one_based(rep_fast[0]) if rep_fast else np.array([])
        slow_path = scan_helpers.to_one_based(rep_slow[0]) if rep_slow else np.array([])

        paths_fast = scan_helpers.collect_paths(
            sample_func,
            label=0,
            n_paths=500,
            rng=rng,
            max_attempts=20000,
        )
        paths_slow = scan_helpers.collect_paths(
            sample_func,
            label=1,
            n_paths=500,
            rng=rng,
            max_attempts=20000,
        )

        heat_view = model_helpers.heat_view_for_case(case, pad=args.heat_view_pad)
        heat_mask = model_helpers.heat_mask_for_case(case)

        plot_helpers.render_case_figures(
            case_geom=case_geom,
            fig_dirs=fig_dirs,
            prefix=prefix,
            t=t,
            f_exact=f_exact,
            f_aw=f_aw,
            metrics=metrics,
            metrics_mode=metrics_mode,
            heat_view=heat_view,
            heat_mask=heat_mask,
            heat_q=args.heat_quantile,
            heat_floor_ratio=args.heat_floor_ratio,
            heatmaps_by_time=heatmaps,
            fast_path=fast_path,
            slow_path=slow_path,
            paths_fast=paths_fast,
            paths_slow=paths_slow,
            mc_centers=mc_centers,
            mc_pmf=mc_binned,
            mc_smooth_window_slow=mc_smooth_window_slow,
            f_fast=f_fast,
            f_slow=f_slow,
            p_fast=p_fast,
            p_slow=p_slow,
            png_dpi=args.png_dpi,
        )

        io_helpers.write_metrics_payload(
            report_dir,
            case=case,
            metrics=metrics,
            absorption_prob=float(p_abs),
            aw_params=aw_params,
            aw_err=aw_err,
            mc_stats=mc_stats,
        )


def run_reflecting_pipeline(argv: list[str] | None = None) -> None:
    parser = _build_parser("Reflecting-boundary bimodality pipeline")
    args = parser.parse_args(argv)
    case_ids = [c.strip() for c in args.cases.split(",") if c.strip()]
    run_cases(
        cases=iter_cases_reflecting(case_ids=case_ids),
        args=args,
        report_dir=REPORT_DIR_REFLECTING,
        dir_map=DIR_MAP_REFLECTING,
        build_barriers=build_barriers_reflecting,
        config_filenames=CONFIG_FILENAMES_REFLECTING,
        include_extra_barriers=False,
        mc_profile="reflecting",
    )


def run_blackboard_pipeline(argv: list[str] | None = None) -> None:
    parser = _build_parser("Reflecting-boundary bimodality pipeline")
    args = parser.parse_args(argv)
    case_ids = [c.strip() for c in args.cases.split(",") if c.strip()]
    run_cases(
        cases=iter_cases_blackboard(case_ids=case_ids),
        args=args,
        report_dir=REPORT_DIR_BLACKBOARD,
        dir_map=DIR_MAP_BLACKBOARD,
        build_barriers=build_barriers_blackboard,
        config_filenames=CONFIG_FILENAMES_BLACKBOARD,
        include_extra_barriers=True,
        mc_profile="blackboard",
    )


__all__ = ["run_blackboard_pipeline", "run_cases", "run_reflecting_pipeline"]
