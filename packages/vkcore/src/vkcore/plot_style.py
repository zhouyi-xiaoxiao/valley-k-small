from __future__ import annotations

from typing import Any


def apply_research_plot_style() -> dict[str, Any]:
    """Apply readable matplotlib defaults for first-passage report figures."""

    import matplotlib.pyplot as plt

    rc_updates: dict[str, Any] = {
        "axes.labelsize": 15,
        "axes.titlesize": 15,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
        "lines.linewidth": 2.0,
        "savefig.dpi": 300,
        "figure.dpi": 120,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linewidth": 0.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
    plt.rcParams.update(rc_updates)
    return rc_updates

