from __future__ import annotations

import numpy as np

from vkcore.grid2d.bimod_legacy_imports import (
    plot_bimodality_diagnostic_v12,
    plot_bimodality_proof_B,
    plot_channel_decomp_v12,
    plot_environment_v12,
    plot_fig3_panel_v12,
    plot_fpt_multiscale_v12,
    plot_paths_density_v12,
)


def render_case_figures(
    *,
    case_geom,
    fig_dirs,
    prefix: str,
    t: np.ndarray,
    f_exact: np.ndarray,
    f_aw: np.ndarray,
    metrics: dict,
    metrics_mode: str,
    heat_view,
    heat_mask: np.ndarray,
    heat_q: float,
    heat_floor_ratio: float,
    heatmaps_by_time: dict,
    fast_path: np.ndarray,
    slow_path: np.ndarray,
    paths_fast,
    paths_slow,
    mc_centers: np.ndarray,
    mc_pmf: np.ndarray,
    mc_smooth_window_slow: int,
    f_fast: np.ndarray,
    f_slow: np.ndarray,
    p_fast: float,
    p_slow: float,
    png_dpi: int,
) -> None:
    t_p1 = int(metrics["t_p1"])
    t_v = int(metrics["t_v"])
    t_p2 = int(metrics["t_p2"])

    mats = [heatmaps_by_time[t_p1], heatmaps_by_time[t_v], heatmaps_by_time[t_p2]]

    plot_environment_v12(
        case_geom,
        outpath=fig_dirs["env"] / f"{prefix}_env.pdf",
        dpi=png_dpi,
        fast_path=fast_path,
        slow_path=slow_path,
    )

    plot_fig3_panel_v12(
        case_geom,
        mats=mats,
        times=[t_p1, t_v, t_p2],
        outpath=fig_dirs["fig3_panels"] / f"{prefix}_fig3_panel.pdf",
        dpi=png_dpi,
        fast_path=fast_path,
        slow_path=slow_path,
        heat_view=heat_view,
        heat_mask=heat_mask,
        heat_q=heat_q,
        heat_floor_ratio=heat_floor_ratio,
    )

    plot_paths_density_v12(
        case_geom,
        paths_density=paths_fast,
        rep_paths=[fast_path] if fast_path.size else [],
        outpath=fig_dirs["paths"] / f"{prefix}_paths_fast.pdf",
        dpi=png_dpi,
    )
    plot_paths_density_v12(
        case_geom,
        paths_density=paths_slow,
        rep_paths=[slow_path] if slow_path.size else [],
        outpath=fig_dirs["paths"] / f"{prefix}_paths_slow.pdf",
        dpi=png_dpi,
    )

    plot_fpt_multiscale_v12(
        t_exact=t,
        f_exact=f_exact,
        t_aw=t,
        f_aw=f_aw,
        mc_centers=mc_centers,
        mc_pmf=mc_pmf,
        peaks=(t_p1, t_v, t_p2),
        outpath=fig_dirs["fpt"] / f"{prefix}_fpt.pdf",
        log_eps=1e-14,
        mc_smooth_window_slow=mc_smooth_window_slow,
    )

    plot_bimodality_proof_B(
        t=t,
        f_exact=f_exact,
        f_aw=f_aw,
        metrics={"t_p1": t_p1, "t_v": t_v, "t_p2": t_p2, "h2_over_h1": metrics["h2_over_h1"], "valley_ratio": metrics["valley_ratio"]},
        t_max_zoom=min(int(t.size), max(t_p2 + 200, t_v + 200)),
        outpath=fig_dirs["fpt"] / f"{prefix}_proof.pdf",
        log_eps=1e-14,
        dpi=png_dpi,
    )

    if metrics_mode == "windowed":
        plot_bimodality_diagnostic_v12(
            t=t,
            f_exact=f_exact,
            smooth_window=int(metrics.get("smooth_window", 9)),
            outpath=fig_dirs["fpt"] / f"{prefix}_diagnostic.pdf",
            prominence=1e-9,
            distance=20,
            min_gap=20,
            method="windowed",
            early_window=metrics.get("early_window"),
            late_window=metrics.get("late_window"),
            dpi=png_dpi,
        )
    else:
        plot_bimodality_diagnostic_v12(
            t=t,
            f_exact=f_exact,
            smooth_window=int(metrics.get("smooth_window", 9)),
            outpath=fig_dirs["fpt"] / f"{prefix}_diagnostic.pdf",
            prominence=1e-9,
            distance=20,
            min_gap=20,
            dpi=png_dpi,
        )

    plot_channel_decomp_v12(
        t=t,
        f_fast=f_fast,
        f_slow=f_slow,
        p_fast=p_fast,
        p_slow=p_slow,
        outpath=fig_dirs["channel_decomp"] / f"{prefix}_channel_decomp.pdf",
        dpi=png_dpi,
        tail_zoom=True,
    )


__all__ = ["render_case_figures"]
