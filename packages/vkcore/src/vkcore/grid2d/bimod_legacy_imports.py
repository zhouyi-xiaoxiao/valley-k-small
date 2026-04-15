from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BIMOD_CODE = REPO_ROOT / "reports" / "grid2d_bimodality" / "code"

if str(BIMOD_CODE) not in sys.path:
    sys.path.insert(0, str(BIMOD_CODE))

from aw_pgf import choose_aw_params  # noqa: E402
from fpt_exact_mc import distributions_at_times, exact_fpt, hist_pmf  # noqa: E402
from plot_fig3_panel_v12 import plot_environment_v12, plot_fig3_panel_v12, plot_symbol_legend_v12  # noqa: E402
from plot_fpt_v12 import (  # noqa: E402
    plot_bimodality_diagnostic_v12,
    plot_bimodality_proof_B,
    plot_channel_decomp_v12,
    plot_fpt_multiscale_v12,
)
from plot_paths_v12 import plot_paths_density_v12  # noqa: E402
from plot_style_fig3v2 import plot_cartoon_channels  # noqa: E402
from plot_style_v12 import ViewBox, compute_bimodality_metrics, smooth_ma  # noqa: E402
from viz.case_data import CaseGeometry  # noqa: E402

__all__ = [
    "BIMOD_CODE",
    "CaseGeometry",
    "ViewBox",
    "choose_aw_params",
    "compute_bimodality_metrics",
    "distributions_at_times",
    "exact_fpt",
    "hist_pmf",
    "plot_bimodality_diagnostic_v12",
    "plot_bimodality_proof_B",
    "plot_cartoon_channels",
    "plot_channel_decomp_v12",
    "plot_environment_v12",
    "plot_fig3_panel_v12",
    "plot_fpt_multiscale_v12",
    "plot_paths_density_v12",
    "plot_symbol_legend_v12",
    "smooth_ma",
]
